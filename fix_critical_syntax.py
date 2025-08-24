# -*- coding: utf-8 -*-
"""
Script para corregir errores de sintaxis críticos
que bloquean las importaciones de módulos
"""

import os
import ast

def check_and_fix_critical_files():
    """Identifica y reporta archivos con errores de sintaxis críticos"""
    
    critical_modules = [
        'rexus/modules/configuracion',
        'rexus/modules/usuarios', 
        'rexus/modules/inventario',
        'rexus/modules/obras',
        'rexus/modules/compras',
        'rexus/modules/pedidos'
    ]
    
    syntax_errors = []
    
    print("ESCANEANDO MÓDULOS CRÍTICOS...")
    
    for module_dir in critical_modules:
        for file_name in ['controller.py', 'model.py', 'view.py']:
            file_path = os.path.join(module_dir, file_name)
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    ast.parse(content)
                    print(f"✓ {file_path}")
                except SyntaxError as e:
                    error_info = f"{file_path}:{e.lineno} - {e.msg}"
                    syntax_errors.append(error_info)
                    print(f"✗ {error_info}")
                except Exception as e:
                    error_info = f"{file_path} - {str(e)}"
                    syntax_errors.append(error_info)
                    print(f"✗ {error_info}")
    
    print(f"\nTOTAL ERRORES CRÍTICOS: {len(syntax_errors)}")
    for error in syntax_errors:
        print(f"  {error}")
    
    return syntax_errors

if __name__ == "__main__":
    os.chdir(r"D:\martin\Rexus.app")
    check_and_fix_critical_files()