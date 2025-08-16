#!/usr/bin/env python3
"""
Test paso a paso para identificar donde falla exactamente
"""

import sys
import os
from pathlib import Path

def main():
    print("=== TEST PASO A PASO ===")

    try:
        print("1. Configurando path...")
        sys.path.insert(0, str(Path(__file__).parent.parent))
        print("   Path configurado OK")

        print("2. Suprimiendo logs...")
        import logging
        logging.getLogger().setLevel(logging.CRITICAL)
        print("   Logs suprimidos OK")

        print("3. Test import rexus...")
        import rexus
        print("   Rexus importado OK")

        print("4. Test import rexus.modules...")
        import rexus.modules
        print("   Modulos importados OK")

        print("5. Test import inventario view...")
        from rexus.modules.inventario.view import InventarioView
        print("   InventarioView importado OK")

        print("6. Test instanciacion...")
        view = InventarioView()
        print("   InventarioView instanciado OK")

        print("7. Test otros modulos...")
        modules_to_test = ['obras', 'usuarios', 'compras', 'pedidos']
        for module in modules_to_test:
            try:
                import importlib
                module_obj = importlib.import_module(f"rexus.modules.{module}.view")
                print(f"   {module}: Import OK")
            except Exception as e:
                print(f"   {module}: Import ERROR - {str(e)}")

        print("\n=== RESULTADO: TODOS LOS TESTS PASARON ===")
        return True

    except Exception as e:
        print(f"\nERROR en paso: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    print(f"\nFinalizado - Exitoso: {success}")
