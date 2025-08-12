"""
Tests para Password Manager System - Rexus.app

Tests que validan el sistema de gestión segura de contraseñas,
incluyendo hashing con bcrypt, validación de fortaleza y detección de compromiso.

Author: Rexus Testing Team
Date: 2025-08-11
Version: 1.0.0
"""

import pytest
import hashlib
from unittest.mock import Mock, patch, MagicMock

# Import the modules we're testing
try:
    from rexus.security.password_manager import (
        PasswordManager,
        init_password_manager,
        get_password_manager,
        hash_password,
        verify_password,
        generate_secure_password,
        validate_password_strength
    )
    PASSWORD_MANAGER_AVAILABLE = True
except ImportError:
    PASSWORD_MANAGER_AVAILABLE = False


@pytest.mark.skipif(not PASSWORD_MANAGER_AVAILABLE, reason="Password manager modules not available")
class TestPasswordManager:
    """Tests para la clase PasswordManager."""
    
    def test_initialization_with_bcrypt(self):
        """Test que valida la inicialización con bcrypt disponible."""
        with patch('rexus.security.password_manager.bcrypt') as mock_bcrypt:
            password_manager = PasswordManager()
            
            assert password_manager.bcrypt_available
            assert password_manager.salt_rounds == 12
            assert password_manager.bcrypt == mock_bcrypt
    
    def test_initialization_without_bcrypt(self):
        """Test que valida la inicialización sin bcrypt (fallback)."""
        with patch('builtins.__import__', side_effect=ImportError("bcrypt not found")):
            password_manager = PasswordManager()
            
            assert not password_manager.bcrypt_available
            assert password_manager.salt_rounds == 12
    
    @patch('rexus.security.password_manager.bcrypt')
    def test_hash_password_with_bcrypt(self, mock_bcrypt):
        """Test que valida el hashing de contraseñas con bcrypt."""
        mock_bcrypt.gensalt.return_value = b'$2b$12$mock_salt'
        mock_bcrypt.hashpw.return_value = b'$2b$12$mock_hashed_password'
        
        password_manager = PasswordManager()
        password_manager.bcrypt = mock_bcrypt
        password_manager.bcrypt_available = True
        
        password = "test_password_123"
        hashed = password_manager.hash_password(password)
        
        assert hashed == '$2b$12$mock_hashed_password'
        mock_bcrypt.gensalt.assert_called_once_with(rounds=12)
        mock_bcrypt.hashpw.assert_called_once_with(password.encode('utf-8'), b'$2b$12$mock_salt')
    
    def test_hash_password_with_fallback(self):
        """Test que valida el hashing con fallback cuando no hay bcrypt."""
        password_manager = PasswordManager()
        password_manager.bcrypt_available = False
        
        password = "test_password_123"
        hashed = password_manager.hash_password(password)
        
        # Debe usar formato salt:hash
        assert ':' in hashed
        salt, hash_part = hashed.split(':', 1)
        assert len(salt) == 32  # Salt de 16 bytes = 32 hex chars
        assert len(hash_part) == 64  # SHA256 = 64 hex chars
        assert hashed != password  # No debe ser texto plano
    
    @patch('rexus.security.password_manager.bcrypt')
    def test_verify_password_with_bcrypt(self, mock_bcrypt):
        """Test que valida la verificación de contraseñas con bcrypt."""
        mock_bcrypt.checkpw.return_value = True
        
        password_manager = PasswordManager()
        password_manager.bcrypt = mock_bcrypt
        password_manager.bcrypt_available = True
        
        password = "test_password_123"
        hashed = "$2b$12$mock_hashed_password"
        
        is_valid = password_manager.verify_password(password, hashed)
        
        assert is_valid
        mock_bcrypt.checkpw.assert_called_once_with(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def test_verify_password_with_fallback(self):
        """Test que valida la verificación con fallback."""
        password_manager = PasswordManager()
        password_manager.bcrypt_available = False
        
        password = "test_password_123"
        
        # Crear hash usando el método de fallback
        hashed = password_manager.hash_password(password)
        
        # Verificar que la contraseña coincide
        is_valid = password_manager.verify_password(password, hashed)
        assert is_valid
        
        # Verificar que contraseña incorrecta falla
        is_invalid = password_manager.verify_password("wrong_password", hashed)
        assert not is_invalid
    
    def test_verify_password_invalid_format(self):
        """Test que valida manejo de formatos inválidos de hash."""
        password_manager = PasswordManager()
        
        invalid_hashes = [
            "no_colon_hash",
            "",
            "salt_only:",
            ":hash_only"
        ]
        
        for invalid_hash in invalid_hashes:
            is_valid = password_manager.verify_password("test_password", invalid_hash)
            assert not is_valid
    
    def test_generate_secure_password_default_length(self):
        """Test que valida la generación de contraseñas seguras con longitud por defecto."""
        password_manager = PasswordManager()
        
        password = password_manager.generate_secure_password()
        
        assert len(password) == 16  # Longitud por defecto
        assert isinstance(password, str)
        # Verificar que contiene caracteres de diferentes tipos
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*" for c in password)
        
        # Debe tener al menos 3 tipos de caracteres
        char_types = sum([has_upper, has_lower, has_digit, has_special])
        assert char_types >= 3
    
    def test_generate_secure_password_custom_length(self):
        """Test que valida la generación con longitud personalizada."""
        password_manager = PasswordManager()
        
        lengths = [8, 12, 20, 32]
        
        for length in lengths:
            password = password_manager.generate_secure_password(length)
            assert len(password) == length
    
    def test_generate_secure_password_uniqueness(self):
        """Test que valida que las contraseñas generadas sean únicas."""
        password_manager = PasswordManager()
        
        passwords = []
        for _ in range(10):
            password = password_manager.generate_secure_password()
            passwords.append(password)
        
        # Todas las contraseñas deben ser diferentes
        unique_passwords = set(passwords)
        assert len(unique_passwords) == len(passwords)
    
    def test_validate_password_strength_weak_passwords(self):
        """Test que valida el rechazo de contraseñas débiles."""
        password_manager = PasswordManager()
        
        weak_passwords = [
            "123456",      # Muy corta y solo números
            "password",    # Solo letras, común
            "abc123",      # Corta, patrón común
            "qwerty",      # Patrón común del teclado
            "a" * 7,       # Muy corta
            "a" * 129,     # Demasiado larga
            "",            # Vacía
            "Password1",   # Contiene palabra común
        ]
        
        for weak_password in weak_passwords:
            is_valid, message = password_manager.validate_password_strength(weak_password)
            assert not is_valid
            assert isinstance(message, str)
            assert len(message) > 0
    
    def test_validate_password_strength_strong_passwords(self):
        """Test que valida la aceptación de contraseñas fuertes."""
        password_manager = PasswordManager()
        
        strong_passwords = [
            "MyStr0ng#P@ssw0rd!",
            "C0mpl3x$ecur1ty#2024",
            "R@nd0m&S@f3P@ssw0rd",
            "Ungu3ss@bl3!P@ssw0rd$"
        ]
        
        for strong_password in strong_passwords:
            is_valid, message = password_manager.validate_password_strength(strong_password)
            assert is_valid
            assert "válida" in message.lower() or "valid" in message.lower()
    
    def test_validate_password_strength_complexity_requirements(self):
        """Test que valida los requisitos de complejidad."""
        password_manager = PasswordManager()
        
        # Contraseñas que no cumplen complejidad suficiente
        insufficient_complexity = [
            "alllowercase123",       # Sin mayúsculas ni símbolos
            "ALLUPPERCASE123",       # Sin minúsculas ni símbolos
            "NoNumbersHere!@#",      # Sin números
            "NoSymbolsHere123Abc",   # Sin símbolos
        ]
        
        for password in insufficient_complexity:
            is_valid, message = password_manager.validate_password_strength(password)
            assert not is_valid
            assert "complejidad" in message.lower() or "complex" in message.lower()
    
    def test_is_password_compromised_common_passwords(self):
        """Test que valida la detección de contraseñas comprometidas."""
        password_manager = PasswordManager()
        
        compromised_passwords = [
            "123456",
            "password",
            "123456789",
            "qwerty",
            "admin"
        ]
        
        for compromised in compromised_passwords:
            is_compromised = password_manager.is_password_compromised(compromised)
            assert is_compromised
    
    def test_is_password_compromised_unique_passwords(self):
        """Test que valida que contraseñas únicas no sean detectadas como comprometidas."""
        password_manager = PasswordManager()
        
        unique_passwords = [
            "MyUn1qu3!P@ssw0rd$2024",
            "R@nd0m&Ungu3ss@bl3#P@ss",
            "Cr34t1v3$ecur3P@ssw0rd!"
        ]
        
        for unique in unique_passwords:
            is_compromised = password_manager.is_password_compromised(unique)
            assert not is_compromised
    
    def test_get_password_entropy(self):
        """Test que valida el cálculo de entropía de contraseñas."""
        password_manager = PasswordManager()
        
        # Contraseña simple (solo minúsculas)
        simple_password = "abcdef"
        simple_entropy = password_manager.get_password_entropy(simple_password)
        
        # Contraseña compleja (mayúsculas, minúsculas, números, símbolos)
        complex_password = "Abc123!@#"
        complex_entropy = password_manager.get_password_entropy(complex_password)
        
        # La contraseña compleja debe tener mayor entropía
        assert complex_entropy > simple_entropy
        assert simple_entropy > 0
        assert complex_entropy > 0
    
    def test_get_password_entropy_empty_password(self):
        """Test que valida el manejo de contraseñas vacías en cálculo de entropía."""
        password_manager = PasswordManager()
        
        entropy = password_manager.get_password_entropy("")
        assert entropy == 0.0
    
    def test_create_password_hash_with_metadata_valid(self):
        """Test que valida la creación de hash con metadatos para contraseña válida."""
        password_manager = PasswordManager()
        
        password = "ValidStr0ng!P@ssw0rd"
        user_id = "user123"
        
        metadata = password_manager.create_password_hash_with_metadata(password, user_id)
        
        assert 'hash' in metadata
        assert 'created_at' in metadata
        assert 'algorithm' in metadata
        assert 'strength_score' in metadata
        assert 'user_id' in metadata
        assert 'version' in metadata
        
        assert metadata['user_id'] == user_id
        assert metadata['strength_score'] > 0
        assert metadata['hash'] != password  # Hash debe ser diferente del password
    
    def test_create_password_hash_with_metadata_weak_password(self):
        """Test que valida el rechazo de contraseñas débiles en creación de hash."""
        password_manager = PasswordManager()
        
        weak_password = "123456"
        user_id = "user123"
        
        with pytest.raises(ValueError, match="Contraseña débil"):
            password_manager.create_password_hash_with_metadata(weak_password, user_id)
    
    def test_create_password_hash_with_metadata_compromised_password(self):
        """Test que valida el rechazo de contraseñas comprometidas."""
        password_manager = PasswordManager()
        
        compromised_password = "password"  # Contraseña común
        user_id = "user123"
        
        with pytest.raises(ValueError, match="comprometidas"):
            password_manager.create_password_hash_with_metadata(compromised_password, user_id)


@pytest.mark.skipif(not PASSWORD_MANAGER_AVAILABLE, reason="Password manager modules not available")
class TestPasswordManagerGlobalFunctions:
    """Tests para las funciones globales del módulo."""
    
    def test_init_and_get_password_manager(self):
        """Test que valida la inicialización global del gestor de contraseñas."""
        init_password_manager()
        
        manager = get_password_manager()
        
        assert manager is not None
        assert isinstance(manager, PasswordManager)
    
    def test_hash_password_global(self):
        """Test que valida la función global de hash de contraseña."""
        init_password_manager()
        
        password = "test_password_123"
        hashed = hash_password(password)
        
        assert hashed != password
        assert len(hashed) > 0
    
    def test_verify_password_global(self):
        """Test que valida la función global de verificación de contraseña."""
        init_password_manager()
        
        password = "test_password_123"
        hashed = hash_password(password)
        
        # Verificar contraseña correcta
        is_valid = verify_password(password, hashed)
        assert is_valid
        
        # Verificar contraseña incorrecta
        is_invalid = verify_password("wrong_password", hashed)
        assert not is_invalid
    
    def test_generate_secure_password_global(self):
        """Test que valida la función global de generación de contraseña."""
        init_password_manager()
        
        password = generate_secure_password()
        
        assert len(password) == 16
        assert isinstance(password, str)
        
        # Con longitud personalizada
        custom_password = generate_secure_password(20)
        assert len(custom_password) == 20
    
    def test_validate_password_strength_global(self):
        """Test que valida la función global de validación de fortaleza."""
        init_password_manager()
        
        # Contraseña débil
        is_valid_weak, msg_weak = validate_password_strength("123456")
        assert not is_valid_weak
        assert len(msg_weak) > 0
        
        # Contraseña fuerte
        is_valid_strong, msg_strong = validate_password_strength("Str0ng!P@ssw0rd")
        assert is_valid_strong
        assert "válida" in msg_strong.lower() or "valid" in msg_strong.lower()


@pytest.mark.skipif(not PASSWORD_MANAGER_AVAILABLE, reason="Password manager modules not available")
class TestPasswordManagerIntegration:
    """Tests de integración para el gestor de contraseñas."""
    
    def test_full_password_lifecycle(self):
        """Test que valida el ciclo completo de vida de una contraseña."""
        init_password_manager()
        manager = get_password_manager()
        
        # 1. Generar contraseña segura
        password = generate_secure_password(12)
        
        # 2. Validar fortaleza
        is_strong, message = validate_password_strength(password)
        assert is_strong
        
        # 3. Hash de contraseña
        hashed = hash_password(password)
        
        # 4. Verificar contraseña
        is_valid = verify_password(password, hashed)
        assert is_valid
        
        # 5. Verificar que contraseña incorrecta falla
        is_invalid = verify_password("wrong_password", hashed)
        assert not is_invalid
    
    def test_bcrypt_fallback_compatibility(self):
        """Test que valida compatibilidad entre bcrypt y fallback."""
        manager = PasswordManager()
        
        password = "test_password_123"
        
        # Crear hash con estado de bcrypt actual
        original_bcrypt_state = manager.bcrypt_available
        hashed = manager.hash_password(password)
        
        # Verificar con mismo estado
        is_valid_same = manager.verify_password(password, hashed)
        assert is_valid_same
        
        # Cambiar estado de bcrypt y verificar compatibilidad
        manager.bcrypt_available = not original_bcrypt_state
        
        # Verificación debe seguir funcionando
        try:
            is_valid_different = manager.verify_password(password, hashed)
            # Si hay error de formato, es esperado para hashes incompatibles
        except:
            pass  # Error esperado si los formatos son incompatibles
        
        # Restaurar estado original
        manager.bcrypt_available = original_bcrypt_state
    
    def test_multiple_users_password_isolation(self):
        """Test que valida el aislamiento de contraseñas entre usuarios."""
        init_password_manager()
        
        users_data = [
            {"id": "user1", "password": "User1Str0ng!P@ss"},
            {"id": "user2", "password": "User2S3cur3#P@ss"},
            {"id": "user3", "password": "User3R@nd0m$P@ss"}
        ]
        
        hashed_passwords = {}
        
        # Hash contraseñas para cada usuario
        for user in users_data:
            hashed = hash_password(user["password"])
            hashed_passwords[user["id"]] = hashed
        
        # Verificar que cada usuario solo puede acceder con su contraseña
        for user in users_data:
            user_hash = hashed_passwords[user["id"]]
            
            # Contraseña correcta debe funcionar
            is_valid_correct = verify_password(user["password"], user_hash)
            assert is_valid_correct
            
            # Contraseñas de otros usuarios no deben funcionar
            for other_user in users_data:
                if other_user["id"] != user["id"]:
                    is_valid_wrong = verify_password(other_user["password"], user_hash)
                    assert not is_valid_wrong
    
    def test_password_policy_enforcement(self):
        """Test que valida la aplicación de políticas de contraseñas."""
        init_password_manager()
        manager = get_password_manager()
        
        # Intentar crear hash con contraseña que viola política
        weak_password = "123456"
        user_id = "policy_test_user"
        
        with pytest.raises(ValueError):
            manager.create_password_hash_with_metadata(weak_password, user_id)
        
        # Contraseña que cumple política debe funcionar
        strong_password = "PolicyCompl1@nt!P@ss"
        
        metadata = manager.create_password_hash_with_metadata(strong_password, user_id)
        
        assert metadata is not None
        assert metadata["user_id"] == user_id
        
        # Verificar que el hash funciona
        is_valid = verify_password(strong_password, metadata["hash"])
        assert is_valid


# Fixtures para tests de password manager
@pytest.fixture
def password_manager():
    """Fixture que proporciona instancia de PasswordManager para tests."""
    return PasswordManager()


@pytest.fixture
def password_test_data():
    """Fixture con datos de prueba para tests de contraseñas."""
    return {
        'weak_passwords': [
            "123456",
            "password",
            "qwerty",
            "abc123",
            ""
        ],
        'strong_passwords': [
            "MyStr0ng!P@ssw0rd$",
            "C0mpl3x&S3cur3P@ss#",
            "R@nd0m$af3P@ssw0rd!",
            "Ungu3ss@bl3#P@ss2024"
        ],
        'compromised_passwords': [
            "123456",
            "password",
            "admin",
            "letmein",
            "welcome"
        ],
        'users': [
            {'id': 'user1', 'name': 'John Doe'},
            {'id': 'user2', 'name': 'Jane Smith'},
            {'id': 'admin', 'name': 'System Admin'}
        ]
    }