"""
MIT License

Copyright (c) 2024 Rexus.app

Sistema de Caché Inteligente
Proporciona cache en memoria con TTL, compresión y métricas de rendimiento
"""

import time
import json
import pickle
import hashlib
import threading
import gzip
import logging
from typing import Any, Dict, Optional, Tuple, List, Callable
from dataclasses import dataclass
from functools import wraps
import weakref

# Configure secure logging
logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Entrada de caché con metadatos."""
    value: Any
    created_at: float
    ttl: float
    access_count: int = 0
    last_accessed: float = 0
    compressed: bool = False
    size_bytes: int = 0


@dataclass
class CacheStats:
    """Estadísticas del sistema de caché."""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    total_entries: int = 0
    memory_usage_bytes: int = 0
    average_access_time_ms: float = 0.0


class CacheManager:
    """Gestor de caché inteligente con TTL y optimizaciones."""

    def __init__(self, max_size: int = 1000, default_ttl: float = 3600,
                 compression_threshold: int = 1024, enable_metrics: bool = True):
        """
        Inicializa el gestor de caché.

        Args:
            max_size: Número máximo de entradas
            default_ttl: TTL por defecto en segundos
            compression_threshold: Tamaño mínimo para compresión
            enable_metrics: Habilitar métricas de rendimiento
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.compression_threshold = compression_threshold
        self.enable_metrics = enable_metrics

        self._cache: Dict[str, CacheEntry] = {}
        self._lock = threading.RLock()
        self._stats = CacheStats()

        # Configuración de limpieza automática
        self._cleanup_interval = 300  # 5 minutos
        self._last_cleanup = time.time()

        # Registro de objetos débiles para limpieza automática
        self._weak_refs: List[weakref.ref] = []

    def _generate_key(self, key: Any) -> str:
        """Genera clave de caché normalizada."""
        if isinstance(key, str):
            return key
        elif isinstance(key, (tuple, list)):
            return hashlib.md5(str(key).encode()).hexdigest()
        else:
            return hashlib.md5(str(key).encode()).hexdigest()

    def _serialize_value(self, value: Any) -> Tuple[bytes, bool]:
        """Serializa y opcionalmente comprime un valor."""
        # WARNING: This method uses pickle for complex objects.
        # Only use with trusted data to prevent deserialization attacks.
        try:
            # Serializar
            if isinstance(value, (str, int, float, bool, type(None))):
                serialized = json.dumps(value).encode('utf-8')
            else:
                # Log pickle usage for security auditing
                logger.debug(f"Using pickle serialization for type: {type(value).__name__}")
                serialized = pickle.dumps(value, protocol=pickle.HIGHEST_PROTOCOL)
        except Exception as e:
            logger.error(f"Error serializing cache value: {e}")
            raise

        # Comprimir si supera el umbral
        compressed = False
        if len(serialized) > self.compression_threshold:
            try:
                compressed_data = gzip.compress(serialized)
                if len(compressed_data) < len(serialized):
                    serialized = compressed_data
                    compressed = True
            except Exception as e:
                logger.warning(f"Compression failed, using uncompressed data: {e}")

        return serialized, compressed

    def _deserialize_value(self, data: bytes, compressed: bool) -> Any:
        """Deserializa y descomprime un valor."""
        # Descomprimir si es necesario
        if compressed:
            try:
                data = gzip.decompress(data)
            except Exception as e:
                logger.error(f"Error decompressing cache data: {e}")
                raise ValueError("Error descomprimiendo datos del caché")

        # Deserializar
        try:
            # Intentar JSON primero (más rápido para tipos simples)
            return json.loads(data.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError):
            try:
                # Usar pickle para objetos complejos (ONLY for trusted data)
                logger.debug("Using pickle deserialization for cached object")
                return pickle.loads(data)
            except Exception as e:
                logger.error(f"Error deserializing cache data: {e}")
                raise

    def _cleanup_expired(self):
        """Limpia entradas expiradas del caché."""
        current_time = time.time()

        # Solo ejecutar limpieza si ha pasado el intervalo
        if current_time - self._last_cleanup < self._cleanup_interval:
            return

        expired_keys = []

        for key, entry in self._cache.items():
            if current_time - entry.created_at > entry.ttl:
                expired_keys.append(key)

        for key in expired_keys:
            del self._cache[key]
            if self.enable_metrics:
                self._stats.evictions += 1
                self._stats.total_entries -= 1

        self._last_cleanup = current_time

    def _evict_lru(self):
        """Expulsa la entrada menos recientemente usada."""
        if not self._cache:
            return

        # Encontrar entrada con menor last_accessed
        lru_key = min(self._cache.keys(),
                     key=lambda k: self._cache[k].last_accessed)

        del self._cache[lru_key]

        if self.enable_metrics:
            self._stats.evictions += 1
            self._stats.total_entries -= 1

    def put(self, key: Any, value: Any, ttl: Optional[float] = None) -> bool:
        """
        Almacena un valor en el caché.

        Args:
            key: Clave del caché
            value: Valor a almacenar
            ttl: Tiempo de vida en segundos (None para usar default)

        Returns:
            bool: True si se almacenó correctamente
        """
        with self._lock:
            try:
                # Limpiar entradas expiradas
                self._cleanup_expired()

                # Verificar espacio disponible
                if len(self._cache) >= self.max_size:
                    self._evict_lru()

                # Serializar valor
                serialized_data, compressed = self._serialize_value(value)

                # Crear entrada
                cache_key = self._generate_key(key)
                current_time = time.time()
                entry_ttl = ttl if ttl is not None else self.default_ttl

                entry = CacheEntry(
                    value=serialized_data,
                    created_at=current_time,
                    ttl=entry_ttl,
                    compressed=compressed,
                    size_bytes=len(serialized_data),
                    last_accessed=current_time
                )

                self._cache[cache_key] = entry

                if self.enable_metrics:
                    self._stats.total_entries += 1
                    self._stats.memory_usage_bytes += entry.size_bytes

                return True

            except Exception as e:
                logger.error(f"Error storing value in cache: {e}", exc_info=True)
                return False

    def get(self, key: Any, default: Any = None) -> Any:
        """
        Obtiene un valor del caché.

        Args:
            key: Clave del caché
            default: Valor por defecto si no existe

        Returns:
            Valor almacenado o default
        """
        with self._lock:
            start_time = time.time()

            try:
                cache_key = self._generate_key(key)

                if cache_key not in self._cache:
                    if self.enable_metrics:
                        self._stats.misses += 1
                    return default

                entry = self._cache[cache_key]
                current_time = time.time()

                # Verificar expiración
                if current_time - entry.created_at > entry.ttl:
                    del self._cache[cache_key]
                    if self.enable_metrics:
                        self._stats.misses += 1
                        self._stats.evictions += 1
                        self._stats.total_entries -= 1
                    return default

                # Actualizar estadístiques de acceso
                entry.access_count += 1
                entry.last_accessed = current_time

                # Deserializar valor
                value = self._deserialize_value(entry.value, entry.compressed)

                if self.enable_metrics:
                    self._stats.hits += 1
                    access_time = (time.time() - start_time) * 1000
                    # Promedio móvil para tiempo de acceso
                    self._stats.average_access_time_ms = (
                        self._stats.average_access_time_ms * 0.9 + access_time * 0.1
                    )

                return value

            except Exception as e:
                logger.error(f"Error retrieving value from cache: {e}", exc_info=True)
                if self.enable_metrics:
                    self._stats.misses += 1
                return default

    def delete(self, key: Any) -> bool:
        """
        Elimina una entrada del caché.

        Args:
            key: Clave a eliminar

        Returns:
            bool: True si se eliminó
        """
        with self._lock:
            cache_key = self._generate_key(key)

            if cache_key in self._cache:
                entry = self._cache[cache_key]
                del self._cache[cache_key]

                if self.enable_metrics:
                    self._stats.total_entries -= 1
                    self._stats.memory_usage_bytes -= entry.size_bytes

                return True

            return False

    def clear(self):
        """Limpia todo el caché."""
        with self._lock:
            self._cache.clear()
            if self.enable_metrics:
                self._stats = CacheStats()

    def exists(self, key: Any) -> bool:
        """Verifica si una clave existe en el caché."""
        with self._lock:
            cache_key = self._generate_key(key)

            if cache_key not in self._cache:
                return False

            entry = self._cache[cache_key]
            current_time = time.time()

            # Verificar si no ha expirado
            return current_time - entry.created_at <= entry.ttl

    def get_stats(self) -> CacheStats:
        """Obtiene estadísticas del caché."""
        if not self.enable_metrics:
            return CacheStats()

        with self._lock:
            # Calcular hit rate
            total_requests = self._stats.hits + self._stats.misses
            hit_rate = (self._stats.hits / total_requests * 100) if total_requests > 0 else 0

            stats = CacheStats(
                hits=self._stats.hits,
                misses=self._stats.misses,
                evictions=self._stats.evictions,
                total_entries=len(self._cache),
                memory_usage_bytes=self._stats.memory_usage_bytes,
                average_access_time_ms=self._stats.average_access_time_ms
            )

            # Agregar hit rate como atributo dinámico
            stats.hit_rate = hit_rate

            return stats

    def get_cache_info(self) -> Dict[str, Any]:
        """Obtiene información detallada del caché."""
        with self._lock:
            stats = self.get_stats()

            return {
                'configuration': {
                    'max_size': self.max_size,
                    'default_ttl': self.default_ttl,
                    'compression_threshold': self.compression_threshold,
                    'enable_metrics': self.enable_metrics
                },
                'statistics': {
                    'hits': stats.hits,
                    'misses': stats.misses,
                    'hit_rate': getattr(stats, 'hit_rate', 0),
                    'evictions': stats.evictions,
                    'total_entries': stats.total_entries,
                    'memory_usage_mb': stats.memory_usage_bytes / (1024 * 1024),
                    'average_access_time_ms': stats.average_access_time_ms
                },
                'health': {
                    'utilization': (stats.total_entries / self.max_size * 100) if self.max_size > 0 else 0,
                    'performance': 'excellent' if getattr(stats, 'hit_rate', 0) > 80 else
                                 'good' if getattr(stats, 'hit_rate', 0) > 60 else 'needs_attention'
                }
            }


