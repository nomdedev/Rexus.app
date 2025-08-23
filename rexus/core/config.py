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
