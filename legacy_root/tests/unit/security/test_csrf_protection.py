"""
Tests para CSRF Protection System - Rexus.app

Tests que validan el sistema de protección contra ataques CSRF,
incluyendo generación de tokens, validación y limpieza automática.

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
    from rexus.security.csrf_protection import (
        CSRFToken, 
        CSRFProtection, 
        init_csrf_protection, 
        get_csrf_protection,
        generate_csrf_token,
        validate_csrf_token
    )
    CSRF_AVAILABLE = True
except ImportError:
    CSRF_AVAILABLE = False


@pytest.mark.skipif(not CSRF_AVAILABLE, reason="CSRF protection modules not available")
class TestCSRFToken:
    """Tests para la clase CSRFToken."""
    
    def test_csrf_token_initialization(self):
        """Test que valida la inicialización del generador de tokens CSRF."""
        secret_key = "test_secret_key_for_csrf"
        csrf_token = CSRFToken(secret_key)
        
        assert csrf_token.secret_key == secret_key.encode()
        assert csrf_token.token_lifetime == 3600  # 1 hora por defecto
    
    def test_generate_token_creates_unique_tokens(self):
        """Test que valida que se generen tokens únicos."""
        secret_key = "test_secret_key"
        csrf_token = CSRFToken(secret_key)
        
        token1 = csrf_token.generate_token("user1", "session1")
        token2 = csrf_token.generate_token("user1", "session1")
        
        # Los tokens deben ser únicos aunque sean para el mismo usuario
        assert token1 != token2
        assert len(token1) > 20  # Debe tener longitud razonable
        assert isinstance(token1, str)
    
    def test_generate_token_different_users_different_tokens(self):
        """Test que valida que usuarios diferentes generen tokens diferentes."""
        secret_key = "test_secret_key"
        csrf_token = CSRFToken(secret_key)
        
        token_user1 = csrf_token.generate_token("user1", "session1")
        token_user2 = csrf_token.generate_token("user2", "session1")
        
        assert token_user1 != token_user2
    
    def test_validate_token_valid_token(self):
        """Test que valida tokens válidos."""
        secret_key = "test_secret_key"
        csrf_token = CSRFToken(secret_key)
        
        user_id = "test_user"
        session_id = "test_session"
        
        # Generar token
        token = csrf_token.generate_token(user_id, session_id)
        
        # Validar token inmediatamente
        is_valid, message = csrf_token.validate_token(token, user_id, session_id)
        
        assert is_valid
        assert "válido" in message.lower()
    
    def test_validate_token_wrong_user(self):
        """Test que valida que tokens no funcionen para usuarios incorrectos."""
        secret_key = "test_secret_key"
        csrf_token = CSRFToken(secret_key)
        
        # Generar token para user1
        token = csrf_token.generate_token("user1", "session1")
        
        # Intentar validar con user2
        is_valid, message = csrf_token.validate_token(token, "user2", "session1")
        
        assert not is_valid
        assert "usuario" in message.lower()
    
    def test_validate_token_wrong_session(self):
        """Test que valida que tokens no funcionen para sesiones incorrectas."""
        secret_key = "test_secret_key"
        csrf_token = CSRFToken(secret_key)
        
        # Generar token para session1
        token = csrf_token.generate_token("user1", "session1")
        
        # Intentar validar con session2
        is_valid, message = csrf_token.validate_token(token, "user1", "session2")
        
        assert not is_valid
        assert "sesión" in message.lower()
    
    def test_validate_token_invalid_format(self):
        """Test que valida rechazo de tokens con formato inválido."""
        secret_key = "test_secret_key"
        csrf_token = CSRFToken(secret_key)
        
        invalid_tokens = [
            "invalid_token",
            "",
            "not_base64_encoded",
            "dGVzdA==",  # válido base64 pero formato incorrecto
        ]
        
        for invalid_token in invalid_tokens:
            is_valid, message = csrf_token.validate_token(invalid_token, "user1", "session1")
            assert not is_valid
            assert len(message) > 0
    
    @patch('time.time')
    def test_validate_token_expired(self, mock_time):
        """Test que valida que tokens expirados sean rechazados."""
        secret_key = "test_secret_key"
        csrf_token = CSRFToken(secret_key)
        csrf_token.token_lifetime = 10  # 10 segundos para test
        
        # Generar token en tiempo inicial
        mock_time.return_value = 1000
        token = csrf_token.generate_token("user1", "session1")
        
        # Validar token después de expiración
        mock_time.return_value = 1020  # 20 segundos después
        is_valid, message = csrf_token.validate_token(token, "user1", "session1")
        
        assert not is_valid
        assert "expirado" in message.lower()


@pytest.mark.skipif(not CSRF_AVAILABLE, reason="CSRF protection modules not available")
class TestCSRFProtection:
    """Tests para la clase CSRFProtection."""
    
    def test_csrf_protection_initialization(self):
        """Test que valida la inicialización del sistema de protección CSRF."""
        secret_key = "test_secret_key"
        csrf_protection = CSRFProtection(secret_key)
        
        assert csrf_protection.token_generator is not None
        assert csrf_protection.active_tokens == {}
        assert csrf_protection.max_tokens_per_user == 10
    
    def test_generate_token_for_user(self):
        """Test que valida la generación de tokens para usuarios."""
        secret_key = "test_secret_key"
        csrf_protection = CSRFProtection(secret_key)
        
        user_id = "test_user"
        session_id = "test_session"
        
        token = csrf_protection.generate_token_for_user(user_id, session_id)
        
        assert token is not None
        assert len(token) > 20
        assert user_id in csrf_protection.active_tokens
        assert token in csrf_protection.active_tokens[user_id]
    
    def test_validate_token_for_user_valid(self):
        """Test que valida tokens válidos para usuarios."""
        secret_key = "test_secret_key"
        csrf_protection = CSRFProtection(secret_key)
        
        user_id = "test_user"
        session_id = "test_session"
        
        # Generar token
        token = csrf_protection.generate_token_for_user(user_id, session_id)
        
        # Validar token
        is_valid, message = csrf_protection.validate_token_for_user(token, user_id, session_id, consume=False)
        
        assert is_valid
        assert "válido" in message.lower()
    
    def test_validate_token_for_user_consume_once(self):
        """Test que valida que tokens de un solo uso sean consumidos."""
        secret_key = "test_secret_key"
        csrf_protection = CSRFProtection(secret_key)
        
        user_id = "test_user"
        token = csrf_protection.generate_token_for_user(user_id)
        
        # Primera validación debe ser exitosa
        is_valid1, message1 = csrf_protection.validate_token_for_user(token, user_id, consume=True)
        assert is_valid1
        
        # Segunda validación debe fallar (token ya usado)
        is_valid2, message2 = csrf_protection.validate_token_for_user(token, user_id, consume=True)
        assert not is_valid2
        assert "utilizado" in message2.lower()
    
    def test_validate_token_for_user_not_active(self):
        """Test que valida rechazo de tokens no activos."""
        secret_key = "test_secret_key"
        csrf_protection = CSRFProtection(secret_key)
        
        user_id = "test_user"
        # Crear token válido criptográficamente pero no registrado como activo
        token = csrf_protection.token_generator.generate_token(user_id)
        
        # No debe ser válido porque no está en tokens activos
        is_valid, message = csrf_protection.validate_token_for_user(token, user_id)
        assert not is_valid
        assert "activo" in message.lower()
    
    def test_invalidate_user_tokens(self):
        """Test que valida la invalidación de todos los tokens de un usuario."""
        secret_key = "test_secret_key"
        csrf_protection = CSRFProtection(secret_key)
        
        user_id = "test_user"
        
        # Generar múltiples tokens
        token1 = csrf_protection.generate_token_for_user(user_id)
        token2 = csrf_protection.generate_token_for_user(user_id)
        
        assert user_id in csrf_protection.active_tokens
        assert len(csrf_protection.active_tokens[user_id]) == 2
        
        # Invalidar tokens
        csrf_protection.invalidate_user_tokens(user_id)
        
        assert user_id not in csrf_protection.active_tokens
    
    def test_max_tokens_per_user_limit(self):
        """Test que valida el límite máximo de tokens por usuario."""
        secret_key = "test_secret_key"
        csrf_protection = CSRFProtection(secret_key)
        csrf_protection.max_tokens_per_user = 3  # Límite bajo para test
        
        user_id = "test_user"
        tokens = []
        
        # Generar más tokens que el límite
        for i in range(5):
            token = csrf_protection.generate_token_for_user(user_id)
            tokens.append(token)
        
        # Solo debe mantener los más recientes
        active_tokens = csrf_protection.active_tokens.get(user_id, {})
        assert len(active_tokens) <= csrf_protection.max_tokens_per_user
        
        # Los tokens más recientes deben estar activos
        assert tokens[-1] in active_tokens
    
    @patch('datetime.datetime')
    def test_cleanup_expired_tokens(self, mock_datetime):
        """Test que valida la limpieza de tokens expirados."""
        secret_key = "test_secret_key"
        csrf_protection = CSRFProtection(secret_key)
        
        user_id = "test_user"
        
        # Generar token en tiempo inicial
        initial_time = datetime(2025, 1, 1, 12, 0, 0)
        mock_datetime.now.return_value = initial_time
        
        token = csrf_protection.generate_token_for_user(user_id)
        assert user_id in csrf_protection.active_tokens
        
        # Avanzar tiempo más de 1 hora
        expired_time = initial_time + timedelta(hours=2)
        mock_datetime.now.return_value = expired_time
        
        # Ejecutar limpieza
        csrf_protection.cleanup_expired_tokens()
        
        # El usuario debe haberse limpiado
        assert user_id not in csrf_protection.active_tokens
    
    def test_get_stats(self):
        """Test que valida las estadísticas del sistema CSRF."""
        secret_key = "test_secret_key"
        csrf_protection = CSRFProtection(secret_key)
        
        # Estado inicial
        stats = csrf_protection.get_stats()
        assert stats['active_users'] == 0
        assert stats['total_tokens'] == 0
        
        # Añadir algunos tokens
        csrf_protection.generate_token_for_user("user1")
        csrf_protection.generate_token_for_user("user1")
        csrf_protection.generate_token_for_user("user2")
        
        stats = csrf_protection.get_stats()
        assert stats['active_users'] == 2
        assert stats['total_tokens'] == 3
        assert stats['avg_tokens_per_user'] == 1.5


@pytest.mark.skipif(not CSRF_AVAILABLE, reason="CSRF protection modules not available")
class TestCSRFProtectionGlobalFunctions:
    """Tests para las funciones globales del módulo CSRF."""
    
    def test_init_and_get_csrf_protection(self):
        """Test que valida la inicialización global del sistema CSRF."""
        secret_key = "test_global_secret"
        
        # Inicializar sistema
        init_csrf_protection(secret_key)
        
        # Obtener instancia
        csrf_protection = get_csrf_protection()
        
        assert csrf_protection is not None
        assert isinstance(csrf_protection, CSRFProtection)
    
    def test_generate_csrf_token_global(self):
        """Test que valida la función global de generación de tokens."""
        secret_key = "test_global_secret"
        init_csrf_protection(secret_key)
        
        user_id = "global_test_user"
        token = generate_csrf_token(user_id)
        
        assert token is not None
        assert len(token) > 20
    
    def test_validate_csrf_token_global(self):
        """Test que valida la función global de validación de tokens."""
        secret_key = "test_global_secret"
        init_csrf_protection(secret_key)
        
        user_id = "global_test_user"
        
        # Generar token
        token = generate_csrf_token(user_id)
        
        # Validar token
        is_valid = validate_csrf_token(token, user_id)
        assert is_valid
    
    def test_get_csrf_protection_not_initialized(self):
        """Test que valida error cuando no está inicializado."""
        # Resetear instancia global para test
        import rexus.security.csrf_protection as csrf_module
        original_protection = csrf_module.csrf_protection
        csrf_module.csrf_protection = None
        
        try:
            with pytest.raises(RuntimeError, match="no está inicializada"):
                get_csrf_protection()
        finally:
            # Restaurar estado original
            csrf_module.csrf_protection = original_protection


@pytest.mark.skipif(not CSRF_AVAILABLE, reason="CSRF protection modules not available")
class TestCSRFProtectionIntegration:
    """Tests de integración para el sistema CSRF."""
    
    def test_full_csrf_workflow(self):
        """Test que valida el workflow completo de CSRF protection."""
        secret_key = "integration_test_key"
        init_csrf_protection(secret_key)
        
        user_id = "integration_user"
        session_id = "integration_session"
        
        # 1. Generar token
        token = generate_csrf_token(user_id, session_id)
        assert token is not None
        
        # 2. Validar token (primera vez)
        csrf_protection = get_csrf_protection()
        is_valid1, msg1 = csrf_protection.validate_token_for_user(token, user_id, session_id, consume=False)
        assert is_valid1
        
        # 3. Usar token (consumir)
        is_valid2, msg2 = csrf_protection.validate_token_for_user(token, user_id, session_id, consume=True)
        assert is_valid2
        
        # 4. Intentar reusar token (debe fallar)
        is_valid3, msg3 = csrf_protection.validate_token_for_user(token, user_id, session_id, consume=True)
        assert not is_valid3
        
        # 5. Generar nuevo token
        new_token = generate_csrf_token(user_id, session_id)
        assert new_token != token
        
        # 6. Validar nuevo token
        is_valid4 = validate_csrf_token(new_token, user_id, session_id)
        assert is_valid4
    
    def test_multiple_users_isolation(self):
        """Test que valida el aislamiento entre múltiples usuarios."""
        secret_key = "multi_user_test_key"
        init_csrf_protection(secret_key)
        
        # Generar tokens para diferentes usuarios
        token_user1 = generate_csrf_token("user1", "session1")
        token_user2 = generate_csrf_token("user2", "session2")
        
        # Los tokens deben ser diferentes
        assert token_user1 != token_user2
        
        # Cada token solo debe ser válido para su usuario
        assert validate_csrf_token(token_user1, "user1", "session1")
        assert validate_csrf_token(token_user2, "user2", "session2")
        
        # Los tokens no deben ser válidos para otros usuarios
        assert not validate_csrf_token(token_user1, "user2", "session1")
        assert not validate_csrf_token(token_user2, "user1", "session2")
    
    @patch('rexus.utils.secure_logger.log_security_event')
    def test_security_logging_integration(self, mock_log):
        """Test que valida la integración con el sistema de logging de seguridad."""
        secret_key = "logging_test_key"
        init_csrf_protection(secret_key)
        
        user_id = "log_test_user"
        
        # Generar y usar token
        token = generate_csrf_token(user_id)
        
        # El logging debe haberse llamado
        mock_log.assert_called()
        
        # Verificar que se logueó el evento correcto
        calls = mock_log.call_args_list
        assert any("CSRF" in str(call) for call in calls)


# Fixtures para tests de CSRF
@pytest.fixture
def csrf_protection():
    """Fixture que proporciona instancia de CSRFProtection para tests."""
    secret_key = "test_fixture_key"
    return CSRFProtection(secret_key)


@pytest.fixture
def csrf_test_data():
    """Fixture con datos de prueba para tests CSRF."""
    return {
        'users': [
            {'id': 'user1', 'session': 'session1'},
            {'id': 'user2', 'session': 'session2'},
            {'id': 'admin', 'session': 'admin_session'}
        ],
        'secret_key': 'test_data_secret_key'
    }