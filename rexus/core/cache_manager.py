"""
Sistema de Cache Distribuido para Rexus
Versión: 2.0.0 - Enterprise Ready
"""

import json
import pickle
import time
import hashlib
from typing import Any, Optional, Dict, List, Callable
from functools import wraps
from dataclasses import dataclass, asdict
import threading

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

try:
    import diskcache
    DISKCACHE_AVAILABLE = True
except ImportError:
    DISKCACHE_AVAILABLE = False

from .config import CACHE_CONFIG, PROJECT_ROOT
from .logger import get_logger

logger = get_logger("cache")

@dataclass
class CacheStats:
    """Estadísticas del cache"""
    hits: int = 0
    misses: int = 0
    sets: int = 0
    deletes: int = 0
    errors: int = 0

    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return (self.hits / total * 100) if total > 0 else 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class CacheBackend:
    """Interfaz base para backends de cache"""

    def get(self, key: str) -> Optional[Any]:
        raise NotImplementedError

    def set(self,
key: str,
        value: Any,
        timeout: Optional[int] = None) -> bool:
        raise NotImplementedError

    def delete(self, key: str) -> bool:
        raise NotImplementedError

    def clear(self) -> bool:
        raise NotImplementedError

    def exists(self, key: str) -> bool:
        raise NotImplementedError

    def get_stats(self) -> Dict[str, Any]:
        raise NotImplementedError

class MemoryCache(CacheBackend):
    """Cache en memoria local (fallback)"""

    def __init__(self):
        self._cache = {}
        self._expiry = {}
        self._lock = threading.RLock()
        self._stats = CacheStats()

    def _is_expired(self, key: str) -> bool:
        if key not in self._expiry:
            return False
        return time.time() > self._expiry[key]

    def _cleanup_expired(self):
        """Limpiar entradas expiradas"""
        current_time = time.time()
        expired_keys = [
            key for key, expiry_time in self._expiry.items()
            if current_time > expiry_time
        ]

        for key in expired_keys:
            self._cache.pop(key, None)
            self._expiry.pop(key, None)

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            self._cleanup_expired()

            if key in self._cache and not self._is_expired(key):
                self._stats.hits += 1
                return self._cache[key]
            else:
                self._stats.misses += 1
                return None

    def set(self,
key: str,
        value: Any,
        timeout: Optional[int] = None) -> bool:
        try:
            with self._lock:
                self._cache[key] = value

                if timeout:
                    self._expiry[key] = time.time() + timeout
                elif key in self._expiry:
                    del self._expiry[key]

                self._stats.sets += 1
                return True
        except Exception:
            self._stats.errors += 1
            return False

    def delete(self, key: str) -> bool:
        try:
            with self._lock:
                deleted = key in self._cache
                self._cache.pop(key, None)
                self._expiry.pop(key, None)

                if deleted:
                    self._stats.deletes += 1

                return deleted
        except Exception:
            self._stats.errors += 1
            return False

    def clear(self) -> bool:
        try:
            with self._lock:
                self._cache.clear()
                self._expiry.clear()
                return True
        except Exception:
            self._stats.errors += 1
            return False

    def exists(self, key: str) -> bool:
        with self._lock:
            return key in self._cache and not self._is_expired(key)

    def get_stats(self) -> Dict[str, Any]:
        with self._lock:
            return {
                **self._stats.to_dict(),
                "backend": "memory",
                "cache_size": len(self._cache),
                "expired_entries": len([k for k in self._expiry.keys() if self._is_expired(k)])
            }

