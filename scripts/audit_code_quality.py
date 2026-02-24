#!/usr/bin/env python3
"""
Script de auditoría de calidad de código para Rexus.app
Analiza múltiples métricas de calidad y genera reportes detallados
"""

import os
import re
import ast
import json
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime
from typing import Dict, List, Any, Tuple
import hashlib


class CodeAnalyzer:
    """Analizador de código Python"""

    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.issues = defaultdict(list)
        self.metrics = defaultdict(dict)
        self.file_metrics = {}

    def analyze_all(self) -> Dict[str, Any]:
        """Ejecuta todos los análisis"""
        print("[*] Iniciando auditoria de codigo...")

        python_files = list(self.root_path.rglob("*.py"))
        print(f"[*] Encontrados {len(python_files)} archivos Python")

        results = {
            "timestamp": datetime.now().isoformat(),
            "total_files": len(python_files),
            "total_lines": 0,
            "files_analyzed": 0,
            "metrics": {},
            "top_issues": {},
            "duplicates": [],
            "documentation_coverage": {},
            "complexity": {},
            "naming_issues": {},
            "architecture": {},
            "recommendations": []
        }

        # Análisis por archivo
        for file_path in python_files:
            try:
                file_analysis = self.analyze_file(file_path)
                if file_analysis:
                    self.file_metrics[str(file_path)] = file_analysis
                    results["files_analyzed"] += 1
                    results["total_lines"] += file_analysis.get("lines", 0)
            except Exception as e:
                self.issues["analysis_errors"].append({
                    "file": str(file_path),
                    "error": str(e)
                })

        # Calcular métricas globales
        results["metrics"] = self.calculate_global_metrics()
        results["top_issues"] = self.get_top_issues()
        results["duplicates"] = self.find_duplicates()
        results["documentation_coverage"] = self.analyze_documentation()
        results["complexity"] = self.analyze_complexity()
        results["naming_issues"] = self.analyze_naming()
        results["architecture"] = self.analyze_architecture()
        results["recommendations"] = self.generate_recommendations()

        return results

    def analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """Analiza un archivo individual"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
        except Exception as e:
            return None

        analysis = {
            "path": str(file_path),
            "lines": len(lines),
            "functions": [],
            "classes": [],
            "imports": [],
            "docstrings": 0,
            "comments": 0,
            "blank_lines": 0,
            "complexity": 0,
            "issues": []
        }

        # Contar líneas en blanco y comentarios
        for line in lines:
            stripped = line.strip()
            if not stripped:
                analysis["blank_lines"] += 1
            elif stripped.startswith('#'):
                analysis["comments"] += 1

        # Análisis AST
        try:
            tree = ast.parse(content, filename=str(file_path))
            analyzer = ASTAnalyzer()
            analyzer.visit(tree)

            analysis["functions"] = analyzer.functions
            analysis["classes"] = analyzer.classes
            analysis["imports"] = analyzer.imports
            analysis["docstrings"] = analyzer.docstrings
            analysis["complexity"] = analyzer.total_complexity

            # Detectar problemas específicos
            analysis["issues"] = self.detect_file_issues(analysis, content)

        except SyntaxError as e:
            analysis["issues"].append({
                "type": "syntax_error",
                "message": f"Error de sintaxis: {e}",
                "severity": "critical"
            })

        return analysis

    def detect_file_issues(self, analysis: Dict, content: str) -> List[Dict]:
        """Detecta issues en un archivo"""
        issues = []

        # Funciones muy largas (>50 líneas)
        for func in analysis["functions"]:
            if func["length"] > 50:
                issues.append({
                    "type": "long_function",
                    "name": func["name"],
                    "length": func["length"],
                    "message": f"Función {func['name']} es muy larga ({func['length']} líneas)",
                    "severity": "medium"
                })

        # Clases muy largas (>300 líneas)
        for cls in analysis["classes"]:
            if cls["length"] > 300:
                issues.append({
                    "type": "long_class",
                    "name": cls["name"],
                    "length": cls["length"],
                    "message": f"Clase {cls['name']} es muy larga ({cls['length']} líneas)",
                    "severity": "high"
                })

        # Alta complejidad ciclomática
        for func in analysis["functions"]:
            if func["complexity"] > 10:
                issues.append({
                    "type": "high_complexity",
                    "name": func["name"],
                    "complexity": func["complexity"],
                    "message": f"Función {func['name']} tiene alta complejidad ({func['complexity']})",
                    "severity": "high" if func["complexity"] > 15 else "medium"
                })

        # Falta de documentación
        has_module_docstring = analysis.get("has_module_docstring", False)
        if not has_module_docstring and len(analysis["functions"]) + len(analysis["classes"]) > 0:
            issues.append({
                "type": "missing_module_docstring",
                "message": "Archivo sin docstring de módulo",
                "severity": "low"
            })

        # Imports no utilizados
        for imp in analysis["imports"]:
            if not self.is_import_used(imp, content):
                issues.append({
                    "type": "unused_import",
                    "name": imp,
                    "message": f"Import no utilizado: {imp}",
                    "severity": "low"
                })

        return issues

    def is_import_used(self, import_name: str, content: str) -> bool:
        """Verifica si un import se utiliza en el código"""
        # Extraer el nombre base del import
        base_name = import_name.split('.')[-1]
        base_name = base_name.split(' as ')[-1].strip()

        # Buscar uso en el código (excluyendo la línea del import)
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if not line.strip().startswith('import'):
                if base_name in line:
                    return True
        return False

    def calculate_global_metrics(self) -> Dict[str, Any]:
        """Calcula métricas globales del proyecto"""
        total_functions = sum(len(m.get("functions", [])) for m in self.file_metrics.values())
        total_classes = sum(len(m.get("classes", [])) for m in self.file_metrics.values())
        total_docstrings = sum(m.get("docstrings", 0) for m in self.file_metrics.values())
        total_complexity = sum(m.get("complexity", 0) for m in self.file_metrics.values())
        total_lines = sum(m.get("lines", 0) for m in self.file_metrics.values())
        total_comments = sum(m.get("comments", 0) for m in self.file_metrics.values())

        avg_function_length = []
        for m in self.file_metrics.values():
            for func in m.get("functions", []):
                avg_function_length.append(func["length"])

        return {
            "total_functions": total_functions,
            "total_classes": total_classes,
            "total_docstrings": total_docstrings,
            "docstring_coverage": round(total_docstrings / max(total_functions + total_classes, 1) * 100, 2),
            "average_complexity": round(total_complexity / max(total_functions, 1), 2),
            "total_lines_of_code": total_lines,
            "total_comments": total_comments,
            "comment_ratio": round(total_comments / max(total_lines, 1) * 100, 2),
            "average_function_length": round(sum(avg_function_length) / max(len(avg_function_length), 1), 2),
            "files_with_issues": sum(1 for m in self.file_metrics.values() if m.get("issues"))
        }

    def get_top_issues(self) -> Dict[str, List[Dict]]:
        """Obtiene los top 10 archivos con más problemas"""
        file_scores = []

        for path, metrics in self.file_metrics.items():
            score = 0
            issues_summary = defaultdict(int)

            for issue in metrics.get("issues", []):
                severity_weight = {"critical": 10, "high": 5, "medium": 2, "low": 1}
                score += severity_weight.get(issue["severity"], 1)
                issues_summary[issue["type"]] += 1

            if score > 0:
                file_scores.append({
                    "path": path,
                    "score": score,
                    "issues_count": len(metrics.get("issues", [])),
                    "issues_by_type": dict(issues_summary),
                    "complexity": metrics.get("complexity", 0),
                    "lines": metrics.get("lines", 0)
                })

        # Ordenar por score descendente
        file_scores.sort(key=lambda x: x["score"], reverse=True)

        return {
            "top_10_problematic_files": file_scores[:10],
            "total_files_with_issues": len(file_scores)
        }

    def find_duplicates(self) -> List[Dict]:
        """Encuentra código duplicado"""
        duplicates = []
        code_blocks = {}

        for path, metrics in self.file_metrics.items():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()

                # Buscar bloques de 5+ líneas duplicadas
                for i in range(len(lines) - 5):
                    block = ''.join(lines[i:i+5])
                    block_hash = hashlib.md5(block.encode()).hexdigest()

                    if block_hash in code_blocks:
                        duplicates.append({
                            "original": code_blocks[block_hash],
                            "duplicate": str(path),
                            "start_line": i + 1,
                            "block_preview": block[:100].strip()
                        })
                    else:
                        code_blocks[block_hash] = str(path)

            except Exception:
                pass

        return duplicates[:20]  # Limitar a 20 resultados

    def analyze_documentation(self) -> Dict[str, Any]:
        """Analiza la cobertura de documentación"""
        documented_funcs = 0
        total_funcs = 0
        documented_classes = 0
        total_classes = 0

        for metrics in self.file_metrics.values():
            for func in metrics.get("functions", []):
                total_funcs += 1
                if func.get("has_docstring"):
                    documented_funcs += 1

            for cls in metrics.get("classes", []):
                total_classes += 1
                if cls.get("has_docstring"):
                    documented_classes += 1

        return {
            "function_coverage": round(documented_funcs / max(total_funcs, 1) * 100, 2),
            "class_coverage": round(documented_classes / max(total_classes, 1) * 100, 2),
            "total_functions": total_funcs,
            "documented_functions": documented_funcs,
            "total_classes": total_classes,
            "documented_classes": documented_classes,
            "files_missing_docstrings": [
                path for path, m in self.file_metrics.items()
                if not m.get("has_module_docstring")
            ][:20]
        }

    def analyze_complexity(self) -> Dict[str, Any]:
        """Analiza complejidad del código"""
        high_complexity_funcs = []
        very_high_complexity_funcs = []

        for path, metrics in self.file_metrics.items():
            for func in metrics.get("functions", []):
                if func["complexity"] > 15:
                    very_high_complexity_funcs.append({
                        "function": func["name"],
                        "file": path,
                        "complexity": func["complexity"]
                    })
                elif func["complexity"] > 10:
                    high_complexity_funcs.append({
                        "function": func["name"],
                        "file": path,
                        "complexity": func["complexity"]
                    })

        return {
            "very_high_complexity": very_high_complexity_funcs[:10],
            "high_complexity": high_complexity_funcs[:20],
            "total_high_complexity": len(high_complexity_funcs) + len(very_high_complexity_funcs)
        }

    def analyze_naming(self) -> Dict[str, List[Dict]]:
        """Analiza convenciones de naming"""
        issues = []

        naming_patterns = {
            "class": r'^[A-Z][a-zA-Z0-9]*$',
            "function": r'^[a-z_][a-z0-9_]*$',
            "variable": r'^[a-z_][a-z0-9_]*$'
        }

        for path, metrics in self.file_metrics.items():
            for cls in metrics.get("classes", []):
                if not re.match(naming_patterns["class"], cls["name"]):
                    issues.append({
                        "type": "class_naming",
                        "name": cls["name"],
                        "file": path,
                        "suggestion": "ClassNames should use PascalCase"
                    })

            for func in metrics.get("functions", []):
                if not re.match(naming_patterns["function"], func["name"]):
                    issues.append({
                        "type": "function_naming",
                        "name": func["name"],
                        "file": path,
                        "suggestion": "function_names should use snake_case"
                    })

        return {
            "naming_violations": issues[:30],
            "total_violations": len(issues)
        }

    def analyze_architecture(self) -> Dict[str, Any]:
        """Analiza patrones de arquitectura"""
        analysis = {
            "module_structure": {},
            "circular_imports_risk": [],
            "large_modules": [],
            "design_patterns": []
        }

        # Analizar estructura de módulos
        module_sizes = defaultdict(int)
        for path, metrics in self.file_metrics.items():
            module = str(Path(path).parent.relative_to(self.root_path))
            module_sizes[module] += metrics.get("lines", 0)

        # Identificar módulos grandes
        for module, size in sorted(module_sizes.items(), key=lambda x: x[1], reverse=True):
            if size > 1000:
                analysis["large_modules"].append({
                    "module": module,
                    "lines": size
                })

        analysis["module_structure"] = dict(module_sizes)

        return analysis

    def generate_recommendations(self) -> List[Dict[str, str]]:
        """Genera recomendaciones priorizadas"""
        recommendations = []

        metrics = self.calculate_global_metrics()

        # Documentación
        if metrics["docstring_coverage"] < 60:
            recommendations.append({
                "priority": "high",
                "category": "documentation",
                "issue": f"Baja cobertura de documentación ({metrics['docstring_coverage']}%)",
                "recommendation": "Añadir docstrings a todas las funciones y clases públicas siguiendo el estilo de Google o NumPy",
                "impact": "Mejora la mantenibilidad y facilita la colaboración"
            })

        # Complejidad
        if metrics["average_complexity"] > 5:
            recommendations.append({
                "priority": "high",
                "category": "complexity",
                "issue": f"Alta complejidad promedio ({metrics['average_complexity']})",
                "recommendation": "Refactorizar funciones complejas en funciones más pequeñas y especializadas",
                "impact": "Reduce bugs y mejora la testabilidad"
            })

        # Longitud de funciones
        avg_func_len = metrics.get("average_function_length", 0)
        if avg_func_len > 20:
            recommendations.append({
                "priority": "medium",
                "category": "function_length",
                "issue": f"Funciones demasiado largas (promedio: {avg_func_len} líneas)",
                "recommendation": "Aplicar principio de responsabilidad única, dividir funciones en <20 líneas",
                "impact": "Mejora la legibilidad y testabilidad"
            })

        # Comentarios
        if metrics["comment_ratio"] < 10:
            recommendations.append({
                "priority": "medium",
                "category": "comments",
                "issue": f"Baja proporción de comentarios ({metrics['comment_ratio']}%)",
                "recommendation": "Añadir comentarios explicativos en lógica compleja y algoritmos",
                "impact": "Facilita la comprensión del código"
            })

        # Testing
        recommendations.append({
            "priority": "high",
            "category": "testing",
            "issue": "Cobertura de pruebas no evaluada",
            "recommendation": "Implementar pytest con mínimo 70% de cobertura",
            "impact": "Previene regresiones y mejora la calidad"
        })

        # Type hints
        recommendations.append({
            "priority": "medium",
            "category": "type_safety",
            "issue": "Falta de type hints",
            "recommendation": "Añadir type hints a todas las funciones según PEP 484",
            "impact": "Mejora la documentación y permite verificación estática con mypy"
        })

        # Error handling
        recommendations.append({
            "priority": "high",
            "category": "error_handling",
            "issue": "Manejo de errores inconsistente",
            "recommendation": "Implementar manejo de errores centralizado y logging estructurado",
            "impact": "Mejora la robustez y facilita el debugging"
        })

        # Code organization
        recommendations.append({
            "priority": "medium",
            "category": "organization",
            "issue": "Posible duplicación de código",
            "recommendation": "Extraer lógica común a utilidades reutilizables",
            "impact": "Reduce la duplicación y mejora la consistencia"
        })

        return sorted(recommendations, key=lambda x: {
            "high": 3,
            "medium": 2,
            "low": 1
        }.get(x["priority"], 0), reverse=True)


class ASTAnalyzer(ast.NodeVisitor):
    """Analizador AST para extraer métricas"""

    def __init__(self):
        self.functions = []
        self.classes = []
        self.imports = []
        self.docstrings = 0
        self.total_complexity = 0
        self.current_class = None

    def visit_Module(self, node):
        if ast.get_docstring(node):
            self.docstrings += 1
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        complexity = self.calculate_complexity(node)
        func_info = {
            "name": node.name,
            "args": len(node.args.args),
            "length": 0,  # Se calculará después
            "complexity": complexity,
            "has_docstring": ast.get_docstring(node) is not None,
            "is_method": self.current_class is not None,
            "class": self.current_class
        }
        self.functions.append(func_info)
        self.total_complexity += complexity
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        self.current_class = node.name
        class_info = {
            "name": node.name,
            "methods": 0,
            "length": 0,
            "has_docstring": ast.get_docstring(node) is not None
        }

        # Contar métodos
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                class_info["methods"] += 1

        self.classes.append(class_info)
        self.generic_visit(node)
        self.current_class = None

    def visit_Import(self, node):
        for alias in node.names:
            self.imports.append(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        module = node.module if node.module else ""
        for alias in node.names:
            self.imports.append(f"{module}.{alias.name}")
        self.generic_visit(node)

    def calculate_complexity(self, node) -> int:
        """Calcula complejidad ciclomática"""
        complexity = 1  # Base complexity

        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1

        return complexity


def generate_markdown_report(results: Dict[str, Any], output_path: str):
    """Genera reporte en Markdown"""
    md = f"""# Auditoría de Calidad de Código - Rexus.app

