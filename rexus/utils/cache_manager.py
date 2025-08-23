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

    logger.info(f"Usuario: {user}")
    logger.info(f"Configuración: {config}")

    # Estadísticas
    stats = cache.get_cache_info()
    logger.info(f"Estadísticas del caché: {json.dumps(stats, indent=2)}")

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

    logger.info(f"Primera llamada: {result1} en {time1:.3f}s")
    logger.info(f"Segunda llamada: {result2} en {time2:.3f}s")
    logger.info(f"Mejora de rendimiento: {time1/time2:.1f}x más rápido")
