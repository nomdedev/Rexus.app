"""
Tests for AuthenticationManager - Sistema de autenticación refactorizado
Tests de seguridad, validación de contraseñas, y manejo de intentos fallidos
"""

import pytest
import datetime
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

# Agregar el directorio raíz al path
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

try:
    from rexus.modules.usuarios.submodules.auth_manager import AuthenticationManager
    from tests.obras.mock_auth_context import MockDatabaseContext
except ImportError as e:
    print(f"Error importando módulos: {e}")
    AuthenticationManager = None


class TestAuthenticationManager:
    """Suite de tests para AuthenticationManager."""
    
    def setup_method(self):
        """Configuración para cada test."""
        self.mock_db = MockDatabaseContext()
        self.auth_manager = AuthenticationManager(self.mock_db.connection) if AuthenticationManager else None
    
    @pytest.mark.skipif(AuthenticationManager is None, reason="AuthenticationManager no disponible")
    def test_autenticar_usuario_exitoso(self):
        """Test de autenticación exitosa."""
        # Preparar datos de prueba
        username = "test_user"
        password = "TestPass123!"
        
        # Mock de usuario existente
        user_data = {
            'id': 1,
            'username': username,
            'password': '$2b$12$test_hash',
            'nombre_completo': 'Usuario Test',
            'rol': 'operator',
            'activo': True
        }
        
        # Mock del cursor y sus métodos
        mock_cursor = Mock()
        mock_cursor.fetchone.side_effect = [
            (0,),  # Intentos fallidos
            (user_data['id'], user_data['username'], user_data['password'], 
             user_data['nombre_completo'], 'test@example.com', 'operator', True,
             datetime.datetime.now(), datetime.datetime.now())
        ]
        
        self.mock_db.connection.cursor.return_value = mock_cursor
        
        # Mock de bcrypt verification
        with patch('bcrypt.checkpw', return_value=True):
            resultado = self.auth_manager.autenticar_usuario_seguro(username, password)
        
        # Verificaciones
        assert resultado['success'] is True
        assert resultado['user_data']['username'] == username
        assert 'password' not in resultado['user_data']
        assert resultado['message'] == 'Autenticación exitosa'
    
    @pytest.mark.skipif(AuthenticationManager is None, reason="AuthenticationManager no disponible")
    def test_autenticar_usuario_password_incorrecta(self):
        """Test de autenticación con contraseña incorrecta."""
        username = "test_user"
        password = "WrongPassword"
        
        user_data = {
            'id': 1,
            'username': username,
            'password': '$2b$12$test_hash',
            'activo': True
        }
        
        mock_cursor = Mock()
        mock_cursor.fetchone.side_effect = [
            (0,),  # Intentos fallidos
            (user_data['id'], user_data['username'], user_data['password'],
             'Usuario Test', 'test@example.com', 'operator', True,
             datetime.datetime.now(), datetime.datetime.now())
        ]
        
        self.mock_db.connection.cursor.return_value = mock_cursor
        
        # Mock de bcrypt verification fallida
        with patch('bcrypt.checkpw', return_value=False):
            resultado = self.auth_manager.autenticar_usuario_seguro(username, password)
        
        # Verificaciones
        assert resultado['success'] is False
        assert resultado['user_data'] is None
        assert 'Credenciales inválidas' in resultado['message']
    
    @pytest.mark.skipif(AuthenticationManager is None, reason="AuthenticationManager no disponible")
    def test_usuario_inexistente(self):
        """Test de autenticación con usuario inexistente."""
        username = "nonexistent_user"
        password = "TestPass123!"
        
        mock_cursor = Mock()
        mock_cursor.fetchone.side_effect = [
            (0,),  # Intentos fallidos
            None   # Usuario no encontrado
        ]
        
        self.mock_db.connection.cursor.return_value = mock_cursor
        
        resultado = self.auth_manager.autenticar_usuario_seguro(username, password)
        
        # Verificaciones
        assert resultado['success'] is False
        assert resultado['user_data'] is None
        assert resultado['message'] == 'Credenciales inválidas'
    
    @pytest.mark.skipif(AuthenticationManager is None, reason="AuthenticationManager no disponible")
    def test_cuenta_bloqueada(self):
        """Test de cuenta bloqueada por intentos fallidos."""
        username = "blocked_user"
        password = "TestPass123!"
        
        # Mock de intentos fallidos excesivos
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = (3,)  # 3 intentos fallidos (máximo)
        
        self.mock_db.connection.cursor.return_value = mock_cursor
        
        resultado = self.auth_manager.autenticar_usuario_seguro(username, password)
        
        # Verificaciones
        assert resultado['success'] is False
        assert resultado['bloqueado'] is True
        assert 'bloqueada' in resultado['message'].lower()
    
    @pytest.mark.skipif(AuthenticationManager is None, reason="AuthenticationManager no disponible")
    def test_validar_fortaleza_password_valida(self):
        """Test de validación de contraseña fuerte."""
        password_fuerte = "MyStr0ng!Pass2024"
        
        resultado = self.auth_manager.validar_fortaleza_password(password_fuerte)
        
        # Verificaciones
        assert resultado['es_valida'] is True
        assert len(resultado['errores']) == 0
        assert resultado['puntuacion'] > 80
    
    @pytest.mark.skipif(AuthenticationManager is None, reason="AuthenticationManager no disponible")
    def test_validar_fortaleza_password_debil(self):
        """Test de validación de contraseña débil."""
        password_debil = "123456"
        
        resultado = self.auth_manager.validar_fortaleza_password(password_debil)
        
        # Verificaciones
        assert resultado['es_valida'] is False
        assert len(resultado['errores']) > 0
        assert resultado['puntuacion'] < 50
        
        # Verificar errores específicos
        errores_texto = ' '.join(resultado['errores'])
        assert 'mayúscula' in errores_texto
        assert 'minúscula' in errores_texto
        assert 'carácter especial' in errores_texto
    
    @pytest.mark.skipif(AuthenticationManager is None, reason="AuthenticationManager no disponible")
    def test_validar_fortaleza_password_comun(self):
        """Test de validación de contraseña común."""
        password_comun = "password"
        
        resultado = self.auth_manager.validar_fortaleza_password(password_comun)
        
        # Verificaciones
        assert resultado['es_valida'] is False
        errores_texto = ' '.join(resultado['errores'])
        assert 'común' in errores_texto
    
    @pytest.mark.skipif(AuthenticationManager is None, reason="AuthenticationManager no disponible")
    def test_cambiar_password_exitoso(self):
        """Test de cambio de contraseña exitoso."""
        usuario_id = 1
        password_actual = "OldPass123!"
        password_nueva = "NewStr0ng!Pass2024"
        
        # Mock del cursor
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = ("test_user", "$2b$12$old_hash")
        mock_cursor.rowcount = 1
        
        self.mock_db.connection.cursor.return_value = mock_cursor
        
        # Mock de verificación de contraseña actual
        with patch.object(self.auth_manager, '_verificar_password_segura', return_value=True):
            with patch.object(self.auth_manager, '_hashear_password_segura', return_value="$2b$12$new_hash"):
                resultado = self.auth_manager.cambiar_password_segura(usuario_id, password_actual, password_nueva)
        
        # Verificaciones
        assert resultado['success'] is True
        assert 'exitosamente' in resultado['message']
    
    @pytest.mark.skipif(AuthenticationManager is None, reason="AuthenticationManager no disponible")
    def test_cambiar_password_actual_incorrecta(self):
        """Test de cambio de contraseña con contraseña actual incorrecta."""
        usuario_id = 1
        password_actual = "WrongPass"
        password_nueva = "NewStr0ng!Pass2024"
        
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = ("test_user", "$2b$12$hash")
        self.mock_db.connection.cursor.return_value = mock_cursor
        
        # Mock de verificación fallida
        with patch.object(self.auth_manager, '_verificar_password_segura', return_value=False):
            resultado = self.auth_manager.cambiar_password_segura(usuario_id, password_actual, password_nueva)
        
        # Verificaciones
        assert resultado['success'] is False
        assert 'incorrecta' in resultado['message']
    
    @pytest.mark.skipif(AuthenticationManager is None, reason="AuthenticationManager no disponible")
    def test_cambiar_password_nueva_debil(self):
        """Test de cambio de contraseña con nueva contraseña débil."""
        usuario_id = 1
        password_actual = "OldPass123!"
        password_nueva = "weak"  # Contraseña demasiado débil
        
        resultado = self.auth_manager.cambiar_password_segura(usuario_id, password_actual, password_nueva)
        
        # Verificaciones
        assert resultado['success'] is False
        assert 'requisitos' in resultado['message']
    
    @pytest.mark.skipif(AuthenticationManager is None, reason="AuthenticationManager no disponible")
    def test_registrar_intento_login(self):
        """Test de registro de intentos de login."""
        username = "test_user"
        
        mock_cursor = Mock()
        self.mock_db.connection.cursor.return_value = mock_cursor
        
        # Test de intento exitoso
        self.auth_manager.registrar_intento_login(username, exitoso=True)
        
        # Verificar que se llamó execute con los parámetros correctos
        mock_cursor.execute.assert_called()
        args = mock_cursor.execute.call_args[0]
        assert username in args[1]
        assert True in args[1]  # exitoso = True
    
    @pytest.mark.skipif(AuthenticationManager is None, reason="AuthenticationManager no disponible")
    def test_verificar_cuenta_bloqueada_no_bloqueada(self):
        """Test de verificación de cuenta no bloqueada."""
        username = "test_user"
        
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = (2,)  # 2 intentos fallidos (menos del máximo)
        self.mock_db.connection.cursor.return_value = mock_cursor
        
        resultado = self.auth_manager.verificar_cuenta_bloqueada(username)
        
        # Verificaciones
        assert resultado is False
    
    @pytest.mark.skipif(AuthenticationManager is None, reason="AuthenticationManager no disponible")
    def test_verificar_cuenta_bloqueada_si_bloqueada(self):
        """Test de verificación de cuenta bloqueada."""
        username = "blocked_user"
        
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = (3,)  # 3 intentos fallidos (máximo alcanzado)
        self.mock_db.connection.cursor.return_value = mock_cursor
        
        resultado = self.auth_manager.verificar_cuenta_bloqueada(username)
        
        # Verificaciones
        assert resultado is True
    
    @pytest.mark.skipif(AuthenticationManager is None, reason="AuthenticationManager no disponible")
    def test_reset_intentos_login(self):
        """Test de reset de intentos fallidos."""
        username = "test_user"
        
        mock_cursor = Mock()
        self.mock_db.connection.cursor.return_value = mock_cursor
        
        resultado = self.auth_manager.reset_intentos_login(username)
        
        # Verificaciones
        assert resultado is True
        mock_cursor.execute.assert_called()
        self.mock_db.connection.commit.assert_called()


if __name__ == "__main__":
    # Ejecutar tests específicos
    test_suite = TestAuthenticationManager()
    test_suite.setup_method()
    
    if AuthenticationManager:
        print("=== EJECUTANDO TESTS DE AUTHENTICATION MANAGER ===")
        
        try:
            test_suite.test_validar_fortaleza_password_valida()
            print("[CHECK] Test contraseña válida - PASADO")
        except Exception as e:
            print(f"[ERROR] Test contraseña válida - FALLIDO: {e}")
        
        try:
            test_suite.test_validar_fortaleza_password_debil()
            print("[CHECK] Test contraseña débil - PASADO")
        except Exception as e:
            print(f"[ERROR] Test contraseña débil - FALLIDO: {e}")
        
        try:
            test_suite.test_validar_fortaleza_password_comun()
            print("[CHECK] Test contraseña común - PASADO")
        except Exception as e:
            print(f"[ERROR] Test contraseña común - FALLIDO: {e}")
        
        print("=== TESTS DE AUTHENTICATION MANAGER COMPLETADOS ===")
    else:
        print("[ERROR] AuthenticationManager no disponible para testing")