#!/usr/bin/env python3
"""
Script para migrar componentes PyQt6 a componentes Rexus en archivos de vista
"""

import os
import re
from pathlib import Path

def migrate_ui_components(file_path):
    """Migra componentes PyQt a Rexus en un archivo específico."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Mapeo de componentes PyQt a Rexus
        component_mapping = [
            # Componentes básicos
            (r'\bQPushButton\(', 'RexusButton('),
            (r'\bQLabel\(', 'RexusLabel('),
            (r'\bQLineEdit\(', 'RexusLineEdit('),
            (r'\bQComboBox\(', 'RexusComboBox('),
            (r'\bQTableWidget\(', 'RexusTable('),
            (r'\bQFrame\(', 'RexusFrame('),
            (r'\bQGroupBox\(', 'RexusGroupBox('),
            
            # Referencias de clase
            (r'QPushButton\.', 'RexusButton.'),
            (r'QLabel\.', 'RexusLabel.'),
            (r'QLineEdit\.', 'RexusLineEdit.'),
            (r'QComboBox\.', 'RexusComboBox.'),
            (r'QTableWidget\.', 'RexusTable.'),
            (r'QFrame\.', 'RexusFrame.'),
            (r'QGroupBox\.', 'RexusGroupBox.'),
        ]
        
        # Aplicar migraciones
        for old_pattern, new_component in component_mapping:
            content = re.sub(old_pattern, new_component, content)
        
        # Verificar si necesita agregar imports de Rexus
        needs_rexus_imports = any(comp in content for comp in [
            'RexusButton', 'RexusLabel', 'RexusLineEdit', 
            'RexusComboBox', 'RexusTable', 'RexusFrame', 'RexusGroupBox'
        ])
        
        if needs_rexus_imports and 'from rexus.ui.components' not in content:
            # Encontrar donde insertar las importaciones
            lines = content.split('\n')
            insert_index = -1
            
            # Buscar el final de las importaciones PyQt6
            for i, line in enumerate(lines):
                if line.strip().startswith('from PyQt6.QtWidgets'):
                    # Buscar el final del bloque de importación
                    j = i + 1
                    while j < len(lines) and (lines[j].strip().startswith(' ') or lines[j].strip() == ''):
                        j += 1
                    insert_index = j
                    break
            
            if insert_index > 0:
                # Insertar las importaciones Rexus
                rexus_imports = """
# Importar componentes Rexus
from rexus.ui.components.base_components import (
    RexusButton,
    RexusLabel,
    RexusLineEdit,
    RexusComboBox,
    RexusTable,
    RexusFrame,
    RexusGroupBox,
    RexusLayoutHelper
)"""
                lines.insert(insert_index, rexus_imports)
                content = '\n'.join(lines)
        
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
    # Archivos específicos que necesitan migración
    files_to_migrate = [
        'rexus/modules/configuracion/view.py',
        'rexus/modules/logistica/view.py',
        'rexus/modules/auditoria/view.py',
        'rexus/modules/compras/pedidos/view.py',
    ]
    
    migrated_files = []
    
    for file_path in files_to_migrate:
        path = Path(file_path)
        if path.exists():
            if migrate_ui_components(path):
                migrated_files.append(str(path))
                print(f"Migrado: {file_path}")
            else:
                print(f"Sin cambios: {file_path}")
        else:
            print(f"No encontrado: {file_path}")
    
    print(f"\nResumen:")
    print(f"- Archivos migrados: {len(migrated_files)}")
    
    if migrated_files:
        print(f"\nArchivos modificados:")
        for file_path in migrated_files:
            print(f"  - {file_path}")

if __name__ == '__main__':
    main()