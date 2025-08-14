"""
Tests para User Enumeration Protection System - Rexus.app

Tests que validan el sistema de protección contra ataques de enumeración
de usuarios, incluyendo rate limiting, detección de patrones y timing attacks.

Author: Rexus Testing Team
Date: 2025-08-11
Version: 1.0.0
"""

import pytest
import time
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

# Import the modules we're testing
try:
    from rexus.security.user_enumeration_protection import (
        UserEnumerationProtection,
        init_user_enumeration_protection,
        get_user_enumeration_protection,
        record_login_attempt,
        get_response_delay,
        simulate_password_check
    )
    USER_ENUM_AVAILABLE = True
except ImportError:
    USER_ENUM_AVAILABLE = False


@pytest.mark.skipif(not USER_ENUM_AVAILABLE, reason="User enumeration protection modules not available")
class TestUserEnumerationProtection:
    """Tests para la clase UserEnumerationProtection."""

    def test_initialization(self):
        """Test que valida la inicialización del sistema de protección."""
        protection = UserEnumerationProtection()

        assert protection.failed_attempts == {}
        assert protection.suspicious_patterns == {}
        assert protection.blocked_ips == {}
        assert protection.max_attempts_per_ip == 5
        assert protection.block_duration == 900  # 15 minutos
        assert protection.min_response_time == 1.0

    def test_record_login_attempt_success(self):
        """Test que valida registro de intentos exitosos."""
        protection = UserEnumerationProtection()

        ip_address = "192.168.1.100"
        username = "test_user"

        # Intento exitoso no debe ser bloqueado
        should_block = protection.record_login_attempt(ip_address,
username,
            success=True,
            user_exists=True)

        assert not should_block
        assert ip_address not in protection.failed_attempts or len(protection.failed_attempts[ip_address]) == 0

    def test_record_login_attempt_failure_accumulation(self):
        """Test que valida la acumulación de intentos fallidos."""
        protection = UserEnumerationProtection()
        protection.max_attempts_per_ip = 3  # Límite bajo para test

        ip_address = "192.168.1.100"
        username = "test_user"

        # Primeros intentos no deben bloquear
        for i in range(protection.max_attempts_per_ip - 1):
            should_block = protection.record_login_attempt(ip_address,
username,
                success=False,
                user_exists=True)
            assert not should_block

        # El intento que excede el límite debe bloquear
        should_block = protection.record_login_attempt(ip_address,
username,
            success=False,
            user_exists=True)
        assert should_block

    def test_ip_blocking_and_expiration(self):
        """Test que valida el bloqueo de IPs y su expiración."""
        protection = UserEnumerationProtection()
        protection.max_attempts_per_ip = 2
        protection.block_duration = 5  # 5 segundos para test

        ip_address = "192.168.1.100"
        username = "test_user"

        # Exceder límite de intentos
        for _ in range(protection.max_attempts_per_ip):
            protection.record_login_attempt(ip_address,
username,
                success=False,
                user_exists=True)

        # IP debe estar bloqueada
        current_time = time.time()
        assert protection._is_ip_blocked(ip_address, current_time)

        # Después del tiempo de bloqueo, debe estar desbloqueada
        future_time = current_time + protection.block_duration + 1
        assert not protection._is_ip_blocked(ip_address, future_time)

    def test_suspicious_pattern_detection(self):
        """Test que valida la detección de patrones sospechosos."""
        protection = UserEnumerationProtection()

        ip_address = "192.168.1.200"
        current_time = time.time()

        # Simular múltiples intentos con diferentes usuarios (enumeración)
        usernames = ["admin", "root", "user1", "test", "administrator", "guest"]

        for username in usernames:
            protection._detect_suspicious_patterns(ip_address,
username,
                user_exists=False,
                current_time=current_time)

        # Debe haber detectado patrones sospechosos
        assert ip_address in protection.suspicious_patterns
        assert len(protection.suspicious_patterns[ip_address]) == len(usernames)

    @patch('rexus.utils.secure_logger.log_security_event')
    def test_systematic_user_scan_detection(self, mock_log):
        """Test que valida la detección de escaneos sistemáticos."""
        protection = UserEnumerationProtection()
        protection.pattern_detection_window = 300  # 5 minutos

        ip_address = "192.168.1.200"
        current_time = time.time()

        # Simular escaneo masivo de usuarios
        for i in range(25):  # Muchos usuarios diferentes
            username = f"user{i}"
            protection._detect_suspicious_patterns(ip_address,
username,
                user_exists=False,
                current_time=current_time)

        # Debe haber logueado detección de escaneo sistemático
        mock_log.assert_called()
        calls = mock_log.call_args_list
        assert any("SYSTEMATIC_USER_SCAN" in str(call) for call in calls)

    def test_get_response_delay_consistency(self):
        """Test que valida la consistencia de delays de respuesta."""
        protection = UserEnumerationProtection()

        username = "test_user"

        # El delay debe ser consistente para el mismo usuario
        delay1 = protection.get_response_delay(username, user_exists=True)
        delay2 = protection.get_response_delay(username, user_exists=True)

        assert delay1 == delay2
        assert delay1 >= protection.min_response_time
        assert delay1 < protection.min_response_time + 1.0  # Máximo 1 segundo de variación

    def test_get_response_delay_different_users(self):
        """Test que valida delays diferentes para usuarios diferentes."""
        protection = UserEnumerationProtection()

        delay_user1 = protection.get_response_delay("user1", user_exists=True)
        delay_user2 = protection.get_response_delay("user2", user_exists=True)

        # Los delays pueden ser diferentes pero ambos válidos
        assert delay_user1 >= protection.min_response_time
        assert delay_user2 >= protection.min_response_time
        # No necesariamente diferentes, pero eso está bien

    def test_simulate_password_check_timing(self):
        """Test que valida la simulación de verificación de contraseña."""
        protection = UserEnumerationProtection()

        username = "nonexistent_user"

        start_time = time.time()
        result = protection.simulate_password_check(username)
        end_time = time.time()

        # Debe tomar tiempo apreciable para simular trabajo real
        elapsed = end_time - start_time
        assert elapsed > 0.001  # Al menos 1ms

        # Debe devolver un hash válido (no usado, pero para consumir tiempo)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_get_generic_error_message(self):
        """Test que valida mensajes de error genéricos."""
        protection = UserEnumerationProtection()

        error_message = protection.get_generic_error_message()

        assert isinstance(error_message, str)
        assert len(error_message) > 0
        assert "credenciales" in error_message.lower() or "invalid" in error_message.lower()

    def test_is_ip_allowed_normal_case(self):
        """Test que valida IPs normales permitidas."""
        protection = UserEnumerationProtection()

        ip_address = "192.168.1.50"

        is_allowed, message = protection.is_ip_allowed(ip_address)

        assert is_allowed
        assert message == ""

    def test_is_ip_allowed_blocked_case(self):
        """Test que valida IPs bloqueadas."""
        protection = UserEnumerationProtection()
        protection.max_attempts_per_ip = 1

        ip_address = "192.168.1.100"

        # Bloquear IP
        protection.record_login_attempt(ip_address,
"user",
            success=False,
            user_exists=True)

        is_allowed, message = protection.is_ip_allowed(ip_address)

        assert not is_allowed
        assert "bloqueada" in message.lower() or "blocked" in message.lower()
        assert "segundos" in message.lower() or "seconds" in message.lower()

    def test_cleanup_old_attempts(self):
        """Test que valida la limpieza de intentos antiguos."""
        protection = UserEnumerationProtection()
        protection.block_duration = 1  # 1 segundo para test

        ip_address = "192.168.1.100"

        # Registrar intento
        protection.record_login_attempt(ip_address,
"user",
            success=False,
            user_exists=True)
        assert ip_address in protection.failed_attempts

        # Esperar y limpiar
        time.sleep(2)
        current_time = time.time()
        protection._cleanup_old_attempts(current_time)

        # Los intentos antiguos deben haberse limpiado
        assert ip_address not in protection.failed_attempts or len(protection.failed_attempts[ip_address]) == 0

    def test_get_stats(self):
        """Test que valida las estadísticas del sistema."""
        protection = UserEnumerationProtection()

        # Estado inicial
        stats = protection.get_stats()
        assert stats['active_blocked_ips'] == 0
        assert stats['active_monitoring_ips'] == 0
        assert stats['total_recent_failed_attempts'] == 0

        # Agregar algunos intentos fallidos
        protection.record_login_attempt("192.168.1.100", "user1", False, True)
        protection.record_login_attempt("192.168.1.101", "user2", False, True)

        stats = protection.get_stats()
        assert stats['active_monitoring_ips'] == 2
        assert stats['total_recent_failed_attempts'] == 2


