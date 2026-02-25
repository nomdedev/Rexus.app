"""
Sistema de Secrets Management - Rexus.app
Gestiona secrets de forma segura usando Vault o cifrado local

Características:
- Soporte para HashiCorp Vault
- Fallback a cifrado local con AES-256-GCM
- Rotación automática de secrets
- Caching con TTL
- Auditoría de accesos a secrets
"""

import os
import json
import logging
import hashlib
from typing import Dict, Optional, Any, List
from datetime import datetime, timedelta
from pathlib import Path
import base64

# Cifrado
try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
    from cryptography.hazmat.backends import default_backend
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    logging.error("cryptography no disponible; backend local cifrado queda bloqueado por seguridad")

logger = logging.getLogger(__name__)


class SecretNotFoundError(Exception):
    """Excepción cuando un secret no se encuentra."""
    pass


class SecretRotationError(Exception):
    """Excepción cuando falla la rotación de un secret."""
    pass


class SecretsBackend:
    """Backend abstracto para almacenamiento de secrets."""

    def get_secret(self, key: str) -> Optional[str]:
        """Obtiene un secret por su clave."""
        raise NotImplementedError

    def set_secret(self, key: str, value: str, metadata: Dict = None) -> bool:
        """Guarda un secret."""
        raise NotImplementedError

    def delete_secret(self, key: str) -> bool:
        """Elimina un secret."""
        raise NotImplementedError

    def list_secrets(self, prefix: str = "") -> List[str]:
        """Lista secrets con un prefijo dado."""
        raise NotImplementedError

    def rotate_secret(self, key: str, new_value: str) -> bool:
        """Rota un secret."""
        raise NotImplementedError


