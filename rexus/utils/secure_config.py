"""
Configuración Segura Unificada - Rexus.app
Gestiona toda la configuración de la aplicación con validación y secrets management

Características:
- Validación de configuración al inicio
- Integración con SecretsManager
- Separación de ambientes (development, staging, production)
- Variables de entorno con fallback a secrets
- Type hints y validación de tipos
"""

import os
import logging
from typing import Optional, List
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


def _is_development_mode() -> bool:
    return os.getenv("ENVIRONMENT", "development").lower() == "development"


def _allow_env_secret_fallback() -> bool:
    if _is_development_mode():
        return True
    return os.getenv("REXUS_ALLOW_ENV_SECRETS_FALLBACK", "false").lower() == "true"


def _get_secret_value(secret_key: str, env_var: str) -> str:
    """Obtiene valor sensible priorizando SecretsManager."""
    try:
        from rexus.core.secrets_manager import get_secrets_manager

        secrets = get_secrets_manager()
        value = secrets.get_secret(secret_key)
        if value:
            return value
    except Exception as exc:
        logger.debug(f"SecretsManager no disponible para {secret_key}: {exc}")

    env_value = os.getenv(env_var, "")
    if env_value and _allow_env_secret_fallback():
        logger.warning(
            f"Usando {env_var} desde entorno (modo transición). Migrar a secret '{secret_key}'."
        )
        return env_value

    return ""


