#!/usr/bin/env python3
"""
Sistema de Testing Automatizado - Rexus.app

Proporciona testing automatizado completo para validar todas las mejoras
implementadas: seguridad, rendimiento, validación, UI/UX, etc.

Fecha: 15/08/2025
Componente: Testing - Automatización de Pruebas
"""

import os
import sys
import time
import unittest
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from unittest.mock import Mock, patch

# Agregar ruta del proyecto
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Importar logging centralizado
try:
    from rexus.utils.app_logger import get_logger
    logger = get_logger("automated_test_runner")
except ImportError:
    import logging
    logger = logging.getLogger("automated_test_runner")


class SecurityTestSuite(unittest.TestCase):
    """Suite de pruebas de seguridad."""

    def setUp(self):
        """Configuración inicial para pruebas de seguridad."""
        try:
            from rexus.utils.input_validator import input_validator
            from rexus.utils.data_sanitizers import unified_sanitizer
            self.validator = input_validator
            self.sanitizer = unified_sanitizer
        except ImportError as e:
            self.skipTest(f"Módulos de seguridad no disponibles: {e}")

    def test_sql_injection_prevention(self):
        """Prueba prevención de SQL injection."""
        malicious_inputs = [
            "'; DROP TABLE usuarios; --",
            "' OR '1'='1",
            "' UNION SELECT * FROM usuarios --",
            "1; DELETE FROM productos",
            "admin'/*",
            "' OR 1=1 #",
        ]

        for malicious_input in malicious_inputs:
            with self.subTest(input=malicious_input):
                is_valid, error_msg, sanitized = self.validator.validate_input(
                    malicious_input, 'text', 'test_field'
                )
                
                # Debe detectar como inválido o sanitizar completamente
                self.assertTrue(
                    not is_valid or (sanitized and malicious_input != sanitized),
                    f"SQL injection no detectado: {malicious_input}"
                )

    def test_xss_prevention(self):
        """Prueba prevención de XSS."""
        xss_inputs = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>",
            "<iframe src='javascript:alert(1)'></iframe>",
            "onclick=alert('XSS')",
            "<svg onload=alert('XSS')>",
        ]

        for xss_input in xss_inputs:
            with self.subTest(input=xss_input):
                is_valid, error_msg, sanitized = self.validator.validate_input(
                    xss_input, 'text', 'test_field'
                )
                
                # Debe detectar como inválido o sanitizar
                self.assertTrue(
                    not is_valid or (sanitized and '<script' not in sanitized.lower()),
                    f"XSS no detectado: {xss_input}"
                )

    def test_path_traversal_prevention(self):
        """Prueba prevención de path traversal."""
        traversal_inputs = [
            "../../../etc/passwd",
            "..\\..\\windows\\system32",
            "%2e%2e/%2e%2e/%2e%2e/etc/passwd",
            "....//....//....//etc/passwd",
        ]

        for traversal_input in traversal_inputs:
            with self.subTest(input=traversal_input):
                sanitized_filename = self.sanitizer.file.sanitize_filename(traversal_input)
                
                # Debe rechazar o sanitizar path traversal
                self.assertTrue(
                    sanitized_filename is None or '..' not in sanitized_filename,
                    f"Path traversal no detectado: {traversal_input}"
                )

    def test_password_validation(self):
        """Prueba validación de contraseñas."""
        weak_passwords = ["123", "password", "abc", "1234567"]
        strong_passwords = ["Password123!", "SecureP@ssw0rd", "MyStr0ng#Pass"]

        for weak_pass in weak_passwords:
            with self.subTest(password=weak_pass):
                result = self.sanitizer.security.sanitize_password(weak_pass)
                self.assertIsNone(result, f"Contraseña débil aceptada: {weak_pass}")

        for strong_pass in strong_passwords:
            with self.subTest(password=strong_pass):
                result = self.sanitizer.security.sanitize_password(strong_pass)
                self.assertIsNotNone(result, f"Contraseña fuerte rechazada: {strong_pass}")


