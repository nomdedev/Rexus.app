#!/usr/bin/env python3
"""
Test detallado del módulo obras para identificar errores específicos
"""

import sys
import os
import traceback
from pathlib import Path

# Configurar entorno
sys.path.insert(0, str(Path(__file__).parent.parent))
os.environ['PYTHONIOENCODING'] = 'utf-8'

def test_obras_step_by_step():
    """Test paso a paso del módulo obras."""

    try:
        print("=== TEST DETALLADO MÓDULO OBRAS ===")

        print("1. Suprimiendo logs...")
        import logging
        logging.getLogger().setLevel(logging.CRITICAL)

        print("2. Test import básico...")
        from rexus.modules.obras import view
        print("   ✓ Import módulo obras OK")

        print("3. Test import clase principal...")
        from rexus.modules.obras.view import ObrasModernView
        print("   ✓ Import ObrasModernView OK")

        print("4. Test dependencias críticas...")
        dependencies = [
            'PyQt6.QtWidgets',
            'PyQt6.QtCore',
            'PyQt6.QtGui',
            'rexus.ui.standard_components',
            'rexus.utils.unified_sanitizer',
            'rexus.utils.message_system'
        ]

        for dep in dependencies:
            try:
                __import__(dep)
                print(f"   ✓ {dep} OK")
            except Exception as e:
                print(f"   ✗ {dep} ERROR: {str(e)}")

        print("5. Test instanciación...")
        try:
            # Intentar instanciación sin parent
            instance = ObrasModernView()
            print("   ✓ Instanciación sin parent OK")

            # Test con parent=None
            instance2 = ObrasModernView(parent=None)
            print("   ✓ Instanciación con parent=None OK")

            # Cleanup
            if hasattr(instance, 'deleteLater'):
                instance.deleteLater()
            if hasattr(instance2, 'deleteLater'):
                instance2.deleteLater()

        except Exception as e:
            print(f"   ✗ Error en instanciación: {str(e)}")
            traceback.print_exc()
            return False

        print("6. Test métodos críticos...")
        try:
            instance = ObrasModernView()
            critical_methods = [
                'configurar_ui',
                'configurar_pestanas',
                'crear_header',
                'crear_pestana_obras',
                'crear_pestana_cronograma',
                'crear_pestana_presupuestos'
            ]

            for method in critical_methods:
                if hasattr(instance, method):
                    print(f"   ✓ Método {method}: disponible")
                else:
                    print(f"   ✗ Método {method}: FALTANTE")

        except Exception as e:
            print(f"   ✗ Error en test de métodos: {str(e)}")

        print("\n=== RESULTADO: TODOS LOS TESTS COMPLETADOS ===")
        return True

    except Exception as e:
        print(f"\n✗ ERROR GENERAL: {str(e)}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_obras_step_by_step()
    print(f"\nTest finalizado - Exitoso: {success}")