class LocalEncryptedBackend(SecretsBackend):
    """
    Backend de cifrado local usando AES-256-GCM.

    Los secrets se almacenan cifrados en disco. La clave maestra
    se deriva de una passphrase del entorno o archivo.
    """

    def __init__(self, storage_path: str = None, master_key: str = None):
        """
        Inicializa el backend local cifrado.

        Args:
            storage_path: Ruta al archivo de almacenamiento cifrado
            master_key: Clave maestra (o variable de entorno SECRETS_MASTER_KEY)
        """
        self.storage_path = storage_path or os.getenv(
            "SECRETS_STORAGE_PATH",
            "./config/secrets.enc"
        )
        self.master_key = master_key or os.getenv("SECRETS_MASTER_KEY")

        if not CRYPTO_AVAILABLE:
            raise RuntimeError(
                "cryptography es obligatorio para LocalEncryptedBackend. "
                "Instalar dependencia o configurar Vault backend."
            )

        if not self.master_key:
            logger.warning("No se proporcionó SECRETS_MASTER_KEY. Generando una temporal.")
            self.master_key = os.urandom(32).hex()

        # Crear directorio si no existe
        Path(self.storage_path).parent.mkdir(parents=True, exist_ok=True)

        # Cargar o inicializar storage
        self._storage = self._load_storage()

        # Registro de accesos para auditoría
        self._access_log: List[Dict] = []

    def _derive_key(self, salt: bytes) -> bytes:
        """Deriva una clave de cifrado desde la master key."""
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        return kdf.derive(self.master_key.encode())

    def _encrypt(self, data: str) -> Dict[str, str]:
        """Cifra datos usando AES-256-GCM."""
        # Generar salt y nonce
        salt = os.urandom(16)
        nonce = os.urandom(12)

        # Derivar clave
        key = self._derive_key(salt)

        # Cifrar
        aesgcm = AESGCM(key)
        ciphertext = aesgcm.encrypt(nonce, data.encode(), None)

        return {
            "salt": base64.b64encode(salt).decode(),
            "nonce": base64.b64encode(nonce).decode(),
            "data": base64.b64encode(ciphertext).decode(),
            "method": "aes-256-gcm"
        }

    def _decrypt(self, encrypted_data: Dict) -> str:
        """Descifra datos."""
        method = encrypted_data.get("method")

        if method == "base64":
            if os.getenv("REXUS_ALLOW_LEGACY_BASE64_DECRYPT", "false").lower() != "true":
                raise RuntimeError(
                    "Se detectó secret en formato base64 legacy no seguro. "
                    "Habilite temporalmente REXUS_ALLOW_LEGACY_BASE64_DECRYPT=true para migrar y re-cifrar."
                )
            logger.warning("Descifrado legacy base64 habilitado temporalmente para migración")
            return base64.b64decode(encrypted_data["data"]).decode()

        if method == "aes-256-gcm":
            if not CRYPTO_AVAILABLE:
                raise RuntimeError("cryptography module required for aes-256-gcm")

            salt = base64.b64decode(encrypted_data["salt"])
            nonce = base64.b64decode(encrypted_data["nonce"])
            ciphertext = base64.b64decode(encrypted_data["data"])

            key = self._derive_key(salt)
            aesgcm = AESGCM(key)

            plaintext = aesgcm.decrypt(nonce, ciphertext, None)
            return plaintext.decode()

        raise ValueError(f"Unknown encryption method: {method}")

    def _load_storage(self) -> Dict:
        """Carga el almacenamiento desde disco."""
        if not os.path.exists(self.storage_path):
            return {"version": 1, "secrets": {}, "metadata": {}}

        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)

            # Descifrar cada secret
            decrypted = {}
            for key, value in data.get("secrets", {}).items():
                try:
                    decrypted[key] = self._decrypt(value)
                except Exception as e:
                    logger.error(f"Error decrypting secret {key}: {e}")
                    decrypted[key] = None

            return {
                "version": data.get("version", 1),
                "secrets": decrypted,
                "metadata": data.get("metadata", {})
            }
        except Exception as e:
            logger.error(f"Error loading storage: {e}")
            return {"version": 1, "secrets": {}, "metadata": {}}

    def _save_storage(self):
        """Guarda el almacenamiento a disco."""
        # Cifrar cada secret
        encrypted_secrets = {}
        for key, value in self._storage.get("secrets", {}).items():
            try:
                encrypted_secrets[key] = self._encrypt(value)
            except Exception as e:
                logger.error(f"Error encrypting secret {key}: {e}")

        data = {
            "version": self._storage.get("version", 1),
            "secrets": encrypted_secrets,
            "metadata": self._storage.get("metadata", {})
        }

        with open(self.storage_path, 'w') as f:
            json.dump(data, f)

    def get_secret(self, key: str) -> Optional[str]:
        """Obtiene un secret por su clave."""
        # Registrar acceso
        self._access_log.append({
            "key": key,
            "action": "get",
            "timestamp": datetime.now().isoformat()
        })

        value = self._storage.get("secrets", {}).get(key)

        if value is None:
            raise SecretNotFoundError(f"Secret '{key}' not found")

        return value

    def set_secret(self, key: str, value: str, metadata: Dict = None) -> bool:
        """Guarda un secret."""
        if "secrets" not in self._storage:
            self._storage["secrets"] = {}
        if "metadata" not in self._storage:
            self._storage["metadata"] = {}

        self._storage["secrets"][key] = value

        if metadata:
            self._storage["metadata"][key] = metadata
            self._storage["metadata"][key]["created_at"] = datetime.now().isoformat()
            self._storage["metadata"][key]["rotated_at"] = datetime.now().isoformat()

        self._save_storage()

        # Registrar acceso
        self._access_log.append({
            "key": key,
            "action": "set",
            "timestamp": datetime.now().isoformat()
        })

        return True

    def delete_secret(self, key: str) -> bool:
        """Elimina un secret."""
        if key in self._storage.get("secrets", {}):
            del self._storage["secrets"][key]
            if key in self._storage.get("metadata", {}):
                del self._storage["metadata"][key]

            self._save_storage()

            # Registrar acceso
            self._access_log.append({
                "key": key,
                "action": "delete",
                "timestamp": datetime.now().isoformat()
            })

            return True
        return False

    def list_secrets(self, prefix: str = "") -> List[str]:
        """Lista secrets con un prefijo dado."""
        secrets = self._storage.get("secrets", {}).keys()
        return [s for s in secrets if s.startswith(prefix)]

    def rotate_secret(self, key: str, new_value: str) -> bool:
        """Rota un secret."""
        if key not in self._storage.get("secrets", {}):
            raise SecretNotFoundError(f"Secret '{key}' not found")

        # Guardar valor anterior en historial
        if "metadata" not in self._storage:
            self._storage["metadata"] = {}
        if "rotation_history" not in self._storage["metadata"]:
            self._storage["metadata"]["rotation_history"] = {}

        if key not in self._storage["metadata"]["rotation_history"]:
            self._storage["metadata"]["rotation_history"][key] = []

        self._storage["metadata"]["rotation_history"][key].append({
            "rotated_at": datetime.now().isoformat(),
            "previous_value_hash": hashlib.sha256(
                self._storage["secrets"][key].encode()
            ).hexdigest()
        })

        # Actualizar valor
        self._storage["secrets"][key] = new_value
        self._storage["metadata"][key]["rotated_at"] = datetime.now().isoformat()

        self._save_storage()

        # Registrar acceso
        self._access_log.append({
            "key": key,
            "action": "rotate",
            "timestamp": datetime.now().isoformat()
        })

        return True

    def get_access_log(self) -> List[Dict]:
        """Obtiene el log de accesos."""
        return self._access_log.copy()