class Environment(Enum):
    """Ambientes soportados."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class ConfigValidationError(Exception):
    """Excepción cuando la configuración es inválida."""
    pass


@dataclass
class DatabaseConfig:
    """Configuración de base de datos."""

    server: str
    port: int
    driver: str
    username: str
    password: str  # Debe venir de SecretsManager
    trusted_connection: bool = False
    pool_size: int = 5
    max_overflow: int = 10
    pool_timeout: int = 30
    pool_recycle: int = 3600

    # Base de datos específicas
    db_users: str = "users"
    db_inventario: str = "inventario"
    db_auditoria: str = "auditoria"

    @staticmethod
    def from_env() -> 'DatabaseConfig':
        """Crea configuración desde variables de entorno."""
        port = int(os.getenv("DB_PORT", "1433"))
        if not (1024 <= port <= 65535):
            raise ConfigValidationError(f"DB_PORT debe estar entre 1024 y 65535, got {port}")

        password = _get_secret_value("database/db_password", "DB_PASSWORD")

        if not password and not os.getenv("DB_TRUSTED_CONNECTION", "false").lower() == "true":
            raise ConfigValidationError("DB_PASSWORD es requerido cuando no se usa autenticación Windows")

        return DatabaseConfig(
            server=os.getenv("DB_SERVER", "localhost"),
            port=port,
            driver=os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server"),
            username=os.getenv("DB_USERNAME", "sa"),
            password=password,
            trusted_connection=os.getenv("DB_TRUSTED_CONNECTION", "false").lower() == "true",
            pool_size=int(os.getenv("DB_POOL_SIZE", "5")),
            max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "10")),
            pool_timeout=int(os.getenv("DB_POOL_TIMEOUT", "30")),
            pool_recycle=int(os.getenv("DB_POOL_RECYCLE", "3600")),
            db_users=os.getenv("DB_USERS", "users"),
            db_inventario=os.getenv("DB_INVENTARIO", "inventario"),
            db_auditoria=os.getenv("DB_AUDITORIA", "auditoria")
        )


@dataclass
class SecurityConfig:
    """Configuración de seguridad."""

    secret_key: str
    jwt_secret_key: str
    encryption_key: str
    password_hash_algorithm: str = "bcrypt"
    password_min_length: int = 8
    password_require_numbers: bool = True
    password_require_symbols: bool = True
    password_uppercase_required: bool = True
    session_timeout: int = 3600
    max_sessions_per_user: int = 3
    max_login_attempts: int = 3
    login_lockout_duration: int = 300
    jwt_access_token_expires: int = 3600
    jwt_refresh_token_expires: int = 86400

    @staticmethod
    def from_env() -> 'SecurityConfig':
        """Crea configuración desde variables de entorno y SecretsManager."""
        secret_key = _get_secret_value("security/secret_key", "SECRET_KEY")
        jwt_secret_key = _get_secret_value("security/jwt_secret_key", "JWT_SECRET_KEY")
        encryption_key = _get_secret_value("security/encryption_key", "ENCRYPTION_KEY")

        # Validar longitudes mínimas
        if len(secret_key) < 32:
            raise ConfigValidationError(f"SECRET_KEY debe tener al menos 32 caracteres, got {len(secret_key)}")
        if len(jwt_secret_key) < 32:
            raise ConfigValidationError(f"JWT_SECRET_KEY debe tener al menos 32 caracteres, got {len(jwt_secret_key)}")
        if len(encryption_key) < 32:
            raise ConfigValidationError(f"ENCRYPTION_KEY debe tener al menos 32 caracteres, got {len(encryption_key)}")

        return SecurityConfig(
            secret_key=secret_key,
            jwt_secret_key=jwt_secret_key,
            encryption_key=encryption_key,
            password_hash_algorithm=os.getenv("PASSWORD_HASH_ALGORITHM", "bcrypt"),
            password_min_length=int(os.getenv("PASSWORD_MIN_LENGTH", "8")),
            password_require_numbers=os.getenv("PASSWORD_REQUIRE_NUMBERS", "true").lower() == "true",
            password_require_symbols=os.getenv("PASSWORD_REQUIRE_SYMBOLS", "true").lower() == "true",
            password_uppercase_required=os.getenv("PASSWORD_UPPERCASE_REQUIRED", "true").lower() == "true",
            session_timeout=int(os.getenv("SESSION_TIMEOUT", "3600")),
            max_sessions_per_user=int(os.getenv("MAX_SESSIONS_PER_USER", "3")),
            max_login_attempts=int(os.getenv("MAX_LOGIN_ATTEMPTS", "3")),
            login_lockout_duration=int(os.getenv("LOGIN_LOCKOUT_DURATION", "300")),
            jwt_access_token_expires=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", "3600")),
            jwt_refresh_token_expires=int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES", "86400"))
        )


@dataclass
class RedisConfig:
    """Configuración de Redis/Cache."""

    host: str
    port: int
    db: int = 0
    password: Optional[str] = None
    maxmemory: str = "256mb"
    maxmemory_policy: str = "allkeys-lru"
    cache_default_ttl: int = 3600
    cache_session_ttl: int = 1800
    enabled: bool = True

    @staticmethod
    def from_env() -> 'RedisConfig':
        """Crea configuración desde variables de entorno."""
        try:
            from rexus.core.secrets_manager import get_secrets_manager
            secrets = get_secrets_manager()
            password = secrets.get_secret("redis/password") or os.getenv("REDIS_PASSWORD", "")
        except Exception:
            password = os.getenv("REDIS_PASSWORD", "")

        return RedisConfig(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", "6379")),
            db=int(os.getenv("REDIS_DB", "0")),
            password=password or None,
            maxmemory=os.getenv("REDIS_MAXMEMORY", "256mb"),
            maxmemory_policy=os.getenv("REDIS_MAXMEMORY_POLICY", "allkeys-lru"),
            cache_default_ttl=int(os.getenv("CACHE_DEFAULT_TTL", "3600")),
            cache_session_ttl=int(os.getenv("CACHE_SESSION_TTL", "1800")),
            enabled=os.getenv("REDIS_ENABLED", "true").lower() == "true"
        )


@dataclass
class MonitoringConfig:
    """Configuración de monitoreo."""

    prometheus_enabled: bool = False
    prometheus_port: int = 8000
    metrics_enabled: bool = True
    metrics_path: str = "/metrics"

    @staticmethod
    def from_env() -> 'MonitoringConfig':
        """Crea configuración desde variables de entorno."""
        return MonitoringConfig(
            prometheus_enabled=os.getenv("PROMETHEUS_ENABLED", "false").lower() == "true",
            prometheus_port=int(os.getenv("PROMETHEUS_PORT", "8000")),
            metrics_enabled=os.getenv("METRICS_ENABLED", "true").lower() == "true",
            metrics_path=os.getenv("METRICS_PATH", "/metrics")
        )


@dataclass
class LoggingConfig:
    """Configuración de logging."""

    level: str = "INFO"
    format: str = "json"
    file: str = "./logs/rexus.log"
    rotation_size_mb: int = 50
    retention_days: int = 30
    sentry_dsn: Optional[str] = None
    sentry_environment: str = "development"

    @staticmethod
    def from_env() -> 'LoggingConfig':
        """Crea configuración desde variables de entorno."""
        try:
            from rexus.core.secrets_manager import get_secrets_manager
            secrets = get_secrets_manager()
            sentry_dsn = secrets.get_secret("logging/sentry_dsn") or os.getenv("SENTRY_DSN", "")
        except Exception:
            sentry_dsn = os.getenv("SENTRY_DSN", "")

        return LoggingConfig(
            level=os.getenv("LOG_LEVEL", "INFO").upper(),
            format=os.getenv("LOG_FORMAT", "json").lower(),
            file=os.getenv("LOG_FILE", "./logs/rexus.log"),
            rotation_size_mb=int(os.getenv("LOG_ROTATION_SIZE_MB", "50")),
            retention_days=int(os.getenv("LOG_RETENTION_DAYS", "30")),
            sentry_dsn=sentry_dsn or None,
            sentry_environment=os.getenv("SENTRY_ENVIRONMENT", "development")
        )


@dataclass
class APIConfig:
    """Configuración de API."""

    host: str = "0.0.0.0"
    port: int = 5000
    workers: int = 4
    cors_origins: List[str] = field(default_factory=lambda: ["http://localhost:3000"])
    cors_methods: List[str] = field(default_factory=lambda: ["GET", "POST", "PUT", "DELETE"])
    cors_headers: List[str] = field(default_factory=lambda: ["Content-Type", "Authorization"])
    rate_limit: int = 100
    rate_limit_window: int = 60

    @staticmethod
    def from_env() -> 'APIConfig':
        """Crea configuración desde variables de entorno."""
        cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
        cors_methods = os.getenv("CORS_METHODS", "GET,POST,PUT,DELETE").split(",")
        cors_headers = os.getenv("CORS_HEADERS", "Content-Type,Authorization").split(",")

        return APIConfig(
            host=os.getenv("API_HOST", "0.0.0.0"),
            port=int(os.getenv("API_PORT", "5000")),
            workers=int(os.getenv("API_WORKERS", "4")),
            cors_origins=[o.strip() for o in cors_origins],
            cors_methods=[m.strip() for m in cors_methods],
            cors_headers=[h.strip() for h in cors_headers],
            rate_limit=int(os.getenv("API_RATE_LIMIT", "100")),
            rate_limit_window=int(os.getenv("API_RATE_LIMIT_WINDOW", "60"))
        )


@dataclass
class BackupConfig:
    """Configuración de backups."""

    enabled: bool = True
    schedule: str = "0 2 * * *"  # Cron expression
    path: str = "./backups"
    retention_days: int = 30
    compress: bool = True
    s3_enabled: bool = False
    s3_bucket: Optional[str] = None
    s3_region: Optional[str] = None

    @staticmethod
    def from_env() -> 'BackupConfig':
        """Crea configuración desde variables de entorno."""
        return BackupConfig(
            enabled=os.getenv("BACKUP_ENABLED", "true").lower() == "true",
            schedule=os.getenv("BACKUP_SCHEDULE", "0 2 * * *"),
            path=os.getenv("BACKUP_PATH", "./backups"),
            retention_days=int(os.getenv("BACKUP_RETENTION_DAYS", "30")),
            compress=os.getenv("BACKUP_COMPRESS", "true").lower() == "true",
            s3_enabled=os.getenv("BACKUP_S3_ENABLED", "false").lower() == "true",
            s3_bucket=os.getenv("BACKUP_S3_BUCKET") or None,
            s3_region=os.getenv("BACKUP_S3_REGION") or None
        )


@dataclass
class EmpresaConfig:
    """Configuración de la empresa."""

    nombre: str = ""
    ruc: str = ""
    direccion: str = ""
    telefono: str = ""
    email: str = ""

    @staticmethod
    def from_env() -> 'EmpresaConfig':
        """Crea configuración desde variables de entorno."""
        return EmpresaConfig(
            nombre=os.getenv("EMPRESA_NOMBRE", ""),
            ruc=os.getenv("EMPRESA_RUC", ""),
            direccion=os.getenv("EMPRESA_DIRECCION", ""),
            telefono=os.getenv("EMPRESA_TELEFONO", ""),
            email=os.getenv("EMPRESA_EMAIL", "")
        )


class Config:
    """
    Configuración unificada de la aplicación.

    Example:
        config = Config.load()
        db_config = config.database
        print(f"Conectando a {db_config.server}:{db_config.port}")
    """

    def __init__(self,
                 environment: Environment,
                 database: DatabaseConfig,
                 security: SecurityConfig,
                 redis: RedisConfig,
                 monitoring: MonitoringConfig,
                 logging: LoggingConfig,
                 api: APIConfig,
                 backup: BackupConfig,
                 empresa: EmpresaConfig):
        self.environment = environment
        self.database = database
        self.security = security
        self.redis = redis
        self.monitoring = monitoring
        self.logging = logging
        self.api = api
        self.backup = backup
        self.empresa = empresa

    @classmethod
    def load(cls, env_file: Optional[str] = None) -> 'Config':
        """
        Carga la configuración desde variables de entorno.

        Args:
            env_file: Ruta opcional a archivo .env

        Returns:
            Configuración validada
        """
        # Cargar archivo .env si se proporciona
        if env_file:
            cls._load_env_file(env_file)

        # Detectar ambiente
        environment = cls._detect_environment()

        # Validar que variables críticas existan
        cls._validate_critical_vars()

        # Cregar configuraciones
        try:
            return cls(
                environment=environment,
                database=DatabaseConfig.from_env(),
                security=SecurityConfig.from_env(),
                redis=RedisConfig.from_env(),
                monitoring=MonitoringConfig.from_env(),
                logging=LoggingConfig.from_env(),
                api=APIConfig.from_env(),
                backup=BackupConfig.from_env(),
                empresa=EmpresaConfig.from_env()
            )
        except Exception as e:
            raise ConfigValidationError(f"Error cargando configuración: {e}")

    @staticmethod
    def _load_env_file(env_file: Optional[str]):
        """Carga variables desde archivo .env."""
        from pathlib import Path
        if not env_file:
            return
        env_path = Path(env_file)
        if not env_path.exists():
            logger.warning(f"Archivo .env no encontrado: {env_file}")
            return

        # Leer y parsear archivo
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

    @staticmethod
    def _detect_environment() -> Environment:
        """Detecta el ambiente actual."""
        env = os.getenv("ENVIRONMENT", os.getenv("NODE_ENV", "development")).lower()

        if env == "production":
            return Environment.PRODUCTION
        elif env == "staging":
            return Environment.STAGING
        else:
            return Environment.DEVELOPMENT

    @staticmethod
    def _validate_critical_vars():
        """Valida variables críticas estén presentes."""
        critical_vars = []

        # Validar que al menos una fuente de secret key exista
        has_secret_key = bool(os.getenv("SECRET_KEY"))
        has_vault = bool(os.getenv("VAULT_ADDR") and os.getenv("VAULT_TOKEN"))
        has_master_key = bool(os.getenv("SECRETS_MASTER_KEY"))

        if not has_secret_key and not has_vault and not has_master_key:
            critical_vars.append("SECRET_KEY o VAULT_ADDR o SECRETS_MASTER_KEY")

        if critical_vars:
            raise ConfigValidationError(
                f"Faltan variables críticas: {', '.join(critical_vars)}"
            )

    def is_development(self) -> bool:
        """Si es ambiente de desarrollo."""
        return self.environment == Environment.DEVELOPMENT

    def is_production(self) -> bool:
        """Si es ambiente de producción."""
        return self.environment == Environment.PRODUCTION

    def is_staging(self) -> bool:
        """Si es ambiente de staging."""
        return self.environment == Environment.STAGING

    def get_connection_string(self, database: str = None) -> str:
        """
        Genera connection string para SQL Server.

        Args:
            database: Nombre de la base de datos (usa db_users por defecto)
        """
        db = database or self.database.db_users

        if self.database.trusted_connection:
            auth = "Trusted_Connection=yes"
        else:
            auth = f"UID={self.database.username};PWD={self.database.password}"

        return (
            f"DRIVER={{{self.database.driver}}};"
            f"SERVER={self.database.server};"
            f"DATABASE={db};"
            f"{auth};"
        )

    def validate(self) -> List[str]:
        """
        Valida la configuración completa.

        Returns:
            Lista de warnings (vacía si todo está OK)
        """
        warnings = []

        # Warnings de seguridad para producción
        if self.is_production():
            if self.security.password_min_length < 12:
                warnings.append("PASSWORD_MIN_LENGTH debería ser al menos 12 en producción")

            if not self.security.password_require_symbols:
                warnings.append("PASSWORD_REQUIRE_SYMBOLS debería ser True en producción")

            if self.api.host == "0.0.0.0":
                warnings.append("API_HOST=0.0.0.0 expone la app a todas las interfaces")

            if "*" in self.api.cors_origins:
                warnings.append("CORS_ORIGINS contiene *, inseguro para producción")

        # Warnings de logging
        if self.logging.level == "DEBUG" and self.is_production():
            warnings.append("LOG_LEVEL=DEBUG no recomendado para producción")

        return warnings


# Instancia global
_config_instance: Optional[Config] = None


def get_config(reload: bool = False) -> Config:
    """
    Obtiene la configuración global (singleton).

    Args:
        reload: Si recargar la configuración

    Returns:
        Configuración actual
    """
    global _config_instance

    if _config_instance is None or reload:
        # Buscar archivo .env apropiado para el ambiente
        env = os.getenv("ENVIRONMENT", os.getenv("NODE_ENV", "development"))
        env_files = [
            f".env.{env}",
            ".env.local",
            ".env"
        ]

        env_file = None
        for f in env_files:
            if Path(f).exists():
                env_file = f
                break

        _config_instance = Config.load(env_file)

        # Loguear warnings
        warnings = _config_instance.validate()
        for w in warnings:
            logger.warning(f"Config warning: {w}")

        logger.info(f"Configuración cargada para ambiente: {_config_instance.environment.value}")

    return _config_instance


def init_config(env_file: Optional[str] = None) -> Config:
    """
    Inicializa la configuración explícitamente.

    Args:
        env_file: Ruta opcional a archivo .env

    Returns:
        Configuración inicializada
    """
    global _config_instance
    _config_instance = Config.load(env_file)
    return _config_instance
