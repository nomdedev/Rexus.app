#!/usr/bin/env python3
"""
Punto de entrada principal para Rexus.app
"""

import sys
import os
from pathlib import Path

def setup_environment():
    """Configura el entorno de la aplicación."""
    root_dir = Path(__file__).parent
    os.chdir(root_dir)
    sys.path.insert(0, str(root_dir))
    
    # Cargar variables de entorno
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    
    return True

def main():
    """Función principal."""
    if not setup_environment():
        sys.exit(1)
    
    try:
        from rexus.main.app import main as app_main
        app_main()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()