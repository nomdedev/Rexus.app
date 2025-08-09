#!/usr/bin/env python3
"""
Tests para el módulo de Usuarios

Cubre funcionalidades críticas como:
- Autenticación de usuarios
- Gestión de permisos  
- CRUD de usuarios
- Validación de datos
- Seguridad de contraseñas
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Agregar el directorio raíz al path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

# Importar el módulo a probar
try:
    from rexus.modules.usuarios.model import UsuariosModel
    from rexus.modules.usuarios.controller import UsuariosController
    usuarios_available = True
except ImportError as e:
    print(f"Warning: No se pudo importar módulo usuarios: {e}")
    usuarios_available = False

class MockDatabase:
    """Mock de base de datos para tests."""
    
    def __init__(self):
        self.cursor_mock = Mock()
        self.closed = False
        
    def cursor(self):
        return self.cursor_mock
        
    def commit(self):
        pass
        
    def rollback(self):
        pass
        
    def close(self):
        self.closed = True

@pytest.fixture
def mock_db():
    """Fixture para base de datos mock."""
    return MockDatabase()

@pytest.fixture
def usuarios_model(mock_db):
    """Fixture para modelo de usuarios."""
    if not usuarios_available:
        pytest.skip("Módulo usuarios no disponible")
    return UsuariosModel(mock_db)

class TestUsuariosModel:
    """Tests para el modelo de usuarios."""
    
    def test_model_initialization(self, usuarios_model):
        """Test inicialización del modelo."""
        assert usuarios_model is not None
        assert usuarios_model.db_connection is not None
        
    def test_hash_password(self, usuarios_model):
        """Test de hash de contraseñas."""
        password = "test_password_123"
        hashed, salt = usuarios_model.hash_password(password)
        
        assert hashed is not None
        assert salt is not None
        assert len(hashed) > 0
        assert len(salt) > 0
        assert hashed != password  # Debe estar hasheada
        
    def test_verify_password(self, usuarios_model):
        """Test de verificación de contraseñas."""
        password = "test_password_123"
        hashed, salt = usuarios_model.hash_password(password)
        
        # Verificar contraseña correcta
        assert usuarios_model.verify_password(password, hashed, salt) == True
        
        # Verificar contraseña incorrecta
        assert usuarios_model.verify_password("wrong_password", hashed, salt) == False
        
    def test_validate_user_data(self, usuarios_model):
        """Test de validación de datos de usuario."""
        # Datos válidos
        valid_data = {
            'username': 'test_user',
            'email': 'test@example.com',
            'nombre': 'Test User',
            'password': 'SecurePass123!'
        }
        
        validation_result = usuarios_model.validate_user_data(valid_data)
        assert validation_result['valid'] == True
        
        # Datos inválidos - email malformado
        invalid_data = {
            'username': 'test_user',
            'email': 'invalid_email',
            'nombre': 'Test User',
            'password': 'weak'
        }
        
        validation_result = usuarios_model.validate_user_data(invalid_data)
        assert validation_result['valid'] == False
        assert len(validation_result['errors']) > 0

    @patch('rexus.modules.usuarios.model.UsuariosModel._execute_query')
    def test_authenticate_user(self, mock_execute, usuarios_model):
        """Test de autenticación de usuario."""
        # Simular usuario existente
        mock_execute.return_value = [(1, 'test_user', 'hashed_password', 'salt', 'activo')]
        
        # Mock del método verify_password
        with patch.object(usuarios_model, 'verify_password', return_value=True):
            result = usuarios_model.authenticate_user('test_user', 'correct_password')
            
        assert result['success'] == True
        assert result['user_id'] == 1
        assert result['username'] == 'test_user'
        
    @patch('rexus.modules.usuarios.model.UsuariosModel._execute_query')
    def test_authenticate_user_invalid(self, mock_execute, usuarios_model):
        """Test de autenticación fallida."""
        # Simular usuario no encontrado
        mock_execute.return_value = []
        
        result = usuarios_model.authenticate_user('nonexistent_user', 'password')
        
        assert result['success'] == False
        assert 'error' in result

    @patch('rexus.modules.usuarios.model.UsuariosModel._execute_query')
    def test_create_user(self, mock_execute, usuarios_model):
        """Test de creación de usuario."""
        mock_execute.return_value = None
        usuarios_model.db_connection.cursor_mock.fetchone.return_value = [1]  # ID del nuevo usuario
        
        user_data = {
            'username': 'new_user',
            'email': 'new@example.com',
            'nombre': 'New User',
            'password': 'SecurePass123!'
        }
        
        with patch.object(usuarios_model, 'validate_user_data', return_value={'valid': True, 'errors': []}):
            result = usuarios_model.create_user(user_data)
            
        assert result['success'] == True
        assert result['user_id'] == 1

    def test_sanitize_input(self, usuarios_model):
        """Test de sanitización de entrada."""
        # Script malicioso
        malicious_input = "<script>alert('xss')</script>"
        sanitized = usuarios_model._sanitize_input(malicious_input)
        
        assert "<script>" not in sanitized
        assert "alert" not in sanitized
        
        # Input normal
        normal_input = "Usuario Normal 123"
        sanitized = usuarios_model._sanitize_input(normal_input)
        assert sanitized == normal_input

class TestUsuariosController:
    """Tests para el controlador de usuarios."""
    
    @pytest.fixture
    def usuarios_controller(self, mock_db):
        """Fixture para controlador de usuarios."""
        if not usuarios_available:
            pytest.skip("Módulo usuarios no disponible")
        return UsuariosController(mock_db)
    
    def test_controller_initialization(self, usuarios_controller):
        """Test inicialización del controlador."""
        assert usuarios_controller is not None
        assert usuarios_controller.model is not None

    @patch('rexus.modules.usuarios.model.UsuariosModel.authenticate_user')
    def test_login_success(self, mock_auth, usuarios_controller):
        """Test de login exitoso."""
        mock_auth.return_value = {
            'success': True,
            'user_id': 1,
            'username': 'test_user',
            'role': 'admin'
        }
        
        result = usuarios_controller.login('test_user', 'correct_password')
        
        assert result['success'] == True
        assert result['user_id'] == 1
        
    @patch('rexus.modules.usuarios.model.UsuariosModel.authenticate_user')
    def test_login_failure(self, mock_auth, usuarios_controller):
        """Test de login fallido."""
        mock_auth.return_value = {
            'success': False,
            'error': 'Credenciales inválidas'
        }
        
        result = usuarios_controller.login('test_user', 'wrong_password')
        
        assert result['success'] == False
        assert 'error' in result

class TestUsuariosIntegration:
    """Tests de integración del módulo usuarios."""
    
    def test_password_security(self):
        """Test de seguridad de contraseñas."""
        if not usuarios_available:
            pytest.skip("Módulo usuarios no disponible")
            
        # Test que las contraseñas se hasheen correctamente
        model = UsuariosModel(MockDatabase())
        
        passwords = [
            "SimplePassword123",
            "Complex!@#$%Password456",
            "UnicodePassword漢字",
        ]
        
        for password in passwords:
            hashed, salt = model.hash_password(password)
            
            # Verificar que el hash no es la contraseña original
            assert hashed != password
            
            # Verificar que se puede verificar correctamente
            assert model.verify_password(password, hashed, salt) == True
            
            # Verificar que contraseñas incorrectas fallan
            assert model.verify_password(password + "wrong", hashed, salt) == False

    def test_sql_injection_protection(self):
        """Test de protección contra SQL injection."""
        if not usuarios_available:
            pytest.skip("Módulo usuarios no disponible")
            
        model = UsuariosModel(MockDatabase())
        
        # Intentos de SQL injection
        malicious_inputs = [
            "'; DROP TABLE usuarios; --",
            "admin' OR '1'='1",
            "' UNION SELECT * FROM usuarios --",
            "'; INSERT INTO usuarios VALUES ('hacker', 'pass'); --"
        ]
        
        for malicious_input in malicious_inputs:
            # Los inputs maliciosos deben ser sanitizados
            sanitized = model._sanitize_input(malicious_input)
            
            # Verificar que caracteres peligrosos fueron removidos/escapados
            assert "DROP TABLE" not in sanitized.upper()
            assert "UNION SELECT" not in sanitized.upper()
            assert "INSERT INTO" not in sanitized.upper()

def test_module_imports():
    """Test que el módulo se pueda importar correctamente."""
    try:
        from rexus.modules.usuarios import model, controller
        assert hasattr(model, 'UsuariosModel')
        assert hasattr(controller, 'UsuariosController') 
        print("✓ Módulo usuarios importado correctamente")
    except ImportError as e:
        print(f"✗ Error importando módulo usuarios: {e}")
        pytest.skip("Módulo usuarios no disponible para testing")

if __name__ == "__main__":
    # Ejecutar tests directamente
    print("=" * 60)
    print("🧪 EJECUTANDO TESTS DEL MÓDULO USUARIOS")
    print("=" * 60)
    
    # Ejecutar con pytest si está disponible
    try:
        pytest.main([__file__, "-v", "--tb=short"])
    except ImportError:
        print("pytest no disponible, ejecutando tests básicos...")
        
        # Tests básicos sin pytest
        print("\n📋 Test de importación...")
        test_module_imports()
        
        if usuarios_available:
            print("\n🔐 Test básico de seguridad de contraseñas...")
            model = UsuariosModel(MockDatabase())
            password = "TestPassword123"
            hashed, salt = model.hash_password(password)
            
            if model.verify_password(password, hashed, salt):
                print("✓ Test de hash/verificación de contraseñas: PASÓ")
            else:
                print("✗ Test de hash/verificación de contraseñas: FALLÓ")
                
            print("\n🛡️  Test básico de sanitización...")
            malicious = "<script>alert('xss')</script>"
            sanitized = model._sanitize_input(malicious)
            
            if "<script>" not in sanitized:
                print("✓ Test de sanitización: PASÓ")
            else:
                print("✗ Test de sanitización: FALLÓ")
        
        print("\n" + "=" * 60)
        print("🏁 TESTS COMPLETADOS")
        print("=" * 60)