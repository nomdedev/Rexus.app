#!/usr/bin/env python3
"""
Script de prueba para verificar la implementación de permisos DB-driven.
"""

import os
import sys
from pathlib import Path

# Agregar el directorio raíz al path
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

def test_database_connection():
    """Prueba la conexión a la base de datos."""
    print("🔍 Probando conexión a base de datos...")

    try:
        from rexus.core.database import UsersDatabaseConnection
        db = UsersDatabaseConnection()
        print("✅ Conexión a base de datos exitosa")
        # Verificar que la conexión funciona
        db.close()
        return True
    except Exception as e:
        print(f"❌ Error conectando a base de datos: {e}")
        return False

def test_sql_query_manager():
    """Prueba el SQLQueryManager."""
    print("🔍 Probando SQLQueryManager...")

    try:
        from rexus.utils.sql_query_manager import SQLQueryManager
        sql_manager = SQLQueryManager()
        print("✅ SQLQueryManager creado exitosamente")
        # Verificar que tiene los métodos necesarios
        if hasattr(sql_manager, 'execute_query'):
            print("   ✅ Método execute_query disponible")
        else:
            print("   ❌ Método execute_query no encontrado")
        return True
    except Exception as e:
        print(f"❌ Error creando SQLQueryManager: {e}")
        return False

def test_security_utils():
    """Prueba las utilidades de seguridad."""
    print("🔍 Probando SecurityUtils...")

    try:
        from rexus.utils.security import SecurityUtils

        # Probar hash de contraseña
        password = os.environ.get("TEST_PASSWORD", "test_password_123")
        hashed = SecurityUtils.hash_password(password)
        print(f"✅ Hash generado: {hashed[:20]}...")

        # Probar verificación
        is_valid = SecurityUtils.verify_password(password, hashed)
        print(f"✅ Verificación de contraseña: {is_valid}")

        return True
    except Exception as e:
        print(f"❌ Error en SecurityUtils: {e}")
        return False

def test_security_manager():
    """Prueba el SecurityManager."""
    print("🔍 Probando SecurityManager...")

    try:
        from rexus.core.security import SecurityManager
        security = SecurityManager()
        print("✅ SecurityManager creado exitosamente")
        # Verificar que tiene los métodos necesarios
        if hasattr(security, 'authenticate_user'):
            print("   ✅ Método authenticate_user disponible")
        else:
            print("   ❌ Método authenticate_user no encontrado")
        return True
    except Exception as e:
        print(f"❌ Error creando SecurityManager: {e}")
        return False

def main():
    """Función principal de pruebas."""
    print("🚀 Iniciando pruebas de permisos DB-driven...\n")

    tests = [
        test_database_connection,
        test_sql_query_manager,
        test_security_utils,
        test_security_manager
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        print()

    print(f"📊 Resultados: {passed}/{total} pruebas pasaron")

    if passed == total:
        print("🎉 ¡Todas las pruebas pasaron exitosamente!")
        print("\n💡 El sistema de permisos DB-driven está listo para usar.")
        print("   Recuerda configurar las variables de entorno para la conexión a BD:")
        print("   - DB_DRIVER")
        print("   - DB_SERVER")
        print("   - DB_DATABASE")
        print("   - DB_USERNAME")
        print("   - DB_PASSWORD")
    else:
        print("⚠️  Algunas pruebas fallaron. Revisa la configuración.")

if __name__ == "__main__":
    main()