class PerformanceTestSuite(unittest.TestCase):
    """Suite de pruebas de rendimiento."""

    def setUp(self):
        """Configuración inicial para pruebas de rendimiento."""
        try:
            from rexus.utils.query_optimizer import QueryOptimizer
            from rexus.utils.smart_cache import SmartCache
            
            # Mock de conexión de base de datos
            self.mock_db = Mock()
            self.optimizer = QueryOptimizer(self.mock_db)
            self.cache = SmartCache()
        except ImportError as e:
            self.skipTest(f"Módulos de rendimiento no disponibles: {e}")

    def test_cache_performance(self):
        """Prueba rendimiento del cache."""
        # Datos de prueba
        test_data = {"key1": "value1", "key2": "value2"}
        
        # Medir tiempo de escritura
        start_time = time.time()
        for i in range(1000):
            self.cache.set(f"test_key_{i}", f"test_value_{i}")
        write_time = time.time() - start_time
        
        # Medir tiempo de lectura
        start_time = time.time()
        for i in range(1000):
            self.cache.get(f"test_key_{i}")
        read_time = time.time() - start_time
        
        # Verificar que las operaciones sean rápidas
        self.assertLess(write_time, 1.0, "Cache write too slow")
        self.assertLess(read_time, 0.5, "Cache read too slow")

    def test_query_batching(self):
        """Prueba agrupamiento de consultas."""
        # Configurar mock para simular múltiples consultas individuales
        individual_queries = []
        
        def mock_execute(query, params=None):
            individual_queries.append((query, params))
            return [{'id': 1, 'name': 'test'}]
        
        self.mock_db.cursor.return_value.execute = mock_execute
        self.mock_db.cursor.return_value.fetchall.return_value = [{'id': 1, 'name': 'test'}]
        
        # Ejecutar consulta en batch
        ids = [1, 2, 3, 4, 5]
        results = self.optimizer.get_by_ids_batched('test_table', ids)
        
        # Verificar que se ejecutó solo una consulta
        self.assertEqual(len(individual_queries), 1, "Batching no funcionó correctamente")

    def test_n_plus_one_optimization(self):
        """Prueba optimización de problemas N+1."""
        # Simular el problema N+1: obtener productos y sus categorías
        products = [{'id': 1, 'name': 'Producto 1'}, {'id': 2, 'name': 'Producto 2'}]
        
        # Método ineficiente (N+1)
        inefficient_queries = 0
        
        def count_queries():
            nonlocal inefficient_queries
            inefficient_queries += 1
            return {'category': 'Test Category'}
        
        # Simular N+1
        start_time = time.time()
        for product in products:
            count_queries()  # Una consulta por producto
        n_plus_one_time = time.time() - start_time
        
        # Método optimizado (batch)
        start_time = time.time()
        # Una sola consulta para todas las categorías
        optimized_result = self.optimizer.get_by_ids_batched('categories', [1, 2])
        optimized_time = time.time() - start_time
        
        # El método optimizado debe ser más rápido
        self.assertLess(optimized_time, n_plus_one_time, "Optimización N+1 no efectiva")


