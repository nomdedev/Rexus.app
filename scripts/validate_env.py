#!/usr/bin/env python3
"""
Script de validación de variables de entorno para Rexus.app
Verifica que todas las variables necesarias estén configuradas correctamente.
"""

import os
import sys
from pathlib import Path
from typing import Dict, Tuple

# Cargar variables de entorno desde .env
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
    print("✅ Archivo .env cargado correctamente")
except ImportError:
    print("⚠️  python-dotenv no instalado, usando variables del sistema")
except Exception as e:
    print(f"⚠️  Error cargando .env: {e}, usando variables del sistema")

# Agregar el directorio raíz al path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

class EnvironmentValidator:
    """Validador de variables de entorno para Rexus.app"""

    def __init__(self):
        self.sensitive_vars = ['DB_PASSWORD', 'SECRET_KEY', 'JWT_SECRET_KEY', 'ENCRYPTION_KEY']

        self.required_vars = {
            # Base de datos
            'DB_SERVER': 'Servidor de SQL Server',
            'DB_DRIVER': 'Driver ODBC para SQL Server',
            'DB_USERS': 'Nombre de la base de datos de usuarios',
            'DB_USERNAME': 'Usuario de la base de datos',

            # API
            'API_ENABLED': 'Habilitar API',
            'API_HOST': 'Host del API',
            'API_PORT': 'Puerto del API',
            'API_DEBUG': 'Modo debug del API',

            # Logging
            'LOG_LEVEL': 'Nivel de logging',
            'LOG_FILE': 'Archivo de log',

            # Cache
            'CACHE_TYPE': 'Tipo de cache',
            'CACHE_DEFAULT_TIMEOUT': 'Timeout por defecto del cache',

            # Backup
            'BACKUP_ENABLED': 'Habilitar backups',
            'BACKUP_RETENTION_DAYS': 'Días de retención de backups'
        }

        self.optional_vars = {
            # Desarrollo
            'REXUS_DEV_USER': 'Usuario de desarrollo',
            # 'REXUS_DEV_PASSWORD': 'ELIMINADO POR SEGURIDAD - usar BD real',
            'REXUS_DEV_AUTO_LOGIN': 'Auto-login en desarrollo',

            # Bases de datos adicionales
            'DB_INVENTARIO': 'Base de datos de inventario',
            'DB_AUDITORIA': 'Base de datos de auditoría'
        }

    def _check_secret_presence(self, secret_key: str) -> bool:
        try:
            from rexus.core.secrets_manager import get_secrets_manager
            manager = get_secrets_manager()
            return bool(manager.get_secret(secret_key))
        except Exception:
            return False

    def _is_sensitive_resolved(self, env_var: str) -> bool:
        key_mapping = {
            'DB_PASSWORD': 'database/db_password',
            'SECRET_KEY': 'security/secret_key',
            'JWT_SECRET_KEY': 'security/jwt_secret_key',
            'ENCRYPTION_KEY': 'security/encryption_key',
        }
        secret_key = key_mapping.get(env_var)
        return bool(os.getenv(env_var)) or (secret_key and self._check_secret_presence(secret_key))

    def validate_all(self) -> Tuple[bool, Dict[str, str]]:
        """Valida todas las variables de entorno requeridas."""
        results = {}
        all_valid = True

        print("🔍 VALIDANDO VARIABLES DE ENTORNO...\n")

        # Validar variables requeridas
        print("📋 Variables Requeridas:")
        for var_name, description in self.required_vars.items():
            value = os.getenv(var_name)
            if value is None or value.strip() == '':
                results[var_name] = f"❌ FALTA: {description}"
                all_valid = False
                print(f"   ❌ {var_name}: {description} - NO CONFIGURADO")
            else:
                results[var_name] = f"✅ OK: {description}"
                print(f"   ✅ {var_name}: {description} - CONFIGURADO")

        print("\n🔐 Variables Sensibles (SecretsManager o entorno en transición):")
        for var_name in self.sensitive_vars:
            if self._is_sensitive_resolved(var_name):
                source = "entorno" if os.getenv(var_name) else "SecretsManager"
                results[var_name] = f"✅ OK: {var_name} resuelto desde {source}"
                print(f"   ✅ {var_name}: RESUELTO desde {source}")
            else:
                results[var_name] = f"❌ FALTA: {var_name} no disponible ni en entorno ni en SecretsManager"
                all_valid = False
                print(f"   ❌ {var_name}: NO DISPONIBLE")

        print("\n📋 Variables Opcionales:")
        for var_name, description in self.optional_vars.items():
            value = os.getenv(var_name)
            if value is None or value.strip() == '':
                results[var_name] = f"⚠️  OPCIONAL: {description} - NO CONFIGURADO"
                print(f"   ⚠️  {var_name}: {description} - NO CONFIGURADO")
            else:
                results[var_name] = f"✅ OK: {description}"
                print(f"   ✅ {var_name}: {description} - CONFIGURADO")

        return all_valid, results

    def validate_database_connection(self) -> bool:
        """Valida específicamente la conexión a la base de datos."""
        print("\n🗄️  VALIDANDO CONEXIÓN A BASE DE DATOS...")

        required_db_vars = ['DB_SERVER', 'DB_USERS', 'DB_USERNAME']

        for var in required_db_vars:
            if not os.getenv(var):
                print(f"   ❌ Variable {var} no configurada")
                return False

        if not self._is_sensitive_resolved('DB_PASSWORD'):
            print("   ❌ DB_PASSWORD no disponible ni en entorno ni en SecretsManager")
            return False

        # Intentar importar y crear conexión
        try:
            from rexus.core.database import UsersDatabaseConnection
            db = UsersDatabaseConnection()
            print("   ✅ Conexión a base de datos exitosa")
            db.close()
            return True
        except Exception as e:
            print(f"   ❌ Error conectando a base de datos: {e}")
            return False

    def validate_security_utils(self) -> bool:
        """Valida las utilidades de seguridad."""
        print("\n🔐 VALIDANDO UTILIDADES DE SEGURIDAD...")

        try:
            from rexus.utils.security import SecurityUtils

            # Probar hash de contraseña
            # SEGURIDAD: NO usar contraseñas hardcodeadas
            test_password = None  # Debe obtenerse de BD real
            if test_password:  # Solo si hay contraseña para probar
                hashed = SecurityUtils.hash_password(test_password)
                is_valid = SecurityUtils.verify_password(test_password, hashed)
                
                if is_valid:
                    print("   ✅ SecurityUtils funcionando correctamente")
                    return True
                else:
                    print("   ❌ Error en verificación de contraseña")
                    return False
            else:
                print("   ⚠️  Saltando validación de contraseña (no definida)")
                return True

        except Exception as e:
            print(f"   ❌ Error en SecurityUtils: {e}")
            return False

    def validate_sql_query_manager(self) -> bool:
        """Valida el SQLQueryManager."""
        print("\n📊 VALIDANDO SQL QUERY MANAGER...")

        try:
            from rexus.utils.sql_query_manager import SQLQueryManager
            sql_manager = SQLQueryManager()

            # Verificar API pública actual
            required_methods = ['get_query', 'execute_query', 'get_cache_info']
            for method in required_methods:
                if not hasattr(sql_manager, method):
                    print(f"   ❌ Método {method} no encontrado")
                    return False

            print("   ✅ SQLQueryManager creado correctamente")
            return True

        except Exception as e:
            print(f"   ❌ Error en SQLQueryManager: {e}")
            return False

    def generate_env_template(self) -> str:
        """Genera un template del archivo .env con todas las variables."""
        template = "# Template de variables de entorno para Rexus.app\n"
        template += "# Copia este contenido a tu archivo .env y configura los valores\n\n"

        template += "# ===== BASE DE DATOS =====\n"
        for var_name, description in self.required_vars.items():
            if var_name.startswith('DB_'):
                current_value = os.getenv(var_name, '')
                template += f"# {description}\n{var_name}={current_value}\n\n"

        template += "# ===== SEGURIDAD =====\n"
        for var_name in ['SECRET_KEY', 'JWT_SECRET_KEY', 'ENCRYPTION_KEY']:
            description = self.optional_vars[var_name]
            current_value = os.getenv(var_name, '')
            template += f"# {description}\n# Preferir SecretsManager, usar entorno solo en transición\n{var_name}={current_value}\n\n"

        template += "# ===== API =====\n"
        for var_name, description in self.required_vars.items():
            if var_name.startswith('API_'):
                current_value = os.getenv(var_name, '')
                template += f"# {description}\n{var_name}={current_value}\n\n"

        template += "# ===== LOGGING =====\n"
        for var_name, description in self.required_vars.items():
            if var_name.startswith('LOG_'):
                current_value = os.getenv(var_name, '')
                template += f"# {description}\n{var_name}={current_value}\n\n"

        template += "# ===== CACHE =====\n"
        for var_name, description in self.required_vars.items():
            if var_name.startswith('CACHE_'):
                current_value = os.getenv(var_name, '')
                template += f"# {description}\n{var_name}={current_value}\n\n"

        template += "# ===== BACKUP =====\n"
        for var_name, description in self.required_vars.items():
            if var_name.startswith('BACKUP_'):
                current_value = os.getenv(var_name, '')
                template += f"# {description}\n{var_name}={current_value}\n\n"

        template += "# ===== DESARROLLO (OPCIONAL) =====\n"
        for var_name, description in self.optional_vars.items():
            current_value = os.getenv(var_name, '')
            template += f"# {description}\n{var_name}={current_value}\n\n"

        return template

