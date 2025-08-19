#!/usr/bin/env python3
"""
Auditoria Simple de Errores - Rexus.app
"""

import sys
import traceback
import importlib

def test_module(module_path, module_name):
    """Testa un modulo y captura errores."""
    print(f"\n{'-'*50}")
    print(f"TESTING MODULE: {module_name}")
    print(f"{'-'*50}")
    
    errors = []
    
    # Test imports
    try:
        print(f"Importing {module_path}.model...")
        model_module = importlib.import_module(f"{module_path}.model")
        print("  Model import: OK")
    except Exception as e:
        error = f"MODEL IMPORT ERROR: {str(e)}"
        print(f"  {error}")
        errors.append(error)
    
    try:
        print(f"Importing {module_path}.view...")
        view_module = importlib.import_module(f"{module_path}.view")
        print("  View import: OK")
    except Exception as e:
        error = f"VIEW IMPORT ERROR: {str(e)}"
        print(f"  {error}")
        errors.append(error)
    
    try:
        print(f"Importing {module_path}.controller...")
        controller_module = importlib.import_module(f"{module_path}.controller")
        print("  Controller import: OK")
    except Exception as e:
        error = f"CONTROLLER IMPORT ERROR: {str(e)}"
        print(f"  {error}")
        errors.append(error)
    
    # Test instantiation
    if 'model_module' in locals():
        try:
            model_class_name = f"{module_name.title()}Model"
            model_class = getattr(model_module, model_class_name, None)
            if model_class:
                model_instance = model_class()
                print("  Model instantiation: OK")
            else:
                error = f"MODEL CLASS NOT FOUND: {model_class_name}"
                print(f"  {error}")
                errors.append(error)
        except Exception as e:
            error = f"MODEL INSTANTIATION ERROR: {str(e)}"
            print(f"  {error}")
            errors.append(error)
    
    return errors

def main():
    """Funcion principal."""
    print("AUDITORIA DE MODULOS REXUS.APP")
    print("=" * 60)
    
    modules = [
        ("rexus.modules.inventario", "inventario"),
        ("rexus.modules.compras", "compras"),  
        ("rexus.modules.administracion", "administracion"),
        ("rexus.modules.auditoria", "auditoria"),
        ("rexus.modules.obras", "obras"),
        ("rexus.modules.pedidos", "pedidos"),
    ]
    
    all_errors = {}
    
    for module_path, module_name in modules:
        errors = test_module(module_path, module_name)
        if errors:
            all_errors[module_name] = errors
    
    print(f"\n{'='*60}")
    print("RESUMEN DE ERRORES")
    print(f"{'='*60}")
    
    if all_errors:
        for module, errors in all_errors.items():
            print(f"\nMODULE {module.upper()}: {len(errors)} errors")
            for i, error in enumerate(errors, 1):
                print(f"  {i}. {error}")
    else:
        print("NO ERRORS FOUND")
    
    return all_errors

if __name__ == "__main__":
    try:
        errors = main()
    except Exception as e:
        print(f"ERROR IN AUDIT: {e}")
        traceback.print_exc()