class ValidationTestSuite(unittest.TestCase):
    """Suite de pruebas de validación."""

    def setUp(self):
        """Configuración inicial para pruebas de validación."""
        try:
            from rexus.utils.input_validator import input_validator
            self.validator = input_validator
        except ImportError as e:
            self.skipTest(f"Módulos de validación no disponibles: {e}")

    def test_email_validation(self):
        """Prueba validación de emails."""
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "test+tag@example.org"
        ]
        
        invalid_emails = [
            "invalid-email",
            "@domain.com",
            "test@",
            "test..test@domain.com",
            "test@domain",
        ]

        for email in valid_emails:
            with self.subTest(email=email):
                is_valid, error_msg, sanitized = self.validator.validate_input(
                    email, 'email', 'email_field'
                )
                self.assertTrue(is_valid, f"Email válido rechazado: {email}")

        for email in invalid_emails:
            with self.subTest(email=email):
                is_valid, error_msg, sanitized = self.validator.validate_input(
                    email, 'email', 'email_field'
                )
                self.assertFalse(is_valid, f"Email inválido aceptado: {email}")

    def test_numeric_validation(self):
        """Prueba validación numérica."""
        valid_numbers = ["123", "123.45", "0", "999.99"]
        invalid_numbers = ["abc", "12.34.56", "", "123abc", "12,34"]

        for number in valid_numbers:
            with self.subTest(number=number):
                is_valid, error_msg, sanitized = self.validator.validate_input(
                    number, 'numeric', 'number_field'
                )
                self.assertTrue(is_valid, f"Número válido rechazado: {number}")

        for number in invalid_numbers:
            with self.subTest(number=number):
                is_valid, error_msg, sanitized = self.validator.validate_input(
                    number, 'numeric', 'number_field'
                )
                self.assertFalse(is_valid, f"Número inválido aceptado: {number}")

    def test_form_validation(self):
        """Prueba validación de formularios completos."""
        # Esquema de validación
        schema = {
            'nombre': {'type': 'name', 'required': True},
            'email': {'type': 'email', 'required': True},
            'precio': {'type': 'currency', 'min_value': 0}
        }

        # Datos válidos
        valid_data = {
            'nombre': 'Juan Pérez',
            'email': 'juan@example.com',
            'precio': '99.99'
        }

        is_valid, errors, sanitized = self.validator.validate_form_data(valid_data, schema)
        self.assertTrue(is_valid, f"Formulario válido rechazado: {errors}")

        # Datos inválidos
        invalid_data = {
            'nombre': '',  # Requerido pero vacío
            'email': 'invalid-email',  # Email inválido
            'precio': '-10'  # Precio negativo
        }

        is_valid, errors, sanitized = self.validator.validate_form_data(invalid_data, schema)
        self.assertFalse(is_valid, "Formulario inválido aceptado")
        self.assertGreater(len(errors), 0, "No se reportaron errores en formulario inválido")


class UITestSuite(unittest.TestCase):
    """Suite de pruebas de UI/UX."""

    def setUp(self):
        """Configuración inicial para pruebas de UI."""
        try:
            from rexus.ui.style_manager import style_manager
            self.style_manager = style_manager
        except ImportError as e:
            self.skipTest(f"Módulos de UI no disponibles: {e}")

    def test_theme_detection(self):
        """Prueba detección automática de tema."""
        # Verificar que el style manager esté inicializado
        self.assertIsNotNone(self.style_manager, "Style manager no inicializado")
        
        # Verificar que tenga un tema por defecto
        current_theme = self.style_manager.get_current_theme()
        self.assertIsNotNone(current_theme, "No hay tema actual")
        
        # Verificar que el tema esté en la lista de disponibles
        available_themes = self.style_manager.get_available_themes()
        self.assertIn(current_theme, available_themes, "Tema actual no está en lista disponible")

    def test_contrast_fixes(self):
        """Prueba correcciones de contraste."""
        # Verificar que las correcciones críticas estén disponibles
        self.assertTrue(
            hasattr(self.style_manager, 'apply_critical_contrast_fixes'),
            "Método de corrección de contraste no disponible"
        )
        
        # Verificar que se puedan aplicar sin errores
        try:
            result = self.style_manager.apply_critical_contrast_fixes()
            self.assertTrue(result, "Correcciones de contraste fallaron")
        except Exception as e:
            self.fail(f"Error aplicando correcciones de contraste: {e}")

    def test_theme_application(self):
        """Prueba aplicación de temas."""
        available_themes = self.style_manager.get_available_themes()
        
        for theme in available_themes[:3]:  # Probar solo algunos temas
            with self.subTest(theme=theme):
                try:
                    result = self.style_manager.apply_global_theme(theme)
                    self.assertTrue(result, f"Fallo aplicando tema: {theme}")
                except Exception as e:
                    self.fail(f"Error aplicando tema {theme}: {e}")


