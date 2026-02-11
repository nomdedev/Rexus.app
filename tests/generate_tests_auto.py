#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador Automático de Tests - Hacia 99% de Cobertura

Analiza el código de Rexus.app y genera automáticamente tests para:
- Módulos sin testear
- Métodos sin cobertura
- Edge cases
- Tests de rendimiento

Uso:
    python tests/generate_tests_auto.py --modulo inventario
    python tests/generate_tests_auto.py --todos
    python tests/generate_tests_auto.py --coverage 99
"""

import sys
import os
import ast
import inspect
from pathlib import Path
from typing import List, Dict, Set, Tuple
import argparse

# Agregar al path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestGenerator:
    """Generador automático de tests."""

    def __init__(self):
        self.modules_path = Path('rexus/modules')
        self.tests_output_path = Path('tests/generated')
        self.tests_output_path.mkdir(exist_ok=True)

    def analyze_module(self, module_path: Path) -> Dict:
        """
        Analiza un módulo y extrae información para generar tests.

        Args:
            module_path: Ruta al módulo a analizar

        Returns:
            Diccionario con información del módulo
        """
        # Leer archivo Python
        with open(module_path, 'r', encoding='utf-8') as f:
            source = f.read()

        # Parsear AST
        tree = ast.parse(source)

        # Extraer clases y métodos
        classes = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_info = {
                    'name': node.name,
                    'methods': [],
                    'functions': []
                }

                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        method_info = {
                            'name': item.name,
                            'args': [arg.arg for arg in item.args.args],
                            'docstring': ast.get_docstring(item)
                        }
                        class_info['methods'].append(method_info)

                classes.append(class_info)

            elif isinstance(node, ast.FunctionDef) and node.col_offset == 0:
                # Función a nivel de módulo
                func_info = {
                    'name': item.name,
                    'args': [arg.arg for arg in item.args.args],
                    'docstring': ast.get_docstring(item)
                }
                classes.append({
                    'name': f"<module>.{item.name}",
                    'methods': [func_info],
                    'functions': [func_info]
                })

        return {
            'path': module_path,
            'name': module_path.stem,
            'classes': classes
        }

    def generate_test_file(self, module_info: Dict) -> str:
        """
        Genera el contenido de un archivo de tests.

        Args:
            module_info: Información del módulo analizado

        Returns:
            Contenido del archivo de tests
        """
        module_name = module_info['name']
        test_content = f'''# -*- coding: utf-8 -*-
"""
Tests Generados Automáticamente para {module_name}

Generado por: Test Generator Automático
Fecha: {datetime.datetime.now().isoformat()}
Módulo: {module_info['path']}
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


@pytest.mark.generated
class Test{module_name.title().replace('_', '')}:
    """Tests generados para el módulo {module_name}."""

'''

        # Generar tests para cada clase
        for class_info in module_info['classes']:
            class_name = class_info['name']
            test_content += f'''
    class Test{class_name}:
        """Tests para la clase {class_name}."""

'''

            # Generar tests para cada método
            for method in class_info['methods']:
                if method['name'].startswith('_') and not method['name'].startswith('__'):
                    continue  # Saltar métodos privados

                test_content += self.generate_test_for_method(
                    class_name,
                    method,
                    module_name
                )

        # Agregar tests generales
        test_content += self.generate_general_tests(module_name)

        test_content += '''

if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
'''

        return test_content

    def generate_test_for_method(self, class_name: str, method: Dict, module_name: str) -> str:
        """Genera un test para un método específico."""
        method_name = method['name']
        args = method['args']

        test_name = f'test_{method_name}'
        test = f'''
    def {test_name}(self):
        """
        Test para el método {class_name}.{method_name}.

        Args del método: {', '.join(args) if args else 'Ninguno'}
        """
        # Setup
        mock_model = Mock()
        mock_connection = Mock()
        mock_cursor = Mock()

        # TODO: Implementar test real
        # Por ahora, este es un placeholder que muestra la estructura

        # Ejemplo de implementación esperada:
        # with patch('rexus.modules.{module_name}.{class_name}') as Model:
        #     model_instance = Model(mock_connection)
        #     result = model_instance.{method_name}(...)
        #
        #     assert result is not None
        #     assert isinstance(result, (dict, list, Model))

        pass

