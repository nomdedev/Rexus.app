#!/usr/bin/env python3
"""
Script para detectar y corregir problemas de imports
"""

import os
import importlib.util
from pathlib import Path

def test_module_imports(module_path):
    """Prueba si un módulo se puede importar correctamente"""
    try:
        spec = importlib.util.spec_from_file_location("test_module", module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return True, None
    except Exception as e:
        return False, str(e)

def main():
    print("DETECTANDO PROBLEMAS DE IMPORTS...")
    
    # Probar módulos críticos que migré
    critical_modules = [
        "rexus/models/productos_model.py",
        "rexus/core/auth.py", 
        "rexus/core/security.py",
        "rexus/modules/13_notificaciones/model.py",
        "rexus/modules/12_administracion/model.py",
        "rexus/modules/07_vidrios/model.py",
        "rexus/modules/02_inventario/submodules/reservas_manager.py"
    ]
    
    issues_found = []
    
    for module_path in critical_modules:
        full_path = Path(module_path)
        if not full_path.exists():
            issues_found.append(f"ARCHIVO NO EXISTE: {module_path}")
            continue
            
        print(f"Probando: {module_path}")
        success, error = test_module_imports(full_path)
        
        if not success:
            issues_found.append(f"ERROR IMPORT: {module_path} - {error}")
            print(f"  FALLO: {error}")
        else:
            print(f"  OK")
    
    print(f"\nRESUMEN:")
    print(f"Módulos probados: {len(critical_modules)}")
    print(f"Problemas encontrados: {len(issues_found)}")
    
    if issues_found:
        print(f"\nPROBLEMAS:")
        for issue in issues_found:
            print(f"  {issue}")
    else:
        print("Todos los modulos se pueden importar correctamente!")

if __name__ == "__main__":
    main()