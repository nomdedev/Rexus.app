#!/usr/bin/env python3
"""
Script para mover, enumerar y organizar archivos secundarios, módulos y scripts de documentación.
"""
import os
import shutil
from pathlib import Path

def ensure_dir(path):
    Path(path).mkdir(parents=True, exist_ok=True)

def mover_y_renombrar(origen, destino):
    destino_dir = os.path.dirname(destino)
    ensure_dir(destino_dir)
    if os.path.exists(origen):
        shutil.move(origen, destino)
        print(f"✔️ {origen} -> {destino}")
    else:
        print(f"⚠️ No encontrado: {origen}")

MOVIMIENTOS = [
    # PLANIFICACIÓN
    ("docs/PLAN_AUDITORIA_COMPLETA.md", "docs/planificacion/01_Plan_Auditoria_Completa.md"),
    ("docs/PLAN_CORRECCION_COMPLETA.md", "docs/planificacion/02_Plan_Correccion_Completa.md"),
    ("docs/PLAN_MAESTRO_IMPLEMENTACION_2025.md", "docs/planificacion/03_Plan_Maestro_Implementacion_2025.md"),
    ("docs/PLAN_PRIORIZACION_AUDITORIA_2025.md", "docs/planificacion/04_Plan_Priorizacion_Auditoria_2025.md"),
    # UI/UX
    ("docs/UI_STANDARDIZATION_FRAMEWORK_IMPLEMENTED_2025.md", "docs/uiux/01_UI_Standardization_Framework.md"),
    ("docs/UI_UX_STANDARDS.md", "docs/uiux/02_UI_UX_Standards.md"),
    ("docs/UI_UX_STYLE_GUIDE.md", "docs/uiux/03_UI_UX_Style_Guide.md"),
    ("docs/UI_UX_STYLE_GUIDE_UNIFIED_2025.md", "docs/uiux/04_UI_UX_Style_Guide_Unified_2025.md"),
    # TABLAS Y BASE DE DATOS
    ("docs/TABLAS_ADICIONALES_REQUERIDAS.md", "docs/tablas/01_Tablas_Adicionales_Requeridas.md"),
    ("docs/TABLA_IMPLEMENTACION_MODULOS.md", "docs/tablas/02_Tabla_Implementacion_Modulos.md"),
    ("docs/USO_BASES_DE_DATOS.md", "docs/tablas/03_Uso_Bases_De_Datos.md"),
    # PERFORMANCE
    ("docs/RESUMEN_OPTIMIZACIONES_RENDIMIENTO.md", "docs/performance/01_Resumen_Optimizaciones_Rendimiento.md"),
    # SCRIPTS
    ("docs/scripts/poblar_datos_completos.py", "docs/scripts/01_Poblar_Datos_Completos.py"),
    ("docs/scripts/poblar_datos_existentes.py", "docs/scripts/02_Poblar_Datos_Existentes.py"),
    ("docs/scripts/verificar_funcionalidad.py", "docs/scripts/03_Verificar_Funcionalidad.py"),
    ("docs/scripts/verificar_funcionalidad_simple.py", "docs/scripts/04_Verificar_Funcionalidad_Simple.py"),
    # MANTENIMIENTO
    ("docs/mantenimiento_module_doc.md", "docs/mantenimiento/01_Mantenimiento_Module_Doc.md"),
    # OTROS
    ("docs/GUIA_REFACTORIZACION_MODULAR.md", "docs/otros/01_Guia_Refactorizacion_Modular.md"),
    ("docs/ISSUES_GENERADOS_AUDITORIA_2025.md", "docs/otros/02_Issues_Generados_Auditoria_2025.md"),
    ("docs/SEGURIDAD_CONFIGURACION_MODULE.md", "docs/seguridad/03_Seguridad_Configuracion_Module.md"),
    ("docs/SEGURIDAD_PEDIDOS_MODULE.md", "docs/seguridad/04_Seguridad_Pedidos_Module.md"),
    ("docs/SEGURIDAD_USUARIOS_AVANZADA.md", "docs/seguridad/05_Seguridad_Usuarios_Avanzada.md"),
    ("docs/SHELL_INTEGRATION.md", "docs/otros/03_Shell_Integration.md"),
    ("docs/SHELL_INTEGRATION_REXUS.md", "docs/otros/04_Shell_Integration_Rexus.md"),
]

def main():
    print("\n--- REORGANIZACIÓN DE DOCUMENTACIÓN SECUNDARIA ---\n")
    for origen, destino in MOVIMIENTOS:
        mover_y_renombrar(origen, destino)
    print("\n✅ Reorganización secundaria completada.\n")

if __name__ == "__main__":
    main()
