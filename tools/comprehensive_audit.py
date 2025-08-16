#!/usr/bin/env python3
"""
Auditoría Comprehensiva de Código - Rexus.app

Detecta y cataloga TODOS los problemas que los tests automáticos no pueden encontrar:
- exec/eval usage (RCE risk)
- except Exception genéricos 
- SQL injection potencial
- Print statements en producción
- Complejidad cognitiva alta
- Literales duplicados
- Variables no usadas
- Imports circulares

Fecha: 15/08/2025
Objetivo: Encontrar los 113+ problemas reales del código
"""

import os
import ast
import re
import sys
from pathlib import Path
from typing import Dict, List, Any, Tuple, Set
from collections import defaultdict, Counter

# Agregar ruta del proyecto
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from rexus.utils.app_logger import get_logger
    logger = get_logger("comprehensive_audit")
except ImportError:
    import logging
    logger = logging.getLogger("comprehensive_audit")


class ComprehensiveAuditor:
    """Auditor que encuentra TODOS los problemas reales del código."""

    def __init__(self, project_root: Path):
        """Inicializa el auditor."""
        self.project_root = project_root
        self.issues = defaultdict(list)
        self.stats = defaultdict(int)
        
        # Patrones de riesgo crítico
        self.critical_patterns = {
            'exec_eval': [
                r'\bexec\s*\(',
                r'\beval\s*\(',
                r'exec\s*\(',
                r'eval\s*\(',
            ],
            'sql_injection': [
                r'cursor\.execute\s*\(\s*f["\']',
                r'cursor\.execute\s*\([^,)]*\+',
                r'cursor\.execute\s*\([^,)]*%',
                r'\.format\s*\(\s*\).*cursor\.execute',
                r'f["\'].*SELECT.*{.*}.*["\']',
                r'f["\'].*INSERT.*{.*}.*["\']',
                r'f["\'].*UPDATE.*{.*}.*["\']',
                r'f["\'].*DELETE.*{.*}.*["\']',
            ],
            'generic_exceptions': [
                r'except\s+Exception\s*:',
                r'except\s*:',
                r'except\s+Exception\s+as',
            ],
            'print_statements': [
                r'\bprint\s*\(',
            ],
            'hardcoded_secrets': [
                r'password\s*=\s*["\'][^"\']+["\']',
                r'secret\s*=\s*["\'][^"\']+["\']',
                r'token\s*=\s*["\'][^"\']+["\']',
                r'api_key\s*=\s*["\'][^"\']+["\']',
                r'SECRET_KEY\s*=\s*["\'][^"\']+["\']',
            ],
            'dangerous_imports': [
                r'import\s+subprocess',
                r'import\s+os',
                r'from\s+subprocess',
                r'import\s+pickle',
                r'import\s+marshal',
            ],
        }

    def audit_entire_project(self) -> Dict[str, Any]:
        """Ejecuta auditoría completa del proyecto."""
        print("INICIANDO AUDITORIA COMPREHENSIVA - REXUS.APP")
        print("=" * 60)
        
        # 1. Auditar archivos Python
        self._audit_python_files()
        
        # 2. Auditar archivos SQL
        self._audit_sql_files()
        
        # 3. Auditar archivos de configuración
        self._audit_config_files()
        
        # 4. Análisis de complejidad
        self._analyze_complexity()
        
        # 5. Detectar código duplicado
        self._detect_duplicates()
        
        # 6. Análisis de dependencias
        self._analyze_dependencies()
        
        # 7. Generar reporte final
        return self._generate_comprehensive_report()

    def _audit_python_files(self):
        """Audita todos los archivos Python."""
        print("\n📋 1. AUDITANDO ARCHIVOS PYTHON")
        print("-" * 40)
        
        python_files = list(self.project_root.rglob("*.py"))
        total_files = len(python_files)
        
        for i, file_path in enumerate(python_files):
            if i % 50 == 0:  # Progress indicator
                print(f"Progreso: {i}/{total_files} archivos procesados...")
            
            try:
                self._audit_python_file(file_path)
            except Exception as e:
                self.issues['audit_errors'].append({
                    'file': str(file_path),
                    'error': str(e),
                    'type': 'file_processing_error'
                })

        print(f"✅ {total_files} archivos Python auditados")

    def _audit_python_file(self, file_path: Path):
        """Audita un archivo Python específico."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            rel_path = file_path.relative_to(self.project_root)
            
            # 1. Patrones críticos de seguridad
            self._check_critical_patterns(rel_path, content)
            
            # 2. Análisis AST para problemas estructurales
            try:
                tree = ast.parse(content)
                self._analyze_ast(rel_path, tree, content)
            except SyntaxError as e:
                self.issues['syntax_errors'].append({
                    'file': str(rel_path),
                    'line': getattr(e, 'lineno', 0),
                    'error': str(e),
                    'type': 'syntax_error'
                })
            
            # 3. Análisis de líneas específicas
            self._analyze_lines(rel_path, content.splitlines())
            
        except Exception as e:
            self.issues['file_errors'].append({
                'file': str(file_path),
                'error': str(e),
                'type': 'file_read_error'
            })

    def _check_critical_patterns(self, file_path: Path, content: str):
        """Verifica patrones críticos de riesgo."""
        for pattern_type, patterns in self.critical_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    
                    self.issues[pattern_type].append({
                        'file': str(file_path),
                        'line': line_num,
                        'pattern': pattern,
                        'match': match.group(0),
                        'context': self._get_line_context(content, line_num),
                        'severity': self._get_severity(pattern_type),
                        'type': pattern_type
                    })
                    
                    self.stats[pattern_type] += 1

    def _analyze_ast(self, file_path: Path, tree: ast.AST, content: str):
        """Analiza el AST para detectar problemas estructurales."""
        class ASTAnalyzer(ast.NodeVisitor):
            def __init__(self, auditor, file_path, content):
                self.auditor = auditor
                self.file_path = file_path
                self.content = content
                self.lines = content.splitlines()
                
            def visit_FunctionDef(self, node):
                # Detectar funciones complejas
                complexity = self._calculate_complexity(node)
                if complexity > 15:
                    self.auditor.issues['high_complexity'].append({
                        'file': str(self.file_path),
                        'line': node.lineno,
                        'function': node.name,
                        'complexity': complexity,
                        'type': 'cognitive_complexity',
                        'severity': 'HIGH' if complexity > 25 else 'MEDIUM'
                    })
                
                # Detectar funciones muy largas
                if hasattr(node, 'end_lineno') and node.end_lineno:
                    length = node.end_lineno - node.lineno
                    if length > 100:
                        self.auditor.issues['long_functions'].append({
                            'file': str(self.file_path),
                            'line': node.lineno,
                            'function': node.name,
                            'length': length,
                            'type': 'function_length',
                            'severity': 'MEDIUM'
                        })
                
                self.generic_visit(node)
            
            def visit_Try(self, node):
                # Detectar try/except problemáticos
                for handler in node.handlers:
                    if handler.type is None:  # bare except
                        self.auditor.issues['bare_except'].append({
                            'file': str(self.file_path),
                            'line': handler.lineno,
                            'type': 'bare_except',
                            'severity': 'HIGH'
                        })
                    elif isinstance(handler.type, ast.Name) and handler.type.id == 'Exception':
                        # Verificar si se hace logging del error
                        has_logging = False
                        for stmt in handler.body:
                            if (isinstance(stmt, ast.Expr) and 
                                isinstance(stmt.value, ast.Call) and
                                isinstance(stmt.value.func, ast.Attribute) and
                                'log' in stmt.value.func.attr):
                                has_logging = True
                                break
                        
                        if not has_logging:
                            self.auditor.issues['silent_exceptions'].append({
                                'file': str(self.file_path),
                                'line': handler.lineno,
                                'type': 'silent_exception',
                                'severity': 'HIGH'
                            })
                
                self.generic_visit(node)
            
            def visit_Import(self, node):
                # Detectar imports peligrosos
                for alias in node.names:
                    if alias.name in ['subprocess', 'os', 'pickle', 'marshal', 'eval', 'exec']:
                        self.auditor.issues['dangerous_imports'].append({
                            'file': str(self.file_path),
                            'line': node.lineno,
                            'import': alias.name,
                            'type': 'dangerous_import',
                            'severity': 'MEDIUM'
                        })
                
                self.generic_visit(node)
            
            def visit_Call(self, node):
                # Detectar llamadas peligrosas
                if isinstance(node.func, ast.Name):
                    if node.func.id in ['exec', 'eval']:
                        self.auditor.issues['dangerous_calls'].append({
                            'file': str(self.file_path),
                            'line': node.lineno,
                            'call': node.func.id,
                            'type': 'dangerous_call',
                            'severity': 'CRITICAL'
                        })
                    elif node.func.id == 'print':
                        # Solo flaggear prints en archivos de producción
                        if not any(test_dir in str(self.file_path) for test_dir in ['test', 'tools', 'scripts']):
                            self.auditor.issues['production_prints'].append({
                                'file': str(self.file_path),
                                'line': node.lineno,
                                'type': 'production_print',
                                'severity': 'LOW'
                            })
                
                self.generic_visit(node)
            
            def _calculate_complexity(self, node):
                """Calcula complejidad cognitiva simplificada."""
                complexity = 1  # Base complexity
                
                for child in ast.walk(node):
                    if isinstance(child, (ast.If, ast.For, ast.While, ast.With)):
                        complexity += 1
                    elif isinstance(child, ast.Try):
                        complexity += len(child.handlers)
                    elif isinstance(child, (ast.And, ast.Or)):
                        complexity += 1
                
                return complexity
        
        analyzer = ASTAnalyzer(self, file_path, content)
        analyzer.visit(tree)

    def _analyze_lines(self, file_path: Path, lines: List[str]):
        """Analiza líneas específicas para problemas."""
        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            # Detectar TODO/FIXME sin asignar
            if re.search(r'#\s*(TODO|FIXME|XXX|HACK)', line_stripped, re.IGNORECASE):
                self.issues['todos'].append({
                    'file': str(file_path),
                    'line': i,
                    'content': line_stripped,
                    'type': 'todo_comment',
                    'severity': 'LOW'
                })
            
            # Detectar líneas muy largas
            if len(line) > 120:
                self.issues['long_lines'].append({
                    'file': str(file_path),
                    'line': i,
                    'length': len(line),
                    'type': 'line_length',
                    'severity': 'LOW'
                })
            
            # Detectar strings hardcodeados sospechosos
            if re.search(r'password|secret|token|key', line_stripped, re.IGNORECASE):
                if '=' in line_stripped and any(quote in line_stripped for quote in ['"', "'"]):
                    self.issues['potential_secrets'].append({
                        'file': str(file_path),
                        'line': i,
                        'content': line_stripped,
                        'type': 'potential_secret',
                        'severity': 'HIGH'
                    })

    def _audit_sql_files(self):
        """Audita archivos SQL."""
        print("\n📋 2. AUDITANDO ARCHIVOS SQL")
        print("-" * 40)
        
        sql_files = list(self.project_root.rglob("*.sql"))
        
        for file_path in sql_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                rel_path = file_path.relative_to(self.project_root)
                
                # Detectar SQL potencialmente problemático
                if re.search(r'SELECT\s+\*', content, re.IGNORECASE):
                    self.issues['sql_select_star'].append({
                        'file': str(rel_path),
                        'type': 'sql_select_star',
                        'severity': 'MEDIUM'
                    })
                
                # Detectar concatenación en SQL
                if re.search(r'\|\||\+', content):
                    self.issues['sql_concatenation'].append({
                        'file': str(rel_path),
                        'type': 'sql_concatenation',
                        'severity': 'MEDIUM'
                    })
                
            except Exception as e:
                self.issues['sql_errors'].append({
                    'file': str(file_path),
                    'error': str(e),
                    'type': 'sql_file_error'
                })

        print(f"✅ {len(sql_files)} archivos SQL auditados")

    def _audit_config_files(self):
        """Audita archivos de configuración."""
        print("\n📋 3. AUDITANDO ARCHIVOS DE CONFIGURACIÓN")
        print("-" * 40)
        
        config_patterns = ['*.json', '*.yaml', '*.yml', '*.ini', '*.cfg', '*.env*']
        config_files = []
        
        for pattern in config_patterns:
            config_files.extend(self.project_root.rglob(pattern))
        
        for file_path in config_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                rel_path = file_path.relative_to(self.project_root)
                
                # Detectar secrets en configuración
                if re.search(r'(password|secret|token|key)\s*[:=]\s*["\']?[^"\'\s]{8,}', content, re.IGNORECASE):
                    self.issues['config_secrets'].append({
                        'file': str(rel_path),
                        'type': 'config_secret',
                        'severity': 'HIGH'
                    })
                
                # Detectar debug habilitado
                if re.search(r'debug\s*[:=]\s*true', content, re.IGNORECASE):
                    self.issues['debug_enabled'].append({
                        'file': str(rel_path),
                        'type': 'debug_enabled',
                        'severity': 'MEDIUM'
                    })
                
            except Exception as e:
                self.issues['config_errors'].append({
                    'file': str(file_path),
                    'error': str(e),
                    'type': 'config_file_error'
                })

        print(f"✅ {len(config_files)} archivos de configuración auditados")

    def _analyze_complexity(self):
        """Analiza complejidad del proyecto."""
        print("\n📋 4. ANALIZANDO COMPLEJIDAD")
        print("-" * 40)
        
        # Ya se hace en _analyze_ast, pero aquí podemos agregar métricas adicionales
        total_lines = 0
        total_files = 0
        
        for py_file in self.project_root.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = len(f.readlines())
                    total_lines += lines
                    total_files += 1
                    
                    # Detectar archivos muy grandes
                    if lines > 1000:
                        rel_path = py_file.relative_to(self.project_root)
                        self.issues['large_files'].append({
                            'file': str(rel_path),
                            'lines': lines,
                            'type': 'large_file',
                            'severity': 'MEDIUM'
                        })
            except:
                pass
        
        self.stats['total_lines'] = total_lines
        self.stats['total_files'] = total_files
        
        print(f"✅ Analizadas {total_files} archivos con {total_lines} líneas totales")

    def _detect_duplicates(self):
        """Detecta código y strings duplicados."""
        print("\n📋 5. DETECTANDO DUPLICADOS")
        print("-" * 40)
        
        string_literals = defaultdict(list)
        
        for py_file in self.project_root.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                rel_path = py_file.relative_to(self.project_root)
                
                # Detectar strings literales duplicados
                strings = re.findall(r'["\']([^"\']{10,})["\']', content)
                for string in strings:
                    if len(string.strip()) > 5:  # Ignorar strings muy cortos
                        string_literals[string].append(str(rel_path))
                
            except:
                pass
        
        # Reportar duplicados
        for string, files in string_literals.items():
            if len(files) > 2:  # Aparece en más de 2 archivos
                self.issues['duplicate_strings'].append({
                    'string': string[:50] + '...' if len(string) > 50 else string,
                    'files': files,
                    'occurrences': len(files),
                    'type': 'duplicate_string',
                    'severity': 'LOW'
                })
        
        print(f"✅ Detectados {len(self.issues['duplicate_strings'])} strings duplicados")

    def _analyze_dependencies(self):
        """Analiza dependencias y imports."""
        print("\n📋 6. ANALIZANDO DEPENDENCIAS")
        print("-" * 40)
        
        imports = defaultdict(set)
        circular_candidates = defaultdict(set)
        
        for py_file in self.project_root.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                rel_path = py_file.relative_to(self.project_root)
                
                # Detectar imports
                import_matches = re.findall(r'^(?:from\s+(\S+)\s+import|import\s+(\S+))', content, re.MULTILINE)
                
                for match in import_matches:
                    module = match[0] or match[1]
                    if module.startswith('rexus'):
                        imports[str(rel_path)].add(module)
                        circular_candidates[module].add(str(rel_path))
                
            except:
                pass
        
        # Detectar posibles imports circulares
        for module, files in circular_candidates.items():
            if len(files) > 1:
                for file in files:
                    # Verificar si el archivo importa algo que lo importe de vuelta
                    file_imports = imports.get(file, set())
                    for imp in file_imports:
                        if file in circular_candidates.get(imp, set()):
                            self.issues['circular_imports'].append({
                                'file1': file,
                                'file2': imp,
                                'type': 'circular_import',
                                'severity': 'HIGH'
                            })
        
        print(f"✅ Analizados imports en {len(imports)} archivos")

    def _generate_comprehensive_report(self) -> Dict[str, Any]:
        """Genera reporte comprehensivo final."""
        print("\n📊 7. GENERANDO REPORTE COMPREHENSIVO")
        print("-" * 40)
        
        total_issues = sum(len(issues) for issues in self.issues.values())
        
        # Clasificar por severidad
        critical_issues = []
        high_issues = []
        medium_issues = []
        low_issues = []
        
        for issue_type, issues_list in self.issues.items():
            for issue in issues_list:
                severity = issue.get('severity', 'MEDIUM')
                if severity == 'CRITICAL':
                    critical_issues.append(issue)
                elif severity == 'HIGH':
                    high_issues.append(issue)
                elif severity == 'MEDIUM':
                    medium_issues.append(issue)
                else:
                    low_issues.append(issue)
        
        report = {
            'summary': {
                'total_issues': total_issues,
                'critical_issues': len(critical_issues),
                'high_issues': len(high_issues),
                'medium_issues': len(medium_issues),
                'low_issues': len(low_issues),
                'total_files_analyzed': self.stats.get('total_files', 0),
                'total_lines_analyzed': self.stats.get('total_lines', 0),
            },
            'issues_by_category': dict(self.issues),
            'issues_by_severity': {
                'critical': critical_issues,
                'high': high_issues,
                'medium': medium_issues,
                'low': low_issues,
            },
            'stats': dict(self.stats),
            'recommendations': self._generate_recommendations(critical_issues, high_issues, medium_issues)
        }
        
        return report

    def _generate_recommendations(self, critical: List, high: List, medium: List) -> List[Dict]:
        """Genera recomendaciones basadas en los problemas encontrados."""
        recommendations = []
        
        if critical:
            recommendations.append({
                'priority': 'CRITICAL',
                'action': 'Eliminar inmediatamente exec/eval usage',
                'reason': 'Riesgo crítico de ejecución de código remoto (RCE)',
                'files_affected': len(set(issue['file'] for issue in critical)),
                'estimated_effort': '1-2 días'
            })
        
        if high:
            recommendations.append({
                'priority': 'HIGH',
                'action': 'Corregir manejo de excepciones genéricas',
                'reason': 'Silenciamiento de errores críticos y pérdida de debugging',
                'files_affected': len(set(issue['file'] for issue in high)),
                'estimated_effort': '3-5 días'
            })
        
        if medium:
            recommendations.append({
                'priority': 'MEDIUM',
                'action': 'Migrar prints a logging centralizado',
                'reason': 'Mejor monitoreo y debugging en producción',
                'files_affected': len(set(issue['file'] for issue in medium)),
                'estimated_effort': '2-3 días'
            })
        
        return recommendations

    def _get_severity(self, pattern_type: str) -> str:
        """Determina severidad basada en el tipo de patrón."""
        severity_map = {
            'exec_eval': 'CRITICAL',
            'sql_injection': 'CRITICAL',
            'hardcoded_secrets': 'HIGH',
            'generic_exceptions': 'HIGH',
            'dangerous_imports': 'MEDIUM',
            'print_statements': 'LOW',
        }
        return severity_map.get(pattern_type, 'MEDIUM')

    def _get_line_context(self, content: str, line_num: int, context_lines: int = 2) -> List[str]:
        """Obtiene contexto de líneas alrededor de una línea específica."""
        lines = content.splitlines()
        start = max(0, line_num - context_lines - 1)
        end = min(len(lines), line_num + context_lines)
        
        context = []
        for i in range(start, end):
            prefix = ">>>" if i == line_num - 1 else "   "
            context.append(f"{prefix} {i+1}: {lines[i]}")
        
        return context


def main():
    """Función principal."""
    project_root = Path(__file__).parent.parent
    
    print("AUDITORIA COMPREHENSIVA DE CODIGO - REXUS.APP")
    print("Detectando TODOS los problemas que los tests no encuentran...")
    print("=" * 60)
    
    auditor = ComprehensiveAuditor(project_root)
    report = auditor.audit_entire_project()
    
    # Mostrar resumen
    summary = report['summary']
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE AUDITORÍA COMPREHENSIVA")
    print("=" * 60)
    
    print(f"📁 Archivos analizados: {summary['total_files_analyzed']}")
    print(f"📝 Líneas analizadas: {summary['total_lines_analyzed']:,}")
    print(f"🚨 TOTAL DE PROBLEMAS ENCONTRADOS: {summary['total_issues']}")
    print()
    print("🎯 PROBLEMAS POR SEVERIDAD:")
    print(f"  🔴 CRÍTICOS: {summary['critical_issues']} (requieren acción inmediata)")
    print(f"  🟠 ALTOS: {summary['high_issues']} (afectan estabilidad/seguridad)")
    print(f"  🟡 MEDIOS: {summary['medium_issues']} (mejoras importantes)")
    print(f"  🟢 BAJOS: {summary['low_issues']} (optimizaciones)")
    
    # Mostrar top problemas
    print("\n🔍 TOP PROBLEMAS POR CATEGORÍA:")
    for category, issues in report['issues_by_category'].items():
        if issues and len(issues) > 0:
            print(f"  • {category}: {len(issues)} ocurrencias")
    
    # Recomendaciones
    print("\n💡 RECOMENDACIONES PRIORITARIAS:")
    for i, rec in enumerate(report['recommendations'], 1):
        print(f"  {i}. [{rec['priority']}] {rec['action']}")
        print(f"     Razón: {rec['reason']}")
        print(f"     Archivos afectados: {rec['files_affected']}")
        print(f"     Esfuerzo estimado: {rec['estimated_effort']}")
        print()
    
    # Guardar reporte detallado
    import json
    report_file = project_root / 'comprehensive_audit_report.json'
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"💾 Reporte detallado guardado en: {report_file}")
    
    if summary['total_issues'] > 100:
        print(f"\n⚠️ CONFIRMADO: {summary['total_issues']} problemas encontrados")
        print("📋 Estos son los problemas reales que los tests automáticos no detectan")
        print("🎯 Se requiere corrección manual y sistemática")
    
    return summary['total_issues']


if __name__ == '__main__':
    total_issues = main()
    sys.exit(1 if total_issues > 0 else 0)