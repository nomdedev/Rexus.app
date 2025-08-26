#!/usr/bin/env python3
"""
Análisis específico del módulo COMPRAS
=====================================
"""

from tests.test_database_schema_validation import DatabaseSchemaValidator

def main():
    validator = DatabaseSchemaValidator()
    validator.setup_connections()
    queries = validator.extract_embedded_queries()

    print('🛒 ANÁLISIS DEL MÓDULO COMPRAS')
    print('=' * 50)

    # Filtrar consultas del módulo compras
    compras_errors = []
    compras_valid = []

    for query_info in queries:
        validation_result = validator.validate_query_against_schema(query_info)
        
        file_path = validation_result['file']
        
        # Buscar archivos del módulo compras
        if 'modules/compras' in file_path.lower():
            
            if not validation_result['valid']:
                compras_errors.append(validation_result)
            else:
                compras_valid.append(validation_result)

    print('📊 RESUMEN MÓDULO COMPRAS:')
    print(f'   ✅ Consultas válidas: {len(compras_valid)}')
    print(f'   ❌ Consultas inválidas: {len(compras_errors)}')
    print()

    if compras_errors:
        print('🚨 CONSULTAS PROBLEMÁTICAS EN COMPRAS:')
        print('-' * 50)
        
        # Agrupar errores por tipo
        errores_por_tabla = {}
        errores_por_archivo = {}
        
        for i, error in enumerate(compras_errors, 1):
            archivo = error["file"].replace('\\', '/')
            print(f'{i}. Archivo: {archivo}')
            
            # Contar errores por archivo
            errores_por_archivo[archivo] = errores_por_archivo.get(archivo, 0) + 1
            
            query_display = error["query"][:150] + '...' if len(error['query']) > 150 else error["query"]
            print(f'   Query: {query_display}')
            print(f'   Errores: {error["errors"]}')
            
            # Contar errores por tabla
            for err_msg in error["errors"]:
                if "Tabla inexistente:" in err_msg or "no encontrada" in err_msg:
                    # Extraer nombre de tabla del mensaje
                    if "Tabla inexistente:" in err_msg:
                        tabla = err_msg.split("Tabla inexistente: ")[1]
                    elif "no encontrada" in err_msg:
                        # Para mensajes como "Tabla 'X' no encontrada en ninguna base de datos"
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
        
        print()
        print('📁 ERRORES POR ARCHIVO:')
        print('-' * 25)
        for archivo, count in sorted(errores_por_archivo.items(), key=lambda x: x[1], reverse=True):
            archivo_corto = archivo.split('/')[-1]
            print(f'   {archivo_corto}: {count} errores')
            
    else:
        print('✅ No se encontraron consultas problemáticas en compras')

    # Mostrar tablas relacionadas con compras que SÍ existen
    print()
    print('🗃️ TABLAS DE COMPRAS QUE SÍ EXISTEN EN LA BD:')
    print('-' * 45)

    for db_name in ['users', 'inventario']:
        tables = validator.get_all_tables(db_name)
        compras_tables = [table for table in tables if 
                         'compra' in table.lower() or 
                         'pedido' in table.lower() or 
                         'orden' in table.lower() or
                         'proveedor' in table.lower()]
        
        if compras_tables:
            print(f'📁 Base de datos: {db_name}')
            for table in sorted(compras_tables):
                print(f'   ✅ {table}')
            print()

    # Listar archivos del módulo compras
    print('📁 ARCHIVOS EN EL MÓDULO COMPRAS:')
    print('-' * 35)
    
    import os
    compras_dir = "rexus/modules/compras"
    if os.path.exists(compras_dir):
        for root, dirs, files in os.walk(compras_dir):
            for file in files:
                if file.endswith('.py'):
                    full_path = os.path.join(root, file).replace('\\', '/')
                    rel_path = full_path.replace('rexus/modules/compras/', '')
                    print(f'   - {rel_path}')
    else:
        print('   ℹ️ Directorio rexus/modules/compras no encontrado')

if __name__ == "__main__":
    main()