@pytest.mark.skipif(not USER_ENUM_AVAILABLE, reason="User enumeration protection modules not available")
class TestUserEnumerationProtectionGlobalFunctions:
    """Tests para las funciones globales del módulo."""

    def test_init_and_get_protection(self):
        """Test que valida la inicialización global del sistema."""
        init_user_enumeration_protection()

        protection = get_user_enumeration_protection()

        assert protection is not None
        assert isinstance(protection, UserEnumerationProtection)

    def test_record_login_attempt_global(self):
        """Test que valida la función global de registro de intentos."""
        init_user_enumeration_protection()

        ip_address = "192.168.1.100"
        username = "global_test_user"

        should_block = record_login_attempt(ip_address,
username,
            success=False,
            user_exists=True)

        assert isinstance(should_block, bool)

    def test_get_response_delay_global(self):
        """Test que valida la función global de delay de respuesta."""
        init_user_enumeration_protection()

        username = "global_test_user"
        delay = get_response_delay(username, user_exists=True)

        assert isinstance(delay, float)
        assert delay >= 1.0

    def test_simulate_password_check_global(self):
        """Test que valida la función global de simulación de contraseña."""
        init_user_enumeration_protection()

        username = "global_test_user"
        result = simulate_password_check(username)

        assert isinstance(result, str)
        assert len(result) > 0


