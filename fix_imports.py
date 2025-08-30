#!/usr/bin/env python3
"""
Script para corregir imports con números en todos los archivos de test
Convierte imports como 'rexus.modules.02_inventario' a 'rexus.modules.inventario'
"""

import os
import re
import glob

# Mapeo de nombres con números a nombres limpios
MODULE_MAPPING = {
    '01_obras': 'obras',
    '02_inventario': 'inventario', 
    '03_pedidos': 'pedidos',
    '04_compras': 'compras',
    '05_logistica': 'logistica',
    '06_herrajes': 'herrajes',
    '07_vidrios': 'vidrios',
    '08_mantenimiento': 'mantenimiento',
    '09_usuarios': 'usuarios',
    '10_configuracion': 'configuracion',
    '11_auditoria': 'auditoria',
    '12_administracion': 'administracion',
    '13_notificaciones': 'notificaciones',
}

def fix_imports_in_file(file_path):
    """Corrige los imports en un archivo específico."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Reemplazar cada import numerado
    for numbered_name, clean_name in MODULE_MAPPING.items():
        # Patrón para encontrar imports del tipo: from rexus.modules.02_inventario
        pattern = f'rexus\\.modules\\.{re.escape(numbered_name)}'
        replacement = f'rexus.modules.{clean_name}'
        content = re.sub(pattern, replacement, content)
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Corregido: {file_path}")
        return True
    return False

def main():
    """Función principal."""
    print("CORRIGIENDO IMPORTS NUMERADOS EN REXUS/ Y TESTS")
    print("=" * 50)
    
    # Encontrar todos los archivos Python en rexus/ y tests/
    rexus_files = glob.glob("rexus/**/*.py", recursive=True)
    test_files = glob.glob("tests/**/*.py", recursive=True)
    all_files = rexus_files + test_files
    
    fixed_count = 0
    for file_path in all_files:
        if fix_imports_in_file(file_path):
            fixed_count += 1
    
    print("\nRESUMEN:")
    print(f"Archivos procesados: {len(all_files)}")
    print(f"Archivos corregidos: {fixed_count}")
    print("Correccion de imports completada!")

if __name__ == "__main__":
    main()