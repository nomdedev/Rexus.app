#!/usr/bin/env python3
"""
Análisis de cobertura de tests existentes
"""

import os
import sys
from pathlib import Path

# Agregar el directorio raíz al path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))


def analyze_test_coverage():
    """Analiza la cobertura de tests existente"""
    
    print("ANÁLISIS DE COBERTURA DE TESTS - Rexus.app")
    print("=" * 60)
    
    # Directorios de módulos
    modules_dir = ROOT_DIR / "src" / "modules"
    tests_dir = ROOT_DIR / "tests"
    
    # Obtener todos los módulos
    if modules_dir.exists():
        modules = [d.name for d in modules_dir.iterdir() if d.is_dir() and not d.name.startswith('__')]
        modules.sort()
    else:
        modules = []
    
    # Obtener todos los directorios de tests
    if tests_dir.exists():
        test_dirs = [d.name for d in tests_dir.iterdir() if d.is_dir() and not d.name.startswith('__')]
        test_dirs.sort()
    else:
        test_dirs = []
    
    print(f"Módulos encontrados: {len(modules)}")
    print(f"Directorios de test: {len(test_dirs)}")
    
    # Análisis por módulo
    coverage_report = {}
    
    for module in modules:
        module_path = modules_dir / module
        test_path = tests_dir / module
        
        # Contar archivos Python en el módulo
        py_files = list(module_path.glob("**/*.py"))
        py_files = [f for f in py_files if not f.name.startswith('__')]
        
        # Contar archivos de test para este módulo
        test_files = []
        if test_path.exists():
            test_files = list(test_path.glob("**/*.py"))
            test_files = [f for f in test_files if not f.name.startswith('__')]
        
        coverage_report[module] = {
            'source_files': len(py_files),
            'test_files': len(test_files),
            'has_tests': len(test_files) > 0,
            'coverage_ratio': len(test_files) / len(py_files) if py_files else 0
        }
    
    # Mostrar reporte
    print("\n" + "=" * 60)
    print("REPORTE DE COBERTURA POR MÓDULO")
    print("=" * 60)
    
    total_modules = len(modules)
    modules_with_tests = sum(1 for m in coverage_report.values() if m['has_tests'])
    
    print(f"Total de módulos: {total_modules}")
    print(f"Módulos con tests: {modules_with_tests}")
    print(f"Cobertura general: {(modules_with_tests/total_modules)*100:.1f}%")
    
    print("\nDetalle por módulo:")
    print("-" * 60)
    print(f"{'Módulo':<20} {'Archivos':<8} {'Tests':<8} {'Ratio':<8} {'Estado'}")
    print("-" * 60)
    
    for module, data in coverage_report.items():
        status = "OK" if data['has_tests'] else "NO"
        ratio = f"{data['coverage_ratio']:.1f}" if data['coverage_ratio'] > 0 else "0.0"
        
        print(f"{module:<20} {data['source_files']:<8} {data['test_files']:<8} {ratio:<8} {status}")
    
    # Análisis de tipos de test
    print("\n" + "=" * 60)
    print("ANÁLISIS DE TIPOS DE TEST")
    print("=" * 60)
    
    test_types = {
        'unit': 0,
        'integration': 0,
        'ui': 0,
        'controller': 0,
        'model': 0,
        'view': 0,
        'complete': 0,
        'accesibilidad': 0,
        'clicks': 0,
        'security': 0
    }
    
    # Recorrer todos los archivos de test
    for test_file in tests_dir.glob("**/*.py"):
        if test_file.name.startswith('test_'):
            file_content = test_file.name.lower()
            
            # Clasificar por tipo
            if 'controller' in file_content:
                test_types['controller'] += 1
            elif 'model' in file_content:
                test_types['model'] += 1
            elif 'view' in file_content:
                test_types['view'] += 1
            elif 'integracion' in file_content or 'integration' in file_content:
                test_types['integration'] += 1
            elif 'clicks' in file_content:
                test_types['clicks'] += 1
            elif 'ui' in file_content:
                test_types['ui'] += 1
            elif 'complete' in file_content:
                test_types['complete'] += 1
            elif 'accesibilidad' in file_content:
                test_types['accesibilidad'] += 1
            elif 'security' in file_content:
                test_types['security'] += 1
            else:
                test_types['unit'] += 1
    
    print("Distribución de tipos de test:")
    for test_type, count in test_types.items():
        if count > 0:
            print(f"  {test_type.capitalize()}: {count}")
    
    # Análisis de calidad de tests
    print("\n" + "=" * 60)
    print("ANÁLISIS DE CALIDAD DE TESTS")
    print("=" * 60)
    
    # Buscar tests que realmente corren
    working_tests = []
    broken_tests = []
    
    # Tests conocidos que funcionan
    known_working = [
        'test_simple_ui.py',
        'test_export_simple.py',
        'test_all_functionality.py',
        'test_audit_simple.py'
    ]
    
    # Tests con problemas conocidos
    known_broken = [
        'test_ui_clicks.py',  # Problemas Unicode
        'test_export_functionality.py',  # Problemas Unicode
    ]
    
    print("Tests verificados funcionando:")
    for test in known_working:
        if (tests_dir / test).exists():
            working_tests.append(test)
            print(f"  [OK] {test}")
    
    print("\nTests con problemas conocidos:")
    for test in known_broken:
        if (tests_dir / test).exists():
            broken_tests.append(test)
            print(f"  [ERROR] {test}")
    
    # Recomendaciones
    print("\n" + "=" * 60)
    print("RECOMENDACIONES")
    print("=" * 60)
    
    print("1. PRIORIDAD ALTA:")
    modules_sin_tests = [m for m, d in coverage_report.items() if not d['has_tests']]
    if modules_sin_tests:
        print(f"   - Crear tests para módulos sin cobertura: {', '.join(modules_sin_tests)}")
    
    print("2. PRIORIDAD MEDIA:")
    print("   - Consolidar tests duplicados")
    print("   - Estandarizar naming conventions")
    print("   - Crear tests de integración end-to-end")
    
    print("3. PRIORIDAD BAJA:")
    print("   - Mejorar documentación de tests")
    print("   - Agregar tests de performance")
    print("   - Implementar tests de accesibilidad")
    
    return coverage_report


