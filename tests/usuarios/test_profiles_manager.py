"""
Tests for ProfilesManager - Sistema de gestión de perfiles refactorizado
Tests de CRUD de usuarios, validaciones y gestión de datos de perfil
"""

import pytest
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# Agregar el directorio raíz al path
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

try:
    from rexus.modules.usuarios.submodules.profiles_manager import ProfilesManager
    from tests.obras.mock_auth_context import MockDatabaseContext
except ImportError as e:
    print(f"Error importando módulos: {e}")
    ProfilesManager = None


class TestProfilesManager:
    """Suite de tests para ProfilesManager."""
    
    def setup_method(self):
        """Configuración para cada test."""
        self.mock_db = MockDatabaseContext()
        self.profiles_manager = ProfilesManager(self.mock_db.connection) if ProfilesManager else None
    
    @pytest.mark.skipif(ProfilesManager is None, reason="ProfilesManager no disponible")
    def test_crear_usuario_exitoso(self):
        """Test crear usuario exitosamente."""
        datos_usuario = {
            'username': 'nuevo_usuario',
            'password_hash': '$2b$12$hashedpassword',
            'nombre_completo': 'Usuario Nuevo',
            'email': 'nuevo@example.com',
            'telefono': '123456789',
            'rol': 'operator'
        }
        
        # Mock del cursor
        mock_cursor = Mock()
        mock_cursor.fetchone.side_effect = [
            (0,),  # Username no existe
            (0,),  # Email no existe
            (5,)   # ID del usuario creado
        ]
        
        self.mock_db.connection.cursor.return_value = mock_cursor
        
        # Mock de validaciones exitosas
        with patch.object(self.profiles_manager, '_validar_datos_usuario', 
                         return_value={'valid': True, 'message': 'Datos válidos'}):
            with patch.object(self.profiles_manager, '_verificar_unicidad_usuario', return_value=True):
                with patch.object(self.profiles_manager, '_sanitizar_datos_usuario', return_value=datos_usuario):
                    resultado = self.profiles_manager.crear_usuario(datos_usuario)
        
        # Verificaciones
        assert resultado['success'] is True
        assert 'exitosamente' in resultado['message']
        assert 'usuario_id' in resultado
        assert resultado['usuario_id'] == 5
        
        # Verificar que se ejecutó el INSERT
        mock_cursor.execute.assert_called()
        self.mock_db.connection.commit.assert_called()
    
    @pytest.mark.skipif(ProfilesManager is None, reason="ProfilesManager no disponible")
    def test_crear_usuario_datos_invalidos(self):
        """Test crear usuario con datos inválidos."""
        datos_usuario = {
            'username': '',  # Username vacío
            'password_hash': 'hash',
            'nombre_completo': 'Usuario Test'
        }
        
        resultado = self.profiles_manager.crear_usuario(datos_usuario)
        
        # Verificaciones
        assert resultado['success'] is False
        assert 'Username es requerido' in resultado['message']
    
    @pytest.mark.skipif(ProfilesManager is None, reason="ProfilesManager no disponible")
    def test_crear_usuario_duplicado(self):
        """Test crear usuario que ya existe."""
        datos_usuario = {
            'username': 'usuario_existente',
            'password_hash': '$2b$12$hash',
            'nombre_completo': 'Usuario Duplicado',
            'email': 'existente@example.com'
        }
        
        # Mock validaciones exitosas pero usuario duplicado
        with patch.object(self.profiles_manager, '_validar_datos_usuario', 
                         return_value={'valid': True, 'message': 'Datos válidos'}):
            with patch.object(self.profiles_manager, '_verificar_unicidad_usuario', return_value=False):
                resultado = self.profiles_manager.crear_usuario(datos_usuario)
        
        # Verificaciones
        assert resultado['success'] is False
        assert 'ya existe' in resultado['message']
    
    @pytest.mark.skipif(ProfilesManager is None, reason="ProfilesManager no disponible")
    def test_obtener_usuario_por_id_existente(self):
        """Test obtener usuario existente por ID."""
        usuario_id = 1
        
        # Mock de datos del usuario
        user_row = (1, 'test_user', 'Juan Pérez', 'juan@example.com', 
                   '123456789', 'Calle 123', 'operator', True,
                   '2024-01-01', '2024-01-15', '2024-01-15 10:00:00')
        
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = user_row
        
        self.mock_db.connection.cursor.return_value = mock_cursor
        
        usuario = self.profiles_manager.obtener_usuario_por_id(usuario_id)
        
        # Verificaciones
        assert usuario is not None
        assert isinstance(usuario, dict)
        assert usuario['id'] == 1
        assert usuario['username'] == 'test_user'
        assert usuario['nombre_completo'] == 'Juan Pérez'
        assert usuario['email'] == 'juan@example.com'
        assert usuario['activo'] is True
    
    @pytest.mark.skipif(ProfilesManager is None, reason="ProfilesManager no disponible")
    def test_obtener_usuario_por_id_inexistente(self):
        """Test obtener usuario que no existe."""
        usuario_id = 999
        
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = None
        
        self.mock_db.connection.cursor.return_value = mock_cursor
        
        usuario = self.profiles_manager.obtener_usuario_por_id(usuario_id)
        
        # Verificaciones
        assert usuario is None
    
    @pytest.mark.skipif(ProfilesManager is None, reason="ProfilesManager no disponible")
    def test_obtener_usuario_por_username(self):
        """Test obtener usuario por username."""
        username = 'test_user'
        
        user_row = (1, 'test_user', 'Juan Pérez', 'juan@example.com', 
                   '123456789', 'Calle 123', 'operator', True,
                   '2024-01-01', '2024-01-15', '2024-01-15 10:00:00')
        
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = user_row
        
        self.mock_db.connection.cursor.return_value = mock_cursor
        
        usuario = self.profiles_manager.obtener_usuario_por_username(username)
        
        # Verificaciones
        assert usuario is not None
        assert usuario['username'] == 'test_user'
        assert usuario['nombre_completo'] == 'Juan Pérez'
    
    @pytest.mark.skipif(ProfilesManager is None, reason="ProfilesManager no disponible")
    def test_obtener_usuario_por_email(self):
        """Test obtener usuario por email."""
        email = 'juan@example.com'
        
        user_row = (1, 'test_user', 'Juan Pérez', 'juan@example.com', 
                   '123456789', 'Calle 123', 'operator', True,
                   '2024-01-01', '2024-01-15', '2024-01-15 10:00:00')
        
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = user_row
        
        self.mock_db.connection.cursor.return_value = mock_cursor
        
        usuario = self.profiles_manager.obtener_usuario_por_email(email)
        
        # Verificaciones
        assert usuario is not None
        assert usuario['email'] == 'juan@example.com'
        assert usuario['username'] == 'test_user'
    
    @pytest.mark.skipif(ProfilesManager is None, reason="ProfilesManager no disponible")
    def test_obtener_todos_usuarios_solo_activos(self):
        """Test obtener todos los usuarios activos."""
        users_data = [
            (1, 'user1', 'Usuario Uno', 'user1@example.com', '111111111', 'Dir1', 'operator', True, '2024-01-01', '2024-01-15', None),
            (2, 'user2', 'Usuario Dos', 'user2@example.com', '222222222', 'Dir2', 'viewer', True, '2024-01-02', '2024-01-16', None)
        ]
        
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = users_data
        
        self.mock_db.connection.cursor.return_value = mock_cursor
        
        usuarios = self.profiles_manager.obtener_todos_usuarios(incluir_inactivos=False)
        
        # Verificaciones
        assert isinstance(usuarios, list)
        assert len(usuarios) == 2
        assert usuarios[0]['username'] == 'user1'
        assert usuarios[1]['username'] == 'user2'
        
        # Verificar que se consultaron solo usuarios activos
        call_args = mock_cursor.execute.call_args[0]
        assert 'WHERE activo = 1' in call_args[0]
    
    @pytest.mark.skipif(ProfilesManager is None, reason="ProfilesManager no disponible")
    def test_obtener_todos_usuarios_incluir_inactivos(self):
        """Test obtener todos los usuarios incluyendo inactivos."""
        users_data = [
            (1, 'user1', 'Usuario Uno', 'user1@example.com', '111111111', 'Dir1', 'operator', True, '2024-01-01', '2024-01-15', None),
            (3, 'user3', 'Usuario Tres', 'user3@example.com', '333333333', 'Dir3', 'viewer', False, '2024-01-03', '2024-01-17', None)
        ]
        
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = users_data
        
        self.mock_db.connection.cursor.return_value = mock_cursor
        
        usuarios = self.profiles_manager.obtener_todos_usuarios(incluir_inactivos=True)
        
        # Verificaciones
        assert isinstance(usuarios, list)
        assert len(usuarios) == 2
        
        # Verificar que se consultaron todos los usuarios
        call_args = mock_cursor.execute.call_args[0]
        assert 'WHERE activo = 1' not in call_args[0]
        assert 'ORDER BY created_at DESC' in call_args[0]
    
    @pytest.mark.skipif(ProfilesManager is None, reason="ProfilesManager no disponible")
    def test_actualizar_usuario_exitoso(self):
        """Test actualizar usuario exitosamente."""
        usuario_id = 1
        datos_actualizados = {
            'nombre_completo': 'Nombre Actualizado',
            'email': 'nuevo_email@example.com',
            'telefono': '987654321',
            'rol': 'supervisor'
        }
        
        mock_cursor = Mock()
        mock_cursor.rowcount = 1  # Una fila actualizada
        
        self.mock_db.connection.cursor.return_value = mock_cursor
        
        # Mock del usuario existente
        with patch.object(self.profiles_manager, 'obtener_usuario_por_id', 
                         return_value={'id': usuario_id, 'username': 'test_user'}):
            with patch.object(self.profiles_manager, '_validar_datos_actualizacion',
                             return_value={'valid': True, 'message': 'Datos válidos'}):
                with patch.object(self.profiles_manager, '_sanitizar_datos_usuario', return_value=datos_actualizados):
                    resultado = self.profiles_manager.actualizar_usuario(usuario_id, datos_actualizados)
        
        # Verificaciones
        assert resultado['success'] is True
        assert 'exitosamente' in resultado['message']
        
        # Verificar que se ejecutó UPDATE
        mock_cursor.execute.assert_called()
        self.mock_db.connection.commit.assert_called()
    
    @pytest.mark.skipif(ProfilesManager is None, reason="ProfilesManager no disponible")
    def test_actualizar_usuario_inexistente(self):
        """Test actualizar usuario que no existe."""
        usuario_id = 999
        datos_actualizados = {'nombre_completo': 'Nuevo Nombre'}
        
        # Mock de usuario no encontrado
        with patch.object(self.profiles_manager, 'obtener_usuario_por_id', return_value=None):
            resultado = self.profiles_manager.actualizar_usuario(usuario_id, datos_actualizados)
        
        # Verificaciones
        assert resultado['success'] is False
        assert 'no encontrado' in resultado['message']
    
    @pytest.mark.skipif(ProfilesManager is None, reason="ProfilesManager no disponible")
    def test_eliminar_usuario_exitoso(self):
        """Test eliminar usuario exitosamente (soft delete)."""
        usuario_id = 2
        
        user_data = {'id': usuario_id, 'username': 'user_to_delete'}
        
        mock_cursor = Mock()
        mock_cursor.rowcount = 1  # Una fila afectada
        
        self.mock_db.connection.cursor.return_value = mock_cursor
        
        # Mock del usuario existente
        with patch.object(self.profiles_manager, 'obtener_usuario_por_id', return_value=user_data):
            resultado = self.profiles_manager.eliminar_usuario(usuario_id)
        
        # Verificaciones
        assert resultado['success'] is True
        assert 'exitosamente' in resultado['message']
        
        # Verificar que se hizo soft delete (activo = 0)
        call_args = mock_cursor.execute.call_args[0]
        assert 'activo = 0' in call_args[0]
        assert 'updated_at = GETDATE()' in call_args[0]
        self.mock_db.connection.commit.assert_called()
    
    @pytest.mark.skipif(ProfilesManager is None, reason="ProfilesManager no disponible")
    def test_obtener_estadisticas_usuarios(self):
        """Test obtener estadísticas de usuarios."""
        mock_cursor = Mock()
        mock_cursor.fetchone.side_effect = [
            (25,),  # Total usuarios
            (20,),  # Usuarios activos
            (3,),   # Nuevos usuarios mes
            (12,)   # Usuarios activos semana
        ]
        
        # Mock de usuarios por rol
        mock_cursor.fetchall.side_effect = [
            [('admin', 2), ('supervisor', 4), ('operator', 8), ('viewer', 6)],  # Por rol
        ]
        
        self.mock_db.connection.cursor.return_value = mock_cursor
        
        stats = self.profiles_manager.obtener_estadisticas_usuarios()
        
        # Verificaciones
        assert isinstance(stats, dict)
        assert stats['total_usuarios'] == 25
        assert stats['usuarios_activos'] == 20
        assert stats['nuevos_usuarios_mes'] == 3
        assert stats['usuarios_activos_semana'] == 12
        assert 'usuarios_por_rol' in stats
        assert stats['usuarios_por_rol']['admin'] == 2
        assert stats['usuarios_por_rol']['operator'] == 8
    
    @pytest.mark.skipif(ProfilesManager is None, reason="ProfilesManager no disponible")
    def test_validar_datos_usuario_validos(self):
        """Test validación de datos de usuario válidos."""
        datos_usuario = {
            'username': 'valid_user',
            'email': 'valid@example.com',
            'nombre_completo': 'Usuario Válido',
            'rol': 'operator'
        }
        
        resultado = self.profiles_manager._validar_datos_usuario(datos_usuario)
        
        # Verificaciones
        assert resultado['valid'] is True
        assert 'válidos' in resultado['message']
    
    @pytest.mark.skipif(ProfilesManager is None, reason="ProfilesManager no disponible")
    def test_validar_datos_usuario_username_vacio(self):
        """Test validación con username vacío."""
        datos_usuario = {
            'username': '',
            'email': 'test@example.com',
            'nombre_completo': 'Usuario Test'
        }
        
        resultado = self.profiles_manager._validar_datos_usuario(datos_usuario)
        
        # Verificaciones
        assert resultado['valid'] is False
        assert 'requerido' in resultado['message']
    
    @pytest.mark.skipif(ProfilesManager is None, reason="ProfilesManager no disponible")
    def test_validar_datos_usuario_username_muy_corto(self):
        """Test validación con username muy corto."""
        datos_usuario = {
            'username': 'ab',  # Solo 2 caracteres, mínimo 3
            'email': 'test@example.com',
            'nombre_completo': 'Usuario Test'
        }
        
        resultado = self.profiles_manager._validar_datos_usuario(datos_usuario)
        
        # Verificaciones
        assert resultado['valid'] is False
        assert 'al menos' in resultado['message']
    
    @pytest.mark.skipif(ProfilesManager is None, reason="ProfilesManager no disponible")
    def test_validar_datos_usuario_email_invalido(self):
        """Test validación con email inválido."""
        datos_usuario = {
            'username': 'valid_user',
            'email': 'email_invalido',  # Sin @ ni dominio
            'nombre_completo': 'Usuario Test'
        }
        
        resultado = self.profiles_manager._validar_datos_usuario(datos_usuario)
        
        # Verificaciones
        assert resultado['valid'] is False
        assert 'inválido' in resultado['message']
    
    @pytest.mark.skipif(ProfilesManager is None, reason="ProfilesManager no disponible")
    def test_validar_datos_usuario_rol_invalido(self):
        """Test validación con rol inválido."""
        datos_usuario = {
            'username': 'valid_user',
            'email': 'valid@example.com',
            'nombre_completo': 'Usuario Test',
            'rol': 'rol_inexistente'
        }
        
        resultado = self.profiles_manager._validar_datos_usuario(datos_usuario)
        
        # Verificaciones
        assert resultado['valid'] is False
        assert 'inválido' in resultado['message']
        assert 'viewer' in resultado['message']  # Debería mostrar roles válidos
    
    @pytest.mark.skipif(ProfilesManager is None, reason="ProfilesManager no disponible")
    def test_verificar_unicidad_usuario_unico(self):
        """Test verificar unicidad cuando usuario es único."""
        username = 'nuevo_usuario'
        email = 'nuevo@example.com'
        
        mock_cursor = Mock()
        mock_cursor.fetchone.side_effect = [
            (0,),  # Username no existe
            (0,)   # Email no existe
        ]
        
        self.mock_db.connection.cursor.return_value = mock_cursor
        
        es_unico = self.profiles_manager._verificar_unicidad_usuario(username, email)
        
        # Verificaciones
        assert es_unico is True
    
    @pytest.mark.skipif(ProfilesManager is None, reason="ProfilesManager no disponible")
    def test_verificar_unicidad_usuario_duplicado(self):
        """Test verificar unicidad cuando usuario ya existe."""
        username = 'usuario_existente'
        email = 'existente@example.com'
        
        mock_cursor = Mock()
        mock_cursor.fetchone.side_effect = [
            (1,),  # Username ya existe
            (0,)   # Email no existe
        ]
        
        self.mock_db.connection.cursor.return_value = mock_cursor
        
        es_unico = self.profiles_manager._verificar_unicidad_usuario(username, email)
        
        # Verificaciones
        assert es_unico is False


