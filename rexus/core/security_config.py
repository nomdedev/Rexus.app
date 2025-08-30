"""
Configuración de Seguridad Centralizada para Rexus.app

Este archivo contiene todas las configuraciones de seguridad y debe ser:
- Protegido con permisos restrictivos (600)
- Excluido de control de versiones
- Validado al inicio de la aplicación
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass
import json

logger = logging.getLogger(__name__)

@dataclass
class SecurityConfig:
    """Configuración de seguridad de la aplicación."""

    # Base de datos
    database_path: str
    database_timeout: int = 30
    max_connections: int = 10

    # Sesiones y autenticación
    session_timeout: int = 3600  # 1 hora
    max_login_attempts: int = 5
    lockout_duration: int = 900  # 15 minutos

    # Encriptación
    encryption_key: Optional[str] = None
    jwt_secret: Optional[str] = None

    # Logging de seguridad
    security_log_level: str = "WARNING"
    audit_log_path: Optional[str] = None

    # Límites de recursos
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    max_request_size: int = 1024 * 1024     # 1MB

    # Configuración de red
    allowed_hosts: list = None
    trusted_proxies: list = None

    def __post_init__(self):
        if self.allowed_hosts is None:
            self.allowed_hosts = ["localhost", "127.0.0.1"]
        if self.trusted_proxies is None:
            self.trusted_proxies = []


class SecurityConfigManager:
    """
    Gestor de configuración de seguridad.

    Proporciona:
    - Validación de configuraciones
    - Carga desde múltiples fuentes
    - Variables de entorno seguras
    - Configuración por defecto segura
    """

    # Configuraciones críticas que deben estar presentes
    REQUIRED_CONFIGS = [
        'database_path',
        'encryption_key',
        'jwt_secret'
    ]

    # Valores por defecto seguros
    DEFAULTS = {
        'database_timeout': 30,
        'max_connections': 10,
        'session_timeout': 3600,
        'max_login_attempts': 5,
        'lockout_duration': 900,
        'security_log_level': 'WARNING',
        'max_file_size': 10 * 1024 * 1024,
        'max_request_size': 1024 * 1024,
        'allowed_hosts': ['localhost', '127.0.0.1'],
        'trusted_proxies': []
    }

    def __init__(self, config_file: str = None):
        self.config_file = config_file or self._get_default_config_path()
        self._config = None
        self._is_loaded = False

    def _get_default_config_path(self) -> str:
        """Obtiene la ruta por defecto del archivo de configuración."""
        # Buscar en orden de prioridad
        possible_paths = [
            os.getenv('REXUS_CONFIG_FILE'),
            'config/security.json',
            'config/rexus_config.json',
            'rexus_config.json'
        ]

        for path in possible_paths:
            if path and Path(path).exists():
                return path

        # Si no existe ninguno, usar ruta por defecto
        return 'config/security.json'

    def load_config(self) -> SecurityConfig:
        """
        Carga y valida la configuración de seguridad.

        Returns:
            SecurityConfig: Configuración validada

        Raises:
            SecurityConfigError: Si la configuración es inválida
        """
        if self._is_loaded and self._config:
            return self._config

        config_data = self._load_from_sources()
        validated_config = self._validate_config(config_data)

        self._config = SecurityConfig(**validated_config)
        self._is_loaded = True

        logger.info("✅ Configuración de seguridad cargada exitosamente")
        return self._config

    def _load_from_sources(self) -> Dict[str, Any]:
        """
        Carga configuración desde múltiples fuentes:
        1. Variables de entorno (prioridad más alta)
        2. Archivo de configuración JSON
        3. Valores por defecto (prioridad más baja)
        """
        config = self.DEFAULTS.copy()

        # Cargar desde archivo si existe
        if Path(self.config_file).exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    file_config = json.load(f)
                    config.update(file_config)
                logger.info(f"Configuración cargada desde: {self.config_file}")
            except Exception as e:
                logger.warning(f"Error cargando configuración desde archivo: {e}")

        # Sobrescribir con variables de entorno (prioridad más alta)
        env_mappings = {
            'REXUS_DATABASE_PATH': 'database_path',
            'REXUS_DATABASE_TIMEOUT': 'database_timeout',
            'REXUS_ENCRYPTION_KEY': 'encryption_key',
            'REXUS_JWT_SECRET': 'jwt_secret',
            'REXUS_SECURITY_LOG_LEVEL': 'security_log_level',
            'REXUS_AUDIT_LOG_PATH': 'audit_log_path',
            'REXUS_MAX_FILE_SIZE': 'max_file_size',
            'REXUS_ALLOWED_HOSTS': 'allowed_hosts',
        }

        for env_var, config_key in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                # Convertir tipos según sea necesario
                if config_key in ['database_timeout', 'max_connections', 'session_timeout',
                                'max_login_attempts', 'lockout_duration', 'max_file_size', 'max_request_size']:
                    try:
                        config[config_key] = int(env_value)
                    except ValueError:
                        logger.warning(f"Valor inválido para {env_var}: {env_value}")
                elif config_key in ['allowed_hosts', 'trusted_proxies']:
                    try:
                        config[config_key] = json.loads(env_value)
                    except json.JSONDecodeError:
                        config[config_key] = [env_value]
                else:
                    config[config_key] = env_value

                logger.info(f"Configuración {config_key} sobrescrita desde variable de entorno")

        return config

    def _validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida la configuración cargada.

        Args:
            config: Configuración a validar

        Returns:
            Configuración validada

        Raises:
            SecurityConfigError: Si hay errores de validación
        """
        errors = []

        # Validar configuraciones requeridas
        for required in self.REQUIRED_CONFIGS:
            if not config.get(required):
                errors.append(f"Configuración requerida faltante: {required}")

        # Validar tipos y rangos
        if config.get('database_timeout', 0) <= 0:
            errors.append("database_timeout debe ser mayor que 0")

        if config.get('max_connections', 0) <= 0:
            errors.append("max_connections debe ser mayor que 0")

        if config.get('session_timeout', 0) <= 0:
            errors.append("session_timeout debe ser mayor que 0")

        if config.get('max_login_attempts', 0) <= 0:
            errors.append("max_login_attempts debe ser mayor que 0")

        if config.get('encryption_key') and len(config['encryption_key']) < 32:
            errors.append("encryption_key debe tener al menos 32 caracteres")

        if config.get('jwt_secret') and len(config['jwt_secret']) < 32:
            errors.append("jwt_secret debe tener al menos 32 caracteres")

        # Validar rutas de archivo
        if config.get('audit_log_path'):
            audit_path = Path(config['audit_log_path'])
            if not audit_path.parent.exists():
                try:
                    audit_path.parent.mkdir(parents=True, exist_ok=True)
                except Exception as e:
                    errors.append(f"No se puede crear directorio para audit_log_path: {e}")

        if errors:
            error_msg = f"Errores de validación de configuración:\n" + "\n".join(f"  - {e}" for e in errors)
            logger.error(error_msg)
            raise SecurityConfigError(error_msg)

        return config

    def save_config(self, config: SecurityConfig, file_path: str = None) -> None:
        """
        Guarda la configuración actual en un archivo.

        Args:
            config: Configuración a guardar
            file_path: Ruta del archivo (opcional)
        """
        save_path = file_path or self.config_file

        # Crear directorio si no existe
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)

        # Convertir a diccionario
        config_dict = {
            'database_path': config.database_path,
            'database_timeout': config.database_timeout,
            'max_connections': config.max_connections,
            'session_timeout': config.session_timeout,
            'max_login_attempts': config.max_login_attempts,
            'lockout_duration': config.lockout_duration,
            'security_log_level': config.security_log_level,
            'audit_log_path': config.audit_log_path,
            'max_file_size': config.max_file_size,
            'max_request_size': config.max_request_size,
            'allowed_hosts': config.allowed_hosts,
            'trusted_proxies': config.trusted_proxies,
        }

        # No guardar secrets en archivo (deben venir de variables de entorno)
        if config.encryption_key:
            config_dict['encryption_key'] = '***CONFIGURADO_VIA_ENV***'
        if config.jwt_secret:
            config_dict['jwt_secret'] = '***CONFIGURADO_VIA_ENV***'

        try:
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, indent=2, ensure_ascii=False)

            logger.info(f"Configuración guardada en: {save_path}")

        except Exception as e:
            logger.error(f"Error guardando configuración: {e}")
            raise

    def get_config(self) -> SecurityConfig:
        """Obtiene la configuración cargada."""
        if not self._is_loaded:
            return self.load_config()
        return self._config


class SecurityConfigError(Exception):
    """Excepción para errores de configuración de seguridad."""
    pass


# ===== FUNCIONES DE CONVENIENCIA =====

def get_security_config() -> SecurityConfig:
    """
    Obtiene la configuración de seguridad global.

    Returns:
        SecurityConfig: Configuración de seguridad
    """
    return SecurityConfigManager().get_config()


def validate_security_config() -> bool:
    """
    Valida que la configuración de seguridad sea correcta.

    Returns:
        bool: True si es válida
    """
    try:
        SecurityConfigManager().load_config()
        return True
    except SecurityConfigError:
        return False


# ===== CONFIGURACIÓN POR DEFECTO PARA DESARROLLO =====

DEFAULT_DEV_CONFIG = {
    "database_path": "data/dev.db",
    "database_timeout": 30,
    "max_connections": 5,
    "session_timeout": 3600,
    "max_login_attempts": 3,
    "lockout_duration": 300,
    "security_log_level": "INFO",
    "max_file_size": 5 * 1024 * 1024,  # 5MB para desarrollo
    "max_request_size": 512 * 1024,     # 512KB para desarrollo
    "allowed_hosts": ["localhost", "127.0.0.1", "0.0.0.0"],
    "trusted_proxies": []
}
