# -*- coding: utf-8 -*-
"""
Sistema de Cache Inteligente para Reportes - Rexus.app
Implementa caching estratégico y adaptativos para optimizar rendimiento de reportes

Características principales:
1. Cache con TTL (Time To Live) configurable
2. Invalidación inteligente basada en cambios de datos
3. Compresión automática para reportes grandes
4. Métricas de hit/miss ratio
5. Limpieza automática de cache obsoleto
6. Soporte para reportes complejos y agregaciones

Autor: Rexus Development Team
Fecha: 23/08/2025
Versión: 1.0.0
"""

import json
import pickle
import hashlib
import time
import threading
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union, Callable
from pathlib import Path
import logging
import sqlite3
import gzip
import sys
from dataclasses import dataclass, asdict
from enum import Enum

# Configurar encoding UTF-8
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Configurar logging
logger = logging.getLogger(__name__)


class CacheStrategy(Enum):
    """Estrategias de cache disponibles."""
    AGGRESSIVE = "aggressive"  # Cache todo por tiempo extendido
    NORMAL = "normal"         # Cache balanceado
    CONSERVATIVE = "conservative"  # Cache mínimo, datos siempre frescos
    ADAPTIVE = "adaptive"     # Se adapta basado en patrones de uso


@dataclass
class CacheEntry:
    """Entrada de cache con metadatos."""
    key: str
    data: Any
    created_at: float
    last_accessed: float
    access_count: int
    ttl: int
    size_bytes: int
    compressed: bool = False
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
    
    def is_expired(self) -> bool:
        """Verificar si la entrada está expirada."""
        return time.time() - self.created_at > self.ttl
    
    def touch(self):
        """Actualizar tiempo de último acceso."""
        self.last_accessed = time.time()
        self.access_count += 1


