#!/usr/bin/env python3
import re
import os

files_to_fix = [
    r'd:\martin\Proyectos\Rexus.app\rexus\modules\07_compras\view_complete.py',
    r'd:\martin\Proyectos\Rexus.app\rexus\modules\06_pedidos\view_complete.py',
]

for filepath in files_to_fix:
    if os.path.exists(filepath):
        print(f"Procesando {filepath}...")
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        modified = False
        for i, line in enumerate(lines):
            # Buscar líneas que terminen con f"....) sin comilla de cierre
            if 'f"' in line and line.rstrip().endswith(')'):
                # Verificar si es un f-string sin cerrar
                if '")' not in line.rstrip()[-3:]:
                    # Es un f-string sin cerrar
                    # Buscar el lugar donde debería estar la comilla
                    if 'setStyleSheet' in line or 'show_error' in line or 'show_success' in line or 'QTableWidgetItem' in line:
                        # Reemplazar el ) final por ")
                        lines[i] = line.rstrip()[:-1] + '")\n'
                        modified = True
                        print(f"  Linea {i+1}: Corregido f-string sin cerrar")
        
        if modified:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            print(f"✓ {filepath} actualizado")
        else:
            print(f"- {filepath} no necesita cambios")
