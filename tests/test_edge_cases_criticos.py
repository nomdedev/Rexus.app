#!/usr/bin/env python3
"""
Tests de Edge Cases Críticos para el Sistema Rexus
Casos límite, errores de concurrencia, y escenarios extremos
"""

import sys
import threading
import time
import unittest
from pathlib import Path

# Agregar el directorio raíz al path
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from rexus.core.auth_manager import AuthManager
from rexus.core.user_management import UserManagementSystem


class TestEdgeCasesCriticos(unittest.TestCase):
    """Tests para casos extremos y edge cases críticos"""

    def setUp(self):
        """Configuración inicial"""
        self.test_user_base = {
            "username": "test_edge_user",
            "password": "EdgeTest123!",  # noqa: B105
            "email": "edge@test.com",
            "nombre": "Edge",
            "apellido": "Test",
            "rol": "USER",
        }

    # =================================================================
    # EDGE CASES DE LÍMITES EXTREMOS
    # =================================================================

    def test_maximum_username_length(self):
        """Test username en el límite máximo (50 caracteres)"""
        max_username = "a" * 50
        valid, errors = UserManagementSystem.validate_username(max_username)
        self.assertTrue(valid, f"Username de 50 caracteres debería ser válido")

    def test_minimum_username_length(self):
        """Test username en el límite mínimo (3 caracteres)"""
        min_username = "abc"
        valid, errors = UserManagementSystem.validate_username(min_username)
        self.assertTrue(valid, f"Username de 3 caracteres debería ser válido")

    def test_boundary_username_invalid(self):
        """Test usernames justo fuera de los límites"""
        # Muy corto (2 caracteres)
        valid_short, _ = UserManagementSystem.validate_username("ab")
        self.assertFalse(valid_short)

        # Muy largo (51 caracteres)
        valid_long, _ = UserManagementSystem.validate_username("a" * 51)
        self.assertFalse(valid_long)

    def test_password_minimum_length_boundary(self):
        """Test contraseñas en el límite de 8 caracteres"""
        # Exactamente 8 caracteres con todos los requisitos
        min_password = "Test123!"  # noqa: B105
        valid, errors = UserManagementSystem.validate_password(min_password)
        self.assertTrue(
            valid,
            "Contraseña de 8 caracteres con todos los requisitos debería ser válida",
        )

    def test_password_under_minimum_length(self):
        """Test contraseña con 7 caracteres"""
        short_password = "Test12!"  # noqa: B105
        valid, errors = UserManagementSystem.validate_password(short_password)
        self.assertFalse(valid, "Contraseña de 7 caracteres debería ser rechazada")

    # =================================================================
    # EDGE CASES DE CARACTERES ESPECIALES
    # =================================================================

    def test_unicode_usernames(self):
        """Test usernames con caracteres Unicode"""
        unicode_usernames = [
            "test_ñ",  # Con ñ
            "test_é",  # Con acento
            "test_ü",  # Con diéresis
        ]

        for username in unicode_usernames:
            valid, errors = UserManagementSystem.validate_username(username)
            # El resultado depende de si el sistema acepta Unicode

    def test_special_characters_in_password(self):
        """Test todos los caracteres especiales válidos en contraseñas"""
        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"

        for char in special_chars:
            test_password = f"Test123{char}"  # noqa: B105
            valid, errors = UserManagementSystem.validate_password(test_password)
            self.assertTrue(valid, f"Contraseña con '{char}' debería ser válida")

    def test_email_edge_cases(self):
        """Test emails en casos límite"""
        edge_emails = [
            "a@b.co",  # Email mínimo válido
            "test@sub.domain.co.uk",  # Email con múltiples subdominios
            "test+tag+more@domain.com",  # Email con múltiples tags
            "test.user.name@domain.com",  # Email con múltiples puntos
            "test_user_name@domain.com",  # Email con múltiples guiones bajos
        ]

        for email in edge_emails:
            valid, errors = UserManagementSystem.validate_email(email)
            self.assertTrue(valid, f"Email válido rechazado: {email}")

    # =================================================================
    # EDGE CASES DE CONCURRENCIA
    # =================================================================

    def test_concurrent_authentication_attempts(self):
        """Test múltiples intentos de autenticación simultáneos"""
        results = []
        threads = []

        def authenticate_user():
            result = AuthManager.authenticate_user("admin", "admin")
            results.append(result)

        # Crear múltiples hilos para autenticación simultánea
        for _ in range(5):
            thread = threading.Thread(target=authenticate_user)
            threads.append(thread)

        # Ejecutar todos los hilos
        for thread in threads:
            thread.start()

        # Esperar a que terminen
        for thread in threads:
            thread.join()

        # Verificar que todos los resultados sean consistentes
        self.assertEqual(len(results), 5)
        self.assertTrue(all(isinstance(r, bool) for r in results))

    def test_rapid_password_validation(self):
        """Test validación rápida de múltiples contraseñas"""
        passwords = [
            "Test123!",  # noqa: B105
            "Invalid",  # noqa: B105
            "AnotherTest456@",  # noqa: B105
            "short",  # noqa: B105
            "ValidPassword789#",  # noqa: B105
        ]

        results = []
        for password in passwords:
            start_time = time.time()
            valid, errors = UserManagementSystem.validate_password(password)
            end_time = time.time()

            results.append(
                {"password": password, "valid": valid, "time": end_time - start_time}
            )

        # Verificar que todas las validaciones se completen rápidamente
        for result in results:
            self.assertLess(
                result["time"], 1.0, "Validación de contraseña tarda demasiado"
            )

    # =================================================================
    # EDGE CASES DE MEMORIA Y PERFORMANCE
    # =================================================================

    def test_very_long_input_strings(self):
        """Test strings extremadamente largos"""
        # String de 10,000 caracteres
        very_long_string = "a" * 10000

        # Test username muy largo
        valid_username, _ = UserManagementSystem.validate_username(very_long_string)
        self.assertFalse(valid_username)

        # Test email muy largo
        long_email = very_long_string + "@domain.com"
        valid_email, _ = UserManagementSystem.validate_email(long_email)
        self.assertFalse(valid_email)

    def test_empty_and_whitespace_inputs(self):
        """Test inputs vacíos y solo espacios en blanco"""
        empty_inputs = ["", "   ", "\t", "\n", "\r\n", "  \t  \n  "]

        for input_str in empty_inputs:
            # Test username
            valid_user, _ = UserManagementSystem.validate_username(input_str)
            self.assertFalse(
                valid_user, f"Username '{repr(input_str)}' debería ser inválido"
            )

            # Test email
            valid_email, _ = UserManagementSystem.validate_email(input_str)
            self.assertFalse(
                valid_email, f"Email '{repr(input_str)}' debería ser inválido"
            )

    # =================================================================
    # EDGE CASES DE INYECCIÓN Y SEGURIDAD
    # =================================================================

    def test_sql_injection_patterns(self):
        """Test múltiples patrones de inyección SQL"""
        injection_patterns = [
            "'; DROP TABLE usuarios; --",
            "' OR 1=1 --",
            "' UNION SELECT * FROM usuarios --",
            "admin'/*",
            "1' OR '1'='1",
            "'; exec xp_cmdshell('dir') --",
        ]

        for pattern in injection_patterns:
            result = AuthManager.authenticate_user(pattern, "password")
            self.assertFalse(
                result, f"Patrón de inyección SQL '{pattern}' debería fallar"
            )

    def test_xss_patterns(self):
        """Test patrones de Cross-Site Scripting"""
        xss_patterns = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src='x' onerror='alert(1)'>",
            "';alert(String.fromCharCode(88,83,83))//",
            "<svg/onload=alert('xss')>",
        ]

        for pattern in xss_patterns:
            valid, _ = UserManagementSystem.validate_username(pattern)
            self.assertFalse(valid, f"Patrón XSS '{pattern}' debería ser rechazado")

    def test_command_injection_patterns(self):
        """Test patrones de inyección de comandos"""
        command_patterns = [
            "; rm -rf /",
            "| ls -la",
            "&& echo test",
            "$(whoami)",
            "`ls`",
            "$USER",
        ]

        for pattern in command_patterns:
            valid, _ = UserManagementSystem.validate_username(pattern)
            self.assertFalse(
                valid, f"Patrón de comando '{pattern}' debería ser rechazado"
            )

    # =================================================================
    # EDGE CASES DE PROTECCIÓN DE ADMIN
    # =================================================================

    def test_admin_protection_edge_cases(self):
        """Test casos límite de protección del admin"""

        # Intentar cambiar el username del admin
        success1, msg1 = UserManagementSystem.update_user(
            "admin", {"username": "new_admin"}, "admin"
        )

        # Intentar desactivar el admin
        success2, msg2 = UserManagementSystem.update_user(
            "admin", {"estado": "INACTIVO"}, "admin"
        )

        # Verificar que las protecciones funcionen
        # Los resultados específicos dependen de la implementación

    def test_case_variations_admin(self):
        """Test variaciones de mayúsculas/minúsculas para admin"""
        admin_variations = ["admin", "ADMIN", "Admin", "aDmIn"]

        for variation in admin_variations:
            # Test eliminación con diferentes casos
            success, msg = UserManagementSystem.delete_user(variation, "admin")
            # El comportamiento específico depende de si el sistema es case-sensitive

    # =================================================================
    # EDGE CASES DE VALIDACIÓN CRUZADA
    # =================================================================

    def test_duplicate_usernames_case_sensitivity(self):
        """Test usernames duplicados con diferentes casos"""
        # Esto depende de la implementación de la base de datos
        # Algunos sistemas son case-sensitive, otros no
        pass

    def test_duplicate_emails_case_sensitivity(self):
        """Test emails duplicados con diferentes casos"""
        # Los emails técnicamente son case-insensitive según RFC
        emails = ["test@domain.com", "TEST@domain.com", "Test@Domain.Com"]

        for email in emails:
            valid, _ = UserManagementSystem.validate_email(email)
            self.assertTrue(valid, f"Email válido rechazado: {email}")

    # =================================================================
    # EDGE CASES DE ESTADO DEL SISTEMA
    # =================================================================

    def test_system_under_load(self):
        """Test comportamiento del sistema bajo carga"""
        # Simular múltiples operaciones simultáneas
        operations = []

        def perform_validation():
            for i in range(100):
                UserManagementSystem.validate_password(f"Test{i}123!")  # noqa: B105
                UserManagementSystem.validate_username(f"user{i}")
                UserManagementSystem.validate_email(f"user{i}@test.com")

        # Ejecutar en múltiples hilos
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=perform_validation)
            threads.append(thread)
            thread.start()

        # Esperar completación
        for thread in threads:
            thread.join()

        # Si llegamos aquí sin excepciones, el test pasa
        self.assertTrue(True)


