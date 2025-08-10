#!/usr/bin/env python3
"""
Análisis Completo de Cobertura de Tests - Rexus.app
Evalúa la completitud de tests para todos los views y controllers con edge cases
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

# Configurar path
ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT_DIR))


class TestCoverageAnalyzer:
    """Analizador de cobertura de tests para views y controllers."""

    def __init__(self):
        self.root_dir = ROOT_DIR
        self.tests_dir = self.root_dir / "tests"
        self.modules_dir = self.root_dir / "rexus" / "modules"
        self.analysis_results = {}

    def get_module_structure(self) -> Dict[str, Dict[str, bool]]:
        """Obtiene la estructura de módulos existentes."""
        modules = {}

        for module_dir in self.modules_dir.iterdir():
            if module_dir.is_dir() and not module_dir.name.startswith("."):
                module_name = module_dir.name
                modules[module_name] = {
                    "has_view": (module_dir / "view.py").exists(),
                    "has_controller": (module_dir / "controller.py").exists(),
                    "has_model": (module_dir / "model.py").exists(),
                }

        return modules

    def get_existing_tests(self) -> Dict[str, Dict[str, List[str]]]:
        """Obtiene todos los tests existentes organizados por módulo."""
        tests = {}

        for test_dir in self.tests_dir.iterdir():
            if test_dir.is_dir() and not test_dir.name.startswith("."):
                module_name = test_dir.name
                tests[module_name] = {
                    "controller_tests": [],
                    "view_tests": [],
                    "model_tests": [],
                    "edge_case_tests": [],
                    "integration_tests": [],
                }

                # Buscar archivos de test en el directorio del módulo
                for test_file in test_dir.glob("*.py"):
                    test_name = test_file.name

                    if "controller" in test_name.lower():
                        tests[module_name]["controller_tests"].append(test_name)
                    elif "view" in test_name.lower():
                        tests[module_name]["view_tests"].append(test_name)
                    elif "model" in test_name.lower():
                        tests[module_name]["model_tests"].append(test_name)
                    elif "edge" in test_name.lower():
                        tests[module_name]["edge_case_tests"].append(test_name)
                    elif (
                        "integration" in test_name.lower()
                        or "integracion" in test_name.lower()
                    ):
                        tests[module_name]["integration_tests"].append(test_name)

        return tests

    def analyze_test_file_quality(self, test_file_path: Path) -> Dict[str, object]:
        """Analiza la calidad de un archivo de test específico."""
        if not test_file_path.exists():
            return {"exists": False}

        try:
            content = test_file_path.read_text(encoding="utf-8")

            # Contar diferentes tipos de tests
            test_functions = content.count("def test_")
            edge_case_tests = len(
                [
                    line
                    for line in content.split("\n")
                    if "edge" in line.lower()
                    or "boundary" in line.lower()
                    or "extreme" in line.lower()
                ]
            )
            mock_usage = content.count("Mock(") + content.count("@patch")
            fixture_usage = content.count("@pytest.fixture")

            # Buscar patrones de edge cases específicos
            security_tests = any(
                term in content.lower()
                for term in ["sql injection", "xss", "csrf", "auth"]
            )
            boundary_tests = any(
                term in content.lower()
                for term in ["boundary", "limit", "extreme", "maximum", "minimum"]
            )
            error_handling = any(
                term in content.lower()
                for term in ["exception", "error", "try:", "except"]
            )
            concurrency_tests = any(
                term in content.lower()
                for term in ["thread", "concurrent", "async", "race"]
            )

            return {
                "exists": True,
                "test_functions": test_functions,
                "edge_case_indicators": edge_case_tests,
                "mock_usage": mock_usage,
                "fixture_usage": fixture_usage,
                "has_security_tests": security_tests,
                "has_boundary_tests": boundary_tests,
                "has_error_handling": error_handling,
                "has_concurrency_tests": concurrency_tests,
                "file_size": len(content),
                "lines_count": len(content.split("\n")),
            }

        except Exception as e:
            return {"exists": True, "error": str(e)}

    def identify_missing_tests(self) -> Dict[str, List[str]]:
        """Identifica tests faltantes o incompletos."""
        modules = self.get_module_structure()
        tests = self.get_existing_tests()
        missing_tests = {}

        for module_name, module_info in modules.items():
            missing_tests[module_name] = []

            # Verificar si existen tests para cada componente
            if module_info["has_controller"] and module_name not in tests:
                missing_tests[module_name].append(
                    "Tests de controller completamente faltantes"
                )
            elif module_info["has_controller"] and not tests.get(module_name, {}).get(
                "controller_tests"
            ):
                missing_tests[module_name].append("Tests de controller faltantes")

            if module_info["has_view"] and module_name not in tests:
                missing_tests[module_name].append(
                    "Tests de view completamente faltantes"
                )
            elif module_info["has_view"] and not tests.get(module_name, {}).get(
                "view_tests"
            ):
                missing_tests[module_name].append("Tests de view faltantes")

            # Verificar edge cases
            if module_name in tests:
                if not tests[module_name]["edge_case_tests"]:
                    missing_tests[module_name].append("Tests de edge cases faltantes")
                if not tests[module_name]["integration_tests"]:
                    missing_tests[module_name].append("Tests de integración faltantes")

        return missing_tests

    def analyze_test_completeness(self) -> Dict[str, Dict]:
        """Análisis completo de la completitud de tests."""
        modules = self.get_module_structure()
        tests = self.get_existing_tests()
        missing = self.identify_missing_tests()

        analysis = {}

        for module_name, module_info in modules.items():
            analysis[module_name] = {
                "module_info": module_info,
                "test_coverage": {},
                "quality_metrics": {},
                "missing_tests": missing.get(module_name, []),
                "recommendations": [],
            }

            # Analizar tests existentes
            if module_name in tests:
                test_info = tests[module_name]

                # Analizar controller tests
                if test_info["controller_tests"]:
                    controller_test_file = (
                        self.tests_dir / module_name / test_info["controller_tests"][0]
                    )
                    analysis[module_name]["quality_metrics"]["controller"] = (
                        self.analyze_test_file_quality(controller_test_file)
                    )
                else:
                    analysis[module_name]["quality_metrics"]["controller"] = {
                        "exists": False
                    }

                # Analizar view tests
                if test_info["view_tests"]:
                    view_test_file = (
                        self.tests_dir / module_name / test_info["view_tests"][0]
                    )
                    analysis[module_name]["quality_metrics"]["view"] = (
                        self.analyze_test_file_quality(view_test_file)
                    )
                else:
                    analysis[module_name]["quality_metrics"]["view"] = {"exists": False}

                # Calcular cobertura
                analysis[module_name]["test_coverage"] = {
                    "has_controller_tests": len(test_info["controller_tests"]) > 0,
                    "has_view_tests": len(test_info["view_tests"]) > 0,
                    "has_edge_cases": len(test_info["edge_case_tests"]) > 0,
                    "has_integration": len(test_info["integration_tests"]) > 0,
                    "controller_tests_count": len(test_info["controller_tests"]),
                    "view_tests_count": len(test_info["view_tests"]),
                    "edge_case_tests_count": len(test_info["edge_case_tests"]),
                }
            else:
                analysis[module_name]["test_coverage"] = {
                    "has_controller_tests": False,
                    "has_view_tests": False,
                    "has_edge_cases": False,
                    "has_integration": False,
                    "controller_tests_count": 0,
                    "view_tests_count": 0,
                    "edge_case_tests_count": 0,
                }
                analysis[module_name]["quality_metrics"] = {
                    "controller": {"exists": False},
                    "view": {"exists": False},
                }

            # Generar recomendaciones
            self.generate_recommendations(analysis[module_name])

        return analysis

    def generate_recommendations(self, module_analysis: Dict):
        """Genera recomendaciones para mejorar la cobertura de tests."""
        recommendations = []

        # Verificar controller tests
        controller_quality = module_analysis["quality_metrics"].get("controller", {})
        if not controller_quality.get("exists", False):
            recommendations.append("[ERROR] CRÍTICO: Crear tests básicos para controller")
        elif controller_quality.get("test_functions", 0) < 5:
            recommendations.append(
                "[WARN] MEJORAR: Aumentar cobertura de tests de controller (actual: {} tests)".format(
                    controller_quality.get("test_functions", 0)
                )
            )

        # Verificar view tests
        view_quality = module_analysis["quality_metrics"].get("view", {})
        if not view_quality.get("exists", False):
            recommendations.append("[ERROR] CRÍTICO: Crear tests básicos para view")
        elif view_quality.get("test_functions", 0) < 5:
            recommendations.append(
                "[WARN] MEJORAR: Aumentar cobertura de tests de view (actual: {} tests)".format(
                    view_quality.get("test_functions", 0)
                )
            )

        # Verificar edge cases
        if not module_analysis["test_coverage"]["has_edge_cases"]:
            recommendations.append("[ERROR] CRÍTICO: Implementar tests de edge cases")

        # Verificar calidad de tests
        for component in ["controller", "view"]:
            quality = module_analysis["quality_metrics"].get(component, {})
            if quality.get("exists", False):
                if not quality.get("has_security_tests", False):
                    recommendations.append(
                        f"[LOCK] SEGURIDAD: Agregar tests de seguridad para {component}"
                    )
                if not quality.get("has_boundary_tests", False):
                    recommendations.append(
                        f"📏 LÍMITES: Agregar tests de valores límite para {component}"
                    )
                if not quality.get("has_error_handling", False):
                    recommendations.append(
                        f"🚨 ERRORES: Agregar tests de manejo de errores para {component}"
                    )
                if quality.get("mock_usage", 0) < 3:
                    recommendations.append(
                        f"🎭 MOCKS: Mejorar uso de mocks en tests de {component}"
                    )

        module_analysis["recommendations"] = recommendations

    def generate_report(self) -> str:
        """Genera reporte completo de análisis."""
        analysis = self.analyze_test_completeness()

        report = []
        report.append("=" * 80)
        report.append("ANÁLISIS COMPLETO DE COBERTURA DE TESTS - REXUS.APP")
        report.append("=" * 80)
        report.append(
            f"Fecha: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        report.append("")

        # Resumen general
        total_modules = len(analysis)
        modules_with_controller_tests = sum(
            1 for m in analysis.values() if m["test_coverage"]["has_controller_tests"]
        )
        modules_with_view_tests = sum(
            1 for m in analysis.values() if m["test_coverage"]["has_view_tests"]
        )
        modules_with_edge_cases = sum(
            1 for m in analysis.values() if m["test_coverage"]["has_edge_cases"]
        )

        report.append("[CHART] RESUMEN GENERAL:")
        report.append(f"   • Total de módulos: {total_modules}")
        report.append(
            f"   • Módulos con tests de controller: {modules_with_controller_tests}/{total_modules} ({modules_with_controller_tests / total_modules * 100:.1f}%)"
        )
        report.append(
            f"   • Módulos con tests de view: {modules_with_view_tests}/{total_modules} ({modules_with_view_tests / total_modules * 100:.1f}%)"
        )
        report.append(
            f"   • Módulos con edge cases: {modules_with_edge_cases}/{total_modules} ({modules_with_edge_cases / total_modules * 100:.1f}%)"
        )
        report.append("")

        # Análisis por módulo
        report.append("📋 ANÁLISIS DETALLADO POR MÓDULO:")
        report.append("-" * 80)

        for module_name, module_data in sorted(analysis.items()):
            report.append(f"\n🏗️ MÓDULO: {module_name.upper()}")

            # Estado del módulo
            module_info = module_data["module_info"]
            report.append(
                f"   📁 Componentes: View: {'[CHECK]' if module_info['has_view'] else '[ERROR]'} | "
                f"Controller: {'[CHECK]' if module_info['has_controller'] else '[ERROR]'} | "
                f"Model: {'[CHECK]' if module_info['has_model'] else '[ERROR]'}"
            )

            # Cobertura de tests
            coverage = module_data["test_coverage"]
            report.append(
                f"   🧪 Tests: Controller: {'[CHECK]' if coverage['has_controller_tests'] else '[ERROR]'} "
                f"({coverage['controller_tests_count']}) | "
                f"View: {'[CHECK]' if coverage['has_view_tests'] else '[ERROR]'} "
                f"({coverage['view_tests_count']}) | "
                f"Edge Cases: {'[CHECK]' if coverage['has_edge_cases'] else '[ERROR]'} "
                f"({coverage['edge_case_tests_count']})"
            )

            # Calidad de tests
            quality = module_data["quality_metrics"]
            if quality.get("controller", {}).get("exists", False):
                ctrl_metrics = quality["controller"]
                report.append(
                    f"   [CHART] Controller Tests: {ctrl_metrics.get('test_functions', 0)} funciones | "
                    f"Security: {'[CHECK]' if ctrl_metrics.get('has_security_tests') else '[ERROR]'} | "
                    f"Boundaries: {'[CHECK]' if ctrl_metrics.get('has_boundary_tests') else '[ERROR]'} | "
                    f"Errors: {'[CHECK]' if ctrl_metrics.get('has_error_handling') else '[ERROR]'}"
                )

            if quality.get("view", {}).get("exists", False):
                view_metrics = quality["view"]
                report.append(
                    f"   [CHART] View Tests: {view_metrics.get('test_functions', 0)} funciones | "
                    f"Security: {'[CHECK]' if view_metrics.get('has_security_tests') else '[ERROR]'} | "
                    f"Boundaries: {'[CHECK]' if view_metrics.get('has_boundary_tests') else '[ERROR]'} | "
                    f"Errors: {'[CHECK]' if view_metrics.get('has_error_handling') else '[ERROR]'}"
                )

            # Recomendaciones
            recommendations = module_data["recommendations"]
            if recommendations:
                report.append("   💡 RECOMENDACIONES:")
                for rec in recommendations:
                    report.append(f"      {rec}")
            else:
                report.append("   [CHECK] COMPLETO: Tests adecuados implementados")

        # Módulos críticos que necesitan atención
        critical_modules = []
        for module_name, module_data in analysis.items():
            if (
                module_data["module_info"]["has_controller"]
                and not module_data["test_coverage"]["has_controller_tests"]
            ):
                critical_modules.append(f"{module_name} (controller)")
            if (
                module_data["module_info"]["has_view"]
                and not module_data["test_coverage"]["has_view_tests"]
            ):
                critical_modules.append(f"{module_name} (view)")

        if critical_modules:
            report.append("\n🚨 MÓDULOS QUE REQUIEREN ATENCIÓN INMEDIATA:")
            report.append("-" * 50)
            for module in critical_modules:
                report.append(f"   [ERROR] {module}")

        # Prioridades de implementación
        report.append("\n📋 PLAN DE IMPLEMENTACIÓN RECOMENDADO:")
        report.append("-" * 50)

        priority_1 = [
            name
            for name, data in analysis.items()
            if not data["test_coverage"]["has_controller_tests"]
            and data["module_info"]["has_controller"]
        ]
        priority_2 = [
            name
            for name, data in analysis.items()
            if not data["test_coverage"]["has_view_tests"]
            and data["module_info"]["has_view"]
        ]
        priority_3 = [
            name
            for name, data in analysis.items()
            if not data["test_coverage"]["has_edge_cases"]
        ]

        if priority_1:
            report.append("🔴 PRIORIDAD 1 - Tests de Controller:")
            for module in priority_1:
                report.append(f"   • {module}")

        if priority_2:
            report.append("🟡 PRIORIDAD 2 - Tests de View:")
            for module in priority_2:
                report.append(f"   • {module}")

        if priority_3:
            report.append("🟠 PRIORIDAD 3 - Edge Cases:")
            for module in priority_3:
                report.append(f"   • {module}")

        report.append("\n" + "=" * 80)

        return "\n".join(report)

    def save_detailed_analysis(self, filename: str = "test_coverage_analysis.json"):
        """Guarda análisis detallado en JSON."""
        analysis = self.analyze_test_completeness()

        # Convertir a formato serializable
        serializable_analysis = {}
        for module_name, data in analysis.items():
            serializable_analysis[module_name] = {
                "module_info": data["module_info"],
                "test_coverage": data["test_coverage"],
                "quality_metrics": data["quality_metrics"],
                "missing_tests": data["missing_tests"],
                "recommendations": data["recommendations"],
            }

        output_file = self.root_dir / filename
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(serializable_analysis, f, indent=2, ensure_ascii=False)

        return output_file


def main():
    """Función principal."""
    print("Iniciando análisis de cobertura de tests...")

    analyzer = TestCoverageAnalyzer()

    # Generar reporte
    report = analyzer.generate_report()
    print(report)

    # Guardar análisis detallado
    json_file = analyzer.save_detailed_analysis()
    print(f"\n📄 Análisis detallado guardado en: {json_file}")

    # Guardar reporte en archivo
    report_file = analyzer.root_dir / "REPORTE_COBERTURA_TESTS.md"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"📄 Reporte guardado en: {report_file}")


if __name__ == "__main__":
    main()
