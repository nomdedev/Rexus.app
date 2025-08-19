#!/usr/bin/env python3
"""
Sistema de Cache Inteligente para Rexus
Mejora el rendimiento de consultas frecuentes
"""

import time
import hashlib
from typing import Any, Optional, Dict
from functools import wraps

class IntelligentCache:
    """Sistema de cache inteligente con TTL y LRU"""

    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: Dict[str, Dict] = {}
        self.access_times: Dict[str, float] = {}

    def _generate_key(self, func_name: str, args: tuple, kwargs: dict) -> str:
        """Genera clave única para la función y parámetros"""
        key_data = f"{func_name}:{str(args)}:{str(sorted(kwargs.items()))}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def _is_expired(self, cache_entry: Dict) -> bool:
        """Verifica si una entrada de cache ha expirado"""
        return time.time() > cache_entry['expires_at']

    def _evict_lru(self):
        """Elimina la entrada menos recientemente usada"""
        if len(self.cache) >= self.max_size:
            lru_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
            del self.cache[lru_key]
            del self.access_times[lru_key]

    def get(self, key: str) -> Optional[Any]:
        """Obtiene valor del cache"""
        if key in self.cache:
            if not self._is_expired(self.cache[key]):
                self.access_times[key] = time.time()
                return self.cache[key]['data']
            else:
                # Entrada expirada, eliminar
                del self.cache[key]
                del self.access_times[key]
        return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Almacena valor en cache"""
        self._evict_lru()

        ttl = ttl or self.default_ttl
        self.cache[key] = {
            'data': value,
            'expires_at': time.time() + ttl,
            'created_at': time.time()
        }
        self.access_times[key] = time.time()

    def invalidate(self, pattern: str = None):
        """Invalida entradas de cache"""
        if pattern:
            keys_to_remove = [k for k in self.cache.keys() if pattern in k]
            for key in keys_to_remove:
                del self.cache[key]
                del self.access_times[key]
        else:
            self.cache.clear()
            self.access_times.clear()

    def get_stats(self) -> Dict:
        """Obtiene estadísticas del cache"""
        total_entries = len(self.cache)
        expired_entries = sum(1 for entry in self.cache.values() if self._is_expired(entry))

        return {
            'total_entries': total_entries,
            'expired_entries': expired_entries,
            'active_entries': total_entries - expired_entries,
            'max_size': self.max_size,
            'hit_ratio': getattr(self,
'_hit_count',
                0) / max(getattr(self,
                '_total_requests',
                1),
                1)
        }

# Instancia global del cache
cache_instance = IntelligentCache()

def cached_query(ttl: int = 300):
    """Decorador para cachear resultados de consultas"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generar clave de cache
            cache_key = cache_instance._generate_key(func.__name__, args, kwargs)

            # Intentar obtener del cache
            cached_result = cache_instance.get(cache_key)
            if cached_result is not None:
                cache_instance._hit_count = getattr(cache_instance, '_hit_count', 0) + 1
                return cached_result

            # Ejecutar función y cachear resultado
            result = func(*args, **kwargs)
            cache_instance.set(cache_key, result, ttl)

            cache_instance._total_requests = getattr(cache_instance, '_total_requests', 0) + 1
            return result
        return wrapper
    return decorator

def invalidate_cache(pattern: str = None):
    """Función utilitaria para invalidar cache"""
    cache_instance.invalidate(pattern)

def get_cache_stats() -> Dict:
    """Función utilitaria para obtener estadísticas del cache"""
    return cache_instance.get_stats()
