#!/usr/bin/env python3
"""
Verifica y corrige imports después del renombrado de módulos
Busca imports rotos y sugiere correcciones
"""

import re
from pathlib import Path

def find_broken_imports():
    """Encuentra imports que necesitan corrección después del rename"""
    
    # Mapeo de nombres viejos a nuevos
    module_mapping = {
        'obras': '01_obras',
        'inventario': '02_inventario', 
        'pedidos': '03_pedidos',
        'compras': '04_compras',
        'logistica': '05_logistica',
        'herrajes': '06_herrajes',
        'vidrios': '07_vidrios',
        'mantenimiento': '08_mantenimiento',
        'usuarios': '09_usuarios',
        'configuracion': '10_configuracion',
        'auditoria': '11_auditoria',
        'administracion': '12_administracion',
        'notificaciones': '13_notificaciones'
    }
    
    broken_imports = []
    
    # Buscar en todos los archivos Python
    for py_file in Path('.').rglob('*.py'):
        if '__pycache__' in str(py_file) or '.git' in str(py_file):
            continue
            
        try:
            with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            lines = content.split('\n')
            for line_num, line in enumerate(lines, 1):
                # Buscar imports de módulos renombrados
                for old_name, new_name in module_mapping.items():
                    patterns = [
                        rf'from\s+.*\.modules\.{old_name}\s+import',
                        rf'from\s+.*modules\.{old_name}\s+import',
                        rf'from\s+rexus\.modules\.{old_name}\s+import',
                        rf'import\s+.*\.modules\.{old_name}',
                        rf'import\s+.*modules\.{old_name}',
                        rf'import\s+rexus\.modules\.{old_name}',
                    ]
                    
                    for pattern in patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            suggested_fix = line.replace(f'.{old_name}', f'.{new_name}').replace(f'/{old_name}', f'/{new_name}')
                            
                            broken_imports.append({
                                'file': str(py_file),
                                'line': line_num,
                                'original': line.strip(),
                                'suggested': suggested_fix.strip(),
                                'old_module': old_name,
                                'new_module': new_name
                            })
                            break
        except Exception as e:
            print(f"Error reading {py_file}: {e}")
    
    return broken_imports

def main():
    """Main execution"""
    print("=== VERIFICACION DE IMPORTS DESPUES DE RENAME ===\n")
    
    broken = find_broken_imports()
    
    if not broken:
        print("*** EXCELENTE ***")
        print("No se encontraron imports rotos por el renombrado de modulos.")
        return
    
    print(f"*** IMPORTS ROTOS ENCONTRADOS: {len(broken)} ***\n")
    
    # Agrupar por archivo
    files_affected = {}
    for item in broken:
        file_path = item['file']
        if file_path not in files_affected:
            files_affected[file_path] = []
        files_affected[file_path].append(item)
    
    for file_path, imports in files_affected.items():
        print(f"Archivo: {file_path}")
        print(f"Imports rotos: {len(imports)}")
        
        for imp in imports[:3]:  # Show first 3
            print(f"  Linea {imp['line']}:")
            print(f"    Actual:   {imp['original']}")
            print(f"    Corregir: {imp['suggested']}")
        
        if len(imports) > 3:
            print(f"  ... y {len(imports) - 3} mas")
        
        print()
    
    print("*** ACCION REQUERIDA ***")
    print("Ejecutar correcciones automáticas o manuales para estos imports.")

if __name__ == "__main__":
    main()