class VaultBackend(SecretsBackend):
    """
    Backend para HashiCorp Vault.

    Requiere:
    - VAULT_ADDR: URL del servidor Vault
    - VAULT_TOKEN: Token de autenticación
    """

    def __init__(self, vault_addr: str = None, token: str = None, mount: str = "secret"):
        """
        Inicializa el backend de Vault.

        Args:
            vault_addr: URL del servidor Vault
            token: Token de autenticación
            mount: Mount point de KV engine (default: secret)
        """
        self.vault_addr = vault_addr or os.getenv("VAULT_ADDR", "http://localhost:8200")
        self.token = token or os.getenv("VAULT_TOKEN")
        self.mount = mount

        try:
            import requests
            self._session = requests.Session()
            if self.token:
                self._session.headers.update({"X-Vault-Token": self.token})
            self._available = True
        except ImportError:
            logger.warning("requests no disponible, Vault backend no funcional")
            self._available = False

    def _vault_request(self, method: str, path: str, data: Dict = None) -> Dict:
        """Realiza una petición a Vault."""
        if not self._available:
            raise RuntimeError("Vault backend not available")

        url = f"{self.vault_addr}/v1/{self.mount}/data/{path}"

        if method == "GET":
            response = self._session.get(url, timeout=10)
        elif method == "POST":
            response = self._session.post(url, json={"data": data}, timeout=10)
        elif method == "DELETE":
            response = self._session.delete(url, timeout=10)
        else:
            raise ValueError(f"Unknown method: {method}")

        if response.status_code == 404:
            raise SecretNotFoundError(f"Secret not found: {path}")
        elif response.status_code >= 400:
            raise RuntimeError(f"Vault error: {response.status_code} - {response.text}")

        if response.status_code == 204:  # No content
            return {}

        return response.json()

    def get_secret(self, key: str) -> Optional[str]:
        """Obtiene un secret desde Vault."""
        try:
            result = self._vault_request("GET", key)
            return result.get("data", {}).get("data", {}).get("value")
        except SecretNotFoundError:
            return None
        except Exception as e:
            logger.error(f"Error getting secret from Vault: {e}")
            return None

    def set_secret(self, key: str, value: str, metadata: Dict = None) -> bool:
        """Guarda un secret en Vault."""
        try:
            data = {"value": value}
            if metadata:
                data.update(metadata)

            self._vault_request("POST", key, data)
            return True
        except Exception as e:
            logger.error(f"Error setting secret in Vault: {e}")
            return False

    def delete_secret(self, key: str) -> bool:
        """Elimina un secret de Vault."""
        try:
            self._vault_request("DELETE", key)
            return True
        except Exception as e:
            logger.error(f"Error deleting secret from Vault: {e}")
            return False

    def list_secrets(self, prefix: str = "") -> List[str]:
        """Lista secrets en Vault."""
        try:
            if prefix:
                path = f"{prefix}?list=true"
            else:
                path = "?list=true"

            result = self._vault_request("GET", path)
            return result.get("data", {}).get("keys", [])
        except Exception as e:
            logger.error(f"Error listing secrets from Vault: {e}")
            return []

    def rotate_secret(self, key: str, new_value: str) -> bool:
        """Rota un secret en Vault."""
        # En Vault, la rotación es simplemente actualizar el valor
        # Para rotación automática, se puede usar Vault's rotation features
        return self.set_secret(key, new_value)


