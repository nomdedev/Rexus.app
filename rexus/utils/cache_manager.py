"""
💾 CacheManager - Sistema de Caching con Redis
=================================================

Sistema de caching empresarial basado en Redis siguiendo
mejores prácticas de:
- Redis Labs Best Practices
- Uber Engineering Cache Architecture
- Instagram Scale strategies

Author: Rexus.app Team
Version: 2.0.0
"""

import json
import logging
from typing import Any, Optional, Dict, List, Type, TypeVar, Callable
from functools import wraps
from datetime import timedelta
import hashlib

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logging.warning("Redis no disponible. Cache será deshabilitado.")

# Type hints para generics
T = TypeVar('T')


class CacheConfig:
    """Configuración centralizada de caché"""

    # TTLs (Time To Live) en segundos
    TTL_CORTO = 60            # 1 minuto - Datos muy volátiles
    TTL_MEDIO = 300          # 5 minutos - Datos cambiantes
    TTL_LARGO = 1800         # 30 minutos - Datos estables
    TTL_MUY_LARGO = 3600     # 1 hora - Datos muy estables

    # Configuraciones específicas por tipo de dato
    CACHE_CONFIG = {
        'estadisticas': TTL_MEDIO,           # 5 minutos
        'productos': TTL_LARGO,             # 30 minutos
        'obras': TTL_MEDIO,                 # 5 minutos
        'usuarios': TTL_CORTO,              # 1 minuto (seguridad)
        'permisos': TTL_CORTO,             # 1 minuto
        'configuracion': TTL_MUY_LARGO,    # 1 hora
        'clientes': TTL_LARGO,             # 30 minutos
        'proveedores': TTL_LARGO,          # 30 minutos
    }

    # Prefijos para organizar keys en Redis
    PREFIX_ESTADISTICAS = "estadisticas"
    PREFIX_PRODUCTOS = "productos"
    PREFIX_OBRAS = "obras"
    PREFIX_USUARIOS = "usuarios"
    PREFIX_PERMISOS = "permisos"

    # Serialización
    ENCODING = 'utf-8'


class CacheKeyBuilder:
    """Constructor de keys de caché consistentes"""

    @staticmethod
    def build(prefix: str, *args, **kwargs) -> str:
        """
        Construye una key de caché con formato consistente.

        Ejemplo:
            build('productos', 'all', page=1)
            -> 'productos:all:page:1'
        """
        parts = [prefix]

        # Agregar argumentos posicionales
        parts.extend(str(arg) for arg in args)

        # Agregar argumentos con nombre
        for key, value in sorted(kwargs.items()):
            parts.append(f"{key}:{value}")

        return ":".join(parts)

    @staticmethod
    def hash_key(key: str) -> str:
        """
        Genera hash de key para evitar keys muy largas.

        Redis limita keys a 512MB, pero keys cortas son más eficientes.
        """
        return hashlib.md5(key.encode(CacheConfig.ENCODING)).hexdigest()


