#!/usr/bin/env python3
"""
Script para reorganizar, mover y enumerar archivos de documentación en carpetas temáticas.
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

# Definición de movimientos y renombrados
MOVIMIENTOS = [
    # GUÍA Y GENERAL
    ("docs/01_Introduccion.md", "docs/guia/01_Introduccion.md"),
    ("docs/06_Desarrollo.md", "docs/guia/02_Desarrollo.md"),
    ("docs/07_DocumentacionTecnica.md", "docs/guia/03_DocumentacionTecnica.md"),
    ("docs/13_ResumenFuncionalidades.md", "docs/guia/04_ResumenFuncionalidades.md"),
    # ARQUITECTURA
    ("docs/02_Arquitectura.md", "docs/arquitectura/01_Arquitectura.md"),
    ("docs/03_BaseDeDatos.md", "docs/arquitectura/02_BaseDeDatos.md"),
    ("docs/08_MVC_Guia.md", "docs/arquitectura/03_MVC_Guia.md"),
    ("docs/09_EstructuraCodigo.md", "docs/arquitectura/04_EstructuraCodigo.md"),
    ("docs/11_EstructuraProyecto.md", "docs/arquitectura/05_EstructuraProyecto.md"),
    ("docs/ARQUITECTURA_MODULAR_INVENTARIO.md", "docs/arquitectura/06_Arquitectura_Modular_Inventario.md"),
    # SEGURIDAD
    ("docs/04_Seguridad.md", "docs/seguridad/01_Seguridad.md"),
    ("docs/10_EstandaresSeguridad.md", "docs/seguridad/02_EstandaresSeguridad.md"),
    # DESPLIEGUE
    ("docs/05_Despliegue.md", "docs/despliegue/01_Despliegue.md"),
    ("docs/12_ComoEjecutar.md", "docs/despliegue/02_ComoEjecutar.md"),
    # CHECKLISTS
    ("docs/CHECKLIST_CORRECCIONES_COMPLETADO.md", "docs/checklists/01_Checklist_Correcciones_Completado.md"),
    # AUDITORÍA
    ("docs/AUDITORIA_API_REXUS_2025.md", "docs/auditoria/01_Auditoria_API_REXUS_2025.md"),
    ("docs/AUDITORIA_CORE_REXUS_2025.md", "docs/auditoria/02_Auditoria_CORE_REXUS_2025.md"),
    ("docs/AUDITORIA_CRITICA_SEGURIDAD_PASSWORDS.md", "docs/auditoria/03_Auditoria_Critica_Seguridad_Passwords.md"),
    ("docs/AUDITORIA_FINALIZADA_EXITOSAMENTE.md", "docs/auditoria/04_Auditoria_Finalizada_Exitosamente.md"),
    ("docs/AUDITORIA_FINAL_COMPLETADA_2025.md", "docs/auditoria/05_Auditoria_Final_Completada_2025.md"),
    ("docs/AUDITORIA_INVENTARIO_FINALIZADA_EXITOSAMENTE.md", "docs/auditoria/06_Auditoria_Inventario_Finalizada_Exitosamente.md"),
    ("docs/AUDITORIA_INVENTARIO_UI_VIOLACIONES_2025.md", "docs/auditoria/07_Auditoria_Inventario_UI_Violaciones_2025.md"),
    ("docs/AUDITORIA_MAIN_REXUS_2025.md", "docs/auditoria/08_Auditoria_Main_REXUS_2025.md"),
    ("docs/AUDITORIA_MODULOS_RESTANTES_CONSOLIDADA_2025.md", "docs/auditoria/09_Auditoria_Modulos_Restantes_Consolidada_2025.md"),
    ("docs/AUDITORIA_MODULO_ADMINISTRACION_CRITICA_2025.md", "docs/auditoria/10_Auditoria_Modulo_Administracion_Critica_2025.md"),
    ("docs/AUDITORIA_MODULO_COMPRAS_2025.md", "docs/auditoria/11_Auditoria_Modulo_Compras_2025.md"),
    ("docs/AUDITORIA_MODULO_HERRAJES_2025.md", "docs/auditoria/12_Auditoria_Modulo_Herrajes_2025.md"),
    ("docs/AUDITORIA_MODULO_LOGISTICA_2025.md", "docs/auditoria/13_Auditoria_Modulo_Logistica_2025.md"),
    ("docs/AUDITORIA_MODULO_MANTENIMIENTO_2025.md", "docs/auditoria/14_Auditoria_Modulo_Mantenimiento_2025.md"),
    ("docs/AUDITORIA_MODULO_NOTIFICACIONES_2025.md", "docs/auditoria/15_Auditoria_Modulo_Notificaciones_2025.md"),
    ("docs/AUDITORIA_OBRAS_COMPLETADA.md", "docs/auditoria/16_Auditoria_Obras_Completada.md"),
    ("docs/AUDITORIA_SEGURIDAD_COMPLETADA.md", "docs/auditoria/17_Auditoria_Seguridad_Completada.md"),
    ("docs/AUDITORIA_TESTS_EDGE_CASES_COBERTURA.md", "docs/auditoria/18_Auditoria_Tests_Edge_Cases_Cobertura.md"),
    ("docs/AUDITORIA_UTILS_REXUS_2025.md", "docs/auditoria/19_Auditoria_Utils_REXUS_2025.md"),
]

def main():
    print("\n--- REORGANIZACIÓN DE DOCUMENTACIÓN ---\n")
    for origen, destino in MOVIMIENTOS:
        mover_y_renombrar(origen, destino)
    print("\n✅ Reorganización completada.\n")

if __name__ == "__main__":
    main()
