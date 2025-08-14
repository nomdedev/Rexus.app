#!/usr/bin/env python3
"""
Auditoría de Consistencia UI/UX para Rexus.app
Revisa estandarización visual, accesibilidad y experiencia de usuario
"""

import json
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


@dataclass
class UIIssue:
    """Representa un problema de UI/UX detectado"""

    modulo: str
    archivo: str
    linea: int
    tipo: str  # color, font, spacing, accessibility, etc.
    severidad: str  # critical, high, medium, low
    descripcion: str
    sugerencia: str
    codigo: str = ""


@dataclass
class UIAuditReport:
    """Reporte completo de auditoría UI/UX"""

    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    issues: List[UIIssue] = field(default_factory=list)
    modulos_analizados: List[str] = field(default_factory=list)
    estadisticas: Dict[str, Any] = field(default_factory=dict)
    recomendaciones: List[str] = field(default_factory=list)


class UIConsistencyAuditor:
    """Auditor de consistencia UI/UX"""

    def __init__(self):
        self.root_path = Path(__file__).parent.parent.parent
        self.views_path = self.root_path / "rexus" / "modules"
        self.static_path = self.root_path / "static"
        self.report = UIAuditReport()

        # Patrones de problemas comunes
        self.ui_patterns = {
            "colores_inconsistentes": [
                r'setStyleSheet\(["\'].*background-color:\s*#([0-9A-Fa-f]{6})',
                r'setStyleSheet\(["\'].*color:\s*#([0-9A-Fa-f]{6})',
                r"QColor\((\d+),\s*(\d+),\s*(\d+)\)",
            ],
            "fuentes_inconsistentes": [
                r'setFont\(.*QFont\(["\']([^"\']*)["\']',
                r'font-family:\s*["\']?([^"\';\n]*)',
                r"font-size:\s*(\d+)px",
            ],
            "espaciado_inconsistente": [
                r"setContentsMargins\((\d+),\s*(\d+),\s*(\d+),\s*(\d+)\)",
                r"setSpacing\((\d+)\)",
                r"margin:\s*(\d+)px",
                r"padding:\s*(\d+)px",
            ],
            "accesibilidad": [
                r'setToolTip\(["\']([^"\']*)["\']',
                r'setAccessibleName\(["\']([^"\']*)["\']',
                r'setWhatsThis\(["\']([^"\']*)["\']',
            ],
        }

        # Estándares definidos
        self.ui_standards = {
            "colores_primarios": ["#2E7D32", "#388E3C", "#4CAF50"],  # Verdes
            "colores_secundarios": ["#1976D2", "#2196F3", "#64B5F6"],  # Azules
            "colores_alertas": [
                "#F44336",
                "#FF9800",
                "#FFC107",
            ],  # Rojo, Naranja, Amarillo
            "fuente_principal": "Arial",
            "fuente_monospace": "Courier New",
            "tamaños_fuente": [8, 9, 10, 11, 12, 14, 16, 18, 20],
            "espaciado_estandar": [5, 10, 15, 20, 25, 30],
            "margenes_estandar": [5, 10, 15, 20],
        }

    def analizar_modulo(self, modulo_path: Path) -> List[UIIssue]:
        """Analiza un módulo específico para problemas UI/UX"""
        issues = []

        # Buscar archivos view.py
        view_files = list(modulo_path.glob("**/view.py"))

        for view_file in view_files:
            modulo_name = modulo_path.name
            issues.extend(self._analizar_archivo_view(view_file, modulo_name))

        return issues

    def _analizar_archivo_view(self, archivo: Path, modulo: str) -> List[UIIssue]:
        """Analiza un archivo view.py específico"""
        issues = []

        try:
            with open(archivo, "r", encoding="utf-8") as f:
                contenido = f.read()
                lineas = contenido.split("\n")

            # Buscar patrones problemáticos
            for i, linea in enumerate(lineas, 1):
                issues.extend(self._verificar_colores(linea,
i,
                    archivo,
                    modulo))
                issues.extend(self._verificar_fuentes(linea,
i,
                    archivo,
                    modulo))
                issues.extend(self._verificar_espaciado(linea,
i,
                    archivo,
                    modulo))
                issues.extend(self._verificar_accesibilidad(linea,
i,
                    archivo,
                    modulo))
                issues.extend(
                    self._verificar_textos_hardcoded(linea,
i,
                        archivo,
                        modulo)
                )

        except Exception as e:
            issues.append(
                UIIssue(
                    modulo=modulo,
                    archivo=str(archivo),
                    linea=0,
                    tipo="error",
                    severidad="high",
                    descripcion=f"Error al analizar archivo: {e}",
                    sugerencia="Verificar sintaxis y encoding del archivo",
                )
            )

        return issues

    def _verificar_colores(
        self, linea: str, num_linea: int, archivo: Path, modulo: str
    ) -> List[UIIssue]:
        """Verifica consistencia de colores"""
        issues = []

        # Buscar colores hexadecimales
        color_hex_pattern = r"#([0-9A-Fa-f]{6})"
        colores_encontrados = re.findall(color_hex_pattern, linea)

        for color in colores_encontrados:
            color_completo = f"#{color.upper()}"
            if not self._es_color_estandar(color_completo):
                issues.append(
                    UIIssue(
                        modulo=modulo,
                        archivo=str(archivo.name),
                        linea=num_linea,
                        tipo="color_inconsistente",
                        severidad="medium",
                        descripcion=f"Color no estándar encontrado: {color_completo}",
                        sugerencia="Usar colores del sistema de diseño definido",
                        codigo=linea.strip(),
                    )
                )

        # Buscar QColor con valores RGB
        qcolor_pattern = r"QColor\((\d+),\s*(\d+),\s*(\d+)\)"
        qcolors = re.findall(qcolor_pattern, linea)

        for r, g, b in qcolors:
            if not self._es_qcolor_estandar(int(r), int(g), int(b)):
                issues.append(
                    UIIssue(
                        modulo=modulo,
                        archivo=str(archivo.name),
                        linea=num_linea,
                        tipo="qcolor_inconsistente",
                        severidad="medium",
                        descripcion=f"QColor no estándar: QColor({r}, {g}, {b})",
                        sugerencia="Usar colores predefinidos del sistema",
                        codigo=linea.strip(),
                    )
                )

        return issues

    def _verificar_fuentes(
        self, linea: str, num_linea: int, archivo: Path, modulo: str
    ) -> List[UIIssue]:
        """Verifica consistencia de fuentes"""
        issues = []

        # Buscar definiciones de fuente
        font_pattern = r'QFont\(["\']([^"\']*)["\'](?:,\s*(\d+))?'
        fuentes_encontradas = re.findall(font_pattern, linea)

        for fuente, tamaño in fuentes_encontradas:
            if fuente and fuente not in [
                self.ui_standards["fuente_principal"],
                self.ui_standards["fuente_monospace"],
            ]:
                issues.append(
                    UIIssue(
                        modulo=modulo,
                        archivo=str(archivo.name),
                        linea=num_linea,
                        tipo="fuente_inconsistente",
                        severidad="low",
                        descripcion=f"Fuente no estándar: {fuente}",
                        sugerencia=f"Usar {self.ui_standards['fuente_principal']} o {self.ui_standards['fuente_monospace']}",
                        codigo=linea.strip(),
                    )
                )

            if tamaño and \
                int(tamaño) not in self.ui_standards["tamaños_fuente"]:
                issues.append(
                    UIIssue(
                        modulo=modulo,
                        archivo=str(archivo.name),
                        linea=num_linea,
                        tipo="tamaño_fuente_inconsistente",
                        severidad="low",
                        descripcion=f"Tamaño de fuente no estándar: {tamaño}px",
                        sugerencia=f"Usar tamaños estándar: {self.ui_standards['tamaños_fuente']}",
                        codigo=linea.strip(),
                    )
                )

        return issues

    def _verificar_espaciado(
        self, linea: str, num_linea: int, archivo: Path, modulo: str
    ) -> List[UIIssue]:
        """Verifica consistencia de espaciado"""
        issues = []

        # Buscar setContentsMargins
        margins_pattern = r"setContentsMargins\((\d+),\s*(\d+),\s*(\d+),\s*(\d+)\)"
        margenes = re.findall(margins_pattern, linea)

        for top, left, bottom, right in margenes:
            valores = [int(top), int(left), int(bottom), int(right)]
            for valor in valores:
                if valor not in self.ui_standards["margenes_estandar"] and \
                    valor != 0:
                    issues.append(
                        UIIssue(
                            modulo=modulo,
                            archivo=str(archivo.name),
                            linea=num_linea,
                            tipo="margen_inconsistente",
                            severidad="low",
                            descripcion=f"Margen no estándar: {valor}px",
                            sugerencia=f"Usar valores estándar: {self.ui_standards['margenes_estandar']}",
                            codigo=linea.strip(),
                        )
                    )
                    break

        # Buscar setSpacing
        spacing_pattern = r"setSpacing\((\d+)\)"
        espaciados = re.findall(spacing_pattern, linea)

        for espaciado in espaciados:
            if (
                int(espaciado) not in self.ui_standards["espaciado_estandar"]
                and int(espaciado) != 0
            ):
                issues.append(
                    UIIssue(
                        modulo=modulo,
                        archivo=str(archivo.name),
                        linea=num_linea,
                        tipo="espaciado_inconsistente",
                        severidad="low",
                        descripcion=f"Espaciado no estándar: {espaciado}px",
                        sugerencia=f"Usar valores estándar: {self.ui_standards['espaciado_estandar']}",
                        codigo=linea.strip(),
                    )
                )

        return issues

    def _verificar_accesibilidad(
        self, linea: str, num_linea: int, archivo: Path, modulo: str
    ) -> List[UIIssue]:
        """Verifica elementos de accesibilidad"""
        issues = []

        # Verificar si hay botones sin tooltip
        if "QPushButton" in linea and "setToolTip" not in linea:
            if any(keyword in linea for keyword in ["Button", "btn_", "button"]):
                issues.append(
                    UIIssue(
                        modulo=modulo,
                        archivo=str(archivo.name),
                        linea=num_linea,
                        tipo="accesibilidad_tooltip",
                        severidad="medium",
                        descripcion="Botón sin tooltip para accesibilidad",
                        sugerencia="Agregar setToolTip() para mejorar accesibilidad",
                        codigo=linea.strip(),
                    )
                )

        # Verificar campos de entrada sin etiquetas claras
        if any(widget in linea for widget in ["QLineEdit", "QTextEdit", "QComboBox"]):
            if "setAccessibleName" not in linea:
                issues.append(
                    UIIssue(
                        modulo=modulo,
                        archivo=str(archivo.name),
                        linea=num_linea,
                        tipo="accesibilidad_label",
                        severidad="medium",
                        descripcion="Campo de entrada sin nombre accesible",
                        sugerencia="Agregar setAccessibleName() para lectores de pantalla",
                        codigo=linea.strip(),
                    )
                )

        return issues

    def _verificar_textos_hardcoded(
        self, linea: str, num_linea: int, archivo: Path, modulo: str
    ) -> List[UIIssue]:
        """Verifica textos hardcoded que deberían estar externalizados"""
        issues = []

        # Buscar textos hardcoded en español
        texto_patterns = [
            r'setText\(["\']([^"\']*)["\']',
            r'setTitle\(["\']([^"\']*)["\']',
            r'setWindowTitle\(["\']([^"\']*)["\']',
        ]

        for pattern in texto_patterns:
            textos = re.findall(pattern, linea)
            for texto in textos:
                if (
                    len(texto) > 5
                    and any(char in texto for char in "aeiouáéíóúñ")
                    and not texto.startswith("&")  # No es shortcut
                    and texto not in ["OK", "Cancel", "Save", "Delete"]
                ):  # No es texto genérico
                    issues.append(
                        UIIssue(
                            modulo=modulo,
                            archivo=str(archivo.name),
                            linea=num_linea,
                            tipo="texto_hardcoded",
                            severidad="low",
                            descripcion=f"Texto hardcoded encontrado: '{texto}'",
                            sugerencia="Externalizar a archivo de recursos o constantes",
                            codigo=linea.strip(),
                        )
                    )

        return issues

    def _es_color_estandar(self, color: str) -> bool:
        """Verifica si un color está en los estándares"""
        todos_colores = (
            self.ui_standards["colores_primarios"]
            + self.ui_standards["colores_secundarios"]
            + self.ui_standards["colores_alertas"]
        )
        return color in todos_colores

    def _es_qcolor_estandar(self, r: int, g: int, b: int) -> bool:
        """Verifica si un QColor está en los estándares"""
        # Convertir RGB a hex
        hex_color = f"#{r:02X}{g:02X}{b:02X}"
        return self._es_color_estandar(hex_color)

    def ejecutar_auditoria(self) -> UIAuditReport:
        """Ejecuta la auditoría completa"""
        print("[AUDIT] Iniciando auditoría de consistencia UI/UX...")

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
        self._generar_recomendaciones()

        print(
            f"[SUCCESS] Auditoría completada. {len(self.report.issues)} issues encontrados."
        )
        return self.report

    def _generar_estadisticas(self):
        """Genera estadísticas del reporte"""
        total_issues = len(self.report.issues)

        # Por severidad
        severidades = {}
        for issue in self.report.issues:
            severidades[issue.severidad] = severidades.get(issue.severidad, 0) + 1

        # Por tipo
        tipos = {}
        for issue in self.report.issues:
            tipos[issue.tipo] = tipos.get(issue.tipo, 0) + 1

        # Por módulo
        modulos = {}
        for issue in self.report.issues:
            modulos[issue.modulo] = modulos.get(issue.modulo, 0) + 1

        self.report.estadisticas = {
            "total_issues": total_issues,
            "modulos_analizados": len(self.report.modulos_analizados),
            "por_severidad": severidades,
            "por_tipo": tipos,
            "por_modulo": modulos,
        }

    def _generar_recomendaciones(self):
        """Genera recomendaciones basadas en los issues encontrados"""
        recomendaciones = []

        if any(issue.tipo.startswith("color") for issue in self.report.issues):
            recomendaciones.append(
                "📎 Crear un sistema de colores centralizado (theme.py) para mantener consistencia"
            )

        if any(issue.tipo.startswith("fuente") for issue in self.report.issues):
            recomendaciones.append(
                "🔤 Implementar un sistema de tipografía estándar con clases reutilizables"
            )

        if any(issue.tipo.startswith("accesibilidad") for issue in self.report.issues):
            recomendaciones.append(
                "♿ Mejorar accesibilidad agregando tooltips y nombres accesibles a todos los elementos interactivos"
            )

        if any(issue.tipo == "texto_hardcoded" for issue in self.report.issues):
            recomendaciones.append(
                "🌐 Externalizar textos a archivos de recursos para facilitar internacionalización"
            )

        if any(issue.tipo.endswith("inconsistente") for issue in self.report.issues):
            recomendaciones.append(
                "📏 Establecer guías de estilo UI/UX documentadas para el equipo de desarrollo"
            )

        self.report.recomendaciones = recomendaciones

    def guardar_reporte(self, archivo: str | None = None):
        """Guarda el reporte en formato JSON"""
        if not archivo:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archivo = f"ui_audit_report_{timestamp}.json"

        reporte_path = self.root_path / "logs" / archivo
        reporte_path.parent.mkdir(exist_ok=True)

        # Convertir dataclasses a dict
        reporte_dict = {
            "timestamp": self.report.timestamp,
            "modulos_analizados": self.report.modulos_analizados,
            "estadisticas": self.report.estadisticas,
            "recomendaciones": self.report.recomendaciones,
            "issues": [
                {
                    "modulo": issue.modulo,
                    "archivo": issue.archivo,
                    "linea": issue.linea,
                    "tipo": issue.tipo,
                    "severidad": issue.severidad,
                    "descripcion": issue.descripcion,
                    "sugerencia": issue.sugerencia,
                    "codigo": issue.codigo,
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
    auditor = UIConsistencyAuditor()
    reporte = auditor.ejecutar_auditoria()

    # Mostrar resumen
    print("\n" + "=" * 60)
    print("[CHART] RESUMEN DE AUDITORÍA UI/UX")
    print("=" * 60)
    print(f"📋 Módulos analizados: {reporte.estadisticas['modulos_analizados']}")
    print(f"🔍 Total de issues: {reporte.estadisticas['total_issues']}")

    if reporte.estadisticas["por_severidad"]:
        print("\n📈 Por severidad:")
        for severidad, count in reporte.estadisticas["por_severidad"].items():
            print(f"  • {severidad}: {count}")

    if reporte.estadisticas["por_tipo"]:
        print("\n📋 Por tipo:")
        for tipo, count in sorted(reporte.estadisticas["por_tipo"].items()):
            print(f"  • {tipo}: {count}")

    if reporte.recomendaciones:
        print("\n💡 Recomendaciones principales:")
        for rec in reporte.recomendaciones:
            print(f"  {rec}")

    # Guardar reporte
    archivo_reporte = auditor.guardar_reporte()

    print("\n[CHECK] Auditoría UI/UX completada exitosamente")
    print(f"📄 Reporte detallado: {archivo_reporte}")


if __name__ == "__main__":
    main()