'''

        return test

    def generate_general_tests(self, module_name: str) -> str:
        """Genera tests generales para el módulo."""
        return f'''
    @pytest.mark.integration
    def test_{module_name}_crud_completo(self):
        """
        Test de CRUD completo para {module_name}.

        Verifica:
        - Create
        - Read
        - Update
        - Delete
        """
        pytest.skip("TODO: Implementar test de CRUD completo")

    @pytest.mark.performance
    def test_{module_name}_performance(self):
        """
        Test de performance para {module_name}.

        Verifica:
        - Tiempo de respuesta aceptable
        - Número de queries optimizado
        - Uso de caché
        """
        pytest.skip("TODO: Implementar test de performance")

    @pytest.mark.security
    def test_{module_name}_sql_injection(self):
        """
        Test de SQL injection para {module_name}.

        Verifica que el módulo sea inmune a SQL injection.
        """
        malicious_inputs = [
            "'; DROP TABLE {module_name}; --",
            "' OR '1'='1",
            "' UNION SELECT * FROM usuarios --"
        ]

        for malicious_input in malicious_inputs:
            # TODO: Implementar test real
            with patch('rexus.modules.{module_name}') as Model:
                model = Model()
                result = model.buscar(malicious_input)

                # Verificar que no hubo fuga de datos
                assert result is None or result == []
'''

    def generate_tests_for_module(self, module_name: str):
        """Genera tests para un módulo específico."""
        # Buscar archivo model.py del módulo
        module_pattern = f'{module_name}*/model.py'

        matching_files = list(self.modules_path.glob(module_pattern))
        if not matching_files:
            print(f"⚠️  No se encontró model.py para {module_name}")
            return

        model_file = matching_files[0]

        print(f"🔍 Analizando {model_file}")
        module_info = self.analyze_module(model_file)

        # Generar contenido del test
        test_content = self.generate_test_file(module_info)

        # Guardar archivo de tests
        test_filename = f"test_{module_name}_generated.py"
        test_path = self.tests_output_path / test_filename

        with open(test_path, 'w', encoding='utf-8') as f:
            f.write(test_content)

        print(f"✅ Tests generados: {test_path}")

        return test_path

    def generate_all_tests(self):
        """Genera tests para TODOS los módulos sin testear."""
        modules_to_test = [
            '03_herrajes',
            '09_mantenimiento',
            '08_administracion/contabilidad',
            '08_administracion/recursos_humanos',
            # Agregar más módulos según necesidad
        ]

        generated_tests = []

        for module_name in modules_to_test:
            try:
                test_path = self.generate_tests_for_module(module_name)
                if test_path:
                    generated_tests.append(test_path)
            except Exception as e:
                print(f"❌ Error generando tests para {module_name}: {e}")

        return generated_tests

    def create_test_runner(self):
        """Crea un test runner que ejecute todos los tests generados."""
        runner_content = '''# -*- coding: utf-8 -*-
"""
Test Runner - Ejecuta Todos los Tests Generados

Ejecuta tests generados automáticamente + tests manuales.
"""

import pytest
import sys
from pathlib import Path

if __name__ == '__main__':
    # Ejecutar todos los tests
    exit_code = pytest.main([
        'tests/',
        'tests/generated/',
        '-v',
        '--tb=short',
        '--cov=rexus',
        '--cov-report=term-missing',
        '--cov-report=html:htmlcov',
        '--cov-report=json:coverage.json',
        '-ra',
        '-m', 'not slow'  # Skip slow tests por defecto
    ])

    sys.exit(exit_code)
