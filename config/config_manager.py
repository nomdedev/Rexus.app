"""
Sistema de Configuración para Entornos de Despliegue - Rexus.app
Maneja configuraciones para desarrollo, testing y producción
"""

import json
import logging
import os
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional


class Environment(Enum):
    """Tipos de entorno disponibles"""

    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


@dataclass
class DatabaseConfig:
    """Configuración de base de datos"""

    host: str
    port: int
    database: str
    username: str
    password: str
    driver: str = "ODBC Driver 17 for SQL Server"
    connection_timeout: int = 30
    command_timeout: int = 30
    pool_size: int = 10
    max_overflow: int = 20

    def get_connection_string(self, mask_password: bool = False) -> str:
        """Genera string de conexión"""
        password = "***" if mask_password else self.password
        return (
            f"Driver={{{self.driver}}};"
            f"Server={self.host},{self.port};"
            f"Database={self.database};"
            f"UID={self.username};"
            f"PWD={password};"
            f"Connection Timeout={self.connection_timeout};"
            f"Command Timeout={self.command_timeout};"
            "Encrypt=yes;"
            "TrustServerCertificate=no;"
        )


@dataclass
class SecurityConfig:
    """Configuración de seguridad"""

    secret_key: str
    jwt_secret: str
    password_salt: str
    max_login_attempts: int = 3
    lockout_duration: int = 900  # 15 minutos
    session_timeout: int = 3600  # 1 hora
    enable_2fa: bool = False
    enable_ssl: bool = True
    cors_origins: list = None

    def __post_init__(self):
        if self.cors_origins is None:
            self.cors_origins = ["http://localhost:3000"]


@dataclass
class LoggingConfig:
    """Configuración de logging"""

    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: str = "logs/rexus.log"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    enable_console: bool = True
    enable_file: bool = True
    enable_rotation: bool = True


@dataclass
class AppConfig:
    """Configuración general de la aplicación"""

    app_name: str = "Rexus.app"
    version: str = "2.0.0"
    debug: bool = False
    host: str = "localhost"
    port: int = 8000
    workers: int = 4
    max_request_size: int = 50 * 1024 * 1024  # 50MB
    static_folder: str = "static"
    upload_folder: str = "uploads"
    temp_folder: str = "temp"
    backup_folder: str = "backups"


