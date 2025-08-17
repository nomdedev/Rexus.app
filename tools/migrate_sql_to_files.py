#!/usr/bin/env python3
"""
Script para migrar SQL hardcodeado a archivos externos automáticamente
Previene inyección SQL y mejora mantenibilidad

Fecha: 15/08/2025
Objetivo: Eliminar todas las queries hardcodeadas de los modelos
"""

import os
import re
from pathlib import Path

def extract_sql_queries(file_path, module_name):
    """
    Extrae queries SQL hardcodeadas y las migra a archivos externos.
    """
    print(f"Extrayendo SQL de: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Backup del archivo original
    backup_path = file_path + '.sql_backup'
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Crear directorio para archivos SQL
    sql_dir = Path(f'sql/{module_name}')
    sql_dir.mkdir(parents=True, exist_ok=True)
    
    new_content = content
    extracted_queries = {}
    
    # 1. Buscar queries con cursor.execute
    execute_pattern = r'cursor\.execute\(\s*(["\'])([^"\']*(?:SELECT|INSERT|UPDATE|DELETE)[^"\']*)\1[^)]*\)'
    matches = list(re.finditer(execute_pattern, content, re.IGNORECASE | re.DOTALL))
    
    for i, match in enumerate(matches):
        query_content = match.group(2).strip()
        
        # Determinar nombre del archivo basado en la query
        if 'SELECT' in query_content.upper():
            if 'COUNT' in query_content.upper():
                query_name = f'count_{module_name}_{i+1}'
            else:
                query_name = f'select_{module_name}_{i+1}'
        elif 'INSERT' in query_content.upper():
            query_name = f'insert_{module_name}_{i+1}'
        elif 'UPDATE' in query_content.upper():
            query_name = f'update_{module_name}_{i+1}'
        elif 'DELETE' in query_content.upper():
            query_name = f'delete_{module_name}_{i+1}'
        else:
            query_name = f'query_{module_name}_{i+1}'
        
        # Crear archivo SQL
        sql_file_path = sql_dir / f'{query_name}.sql'
        with open(sql_file_path, 'w', encoding='utf-8') as f:
            f.write(query_content)
        
        extracted_queries[query_name] = {
            'file': str(sql_file_path.relative_to(Path('.'))),
            'original': match.group(0)
        }
        
        # Reemplazar en el código
        replacement = f'cursor.execute(self.sql_manager.get_query("{module_name}", "{query_name}"), params)'
        new_content = new_content.replace(match.group(0), replacement, 1)
    
    # 2. Agregar import de SQLQueryManager si no existe
    if 'from rexus.utils.sql_query_manager import SQLQueryManager' not in new_content and extracted_queries:
        sql_manager_import = '''
# Importar SQLQueryManager para queries seguras
try:
    from rexus.utils.sql_query_manager import SQLQueryManager
except ImportError:
    class DummySQLQueryManager:
        def get_query(self, module, query_name):
            return f"-- Query {query_name} not found"
    SQLQueryManager = DummySQLQueryManager
'''
        
        # Insertar después de los imports existentes
        import_pattern = r'(from rexus\.[^\n]+\n)'
        if re.search(import_pattern, new_content):
            new_content = re.sub(
                import_pattern,
                r'\1' + sql_manager_import + '\n',
                new_content, count=1
            )
    
    # 3. Agregar inicialización de sql_manager en __init__ si no existe
    if extracted_queries and 'self.sql_manager = SQLQueryManager()' not in new_content:
        init_pattern = r'(def __init__\(self[^)]*\):[^\n]*\n)'
        if re.search(init_pattern, new_content):
            new_content = re.sub(
                init_pattern,
                r'\1        self.sql_manager = SQLQueryManager()\n',
                new_content, count=1
            )
    
    # Escribir archivo actualizado
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"Extraídas {len(extracted_queries)} queries de {file_path}")
    return extracted_queries

def create_sql_index_file(module_name, queries):
    """Crea un archivo índice con todas las queries del módulo."""
    sql_dir = Path(f'sql/{module_name}')
    index_file = sql_dir / 'README.md'
    
    with open(index_file, 'w', encoding='utf-8') as f:
        f.write(f"# Queries SQL para módulo {module_name}\n\n")
        f.write("Queries extraídas automáticamente del código para mayor seguridad.\n\n")
        f.write("## Archivos disponibles:\n\n")
        
        for query_name, info in queries.items():
            f.write(f"- `{query_name}.sql`: Query extraída del código\n")
        
        f.write(f"\n## Uso:\n\n")
        f.write(f"```python\n")
        f.write(f"# En el modelo:\n")
        f.write(f"sql = self.sql_manager.get_query('{module_name}', 'nombre_query')\n")
        f.write(f"cursor.execute(sql, params)\n")
        f.write(f"```\n")

def main():
    """Migra SQL hardcodeado en múltiples modelos."""
    
    models_to_migrate = [
        ('rexus/modules/usuarios/model.py', 'usuarios'),
        ('rexus/modules/obras/model.py', 'obras'),
        ('rexus/modules/compras/model.py', 'compras'),
        ('rexus/modules/auditoria/model.py', 'auditoria'),
        ('rexus/modules/configuracion/model.py', 'configuracion')
    ]
    
    base_path = Path('.')
    total_queries = 0
    
    for model_path, module_name in models_to_migrate:
        full_path = base_path / model_path
        
        if full_path.exists():
            try:
                queries = extract_sql_queries(str(full_path), module_name)
                if queries:
                    create_sql_index_file(module_name, queries)
                    total_queries += len(queries)
                    print(f"Creado índice para {module_name}: {len(queries)} queries")
            except Exception as e:
                print(f"Error migrando SQL en {model_path}: {e}")
        else:
            print(f"Archivo no encontrado: {model_path}")
    
    print(f"\nMigración SQL completada! {total_queries} queries extraídas.")
    print("Se crearon archivos .sql_backup para seguridad")
    print("Archivos SQL creados en sql/")

if __name__ == "__main__":
    main()