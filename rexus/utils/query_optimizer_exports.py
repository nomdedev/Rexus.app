"""
Exportaciones de funciones de optimización de consultas para compatibilidad
Este archivo proporciona las funciones que se esperan encontrar en query_optimizer
"""

from functools import wraps
from typing import Any, Optional, Callable
import time

# Importar el optimizador real
# from .query_optimizer import QueryOptimizer, setup_query_optimizer

# Clase simple para compatibilidad
class QueryOptimizer:
    """Clase simple para compatibilidad."""
    def __init__(self, *args, **kwargs):
        self.cache = SimpleCache()
        self.batcher = SimpleBatcher()

class SimpleCache:
    """Cache simple para compatibilidad."""
    def get(self, key):
        return None
    def set(self, key, value, ttl=None):
        pass

class SimpleBatcher:
    """Batcher simple para compatibilidad."""
    def flush_all(self):
        pass

def setup_query_optimizer(*args, **kwargs):
    """Función simple para compatibilidad."""
    return QueryOptimizer()

# Variables globales para el optimizador (debería ser inyectado)
_current_optimizer: Optional[QueryOptimizer] = None

def set_current_optimizer(optimizer: QueryOptimizer):
    """Establece el optimizador actual para uso en decoradores."""
    global _current_optimizer
    _current_optimizer = optimizer

def get_current_optimizer() -> Optional[QueryOptimizer]:
    """Obtiene el optimizador actual."""
    return _current_optimizer

def cached_query(func=None, *, cache_key=None, ttl=None):
    """
    Decorador para cachear resultados de consultas.
    
    Args:
        func: Función a decorar (si se usa sin paréntesis)
        cache_key: Clave de cache personalizada
        ttl: Time to live en segundos
        
    Returns:
        Decorador configurado
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def wrapper(*args, **kwargs):
            optimizer = get_current_optimizer()
            if optimizer:
                # Usar el cache del optimizador
                key = cache_key or f"{f.__name__}_{str(args)}_{str(kwargs)}"
                cached_result = optimizer.cache.get(key)
                if cached_result is not None:
                    return cached_result
                
                # Ejecutar y cachear
                result = f(*args, **kwargs)
                optimizer.cache.set(key, result, ttl)
                return result
            else:
                # Sin optimizador, ejecutar directamente
                return f(*args, **kwargs)
        return wrapper
    
    # Permitir uso con y sin paréntesis
    if func is None:
        return decorator
    else:
        return decorator(func)

def track_performance(func: Callable) -> Callable:
    """
    Decorador para trackear rendimiento de consultas.
    
    Args:
        func: Función a decorar
        
    Returns:
        Función decorada con tracking
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            print(f"[PERFORMANCE] {func.__name__}: {execution_time:.4f}s")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            print(f"[PERFORMANCE] {func.__name__}: {execution_time:.4f}s (ERROR: {e})")
            raise
    return wrapper

def prevent_n_plus_one(func=None, *, batch_key=None):
    """
    Decorador para prevenir problemas N+1.
    
    Args:
        func: Función a decorar (si se usa sin paréntesis)
        batch_key: Clave de batch personalizada
        
    Returns:
        Función decorada con prevención N+1
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def wrapper(*args, **kwargs):
            optimizer = get_current_optimizer()
            if optimizer:
                # Forzar flush de batches pendientes
                optimizer.batcher.flush_all()
            
            return f(*args, **kwargs)
        return wrapper
    
    # Permitir uso con y sin paréntesis
    if func is None:
        return decorator
    else:
        return decorator(func)

def paginated(func=None, *, page_size: int = 50):
    """
    Decorador para paginar resultados.
    
    Args:
        func: Función a decorar (si se usa sin paréntesis)
        page_size: Tamaño de página
        
    Returns:
        Decorador configurado
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def wrapper(*args, **kwargs):
            # Extraer página de kwargs o usar por defecto
            page = kwargs.pop('page', 1)
            limit = kwargs.pop('limit', page_size)
            offset = (page - 1) * limit
            
            # Ejecutar función con paginación
            result = f(*args, **kwargs, limit=limit, offset=offset)
            
            # Agregar metadata de paginación
            if isinstance(result, dict):
                result['pagination'] = {
                    'page': page,
                    'page_size': limit,
                    'offset': offset
                }
            elif isinstance(result, list):
                # Si es una lista, envolver en diccionario
                result = {
                    'data': result,
                    'pagination': {
                        'page': page,
                        'page_size': limit,
                        'offset': offset
                    }
                }
            
            return result
        return wrapper
    
    # Permitir uso con y sin paréntesis
    if func is None:
        return decorator
    else:
        return decorator(func)