#!/usr/bin/env python3
"""
Analizador de Seguridad para Rexus.app
Detecta patrones de riesgo en el código y genera reportes.
"""


import logging
logger = logging.getLogger(__name__)

import re
import os
from pathlib import Path
from typing import List, Dict, Tuple


class SecurityAnalyzer:
    """Analizador de seguridad para el código de Rexus.app"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.issues = []
        
    def analyze_project(self) -> Dict[str, List]:
        """Analiza todo el proyecto y retorna issues de seguridad."""
        results = {
            'broad_exceptions': [],
            'sql_injection_risks': [],
            'unsafe_evals': [],
            'hardcoded_secrets': [],
            'insecure_patterns': []
        }
        
        # Buscar archivos Python
        python_files = list(self.project_root.rglob("*.py"))
        
        for file_path in python_files:
            # Saltar archivos en directorios excluidos
            if self._should_skip_file(file_path):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Analizar diferentes tipos de problemas
                results['broad_exceptions'].extend(
                    self._find_broad_exceptions(file_path, content)
                )
                results['sql_injection_risks'].extend(
                    self._find_sql_injection_risks(file_path, content)
                )
                results['unsafe_evals'].extend(
                    self._find_unsafe_evals(file_path, content)
                )
                results['hardcoded_secrets'].extend(
                    self._find_hardcoded_secrets(file_path, content)
                )
                results['insecure_patterns'].extend(
                    self._find_insecure_patterns(file_path, content)
                )
                
            except UnicodeDecodeError:
                continue
                
        return results
    
    def _should_skip_file(self, file_path: Path) -> bool:
        """Determina si se debe saltar un archivo."""
        skip_dirs = {'.git', '__pycache__', '.pytest_cache', 'node_modules', '.venv'}
        skip_files = {'__init__.py'}
        
        # Verificar directorios a saltar
        for part in file_path.parts:
            if part in skip_dirs:
                return True
                
        # Verificar archivos específicos a saltar
        if file_path.name in skip_files:
            return True
            
        return False
    
    def _find_broad_exceptions(self, file_path: Path, content: str) -> List[Dict]:
        """Encuentra excepciones amplias."""
        issues = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            if re.search(r'except\s+Exception\s*:', line):
                issues.append({
                    'file': str(file_path),
                    'line': i,
                    'type': 'broad_exception',
                    'content': line.strip(),
                    'severity': 'medium',
                    'recommendation': 'Usar excepciones específicas como ValueError, TypeError, etc.'
                })
                
        return issues
    
    def _find_sql_injection_risks(self, file_path: Path, content: str) -> List[Dict]:
        """Encuentra riesgos de SQL injection."""
        issues = []
        lines = content.split('\n')
        
        # Patrones peligrosos
        dangerous_patterns = [
            r'f".*SELECT.*{.*}',
            r'f".*INSERT.*{.*}',
            r'f".*UPDATE.*{.*}',
            r'f".*DELETE.*{.*}',
            r'cursor\.execute\(.*\+.*\)',
            r'\.execute\(.*%.*\)',
        ]
        
        for i, line in enumerate(lines, 1):
            for pattern in dangerous_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    # Saltar casos que usan placeholders o sanitización
                    if 'sanitiz' in line.lower() or '?' in line:
                        continue
                        
                    issues.append({
                        'file': str(file_path),
                        'line': i,
                        'type': 'sql_injection_risk',
                        'content': line.strip(),
                        'severity': 'high',
                        'recommendation': 'Usar consultas parametrizadas o SQLQueryManager'
                    })
                    
        return issues
    
    def _find_unsafe_evals(self, file_path: Path, content: str) -> List[Dict]:
        """Encuentra usos de eval() y exec()."""
        issues = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            if re.search(r'\b(eval|exec)\s*\(', line):
                issues.append({
                    'file': str(file_path),
                    'line': i,
                    'type': 'unsafe_eval',
                    'content': line.strip(),
                    'severity': 'critical',
                    'recommendation': 'Evitar eval/exec, usar parsing seguro o funciones específicas'
                })
                
        return issues
    
    def _find_hardcoded_secrets(self, file_path: Path, content: str) -> List[Dict]:
        """Encuentra secrets hardcodeados."""
        issues = []
        lines = content.split('\n')
        
        secret_patterns = [
            r'password\s*=\s*["\'][^"\']{8,}["\']',
            r'api_key\s*=\s*["\'][^"\']{20,}["\']',
            r'secret\s*=\s*["\'][^"\']{16,}["\']',
            r'token\s*=\s*["\'][^"\']{20,}["\']',
        ]
        
        for i, line in enumerate(lines, 1):
            for pattern in secret_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    # Saltar casos obvios de ejemplo o comentarios
                    if any(word in line.lower() for word in ['example', 'todo', 'fixme', 'xxx']):
                        continue
                        
                    issues.append({
                        'file': str(file_path),
                        'line': i,
                        'type': 'hardcoded_secret',
                        'content': line.strip()[:50] + '...',  # Truncar por seguridad
                        'severity': 'high',
                        'recommendation': 'Mover secrets a variables de entorno o archivos de configuración'
                    })
                    
        return issues
    
    def _find_insecure_patterns(self, file_path: Path, content: str) -> List[Dict]:
        """Encuentra otros patrones inseguros."""
        issues = []
        lines = content.split('\n')
        
        insecure_patterns = [
            (r'shell\s*=\s*True', 'shell_injection', 'medium', 'Evitar shell=True en subprocess'),
            (r'pickle\.load', 'unsafe_deserialization', 'high', 'Usar JSON u otros formatos seguros'),
            (r'input\(.*\)', 'unsafe_input', 'low', 'Validar entrada del usuario'),
        ]
        
        for i, line in enumerate(lines, 1):
            for pattern, issue_type, severity, recommendation in insecure_patterns:
                if re.search(pattern, line):
                    issues.append({
                        'file': str(file_path),
                        'line': i,
                        'type': issue_type,
                        'content': line.strip(),
                        'severity': severity,
                        'recommendation': recommendation
                    })
                    
        return issues
    
    def generate_report(self, results: Dict[str, List]) -> str:
        """Genera un reporte de seguridad."""
        report = """
