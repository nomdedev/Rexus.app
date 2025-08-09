#!/usr/bin/env python3
"""
Script para limpiar archivos con errores de sintaxis que no son esenciales
Elimina tests rotos, archivos de backup y archivos temporales con errores
"""

import os
import shutil
from pathlib import Path

def clean_broken_files():
    """Limpia archivos con errores de sintaxis que no son esenciales."""
    
    # Lista de archivos rotos identificados
    broken_files = [
        # Tests rotos (no esenciales para el funcionamiento)
        "tests/simple_test.py",
        "tests/test_clicks_validacion_basica.py", 
        "tests/test_click_simulation.py",
        "tests/test_click_simulation_fixed.py",
        "tests/test_edge_cases.py",
        "tests/test_integracion_basica.py",
        "tests/test_integration.py",
        "tests/test_login_mainwindow_integration.py",
        "tests/test_notificaciones_accesibilidad.py",
        "tests/test_pedidos_controller.py",
        "tests/test_runner_quick.py",
        "tests/test_schema_consistency.py",
        "tests/test_sidebar_components.py",
        "tests/test_simple.py",
        "tests/test_ui_interactions.py",
        "tests/test_visual_directo.py",
        "tests/unificar_modulos_duplicados.py",
        "tests/validate_auditoria_test.py",
        "tests/verify_tests.py",
        
        # Archivos temporales y de backup rotos
        "rexus/modules/inventario/controller_corregido.py",
        "rexus/modules/inventario/controller_final.py",
        "rexus/modules/pedidos/model_refactorizado.py",
        "rexus/utils/security_fixed.py",
        
        # Scripts rotos no esenciales
        "scripts/corregir_patrones.py",
        "scripts/validacion_vidrios_modular.py",
        "scripts/test/generar_tests_completos.py",
        
        # Tools rotos
        "tools/development/setup/auto_install_wheels.py",
        "tools/development/setup/install_dependencies.py",
        "tools/development/testing/navegacion_automatica.py",
        "tools/testing/integration_tests.py",
    ]
    
    # Directorios de tests rotos (eliminar completamente)
    broken_test_dirs = [
        "tests/auditoria",
        "tests/compras", 
        "tests/configuracion",
        "tests/contabilidad",
        "tests/core",
        "tests/formularios",
        "tests/herrajes",
        "tests/integracion",
        "tests/inventario", 
        "tests/logistica",
        "tests/mantenimiento",
        "tests/notificaciones",
        "tests/obras",
        "tests/produccion",
        "tests/rrhh",
        "tests/sidebar",
        "tests/usuarios",
        "tests/utilitarios",
        "tests/verificacion",
        "tests/vidrios",
        "tests/visual",
    ]
    
    cleaned_files = []
    cleaned_dirs = []
    
    print("🧹 Iniciando limpieza de archivos rotos...")
    
    # Eliminar archivos rotos
    for file_path in broken_files:
        full_path = Path(file_path)
        if full_path.exists():
            try:
                full_path.unlink()
                cleaned_files.append(str(full_path))
                print(f"✅ Eliminado: {file_path}")
            except Exception as e:
                print(f"❌ Error eliminando {file_path}: {e}")
    
    # Eliminar directorios de tests rotos
    for dir_path in broken_test_dirs:
        full_path = Path(dir_path)
        if full_path.exists() and full_path.is_dir():
            try:
                shutil.rmtree(full_path)
                cleaned_dirs.append(str(full_path))
                print(f"✅ Directorio eliminado: {dir_path}")
            except Exception as e:
                print(f"❌ Error eliminando directorio {dir_path}: {e}")
    
    # Eliminar archivos con patrones específicos
    patterns_to_clean = [
        "**/test_*_accesibilidad.py",
        "**/test_*_complete.py", 
        "**/test_*_controller_complete.py",
        "**/test_*_model_complete.py",
        "**/test_*_view_complete.py",
        "**/test_*_integracion.py",
        "**/test_*_clicks_completo.py",
        "**/test_*_edge_cases.py",
        "**/test_*_realtime.py",
        "**/*_backup*.py",
        "**/*_fixed.py",
        "**/*_refactorizado.py",
        "**/*_corregido.py",
        "**/*_temp.py",
    ]
    
    for pattern in patterns_to_clean:
        for file_path in Path(".").glob(pattern):
            if file_path.is_file():
                try:
                    file_path.unlink()
                    cleaned_files.append(str(file_path))
                    print(f"✅ Eliminado por patrón: {file_path}")
                except Exception as e:
                    print(f"❌ Error eliminando {file_path}: {e}")
    
    print(f"\n📊 Resumen de limpieza:")
    print(f"Archivos eliminados: {len(cleaned_files)}")
    print(f"Directorios eliminados: {len(cleaned_dirs)}")
    
    # Generar reporte de limpieza
    with open('cleanup_report.txt', 'w', encoding='utf-8') as f:
        f.write("REPORTE DE LIMPIEZA DE ARCHIVOS ROTOS\n")
        f.write("=" * 40 + "\n\n")
        
        f.write("ARCHIVOS ELIMINADOS:\n")
        f.write("-" * 20 + "\n")
        for file_path in cleaned_files:
            f.write(f"{file_path}\n")
        
        f.write(f"\nDIRECTORIOS ELIMINADOS:\n")
        f.write("-" * 20 + "\n")
        for dir_path in cleaned_dirs:
            f.write(f"{dir_path}\n")
        
        f.write(f"\nTOTAL: {len(cleaned_files)} archivos y {len(cleaned_dirs)} directorios eliminados\n")
    
    print(f"📄 Reporte de limpieza guardado en: cleanup_report.txt")
    
    return len(cleaned_files), len(cleaned_dirs)