**Fecha:** {results['timestamp']}
**Archivos analizados:** {results['files_analyzed']} / {results['total_files']}
**Líneas totales de código:** {results['total_lines']:,}

---

## 📊 Resumen Ejecutivo

### Métricas Generales

- **Funciones totales:** {results['metrics']['total_functions']:,}
- **Clases totales:** {results['metrics']['total_classes']:,}
- **Cobertura de documentación:** {results['metrics']['docstring_coverage']}%
- **Complejidad promedio:** {results['metrics']['average_complexity']}
- **Comentarios:** {results['metrics']['comment_ratio']}% del código
- **Archivos con issues:** {results['metrics']['files_with_issues']}

---

## TOP 10 ARCHIVOS CON MAS PROBLEMAS

"""

    top_files = results["top_issues"]["top_10_problematic_files"]
    for i, file_info in enumerate(top_files, 1):
        md += f"""### {i}. {file_info['path']}

- **Score de problemas:** {file_info['score']}
- **Cantidad de issues:** {file_info['issues_count']}
- **Complejidad:** {file_info['complexity']}
- **Líneas:** {file_info['lines']}

**Tipos de problemas:**
"""
        for issue_type, count in file_info['issues_by_type'].items():
            md += f"- {issue_type}: {count}\n"
        md += "\n"

    md += """---

