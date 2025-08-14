#!/usr/bin/env python3
"""
Test basico de instanciacion de modulos
"""

import sys
import os
from pathlib import Path

# Configurar codificacion para Windows
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Anadir el directorio raiz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_module_instantiation():
    """Prueba instanciacion de modulos uno por uno."""

    modules = ['inventario', 'obras', 'usuarios', 'compras', 'pedidos',
               'herrajes', 'vidrios', 'logistica', 'auditoria',
               'configuracion', 'mantenimiento']

    results = {}

    for module_name in modules:
        try:
            print(f"Testeando {module_name}...")

            # Import view
            view_module = __import__(f'rexus.modules.{module_name}.view', fromlist=[''])

            # Buscar clases View
            view_classes = [name for name in dir(view_module) if 'View' in name and \
                not name.startswith('_')]

            if not view_classes:
                results[module_name] = "ERROR: No view classes found"
                continue

            # Intentar instanciar primera clase view
            view_class_name = view_classes[0]
            view_class = getattr(view_module, view_class_name)

            try:
                # Intentar instanciacion
                if 'parent' in view_class.__init__.__code__.co_varnames:
                    instance = view_class(parent=None)
                else:
                    instance = view_class()

                results[module_name] = f"OK: {view_class_name} instanciado correctamente"

                # Cleanup
                if hasattr(instance, 'deleteLater'):
                    instance.deleteLater()

            except Exception as e:
                results[module_name] = f"ERROR instanciando {view_class_name}: {str(e)}"

        except Exception as e:
            results[module_name] = f"ERROR importando: {str(e)}"

    # Mostrar resultados
    print("\n" + "="*60)
    print("RESULTADOS DEL TEST DE INSTANCIACION")
    print("="*60)

    ok_count = 0
    error_count = 0

    for module, result in results.items():
        if "OK:" in result:
            print(f"[OK] {module}: {result}")
            ok_count += 1
        else:
            print(f"[ERROR] {module}: {result}")
            error_count += 1

    print(f"\nRESUMEN: {ok_count} OK, {error_count} ERROR")

    return error_count == 0

if __name__ == "__main__":
    success = test_module_instantiation()
    if success:
        print("\nTodos los modulos pueden instanciarse correctamente!")
    else:
        print("\nAlgunos modulos tienen problemas de instanciacion.")
