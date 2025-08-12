#!/usr/bin/env python3
"""
Verificador MIT License Headers - Rexus.app
==========================================

Verifica que todos los archivos de interfaz tengan headers MIT License completos
"""

from pathlib import Path

def verificar_mit_header(file_path):
    """Verifica si un archivo tiene MIT License header"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read(1000)  # Leer primeros 1000 caracteres
        
        mit_indicators = [
            "MIT License",
            "Copyright (c)",
            "Permission is hereby granted"
        ]
        
        tiene_mit = all(indicator in content for indicator in mit_indicators)
        return tiene_mit
        
    except Exception:
        return False

def main():
    """Verificar headers MIT en archivos de interfaz"""
    
    print("[MIT CHECK] Verificando headers MIT License")
    print("=" * 50)
    
    # Patrones de archivos a verificar
    patterns = [
        "rexus/modules/**/view*.py",
        "rexus/modules/**/*dialog*.py", 
        "rexus/core/login_dialog.py",
        "rexus/main/app.py",
        "rexus/ui/*.py",
        "rexus/utils/*dialog*.py"
    ]
    
    total_archivos = 0
    con_mit_header = 0
    sin_mit_header = []
    
    for pattern in patterns:
        for file_path in Path('.').glob(pattern):
            if file_path.is_file() and not file_path.name.startswith('__'):
                total_archivos += 1
                
                if verificar_mit_header(file_path):
                    status = "[OK] CON MIT"
                    con_mit_header += 1
                else:
                    status = "[MISSING] SIN MIT"
                    sin_mit_header.append(str(file_path))
                
                print(f"{status:15} {file_path}")
    
    print("\n" + "=" * 50)
    print("[SUMMARY] RESUMEN")
    print("=" * 50)
    
    print(f"Total archivos verificados: {total_archivos}")
    print(f"Con MIT License: {con_mit_header}")
    print(f"Sin MIT License: {len(sin_mit_header)}")
    
    if sin_mit_header:
        print(f"\n[PENDING] Archivos sin MIT License:")
        for archivo in sin_mit_header:
            print(f"  - {archivo}")
    
    if total_archivos > 0:
        cobertura = (con_mit_header / total_archivos) * 100
        print(f"\n[RESULT] Cobertura MIT License: {cobertura:.1f}%")
    
    if len(sin_mit_header) == 0:
        print("[SUCCESS] Todos los archivos tienen MIT License!")
    else:
        print(f"[WARNING] {len(sin_mit_header)} archivos necesitan MIT License")

if __name__ == "__main__":
    main()