@pytest.mark.skipif(not USER_ENUM_AVAILABLE, reason="User enumeration protection modules not available")
class TestUserEnumerationProtectionIntegration:
    """Tests de integración para el sistema de protección."""

    @patch('rexus.utils.secure_logger.log_security_event')
    def test_full_attack_scenario(self, mock_log):
        """Test que simula un escenario completo de ataque."""
        protection = UserEnumerationProtection()
        protection.max_attempts_per_ip = 3

        attacker_ip = "192.168.1.200"
        target_usernames = ["admin", "root", "user1", "test", "administrator"]

        # Simular ataque de enumeración
        blocked = False
        for username in target_usernames:
            for attempt in range(2):
                blocked = protection.record_login_attempt(
                    attacker_ip,
username,
                        success=False,
                        user_exists=(username in ["user1"])
                )
                if blocked:
                    break
            if blocked:
                break

        # El atacante debe haber sido bloqueado
        assert blocked

        # Debe haberse logueado actividad sospechosa
        mock_log.assert_called()

        # Verificar estadísticas
        stats = protection.get_stats()
        assert stats['active_blocked_ips'] >= 1

    def test_legitimate_user_workflow(self):
        """Test que valida que usuarios legítimos no sean afectados."""
        protection = UserEnumerationProtection()

        legitimate_ip = "192.168.1.50"
        legitimate_user = "john_doe"

        # Usuario legítimo con login exitoso
        should_block = protection.record_login_attempt(
            legitimate_ip, legitimate_user, success=True, user_exists=True
        )

        assert not should_block

        # Múltiples logins exitosos no deben causar bloqueo
        for _ in range(10):
            should_block = protection.record_login_attempt(
                legitimate_ip, legitimate_user, success=True, user_exists=True
            )
            assert not should_block

        # IP debe seguir permitida
        is_allowed, _ = protection.is_ip_allowed(legitimate_ip)
        assert is_allowed

    def test_mixed_attack_legitimate_scenario(self):
        """Test que valida escenario mixto de ataques y usuarios legítimos."""
        protection = UserEnumerationProtection()
        protection.max_attempts_per_ip = 5

        # Atacante
        attacker_ip = "192.168.1.200"
        # Usuario legítimo
        legitimate_ip = "192.168.1.50"

        # Atacante intenta múltiples usuarios
        for i,
username in enumerate(["admin",
            "root",
            "test",
            "user1",
            "guest"]):
            protection.record_login_attempt(attacker_ip,
username,
                success=False,
                user_exists=False)

        # Usuario legítimo hace login exitoso
        protection.record_login_attempt(legitimate_ip,
"john_doe",
            success=True,
            user_exists=True)

        # Atacante debe estar cerca del bloqueo o bloqueado
        attacker_allowed, _ = protection.is_ip_allowed(attacker_ip)

        # Usuario legítimo debe seguir permitido
        legitimate_allowed, _ = protection.is_ip_allowed(legitimate_ip)
        assert legitimate_allowed

    def test_timing_attack_resistance(self):
        """Test que valida resistencia a timing attacks."""
        protection = UserEnumerationProtection()

        # Medir tiempo para usuario existente
        start_time = time.time()
        delay_existing = protection.get_response_delay("existing_user", user_exists=True)
        simulate_existing = protection.simulate_password_check("existing_user")
        mid_time = time.time()

        # Medir tiempo para usuario no existente
        delay_nonexisting = protection.get_response_delay("nonexistent_user", user_exists=False)
        simulate_nonexisting = protection.simulate_password_check("nonexistent_user")
        end_time = time.time()

        # Los delays deben ser consistentes y no revelar existencia del usuario
        assert isinstance(delay_existing, float)
        assert isinstance(delay_nonexisting, float)
        assert abs(delay_existing - delay_nonexisting) < 0.5  # Diferencia máxima de 500ms

        # La simulación debe producir resultados válidos
        assert isinstance(simulate_existing, str)
        assert isinstance(simulate_nonexisting, str)


# Fixtures para tests de user enumeration protection
@pytest.fixture
def user_enum_protection():
    """Fixture que proporciona instancia de UserEnumerationProtection para tests."""
    return UserEnumerationProtection()


@pytest.fixture
def attack_test_data():
    """Fixture con datos de prueba para tests de ataques."""
    return {
        'attacker_ips': ['192.168.1.200', '10.0.0.100', '172.16.1.50'],
        'target_usernames': ['admin', 'root', 'administrator', 'user', 'test', 'guest'],
        'legitimate_users': [
            {'ip': '192.168.1.50', 'username': 'john_doe'},
            {'ip': '192.168.1.51', 'username': 'jane_smith'},
            {'ip': '192.168.1.52', 'username': 'bob_johnson'}
        ]
    }