class ConfigManager:
    """Gestor de configuración para diferentes entornos"""

    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.current_env = Environment.DEVELOPMENT
        self._config_cache: Dict[Environment, Dict[str, Any]] = {}

        # Crear directorio de configuración si no existe
        self.config_dir.mkdir(exist_ok=True)

        # Inicializar logging
        self._setup_logging()

    def _setup_logging(self):
        """Configura el sistema de logging"""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        self.logger = logging.getLogger(__name__)

    def set_environment(self, env: Environment):
        """Establece el entorno actual"""
        self.current_env = env
        self.logger.info(f"Entorno configurado: {env.value}")

    def get_environment(self) -> Environment:
        """Obtiene el entorno actual"""
        # Verificar variable de entorno
        env_var = os.getenv("REXUS_ENV", self.current_env.value)
        try:
            return Environment(env_var.lower())
        except ValueError:
            self.logger.warning(
                f"Entorno inválido: {env_var}, usando {self.current_env.value}"
            )
            return self.current_env

    def _get_config_file_path(self, env: Environment) -> Path:
        """Obtiene la ruta del archivo de configuración para un entorno"""
        return self.config_dir / f"{env.value}.json"

    def _load_config_file(self, env: Environment) -> Dict[str, Any]:
        """Carga configuración desde archivo"""
        config_file = self._get_config_file_path(env)

        if not config_file.exists():
            self.logger.warning(
                f"Archivo de configuración no encontrado: {config_file}"
            )
            return {}

        try:
            with open(config_file, "r", encoding="utf-8") as f:
                config = json.load(f)
            self.logger.info(f"Configuración cargada: {config_file}")
            return config
        except (json.JSONDecodeError, IOError) as e:
            self.logger.error(f"Error cargando configuración {config_file}: {e}")
            return {}

    def _save_config_file(self, env: Environment, config: Dict[str, Any]):
        """Guarda configuración en archivo"""
        config_file = self._get_config_file_path(env)

        try:
            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Configuración guardada: {config_file}")
        except IOError as e:
            self.logger.error(f"Error guardando configuración {config_file}: {e}")
            raise

    def get_database_config(self, env: Optional[Environment] = None) -> DatabaseConfig:
        """Obtiene configuración de base de datos"""
        if env is None:
            env = self.get_environment()

        config = self._load_config_file(env)
        db_config = config.get("database", {})

        # Valores por defecto según entorno
        defaults = self._get_database_defaults(env)

        # Combinar con valores del archivo
        for key, value in defaults.items():
            if key not in db_config:
                db_config[key] = value

        return DatabaseConfig(**db_config)

    def _get_database_defaults(self, env: Environment) -> Dict[str, Any]:
        """Obtiene valores por defecto de DB según entorno"""
        if env == Environment.PRODUCTION:
            return {
                "host": os.getenv("DB_HOST", "prod-sql-server"),
                "port": int(os.getenv("DB_PORT", "1433")),
                "database": os.getenv("DB_NAME", "rexus_prod"),
                "username": os.getenv("DB_USER", "rexus_user"),
                "password": os.getenv("DB_PASSWORD", ""),
                "connection_timeout": 60,
                "command_timeout": 120,
                "pool_size": 20,
            }
        elif env == Environment.STAGING:
            return {
                "host": os.getenv("DB_HOST", "staging-sql-server"),
                "port": int(os.getenv("DB_PORT", "1433")),
                "database": os.getenv("DB_NAME", "rexus_staging"),
                "username": os.getenv("DB_USER", "rexus_staging"),
                "password": os.getenv("DB_PASSWORD", ""),
                "connection_timeout": 30,
                "pool_size": 10,
            }
        elif env == Environment.TESTING:
            return {
                "host": "localhost",
                "port": 1433,
                "database": "rexus_test",
                "username": "test_user",
                "password": "test_password",
                "connection_timeout": 15,
                "pool_size": 5,
            }
        else:  # DEVELOPMENT
            return {
                "host": "localhost",
                "port": 1433,
                "database": "rexus_dev",
                "username": "dev_user",
                "password": "dev_password",
                "connection_timeout": 30,
                "pool_size": 5,
            }

    def get_security_config(self, env: Optional[Environment] = None) -> SecurityConfig:
        """Obtiene configuración de seguridad"""
        if env is None:
            env = self.get_environment()

        config = self._load_config_file(env)
        security_config = config.get("security", {})

        # Valores por defecto según entorno
        defaults = self._get_security_defaults(env)

        # Combinar con valores del archivo
        for key, value in defaults.items():
            if key not in security_config:
                security_config[key] = value

        return SecurityConfig(**security_config)

    def _get_security_defaults(self, env: Environment) -> Dict[str, Any]:
        """Obtiene valores por defecto de seguridad según entorno"""
        if env == Environment.PRODUCTION:
            return {
                "secret_key": os.getenv("SECRET_KEY", ""),
                "jwt_secret": os.getenv("JWT_SECRET", ""),
                "password_salt": os.getenv("PASSWORD_SALT", ""),
                "max_login_attempts": 3,
                "lockout_duration": 1800,  # 30 minutos en producción
                "session_timeout": 3600,  # 1 hora
                "enable_2fa": True,
                "enable_ssl": True,
                "cors_origins": ["https://rexus.company.com"],
            }
        elif env == Environment.STAGING:
            return {
                "secret_key": os.getenv("SECRET_KEY", "staging-secret-key"),
                "jwt_secret": os.getenv("JWT_SECRET", "staging-jwt-secret"),
                "password_salt": os.getenv("PASSWORD_SALT", "staging-salt"),
                "max_login_attempts": 5,
                "lockout_duration": 900,  # 15 minutos
                "session_timeout": 7200,  # 2 horas
                "enable_2fa": True,
                "enable_ssl": True,
                "cors_origins": ["https://staging.rexus.company.com"],
            }
        elif env == Environment.TESTING:
            return {
                "secret_key": "test-secret-key",
                "jwt_secret": "test-jwt-secret",
                "password_salt": "test-salt",
                "max_login_attempts": 10,
                "lockout_duration": 300,  # 5 minutos
                "session_timeout": 3600,
                "enable_2fa": False,
                "enable_ssl": False,
                "cors_origins": ["http://localhost:3000", "http://localhost:8080"],
            }
        else:  # DEVELOPMENT
            return {
                "secret_key": "dev-secret-key-not-for-production",
                "jwt_secret": "dev-jwt-secret",
                "password_salt": "dev-salt",
                "max_login_attempts": 10,
                "lockout_duration": 60,  # 1 minuto
                "session_timeout": 86400,  # 24 horas
                "enable_2fa": False,
                "enable_ssl": False,
                "cors_origins": ["*"],
            }

    def get_logging_config(self, env: Optional[Environment] = None) -> LoggingConfig:
        """Obtiene configuración de logging"""
        if env is None:
            env = self.get_environment()

        config = self._load_config_file(env)
        logging_config = config.get("logging", {})

        # Valores por defecto según entorno
        defaults = self._get_logging_defaults(env)

        # Combinar con valores del archivo
        for key, value in defaults.items():
            if key not in logging_config:
                logging_config[key] = value

        return LoggingConfig(**logging_config)

    def _get_logging_defaults(self, env: Environment) -> Dict[str, Any]:
        """Obtiene valores por defecto de logging según entorno"""
        if env == Environment.PRODUCTION:
            return {
                "level": "WARNING",
                "file_path": "/var/log/rexus/rexus.log",
                "max_file_size": 50 * 1024 * 1024,  # 50MB
                "backup_count": 10,
                "enable_console": False,
                "enable_file": True,
                "enable_rotation": True,
            }
        elif env == Environment.STAGING:
            return {
                "level": "INFO",
                "file_path": "/var/log/rexus/staging.log",
                "max_file_size": 20 * 1024 * 1024,  # 20MB
                "backup_count": 5,
                "enable_console": True,
                "enable_file": True,
                "enable_rotation": True,
            }
        elif env == Environment.TESTING:
            return {
                "level": "DEBUG",
                "file_path": "logs/test.log",
                "max_file_size": 5 * 1024 * 1024,  # 5MB
                "backup_count": 3,
                "enable_console": True,
                "enable_file": True,
                "enable_rotation": False,
            }
        else:  # DEVELOPMENT
            return {
                "level": "DEBUG",
                "file_path": "logs/development.log",
                "max_file_size": 10 * 1024 * 1024,  # 10MB
                "backup_count": 3,
                "enable_console": True,
                "enable_file": True,
                "enable_rotation": True,
            }

    def get_app_config(self, env: Optional[Environment] = None) -> AppConfig:
        """Obtiene configuración de la aplicación"""
        if env is None:
            env = self.get_environment()

        config = self._load_config_file(env)
        app_config = config.get("app", {})

        # Valores por defecto según entorno
        defaults = self._get_app_defaults(env)

        # Combinar con valores del archivo
        for key, value in defaults.items():
            if key not in app_config:
                app_config[key] = value

        return AppConfig(**app_config)

    def _get_app_defaults(self, env: Environment) -> Dict[str, Any]:
        """Obtiene valores por defecto de la app según entorno"""
        if env == Environment.PRODUCTION:
            return {
                "debug": False,
                "host": "0.0.0.0",
                "port": int(os.getenv("PORT", "80")),
                "workers": int(os.getenv("WORKERS", "8")),
                "max_request_size": 100 * 1024 * 1024,  # 100MB
                "static_folder": "/var/www/rexus/static",
                "upload_folder": "/var/data/rexus/uploads",
                "temp_folder": "/tmp/rexus",
                "backup_folder": "/var/backups/rexus",
            }
        elif env == Environment.STAGING:
            return {
                "debug": False,
                "host": "0.0.0.0",
                "port": int(os.getenv("PORT", "8080")),
                "workers": 4,
                "max_request_size": 50 * 1024 * 1024,  # 50MB
                "static_folder": "static",
                "upload_folder": "uploads",
                "temp_folder": "temp",
                "backup_folder": "backups",
            }
        elif env == Environment.TESTING:
            return {
                "debug": True,
                "host": "localhost",
                "port": 8001,
                "workers": 1,
                "max_request_size": 10 * 1024 * 1024,  # 10MB
                "static_folder": "test_static",
                "upload_folder": "test_uploads",
                "temp_folder": "test_temp",
                "backup_folder": "test_backups",
            }
        else:  # DEVELOPMENT
            return {
                "debug": True,
                "host": "localhost",
                "port": 8000,
                "workers": 1,
                "max_request_size": 50 * 1024 * 1024,  # 50MB
                "static_folder": "static",
                "upload_folder": "uploads",
                "temp_folder": "temp",
                "backup_folder": "backups",
            }

    def generate_default_configs(self):
        """Genera archivos de configuración por defecto para todos los entornos"""
        for env in Environment:
            self.logger.info(f"Generando configuración por defecto para {env.value}")

            config = {
                "environment": env.value,
                "database": self._get_database_defaults(env),
                "security": self._get_security_defaults(env),
                "logging": self._get_logging_defaults(env),
                "app": self._get_app_defaults(env),
            }

            self._save_config_file(env, config)

    def validate_config(self, env: Optional[Environment] = None) -> Dict[str, Any]:
        """Valida la configuración actual"""
        if env is None:
            env = self.get_environment()

        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "environment": env.value,
        }

        try:
            # Validar configuración de DB
            db_config = self.get_database_config(env)
            if not db_config.host:
                validation_result["errors"].append("DB host no configurado")
            if not db_config.username:
                validation_result["errors"].append("DB username no configurado")
            if not db_config.password and env == Environment.PRODUCTION:
                validation_result["errors"].append(
                    "DB password no configurado en producción"
                )

            # Validar configuración de seguridad
            security_config = self.get_security_config(env)
            if not security_config.secret_key and env in [
                Environment.PRODUCTION,
                Environment.STAGING,
            ]:
                validation_result["errors"].append("Secret key no configurado")
            if env == Environment.PRODUCTION and not security_config.enable_ssl:
                validation_result["warnings"].append("SSL deshabilitado en producción")

            # Validar configuración de app
            app_config = self.get_app_config(env)
            if app_config.debug and env == Environment.PRODUCTION:
                validation_result["errors"].append(
                    "Debug mode habilitado en producción"
                )

            # Validar directorios
            for folder_attr in [
                "static_folder",
                "upload_folder",
                "temp_folder",
                "backup_folder",
            ]:
                folder_path = getattr(app_config, folder_attr)
                if not os.path.exists(folder_path):
                    validation_result["warnings"].append(
                        f"Directorio no existe: {folder_path}"
                    )

        except Exception as e:
            validation_result["errors"].append(
                f"Error validando configuración: {str(e)}"
            )

        validation_result["valid"] = len(validation_result["errors"]) == 0

        return validation_result

    def get_all_configs(self, env: Optional[Environment] = None) -> Dict[str, Any]:
        """Obtiene todas las configuraciones para un entorno"""
        if env is None:
            env = self.get_environment()

        return {
            "environment": env.value,
            "database": self.get_database_config(env),
            "security": self.get_security_config(env),
            "logging": self.get_logging_config(env),
            "app": self.get_app_config(env),
        }


