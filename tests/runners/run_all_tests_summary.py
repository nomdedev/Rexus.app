#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Resumen Final de Tests - Rexus.app
Ejecuta todos los tests unitarios y genera reporte completo
"""

import subprocess
import sys
import os
from pathlib import Path

# Configurar path y encoding
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
os.environ['PYTHONIOENCODING'] = 'utf-8'

def run_tests_by_module():
    """Ejecutar tests por módulo y generar resumen."""
    
    print("=" * 80)
    print("RESUMEN FINAL DE TESTS UNITARIOS - REXUS.APP")
    print("=" * 80)
    print()
    
    modules_to_test = [
        ('usuarios', 'Usuarios y Seguridad'),
        ('inventario', 'Inventario y Reportes'),
        ('configuracion', 'Configuración del Sistema'),
        ('compras', 'Compras y Proveedores'),
        ('obras', 'Obras y Proyectos'),
        ('administracion', 'Administración del Sistema'),
        ('auditoria', 'Auditoría y Compliance')
    ]
    
    results = {}
    total_passed = 0
    total_failed = 0
    total_errors = 0
    total_tests = 0
    
    for module_dir, module_name in modules_to_test:
        print(f"Ejecutando tests: {module_name}")
        print("-" * 50)
        
        try:
            # Ejecutar pytest para el módulo
            cmd = [
                sys.executable, '-m', 'pytest', 
                f'tests/unit/{module_dir}/', 
                '-v', '--tb=no'
            ]
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                cwd=Path(__file__).parent.parent.parent,
                timeout=60
            )
            
            # Parsear resultados
            output_lines = result.stdout.split('\n')
            
            passed = 0
            failed = 0 
            errors = 0
            
            for line in output_lines:
                if 'PASSED' in line:
                    passed += 1
                elif 'FAILED' in line:
                    failed += 1
                elif 'ERROR' in line:
                    errors += 1
            
            # Si no encontramos tests individuales, buscar en summary
            if passed == 0 and failed == 0 and errors == 0:
                for line in output_lines:
                    if ' passed' in line:
                        try:
                            passed = int(line.split(' passed')[0].split()[-1])
                        except (ValueError, IndexError):
                            pass
                    if ' failed' in line:
                        try:
                            failed = int(line.split(' failed')[0].split()[-1])
                        except (ValueError, IndexError):
                            pass
                    if ' error' in line:
                        try:
                            errors = int(line.split(' error')[0].split()[-1])
                        except (ValueError, IndexError):
                            pass
            
            module_total = passed + failed + errors
            
            results[module_name] = {
                'passed': passed,
                'failed': failed,
                'errors': errors,
                'total': module_total,
                'success_rate': (passed / module_total * 100) if module_total > 0 else 0
            }
            
            total_passed += passed
            total_failed += failed
            total_errors += errors
            total_tests += module_total
            
            # Mostrar resultado del módulo
            status_icon = "✅" if failed == 0 and errors == 0 else "❌" if failed > 0 or errors > 0 else "⚠️"
            print(f"{status_icon} {module_name}: {passed} PASSED, {failed} FAILED, {errors} ERRORS")
            if module_total > 0:
                print(f"   Success Rate: {passed/module_total*100:.1f}%")
            print()
            
        except subprocess.TimeoutExpired:
            print(f"❌ {module_name}: TIMEOUT")
            results[module_name] = {'passed': 0, 'failed': 0, 'errors': 1, 'total': 1, 'success_rate': 0}
            total_errors += 1
            total_tests += 1
            print()
        except Exception as e:
            print(f"❌ {module_name}: ERROR - {e}")
            results[module_name] = {'passed': 0, 'failed': 0, 'errors': 1, 'total': 1, 'success_rate': 0}
            total_errors += 1
            total_tests += 1
            print()
    
    # Resumen final
    print("=" * 80)
    print("RESUMEN FINAL")
    print("=" * 80)
    
    print(f"📊 ESTADÍSTICAS GENERALES:")
    print(f"   Total Tests Ejecutados: {total_tests}")
    print(f"   ✅ Tests PASSED: {total_passed}")
    print(f"   ❌ Tests FAILED: {total_failed}")
    print(f"   🚨 Tests ERRORS: {total_errors}")
    
    if total_tests > 0:
        success_rate = (total_passed / total_tests) * 100
        print(f"   📈 Success Rate Global: {success_rate:.1f}%")
        
        if success_rate >= 90:
            print("   🎉 ESTADO: EXCELENTE")
        elif success_rate >= 80:
            print("   👍 ESTADO: BUENO")
        elif success_rate >= 70:
            print("   ⚠️  ESTADO: REGULAR")
        else:
            print("   🚨 ESTADO: CRÍTICO")
    
    print(f"\n📋 DETALLE POR MÓDULO:")
    for module_name, stats in results.items():
        icon = "✅" if stats['success_rate'] == 100 else "⚠️" if stats['success_rate'] >= 80 else "❌"
        print(f"   {icon} {module_name}: {stats['passed']}/{stats['total']} ({stats['success_rate']:.1f}%)")
    
    # Recomendaciones
    print(f"\n🎯 PRÓXIMOS PASOS:")
    
    if total_failed > 0:
        print(f"   1. Corregir {total_failed} tests fallidos")
    
    if total_errors > 0:
        print(f"   2. Resolver {total_errors} errores de tests")
    
    if total_tests == 0:
        print("   1. No se encontraron tests - verificar estructura")
    elif success_rate < 90:
        print("   1. Mejorar tests para alcanzar >90% success rate")
    else:
        print("   1. Mantener alta calidad de tests")
        print("   2. Continuar con tests de integración y E2E")
    
    print("\n" + "=" * 80)
    return results

if __name__ == "__main__":
    results = run_tests_by_module()