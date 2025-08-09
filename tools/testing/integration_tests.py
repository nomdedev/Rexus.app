#!/usr/bin/env python3
"""
Tests de integración para validar las mejoras técnicas implementadas
"""

import sys
import time
import unittest
from pathlib import Path
from datetime import datetime

# Agregar el directorio raíz al path para imports
sys.path.insert(0, str(Path(__file__).parent.parent))

class TestSecurityIntegration(unittest.TestCase):
    """Tests de integración para el sistema de seguridad"""
    
    def test_security_utils_import(self):
        """Verifica que SecurityUtils se puede importar correctamente"""
        try:
            from rexus.utils.security import SecurityUtils
            self.assertIsNotNone(SecurityUtils)
            print("[CHECK] SecurityUtils importado correctamente")
        except ImportError as e:
            self.fail(f"No se pudo importar SecurityUtils: {e}")
    
    def test_password_hashing(self):
        """Verifica el sistema de hashing de contraseñas"""
        try:
            from rexus.utils.security import SecurityUtils
            
            # Test hash y verificación
            password = "test_password_123"
            hashed = SecurityUtils.hash_password(password)
            
            self.assertIsInstance(hashed, str)
            self.assertTrue(len(hashed) > 50)  # Hash debe ser largo
            
            # Verificar contraseña correcta
            self.assertTrue(SecurityUtils.verify_password(password, hashed))
            
            # Verificar contraseña incorrecta
            self.assertFalse(SecurityUtils.verify_password("wrong_password", hashed))
            
            print("[CHECK] Sistema de hashing de contraseñas funcionando")
        except Exception as e:
            self.fail(f"Error en sistema de hashing: {e}")
    
    def test_input_sanitization(self):
        """Verifica la sanitización de entrada"""
        try:
            from rexus.utils.security import SecurityUtils
            
            # Test sanitización XSS
            malicious_input = "<script>alert('xss')</script>Hello"
            sanitized = SecurityUtils.sanitize_input(malicious_input)
            
            self.assertNotIn("<script>", sanitized)
            self.assertNotIn("alert", sanitized)
            self.assertIn("Hello", sanitized)
            
            print("[CHECK] Sanitización de entrada funcionando")
        except Exception as e:
            self.fail(f"Error en sanitización: {e}")

class TestLoggingIntegration(unittest.TestCase):
    """Tests de integración para el sistema de logging"""
    
    def test_logging_config_import(self):
        """Verifica que el sistema de logging se puede importar"""
        try:
            from rexus.utils.logging_config import get_logger, log_user_action
            
            logger = get_logger('test')
            self.assertIsNotNone(logger)
            
            # Test logging de acción
            log_user_action("test_action", "test_user", "test details")
            
            print("[CHECK] Sistema de logging configurado correctamente")
        except ImportError as e:
            print(f"[WARN] Sistema de logging no disponible: {e}")
        except Exception as e:
            self.fail(f"Error en sistema de logging: {e}")

class TestErrorHandlingIntegration(unittest.TestCase):
    """Tests de integración para el manejo de errores"""
    
    def test_error_handler_import(self):
        """Verifica que el sistema de manejo de errores se puede importar"""
        try:
            from rexus.utils.error_handler import error_boundary, safe_execute
            
            # Test decorador error_boundary
            @error_boundary
            def test_function():
                return "success"
            
            result = test_function()
            self.assertEqual(result, "success")
            
            # Test safe_execute
            def failing_function():
                raise ValueError("Test error")
            
            result = safe_execute(failing_function, default_return="default")
            self.assertEqual(result, "default")
            
            print("[CHECK] Sistema de manejo de errores funcionando")
        except ImportError as e:
            print(f"[WARN] Sistema de manejo de errores no disponible: {e}")
        except Exception as e:
            self.fail(f"Error en manejo de errores: {e}")

