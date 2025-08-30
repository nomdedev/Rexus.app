#!/usr/bin/env python3
"""
Sistema de Cache Inteligente para Rexus
Mejora el rendimiento de consultas frecuentes
"""

import logging
from typing import Any, Dict, Optional
from functools import wraps
import time
import hashlib
import threading
from collections import OrderedDict

logger = logging.getLogger(__name__)


class IntelligentCache:
    """
    Sistema de cache inteligente con TTL, invalidación automática y estadísticas
    """

    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        """
        Inicializar el cache inteligente

        Args:
            max_size: Tamaño máximo del cache
            default_ttl: TTL por defecto en segundos
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache = OrderedDict()
        self._lock = threading.RLock()
        self._hit_count = 0
        self._miss_count = 0
        self._total_requests = 0

        # Iniciar limpieza automática
        self._start_cleanup_thread()

    def _start_cleanup_thread(self):
        """Iniciar hilo de limpieza automática"""
        def cleanup_worker():
            while True:
                try:
                    time.sleep(60)  # Limpiar cada minuto
                    self._cleanup_expired()
                except Exception as e:
                    logger.error(f"Error en limpieza automática: {str(e)}")

        thread = threading.Thread(target=cleanup_worker, daemon=True)
        thread.start()

    def _generate_key(self, func_name: str, args: tuple, kwargs: dict) -> str:
        """
        Generar clave única para el cache

        Args:
            func_name: Nombre de la función
            args: Argumentos posicionales
            kwargs: Argumentos nombrados

        Returns:
            str: Clave única
        """
        # Convertir args y kwargs a string serializable
        args_str = str(args) if args else ""
        kwargs_str = str(sorted(kwargs.items())) if kwargs else ""

        # Crear hash
        key_data = f"{func_name}:{args_str}:{kwargs_str}"
        return hashlib.sha256(key_data.encode()).hexdigest()

    def get(self, key: str) -> Optional[Any]:
        """
        Obtener valor del cache

        Args:
            key: Clave del cache

        Returns:
            Valor cacheado o None si no existe o expiró
        """
        with self._lock:
            self._total_requests += 1

            if key not in self._cache:
                self._miss_count += 1
                return None

            value, expiry = self._cache[key]

            # Verificar si expiró
            if time.time() > expiry:
                del self._cache[key]
                self._miss_count += 1
                return None

            # Mover al final (LRU)
            self._cache.move_to_end(key)
            self._hit_count += 1

            return value

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Almacenar valor en el cache

        Args:
            key: Clave del cache
            value: Valor a almacenar
            ttl: Tiempo de vida en segundos
        """
        with self._lock:
            if ttl is None:
                ttl = self.default_ttl

            expiry = time.time() + ttl

            # Verificar límite de tamaño
            if len(self._cache) >= self.max_size:
                # Remover el más antiguo (LRU)
                self._cache.popitem(last=False)

            self._cache[key] = (value, expiry)
            self._cache.move_to_end(key)

    def invalidate(self, pattern: Optional[str] = None) -> int:
        """
        Invalidar entradas del cache

        Args:
            pattern: Patrón para invalidar (opcional)

        Returns:
            int: Número de entradas invalidadas
        """
        with self._lock:
            if pattern is None:
                # Invalidar todo
                count = len(self._cache)
                self._cache.clear()
                return count

            # Invalidar por patrón
            keys_to_remove = []
            for key in self._cache.keys():
                if pattern in key:
                    keys_to_remove.append(key)

            for key in keys_to_remove:
                del self._cache[key]

            return len(keys_to_remove)

    def _cleanup_expired(self) -> int:
        """
        Limpiar entradas expiradas

        Returns:
            int: Número de entradas limpiadas
        """
        with self._lock:
            current_time = time.time()
            expired_keys = []

            for key, (value, expiry) in self._cache.items():
                if current_time > expiry:
                    expired_keys.append(key)

            for key in expired_keys:
                del self._cache[key]

            if expired_keys:
                logger.debug(f"Limpiados {len(expired_keys)} elementos expirados del cache")

            return len(expired_keys)

    def get_stats(self) -> Dict[str, Any]:
        """
        Obtener estadísticas del cache

        Returns:
            dict: Estadísticas del cache
        """
        with self._lock:
            total_requests = self._hit_count + self._miss_count
            hit_ratio = (self._hit_count / total_requests) if total_requests > 0 else 0

            return {
                'size': len(self._cache),
                'max_size': self.max_size,
                'hit_count': self._hit_count,
                'miss_count': self._miss_count,
                'total_requests': self._total_requests,
                'hit_ratio': hit_ratio,
                'efficiency': f"{hit_ratio*100:.1f}%"
            }

    def clear(self) -> None:
        """Limpiar todo el cache"""
        with self._lock:
            self._cache.clear()
            self._hit_count = 0
            self._miss_count = 0
            self._total_requests = 0


# Instancia global del cache
cache_instance = IntelligentCache()


def cached_query(ttl: int = 300):
    """
    Decorador para cachear resultados de consultas

    Args:
        ttl: Tiempo de vida en segundos

    Returns:
        Decorador de función
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generar clave de cache
            cache_key = cache_instance._generate_key(func.__name__, args, kwargs)

            # Intentar obtener del cache
            cached_result = cache_instance.get(cache_key)
            if cached_result is not None:
                return cached_result

            # Ejecutar función y cachear resultado
            result = func(*args, **kwargs)
            cache_instance.set(cache_key, result, ttl)

            return result

        return wrapper
    return decorator


def invalidate_cache(pattern: Optional[str] = None) -> int:
    """
    Función utilitaria para invalidar cache

    Args:
        pattern: Patrón para invalidar

    Returns:
        int: Número de entradas invalidadas
    """
    return cache_instance.invalidate(pattern)


def get_cache_stats() -> Dict[str, Any]:
    """
    Función utilitaria para obtener estadísticas del cache

    Returns:
        dict: Estadísticas del cache
    """
    return cache_instance.get_stats()


def clear_cache() -> None:
    """Función utilitaria para limpiar todo el cache"""
    cache_instance.clear()


# Funciones de conveniencia para casos de uso comunes
def cached_database_query(ttl: int = 600):
    """Decorador específico para consultas de base de datos (TTL más largo)"""
    return cached_query(ttl)


def cached_api_call(ttl: int = 300):
    """Decorador específico para llamadas API"""
    return cached_query(ttl)


def cached_computation(ttl: int = 1800):
    """Decorador específico para computaciones pesadas (TTL de 30 minutos)"""
    return cached_query(ttl)
