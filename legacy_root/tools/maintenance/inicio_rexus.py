#!/usr/bin/env python3
"""
Script de inicio oficial para Rexus.app

Este script asegura que todas las configuraciones estén correctas
antes de iniciar la aplicación principal.
"""

import sys
import os
from pathlib import Path

def setup_environment():
    """Configura el entorno de la aplicación."""
    # Establecer directorio raíz
    root_dir = Path(__file__).parent
    os.chdir(root_dir)
    sys.path.insert(0, str(root_dir))

    print(f"[SETUP] Directorio raíz: {root_dir}")
    print(f"[SETUP] Directorio actual: {os.getcwd()}")

    # Cargar variables de entorno
    try:
        from dotenv import load_dotenv
        env_loaded = load_dotenv()
        if env_loaded:
            print("[OK] Variables de entorno cargadas desde .env")
        else:
            print("[WARNING] Archivo .env no encontrado, usando variables del sistema")
    except ImportError:
        print("[ERROR] python-dotenv no instalado")
        print("Ejecute: pip install python-dotenv")
        return False
    except Exception as e:
        print(f"[ERROR] Error cargando variables de entorno: {e}")
        return False

    # Verificar variables críticas
    critical_vars = ['DB_SERVER', 'DB_USERNAME', 'DB_PASSWORD', 'DB_USERS']
    missing_vars = []

    for var in critical_vars:
        if not os.getenv(var):
            missing_vars.append(var)

    if missing_vars:
        print(f"[WARNING] Variables faltantes: {', '.join(missing_vars)}")
        print("[INFO] La aplicación funcionará en modo demo limitado")
    else:
        print("[OK] Todas las variables críticas están configuradas")

    return True

def test_database_connection():
    """Prueba la conexión a la base de datos."""
    try:
        from src.core.database import UsersDatabaseConnection

        print("[TEST] Probando conexión a base de datos...")
        db = UsersDatabaseConnection()
        db.connect()
        print("[OK] Conexión a base de datos exitosa")

        # Probar autenticación
        from src.core.auth import AuthManager
        auth = AuthManager()

        print("[TEST] Verificando usuario admin...")
        admin_result = auth.authenticate_user('admin', 'admin')

        if admin_result:
            print(f"[OK] Usuario admin disponible (ID: {admin_result['id']})")
            return True
        else:
            print("[WARNING] Usuario admin no encontrado o contraseña incorrecta")
            print("[INFO] Puede que necesite ejecutar scripts/setup_admin_simple.py")
            return False

    except Exception as e:
        print(f"[ERROR] Error de base de datos: {e}")
        print("[INFO] La aplicación funcionará en modo de prueba")
        return False

def start_application():
    """Inicia la aplicación principal."""
    try:
        print("[START] Iniciando Rexus.app...")
        from src.main.app import main
        main()
    except KeyboardInterrupt:
        print("\n[EXIT] Aplicación cerrada por el usuario")
    except Exception as e:
        print(f"[ERROR] Error iniciando aplicación: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True

def main():
    """Función principal."""
    print("=" * 50)
    print("[ROCKET] INICIANDO REXUS.APP v2.0.0")
    print("=" * 50)

    # Configurar entorno
    if not setup_environment():
        print("[FATAL] No se pudo configurar el entorno")
        sys.exit(1)

    # Probar conexión BD (no crítico)
    db_ok = test_database_connection()

    if db_ok:
        print("[READY] Sistema completamente operativo")
    else:
        print("[READY] Sistema en modo limitado (sin BD)")

    print("\n" + "=" * 50)
    print("💡 CREDENCIALES DE ACCESO:")
    print("   Usuario: admin")
    print("   Contraseña: admin")
    print("=" * 50 + "\n")

    # Iniciar aplicación
    success = start_application()

    if success:
        print("\n[EXIT] Aplicación cerrada normalmente")
    else:
        print("\n[EXIT] Aplicación cerrada con errores")
        sys.exit(1)

if __name__ == "__main__":
    main()