class IntegrationTestSuite(unittest.TestCase):
    """Suite de pruebas de integración."""

    def test_logging_system(self):
        """Prueba sistema de logging centralizado."""
        try:
            from rexus.utils.app_logger import get_logger
            test_logger = get_logger("test_module")
            
            # Verificar que se puede crear logger
            self.assertIsNotNone(test_logger, "No se pudo crear logger")
            
            # Verificar que se pueden hacer logs
            test_logger.info("Test log message")
            test_logger.warning("Test warning message")
            test_logger.error("Test error message")
            
            # Si llegamos aquí, el logging funciona
            self.assertTrue(True)
            
        except Exception as e:
            self.fail(f"Sistema de logging falló: {e}")

    def test_sql_manager_integration(self):
        """Prueba integración del SQLQueryManager."""
        try:
            from rexus.utils.sql_query_manager import SQLQueryManager
            
            # Crear instancia
            sql_manager = SQLQueryManager()
            self.assertIsNotNone(sql_manager, "SQLQueryManager no se pudo crear")
            
            # Verificar que tiene métodos necesarios
            self.assertTrue(hasattr(sql_manager, 'get_query'), "Método get_query no disponible")
            
        except Exception as e:
            self.fail(f"SQLQueryManager falló: {e}")

    def test_sanitizer_integration(self):
        """Prueba integración de sanitizadores."""
        try:
            from rexus.utils.data_sanitizers import unified_sanitizer
            
            # Verificar que está disponible
            self.assertIsNotNone(unified_sanitizer, "Unified sanitizer no disponible")
            
            # Verificar componentes principales
            self.assertTrue(hasattr(unified_sanitizer, 'text'), "Text sanitizer no disponible")
            self.assertTrue(hasattr(unified_sanitizer, 'numeric'), "Numeric sanitizer no disponible")
            self.assertTrue(hasattr(unified_sanitizer, 'security'), "Security sanitizer no disponible")
            
        except Exception as e:
            self.fail(f"Sanitizers integration falló: {e}")


