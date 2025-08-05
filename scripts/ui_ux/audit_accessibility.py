#!/usr/bin/env python3
"""
Auditoría de Accesibilidad para Rexus.app
Evalúa cumplimiento de estándares de accesibilidad WCAG 2.1
"""

import json
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class WCAGLevel(Enum):
    """Niveles de conformidad WCAG"""

    A = "A"
    AA = "AA"
    AAA = "AAA"


class WCAGGuideline(Enum):
    """Principales directrices WCAG 2.1"""

    PERCEIVABLE = "1_perceivable"
    OPERABLE = "2_operable"
    UNDERSTANDABLE = "3_understandable"
    ROBUST = "4_robust"


@dataclass
class AccessibilityIssue:
    """Representa un problema de accesibilidad detectado"""

    modulo: str
    archivo: str
    linea: int
    guideline: WCAGGuideline
    criterio: str  # Criterio WCAG específico (ej: 1.4.3)
    nivel: WCAGLevel
    severidad: str  # critical, high, medium, low
    descripcion: str
    solucion_recomendada: str
    codigo: str = ""
    element_type: str = ""


@dataclass
class AccessibilityReport:
    """Reporte completo de auditoría de accesibilidad"""

    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    issues: List[AccessibilityIssue] = field(default_factory=list)
    modulos_analizados: List[str] = field(default_factory=list)
    estadisticas: Dict[str, Any] = field(default_factory=dict)
    score_accesibilidad: float = 0.0
    nivel_conformidad: WCAGLevel | None = WCAGLevel.A
    recomendaciones_prioritarias: List[str] = field(default_factory=list)


