#!/usr/bin/env python3
"""
UI Consistency Validator - Rexus.app v2.0.0

Valida la consistencia de componentes UI entre módulos.
Detecta inconsistencias y sugiere mejoras.
"""

import sys
import os
import re
from pathlib import Path
from typing import Dict, List, Tuple
import ast

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class UIConsistencyValidator:
    """Validador de consistencia UI entre módulos"""
    
    def __init__(self):
        self.project_root = project_root
        self.view_files = []
        self.validation_results = {
            'component_consistency': [],
            'style_consistency': [],
            'layout_consistency': [],
            'color_consistency': [],
            'typography_consistency': [],
            'recommendations': []
        }
    
    def validate_all_modules(self) -> Dict:
        """Ejecuta validación completa de consistencia UI"""
        
        print("UI CONSISTENCY VALIDATION - REXUS.APP")
        print("=" * 50)
        
        # 1. Encontrar archivos view.py
        self._find_view_files()
        
        # 2. Validar uso de componentes estándar
        self._validate_component_usage()
        
        # 3. Validar consistencia de estilos
        self._validate_style_consistency()
        
        # 4. Validar layouts estándar
        self._validate_layout_patterns()
        
        # 5. Validar uso de colores
        self._validate_color_usage()
        
        # 6. Validar tipografía
        self._validate_typography()
        
        # 7. Generar recomendaciones
        self._generate_recommendations()
        
        return self.validation_results
    
    def _find_view_files(self):
        """Encuentra todos los archivos view.py en módulos"""
        
        print("\nBUSCANDO ARCHIVOS VIEW")
        print("-" * 30)
        
        modules_dir = self.project_root / "rexus" / "modules"
        
        for view_file in modules_dir.rglob("view.py"):
            self.view_files.append(view_file)
            print(f"  OK {view_file.relative_to(self.project_root)}")
        
        print(f"\nTotal archivos encontrados: {len(self.view_files)}")
    
    def _validate_component_usage(self):
        """Valida uso de componentes Rexus estándar"""
        
        print("\n🧩 VALIDANDO USO DE COMPONENTES")
        print("-" * 35)
        
        # Componentes que deberían usarse
        standard_components = {
            'QPushButton': 'RexusButton',
            'QLabel': 'RexusLabel',
            'QLineEdit': 'RexusLineEdit',
            'QComboBox': 'RexusComboBox',
            'QTableWidget': 'RexusTable',
            'QGroupBox': 'RexusGroupBox',
            'QFrame': 'RexusFrame',
            'QProgressBar': 'RexusProgressBar'
        }
        
        inconsistent_files = []
        
        for view_file in self.view_files:
            try:
                content = view_file.read_text(encoding='utf-8')
                inconsistencies = []
                
                # Buscar imports de componentes Qt básicos
                for qt_component, rexus_component in standard_components.items():
                    if qt_component in content:
                        # Verificar si también importa el componente Rexus
                        if rexus_component not in content:
                            inconsistencies.append({
                                'file': str(view_file.relative_to(self.project_root)),
                                'qt_component': qt_component,
                                'suggested_component': rexus_component,
                                'line_count': content.count(qt_component)
                            })
                
                if inconsistencies:
                    inconsistent_files.extend(inconsistencies)
                    print(f"  ⚠️  {view_file.name}: {len(inconsistencies)} inconsistencias")
                else:
                    print(f"  ✅ {view_file.name}: Consistente")
                    
            except Exception as e:
                print(f"  ❌ Error leyendo {view_file.name}: {e}")
        
        self.validation_results['component_consistency'] = inconsistent_files
        print(f"\nTotal inconsistencias de componentes: {len(inconsistent_files)}")
    
    def _validate_style_consistency(self):
        """Valida consistencia en el uso de estilos"""
        
        print("\n🎨 VALIDANDO CONSISTENCIA DE ESTILOS")
        print("-" * 38)
        
        # Patrones de estilos que indican inconsistencia
        style_patterns = [
            r'setStyleSheet\(["\'].*background.*["\']',
            r'setStyleSheet\(["\'].*color.*["\']',
            r'setStyleSheet\(["\'].*font.*["\']',
            r'setStyleSheet\(["\'].*border.*["\']'
        ]
        
        style_violations = []
        
        for view_file in self.view_files:
            try:
                content = view_file.read_text(encoding='utf-8')
                violations = 0
                
                for pattern in style_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    violations += len(matches)
                
                if violations > 0:
                    style_violations.append({
                        'file': str(view_file.relative_to(self.project_root)),
                        'inline_styles': violations
                    })
                    print(f"  ⚠️  {view_file.name}: {violations} estilos inline")
                else:
                    print(f"  ✅ {view_file.name}: Sin estilos inline")
                    
            except Exception as e:
                print(f"  ❌ Error leyendo {view_file.name}: {e}")
        
        self.validation_results['style_consistency'] = style_violations
        print(f"\nTotal violaciones de estilo: {len(style_violations)}")
    
    def _validate_layout_patterns(self):
        """Valida uso de patrones de layout estándar"""
        
        print("\n📐 VALIDANDO PATRONES DE LAYOUT")
        print("-" * 32)
        
        layout_components = [
            'QVBoxLayout',
            'QHBoxLayout', 
            'QGridLayout',
            'QFormLayout'
        ]
        
        layout_usage = []
        
        for view_file in self.view_files:
            try:
                content = view_file.read_text(encoding='utf-8')
                file_layouts = {}
                
                for layout in layout_components:
                    count = content.count(layout)
                    if count > 0:
                        file_layouts[layout] = count
                
                # Verificar si usa RexusLayoutHelper
                uses_helper = 'RexusLayoutHelper' in content
                
                if file_layouts:
                    layout_usage.append({
                        'file': str(view_file.relative_to(self.project_root)),
                        'layouts': file_layouts,
                        'uses_helper': uses_helper,
                        'total_layouts': sum(file_layouts.values())
                    })
                    
                    status = "✅" if uses_helper else "⚠️ "
                    print(f"  {status} {view_file.name}: {sum(file_layouts.values())} layouts")
                
            except Exception as e:
                print(f"  ❌ Error leyendo {view_file.name}: {e}")
        
        self.validation_results['layout_consistency'] = layout_usage
        print(f"\nArchivos con layouts: {len(layout_usage)}")
    
    def _validate_color_usage(self):
        """Valida uso de colores estándar"""
        
        print("\n🌈 VALIDANDO USO DE COLORES")
        print("-" * 27)
        
        # Patrones de colores hardcodeados
        color_patterns = [
            r'#[0-9a-fA-F]{6}',  # Hex colors
            r'#[0-9a-fA-F]{3}',   # Short hex colors
            r'rgb\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*\)',  # RGB
            r'rgba\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*,\s*[\d.]+\s*\)'  # RGBA
        ]
        
        color_violations = []
        
        for view_file in self.view_files:
            try:
                content = view_file.read_text(encoding='utf-8')
                hardcoded_colors = []
                
                for pattern in color_patterns:
                    matches = re.findall(pattern, content)
                    hardcoded_colors.extend(matches)
                
                uses_rexus_colors = 'RexusColors' in content
                
                if hardcoded_colors:
                    color_violations.append({
                        'file': str(view_file.relative_to(self.project_root)),
                        'hardcoded_colors': len(hardcoded_colors),
                        'uses_rexus_colors': uses_rexus_colors,
                        'colors': list(set(hardcoded_colors))  # Unique colors
                    })
                    
                    status = "⚠️ " if not uses_rexus_colors else "🔶"
                    print(f"  {status} {view_file.name}: {len(hardcoded_colors)} colores hardcodeados")
                else:
                    print(f"  ✅ {view_file.name}: Sin colores hardcodeados")
                    
            except Exception as e:
                print(f"  ❌ Error leyendo {view_file.name}: {e}")
        
        self.validation_results['color_consistency'] = color_violations
        print(f"\nTotal violaciones de color: {len(color_violations)}")
    
    def _validate_typography(self):
        """Valida consistencia tipográfica"""
        
        print("\n📝 VALIDANDO TIPOGRAFÍA")
        print("-" * 22)
        
        typography_violations = []
        
        for view_file in self.view_files:
            try:
                content = view_file.read_text(encoding='utf-8')
                
                # Buscar uso de QFont directo
                qfont_usage = content.count('QFont(')
                setfont_usage = content.count('setFont(')
                uses_rexus_fonts = 'RexusFonts' in content
                
                if qfont_usage > 0 or setfont_usage > 0:
                    if not uses_rexus_fonts:
                        typography_violations.append({
                            'file': str(view_file.relative_to(self.project_root)),
                            'qfont_usage': qfont_usage,
                            'setfont_usage': setfont_usage,
                            'uses_rexus_fonts': uses_rexus_fonts
                        })
                        print(f"  ⚠️  {view_file.name}: Tipografía inconsistente")
                    else:
                        print(f"  ✅ {view_file.name}: Usa RexusFonts")
                else:
                    print(f"  ✅ {view_file.name}: Sin tipografía custom")
                    
            except Exception as e:
                print(f"  ❌ Error leyendo {view_file.name}: {e}")
        
        self.validation_results['typography_consistency'] = typography_violations
        print(f"\nTotal violaciones tipográficas: {len(typography_violations)}")
    
    def _generate_recommendations(self):
        """Genera recomendaciones de mejora"""
        
        print("\n💡 GENERANDO RECOMENDACIONES")
        print("-" * 29)
        
        recommendations = []
        
        # Recomendaciones basadas en componentes
        component_issues = len(self.validation_results['component_consistency'])
        if component_issues > 0:
            recommendations.append({
                'category': 'Componentes',
                'priority': 'Alta',
                'description': f"Migrar {component_issues} usos de componentes Qt a componentes Rexus",
                'action': "Reemplazar QPushButton por RexusButton, QLabel por RexusLabel, etc."
            })
        
        # Recomendaciones basadas en estilos
        style_issues = len(self.validation_results['style_consistency'])
        if style_issues > 0:
            recommendations.append({
                'category': 'Estilos',
                'priority': 'Media',
                'description': f"Eliminar {style_issues} archivos con estilos inline",
                'action': "Usar componentes Rexus que incluyen estilos estándar automáticamente"
            })
        
        # Recomendaciones basadas en colores
        color_issues = len(self.validation_results['color_consistency'])
        if color_issues > 0:
            recommendations.append({
                'category': 'Colores',
                'priority': 'Media',
                'description': f"Estandarizar colores en {color_issues} archivos",
                'action': "Usar RexusColors.PRIMARY, RexusColors.SUCCESS, etc. en lugar de colores hardcodeados"
            })
        
        # Recomendaciones basadas en tipografía
        typography_issues = len(self.validation_results['typography_consistency'])
        if typography_issues > 0:
            recommendations.append({
                'category': 'Tipografía',
                'priority': 'Baja',
                'description': f"Estandarizar tipografía en {typography_issues} archivos",
                'action': "Usar RexusFonts.get_title_font(), RexusFonts.get_body_font(), etc."
            })
        
        # Recomendaciones generales
        if len(self.view_files) > 0:
            recommendations.append({
                'category': 'General',
                'priority': 'Alta',
                'description': "Implementar BaseModuleView para consistencia estructural",
                'action': "Hacer que las vistas hereden de BaseModuleView para estructura unificada"
            })
        
        self.validation_results['recommendations'] = recommendations
        
        for rec in recommendations:
            priority_icon = {"Alta": "🔴", "Media": "🟡", "Baja": "🟢"}
            print(f"  {priority_icon[rec['priority']]} {rec['category']}: {rec['description']}")
    
    def generate_report(self) -> str:
        """Genera reporte completo de validación"""
        
        lines = [
            "UI CONSISTENCY VALIDATION REPORT - REXUS.APP",
            "=" * 50,
            f"Fecha: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Archivos analizados: {len(self.view_files)}",
            ""
        ]
        
        # Resumen de resultados
        lines.extend([
            "📊 RESUMEN DE RESULTADOS",
            "-" * 25,
            f"• Componentes inconsistentes: {len(self.validation_results['component_consistency'])}",
            f"• Archivos con estilos inline: {len(self.validation_results['style_consistency'])}",
            f"• Archivos con layouts: {len(self.validation_results['layout_consistency'])}",
            f"• Violaciones de colores: {len(self.validation_results['color_consistency'])}",
            f"• Violaciones tipográficas: {len(self.validation_results['typography_consistency'])}",
            ""
        ])
        
        # Recomendaciones detalladas
        lines.extend([
            "💡 RECOMENDACIONES DE MEJORA",
            "-" * 28,
        ])
        
        for rec in self.validation_results['recommendations']:
            lines.extend([
                f"[{rec['priority'].upper()}] {rec['category']}",
                f"  Problema: {rec['description']}",
                f"  Acción: {rec['action']}",
                ""
            ])
        
        # Detalles de componentes inconsistentes
        if self.validation_results['component_consistency']:
            lines.extend([
                "🔧 DETALLES DE COMPONENTES INCONSISTENTES",
                "-" * 41,
            ])
            
            for issue in self.validation_results['component_consistency'][:5]:  # Mostrar top 5
                lines.extend([
                    f"Archivo: {issue['file']}",
                    f"  Componente Qt: {issue['qt_component']} ({issue['line_count']} usos)",
                    f"  Reemplazar con: {issue['suggested_component']}",
                    ""
                ])
        
        # Estado final
        total_issues = sum([
            len(self.validation_results['component_consistency']),
            len(self.validation_results['style_consistency']),
            len(self.validation_results['color_consistency']),
            len(self.validation_results['typography_consistency'])
        ])
        
        if total_issues == 0:
            status = "✅ EXCELENTE - UI Completamente Consistente"
        elif total_issues <= 5:
            status = "🟡 BUENO - Pocas Inconsistencias"
        elif total_issues <= 15:
            status = "🟠 REGULAR - Necesita Mejoras"
        else:
            status = "🔴 CRÍTICO - Requiere Refactorización"
        
        lines.extend([
            "🎯 ESTADO FINAL",
            "-" * 14,
            f"Estado: {status}",
            f"Total de problemas encontrados: {total_issues}",
            f"Archivos que requieren atención: {len(set([item['file'] for category in ['component_consistency', 'style_consistency', 'color_consistency', 'typography_consistency'] for item in self.validation_results[category]]))}"
        ])
        
        return "\n".join(lines)
    
    def save_report(self, filename: str = None) -> str:
        """Guarda el reporte en un archivo"""
        
        if not filename:
            timestamp = __import__('datetime').datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ui_consistency_report_{timestamp}.txt"
        
        report_text = self.generate_report()
        
        report_path = self.project_root / filename
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_text)
        
        return str(report_path)


def main():
    """Función principal para ejecutar la validación"""
    
    validator = UIConsistencyValidator()
    
    # Ejecutar validación completa
    results = validator.validate_all_modules()
    
    # Mostrar reporte
    print("\n" + validator.generate_report())
    
    # Guardar reporte
    report_file = validator.save_report()
    print(f"\n📄 Reporte guardado en: {report_file}")
    
    # Código de salida basado en problemas encontrados
    total_issues = sum([
        len(results['component_consistency']),
        len(results['style_consistency']),
        len(results['color_consistency']),
        len(results['typography_consistency'])
    ])
    
    if total_issues == 0:
        return 0
    elif total_issues <= 5:
        return 1
    else:
        return 2


if __name__ == "__main__":
    sys.exit(main())