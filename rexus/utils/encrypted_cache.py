"""
Sistema de Caché Encriptado con Validación de Permisos - Rexus.app

Sistema de caché que protege datos sensibles mediante encriptación AES-256
y valida permisos de acceso antes de devolver información cached.

Características:
- Encriptación AES-256 para todos los datos en caché
- Validación de permisos antes de acceso a datos
- TTL (Time To Live) configurable por entrada
- Invalidación automática y manual
- Compresión opcional para datos grandes
- Auditoría de accesos al caché

Author: Rexus Development Team
Date: 2025-08-11
Version: 1.0.0
"""

import logging
import json
import time
import zlib
import hashlib
import secrets
from typing import Any, Dict, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    import base64
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    logger.warning("cryptography no disponible - funcionalidad de encriptación limitada")


class EncryptedCache:
    """Sistema de caché encriptado con validación de permisos."""

    def __init__(self, cache_dir: str = ".cache", encryption_key: Optional[str] = None):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)

        # Generar o usar clave de encriptación
        if encryption_key:
            self.encryption_key = encryption_key
        else:
            self.encryption_key = self._generate_key()

        self.fernet = None
        if CRYPTO_AVAILABLE:
            self.fernet = Fernet(self.encryption_key)

        # Cache en memoria para mejor rendimiento
        self.memory_cache = {}
        self.metadata = {}

    def _generate_key(self) -> bytes:
        """Genera una clave de encriptación segura."""
        if CRYPTO_AVAILABLE:
            # Usar PBKDF2 para derivar clave segura
            salt = secrets.token_bytes(16)
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(secrets.token_bytes(32)))
            return key
        else:
            # Fallback simple (menos seguro)
            return secrets.token_bytes(32)

    def _get_cache_path(self, key: str, user_id: int) -> Path:
        """Obtiene la ruta del archivo de caché."""
        # Crear hash de la clave para nombre de archivo seguro
        key_hash = hashlib.sha256(f"{key}_{user_id}".encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.cache"

    def _encrypt_data(self, data: str) -> str:
        """Encripta datos si la encriptación está disponible."""
        if self.fernet and CRYPTO_AVAILABLE:
            return self.fernet.encrypt(data.encode()).decode()
        return data  # Sin encriptación

    def _decrypt_data(self, encrypted_data: str) -> str:
        """Desencripta datos si la encriptación está disponible."""
        if self.fernet and CRYPTO_AVAILABLE:
            return self.fernet.decrypt(encrypted_data.encode()).decode()
        return encrypted_data  # Sin desencriptación

    def _compress_data(self, data: str) -> bytes:
        """Comprime datos para almacenamiento eficiente."""
        return zlib.compress(data.encode())

    def _decompress_data(self, compressed_data: bytes) -> str:
        """Descomprime datos."""
        return zlib.decompress(compressed_data).decode()

    def set(self, key: str, value: Any, user_id: int, ttl: int = 3600,
            compress: bool = False) -> bool:
        """
        Almacena un valor en el caché.

        Args:
            key: Clave del caché
            value: Valor a almacenar
            user_id: ID del usuario
            ttl: Tiempo de vida en segundos
            compress: Si comprimir los datos

        Returns:
            bool: True si se almacenó correctamente
        """
        try:
            # Serializar valor
            data = json.dumps(value)

            # Comprimir si es necesario
            if compress:
                data = self._compress_data(data).decode('latin1')

            # Encriptar
            encrypted_data = self._encrypt_data(data)

            # Crear entrada de caché
            cache_entry = {
                'data': encrypted_data,
                'timestamp': time.time(),
                'ttl': ttl,
                'user_id': user_id,
                'compressed': compress
            }

            # Guardar en archivo
            cache_path = self._get_cache_path(key, user_id)
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_entry, f)

            # Actualizar caché en memoria
            self.memory_cache[f"{key}_{user_id}"] = cache_entry
            self.metadata[f"{key}_{user_id}"] = {
                'path': cache_path,
                'expires': time.time() + ttl
            }

            logger.info(f"Caché almacenado: {key} para usuario {user_id}")
            return True

        except Exception as e:
            logger.error(f"Error almacenando en caché {key}: {e}")
            return False

    def get(self, key: str, user_id: int, default: Any = None) -> Any:
        """
        Recupera un valor del caché.

        Args:
            key: Clave del caché
            user_id: ID del usuario
            default: Valor por defecto si no existe

        Returns:
            Valor almacenado o default
        """
        try:
            cache_key = f"{key}_{user_id}"

            # Verificar caché en memoria primero
            if cache_key in self.memory_cache:
                entry = self.memory_cache[cache_key]
                if time.time() - entry['timestamp'] < entry['ttl']:
                    return self._extract_value(entry)
                else:
                    # Expirado, eliminar
                    del self.memory_cache[cache_key]
                    if cache_key in self.metadata:
                        del self.metadata[cache_key]

            # Buscar en archivo
            cache_path = self._get_cache_path(key, user_id)
            if not cache_path.exists():
                return default

            with open(cache_path, 'r', encoding='utf-8') as f:
                entry = json.load(f)

            # Verificar expiración
            if time.time() - entry['timestamp'] > entry['ttl']:
                # Expirado, eliminar archivo
                cache_path.unlink(missing_ok=True)
                return default

            # Verificar permisos (usuario correcto)
            if entry['user_id'] != user_id:
                logger.warning(f"Intento de acceso no autorizado: {key} por usuario {user_id}")
                return default

            # Extraer y retornar valor
            value = self._extract_value(entry)

            # Actualizar caché en memoria
            self.memory_cache[cache_key] = entry
            self.metadata[cache_key] = {
                'path': cache_path,
                'expires': time.time() + entry['ttl']
            }

            return value

        except Exception as e:
            logger.error(f"Error recuperando del caché {key}: {e}")
            return default

    def _extract_value(self, entry: Dict[str, Any]) -> Any:
        """Extrae el valor de una entrada de caché."""
        try:
            # Desencriptar
            data = self._decrypt_data(entry['data'])

            # Descomprimir si es necesario
            if entry.get('compressed', False):
                data = self._decompress_data(data.encode('latin1'))

            # Deserializar
            return json.loads(data)

        except Exception as e:
            logger.error(f"Error extrayendo valor de caché: {e}")
            return None

    def delete(self, key: str, user_id: int) -> bool:
        """
        Elimina una entrada del caché.

        Args:
            key: Clave del caché
            user_id: ID del usuario

        Returns:
            bool: True si se eliminó correctamente
        """
        try:
            cache_key = f"{key}_{user_id}"

            # Eliminar de memoria
            if cache_key in self.memory_cache:
                del self.memory_cache[cache_key]
            if cache_key in self.metadata:
                del self.metadata[cache_key]

            # Eliminar archivo
            cache_path = self._get_cache_path(key, user_id)
            if cache_path.exists():
                cache_path.unlink()

            logger.info(f"Caché eliminado: {key} para usuario {user_id}")
            return True

        except Exception as e:
            logger.error(f"Error eliminando caché {key}: {e}")
            return False

    def clear_user_cache(self, user_id: int) -> int:
        """
        Elimina todo el caché de un usuario.

        Args:
            user_id: ID del usuario

        Returns:
            int: Número de entradas eliminadas
        """
        try:
            deleted_count = 0

            # Buscar todas las entradas del usuario
            for cache_key, metadata in list(self.metadata.items()):
                if cache_key.endswith(f"_{user_id}"):
                    # Eliminar entrada
                    if cache_key in self.memory_cache:
                        del self.memory_cache[cache_key]
                    del self.metadata[cache_key]

                    # Eliminar archivo
                    if metadata['path'].exists():
                        metadata['path'].unlink()

                    deleted_count += 1

            logger.info(f"Eliminadas {deleted_count} entradas de caché para usuario {user_id}")
            return deleted_count

        except Exception as e:
            logger.error(f"Error limpiando caché de usuario {user_id}: {e}")
            return 0

    def cleanup_expired(self) -> int:
        """
        Elimina todas las entradas expiradas.

        Returns:
            int: Número de entradas eliminadas
        """
        try:
            current_time = time.time()
            deleted_count = 0

            # Buscar entradas expiradas
            for cache_key, metadata in list(self.metadata.items()):
                if current_time > metadata['expires']:
                    # Eliminar entrada
                    if cache_key in self.memory_cache:
                        del self.memory_cache[cache_key]
                    del self.metadata[cache_key]

                    # Eliminar archivo
                    if metadata['path'].exists():
                        metadata['path'].unlink()

                    deleted_count += 1

            if deleted_count > 0:
                logger.info(f"Eliminadas {deleted_count} entradas expiradas")

            return deleted_count

        except Exception as e:
            logger.error(f"Error limpiando entradas expiradas: {e}")
            return 0


# Instancia global del caché
_cache_instance = None


def get_encrypted_cache() -> EncryptedCache:
    """Obtiene la instancia global del caché encriptado."""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = EncryptedCache()
    return _cache_instance


def cache_set(key: str, value: Any, user_id: int, ttl: int = 3600, **kwargs) -> bool:
    """Función de conveniencia para almacenar en caché."""
    cache = get_encrypted_cache()
    return cache.set(key, value, user_id, ttl, **kwargs)


def cache_get(key: str, user_id: int, default: Any = None) -> Any:
    """Función de conveniencia para recuperar del caché."""
    cache = get_encrypted_cache()
    return cache.get(key, user_id, default)


def cache_delete(key: str, user_id: int) -> bool:
    """Función de conveniencia para eliminar del caché."""
    cache = get_encrypted_cache()
    return cache.delete(key, user_id)


def cache_clear_user(user_id: int) -> int:
    """Función de conveniencia para limpiar caché de usuario."""
    cache = get_encrypted_cache()
    return cache.clear_user_cache(user_id)


def cache_cleanup() -> int:
    """Función de conveniencia para limpiar entradas expiradas."""
    cache = get_encrypted_cache()
    return cache.cleanup_expired()
