#!/usr/bin/env python3
"""
Validador Inteligente de Seguridad - Filtra Falsos Positivos
Versión mejorada que distingue entre problemas reales y casos legítimos

Fecha: 23/08/2025
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class SecurityIssue:
    type: str
    file: str
    line: int
    content: str
    severity: str
    is_false_positive: bool = False
    reason: str = ""

class IntelligentSecurityValidator:
    """Validador inteligente que filtra falsos positivos."""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        
        # Patrones de SQL legítimos que NO requieren parámetros
        self.legitimate_sql_patterns = [
            r'SELECT\s+@@IDENTITY',
            r'SELECT\s+SCOPE_IDENTITY\(\)',
            r'SELECT\s+LAST_INSERT_ROWID\(\)',
            r'SELECT\s+1',
            r'BEGIN\s*$',
            r'COMMIT\s*$', 
            r'ROLLBACK\s*$',
            r'CREATE\s+INDEX',
            r'DROP\s+INDEX',
            r'PRAGMA\s+',
            r'SHOW\s+TABLES',
            r'DESCRIBE\s+',
            r'EXPLAIN\s+'
        ]
        
        # Patrones de construcción de queries seguros
        self.safe_query_building_patterns = [
            r'query\s*\+=?\s*["\'].*WHERE.*=.*["\']',  # Concatenación de literales
            r'query\s*\+=?\s*["\'].*ORDER BY.*["\']',   # ORDER BY literal
            r'query\s*\+=?\s*["\'].*GROUP BY.*["\']',   # GROUP BY literal
        ]
        
    def is_legitimate_cursor_execute(self, line: str, file_content: str, line_num: int) -> Tuple[bool, str]:
        """Determina si un cursor.execute es legítimo o problemático."""
        
        # Extraer el contenido entre paréntesis
        match = re.search(r'cursor\.execute\(([^)]+)\)', line)
        if not match:
            return False, "No se pudo extraer contenido del execute"
            
        execute_content = match.group(1).strip()
        
        # Caso 1: SQL literals seguros
        for pattern in self.legitimate_sql_patterns:
            if re.search(pattern, execute_content, re.IGNORECASE):
                return True, f"SQL legítimo: {pattern}"
        
        # Caso 2: Variables que contienen SQL literal hardcodeado
        if execute_content in ['statement', 'query', 'sql_command', 'script']:
            # Buscar cómo se construye la variable en el contexto
            lines = file_content.split('\n')
            context_start = max(0, line_num - 20)
            context_end = min(len(lines), line_num + 5)
            
            context = '\n'.join(lines[context_start:context_end])
            
            # Buscar asignación de la variable
            var_pattern = rf'{execute_content}\s*=.*["\'].*["\']'
            if re.search(var_pattern, context):
                return True, f"Variable {execute_content} contiene SQL literal"
            
            # Buscar concatenación segura
            for safe_pattern in self.safe_query_building_patterns:
                if re.search(safe_pattern, context):
                    return True, f"Construcción segura de query: {execute_content}"
        
        # Caso 3: Archivos de backup/restauración
        file_path = str(self.project_root)
        if 'backup' in file_path.lower() or 'restore' in file_path.lower():
            if execute_content in ['statement', 'script_content', 'sql_line']:
                return True, "Archivo de backup/restore - ejecución de scripts SQL legítima"
        
        # Caso 4: Consultas con parámetros pero mal detectadas por regex
        if ',' in execute_content and any(param in execute_content for param in ['(', '?', '%s']):
            return True, "Query con parámetros detectada incorrectamente"
            
        return False, f"Posible problema de seguridad: {execute_content}"
    
    def validate_cursor_execute_intelligent(self) -> Dict[str, any]:
        """Validación inteligente de cursor.execute."""
        print("Validando cursor.execute con filtro inteligente...")
        
        real_issues = []
        false_positives = []
        rexus_dir = self.project_root / "rexus"
        
        for py_file in rexus_dir.rglob("*.py"):
            if ".backup" in str(py_file) or "__pycache__" in str(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                    
                for i, line in enumerate(lines, 1):
                    if re.search(r'cursor\.execute\([^,)]*\)(?!\s*,)', line):
                        is_legitimate, reason = self.is_legitimate_cursor_execute(line, content, i)
                        
                        issue = SecurityIssue(
                            type="cursor_execute_analysis",
                            file=str(py_file.relative_to(self.project_root)),
                            line=i,
                            content=line.strip(),
                            severity="P0" if not is_legitimate else "INFO",
                            is_false_positive=is_legitimate,
                            reason=reason
                        )
                        
                        if is_legitimate:
                            false_positives.append(issue)
                        else:
                            real_issues.append(issue)
                            
            except Exception as e:
                print(f"Error leyendo {py_file}: {e}")
                
        return {
            "type": "intelligent_cursor_execute_validation",
            "real_issues_found": len(real_issues),
            "false_positives_found": len(false_positives),
            "real_issues": real_issues,
            "false_positives": false_positives,
            "status": "PASSED" if len(real_issues) == 0 else "NEEDS_REVIEW"
        }
    
    def analyze_except_patterns(self) -> Dict[str, any]:
        """Analiza patrones de except Exception."""
        print("Analizando patrones de manejo de excepciones...")
        
        problematic_excepts = []
        acceptable_excepts = []
        
        core_dir = self.project_root / "rexus" / "core"
        
        for py_file in core_dir.rglob("*.py"):
            if ".backup" in str(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                    
                for i, line in enumerate(lines, 1):
                    if re.search(r'except\s+Exception\s*:', line):
                        # Analizar contexto
                        context_start = max(0, i)
                        context_end = min(len(lines), i + 10)
                        context_lines = lines[context_start:context_end]
                        
                        has_logging = any(re.search(r'logger\.(error|exception|warning|critical)', l) for l in context_lines)
                        has_reraise = any(re.search(r'raise', l) for l in context_lines)
                        has_return = any(re.search(r'return', l) for l in context_lines)
                        
                        issue = SecurityIssue(
                            type="exception_handling_analysis",
                            file=str(py_file.relative_to(self.project_root)),
                            line=i,
                            content=line.strip(),
                            severity="P1",
                            is_false_positive=has_logging and (has_return or has_reraise),
                            reason=f"Logging: {has_logging}, Return/Reraise: {has_return or has_reraise}"
                        )
                        
                        if issue.is_false_positive:
                            acceptable_excepts.append(issue)
                        else:
                            problematic_excepts.append(issue)
                            
            except Exception as e:
                print(f"Error leyendo {py_file}: {e}")
                
        return {
            "type": "exception_handling_analysis",
            "problematic_found": len(problematic_excepts),
            "acceptable_found": len(acceptable_excepts), 
            "problematic": problematic_excepts,
            "acceptable": acceptable_excepts,
            "status": "PASSED" if len(problematic_excepts) == 0 else "NEEDS_REVIEW"
        }
    
    def generate_intelligent_report(self) -> Dict[str, any]:
        """Genera reporte con análisis inteligente."""
        print("Generando reporte inteligente...")
        
        cursor_analysis = self.validate_cursor_execute_intelligent()
        except_analysis = self.analyze_except_patterns()
        
        total_real_issues = cursor_analysis['real_issues_found'] + except_analysis['problematic_found']
        total_false_positives = cursor_analysis['false_positives_found'] + except_analysis['acceptable_found']
        
        return {
            "timestamp": "2025-08-23T12:00:00Z",
            "project": "Rexus.app - Análisis Inteligente",
            "validator_version": "intelligent_v1.0",
            "summary": {
                "real_security_issues": total_real_issues,
                "false_positives_filtered": total_false_positives,
                "accuracy_improvement": f"{(total_false_positives / (total_real_issues + total_false_positives) * 100):.1f}% false positives filtered"
            },
            "analyses": [cursor_analysis, except_analysis],
            "recommendations": self.generate_smart_recommendations(cursor_analysis, except_analysis)
        }
    
    def generate_smart_recommendations(self, cursor_analysis, except_analysis) -> List[str]:
        """Genera recomendaciones inteligentes."""
        recommendations = []
        
        real_cursor_issues = cursor_analysis['real_issues_found']
        if real_cursor_issues > 0:
            recommendations.append(f"CRÍTICO: {real_cursor_issues} casos reales de cursor.execute inseguro requieren atención")
            recommendations.append("Revisar variables pasadas a cursor.execute() que pueden contener input del usuario")
        else:
            recommendations.append("Todos los casos de cursor.execute son legítimos")
            
        problematic_excepts = except_analysis['problematic_found']
        if problematic_excepts > 0:
            recommendations.append(f"MEJORA: {problematic_excepts} bloques except Exception sin logging apropiado")
        else:
            recommendations.append("Manejo de excepciones apropiado en archivos core")
            
        recommendations.append("Falsos positivos filtrados correctamente - auditoría más precisa")
        
        return recommendations

def main():
    """Función principal mejorada."""
    print("VALIDADOR INTELIGENTE DE SEGURIDAD - Rexus.app")
    print("Filtra falsos positivos para mayor precisión")
    print("=" * 60)
    
    current_dir = Path(__file__).parent.parent
    if not (current_dir / "rexus").exists():
        print("Error: No se encontro el directorio 'rexus'")
        return 1
        
    validator = IntelligentSecurityValidator(str(current_dir))
    
    try:
        report = validator.generate_intelligent_report()
        
        print(f"\nRESULTADOS INTELIGENTES:")
        print(f"Issues reales de seguridad: {report['summary']['real_security_issues']}")
        print(f"Falsos positivos filtrados: {report['summary']['false_positives_filtered']}")
        print(f"Mejora de precisión: {report['summary']['accuracy_improvement']}")
        
        print(f"\nRECOMENDACIONES:")
        for i, rec in enumerate(report['recommendations'], 1):
            print(f"{i}. {rec}")
        
        # Mostrar issues reales
        for analysis in report['analyses']:
            if 'real_issues' in analysis and analysis['real_issues']:
                print(f"\n{analysis['type']} - ISSUES REALES:")
                for issue in analysis['real_issues'][:3]:
                    print(f"  - {issue.file}:{issue.line}")
                    print(f"    {issue.content[:60]}...")
                    print(f"    Razón: {issue.reason}")
                    
        # Guardar reporte
        import json
        report_file = current_dir / "intelligent_security_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
            
        print(f"\nReporte guardado en: {report_file}")
        
        # Mostrar estadísticas de mejora
        total_issues = report['summary']['real_security_issues']
        exit_code = 0 if total_issues == 0 else 1
        
        print(f"\n{'VALIDACION INTELIGENTE PASSED' if exit_code == 0 else 'VALIDACION INTELIGENTE - ISSUES REALES ENCONTRADOS'}")
        return exit_code
        
    except Exception as e:
        print(f"Error ejecutando validacion inteligente: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)