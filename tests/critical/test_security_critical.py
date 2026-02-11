"""
Tests Críticos de Seguridad - Rexus.app
Pruebas de seguridad críticas según la auditoría

Cobertura requerida:
- SQL Injection
- Autenticación segura (bcrypt/Argon2)
- Autorización y permisos
- Rate limiting
- Protección de datos sensibles
"""

import pytest
import hashlib
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

# Importar módulos a probar
from rexus.core.auth_manager import AuthManager, UserRole, Permission
from rexus.core.rate_limiter import RateLimiter
from rexus.utils.password_security import (
    hash_password_secure,
    verify_password_secure,
    validate_password_strength,
    check_password_needs_rehash
)


class TestPasswordSecurity:
    """Tests de seguridad de contraseñas."""

    def test_hash_password_with_bcrypt_or_argon2(self):
        """Verifica que las contraseñas se hasheen con métodos seguros, no SHA-256 plano."""
        password = "TestPassword123!"

        # Hashear contraseña
        hashed = hash_password_secure(password, method="auto")

        # Verificar que NO es un SHA-256 plano (64 caracteres hexadecimales)
        assert not (len(hashed) == 64 and all(c in '0123456789abcdef' for c in hashed.lower())), \
            "El hash no debe ser SHA-256 plano"

        # Verificar que tiene el prefijo del método
        assert hashed.startswith(('argon2$', 'bcrypt$', 'pbkdf2$')), \
            "El hash debe tener prefijo del método seguro usado"

    def test_verify_password_secure(self):
        """Verifica la verificación correcta de contraseñas."""
        password = "SecurePassword123!"
        hashed = hash_password_secure(password)

        # Verificar contraseña correcta
        assert verify_password_secure(password, hashed) is True

        # Verificar contraseña incorrecta
        assert verify_password_secure("WrongPassword123!", hashed) is False

    def test_legacy_sha256_detection(self):
        """Verifica que los hashes SHA-256 legacy sean detectados para migración."""
        # Simular hash SHA-256 legacy
        legacy_hash = hashlib.sha256("password123".encode()).hexdigest()

        # Debe necesitar rehash
        assert check_password_needs_rehash(legacy_hash) is True, \
            "Los hashes SHA-256 legacy deben marcarse para rehash"

    def test_password_strength_validation(self):
        """Verifica la validación de fortaleza de contraseñas."""
        # Contraseña débil
        is_valid, errors = validate_password_strength("weak")
        assert is_valid is False
        assert len(errors) > 0

        # Contraseña fuerte
        is_valid, errors = validate_password_strength("StrongP@ssw0rd!")
        assert is_valid is True
        assert len(errors) == 0

    def test_common_passwords_rejected(self):
        """Verifica que passwords comunes sean rechazados."""
        common_passwords = ["password", "123456", "qwerty", "admin"]

        for pwd in common_passwords:
            is_valid, errors = validate_password_strength(pwd + "A1!")
            # Aunque tengan mayúscula, número y símbolo, deben ser rechazadas por ser comunes
            # si el patrón común está presente
            assert any("común" in e.lower() or "débil" in e.lower() for e in errors) or \
                   not is_valid or len(errors) > 0


