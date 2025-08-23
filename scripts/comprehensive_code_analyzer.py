#!/usr/bin/env python3
"""
Analizador Comprehensivo de Código - Simula SonarQube
Identifica múltiples tipos de issues de calidad de código

Fecha: 23/08/2025
"""

import os
import re
import ast
from pathlib import Path
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from collections import defaultdict
import json

@dataclass
class CodeIssue:
    type: str
    severity: str  # BLOCKER, CRITICAL, MAJOR, MINOR, INFO
    file: str
    line: int
    message: str
    rule: str
    content: str = ""

class ComprehensiveCodeAnalyzer:
    """Analizador completo de calidad de código."""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.issues = []
        
        # Patrones de problemas comunes (estilo SonarQube)
        self.patterns = {
            # Problemas de seguridad
            'sql_injection': {
                'patterns': [
                    r'cursor\.execute\s*\(\s*[^"\'].*\%.*\)',
                    r'cursor\.execute\s*\(\s*.*\.format\(',
                    r'cursor\.execute\s*\(\s*f["\'].*\{.*\}',
                ],
                'severity': 'BLOCKER',
                'message': 'Potential SQL injection vulnerability'
            },
            
            # Problemas de fiabilidad
            'bare_except': {
                'patterns': [r'except\s*:(?!\s*#)'],
                'severity': 'MAJOR',
                'message': 'Bare except clause should be avoided'
            },
            
            'broad_exception': {
                'patterns': [r'except\s+Exception\s*:(?!\s*#)'],
                'severity': 'MAJOR', 
                'message': 'Catching generic Exception should be avoided'
            },
            
            # Problemas de mantenibilidad
            'long_line': {
                'patterns': [r'^.{121,}$'],
                'severity': 'MINOR',
                'message': 'Line too long (>120 characters)'
            },
            
            'todo_fixme': {
                'patterns': [r'#\s*(TODO|FIXME|XXX|HACK)'],
                'severity': 'MINOR',
                'message': 'TODO/FIXME comment should be resolved'
            },
            
            'print_statement': {
                'patterns': [r'(?<!#.*)\bprint\s*\('],
                'severity': 'MINOR',
                'message': 'Print statement should be replaced with logging'
            },
            
            # Problemas de legibilidad
            'cognitive_complexity': {
                'patterns': [],  # Requiere análisis AST
                'severity': 'MAJOR',
                'message': 'Function has high cognitive complexity'
            },
            
            'magic_number': {
                'patterns': [r'(?<![=<>!+\-*/])\b(?<![\w\.])[1-9]\d{2,}\b(?![.\w])'],
                'severity': 'MINOR',
                'message': 'Magic number should be replaced with named constant'
            },
            
            'duplicate_string': {
                'patterns': [],  # Requiere análisis especial
                'severity': 'MINOR',
                'message': 'String literal should be extracted to constant'
            },
            
            # Problemas de performance
            'inefficient_loop': {
                'patterns': [
                    r'for\s+.*\s+in\s+range\s*\(\s*len\s*\(',
                ],
                'severity': 'MINOR',
                'message': 'Inefficient loop pattern'
            },
            
            # Problemas de diseño
            'too_many_parameters': {
                'patterns': [],  # Requiere análisis AST
                'severity': 'MAJOR',
                'message': 'Function has too many parameters'
            },
            
            'unused_import': {
                'patterns': [],  # Requiere análisis AST
                'severity': 'MINOR',
                'message': 'Unused import'
            },
            
            'method_too_long': {
                'patterns': [],  # Requiere análisis AST
                'severity': 'MAJOR',
                'message': 'Method too long'
            }
        }
        
    def analyze_project(self) -> Dict[str, Any]:
        """Analiza todo el proyecto."""
        print("Analizando proyecto Rexus.app...")
        
        self.issues = []
        rexus_dir = self.project_root / "rexus"
        
        # Analizar archivos Python
        py_files = list(rexus_dir.rglob("*.py"))
        py_files = [f for f in py_files if not self._should_skip_file(f)]
        
        print(f"Analizando {len(py_files)} archivos Python...")
        
        for i, py_file in enumerate(py_files):
            if i % 20 == 0:
                print(f"Progreso: {i}/{len(py_files)} archivos")
                
            self._analyze_file(py_file)
        
        # Generar estadísticas
        stats = self._generate_statistics()
        
        return {
            'timestamp': '2025-08-23T12:00:00Z',
            'project': 'Rexus.app',
            'analyzer': 'comprehensive_v1.0',
            'files_analyzed': len(py_files),
            'total_issues': len(self.issues),
            'statistics': stats,
            'issues_by_severity': self._group_by_severity(),
            'issues_by_type': self._group_by_type(),
            'top_problematic_files': self._get_top_files(),
            'recommendations': self._generate_recommendations()
        }
    
    def _should_skip_file(self, file_path: Path) -> bool:
        """Determina si un archivo debe ser omitido."""
        skip_patterns = [
            '__pycache__',
            '.backup',
            'test_',
            '_test.py',
            'migrations/',
            'venv/',
            '.git/'
        ]
        
        file_str = str(file_path)
        return any(pattern in file_str for pattern in skip_patterns)
    
    def _analyze_file(self, file_path: Path):
        """Analiza un archivo específico."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                
            # Análisis basado en patrones regex
            self._analyze_with_patterns(file_path, lines)
            
            # Análisis AST para problemas más complejos
            try:
                tree = ast.parse(content)
                self._analyze_ast(file_path, tree, lines)
            except SyntaxError:
                self.issues.append(CodeIssue(
                    type='syntax_error',
                    severity='BLOCKER',
                    file=str(file_path.relative_to(self.project_root)),
                    line=1,
                    message='Syntax error in file',
                    rule='syntax',
                    content='Syntax error prevents analysis'
                ))
                
        except Exception as e:
            # Error leyendo archivo
            pass
    
    def _analyze_with_patterns(self, file_path: Path, lines: List[str]):
        """Análisis basado en expresiones regulares."""
        rel_path = str(file_path.relative_to(self.project_root))
        
        for line_num, line in enumerate(lines, 1):
            # Aplicar cada patrón
            for rule_name, rule_config in self.patterns.items():
                for pattern in rule_config['patterns']:
                    if re.search(pattern, line):
                        self.issues.append(CodeIssue(
                            type=rule_name,
                            severity=rule_config['severity'],
                            file=rel_path,
                            line=line_num,
                            message=rule_config['message'],
                            rule=rule_name,
                            content=line.strip()[:100]
                        ))
    
    def _analyze_ast(self, file_path: Path, tree: ast.AST, lines: List[str]):
        """Análisis basado en AST."""
        rel_path = str(file_path.relative_to(self.project_root))
        
        # Visitor para análisis AST
        class CodeAnalysisVisitor(ast.NodeVisitor):
            def __init__(self, analyzer, file_path, lines):
                self.analyzer = analyzer
                self.file_path = file_path
                self.lines = lines
                self.function_lengths = {}
                self.imports = set()
                self.used_names = set()
                
            def visit_FunctionDef(self, node):
                # Función muy larga
                start_line = node.lineno
                end_line = max([child.lineno for child in ast.walk(node) if hasattr(child, 'lineno')] + [start_line])
                length = end_line - start_line
                
                if length > 50:  # Función muy larga
                    self.analyzer.issues.append(CodeIssue(
                        type='method_too_long',
                        severity='MAJOR',
                        file=self.file_path,
                        line=start_line,
                        message=f'Function "{node.name}" is too long ({length} lines)',
                        rule='method_too_long',
                        content=f"def {node.name}..."
                    ))
                
                # Demasiados parámetros
                if len(node.args.args) > 7:
                    self.analyzer.issues.append(CodeIssue(
                        type='too_many_parameters',
                        severity='MAJOR',
                        file=self.file_path,
                        line=start_line,
                        message=f'Function "{node.name}" has {len(node.args.args)} parameters (max 7)',
                        rule='too_many_parameters',
                        content=f"def {node.name}(...)"
                    ))
                
                # Complejidad cognitiva (simplificada)
                complexity = self._calculate_cognitive_complexity(node)
                if complexity > 15:
                    self.analyzer.issues.append(CodeIssue(
                        type='cognitive_complexity',
                        severity='MAJOR',
                        file=self.file_path,
                        line=start_line,
                        message=f'Function "{node.name}" has cognitive complexity {complexity} (max 15)',
                        rule='cognitive_complexity',
                        content=f"def {node.name}..."
                    ))
                
                self.generic_visit(node)
            
            def visit_Import(self, node):
                for alias in node.names:
                    self.imports.add(alias.name)
                self.generic_visit(node)
            
            def visit_ImportFrom(self, node):
                if node.module:
                    for alias in node.names:
                        self.imports.add(f"{node.module}.{alias.name}")
                self.generic_visit(node)
            
            def visit_Name(self, node):
                if isinstance(node.ctx, ast.Load):
                    self.used_names.add(node.id)
                self.generic_visit(node)
            
            def _calculate_cognitive_complexity(self, node):
                """Cálculo simplificado de complejidad cognitiva."""
                complexity = 0
                for child in ast.walk(node):
                    if isinstance(child, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                        complexity += 1
                    elif isinstance(child, ast.BoolOp):
                        complexity += len(child.values) - 1
                return complexity
        
        visitor = CodeAnalysisVisitor(self, rel_path, lines)
        visitor.visit(tree)
        
        # Detectar imports no utilizados (simplificado)
        # Esta lógica es básica, un análisis real sería más complejo
        for imp in visitor.imports:
            simple_name = imp.split('.')[-1]
            if simple_name not in visitor.used_names and not simple_name.startswith('_'):
                self.issues.append(CodeIssue(
                    type='unused_import',
                    severity='MINOR',
                    file=rel_path,
                    line=1,  # Simplificado
                    message=f'Unused import: {imp}',
                    rule='unused_import',
                    content=f"import {imp}"
                ))
    
    def _generate_statistics(self) -> Dict[str, Any]:
        """Genera estadísticas del análisis."""
        severity_counts = defaultdict(int)
        type_counts = defaultdict(int)
        
        for issue in self.issues:
            severity_counts[issue.severity] += 1
            type_counts[issue.type] += 1
            
        return {
            'by_severity': dict(severity_counts),
            'by_type': dict(type_counts),
            'total_issues': len(self.issues)
        }
    
    def _group_by_severity(self) -> Dict[str, List]:
        """Agrupa issues por severidad."""
        groups = defaultdict(list)
        for issue in self.issues:
            groups[issue.severity].append({
                'type': issue.type,
                'file': issue.file,
                'line': issue.line,
                'message': issue.message,
                'content': issue.content[:50] + '...' if len(issue.content) > 50 else issue.content
            })
        return dict(groups)
    
    def _group_by_type(self) -> Dict[str, int]:
        """Cuenta issues por tipo."""
        counts = defaultdict(int)
        for issue in self.issues:
            counts[issue.type] += 1
        return dict(counts)
    
    def _get_top_files(self, limit: int = 10) -> List[Dict]:
        """Obtiene los archivos con más issues."""
        file_counts = defaultdict(int)
        for issue in self.issues:
            file_counts[issue.file] += 1
            
        sorted_files = sorted(file_counts.items(), key=lambda x: x[1], reverse=True)
        
        return [
            {'file': file, 'issues': count}
            for file, count in sorted_files[:limit]
        ]
    
    def _generate_recommendations(self) -> List[str]:
        """Genera recomendaciones basadas en el análisis."""
        recommendations = []
        
        stats = self._generate_statistics()
        
        if stats['by_severity'].get('BLOCKER', 0) > 0:
            recommendations.append(f"CRÍTICO: {stats['by_severity']['BLOCKER']} issues bloqueantes requieren atención inmediata")
        
        if stats['by_type'].get('broad_exception', 0) > 5:
            recommendations.append("Alto número de 'except Exception' - implementar manejo específico de excepciones")
            
        if stats['by_type'].get('print_statement', 0) > 10:
            recommendations.append("Migrar statements print() a sistema de logging centralizado")
            
        if stats['by_type'].get('long_line', 0) > 20:
            recommendations.append("Implementar linting automático para mantener líneas <120 caracteres")
            
        if stats['by_type'].get('method_too_long', 0) > 10:
            recommendations.append("Refactorizar funciones largas para mejorar mantenibilidad")
            
        if not recommendations:
            recommendations.append("Calidad de código en buen estado general")
            
        return recommendations

def main():
    """Función principal."""
    print("ANALIZADOR COMPREHENSIVO DE CODIGO - Estilo SonarQube")
    print("=" * 60)
    
    current_dir = Path(__file__).parent.parent
    if not (current_dir / "rexus").exists():
        print("Error: No se encontro el directorio 'rexus'")
        return 1
        
    analyzer = ComprehensiveCodeAnalyzer(str(current_dir))
    
    try:
        report = analyzer.analyze_project()
        
        print(f"\nRESULTADOS DEL ANALISIS:")
        print(f"Archivos analizados: {report['files_analyzed']}")
        print(f"Issues totales encontrados: {report['total_issues']}")
        
        print(f"\nPOR SEVERIDAD:")
        for severity, count in report['statistics']['by_severity'].items():
            print(f"  {severity}: {count}")
            
        print(f"\nTOP 5 TIPOS DE ISSUES:")
        top_types = sorted(report['statistics']['by_type'].items(), key=lambda x: x[1], reverse=True)[:5]
        for issue_type, count in top_types:
            print(f"  {issue_type}: {count}")
            
        print(f"\nARCHIVOS MAS PROBLEMATICOS:")
        for file_info in report['top_problematic_files'][:5]:
            print(f"  {file_info['file']}: {file_info['issues']} issues")
            
        print(f"\nRECOMENDACIONES:")
        for i, rec in enumerate(report['recommendations'], 1):
            print(f"{i}. {rec}")
        
        # Guardar reporte completo
        report_file = current_dir / "comprehensive_code_analysis.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
            
        print(f"\nReporte completo guardado en: {report_file}")
        
        # Mostrar algunos issues críticos
        blockers = report['issues_by_severity'].get('BLOCKER', [])
        if blockers:
            print(f"\nISSUES BLOQUEANTES (primeros 3):")
            for issue in blockers[:3]:
                print(f"  - {issue['file']}:{issue['line']}")
                print(f"    {issue['message']}")
                print(f"    {issue['content']}")
        
        # Código de salida basado en severidad
        exit_code = 1 if report['statistics']['by_severity'].get('BLOCKER', 0) > 0 else 0
        print(f"\n{'ANALISIS COMPLETADO - REVISAR ISSUES CRITICOS' if exit_code == 1 else 'ANALISIS COMPLETADO - CALIDAD ACEPTABLE'}")
        
        return exit_code
        
    except Exception as e:
        print(f"Error ejecutando analisis: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)