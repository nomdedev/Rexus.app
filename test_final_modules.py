#!/usr/bin/env python3
"""
Test final de módulos para verificar que todos se pueden importar
"""

import sys
import os
from pathlib import Path

# Agregar path del proyecto
sys.path.insert(0, os.getcwd())

def test_module_import(module_name):
    """Testa la importación de un módulo"""
    try:
        module_path = f"rexus.modules.{module_name}.view"
        module = __import__(module_path, fromlist=[''])
        
        # Buscar clase principal del módulo
        view_class_name = f"{module_name.title()}View"
        
        if hasattr(module, view_class_name):
            view_class = getattr(module, view_class_name)
            return True, f"Clase {view_class_name} encontrada"
        else:
            # Buscar cualquier clase que termine en View
            view_classes = [name for name in dir(module) if name.endswith('View') and not name.startswith('_')]
            if view_classes:
                return True, f"Clases encontradas: {', '.join(view_classes)}"
            else:
                return False, "No se encontraron clases View"
                
    except ImportError as e:
        return False, f"ImportError: {e}"
    except Exception as e:
        return False, f"Error: {e}"

def main():
    """Función principal"""
    print("TEST FINAL DE MÓDULOS REXUS")
    print("=" * 50)
    
    modules = [
        "administracion", "auditoria", "compras", "configuracion",
        "herrajes", "inventario", "logistica", "mantenimiento", 
        "obras", "pedidos", "usuarios", "vidrios"
    ]
    
    success_count = 0
    fail_count = 0
    
    for module in modules:
        success, message = test_module_import(module)
        status = "[OK]" if success else "[FAIL]"
        
        print(f"{module:15} | {status}")
        if not success:
            print(f"                 | {message}")
        
        if success:
            success_count += 1
        else:
            fail_count += 1
    
    print("=" * 50)
    print(f"TOTAL: {len(modules)} módulos")
    print(f"EXITOSOS: {success_count}")
    print(f"FALLIDOS: {fail_count}")
    
    if fail_count == 0:
        print("\n✓ TODOS LOS MÓDULOS SE PUEDEN IMPORTAR CORRECTAMENTE")
    else:
        print(f"\n✗ {fail_count} MÓDULOS TIENEN PROBLEMAS")
    
    print("=" * 50)

if __name__ == "__main__":
    main()