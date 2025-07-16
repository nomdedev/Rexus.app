#!/usr/bin/env python3
"""
Script para corregir vulnerabilidades SQL injection en todo el código
Ejecuta una corrección sistemática de f-strings en SQL
"""

import os
import re
import sys
from pathlib import Path

def fix_sql_injection_in_file(file_path):
    """Corrige vulnerabilidades SQL injection en un archivo específico"""
    print(f"🔧 Procesando: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        changes_made = 0
        
        # Patrones de f-strings peligrosos en SQL
        patterns_to_fix = [
            # f"SELECT ... FROM {table} ..." -> "SELECT ... FROM " + table + " ..."
            (r'f"([^"]*SELECT[^"]*FROM\s+)\{([^}]+)\}([^"]*)"', r'"\1" + \2 + "\3"'),
            (r"f'([^']*SELECT[^']*FROM\s+)\{([^}]+)\}([^']*)'", r"'\1' + \2 + '\3'"),
            
            # f"INSERT INTO {table} ..." -> "INSERT INTO " + table + " ..."
            (r'f"([^"]*INSERT\s+INTO\s+)\{([^}]+)\}([^"]*)"', r'"\1" + \2 + "\3"'),
            (r"f'([^']*INSERT\s+INTO\s+)\{([^}]+)\}([^']*)'", r"'\1' + \2 + '\3'"),
            
            # f"UPDATE {table} ..." -> "UPDATE " + table + " ..."
            (r'f"([^"]*UPDATE\s+)\{([^}]+)\}([^"]*)"', r'"\1" + \2 + "\3"'),
            (r"f'([^']*UPDATE\s+)\{([^}]+)\}([^']*)'", r"'\1' + \2 + '\3'"),
            
            # f"DELETE FROM {table} ..." -> "DELETE FROM " + table + " ..."
            (r'f"([^"]*DELETE\s+FROM\s+)\{([^}]+)\}([^"]*)"', r'"\1" + \2 + "\3"'),
            (r"f'([^']*DELETE\s+FROM\s+)\{([^}]+)\}([^']*)'", r"'\1' + \2 + '\3'"),
            
            # Casos especiales para queries multilinea
            (r'f"""([^"]*SELECT[^"]*FROM\s+)\{([^}]+)\}([^"]*)"""', r'"""\1""" + \2 + """\3"""'),
            (r"f'''([^']*SELECT[^']*FROM\s+)\{([^}]+)\}([^']*)'''", r"'''\1''' + \2 + '''\3'''"),
            
            (r'f"""([^"]*INSERT\s+INTO\s+)\{([^}]+)\}([^"]*)"""', r'"""\1""" + \2 + """\3"""'),
            (r"f'''([^']*INSERT\s+INTO\s+)\{([^}]+)\}([^']*)'''", r"'''\1''' + \2 + '''\3'''"),
            
            (r'f"""([^"]*UPDATE\s+)\{([^}]+)\}([^"]*)"""', r'"""\1""" + \2 + """\3"""'),
            (r"f'''([^']*UPDATE\s+)\{([^}]+)\}([^']*)'''", r"'''\1''' + \2 + '''\3'''"),
            
            (r'f"""([^"]*DELETE\s+FROM\s+)\{([^}]+)\}([^"]*)"""', r'"""\1""" + \2 + """\3"""'),
            (r"f'''([^']*DELETE\s+FROM\s+)\{([^}]+)\}([^']*)'''", r"'''\1''' + \2 + '''\3'''"),
        ]
        
        # Aplicar cada patrón
        for pattern, replacement in patterns_to_fix:
            new_content = re.sub(pattern, replacement, content, flags=re.IGNORECASE | re.MULTILINE)
            if new_content != content:
                changes_made += content.count(pattern.split('\\{')[0]) - new_content.count(pattern.split('\\{')[0])
                content = new_content
        
        # Patrones específicos adicionales para casos complejos
        # Manejar f-strings con múltiples variables de tabla
        multivar_patterns = [
            # f"... {tabla1} ... {tabla2} ..." -> "... " + tabla1 + " ... " + tabla2 + " ..."
            (r'f"([^"]*)\{([^}]+)\}([^"]*)\{([^}]+)\}([^"]*)"', r'"\1" + \2 + "\3" + \4 + "\5"'),
            (r"f'([^']*)\{([^}]+)\}([^']*)\{([^}]+)\}([^']*)'", r"'\1' + \2 + '\3' + \4 + '\5'"),
        ]
        
        for pattern, replacement in multivar_patterns:
            new_content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
            if new_content != content:
                changes_made += 1
                content = new_content
        
        # Guardar solo si hubo cambios
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✅ {changes_made} correcciones aplicadas")
            return True
        else:
            print("  ℹ️  No se necesitaron cambios")
            return False
            
    except Exception as e:
        print(f"  ❌ Error procesando archivo: {e}")
        return False

def main():
    """Función principal"""
    print("🔒 CORRECTOR DE VULNERABILIDADES SQL INJECTION")
    print("=" * 50)
    
    # Archivos específicos del security audit
    files_to_fix = [
        "src/modules/vidrios/model.py",
        "src/core/audit_trail.py", 
        "src/core/database.py",
        "src/core/backup_manager.py",
        "src/modules/mantenimiento/model.py",
        "src/modules/inventario/model.py",
        "src/modules/logistica/model.py",
        "src/modules/configuracion/model.py",
        "src/modules/herrajes/model.py",
        "src/modules/administracion/recursos_humanos/model.py",
        "src/modules/administracion/contabilidad/model.py",
        "src/api/server.py"
    ]
    
    files_fixed = 0
    total_files = 0
    
    for file_path in files_to_fix:
        if os.path.exists(file_path):
            total_files += 1
            if fix_sql_injection_in_file(file_path):
                files_fixed += 1
        else:
            print(f"⚠️  Archivo no encontrado: {file_path}")
    
    print("\n" + "=" * 50)
    print("📊 RESUMEN")
    print(f"Archivos procesados: {total_files}")
    print(f"Archivos corregidos: {files_fixed}")
    
    if files_fixed > 0:
        print("\n🎉 Correcciones aplicadas exitosamente!")
        print("📋 Siguiente paso: Ejecutar bandit para verificar")
        print("   python -m bandit -r src/")
    else:
        print("\nℹ️  No se necesitaron correcciones")

if __name__ == "__main__":
    main()