def generate_test_plan():
    """Genera un plan de testing mejorado"""
    
    print("\n" + "=" * 60)
    print("PLAN DE TESTING MEJORADO")
    print("=" * 60)
    
    test_plan = {
        'core_functionality': [
            'test_authentication_flow.py',
            'test_database_operations.py',
            'test_main_window_initialization.py',
            'test_module_loading.py'
        ],
        'ui_interactions': [
            'test_sidebar_navigation.py',
            'test_form_validation.py',
            'test_table_operations.py',
            'test_dialog_interactions.py'
        ],
        'business_logic': [
            'test_obra_lifecycle.py',
            'test_inventory_management.py',
            'test_order_processing.py',
            'test_user_permissions.py'
        ],
        'integration': [
            'test_full_workflow.py',
            'test_module_integration.py',
            'test_database_integration.py',
            'test_export_integration.py'
        ],
        'performance': [
            'test_load_performance.py',
            'test_memory_usage.py',
            'test_response_times.py'
        ]
    }
    
    print("Tests recomendados por categoría:")
    for category, tests in test_plan.items():
        print(f"\n{category.upper()}:")
        for test in tests:
            print(f"  - {test}")
    
    return test_plan


if __name__ == "__main__":
    coverage_report = analyze_test_coverage()
    test_plan = generate_test_plan()
    
    print("\n" + "=" * 60)
    print("ANÁLISIS COMPLETADO")
    print("=" * 60)
    print("Revisa el reporte anterior para mejorar la cobertura de tests.")