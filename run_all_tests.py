#!/usr/bin/env python3
"""
Runner Principal de Tests - Rexus.app

Script centralizado para ejecutar todos los tipos de tests del sistema
y generar reportes completos de cobertura y calidad.

Uso:
    python run_all_tests.py [--type unit|integration|visual|security|performance|all]
    python run_all_tests.py [--coverage] [--report] [--verbose]
"""

import os
import sys
import subprocess
import argparse
import time
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Configuración de rutas
PROJECT_ROOT = Path(__file__).parent
TESTS_ROOT = PROJECT_ROOT / "tests"
REPORTS_DIR = PROJECT_ROOT / "test_reports"
COVERAGE_DIR = REPORTS_DIR / "coverage"

# Configuración de tests por tipo
TEST_TYPES = {
    "unit": {
        "path": "tests/unit",
        "pattern": "test_*.py",
        "description": "Tests unitarios de lógica de negocio"
    },
    "integration": {
        "path": "tests/integration", 
        "pattern": "test_*_integration.py",
        "description": "Tests de integración entre módulos"
    },
    "visual": {
        "path": "tests/visual",
        "pattern": "test_*_visual*.py",
        "description": "Tests visuales híbridos de UI"
    },
    "security": {
        "path": "tests/security",
        "pattern": "test_*_security.py",
        "description": "Tests de seguridad y vulnerabilidades"
    },
    "performance": {
        "path": "tests/performance",
        "pattern": "test_*_performance.py",
        "description": "Tests de rendimiento y carga"
    },
    "e2e": {
        "path": "tests/e2e",
        "pattern": "test_*_e2e.py",
        "description": "Tests end-to-end completos"
    },
    "usability": {
        "path": "tests/usability",
        "pattern": "test_*_usability.py",
        "description": "Tests de usabilidad y accesibilidad"
    }
}

