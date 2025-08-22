# -*- coding: utf-8 -*-
"""
Test Automatizado de Contraste y Estilos UI - Rexus.app
Verifica problemas de contraste y consistencia visual en todos los módulos
"""

import sys
import re
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass

# Agregar ruta raíz para imports
root_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_path))


@dataclass
class ContrastIssue:
    """Representa un problema de contraste detectado."""
    file: str
    line_number: int
    issue_type: str
    description: str
    severity: str  # 'critical', 'warning', 'info'
    suggestion: str


class ContrastAnalyzer:
    """Analizador de problemas de contraste y estilos."""

    def __init__(self):
        self.issues: List[ContrastIssue] = []
        self.module_paths = [
            root_path / "rexus" / "modules",
            root_path / "rexus" / "ui"
        ]

        # Colores problemáticos conocidos
        self.problematic_combinations = [
            ("#000000", "#000000"),  # Negro sobre negro
            ("#ffffff", "#ffffff"),  # Blanco sobre blanco
            ("#000", "#000"),        # Negro sobre negro (abreviado)
            ("#fff", "#fff"),        # Blanco sobre blanco (abreviado)
        ]

        # Colores de bajo contraste
        self.low_contrast_colors = [
            "#888888", "#999999", "#aaaaaa", "#bbbbbb", "#cccccc"
        ]

        # Patrones problemáticos
        self.problematic_patterns = [
            (r'color:\s*#000.*background.*#000', 'Negro sobre negro'),
            (r'background.*#000.*color:\s*#000', 'Negro sobre negro'),
            (r'color:\s*white.*background.*white', 'Blanco sobre blanco'),
            (r'background.*white.*color:\s*white', 'Blanco sobre blanco'),
            (r'font-size:\s*[1-7]px', 'Fuente demasiado pequeña'),
            (r'min-height:\s*[1-9]px[^0-9]', 'Altura mínima muy pequeña'),
            (r'padding:\s*[0-1]px', 'Padding muy pequeño'),
            (r'QLineEdit.*background.*transparent', 'Input transparente problemático'),
            (r'color:\s*transparent', 'Texto transparente'),
        ]

    def analyze_file(self, file_path: Path) -> List[ContrastIssue]:
        """Analiza un archivo específico en busca de problemas de contraste."""
        issues = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')

            # Analizar línea por línea
            for i, line in enumerate(lines, 1):
                line_lower = line.lower()

                # Verificar patrones problemáticos
                for pattern, description in self.problematic_patterns:
                    if re.search(pattern, line_lower):
                        issues.append(ContrastIssue(
                            file=str(file_path),
                            line_number=i,
                            issue_type="contrast",
                            description=f"{description}: {line.strip()}",
                            severity="critical",
                            suggestion=self._get_suggestion_for_pattern(pattern)
                        ))

                # Verificar estilos QSS problemáticos
                if 'setStyleSheet' in line or '.qss' in file_path.suffix:
                    issues.extend(self._analyze_qss_line(file_path, i, line))

                # Verificar colores específicos problemáticos
                issues.extend(self._analyze_color_usage(file_path, i, line))

        except Exception as e:
            issues.append(ContrastIssue(
                file=str(file_path),
                line_number=0,
                issue_type="file_error",
                description=f"Error leyendo archivo: {e}",
                severity="warning",
                suggestion="Verificar codificación del archivo"
            ))

        return issues

    def _analyze_qss_line(self,
file_path: Path,
        line_num: int,
        line: str) -> List[ContrastIssue]:
        """Analiza una línea que contiene estilos QSS."""
        issues = []
        line_lower = line.lower()

        # Detectar estilos problemáticos comunes
        if 'background' in line_lower and 'color' in line_lower:
            # Verificar si hay colores similares en la misma línea
            colors = re.findall(r'#[0-9a-fA-F]{3,6}', line)
            if len(colors) >= 2:
                bg_color = colors[0] if 'background' in line[:line.find(colors[0])] else None
                text_color = colors[1] if 'color' in line[:line.find(colors[1])] else colors[0]

                if bg_color and text_color and self._colors_too_similar(bg_color, text_color):
                    issues.append(ContrastIssue(
                        file=str(file_path),
                        line_number=line_num,
                        issue_type="low_contrast",
                        description=f"Contraste bajo entre {bg_color} y {text_color}",
                        severity="warning",
                        suggestion="Usar colores con mayor contraste (ratio mínimo 4.5:1)"
                    ))

        # Verificar tamaños de fuente muy pequeños
        font_match = re.search(r'font-size:\s*(\d+)px', line_lower)
        if font_match:
            size = int(font_match.group(1))
            if size < 10:
                issues.append(ContrastIssue(
                    file=str(file_path),
                    line_number=line_num,
                    issue_type="font_size",
                    description=f"Fuente muy pequeña: {size}px",
                    severity="warning",
                    suggestion="Usar mínimo 12px para texto normal, 14px para texto principal"
                ))

        return issues

    def _analyze_color_usage(self,
file_path: Path,
        line_num: int,
        line: str) -> List[ContrastIssue]:
        """Analiza el uso de colores en una línea."""
        issues = []

        # Buscar colores problemáticos específicos
        for color in self.low_contrast_colors:
            if color in line.lower():
                issues.append(ContrastIssue(
                    file=str(file_path),
                    line_number=line_num,
                    issue_type="low_contrast_color",
                    description=f"Color de bajo contraste detectado: {color}",
                    severity="info",
                    suggestion="Considerar usar colores más contrastantes"
                ))

        return issues

    def _colors_too_similar(self, color1: str, color2: str) -> bool:
        """Verifica si dos colores son demasiado similares."""
        # Simplificación: convertir a valores RGB y comparar
        try:
            c1 = self._hex_to_rgb(color1)
            c2 = self._hex_to_rgb(color2)

            # Calcular diferencia euclidiana
            diff = sum((a - b) ** 2 for a, b in zip(c1, c2)) ** 0.5
            return diff < 50  # Threshold arbitrario
        except:
            return False

    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Convierte color hexadecimal a RGB."""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 3:
            hex_color = ''.join([c*2 for c in hex_color])
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def _get_suggestion_for_pattern(self, pattern: str) -> str:
        """Retorna sugerencia específica para un patrón problemático."""
        suggestions = {
            r'font-size:\s*[1-7]px': 'Usar mínimo 12px para texto legible',
            r'min-height:\s*[1-9]px[^0-9]': 'Usar mínimo 20px para elementos clickeables',
            r'padding:\s*[0-1]px': 'Usar mínimo 4px de padding para espaciado',
            r'QLineEdit.*background.*transparent': 'Definir background sólido para inputs',
            r'color:\s*transparent': 'Evitar texto transparente, usar colores visibles'
        }

        for p, suggestion in suggestions.items():
            if pattern == p:
                return suggestion

        return "Revisar contraste y legibilidad"

    def analyze_modules(self) -> Dict[str, List[ContrastIssue]]:
        """Analiza todos los módulos en busca de problemas de contraste."""
        results = {}

        for module_path in self.module_paths:
            if module_path.exists():
                for py_file in module_path.rglob("*.py"):
                    if py_file.is_file():
                        issues = self.analyze_file(py_file)
                        if issues:
                            relative_path = str(py_file.relative_to(root_path))
                            results[relative_path] = issues

                # También analizar archivos QSS
                for qss_file in module_path.rglob("*.qss"):
                    if qss_file.is_file():
                        issues = self.analyze_file(qss_file)
                        if issues:
                            relative_path = str(qss_file.relative_to(root_path))
                            results[relative_path] = issues

        return results

    def generate_report(self, results: Dict[str, List[ContrastIssue]]) -> str:
        """Genera un reporte detallado de los problemas encontrados."""
        report = []
        report.append("=" * 80)
        report.append("REPORTE DE ANÁLISIS DE CONTRASTE Y ESTILOS UI")
        report.append("=" * 80)
        report.append("")

        total_issues = sum(len(issues) for issues in results.values())
        critical_issues = sum(
            len([i for i in issues if i.severity == 'critical'])
            for issues in results.values()
        )
        warning_issues = sum(
            len([i for i in issues if i.severity == 'warning'])
            for issues in results.values()
        )

        report.append(f"RESUMEN:")
        report.append(f"  - Total de archivos analizados: {len(results)}")
        report.append(f"  - Total de problemas: {total_issues}")
        report.append(f"  - Problemas críticos: {critical_issues}")
        report.append(f"  - Advertencias: {warning_issues}")
        report.append("")

        if total_issues == 0:
            report.append("[OK] No se encontraron problemas de contraste!")
            report.append("")
            return "\n".join(report)

        # Agrupar por severidad
        for severity in ['critical', 'warning', 'info']:
            severity_issues = []
            for file_path, issues in results.items():
                for issue in issues:
                    if issue.severity == severity:
                        severity_issues.append((file_path, issue))

            if severity_issues:
                report.append(f"{severity.upper()} ISSUES:")
                report.append("-" * 40)

                for file_path, issue in severity_issues:
                    report.append(f"[FILE] {file_path}:{issue.line_number}")
                    report.append(f"   [ISSUE] {issue.description}")
                    report.append(f"   [FIX] {issue.suggestion}")
                    report.append("")

        # Resumen por módulo
        report.append("RESUMEN POR MÓDULO:")
        report.append("-" * 40)

        module_stats = {}
        for file_path, issues in results.items():
            if 'modules/' in file_path:
                module = file_path.split('modules/')[1].split('/')[0]
                if module not in module_stats:
                    module_stats[module] = 0
                module_stats[module] += len(issues)

        for module, count in sorted(module_stats.items(), key=lambda x: x[1], reverse=True):
            status = "[CRITICAL]" if count > 10 else "[WARNING]" if count > 5 else "[OK]"
            report.append(f"  {status} {module}: {count} problemas")

        return "\n".join(report)


def run_contrast_test():
    """Ejecuta el test de contraste y genera el reporte."""
    print("[CONTRAST] Iniciando analisis de contraste y estilos UI...")

    analyzer = ContrastAnalyzer()
    results = analyzer.analyze_modules()
    report = analyzer.generate_report(results)

    # Mostrar reporte en consola
    print(report)

    # Guardar reporte en archivo
    report_file = root_path / "contrast_report.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"\n[REPORT] Reporte guardado en: {report_file}")

    # Retornar número de problemas críticos
    total_critical = sum(
        len([i for i in issues if i.severity == 'critical'])
        for issues in results.values()
    )

    return total_critical == 0


if __name__ == "__main__":
    success = run_contrast_test()
    sys.exit(0 if success else 1)
