#!/usr/bin/env python3
"""
Auditoría Comprehensiva de UI/UX para Rexus.app

Realiza una auditoría completa de la interfaz de usuario:
- Consistencia visual entre módulos
- Accesibilidad y usabilidad
- Feedback visual y interacciones
- Estándares de diseño
- Métricas de usabilidad
"""

import os
import re
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class UIAuditResult:
    """Resultado de auditoría UI/UX."""
    module_name: str
    category: str
    issue: str
    severity: str  # critical, high, medium, low
    line_number: int = 0
    recommendation: str = ""
    code_snippet: str = ""


class UIUXAuditor:
    """Auditor comprehensivo de interfaz de usuario."""
    
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.modules_dir = root_dir / "rexus" / "modules"
        self.audit_results = []
        
        # Patrones de problemas UI/UX
        self.ui_patterns = {
            # Inconsistencias de estilo
            'hardcoded_colors': [
                r'#[0-9a-fA-F]{6}',  # Colores hexadecimales hardcodeados
                r'rgb\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*\)',  # RGB hardcodeados
            ],
            'hardcoded_sizes': [
                r'font-size:\s*\d+px',  # Tamaños de fuente hardcodeados
                r'width:\s*\d+px',  # Anchos hardcodeados
                r'height:\s*\d+px',  # Alturas hardcodeadas
            ],
            'missing_accessibility': [
                r'QLabel\([^)]*\)(?![^{]*setAccessible)',  # Labels sin accesibilidad
                r'QPushButton\([^)]*\)(?![^{]*setAccessible)',  # Botones sin accesibilidad
            ],
            'poor_feedback': [
                r'\.setText\([^)]*\)(?![^{]*setStyleSheet)',  # Texto sin feedback visual
                r'QMessageBox\.information\(',  # Usar sistema de feedback propio
            ],
            'inconsistent_naming': [
                r'btn_[a-z]+',  # Botones con prefijo inconsistente
                r'label_[a-z]+',  # Labels con prefijo inconsistente
            ]
        }
        
        # Estándares UI/UX esperados
        self.ui_standards = {
            'colors': {
                'primary': '#2980b9',
                'secondary': '#3498db', 
                'success': '#27ae60',
                'warning': '#f39c12',
                'error': '#e74c3c',
                'text': '#2c3e50',
                'background': '#ffffff'
            },
            'fonts': {
                'primary': 'Arial, sans-serif',
                'monospace': 'Courier New, monospace'
            },
            'spacing': {
                'small': '4px',
                'medium': '8px', 
                'large': '16px',
                'xlarge': '24px'
            },
            'required_feedback_elements': [
                'loading_indicator',
                'success_message',
                'error_message',
                'progress_feedback'
            ]
        }
    
    def audit_all_modules(self) -> List[UIAuditResult]:
        """Audita todos los módulos de la aplicación."""
        print("=== AUDITORÍA COMPREHENSIVA UI/UX ===")
        print(f"Analizando módulos en: {self.modules_dir}")
        print()
        
        if not self.modules_dir.exists():
            print("[ERROR] Directorio de módulos no encontrado")
            return []
        
        modules_found = 0
        
        for module_dir in self.modules_dir.iterdir():
            if module_dir.is_dir() and not module_dir.name.startswith('__'):
                modules_found += 1
                print(f"[MODULE] Auditando módulo: {module_dir.name}")
                
                # Auditar vista principal
                view_file = module_dir / "view.py"
                if view_file.exists():
                    self.audit_view_file(view_file, module_dir.name)
                
                # Auditar vista completa si existe
                view_completa = module_dir / "view_completa.py"
                if view_completa.exists():
                    self.audit_view_file(view_completa, f"{module_dir.name}_completa")
                
                # Auditar diálogos específicos
                for dialog_file in module_dir.glob("*dialog*.py"):
                    self.audit_view_file(dialog_file, f"{module_dir.name}_{dialog_file.stem}")
        
        print(f"\n[OK] Auditoría completada: {modules_found} módulos analizados")
        return self.audit_results
    
    def audit_view_file(self, file_path: Path, module_name: str):
        """Audita un archivo de vista específico."""
        try:
            content = file_path.read_text(encoding='utf-8')
            lines = content.splitlines()
            
            # Auditorías específicas
            self.check_visual_consistency(content, lines, module_name)
            self.check_accessibility(content, lines, module_name)
            self.check_user_feedback(content, lines, module_name)
            self.check_responsive_design(content, lines, module_name)
            self.check_performance_ui(content, lines, module_name)
            
        except Exception as e:
            print(f"[WARNING] Error auditando {file_path}: {e}")
    
    def check_visual_consistency(self, content: str, lines: List[str], module_name: str):
        """Verifica consistencia visual."""
        # Buscar colores hardcodeados
        for line_num, line in enumerate(lines, 1):
            for pattern in self.ui_patterns['hardcoded_colors']:
                if re.search(pattern, line):
                    self.audit_results.append(UIAuditResult(
                        module_name=module_name,
                        category="Consistencia Visual",
                        issue="Color hardcodeado encontrado",
                        severity="medium",
                        line_number=line_num,
                        recommendation="Usar variables de color definidas en theme_manager",
                        code_snippet=line.strip()
                    ))
        
        # Buscar tamaños hardcodeados
        for line_num, line in enumerate(lines, 1):
            for pattern in self.ui_patterns['hardcoded_sizes']:
                if re.search(pattern, line):
                    self.audit_results.append(UIAuditResult(
                        module_name=module_name,
                        category="Consistencia Visual",
                        issue="Tamaño hardcoded encontrado",
                        severity="low",
                        line_number=line_num,
                        recommendation="Usar constantes de spacing definidas",
                        code_snippet=line.strip()
                    ))
        
        # Verificar uso de estilos inline vs clases CSS
        inline_style_count = len(re.findall(r'setStyleSheet\([^)]*\)', content))
        if inline_style_count > 10:
            self.audit_results.append(UIAuditResult(
                module_name=module_name,
                category="Consistencia Visual",
                issue=f"Muchos estilos inline ({inline_style_count})",
                severity="medium",
                recommendation="Migrar estilos a archivos QSS centralizados"
            ))
    
    def check_accessibility(self, content: str, lines: List[str], module_name: str):
        """Verifica accesibilidad."""
        # Verificar elementos sin descripción accesible
        ui_elements = ['QLabel', 'QPushButton', 'QLineEdit', 'QComboBox', 'QTextEdit']
        
        for element in ui_elements:
            element_count = len(re.findall(f'{element}\\(', content))
            accessible_count = len(re.findall(f'{element}[^{{}}]*setAccessible', content))
            
            if element_count > 0 and accessible_count / element_count < 0.3:
                self.audit_results.append(UIAuditResult(
                    module_name=module_name,
                    category="Accesibilidad",
                    issue=f"Solo {accessible_count}/{element_count} {element} tienen información accesible",
                    severity="high",
                    recommendation="Agregar setAccessibleName/Description a elementos UI"
                ))
        
        # Verificar tooltips
        tooltip_count = len(re.findall(r'setToolTip\(', content))
        button_count = len(re.findall(r'QPushButton\(', content))
        
        if button_count > 0 and tooltip_count / button_count < 0.5:
            self.audit_results.append(UIAuditResult(
                module_name=module_name,
                category="Accesibilidad",
                issue=f"Solo {tooltip_count}/{button_count} botones tienen tooltips",
                severity="medium",
                recommendation="Agregar tooltips descriptivos a botones"
            ))
    
    def check_user_feedback(self, content: str, lines: List[str], module_name: str):
        """Verifica feedback visual para el usuario."""
        # Verificar sistema de mensajes
        feedback_indicators = [
            'mostrar_mensaje',
            'feedback',
            'loading',
            'progress',
            'success',
            'error',
            'warning'
        ]
        
        feedback_found = any(indicator in content.lower() for indicator in feedback_indicators)
        
        if not feedback_found:
            self.audit_results.append(UIAuditResult(
                module_name=module_name,
                category="Feedback Usuario",
                issue="No se encontró sistema de feedback visual",
                severity="high",
                recommendation="Implementar sistema de mensajes y feedback visual"
            ))
        
        # Verificar indicadores de progreso para operaciones largas
        long_operations = ['obtener_', 'cargar_', 'guardar_', 'eliminar_', 'buscar_']
        progress_indicators = ['QProgressBar', 'loading', 'progress']
        
        has_long_ops = any(op in content for op in long_operations)
        has_progress = any(indicator in content for indicator in progress_indicators)
        
        if has_long_ops and not has_progress:
            self.audit_results.append(UIAuditResult(
                module_name=module_name,
                category="Feedback Usuario",
                issue="Operaciones largas sin indicadores de progreso",
                severity="medium",
                recommendation="Agregar indicadores de progreso/loading"
            ))
    
    def check_responsive_design(self, content: str, lines: List[str], module_name: str):
        """Verifica diseño responsivo."""
        # Verificar uso de layouts responsivos
        responsive_layouts = ['QVBoxLayout', 'QHBoxLayout', 'QGridLayout', 'QFormLayout']
        fixed_positioning = ['move(', 'setGeometry(', 'resize(']
        
        layout_count = sum(len(re.findall(layout, content)) for layout in responsive_layouts)
        fixed_count = sum(len(re.findall(pos, content)) for pos in fixed_positioning)
        
        if fixed_count > layout_count:
            self.audit_results.append(UIAuditResult(
                module_name=module_name,
                category="Diseño Responsivo",
                issue="Más posicionamiento fijo que layouts responsivos",
                severity="medium",
                recommendation="Usar layouts en lugar de posicionamiento fijo"
            ))
        
        # Verificar políticas de tamaño
        size_policies = ['setSizePolicy', 'sizeHint', 'minimumSize', 'maximumSize']
        has_size_policy = any(policy in content for policy in size_policies)
        
        if not has_size_policy and layout_count > 0:
            self.audit_results.append(UIAuditResult(
                module_name=module_name,
                category="Diseño Responsivo",
                issue="Layouts sin políticas de tamaño definidas",
                severity="low",
                recommendation="Agregar políticas de tamaño apropiadas"
            ))
    
    def check_performance_ui(self, content: str, lines: List[str], module_name: str):
        """Verifica rendimiento de UI."""
        # Verificar carga perezosa
        large_ui_indicators = ['QTableWidget', 'QTreeWidget', 'QListWidget']
        lazy_loading = ['setRowCount', 'setModel', 'pagination']
        
        has_large_ui = any(indicator in content for indicator in large_ui_indicators)
        has_lazy_loading = any(lazy in content for lazy in lazy_loading)
        
        if has_large_ui and not has_lazy_loading:
            self.audit_results.append(UIAuditResult(
                module_name=module_name,
                category="Rendimiento UI",
                issue="Widgets grandes sin carga perezosa/paginación",
                severity="medium",
                recommendation="Implementar carga perezosa o paginación"
            ))
        
        # Verificar optimización de imágenes
        image_loads = len(re.findall(r'QPixmap\(.*\)', content))
        image_cache = len(re.findall(r'cache|Cache', content))
        
        if image_loads > 5 and image_cache == 0:
            self.audit_results.append(UIAuditResult(
                module_name=module_name,
                category="Rendimiento UI",
                issue=f"{image_loads} cargas de imagen sin cache",
                severity="low",
                recommendation="Implementar cache para imágenes"
            ))
    
    def generate_audit_report(self) -> Dict[str, Any]:
        """Genera reporte completo de auditoría."""
        if not self.audit_results:
            return {"error": "No hay resultados de auditoría"}
        
        # Agrupar resultados por severidad
        by_severity = {}
        for result in self.audit_results:
            if result.severity not in by_severity:
                by_severity[result.severity] = []
            by_severity[result.severity].append(result)
        
        # Agrupar por categoría
        by_category = {}
        for result in self.audit_results:
            if result.category not in by_category:
                by_category[result.category] = []
            by_category[result.category].append(result)
        
        # Agrupar por módulo
        by_module = {}
        for result in self.audit_results:
            if result.module_name not in by_module:
                by_module[result.module_name] = []
            by_module[result.module_name].append(result)
        
        # Calcular métricas
        total_issues = len(self.audit_results)
        critical_issues = len(by_severity.get('critical', []))
        high_issues = len(by_severity.get('high', []))
        medium_issues = len(by_severity.get('medium', []))
        low_issues = len(by_severity.get('low', []))
        
        # Score de calidad UI/UX (0-100)
        quality_score = max(0, 100 - (critical_issues * 20 + high_issues * 10 + medium_issues * 5 + low_issues * 2))
        
        return {
            'timestamp': datetime.now().isoformat(),
            'total_issues': total_issues,
            'quality_score': quality_score,
            'severity_breakdown': {
                'critical': critical_issues,
                'high': high_issues,
                'medium': medium_issues,
                'low': low_issues
            },
            'category_breakdown': {cat: len(issues) for cat, issues in by_category.items()},
            'module_breakdown': {mod: len(issues) for mod, issues in by_module.items()},
            'recommendations': self.generate_recommendations(),
            'detailed_results': [
                {
                    'module': r.module_name,
                    'category': r.category,
                    'issue': r.issue,
                    'severity': r.severity,
                    'line': r.line_number,
                    'recommendation': r.recommendation,
                    'code': r.code_snippet
                }
                for r in self.audit_results
            ]
        }
    
    def generate_recommendations(self) -> List[str]:
        """Generate prioritized recommendations."""
        recommendations = []
        
        # Analizar patrones de issues
        categories = {}
        for result in self.audit_results:
            if result.category not in categories:
                categories[result.category] = []
            categories[result.category].append(result)
        
        # Generar recomendaciones por categoría
        for category, issues in categories.items():
            high_priority = [i for i in issues if i.severity in ['critical', 'high']]
            if high_priority:
                if category == "Accesibilidad":
                    recommendations.append(
                        f"ALTA PRIORIDAD: Implementar informacion accesible (setAccessibleName/Description) "
                        f"en {len(high_priority)} elementos"
                    )
                elif category == "Feedback Usuario":
                    recommendations.append(
                        f"ALTA PRIORIDAD: Implementar sistema de feedback visual y indicadores "
                        f"de progreso en {len(high_priority)} modulos"
                    )
                elif category == "Consistencia Visual":
                    recommendations.append(
                        f"MEDIA PRIORIDAD: Crear sistema de diseno centralizado para "
                        f"resolver {len(issues)} inconsistencias visuales"
                    )
        
        if not recommendations:
            recommendations.append("No se encontraron issues criticos de UI/UX")
        
        return recommendations
    
    def save_report(self, output_path: Path):
        """Guarda el reporte de auditoría."""
        report = self.generate_audit_report()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"[REPORT] Reporte guardado en: {output_path}")
        return report