class TestRunner:
    """Ejecutor principal de tests con reporting avanzado."""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results = {}
        self.start_time = None
        self.end_time = None
        self.setup_directories()
    
    def setup_directories(self):
        """Crea directorios necesarios para reportes."""
        REPORTS_DIR.mkdir(exist_ok=True)
        COVERAGE_DIR.mkdir(exist_ok=True)
        
        for test_type in TEST_TYPES.keys():
            (REPORTS_DIR / test_type).mkdir(exist_ok=True)
    
    def log(self, message: str, level: str = "INFO"):
        """Log con timestamp."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = {
            "INFO": "ℹ️",
            "SUCCESS": "✅", 
            "ERROR": "❌",
            "WARNING": "⚠️",
            "DEBUG": "🔍"
        }.get(level, "📝")
        
        print(f"[{timestamp}] {prefix} {message}")
        
        if self.verbose and level == "DEBUG":
            print(f"    {message}")
    
    def run_command(self, command: List[str], cwd: Optional[Path] = None) -> Dict:
        """Ejecuta comando y retorna resultado."""
        try:
            self.log(f"Ejecutando: {' '.join(command)}", "DEBUG")
            
            result = subprocess.run(
                command,
                cwd=cwd or PROJECT_ROOT,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutos timeout
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
            
        except subprocess.TimeoutExpired:
            self.log("Comando timeout después de 5 minutos", "ERROR")
            return {
                "success": False,
                "stdout": "",
                "stderr": "Timeout",
                "returncode": -1
            }
        except Exception as e:
            self.log(f"Error ejecutando comando: {e}", "ERROR")
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "returncode": -1
            }
    
    def check_dependencies(self) -> bool:
        """Verifica dependencias necesarias."""
        self.log("Verificando dependencias...", "INFO")
        
        dependencies = [
            ("python", "--version"),
            ("pytest", "--version"),
            ("coverage", "--version")
        ]
        
        missing = []
        for dep, version_flag in dependencies:
            result = self.run_command([dep, version_flag])
            if not result["success"]:
                missing.append(dep)
        
        if missing:
            self.log(f"Dependencias faltantes: {', '.join(missing)}", "ERROR")
            self.log("Instalar con: pip install pytest coverage pytest-cov pytest-html", "INFO")
            return False
        
        self.log("Todas las dependencias están disponibles", "SUCCESS")
        return True
    
    def discover_tests(self, test_type: str) -> List[Path]:
        """Descubre tests de un tipo específico."""
        if test_type not in TEST_TYPES:
            return []
        
        config = TEST_TYPES[test_type]
        test_path = PROJECT_ROOT / config["path"]
        
        if not test_path.exists():
            self.log(f"Directorio {test_path} no existe", "WARNING")
            return []
        
        # Buscar archivos de test
        pattern = config["pattern"]
        tests = list(test_path.rglob(pattern))
        
        self.log(f"Encontrados {len(tests)} tests de tipo {test_type}", "INFO")
        return tests
    
    def run_pytest(self, test_type: str, tests: List[Path], with_coverage: bool = False) -> Dict:
        """Ejecuta pytest para un tipo de test específico."""
        if not tests:
            return {
                "success": True,
                "tests_run": 0,
                "passed": 0,
                "failed": 0,
                "skipped": 0,
                "duration": 0,
                "coverage": None
            }
        
        # Preparar comando pytest
        cmd = ["python", "-m", "pytest"]
        
        # Agregar paths de tests
        for test in tests:
            cmd.append(str(test))
        
        # Configuración común
        cmd.extend([
            "-v",  # Verbose
            "--tb=short",  # Traceback corto
            f"--junit-xml={REPORTS_DIR / test_type / 'results.xml'}",
            f"--html={REPORTS_DIR / test_type / 'report.html'}",
            "--self-contained-html"
        ])
        
        # Coverage si se solicita
        if with_coverage:
            cmd.extend([
                "--cov=rexus",
                "--cov-report=html:" + str(COVERAGE_DIR / test_type),
                "--cov-report=xml:" + str(REPORTS_DIR / test_type / "coverage.xml"),
                "--cov-report=term"
            ])
        
        self.log(f"Ejecutando tests {test_type}...", "INFO")
        start_time = time.time()
        
        result = self.run_command(cmd)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Parsear resultados
        stats = self.parse_pytest_output(result["stdout"])
        stats["duration"] = duration
        stats["success"] = result["success"]
        
        if result["success"]:
            self.log(f"Tests {test_type} completados en {duration:.2f}s", "SUCCESS")
        else:
            self.log(f"Tests {test_type} fallaron", "ERROR")
            if self.verbose:
                self.log(f"STDERR: {result['stderr']}", "DEBUG")
        
        return stats
    
    def parse_pytest_output(self, output: str) -> Dict:
        """Parsea output de pytest para extraer estadísticas."""
        stats = {
            "tests_run": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "errors": 0
        }
        
        # Buscar línea de resumen (ej: "5 passed, 2 failed, 1 skipped")
        lines = output.split('\\n')
        for line in lines:
            if 'passed' in line or 'failed' in line or 'skipped' in line:
                # Parsear números
                import re
                
                passed_match = re.search(r'(\\d+) passed', line)
                if passed_match:
                    stats["passed"] = int(passed_match.group(1))
                
                failed_match = re.search(r'(\\d+) failed', line)
                if failed_match:
                    stats["failed"] = int(failed_match.group(1))
                
                skipped_match = re.search(r'(\\d+) skipped', line)
                if skipped_match:
                    stats["skipped"] = int(skipped_match.group(1))
                
                error_match = re.search(r'(\\d+) error', line)
                if error_match:
                    stats["errors"] = int(error_match.group(1))
                
                break
        
        stats["tests_run"] = stats["passed"] + stats["failed"] + stats["skipped"] + stats["errors"]
        return stats
    
    def run_type_tests(self, test_type: str, with_coverage: bool = False) -> Dict:
        """Ejecuta todos los tests de un tipo específico."""
        self.log(f"Iniciando tests de tipo: {test_type.upper()}", "INFO")
        
        config = TEST_TYPES[test_type]
        self.log(f"Descripción: {config['description']}", "INFO")
        
        # Descubrir tests
        tests = self.discover_tests(test_type)
        
        if not tests:
            self.log(f"No se encontraron tests para {test_type}", "WARNING")
            return {
                "success": True,
                "tests_run": 0,
                "message": "No tests found"
            }
        
        # Ejecutar tests
        result = self.run_pytest(test_type, tests, with_coverage)
        
        # Guardar resultado
        self.results[test_type] = result
        
        return result
    
    def run_all_tests(self, test_types: List[str], with_coverage: bool = False) -> Dict:
        """Ejecuta todos los tipos de tests especificados."""
        self.start_time = datetime.now()
        self.log("🚀 Iniciando ejecución completa de tests", "INFO")
        
        # Verificar dependencias
        if not self.check_dependencies():
            return {"success": False, "message": "Dependencies missing"}
        
        # Ejecutar cada tipo de test
        total_stats = {
            "tests_run": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "errors": 0,
            "total_duration": 0
        }
        
        for test_type in test_types:
            if test_type not in TEST_TYPES:
                self.log(f"Tipo de test '{test_type}' no válido", "WARNING")
                continue
            
            result = self.run_type_tests(test_type, with_coverage)
            
            # Acumular estadísticas
            for key in ["tests_run", "passed", "failed", "skipped", "errors"]:
                if key in result:
                    total_stats[key] += result[key]
            
            if "duration" in result:
                total_stats["total_duration"] += result["duration"]
        
        self.end_time = datetime.now()
        
        # Generar reporte final
        total_stats["success"] = total_stats["failed"] == 0 and total_stats["errors"] == 0
        total_stats["execution_time"] = (self.end_time - self.start_time).total_seconds()
        
        self.generate_summary_report(total_stats)
        
        return total_stats
    
    def generate_summary_report(self, stats: Dict):
        """Genera reporte resumen de toda la ejecución."""
        self.log("📊 Generando reporte resumen...", "INFO")
        
        # Reporte en consola
        print("\\n" + "="*60)
        print("📋 REPORTE RESUMEN DE TESTS - REXUS.APP")
        print("="*60)
        print(f"🕐 Inicio: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🏁 Fin: {self.end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⏱️  Duración total: {stats['execution_time']:.2f}s")
        print()
        
        # Estadísticas por tipo
        print("📈 ESTADÍSTICAS POR TIPO:")
        for test_type, result in self.results.items():
            status = "✅" if result.get("success", False) else "❌"
            duration = result.get("duration", 0)
            tests_run = result.get("tests_run", 0)
            passed = result.get("passed", 0)
            failed = result.get("failed", 0)
            
            print(f"  {status} {test_type.upper()}: {passed}/{tests_run} tests ({duration:.2f}s)")
            if failed > 0:
                print(f"    ⚠️  {failed} tests fallaron")
        
        print()
        print("📊 TOTALES:")
        print(f"  🧪 Tests ejecutados: {stats['tests_run']}")
        print(f"  ✅ Exitosos: {stats['passed']}")
        print(f"  ❌ Fallidos: {stats['failed']}")
        print(f"  ⏭️  Omitidos: {stats['skipped']}")
        print(f"  🚫 Errores: {stats['errors']}")
        
        if stats['tests_run'] > 0:
            success_rate = (stats['passed'] / stats['tests_run']) * 100
            print(f"  📈 Tasa de éxito: {success_rate:.1f}%")
        
        print()
        status_final = "✅ TODOS LOS TESTS PASARON" if stats['success'] else "❌ HAY TESTS FALLIDOS"
        print(f"🎯 RESULTADO FINAL: {status_final}")
        print("="*60)
        
        # Guardar reporte JSON
        report_data = {
            "timestamp": self.start_time.isoformat(),
            "execution_time": stats['execution_time'],
            "total_stats": stats,
            "results_by_type": self.results
        }
        
        report_file = REPORTS_DIR / f"summary_{self.start_time.strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        self.log(f"Reporte guardado en: {report_file}", "INFO")
    
    def generate_coverage_report(self):
        """Genera reporte consolidado de cobertura."""
        self.log("📈 Generando reporte de cobertura consolidado...", "INFO")
        
        # Combinar todos los reportes de cobertura
        cmd = [
            "python", "-m", "coverage", "combine",
            "--append"  # Combinar múltiples archivos .coverage
        ]
        
        result = self.run_command(cmd)
        
        if result["success"]:
            # Generar reporte HTML consolidado
            cmd_html = [
                "python", "-m", "coverage", "html",
                "-d", str(COVERAGE_DIR / "consolidated")
            ]
            self.run_command(cmd_html)
            
            # Generar reporte de terminal
            cmd_report = ["python", "-m", "coverage", "report"]
            report_result = self.run_command(cmd_report)
            
            if report_result["success"]:
                print("\\n📈 REPORTE DE COBERTURA:")
                print(report_result["stdout"])
            
            self.log("Reporte de cobertura generado", "SUCCESS")
        else:
            self.log("Error generando reporte de cobertura", "ERROR")

def main():
    """Función principal."""
    parser = argparse.ArgumentParser(description='Runner completo de tests para Rexus.app')
    
    parser.add_argument('--type', 
                       choices=list(TEST_TYPES.keys()) + ['all'],
                       default='all',
                       help='Tipo de tests a ejecutar')
    
    parser.add_argument('--coverage', 
                       action='store_true',
                       help='Generar reporte de cobertura')
    
    parser.add_argument('--report', 
                       action='store_true',
                       help='Generar solo reportes (sin ejecutar tests)')
    
    parser.add_argument('--verbose', '-v',
                       action='store_true',
                       help='Output verbose')
    
    parser.add_argument('--list-types',
                       action='store_true',
                       help='Listar tipos de tests disponibles')
    
    args = parser.parse_args()
    
    # Listar tipos disponibles
    if args.list_types:
        print("🧪 TIPOS DE TESTS DISPONIBLES:")
        print("="*50)
        for test_type, config in TEST_TYPES.items():
            print(f"📁 {test_type}: {config['description']}")
            print(f"   Ruta: {config['path']}")
            print(f"   Patrón: {config['pattern']}")
            print()
        return
    
    # Inicializar runner
    runner = TestRunner(verbose=args.verbose)
    
    # Solo generar reportes
    if args.report:
        runner.generate_coverage_report()
        return
    
    # Determinar tipos de tests a ejecutar
    if args.type == 'all':
        test_types_to_run = list(TEST_TYPES.keys())
    else:
        test_types_to_run = [args.type]
    
    # Ejecutar tests
    try:
        result = runner.run_all_tests(test_types_to_run, args.coverage)
        
        # Generar reporte de cobertura si se solicita
        if args.coverage:
            runner.generate_coverage_report()
        
        # Exit code basado en resultados
        sys.exit(0 if result.get("success", False) else 1)
        
    except KeyboardInterrupt:
        runner.log("\\n⚠️  Ejecución cancelada por usuario", "WARNING")
        sys.exit(130)
    except Exception as e:
        runner.log(f"Error inesperado: {e}", "ERROR")
        sys.exit(1)

if __name__ == "__main__":
    main()