class SecretsManager:
    """
    Gestor centralizado de secrets.

    Provee una interfaz unificada para gestionar secrets
    independientemente del backend usado.
    """

    def __init__(self, backend: SecretsBackend = None):
        """
        Inicializa el gestor de secrets.

        Args:
            backend: Backend a usar (auto-detecta si no se proporciona)
        """
        self.backend = backend or self._detect_backend()

        # Cache con TTL
        self._cache: Dict[str, tuple] = {}  # key -> (value, expiry)
        self._cache_ttl = int(os.getenv("SECRETS_CACHE_TTL", "300"))  # 5 minutos default

    def _detect_backend(self) -> SecretsBackend:
        """Detecta el backend a usar basado en configuración."""
        # Preferir Vault si está configurado
        if os.getenv("VAULT_ADDR") and os.getenv("VAULT_TOKEN"):
            logger.info("Using Vault backend for secrets")
            return VaultBackend()

        # Fallback a backend local cifrado
        logger.info("Using local encrypted backend for secrets")
        return LocalEncryptedBackend()

    def get_secret(self, key: str, use_cache: bool = True) -> Optional[str]:
        """
        Obtiene un secret.

        Args:
            key: Clave del secret
            use_cache: Si usar caché

        Returns:
            Valor del secret o None si no existe
        """
        # Verificar caché
        if use_cache and key in self._cache:
            value, expiry = self._cache[key]
            if datetime.now() < expiry:
                return value
            else:
                del self._cache[key]

        # Obtener del backend
        try:
            value = self.backend.get_secret(key)

            if value is not None and use_cache:
                # Guardar en caché
                expiry = datetime.now() + timedelta(seconds=self._cache_ttl)
                self._cache[key] = (value, expiry)

            return value
        except SecretNotFoundError:
            return None

    def set_secret(self, key: str, value: str, metadata: Dict = None) -> bool:
        """
        Guarda un secret.

        Args:
            key: Clave del secret
            value: Valor del secret
            metadata: Metadatos adicionales

        Returns:
            True si se guardó exitosamente
        """
        # Invalidar caché
        if key in self._cache:
            del self._cache[key]

        return self.backend.set_secret(key, value, metadata)

    def delete_secret(self, key: str) -> bool:
        """
        Elimina un secret.

        Args:
            key: Clave del secret

        Returns:
            True si se eliminó exitosamente
        """
        # Invalidar caché
        if key in self._cache:
            del self._cache[key]

        return self.backend.delete_secret(key)

    def list_secrets(self, prefix: str = "") -> List[str]:
        """Lista secrets con un prefijo dado."""
        return self.backend.list_secrets(prefix)

    def rotate_secret(self, key: str, new_value: str = None) -> bool:
        """
        Rota un secret.

        Args:
            key: Clave del secret
            new_value: Nuevo valor (genera uno si es None)

        Returns:
            True si se rotó exitosamente
        """
        # Generar nuevo valor si no se proporciona
        if new_value is None:
            new_value = self._generate_secret_value(key)

        # Invalidar caché
        if key in self._cache:
            del self._cache[key]

        return self.backend.rotate_secret(key, new_value)

    def _generate_secret_value(self, key: str) -> str:
        """Genera un valor para un secret basado en su tipo."""
        import secrets

        if "password" in key.lower() or "pwd" in key.lower():
            # Generar contraseña segura
            import string
            alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
            return ''.join(secrets.choice(alphabet) for _ in range(24))

        elif "key" in key.lower() or "token" in key.lower():
            # Generar token seguro
            return secrets.token_urlsafe(32)

        else:
            # Generar string aleatorio
            return secrets.token_hex(32)

    def invalidate_cache(self, key: str = None):
        """
        Invalida la caché.

        Args:
            key: Clave específica o todas si es None
        """
        if key:
            if key in self._cache:
                del self._cache[key]
        else:
            self._cache.clear()

    def check_rotation_needed(self, key: str, max_age_days: int = 90) -> bool:
        """
        Verifica si un secret necesita rotación.

        Args:
            key: Clave del secret
            max_age_days: Edad máxima en días

        Returns:
            True si necesita rotación
        """
        if isinstance(self.backend, LocalEncryptedBackend):
            metadata = self.backend._storage.get("metadata", {}).get(key, {})

            if "rotated_at" in metadata:
                rotated_at = datetime.fromisoformat(metadata["rotated_at"])
                age = (datetime.now() - rotated_at).days
                return age >= max_age_days

            return True  # Sin fecha de rotación = necesita rotación

        # Para Vault, verificar si hay metadata
        return False