'''

        runner_path = self.tests_output_path / 'run_all_tests.py'
        with open(runner_path, 'w', encoding='utf-8') as f:
            f.write(runner_content)

        print(f"✅ Test runner creado: {runner_path}")
        return runner_path


class CoverageAnalyzer:
    """Analizador de cobertura de tests."""

    def __init__(self):
        self.uncovered_files = []
        self.uncovered_lines = {}

    def analyze_coverage_report(self, coverage_json_path: str = 'coverage_report.json'):
        """Analiza el reporte de cobertura y sugiere tests a crear."""
        import json

        try:
            with open(coverage_json_path, 'r') as f:
                coverage_data = json.load(f)

            files = coverage_data.get('files', {})

            for filename, file_data in files.items():
                summary = file_data.get('summary', {})
                coverage = summary.get('percent_covered', 0)

                if coverage < 99:  # Objetivo: 99%
                    missing_lines = file_data.get('missing_lines', [])
                    uncovered_summary = file_data.get('summary', {})

                    self.uncovered_files.append({
                        'file': filename,
                        'coverage': coverage,
                        'missing_lines': len(missing_lines),
                        'total_lines': uncovered_summary.get('num_statements', 0)
                    })

                    if missing_lines:
                        self.uncovered_lines[filename] = missing_lines

        except FileNotFoundError:
            print("⚠️  No se encontró coverage_report.json")
            print("   Ejecuta: pytest --cov=rexus --cov-report=json")

    def generate_test_suggestions(self):
        """Genera sugerencias de tests basado en líneas sin cubrir."""
        suggestions = []

        for file_info in sorted(self.uncovered_files, key=lambda x: x['coverage']):
            filename = file_info['file']
            coverage = file_info['coverage']
            missing_count = file_info['missing_lines']

            if 'rexus/modules' in filename:
                module_name = filename.split('modules/')[-1].split('/')[0]

                suggestion = {
                    'module': module_name,
                    'file': filename,
                    'coverage': coverage,
                    'missing_lines': missing_count,
                    'test_types': self.suggest_test_types(module_name, coverage)
                }

                suggestions.append(suggestion)

        return suggestions

    def suggest_test_types(self, module_name: str, coverage: float) -> List[str]:
        """Sugiere tipos de tests a crear basado en cobertura."""
        types = []

        if coverage < 30:
            types.append('unitarios_basicos')  # CRUD básico
            types.append('integracion_simple')
        elif coverage < 60:
            types.append('unitarios_completos')
            types.append('integracion')
            types.append('edge_cases')
        elif coverage < 80:
            types.append('optimizaciones')
            types.append('performance')
            types.append('seguridad')
        elif coverage < 99:
            types.append('e2e_workflows')
            types.append('stress_tests')
            types.append('regression_tests')

        # Agregar tests específicos según módulo
        if 'herrajes' in module_name.lower():
            types.append('optimizacion_n1')
        elif 'inventario' in module_name.lower():
            types.append('cache_operations')
            types.append('stock_validation')
        elif 'usuarios' in module_name.lower():
            types.append('auth_security')
            types.append('permissions')

        return types

    def print_report(self):
        """Imprime reporte de análisis."""
        print("\n" + "="*80)
        print("📊 ANÁLISIS DE COBERTURA - SUGERENCIAS DE TESTS")
        print("="*80)

        if not self.uncovered_files:
            print("✅ ¡Excelente! Todos los archivos tienen 99%+ cobertura")
            return

        print(f"\n📁 Archivos sin 99% de cobertura: {len(self.uncovered_files)}\n")

        for suggestion in self.analyze_coverage_report():
            module = suggestion['module']
            coverage = suggestion['coverage']
            missing = suggestion['missing_lines']
            test_types = suggestion['test_types']

            status = "🔴" if coverage < 30 else "🟡" if coverage < 70 else "🟢"
            print(f"{status} {module:40} {coverage:5.1f}% - {missing} líneas sin cubrir")

            print(f"   Tests sugeridos:")
            for test_type in test_types:
                print(f"   • {test_type}")

            print()


def main():
    """Función principal."""
    parser = argparse.ArgumentParser(description='Generador Automático de Tests')
    parser.add_argument('--modulo', help='Módulo específico a testear')
    parser.add_argument('--todos', action='store_true', help='Generar tests para todos los módulos')
    parser.add_argument('--analizar', action='store_true', help='Analizar cobertura actual')
    parser.add_argument('--coverage', type=int, default=99, help='Objetivo de cobertura (default: 99)')

    args = parser.parse_args()

    print("="*80)
    print("🤖 GENERADOR AUTOMÁTICO DE TESTS - Rexus.app")
    print("="*80)

    if args.analizar:
        # Analizar cobertura actual
        analyzer = CoverageAnalyzer()
        analyzer.analyze_coverage_report()
        analyzer.print_report()

    elif args.modulo:
        # Generar tests para módulo específico
        generator = TestGenerator()
        generator.generate_tests_for_module(args.modulo)
        generator.create_test_runner()

    elif args.todos:
        # Generar tests para todos los módulos
        generator = TestGenerator()
        generator.generate_all_tests()
        generator.create_test_runner()

    else:
        print("Uso:")
        print("  python generate_tests_auto.py --analizar")
        print("  python generate_tests_auto.py --modulo inventario")
        print("  python generate_tests_auto.py --todos")


if __name__ == '__main__':
    import datetime
    main()
