#!/usr/bin/env python3
"""
Test simple del modulo obras
"""

import sys
import os
import traceback
from pathlib import Path

# Configurar entorno
sys.path.insert(0, str(Path(__file__).parent.parent))
os.environ['PYTHONIOENCODING'] = 'utf-8'

def test_obras():
    """Test simple de obras."""

    try:
        print("=== TEST OBRAS ===")

        print("1. Suprimiendo logs...")
        import logging
        logging.getLogger().setLevel(logging.CRITICAL)

        print("2. Test import...")
        from rexus.modules.obras.view import ObrasModernView
        print("   Import OK")

        print("3. Test instanciacion...")
        try:
            instance = ObrasModernView()
            print("   Instanciacion OK")

            if hasattr(instance, 'deleteLater'):
                instance.deleteLater()

        except Exception as e:
            print(f"   ERROR en instanciacion: {str(e)}")
            traceback.print_exc()
            return False

        print("=== TEST COMPLETADO ===")
        return True

    except Exception as e:
        print(f"ERROR GENERAL: {str(e)}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_obras()
    print(f"Exitoso: {success}")
