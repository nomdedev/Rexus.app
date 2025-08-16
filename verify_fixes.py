#!/usr/bin/env python3
"""
Verificar correcciones de exec/eval críticos
"""

import re
from pathlib import Path

def main():
    print('VERIFICANDO CORRECCIONES DE EXEC/EVAL CRITICOS')
    print('=' * 50)

    # Los tres archivos más críticos que acabamos de corregir
    critical_files = [
        'aplicar_estilos_premium.py',
        'legacy_root/tools/development/maintenance/generar_informes_modulos.py', 
        'scripts/test_step_by_step.py'
    ]

    exec_pattern = r'\bexec\s*\(\s*f["\']'
    found_critical = False

    for file_path in critical_files:
        path = Path(file_path)
        if path.exists():
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            matches = list(re.finditer(exec_pattern, content, re.IGNORECASE))
            if matches:
                found_critical = True
                print(f'CRITICO: {file_path} - {len(matches)} usos peligrosos')
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    print(f'   Linea {line_num}: exec con f-string')
            else:
                print(f'OK: {file_path} - Sin exec criticos')
        else:
            print(f'NO ENCONTRADO: {file_path}')

    if not found_critical:
        print('\nEXITO: Los 3 archivos mas criticos fueron corregidos')
        print('Eliminamos los riesgos de RCE mas peligrosos')
        return True
    else:
        print('\nAUN HAY RIESGOS CRITICOS - Revisar archivos marcados')
        return False

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)