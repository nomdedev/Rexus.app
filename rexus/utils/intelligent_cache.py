#!/usr/bin/env python3
"""
Sistema de Cache Inteligente para Rexus
Mejora el rendimiento de consultas frecuentes
"""


import logging
logger = logging.getLogger(__name__)

import time
import hashlib
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