class AutomatedTestRunner:
    """Runner principal para ejecutar todas las pruebas automatizadas."""

    def __init__(self):
        """Inicializa el runner de pruebas."""
        self.test_suites = [
            SecurityTestSuite,
            PerformanceTestSuite,
            ValidationTestSuite,
            UITestSuite,
            IntegrationTestSuite,
        ]
        self.results = {}

    def run_all_tests(self, verbose: bool = True) -> Dict[str, Any]:
        """
        Ejecuta todas las suites de pruebas.
        
        Args:
            verbose: Si mostrar output detallado
        
        Returns:
            Dict[str, Any]: Resultados de las pruebas
        """
        print("🚀 Iniciando Tests Automatizados - Rexus.app")
        print("=" * 60)
        
        total_tests = 0
        total_failures = 0
        total_errors = 0
        start_time = time.time()

        for suite_class in self.test_suites:
            suite_name = suite_class.__name__
            print(f"\n📋 Ejecutando: {suite_name}")
            print("-" * 40)
            
            # Crear suite de pruebas
            suite = unittest.TestLoader().loadTestsFromTestCase(suite_class)
            
            # Ejecutar pruebas
            if verbose:
                runner = unittest.TextTestRunner(verbosity=2)
            else:
                runner = unittest.TextTestRunner(verbosity=1)
            
            result = runner.run(suite)
            
            # Almacenar resultados
            self.results[suite_name] = {
                'tests_run': result.testsRun,
                'failures': len(result.failures),
                'errors': len(result.errors),
                'success_rate': (result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100 if result.testsRun > 0 else 0
            }
            
            total_tests += result.testsRun
            total_failures += len(result.failures)
            total_errors += len(result.errors)

        # Resultados finales
        total_time = time.time() - start_time
        overall_success_rate = (total_tests - total_failures - total_errors) / total_tests * 100 if total_tests > 0 else 0

        self.results['summary'] = {
            'total_tests': total_tests,
            'total_failures': total_failures,
            'total_errors': total_errors,
            'overall_success_rate': overall_success_rate,
            'execution_time': total_time
        }

        self._print_summary()
        return self.results

    def _print_summary(self):
        """Imprime resumen de resultados."""
        print("\n" + "=" * 60)
        print("📊 RESUMEN DE PRUEBAS AUTOMATIZADAS")
        print("=" * 60)
        
        summary = self.results['summary']
        
        # Estado general
        if summary['overall_success_rate'] >= 95:
            status_emoji = "✅"
            status_text = "EXCELENTE"
        elif summary['overall_success_rate'] >= 80:
            status_emoji = "⚠️"
            status_text = "BUENO"
        else:
            status_emoji = "❌"
            status_text = "NECESITA MEJORAS"
        
        print(f"Estado General: {status_emoji} {status_text}")
        print(f"Tests Ejecutados: {summary['total_tests']}")
        print(f"Tasa de Éxito: {summary['overall_success_rate']:.1f}%")
        print(f"Fallos: {summary['total_failures']}")
        print(f"Errores: {summary['total_errors']}")
        print(f"Tiempo Total: {summary['execution_time']:.2f}s")
        
        print("\n📋 Resultados por Suite:")
        print("-" * 40)
        
        for suite_name, results in self.results.items():
            if suite_name == 'summary':
                continue
                
            success_rate = results['success_rate']
            if success_rate >= 95:
                emoji = "✅"
            elif success_rate >= 80:
                emoji = "⚠️"
            else:
                emoji = "❌"
            
            print(f"{emoji} {suite_name}: {success_rate:.1f}% ({results['tests_run']} tests)")

    def run_specific_suite(self, suite_name: str) -> Optional[Dict[str, Any]]:
        """
        Ejecuta una suite específica.
        
        Args:
            suite_name: Nombre de la suite a ejecutar
        
        Returns:
            Optional[Dict[str, Any]]: Resultados de la suite o None si no existe
        """
        suite_class = None
        for cls in self.test_suites:
            if cls.__name__ == suite_name:
                suite_class = cls
                break
        
        if not suite_class:
            print(f"❌ Suite '{suite_name}' no encontrada")
            return None
        
        print(f"🚀 Ejecutando suite: {suite_name}")
        
        suite = unittest.TestLoader().loadTestsFromTestCase(suite_class)
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        return {
            'tests_run': result.testsRun,
            'failures': len(result.failures),
            'errors': len(result.errors),
            'success_rate': (result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100 if result.testsRun > 0 else 0
        }

    def save_results(self, filepath: str):
        """Guarda resultados en archivo JSON."""
        import json
        
        # Agregar metadata
        self.results['metadata'] = {
            'timestamp': datetime.now().isoformat(),
            'python_version': sys.version,
            'platform': sys.platform,
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"💾 Resultados guardados en: {filepath}")


def main():
    """Función principal para ejecutar tests desde línea de comandos."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Sistema de Testing Automatizado - Rexus.app')
    parser.add_argument('--suite', help='Suite específica a ejecutar')
    parser.add_argument('--output', help='Archivo para guardar resultados')
    parser.add_argument('--quiet', action='store_true', help='Modo silencioso')
    
    args = parser.parse_args()
    
    runner = AutomatedTestRunner()
    
    if args.suite:
        results = runner.run_specific_suite(args.suite)
    else:
        results = runner.run_all_tests(verbose=not args.quiet)
    
    if args.output:
        runner.save_results(args.output)
    
    # Código de salida basado en resultados
    if results and 'summary' in results:
        success_rate = results['summary']['overall_success_rate']
        sys.exit(0 if success_rate >= 95 else 1)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()