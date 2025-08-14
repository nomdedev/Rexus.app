# Test Quality Audit Tool
# Herramienta para auditar la calidad de tests

import ast
import os
import re
from pathlib import Path
from typing import Dict, List, Tuple


class TestQualityAuditor:
    """Auditor de calidad para tests de Rexus.app"""

    def __init__(self, tests_dir: str = "tests"):
        self.tests_dir = Path(tests_dir)
        self.quality_report = {
            "total_files": 0,
            "passed_audit": 0,
            "failed_audit": 0,
            "issues": [],
            "recommendations": []
        }

    def audit_test_file(self, file_path: Path) -> Dict:
        """Audita un archivo de test individual."""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            return {
                "file": str(file_path),
                "valid": False,
                "errors": [f"Syntax Error: {e}"],
                "score": 0
            }

        audit_result = {
            "file": str(file_path),
            "valid": True,
            "errors": [],
            "warnings": [],
            "score": 0,
            "details": {}
        }

        # Auditorías específicas
        self._audit_naming_convention(file_path, audit_result)
        self._audit_docstrings(tree, audit_result)
        self._audit_test_structure(tree, audit_result)
        self._audit_assertions(tree, content, audit_result)
        self._audit_fixtures_usage(content, audit_result)
        self._audit_imports(tree, audit_result)

        # Calcular score final
        audit_result["score"] = self._calculate_score(audit_result)

        return audit_result

    def _audit_naming_convention(self, file_path: Path, result: Dict):
        """Audita convenciones de nomenclatura."""
        filename = file_path.name

        # Verificar que el archivo empiece con 'test_'
        if not filename.startswith('test_'):
            result["errors"].append("El archivo debe comenzar con 'test_'")

        # Verificar que use snake_case
        if not re.match(r'^test_[a-z0-9_]+\.py$', filename):
            result["warnings"].append("El nombre debe usar snake_case")

    def _audit_docstrings(self, tree: ast.AST, result: Dict):
        """Audita documentación de tests."""
        functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        test_functions = [f for f in functions if f.name.startswith('test_')]

        documented_tests = 0
        for func in test_functions:
            if ast.get_docstring(func):
                documented_tests += 1

        if test_functions:
            doc_ratio = documented_tests / len(test_functions)
            result["details"]["documentation_ratio"] = doc_ratio

            if doc_ratio < 0.8:
                result["warnings"].append(f"Solo {doc_ratio:.1%} de tests están documentados")

    def _audit_test_structure(self, tree: ast.AST, result: Dict):
        """Audita estructura AAA (Arrange-Act-Assert)."""
        functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        test_functions = [f for f in functions if f.name.startswith('test_')]

        structured_tests = 0
        for func in test_functions:
            # Buscar comentarios AAA en el código
            func_source = ast.get_source_segment(open(result["file"]).read(), func) or ""
            if any(pattern in func_source.lower() for pattern in ["arrange", "act", "assert", "given", "when", "then"]):
                structured_tests += 1

        if test_functions:
            structure_ratio = structured_tests / len(test_functions)
            result["details"]["structure_ratio"] = structure_ratio

            if structure_ratio < 0.5:
                result["warnings"].append("Pocos tests siguen estructura AAA clara")

    def _audit_assertions(self, tree: ast.AST, content: str, result: Dict):
        """Audita uso de assertions."""
        functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        test_functions = [f for f in functions if f.name.startswith('test_')]

        tests_with_assertions = 0
        weak_assertions = 0

        for func in test_functions:
            has_assertion = False
            weak_assertion = False

            for node in ast.walk(func):
                if isinstance(node, ast.Assert):
                    has_assertion = True
                    # Detectar assertions débiles como assert True
                    if isinstance(node.test, ast.Constant) and \
                        node.test.value is True:
                        weak_assertion = True

            if has_assertion:
                tests_with_assertions += 1
            if weak_assertion:
                weak_assertions += 1

        if test_functions:
            assertion_ratio = tests_with_assertions / len(test_functions)
            result["details"]["assertion_ratio"] = assertion_ratio

            if assertion_ratio < 1.0:
                result["errors"].append("Algunos tests no tienen assertions")

            if weak_assertions > 0:
                result["warnings"].append(f"{weak_assertions} tests tienen assertions débiles")

    def _audit_fixtures_usage(self, content: str, result: Dict):
        """Audita uso de fixtures."""
        # Buscar patterns de fixtures
        if "@pytest.fixture" in content:
            result["details"]["uses_fixtures"] = True
        else:
            result["warnings"].append("No usa fixtures de pytest")

        # Detectar setup/teardown manual
        if "setUp" in content or "tearDown" in content:
            result["warnings"].append("Usa setUp/tearDown en lugar de fixtures")

    def _audit_imports(self, tree: ast.AST, result: Dict):
        """Audita imports y dependencias."""
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend([alias.name for alias in node.names])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)

        # Verificar imports esenciales
        if "pytest" not in imports:
            result["warnings"].append("No importa pytest")

        # Detectar imports problemáticos
        problematic = ["time.sleep", "random", "datetime.now"]
        for imp in imports:
            if any(prob in imp for prob in problematic):
                result["warnings"].append(f"Import problemático: {imp}")

    def _calculate_score(self, result: Dict) -> int:
        """Calcula score de calidad (0-100)."""
        score = 100

        # Penalizar errores críticos
        score -= len(result["errors"]) * 20

        # Penalizar warnings
        score -= len(result["warnings"]) * 5

        # Bonificar buenas prácticas
        details = result["details"]
        if details.get("documentation_ratio", 0) > 0.8:
            score += 10
        if details.get("assertion_ratio", 0) == 1.0:
            score += 10
        if details.get("uses_fixtures", False):
            score += 5

        return max(0, min(100, score))

    def audit_all_tests(self) -> Dict:
        """Audita todos los archivos de test."""
        test_files = list(self.tests_dir.rglob("test_*.py"))

        results = []
        total_score = 0

        for test_file in test_files:
            result = self.audit_test_file(test_file)
            results.append(result)
            total_score += result["score"]

        if test_files:
            average_score = total_score / len(test_files)
        else:
            average_score = 0

        return {
            "summary": {
                "total_files": len(test_files),
                "average_score": average_score,
                "files_above_80": len([r for r in results if r["score"] >= 80]),
                "files_below_50": len([r for r in results if r["score"] < 50])
            },
            "results": results
        }

    def generate_report(self, output_file: str = "test_quality_report.md"):
        """Genera reporte de calidad."""
        audit_results = self.audit_all_tests()

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# Test Quality Audit Report\n\n")

            # Summary
            summary = audit_results["summary"]
            f.write(f"## 📊 Resumen\n\n")
            f.write(f"- **Total de archivos**: {summary['total_files']}\n")
            f.write(f"- **Score promedio**: {summary['average_score']:.1f}/100\n")
            f.write(f"- **Archivos con score ≥80**: {summary['files_above_80']}\n")
            f.write(f"- **Archivos con score <50**: {summary['files_below_50']}\n\n")

            # Individual results
            f.write("## 📋 Resultados Individuales\n\n")

            for result in sorted(audit_results["results"], key=lambda x: x["score"], reverse=True):
                status = "✅" if result["score"] >= 80 else "⚠️" if result["score"] >= 50 else "❌"
                f.write(f"### {status} {result['file']} - Score: {result['score']}/100\n\n")

                if result["errors"]:
                    f.write("**Errores:**\n")
                    for error in result["errors"]:
                        f.write(f"- ❌ {error}\n")
                    f.write("\n")

                if result["warnings"]:
                    f.write("**Advertencias:**\n")
                    for warning in result["warnings"]:
                        f.write(f"- ⚠️ {warning}\n")
                    f.write("\n")

                f.write("---\n\n")


if __name__ == "__main__":
    auditor = TestQualityAuditor()
    auditor.generate_report()
    print("✅ Reporte de calidad generado: test_quality_report.md")