# Instancia global
_secrets_manager_instance = None


def get_secrets_manager() -> SecretsManager:
    """Obtiene la instancia singleton del SecretsManager."""
    global _secrets_manager_instance
    if _secrets_manager_instance is None:
        _secrets_manager_instance = SecretsManager()
    return _secrets_manager_instance


# Funciones de conveniencia para migración desde .env
def migrate_env_to_secrets(prefix: str = "REXUS") -> Dict[str, bool]:
    """
    Migra variables de entorno a secrets.

    Args:
        prefix: Prefijo de variables a migrar

    Returns:
        Diccionario con resultados de migración
    """
    manager = get_secrets_manager()
    results = {}

    for key, value in os.environ.items():
        if key.startswith(prefix):
            secret_key = key.lower().replace("_", "/")
            results[key] = manager.set_secret(secret_key, value)

    # Migración explícita de claves críticas legacy
    critical_mapping = {
        "DB_PASSWORD": "database/db_password",
        "SECRET_KEY": "security/secret_key",
        "JWT_SECRET_KEY": "security/jwt_secret_key",
        "ENCRYPTION_KEY": "security/encryption_key",
    }
    for env_key, secret_key in critical_mapping.items():
        env_value = os.getenv(env_key)
        if env_value:
            results[env_key] = manager.set_secret(secret_key, env_value)

    return results


# Función para cargar secrets como variables de entorno
def load_secrets_to_env(prefix: str = "rexus") -> int:
    """
    Carga secrets al entorno.

    Args:
        prefix: Prefijo para las variables de entorno

    Returns:
        Cantidad de secrets cargados
    """
    manager = get_secrets_manager()
    secrets = manager.list_secrets(prefix)
    loaded = 0

    for secret_key in secrets:
        value = manager.get_secret(secret_key)
        if value:
            # Convertir: database/db_server -> DATABASE_DB_SERVER
            env_key = secret_key.upper().replace("/", "_")
            os.environ[env_key] = value
            loaded += 1

    return loaded