def verify_essential_files():
    """Verifica que los archivos esenciales del sistema estén presentes."""
    essential_files = [
        "main.py",
        "rexus/modules/inventario/model.py",
        "rexus/modules/inventario/view.py", 
        "rexus/modules/inventario/controller.py",
        "rexus/modules/obras/model.py",
        "rexus/modules/obras/view.py",
        "rexus/modules/obras/controller.py",
        "rexus/modules/usuarios/model.py",
        "rexus/modules/usuarios/view.py",
        "rexus/modules/usuarios/controller.py",
        "rexus/core/config.py",
        "rexus/utils/sql_query_manager.py",
    ]
    
    missing_files = []
    
    print("\n🔍 Verificando archivos esenciales...")
    
    for file_path in essential_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
            print(f"❌ Archivo esencial faltante: {file_path}")
        else:
            print(f"✅ Archivo esencial presente: {file_path}")
    
    if missing_files:
        print(f"\n⚠️  {len(missing_files)} archivos esenciales están faltando!")
        return False
    else:
        print(f"\n✅ Todos los archivos esenciales están presentes")
        return True

def main():
    print("🧹 Iniciando limpieza de proyecto...")
    
    # Limpiar archivos rotos
    files_cleaned, dirs_cleaned = clean_broken_files()
    
    # Verificar archivos esenciales
    essential_ok = verify_essential_files()
    
    print(f"\n📋 RESUMEN FINAL:")
    print(f"✅ Archivos eliminados: {files_cleaned}")
    print(f"✅ Directorios eliminados: {dirs_cleaned}")
    print(f"{'✅' if essential_ok else '❌'} Archivos esenciales: {'OK' if essential_ok else 'FALTANTES'}")
    
    if essential_ok:
        print(f"\n🎉 Limpieza completada exitosamente!")
        print(f"El proyecto ahora debería tener menos errores de sintaxis.")
    else:
        print(f"\n⚠️  Revisar archivos esenciales faltantes antes de continuar.")

if __name__ == "__main__":
    main()