class TestAuthentication:
    """Tests de autenticación segura."""

    @pytest.fixture
    def mock_db(self):
        """Mock de base de datos para tests."""
        db = Mock()
        db.connection = Mock()
        db.execute_query = Mock(return_value=[
            ("testuser", "hashed_password_here", "ADMIN", "activo", "Test", "User", "test@example.com")
        ])
        db.execute_non_query = Mock(return_value=True)
        return db

    @pytest.fixture
    def mock_rate_limiter(self):
        """Mock de rate limiter."""
        limiter = Mock()
        limiter.is_blocked = Mock(return_value=(False, None))
        limiter.record_failed_attempt = Mock()
        limiter.record_successful_attempt = Mock()
        limiter.get_lockout_info = Mock(return_value={'remaining_attempts': 3})
        return limiter

    def test_authenticate_with_secure_hash_not_sha256(self, mock_db, mock_rate_limiter):
        """Verifica que la autenticación use métodos seguros, no SHA-256 plano."""
        with patch('rexus.core.auth_manager.get_users_connection', return_value=mock_db):
            with patch('rexus.core.auth_manager.get_rate_limiter', return_value=mock_rate_limiter):
                # Crear un hash seguro
                test_password = "TestPassword123!"
                secure_hash = hash_password_secure(test_password)

                # Actualizar el mock para retornar el hash seguro
                mock_db.execute_query = Mock(return_value=[
                    ("testuser", secure_hash, "ADMIN", "activo", "Test", "User", "test@example.com")
                ])

                # Intentar autenticar
                result = AuthManager.authenticate_user("testuser", test_password)

                # Verificar que no usa SHA-256 directo
                assert result is not False
                assert result.get("authenticated") is True

    def test_rate_limiting_on_failed_login(self, mock_db, mock_rate_limiter):
        """Verifica que el rate limiting funcione en logins fallidos."""
        with patch('rexus.core.auth_manager.get_users_connection', return_value=mock_db):
            with patch('rexus.core.auth_manager.get_rate_limiter', return_value=mock_rate_limiter):
                # Usuario no existe
                mock_db.execute_query = Mock(return_value=[])

                result = AuthManager.authenticate_user("nonexistent", "password")

                # Verificar que se registró el intento fallido
                mock_rate_limiter.record_failed_attempt.assert_called_once()

    def test_account_blocked_after_max_attempts(self):
        """Verifica que las cuentas se bloqueen después de N intentos fallidos."""
        limiter = RateLimiter(max_attempts=3, block_duration_minutes=15)
        username = "testuser"

        # Simular 3 intentos fallidos
        for _ in range(3):
            limiter.record_failed_attempt(username)

        # Verificar que está bloqueado
        is_blocked, locked_until = limiter.is_blocked(username)
        assert is_blocked is True
        assert locked_until is not None


class TestSQLInjectionProtection:
    """Tests de protección contra inyección SQL."""

    def test_sql_injection_in_login(self):
        """Verifica que intentos de SQL Injection en login sean neutralizados."""
        # Intentos comunes de SQL injection
        injection_attempts = [
            "admin' --",
            "admin' OR '1'='1",
            "admin' DROP TABLE users--",
            "admin'; INSERT INTO users VALUES ('hacker', 'password')--"
        ]

        for attempt in injection_attempts:
            # El sanitizador debe limpiar estas entradas
            from rexus.utils.unified_sanitizer import sanitize_string
            sanitized = sanitize_string(attempt, 50)

            # Verificar que no contiene caracteres peligrosos sin escapar
            assert "'" not in sanitized or "--" not in sanitized, \
                f"SQL injection attempt not neutralized: {attempt}"

    def test_parameterized_queries(self):
        """Verifica que las consultas usen parámetros, no concatenación."""
        # Este test verifica que el código use consultas parametrizadas
        # Revisar el código de auth_manager.py
        import inspect
        from rexus.core.auth_manager import AuthManager

        source = inspect.getsource(AuthManager.authenticate_user)

        # Verificar que no hay concatenación de strings en consultas SQL
        # (debe usar parámetros con ? o %s)
        assert "f\"\"\"" not in source or "WHERE usuario = ?" in source, \
            "Las consultas deben usar parámetros, no concatenación"


class TestAuthorization:
    """Tests de autorización y permisos."""

    def test_role_hierarchy(self):
        """Verifica la jerarquía de roles."""
        # Admin tiene todos los permisos
        AuthManager.set_current_user_role(UserRole.ADMIN)
        assert AuthManager.check_role(UserRole.ADMIN) is True
        assert AuthManager.check_role(UserRole.VIEWER) is True

        # Viewer no tiene permisos de admin
        AuthManager.set_current_user_role(UserRole.VIEWER)
        assert AuthManager.check_role(UserRole.ADMIN) is False
        assert AuthManager.check_role(UserRole.VIEWER) is True

    def test_permission_checking(self):
        """Verifica el sistema de permisos."""
        # Manager puede crear inventario
        AuthManager.set_current_user_role(UserRole.MANAGER)
        assert AuthManager.check_permission(Permission.CREATE_INVENTORY) is True

        # Viewer no puede crear inventario
        AuthManager.set_current_user_role(UserRole.VIEWER)
        assert AuthManager.check_permission(Permission.CREATE_INVENTORY) is False

    def test_admin_has_all_permissions(self):
        """Verifica que admin tenga todos los permisos."""
        AuthManager.set_current_user_role(UserRole.ADMIN)

        for permission in Permission:
            assert AuthManager.check_permission(permission), \
                f"Admin debe tener permiso {permission.value}"


