"""
Auditoría Automática de Módulos - Rexus.app
Detecta variables no definidas, botones sin configurar, formularios con problemas, etc.
"""

import sys
import ast
import re
from pathlib import Path
from typing import Dict, List, Tuple, Set
from dataclasses import dataclass

# Agregar ruta raíz
root_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_path))


@dataclass
class AuditIssue:
    """Representa un problema encontrado en la auditoría."""
    file: str
    line_number: int
    issue_type: str
    severity: str  # 'critical', 'warning', 'info'
    description: str
    suggestion: str


class ModuleAuditor:
    """Auditor automático de módulos."""
    
    def __init__(self):
        self.modules_path = root_path / "rexus" / "modules"
        self.issues: List[AuditIssue] = []
        
        # Patrones problemáticos comunes
        self.undefined_patterns = [
            r'self\.([a-zA-Z_][a-zA-Z0-9_]*)\s*\.',  # Acceso a self.variable
            r'self\.([a-zA-Z_][a-zA-Z0-9_]*)\s*\(',  # Llamada a self.método()
        ]
        
        # Métodos de PyQt6 que requieren configuración
        self.unconfigured_methods = [
            'clicked.connect',
            'textChanged.connect', 
            'currentTextChanged.connect',
            'itemSelectionChanged.connect',
            'itemDoubleClicked.connect'
        ]
        
        # Problemas comunes en formularios
        self.form_issues = [
            r'setStyleSheet\(["\'].*color:\s*transparent',  # Texto transparente
            r'setStyleSheet\(["\'].*background:\s*transparent',  # Fondo transparente problemático
            r'\.text\(\).*without.*validation',  # Texto sin validación
        ]
    
    def audit_all_modules(self) -> Dict[str, List[AuditIssue]]:
        """Audita todos los módulos y retorna un diccionario con los problemas."""
        results = {}
        
        for module_dir in self.modules_path.iterdir():
            if module_dir.is_dir() and not module_dir.name.startswith('.'):
                module_issues = self.audit_module(module_dir)
                if module_issues:
                    results[module_dir.name] = module_issues
        
        return results
    
    def audit_module(self, module_path: Path) -> List[AuditIssue]:
        """Audita un módulo específico."""
        issues = []
        
        # Auditar archivos Python principales
        for py_file in module_path.glob("*.py"):
            if py_file.name in ['view.py', 'controller.py', 'model.py']:
                issues.extend(self.audit_file(py_file))
        
        return issues
    
    def audit_file(self, file_path: Path) -> List[AuditIssue]:
        """Audita un archivo específico."""
        issues = []
        
        try:
            content = file_path.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            # Analizar sintaxis con AST
            try:
                tree = ast.parse(content)
                issues.extend(self.audit_ast(file_path, tree, lines))
            except SyntaxError as e:
                issues.append(AuditIssue(
                    file=str(file_path),
                    line_number=e.lineno or 0,
                    issue_type="syntax_error",
                    severity="critical",
                    description=f"Error de sintaxis: {e.msg}",
                    suggestion="Corregir error de sintaxis antes de continuar"
                ))
                return issues
            
            # Análisis línea por línea
            for i, line in enumerate(lines, 1):
                issues.extend(self.audit_line(file_path, i, line))
        
        except Exception as e:
            issues.append(AuditIssue(
                file=str(file_path),
                line_number=0,
                issue_type="file_error",
                severity="warning",
                description=f"Error leyendo archivo: {e}",
                suggestion="Verificar permisos y encoding del archivo"
            ))
        
        return issues
    
    def audit_ast(self, file_path: Path, tree: ast.AST, lines: List[str]) -> List[AuditIssue]:
        """Audita usando el AST para detectar problemas estructurales."""
        issues = []
        
        class VariableTracker(ast.NodeVisitor):
            def __init__(self, auditor, file_path, lines):
                self.auditor = auditor
                self.file_path = file_path
                self.lines = lines
                self.defined_vars: Set[str] = set()
                self.used_vars: Set[str] = set()
                self.issues = []
                
            def visit_FunctionDef(self, node):
                # Resetear variables definidas para cada función
                old_vars = self.defined_vars.copy()
                
                # Agregar parámetros como variables definidas
                for arg in node.args.args:
                    self.defined_vars.add(arg.arg)
                
                self.generic_visit(node)
                
                # Restaurar variables después de la función
                self.defined_vars = old_vars
                
            def visit_Assign(self, node):
                # Rastrear asignaciones de variables
                for target in node.targets:
                    if isinstance(target, ast.Attribute):
                        if isinstance(target.value, ast.Name) and target.value.id == 'self':
                            self.defined_vars.add(f"self.{target.attr}")
                    elif isinstance(target, ast.Name):
                        self.defined_vars.add(target.id)
                self.generic_visit(node)
                
            def visit_Attribute(self, node):
                # Rastrear acceso a atributos
                if isinstance(node.value, ast.Name) and node.value.id == 'self':
                    var_name = f"self.{node.attr}"
                    self.used_vars.add(var_name)
                    
                    # Verificar si la variable fue definida
                    if var_name not in self.defined_vars and not self.is_likely_method(node.attr):
                        self.issues.append(AuditIssue(
                            file=str(self.file_path),
                            line_number=node.lineno,
                            issue_type="undefined_variable",
                            severity="critical",
                            description=f"Variable/atributo posiblemente no definido: {var_name}",
                            suggestion=f"Verificar que {var_name} sea inicializado en __init__ o antes de usar"
                        ))
                
                self.generic_visit(node)
                
            def is_likely_method(self, name: str) -> bool:
                """Determina si un nombre es probablemente un método en lugar de una variable."""
                method_patterns = [
                    'connect', 'disconnect', 'emit', 'show', 'hide', 'close',
                    'setText', 'getText', 'setEnabled', 'isEnabled',
                    'addWidget', 'removeWidget', 'setLayout', 'layout',
                    'setStyleSheet', 'styleSheet', 'update', 'repaint'
                ]
                return any(pattern in name for pattern in method_patterns)
        
        tracker = VariableTracker(self, file_path, lines)
        tracker.visit(tree)
        issues.extend(tracker.issues)
        
        return issues
    
    def audit_line(self, file_path: Path, line_num: int, line: str) -> List[AuditIssue]:
        """Audita una línea específica."""
        issues = []
        line_lower = line.lower().strip()
        
        # Detectar botones sin configurar
        if 'QPushButton' in line and '=' in line:
            button_name = self.extract_variable_name(line)
            if button_name:
                # Verificar si hay una línea .clicked.connect cerca
                issues.extend(self.check_button_configuration(file_path, line_num, button_name))
        
        # Detectar formularios con problemas de contraste
        if 'setStyleSheet' in line:
            if 'transparent' in line_lower and ('color' in line_lower or 'background' in line_lower):
                issues.append(AuditIssue(
                    file=str(file_path),
                    line_number=line_num,
                    issue_type="contrast_issue",
                    severity="warning",
                    description="Posible problema de contraste: uso de transparent",
                    suggestion="Usar colores específicos en lugar de transparent para mejor legibilidad"
                ))
        
        # Detectar inputs sin validación
        if '.text()' in line and 'validate' not in line_lower and 'sanitize' not in line_lower:
            if any(word in line for word in ['password', 'user', 'email', 'data']):
                issues.append(AuditIssue(
                    file=str(file_path),
                    line_number=line_num,
                    issue_type="validation_missing",
                    severity="warning",
                    description="Input sin validación aparente",
                    suggestion="Agregar validación/sanitización de entrada"
                ))
        
        # Detectar try/except sin manejo
        if line.strip() == 'except:' or line.strip() == 'except Exception:':
            issues.append(AuditIssue(
                file=str(file_path),
                line_number=line_num,
                issue_type="broad_exception",
                severity="warning", 
                description="Exception muy amplia sin manejo específico",
                suggestion="Usar excepciones específicas y logging apropiado"
            ))
        
        return issues
    
    def extract_variable_name(self, line: str) -> str:
        """Extrae el nombre de variable de una línea de asignación."""
        match = re.match(r'\s*(\w+)\s*=', line)
        return match.group(1) if match else ""
    
    def check_button_configuration(self, file_path: Path, line_num: int, button_name: str) -> List[AuditIssue]:
        """Verifica si un botón está configurado con clicked.connect."""
        issues = []
        
        try:
            content = file_path.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            # Buscar clicked.connect en las siguientes 10 líneas
            for i in range(line_num, min(line_num + 10, len(lines))):
                if f"{button_name}.clicked.connect" in lines[i]:
                    return []  # Botón está configurado
            
            # Si llegamos aquí, el botón no está configurado
            issues.append(AuditIssue(
                file=str(file_path),
                line_number=line_num,
                issue_type="unconfigured_button",
                severity="warning",
                description=f"Botón '{button_name}' no tiene clicked.connect configurado",
                suggestion=f"Agregar {button_name}.clicked.connect(método_handler)"
            ))
            
        except Exception:
            pass
        
        return issues
    
    def generate_report(self, results: Dict[str, List[AuditIssue]]) -> str:
        """Genera reporte de auditoría."""
        report = []
        report.append("=" * 80)
        report.append("REPORTE DE AUDITORÍA DE MÓDULOS")
        report.append("=" * 80)
        report.append("")
        
        total_issues = sum(len(issues) for issues in results.values())
        critical_issues = sum(
            len([i for i in issues if i.severity == 'critical'])
            for issues in results.values()
        )
        
        report.append(f"RESUMEN EJECUTIVO:")
        report.append(f"  - Módulos auditados: {len(results)}")
        report.append(f"  - Total de problemas: {total_issues}")
        report.append(f"  - Problemas críticos: {critical_issues}")
        report.append("")
        
        if total_issues == 0:
            report.append("[OK] No se encontraron problemas críticos!")
            return "\n".join(report)
        
        # Problemas por módulo
        for module_name, issues in sorted(results.items()):
            if not issues:
                continue
                
            critical = len([i for i in issues if i.severity == 'critical'])
            warnings = len([i for i in issues if i.severity == 'warning'])
            
            status = "[CRITICAL]" if critical > 0 else "[WARNING]" if warnings > 0 else "[INFO]"
            
            report.append(f"{status} MÓDULO: {module_name.upper()}")
            report.append("-" * 60)
            report.append(f"  Críticos: {critical} | Advertencias: {warnings}")
            report.append("")
            
            # Agrupar por tipo de problema
            by_type = {}
            for issue in issues:
                if issue.issue_type not in by_type:
                    by_type[issue.issue_type] = []
                by_type[issue.issue_type].append(issue)
            
            for issue_type, type_issues in by_type.items():
                report.append(f"  {issue_type.upper().replace('_', ' ')} ({len(type_issues)}):")
                
                for issue in type_issues[:3]:  # Mostrar solo los primeros 3
                    file_short = Path(issue.file).name
                    report.append(f"    - {file_short}:{issue.line_number} - {issue.description}")
                
                if len(type_issues) > 3:
                    report.append(f"    ... y {len(type_issues) - 3} más")
                report.append("")
        
        return "\n".join(report)


def run_modules_audit():
    """Ejecuta la auditoría de módulos."""
    print("[AUDIT] Iniciando auditoría de módulos...")
    
    auditor = ModuleAuditor()
    results = auditor.audit_all_modules()
    report = auditor.generate_report(results)
    
    # Mostrar reporte
    print(report)
    
    # Guardar reporte
    report_file = root_path / "modules_audit_report.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n[REPORT] Reporte guardado en: {report_file}")
    
    # Retornar éxito si no hay problemas críticos
    total_critical = sum(
        len([i for i in issues if i.severity == 'critical'])
        for issues in results.values()
    )
    
    return total_critical == 0


if __name__ == "__main__":
    success = run_modules_audit()
    sys.exit(0 if success else 1)