# 🔒 REPORTE DE SEGURIDAD - Rexus.app

## Resumen Ejecutivo
"""
        
        total_issues = sum(len(issues) for issues in results.values())
        critical_issues = sum(1 for issues in results.values() 
                            for issue in issues if issue.get('severity') == 'critical')
        high_issues = sum(1 for issues in results.values() 
                         for issue in issues if issue.get('severity') == 'high')
        
        report += f"""
- **Total de issues**: {total_issues}
- **Críticos**: {critical_issues}
- **Altos**: {high_issues}
- **Estado**: {'🔴 CRÍTICO' if critical_issues > 0 else '🟡 ATENCIÓN' if high_issues > 0 else '🟢 ACEPTABLE'}

## Detalles por Categoría

"""
        
        for category, issues in results.items():
            if not issues:
                continue
                
            report += f"### {category.replace('_', ' ').title()}\n\n"
            
            for issue in issues:
                severity_emoji = {
                    'critical': '🔴',
                    'high': '🟠', 
                    'medium': '🟡',
                    'low': '🟢'
                }.get(issue.get('severity', 'medium'), '🟡')
                
                report += f"**{severity_emoji} {issue['file']}:{issue['line']}**\n"
                report += f"- Contenido: `{issue['content']}`\n"
                report += f"- Recomendación: {issue['recommendation']}\n\n"
        
        report += """
## Próximos Pasos

1. **Priorizar issues críticos y altos**
2. **Implementar fixes siguiendo las recomendaciones**
3. **Ejecutar este análisis regularmente en CI/CD**
4. **Considerar integrar herramientas como bandit para análisis continuo**

---
Generado por SecurityAnalyzer de Rexus.app
"""
        
        return report


def main():
    """Función principal para ejecutar el análisis."""
    analyzer = SecurityAnalyzer()
    logger.info("Analizando seguridad del proyecto...")
    
    results = analyzer.analyze_project()
    report = analyzer.generate_report(results)
    
    # Guardar reporte
    with open('security_report.md', 'w', encoding='utf-8') as f:
        f.write(report)
    
    logger.info("Analisis completado. Reporte guardado en 'security_report.md'")
    
    # Mostrar resumen en consola
    total_issues = sum(len(issues) for issues in results.values())
    if total_issues > 0:
        logger.info(f"Se encontraron {total_issues} problemas de seguridad.")
        return 1
    else:
        logger.info("No se encontraron problemas de seguridad criticos.")
        return 0


if __name__ == "__main__":
    exit(main())