class RedisCache(CacheBackend):
    """Cache con Redis"""

    def __init__(self, redis_url: str):
        if not REDIS_AVAILABLE:
            raise ImportError("redis no está disponible")

        self.redis_client = redis.from_url(redis_url, decode_responses=False)
        self._stats = CacheStats()

        # Verificar conexión
        try:
            self.redis_client.ping()
            logger.info("Conexión a Redis establecida", extra={"redis_url": redis_url})
        except redis.ConnectionError as e:
            logger.error("Error conectando a Redis", extra={"error": str(e)})
            raise

    def _serialize(self, value: Any) -> bytes:
        """Serializar valor para almacenamiento"""
        try:
            return pickle.dumps(value)
        except Exception:
            # Fallback a JSON para objetos simples
            return json.dumps(value).encode('utf-8')

    def _deserialize(self, data: bytes) -> Any:
        """Deserializar valor desde almacenamiento"""
        try:
            return pickle.loads(data)
        except Exception:
            # Fallback a JSON
            try:
                return json.loads(data.decode('utf-8'))
            except Exception:
                return data.decode('utf-8')

    def get(self, key: str) -> Optional[Any]:
        try:
            data = self.redis_client.get(key)
            if data is not None:
                self._stats.hits += 1
                return self._deserialize(data)
            else:
                self._stats.misses += 1
                return None
        except Exception as e:
            self._stats.errors += 1
            logger.error("Error obteniendo del cache Redis", extra={
                "key": key,
                "error": str(e)
            })
            return None

    def set(self,
key: str,
        value: Any,
        timeout: Optional[int] = None) -> bool:
        try:
            data = self._serialize(value)
            result = self.redis_client.set(key, data, ex=timeout)

            if result:
                self._stats.sets += 1
            else:
                self._stats.errors += 1

            return bool(result)
        except Exception as e:
            self._stats.errors += 1
            logger.error("Error guardando en cache Redis", extra={
                "key": key,
                "error": str(e)
            })
            return False

    def delete(self, key: str) -> bool:
        try:
            result = self.redis_client.delete(key)

            if result > 0:
                self._stats.deletes += 1
                return True
            return False
        except Exception as e:
            self._stats.errors += 1
            logger.error("Error eliminando del cache Redis", extra={
                "key": key,
                "error": str(e)
            })
            return False

    def clear(self) -> bool:
        try:
            self.redis_client.flushdb()
            return True
        except Exception as e:
            self._stats.errors += 1
            logger.error("Error limpiando cache Redis", extra={
                "error": str(e)
            })
            return False

    def exists(self, key: str) -> bool:
        try:
            return bool(self.redis_client.exists(key))
        except Exception as e:
            self._stats.errors += 1
            logger.error("Error verificando existencia en Redis", extra={
                "key": key,
                "error": str(e)
            })
            return False

    def get_stats(self) -> Dict[str, Any]:
        try:
            redis_info = self.redis_client.info()
            return {
                **self._stats.to_dict(),
                "backend": "redis",
                "redis_memory_used": redis_info.get("used_memory_human", "unknown"),
                "redis_connected_clients": redis_info.get("connected_clients", 0),
                "redis_keyspace_hits": redis_info.get("keyspace_hits", 0),
                "redis_keyspace_misses": redis_info.get("keyspace_misses", 0)
            }
        except Exception:
            return {
                **self._stats.to_dict(),
                "backend": "redis",
                "error": "Could not retrieve Redis stats"
            }

class DiskCache(CacheBackend):
    """Cache en disco usando diskcache"""

    def __init__(self, cache_dir: str):
        if not DISKCACHE_AVAILABLE:
            raise ImportError("diskcache no está disponible")

        self.cache = diskcache.Cache(cache_dir)
        self._stats = CacheStats()

        logger.info("Cache en disco inicializado", extra={"cache_dir": cache_dir})

    def get(self, key: str) -> Optional[Any]:
        try:
            value = self.cache.get(key)
            if value is not None:
                self._stats.hits += 1
            else:
                self._stats.misses += 1
            return value
        except Exception as e:
            self._stats.errors += 1
            logger.error("Error obteniendo del cache en disco", extra={
                "key": key,
                "error": str(e)
            })
            return None

    def set(self,
key: str,
        value: Any,
        timeout: Optional[int] = None) -> bool:
        try:
            expire_time = None
            if timeout:
                expire_time = time.time() + timeout

            result = self.cache.set(key, value, expire=expire_time)

            if result:
                self._stats.sets += 1
            else:
                self._stats.errors += 1

            return result
        except Exception as e:
            self._stats.errors += 1
            logger.error("Error guardando en cache en disco", extra={
                "key": key,
                "error": str(e)
            })
            return False

    def delete(self, key: str) -> bool:
        try:
            result = self.cache.delete(key)
            if result:
                self._stats.deletes += 1
            return result
        except Exception as e:
            self._stats.errors += 1
            logger.error("Error eliminando del cache en disco", extra={
                "key": key,
                "error": str(e)
            })
            return False

    def clear(self) -> bool:
        try:
            self.cache.clear()
            return True
        except Exception as e:
            self._stats.errors += 1
            logger.error("Error limpiando cache en disco", extra={
                "error": str(e)
            })
            return False

    def exists(self, key: str) -> bool:
        try:
            return key in self.cache
        except Exception as e:
            self._stats.errors += 1
            return False

    def get_stats(self) -> Dict[str, Any]:
        try:
            return {
                **self._stats.to_dict(),
                "backend": "disk",
                "cache_size": len(self.cache),
                "disk_usage_mb": round(sum(
                    f.stat().st_size for f in self.cache.directory.rglob('*')
                    if f.is_file()
                ) / 1024 / 1024, 2)
            }
        except Exception:
            return {
                **self._stats.to_dict(),
                "backend": "disk",
                "error": "Could not retrieve disk cache stats"
            }

