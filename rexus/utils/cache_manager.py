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
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass


@dataclass
class CacheEntry:
    """Entrada individual del cache"""
    value: Any
    created_at: float
    ttl: float
    compressed: bool
    size_bytes: int
    last_accessed: float


@dataclass
class CacheStats:
    """Estadísticas del cache"""
    hits: int = 0
    misses: int = 0
    total_entries: int = 0
    memory_usage_bytes: int = 0


class CacheManager:
    """
    Sistema de cache inteligente con TTL, compresión y métricas
    """
    
    def __init__(self, 
                 max_size: int = 1000,
                 default_ttl: float = 3600.0,  # 1 hora por defecto
                 enable_compression: bool = True,
                 enable_metrics: bool = True):
        """
        Inicializa el cache manager
        
        Args:
            max_size: Número máximo de entradas en cache
            default_ttl: TTL por defecto en segundos
            enable_compression: Habilitar compresión para valores grandes
            enable_metrics: Habilitar recolección de métricas
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.enable_compression = enable_compression
        self.enable_metrics = enable_metrics
        
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = threading.RLock()
        self._stats = CacheStats()
        
        # Logger
        self.logger = logging.getLogger(__name__)
    
    def _generate_key(self, key: Any) -> str:
        """Genera una clave hash única para cualquier tipo de input"""
        if isinstance(key, str):
            return hashlib.md5(key.encode()).hexdigest()
        elif isinstance(key, (dict, list, tuple)):
            serialized = json.dumps(key, sort_keys=True, default=str)
            return hashlib.md5(serialized.encode()).hexdigest()
        else:
            return hashlib.md5(str(key).encode()).hexdigest()
    
    def _serialize_value(self, value: Any) -> tuple[bytes, bool]:
        """Serializa y opcionalmente comprime un valor"""
        # Serializar con pickle
        serialized = pickle.dumps(value)
        
        # Comprimir si está habilitado y el valor es grande
        compressed = False
        if self.enable_compression and len(serialized) > 1024:  # > 1KB
            try:
                compressed_data = gzip.compress(serialized)
                if len(compressed_data) < len(serialized):
                    serialized = compressed_data
                    compressed = True
            except Exception as e:
                self.logger.warning(f"Error comprimiendo valor: {e}")
        
        return serialized, compressed
    
    def _deserialize_value(self, data: bytes, compressed: bool) -> Any:
        """Deserializa y descomprime un valor"""
        try:
            if compressed:
                data = gzip.decompress(data)
            return pickle.loads(data)
        except Exception as e:
            self.logger.error(f"Error deserializando valor: {e}")
            raise
    
    def _evict_lru(self) -> None:
        """Elimina las entradas menos utilizadas recientemente"""
        if not self._cache:
            return
        
        # Encontrar la entrada menos accedida
        oldest_key = min(
            self._cache.keys(),
            key=lambda k: self._cache[k].last_accessed
        )
        
        entry = self._cache.pop(oldest_key)
        if self.enable_metrics:
            self._stats.total_entries -= 1
            self._stats.memory_usage_bytes -= entry.size_bytes
    
    def _cleanup_expired(self) -> None:
        """Limpia entradas expiradas"""
        current_time = time.time()
        expired_keys = []
        
        for key, entry in self._cache.items():
            if current_time - entry.created_at > entry.ttl:
                expired_keys.append(key)
        
        for key in expired_keys:
            entry = self._cache.pop(key)
            if self.enable_metrics:
                self._stats.total_entries -= 1
                self._stats.memory_usage_bytes -= entry.size_bytes
    
    def set(self, key: Any, value: Any, ttl: Optional[float] = None) -> bool:
        """
        Almacena un valor en cache
        
        Args:
            key: Clave única para identificar el valor
            value: Valor a almacenar
            ttl: Time To Live en segundos (None para usar default)
            
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
                self.logger.error(f"Error almacenando en cache: {e}")
                return False
    
    def get(self, key: Any, default: Any = None) -> Any:
        """
        Recupera un valor del cache
        
        Args:
            key: Clave del valor a recuperar
            default: Valor por defecto si no existe
            
        Returns:
            Any: El valor almacenado o el valor por defecto
        """
        with self._lock:
            cache_key = self._generate_key(key)
            
            if cache_key not in self._cache:
                if self.enable_metrics:
                    self._stats.misses += 1
                return default
            
            entry = self._cache[cache_key]
            current_time = time.time()
            
            # Verificar si ha expirado
            if current_time - entry.created_at > entry.ttl:
                del self._cache[cache_key]
                if self.enable_metrics:
                    self._stats.misses += 1
                    self._stats.total_entries -= 1
                    self._stats.memory_usage_bytes -= entry.size_bytes
                return default
            
            # Actualizar tiempo de acceso
            entry.last_accessed = current_time
            
            if self.enable_metrics:
                self._stats.hits += 1
            
            try:
                return self._deserialize_value(entry.value, entry.compressed)
            except Exception as e:
                self.logger.error(f"Error recuperando del cache: {e}")
                return default
    
    def delete(self, key: Any) -> bool:
        """
        Elimina una entrada del cache
        
        Args:
            key: Clave a eliminar
            
        Returns:
            bool: True si se eliminó correctamente
        """
        with self._lock:
            cache_key = self._generate_key(key)
            
            if cache_key in self._cache:
                entry = self._cache.pop(cache_key)
                if self.enable_metrics:
                    self._stats.total_entries -= 1
                    self._stats.memory_usage_bytes -= entry.size_bytes
                return True
            
            return False
    
    def clear(self) -> None:
        """Limpia todo el cache"""
        with self._lock:
            self._cache.clear()
            if self.enable_metrics:
                self._stats.total_entries = 0
                self._stats.memory_usage_bytes = 0
    
    def get_stats(self) -> CacheStats:
        """Obtiene estadísticas del cache"""
        with self._lock:
            return CacheStats(
                hits=self._stats.hits,
                misses=self._stats.misses,
                total_entries=self._stats.total_entries,
                memory_usage_bytes=self._stats.memory_usage_bytes
            )
    
    def get_hit_ratio(self) -> float:
        """Calcula el hit ratio del cache"""
        total_requests = self._stats.hits + self._stats.misses
        if total_requests == 0:
            return 0.0
        return self._stats.hits / total_requests


# Instancia global del cache manager
_cache_manager_instance = None
_cache_manager_lock = threading.Lock()


def get_cache_manager() -> CacheManager:
    """
    Obtiene la instancia global del cache manager (singleton)
    
    Returns:
        CacheManager: Instancia del cache manager
    """
    global _cache_manager_instance
    
    if _cache_manager_instance is None:
        with _cache_manager_lock:
            if _cache_manager_instance is None:
                _cache_manager_instance = CacheManager()
    
    return _cache_manager_instance


# Funciones de conveniencia
def cache_set(key: Any, value: Any, ttl: Optional[float] = None) -> bool:
    """Función de conveniencia para set"""
    return get_cache_manager().set(key, value, ttl)


def cache_get(key: Any, default: Any = None) -> Any:
    """Función de conveniencia para get"""
    return get_cache_manager().get(key, default)


def cache_delete(key: Any) -> bool:
    """Función de conveniencia para delete"""
    return get_cache_manager().delete(key)


def cache_clear() -> None:
    """Función de conveniencia para clear"""
    get_cache_manager().clear()