#!/usr/bin/env python3
"""
🔧 Development Scripts - Rexus.app v2.0.0
========================================

Scripts de desarrollo automatizados para facilitar el workflow.
Basado en mejores prácticas de Python packaging.

Uso:
    python scripts/dev.py format       # Formatear código
    python scripts/dev.py lint         # Verificar calidad
    python scripts/dev.py test         # Ejecutar tests
    python scripts/dev.py all          # Ejecutar todo
"""

import subprocess
import sys
from pathlib import Path
from typing import List, Tuple
import argparse


class Colors:
    """Colores para terminal"""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_success(msg: str):
    """Imprime mensaje de éxito"""
    print(f"{Colors.GREEN}✅ {msg}{Colors.END}")


def print_warning(msg: str):
    """Imprime mensaje de advertencia"""
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.END}")


def print_error(msg: str):
    """Imprime mensaje de error"""
    print(f"{Colors.RED}❌ {msg}{Colors.END}")


def print_info(msg: str):
    """Imprime mensaje informativo"""
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.END}")


def run_command(
    command: List[str],
    description: str,
    check: bool = True
) -> Tuple[bool, str]:
    """
    Ejecuta un comando y retorna el resultado.

    Args:
        command: Comando a ejecutar
        description: Descripción del comando
        check: Si debe lanzar excepción en error

    Returns:
        Tuple (exitoso, output)
    """
    print_info(f"Ejecutando: {description}")
    print(f"   Comando: {' '.join(command)}\n")

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=check
        )

        if result.returncode == 0:
            print_success(f"{description} - Completado")
            return True, result.stdout
        else:
            print_error(f"{description} - Falló")
            return False, result.stderr

    except subprocess.CalledProcessError as e:
        print_error(f"{description} - Error")
        return False, str(e)
    except FileNotFoundError:
        print_error(f"Comando no encontrado: {command[0]}")
        print_info("Instala las dependencias: pip install -r requirements-dev.txt")
        return False, ""


def format_code(check_only: bool = False):
    """
    Formatea código con Black e isort

    Args:
        check_only: Si es True, solo verifica sin modificar
    """
    print(f"\n{Colors.BOLD}{'='*60}")
    print("🎨 FORMATEANDO CÓDIGO")
    print(f"{'='*60}{Colors.END}\n")

    success = True

    # Black - Formateador de código
    black_cmd = ["black", "rexus/", "tests/"]
    if check_only:
        black_cmd.insert(1, "--check")

    ok, _ = run_command(
        black_cmd,
        "Black - Formateador de código",
        check=False
    )
    success = success and ok

    # isort - Organizador de imports
    isort_cmd = ["isort", "rexus/", "tests/"]
    if check_only:
        isort_cmd.insert(1, "--check-only")

    ok, _ = run_command(
        isort_cmd,
        "isort - Organizador de imports",
        check=False
    )
    success = success and ok

    return success


def lint_code():
    """Ejecuta linters para verificar calidad de código"""
    print(f"\n{Colors.BOLD}{'='*60}")
    print("🔍 ANALIZANDO CALIDAD DE CÓDIGO")
    print(f"{'='*60}{Colors.END}\n")

    success = True

    # Flake8 - PEP 8
    ok, _ = run_command(
        ["flake8", "rexus/", "tests/",
         "--max-line-length=100",
         "--extend-ignore=E203,W503",
         "--statistics"],
        "Flake8 - Verificación PEP 8",
        check=False
    )
    success = success and ok

    # Pylint - Análisis profundo
    ok, _ = run_command(
        ["pylint", "rexus/",
         "--fail-under=8.0",
         "--max-complexity=10"],
        "Pylint - Análisis de calidad",
        check=False
    )
    success = success and ok

    # MyPy - Type checking
    ok, _ = run_command(
        ["mypy", "rexus/", "--strict"],
        "MyPy - Verificación de tipos",
        check=False
    )
    success = success and ok

    # Bandit - Security
    ok, _ = run_command(
        ["bandit", "-r", "rexus/", "-f", "json"],
        "Bandit - Análisis de seguridad",
        check=False
    )
    success = success and ok

    return success


def run_tests(
    coverage: bool = True,
    verbose: bool = True,
    parallel: bool = True,
    target: str = None
):
    """
    Ejecuta tests con pytest

    Args:
        coverage: Si debe generar reporte de cobertura
        verbose: Si debe ser verbose
        parallel: Si debe ejecutar en paralelo
        target: Directorio específico de tests
    """
    print(f"\n{Colors.BOLD}{'='*60}")
    print("🧪 EJECUTANDO TESTS")
    print(f"{'='*60}{Colors.END}\n")

    command = ["pytest"]

    if verbose:
        command.append("-v")

    if parallel:
        command.extend(["-n", "auto"])

    if coverage:
        command.extend([
            "--cov=rexus",
            "--cov-report=html",
            "--cov-report=term-missing",
            "--cov-fail-under=50"
        ])

    if target:
        command.append(target)
    else:
        command.append("tests/")

    ok, _ = run_command(command, "Pytest - Suite de tests", check=False)

    return ok