## ANALISIS DE COMPLEJIDAD

### Funciones con Complejidad Muy Alta (>15)

"""
    for func in results["complexity"]["very_high_complexity"]:
        md += f"- **{func['function']}** ({func['complexity']}) en `{func['file']}`\n"

    md += f"""
**Total funciones de alta complejidad:** {results['complexity']['total_high_complexity']}

---

## COBERTURA DE DOCUMENTACION

- **Cobertura en funciones:** {results['documentation_coverage']['function_coverage']}%
- **Cobertura en clases:** {results['documentation_coverage']['class_coverage']}%
- **Funciones documentadas:** {results['documentation_coverage']['documented_functions']:,} / {results['documentation_coverage']['total_functions']:,}
- **Clases documentadas:** {results['documentation_coverage']['documented_classes']:,} / {results['documentation_coverage']['total_classes']:,}

---

## RECOMENDACIONES PRIORIZADAS

"""

    for i, rec in enumerate(results["recommendations"], 1):
        priority_icon = {
            "high": "[ALTA]",
            "medium": "[MEDIA]",
            "low": "[BAJA]"
        }.get(rec["priority"], "[INFO]")

        md += f"""### {priority_icon} {i}. {rec['category'].replace('_', ' ').title()} (Prioridad: {rec['priority']})

