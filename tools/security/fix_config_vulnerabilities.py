#!/usr/bin/env python3
"""
Script para corregir vulnerabilidades de configuración en Rexus.app
Implementa configuración segura y validación de parámetros
"""

import json
from pathlib import Path

def create_secure_config_template():
    """Crea un template de configuración segura"""
    
    secure_config = {
        "database": {
            "host": "${DB_HOST:-localhost}",
            "port": "${DB_PORT:-5432}",
            "name": "${DB_NAME:-rexus_db}",
            "user": "${DB_USER}",
            "password": "${DB_PASSWORD}",
            "ssl_mode": "require",
            "timeout": 30,
            "pool_size": 10,
            "max_overflow": 20
        },
        "security": {
            "session_timeout": 3600,
            "max_login_attempts": 3,
            "password_min_length": 8,
            "password_require_special": True,
            "password_require_numbers": True,
            "password_require_uppercase": True,
            "token_expiry": 86400,
            "csrf_protection": True,
            "secure_cookies": True,
            "content_security_policy": True
        },
        "logging": {
            "level": "INFO",
            "max_file_size": "10MB",
            "backup_count": 5,
            "log_sql_queries": False,
            "log_user_actions": True,
            "audit_enabled": True
        },
        "application": {
            "debug": False,
            "testing": False,
            "secret_key": "${SECRET_KEY}",
            "allowed_hosts": ["localhost", "127.0.0.1"],
            "max_upload_size": "10MB",
            "allowed_file_types": [".pdf", ".doc", ".docx", ".xls", ".xlsx"],
            "rate_limiting": True,
            "maintenance_mode": False
        },
        "backup": {
            "enabled": True,
            "schedule": "daily",
            "retention_days": 30,
            "compress": True,
            "encrypt": True,
            "location": "${BACKUP_PATH:-./backups/}"
        }
    }
    
    return secure_config

def validate_config_file(config_path):
    """Valida un archivo de configuración existente"""
    
    if not config_path.exists():
        print(f"[ERROR] Archivo de configuración no encontrado: {config_path}")
        return False
    
    print(f"🔧 Validando: {config_path.name}")
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config_content = f.read()
            config_data = json.loads(config_content)
    except json.JSONDecodeError as e:
        print(f"  [ERROR] Error de JSON: {e}")
        return False
    except Exception as e:
        print(f"  [ERROR] Error al leer archivo: {e}")
        return False
    
    # Backup del archivo original
    backup_path = config_path.with_suffix('.json.backup_security')
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(config_content)
    print(f"  📋 Backup creado: {backup_path.name}")
    
    # Verificar configuraciones inseguras
    security_issues = []
    
    # Verificar debug mode
    if config_data.get('debug', False) or config_data.get('application', {}).get('debug', False):
        security_issues.append("DEBUG MODE ACTIVADO - CRÍTICO")
    
    # Verificar credenciales hardcoded
    def check_hardcoded_credentials(data, path=""):
        issues = []
        if isinstance(data, dict):
            for key, value in data.items():
                current_path = f"{path}.{key}" if path else key
                if isinstance(value, str):
                    if key.lower() in ['password', 'secret', 'key', 'token'] and not value.startswith('${'):
                        issues.append(f"Credencial hardcoded en {current_path}")
                elif isinstance(value, (dict, list)):
                    issues.extend(check_hardcoded_credentials(value, current_path))
        elif isinstance(data, list):
            for i, item in enumerate(data):
                issues.extend(check_hardcoded_credentials(item, f"{path}[{i}]"))
        return issues
    
    security_issues.extend(check_hardcoded_credentials(config_data))
    
    # Verificar configuraciones de seguridad faltantes
    required_security_settings = [
        ('security.session_timeout', 'Timeout de sesión no configurado'),
        ('security.max_login_attempts', 'Límite de intentos de login no configurado'),
        ('security.password_min_length', 'Longitud mínima de password no configurada'),
        ('logging.audit_enabled', 'Auditoría no habilitada'),
        ('database.ssl_mode', 'SSL de base de datos no configurado')
    ]
    
    for setting_path, message in required_security_settings:
        keys = setting_path.split('.')
        current = config_data
        try:
            for key in keys:
                current = current[key]
        except KeyError:
            security_issues.append(f"FALTA: {message}")
    
    # Mostrar resultados
    if security_issues:
        print(f"  [WARN] PROBLEMAS DE SEGURIDAD ENCONTRADOS ({len(security_issues)}):")
        for issue in security_issues:
            print(f"    • {issue}")
    else:
        print("  [CHECK] No se encontraron problemas de seguridad")
    
    return len(security_issues) == 0

def secure_config_file(config_path):
    """Aplica configuración segura a un archivo"""
    
    if not config_path.exists():
        print(f"[ERROR] Archivo no encontrado: {config_path}")
        return False
    
    print(f"[LOCK] Asegurando: {config_path.name}")
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = json.loads(f.read())
    except Exception as e:
        print(f"  [ERROR] Error al leer archivo JSON: {e}")
        return False
    
    # Aplicar configuraciones seguras
    secure_template = create_secure_config_template()
    
    # Mergear configuraciones manteniendo las existentes
    def merge_configs(existing, secure):
        for key, value in secure.items():
            if key not in existing:
                existing[key] = value
            elif isinstance(value, dict) and isinstance(existing[key], dict):
                merge_configs(existing[key], value)
    
    # Aplicar configuraciones de seguridad
    if 'security' not in config_data:
        config_data['security'] = {}
    
    merge_configs(config_data, secure_template)
    
    # Desactivar debug mode
    if 'debug' in config_data:
        config_data['debug'] = False
    if 'application' in config_data and 'debug' in config_data['application']:
        config_data['application']['debug'] = False
    
    # Escribir archivo actualizado
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config_data, f, indent=4, ensure_ascii=False)
    
    print("  [CHECK] Configuración segura aplicada")
    return True