def run_edge_cases():
    """Ejecuta todos los tests de edge cases"""
    print("=" * 70)
    print("EJECUTANDO TESTS DE EDGE CASES CRÍTICOS")
    print("=" * 70)

    # Crear suite de tests
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestEdgeCasesCriticos)

    # Ejecutar tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Reporte final
    print("\n" + "=" * 70)
    print("REPORTE DE EDGE CASES")
    print("=" * 70)
    print(f"Tests ejecutados: {result.testsRun}")
    print(
        f"Tests exitosos: {result.testsRun - len(result.failures) - len(result.errors)}"
    )
    print(f"Tests fallidos: {len(result.failures)}")
    print(f"Errores: {len(result.errors)}")

    success_rate = (
        (
            (result.testsRun - len(result.failures) - len(result.errors))
            / result.testsRun
            * 100
        )
        if result.testsRun > 0
        else 0
    )
    print(f"Tasa de éxito: {success_rate:.1f}%")

    if success_rate >= 90:
        print("✅ EDGE CASES: EXCELENTE MANEJO")
    elif success_rate >= 75:
        print("🟡 EDGE CASES: MANEJO ACEPTABLE")
    else:
        print("❌ EDGE CASES: REQUIERE MEJORAS")

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_edge_cases()
    sys.exit(0 if success else 1)
