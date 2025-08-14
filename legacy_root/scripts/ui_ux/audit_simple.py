#!/usr/bin/env python3
"""
Ejecutor Simplificado de Auditorías UI/UX para Windows
"""

import os
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def ejecutar_auditoria_manual():
    """Ejecuta auditorías de forma manual para evitar problemas de encoding"""

    # Configurar encoding para Windows
    if os.name == "nt":
        os.environ["PYTHONIOENCODING"] = "utf-8"

    root_path = Path(__file__).parent.parent.parent
    rexus_path = root_path / "rexus" / "modules"

    print("=" * 60)
    print("AUDITORIA UI/UX - REXUS APP")
    print("=" * 60)

    if not rexus_path.exists():
        print(f"[ERROR] No se encuentra el directorio: {rexus_path}")
        return

    # Contar módulos disponibles
    modulos = [
        d for d in rexus_path.iterdir() if d.is_dir() and \
            not d.name.startswith("__")
    ]
    print(f"[INFO] Encontrados {len(modulos)} módulos para analizar")

    issues_consistencia = 0
    issues_accesibilidad = 0

    # Análisis básico por módulo
    for modulo in modulos:
        print(f"[MODULO] Analizando: {modulo.name}")

        # Buscar archivos view.py
        view_files = list(modulo.glob("**/view.py"))

        for view_file in view_files:
            try:
                with open(view_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    lines = content.split("\n")

                # Análisis básico de consistencia
                for i, line in enumerate(lines, 1):
                    # Colores inconsistentes
                    if "#" in line and any(
                        color in line.lower() for color in ["#999", "#ccc", "#ddd"]
                    ):
                        issues_consistencia += 1

                    # Fuentes no estándar
                    if (
                        "QFont" in line
                        and "Arial" not in line
                        and "Courier" not in line
                    ):
                        issues_consistencia += 1

                    # Elementos sin accesibilidad
                    if (
                        "QPushButton" in line or "QLineEdit" in line
                    ) and "setAccessibleName" not in line:
                        issues_accesibilidad += 1

                    # Imágenes sin texto alternativo
                    if (
                        "setPixmap" in line
                        and "setAccessibleDescription" not in content
                    ):
                        issues_accesibilidad += 1

            except Exception as e:
                print(f"  [ERROR] Error leyendo {view_file}: {e}")

        print(f"  [INFO] Análisis de {modulo.name} completado")

    # Resumen final
    print("\n" + "=" * 60)
    print("RESUMEN DE AUDITORIA")
    print("=" * 60)
    print(f"Módulos analizados: {len(modulos)}")
    print(f"Issues de consistencia: {issues_consistencia}")
    print(f"Issues de accesibilidad: {issues_accesibilidad}")

    # Calcular score
    total_checks = len(modulos) * 20  # Estimación
    total_issues = issues_consistencia + issues_accesibilidad
    score = (
        max(0, 100 - (total_issues / total_checks * 100)) if total_checks > 0 else 100
    )

    print(f"Score general UI/UX: {score:.2f}/100")

    # Nivel de prioridad
    if total_issues > 50:
        prioridad = "ALTA - Requiere atención inmediata"
    elif total_issues > 20:
        prioridad = "MEDIA - Resolver en próxima iteración"
    elif total_issues > 0:
        prioridad = "BAJA - Mejoras opcionales"
    else:
        prioridad = "EXCELENTE - No se encontraron issues"

    print(f"Prioridad de mejoras: {prioridad}")

    # Recomendaciones básicas
    print("\nRECOMENDACIONES PRINCIPALES:")
    if issues_consistencia > 0:
        print("- Estandarizar colores y fuentes en todos los módulos")
        print("- Crear un sistema de diseño centralizado")

    if issues_accesibilidad > 0:
        print("- Agregar nombres accesibles a elementos interactivos")
        print("- Incluir texto alternativo para imágenes")
        print("- Mejorar navegación por teclado")

    # Guardar reporte básico
    try:
        logs_path = root_path / "logs"
        logs_path.mkdir(exist_ok=True)

        from datetime import datetime

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        reporte = {
            "timestamp": timestamp,
            "modulos_analizados": len(modulos),
            "issues_consistencia": issues_consistencia,
            "issues_accesibilidad": issues_accesibilidad,
            "score_general": round(score, 2),
            "prioridad": prioridad,
        }

        reporte_path = logs_path / f"ui_ux_basic_report_{timestamp}.json"

        import json

        with open(reporte_path, "w", encoding="utf-8") as f:
            json.dump(reporte, f, indent=2, ensure_ascii=False)

        print(f"\n[SUCCESS] Reporte guardado en: {reporte_path}")

    except Exception as e:
        print(f"[ERROR] No se pudo guardar el reporte: {e}")

    print("\n[SUCCESS] Auditoría UI/UX completada exitosamente!")


if __name__ == "__main__":
    ejecutar_auditoria_manual()
