#!/usr/bin/env python3
"""
Script para reorganizar los tests de Rexus.app en la nueva estructura de carpetas.
Mueve los archivos existentes a su ubicación correcta según la nueva organización.

Uso: python reorganize_tests.py [--dry-run] [--backup]
"""

import os
import shutil
import sys
from pathlib import Path
from datetime import datetime

# Configuración
TESTS_DIR = Path("tests")
BACKUP_DIR = Path("tests_backup_" + datetime.now().strftime("%Y%m%d_%H%M%S"))

# Mapeo de archivos a nueva estructura
FILE_MAPPING = {
    # Tests unitarios por módulo
    "test_configuracion_persistence_real.py": "unit/configuracion/test_persistence.py",
    "test_configuracion_audit_fixed.py": "unit/configuracion/test_audit.py",
    
    "test_inventario_simple.py": "unit/inventario/test_model_basic.py", 
    "test_inventario_integracion_avanzada.py": "unit/inventario/test_advanced_integration.py",
    
    "test_obras_completo.py": "unit/obras/test_model_complete.py",
    "test_obras_integracion_avanzada.py": "unit/obras/test_advanced_integration.py",
    
    "test_compras_complete.py": "unit/compras/test_model_complete.py",
    "test_compras_workflows_real.py": "unit/compras/test_workflows.py",
    
    "test_pedidos_complete.py": "unit/pedidos/test_model_complete.py", 
    "test_pedidos_workflows_real.py": "unit/pedidos/test_workflows.py",
    
    "test_vidrios_complete.py": "unit/vidrios/test_model_complete.py",
    "test_vidrios_workflows_completos.py": "unit/vidrios/test_workflows.py",
    
    "test_notificaciones_complete.py": "unit/notificaciones/test_model_complete.py",
    "test_notificaciones_workflows_completos.py": "unit/notificaciones/test_workflows.py",
    
    # Tests de usuarios/seguridad
    "test_usuarios_seguridad.py": "unit/usuarios/test_auth_core.py",
    "test_usuarios_seguridad_fixed.py": "unit/usuarios/test_auth_fixed.py", 
    "test_auditoria_seguridad.py": "security/test_audit.py",
    "test_permisos_roles.py": "security/test_permissions.py",
    "test_sesiones.py": "security/test_sessions.py",
    
    # Tests de integración  
    "test_database_integration_real.py": "integration/test_database_real.py",
    "test_database_integration_migrated.py": "integration/test_database_migrated.py",
    "test_consolidated_models_migrated.py": "integration/test_models_consolidated.py",
    
    # Tests E2E
    "test_e2e_integration_workflows.py": "e2e/test_integration_workflows.py",
    "test_e2e_workflows_inter_modulos.py": "e2e/test_inter_module_workflows.py",
    
    # Tests UI
    "test_login_ui.py": "ui/test_login.py",
    "test_accessibility_comprehensive.py": "ui/test_accessibility.py",
    "test_form_validations_comprehensive.py": "ui/test_form_validations.py",
    "test_form_validators_none_handling.py": "ui/test_form_validators.py",
    
    # Tests de performance
    "test_critical_modules.py": "performance/test_critical_modules.py",
    
    # Tests de seguridad adicionales  
    "test_security_module_audit.py": "security/test_module_audit.py",
    
    # Scripts y runners
    "run_security_tests.py": "runners/run_security_tests.py",
    "run_phase2_workflows_complete.py": "runners/run_phase2_workflows.py", 
    "run_comprehensive_test_suite.py": "runners/run_comprehensive_suite.py",
    "master_phase3_runner.py": "runners/master_phase3_runner.py",
    "test_runner.py": "runners/test_runner.py",
    
    # Utilidades y fixtures
    "auth_test_patch.py": "utils/auth_test_patch.py",
    "fix_all_patches.py": "utils/fix_all_patches.py", 
    "demo_security_implementation.py": "utils/demo_security.py",
    "fase2_completion_summary.py": "utils/completion_summary.py",
    
    # Archivos de reporte (mantener en raíz por ahora)
    "fase2_completion_certificate_20250820.json": "reports/fase2_completion_certificate.json",
    "phase2_workflow_report_20250820_151026.json": "reports/phase2_workflow_report.json",
}

# Directorios a crear
DIRECTORIES = [
    "unit", "unit/configuracion", "unit/inventario", "unit/obras", 
    "unit/compras", "unit/pedidos", "unit/vidrios", "unit/notificaciones", "unit/usuarios",
    "integration", "e2e", "ui", "performance", "security", 
    "fixtures", "utils", "runners", "reports"
]

def create_directories(base_path: Path, dry_run: bool = False):
    """Crea la estructura de directorios."""
    print("📁 Creando estructura de directorios...")
    
    for directory in DIRECTORIES:
        dir_path = base_path / directory
        if not dry_run:
            dir_path.mkdir(parents=True, exist_ok=True)
        print(f"   ✅ {dir_path}")

def backup_current_tests(dry_run: bool = False):
    """Crea backup de la estructura actual."""
    if dry_run:
        print(f"🔄 [DRY RUN] Crearía backup en: {BACKUP_DIR}")
        return
    
    print(f"💾 Creando backup en: {BACKUP_DIR}")
    shutil.copytree(TESTS_DIR, BACKUP_DIR, ignore=shutil.ignore_patterns('__pycache__'))
    print("   ✅ Backup completado")

