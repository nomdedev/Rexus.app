#!/usr/bin/env python3
"""
Análisis específico del módulo de OBRAS
======================================
"""

from tests.test_database_schema_validation import DatabaseSchemaValidator

def main():
    validator = DatabaseSchemaValidator()
    validator.setup_connections()
    queries = validator.extract_embedded_queries()

    print('🏗️ ANÁLISIS DEL MÓDULO DE OBRAS')
    print('=' * 50)

    # Filtrar consultas relacionadas con obras
    obras_errors = []
    obras_valid = []

    for query_info in queries:
        validation_result = validator.validate_query_against_schema(query_info)
        
        file_path = validation_result['file']
        
        # Buscar archivos relacionados con obras
        if ('obras' in file_path.lower() or 
            'cronograma' in file_path.lower() or
            'proyecto' in file_path.lower() or
            'obra' in validation_result['query'].lower()):
            
            if not validation_result['valid']:
                obras_errors.append(validation_result)
            else:
                obras_valid.append(validation_result)

    print('📊 RESUMEN MÓDULO OBRAS:')
    print(f'   ✅ Consultas válidas: {len(obras_valid)}')
    print(f'   ❌ Consultas inválidas: {len(obras_errors)}')
    print()

    if obras_errors:
        print('🚨 CONSULTAS PROBLEMÁTICAS EN OBRAS:')
        print('-' * 45)
        
        for i, error in enumerate(obras_errors, 1):
            print(f'{i}. Archivo: {error["file"]}')
            query_display = error["query"][:100] + '...' if len(error['query']) > 100 else error["query"]
            print(f'   Query: {query_display}')
            print(f'   Errores: {error["errors"]}')
            print()
    else:
        print('✅ No se encontraron consultas problemáticas específicas de obras')

    # También buscar tablas relacionadas con obras en la BD
    print('🗃️ TABLAS RELACIONADAS CON OBRAS EN LA BD:')
    print('-' * 45)

    for db_name in ['users', 'inventario']:
        tables = validator.get_all_tables(db_name)
        obras_tables = [table for table in tables if 'obra' in table.lower() or 'proyecto' in table.lower() or 'cronograma' in table.lower()]
        
        if obras_tables:
            print(f'📁 Base de datos: {db_name}')
            for table in obras_tables:
                print(f'   - {table}')
            print()

    # Buscar archivos relacionados con obras en el proyecto
    print('📁 ARCHIVOS RELACIONADOS CON OBRAS EN EL PROYECTO:')
    print('-' * 50)
    
    import os
    obras_files = []
    for root, dirs, files in os.walk('rexus'):
        for file in files:
            if file.endswith('.py'):
                full_path = os.path.join(root, file)
                if ('obra' in full_path.lower() or 
                    'cronograma' in full_path.lower() or
                    'proyecto' in full_path.lower()):
                    obras_files.append(full_path.replace('\\', '/'))
    
    if obras_files:
        for file in sorted(obras_files):
            print(f'   - {file}')
    else:
        print('   ℹ️ No se encontraron archivos específicos de obras')

if __name__ == "__main__":
    main()
