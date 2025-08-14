#!/usr/bin/env python3
"""
Analizador Simple de Patrones MVC en Rexus.app
Detecta violaciones del patron Model-View-Controller
"""

import re
from pathlib import Path


def analyze_mvc_violations():
    """Analiza violaciones MVC en los modulos de Rexus"""
    print("ANALIZANDO PATRONES MVC EN REXUS.APP")
    print("=" * 50)

    project_root = Path(__file__).parent.parent.parent
    modules_path = project_root / "rexus" / "modules"

    violations = []
    stats = {
        "modules_analyzed": 0,
        "critical_violations": 0,
        "business_logic_in_views": 0,
        "ui_logic_in_models": 0,
    }

    if not modules_path.exists():
        print(f"ERROR: Directorio de modulos no encontrado: {modules_path}")
        return

    modules = [
        d for d in modules_path.iterdir() if d.is_dir() and \
            not d.name.startswith("__")
    ]

    for module_dir in modules:
        module_name = module_dir.name
        print(f"\nAnalizando modulo: {module_name}")
        stats["modules_analyzed"] += 1

        # Analizar VIEW
        view_file = module_dir / "view.py"
        if view_file.exists():
            view_violations = analyze_view_file(view_file, module_name)
            violations.extend(view_violations)
            stats["business_logic_in_views"] += len(
                [v for v in view_violations if "BUSINESS" in v["type"]]
            )

        # Analizar MODEL
        model_file = module_dir / "model.py"
        if model_file.exists():
            model_violations = analyze_model_file(model_file, module_name)
            violations.extend(model_violations)
            stats["ui_logic_in_models"] += len(
                [v for v in model_violations if "UI" in v["type"]]
            )

    # Contar violaciones criticas
    stats["critical_violations"] = len(
        [v for v in violations if v["severity"] == "CRITICO"]
    )

    # Generar reporte
    print("\n" + "=" * 60)
    print("REPORTE DE ANALISIS MVC")
    print("=" * 60)
    print(f"Modulos analizados: {stats['modules_analyzed']}")
    print(f"Violaciones criticas: {stats['critical_violations']}")
    print(f"Logica de negocio en vistas: {stats['business_logic_in_views']}")
    print(f"Logica UI en modelos: {stats['ui_logic_in_models']}")

    print("\nVIOLACIONES CRITICAS DETECTADAS:")
    critical_violations = [v for v in violations if v["severity"] == "CRITICO"]

    for violation in critical_violations:
        print(
            f"  - {violation['module']}/{violation['file']}: {violation['description']}"
        )

    if len(critical_violations) == 0:
        print("  Ninguna violacion critica detectada!")

    return violations, stats


def analyze_view_file(file_path, module_name):
    """Analiza archivo view.py para detectar violaciones"""
    violations = []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # VIOLACION CRITICA: SQL directo en vista
        sql_patterns = [
            r"cursor\.execute",
            r"SELECT\s+",
            r"INSERT\s+INTO",
            r"UPDATE\s+",
            r"DELETE\s+FROM",
        ]

        for pattern in sql_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                violations.append(
                    {
                        "type": "BUSINESS_LOGIC_IN_VIEW",
                        "module": module_name,
                        "file": "view.py",
                        "description": f"Vista contiene SQL directo: {pattern}",
                        "severity": "CRITICO",
                    }
                )
                break

        # VIOLACION CRITICA: Conexion directa a BD
        if "db_connection" in content and not has_proper_model_usage(content):
            violations.append(
                {
                    "type": "DIRECT_DB_IN_VIEW",
                    "module": module_name,
                    "file": "view.py",
                    "description": "Vista accede directamente a base de datos",
                    "severity": "CRITICO",
                }
            )

        # VIOLACION MEDIA: Calculos complejos
        if has_complex_calculations(content):
            violations.append(
                {
                    "type": "COMPLEX_CALC_IN_VIEW",
                    "module": module_name,
                    "file": "view.py",
                    "description": "Vista contiene calculos complejos",
                    "severity": "MEDIO",
                }
            )

    except Exception as e:
        violations.append(
            {
                "type": "ANALYSIS_ERROR",
                "module": module_name,
                "file": "view.py",
                "description": f"Error analizando: {e}",
                "severity": "BAJO",
            }
        )

    return violations


def analyze_model_file(file_path, module_name):
    """Analiza archivo model.py para detectar violaciones"""
    violations = []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # VIOLACION CRITICA: Imports de UI en modelo
        if has_ui_imports(content):
            violations.append(
                {
                    "type": "UI_IMPORTS_IN_MODEL",
                    "module": module_name,
                    "file": "model.py",
                    "description": "Modelo contiene imports de UI (PyQt6, etc.)",
                    "severity": "CRITICO",
                }
            )

        # VIOLACION ALTA: Logica de presentacion en modelo
        ui_patterns = [
            r"\.setText\(",
            r"\.setStyleSheet\(",
            r"QMessageBox",
            r"show\(\)",
            r"hide\(\)",
        ]

        for pattern in ui_patterns:
            if re.search(pattern, content):
                violations.append(
                    {
                        "type": "PRESENTATION_IN_MODEL",
                        "module": module_name,
                        "file": "model.py",
                        "description": f"Modelo contiene logica de presentacion: {pattern}",
                        "severity": "ALTO",
                    }
                )
                break

        # VIOLACION BAJA: Falta documentacion
        if '"""' not in content:
            violations.append(
                {
                    "type": "NO_DOCSTRING",
                    "module": module_name,
                    "file": "model.py",
                    "description": "Falta documentacion en el modelo",
                    "severity": "BAJO",
                }
            )

    except Exception as e:
        violations.append(
            {
                "type": "ANALYSIS_ERROR",
                "module": module_name,
                "file": "model.py",
                "description": f"Error analizando: {e}",
                "severity": "BAJO",
            }
        )

    return violations


def has_ui_imports(content):
    """Detecta imports de UI"""
    ui_imports = ["from PyQt6", "import PyQt6", "from tkinter", "import tkinter"]
    return any(ui_import in content for ui_import in ui_imports)


def has_proper_model_usage(content):
    """Verifica uso correcto del modelo"""
    model_patterns = [
        r"self\.model\.",
        r"\.model\.",
        r"model\s*=.*Model\(",
        r"from.*model.*import",
    ]
    return any(re.search(pattern, content) for pattern in model_patterns)


def has_complex_calculations(content):
    """Detecta calculos complejos"""
    calc_patterns = [
        r"for.*in.*range\(.*\).*\+.*\*",
        r"sum\(.*for.*in.*\)",
        r"math\.",
        r"decimal\.Decimal",
    ]
    return any(re.search(pattern, content) for pattern in calc_patterns)


def main():
    """Funcion principal"""
    violations, stats = analyze_mvc_violations()

    print("\nSIGUIENTE PASO:")
    if stats["critical_violations"] > 0:
        print("  1. Reparar violaciones criticas detectadas")
        print("  2. Crear script de refactorizacion MVC")
    else:
        print("  1. Revisar violaciones de severidad menor")
        print("  2. Mejorar documentacion y patrones")

    return violations, stats


if __name__ == "__main__":
    main()
