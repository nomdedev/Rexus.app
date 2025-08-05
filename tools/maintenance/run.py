#!/usr/bin/env python3
"""
Rexus.app - Script Principal de Ejecución

Punto de entrada unificado para la aplicación.
Maneja configuración de entorno y fallback a modo demo.

Usage:
    python run.py

Author: Rexus Development Team
Version: 2.0.0
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Configurar path del proyecto - ir dos niveles arriba para llegar a la raíz
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def setup_environment():
    """Configura variables de entorno por defecto si no existen"""
    # Cargar variables desde .env (si existe)
    env_path = os.path.join(project_root, ".env")
    if os.path.exists(env_path):
        load_dotenv(env_path)
    else:
        print(
            "[ADVERTENCIA] No se encontró archivo .env en el directorio del proyecto."
        )

    # Requerir que las variables críticas estén definidas en el entorno
    required_env_vars = [
        "DB_SERVER",
        "DB_DRIVER",
        "DB_USERNAME",
        "DB_PASSWORD",
        "SECRET_KEY",
        "JWT_SECRET_KEY",
        "ENCRYPTION_KEY",
    ]
    missing = [key for key in required_env_vars if not os.environ.get(key)]
    if missing:
        print(f"\n[ERROR] Faltan variables de entorno críticas: {', '.join(missing)}")
        print(
            "Por favor configura todas las variables requeridas en un archivo .env antes de ejecutar la app."
        )
        sys.exit(1)


def main():
    """Función principal unificada de la aplicación"""
    # Configurar encoding para Windows
    if sys.platform.startswith("win"):
        os.system("chcp 65001 >nul 2>&1")

    print("Iniciando Rexus.app v2.0.0...")

    try:
        # Configurar entorno
        setup_environment()

        # Importar y ejecutar aplicación principal
        from rexus.main.app import main as app_main

        app_main()

    except ImportError as e:
        print(f"Error importando la aplicacion: {e}")
        print("Asegurate de que todas las dependencias esten instaladas:")
        print("   pip install -r requirements.txt")
        sys.exit(1)

    except Exception as e:
        print(f"Error ejecutando la aplicacion: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