class AccessibilityAuditor:
    """Auditor de accesibilidad WCAG 2.1"""

    def __init__(self):
        self.root_path = Path(__file__).parent.parent.parent
        self.views_path = self.root_path / "rexus" / "modules"
        self.report = AccessibilityReport()

        # Criterios WCAG 2.1 que podemos evaluar automáticamente
        self.wcag_patterns = {
            # 1.1.1 Non-text Content (Level A)
            "alt_text_missing": {
                "pattern": r"QLabel.*setPixmap|QIcon\(",
                "guideline": WCAGGuideline.PERCEIVABLE,
                "criterio": "1.1.1",
                "nivel": WCAGLevel.A,
                "descripcion": "Imagen sin texto alternativo",
                "solucion": "Agregar setAccessibleDescription() con descripción de la imagen",
            },
            # 1.3.1 Info and Relationships (Level A)
            "missing_labels": {
                "pattern": r"QLineEdit\(|QTextEdit\(|QComboBox\(",
                "guideline": WCAGGuideline.PERCEIVABLE,
                "criterio": "1.3.1",
                "nivel": WCAGLevel.A,
                "descripcion": "Campo de entrada sin etiqueta asociada",
                "solucion": "Agregar setAccessibleName() y asociar con QLabel",
            },
            # 1.4.3 Contrast (Level AA)
            "low_contrast": {
                "pattern": r"color:\s*#[0-9A-Fa-f]{6}|QColor\(\d+,\s*\d+,\s*\d+\)",
                "guideline": WCAGGuideline.PERCEIVABLE,
                "criterio": "1.4.3",
                "nivel": WCAGLevel.AA,
                "descripcion": "Posible problema de contraste de color",
                "solucion": "Verificar que el contraste sea al menos 4.5:1 para texto normal",
            },
            # 2.1.1 Keyboard Access (Level A)
            "keyboard_trap": {
                "pattern": r"setFocusPolicy\(Qt\.NoFocus\)",
                "guideline": WCAGGuideline.OPERABLE,
                "criterio": "2.1.1",
                "nivel": WCAGLevel.A,
                "descripcion": "Elemento no accesible por teclado",
                "solucion": "Permitir navegación por teclado con Qt.TabFocus o Qt.StrongFocus",
            },
            # 2.4.3 Focus Order (Level A)
            "focus_order": {
                "pattern": r"setTabOrder\(",
                "guideline": WCAGGuideline.OPERABLE,
                "criterio": "2.4.3",
                "nivel": WCAGLevel.A,
                "descripcion": "Verificar orden lógico de navegación",
                "solucion": "Asegurar que setTabOrder() sigue un orden lógico",
            },
            # 2.4.6 Headings and Labels (Level AA)
            "descriptive_labels": {
                "pattern": r'setText\(["\'].*["\']|setTitle\(["\'].*["\']',
                "guideline": WCAGGuideline.OPERABLE,
                "criterio": "2.4.6",
                "nivel": WCAGLevel.AA,
                "descripcion": "Etiqueta poco descriptiva",
                "solucion": "Usar etiquetas claras y descriptivas del propósito",
            },
            # 3.2.2 On Input (Level A)
            "context_change": {
                "pattern": r"currentTextChanged\.connect|textChanged\.connect",
                "guideline": WCAGGuideline.UNDERSTANDABLE,
                "criterio": "3.2.2",
                "nivel": WCAGLevel.A,
                "descripcion": "Posible cambio inesperado de contexto",
                "solucion": "Asegurar que cambios de entrada no causen cambios inesperados",
            },
            # 4.1.2 Name, Role, Value (Level A)
            "missing_role": {
                "pattern": r"QPushButton\(|QToolButton\(",
                "guideline": WCAGGuideline.ROBUST,
                "criterio": "4.1.2",
                "nivel": WCAGLevel.A,
                "descripcion": "Botón sin nombre accesible",
                "solucion": "Agregar setAccessibleName() y setAccessibleDescription()",
            },
        }

        # Colores para verificación de contraste
        self.color_combinations = []

    def analizar_modulo(self, modulo_path: Path) -> List[AccessibilityIssue]:
        """Analiza un módulo específico para problemas de accesibilidad"""
        issues = []

        # Buscar archivos view.py
        view_files = list(modulo_path.glob("**/view.py"))

        for view_file in view_files:
            modulo_name = modulo_path.name
            issues.extend(self._analizar_archivo_view(view_file, modulo_name))

        return issues

    def _analizar_archivo_view(
        self, archivo: Path, modulo: str
    ) -> List[AccessibilityIssue]:
        """Analiza un archivo view.py para problemas de accesibilidad"""
        issues = []

        try:
            with open(archivo, "r", encoding="utf-8") as f:
                contenido = f.read()
                lineas = contenido.split("\n")

            # Analizar cada línea
            for i, linea in enumerate(lineas, 1):
                issues.extend(self._verificar_patrones_wcag(linea, i, archivo, modulo))
                issues.extend(
                    self._verificar_estructura_accesible(
                        linea, i, archivo, modulo, contenido
                    )
                )

        except Exception as e:
            issues.append(
                AccessibilityIssue(
                    modulo=modulo,
                    archivo=str(archivo),
                    linea=0,
                    guideline=WCAGGuideline.ROBUST,
                    criterio="4.1.1",
                    nivel=WCAGLevel.A,
                    severidad="high",
                    descripcion=f"Error al analizar archivo: {e}",
                    solucion_recomendada="Verificar sintaxis y encoding del archivo",
                )
            )

        return issues

    def _verificar_patrones_wcag(
        self, linea: str, num_linea: int, archivo: Path, modulo: str
    ) -> List[AccessibilityIssue]:
        """Verifica patrones específicos de WCAG"""
        issues = []

        for patron_name, patron_info in self.wcag_patterns.items():
            if re.search(patron_info["pattern"], linea):
                # Verificaciones específicas por patrón
                if patron_name == "alt_text_missing":
                    issues.extend(
                        self._verificar_alt_text(
                            linea, num_linea, archivo, modulo, patron_info
                        )
                    )
                elif patron_name == "missing_labels":
                    issues.extend(
                        self._verificar_labels(
                            linea, num_linea, archivo, modulo, patron_info
                        )
                    )
                elif patron_name == "low_contrast":
                    issues.extend(
                        self._verificar_contraste(
                            linea, num_linea, archivo, modulo, patron_info
                        )
                    )
                elif patron_name == "keyboard_trap":
                    issues.extend(
                        self._verificar_navegacion_teclado(
                            linea, num_linea, archivo, modulo, patron_info
                        )
                    )
                elif patron_name == "descriptive_labels":
                    issues.extend(
                        self._verificar_etiquetas_descriptivas(
                            linea, num_linea, archivo, modulo, patron_info
                        )
                    )
                elif patron_name == "missing_role":
                    issues.extend(
                        self._verificar_roles_accesibles(
                            linea, num_linea, archivo, modulo, patron_info
                        )
                    )

        return issues

    def _verificar_alt_text(
        self, linea: str, num_linea: int, archivo: Path, modulo: str, patron_info: dict
    ) -> List[AccessibilityIssue]:
        """Verifica que las imágenes tengan texto alternativo"""
        issues = []

        if (
            "setPixmap" in linea or "QIcon" in linea
        ) and "setAccessibleDescription" not in linea:
            issues.append(
                AccessibilityIssue(
                    modulo=modulo,
                    archivo=str(archivo.name),
                    linea=num_linea,
                    guideline=patron_info["guideline"],
                    criterio=patron_info["criterio"],
                    nivel=patron_info["nivel"],
                    severidad="high",
                    descripcion=patron_info["descripcion"],
                    solucion_recomendada=patron_info["solucion"],
                    codigo=linea.strip(),
                    element_type="image",
                )
            )

        return issues

    def _verificar_labels(
        self, linea: str, num_linea: int, archivo: Path, modulo: str, patron_info: dict
    ) -> List[AccessibilityIssue]:
        """Verifica que los campos de entrada tengan etiquetas"""
        issues = []

        widgets_entrada = [
            "QLineEdit",
            "QTextEdit",
            "QComboBox",
            "QSpinBox",
            "QDateEdit",
        ]

        if any(widget in linea for widget in widgets_entrada):
            if "setAccessibleName" not in linea:
                issues.append(
                    AccessibilityIssue(
                        modulo=modulo,
                        archivo=str(archivo.name),
                        linea=num_linea,
                        guideline=patron_info["guideline"],
                        criterio=patron_info["criterio"],
                        nivel=patron_info["nivel"],
                        severidad="high",
                        descripcion=patron_info["descripcion"],
                        solucion_recomendada=patron_info["solucion"],
                        codigo=linea.strip(),
                        element_type="input",
                    )
                )

        return issues

    def _verificar_contraste(
        self, linea: str, num_linea: int, archivo: Path, modulo: str, patron_info: dict
    ) -> List[AccessibilityIssue]:
        """Verifica posibles problemas de contraste"""
        issues = []

        # Buscar colores que podrían tener bajo contraste
        colores_problematicos = ["#999999", "#CCCCCC", "#DDDDDD", "#888888"]

        for color in colores_problematicos:
            if color.lower() in linea.lower():
                issues.append(
                    AccessibilityIssue(
                        modulo=modulo,
                        archivo=str(archivo.name),
                        linea=num_linea,
                        guideline=patron_info["guideline"],
                        criterio=patron_info["criterio"],
                        nivel=patron_info["nivel"],
                        severidad="medium",
                        descripcion=f"Color con posible bajo contraste: {color}",
                        solucion_recomendada="Verificar contraste mínimo 4.5:1 para texto normal, 3:1 para texto grande",
                        codigo=linea.strip(),
                        element_type="color",
                    )
                )

        return issues

    def _verificar_navegacion_teclado(
        self, linea: str, num_linea: int, archivo: Path, modulo: str, patron_info: dict
    ) -> List[AccessibilityIssue]:
        """Verifica navegación por teclado"""
        issues = []

        if "setFocusPolicy(Qt.NoFocus)" in linea:
            # Verificar si es realmente necesario deshabilitar el foco
            issues.append(
                AccessibilityIssue(
                    modulo=modulo,
                    archivo=str(archivo.name),
                    linea=num_linea,
                    guideline=patron_info["guideline"],
                    criterio=patron_info["criterio"],
                    nivel=patron_info["nivel"],
                    severidad="high",
                    descripcion="Elemento interactivo sin acceso por teclado",
                    solucion_recomendada="Usar Qt.TabFocus o Qt.StrongFocus para elementos interactivos",
                    codigo=linea.strip(),
                    element_type="focus",
                )
            )

        return issues

    def _verificar_etiquetas_descriptivas(
        self, linea: str, num_linea: int, archivo: Path, modulo: str, patron_info: dict
    ) -> List[AccessibilityIssue]:
        """Verifica que las etiquetas sean descriptivas"""
        issues = []

        # Buscar etiquetas poco descriptivas
        etiquetas_vagas = ["OK", "Cancelar", "Botón", "Campo", "Texto", "Item"]

        for etiqueta in etiquetas_vagas:
            if f'"{etiqueta}"' in linea or f"'{etiqueta}'" in linea:
                issues.append(
                    AccessibilityIssue(
                        modulo=modulo,
                        archivo=str(archivo.name),
                        linea=num_linea,
                        guideline=patron_info["guideline"],
                        criterio=patron_info["criterio"],
                        nivel=patron_info["nivel"],
                        severidad="medium",
                        descripcion=f"Etiqueta poco descriptiva: '{etiqueta}'",
                        solucion_recomendada="Usar etiquetas específicas que describan claramente la función",
                        codigo=linea.strip(),
                        element_type="label",
                    )
                )

        return issues

    def _verificar_roles_accesibles(
        self, linea: str, num_linea: int, archivo: Path, modulo: str, patron_info: dict
    ) -> List[AccessibilityIssue]:
        """Verifica que los elementos tengan roles accesibles"""
        issues = []

        botones = ["QPushButton", "QToolButton"]

        if any(boton in linea for boton in botones):
            if "setAccessibleName" not in linea:
                issues.append(
                    AccessibilityIssue(
                        modulo=modulo,
                        archivo=str(archivo.name),
                        linea=num_linea,
                        guideline=patron_info["guideline"],
                        criterio=patron_info["criterio"],
                        nivel=patron_info["nivel"],
                        severidad="high",
                        descripcion="Botón sin nombre accesible",
                        solucion_recomendada="Agregar setAccessibleName() con descripción clara de la acción",
                        codigo=linea.strip(),
                        element_type="button",
                    )
                )

        return issues

    def _verificar_estructura_accesible(
        self, linea: str, num_linea: int, archivo: Path, modulo: str, contenido: str
    ) -> List[AccessibilityIssue]:
        """Verifica estructura general accesible"""
        issues = []

        # Verificar si hay shortcuts de teclado definidos
        if "QPushButton" in linea and "&" not in contenido:
            # Solo reportar una vez por archivo
            if not hasattr(self, "_shortcuts_reported"):
                self._shortcuts_reported = set()

            if archivo not in self._shortcuts_reported:
                issues.append(
                    AccessibilityIssue(
                        modulo=modulo,
                        archivo=str(archivo.name),
                        linea=num_linea,
                        guideline=WCAGGuideline.OPERABLE,
                        criterio="2.1.1",
                        nivel=WCAGLevel.A,
                        severidad="medium",
                        descripcion="No se encontraron atajos de teclado definidos",
                        solucion_recomendada="Agregar atajos de teclado (&) para elementos principales",
                        codigo="",
                        element_type="keyboard_shortcut",
                    )
                )
                self._shortcuts_reported.add(archivo)

        return issues

    def ejecutar_auditoria(self) -> AccessibilityReport:
        """Ejecuta la auditoría completa de accesibilidad"""
        print("[ACCESSIBILITY] Iniciando auditoría de accesibilidad WCAG 2.1...")

        # Encontrar todos los módulos
        modulos = [
            d
            for d in self.views_path.iterdir()
            if d.is_dir() and not d.name.startswith("__")
        ]

        for modulo_path in modulos:
            print(f"  [INFO] Analizando módulo: {modulo_path.name}")
            issues = self.analizar_modulo(modulo_path)
            self.report.issues.extend(issues)
            self.report.modulos_analizados.append(modulo_path.name)

        # Generar estadísticas
        self._generar_estadisticas()
        self._calcular_score_accesibilidad()
        self._determinar_nivel_conformidad()
        self._generar_recomendaciones_prioritarias()

        print(
            f"[SUCCESS] Auditoría de accesibilidad completada. {len(self.report.issues)} issues encontrados."
        )
        return self.report

    def _generar_estadisticas(self):
        """Genera estadísticas del reporte"""
        # Por nivel WCAG
        niveles = {}
        for issue in self.report.issues:
            niveles[issue.nivel.value] = niveles.get(issue.nivel.value, 0) + 1

        # Por directriz WCAG
        directrices = {}
        for issue in self.report.issues:
            directrices[issue.guideline.value] = (
                directrices.get(issue.guideline.value, 0) + 1
            )

        # Por severidad
        severidades = {}
        for issue in self.report.issues:
            severidades[issue.severidad] = severidades.get(issue.severidad, 0) + 1

        # Por módulo
        modulos = {}
        for issue in self.report.issues:
            modulos[issue.modulo] = modulos.get(issue.modulo, 0) + 1

        self.report.estadisticas = {
            "total_issues": len(self.report.issues),
            "modulos_analizados": len(self.report.modulos_analizados),
            "por_nivel_wcag": niveles,
            "por_directriz": directrices,
            "por_severidad": severidades,
            "por_modulo": modulos,
        }

    def _calcular_score_accesibilidad(self):
        """Calcula score de accesibilidad (0-100)"""
        total_checks = (
            len(self.report.modulos_analizados) * 50
        )  # Estimación de checks por módulo

        # Peso por severidad
        peso_severidad = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        peso_total = sum(
            peso_severidad.get(issue.severidad, 1) for issue in self.report.issues
        )

        if total_checks > 0:
            # Score basado en proporción de issues ponderados
            score = max(0, 100 - (peso_total / total_checks * 100))
            self.report.score_accesibilidad = round(score, 2)
        else:
            self.report.score_accesibilidad = 100.0

    def _determinar_nivel_conformidad(self):
        """Determina el nivel de conformidad WCAG alcanzado"""
        issues_por_nivel = {}
        for issue in self.report.issues:
            nivel = issue.nivel.value
            if nivel not in issues_por_nivel:
                issues_por_nivel[nivel] = 0
            issues_por_nivel[nivel] += 1

        # Si hay issues críticos en nivel A, no se cumple ningún nivel
        if issues_por_nivel.get("A", 0) > 0:
            # Verificar si son críticos
            issues_criticos_a = [
                i
                for i in self.report.issues
                if i.nivel == WCAGLevel.A and i.severidad in ["critical", "high"]
            ]
            if issues_criticos_a:
                self.report.nivel_conformidad = None
                return

        # Determinar el nivel más alto alcanzado
        if issues_por_nivel.get("AAA", 0) == 0:
            self.report.nivel_conformidad = WCAGLevel.AAA
        elif issues_por_nivel.get("AA", 0) == 0:
            self.report.nivel_conformidad = WCAGLevel.AA
        elif issues_por_nivel.get("A", 0) == 0:
            self.report.nivel_conformidad = WCAGLevel.A
        else:
            self.report.nivel_conformidad = None

    def _generar_recomendaciones_prioritarias(self):
        """Genera recomendaciones prioritarias basadas en los issues"""
        recomendaciones = []

        # Issues críticos de nivel A
        issues_criticos_a = [
            i
            for i in self.report.issues
            if i.nivel == WCAGLevel.A and i.severidad in ["critical", "high"]
        ]

        if issues_criticos_a:
            recomendaciones.append(
                f"🚨 CRÍTICO: Resolver {len(issues_criticos_a)} issues de nivel A para cumplir accesibilidad básica"
            )

        # Accesibilidad de teclado
        issues_teclado = [
            i
            for i in self.report.issues
            if i.element_type in ["focus", "keyboard_shortcut"]
        ]
        if issues_teclado:
            recomendaciones.append(
                "⌨️ Mejorar navegación por teclado en todos los elementos interactivos"
            )

        # Etiquetas y roles
        issues_etiquetas = [
            i
            for i in self.report.issues
            if i.element_type in ["label", "input", "button"]
        ]
        if issues_etiquetas:
            recomendaciones.append(
                "🏷️ Agregar etiquetas descriptivas y nombres accesibles a todos los elementos"
            )

        # Contraste de colores
        issues_contraste = [i for i in self.report.issues if i.element_type == "color"]
        if issues_contraste:
            recomendaciones.append(
                "🎨 Verificar y corregir contraste de colores para cumplir WCAG AA (4.5:1)"
            )

        # Imágenes
        issues_imagenes = [i for i in self.report.issues if i.element_type == "image"]
        if issues_imagenes:
            recomendaciones.append(
                "🖼️ Agregar texto alternativo a todas las imágenes informativas"
            )

        self.report.recomendaciones_prioritarias = recomendaciones

    def guardar_reporte(self, archivo: str | None = None):
        """Guarda el reporte en formato JSON"""
        if not archivo:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archivo = f"accessibility_audit_report_{timestamp}.json"

        reporte_path = self.root_path / "logs" / archivo
        reporte_path.parent.mkdir(exist_ok=True)

        # Convertir dataclasses a dict
        reporte_dict = {
            "timestamp": self.report.timestamp,
            "modulos_analizados": self.report.modulos_analizados,
            "estadisticas": self.report.estadisticas,
            "score_accesibilidad": self.report.score_accesibilidad,
            "nivel_conformidad": self.report.nivel_conformidad.value
            if self.report.nivel_conformidad
            else None,
            "recomendaciones_prioritarias": self.report.recomendaciones_prioritarias,
            "issues": [
                {
                    "modulo": issue.modulo,
                    "archivo": issue.archivo,
                    "linea": issue.linea,
                    "guideline": issue.guideline.value,
                    "criterio": issue.criterio,
                    "nivel": issue.nivel.value,
                    "severidad": issue.severidad,
                    "descripcion": issue.descripcion,
                    "solucion_recomendada": issue.solucion_recomendada,
                    "codigo": issue.codigo,
                    "element_type": issue.element_type,
                }
                for issue in self.report.issues
            ],
        }

        with open(reporte_path, "w", encoding="utf-8") as f:
            json.dump(reporte_dict, f, indent=2, ensure_ascii=False)

        print(f"📄 Reporte guardado en: {reporte_path}")
        return reporte_path


