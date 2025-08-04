#!/usr/bin/env python3
"""
Analizador de Patrones MVC en Rexus.app
Detecta violaciones del patrón Model-View-Controller y sugiere mejoras
Parte del sistema de calidad de código de Rexus.app
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple


class MVCPatternAnalyzer:
    """Analizador de patrones MVC para detectar violaciones arquitecturales"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.modules_path = self.project_root / "rexus" / "modules"
        self.violations = []
        self.stats = {
            "modules_analyzed": 0,
            "mvc_violations": 0,
            "business_logic_in_views": 0,
            "ui_logic_in_models": 0,
            "controller_issues": 0,
        }

    def analyze_all_modules(self) -> Dict:
        """Analiza todos los módulos para detectar violaciones MVC"""
        print("🔍 ANALIZANDO PATRONES MVC EN REXUS.APP")
        print("=" * 50)

        if not self.modules_path.exists():
            print(f"❌ Directorio de módulos no encontrado: {self.modules_path}")
            return {}

        modules = [
            d
            for d in self.modules_path.iterdir()
            if d.is_dir() and not d.name.startswith("__")
        ]

        for module_dir in modules:
            self.analyze_module(module_dir)

        self.generate_report()
        return self.get_summary()

    def analyze_module(self, module_path: Path):
        """Analiza un módulo específico para violaciones MVC"""
        module_name = module_path.name
        print(f"\n📁 Analizando módulo: {module_name}")

        self.stats["modules_analyzed"] += 1

        # Archivos esperados en un módulo MVC bien estructurado
        model_file = module_path / "model.py"
        view_file = module_path / "view.py"
        controller_file = module_path / "controller.py"

        # Analizar MODEL
        if model_file.exists():
            self.analyze_model_file(model_file, module_name)
        else:
            self.add_violation(
                "MISSING_FILE", module_name, "model.py", "Archivo model.py faltante"
            )

        # Analizar VIEW
        if view_file.exists():
            self.analyze_view_file(view_file, module_name)
        else:
            self.add_violation(
                "MISSING_FILE", module_name, "view.py", "Archivo view.py faltante"
            )

        # Analizar CONTROLLER
        if controller_file.exists():
            self.analyze_controller_file(controller_file, module_name)
        else:
            self.add_violation(
                "MISSING_FILE",
                module_name,
                "controller.py",
                "Archivo controller.py faltante",
            )

    def analyze_model_file(self, file_path: Path, module_name: str):
        """Analiza archivo model.py para detectar violaciones"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # VIOLACIÓN: Código UI en modelo (imports de PyQt)
            if self.has_ui_imports(content):
                self.add_violation(
                    "UI_IN_MODEL",
                    module_name,
                    "model.py",
                    "Modelo contiene imports de UI (PyQt6, tkinter, etc.)",
                )
                self.stats["ui_logic_in_models"] += 1

            # VIOLACIÓN: Lógica de presentación en modelo
            ui_patterns = [
                r"\.setText\(",
                r"\.setStyleSheet\(",
                r"QMessageBox",
                r"QDialog",
                r"show\(\)",
                r"hide\(\)",
                r"setWindowTitle",
            ]

            for pattern in ui_patterns:
                if re.search(pattern, content):
                    self.add_violation(
                        "PRESENTATION_IN_MODEL",
                        module_name,
                        "model.py",
                        f"Modelo contiene lógica de presentación: {pattern}",
                    )
                    self.stats["ui_logic_in_models"] += 1
                    break

            # VALIDACIÓN POSITIVA: Verificar buenas prácticas
            self.check_model_best_practices(content, module_name)

        except Exception as e:
            self.add_violation(
                "ANALYSIS_ERROR", module_name, "model.py", f"Error analizando: {e}"
            )

    def analyze_view_file(self, file_path: Path, module_name: str):
        """Analiza archivo view.py para detectar violaciones"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # VIOLACIÓN: Lógica de negocio en vista (SQL directo)
            business_patterns = [
                r"cursor\.execute",
                r"SELECT\s+",
                r"INSERT\s+INTO",
                r"UPDATE\s+",
                r"DELETE\s+FROM",
                r"\.commit\(\)",
                r"\.rollback\(\)",
            ]

            for pattern in business_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    self.add_violation(
                        "BUSINESS_LOGIC_IN_VIEW",
                        module_name,
                        "view.py",
                        f"Vista contiene lógica de negocio: {pattern}",
                    )
                    self.stats["business_logic_in_views"] += 1
                    break

            # VIOLACIÓN: Conexiones directas a base de datos
            if "db_connection" in content or "database" in content.lower():
                if not self.is_proper_model_usage(content):
                    self.add_violation(
                        "DIRECT_DB_IN_VIEW",
                        module_name,
                        "view.py",
                        "Vista accede directamente a base de datos",
                    )
                    self.stats["business_logic_in_views"] += 1

            # VIOLACIÓN: Cálculos complejos en vista
            if self.has_complex_calculations(content):
                self.add_violation(
                    "COMPLEX_CALC_IN_VIEW",
                    module_name,
                    "view.py",
                    "Vista contiene cálculos complejos que deberían estar en modelo",
                )
                self.stats["business_logic_in_views"] += 1

            # VALIDACIÓN POSITIVA: Verificar buenas prácticas
            self.check_view_best_practices(content, module_name)

        except Exception as e:
            self.add_violation(
                "ANALYSIS_ERROR", module_name, "view.py", f"Error analizando: {e}"
            )

    def analyze_controller_file(self, file_path: Path, module_name: str):
        """Analiza archivo controller.py para detectar violaciones"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # VIOLACIÓN: Controller con lógica de negocio pesada
            if self.has_heavy_business_logic(content):
                self.add_violation(
                    "HEAVY_LOGIC_IN_CONTROLLER",
                    module_name,
                    "controller.py",
                    "Controlador contiene lógica de negocio pesada",
                )
                self.stats["controller_issues"] += 1

            # VIOLACIÓN: Controller manipulando UI directamente
            if self.has_direct_ui_manipulation(content):
                self.add_violation(
                    "DIRECT_UI_IN_CONTROLLER",
                    module_name,
                    "controller.py",
                    "Controlador manipula UI directamente sin usar vista",
                )
                self.stats["controller_issues"] += 1

        except Exception as e:
            self.add_violation(
                "ANALYSIS_ERROR", module_name, "controller.py", f"Error analizando: {e}"
            )

    def has_ui_imports(self, content: str) -> bool:
        """Detecta imports de UI en archivos que no deberían tenerlos"""
        ui_imports = [
            "from PyQt6",
            "import PyQt6",
            "from tkinter",
            "import tkinter",
            "from PySide",
            "import PySide",
        ]
        return any(ui_import in content for ui_import in ui_imports)

    def is_proper_model_usage(self, content: str) -> bool:
        """Verifica si el acceso a datos se hace a través del modelo"""
        # Buscar patrones de uso correcto del modelo
        model_patterns = [
            r"self\.model\.",
            r"\.model\.",
            r"model\s*=.*Model\(",
            r"from.*model.*import",
        ]
        return any(re.search(pattern, content) for pattern in model_patterns)

    def has_complex_calculations(self, content: str) -> bool:
        """Detecta cálculos complejos que deberían estar en el modelo"""
        calc_patterns = [
            r"for.*in.*range\(.*\).*\+.*\*",  # Loops con cálculos
            r"sum\(.*for.*in.*\)",  # Comprensiones complejas
            r"math\.",  # Operaciones matemáticas
            r"decimal\.Decimal",  # Cálculos decimales
            r"statistics\.",  # Estadísticas
        ]
        return any(re.search(pattern, content) for pattern in calc_patterns)

    def has_heavy_business_logic(self, content: str) -> bool:
        """Detecta lógica de negocio pesada en controladores"""
        heavy_patterns = [
            r"class.*\{.*def.*\{.*def.*\{",  # Muchos métodos anidados
            r"def.*\(.*\):\s*.*\n.*\n.*\n.*\n.*\n.*\n.*\n.*\n.*\n.*\n",  # Métodos muy largos
        ]
        # Simplificado: verificar longitud de métodos
        methods = re.findall(r"def\s+\w+\(.*?\):(.*?)(?=def|\Z)", content, re.DOTALL)
        return any(len(method.split("\n")) > 30 for method in methods)

    def has_direct_ui_manipulation(self, content: str) -> bool:
        """Detecta manipulación directa de UI en controladores"""
        ui_patterns = [
            r"\.setText\(",
            r"\.setStyleSheet\(",
            r"\.show\(\)",
            r"\.hide\(\)",
            r"\.update\(\)",
        ]
        return any(re.search(pattern, content) for pattern in ui_patterns)

    def check_model_best_practices(self, content: str, module_name: str):
        """Verifica buenas prácticas en modelos"""
        # Verificar que tenga docstrings
        if '"""' not in content:
            self.add_violation(
                "NO_DOCSTRING",
                module_name,
                "model.py",
                "Falta documentación (docstrings) en el modelo",
            )

        # Verificar manejo de errores
        if "try:" not in content or "except" not in content:
            self.add_violation(
                "NO_ERROR_HANDLING",
                module_name,
                "model.py",
                "Falta manejo de errores en el modelo",
            )

    def check_view_best_practices(self, content: str, module_name: str):
        """Verifica buenas prácticas en vistas"""
        # Verificar separación de responsabilidades
        if "self.model" not in content and "model" not in content.lower():
            self.add_violation(
                "NO_MODEL_REFERENCE",
                module_name,
                "view.py",
                "Vista no parece referenciar ningún modelo",
            )

    def add_violation(
        self, violation_type: str, module_name: str, file_name: str, description: str
    ):
        """Agrega una violación detectada"""
        self.violations.append(
            {
                "type": violation_type,
                "module": module_name,
                "file": file_name,
                "description": description,
                "severity": self.get_severity(violation_type),
            }
        )
        self.stats["mvc_violations"] += 1

    def get_severity(self, violation_type: str) -> str:
        """Determina la severidad de una violación"""
        critical = ["BUSINESS_LOGIC_IN_VIEW", "UI_IN_MODEL", "DIRECT_DB_IN_VIEW"]
        high = ["PRESENTATION_IN_MODEL", "HEAVY_LOGIC_IN_CONTROLLER"]
        medium = ["DIRECT_UI_IN_CONTROLLER", "COMPLEX_CALC_IN_VIEW"]

        if violation_type in critical:
            return "CRÍTICO"
        elif violation_type in high:
            return "ALTO"
        elif violation_type in medium:
            return "MEDIO"
        else:
            return "BAJO"

    def generate_report(self):
        """Genera reporte detallado de violaciones MVC"""
        print("\n" + "=" * 60)
        print("📊 REPORTE DE ANÁLISIS MVC")
        print("=" * 60)

        # Estadísticas generales
        print(f"📁 Módulos analizados: {self.stats['modules_analyzed']}")
        print(f"⚠️  Total violaciones MVC: {self.stats['mvc_violations']}")
        print(
            f"🔴 Lógica de negocio en vistas: {self.stats['business_logic_in_views']}"
        )
        print(f"🔴 Lógica UI en modelos: {self.stats['ui_logic_in_models']}")
        print(f"🟡 Problemas en controladores: {self.stats['controller_issues']}")

        # Violaciones por severidad
        severities = {}
        for violation in self.violations:
            sev = violation["severity"]
            severities[sev] = severities.get(sev, 0) + 1

        print(f"\n📈 VIOLACIONES POR SEVERIDAD:")
        for severity, count in sorted(severities.items()):
            print(f"  {severity}: {count}")

        # Top violaciones
        print(f"\n🔍 VIOLACIONES CRÍTICAS DETECTADAS:")
        critical_violations = [v for v in self.violations if v["severity"] == "CRÍTICO"]

        for violation in critical_violations[:10]:  # Top 10
            print(
                f"  ❌ {violation['module']}/{violation['file']}: {violation['description']}"
            )

        if len(critical_violations) > 10:
            print(f"  ... y {len(critical_violations) - 10} más")

    def get_summary(self) -> Dict:
        """Retorna resumen del análisis"""
        return {
            "stats": self.stats,
            "violations": self.violations,
            "severity_counts": self.get_severity_counts(),
            "recommendations": self.get_recommendations(),
        }

    def get_severity_counts(self) -> Dict[str, int]:
        """Cuenta violaciones por severidad"""
        counts = {}
        for violation in self.violations:
            sev = violation["severity"]
            counts[sev] = counts.get(sev, 0) + 1
        return counts

    def get_recommendations(self) -> List[str]:
        """Genera recomendaciones basadas en violaciones encontradas"""
        recommendations = []

        if self.stats["business_logic_in_views"] > 0:
            recommendations.append(
                "🔧 Mover lógica de negocio desde vistas hacia modelos"
            )

        if self.stats["ui_logic_in_models"] > 0:
            recommendations.append("🔧 Eliminar código UI de modelos y mover a vistas")

        if self.stats["controller_issues"] > 0:
            recommendations.append(
                "🔧 Simplificar controladores y delegar responsabilidades"
            )

        recommendations.append("📚 Implementar patrón MVC más estricto")
        recommendations.append("🧪 Agregar tests unitarios por capa")

        return recommendations


def main():
    """Función principal para ejecutar análisis MVC"""
    analyzer = MVCPatternAnalyzer()
    summary = analyzer.analyze_all_modules()

    print(f"\n🎯 SIGUIENTE PASO:")
    print(f"  📋 Revisar violaciones críticas y crear plan de refactorización")
    print(f"  🔧 Implementar separación MVC más estricta")

    return summary


if __name__ == "__main__":
    main()