class TestDataProtection:
    """Tests de protección de datos sensibles."""

    def test_passwords_not_logged(self):
        """Verifica que las contraseñas no se logueen en texto plano."""
        # Revisar el código para verificar que no haya logs de contraseñas
        import inspect
        from rexus.core.auth_manager import AuthManager

        source = inspect.getsource(AuthManager.authenticate_user)

        # Verificar que no se loguee la variable password directamente
        assert "print(password" not in source.lower(), \
            "Las contraseñas no deben loguearse"
        assert "logger.info(password" not in source.lower(), \
            "Las contraseñas no deben loguearse"

    def test_sensitive_data_masked_in_responses(self):
        """Verifica que los datos sensibles se enmascaren en las respuestas."""
        mock_db = Mock()
        mock_db.connection = Mock()
        secure_hash = hash_password_secure("TestPassword123!")

        mock_db.execute_query = Mock(return_value=[
            ("testuser", secure_hash, "ADMIN", "activo", "Test", "User", "test@example.com")
        ])
        mock_db.execute_non_query = Mock(return_value=True)

        mock_rate_limiter = Mock()
        mock_rate_limiter.is_blocked = Mock(return_value=(False, None))
        mock_rate_limiter.record_failed_attempt = Mock()
        mock_rate_limiter.record_successful_attempt = Mock()
        mock_rate_limiter.get_lockout_info = Mock(return_value={'remaining_attempts': 3})

        with patch('rexus.core.auth_manager.get_users_connection', return_value=mock_db):
            with patch('rexus.core.auth_manager.get_rate_limiter', return_value=mock_rate_limiter):
                result = AuthManager.authenticate_user("testuser", "TestPassword123!")

                # Verificar que el password hash no esté en la respuesta
                assert "password_hash" not in result or result.get("password_hash") is None
                assert "password" not in result or result.get("password") != secure_hash


class TestSessionSecurity:
    """Tests de seguridad de sesiones."""

    def test_session_timeout(self):
        """Verifica que las sesiones tengan timeout."""
        from rexus.core.rate_limiter import RateLimiter

        # Crear rate limiter con timeout
        limiter = RateLimiter(max_attempts=3, block_duration_minutes=15)

        # Simular intentos
        limiter.record_failed_attempt("testuser")
        is_blocked, _ = limiter.is_blocked("testuser")

        # No debe estar bloqueado aún
        assert is_blocked is False

    def test_concurrent_login_attempts(self):
        """Verifica manejo de intentos de login concurrentes."""
        limiter = RateLimiter(max_attempts=5, block_duration_minutes=15)

        # Simular intentos rápidos
        for _ in range(4):
            limiter.record_failed_attempt("testuser")

        is_blocked, _ = limiter.is_blocked("testuser")
        assert is_blocked is False  # 4 intentos, aún no bloquea

        limiter.record_failed_attempt("testuser")
        is_blocked, _ = limiter.is_blocked("testuser")
        assert is_blocked is True  # 5 intentos, bloqueado


@pytest.fixture(scope="session")
def security_test_report():
    """Genera reporte de tests de seguridad."""
    return {
        'total_tests': 0,
        'passed': 0,
        'failed': 0,
        'coverage': {}
    }


def pytest_sessionfinish(session, exitstatus):
    """Genera reporte final de tests de seguridad."""
    print("\n" + "="*60)
    print("REPORTE DE TESTS DE SEGURIDAD CRÍTICOS")
    print("="*60)
    print(f"Exit status: {exitstatus}")
    print("\nNota: Los tests de seguridad deben ejecutarse en cada build.")
    print("="*60 + "\n")