# Instancia global del gestor de caché
_global_cache = CacheManager(
    max_size=1000,
    default_ttl=3600,  # 1 hora
    compression_threshold=1024,
    enable_metrics=True
)


def cached(ttl: Optional[float] = None, key_func: Optional[Callable] = None):
    """
    Decorador para cachear resultados de funciones.

    Args:
        ttl: Tiempo de vida del caché en segundos
        key_func: Función para generar clave personalizada
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generar clave de caché
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__name__}:{args}:{sorted(kwargs.items())}"

            # Intentar obtener del caché
            result = _global_cache.get(cache_key)
            if result is not None:
                return result

            # Ejecutar función y cachear resultado
            result = func(*args, **kwargs)
            _global_cache.put(cache_key, result, ttl)

            return result

        # Agregar método para limpiar caché de la función
        wrapper.clear_cache = lambda: _global_cache.clear()
        wrapper.cache_info = lambda: _global_cache.get_cache_info()

        return wrapper

    return decorator


def get_cache_manager() -> CacheManager:
    """Obtiene la instancia global del gestor de caché."""
    return _global_cache


def cache_put(key: Any, value: Any, ttl: Optional[float] = None) -> bool:
    """Función de conveniencia para almacenar en caché global."""
    return _global_cache.put(key, value, ttl)


def cache_get(key: Any, default: Any = None) -> Any:
    """Función de conveniencia para obtener del caché global."""
    return _global_cache.get(key, default)


def cache_delete(key: Any) -> bool:
    """Función de conveniencia para eliminar del caché global."""
    return _global_cache.delete(key)


def cache_clear():
    """Función de conveniencia para limpiar caché global."""
    _global_cache.clear()


def cache_stats() -> Dict[str, Any]:
    """Función de conveniencia para obtener estadísticas del caché global."""
    return _global_cache.get_cache_info()


# Ejemplos de uso
if __name__ == "__main__":
    # Test básico del sistema de caché
    cache = CacheManager(max_size=100, default_ttl=60)

    # Almacenar valores
    cache.put("user:1", {"name": "Juan", "email": "juan@example.com"})
    cache.put("config:app", {"theme": "dark", "language": "es"})

    # Obtener valores
    user = cache.get("user:1")
    config = cache.get("config:app")

    print(f"Usuario: {user}")
    print(f"Configuración: {config}")

    # Estadísticas
    stats = cache.get_cache_info()
    print(f"Estadísticas del caché: {json.dumps(stats, indent=2)}")

    # Test del decorador
    @cached(ttl=30)
    def expensive_calculation(n):
        """Función costosa para demostrar caché."""
        time.sleep(0.1)  # Simular operación costosa
        return n * n * n

    # Primera llamada (sin caché)
    start = time.time()
    result1 = expensive_calculation(10)
    time1 = time.time() - start

    # Segunda llamada (con caché)
    start = time.time()
    result2 = expensive_calculation(10)
    time2 = time.time() - start

    print(f"Primera llamada: {result1} en {time1:.3f}s")
    print(f"Segunda llamada: {result2} en {time2:.3f}s")
    print(f"Mejora de rendimiento: {time1/time2:.1f}x más rápido")
