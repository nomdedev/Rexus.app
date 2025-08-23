#!/usr/bin/env python3
"""
Optimizador de Consultas - Rexus.app

Proporciona herramientas para optimizar consultas SQL y eliminar problemas N+1.
Incluye técnicas de batching, prefetch, y caching de consultas.

Fecha: 15/08/2025
Componente: Rendimiento - Optimización de Consultas
"""

import time
import threading
                    self.batcher.flush_all()


# Decorador para optimización automática
def optimize_query(use_cache: bool = True, ttl: Optional[int] = None, 
                  batch_key: Optional[str] = None):
    """
    Decorador para optimización automática de consultas.
    
    Args:
        use_cache: Si usar cache
        ttl: TTL específico para cache
        batch_key: Clave para agrupamiento en batches
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Extraer optimizador del contexto (debe ser inyectado)
            optimizer = getattr(wrapper, '_optimizer', None)
            if not optimizer:
                # Sin optimizador - ejecutar función normal
                return func(*args, **kwargs)
            
            # Generar clave de cache
            cache_key = f"{func.__name__}:{str(args)}:{str(sorted(kwargs.items()))}"
            
            # Intentar obtener del cache
            if use_cache:
                cached_result = optimizer.cache.get(cache_key)
                if cached_result is not None:
                    return cached_result
            
            # Ejecutar función original
            result = func(*args, **kwargs)
            
            # Almacenar en cache
            if use_cache and result is not None:
                optimizer.cache.put(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator


# Función de utilidad para configurar optimizador
def setup_query_optimizer(db_connection, **kwargs) -> QueryOptimizer:
    """
    Configura y retorna un optimizador de consultas.
    
    Args:
        db_connection: Conexión a la base de datos
        **kwargs: Argumentos adicionales para el optimizador
    
    Returns:
        QueryOptimizer: Optimizador configurado
    """
    optimizer = QueryOptimizer(db_connection, **kwargs)
    logger.info("Query optimizer configurado exitosamente")
    return optimizer