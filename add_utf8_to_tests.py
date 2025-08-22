# -*- coding: utf-8 -*-
"""
Script para agregar encoding UTF-8 a archivos de test que no lo tengan
"""

import os
import glob

def add_utf8_encoding(file_path):
    """Agrega encoding UTF-8 al inicio del archivo si no lo tiene"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar si ya tiene encoding UTF-8
        if '# -*- coding: utf-8 -*-' in content[:100]:
            return False  # Ya tiene encoding
        
        # Agregar encoding al inicio
        new_content = '# -*- coding: utf-8 -*-\n' + content
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return True
    except Exception as e:
        print(f"Error procesando {file_path}: {e}")
        return False

def main():
    # Buscar todos los archivos .py en tests/
    test_files = glob.glob('tests/**/*.py', recursive=True)
    
    updated_files = []
    for file_path in test_files:
        if add_utf8_encoding(file_path):
            updated_files.append(file_path)
    
    print(f"Archivos actualizados: {len(updated_files)}")
    for file in updated_files:
        print(f"  ✅ {file}")

if __name__ == '__main__':
    main()