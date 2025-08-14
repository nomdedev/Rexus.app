#!/usr/bin/env python3
"""
Test específico para obras con captura de errores
"""

import sys
import os
import traceback
from pathlib import Path

# Configurar entorno
sys.path.insert(0, str(Path(__file__).parent.parent))
os.environ['PYTHONIOENCODING'] = 'utf-8'

def test_obras_especifico():
    """Test específico de obras."""

    try:
        print("Test obras iniciado...")

        # Suprimir logs
        import logging
        logging.getLogger().setLevel(logging.CRITICAL)

        print("Importando ObrasModernView...")
        from rexus.modules.obras.view import ObrasModernView
        print("Import completado")

        print("Creando instancia...")
        try:
            instance = ObrasModernView()
            print("Instancia creada exitosamente")

            # Test método crítico
            if hasattr(instance, 'cargar_obras_en_tabla'):
                print("Método cargar_obras_en_tabla: DISPONIBLE")
            else:
                print("Método cargar_obras_en_tabla: FALTANTE")

            # Cleanup
            if hasattr(instance, 'deleteLater'):
                instance.deleteLater()

            return True

        except Exception as e:
            print(f"Error en instanciación: {str(e)}")
            print("Traceback completo:")
            traceback.print_exc()
            return False

    except Exception as e:
        print(f"Error en import: {str(e)}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_obras_especifico()
    print(f"Test resultado: {'EXITOSO' if success else 'FALLIDO'}")
