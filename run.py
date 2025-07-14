#!/usr/bin/env python3
"""
Script principal para ejecutar la aplicación
Punto de entrada simplificado
"""

import os
import sys
from pathlib import Path

# Añadir src al path
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))


def main():
    """Función principal de la aplicación"""
    try:
        from src.main.app import main as app_main

        app_main()
    except ImportError as e:
        print(f"Error importando la aplicación: {e}")
        print("Asegúrate de que todas las dependencias estén instaladas:")
        print("pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"Error ejecutando la aplicación: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
