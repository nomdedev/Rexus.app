#!/usr/bin/env python3
"""
Test silencioso de modulos para identificar errores especificos
"""

import sys
import os
import logging
from pathlib import Path

# Suprimir logs molestos
logging.getLogger().setLevel(logging.CRITICAL)
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Anadir el directorio raiz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_modules():
    """Test de todos los modulos."""

    modules = {
        'inventario': 'InventarioView',
        'obras': 'ObrasView',
        'usuarios': 'UsuariosView',
        'compras': 'ComprasView',
        'pedidos': 'PedidosView',
        'herrajes': 'HerrajesView',
        'vidrios': 'VidriosView',
        'logistica': 'LogisticaView',
        'auditoria': 'AuditoriaView',
        'configuracion': 'ConfiguracionView',
        'mantenimiento': 'MantenimientoView'
    }

    results = {}

    for module_name, view_class_name in modules.items():
        try:
            # Import view module
            view_module = __import__(f'rexus.modules.{module_name}.view', fromlist=[''])

            # Get view class
            if hasattr(view_module, view_class_name):
                view_class = getattr(view_module, view_class_name)

                try:
                    # Try instantiation without parent
                    instance = view_class()
                    results[module_name] = "OK"

                    # Cleanup
                    if hasattr(instance, 'deleteLater'):
                        instance.deleteLater()

                except Exception as e:
                    # Try with parent=None
                    try:
                        instance = view_class(parent=None)
                        results[module_name] = "OK_WITH_PARENT"

                        if hasattr(instance, 'deleteLater'):
                            instance.deleteLater()

                    except Exception as e2:
                        results[module_name] = f"INST_ERROR: {str(e)[:50]}"

            else:
                results[module_name] = f"CLASS_NOT_FOUND: {view_class_name}"

        except Exception as e:
            results[module_name] = f"IMPORT_ERROR: {str(e)[:50]}"

    return results

def main():
    print("TEST DE MODULOS REXUS.APP")
    print("=" * 40)

    results = test_modules()

    ok_count = 0
    error_count = 0

    for module, status in results.items():
        if "OK" in status:
            print(f"[OK] {module}: {status}")
            ok_count += 1
        else:
            print(f"[ERROR] {module}: {status}")
            error_count += 1

    print("\n" + "=" * 40)
    print(f"RESUMEN: {ok_count} OK, {error_count} ERRORES")

    return error_count == 0

if __name__ == "__main__":
    success = main()
