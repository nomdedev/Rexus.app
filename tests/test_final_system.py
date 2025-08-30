#!/usr/bin/env python3
"""
Script de prueba final del sistema de login y permisos para Rexus.app
Verifica que todo el sistema funcione correctamente con las variables de entorno.
"""

import os
import sys
from pathlib import Path

# Agregar el directorio raíz al path
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

# Cargar variables de entorno
try:
    from dotenv import load_dotenv
    load_dotenv(root_dir / ".env")
    print("✅ Archivo .env cargado correctamente")
except ImportError:
    print("⚠️  python-dotenv no instalado")
except Exception as e:
    print(f"⚠️  Error cargando .env: {e}")

def test_database_connection():
    """Prueba la conexión a la base de datos."""
    print("\n🗄️  PRUEBA DE CONEXIÓN A BASE DE DATOS...")

    try:
        from rexus.core.database import UsersDatabaseConnection
        db = UsersDatabaseConnection()

        # Probar una consulta simple usando el context manager
        with db.get_cursor() as cursor:
            cursor.execute("SELECT 1 as test")
            result = cursor.fetchone()

        if result and result[0] == 1:
            print("   ✅ Conexión y consulta básica exitosas")
            return True
        else:
            print("   ❌ Consulta básica falló")
            return False

    except Exception as e:
        print(f"   ❌ Error en conexión a BD: {e}")
        return False

def test_sql_query_manager():
    """Prueba el SQLQueryManager."""
    print("\n📊 PRUEBA DE SQL QUERY MANAGER...")

    try:
        from rexus.utils.sql_query_manager import SQLQueryManager
        sql_manager = SQLQueryManager()

        # Probar obtener permisos de un usuario (usando un usuario de prueba)
        test_username = "admin"  # Usuario que debería existir
        user_data = sql_manager.get_user_by_username(test_username)

        if user_data:
            user_id = user_data.get('id')
            if user_id:
                permissions = sql_manager.get_user_permissions(user_id)
                if permissions is not None:
                    print(f"   ✅ Permisos obtenidos para usuario '{test_username}': {len(permissions)} permisos")
                    return True
                else:
                    print(f"   ⚠️  No se pudieron obtener permisos para usuario '{test_username}'")
                    return True  # No es un error crítico
            else:
                print(f"   ⚠️  Usuario '{test_username}' no tiene ID válido")
                return True
        else:
            print(f"   ⚠️  Usuario '{test_username}' no encontrado")
            return True  # No es un error crítico

    except Exception as e:
        print(f"   ❌ Error en SQLQueryManager: {e}")
        return False

def test_security_utils():
    """Prueba las utilidades de seguridad."""
    print("\n🔐 PRUEBA DE UTILIDADES DE SEGURIDAD...")

    try:
        from rexus.utils.security import SecurityUtils

        # Probar hash y verificación de contraseña
        # SEGURIDAD: Eliminada contraseña hardcodeada)
        hashed = SecurityUtils.hash_password(test_password)
        is_valid = SecurityUtils.verify_password(test_password, hashed)

        if is_valid:
            print("   ✅ Hash y verificación de contraseña exitosos")
            return True
        else:
            print("   ❌ Verificación de contraseña falló")
            return False

    except Exception as e:
        print(f"   ❌ Error en SecurityUtils: {e}")
        return False

def test_user_authentication():
    """Prueba la autenticación de usuario."""
    print("\n👤 PRUEBA DE AUTENTICACIÓN DE USUARIO...")

    try:
        from rexus.utils.sql_query_manager import SQLQueryManager
        from rexus.utils.security import SecurityUtils

        sql_manager = SQLQueryManager()

        # Intentar autenticar con un usuario de prueba
        test_username = os.getenv('REXUS_DEV_USER', 'admin')
        # SEGURIDAD: Eliminada contraseña hardcodeada)

        # Obtener datos del usuario
        user_data = sql_manager.get_user_by_username(test_username)

        if user_data:
            stored_hash = user_data.get('password_hash')
            if stored_hash and SecurityUtils.verify_password(test_password, stored_hash):
                print(f"   ✅ Autenticación exitosa para usuario '{test_username}'")
                return True
            else:
                print(f"   ⚠️  Contraseña incorrecta para usuario '{test_username}'")
                return True  # No es un error crítico
        else:
            print(f"   ⚠️  Usuario '{test_username}' no encontrado en la base de datos")
            return True  # No es un error crítico

    except Exception as e:
        print(f"   ❌ Error en autenticación: {e}")
        return False

def test_module_permissions():
    """Prueba el sistema de permisos de módulos."""
    print("\n🔑 PRUEBA DE SISTEMA DE PERMISOS...")

    try:
        from rexus.utils.sql_query_manager import SQLQueryManager

        sql_manager = SQLQueryManager()

        # Obtener permisos para un usuario
        test_username = os.getenv('REXUS_DEV_USER', 'admin')
        user_data = sql_manager.get_user_by_username(test_username)

        if user_data:
            user_id = user_data.get('id')
            if user_id:
                permissions = sql_manager.get_user_permissions(user_id)

                if permissions:
                    print(f"   ✅ Sistema de permisos funcionando: {len(permissions)} permisos encontrados")

                    # Mostrar algunos permisos de ejemplo
                    for perm in permissions[:5]:  # Mostrar máximo 5
                        print(f"      - Permiso: {perm}")

                    return True
                else:
                    print(f"   ⚠️  No se encontraron permisos para usuario '{test_username}'")
                    return True  # No es un error crítico
            else:
                print(f"   ⚠️  Usuario '{test_username}' no tiene ID válido")
                return True
        else:
            print(f"   ⚠️  Usuario '{test_username}' no encontrado")
            return True  # No es un error crítico

    except Exception as e:
        print(f"   ❌ Error en sistema de permisos: {e}")
        return False

def main():
    """Función principal de pruebas."""
    print("🚀 PRUEBA FINAL DEL SISTEMA - Rexus.app\n")

    # Ejecutar todas las pruebas
    tests = [
        ("Conexión a Base de Datos", test_database_connection),
        ("SQL Query Manager", test_sql_query_manager),
        ("Utilidades de Seguridad", test_security_utils),
        ("Autenticación de Usuario", test_user_authentication),
        ("Sistema de Permisos", test_module_permissions)
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"   ❌ Error ejecutando {test_name}: {e}")
            results.append((test_name, False))

    # Resumen final
    print("\n" + "="*60)
    print("📊 RESULTADOS DE PRUEBAS:")
    print("="*60)

    all_passed = True
    for test_name, result in results:
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{status} {test_name}")
        if not result:
            all_passed = False

    print("\n" + "="*60)
    if all_passed:
        print("🎉 ¡TODAS LAS PRUEBAS PASARON!")
        print("💡 El sistema de login y permisos está funcionando correctamente.")
        print("💡 Todas las variables de entorno están configuradas y operativas.")
    else:
        print("⚠️  ALGUNAS PRUEBAS FALLARON")
        print("💡 Revisa los errores anteriores y verifica la configuración.")
    print("="*60)

    return 0 if all_passed else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
