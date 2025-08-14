"""
Sistema de Cache Inteligente para Rexus.app
Proporciona cache automático y gestión inteligente de datos frecuentes

Fecha: 13/08/2025
Objetivo: Optimizar rendimiento con cache selectivo por módulo
"""

import time
import functools
import threading
from typing import Any, Dict, Optional, Callable, Tuple
import json
import hashlib


class SmartCache:
    """
    Sistema de cache inteligente con TTL, invalidación automática y métricas.
    """

    def __init__(self, default_ttl: int = 300, max_size: int = 1000):
        """
        Inicializa el sistema de cache.

        Args:
            default_ttl: Tiempo de vida por defecto en segundos
            max_size: Máximo número de entradas en cache
        """
        self.default_ttl = default_ttl
        self.max_size = max_size
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.RLock()
        self._stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'invalidations': 0
        }

    def _generate_key(self, func_name: str, args: Tuple, kwargs: Dict) -> str:
        """Genera clave única para función y parámetros."""
        # Crear string único basado en función y parámetros
        key_data = {
            'func': func_name,
            'args': args,
            'kwargs': sorted(kwargs.items()) if kwargs else []
        }
        key_string = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.md5(key_string.encode()).hexdigest()

    def _is_expired(self, entry: Dict[str, Any]) -> bool:
        """Verifica si una entrada del cache ha expirado."""
        return time.time() > entry['expires_at']

    def _evict_expired(self):
        """Elimina entradas expiradas del cache."""
        current_time = time.time()
        expired_keys = [
            key for key, entry in self._cache.items()
            if current_time > entry['expires_at']
        ]

        for key in expired_keys:
            del self._cache[key]
            self._stats['evictions'] += 1

    def _evict_lru(self):
        """Elimina entradas menos usadas recientemente si se alcanza el límite."""
        if len(self._cache) >= self.max_size:
            # Encontrar entrada menos usada
            lru_key = min(
                self._cache.keys(),
                key=lambda k: self._cache[k]['last_accessed']
            )
            del self._cache[lru_key]
            self._stats['evictions'] += 1

    def get(self, key: str) -> Optional[Any]:
        """
        Obtiene valor del cache si existe y no ha expirado.

        Args:
            key: Clave del cache

        Returns:
            Valor almacenado o None si no existe/expiró
        """
        with self._lock:
            if key in self._cache:
                entry = self._cache[key]

                if not self._is_expired(entry):
                    # Cache hit
                    entry['last_accessed'] = time.time()
                    entry['hit_count'] += 1
                    self._stats['hits'] += 1
                    return entry['value']
                else:
                    # Expirado - eliminar
                    del self._cache[key]
                    self._stats['evictions'] += 1

            # Cache miss
            self._stats['misses'] += 1
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Almacena valor en cache con TTL especificado.

        Args:
            key: Clave del cache
            value: Valor a almacenar
            ttl: Tiempo de vida en segundos (usa default si no se especifica)
        """
        if ttl is None:
            ttl = self.default_ttl

        expires_at = time.time() + ttl

        with self._lock:
            # Limpiar expirados y controlar tamaño
            self._evict_expired()
            self._evict_lru()

            self._cache[key] = {
                'value': value,
                'created_at': time.time(),
                'expires_at': expires_at,
                'last_accessed': time.time(),
                'hit_count': 0,
                'ttl': ttl
            }

    def invalidate(self, pattern: Optional[str] = None) -> int:
        """
        Invalida entradas del cache.

        Args:
            pattern: Patrón para invalidar claves específicas (None = todas)

        Returns:
            Número de entradas invalidadas
        """
        with self._lock:
            if pattern is None:
                # Invalidar todo
                count = len(self._cache)
                self._cache.clear()
            else:
                # Invalidar por patrón
                keys_to_remove = [
                    key for key in self._cache.keys()
                    if pattern in key
                ]
                count = len(keys_to_remove)
                for key in keys_to_remove:
                    del self._cache[key]

            self._stats['invalidations'] += count
            return count

    def get_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del cache."""
        with self._lock:
            total_requests = self._stats['hits'] + self._stats['misses']
            hit_rate = (self._stats['hits'] / total_requests * 100) if total_requests > 0 else 0

            return {
                'hits': self._stats['hits'],
                'misses': self._stats['misses'],
                'hit_rate': round(hit_rate, 2),
                'evictions': self._stats['evictions'],
                'invalidations': self._stats['invalidations'],
                'current_size': len(self._cache),
                'max_size': self.max_size,
                'memory_usage': f"{len(self._cache)}/{self.max_size} ({round(len(self._cache)/self.max_size*100, 1)}%)"
            }

    def clear(self):
        """Limpia completamente el cache."""
        with self._lock:
            self._cache.clear()
            self._stats = {
                'hits': 0,
                'misses': 0,
                'evictions': 0,
                'invalidations': 0
            }


