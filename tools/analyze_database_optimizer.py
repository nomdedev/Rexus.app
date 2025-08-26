#!/usr/bin/env python3
"""
Análisis específico del módulo DATABASE_OPTIMIZER
================================================
"""

from tests.test_database_schema_validation import DatabaseSchemaValidator

def main():
    validator = DatabaseSchemaValidator()
    validator.setup_connections()
    queries = validator.extract_embedded_queries()

    print('🔧 ANÁLISIS DEL MÓDULO DATABASE_OPTIMIZER')
    print('=' * 55)

    # Filtrar consultas del database_optimizer
    optimizer_errors = []
    optimizer_valid = []

    for query_info in queries:
        validation_result = validator.validate_query_against_schema(query_info)
        
        file_path = validation_result['file']
        
        # Buscar archivos del database_optimizer
        if 'database_optimizer' in file_path.lower():
            
            if not validation_result['valid']:
                optimizer_errors.append(validation_result)
            else:
                optimizer_valid.append(validation_result)

    print('📊 RESUMEN MÓDULO DATABASE_OPTIMIZER:')
    print(f'   ✅ Consultas válidas: {len(optimizer_valid)}')
    print(f'   ❌ Consultas inválidas: {len(optimizer_errors)}')
    print()

    if optimizer_errors:
        print('🚨 CONSULTAS PROBLEMÁTICAS EN DATABASE_OPTIMIZER:')
        print('-' * 55)
        
        # Agrupar errores por tipo
        errores_por_tabla = {}
        errores_por_linea = {}
        
        for i, error in enumerate(optimizer_errors, 1):
            archivo = error["file"].replace('\\', '/')
            print(f'{i}. Archivo: {archivo}')
            
            query_display = error["query"][:200] + '...' if len(error['query']) > 200 else error["query"]
            print(f'   Query: {query_display}')
            print(f'   Errores: {error["errors"]}')
            
            # Contar errores por tabla
            for err_msg in error["errors"]:
                if "Tabla inexistente:" in err_msg or "no encontrada" in err_msg:
                    # Extraer nombre de tabla del mensaje
                    if "Tabla inexistente:" in err_msg:
                        tabla = err_msg.split("Tabla inexistente: ")[1]
                    elif "no encontrada" in err_msg:
                        import re
                        match = re.search(r"Tabla '([^']+)'", err_msg)
                        if match:
                            tabla = match.group(1)
                        else:
                            tabla = "DESCONOCIDA"
                    
                    errores_por_tabla[tabla] = errores_por_tabla.get(tabla, 0) + 1
            print('-' * 30)

        print()
        print('📊 ERRORES POR TABLA:')
        print('-' * 25)
        for tabla, count in sorted(errores_por_tabla.items(), key=lambda x: x[1], reverse=True):
            print(f'   {tabla}: {count} errores')
            
    else:
        print('✅ No se encontraron consultas problemáticas en database_optimizer')

    # Mostrar qué tipos de optimización se están intentando
    print()
    print('🔍 ANÁLISIS DEL PROPÓSITO DEL OPTIMIZADOR:')
    print('-' * 45)
    
    # Buscar el archivo database_optimizer.py
    import os
    optimizer_file = "utils/database_optimizer.py"
    if os.path.exists(optimizer_file):
        print(f'📁 Archivo encontrado: {optimizer_file}')
        
        # Leer algunas líneas para entender el propósito
        try:
            with open(optimizer_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()[:20]  # Primeras 20 líneas
            
            print('📋 Primeras líneas del archivo:')
            for i, line in enumerate(lines, 1):
                if line.strip():
                    print(f'   {i:2d}: {line.rstrip()}')
                    
        except Exception as e:
            print(f'   ❌ Error leyendo archivo: {e}')
    else:
        print(f'   ❌ Archivo no encontrado: {optimizer_file}')

    print()
    print('🗃️ TABLAS DISPONIBLES EN LA BD PARA OPTIMIZACIÓN:')
    print('-' * 55)

    for db_name in ['users', 'inventario']:
        tables = validator.get_all_tables(db_name)
        
        # Buscar tablas que podrían ser útiles para optimización
        optimization_tables = [table for table in tables if 
                              'log' in table.lower() or 
                              'audit' in table.lower() or
                              'performance' in table.lower() or
                              'metric' in table.lower() or
                              'cache' in table.lower()]
        
        if optimization_tables:
            print(f'📁 Base de datos: {db_name}')
            for table in sorted(optimization_tables):
                print(f'   ✅ {table}')
            print()
        
        # También mostrar algunas tablas principales para referencia
        if db_name == 'inventario':
            main_tables = [table for table in tables if table in ['productos', 'compras', 'obras', 'herrajes', 'vidrios']]
            if main_tables:
                print(f'📁 Tablas principales en {db_name}:')
                for table in sorted(main_tables):
                    print(f'   📊 {table}')
                print()

if __name__ == "__main__":
    main()
