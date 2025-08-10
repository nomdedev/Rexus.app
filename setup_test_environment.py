#!/usr/bin/env python3
"""
Setup y Validación del Entorno de Tests - Rexus.app

Script para configurar el entorno de desarrollo y validar
la calidad del código antes de ejecutar tests.

Uso:
    python setup_test_environment.py [--install-deps] [--validate] [--fix]
"""

import os
import sys
import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional

# Rutas del proyecto
PROJECT_ROOT = Path(__file__).parent
REXUS_ROOT = PROJECT_ROOT / "rexus"
TESTS_ROOT = PROJECT_ROOT / "tests"
CONFIG_ROOT = PROJECT_ROOT / "config"

# Dependencias necesarias para testing
TEST_DEPENDENCIES = {
    "core": [
        "pytest>=7.0.0",
        "pytest-cov>=4.0.0", 
        "pytest-html>=3.0.0",
        "pytest-xvfb>=3.0.0",  # Para tests visuales en headless
        "coverage>=7.0.0"
    ],
    "ui": [
        "PyQt6>=6.5.0",
        "pytest-qt>=4.0.0"
    ],
    "security": [
        "bandit>=1.7.0",
        "safety>=2.0.0"
    ],
    "quality": [
        "flake8>=6.0.0",
        "black>=23.0.0",
        "mypy>=1.0.0",
        "isort>=5.0.0"
    ],
    "performance": [
        "memory-profiler>=0.61.0",
        "pytest-benchmark>=4.0.0"
    ]
}

# Configuraciones de calidad de código
QUALITY_CONFIGS = {
    "pytest.ini": """[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --strict-markers
    --disable-warnings
    --cov=rexus
    --cov-report=html:test_reports/coverage
    --cov-report=xml:test_reports/coverage.xml
    --cov-report=term-missing
    --html=test_reports/report.html
    --self-contained-html
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    visual: marks tests as visual/UI tests
    security: marks tests as security tests
    performance: marks tests as performance tests
    unit: marks tests as unit tests
""",
    
    ".flake8": """[flake8]
max-line-length = 88
extend-ignore = 
    E203,  # whitespace before ':'
    W503,  # line break before binary operator
    E501,  # line too long (handled by black)
exclude = 
    .git,
    __pycache__,
    build,
    dist,
    *.egg-info,
    .pytest_cache,
    .coverage
per-file-ignores =
    tests/*:F401,F811,D100,D101,D102,D103,D104
""",
    
    "pyproject.toml": """[tool.black]
line-length = 88
target-version = ['py39', 'py310', 'py311']
include = '\\.pyi?$'
extend-exclude = '''
/(
  # directories
  \\.eggs
  | \\.git
  | \\.pytest_cache
  | build
  | dist
)/
'''

[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88
known_first_party = ["rexus"]
known_third_party = ["PyQt6", "pytest"]

[tool.mypy]
python_version = "3.10"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
ignore_missing_imports = true
exclude = [
    "tests/",
    "build/",
    "dist/"
]

[tool.coverage.run]
source = ["rexus"]
omit = [
    "*/tests/*",
    "*/test_*",
    "*/__pycache__/*",
    "*/migrations/*",
    "*/venv/*",
    "*/virtualenv/*"
]

[tool.coverage.report]
precision = 2
show_missing = true
skip_covered = false
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:"
]

[tool.coverage.html]
directory = "test_reports/coverage"
""",
    
    "bandit.yaml": """# Bandit security linter configuration
tests: [B101, B102, B103, B104, B105, B106, B107, B108, B110, B112, B201, B301, B302, B303, B304, B305, B306, B307, B308, B309, B310, B311, B312, B313, B314, B315, B316, B317, B318, B319, B320, B321, B322, B323, B324, B325, B401, B402, B403, B404, B405, B406, B407, B408, B409, B410, B411, B412, B413, B501, B502, B503, B504, B505, B506, B507, B601, B602, B603, B604, B605, B606, B607, B608, B609, B610, B611, B701, B702, B703]

# Exclusions
exclude_dirs:
  - /tests/
  - /test_*
  - /.pytest_cache/
  - /build/
  - /dist/

# Skip specific tests in certain contexts
skips:
  - B101  # Skip assert_used test
  - B603  # Allow subprocess calls (controlled in our codebase)
  - B404  # Allow subprocess import (needed for development tools)
"""
}

