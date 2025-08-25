#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script sistemático para corregir errores de indentación en módulo compras
"""
import os
import re
import shutil

def fix_indentation_patterns(content):
    """Corrige patrones específicos de indentación"""
    lines = content.split('\n')
    corrected_lines = []
    
    for i, line in enumerate(lines):
        # Si la línea anterior termina en : y esta línea no está indentada
        if i > 0:
            prev_line = lines[i-1].strip()
            current_line = line.strip()
            current_indent = len(line) - len(line.lstrip())
            
            # Patrones que necesitan indentación después de ":"
            if (prev_line.endswith(':') and 
                current_line and 
                not current_line.startswith(('#', '"""', "'''")) and
                current_indent == 0 and
                prev_line.startswith(('try', 'except', 'if ', 'elif ', 'else', 'for ', 'while ', 'with ', 'def ', 'class '))):
                
                # Determinar nivel de indentación basado en contexto
                if prev_line.startswith('class '):
                    corrected_lines.append('    ' + current_line)
                elif prev_line.startswith('def '):
                    corrected_lines.append('        ' + current_line)  
                else:
                    # Para try, if, etc dentro de métodos
                    corrected_lines.append('            ' + current_line)
            else:
                corrected_lines.append(line)
        else:
            corrected_lines.append(line)
    
    return '\n'.join(corrected_lines)

def fix_specific_method_patterns(content):
    """Corrige patrones específicos de métodos mal indentados"""
    # Corregir métodos que empiezan sin indentación después de una clase
    content = re.sub(r'\nclass [^:]+:\n    """[^"]*"""\n\ndef ([^(]+\([^)]*\):)', 
                     r'\nclass \1:\n    """\2"""\n\n    def \3:', content, flags=re.DOTALL)
    
    # Corregir bloques try-except mal indentados
    content = re.sub(r'\ntry:\n([a-zA-Z_])', r'\ntry:\n    \1', content)
    content = re.sub(r'\nexcept ([^:]+):\n([a-zA-Z_])', r'\nexcept \1:\n    \2', content)
    content = re.sub(r'\nfinally:\n([a-zA-Z_])', r'\nfinally:\n    \1', content)
    
    return content

def fix_file_indentation(filepath):
    """Corrige indentación en un archivo específico"""
    print(f"Corrigiendo: {filepath}")
    
    # Backup
    backup_path = filepath + ".backup"
    shutil.copy2(filepath, backup_path)
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Aplicar correcciones
        corrected_content = fix_indentation_patterns(content)
        corrected_content = fix_specific_method_patterns(corrected_content)
        
        # Escribir archivo corregido
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(corrected_content)
            
        print(f"  ✓ {filepath} corregido")
        return True
        
    except Exception as e:
        print(f"  ❌ Error en {filepath}: {e}")
        # Restaurar backup
        shutil.copy2(backup_path, filepath)
        return False

if __name__ == "__main__":
    archivos_con_errores = [
        "rexus/modules/compras/model.py",
        "rexus/modules/compras/detalle_model.py", 
        "rexus/modules/compras/inventory_integration.py",
        "rexus/modules/compras/proveedores_model.py",
        "rexus/modules/compras/dialogs/dialog_proveedor.py",
        "rexus/modules/compras/dialogs/dialog_seguimiento.py",
        "rexus/modules/compras/pedidos/model.py",
        "rexus/modules/compras/pedidos/view.py"
    ]
    
    corregidos = 0
    for archivo in archivos_con_errores:
        if os.path.exists(archivo):
            if fix_file_indentation(archivo):
                corregidos += 1
        else:
            print(f"❌ No encontrado: {archivo}")
    
    print(f"\n✅ Archivos corregidos: {corregidos}/{len(archivos_con_errores)}")