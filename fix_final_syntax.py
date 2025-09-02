#!/usr/bin/env python3
"""
Script final para corregir errores específicos de sintaxis
"""
import os
import re

def fix_specific_syntax_errors(file_path):
    """Corrige errores específicos de sintaxis"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except:
        return False
    
    original_content = content
    
    # 1. Corregir paréntesis desbalanceados en f-strings con }} extra
    # logger.info(f"...{var}") por usuario {var2")")}")
    pattern = r'logger\.(info|error|warning|debug)\(f\"([^"]*\{[^}]*\}[^"]*)\"\)([^"]*\{[^}]*\}[^"]*\")\)\"\)'
    content = re.sub(pattern, r'logger.\1(f"\2\3")', content)
    
    # 2. Corregir strings no terminados en f-strings
    # logger.error(f"Error ejecutando script {script_name}: {e})
    pattern = r'logger\.(info|error|warning|debug)\(f\"([^"]*\{[^}]*\}[^"]*\{[^}]*\}[^"]*)\)$'
    content = re.sub(pattern, r'logger.\1(f"\2")', content, flags=re.MULTILINE)
    
    # 3. Corregir paréntesis extra con comillas malformadas
    # logger.error(f"Error editando vidrio ID: {vidrio_id}: {str(e")}
    pattern = r'logger\.(info|error|warning|debug)\(f\"([^"]*\{[^}]*\}[^"]*\{[^}]*)\"\)\}'
    content = re.sub(pattern, r'logger.\1(f"\2")', content)
    
    # 4. Corregir casos específicos con } desbalanceados
    pattern = r'(\{[^}]*\")\)(\"\})'
    content = re.sub(pattern, r'\1\2', content)
    
    if content != original_content:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except:
            pass
    
    return False

# Correcciones manuales específicas por archivo
def fix_specific_files():
    fixes = [
        {
            'file': 'rexus/modules/01_obras/model.py',
            'old': 'logger.info(f"Obra creada exitosamente: {datos_limpios.get(\'codigo\')} por usuario {datos_limpios.get(\'usuario_creacion\', \'SISTEMA\'")}")',
            'new': 'logger.info(f"Obra creada exitosamente: {datos_limpios.get(\'codigo\')} por usuario {datos_limpios.get(\'usuario_creacion\', \'SISTEMA\')}")'
        },
        {
            'file': 'rexus/modules/02_inventario/model.py', 
            'old': 'logger.error(f"Error ejecutando script {script_name}: {e})',
            'new': 'logger.error(f"Error ejecutando script {script_name}: {e}")'
        },
        {
            'file': 'rexus/modules/04_vidrios/controller.py',
            'old': 'logger.error(f"Error editando vidrio ID: {vidrio_id}: {str(e")}", exc_info=True)',
            'new': 'logger.error(f"Error editando vidrio ID: {vidrio_id}: {str(e)}", exc_info=True)'
        }
    ]
    
    for fix in fixes:
        file_path = fix['file']
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                if fix['old'] in content:
                    content = content.replace(fix['old'], fix['new'])
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"MANUAL FIX: {file_path}")
            except:
                pass

def main():
    print("Aplicando correcciones finales de sintaxis...")
    
    # Aplicar correcciones manuales específicas
    fix_specific_files()
    
    # Aplicar correcciones automáticas
    total_changes = 0
    for root, dirs, files in os.walk('rexus'):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                if fix_specific_syntax_errors(file_path):
                    print(f"AUTO FIX: {file_path}")
                    total_changes += 1
    
    print(f"Correcciones finales aplicadas: {total_changes}")

if __name__ == "__main__":
    main()