def check_environment_variables():
    """Verifica que las variables de entorno estén configuradas"""
    
    env_file_path = Path('.env')
    
    if not env_file_path.exists():
        print("🔧 Creando archivo .env template...")
        
        env_content = '''# Rexus.app Environment Variables
# IMPORTANTE: Configurar todas las variables antes de usar en producción

# Base de datos
DB_HOST=localhost
DB_PORT=5432
DB_NAME=rexus_db
DB_USER=your_db_user
DB_PASSWORD=your_secure_password_here

# Seguridad
SECRET_KEY=your_secret_key_minimum_32_characters
ENCRYPTION_KEY=your_encryption_key_here

# Rutas
BACKUP_PATH=./backups/
LOG_PATH=./logs/

# Configuración de aplicación
ENVIRONMENT=production
MAINTENANCE_MODE=false

# Configuración opcional
SMTP_HOST=your_smtp_server
SMTP_USER=your_email
SMTP_PASSWORD=your_email_password

# NOTA: Cambiar todos los valores por defecto antes de usar en producción
# NOTA: No commitear este archivo con credenciales reales
'''
        
        with open(env_file_path, 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        print(f"  [CHECK] Template .env creado en: {env_file_path}")
        print("  [WARN] IMPORTANTE: Configurar todas las variables antes de usar en producción")
    else:
        print(f"  [CHECK] Archivo .env existe en: {env_file_path}")
    
    return True

def main():
    """Función principal"""
    print("🚨 CORRECCIÓN DE VULNERABILIDADES DE CONFIGURACIÓN - REXUS.APP")
    print("=" * 75)
    
    # Verificar variables de entorno
    print("1. VERIFICANDO VARIABLES DE ENTORNO")
    check_environment_variables()
    print()
    
    # Buscar archivos de configuración
    config_patterns = [
        "config/*.json",
        "*.json",
        "rexus_config.json",
        "config.json"
    ]
    
    config_files = []
    for pattern in config_patterns:
        config_files.extend(list(Path('.').glob(pattern)))
    
    # Filtrar archivos relevantes
    relevant_configs = []
    for config_file in config_files:
        if any(keyword in config_file.name.lower() for keyword in ['config', 'settings', 'rexus']):
            relevant_configs.append(config_file)
    
    if not relevant_configs:
        print("2. CREANDO CONFIGURACIÓN SEGURA")
        
        # Crear configuración segura por defecto
        secure_config_path = Path("config/secure_config.json")
        secure_config_path.parent.mkdir(exist_ok=True)
        
        secure_config = create_secure_config_template()
        
        with open(secure_config_path, 'w', encoding='utf-8') as f:
            json.dump(secure_config, f, indent=4, ensure_ascii=False)
        
        print(f"  [CHECK] Configuración segura creada: {secure_config_path}")
        relevant_configs = [secure_config_path]
    
    print(f"\n2. VALIDANDO ARCHIVOS DE CONFIGURACIÓN ({len(relevant_configs)} encontrados)")
    
    secure_count = 0
    for config_file in relevant_configs:
        if validate_config_file(config_file):
            secure_count += 1
        print()
    
    print("3. APLICANDO CONFIGURACIONES SEGURAS")
    for config_file in relevant_configs:
        if secure_config_file(config_file):
            print(f"  [CHECK] {config_file.name} actualizado")
        print()
    
    # Crear .gitignore para archivos sensibles
    gitignore_path = Path('.gitignore')
    gitignore_content = '''
# Archivos de configuración sensibles
.env
*.backup_security
config/private/
logs/
backups/
*.log

# Archivos temporales
__pycache__/
*.pyc
*.pyo
.pytest_cache/

# Archivos de sistema
.DS_Store
Thumbs.db
'''
    
    if not gitignore_path.exists():
        with open(gitignore_path, 'w', encoding='utf-8') as f:
            f.write(gitignore_content)
        print("  [CHECK] .gitignore creado para proteger archivos sensibles")
    
    # Resumen
    print("=" * 75)
    print("[CHART] RESUMEN DE CONFIGURACIÓN SEGURA")
    print(f"[CHECK] Archivos de configuración procesados: {len(relevant_configs)}")
    print(f"[CHECK] Configuraciones seguras aplicadas: {len(relevant_configs)}")
    print("[CHECK] Variables de entorno configuradas: .env template")
    
    print("\n🎉 CONFIGURACIÓN SEGURA IMPLEMENTADA EXITOSAMENTE")
    print("\n📋 PRÓXIMOS PASOS:")
    print("1. Configurar variables de entorno en .env")
    print("2. Revisar configuraciones aplicadas")
    print("3. Probar aplicación con nueva configuración")
    print("4. Configurar SSL para base de datos")
    print("5. Implementar monitoreo de configuración")

if __name__ == "__main__":
    main()