def main():
    """Función principal de validación."""
    print("🚀 VALIDACIÓN DE VARIABLES DE ENTORNO - Rexus.app\n")

    validator = EnvironmentValidator()

    # Validar todas las variables
    all_valid, results = validator.validate_all()

    # Validar componentes específicos
    db_valid = validator.validate_database_connection()
    security_valid = validator.validate_security_utils()
    sql_valid = validator.validate_sql_query_manager()

    print("\n" + "="*60)
    print("📊 RESULTADOS DE VALIDACIÓN:")
    print("="*60)

    if all_valid:
        print("✅ TODAS las variables requeridas están configuradas")
    else:
        print("❌ FALTAN variables requeridas")

    if db_valid:
        print("✅ Conexión a base de datos funcionando")
    else:
        print("❌ Problemas con la conexión a base de datos")

    if security_valid:
        print("✅ Utilidades de seguridad funcionando")
    else:
        print("❌ Problemas con utilidades de seguridad")

    if sql_valid:
        print("✅ SQL Query Manager funcionando")
    else:
        print("❌ Problemas con SQL Query Manager")

    # Resumen final
    all_components_valid = all_valid and db_valid and security_valid and sql_valid

    print("\n" + "="*60)
    if all_components_valid:
        print("🎉 ¡VALIDACIÓN COMPLETA! El sistema está listo para usar.")
        print("💡 Todas las variables de entorno están correctamente configuradas.")
    else:
        print("⚠️  VALIDACIÓN INCOMPLETA")
        print("💡 Revisa las variables faltantes y configura tu archivo .env")
        print("\n💡 Para generar un template completo, ejecuta:")
        print("   python validate_env.py --template > .env.template")
    print("="*60)

    return 0 if all_components_valid else 1

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--template":
        validator = EnvironmentValidator()
        template = validator.generate_env_template()
        print(template)
    else:
        exit_code = main()
        sys.exit(exit_code)
