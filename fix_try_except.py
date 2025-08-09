#!/usr/bin/env python3
"""
Script para corregir bloques try-except malformados en archivos de inventario submodules
"""

import os
import re
from pathlib import Path

def fix_malformed_try_except(file_path):
    """Corrige bloques try-except malformados en un archivo."""
    print(f"Corrigiendo {file_path}...")
    
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Patrón malformado que necesita corrección
    malformed_pattern = re.compile(
        r'# DataSanitizer unificado - Usar sistema unificado de sanitización\s*\n'
        r'try:\s*\n'
        r'\s*except ImportError:\s*\n'
        r'\s*try:\s*\n'
        r'\s*except ImportError:\s*\n'
        r'\s*# Fallback seguro\s*\n'
        r'\s*class DataSanitizer:',
        re.MULTILINE | re.DOTALL
    )
    
    # Reemplazo correcto
    correct_replacement = '''# DataSanitizer unificado - Usar sistema unificado de sanitización
try:
    from rexus.utils.data_sanitizer import DataSanitizer
except ImportError:
    try:
        from rexus.utils.unified_sanitizer import DataSanitizer
    except ImportError:
        # Fallback seguro
        class DataSanitizer:'''
    
    if malformed_pattern.search(content):
        print(f"  - Encontrado patrón malformado, corrigiendo...")
        content = malformed_pattern.sub(correct_replacement, content)
        
        # Escribir archivo corregido
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"  - OK Corregido")
        return True
    else:
        print(f"  - No necesita corrección")
        return False

def main():
    """Función principal."""
    print("CORRIGIENDO BLOQUES TRY-EXCEPT MALFORMADOS")
    print("=" * 50)
    
    # Archivos a corregir
    submodules_dir = Path("rexus/modules/inventario/submodules")
    files_to_fix = [
        "categorias_manager.py",
        "consultas_manager.py", 
        "consultas_manager_refactorizado.py",
        "movimientos_manager_refactorizado.py",
        "productos_manager_refactorizado.py",
        "reservas_manager.py"
    ]
    
    fixed_count = 0
    for filename in files_to_fix:
        file_path = submodules_dir / filename
        if file_path.exists():
            if fix_malformed_try_except(file_path):
                fixed_count += 1
        else:
            print(f"ADVERTENCIA: {file_path} no existe")
    
    print(f"\nCORRECCION COMPLETADA: {fixed_count} archivos corregidos")

if __name__ == "__main__":
    main()