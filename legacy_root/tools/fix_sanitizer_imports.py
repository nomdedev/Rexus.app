#!/usr/bin/env python3
"""
Script para corregir importaciones inconsistentes de DataSanitizer
Migra todas las importaciones al sistema unificado unified_sanitizer
"""

import os
import re
import sys
from pathlib import Path

def fix_sanitizer_imports(file_path):
    """Corrige las importaciones de DataSanitizer en un archivo específico."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        # Patrones de importaciones a reemplazar
        old_patterns = [
            # Importaciones try/except
            re.compile(r'try:\s*\n\s*from utils\.data_sanitizer import DataSanitizer.*?\n.*?except.*?:\s*\n\s*from rexus\.utils\.data_sanitizer import DataSanitizer.*?\n', re.DOTALL),

            # Importaciones directas
            r'from utils\.data_sanitizer import DataSanitizer.*?\n',
            r'from rexus\.utils\.data_sanitizer import DataSanitizer.*?\n',

            # Variables de tipo
            r'_SANITIZER_TYPE = ".*?"\n',

            # Alias específicos
            r'from rexus\.utils\.unified_sanitizer import unified_sanitizer as DataSanitizer.*?\n',
        ]

        # Reemplazar patrones
        for pattern in old_patterns:
            if isinstance(pattern, re.Pattern):
                content = pattern.sub('', content)
            else:
                content = re.sub(pattern, '', content, flags=re.MULTILINE)

        # Agregar la importación unificada si no existe
        if 'from rexus.utils.unified_sanitizer import' not in content:
            # Encontrar las importaciones existentes
            import_section = re.search(r'(from rexus\..*?import.*?\n)+', content, re.MULTILINE)
            if import_section:
                # Insertar después de las importaciones de rexus
                insertion_point = import_section.end()
                new_import = 'from rexus.utils.unified_sanitizer import unified_sanitizer, sanitize_string, sanitize_numeric\n'
                content = content[:insertion_point] + new_import + content[insertion_point:]
            else:
                # Insertar después de los imports estándar
                lines = content.split('\n')
                insert_index = 0
                for i, line in enumerate(lines):
                    if line.startswith('import ') or line.startswith('from '):
                        insert_index = i + 1
                    elif line.strip() == '' and insert_index > 0:
                        break

                lines.insert(insert_index, 'from rexus.utils.unified_sanitizer import unified_sanitizer, sanitize_string, sanitize_numeric')
                content = '\n'.join(lines)

        # Corregir referencias en el código
        code_fixes = [
            # Inicialización de instancias
            (r'self\.data_sanitizer = DataSanitizer\(\)', 'self.sanitizer = unified_sanitizer'),
            (r'self\.data_sanitizer = DataSanitizer', 'self.sanitizer = unified_sanitizer'),

            # Uso de métodos
            (r'self\.data_sanitizer\.sanitize_string\((.*?)\)', r'sanitize_string(\1)'),
            (r'self\.data_sanitizer\.sanitize_text\((.*?)\)', r'sanitize_string(\1)'),
            (r'DataSanitizer\.sanitize_string\((.*?)\)', r'sanitize_string(\1)'),
            (r'DataSanitizer\.sanitize_text\((.*?)\)', r'sanitize_string(\1)'),

            # Referencias a variables de tipo
            (r'if _SANITIZER_TYPE == ".*?":', '# Usando sistema unificado'),
            (r'else:\s*# Versión de rexus.*?\n.*?return.*?sanitize_text\(.*?\)', ''),

            # Limpiar bloques de código obsoletos
            (r'if _SANITIZER_TYPE == "utils":\s*\n.*?sanitize_string\(.*?\)\s*\n.*?else:\s*\n.*?sanitize_text\(.*?\)\s*\n', 'return sanitize_string(text)\n'),
        ]

        for pattern, replacement in code_fixes:
            content = re.sub(pattern,
replacement,
                content,
                flags=re.DOTALL | re.MULTILINE)

        # Solo escribir si hubo cambios
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True

        return False

    except Exception as e:
        print(f"Error procesando {file_path}: {e}")
        return False

def main():
    """Función principal."""
    base_path = Path('rexus/modules')

    if not base_path.exists():
        print(f"Error: No se encontró el directorio {base_path}")
        sys.exit(1)

    # Encontrar todos los archivos Python
    python_files = list(base_path.rglob('*.py'))

    print(f"Encontrados {len(python_files)} archivos Python")

    fixed_files = []

    for file_path in python_files:
        # Saltar archivos de backup y temporales
        if any(x in str(file_path) for x in ['backup', 'temp', '__pycache__']):
            continue

        if fix_sanitizer_imports(file_path):
            fixed_files.append(str(file_path))
            print(f"Corregido: {file_path}")

    print(f"\nResumen:")
    print(f"- Archivos procesados: {len(python_files)}")
    print(f"- Archivos corregidos: {len(fixed_files)}")

    if fixed_files:
        print(f"\nArchivos modificados:")
        for file_path in fixed_files[:10]:  # Mostrar solo los primeros 10
            print(f"  - {file_path}")
        if len(fixed_files) > 10:
            print(f"  ... y {len(fixed_files) - 10} más")

if __name__ == '__main__':
    main()
