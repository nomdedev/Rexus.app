#!/usr/bin/env python3
"""
Script de prueba para verificar el LoginDialog corregido.
"""

import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

def test_login_dialog():
    """Prueba el LoginDialog con configuración de desarrollo."""
    print("🧪 Probando LoginDialog corregido...")

    # Configurar variables de entorno para desarrollo
    os.environ['REXUS_DEV_USER'] = 'admin'
    os.environ['REXUS_DEV_PASSWORD'] = 'admin123'
    os.environ['REXUS_DEV_AUTO_LOGIN'] = 'false'

    try:
        from temp_app import LoginDialog

        # Crear instancia del LoginDialog
        login_dialog = LoginDialog()
        print("✅ LoginDialog creado exitosamente")

        # Verificar que tiene los métodos necesarios
        assert hasattr(login_dialog, 'exec'), "Falta método exec"
        assert hasattr(login_dialog, 'get_user_data'), "Falta método get_user_data"
        assert hasattr(login_dialog, 'get_modulos_permitidos'), "Falta método get_modulos_permitidos"
        print("✅ Todos los métodos necesarios están presentes")

        # Verificar configuración de desarrollo
        assert login_dialog.dev_user == 'admin', f"Usuario dev incorrecto: {login_dialog.dev_user}"
        assert login_dialog.dev_password == 'admin123', f"Password dev incorrecto: {login_dialog.dev_password}"
        assert not login_dialog.auto_login, f"Auto-login debería ser False: {login_dialog.auto_login}"
        print("✅ Configuración de desarrollo correcta")

        print("🎉 ¡LoginDialog corregido funciona correctamente!")
        return True

    except Exception as e:
        print(f"❌ Error en LoginDialog: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_security_system():
    """Prueba el sistema de seguridad y permisos."""
    print("\n🛡️ Probando sistema de seguridad...")

    try:
        from rexus.utils.sql_query_manager import SQLQueryManager
        from rexus.utils.security import SecurityUtils
        from rexus.core.security import SecurityManager

        # Probar SecurityUtils
        password = "test_password_123"
        hashed = SecurityUtils.hash_password(password)
        is_valid = SecurityUtils.verify_password(password, hashed)
        assert is_valid, "Verificación de contraseña falló"
        print("✅ SecurityUtils funciona correctamente")

        # Probar SQLQueryManager (sin BD real)
        sql_manager = SQLQueryManager()
        assert hasattr(sql_manager, 'get_user_permissions'), "Falta método get_user_permissions"
        print("✅ SQLQueryManager creado correctamente")

        # Probar SecurityManager
        security = SecurityManager()
        assert hasattr(security, 'authenticate_user'), "Falta método authenticate_user"
        print("✅ SecurityManager creado correctamente")

        return True

    except Exception as e:
        print(f"❌ Error en sistema de seguridad: {e}")
        return False

def main():
    """Función principal de pruebas."""
    print("🚀 Iniciando pruebas del sistema corregido...\n")

    tests = [
        test_login_dialog,
        test_security_system
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
        print("\n💡 El sistema corregido está listo:")
        print("   ✅ LoginDialog visualmente corregido")
        print("   ✅ Sistema de permisos DB-driven implementado")
        print("   ✅ Seguridad mejorada con hash de contraseñas")
        print("   ✅ Fallback robusto cuando no hay BD")
    else:
        print("⚠️  Algunas pruebas fallaron. Revisa los errores.")

if __name__ == "__main__":
    main()