def run_comprehensive_ui_audit():
    """Ejecuta auditoría comprehensiva de UI/UX."""
    # Obtener directorio raíz
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent.parent
    
    print(f"[AUDIT] Directorio del proyecto: {root_dir}")
    print()
    
    # Crear auditor
    auditor = UIUXAuditor(root_dir)
    
    # Ejecutar auditoría
    results = auditor.audit_all_modules()
    
    if not results:
        print("[OK] No se encontraron issues de UI/UX")
        return True
    
    # Generar y guardar reporte
    reports_dir = root_dir / "logs"
    reports_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = reports_dir / f"ui_ux_audit_{timestamp}.json"
    
    report = auditor.save_report(report_path)
    
    # Mostrar resumen
    print("\n" + "="*60)
    print("RESUMEN DE AUDITORIA UI/UX")
    print("="*60)
    print(f"Total de issues encontrados: {report['total_issues']}")
    print(f"Puntuacion de calidad: {report['quality_score']}/100")
    print()
    
    print("Por severidad:")
    severity_colors = {'critical': '[CRIT]', 'high': '[HIGH]', 'medium': '[MED]', 'low': '[LOW]'}
    for severity, count in report['severity_breakdown'].items():
        if count > 0:
            color = severity_colors.get(severity, '[UNK]')
            print(f"  {color} {severity.upper()}: {count}")
    
    print("\nPor categoria:")
    for category, count in report['category_breakdown'].items():
        print(f"  - {category}: {count}")
    
    print("\nRECOMENDACIONES PRIORITARIAS:")
    for rec in report['recommendations']:
        print(f"  {rec}")
    
    # Evaluación general
    quality_score = report['quality_score']
    print(f"\n{'='*60}")
    if quality_score >= 90:
        print("CALIDAD UI/UX: EXCELENTE")
        print("Interfaz cumple altos estandares de usabilidad")
    elif quality_score >= 75:
        print("CALIDAD UI/UX: BUENA")
        print("Algunas mejoras menores recomendadas")
    elif quality_score >= 60:
        print("CALIDAD UI/UX: ACEPTABLE")
        print("Varias mejoras necesarias")
    else:
        print("CALIDAD UI/UX: REQUIERE ATENCION")
        print("Mejoras criticas necesarias")
    
    return quality_score >= 70


if __name__ == "__main__":
    success = run_comprehensive_ui_audit()
    sys.exit(0 if success else 1)