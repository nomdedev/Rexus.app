#!/usr/bin/env python3
"""
Analiza qué archivos de rexus/core se utilizan realmente en el proyecto
Identifica archivos huérfanos o no utilizados
"""

import os
import re
from pathlib import Path

def get_core_files():
    """Obtiene lista de archivos en rexus/core"""
    core_path = Path('rexus/core')
    files = []
    
    if core_path.exists():
        for file_path in core_path.glob('*.py'):
            if file_path.name != '__init__.py':
                files.append(file_path.stem)
    
    return files

def search_imports_in_project(core_file):
    """Busca imports de un archivo específico de core en todo el proyecto"""
    import_patterns = [
        rf'from\s+.*\.core\.{core_file}\s+import',
        rf'from\s+.*core\.{core_file}\s+import',
        rf'from\s+rexus\.core\.{core_file}\s+import',
        rf'import\s+.*\.core\.{core_file}',
        rf'import\s+.*core\.{core_file}',
        rf'import\s+rexus\.core\.{core_file}',
    ]
    
    found_in = []
    
    # Buscar en rexus/
    for py_file in Path('rexus').rglob('*.py'):
        if 'core' in str(py_file) and core_file in str(py_file):
            continue  # Skip self-references
            
        try:
            with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
                for pattern in import_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        found_in.append(str(py_file))
                        break
        except Exception:
            continue
    
    # Buscar en main.py
    if Path('main.py').exists():
        try:
            with open('main.py', 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                for pattern in import_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        found_in.append('main.py')
                        break
        except Exception:
            pass
    
    return found_in

def analyze_core_usage():
    """Analiza el uso de archivos core"""
    core_files = get_core_files()
    
    print("=== ANÁLISIS DE USO - REXUS/CORE ===\n")
    print(f"Total archivos en core: {len(core_files)}\n")
    
    used_files = []
    unused_files = []
    
    for core_file in sorted(core_files):
        print(f"Analizando: {core_file}")
        
        usage = search_imports_in_project(core_file)
        
        if usage:
            used_files.append(core_file)
            print(f"  ✅ USADO - Encontrado en {len(usage)} archivos:")
            for file_path in usage[:3]:  # Show first 3
                print(f"    - {file_path}")
            if len(usage) > 3:
                print(f"    ... y {len(usage) - 3} más")
        else:
            unused_files.append(core_file)
            print(f"  ❌ NO USADO - Sin imports encontrados")
        
        print()
    
    print("=== RESUMEN ===")
    print(f"Archivos utilizados: {len(used_files)}")
    print(f"Archivos sin uso: {len(unused_files)}")
    
    if unused_files:
        print(f"\n🗑️ ARCHIVOS POSIBLEMENTE HUÉRFANOS:")
        for file_name in unused_files:
            print(f"  - {file_name}.py")
        
        print(f"\n⚠️  RECOMENDACIÓN:")
        print("Revisar estos archivos manualmente antes de eliminarlos.")
        print("Pueden ser utilizados dinámicamente o ser archivos de desarrollo.")
    
    return {'used': used_files, 'unused': unused_files}

def get_main_files():
    """Obtiene archivos en rexus/main"""
    main_path = Path('rexus/main')
    files = []
    
    if main_path.exists():
        for file_path in main_path.glob('*.py'):
            if file_path.name != '__init__.py':
                files.append(file_path.name)
    
    return files

def analyze_main_usage():
    """Analiza archivos en rexus/main"""
    main_files = get_main_files()
    
    print(f"\n=== ANÁLISIS DE USO - REXUS/MAIN ===")
    print(f"Total archivos en main: {len(main_files)}\n")
    
    for main_file in sorted(main_files):
        file_stem = Path(main_file).stem
        print(f"Archivo: {main_file}")
        
        # Buscar references al archivo
        found_refs = []
        for py_file in Path('rexus').rglob('*.py'):
            if main_file in str(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if file_stem in content or main_file in content:
                        found_refs.append(str(py_file))
            except Exception:
                continue
        
        if found_refs:
            print(f"  ✅ Referenciado en {len(found_refs)} archivos")
        else:
            print(f"  ❌ Sin referencias encontradas")
        
        print()

if __name__ == "__main__":
    # Analizar core
    core_analysis = analyze_core_usage()
    
    # Analizar main
    analyze_main_usage()