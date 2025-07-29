#!/usr/bin/env python3
"""
Script para organizar y limpiar la estructura de scripts del proyecto
Clasifica scripts por propósito y elimina los de uso único
"""

def organizar_scripts():
    """Organiza los scripts en categorías y elimina obsoletos"""
import os
import shutil
from datetime import datetime

    print("🗂️ ORGANIZANDO ESTRUCTURA DE SCRIPTS")
    print("=" * 50)

    # Mapeo de scripts por categoría
    organizacion = {
        "setup": [
            "auto_install_wheels.py",
            "install_dependencies.py",
            "install.bat",
            "install.sh",
            "build_windows.bat"
        ],
        "database": [
            "get_schema_info.py",
            "migrate.py",
            "migrar_estructura_bd.sql",
            "migrar_estructura_bd_adaptado.sql",
            "MPS_SQL_COMPLETO_SIN_PREFIJOS.sql",
            "sync_db_auditoria.sql",
            "sync_db_inventario.sql",
            "sync_db_unificado.sql",
            "sync_db_users.sql",
            "obtener_estructura.bat",
            "obtener_estructura.sql"
        ],
        "maintenance": [
            "limpiar_proyecto.py",
            "limpiar_json_raiz.py",
            "validar_permisos_iniciales.py"
        ],
        "testing": [
            "verificar_seguridad_completa.py"
        ],
        "security": []
    }

    # Scripts de uso único a eliminar
    scripts_eliminar = [
        "analizar_bd_simplificado.py",
        "analizar_estructura_bd.py",
        "diagnostico_completo.py",
        "generar_inventario_formato_final.py",
        "importar_inventario_csv.py",
        "listar_tablas_users.py",
        "procesar_e_importar_inventario.py",
        "test_startup_app.ps1",
        "unificar_tablas_y_actualizar_modelos.py",
        "actualizaciones_modelos.py",
        "ejecutar_migracion_win.bat",
        "ejecutar_unificacion_win.bat"
    ]

    # Scripts de verificación de uso único a eliminar
    scripts_verificacion_eliminar = [
        "ajustar_tests_metodos_reales.py",
        "completar_estructura_tests.py",
        "completar_todos_los_tests.py",
        "configurar_ci_cd.py",
        "corregir_paths_tests.py",
        "ejecutar_tests_masivos.py",
        "finalizar_iteracion_tests.py",
        "finalizar_mejoras.py",
        "generar_tests_basicos.py",
        "generar_tests_completos.py",
        "generar_tests_especificos.py",
        "iniciar_investigacion_modulos.py",
        "inspeccionar_estructura_bd.py",
        "reporte_final_cobertura.py"
    ]

    # Scripts de verificación a mantener (categorizados)
    scripts_verificacion_mantener = {
        "testing": [
            "generar_reporte_cobertura.py",
            "metricas_rapidas.py",
            "verificacion_completa.py"
        ],
        "security": [
            "analisis_seguridad_completo.py",
            "analizar_seguridad_sql_codigo.py",
            "diagnostico_seguridad_bd.py",
            "escanear_vulnerabilidades.py"
        ],
        "database": [
            "analisis_tablas.py",
            "analizar_tablas_faltantes.py",
            "diagnostico_db.py",
            "diagnostico_errores_sql.py",
            "verificar_conexion_bd.py",
            "verificar_tablas_rapido.py"
        ],
        "maintenance": [
            "analizador_modulos.py",
            "analizar_estructura_modulos.py",
            "generar_checklists_completados.py",
            "generar_indice_modulos.py",
            "generar_informes_modulos.py",
            "mejorar_feedback_visual.py",
            "ejecutar_analisis_completo.py",
            "verificar_integracion.py"
        ]
    }

    contador_movidos = 0
    contador_eliminados = 0

    # Crear backup
    backup_dir = f"scripts_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(backup_dir, exist_ok=True)

    # Mover scripts de la raíz a categorías
    print("\n📁 ORGANIZANDO SCRIPTS POR CATEGORÍA:")
    for categoria, scripts in organizacion.items():
        destino_dir = f"scripts/{categoria}"
        for script in scripts:
            origen = f"scripts/{script}"
            if os.path.exists(origen):
                # Backup primero
                shutil.copy2(origen, backup_dir)
                # Mover a nueva ubicación
                destino = f"{destino_dir}/{script}"
                shutil.move(origen, destino)
                print(f"   ✅ {script} → {categoria}/")
                contador_movidos += 1

    # Mover scripts de verificación
    print("\n📁 ORGANIZANDO SCRIPTS DE VERIFICACIÓN:")
    for categoria, scripts in scripts_verificacion_mantener.items():
        destino_dir = f"scripts/{categoria}"
        for script in scripts:
            origen = f"scripts/verificacion/{script}"
            if os.path.exists(origen):
                # Backup primero
                shutil.copy2(origen, backup_dir)
                # Mover a nueva ubicación
                destino = f"{destino_dir}/{script}"
                shutil.move(origen, destino)
                print(f"   ✅ verificacion/{script} → {categoria}/")
                contador_movidos += 1

    # Eliminar scripts obsoletos de la raíz
    print("\n🗑️ ELIMINANDO SCRIPTS OBSOLETOS:")
    for script in scripts_eliminar:
        origen = f"scripts/{script}"
        if os.path.exists(origen):
            shutil.copy2(origen, backup_dir)
            os.remove(origen)
            print(f"   ❌ Eliminado: {script}")
            contador_eliminados += 1

    # Eliminar scripts obsoletos de verificación
    for script in scripts_verificacion_eliminar:
        origen = f"scripts/verificacion/{script}"
        if os.path.exists(origen):
            shutil.copy2(origen, backup_dir)
            os.remove(origen)
            print(f"   ❌ Eliminado: verificacion/{script}")
            contador_eliminados += 1

    # Limpiar directorios vacíos
    print("\n📂 LIMPIANDO DIRECTORIOS:")
    directorios_verificar = [
        "scripts/verificacion",
        "scripts/db",
        "scripts/logs",
        "scripts/migraciones"
    ]

    for directorio in directorios_verificar:
        if os.path.exists(directorio):
            try:
                if not os.listdir(directorio):  # Si está vacío
                    os.rmdir(directorio)
                    print(f"   🗂️ Eliminado directorio vacío: {directorio}")
                else:
                    # Si no está vacío, mover contenido a backup
                    backup_subdir = os.path.join(backup_dir, os.path.basename(directorio))
                    shutil.copytree(directorio, backup_subdir)
                    shutil.rmtree(directorio)
                    print(f"   📦 Movido a backup: {directorio}")
            except OSError:
                print(f"   ⚠️ No se pudo eliminar: {directorio}")

    # Crear README para cada categoría
    print("\n📝 CREANDO DOCUMENTACIÓN:")

    categorias_info = {
        "setup": "Scripts de instalación y configuración inicial del proyecto",
        "database": "Scripts de gestión y mantenimiento de base de datos",
        "maintenance": "Scripts de mantenimiento, limpieza y análisis del proyecto",
        "testing": "Scripts para ejecución y reporte de tests",
        "security": "Scripts de análisis y verificación de seguridad"
    }

    for categoria, descripcion in categorias_info.items():
        readme_path = f"scripts/{categoria}/README.md"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(f"""# {categoria.title()} Scripts

{descripcion}

## Scripts disponibles:

""")
            # Listar scripts en la categoría
            categoria_dir = f"scripts/{categoria}"
            if os.path.exists(categoria_dir):
                for archivo in sorted(os.listdir(categoria_dir)):
                    if archivo.endswith(('.py', '.bat', '.sh', '.sql')) and archivo != 'README.md':
                        f.write(f"- `{archivo}`\n")

            f.write(f"""
## Uso:

```bash
# Ejecutar desde la raíz del proyecto
python scripts/{categoria}/[script_name].py
```

---
*Generado automáticamente - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
""")
        print(f"   📄 Creado: scripts/{categoria}/README.md")

    # Actualizar .gitignore si es necesario
    gitignore_path = ".gitignore"
    if os.path.exists(gitignore_path):
        with open(gitignore_path, 'r') as f:
            contenido = f.read()

        # Agregar entradas para backups si no existen
        nuevas_entradas = [
            "scripts_backup_*/",
            "archivos_eliminados_*/",
            "tests/reports/*.html",
            "tests/reports/*.json"
        ]

        contenido_actualizado = contenido
        for entrada in nuevas_entradas:
            if entrada not in contenido:
                contenido_actualizado += f"\n{entrada}"

        if contenido_actualizado != contenido:
            with open(gitignore_path, 'w') as f:
                f.write(contenido_actualizado)
            print("   📄 Actualizado .gitignore")

    # Resumen final
    print("\n" + "=" * 50)
    print("✅ ORGANIZACIÓN COMPLETADA")
    print("=" * 50)
    print(f"📊 Scripts movidos: {contador_movidos}")
    print(f"🗑️ Scripts eliminados: {contador_eliminados}")
    print(f"📦 Backup creado en: {backup_dir}")
    print("\n🎯 NUEVA ESTRUCTURA:")
    print("   scripts/")
    print("   ├── setup/          # Instalación y configuración")
    print("   ├── database/       # Gestión de BD")
    print("   ├── maintenance/    # Mantenimiento")
    print("   ├── testing/        # Tests y reportes")
    print("   └── security/       # Seguridad")
    print("\n📁 REPORTES DE TESTS:")
    print("   tests/reports/      # Ubicación para todos los reportes")

if __name__ == "__main__":
    organizar_scripts()