# Instancia global del cache
_global_cache = SmartCache(default_ttl=300, max_size=1000)


def cached_function(ttl: int = 300, cache_key_prefix: str = None):
    """
    Decorador para hacer cache automático de funciones.

    Args:
        ttl: Tiempo de vida del cache en segundos
        cache_key_prefix: Prefijo personalizado para la clave

    Usage:
        @cached_function(ttl=600, cache_key_prefix='estadisticas')
        def obtener_estadisticas_modulo(modulo_id):
            # Lógica costosa aquí
            return estadisticas
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Generar clave de cache
            prefix = cache_key_prefix or func.__name__
            cache_key = f"{prefix}:{_global_cache._generate_key(func.__name__, args, kwargs)}"

            # Intentar obtener del cache
            cached_result = _global_cache.get(cache_key)
            if cached_result is not None:
                print(f"[CACHE HIT] {func.__name__}")
                return cached_result

            # Ejecutar función y guardar resultado
            print(f"[CACHE MISS] {func.__name__}")
            result = func(*args, **kwargs)
            _global_cache.set(cache_key, result, ttl)

            return result

        return wrapper
    return decorator


def invalidate_cache_pattern(pattern: str) -> int:
    """
    Invalida entradas del cache que coinciden con un patrón.

    Args:
        pattern: Patrón a buscar en las claves

    Returns:
        Número de entradas invalidadas
    """
    return _global_cache.invalidate(pattern)


def get_cache_stats() -> Dict[str, Any]:
    """Obtiene estadísticas globales del cache."""
    return _global_cache.get_stats()


def clear_all_cache():
    """Limpia todo el cache global."""
    _global_cache.clear()


# Decoradores específicos para módulos
def cache_estadisticas(ttl: int = 900):
    """Cache para estadísticas (15 minutos por defecto)."""
    return cached_function(ttl=ttl, cache_key_prefix='stats')


def cache_reportes(ttl: int = 1800):
    """Cache para reportes (30 minutos por defecto)."""
    return cached_function(ttl=ttl, cache_key_prefix='reports')


def cache_consultas(ttl: int = 600):
    """Cache para consultas frecuentes (10 minutos por defecto)."""
    return cached_function(ttl=ttl, cache_key_prefix='queries')


def cache_catalogos(ttl: int = 3600):
    """Cache para catálogos (1 hora por defecto)."""
    return cached_function(ttl=ttl, cache_key_prefix='catalogs')


# Funciones de utilidad para módulos
def invalidate_module_cache(module_name: str) -> int:
    """
    Invalida todo el cache relacionado con un módulo específico.

    Args:
        module_name: Nombre del módulo (inventario, obras, etc.)

    Returns:
        Número de entradas invalidadas
    """
    patterns = [module_name, f"stats:{module_name}", f"reports:{module_name}", f"queries:{module_name}"]
    total_invalidated = 0

    for pattern in patterns:
        total_invalidated += invalidate_cache_pattern(pattern)

    print(f"[CACHE] Invalidadas {total_invalidated} entradas para módulo '{module_name}'")
    return total_invalidated


def preload_module_cache(module_name: str, data_loaders: Dict[str, Callable]):
    """
    Precarga cache para un módulo con datos frecuentemente utilizados.

    Args:
        module_name: Nombre del módulo
        data_loaders: Dict con funciones para cargar datos

    Usage:
        preload_module_cache('inventario', {
            'estadisticas': lambda: obtener_estadisticas_inventario(),
            'categorias': lambda: obtener_categorias()
        })
    """
    print(f"[CACHE] Precargando cache para módulo '{module_name}'")

    for cache_key, loader_func in data_loaders.items():
        try:
            full_key = f"{module_name}:{cache_key}"
            data = loader_func()
            _global_cache.set(full_key, data)
            print(f"[CACHE] Precargado: {full_key}")
        except Exception as e:
            print(f"[CACHE ERROR] Error precargando {cache_key}: {e}")


# Ejemplo de uso en módulos
"""
# En el modelo de un módulo:
from rexus.utils.smart_cache import cache_estadisticas, cache_catalogos

class InventarioModel:

    @cache_estadisticas(ttl=900)  # 15 minutos
    def obtener_estadisticas_inventario(self):
        # Consulta costosa aquí
        pass

    @cache_catalogos(ttl=3600)  # 1 hora
    def obtener_categorias(self):
        # Consulta a catálogo que cambia poco
        pass

# Invalidar cache cuando se modifica data:
from rexus.utils.smart_cache import invalidate_module_cache

def crear_producto(self, datos):
    # Crear producto...
    # Invalidar cache relacionado
    invalidate_module_cache('inventario')
"""
