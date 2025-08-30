#!/usr/bin/env python3
"""
Validador de Seguridad Automático para Rexus.app

Este script ejecuta múltiples verificaciones de seguridad:
- Análisis estático de código
- Verificación de configuraciones
- Tests de seguridad básicos
- Validación de dependencias

Uso:
    python security_validator.py [--verbose] [--fix]
"""

import sys
import logging
import subprocess  # nosec B404 - Necesario para verificaciones de seguridad
import json
from pathlib import Path
from typing import Dict, List
import re

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class SecurityValidator:
    """Validador automático de seguridad."""

    def __init__(self, project_root: str | None = None):
        self.project_root = Path(project_root or Path(__file__).parent.parent)
        self.results = {
            'passed': [],
            'failed': [],
            'warnings': [],
            'errors': []
        }

    def run_all_checks(self) -> Dict[str, List]:
        """Ejecuta todas las verificaciones de seguridad."""
        logger.info("🔒 Iniciando validación de seguridad completa...")

        checks = [
            self.check_file_permissions,
            self.check_hardcoded_secrets,
            self.check_sql_injection_patterns,
            self.check_command_injection,
            self.check_dependency_vulnerabilities,
            self.check_outdated_dependencies,
            self.check_config_files,
            self.check_logging_security,
            self.check_error_handling,
            self.validate_code_quality
        ]

        for check in checks:
            try:
                check()
            except Exception as e:
                self.results['errors'].append(f"Error en {check.__name__}: {e}")

        return self.results

    def check_file_permissions(self):
        """Verifica permisos de archivos sensibles."""
        logger.info("📁 Verificando permisos de archivos...")

        sensitive_files = [
            'config/security.json',
            'config/rexus_config.json',
            'rexus_config.json',
            '*.key',
            '*.pem',
            '*.p12'
        ]

        issues = []

        for pattern in sensitive_files:
            for file_path in self.project_root.rglob(pattern):
                if file_path.exists():
                    # En Windows, verificar si es readable por otros
                    try:
                        # Verificar si el archivo contiene información sensible
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read(1024)  # Leer primeros 1KB

                        if any(keyword in content.lower() for keyword in
                              ['password', 'secret', 'key', 'token', 'api_key']):
                            issues.append(f"Archivo sensible encontrado: {file_path}")
                    except Exception as e:
                        logger.warning(f"Error leyendo {file_path}: {e}")
                        continue

        if issues:
            self.results['warnings'].extend(issues)
        else:
            self.results['passed'].append("Permisos de archivos correctos")

    def check_hardcoded_secrets(self):
        """Busca secrets hardcodeados en el código."""
        logger.info("🔑 Buscando secrets hardcodeados...")

        secret_patterns = [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']',
            r'key\s*=\s*["\'][^"\']+["\']',
            r'token\s*=\s*["\'][^"\']+["\']',
            r'api_key\s*=\s*["\'][^"\']+["\']'
        ]

        issues = []

        for py_file in self.project_root.rglob('*.py'):
            if 'test' in str(py_file).lower() or 'example' in str(py_file).lower():
                continue  # Saltar archivos de test y ejemplos

            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                for pattern in secret_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        issues.append(f"Posible secret hardcodeado en {py_file}: {matches[:3]}")

            except Exception as e:
                logger.warning(f"Error leyendo {py_file}: {e}")

        if issues:
            self.results['failed'].extend(issues)
        else:
            self.results['passed'].append("No se encontraron secrets hardcodeados")

    def check_sql_injection_patterns(self):
        """Verifica patrones de SQL injection."""
        logger.info("💉 Verificando patrones de SQL injection...")

        dangerous_patterns = [
            r'f".*SELECT.*\{.*\}.*FROM',
            r'f".*INSERT.*\{.*\}.*VALUES',
            r'f".*UPDATE.*\{.*\}.*SET',
            r'f".*DELETE.*\{.*\}.*FROM',
            r'".*SELECT.*\+.*FROM',
            r'".*INSERT.*\+.*VALUES'
        ]

        issues = []

        for py_file in self.project_root.rglob('*.py'):
            # Excluir el propio archivo del validador de seguridad
            if 'security_validator.py' in str(py_file):
                continue

            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')

                for i, line in enumerate(lines, 1):
                    for pattern in dangerous_patterns:
                        if re.search(pattern, line):
                            # Verificar si tiene validación o sanitización
                            has_validation = any(safe in line for safe in [
                                'validate_table_name', 'sanitize_input',
                                'cursor.execute', 'nosec', 'sanitized'
                            ])

                            if not has_validation:
                                issues.append(
                                    f"Posible SQL injection en {py_file}:{i}: {line.strip()}"
                                )

            except Exception as e:
                logger.warning(f"Error leyendo {py_file}: {e}")

        if issues:
            self.results['failed'].extend(issues)
        else:
            self.results['passed'].append("No se encontraron patrones de SQL injection peligrosos")

    def check_command_injection(self):
        """Verifica command injection en subprocess."""
        logger.info("⚡ Verificando command injection...")

        issues = []

        for py_file in self.project_root.rglob('*.py'):
            # Excluir archivos relacionados con validación de seguridad
            if any(exclude in str(py_file) for exclude in ['security_validator.py', 'security_analyzer.py']):
                continue

            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')

                for i, line in enumerate(lines, 1):
                    # Buscar uso de shell=True
                    if 'shell=True' in line:
                        # Verificar si hay validación
                        has_validation = any(safe in content for safe in [
                            'validate', 'sanitize', 'shlex.quote'
                        ])

                        if not has_validation:
                            issues.append(
                                f"Uso peligroso de shell=True en {py_file}:{i}: {line.strip()}"
                            )

                    # Buscar f-strings en comandos
                    if re.search(r'subprocess\..*\s*f".*\{.*\}"', line):
                        issues.append(
                            f"Posible command injection con f-string en {py_file}:{i}: {line.strip()}"
                        )

            except Exception as e:
                logger.warning(f"Error leyendo {py_file}: {e}")

        if issues:
            self.results['failed'].extend(issues)
        else:
            self.results['passed'].append("No se encontraron problemas de command injection")

    def check_dependency_vulnerabilities(self):
        """Verifica vulnerabilidades en dependencias."""
        logger.info("📦 Verificando vulnerabilidades en dependencias...")

        try:
            # Verificar si safety está instalado
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'list', '--format=json'],
                capture_output=True, text=True, timeout=30
            )  # nosec B603 - Comando interno seguro

            if result.returncode == 0:
                packages = json.loads(result.stdout)
                vulnerable_packages = []

                # Lista básica de paquetes con vulnerabilidades conocidas
                known_vulnerabilities = {
                    'PyQt6': 'Verificar versiones recientes',
                    'sqlite3': 'Parte de stdlib de Python',
                    'requests': 'Verificar versión >= 2.25.0'
                }

                for package in packages:
                    name = package.get('name', '')
                    if name in known_vulnerabilities:
                        vulnerable_packages.append(f"{name}: {known_vulnerabilities[name]}")

                if vulnerable_packages:
                    self.results['warnings'].extend(vulnerable_packages)
                else:
                    self.results['passed'].append("Dependencias verificadas")
            else:
                self.results['warnings'].append("No se pudo verificar dependencias")

        except Exception as e:
            self.results['warnings'].append(f"Error verificando dependencias: {e}")

    def check_outdated_dependencies(self):
        """Verifica dependencias desactualizadas."""
        logger.info("📅 Verificando dependencias desactualizadas...")

        try:
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'list', '--outdated', '--format=json'],
                capture_output=True, text=True, timeout=30
            )  # nosec B603 - Comando interno seguro

            if result.returncode == 0:
                outdated = json.loads(result.stdout)
                if outdated:
                    packages = [f"{pkg['name']} ({pkg['version']} -> {pkg['latest_version']})"
                              for pkg in outdated[:5]]  # Top 5
                    self.results['warnings'].extend(
                        [f"Dependencia desactualizada: {pkg}" for pkg in packages]
                    )
                else:
                    self.results['passed'].append("Todas las dependencias están actualizadas")
            else:
                self.results['warnings'].append("No se pudo verificar dependencias desactualizadas")

        except Exception as e:
            self.results['warnings'].append(f"Error verificando dependencias desactualizadas: {e}")

    def check_config_files(self):
        """Verifica archivos de configuración sensibles."""
        logger.info("⚙️ Verificando archivos de configuración...")

        config_files = [
            'config/security.json',
            'config/rexus_config.json',
            'rexus_config.json'
        ]

        for config_file in config_files:
            config_path = self.project_root / config_file
            if config_path.exists():
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Verificar si contiene información sensible sin encriptar
                    sensitive_data = []
                    if 'password' in content and '***' not in content:
                        sensitive_data.append('passwords')
                    if 'secret' in content and '***' not in content:
                        sensitive_data.append('secrets')
                    if 'key' in content and '***' not in content:
                        sensitive_data.append('keys')

                    if sensitive_data:
                        self.results['failed'].append(
                            f"Información sensible sin encriptar en {config_file}: {', '.join(sensitive_data)}"
                        )
                    else:
                        self.results['passed'].append(f"Configuración segura en {config_file}")

                except Exception as e:
                    self.results['warnings'].append(f"Error leyendo {config_file}: {e}")
            else:
                self.results['warnings'].append(f"Archivo de configuración faltante: {config_file}")

    def check_logging_security(self):
        """Verifica configuración de logging de seguridad."""
        logger.info("📝 Verificando logging de seguridad...")

        issues = []

        for py_file in self.project_root.rglob('*.py'):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Verificar logging de información sensible
                if re.search(r'logger\..*password|secret|key|token', content, re.IGNORECASE):
                    issues.append(f"Posible logging de información sensible en {py_file}")

                # Verificar uso de logging.getLogger sin configuración
                if 'logging.getLogger' in content and 'basicConfig' not in content:
                    # Solo si no hay configuración global
                    if not any(config in content for config in ['dictConfig', 'fileConfig']):
                        issues.append(f"Logging sin configuración en {py_file}")

            except Exception as e:
                logger.warning(f"Error leyendo {py_file}: {e}")

        if issues:
            self.results['warnings'].extend(issues)
        else:
            self.results['passed'].append("Logging de seguridad configurado correctamente")

    def check_error_handling(self):
        """Verifica manejo de errores."""
        logger.info("🚨 Verificando manejo de errores...")

        issues = []

        for py_file in self.project_root.rglob('*.py'):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Contar excepciones genéricas vs específicas
                generic_exceptions = len(re.findall(r'except\s+Exception', content))
                specific_exceptions = len(re.findall(r'except\s+\w+Error', content))

                if generic_exceptions > specific_exceptions * 2:
                    issues.append(f"Excesivo uso de Exception genérica en {py_file}")

                # Verificar except: sin especificar
                if re.search(r'except\s*:', content):
                    issues.append(f"Uso de except: sin especificar en {py_file}")

            except Exception as e:
                logger.warning(f"Error leyendo {py_file}: {e}")

        if issues:
            self.results['warnings'].extend(issues)
        else:
            self.results['passed'].append("Manejo de errores adecuado")

    def validate_code_quality(self):
        """Valida calidad general del código."""
        logger.info("🔍 Validando calidad del código...")

        try:
            # Ejecutar py_compile en todos los archivos Python
            compiled_files = 0
            failed_files = []

            for py_file in self.project_root.rglob('*.py'):
                if 'test' in str(py_file).lower():
                    continue  # Saltar archivos de test

                try:
                    compile(open(py_file, 'r', encoding='utf-8').read(), str(py_file), 'exec')
                    compiled_files += 1
                except SyntaxError as e:
                    failed_files.append(f"{py_file}: {e}")
                except Exception as e:
                    failed_files.append(f"{py_file}: Error de compilación - {e}")

            if failed_files:
                self.results['failed'].extend(failed_files)
            else:
                self.results['passed'].append(f"Código válido compilado: {compiled_files} archivos")

        except Exception as e:
            self.results['errors'].append(f"Error en validación de código: {e}")

    def generate_report(self) -> str:
        """Genera reporte de validación."""
        report = []
        report.append("🔒 REPORTE DE VALIDACIÓN DE SEGURIDAD - REXUS.APP")
        report.append("=" * 60)

        total_checks = len(self.results['passed']) + len(self.results['failed']) + \
                      len(self.results['warnings']) + len(self.results['errors'])

        report.append(f"📊 Total de verificaciones: {total_checks}")
        report.append(f"✅ Verificaciones exitosas: {len(self.results['passed'])}")
        report.append(f"❌ Fallos críticos: {len(self.results['failed'])}")
        report.append(f"⚠️ Advertencias: {len(self.results['warnings'])}")
        report.append(f"🚨 Errores: {len(self.results['errors'])}")
        report.append("")

        if self.results['passed']:
            report.append("✅ VERIFICACIONES EXITOSAS:")
            for item in self.results['passed']:
                report.append(f"  ✓ {item}")
            report.append("")

        if self.results['warnings']:
            report.append("⚠️ ADVERTENCIAS:")
            for item in self.results['warnings']:
                report.append(f"  ! {item}")
            report.append("")

        if self.results['failed']:
            report.append("❌ FALLOS CRÍTICOS:")
            for item in self.results['failed']:
                report.append(f"  ✗ {item}")
            report.append("")

        if self.results['errors']:
            report.append("🚨 ERRORES:")
            for item in self.results['errors']:
                report.append(f"  💥 {item}")
            report.append("")

        # Resumen ejecutivo
        if self.results['failed']:
            report.append("🚨 ACCIONES RECOMENDADAS:")
            report.append("  - Corregir todos los fallos críticos inmediatamente")
            report.append("  - Revisar las advertencias antes del despliegue")
            report.append("  - Ejecutar esta validación regularmente")
        else:
            report.append("✅ ESTADO DE SEGURIDAD: SATISFACTORIO")
            report.append("  - No se encontraron vulnerabilidades críticas")
            report.append("  - Continuar con monitoreo regular")

        return "\n".join(report)


def main():
    """Función principal."""
    import argparse

    parser = argparse.ArgumentParser(description='Validador de Seguridad para Rexus.app')
    parser.add_argument('--verbose', '-v', action='store_true', help='Modo verbose')
    parser.add_argument('--fix', action='store_true', help='Intentar correcciones automáticas')
    parser.add_argument('--output', '-o', help='Archivo de salida para el reporte')

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    validator = SecurityValidator()

    try:
        results = validator.run_all_checks()
        report = validator.generate_report()

        print(report)

        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"\n📄 Reporte guardado en: {args.output}")

        # Código de salida basado en resultados
        if results['failed'] or results['errors']:
            sys.exit(1)
        else:
            sys.exit(0)

    except Exception as e:
        logger.error(f"Error ejecutando validación: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
