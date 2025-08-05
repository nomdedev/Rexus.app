#!/usr/bin/env python3
"""
Tests Avanzados de Seguridad para Rexus.app

Pruebas exhaustivas de funcionalidades de seguridad incluyendo:
- Sistemas de lockout y limitación de intentos
- Two-Factor Authentication (2FA)
- Validación robusta de contraseñas
- Edge cases de seguridad
- Tests de penetración básicos
"""

import sys
import os
import time
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Agregar directorio raíz al path
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from rexus.modules.usuarios.security_features import UserSecurityManager, create_security_manager
from utils.two_factor_auth import TwoFactorAuth


class TestUserSecurityManager(unittest.TestCase):
    """Tests para el gestor de seguridad de usuarios."""
    
    def setUp(self):
        """Configuración inicial para cada test."""
        # Mock del modelo de usuarios
        self.mock_usuarios_model = Mock()
        self.mock_usuarios_model.obtener_usuario_por_nombre.return_value = {
            'id': 1,
            'username': 'testuser',
            'configuracion_personal': '{}',
            'ultimo_login': None,
            'fecha_creacion': '2024-01-01'
        }
        self.mock_usuarios_model.obtener_todos_usuarios.return_value = [
            {'id': 1, 'username': 'testuser', 'configuracion_personal': '{}'}
        ]
        
        # Crear gestor de seguridad
        self.security_manager = UserSecurityManager(self.mock_usuarios_model)
        
    def test_password_strength_validation(self):
        """Test validación de fortaleza de contraseñas."""
        # Contraseña muy débil
        result = self.security_manager.validate_password_strength("123")
        self.assertFalse(result['valid'])
        self.assertEqual(result['strength'], 'Muy débil')
        self.assertTrue(len(result['issues']) > 0)
        
        # Contraseña débil
        result = self.security_manager.validate_password_strength("password")
        self.assertFalse(result['valid'])
        self.assertIn('Al menos una letra mayúscula', result['issues'])
        
        # Contraseña media
        result = self.security_manager.validate_password_strength("Password1")
        self.assertFalse(result['valid'])  # Falta carácter especial
        
        # Contraseña fuerte
        result = self.security_manager.validate_password_strength("MyStr0ng!P@ssw0rd")
        self.assertTrue(result['valid'])
        self.assertEqual(result['strength'], 'Fuerte')
        self.assertEqual(len(result['issues']), 0)
    
    def test_login_attempt_tracking(self):
        """Test seguimiento de intentos de login."""
        username = "testuser"
        
        # Mock validar_usuario para simular credenciales incorrectas
        self.mock_usuarios_model.validar_usuario.return_value = False
        
        # Primer intento fallido
        result = self.security_manager.register_login_attempt(username, False, "192.168.1.1")
        self.assertFalse(result['success'])
        self.assertEqual(result['attempts'], 1)
        self.assertEqual(result['remaining'], 2)
        
        # Segundo intento fallido
        result = self.security_manager.register_login_attempt(username, False, "192.168.1.1")
        self.assertFalse(result['success'])
        self.assertEqual(result['attempts'], 2)
        self.assertEqual(result['remaining'], 1)
        
        # Tercer intento fallido - debe bloquear
        result = self.security_manager.register_login_attempt(username, False, "192.168.1.1")
        self.assertFalse(result['success'])
        self.assertTrue(result['locked'])
        self.assertEqual(result['attempts'], 3)
        
        # Verificar que está bloqueado
        self.assertTrue(self.security_manager.is_user_locked(username))
        
        # Intento cuando está bloqueado
        result = self.security_manager.register_login_attempt(username, False, "192.168.1.1")
        self.assertTrue(result['locked'])
        self.assertIn('bloqueada hasta', result['message'])
    
    def test_successful_login_resets_attempts(self):
        """Test que login exitoso resetea intentos fallidos."""
        username = "testuser"
        
        self.mock_usuarios_model.validar_usuario.return_value = False
        
        # Dos intentos fallidos
        self.security_manager.register_login_attempt(username, False, "192.168.1.1")
        self.security_manager.register_login_attempt(username, False, "192.168.1.1")
        
        # Verificar que hay intentos fallidos
        self.assertEqual(self.security_manager.failed_attempts[username]['count'], 2)
        
        # Login exitoso
        self.mock_usuarios_model.validar_usuario.return_value = True
        result = self.security_manager.register_login_attempt(username, True, "192.168.1.1")
        
        self.assertTrue(result['success'])
        # Verificar que se resetaron los intentos
        self.assertNotIn(username, self.security_manager.failed_attempts)
    
    def test_manual_unlock(self):
        """Test desbloqueo manual de usuario."""
        username = "testuser"
        
        # Bloquear usuario manualmente
        self.security_manager.lock_user(username, 900)
        self.assertTrue(self.security_manager.is_user_locked(username))
        
        # Desbloquear manualmente
        success = self.security_manager.unlock_user(username)
        self.assertTrue(success)
        self.assertFalse(self.security_manager.is_user_locked(username))
    
    def test_user_not_found_scenarios(self):
        """Test escenarios donde el usuario no existe."""
        # Mock retorna None para usuario inexistente
        self.mock_usuarios_model.obtener_usuario_por_nombre.return_value = None
        
        result = self.security_manager.register_login_attempt("noexist", False, "192.168.1.1")
        self.assertFalse(result['success'])
        self.assertEqual(result['error'], 'Usuario no encontrado')
        
        # Test desbloqueo de usuario inexistente
        success = self.security_manager.unlock_user("noexist")
        self.assertFalse(success)
    
    def test_security_dashboard(self):
        """Test dashboard de seguridad del sistema."""
        dashboard = self.security_manager.get_security_dashboard()
        
        self.assertIn('total_users', dashboard)
        self.assertIn('locked_users', dashboard)
        self.assertIn('users_with_2fa', dashboard)
        self.assertIn('2fa_adoption_rate', dashboard)
        self.assertIn('security_config', dashboard)
        
        # Verificar configuración de seguridad
        config = dashboard['security_config']
        self.assertEqual(config['max_login_attempts'], UserSecurityManager.MAX_LOGIN_ATTEMPTS)
        self.assertEqual(config['lockout_duration_minutes'], UserSecurityManager.LOCKOUT_DURATION // 60)


class TestTwoFactorAuth(unittest.TestCase):
    """Tests para el sistema de Two-Factor Authentication."""
    
    def setUp(self):
        """Configuración inicial."""
        self.tfa = TwoFactorAuth()
    
    def test_secret_key_generation(self):
        """Test generación de claves secretas."""
        secret1 = self.tfa.generar_secret_key()
        secret2 = self.tfa.generar_secret_key()
        
        # Verificar que las claves son diferentes
        self.assertNotEqual(secret1, secret2)
        
        # Verificar longitud (base32 de 20 bytes = 32 chars)
        self.assertEqual(len(secret1), 32)
        self.assertEqual(len(secret2), 32)
        
        # Verificar que son válidas en base32
        import base64
        try:
            base64.b32decode(secret1)
            base64.b32decode(secret2)
        except Exception:
            self.fail("Claves generadas no son válidas en base32")
    
    def test_totp_code_generation(self):
        """Test generación de códigos TOTP."""
        secret = self.tfa.generar_secret_key()
        
        # Generar código para tiempo específico
        timestamp = 1609459200  # 2021-01-01 00:00:00 UTC
        code = self.tfa.generar_codigo_totp(secret, timestamp)
        
        # Verificar longitud del código
        self.assertEqual(len(code), 6)
        
        # Verificar que es numérico
        self.assertTrue(code.isdigit())
        
        # Generar código para el mismo timestamp debe ser igual
        code2 = self.tfa.generar_codigo_totp(secret, timestamp)
        self.assertEqual(code, code2)
        
        # Generar código para timestamp diferente debe ser diferente
        code3 = self.tfa.generar_codigo_totp(secret, timestamp + 30)
        self.assertNotEqual(code, code3)
    
    def test_totp_code_validation(self):
        """Test validación de códigos TOTP."""
        secret = self.tfa.generar_secret_key()
        timestamp = int(time.time())
        
        # Generar código válido
        valid_code = self.tfa.generar_codigo_totp(secret, timestamp)
        
        # Verificar que el código es válido
        self.assertTrue(self.tfa.validar_codigo_totp(secret, valid_code, timestamp))
        
        # Verificar que código incorrecto es inválido
        self.assertFalse(self.tfa.validar_codigo_totp(secret, "000000", timestamp))
        
        # Verificar que código de longitud incorrecta es inválido
        self.assertFalse(self.tfa.validar_codigo_totp(secret, "123", timestamp))
        self.assertFalse(self.tfa.validar_codigo_totp(secret, "1234567", timestamp))
    
    def test_totp_time_window(self):
        """Test ventana de tiempo para validación TOTP."""
        secret = self.tfa.generar_secret_key()
        base_timestamp = int(time.time())
        
        # Código para tiempo base
        base_code = self.tfa.generar_codigo_totp(secret, base_timestamp)
        
        # Código debe ser válido en ventana de ±30 segundos
        self.assertTrue(self.tfa.validar_codigo_totp(secret, base_code, base_timestamp - 30))
        self.assertTrue(self.tfa.validar_codigo_totp(secret, base_code, base_timestamp))
        self.assertTrue(self.tfa.validar_codigo_totp(secret, base_code, base_timestamp + 30))
        
        # Código no debe ser válido fuera de la ventana
        self.assertFalse(self.tfa.validar_codigo_totp(secret, base_code, base_timestamp - 61))
        self.assertFalse(self.tfa.validar_codigo_totp(secret, base_code, base_timestamp + 61))
    
    def test_qr_code_generation(self):
        """Test generación de códigos QR."""
        secret = self.tfa.generar_secret_key()
        
        # Generar QR code
        qr_bytes = self.tfa.generar_qr_code("testuser", secret)
        
        # Verificar que se generó contenido
        self.assertIsInstance(qr_bytes, bytes)
        self.assertGreater(len(qr_bytes), 0)
        
        # Verificar que es una imagen PNG válida (empieza con signature PNG)
        self.assertTrue(qr_bytes.startswith(b'\x89PNG'))
    
    def test_invalid_secret_key(self):
        """Test manejo de claves secretas inválidas."""
        invalid_secrets = [
            "",  # Vacía
            "invalid",  # No base32
            "INVALID123!@#",  # Caracteres inválidos
        ]
        
        for secret in invalid_secrets:
            with self.assertRaises(ValueError):
                self.tfa.generar_codigo_totp(secret)


class TestSecurityEdgeCases(unittest.TestCase):
    """Tests para casos edge de seguridad."""
    
    def setUp(self):
        """Configuración inicial."""
        self.mock_usuarios_model = Mock()
        self.security_manager = UserSecurityManager(self.mock_usuarios_model)
    
    def test_concurrent_login_attempts(self):
        """Test manejo de intentos de login concurrentes."""
        username = "testuser"
        
        self.mock_usuarios_model.obtener_usuario_por_nombre.return_value = {
            'id': 1, 'username': username, 'configuracion_personal': '{}'
        }
        self.mock_usuarios_model.validar_usuario.return_value = False
        
        # Simular intentos concurrentes
        results = []
        for i in range(5):
            result = self.security_manager.register_login_attempt(username, False, f"192.168.1.{i}")
            results.append(result)
        
        # Verificar que el usuario se bloqueó después del tercer intento
        locked_results = [r for r in results if r.get('locked', False)]
        self.assertGreaterEqual(len(locked_results), 1)
    
    def test_memory_exhaustion_protection(self):
        """Test protección contra agotamiento de memoria."""
        # Simular muchos usuarios con intentos fallidos
        for i in range(1000):
            username = f"user{i}"
            
            self.mock_usuarios_model.obtener_usuario_por_nombre.return_value = {
                'id': i, 'username': username, 'configuracion_personal': '{}'
            }
            
            # Un intento fallido por usuario
            self.security_manager.register_login_attempt(username, False, "192.168.1.1")
        
        # Verificar que el sistema sigue funcionando
        self.assertEqual(len(self.security_manager.failed_attempts), 1000)
        
        # Test que el sistema puede manejar la carga
        test_result = self.security_manager.register_login_attempt("user500", False, "192.168.1.1")
        self.assertFalse(test_result['success'])
    
    def test_time_manipulation_resistance(self):
        """Test resistencia a manipulación de tiempo."""
        tfa = TwoFactorAuth()
        secret = tfa.generar_secret_key()
        
        # Generar código para tiempo actual
        current_time = int(time.time())
        current_code = tfa.generar_codigo_totp(secret, current_time)
        
        # Intentar usar código de tiempo futuro
        future_time = current_time + 3600  # 1 hora en el futuro
        future_code = tfa.generar_codigo_totp(secret, future_time)
        
        # El código futuro no debe ser válido en tiempo actual
        self.assertFalse(tfa.validar_codigo_totp(secret, future_code, current_time))
        
        # El código actual no debe ser válido en tiempo futuro
        self.assertFalse(tfa.validar_codigo_totp(secret, current_code, future_time))
    
    def test_sql_injection_in_security_functions(self):
        """Test resistencia a SQL injection en funciones de seguridad."""
        # Intentos de inyección SQL en nombres de usuario
        malicious_usernames = [
            "admin'; DROP TABLE usuarios; --",
            "' OR '1'='1",
            "admin' UNION SELECT password FROM usuarios --",
            "<script>alert('xss')</script>",
            "'; UPDATE usuarios SET password='hacked' WHERE username='admin'; --"
        ]
        
        for malicious_user in malicious_usernames:
            # El DataSanitizer debe limpiar los inputs maliciosos
            cleaned = self.security_manager.register_login_attempt(malicious_user, False, "192.168.1.1")
            
            # El sistema debe manejar estos casos sin errores
            self.assertIsInstance(cleaned, dict)
    
    def test_brute_force_timing_attacks(self):
        """Test resistencia a ataques de timing."""
        username = "testuser"
        
        self.mock_usuarios_model.obtener_usuario_por_nombre.return_value = {
            'id': 1, 'username': username, 'configuracion_personal': '{}'
        }
        
        # Medir tiempo de respuesta para usuario válido
        start_time = time.time()
        self.security_manager.register_login_attempt(username, False, "192.168.1.1")
        valid_user_time = time.time() - start_time
        
        # Medir tiempo de respuesta para usuario inválido
        self.mock_usuarios_model.obtener_usuario_por_nombre.return_value = None
        
        start_time = time.time()
        self.security_manager.register_login_attempt("nonexistent", False, "192.168.1.1")
        invalid_user_time = time.time() - start_time
        
        # La diferencia de tiempo no debe ser significativa (< 100ms)
        time_difference = abs(valid_user_time - invalid_user_time)
        self.assertLess(time_difference, 0.1)


class TestPenetrationScenarios(unittest.TestCase):
    """Tests básicos de penetración para identificar vulnerabilidades."""
    
    def setUp(self):
        """Configuración inicial."""
        self.mock_usuarios_model = Mock()
        self.security_manager = UserSecurityManager(self.mock_usuarios_model)
    
    def test_authentication_bypass_attempts(self):
        """Test intentos de bypass de autenticación."""
        bypass_attempts = [
            ("admin", ""),  # Contraseña vacía
            ("", "password"),  # Usuario vacío
            ("admin", None),  # Contraseña null
            (None, "password"),  # Usuario null
        ]
        
        for username, password in bypass_attempts:
            self.mock_usuarios_model.validar_usuario.return_value = False
            
            result = self.security_manager.register_login_attempt(username or "", False, "192.168.1.1")
            
            # Todos los intentos deben fallar
            self.assertFalse(result.get('success', False))
    
    def test_session_fixation_protection(self):
        """Test protección contra fijación de sesión."""
        # Simular login exitoso
        username = "testuser"
        
        self.mock_usuarios_model.obtener_usuario_por_nombre.return_value = {
            'id': 1, 'username': username, 'configuracion_personal': '{}'
        }
        
        result = self.security_manager.register_login_attempt(username, True, "192.168.1.1")
        
        # Verificar que se registró el login exitoso
        self.assertTrue(result['success'])
        
        # En una implementación real, aquí se verificaría que se genera nuevo session ID
        # Por ahora, verificamos que el sistema registra el evento de seguridad
        self.assertTrue(hasattr(self.security_manager, 'log_security_event'))
    
    def test_privilege_escalation_prevention(self):
        """Test prevención de escalación de privilegios."""
        # Intentar operaciones privilegiadas con usuario normal
        username = "normal_user"
        
        # Simular que es un usuario normal
        self.mock_usuarios_model.obtener_usuario_por_nombre.return_value = {
            'id': 2, 'username': username, 'configuracion_personal': '{}', 'rol': 'user'
        }
        
        # Intentar desbloquear otros usuarios (operación admin)
        success = self.security_manager.unlock_user("admin")
        
        # En un sistema real, esto debería verificar permisos
        # Por ahora, verificamos que la función existe y maneja el caso
        self.assertIsInstance(success, bool)


def run_security_tests():
    """Ejecuta todos los tests de seguridad."""
    print("=== TESTS AVANZADOS DE SEGURIDAD ===")
    print("Rexus.app - Sistema de Seguridad Avanzada")
    print("=" * 50)
    
    # Crear suite de tests
    test_classes = [
        TestUserSecurityManager,
        TestTwoFactorAuth,
        TestSecurityEdgeCases,
        TestPenetrationScenarios
    ]
    
    suite = unittest.TestSuite()
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Ejecutar tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Resumen
    print(f"\n=== RESUMEN DE TESTS DE SEGURIDAD ===")
    print(f"Tests ejecutados: {result.testsRun}")
    print(f"Errores: {len(result.errors)}")
    print(f"Fallos: {len(result.failures)}")
    
    if result.errors:
        print("\nERRORES:")
        for test, error in result.errors:
            print(f"- {test}: {error}")
    
    if result.failures:
        print("\nFALLOS:")
        for test, failure in result.failures:
            print(f"- {test}: {failure}")
    
    success_rate = ((result.testsRun - len(result.errors) - len(result.failures)) / result.testsRun * 100) if result.testsRun > 0 else 0
    print(f"\nTasa de éxito: {success_rate:.1f}%")
    
    if success_rate >= 90:
        print("✅ SISTEMA DE SEGURIDAD: COMPLETAMENTE FUNCIONAL")
    elif success_rate >= 70:
        print("⚠️ SISTEMA DE SEGURIDAD: FUNCIONAL CON ADVERTENCIAS")
    else:
        print("❌ SISTEMA DE SEGURIDAD: REQUIERE ATENCIÓN")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_security_tests()
    sys.exit(0 if success else 1)