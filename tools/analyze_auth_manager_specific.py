#!/usr/bin/env python3
"""
Script para analizar específicamente el módulo auth_manager
"""

import os
import sys
import re
from pathlib import Path

def analyze_auth_manager():
    """Analiza el módulo auth_manager específicamente."""
    
    print("🔍 ANÁLISIS ESPECÍFICO: AUTH_MANAGER")
    print("=" * 50)
    
    # Leer el archivo
    auth_file = Path("rexus/core/auth_manager.py")
    
    if not auth_file.exists():
        print("❌ Archivo no encontrado: rexus/core/auth_manager.py")
        return
        
    with open(auth_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar todas las queries embebidas
    embedded_queries = []
    lines = content.split('\n')
    
    in_query = False
    current_query = []
    query_start_line = 0
    
    for i, line in enumerate(lines, 1):
        if 'cursor.execute("""' in line or 'cursor.execute("' in line:
            in_query = True
            query_start_line = i
            current_query = [line.strip()]
        elif in_query:
            current_query.append(line.strip())
            if '""")' in line or '")' in line:
                in_query = False
                full_query = '\n'.join(current_query)
                embedded_queries.append({
                    'line': query_start_line,
                    'query': full_query
                })
                current_query = []
    
    print(f"📊 QUERIES EMBEBIDAS ENCONTRADAS: {len(embedded_queries)}")
    print()
    
    for i, query_info in enumerate(embedded_queries, 1):
        print(f"🔸 Query #{i} (línea {query_info['line']}):")
        query_text = query_info['query']
        
        # Extraer tabla principal
        table_match = re.search(r'FROM\s+(\w+)|UPDATE\s+(\w+)|INSERT\s+INTO\s+(\w+)', query_text, re.IGNORECASE)
        if table_match:
            table = table_match.group(1) or table_match.group(2) or table_match.group(3)
            print(f"   📋 Tabla: {table}")
        
        # Mostrar tipo de operación
        if 'SELECT' in query_text.upper():
            print("   🔍 Tipo: SELECT")
        elif 'INSERT' in query_text.upper():
            print("   ➕ Tipo: INSERT")
        elif 'UPDATE' in query_text.upper():
            print("   ✏️ Tipo: UPDATE")
        elif 'DELETE' in query_text.upper():
            print("   🗑️ Tipo: DELETE")
        
        # Verificar si es fallback
        if 'else:' in lines[query_info['line'] - 2:query_info['line'] + 1]:
            print("   ✅ Es query de FALLBACK (OK)")
        elif 'if self.sql_manager:' in '\n'.join(lines[max(0, query_info['line'] - 5):query_info['line']]):
            print("   ✅ Tiene versión EXTERNALIZADA (OK)")
        else:
            print("   ❌ Query SIN EXTERNALIZAR")
        
        print(f"   📝 Query: {query_text[:100]}...")
        print()
    
    # Verificar archivos SQL
    print("📁 ARCHIVOS SQL EXTERNOS CREADOS:")
    sql_dir = Path("sql/auth")
    if sql_dir.exists():
        sql_files = list(sql_dir.glob("*.sql"))
        for sql_file in sql_files:
            print(f"   ✅ {sql_file.name}")
    else:
        print("   ❌ Directorio sql/auth no existe")
    
    # Verificar SQLQueryManager
    print()
    print("🔧 VERIFICACIÓN SQLQueryManager:")
    if 'from ..utils.sql_query_manager import SQLQueryManager' in content:
        print("   ✅ SQLQueryManager importado")
    else:
        print("   ❌ SQLQueryManager NO importado")
    
    if 'self.sql_manager = SQLQueryManager()' in content:
        print("   ✅ sql_manager inicializado")
    else:
        print("   ❌ sql_manager NO inicializado")
    
    # Contar uso de sql_manager
    sql_manager_usage = content.count('self.sql_manager.get_query(')
    print(f"   📊 Usos de sql_manager.get_query(): {sql_manager_usage}")

if __name__ == "__main__":
    analyze_auth_manager()
