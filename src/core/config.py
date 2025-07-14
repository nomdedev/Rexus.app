"""
Configuración principal de la aplicación Rexus
Versión: 2.0.0 - Producción Ready con variables de entorno
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional
import logging

# Intentar cargar python-dotenv si está disponible
try:
    from dotenv import load_dotenv
    # Cargar variables de entorno desde .env
    load_dotenv()
    dotenv_available = True
except ImportError:
    dotenv_available = False
    logging.warning("python-dotenv no disponible. Variables de entorno desde sistema únicamente.")

# Rutas del proyecto
PROJECT_ROOT = Path(__file__).parent.parent.parent
SRC_DIR = PROJECT_ROOT / "src"
CONFIG_DIR = PROJECT_ROOT / "config"
DOCS_DIR = PROJECT_ROOT / "docs"
TESTS_DIR = PROJECT_ROOT / "tests"
LOGS_DIR = PROJECT_ROOT / "logs"
UPLOADS_DIR = PROJECT_ROOT / "uploads"
BACKUPS_DIR = PROJECT_ROOT / "backups"

# Crear directorios si no existen
for directory in [LOGS_DIR, UPLOADS_DIR, BACKUPS_DIR]:
    directory.mkdir(exist_ok=True)

def get_env_var(key: str, default: Any = None, required: bool = False, var_type: type = str) -> Any:
    """
    Obtiene una variable de entorno con validación y conversión de tipos.
    
    Args:
        key: Nombre de la variable de entorno
        default: Valor por defecto
        required: Si es True, lanza excepción si no existe
        var_type: Tipo al que convertir el valor
    
    Returns:
        Valor convertido al tipo especificado
    
    Raises:
        ValueError: Si la variable es requerida y no existe
    """
    value = os.getenv(key, default)
    
    if required and value is None:
        raise ValueError(f"Variable de entorno requerida no encontrada: {key}")
    
    if value is None:
        return default
    
    # Conversión de tipos
    if var_type == bool:
        return str(value).lower() in ('true', '1', 'yes', 'on')
    elif var_type == int:
        try:
            return int(value)
        except ValueError:
            return default if default is not None else 0
    elif var_type == float:
        try:
            return float(value)
        except ValueError:
            return default if default is not None else 0.0
    
    return str(value)

# ===== CONFIGURACIÓN DE LA APLICACIÓN =====
APP_CONFIG = {
    "name": get_env_var("APP_NAME", "Rexus"),
    "version": get_env_var("APP_VERSION", "2.0.0"),
    "environment": get_env_var("APP_ENV", "production"),
    "debug": get_env_var("APP_DEBUG", False, var_type=bool),
    "log_level": get_env_var("APP_LOG_LEVEL", "INFO"),
    "window_size": (1280, 720),
    "min_window_size": (1024, 600),
}

# ===== CONFIGURACIÓN DE BASE DE DATOS =====
DATABASE_CONFIG = {
    "driver": get_env_var("DB_DRIVER", "ODBC Driver 17 for SQL Server"),
    "server": get_env_var("DB_SERVER", "localhost\\SQLEXPRESS"),
    "server_alternate": get_env_var("DB_SERVER_ALTERNATE", "localhost"),
    "port": get_env_var("DB_PORT", 1433, var_type=int),
    "username": get_env_var("DB_USERNAME", "sa"),
    "password": get_env_var("DB_PASSWORD", "", required=True),
    "timeout": get_env_var("DB_TIMEOUT", 30, var_type=int),
    "pool_size": get_env_var("DB_CONNECTION_POOL_SIZE", 10, var_type=int),
    "max_overflow": get_env_var("DB_CONNECTION_POOL_MAX_OVERFLOW", 20, var_type=int),
    "databases": {
        "inventario": get_env_var("DB_INVENTARIO", "inventario"),
        "users": get_env_var("DB_USERS", "users"),
        "auditoria": get_env_var("DB_AUDITORIA", "auditoria"),
    },
}

# ===== CONFIGURACIÓN DE SEGURIDAD =====
SECURITY_CONFIG = {
    "secret_key": get_env_var("SECRET_KEY", "", required=True),
    "jwt_secret": get_env_var("JWT_SECRET_KEY", "", required=True),
    "jwt_expiration_hours": get_env_var("JWT_EXPIRATION_HOURS", 24, var_type=int),
    "encryption_key": get_env_var("ENCRYPTION_KEY", "", required=True),
    "password_salt_rounds": get_env_var("PASSWORD_SALT_ROUNDS", 12, var_type=int),
}

# ===== CONFIGURACIÓN DE LOGGING =====
LOGGING_CONFIG = {
    "level": get_env_var("LOG_LEVEL", "INFO"),
    "file_path": get_env_var("LOG_FILE_PATH", str(LOGS_DIR / "rexus.log")),
    "max_size": get_env_var("LOG_MAX_SIZE", "10MB"),
    "backup_count": get_env_var("LOG_BACKUP_COUNT", 5, var_type=int),
    "format": get_env_var("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"),
}

# ===== CONFIGURACIÓN DE CACHE =====
CACHE_CONFIG = {
    "type": get_env_var("CACHE_TYPE", "memory"),  # memory, redis, disk
    "redis_url": get_env_var("CACHE_REDIS_URL", "redis://localhost:6379/0"),
    "default_timeout": get_env_var("CACHE_DEFAULT_TIMEOUT", 3600, var_type=int),
    "query_cache_enabled": get_env_var("QUERY_CACHE_ENABLED", True, var_type=bool),
    "query_cache_timeout": get_env_var("QUERY_CACHE_TIMEOUT", 1800, var_type=int),
}

# ===== CONFIGURACIÓN DE ARCHIVOS =====
FILES_CONFIG = {
    "upload_path": Path(get_env_var("UPLOAD_PATH", str(UPLOADS_DIR))),
    "backup_path": Path(get_env_var("BACKUP_PATH", str(BACKUPS_DIR))),
    "temp_path": Path(get_env_var("TEMP_PATH", str(PROJECT_ROOT / "temp"))),
    "max_upload_size": get_env_var("MAX_UPLOAD_SIZE", "50MB"),
    "allowed_extensions": get_env_var("ALLOWED_EXTENSIONS", "pdf,xlsx,xls,csv,png,jpg,jpeg,gif").split(","),
}

# ===== CONFIGURACIÓN DE BACKUP =====
BACKUP_CONFIG = {
    "enabled": get_env_var("BACKUP_ENABLED", True, var_type=bool),
    "schedule": get_env_var("BACKUP_SCHEDULE", "0 2 * * *"),  # Cron format
    "retention_days": get_env_var("BACKUP_RETENTION_DAYS", 30, var_type=int),
    "compression": get_env_var("BACKUP_COMPRESSION", True, var_type=bool),
}

# ===== CONFIGURACIÓN DE MONITOREO =====
MONITORING_CONFIG = {
    "enabled": get_env_var("MONITORING_ENABLED", True, var_type=bool),
    "metrics_port": get_env_var("METRICS_PORT", 9090, var_type=int),
    "health_check_interval": get_env_var("HEALTH_CHECK_INTERVAL", 60, var_type=int),
    "alert_email": get_env_var("ALERT_EMAIL", ""),
}

# Tema por defecto
DEFAULT_THEME = get_env_var("DEFAULT_THEME", "light")

# ===== COMPATIBILIDAD CON CÓDIGO LEGACY =====
# Variables individuales para compatibilidad con código existente
DB_DRIVER = DATABASE_CONFIG["driver"]
DB_SERVER = DATABASE_CONFIG["server"]
DB_SERVER_ALTERNATE = DATABASE_CONFIG["server_alternate"]
DB_USERNAME = DATABASE_CONFIG["username"]
DB_PASSWORD = DATABASE_CONFIG["password"]
DB_TIMEOUT = DATABASE_CONFIG["timeout"]

# Bases de datos específicas
DB_INVENTARIO = DATABASE_CONFIG["databases"]["inventario"]
DB_USERS = DATABASE_CONFIG["databases"]["users"]
DB_AUDITORIA = DATABASE_CONFIG["databases"]["auditoria"]
DB_DEFAULT_DATABASE = DB_INVENTARIO

# Configuración de UI/UX (extraída del main.py original)
UI_CONFIG = {
    "padding": {"dialog_vertical": 20, "dialog_horizontal": 24, "element_margin": 16},
    "borders": {"radius": 8, "button_radius": 8},
    "typography": {
        "family": "Segoe UI, Roboto, sans-serif",
        "size_small": 11,
        "size_normal": 13,
        "size_title": 14,
        "weight_normal": 400,
        "weight_medium": 500,
        "weight_semibold": 600,
    },
    "colors": {
        "text_primary": "#1e293b",
        "text_error": "#ef4444",
        "text_info": "#2563eb",
        "text_success": "#22c55e",
        "text_warning": "#fbbf24",
        "button_primary": "#2563eb",
        "button_secondary": "#f1f5f9",
    },
    "button": {
        "min_width": 80,
        "min_height": 28,
        "padding_horizontal": 16,
        "spacing": 16,
    },
}