def run_security_scan():
    """Ejecuta escaneo de seguridad completo"""
    print(f"\n{Colors.BOLD}{'='*60}")
    print("🔒 ESCANEO DE SEGURIDAD")
    print(f"{'='*60}{Colors.END}\n")

    success = True

    # Bandit - Security linter
    ok, output = run_command(
        ["bandit", "-r", "rexus/", "-f", "json"],
        "Bandit - Vulnerabilidades de seguridad",
        check=False
    )
    success = success and ok

    # Safety - Vulnerabilidades en dependencias
    ok, _ = run_command(
        ["safety", "check", "--json"],
        "Safety - Dependencias vulnerables",
        check=False
    )
    success = success and ok

    return success


def install_dev_dependencies():
    """Instala dependencias de desarrollo"""
    print(f"\n{Colors.BOLD}{'='*60}")
    print("📦 INSTALANDO DEPENDENCIAS DE DESARROLLO")
    print(f"{'='*60}{Colors.END}\n")

    ok, _ = run_command(
        ["pip", "install", "-r", "requirements-dev.txt"],
        "Instalando dependencias de desarrollo"
    )

    if ok:
        print_success("Dependencias instaladas correctamente")
        print_info("Ahora puedes ejecutar: python scripts/dev.py setup")

    return ok


def setup_pre_commit():
    """Configura pre-commit hooks"""
    print(f"\n{Colors.BOLD}{'='*60}")
    print("🎣 CONFIGURANDO PRE-COMMIT HOOKS")
    print(f"{'='*60}{Colors.END}\n")

    ok, _ = run_command(
        ["pre-commit", "install"],
        "Instalando pre-commit hooks"
    )

    if ok:
        print_success("Pre-commit hooks instalados")
        print_info("Se ejecutarán automáticamente antes de cada commit")

    return ok


def run_all(fix: bool = False):
    """
    Ejecuta todo el pipeline de calidad

    Args:
        fix: Si es True, formatea código automáticamente
    """
    print(f"\n{Colors.BLUE}{Colors.BOLD}")
    print("╔" + "═"*58 + "╗")
    print("║" + "  🔍 PIPELINE COMPLETO DE CALIDAD DE CÓDIGO  ".center(58) + "║")
    print("╚" + "═"*58 + "╝")
    print(f"{Colors.END}\n")

    results = {}

    # 1. Formatear código
    if fix:
        results["format"] = format_code(check_only=False)
    else:
        results["format"] = format_code(check_only=True)

    # 2. Linting
    results["lint"] = lint_code()

    # 3. Tests
    results["tests"] = run_tests()

    # 4. Security scan
    results["security"] = run_security_scan()

    # Resumen
    print(f"\n{Colors.BOLD}{'='*60}")
    print("📊 RESUMEN DE RESULTADOS")
    print(f"{'='*60}{Colors.END}\n")

    all_passed = True
    for step, result in results.items():
        status = f"{Colors.GREEN}✅ PASS{Colors.END}" if result else f"{Colors.RED}❌ FAIL{Colors.END}"
        print(f"  {step.upper():15} {status}")
        all_passed = all_passed and result

    print(f"\n{'='*60}\n")

    if all_passed:
        print_success(f"🎉 Todos los checks pasaron correctamente")
        return 0
    else:
        print_error(f"❌ Algunos checks fallaron")
        print_info("Revisa los errores arriba y ejecuta: python scripts/dev.py all --fix")
        return 1


def main():
    """Función principal"""
    parser = argparse.ArgumentParser(
        description="Scripts de desarrollo - Rexus.app",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python scripts/dev.py format          # Formatear código
  python scripts/dev.py lint            # Verificar calidad
  python scripts/dev.py test            # Ejecutar tests
  python scripts/dev.py security        # Escaneo de seguridad
  python scripts/dev.py all             # Ejecutar todo
  python scripts/dev.py all --fix       # Ejecutar y corregir automáticamente
  python scripts/dev.py setup           # Configurar pre-commit hooks
        """
    )

    parser.add_argument(
        "command",
        choices=["format", "lint", "test", "security", "all", "install", "setup"],
        help="Comando a ejecutar"
    )

    parser.add_argument(
        "--fix",
        action="store_true",
        help="Corregir automáticamente los problemas encontrados"
    )

    parser.add_argument(
        "--no-coverage",
        action="store_true",
        help="No generar reporte de cobertura en tests"
    )

    parser.add_argument(
        "--target",
        help="Directorio específico (ej: tests/security/)"
    )

    args = parser.parse_args()

    # Ejecutar comando
    if args.command == "format":
        success = format_code(check_only=not args.fix)
    elif args.command == "lint":
        success = lint_code()
    elif args.command == "test":
        success = run_tests(
            coverage=not args.no_coverage,
            target=args.target
        )
    elif args.command == "security":
        success = run_security_scan()
    elif args.command == "all":
        success = run_all(fix=args.fix) == 0
    elif args.command == "install":
        success = install_dev_dependencies()
    elif args.command == "setup":
        success = setup_pre_commit()
    else:
        parser.print_help()
        return 1

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
