#!/usr/bin/env python3
"""
Validador de Correcciones de Auditoría de Seguridad
Verifica que los issues identificados en AUDITORIA_EXPERTA_2025 hayan sido corregidos

Fecha: 23/08/2025
"""

import os
import re
import json
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
    status: str = "pending"

class SecurityAuditValidator:
    """Validador de correcciones de seguridad aplicadas."""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.issues_found = []
        self.corrections_applied = []
        
    def validate_cursor_execute_issues(self) -> Dict[str, any]:
        """Valida que no haya cursor.execute sin parámetros."""
        print("Validando correcciones de cursor.execute...")
        
        issues = []
        rexus_dir = self.project_root / "rexus"
        
        # Buscar archivos Python
        for py_file in rexus_dir.rglob("*.py"):
            if ".backup" in str(py_file) or "__pycache__" in str(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                    
                for i, line in enumerate(lines, 1):
                    # Buscar cursor.execute con un solo argumento (potencialmente inseguro)
                    if re.search(r'cursor\.execute\([^,)]*\)(?!\s*,)', line):
                        # Verificar que no sea un caso válido (literal hardcodeado)
                        if not re.search(r'cursor\.execute\s*\(\s*["\']SELECT\s+1["\']', line):
                            issues.append(SecurityIssue(
                                type="unsafe_cursor_execute",
                                file=str(py_file.relative_to(self.project_root)),
                                line=i,
                                content=line.strip(),
                                severity="P0"
                            ))
                            
            except Exception as e:
                print(f"Error leyendo {py_file}: {e}")
                
        return {
            "type": "cursor_execute_validation",
            "issues_found": len(issues),
            "issues": issues,
            "status": "PASSED" if len(issues) == 0 else "FAILED"
        }
    
    def validate_except_exception_issues(self) -> Dict[str, any]:
        """Valida correcciones de except Exception genéricos."""
        print("Validando correcciones de except Exception...")
        
        issues = []
        rexus_core_dir = self.project_root / "rexus" / "core"
        
        for py_file in rexus_core_dir.rglob("*.py"):
            if ".backup" in str(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                    
                for i, line in enumerate(lines, 1):
                    if re.search(r'except\s+Exception\s*:', line):
                        # Buscar si hay logging en las siguientes líneas
                        has_logging = False
                        for j in range(i, min(i + 5, len(lines))):
                            if re.search(r'logger\.(error|exception|warning)', lines[j]):
                                has_logging = True
                                break
                                
                        if not has_logging:
                            issues.append(SecurityIssue(
                                type="generic_exception_without_logging",
                                file=str(py_file.relative_to(self.project_root)),
                                line=i,
                                content=line.strip(),
                                severity="P1"
                            ))
                            
            except Exception as e:
                print(f"Error leyendo {py_file}: {e}")
                
        return {
            "type": "except_exception_validation",
            "issues_found": len(issues),
            "issues": issues,
            "status": "PASSED" if len(issues) == 0 else "NEEDS_REVIEW"
        }
    
    def validate_print_statements(self) -> Dict[str, any]:
        """Valida que no haya print() en archivos de producción."""
        print("Validando eliminación de print() statements...")
        
        issues = []
        modules_dir = self.project_root / "rexus" / "modules"
        
        for py_file in modules_dir.rglob("*.py"):
            if ".backup" in str(py_file) or "test_" in py_file.name:
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                    
                for i, line in enumerate(lines, 1):
                    if re.search(r'print\s*\(', line) and not line.strip().startswith('#'):
                        issues.append(SecurityIssue(
                            type="print_statement_in_production",
                            file=str(py_file.relative_to(self.project_root)),
                            line=i,
                            content=line.strip(),
                            severity="P1"
                        ))
                        
            except Exception as e:
                print(f"Error leyendo {py_file}: {e}")
                
        return {
            "type": "print_statements_validation", 
            "issues_found": len(issues),
            "issues": issues,
            "status": "PASSED" if len(issues) == 0 else "FAILED"
        }
    
    def validate_sql_injection_patterns(self) -> Dict[str, any]:
        """Valida patrones de SQL injection."""
        print("Validando patrones de SQL injection...")
        
        issues = []
        rexus_dir = self.project_root / "rexus"
        
        # Patrones peligrosos
        dangerous_patterns = [
            r'f".*{.*}.*".*execute',  # f-string con variables en SQL
            r'f\'.*{.*}.*\'.*execute',  # f-string con variables en SQL
            r'%.*%.*execute',  # string formatting viejo
            r'\+.*\+.*execute'  # concatenación de strings
        ]
        
        for py_file in rexus_dir.rglob("*.py"):
            if ".backup" in str(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                    
                for i, line in enumerate(lines, 1):
                    for pattern in dangerous_patterns:
                        if re.search(pattern, line):
                            issues.append(SecurityIssue(
                                type="potential_sql_injection",
                                file=str(py_file.relative_to(self.project_root)),
                                line=i,
                                content=line.strip(),
                                severity="P0"
                            ))
                            
            except Exception as e:
                print(f"Error leyendo {py_file}: {e}")
                
        return {
            "type": "sql_injection_validation",
            "issues_found": len(issues),
            "issues": issues,
            "status": "PASSED" if len(issues) == 0 else "CRITICAL"
        }
    
    def generate_security_report(self) -> Dict[str, any]:
        """Genera reporte completo de seguridad."""
        print("Generando reporte de seguridad...")
        
        validations = [
            self.validate_cursor_execute_issues(),
            self.validate_except_exception_issues(), 
            self.validate_print_statements(),
            self.validate_sql_injection_patterns()
        ]
        
        total_issues = sum(v['issues_found'] for v in validations)
        critical_issues = sum(1 for v in validations if v['status'] in ['FAILED', 'CRITICAL'])
        
        overall_status = "PASSED" if critical_issues == 0 else "FAILED"
        
        report = {
            "timestamp": "2025-08-23T12:00:00Z",
            "project": "Rexus.app",
            "audit_source": "AUDITORIA_EXPERTA_2025",
            "overall_status": overall_status,
            "summary": {
                "total_validations": len(validations),
                "total_issues_found": total_issues,
                "critical_validations_failed": critical_issues,
                "validations_passed": len(validations) - critical_issues
            },
            "validations": validations,
            "recommendations": self.generate_recommendations(validations)
        }
        
        return report
    
    def generate_recommendations(self, validations: List[Dict]) -> List[str]:
        """Genera recomendaciones basadas en validaciones."""
        recommendations = []
        
        for validation in validations:
            if validation['status'] in ['FAILED', 'CRITICAL']:
                if validation['type'] == 'cursor_execute_validation':
                    recommendations.append("Implementar consultas parametrizadas en todos los cursor.execute")
                elif validation['type'] == 'sql_injection_validation':
                    recommendations.append("CRÍTICO: Eliminar interpolación de strings en consultas SQL")
                elif validation['type'] == 'print_statements_validation':
                    recommendations.append("Migrar print() statements a sistema de logging central")
                    
            elif validation['status'] == 'NEEDS_REVIEW':
                if validation['type'] == 'except_exception_validation':
                    recommendations.append("Agregar logging específico en bloques except Exception")
                    
        if not recommendations:
            recommendations.append("Todas las validaciones de seguridad han pasado correctamente")
            
        return recommendations

def main():
    """Función principal."""
    print("VALIDADOR DE AUDITORIA DE SEGURIDAD - Rexus.app")
    print("=" * 60)
    
    # Detectar directorio del proyecto
    current_dir = Path(__file__).parent.parent
    if not (current_dir / "rexus").exists():
        print("Error: No se encontro el directorio 'rexus'")
        return
        
    validator = SecurityAuditValidator(str(current_dir))
    
    try:
        # Generar reporte completo
        report = validator.generate_security_report()
        
        # Mostrar resultados
        print(f"\nRESULTADOS:")
        print(f"Estado general: {report['overall_status']}")
        print(f"Issues encontrados: {report['summary']['total_issues_found']}")
        print(f"Validaciones fallidas: {report['summary']['critical_validations_failed']}")
        
        print(f"\nRECOMENDACIONES:")
        for i, rec in enumerate(report['recommendations'], 1):
            print(f"{i}. {rec}")
            
        # Guardar reporte
        report_file = current_dir / "security_audit_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
            
        print(f"\nReporte guardado en: {report_file}")
        
        # Mostrar issues críticos
        if report['summary']['total_issues_found'] > 0:
            print(f"\nISSUES ENCONTRADOS:")
            for validation in report['validations']:
                if validation['issues_found'] > 0:
                    print(f"\n{validation['type']} ({validation['status']}):")
                    for issue in validation['issues'][:5]:  # Mostrar solo primeros 5
                        print(f"  - {issue.file}:{issue.line} | {issue.content[:50]}...")
                    if len(validation['issues']) > 5:
                        print(f"  ... y {len(validation['issues']) - 5} más")
        
        # Código de salida
        exit_code = 0 if report['overall_status'] == 'PASSED' else 1
        print(f"\n{'AUDITORIA PASSED' if exit_code == 0 else 'AUDITORIA FAILED'}")
        
        return exit_code
        
    except Exception as e:
        print(f"Error ejecutando validacion: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)