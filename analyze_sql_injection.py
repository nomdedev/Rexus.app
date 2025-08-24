#!/usr/bin/env python3
"""
Script para identificar vulnerabilidades SQL injection en modelo de administración
"""
import re

def analyze_sql_injection_vulnerabilities():
    """Analiza el archivo model.py en busca de vulnerabilidades SQL injection"""
    file_path = 'rexus/modules/administracion/model.py'
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Patrones de vulnerabilidades SQL injection
        vulnerabilities = []
        
        # 1. f-strings con SQL
        pattern1 = r'f["\'](.*?)(INSERT|SELECT|UPDATE|DELETE|CREATE|DROP)(.*?)["\']\s*(?:,|\))'
        matches1 = re.finditer(pattern1, content, re.IGNORECASE | re.DOTALL)
        for match in matches1:
            line_num = content[:match.start()].count('\n') + 1
            vulnerabilities.append({
                'tipo': 'F-string SQL',
                'linea': line_num,
                'codigo': match.group(0)[:100] + '...' if len(match.group(0)) > 100 else match.group(0)
            })
        
        # 2. Concatenación directa de strings SQL
        pattern2 = r'["\'](.*?)(INSERT|SELECT|UPDATE|DELETE|CREATE|DROP)(.*?)["\']\s*\+\s*'
        matches2 = re.finditer(pattern2, content, re.IGNORECASE | re.DOTALL)
        for match in matches2:
            line_num = content[:match.start()].count('\n') + 1
            vulnerabilities.append({
                'tipo': 'Concatenación SQL',
                'linea': line_num,
                'codigo': match.group(0)[:100] + '...' if len(match.group(0)) > 100 else match.group(0)
            })
        
        # 3. cursor.execute con variables no parametrizadas
        pattern3 = r'cursor\.execute\s*\(\s*f?["\'](.*?)(INSERT|SELECT|UPDATE|DELETE)(.*?)["\']\s*(?:,|\)|\.format)'
        matches3 = re.finditer(pattern3, content, re.IGNORECASE | re.DOTALL)
        for match in matches3:
            line_num = content[:match.start()].count('\n') + 1
            # Solo si no usa parámetros preparados (?)
            if '?' not in match.group(0):
                vulnerabilities.append({
                    'tipo': 'cursor.execute vulnerable',
                    'linea': line_num,
                    'codigo': match.group(0)[:100] + '...' if len(match.group(0)) > 100 else match.group(0)
                })
        
        # 4. Buscar métodos que no usan sql_manager
        methods_without_sql_manager = []
        method_pattern = r'def\s+(\w+)\s*\([^)]*\):'
        methods = re.finditer(method_pattern, content)
        
        for method in methods:
            method_name = method.group(1)
            method_start = method.start()
            
            # Buscar el siguiente método o final de clase
            next_method = re.search(method_pattern, content[method.end():])
            if next_method:
                method_end = method.end() + next_method.start()
            else:
                method_end = len(content)
            
            method_content = content[method_start:method_end]
            
            # Si tiene cursor.execute pero no sql_manager
            if 'cursor.execute' in method_content and 'sql_manager' not in method_content:
                if any(keyword in method_content.upper() for keyword in ['INSERT', 'SELECT', 'UPDATE', 'DELETE']):
                    methods_without_sql_manager.append(method_name)
        
        # Mostrar resultados
        print(f"🔍 ANÁLISIS SQL INJECTION - {file_path}")
        print(f"=" * 60)
        
        if vulnerabilities:
            print(f"\n❌ VULNERABILIDADES ENCONTRADAS ({len(vulnerabilities)}):")
            for vuln in vulnerabilities:
                print(f"  📍 Línea {vuln['linea']} - {vuln['tipo']}")
                print(f"     {vuln['codigo']}")
                print()
        
        if methods_without_sql_manager:
            print(f"\n⚠️ MÉTODOS SIN SQL_MANAGER ({len(methods_without_sql_manager)}):")
            for method in methods_without_sql_manager:
                print(f"  🔧 {method}()")
            print()
        
        # Archivos SQL necesarios
        required_sql_files = [
            'insert_auditoria.sql',
            'insert_empleado.sql', 
            'insert_departamento.sql',
            'select_empleados_activos.sql',
            'select_departamentos_activos.sql',
            'insert_asiento_contable.sql',
            'insert_recibo.sql',
            'insert_pago_obra.sql',
            'insert_compra_material.sql',
            'update_recibo_impreso.sql',
            'select_libro_contable.sql',
            'select_recibos.sql',
            'select_pagos_obra.sql',
            'select_auditoria.sql'
        ]
        
        print(f"📁 ARCHIVOS SQL REQUERIDOS ({len(required_sql_files)}):")
        for sql_file in required_sql_files:
            print(f"  📄 sql/administracion/{sql_file}")
        
        print(f"\n✅ RESUMEN:")
        print(f"  - Vulnerabilidades encontradas: {len(vulnerabilities)}")
        print(f"  - Métodos a corregir: {len(methods_without_sql_manager)}")
        print(f"  - Archivos SQL necesarios: {len(required_sql_files)}")
        
    except Exception as e:
        print(f"❌ Error analizando archivo: {e}")

if __name__ == '__main__':
    analyze_sql_injection_vulnerabilities()