# Instancia global del gestor de configuración
config_manager = ConfigManager()


def get_config() -> ConfigManager:
    """Obtiene el gestor de configuración global"""
    return config_manager


if __name__ == "__main__":
    # Demo del sistema de configuración
    manager = ConfigManager()

    # Generar configuraciones por defecto
    print("🔧 Generando configuraciones por defecto...")
    manager.generate_default_configs()

    # Probar configuraciones para cada entorno
    for env in Environment:
        print(f"\n📋 Configuración para {env.value.upper()}:")

        manager.set_environment(env)

        # Validar configuración
        validation = manager.validate_config()
        if validation["valid"]:
            print("✅ Configuración válida")
        else:
            print("❌ Errores en configuración:")
            for error in validation["errors"]:
                print(f"   - {error}")

        if validation["warnings"]:
            print("⚠️  Advertencias:")
            for warning in validation["warnings"]:
                print(f"   - {warning}")

        # Mostrar configuración de DB (con contraseña enmascarada)
        db_config = manager.get_database_config()
        print(f"🗄️  DB: {db_config.get_connection_string(mask_password=True)}")

        # Mostrar configuración de app
        app_config = manager.get_app_config()
        print(f"🚀 App: {app_config.host}:{app_config.port} (debug={app_config.debug})")