**Problema:** {rec['issue']}

**Recomendación:** {rec['recommendation']}

**Impacto:** {rec['impact']}

---

"""

    md += """---

## MODULOS MAS GRANDES

"""
    for module in results["architecture"]["large_modules"][:5]:
        md += f"- **{module['module']}:** {module['lines']:,} líneas\n"

    md += """

---

## CODIGO DUPLICADO

Se detectaron **{}** bloques de codigo potencialmente duplicados.

---

## PROXIMOS PASOS SUGERIDOS

1. **Atender problemas críticos** en los archivos identificados
2. **Mejorar documentación** hasta alcanzar >80% de cobertura
3. **Refactorizar funciones complejas** para reducir complejidad ciclomática
4. **Implementar testing** con mínimo 70% de cobertura
5. **Establecer linting** automático (flake8, black, mypy)
6. **Configurar pre-commit hooks** para mantener calidad
7. **Documentar arquitectura** y patrones de diseño

---

*Reporte generado automáticamente por el script de auditoría de Rexus.app*
""".format(len(results["duplicates"]))

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(md)


def main():
    """Función principal"""
    import sys
    import io

    # Configurar UTF-8 para salida en Windows
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

    rexus_path = Path(__file__).parent.parent / "rexus"

    print("=" * 60)
    print("AUDITORIA DE CALIDAD DE CODIGO - REXUS.APP")
    print("=" * 60)

    analyzer = CodeAnalyzer(str(rexus_path))
    results = analyzer.analyze_all()

    # Crear directorio de reportes
    reports_dir = Path(__file__).parent.parent / "reports"
    reports_dir.mkdir(exist_ok=True)

    # Guardar JSON
    json_path = reports_dir / f"code_quality_{datetime.now().strftime('%Y%m%d')}.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"[OK] Reporte JSON guardado: {json_path}")

    # Guardar Markdown
    md_path = reports_dir / f"code_quality_{datetime.now().strftime('%Y%m%d')}.md"
    generate_markdown_report(results, str(md_path))
    print(f"[OK] Reporte Markdown guardado: {md_path}")

    # Imprimir resumen
    print("\n" + "=" * 60)
    print("RESUMEN EJECUTIVO")
    print("=" * 60)
    print(f"Archivos analizados: {results['files_analyzed']}")
    print(f"Lineas de codigo: {results['total_lines']:,}")
    print(f"Funciones totales: {results['metrics']['total_functions']:,}")
    print(f"Clases totales: {results['metrics']['total_classes']:,}")
    print(f"\nCobertura documentacion: {results['metrics']['docstring_coverage']}%")
    print(f"Complejidad promedio: {results['metrics']['average_complexity']}")
    print(f"Archivos con problemas: {results['metrics']['files_with_issues']}")
    print(f"\n[!] Archivos mas problematicos:")
    for i, f in enumerate(results['top_issues']['top_10_problematic_files'][:5], 1):
        print(f"  {i}. {Path(f['path']).name} ({f['score']} puntos)")

    print("\n[OK] Auditoria completada")


if __name__ == "__main__":
    main()