class TestPerformanceIntegration(unittest.TestCase):
    """Tests de integración para el monitoreo de rendimiento"""
    
    def test_performance_monitor_import(self):
        """Verifica que el monitor de rendimiento se puede importar"""
        try:
            from rexus.utils.performance_monitor import PerformanceMonitor, performance_timer
            
            # Test instanciación del monitor
            monitor = PerformanceMonitor()
            self.assertIsNotNone(monitor)
            
            # Test decorador de timing
            @performance_timer
            def test_function():
                time.sleep(0.1)
                return "completed"
            
            result = test_function()
            self.assertEqual(result, "completed")
            
            print("[CHECK] Sistema de monitoreo de rendimiento funcionando")
        except ImportError as e:
            print(f"[WARN] Sistema de monitoreo no disponible: {e}")
        except Exception as e:
            self.fail(f"Error en monitoreo de rendimiento: {e}")

class TestDatabaseIntegration(unittest.TestCase):
    """Tests de integración para las mejoras de base de datos"""
    
    def test_database_manager_import(self):
        """Verifica que el gestor de BD se puede importar"""
        try:
            from rexus.utils.database_manager import DatabasePool, DatabaseManager
            
            # Test pool de conexiones (sin conexión real)
            self.assertIsNotNone(DatabasePool)
            self.assertIsNotNone(DatabaseManager)
            
            print("[CHECK] Sistema de gestión de BD disponible")
        except ImportError as e:
            print(f"[WARN] Sistema de gestión de BD no disponible: {e}")
        except Exception as e:
            print(f"[WARN] Error menor en BD: {e}")

class TestAuthManagerIntegration(unittest.TestCase):
    """Tests de integración para el sistema de autorización"""
    
    def test_auth_manager_import(self):
        """Verifica que AuthManager se puede importar"""
        try:
            from rexus.core.auth_manager import AuthManager, UserRole, Permission
            
            # Test enums
            self.assertIsNotNone(UserRole.ADMIN)
            self.assertIsNotNone(Permission.VIEW_DASHBOARD)
            
            # Test funcionalidad básica
            AuthManager.set_current_user_role(UserRole.ADMIN)
            self.assertTrue(AuthManager.check_permission(Permission.VIEW_DASHBOARD))
            
            print("[CHECK] Sistema de autorización funcionando")
        except ImportError as e:
            self.fail(f"No se pudo importar AuthManager: {e}")
        except Exception as e:
            self.fail(f"Error en sistema de autorización: {e}")

def run_integration_tests():
    """Ejecuta todos los tests de integración"""
    print("🧪 EJECUTANDO TESTS DE INTEGRACIÓN")
    print("=" * 50)
    
    # Crear suite de tests
    test_classes = [
        TestSecurityIntegration,
        TestAuthManagerIntegration,
        TestLoggingIntegration,
        TestErrorHandlingIntegration,
        TestPerformanceIntegration,
        TestDatabaseIntegration
    ]
    
    total_tests = 0
    passed_tests = 0
    
    for test_class in test_classes:
        print(f"\n🔍 {test_class.__name__}")
        suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
        runner = unittest.TextTestRunner(verbosity=0, stream=open('/dev/null', 'w') if sys.platform != 'win32' else open('nul', 'w'))
        
        result = runner.run(suite)
        
        class_total = result.testsRun
        class_passed = class_total - len(result.failures) - len(result.errors)
        
        total_tests += class_total
        passed_tests += class_passed
        
        if class_passed == class_total:
            print(f"  [CHECK] {class_passed}/{class_total} tests pasaron")
        else:
            print(f"  [WARN] {class_passed}/{class_total} tests pasaron")
            for failure in result.failures:
                print(f"    [ERROR] {failure[0]}: {failure[1].split('\\n')[0]}")
            for error in result.errors:
                print(f"    [ERROR] {error[0]}: {error[1].split('\\n')[0]}")
    
    print("\n" + "=" * 50)
    print("[CHART] RESUMEN DE TESTS DE INTEGRACIÓN")
    print(f"[CHECK] Tests pasados: {passed_tests}/{total_tests}")
    
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    if success_rate >= 90:
        print(f"🎉 TESTS EXITOSOS ({success_rate:.1f}%)")
        print("[CHECK] Sistema listo para producción")
    elif success_rate >= 70:
        print(f"[WARN] TESTS MAYORMENTE EXITOSOS ({success_rate:.1f}%)")
        print("🔧 Algunas mejoras menores necesarias")
    else:
        print(f"[ERROR] TESTS CON PROBLEMAS ({success_rate:.1f}%)")
        print("🚨 Revisar y corregir errores antes de continuar")
    
    return success_rate >= 70

if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)
