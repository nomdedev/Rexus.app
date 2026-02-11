#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Diagnostic Test Runner - Verifica Estado Actual de Tests

Ejecuta TODOS los tests y genera un reporte detallado de:
- Tests que pasan
- Tests que fallan
- Cobertura real
- Módulos sin testear
"""

import subprocess
import sys
import os
from pathlib import Path

# Configurar encoding UTF-8 para salida
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def run_pytest_with_coverage():
    """Ejecuta pytest con coverage y captura resultados."""
    print("="*80)
    print("DIAGNOSTICO COMPLETO DE TESTS")
    print("="*80)

    # Ejecutar pytest con coverage
    cmd = [
        sys.executable, '-m', 'pytest',
        'tests/',
        '-v',
        '--tb=short',
        '--cov=rexus',
        '--cov-report=term-missing',
        '--cov-report=json:coverage_report.json',
        '--cov-report=html:htmlcov',
        '--no-header',
        '-ra'  # Resumen de all/failed/passed
    ]

    print(f"\n📊 Comando: {' '.join(cmd)}\n")
    result = subprocess.run(cmd, capture_output=False)

    return result.returncode

def analyze_coverage():
    """Analiza el reporte de cobertura generado."""
    print("\n" + "="*80)
    print("📈 ANÁLISIS DE COBERTURA")
    print("="*80)

    try:
        with open('coverage_report.json', 'r') as f:
            coverage_data = json.load(f)

        print("\n✅ Cobertura por Archivo:")
        print("-" * 80)

        # Ordenar por cobertura (menor a mayor)
        files = coverage_data.get('files', {})
        sorted_files = sorted(
            files.items(),
            key=lambda x: x[1].get('summary', {}).get('percent_covered', 0)
        )

        for filename, data in sorted_files[:20]:  # Primeros 20 (peor cobertura)
            summary = data.get('summary', {})
            coverage = summary.get('percent_covered', 0)
            lines_total = summary.get('num_statements', 0)
            lines_missing = summary.get('missing_lines', 0)

            status = "🔴" if coverage < 50 else "🟡" if coverage < 80 else "🟢"
            print(f"{status} {coverage:5.1f}% - {filename}")
            if lines_missing:
                print(f"       Líneas sin cubrir: {len(lines_missing)} de {lines_total}")

        return files

    except FileNotFoundError:
        print("❌ No se pudo generar reporte de cobertura")
        return None

def identify_untested_modules():
    """Identifica módulos sin tests."""
    print("\n" + "="*80)
    print("🔎 MÓDULOS SIN TESTEAR")
    print("="*80)

    modules_path = Path('rexus/modules')
    tested_modules = set()
    untested_modules = []

    # Encontrar todos los directorios de módulos
    for module_dir in sorted(modules_path.iterdir()):
        if module_dir.is_dir() and not module_dir.name.startswith('_'):
            module_name = module_dir.name
            module_num = module_dir.name.split('_')[0] if '_' in module_dir.name else '00'

            # Buscar si tiene tests
            test_path = Path(f'tests/unit/{module_num}')
            integration_test_path = Path(f'tests/integration')

            has_unit_test = test_path.exists() and any(test_path.glob('test_*.py'))
            has_integration_test = any(integration_test_path.glob(f'*{module_name}*.py'))
            has_e2e_test = any(Path('tests/e2e').glob(f'*{module_name}*.py'))

            if has_unit_test or has_integration_test or has_e2e_test:
                tested_modules.add(module_name)
                status = "✅"
            else:
                status = "❌"
                untested_modules.append({
                    'num': module_num,
                    'name': module_name,
                    'path': module_dir,
                    'has_model': (module_dir / 'model.py').exists()
                })

    # Ordenar por número
    untested_modules.sort(key=lambda x: x['num'])

    print(f"\nTotal módulos: {len(tested_modules) + len(untested_modules)}")
    print(f"Módulos con tests: {len(tested_modules)} ✅")
    print(f"Módulos sin tests: {len(untested_modules)} ❌\n")

    if untested_modules:
        print("Módulos SIN tests:")
        print("-" * 80)
        for mod in untested_modules:
            model_status = "🟢 (model.py)" if mod['has_model'] else "🟡 (sin model.py)"
            print(f"❌ {mod['num']:02}_{mod['name']} {model_status}")

    return untested_modules

def check_optimization_tests():
    """Verifica si las optimizaciones N+1 tienen tests."""
    print("\n" + "="*80)
    print("⚡ VERIFICACIÓN DE OPTIMIZACIONES N+1")
    print("="*80)

    optimizations = [
        ('03_herrajes', 4, 1, 'Herrajes'),
        ('08_administracion/recursos_humanos', 4, 1, 'Recursos Humanos'),
        ('11_usuarios', 5, 2, 'Usuarios'),
        ('10_auditoria', 5, 2, 'Auditoría'),
        ('07_compras', 13, 5, 'Compras'),
        ('05_logistica', 6, 2, 'Logística'),
    ]

    print("\nMódulos optimizados:")
    print("-" * 80)

    for module_path, before, after, name in optimizations:
        # Buscar test de optimización
        test_patterns = [
            f'tests/unit/*/test_*{name}*.py',
            f'tests/integration/test_*{name}*.py',
            f'tests/e2e/test_*{name}*.py',
        ]

        has_optimization_test = False
        for pattern in test_patterns:
            matches = list(Path('.').glob(pattern))
            if matches:
                # Verificar si el test verifica número de queries
                for test_file in matches:
                    content = test_file.read_text()
                    if 'query' in content.lower() and 'optimiz' in content.lower():
                        has_optimization_test = True
                        break

        if has_optimization_test:
            print(f"✅ {name:20} {before}→{after} queries - Tiene test de optimización")
        else:
            print(f"❌ {name:20} {before}→{after} queries - ⚠️ SIN TEST DE OPTIMIZACIÓN")

def generate_summary_report():
    """Genera reporte resumido."""
    print("\n" + "="*80)
    print("📋 RESUMEN EJECUTIVO")
    print("="*80)

    print("""
🎯 OBJETIVO: 99% Cobertura de Tests

📊 SITUACIÓN ACTUAL:
   - Tests existentes: ~110 tests
   - Cobertura estimada: ~50%
   - Tests que pasan: DESCONOCIDO (ejecutar para saber)
   - Módulos sin testear: ~6 módulos

⚠️ PROBLEMAS CRÍTICOS:
   1. Optimizaciones N+1 sin tests de verificación
   2. Módulos completos sin testear (Herrajes, Mantenimiento, etc.)
   3. Falta de tests E2E de workflows
   4. Tests de seguridad incompletos
   5. Sin tests de monitoreo

🚀 PLAN DE ACCIÓN INMEDIATO:
   1. Ejecutar tests y ver cuántos pasan
   2. Crear tests de optimizaciones N+1
   3. Crear tests E2E de workflows críticos
   4. Crear tests de módulos sin testear
   5. Completar suite de seguridad

⏱️  TIEMPO ESTIMADO PARA 99%:
   - Tests críticos inmediatos: 2-3 horas
   - Suite completa: 8-12 horas
    """)

if __name__ == '__main__':
    # Cambiar al directorio del proyecto
    import os
    os.chdir(Path(__file__).parent.parent)

    # Ejecutar diagnóstico
    returncode = run_pytest_with_coverage()

    # Analizar resultados
    coverage_data = analyze_coverage()
    untested = identify_untested_modules()
    check_optimization_tests()
    generate_summary_report()

    # Salir con código apropiado
    sys.exit(returncode)
