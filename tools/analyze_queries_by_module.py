#!/usr/bin/env python3
"""
Análisis de consultas problemáticas por módulo
==============================================
Script para generar un resumen detallado de errores por módulo
"""

from tests.test_database_schema_validation import DatabaseSchemaValidator
import collections

def main():
    validator = DatabaseSchemaValidator()
    validator.setup_connections()
    queries = validator.extract_embedded_queries()

    print('🔍 ANÁLISIS POR MÓDULO - CONSULTAS PROBLEMÁTICAS')
    print('=' * 60)

    # Analizar cada consulta
    module_errors = collections.defaultdict(list)
    valid_queries = 0
    invalid_queries = 0

    for query_info in queries:
        validation_result = validator.validate_query_against_schema(query_info)
        
        if not validation_result['valid']:
            # Extraer módulo del archivo
            file_path = validation_result['file']
            if 'rexus/' in file_path:
                module_parts = file_path.replace('rexus/', '').split('/')
                if len(module_parts) >= 2:
                    module = module_parts[0] + '/' + module_parts[1]
                else:
                    module = module_parts[0] if module_parts else 'core'
            else:
                module = file_path.split('/')[0] if '/' in file_path else 'root'
            
            module_errors[module].append({
                'file': validation_result['file'],
                'query': validation_result['query'][:100] + '...' if len(validation_result['query']) > 100 else validation_result['query'],
                'errors': validation_result['errors']
            })
            invalid_queries += 1
        else:
            valid_queries += 1

    # Mostrar resumen por módulo
    print(f'📊 RESUMEN GENERAL:')
    print(f'   ✅ Consultas válidas: {valid_queries}')
    print(f'   ❌ Consultas inválidas: {invalid_queries}')
    print(f'   📁 Módulos con problemas: {len(module_errors)}')
    print()

    # Ordenar módulos por cantidad de errores (descendente)
    sorted_modules = sorted(module_errors.items(), key=lambda x: len(x[1]), reverse=True)

    for module, errors in sorted_modules:
        print(f'📁 MÓDULO: {module}')
        print(f'   🚨 Errores: {len(errors)}')
        
        # Contar tipos de errores
        error_types = collections.defaultdict(int)
        for error in errors:
            for err_msg in error['errors']:
                if 'no encontrada en ninguna base de datos' in err_msg:
                    table_name = err_msg.split("'")[1]
                    error_types[f'Tabla inexistente: {table_name}'] += 1
                elif 'no existe en tabla' in err_msg:
                    column_name = err_msg.split("'")[1]
                    error_types[f'Columna inexistente: {column_name}'] += 1
                else:
                    error_types['Otro error'] += 1
        
        for error_type, count in sorted(error_types.items(), key=lambda x: x[1], reverse=True):
            print(f'     - {error_type}: {count}')
        print()

    print('🎯 PRIORIZACIÓN RECOMENDADA:')
    print('=' * 40)
    for i, (module, errors) in enumerate(sorted_modules[:5], 1):
        print(f'{i}. {module}: {len(errors)} errores')

    # Generar reporte detallado en Markdown
    generate_markdown_report(sorted_modules, valid_queries, invalid_queries)

def generate_markdown_report(sorted_modules, valid_queries, invalid_queries):
    """Genera un reporte detallado en formato Markdown"""
    
    with open('RESUMEN_ERRORES_POR_MODULO.md', 'w', encoding='utf-8') as f:
        f.write("# 📊 RESUMEN DE CONSULTAS PROBLEMÁTICAS POR MÓDULO\n\n")
        f.write(f"**Fecha:** {__import__('datetime').datetime.now().strftime('%d de %B de %Y')}\n\n")
        
        f.write("## 📈 Estadísticas Generales\n\n")
        f.write(f"- ✅ **Consultas válidas:** {valid_queries}\n")
        f.write(f"- ❌ **Consultas inválidas:** {invalid_queries}\n")
        f.write(f"- 📁 **Módulos con problemas:** {len(sorted_modules)}\n")
        f.write(f"- 📊 **Total consultas analizadas:** {valid_queries + invalid_queries}\n\n")
        
        f.write("## 🎯 Priorización por Módulo\n\n")
        f.write("| Posición | Módulo | Cantidad de Errores | Prioridad |\n")
        f.write("|----------|--------|--------------------|-----------|\n")
        
        for i, (module, errors) in enumerate(sorted_modules[:10], 1):
            priority = "🔥 ALTA" if len(errors) >= 10 else "⚠️ MEDIA" if len(errors) >= 5 else "🟡 BAJA"
            f.write(f"| {i} | `{module}` | {len(errors)} | {priority} |\n")
        
        f.write("\n## 📁 Detalle por Módulo\n\n")
        
        for module, errors in sorted_modules:
            f.write(f"### 📁 {module}\n")
            f.write(f"**Errores encontrados:** {len(errors)}\n\n")
            
            # Contar tipos de errores
            error_types = collections.defaultdict(int)
            for error in errors:
                for err_msg in error['errors']:
                    if 'no encontrada en ninguna base de datos' in err_msg:
                        table_name = err_msg.split("'")[1]
                        error_types[f'Tabla inexistente: `{table_name}`'] += 1
                    elif 'no existe en tabla' in err_msg:
                        column_name = err_msg.split("'")[1]
                        error_types[f'Columna inexistente: `{column_name}`'] += 1
                    else:
                        error_types['Otro error'] += 1
            
            f.write("**Tipos de errores:**\n")
            for error_type, count in sorted(error_types.items(), key=lambda x: x[1], reverse=True):
                f.write(f"- {error_type}: {count}\n")
            
            f.write(f"\n**Archivos afectados:**\n")
            files = set(error['file'] for error in errors)
            for file in sorted(files):
                f.write(f"- `{file}`\n")
            
            f.write("\n---\n\n")
        
        f.write("## ⚡ Acciones Recomendadas\n\n")
        f.write("1. **Prioridad ALTA** (>= 10 errores): Atacar primero los módulos con más errores\n")
        f.write("2. **Estandarizar nombres de tablas** según el esquema real de SQL Server\n")
        f.write("3. **Eliminar consultas de metadatos** de otros SGBD (SQLite, MySQL, etc.)\n")
        f.write("4. **Verificar columnas** contra el esquema real\n")
        f.write("5. **Crear tablas faltantes** si son necesarias para la funcionalidad\n\n")
        
    print(f"\n✅ Reporte detallado guardado en: RESUMEN_ERRORES_POR_MODULO.md")

if __name__ == "__main__":
    main()
