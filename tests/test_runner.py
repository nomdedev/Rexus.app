"""
Test Runner para Rexus.app
Ejecuta tests críticos y de integración de forma eficiente

Fecha: 15/08/2025
Objetivo: Proporcionar validación rápida de componentes críticos
"""

import unittest
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple, Any
from io import StringIO

# Agregar directorio raíz al path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))


class QuickTestRunner:
    """
    Runner de tests optimizado para validación rápida.
    
    Ejecuta solo tests críticos para validación de arranque.
    """
    
    def __init__(self):
        self.results = {}
        self.start_time = None
        self.end_time = None
    
    def run_quick_validation(self) -> Dict[str, Any]:
        """
        Ejecuta validación rápida de componentes críticos.
        
        Returns:
            Dict con resultados de validación
        """
        self.start_time = time.time()
        
        validation_results = {
            'components': self._test_critical_components(),
            'imports': self._test_critical_imports(),
            'database': self._test_database_availability(),
            'modules': self._test_module_availability()
        }
        
        self.end_time = time.time()
        
        # Calcular resumen
        total_tests = sum(len(category['results']) for category in validation_results.values())
        failed_tests = sum(
            len([test for test in category['results'] if not test['passed']]) 
            for category in validation_results.values()
        )
        
        return {
            'status': 'PASSED' if failed_tests == 0 else 'FAILED',
            'total_tests': total_tests,
            'failed_tests': failed_tests,
            'execution_time': round(self.end_time - self.start_time, 3),
            'details': validation_results,
            'can_continue': failed_tests == 0
        }
    
    def _test_critical_components(self) -> Dict[str, Any]:
        """Tests de componentes críticos del sistema."""
        tests = []
        
        # Test SQLQueryManager
        try:
            from rexus.utils.sql_query_manager import SQLQueryManager
            manager = SQLQueryManager()
            has_get_query = hasattr(manager, 'get_query')
            
            tests.append({
                'name': 'SQLQueryManager',
                'passed': has_get_query,
                'details': 'get_query method available' if has_get_query else 'get_query method missing'
            })
        except Exception as e:
            tests.append({
                'name': 'SQLQueryManager',
                'passed': False,
                'details': f'Import error: {e}'
            })
        
        # Test Unified Sanitizer
        try:
            from rexus.utils.unified_sanitizer import unified_sanitizer
            has_sanitize = hasattr(unified_sanitizer, 'sanitize_dict')
            
            tests.append({
                'name': 'UnifiedSanitizer',
                'passed': has_sanitize,
                'details': 'sanitize_dict available' if has_sanitize else 'sanitize_dict missing'
            })
        except Exception as e:
            tests.append({
                'name': 'UnifiedSanitizer',
                'passed': False,
                'details': f'Import error: {e}'
            })
        
        # Test Module Manager
        try:
            from rexus.core.module_manager import module_manager
            has_create_safely = hasattr(module_manager, 'create_module_safely')
            
            tests.append({
                'name': 'ModuleManager',
                'passed': has_create_safely,
                'details': 'create_module_safely available' if has_create_safely else 'create_module_safely missing'
            })
        except Exception as e:
            tests.append({
                'name': 'ModuleManager',
                'passed': False,
                'details': f'Import error: {e}'
            })
        
        return {
            'category': 'Critical Components',
            'passed': all(test['passed'] for test in tests),
            'results': tests
        }
    
    def _test_critical_imports(self) -> Dict[str, Any]:
        """Tests de imports críticos."""
        critical_imports = [
            'PyQt6.QtCore',
            'PyQt6.QtWidgets',
            'PyQt6.QtGui',
            'sqlite3',
            'pathlib',
            'datetime'
        ]
        
        tests = []
        
        for import_name in critical_imports:
            try:
                __import__(import_name)
                tests.append({
                    'name': import_name,
                    'passed': True,
                    'details': 'Import successful'
                })
            except ImportError as e:
                tests.append({
                    'name': import_name,
                    'passed': False,
                    'details': f'Import failed: {e}'
                })
        
        return {
            'category': 'Critical Imports',
            'passed': all(test['passed'] for test in tests),
            'results': tests
        }
    
    def _test_database_availability(self) -> Dict[str, Any]:
        """Tests de disponibilidad de conexiones de BD."""
        tests = []
        
        # Test conexión inventario
        try:
            from rexus.core.database import get_inventario_connection
            tests.append({
                'name': 'InventarioDB',
                'passed': True,
                'details': 'Connection function available'
            })
        except ImportError as e:
            tests.append({
                'name': 'InventarioDB',
                'passed': False,
                'details': f'Connection unavailable: {e}'
            })
        
        # Test conexión usuarios
        try:
            from rexus.core.database import get_users_connection
            tests.append({
                'name': 'UserDB',
                'passed': True,
                'details': 'Connection function available'
            })
        except ImportError as e:
            tests.append({
                'name': 'UserDB',
                'passed': False,
                'details': f'Connection unavailable: {e}'
            })
        
        return {
            'category': 'Database Connections',
            'passed': all(test['passed'] for test in tests),
            'results': tests
        }
    
    def _test_module_availability(self) -> Dict[str, Any]:
        """Tests de disponibilidad de módulos críticos."""
        critical_modules = [
            'rexus.modules.inventario.view',
            'rexus.modules.compras.view',
            'rexus.modules.pedidos.view',
            'rexus.modules.usuarios.view'
        ]
        
        tests = []
        
        for module_name in critical_modules:
            try:
                __import__(module_name)
                tests.append({
                    'name': module_name.split('.')[-2],  # Extraer nombre del módulo
                    'passed': True,
                    'details': 'Module view available'
                })
            except ImportError as e:
                tests.append({
                    'name': module_name.split('.')[-2],
                    'passed': False,
                    'details': f'Module unavailable: {e}'
                })
        
        return {
            'category': 'Business Modules',
            'passed': all(test['passed'] for test in tests),
            'results': tests
        }
    
    def print_results(self, results: Dict[str, Any]):
        """Imprime resultados de forma legible."""
        print(f"\n{'='*50}")
        print("REXUS.APP - VALIDACIÓN RÁPIDA DE COMPONENTES")
        print(f"{'='*50}")
        print(f"Estado: {results['status']}")
        print(f"Tests Ejecutados: {results['total_tests']}")
        print(f"Tests Fallidos: {results['failed_tests']}")
        print(f"Tiempo: {results['execution_time']}s")
        print(f"Puede Continuar: {'SÍ' if results['can_continue'] else 'NO'}")
        
        for category in results['details'].values():
            status_text = 'PASS' if category['passed'] else 'FAIL'
            print(f"\n[{category['category']}] - {status_text}")
            
            for test in category['results']:
                status = 'OK' if test['passed'] else 'FAIL'
                print(f"  [{status}] {test['name']}: {test['details']}")
        
        print(f"\n{'='*50}")


def run_startup_validation() -> Tuple[bool, Dict[str, Any]]:
    """
    Ejecuta validación rápida para startup de la aplicación.
    
    Returns:
        Tuple[bool, Dict]: (puede_continuar, resultados_detallados)
    """
    runner = QuickTestRunner()
    results = runner.run_quick_validation()
    return results['can_continue'], results


def run_full_tests() -> bool:
    """
    Ejecuta suite completa de tests.
    
    Returns:
        bool: True si todos los tests pasan
    """
    try:
        from test_critical_modules import run_critical_tests
        return run_critical_tests()
    except ImportError:
        print("❌ No se puede ejecutar suite completa - test_critical_modules no disponible")
        return False


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--quick':
        # Validación rápida
        can_continue, results = run_startup_validation()
        runner = QuickTestRunner()
        runner.print_results(results)
        sys.exit(0 if can_continue else 1)
    else:
        # Suite completa
        print("Ejecutando suite completa de tests...")
        success = run_full_tests()
        sys.exit(0 if success else 1)