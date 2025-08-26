#!/usr/bin/env python3
"""
Análisis específico del módulo SCRIPTS
=====================================
"""

from tests.test_database_schema_validation import DatabaseSchemaValidator

def main():
    validator = DatabaseSchemaValidator()
    validator.setup_connections()
    queries = validator.extract_embedded_queries()

    print('📜 ANÁLISIS DEL MÓDULO SCRIPTS')
    print('=' * 50)

    # Filtrar consultas del módulo scripts
    scripts_errors = []
    scripts_valid = []

    for query_info in queries:
        validation_result = validator.validate_query_against_schema(query_info)
        
        file_path = validation_result['file']
        
        # Buscar archivos del módulo scripts
        if 'scripts' in file_path.lower():
            
            if not validation_result['valid']:
                scripts_errors.append(validation_result)
            else:
                scripts_valid.append(validation_result)

    print('📊 RESUMEN MÓDULO SCRIPTS:')
    print(f'   ✅ Consultas válidas: {len(scripts_valid)}')
    print(f'   ❌ Consultas inválidas: {len(scripts_errors)}')
    print()

    if scripts_errors:
        print('🚨 CONSULTAS PROBLEMÁTICAS EN SCRIPTS:')
        print('-' * 50)
        
        # Agrupar errores por tipo
        errores_por_tabla = {}
        archivos_con_errores = set()
        
        for i, error in enumerate(scripts_errors, 1):
            print(f'{i}. Archivo: {error["file"]}')
            archivos_con_errores.add(error["file"])
            
            query_display = error["query"][:200] + '...' if len(error['query']) > 200 else error["query"]
            print(f'   Query: {query_display}')
            print(f'   Errores: {error["errors"]}')
            
            # Contar errores por tabla
            for err_msg in error["errors"]:
                if "Tabla inexistente:" in err_msg:
                    tabla = err_msg.split("Tabla inexistente: ")[1]
                    errores_por_tabla[tabla] = errores_por_tabla.get(tabla, 0) + 1
            print('-' * 30)

        print()
        print('📊 ERRORES POR TABLA:')
        print('-' * 25)
        for tabla, count in sorted(errores_por_tabla.items(), key=lambda x: x[1], reverse=True):
            print(f'   {tabla}: {count} errores')
        
        print()
        print('📁 ARCHIVOS CON ERRORES:')
        print('-' * 25)
        for archivo in sorted(archivos_con_errores):
            print(f'   - {archivo}')
            
    else:
        print('✅ No se encontraron consultas problemáticas en scripts')

    # Listar todos los archivos en el directorio scripts
    print()
    print('📁 TODOS LOS ARCHIVOS EN SCRIPTS:')
    print('-' * 35)
    
    import os
    scripts_dir = "scripts"
    if os.path.exists(scripts_dir):
        for root, dirs, files in os.walk(scripts_dir):
            for file in files:
                if file.endswith('.py'):
                    full_path = os.path.join(root, file).replace('\\', '/')
                    print(f'   - {full_path}')
    else:
        print('   ℹ️ Directorio scripts no encontrado')

if __name__ == "__main__":
    main()