class CacheManager:
    """
    Manager principal del sistema de cache
    Soporta múltiples backends y failover automático
    """

    def __init__(self):
        self.logger = get_logger("cache_manager")
        self.config = CACHE_CONFIG  # Agregar referencia a configuración
        self.default_timeout = CACHE_CONFIG.get("default_timeout", 3600)

        # Inicializar backend
        self.backend = self._initialize_backend()

        self.logger.info("CacheManager inicializado", extra={
            "backend": type(self.backend).__name__,
            "default_timeout": self.default_timeout
        })

    def _initialize_backend(self) -> CacheBackend:
        """Inicializar backend de cache con fallback"""
        cache_type = CACHE_CONFIG.get("type", "memory").lower()

        # Intentar Redis primero si está configurado
        if cache_type == "redis" and REDIS_AVAILABLE:
            try:
                redis_url = CACHE_CONFIG.get("redis_url", "redis://localhost:6379/0")
                return RedisCache(redis_url)
            except Exception as e:
                self.logger.warning("Error inicializando Redis, usando fallback", extra={
                    "error": str(e)
                })

        # Intentar DiskCache
        if cache_type == "disk" and DISKCACHE_AVAILABLE:
            try:
                cache_dir = PROJECT_ROOT / "cache"
                cache_dir.mkdir(exist_ok=True)
                return DiskCache(str(cache_dir))
            except Exception as e:
                self.logger.warning("Error inicializando DiskCache, usando memoria", extra={
                    "error": str(e)
                })

        # Fallback a memoria
        fallback_warnings = self.config.get("enable_fallback_warnings", False)
        if fallback_warnings:
            self.logger.info("Usando cache en memoria como fallback")
        return MemoryCache()

    def get(self, key: str, default: Any = None) -> Any:
        """Obtener valor del cache"""
        try:
            value = self.backend.get(key)
            return value if value is not None else default
        except Exception as e:
            self.logger.error("Error obteniendo del cache", extra={
                "key": key,
                "error": str(e)
            })
            return default

    def set(self,
key: str,
        value: Any,
        timeout: Optional[int] = None) -> bool:
        """Guardar valor en cache"""
        if timeout is None:
            timeout = self.default_timeout

        return self.backend.set(key, value, timeout)

    def delete(self, key: str) -> bool:
        """Eliminar valor del cache"""
        return self.backend.delete(key)

    def clear(self) -> bool:
        """Limpiar todo el cache"""
        return self.backend.clear()

    def exists(self, key: str) -> bool:
        """Verificar si existe una clave"""
        return self.backend.exists(key)

    def get_or_set(self,
key: str,
        func: Callable[[],
        Any],
        timeout: Optional[int] = None) -> Any:
        """Obtener del cache o ejecutar función y cachear resultado"""
        value = self.get(key)

        if value is not None:
            return value

        # Ejecutar función y cachear resultado
        try:
            result = func()
            self.set(key, result, timeout)
            return result
        except Exception as e:
            self.logger.error("Error ejecutando función para cache", extra={
                "key": key,
                "error": str(e)
            })
            raise

    def mget(self, keys: List[str]) -> Dict[str, Any]:
        """Obtener múltiples valores"""
        result = {}
        for key in keys:
            result[key] = self.get(key)
        return result

    def mset(self,
mapping: Dict[str,
        Any],
        timeout: Optional[int] = None) -> bool:
        """Establecer múltiples valores"""
        success = True
        for key, value in mapping.items():
            if not self.set(key, value, timeout):
                success = False
        return success

    def get_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del cache"""
        return self.backend.get_stats()

    def generate_key(self, *parts) -> str:
        """Generar clave de cache consistente"""
        key_string = ":".join(str(part) for part in parts)
        return hashlib.md5(key_string.encode('utf-8')).hexdigest()

# Decorador para cache automático
def cached(timeout: Optional[int] = None, key_prefix: str = "func"):
    """
    Decorador para cachear automáticamente resultados de funciones

    Args:
        timeout: Tiempo de expiración en segundos
        key_prefix: Prefijo para la clave de cache
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generar clave única para esta llamada
            cache_key_parts = [
                key_prefix,
                func.__module__,
                func.__name__,
                str(hash(str(args) + str(sorted(kwargs.items()))))
            ]
            cache_key = cache_manager.generate_key(*cache_key_parts)

            # Intentar obtener del cache
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result

            # Ejecutar función y cachear resultado
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result, timeout)

            return result

        # Agregar método para limpiar cache de esta función
        def clear_cache():
            # Esto es una implementación simplificada
            # En producción, podrías usar patrones de clave más sofisticados
            pass

        wrapper.clear_cache = clear_cache
        return wrapper

    return decorator

def cache_query_result(query_hash: str, timeout: Optional[int] = None):
    """Decorador específico para cachear resultados de queries de BD"""
    if timeout is None:
        timeout = CACHE_CONFIG.get("query_cache_timeout", 1800)

    return cached(timeout=timeout, key_prefix=f"query:{query_hash}")

# Instancia global del cache manager
cache_manager = CacheManager()

# Funciones de conveniencia
def get_cache(key: str, default: Any = None) -> Any:
    """Función de conveniencia para obtener del cache"""
    return cache_manager.get(key, default)

def set_cache(key: str, value: Any, timeout: Optional[int] = None) -> bool:
    """Función de conveniencia para guardar en cache"""
    return cache_manager.set(key, value, timeout)

def delete_cache(key: str) -> bool:
    """Función de conveniencia para eliminar del cache"""
    return cache_manager.delete(key)

def clear_all_cache() -> bool:
    """Función de conveniencia para limpiar todo el cache"""
    return cache_manager.clear()

def get_cache_stats() -> Dict[str, Any]:
    """Función de conveniencia para obtener estadísticas"""
    return cache_manager.get_stats()