class CacheManager:
    """
    Gestor de caché con Redis.

    Implementa patrón Cache-Aside:
    - La aplicación busca en caché primero
    - Si no está, busca en BD y guarda en caché
    - La aplicación es responsable de invalidación

    Features:
    - Graceful degradation (funciona si Redis cae)
    - TTLs configurables por tipo de dato
    - Serialización JSON automática
    - Métricas de hit/miss
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        """Singleton pattern para CacheManager"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(
        self,
        host: str = 'localhost',
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        enabled: bool = True
    ):
        """
        Inicializa el gestor de caché.

        Args:
            host: Host de Redis
            port: Puerto de Redis
            db: Número de base de datos Redis (0-15)
            password: Password de Redis (si requiere)
            enabled: Si el caché está habilitado
        """
        if self._initialized:
            return

        self.enabled = enabled and REDIS_AVAILABLE
        self.stats = {
            'hits': 0,
            'misses': 0,
            'errors': 0
        }

        if self.enabled:
            try:
                self.redis_client = redis.Redis(
                    host=host,
                    port=port,
                    db=db,
                    password=password,
                    decode_responses=True,  # Retorna strings en lugar de bytes
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    retry_on_timeout=True,
                    health_check_interval=30
                )
                # Verificar conexión
                self.redis_client.ping()
                logging.info("✅ Redis conectado exitosamente")
            except Exception as e:
                logging.error(f"❌ Error conectando a Redis: {e}")
                logging.warning("🔄 Cache deshabilitado, usando BD directamente")
                self.enabled = False
                self.redis_client = None
        else:
            self.redis_client = None
            logging.warning("⚠️  Cache deshabilitado (Redis no disponible)")

        self._initialized = True

    @classmethod
    def get_instance(cls) -> 'CacheManager':
        """Obtiene la instancia singleton del CacheManager"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def get(self, key: str, default: Any = None) -> Optional[Any]:
        """
        Obtiene valor del caché.

        Args:
            key: Key del caché
            default: Valor por defecto si no existe

        Returns:
            Valor del caché o default
        """
        if not self.enabled:
            return default

        try:
            value = self.redis_client.get(key)
            if value is not None:
                self.stats['hits'] += 1
                logging.debug(f"✅ Cache HIT: {key}")
                return json.loads(value)
            else:
                self.stats['misses'] += 1
                logging.debug(f"❌ Cache MISS: {key}")
                return default
        except Exception as e:
            self.stats['errors'] += 1
            logging.error(f"❌ Error obteniendo del caché: {e}")
            return default

    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        tipo_dato: Optional[str] = None
    ) -> bool:
        """
        Guarda valor en el caché.

        Args:
            key: Key del caché
            value: Valor a guardar (debe ser JSON-serializable)
            ttl: Time to live en segundos (opcional)
            tipo_dato: Tipo de dato (usa TTL preconfigurado)

        Returns:
            True si exitoso, False en caso contrario
        """
        if not self.enabled:
            return False

        try:
            # Usar TTL preconfigurado si se especifica tipo_dato
            if ttl is None and tipo_dato:
                ttl = CacheConfig.CACHE_CONFIG.get(tipo_dato, CacheConfig.TTL_MEDIO)

            # Serializar a JSON
            serialized_value = json.dumps(value, ensure_ascii=False)

            # Guardar en Redis
            if ttl:
                self.redis_client.setex(key, ttl, serialized_value)
            else:
                self.redis_client.set(key, serialized_value)

            logging.debug(f"💾 Cache SET: {key} (TTL: {ttl}s)")
            return True

        except Exception as e:
            self.stats['errors'] += 1
            logging.error(f"❌ Error guardando en caché: {e}")
            return False

    def delete(self, key: str) -> bool:
        """
        Elimina key del caché.

        Args:
            key: Key a eliminar

        Returns:
            True si exitoso, False en caso contrario
        """
        if not self.enabled:
            return False

        try:
            self.redis_client.delete(key)
            logging.debug(f"🗑️  Cache DELETE: {key}")
            return True
        except Exception as e:
            logging.error(f"❌ Error eliminando del caché: {e}")
            return False

    def delete_pattern(self, pattern: str) -> int:
        """
        Elimina keys que coinciden con patrón.

        Args:
            pattern: Patrón de Redis (ej: 'productos:*')

        Returns:
            Número de keys eliminadas
        """
        if not self.enabled:
            return 0

        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logging.error(f"❌ Error eliminando patrón {pattern}: {e}")
            return 0

    def invalidate_tipo(self, tipo_dato: str) -> int:
        """
        Invalida todas las keys de un tipo de dato.

        Args:
            tipo_dato: Tipo de dato ('productos', 'obras', etc.)

        Returns:
            Número de keys eliminadas
        """
        prefix = CacheConfig.PREFIX_ESTADISTICAS if tipo_dato == 'estadisticas' else \
                  CacheConfig.PREFIX_PRODUCTOS if tipo_dato == 'productos' else \
                  CacheConfig.PREFIX_OBRAS if tipo_dato == 'obras' else \
                  CacheConfig.PREFIX_USUARIOS

        pattern = f"{prefix}:*"
        return self.delete_pattern(pattern)

    def exists(self, key: str) -> bool:
        """Verifica si una key existe en el caché"""
        if not self.enabled:
            return False

        try:
            return bool(self.redis_client.exists(key))
        except Exception as e:
            logging.error(f"❌ Error verificando existencia: {e}")
            return False

    def clear_all(self) -> bool:
        """Limpia TODO el caché (útil para testing)"""
        if not self.enabled:
            return False

        try:
            self.redis_client.flushdb()
            logging.warning("🧹 Caché limpiado completamente")
            return True
        except Exception as e:
            logging.error(f"❌ Error limpiando caché: {e}")
            return False

    def get_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de uso del caché.

        Returns:
            Dict con estadísticas
        """
        total_requests = self.stats['hits'] + self.stats['misses']
        hit_rate = (self.stats['hits'] / total_requests * 100) if total_requests > 0 else 0

        return {
            'hits': self.stats['hits'],
            'misses': self.stats['misses'],
            'errors': self.stats['errors'],
            'hit_rate': f"{hit_rate:.2f}%",
            'total_requests': total_requests,
            'enabled': self.enabled
        }

    def get_info(self) -> Dict[str, Any]:
        """Obtiene información de Redis"""
        if not self.enabled:
            return {'status': 'disabled'}

        try:
            info = self.redis_client.info()
            return {
                'status': 'connected',
                'used_memory': info.get('used_memory_human', 'N/A'),
                'connected_clients': info.get('connected_clients', 0),
                'total_keys': info.get('db0', {}).get('keys', 0),
                'uptime_seconds': info.get('uptime_in_seconds', 0)
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}


