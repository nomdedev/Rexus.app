#!/usr/bin/env python3
"""
Script específico para encontrar queries SQL embebidas reales
"""

import os
import re

def find_sql_queries(file_path):
    """Encuentra queries SQL en un archivo específico"""
    queries = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Buscar patrones SQL más específicos
            sql_keywords = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'ALTER', 'DROP']
            
            for keyword in sql_keywords:
                # Buscar keyword seguido de espacios y contenido SQL
                pattern = rf'{keyword}\s+.*?(?:FROM|INTO|SET|TABLE|INDEX)'
                matches = re.finditer(pattern, line, re.IGNORECASE)
                
                for match in matches:
                    # Filtrar falsos positivos obvios
                    if not any(exclude in line.lower() for exclude in [
                        'ejemplo', 'example', 'comment', 'documentation', 'doc', '#', '//',
                        'print', 'log', 'debug', 'qss', 'style', 'css', 'color'
                    ]):
                        queries.append({
                            'line': i,
                            'content': line.strip(),
                            'keyword': keyword,
                            'match': match.group()
                        })
        
        return queries
        
    except Exception as e:
        print(f"Error leyendo {file_path}: {e}")
        return []

def main():
    target_files = [
        'rexus/core/audit_trail.py',
        'rexus/modules/vidrios/model.py', 
        'rexus/modules/inventario/model.py',
        'rexus/utils/data_integrity_validator.py',
        'rexus/models/productos_model.py'
    ]
    
    print("=== BÚSQUEDA ESPECÍFICA DE QUERIES SQL ===\n")
    
    for file_path in target_files:
        if os.path.exists(file_path):
            queries = find_sql_queries(file_path)
            
            print(f"📁 {file_path}")
            if queries:
                print(f"   🔴 {len(queries)} queries encontradas:")
                for q in queries[:5]:  # Mostrar solo las primeras 5
                    print(f"   Línea {q['line']}: {q['content'][:100]}...")
            else:
                print("   ✅ No hay queries embebidas")
            print()
        else:
            print(f"❌ Archivo no encontrado: {file_path}\n")

if __name__ == "__main__":
    main()