class TestEnvironmentSetup:
    """Configurador del entorno de tests."""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results = {}
    
    def log(self, message: str, level: str = "INFO"):
        """Log con diferentes niveles."""
        icons = {
            "INFO": "ℹ️",
            "SUCCESS": "✅",
            "ERROR": "❌", 
            "WARNING": "⚠️",
            "DEBUG": "🔍"
        }
        print(f"{icons.get(level, '📝')} {message}")
    
    def check_python_version(self) -> bool:
        """Verifica versión de Python."""
        self.log("Verificando versión de Python...", "INFO")
        
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 9):
            self.log(f"Python {version.major}.{version.minor} no soportado. Mínimo: Python 3.9", "ERROR")
            return False
        
        self.log(f"Python {version.major}.{version.minor}.{version.micro} ✓", "SUCCESS")
        return True
    
    def create_config_files(self) -> bool:
        """Crea archivos de configuración necesarios."""
        self.log("Creando archivos de configuración...", "INFO")
        
        try:
            for filename, content in QUALITY_CONFIGS.items():
                config_path = PROJECT_ROOT / filename
                
                if config_path.exists():
                    self.log(f"Archivo {filename} ya existe, respaldando...", "WARNING")
                    backup_path = config_path.with_suffix(f"{config_path.suffix}.backup")
                    shutil.copy2(config_path, backup_path)
                
                with open(config_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.log(f"Creado: {filename}", "SUCCESS")
            
            return True
            
        except Exception as e:
            self.log(f"Error creando configuraciones: {e}", "ERROR")
            return False
    
    def check_dependencies(self) -> Dict[str, List[str]]:
        """Verifica dependencias instaladas."""
        self.log("Verificando dependencias...", "INFO")
        
        import importlib
        import pkg_resources
        
        missing = {}
        
        for category, deps in TEST_DEPENDENCIES.items():
            missing_in_category = []
            
            for dep in deps:
                package_name = dep.split('>=')[0].split('==')[0]
                
                try:
                    # Intentar importar
                    if package_name == "pytest-cov":
                        import pytest_cov
                    elif package_name == "pytest-html":
                        import pytest_html
                    elif package_name == "pytest-qt":
                        import pytestqt
                    elif package_name == "pytest-xvfb":
                        import pytest_xvfb
                    elif package_name == "pytest-benchmark":
                        import pytest_benchmark
                    elif package_name == "memory-profiler":
                        import memory_profiler
                    else:
                        importlib.import_module(package_name.replace('-', '_'))
                    
                    self.log(f"  ✓ {package_name}", "DEBUG" if self.verbose else None)
                    
                except ImportError:
                    missing_in_category.append(dep)
                    self.log(f"  ✗ {package_name}", "DEBUG" if self.verbose else None)
            
            if missing_in_category:
                missing[category] = missing_in_category
        
        if missing:
            self.log("Dependencias faltantes encontradas", "WARNING")
            for category, deps in missing.items():
                self.log(f"  {category}: {', '.join(deps)}", "WARNING")
        else:
            self.log("Todas las dependencias están instaladas", "SUCCESS")
        
        return missing
    
    def install_dependencies(self, missing: Dict[str, List[str]]) -> bool:
        """Instala dependencias faltantes."""
        if not missing:
            self.log("No hay dependencias por instalar", "INFO")
            return True
        
        self.log("Instalando dependencias faltantes...", "INFO")
        
        import subprocess
        
        all_deps = []
        for deps in missing.values():
            all_deps.extend(deps)
        
        try:
            # Instalar con pip
            cmd = [sys.executable, "-m", "pip", "install"] + all_deps
            
            self.log(f"Ejecutando: {' '.join(cmd)}", "DEBUG" if self.verbose else None)
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutos
            )
            
            if result.returncode == 0:
                self.log("Dependencias instaladas correctamente", "SUCCESS")
                return True
            else:
                self.log(f"Error instalando dependencias: {result.stderr}", "ERROR")
                return False
                
        except subprocess.TimeoutExpired:
            self.log("Timeout instalando dependencias", "ERROR")
            return False
        except Exception as e:
            self.log(f"Error instalando dependencias: {e}", "ERROR")
            return False
    
    def validate_code_quality(self) -> Dict[str, bool]:
        """Valida calidad del código."""
        self.log("Validando calidad del código...", "INFO")
        
        import subprocess
        
        validators = {
            "flake8": ["python", "-m", "flake8", "rexus/", "tests/"],
            "black": ["python", "-m", "black", "--check", "rexus/", "tests/"],
            "isort": ["python", "-m", "isort", "--check-only", "rexus/", "tests/"],
            "mypy": ["python", "-m", "mypy", "rexus/"],
            "bandit": ["python", "-m", "bandit", "-r", "rexus/", "-f", "json"]
        }
        
        results = {}
        
        for tool, cmd in validators.items():
            try:
                self.log(f"Ejecutando {tool}...", "DEBUG" if self.verbose else None)
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    cwd=PROJECT_ROOT,
                    timeout=120
                )
                
                success = result.returncode == 0
                results[tool] = success
                
                if success:
                    self.log(f"  ✓ {tool}", "SUCCESS")
                else:
                    self.log(f"  ✗ {tool}", "ERROR")
                    if self.verbose:
                        self.log(f"    Output: {result.stdout}", "DEBUG")
                        self.log(f"    Error: {result.stderr}", "DEBUG")
                
            except subprocess.TimeoutExpired:
                self.log(f"  ✗ {tool} (timeout)", "ERROR")
                results[tool] = False
            except FileNotFoundError:
                self.log(f"  ✗ {tool} (no encontrado)", "WARNING")
                results[tool] = False
            except Exception as e:
                self.log(f"  ✗ {tool} (error: {e})", "ERROR")
                results[tool] = False
        
        passed = sum(results.values())
        total = len(results)
        
        self.log(f"Validación de calidad: {passed}/{total} herramientas pasaron", 
                "SUCCESS" if passed == total else "WARNING")
        
        return results
    
    def fix_code_issues(self) -> bool:
        """Intenta arreglar problemas de código automáticamente."""
        self.log("Aplicando correcciones automáticas...", "INFO")
        
        import subprocess
        
        fixers = {
            "black": ["python", "-m", "black", "rexus/", "tests/"],
            "isort": ["python", "-m", "isort", "rexus/", "tests/"]
        }
        
        success_count = 0
        
        for tool, cmd in fixers.items():
            try:
                self.log(f"Aplicando {tool}...", "DEBUG" if self.verbose else None)
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    cwd=PROJECT_ROOT,
                    timeout=60
                )
                
                if result.returncode == 0:
                    self.log(f"  ✓ {tool} aplicado", "SUCCESS")
                    success_count += 1
                else:
                    self.log(f"  ✗ Error en {tool}: {result.stderr}", "ERROR")
                    
            except Exception as e:
                self.log(f"  ✗ Error aplicando {tool}: {e}", "ERROR")
        
        return success_count > 0
    
    def create_test_structure(self) -> bool:
        """Crea estructura de directorios de tests."""
        self.log("Creando estructura de tests...", "INFO")
        
        test_dirs = [
            "tests/unit/core",
            "tests/unit/modules",
            "tests/integration",
            "tests/visual",
            "tests/security", 
            "tests/performance",
            "tests/e2e",
            "tests/usability",
            "tests/business",
            "tests/advanced",
            "test_reports/coverage",
            "test_reports/html",
            "test_reports/xml"
        ]
        
        try:
            for dir_path in test_dirs:
                full_path = PROJECT_ROOT / dir_path
                full_path.mkdir(parents=True, exist_ok=True)
                
                # Crear __init__.py si no existe
                init_file = full_path / "__init__.py"
                if not init_file.exists() and "test_reports" not in str(full_path):
                    init_file.write_text("# Tests module\n")
                
                self.log(f"  📁 {dir_path}", "DEBUG" if self.verbose else None)
            
            self.log("Estructura de tests creada", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"Error creando estructura: {e}", "ERROR")
            return False
    
    def generate_setup_report(self) -> Dict:
        """Genera reporte del setup del entorno."""
        report = {
            "timestamp": str(Path(__file__).stat().st_mtime),
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "project_root": str(PROJECT_ROOT),
            "results": self.results
        }
        
        report_file = PROJECT_ROOT / "test_setup_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.log(f"Reporte guardado: {report_file}", "INFO")
        return report
    
    def setup_complete_environment(self, install_deps: bool = False, fix_issues: bool = False) -> bool:
        """Setup completo del entorno de tests."""
        self.log("🚀 Iniciando setup del entorno de tests...", "INFO")
        
        success = True
        
        # 1. Verificar Python
        if not self.check_python_version():
            return False
        
        # 2. Crear estructura
        if not self.create_test_structure():
            success = False
        
        # 3. Crear configuraciones
        if not self.create_config_files():
            success = False
        
        # 4. Verificar dependencias
        missing_deps = self.check_dependencies()
        self.results["missing_dependencies"] = missing_deps
        
        # 5. Instalar dependencias si se solicita
        if install_deps and missing_deps:
            if not self.install_dependencies(missing_deps):
                success = False
        
        # 6. Validar calidad
        quality_results = self.validate_code_quality()
        self.results["code_quality"] = quality_results
        
        # 7. Arreglar problemas si se solicita
        if fix_issues:
            if self.fix_code_issues():
                # Volver a validar después de arreglar
                quality_results = self.validate_code_quality()
                self.results["code_quality_after_fix"] = quality_results
        
        # 8. Generar reporte
        self.generate_setup_report()
        
        if success:
            self.log("✅ Setup del entorno completado exitosamente", "SUCCESS")
        else:
            self.log("⚠️  Setup completado con algunas advertencias", "WARNING")
        
        return success

def main():
    """Función principal."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Setup del entorno de tests para Rexus.app')
    
    parser.add_argument('--install-deps', 
                       action='store_true',
                       help='Instalar dependencias faltantes automáticamente')
    
    parser.add_argument('--validate', 
                       action='store_true',
                       help='Solo validar entorno (no instalar ni arreglar)')
    
    parser.add_argument('--fix',
                       action='store_true', 
                       help='Aplicar correcciones automáticas de código')
    
    parser.add_argument('--verbose', '-v',
                       action='store_true',
                       help='Output detallado')
    
    args = parser.parse_args()
    
    # Inicializar setup
    setup = TestEnvironmentSetup(verbose=args.verbose)
    
    if args.validate:
        # Solo validar
        setup.check_python_version()
        missing = setup.check_dependencies()
        quality = setup.validate_code_quality()
        
        print("\n📋 RESUMEN DE VALIDACIÓN:")
        print(f"  Dependencias faltantes: {len(sum(missing.values(), []))}")
        print(f"  Validaciones de calidad: {sum(quality.values())}/{len(quality)} pasaron")
        
    else:
        # Setup completo
        success = setup.setup_complete_environment(
            install_deps=args.install_deps,
            fix_issues=args.fix
        )
        
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
