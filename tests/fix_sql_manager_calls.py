#!/usr/bin/env python3
"""
Script para corregir las llamadas al SQLQueryManager en mantenimiento/model.py
"""

import re

def fix_sql_manager_calls():
    """Corrige todas las llamadas incorrectas al SQLQueryManager."""
    
    file_path = "rexus/modules/mantenimiento/model.py"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Patrón para encontrar llamadas incorrectas
        pattern = r'self\.sql_manager\.get_query\("([^"]+)\.([^"]+)"\)'
        
        def replace_call(match):
            full_name = match.group(1) + "." + match.group(2)
            module = match.group(1)
            query_name = match.group(2)
            return f'self.sql_manager.get_query("{module}", "{query_name}")'
        
        # Reemplazar todas las llamadas
        content = re.sub(pattern, replace_call, content)
        
        # También corregir las que usan format() para SQL injection
        injection_patterns = [
            (r'"SELECT equipo_id FROM \[\{\}\] WHERE id = \?"\.format\([^)]+\)', 
             '"SELECT equipo_id FROM equipos WHERE id = ?"'),
            (r'query\.format\([^)]+\)', 'query'),  # Remover cualquier .format() restante
        ]
        
        for pattern, replacement in injection_patterns:
            content = re.sub(pattern, replacement, content)
        
        # Escribir el archivo corregido
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Archivo corregido exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error corrigiendo archivo: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Corrigiendo llamadas al SQLQueryManager...")
    success = fix_sql_manager_calls()
    
    if success:
        print("🎉 Corrección completada!")
    else:
        print("❌ Error en la corrección")
