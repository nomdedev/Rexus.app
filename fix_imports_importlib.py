#!/usr/bin/env python3
"""
Script para corregir imports usando importlib para evitar problemas de sintaxis
"""

import os
import re
import glob

def fix_imports_in_file(file_path):
    """Corrige los imports en un archivo usando importlib."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Patrones específicos a corregir
    imports_to_fix = [
        # (pattern, replacement_code)
        (r'from rexus\.modules\.inventario\.controller import InventarioController', 
         '''# Import usando importlib
import importlib
inventario_controller = importlib.import_module('rexus.modules.02_inventario.controller')
InventarioController = inventario_controller.InventarioController'''),
        
        (r'from rexus\.modules\.inventario\.submodules\.reportes_manager import ReportesManager',
         '''# Import usando importlib
import importlib
reportes_manager = importlib.import_module('rexus.modules.02_inventario.submodules.reportes_manager')
ReportesManager = reportes_manager.ReportesManager'''),
        
        (r'from rexus\.modules\.logistica\.components\.estadisticas_widget import EstadisticasWidget',
         '''# Import usando importlib
import importlib
estadisticas_widget = importlib.import_module('rexus.modules.05_logistica.components.estadisticas_widget')
EstadisticasWidget = estadisticas_widget.EstadisticasWidget'''),
        
        # Agregar más patrones según sea necesario
    ]
    
    for pattern, replacement in imports_to_fix:
        content = re.sub(pattern, replacement, content)
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Corregido: {file_path}")
        return True
    return False

def main():
    """Función principal."""
    print("CORRIGIENDO IMPORTS CON IMPORTLIB")
    print("=" * 50)
    
    # Solo algunos archivos específicos que tienen problemas
    problematic_files = [
        "tests/unit/compras/test_compras_controller.py",  # Ya corregido manualmente
        "tests/unit/inventario/test_inventario_controller.py",
        "tests/unit/inventario/test_reportes_manager.py",
        "tests/unit/logistica/test_estadisticas_widget.py",
    ]
    
    fixed_count = 0
    for file_path in problematic_files:
        if os.path.exists(file_path):
            if fix_imports_in_file(file_path):
                fixed_count += 1
    
    print(f"\nRESUMEN:")
    print(f"Archivos procesados: {len(problematic_files)}")
    print(f"Archivos corregidos: {fixed_count}")
    print("Correccion con importlib completada!")

if __name__ == "__main__":
    main()