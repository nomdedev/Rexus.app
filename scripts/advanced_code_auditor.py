#!/usr/bin/env python3
"""
Advanced Code Auditor - Auditoría Exhaustiva Módulo por Módulo
Identifica errores avanzados y patrones problemáticos
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
class AdvancedIssue:
    type: str
    severity: str  # BLOCKER, CRITICAL, MAJOR, MINOR, INFO
    file: str
    line: int
    message: str
    rule: str
    content: str = ""
    module: str = ""

class AdvancedCodeAuditor:
    """Auditor avanzado de código módulo por módulo."""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.issues = []
        
        # Patrones avanzados de problemas
        self.advanced_patterns = {
            # Problemas de imports
            'circular_import': {
                'severity': 'MAJOR',
                'message': 'Posible importación circular detectada'
            },
            
            'unused_import': {
                'severity': 'MINOR', 
                'message': 'Import no utilizado detectado'
            },
            
            # Problemas de variables
            'undefined_variable': {
                'severity': 'BLOCKER',
                'message': 'Variable posiblemente no definida'
            },
            
            'global_variable': {
                'patterns': [r'^[A-Z_]+\s*=(?!.*def|.*class)'],
                'severity': 'MINOR',
                'message': 'Variable global detectada'
            },
            
            # Problemas de funciones
            'function_too_complex': {
                'severity': 'MAJOR',
                'message': 'Función demasiado compleja'
            },
            
            'missing_docstring': {
                'severity': 'MINOR',
                'message': 'Función sin docstring'
            },
            
            # Problemas de seguridad
            'hardcoded_password': {
                'patterns': [
                    r'password\s*=\s*["\'][^"\']{3,}["\']',
                    r'pwd\s*=\s*["\'][^"\']{3,}["\']',
                    r'secret\s*=\s*["\'][^"\']{3,}["\']'
                ],
                'severity': 'BLOCKER',
                'message': 'Contraseña hardcodeada detectada'
            },
            
            'sql_concatenation': {
                'patterns': [
                    r'["\'].*SELECT.*["\'].*\+.*[^"\']*["\']',
                    r'["\'].*INSERT.*["\'].*\+.*[^"\']*["\']',
                    r'["\'].*UPDATE.*["\'].*\+.*[^"\']*["\']'
                ],
                'severity': 'CRITICAL',
                'message': 'Posible concatenación SQL insegura'
            },
            
            # Problemas de performance
            'inefficient_loop': {
                'patterns': [
                    r'for\s+\w+\s+in\s+range\s*\(\s*len\s*\(\s*\w+\s*\)\s*\):',
                    r'while.*len\(',
                ],
                'severity': 'MINOR',
                'message': 'Loop ineficiente detectado'
            },
            
            'string_concatenation_loop': {
                'patterns': [r'(for|while).*:\s*\w+\s*\+=\s*["\']'],
                'severity': 'MINOR', 
                'message': 'Concatenación de string en loop'
            },
            
            # Problemas de código
            'duplicate_code': {
                'severity': 'MAJOR',
                'message': 'Código duplicado detectado'
            },
            
            'dead_code': {
                'patterns': [
                    r'if\s+False\s*:',
                    r'while\s+False\s*:',
                    r'return.*\n.*return'
                ],
                'severity': 'MINOR',
                'message': 'Código muerto detectado'
            },
            
            # Problemas de estilo
            'long_line': {
                'patterns': [r'^.{121,}$'],
                'severity': 'MINOR',
                'message': 'Línea demasiado larga (>120 chars)'
            },
            
            'mixed_tabs_spaces': {
                'severity': 'MINOR',
                'message': 'Mezcla de tabs y espacios'
            },
        }
        
    def audit_project_by_modules(self) -> Dict[str, Any]:
        """Audita el proyecto módulo por módulo."""
        print("Iniciando auditoría avanzada módulo por módulo...")
        
        self.issues = []
        modules_dir = self.project_root / "rexus"
        
        # Obtener todos los módulos
        modules = []
        for item in modules_dir.iterdir():
            if item.is_dir() and item.name not in ['__pycache__', '.git']:
                modules.append(item)
        
        print(f"Auditando {len(modules)} módulos...")
        
        module_results = {}
        
        for module_path in modules:
            module_name = module_path.name
            print(f"  Auditando módulo: {module_name}")
            
            module_issues = self._audit_module(module_path, module_name)
            module_results[module_name] = module_issues
            
        # Generar estadísticas
        stats = self._generate_advanced_statistics()
        
        return {
            'timestamp': '2025-08-23T18:00:00Z',
            'project': 'Rexus.app',
            'auditor': 'advanced_v2.0',
            'modules_audited': len(modules),
            'total_issues': len(self.issues),
            'statistics': stats,
            'modules': module_results,
            'critical_issues': self._get_critical_issues(),
            'recommendations': self._generate_advanced_recommendations()
        }
    
    def _audit_module(self, module_path: Path, module_name: str) -> Dict[str, Any]:
        """Audita un módulo específico."""
        module_issues = []
        files_audited = 0
        
        # Obtener todos los archivos Python del módulo
        py_files = list(module_path.rglob("*.py"))
        py_files = [f for f in py_files if not self._should_skip_file(f)]
        
        for py_file in py_files:
            files_audited += 1
            file_issues = self._audit_file_advanced(py_file, module_name)
            module_issues.extend(file_issues)
            self.issues.extend(file_issues)
            
        return {
            'files_audited': files_audited,
            'issues_found': len(module_issues),
            'issues': [self._issue_to_dict(issue) for issue in module_issues]
        }
    
    def _audit_file_advanced(self, file_path: Path, module_name: str) -> List[AdvancedIssue]:
        """Auditoría avanzada de un archivo."""
        file_issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            rel_path = str(file_path.relative_to(self.project_root))
            
            # Análisis con patrones regex
            file_issues.extend(self._analyze_with_advanced_patterns(rel_path, lines, module_name))
            
            # Análisis AST avanzado
            try:
                tree = ast.parse(content)
                file_issues.extend(self._analyze_ast_advanced(rel_path, tree, lines, module_name))
            except SyntaxError as e:
                file_issues.append(AdvancedIssue(
                    type='syntax_error',
                    severity='BLOCKER',
                    file=rel_path,
                    line=e.lineno or 1,
                    message=f'Error de sintaxis: {e.msg}',
                    rule='syntax_error',
                    content=f'Line {e.lineno}: Syntax error',
                    module=module_name
                ))
            
            # Análisis de complejidad específico
            file_issues.extend(self._analyze_complexity(rel_path, content, module_name))
            
        except Exception as e:
            file_issues.append(AdvancedIssue(
                type='file_error',
                severity='MAJOR',
                file=str(file_path.relative_to(self.project_root)),
                line=1,
                message=f'Error leyendo archivo: {e}',
                rule='file_access',
                content='File read error',
                module=module_name
            ))
        
        return file_issues
    
    def _analyze_with_advanced_patterns(self, file_path: str, lines: List[str], module_name: str) -> List[AdvancedIssue]:
        """Análisis con patrones avanzados."""
        issues = []
        
        for line_num, line in enumerate(lines, 1):
            # Aplicar patrones regex
            for rule_name, rule_config in self.advanced_patterns.items():
                if 'patterns' in rule_config:
                    for pattern in rule_config['patterns']:
                        if re.search(pattern, line, re.IGNORECASE):
                            issues.append(AdvancedIssue(
                                type=rule_name,
                                severity=rule_config['severity'],
                                file=file_path,
                                line=line_num,
                                message=rule_config['message'],
                                rule=rule_name,
                                content=line.strip()[:100],
                                module=module_name
                            ))
        
        return issues
    
    def _analyze_ast_advanced(self, file_path: str, tree: ast.AST, lines: List[str], module_name: str) -> List[AdvancedIssue]:
        """Análisis AST avanzado."""
        issues = []
        
        class AdvancedASTVisitor(ast.NodeVisitor):
            def __init__(self, auditor, file_path, lines, module_name):
                self.auditor = auditor
                self.file_path = file_path
                self.lines = lines
                self.module_name = module_name
                self.functions = []
                self.imports = set()
                self.names_used = set()
                self.names_defined = set()
                
            def visit_Import(self, node):
                for alias in node.names:
                    self.imports.add(alias.name)
                self.generic_visit(node)
                
            def visit_ImportFrom(self, node):
                if node.module:
                    for alias in node.names:
                        full_name = f"{node.module}.{alias.name}" if alias.name != '*' else node.module
                        self.imports.add(full_name)
                self.generic_visit(node)
                
            def visit_Name(self, node):
                if isinstance(node.ctx, ast.Load):
                    self.names_used.add(node.id)
                elif isinstance(node.ctx, ast.Store):
                    self.names_defined.add(node.id)
                self.generic_visit(node)
                
            def visit_FunctionDef(self, node):
                # Función sin docstring
                if (not node.body or 
                    not isinstance(node.body[0], ast.Expr) or 
                    not isinstance(node.body[0].value, ast.Constant) or 
                    not isinstance(node.body[0].value.value, str)):
                    
                    issues.append(AdvancedIssue(
                        type='missing_docstring',
                        severity='MINOR',
                        file=self.file_path,
                        line=node.lineno,
                        message=f'Función "{node.name}" sin docstring',
                        rule='missing_docstring',
                        content=f"def {node.name}(...)",
                        module=self.module_name
                    ))
                
                # Función demasiado compleja
                complexity = self._calculate_complexity(node)
                if complexity > 10:
                    issues.append(AdvancedIssue(
                        type='function_too_complex',
                        severity='MAJOR',
                        file=self.file_path,
                        line=node.lineno,
                        message=f'Función "{node.name}" muy compleja (complejidad: {complexity})',
                        rule='function_too_complex',
                        content=f"def {node.name}(...)",
                        module=self.module_name
                    ))
                
                # Función demasiado larga
                if hasattr(node, 'end_lineno') and node.end_lineno:
                    length = node.end_lineno - node.lineno
                    if length > 50:
                        issues.append(AdvancedIssue(
                            type='function_too_long',
                            severity='MAJOR',
                            file=self.file_path,
                            line=node.lineno,
                            message=f'Función "{node.name}" demasiado larga ({length} líneas)',
                            rule='function_too_long',
                            content=f"def {node.name}(...)",
                            module=self.module_name
                        ))
                
                self.functions.append(node.name)
                self.generic_visit(node)
                
            def _calculate_complexity(self, node):
                """Calcula complejidad ciclomática."""
                complexity = 1  # Complejidad base
                for child in ast.walk(node):
                    if isinstance(child, (ast.If, ast.For, ast.While, ast.With)):
                        complexity += 1
                    elif isinstance(child, ast.Try):
                        complexity += 1
                    elif isinstance(child, ast.ExceptHandler):
                        complexity += 1
                    elif isinstance(child, ast.BoolOp):
                        complexity += len(child.values) - 1
                return complexity
        
        visitor = AdvancedASTVisitor(self, file_path, lines, module_name)
        visitor.visit(tree)
        
        # Detectar imports no utilizados
        for imp in visitor.imports:
            simple_name = imp.split('.')[-1]
            if (simple_name not in visitor.names_used and 
                simple_name not in visitor.functions and
                not simple_name.startswith('_') and
                simple_name not in ['os', 'sys', 'logging']):  # Excluir imports comunes
                
                issues.append(AdvancedIssue(
                    type='unused_import',
                    severity='MINOR',
                    file=file_path,
                    line=1,  # Simplificado
                    message=f'Import no utilizado: {imp}',
                    rule='unused_import',
                    content=f"import {imp}",
                    module=module_name
                ))
        
        return issues
    
    def _analyze_complexity(self, file_path: str, content: str, module_name: str) -> List[AdvancedIssue]:
        """Análisis de complejidad específico."""
        issues = []
        
        # Detectar mezcla de tabs y espacios
        lines = content.split('\n')
        has_tabs = any('\t' in line for line in lines)
        has_spaces = any(line.startswith('    ') for line in lines)
        
        if has_tabs and has_spaces:
            issues.append(AdvancedIssue(
                type='mixed_tabs_spaces',
                severity='MINOR',
                file=file_path,
                line=1,
                message='Mezcla de tabs y espacios detectada',
                rule='mixed_tabs_spaces',
                content='Mixed indentation',
                module=module_name
            ))
        
        return issues
    
    def _should_skip_file(self, file_path: Path) -> bool:
        """Determina si un archivo debe ser omitido."""
        skip_patterns = [
            '__pycache__',
            '.backup',
            'test_',
            '_test.py',
            'migrations/',
            'venv/',
            '.git/',
            '.pyc'
        ]
        
        file_str = str(file_path)
        return any(pattern in file_str for pattern in skip_patterns)
    
    def _generate_advanced_statistics(self) -> Dict[str, Any]:
        """Genera estadísticas avanzadas."""
        severity_counts = defaultdict(int)
        type_counts = defaultdict(int)
        module_counts = defaultdict(int)
        
        for issue in self.issues:
            severity_counts[issue.severity] += 1
            type_counts[issue.type] += 1
            module_counts[issue.module] += 1
        
        return {
            'by_severity': dict(severity_counts),
            'by_type': dict(type_counts),
            'by_module': dict(module_counts),
            'total_issues': len(self.issues)
        }
    
    def _get_critical_issues(self) -> List[Dict[str, Any]]:
        """Obtiene issues críticos y bloqueantes."""
        critical = [issue for issue in self.issues 
                   if issue.severity in ['BLOCKER', 'CRITICAL']]
        
        return [self._issue_to_dict(issue) for issue in critical[:20]]
    
    def _issue_to_dict(self, issue: AdvancedIssue) -> Dict[str, Any]:
        """Convierte issue a diccionario."""
        return {
            'type': issue.type,
            'severity': issue.severity,
            'file': issue.file,
            'line': issue.line,
            'message': issue.message,
            'rule': issue.rule,
            'content': issue.content,
            'module': issue.module
        }
    
    def _generate_advanced_recommendations(self) -> List[str]:
        """Genera recomendaciones avanzadas."""
        recommendations = []
        
        stats = self._generate_advanced_statistics()
        
        # Recomendaciones por severidad
        if stats['by_severity'].get('BLOCKER', 0) > 0:
            recommendations.append(f"CRÍTICO: {stats['by_severity']['BLOCKER']} issues bloqueantes requieren atención inmediata")
        
        if stats['by_severity'].get('CRITICAL', 0) > 0:
            recommendations.append(f"URGENTE: {stats['by_severity']['CRITICAL']} issues críticos de seguridad")
        
        # Recomendaciones por tipo
        if stats['by_type'].get('missing_docstring', 0) > 10:
            recommendations.append("Implementar documentación sistemática de funciones")
        
        if stats['by_type'].get('function_too_complex', 0) > 5:
            recommendations.append("Refactorizar funciones complejas para mejorar mantenibilidad")
        
        if stats['by_type'].get('hardcoded_password', 0) > 0:
            recommendations.append("SEGURIDAD: Eliminar contraseñas hardcodeadas inmediatamente")
        
        # Recomendaciones por módulo
        problematic_modules = sorted(stats['by_module'].items(), 
                                   key=lambda x: x[1], reverse=True)[:3]
        
        for module, count in problematic_modules:
            if count > 10:
                recommendations.append(f"Módulo '{module}' requiere refactorización ({count} issues)")
        
        if not recommendations:
            recommendations.append("Calidad de código en estado aceptable")
        
        return recommendations

def main():
    """Función principal de auditoría avanzada."""
    print("AUDITOR AVANZADO DE CODIGO - Módulo por Módulo")
    print("=" * 60)
    
    current_dir = Path(__file__).parent.parent
    if not (current_dir / "rexus").exists():
        print("Error: No se encontró el directorio 'rexus'")
        return 1
    
    auditor = AdvancedCodeAuditor(str(current_dir))
    
    try:
        report = auditor.audit_project_by_modules()
        
        print(f"\nRESULTADOS DE AUDITORIA AVANZADA:")
        print(f"Módulos auditados: {report['modules_audited']}")
        print(f"Issues totales encontrados: {report['total_issues']}")
        
        print(f"\nPOR SEVERIDAD:")
        for severity, count in report['statistics']['by_severity'].items():
            print(f"  {severity}: {count}")
        
        print(f"\nTOP 10 TIPOS DE ISSUES:")
        top_types = sorted(report['statistics']['by_type'].items(), 
                          key=lambda x: x[1], reverse=True)[:10]
        for issue_type, count in top_types:
            print(f"  {issue_type}: {count}")
        
        print(f"\nMODULOS MAS PROBLEMATICOS:")
        top_modules = sorted(report['statistics']['by_module'].items(), 
                           key=lambda x: x[1], reverse=True)[:5]
        for module, count in top_modules:
            print(f"  {module}: {count} issues")
        
        print(f"\nRECOMENDACIONES:")
        for i, rec in enumerate(report['recommendations'], 1):
            print(f"{i}. {rec}")
        
        # Mostrar issues críticos
        if report['critical_issues']:
            print(f"\nISSUES CRITICOS (primeros 5):")
            for issue in report['critical_issues'][:5]:
                print(f"  - [{issue['severity']}] {issue['file']}:{issue['line']}")
                print(f"    {issue['message']}")
        
        # Guardar reporte
        report_file = current_dir / "advanced_audit_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\nReporte completo guardado en: {report_file}")
        
        # Código de salida basado en severidad
        exit_code = 0
        if report['statistics']['by_severity'].get('BLOCKER', 0) > 0:
            exit_code = 2
        elif report['statistics']['by_severity'].get('CRITICAL', 0) > 0:
            exit_code = 1
        
        status = "BLOQUEADO" if exit_code == 2 else "CRITICO" if exit_code == 1 else "ACEPTABLE"
        print(f"\nESTADO FINAL: {status}")
        
        return exit_code
        
    except Exception as e:
        print(f"Error ejecutando auditoría: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)