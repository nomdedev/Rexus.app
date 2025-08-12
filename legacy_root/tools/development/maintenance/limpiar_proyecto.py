#!/usr/bin/env python3
"""
Script de limpieza de archivos obsoletos en la raíz del proyecto
Organiza y limpia archivos que ya no son necesarios
"""

def limpiar_proyecto():
    """Limpia archivos obsoletos del proyecto"""
import os
import shutil
from datetime import datetime

    print("🧹 INICIANDO LIMPIEZA DEL PROYECTO")
    print("=" * 50)

    # Archivos a eliminar (obsoletos/temporales)
    archivos_eliminar = [
        ".table_columns_2295734951504.json",
        ".table_columns_tabla_inventario.json",
        "bandit-report.json",
        "coverage.json",
        "estado_proyecto.json",
        "estructura_real_bd.json",
        "informe_estado_proyecto.md",
        "informe_seguridad_sql.html",
        "mejoras_feedback_visual.md",
        "reporte_seguridad_20250625_223627.json",
        "reporte_seguridad_20250625_223745.json"
    ]

    # Archivos de reportes temporales (por fecha)
    reportes_temporales = [
        "METRICAS_RAPIDAS_20250625_215034.md",
        "METRICAS_RAPIDAS_20250625_220849.md",
        "REPORTE_COBERTURA_20250625_214913.md",
        "REPORTE_COBERTURA_20250625_214954.md",
        "REPORTE_SEGURIDAD_20250625_222004.md"
    ]

    # Directorios a limpiar (contenido temporal)
    directorios_limpiar = [
        "backups_feedback",
        "informes_modulos",
        "coverage_html",
        "test_results"
    ]

    contador_eliminados = 0

    # Crear directorio de backup antes de eliminar
    backup_dir = f"archivos_eliminados_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(backup_dir, exist_ok=True)
    print(f"📦 Creando backup en: {backup_dir}")

    # Eliminar archivos obsoletos
    print("\n🗑️ ELIMINANDO ARCHIVOS OBSOLETOS:")
    for archivo in archivos_eliminar + reportes_temporales:
        if os.path.exists(archivo):
            # Hacer backup primero
            shutil.copy2(archivo, backup_dir)
            os.remove(archivo)
            print(f"   [CHECK] Eliminado: {archivo}")
            contador_eliminados += 1
        else:
            print(f"   ℹ️ No existe: {archivo}")

    # Limpiar directorios temporales
    print("\n📁 LIMPIANDO DIRECTORIOS TEMPORALES:")
    for directorio in directorios_limpiar:
        if os.path.exists(directorio):
            # Hacer backup del directorio
            if os.listdir(directorio):  # Si no está vacío
                shutil.copytree(directorio, os.path.join(backup_dir, directorio))
                shutil.rmtree(directorio)
                print(f"   [CHECK] Eliminado directorio: {directorio}")
                contador_eliminados += 1
            else:
                print(f"   ℹ️ Directorio vacío: {directorio}")
        else:
            print(f"   ℹ️ No existe: {directorio}")

    # Organizar documentación en subcarpeta
    print("\n📚 ORGANIZANDO DOCUMENTACIÓN:")

    # Crear directorio de documentación si no existe
    docs_dir = "docs/informes_sesion"
    os.makedirs(docs_dir, exist_ok=True)

    # Mover archivos de documentación final
    docs_finales = [
        "ESTADO_FINAL_SESION_25062025.md",
        "ITERACION_SEGURIDAD_QR_COMPLETADA_25062025.md",
        "REPORTE_MEJORAS_SEGURIDAD_QR_25062025.md",
        "RESUMEN_EJECUTIVO_CI_CD_25062025.md",
        "RESUMEN_EXPANSION_TESTS_25062025.md",
        "RESUMEN_MEJORAS_25062025.md",
        "ROADMAP_MEJORAS_CONTINUAS.md",
        "CORRECCION_TESTS_PEDIDOS.md",
        "CORRECCION_TEST_SCHEMA.md"
    ]

    for doc in docs_finales:
        if os.path.exists(doc):
            destino = os.path.join(docs_dir, doc)
            shutil.move(doc, destino)
            print(f"   📄 Movido a docs: {doc}")

    # Limpiar archivos de cache Python
    print("\n🐍 LIMPIANDO CACHE PYTHON:")
    for root, dirs, files in os.walk("."):
        for dir_name in dirs[:]:  # Usar slice para modificar durante iteración
            if dir_name == "__pycache__":
                cache_path = os.path.join(root, dir_name)
                shutil.rmtree(cache_path)
                print(f"   [CHECK] Eliminado cache: {cache_path}")
                dirs.remove(dir_name)

    # Crear archivo README para el backup
    readme_backup = os.path.join(backup_dir, "README.md")
    with open(readme_backup, 'w', encoding='utf-8') as f:
        f.write(f"""# Backup de Archivos Eliminados

**Fecha:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Acción:** Limpieza automática del proyecto

## Archivos respaldados:
- Archivos de configuración temporal
- Reportes de métricas antiguos
- Archivos de estado temporal
- Directorios de informes temporales

## Nota:
Estos archivos fueron eliminados durante la limpieza del proyecto para mantener
solo los archivos esenciales en la raíz. Se pueden restaurar si es necesario.
""")

    # Resumen final
    print("\n" + "=" * 50)
    print("[CHECK] LIMPIEZA COMPLETADA")
    print("=" * 50)
    print(f"[CHART] Archivos procesados: {contador_eliminados}")
    print(f"📦 Backup creado en: {backup_dir}")
    print(f"📚 Documentación organizada en: {docs_dir}")
    print("\n🎯 ESTRUCTURA LIMPIA LOGRADA:")
    print("   - Raíz del proyecto más organizada")
    print("   - Documentación movida a docs/")
    print("   - Archivos temporales eliminados")
    print("   - Cache Python limpiado")
    print("   - Backup de seguridad creado")

if __name__ == "__main__":
    limpiar_proyecto()
