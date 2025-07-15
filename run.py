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

# Configurar path del proyecto
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def setup_environment():
    """Configura variables de entorno por defecto si no existen"""
    default_env_vars = {
        "DB_PASSWORD": "default_password",
        "SECRET_KEY": "default_secret_key", 
        "JWT_SECRET_KEY": "default_jwt_secret",
        "ENCRYPTION_KEY": "default_encryption_key"
    }
    
    for key, default_value in default_env_vars.items():
        if not os.getenv(key):
            os.environ[key] = default_value


def main():
    """Función principal unificada de la aplicación"""
    # Configurar encoding para Windows
    if sys.platform.startswith('win'):
        os.system('chcp 65001 >nul 2>&1')
    
    print("Iniciando Rexus.app v2.0.0...")
    
    try:
        # Configurar entorno
        setup_environment()
        
        # Importar y ejecutar aplicación principal
        from src.main.app import main as app_main
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