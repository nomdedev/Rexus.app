#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick Test Runner - Ejecuta Tests Críticos

Ejecuta los tests más importantes para verificar rápidamente:
- Tests de optimizaciones N+1
- Tests E2E críticos
- Tests de seguridad críticos

Uso:
    python tests/quick_run.py
    python tests/quick_run.py --security
    python tests/quick_run.py --e2e
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Ejecuta un comando y muestra resultado."""
    print(f"\n{'='*80}")
    print(f"🧪 {description}")
    print(f"{'='*80}")
    print(f"Comando: {' '.join(cmd)}\n")

    result = subprocess.run(cmd, capture_output=False)

    if result.returncode == 0:
        print(f"✅ {description} - PASÓ")
    else:
        print(f"❌ {description} - FALLÓ (código: {result.returncode})")

    return result.returncode == 0


def main():
    """Función principal."""
    import argparse

    parser = argparse.ArgumentParser(description='Ejecuta tests críticos rápidamente')
    parser.add_argument('--optimizaciones', action='store_true', help='Tests de optimizaciones N+1')
    parser.add_argument('--e2e', action='store_true', help='Tests E2E de workflows')
    parser.add_argument('--security', action='store_true', help='Tests de seguridad')
    parser.add_argument('--all', action='store_true', help='Todos los tests críticos')

    args = parser.parse_args()

    # Cambiar al directorio del proyecto
    os.chdir(Path(__file__).parent.parent)

    print("\n" + "="*80)
    print("🚀 QUICK TEST RUNNER - Tests Críticos de Rexus.app")
    print("="*80)

    all_passed = True

    # Tests de optimizaciones N+1
    if args.optimizaciones or args.all:
        passed = run_command(
            [sys.executable, '-m', 'pytest', 'tests/optimizacion_n1/', '-v', '--tb=short'],
            "Tests de Optimización N+1 (Herrajes)"
        )
        all_passed = all_passed and passed

    # Tests E2E
    if args.e2e or args.all:
        passed = run_command(
            [sys.executable, '-m', 'pytest', 'tests/e2e/test_workflows_completos.py',
             '-v', '--tb=short', '-k', 'test_flujo_completo'],
            "Tests E2E de Workflows Completos"
        )
        all_passed = all_passed and passed

    # Tests de seguridad
    if args.security or args.all:
        passed = run_command(
            [sys.executable, '-m', 'pytest', 'tests/security/test_security_complete.py',
             '-v', '--tb=short', '-k', 'sql_injection'],
            "Tests de Seguridad (SQL Injection)"
        )
        all_passed = all_passed and passed

    # Si no hay argumentos, ejecutar todos
    if not any([args.optimizaciones, args.e2e, args.security, args.all]):
        print("\n🎯 Ejecutando todos los tests críticos...\n")
        all_passed = main()
        return

    # Resumen
    print("\n" + "="*80)
    if all_passed:
        print("✅ TODOS LOS TESTS CRÍTICOS PASARON")
    else:
        print("❌ ALGUNOS TESTS FALLARON - Revisar logs arriba")
    print("="*80)

    return 0 if all_passed else 1


if __name__ == '__main__':
    import os
    sys.exit(main())