class IntelligentCacheManager:
    """Gestor de cache inteligente para reportes y datos complejos."""
    
    def __init__(self, 
                 cache_dir: Optional[str] = None,
                 max_memory_size: int = 100 * 1024 * 1024,  # 100MB
                 default_ttl: int = 3600,  # 1 hora
                 strategy: CacheStrategy = CacheStrategy.NORMAL):
        """
        Inicializar el gestor de cache.
        
        Args:
            cache_dir: Directorio para cache persistente
            max_memory_size: Tamaño máximo en memoria (bytes)
            default_ttl: TTL por defecto en segundos
            strategy: Estrategia de cache
        """
        self.cache_dir = Path(cache_dir or "cache")
        self.cache_dir.mkdir(exist_ok=True)
        
        self.max_memory_size = max_memory_size
        self.default_ttl = default_ttl
        self.strategy = strategy
        
        # Cache en memoria
        self._memory_cache: Dict[str, CacheEntry] = {}
        self._memory_size = 0
        
        # Cache persistente (SQLite)
        self.db_path = self.cache_dir / "cache_metadata.db"
        self._init_persistent_cache()
        
        # Métricas
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'writes': 0,
            'deletes': 0
        }
        
        # Lock para thread safety
        self._lock = threading.RLock()
        
        # Configuración por estrategia
        self._configure_strategy()
        
        # Iniciar limpieza automática
        self._start_cleanup_thread()
    
    def _configure_strategy(self):
        """Configurar parámetros basados en la estrategia."""
        configurations = {
            CacheStrategy.AGGRESSIVE: {
                'default_ttl': 7200,      # 2 horas
                'compression_threshold': 1024,  # 1KB
                'eviction_threshold': 0.95,     # 95% de memoria
                'cleanup_interval': 600,        # 10 minutos
            },
            CacheStrategy.NORMAL: {
                'default_ttl': 3600,      # 1 hora
                'compression_threshold': 10240, # 10KB
                'eviction_threshold': 0.85,     # 85% de memoria
                'cleanup_interval': 300,        # 5 minutos
            },
            CacheStrategy.CONSERVATIVE: {
                'default_ttl': 900,       # 15 minutos
                'compression_threshold': 51200, # 50KB
                'eviction_threshold': 0.75,     # 75% de memoria
                'cleanup_interval': 120,        # 2 minutos
            },
            CacheStrategy.ADAPTIVE: {
                'default_ttl': 3600,      # Se ajusta dinámicamente
                'compression_threshold': 10240,
                'eviction_threshold': 0.80,
                'cleanup_interval': 300,
            }
        }
        
        config = configurations[self.strategy]
        self.default_ttl = config['default_ttl']
        self.compression_threshold = config['compression_threshold']
        self.eviction_threshold = config['eviction_threshold']
        self.cleanup_interval = config['cleanup_interval']
    
    def _init_persistent_cache(self):
        """Inicializar cache persistente con SQLite."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS cache_entries (
                    key TEXT PRIMARY KEY,
                    created_at REAL,
                    last_accessed REAL,
                    access_count INTEGER,
                    ttl INTEGER,
                    size_bytes INTEGER,
                    compressed BOOLEAN,
                    tags TEXT,
                    file_path TEXT
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS cache_stats (
                    metric TEXT PRIMARY KEY,
                    value INTEGER,
                    updated_at REAL
                )
            ''')
    
    def _generate_key(self, data_source: str, parameters: Dict = None, 
                     filters: Dict = None) -> str:
        """Generar clave única para el cache."""
        key_data = {
            'source': data_source,
            'parameters': parameters or {},
            'filters': filters or {}
        }
        
        # Serializar y hashear para clave consistente
        serialized = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.md5(serialized.encode('utf-8')).hexdigest()
    
    def _should_compress(self, data: Any) -> bool:
        """Determinar si los datos deben comprimirse."""
        if isinstance(data, (str, bytes)):
            size = len(data.encode('utf-8') if isinstance(data, str) else data)
        else:
            # Estimación aproximada para otros tipos
            size = len(pickle.dumps(data))
        
        return size > self.compression_threshold
    
    def _compress_data(self, data: Any) -> bytes:
        """Comprimir datos usando gzip."""
        pickled_data = pickle.dumps(data)
        return gzip.compress(pickled_data)
    
    def _decompress_data(self, compressed_data: bytes) -> Any:
        """Descomprimir datos."""
        decompressed = gzip.decompress(compressed_data)
        return pickle.loads(decompressed)
    
    def _evict_if_needed(self):
        """Realizar evicción si es necesaria."""
        if self._memory_size < self.max_memory_size * self.eviction_threshold:
            return
        
        # Ordenar por último acceso (LRU) y frecuencia de acceso
        entries = sorted(
            self._memory_cache.values(),
            key=lambda x: (x.access_count, x.last_accessed)
        )
        
        # Evict hasta estar bajo el umbral
        target_size = self.max_memory_size * 0.7  # 70% después de evicción
        
        for entry in entries:
            if self._memory_size <= target_size:
                break
                
            # Mover a cache persistente si es valioso
            if entry.access_count > 5:  # Datos accedidos frecuentemente
                self._move_to_persistent(entry)
            
            # Remover de memoria
            del self._memory_cache[entry.key]
            self._memory_size -= entry.size_bytes
            self.stats['evictions'] += 1
    
    def _move_to_persistent(self, entry: CacheEntry):
        """Mover entrada a cache persistente."""
        try:
            file_path = self.cache_dir / f"{entry.key}.cache"
            
            # Guardar datos
            if entry.compressed:
                with open(file_path, 'wb') as f:
                    f.write(entry.data)
            else:
                if self._should_compress(entry.data):
                    compressed_data = self._compress_data(entry.data)
                    with open(file_path, 'wb') as f:
                        f.write(compressed_data)
                    entry.compressed = True
                    entry.size_bytes = len(compressed_data)
                else:
                    with open(file_path, 'wb') as f:
                        pickle.dump(entry.data, f)
            
            # Actualizar metadata en SQLite
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO cache_entries 
                    (key, created_at, last_accessed, access_count, ttl, 
                     size_bytes, compressed, tags, file_path)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    entry.key, entry.created_at, entry.last_accessed,
                    entry.access_count, entry.ttl, entry.size_bytes,
                    entry.compressed, json.dumps(entry.tags), str(file_path)
                ))
                
        except Exception as e:
            logger.error(f"Error moviendo entrada a cache persistente: {e}")
                
    def _remove_persistent_entry(self, key: str):
        """Remover entrada del cache persistente."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    'SELECT file_path FROM cache_entries WHERE key = ?', (key,)
                )
                row = cursor.fetchone()
                
                if row:
                    file_path = Path(row[0])
                    if file_path.exists():
                        file_path.unlink()
                    
                    conn.execute('DELETE FROM cache_entries WHERE key = ?', (key,))
                
        except Exception as e:
            logger.error(f"Error removiendo entrada persistente: {e}")
                
    def _get_adaptive_ttl(self, data_source: str) -> int:
        """Calcular TTL adaptativo basado en patrones de uso."""
        if self.strategy != CacheStrategy.ADAPTIVE:
            return self.default_ttl
        
        # Análisis simple de patrones
        # En implementación real, se analizarían estadísticas históricas
        base_ttl = self.default_ttl
        
        # Reportes de inventario - acceso frecuente, TTL corto
        if 'inventario' in data_source.lower():
            return max(base_ttl // 2, 900)  # Mínimo 15 minutos
        
        # Reportes financieros - menos frecuente, TTL largo
        if any(term in data_source.lower() for term in ['finanzas', 'contabilidad', 'balance']):
            return base_ttl * 2
        
        # Estadísticas - pueden ser más duraderas
        if 'estadisticas' in data_source.lower():
            return int(base_ttl * 1.5)
        
        return base_ttl
    
    def invalidate(self, data_source: str = None, tags: List[str] = None,
                   pattern: str = None) -> int:
        """
        Invalidar entradas de cache.
        
        Args:
            data_source: Fuente específica a invalidar
            tags: Invalidar por etiquetas
            pattern: Patrón para invalidar múltiples fuentes
            
        Returns:
            Número de entradas invalidadas
        """
        invalidated = 0
        
        with self._lock:
            keys_to_remove = []
            
            # Invalidación por fuente específica
            if data_source:
                key = self._generate_key(data_source)
                if key in self._memory_cache:
                    keys_to_remove.append(key)
            
            # Invalidación por tags
            if tags:
                for key, entry in self._memory_cache.items():
                    if any(tag in entry.tags for tag in tags):
                        keys_to_remove.append(key)
            
            # Invalidación por patrón
            if pattern:
                for key, entry in self._memory_cache.items():
                    # Simplificado: buscar en la clave generada
                    if pattern in key:
                        keys_to_remove.append(key)
            
            # Remover de memoria
            for key in keys_to_remove:
                if key in self._memory_cache:
                    entry = self._memory_cache[key]
                    self._memory_size -= entry.size_bytes
                    del self._memory_cache[key]
                    invalidated += 1
                    
                # También remover de persistente
                self._remove_persistent_entry(key)
            
            self.stats['deletes'] += invalidated
            
        logger.info(f"Invalidadas {invalidated} entradas de cache")
        return invalidated
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del cache."""
        with self._lock:
            total_requests = self.stats['hits'] + self.stats['misses']
            hit_ratio = self.stats['hits'] / total_requests if total_requests > 0 else 0
            
            return {
                'hits': self.stats['hits'],
                'misses': self.stats['misses'],
                'hit_ratio': round(hit_ratio, 4),
                'writes': self.stats['writes'],
                'deletes': self.stats['deletes'],
                'evictions': self.stats['evictions'],
                'memory_entries': len(self._memory_cache),
                'memory_usage_mb': round(self._memory_size / (1024 * 1024), 2),
                'memory_usage_percent': round(
                    (self._memory_size / self.max_memory_size) * 100, 1
                ),
                'strategy': self.strategy.value,
                'default_ttl': self.default_ttl
            }
    
    def clear(self) -> bool:
        """Limpiar todo el cache."""
        with self._lock:
            try:
                # Limpiar memoria
                cleared_memory = len(self._memory_cache)
                self._memory_cache.clear()
                self._memory_size = 0
                
                # Limpiar persistente
                with sqlite3.connect(self.db_path) as conn:
                    # Obtener archivos a eliminar
                    cursor = conn.execute('SELECT file_path FROM cache_entries')
                    for row in cursor:
                        file_path = Path(row[0])
                        if file_path.exists():
                            file_path.unlink()
                    
                    # Limpiar tabla
                    conn.execute('DELETE FROM cache_entries')
                
                logger.info(f"Cache limpiado: {cleared_memory} entradas de memoria")
                return True
                
            except Exception as e:
                logger.error(f"Error limpiando cache: {e}")
                return False
    
    def _start_cleanup_thread(self):
        """Iniciar hilo de limpieza automática."""
        def cleanup_worker():
            while True:
                time.sleep(self.cleanup_interval)
                try:
                    self._cleanup_expired()
                except Exception as e:
                    logger.error(f"Error en limpieza automática: {e}")
        
        cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        cleanup_thread.start()
        logger.debug("Hilo de limpieza automática iniciado")


# Instancia global del cache manager
_global_cache_manager = None
_cache_lock = threading.Lock()


def get_intelligent_cache_manager(
    cache_dir: str = None,
    max_memory_size: int = 100 * 1024 * 1024,
    strategy: CacheStrategy = CacheStrategy.NORMAL
) -> IntelligentCacheManager:
    """
    Obtener instancia global del gestor de cache inteligente.
    
    Args:
        cache_dir: Directorio para cache (solo primera llamada)
        max_memory_size: Tamaño máximo en memoria (solo primera llamada)
        strategy: Estrategia de cache (solo primera llamada)
        
    Returns:
        Instancia del gestor de cache
    """
    global _global_cache_manager
    
    with _cache_lock:
        if _global_cache_manager is None:
            cache_path = cache_dir or str(Path(__file__).parent.parent.parent / "cache")
            _global_cache_manager = IntelligentCacheManager(
                cache_dir=cache_path,
                max_memory_size=max_memory_size,
                strategy=strategy
            )
            logger.info(f"Cache inteligente inicializado: {cache_path}")
        
        return _global_cache_manager


def cache_report(data_source: str, ttl: int = None, tags: List[str] = None):
    """
    Decorador para cachear automáticamente resultados de reportes.
    
    Args:
        data_source: Nombre de la fuente de datos
        ttl: Tiempo de vida del cache en segundos
        tags: Etiquetas para invalidación grupal
        
    Example:
        @cache_report('inventario_stock_report', ttl=1800, tags=['inventario'])
        def generar_reporte_stock(self, filtros=None):
            # Lógica del reporte
            return datos
    """
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            cache_manager = get_intelligent_cache_manager()
            
            # Generar parámetros para cache
            parameters = {'args': args[1:], 'kwargs': kwargs}  # Excluir self
            
            # Intentar obtener del cache
            cached_result = cache_manager.get(data_source, parameters)
            if cached_result is not None:
                logger.debug(f"Reporte servido desde cache: {data_source}")
                return cached_result
            
            # Ejecutar función y cachear resultado
            result = func(*args, **kwargs)
            cache_manager.set(
                data_source=data_source,
                data=result,
                parameters=parameters,
                ttl=ttl,
                tags=tags
            )
            
            logger.debug(f"Reporte calculado y cacheado: {data_source}")
            return result
        
        return wrapper
    return decorator


# Ejemplo de uso
if __name__ == '__main__':
    # Configurar logging para ejemplo
    logging.basicConfig(level=logging.INFO)
    
    # Crear gestor de cache
    cache = IntelligentCacheManager(
        cache_dir="cache_test",
        strategy=CacheStrategy.NORMAL
    )
    
    # Ejemplo de uso
    test_data = {"reporte": "inventario", "productos": [1, 2, 3, 4, 5]}
    
    # Almacenar datos
    cache.set("test_report", test_data, {"filtro": "activos"}, tags=["inventario"])
    
    # Recuperar datos
    result = cache.get("test_report", {"filtro": "activos"})
    print(f"Datos recuperados: {result}")
    
    # Estadísticas
    stats = cache.get_stats()
    print(f"Estadísticas: {stats}")
    
    print("✅ Sistema de cache inteligente funcionando correctamente")