if __name__ == "__main__":
    # Ejecutar tests específicos
    test_suite = TestProfilesManager()
    test_suite.setup_method()
    
    if ProfilesManager:
        print("=== EJECUTANDO TESTS DE PROFILES MANAGER ===")
        
        try:
            test_suite.test_validar_datos_usuario_validos()
            print("[CHECK] Test validar datos válidos - PASADO")
        except Exception as e:
            print(f"[ERROR] Test validar datos válidos - FALLIDO: {e}")
        
        try:
            test_suite.test_validar_datos_usuario_username_vacio()
            print("[CHECK] Test username vacío - PASADO")
        except Exception as e:
            print(f"[ERROR] Test username vacío - FALLIDO: {e}")
        
        try:
            test_suite.test_validar_datos_usuario_email_invalido()
            print("[CHECK] Test email inválido - PASADO")
        except Exception as e:
            print(f"[ERROR] Test email inválido - FALLIDO: {e}")
        
        try:
            test_suite.test_validar_datos_usuario_rol_invalido()
            print("[CHECK] Test rol inválido - PASADO")
        except Exception as e:
            print(f"[ERROR] Test rol inválido - FALLIDO: {e}")
        
        print("=== TESTS DE PROFILES MANAGER COMPLETADOS ===")
    else:
        print("[ERROR] ProfilesManager no disponible para testing")