def move_files(dry_run: bool = False):
    """Mueve los archivos a su nueva ubicación."""
    print("📦 Reorganizando archivos de test...")
    
    moved_count = 0
    skipped_count = 0
    
    for old_file, new_location in FILE_MAPPING.items():
        old_path = TESTS_DIR / old_file
        new_path = TESTS_DIR / new_location
        
        if old_path.exists():
            if dry_run:
                print(f"   🔄 [DRY RUN] {old_file} → {new_location}")
            else:
                # Crear directorio padre si no existe
                new_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Mover archivo
                shutil.move(str(old_path), str(new_path))
                print(f"   ✅ {old_file} → {new_location}")
            
            moved_count += 1
        else:
            print(f"   ⚠️  {old_file} no encontrado")
            skipped_count += 1
    
    print(f"\n📊 Resumen: {moved_count} archivos movidos, {skipped_count} no encontrados")

def create_init_files(dry_run: bool = False):
    """Crea archivos __init__.py en los directorios."""
    print("📄 Creando archivos __init__.py...")
    
    for directory in DIRECTORIES:
        init_path = TESTS_DIR / directory / "__init__.py"
        if not dry_run:
            if not init_path.exists():
                init_path.write_text(f'"""Tests {directory} para Rexus.app"""\n')
        print(f"   ✅ {init_path}")

def update_imports_in_files(dry_run: bool = False):
    """Actualiza imports en archivos de configuración."""
    print("🔄 Actualizando imports en conftest.py...")
    
    conftest_path = TESTS_DIR / "conftest.py"
    if conftest_path.exists() and not dry_run:
        # Leer contenido actual
        content = conftest_path.read_text(encoding='utf-8')
        
        # Agregar imports para nueva estructura
        additional_imports = """
# Imports para nueva estructura de tests
import sys
from pathlib import Path

# Agregar subdirectorios al path para imports
test_dirs = ['unit', 'integration', 'e2e', 'ui', 'performance', 'security', 'utils', 'fixtures']
for test_dir in test_dirs:
    dir_path = Path(__file__).parent / test_dir
    if dir_path.exists():
        sys.path.insert(0, str(dir_path))
"""
        
        if "# Imports para nueva estructura" not in content:
            content = additional_imports + "\n" + content
            conftest_path.write_text(content, encoding='utf-8')
            print("   ✅ conftest.py actualizado")
        else:
            print("   ℹ️  conftest.py ya está actualizado")

def create_readme_files(dry_run: bool = False):
    """Crea archivos README en cada directorio."""
    readme_contents = {
        "unit": "# Tests Unitarios\n\nTests que prueban componentes individuales de forma aislada.",
        "integration": "# Tests de Integración\n\nTests que verifican la interacción entre múltiples componentes.",
        "e2e": "# Tests End-to-End\n\nTests que verifican workflows completos del usuario.",
        "ui": "# Tests de Interfaz\n\nTests específicos para componentes de UI y usabilidad.",
        "performance": "# Tests de Performance\n\nTests que verifican rendimiento y tiempos de respuesta.",
        "security": "# Tests de Seguridad\n\nTests de autenticación, autorización y seguridad general.",
        "utils": "# Utilidades de Testing\n\nHelpers, patches y utilidades para facilitar testing.",
        "fixtures": "# Fixtures y Datos de Prueba\n\nDatos de muestra y configuraciones para tests.",
        "runners": "# Scripts de Ejecución\n\nScripts para ejecutar grupos específicos de tests."
    }
    
    print("📝 Creando archivos README...")
    
    for directory, content in readme_contents.items():
        readme_path = TESTS_DIR / directory / "README.md"
        if not dry_run:
            if not readme_path.exists():
                readme_path.write_text(content + "\n", encoding='utf-8')
        print(f"   ✅ {readme_path}")

def main():
    """Función principal."""
    dry_run = "--dry-run" in sys.argv
    create_backup = "--backup" in sys.argv
    
    print("🚀 Iniciando reorganización de tests de Rexus.app")
    print(f"📂 Directorio de tests: {TESTS_DIR.absolute()}")
    
    if dry_run:
        print("⚠️  MODO DRY RUN - No se realizarán cambios reales")
    
    # Verificar que el directorio tests existe
    if not TESTS_DIR.exists():
        print(f"❌ Error: Directorio {TESTS_DIR} no encontrado")
        return 1
    
    try:
        # Crear backup si se solicita
        if create_backup:
            backup_current_tests(dry_run)
        
        # Crear estructura de directorios
        create_directories(TESTS_DIR, dry_run)
        
        # Mover archivos
        move_files(dry_run)
        
        # Crear archivos __init__.py
        create_init_files(dry_run)
        
        # Actualizar imports
        update_imports_in_files(dry_run)
        
        # Crear READMEs
        create_readme_files(dry_run)
        
        print("\n🎉 Reorganización completada exitosamente!")
        
        if not dry_run:
            print("\n📋 Próximos pasos recomendados:")
            print("1. Ejecutar tests para verificar que funcionan: pytest tests/")
            print("2. Actualizar imports en archivos de test si es necesario")
            print("3. Revisar y actualizar scripts de CI/CD")
            print("4. Actualizar documentación de testing")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error durante la reorganización: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())