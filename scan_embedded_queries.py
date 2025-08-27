#!/usr/bin/env python3
"""
Script para escanear y catalogar queries SQL embebidos en módulos
Genera un reporte detallado para facilitar la migración
"""
import os
import re
from pathlib import Path

def extract_sql_queries(file_path):
    """Extrae queries SQL embebidos de un archivo Python"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception:
        return []
    
    queries = []
    
    # Patrones para detectar SQL embebido
    patterns = [
        # Triple quotes multiline
        (r'"""\s*((?:SELECT|INSERT|UPDATE|DELETE|CREATE|ALTER|DROP).*?)"""', 'MULTILINE_TRIPLE'),
        # Single quotes multiline  
        (r"'''\s*((?:SELECT|INSERT|UPDATE|DELETE|CREATE|ALTER|DROP).*?)'''", 'MULTILINE_SINGLE'),
        # Execute statements
        (r'\.execute\s*\(\s*["\']([^"\']*(?:SELECT|INSERT|UPDATE|DELETE|CREATE|ALTER|DROP)[^"\']*)["\']', 'EXECUTE_DIRECT'),
        # Query variables
        (r'(?:query|sql|consulta)\s*=\s*["\']([^"\']*(?:SELECT|INSERT|UPDATE|DELETE|CREATE|ALTER|DROP)[^"\']*)["\']', 'VARIABLE'),
        # f-strings with SQL
        (r'f["\']([^"\']*(?:SELECT|INSERT|UPDATE|DELETE|CREATE|ALTER|DROP)[^"\']*)["\']', 'F_STRING'),
    ]
    
    for pattern, query_type in patterns:
        matches = re.finditer(pattern, content, re.IGNORECASE | re.DOTALL)
        for match in matches:
            line_num = content[:match.start()].count('\n') + 1
            sql_content = match.group(1).strip()
            
            # Limpiar el SQL para analysis
            clean_sql = ' '.join(sql_content.split())
            if len(clean_sql) > 20:  # Filtrar queries muy pequeños
                queries.append({
                    'line': line_num,
                    'type': query_type,
                    'sql': sql_content,
                    'preview': clean_sql[:80] + '...' if len(clean_sql) > 80 else clean_sql,
                    'operation': get_sql_operation(clean_sql)
                })
    
    return queries

def get_sql_operation(sql):
    """Determina el tipo de operación SQL"""
    sql_upper = sql.upper().strip()
    if sql_upper.startswith('SELECT'):
        return 'SELECT'
    elif sql_upper.startswith('INSERT'):
        return 'INSERT'
    elif sql_upper.startswith('UPDATE'):
        return 'UPDATE'
    elif sql_upper.startswith('DELETE'):
        return 'DELETE'
    elif sql_upper.startswith('CREATE'):
        return 'CREATE'
    elif sql_upper.startswith('ALTER'):
        return 'ALTER'
    elif sql_upper.startswith('DROP'):
        return 'DROP'
    else:
        return 'OTHER'

def scan_module(module_path):
    """Escanea un módulo completo por queries embebidos"""
    module_queries = {}
    
    # Archivos a escanear en cada módulo
    files_to_scan = ['model.py', 'controller.py', 'view.py']
    
    for filename in files_to_scan:
        file_path = os.path.join(module_path, filename)
        if os.path.exists(file_path):
            queries = extract_sql_queries(file_path)
            if queries:
                module_queries[filename] = queries
    
    # También escanear submodules si existe
    submodules_path = os.path.join(module_path, 'submodules')
    if os.path.exists(submodules_path):
        for subfile in os.listdir(submodules_path):
            if subfile.endswith('.py'):
                subfile_path = os.path.join(submodules_path, subfile)
                queries = extract_sql_queries(subfile_path)
                if queries:
                    module_queries[f'submodules/{subfile}'] = queries
    
    return module_queries

def generate_migration_suggestions(module_name, queries_by_file):
    """Genera sugerencias de archivos SQL para migración"""
    suggestions = []
    
    for filename, queries in queries_by_file.items():
        for query in queries:
            operation = query['operation'].lower()
            preview = query['preview'].replace(' ', '_').replace(',', '')[:30]
            
            # Generar nombre de archivo sugerido
            if 'SELECT' in query['operation']:
                if 'COUNT' in query['sql'].upper():
                    suggested_name = f"count_{preview.lower()}.sql"
                else:
                    suggested_name = f"select_{preview.lower()}.sql"
            elif 'INSERT' in query['operation']:
                suggested_name = f"insert_{preview.lower()}.sql"
            elif 'UPDATE' in query['operation']:
                suggested_name = f"update_{preview.lower()}.sql"
            elif 'DELETE' in query['operation']:
                suggested_name = f"delete_{preview.lower()}.sql"
            else:
                suggested_name = f"{operation}_{preview.lower()}.sql"
            
            # Limpiar caracteres especiales del nombre
            suggested_name = re.sub(r'[^\w\.]', '_', suggested_name)
            suggested_name = re.sub(r'_+', '_', suggested_name)
            
            suggestions.append({
                'file': filename,
                'line': query['line'],
                'operation': query['operation'],
                'suggested_sql_file': f"sql/{module_name}/{suggested_name}",
                'preview': query['preview']
            })
    
    return suggestions

def main():
    """Función principal"""
    print("="*80)
    print("ESCANEANDO QUERIES SQL EMBEBIDOS EN MODULOS REXUS")
    print("="*80)
    print()
    
    modules_dir = Path("rexus/modules")
    if not modules_dir.exists():
        print("ERROR: Directorio rexus/modules no encontrado")
        return
    
    # Obtener módulos numerados
    numbered_modules = []
    for item in modules_dir.iterdir():
        if item.is_dir() and item.name.startswith(('01_', '02_', '03_', '04_', '05_', '06_', '07_', '08_', '09_', '10_', '11_', '12_', '13_')):
            numbered_modules.append(item.name)
    
    numbered_modules.sort()
    
    total_queries = 0
    modules_with_queries = 0
    detailed_report = {}
    
    for module_name in numbered_modules:
        module_path = modules_dir / module_name
        print(f"Escaneando {module_name}...")
        
        module_queries = scan_module(module_path)
        
        if module_queries:
            modules_with_queries += 1
            detailed_report[module_name] = module_queries
            
            # Contar queries en este módulo
            module_query_count = sum(len(queries) for queries in module_queries.values())
            total_queries += module_query_count
            
            print(f"  -> {module_query_count} queries encontrados")
            
            # Mostrar detalle por archivo
            for filename, queries in module_queries.items():
                print(f"     {filename}: {len(queries)} queries")
                for query in queries[:3]:  # Mostrar solo primeros 3
                    print(f"       Linea {query['line']}: {query['operation']} - {query['preview']}")
                if len(queries) > 3:
                    print(f"       ... y {len(queries)-3} más")
        else:
            print(f"  -> Sin queries embebidos")
    
    print()
    print("="*80)
    print("RESUMEN DEL ESCANEO")
    print("="*80)
    print(f"Módulos escaneados: {len(numbered_modules)}")
    print(f"Módulos con queries embebidos: {modules_with_queries}")
    print(f"Total queries encontrados: {total_queries}")
    print()
    
    # Mostrar módulos prioritarios por cantidad de queries
    if detailed_report:
        print("MODULOS PRIORITARIOS PARA MIGRACION:")
        module_counts = []
        for module_name, module_queries in detailed_report.items():
            count = sum(len(queries) for queries in module_queries.values())
            module_counts.append((module_name, count))
        
        module_counts.sort(key=lambda x: x[1], reverse=True)
        
        for i, (module_name, count) in enumerate(module_counts[:5], 1):
            print(f"{i}. {module_name}: {count} queries")
    
    print()
    print("="*80)
    print("SIGUIENTE PASO: Migrar queries por módulo en orden de prioridad")
    print("="*80)
    
    return detailed_report

if __name__ == "__main__":
    main()