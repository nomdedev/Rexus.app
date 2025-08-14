#!/usr/bin/env python3
"""
Script para detectar y corregir vulnerabilidades de SQL injection
Parte del checklist de preparación para producción
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Tuple

class SQLInjectionFixer:
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path)
        self.vulnerabilities_found = []
        self.fixes_applied = []

    def detect_sql_vulnerabilities(self) -> List[Dict]:
        """Detecta vulnerabilidades de SQL injection en archivos Python."""
        vulnerabilities = []

        # Patrones peligrosos de SQL injection
        dangerous_patterns = [
            # f-strings en consultas SQL
            (r'f"[^"]*\{[^}]*\}[^"]*".*(?:execute|query|cursor)', 'f-string en consulta SQL'),
            # .format() en consultas SQL
            (r'\.format\([^)]*\).*(?:execute|query|cursor)', '.format() en consulta SQL'),
            # Concatenación con + en consultas SQL
            (r'"[^"]*"\s*\+[^;]*(?:execute|query|cursor)', 'Concatenación + en consulta SQL'),
            # % formatting en consultas SQL
            (r'%.*%.*(?:execute|query|cursor)', '% formatting en consulta SQL'),
            # execute() sin parámetros preparados
            (r'cursor\.execute\s*\(\s*[^?]*["\'][^"\']*["\'][^)]*\)', 'execute() sin parámetros'),
            # Variables directamente interpoladas en queries
            (r'(SELECT|INSERT|UPDATE|DELETE)[^?]*\{[^}]*\}', 'Variable interpolada en query'),
        ]

        for py_file in self.root_path.rglob("*.py"):
            # Saltar archivos no relevantes
            if any(skip in str(py_file) for skip in ['__pycache__',
'.pyc',
                'backup',
                '.venv',
                'test']):
                continue

            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                lines = content.split('\n')
                for i, line in enumerate(lines, 1):
                    for pattern, description in dangerous_patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            vulnerabilities.append({
                                'file': str(py_file.relative_to(self.root_path)),
                                'line': i,
                                'content': line.strip(),
                                'type': description,
                                'pattern': pattern
                            })

            except Exception as e:
                continue

        return vulnerabilities

    def fix_f_string_queries(self,
file_path: str,
        line_num: int,
        line_content: str) -> str:
        """Corrige f-strings en consultas SQL convirtiendo a parámetros preparados."""
        # Ejemplo: f"SELECT * FROM users WHERE id = {user_id}"
        # Se convierte a: "SELECT * FROM users WHERE id = ?", (user_id,)

        # Buscar f-strings con variables
        f_string_pattern = r'f"([^"]*\{([^}]*)\}[^"]*)"'
        match = re.search(f_string_pattern, line_content)

        if match:
            query_template = match.group(1)
            variables = re.findall(r'\{([^}]*)\}', query_template)

            # Reemplazar variables con placeholders
            fixed_query = query_template
            for var in variables:
                fixed_query = fixed_query.replace(f'{{{var}}}', '?')

            # Construir línea corregida
            if len(variables) == 1:
                params = f"({variables[0]},)"
            else:
                params = f"({', '.join(variables)})"

            new_line = line_content.replace(
                f'f"{query_template}"',
                f'"{fixed_query}", {params}'
            )

            return new_line

        return line_content

    def fix_format_queries(self,
file_path: str,
        line_num: int,
        line_content: str) -> str:
        """Corrige .format() en consultas SQL."""
        # Buscar patrones .format()
        format_pattern = r'"([^"]+)"\.format\(([^)]+)\)'
        match = re.search(format_pattern, line_content)

        if match:
            query_template = match.group(1)
            format_args = match.group(2)

            # Reemplazar {} con ?
            fixed_query = re.sub(r'\{\}', '?', query_template)
            fixed_query = re.sub(r'\{[^}]*\}', '?', fixed_query)

            new_line = line_content.replace(
                f'"{query_template}".format({format_args})',
                f'"{fixed_query}", ({format_args})'
            )

            return new_line

        return line_content

    def apply_fixes(self, vulnerabilities: List[Dict]) -> List[str]:
        """Aplica correcciones a las vulnerabilidades encontradas."""
        fixes_applied = []
        files_to_fix = {}

        # Agrupar vulnerabilidades por archivo
        for vuln in vulnerabilities:
            file_path = vuln['file']
            if file_path not in files_to_fix:
                files_to_fix[file_path] = []
            files_to_fix[file_path].append(vuln)

        for file_path, vulns in files_to_fix.items():
            try:
                full_path = self.root_path / file_path
                with open(full_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()

                # Aplicar correcciones (de abajo hacia arriba para mantener números de línea)
                vulns_sorted = sorted(vulns, key=lambda x: x['line'], reverse=True)

                for vuln in vulns_sorted:
                    line_idx = vuln['line'] - 1
                    original_line = lines[line_idx]

                    # Aplicar corrección según el tipo
                    if 'f-string' in vuln['type']:
                        fixed_line = self.fix_f_string_queries(file_path, vuln['line'], original_line)
                    elif 'format()' in vuln['type']:
                        fixed_line = self.fix_format_queries(file_path, vuln['line'], original_line)
                    else:
                        # Para otros tipos, añadir comentario de advertencia
                        fixed_line = f"        # TODO: SECURITY - Fix SQL injection: {original_line.strip()}\n        {original_line}"

                    if fixed_line != original_line:
                        lines[line_idx] = fixed_line
                        fixes_applied.append(f"{file_path}:{vuln['line']} - {vuln['type']}")

                # Escribir archivo corregido
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)

            except Exception as e:
                print(f"Error procesando {file_path}: {e}")

        return fixes_applied

    def generate_security_report(self) -> Dict:
        """Genera reporte completo de seguridad SQL."""
        print("🔍 Detectando vulnerabilidades de SQL injection...")

        vulnerabilities = self.detect_sql_vulnerabilities()

        # Filtrar vulnerabilidades en archivos del proyecto (no librerías)
        project_vulns = [
            v for v in vulnerabilities
            if not any(exclude in v['file'] for exclude in ['.venv', 'site-packages', 'backup'])
        ]

        print(f"📊 Vulnerabilidades encontradas en el proyecto: {len(project_vulns)}")

        if project_vulns:
            print("\n🚨 VULNERABILIDADES CRÍTICAS:")
            for vuln in project_vulns[:10]:  # Mostrar primeras 10
                print(f"  • {vuln['file']}:{vuln['line']} - {vuln['type']}")
                print(f"    {vuln['content'][:80]}...")

            if len(project_vulns) > 10:
                print(f"  • ... y {len(project_vulns) - 10} más")

        return {
            'total_vulnerabilities': len(project_vulns),
            'vulnerabilities': project_vulns,
            'needs_fixing': len(project_vulns) > 0
        }

def main():
    print("🛡️ CORRECTOR DE VULNERABILIDADES SQL - REXUS.APP")
    print("=" * 60)

    fixer = SQLInjectionFixer()
    report = fixer.generate_security_report()

    if report['needs_fixing']:
        print(f"\n⚠️ Se encontraron {report['total_vulnerabilities']} vulnerabilidades que requieren atención manual.")
        print("📋 Recomendaciones:")
        print("1. Usar parámetros preparados (?) en lugar de interpolación de strings")
        print("2. Validar y sanitizar todas las entradas de usuario")
        print("3. Usar SQLQueryManager para consultas seguras")
        print("4. Revisar y corregir manualmente cada caso")

        # Mostrar ejemplos de corrección
        print(f"\n💡 EJEMPLOS DE CORRECCIÓN:")
        print("❌ Incorrecto:")
        print('   cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")')
        print("✅ Correcto:")
        print('   cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))')

    else:
        print(f"\n✅ No se encontraron vulnerabilidades de SQL injection en el proyecto")

    return report

if __name__ == "__main__":
    main()
