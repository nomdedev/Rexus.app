#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corrección final para eliminar todos los errores de formato restantes
"""

import re

def fix_final_format_errors():
    """Corrige los errores de formato restantes con enfoque sistemático."""
    
    with open('rexus/modules/logistica/controller.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    corrected_lines = []
    
    for i, line in enumerate(lines):
        original_line = line
        
        # 1. Corregir líneas demasiado largas (E501)
        if len(line.rstrip()) > 79:
            # Casos específicos de división de línea
            if 'show_error(self.view, "Error",' in line:
                indent = len(line) - len(line.lstrip())
                parts = line.strip().split('", "')
                if len(parts) >= 2:
                    line = ' ' * indent + parts[0] + '",\n' + ' ' * (indent + 20) + '"' + parts[1] + '\n'
            
            elif 'show_success(self.view, "Éxito",' in line:
                indent = len(line) - len(line.lstrip())
                parts = line.strip().split('", "')
                if len(parts) >= 2:
                    line = ' ' * indent + parts[0] + '",\n' + ' ' * (indent + 22) + '"' + parts[1] + '\n'
            
            elif 'logger.warning(' in line and len(line.rstrip()) > 79:
                indent = len(line) - len(line.lstrip())
                if '"' in line:
                    before_quote = line[:line.find('"')]
                    quote_content = line[line.find('"'):]
                    line = before_quote + '\n' + ' ' * (indent + 4) + quote_content
            
            elif 'if (self.model and' in line:
                indent = len(line) - len(line.lstrip())
                line = line[:79] + ' \\\n' + ' ' * (indent + 8) + line[79:].lstrip()
            
            elif '= self.model.' in line and len(line.rstrip()) > 79:
                indent = len(line) - len(line.lstrip())
                equals_pos = line.find(' = ')
                if equals_pos > 0:
                    line = line[:equals_pos + 3] + '\\\n' + ' ' * (indent + 12) + line[equals_pos + 3:].lstrip()
            
        # 2. Corregir continuaciones mal indentadas (E122, E128)
        if (i > 0 and (line.strip().startswith('"') or 
                      line.strip().startswith('hasattr') or
                      'no disponible' in line)):
            prev_line = lines[i-1].rstrip()
            if prev_line.endswith('\\') or prev_line.endswith('(') or prev_line.endswith(','):
                # Determinar indentación correcta basada en la línea anterior
                prev_indent = len(prev_line) - len(prev_line.lstrip())
                if prev_line.rstrip().endswith('('):
                    correct_indent = prev_indent + 4
                elif 'if (' in prev_line:
                    correct_indent = prev_indent + 8
                elif prev_line.rstrip().endswith(','):
                    correct_indent = prev_indent + 4
                else:
                    correct_indent = prev_indent + 4
                
                content = line.lstrip()
                line = ' ' * correct_indent + content
        
        corrected_lines.append(line)
    
    # Escribir archivo corregido
    with open('rexus/modules/logistica/controller.py', 'w', encoding='utf-8') as f:
        f.writelines(corrected_lines)
    
    print("Corrección final aplicada")

if __name__ == "__main__":
    fix_final_format_errors()