def cache_result(
    ttl: Optional[int] = None,
    tipo_dato: Optional[str] = None,
    key_prefix: Optional[str] = None
):
    """
    Decorador para cachear resultados de funciones.

    Uso:
        @cache_result(tipo_dato='productos')
        def obtener_productos():
            return db.execute("SELECT * FROM productos")

    Args:
        ttl: Time to live en segundos
        tipo_dato: Tipo de dato (usa TTL preconfigurado)
        key_prefix: Prefijo personalizado para la key
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            cache = CacheManager.get_instance()

            # Construir key de caché
            func_name = func.__name__
            module_name = func.__module__

            # Key personalizado o autogenerada
            if key_prefix:
                key = CacheKeyBuilder.build(key_prefix, *args, **kwargs)
            else:
                # Autogenerar key basada en función y args
                key_parts = [module_name, func_name]
                key_parts.extend(str(arg) for arg in args)
                key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
                key = ":".join(key_parts)

            # Intentar obtener del caché
            cached_value = cache.get(key)
            if cached_value is not None:
                return cached_value

            # Si no está en caché, ejecutar función
            result = func(*args, **kwargs)

            # Guardar en caché
            cache.set(key, result, ttl=ttl, tipo_dato=tipo_dato)

            return result

        return wrapper
    return decorator


def cache_invalidate(tipo_dato: str, *args, **kwargs):
    """
    Invalida caché de un tipo de dato.

    Uso:
        cache_invalidate('productos')  # Invalida todos los productos
        cache_invalidate('productos', id=123)  # Invalida producto específico

    Args:
        tipo_dato: Tipo de dato a invalidar
        *args, **kwargs: Argumentos para key específica
    """
    cache = CacheManager.get_instance()

    if args or kwargs:
        # Invalidar key específica
        if tipo_dato == 'productos':
            prefix = CacheConfig.PREFIX_PRODUCTOS
        elif tipo_dato == 'obras':
            prefix = CacheConfig.PREFIX_OBRAS
        elif tipo_dato == 'estadisticas':
            prefix = CacheConfig.PREFIX_ESTADISTICAS
        else:
            prefix = tipo_dato

        key = CacheKeyBuilder.build(prefix, *args, **kwargs)
        cache.delete(key)
    else:
        # Invalidar todas las keys del tipo
        cache.invalidate_tipo(tipo_dato)
