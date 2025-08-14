#!/usr/bin/env python3
"""
Probar el flujo completo de login
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Configurar path del proyecto
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Cargar variables de entorno
load_dotenv()

def test_complete_login_flow():
    """Probar el flujo completo de login como en la aplicación real"""
    print("PRUEBA COMPLETA DEL FLUJO DE LOGIN")
    print("=" * 50)

    try:
        # 1. Inicializar sistema de seguridad
        print("1. Inicializando sistema de seguridad...")
        from src.core.security import initialize_security_manager

        try:
            security_manager = initialize_security_manager()
            print("   OK: Sistema de seguridad inicializado")
        except Exception as e:
            print(f"   FALLO: {e}")
            print("   Continuando con SecurityManager simple...")
            from src.core.security import SecurityManager
            security_manager = SecurityManager()

        # 2. Simular login desde LoginDialog
        print(f"\n2. Simulando login con admin/admin...")

        # SEGURIDAD: No usar contraseñas hardcodeadas
        import getpass
        username = input("Usuario: ")
        password = getpass.getpass("Contraseña: ")

        # AuthManager se encarga de la autenticación
        from src.core.auth import get_auth_manager
        auth_manager = get_auth_manager()
        user = auth_manager.authenticate_user(username, password)

        if user:
            print(f"   OK: AuthManager autenticó usuario: {user['username']}")

            # Simular on_login_success de app.py
            print(f"\n3. Simulando on_login_success...")

            # Verificar que security_manager tenga el usuario
            if security_manager:
                user_data = security_manager.get_current_user()
                if not user_data:
                    print("   ERROR: No se pudo obtener datos del usuario desde SecurityManager")

                    # Intentar login directo en SecurityManager
                    print("   Intentando login directo en SecurityManager...")
                    login_result = security_manager.login(username, password)
                    if login_result:
                        print("   OK: SecurityManager login exitoso")
                        user_data = security_manager.get_current_user()
                        if user_data:
                            print(f"   OK: Datos del usuario obtenidos: {user_data}")
                        else:
                            print("   ERROR: Aún no se pueden obtener datos del usuario")
                    else:
                        print("   ERROR: SecurityManager login falló")
                else:
                    print(f"   OK: Datos del usuario desde SecurityManager: {user_data}")

                # Simular obtención de módulos
                if user_data:
                    print(f"\n4. Obteniendo módulos permitidos...")
                    modulos_permitidos = security_manager.get_user_modules(user_data["id"])
                    print(f"   Módulos: {modulos_permitidos}")

                    print(f"\n[CHECK] FLUJO COMPLETO EXITOSO")
                    print(f"Usuario: {user_data['username']}")
                    print(f"Rol: {user_data.get('role', user_data.get('rol', 'N/A'))}")
                    print(f"Módulos: {len(modulos_permitidos)}")
                    return True
        else:
            print("   ERROR: AuthManager no pudo autenticar")
            return False

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_complete_login_flow()

    if success:
        print(f"\n🎉 LOGIN FUNCIONANDO CORRECTAMENTE")
        print("La aplicación debería abrir sin problemas con admin/admin")
    else:
        print(f"\n[ERROR] HAY PROBLEMAS EN EL LOGIN")
        print("Revisar los errores mostrados arriba")
