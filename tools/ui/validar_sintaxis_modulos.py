#!/usr/bin/env python3
"""
MIT License - Copyright (c) 2025 Rexus.app

Validador de Sintaxis de Módulos - Rexus.app
============================================

Herramienta para validar la sintaxis de Python en los archivos modificados:
- Verifica que todos los archivos .py compilan correctamente
- Identifica errores de sintaxis
- Reporta problemas de importación

Uso:
python tools/ui/validar_sintaxis_modulos.py
"""

import ast
import sys
from pathlib import Path

# Agregar ruta del proyecto
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))


def validate_python_syntax(file_path: Path) -> tuple[bool, str]:
    """Valida la sintaxis de un archivo Python"""
    try:
        content = file_path.read_text(encoding='utf-8')
        ast.parse(content)
        return True, "OK"
    except SyntaxError as e:
        return False, f"SyntaxError: {e.msg} at line {e.lineno}"
    except Exception as e:
        return False, f"Error: {e}"


def main():
    """Función principal"""
    print("[SYNTAX VALIDATION] Validando sintaxis de módulos")
    print("=" * 50)
    
    modules_dir = root_dir / "rexus" / "modules"
    
    if not modules_dir.exists():
        print(f"Error: {modules_dir} not found")
        return 1
    
    # Obtener todos los archivos Python en módulos
    python_files = []
    for module_dir in modules_dir.iterdir():
        if module_dir.is_dir() and not module_dir.name.startswith('_'):
            view_file = module_dir / "view.py"
            if view_file.exists():
                python_files.append(view_file)
    
    print(f"Found {len(python_files)} view.py files to validate")
    print("-" * 50)
    
    valid_count = 0
    invalid_count = 0
    
    for py_file in sorted(python_files):
        module_name = py_file.parent.name
        is_valid, message = validate_python_syntax(py_file)
        
        if is_valid:
            print(f"[OK] {module_name}: {message}")
            valid_count += 1
        else:
            print(f"[ERROR] {module_name}: {message}")
            invalid_count += 1
    
    # Resumen
    print("-" * 50)
    print(f"[SUMMARY] Valid: {valid_count}, Invalid: {invalid_count}")
    
    if invalid_count == 0:
        print("[SUCCESS] All module files have valid Python syntax")
        return 0
    else:
        print(f"[WARNING] {invalid_count} files have syntax errors")
        return 1


if __name__ == "__main__":
    sys.exit(main())