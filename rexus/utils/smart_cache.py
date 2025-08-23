"""
Sistema de Cache Inteligente para Rexus.app
Proporciona cache automático y gestión inteligente de datos frecuentes

Fecha: 13/08/2025
Objetivo: Optimizar rendimiento con cache selectivo por módulo
"""

import time
import functools
import logging
import threading
            

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
                logger.debug(f"[CACHE HIT] {func.__name__}")
                return cached_result

            # Ejecutar función y guardar resultado
            logger.debug(f"[CACHE MISS] {func.__name__}")
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

    logger.info(f"[CACHE] Invalidadas {total_invalidated} entradas para módulo '{module_name}'")
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
    logger.info(f"[CACHE] Precargando cache para módulo '{module_name}'")

    for cache_key, loader_func in data_loaders.items():
        try:
            full_key = f"{module_name}:{cache_key}"
            data = loader_func()
            _global_cache.set(full_key, data)
            logger.info(f"[CACHE] Precargado: {full_key}")
        except Exception as e:
            logger.info(f"[CACHE ERROR] Error precargando {cache_key}: {e}")


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