def main():
    """Función principal"""
    auditor = AccessibilityAuditor()
    reporte = auditor.ejecutar_auditoria()

    # Mostrar resumen
    print("\n" + "=" * 60)
    print("♿ RESUMEN DE AUDITORÍA DE ACCESIBILIDAD")
    print("=" * 60)
    print(f"📋 Módulos analizados: {reporte.estadisticas['modulos_analizados']}")
    print(f"🔍 Total de issues: {reporte.estadisticas['total_issues']}")
    print(f"📊 Score de accesibilidad: {reporte.score_accesibilidad}/100")

    if reporte.nivel_conformidad:
        print(f"🏆 Nivel WCAG alcanzado: {reporte.nivel_conformidad.value}")
    else:
        print("❌ No cumple nivel WCAG mínimo (A)")

    if reporte.estadisticas["por_nivel_wcag"]:
        print("\n📈 Issues por nivel WCAG:")
        for nivel, count in reporte.estadisticas["por_nivel_wcag"].items():
            print(f"  • Nivel {nivel}: {count}")

    if reporte.estadisticas["por_directriz"]:
        print("\n📋 Issues por directriz:")
        directrices_nombres = {
            "1_perceivable": "Perceptible",
            "2_operable": "Operable",
            "3_understandable": "Comprensible",
            "4_robust": "Robusto",
        }
        for directriz, count in reporte.estadisticas["por_directriz"].items():
            nombre = directrices_nombres.get(directriz, directriz)
            print(f"  • {nombre}: {count}")

    if reporte.recomendaciones_prioritarias:
        print("\n🎯 Recomendaciones prioritarias:")
        for rec in reporte.recomendaciones_prioritarias:
            print(f"  {rec}")

    # Guardar reporte
    archivo_reporte = auditor.guardar_reporte()

    print("\n[SUCCESS] Auditoría de accesibilidad completada exitosamente")
    print(f"📄 Reporte detallado: {archivo_reporte}")


if __name__ == "__main__":
    main()
