"""
Tests for SessionsManager - Sistema de sesiones refactorizado
Tests de creación, validación, timeout y límites de sesiones concurrentes
"""

import pytest
import datetime
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# Agregar el directorio raíz al path
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

try:
    from rexus.modules.usuarios.submodules.sessions_manager import SessionsManager, SessionInfo
    from tests.obras.mock_auth_context import MockDatabaseContext
except ImportError as e:
    print(f"Error importando módulos: {e}")
    SessionsManager = None
    SessionInfo = None


class TestSessionsManager:
    """Suite de tests para SessionsManager."""
    
    def setup_method(self):
        """Configuración para cada test."""
        self.mock_db = MockDatabaseContext()
        self.sessions_manager = SessionsManager(self.mock_db.connection) if SessionsManager else None
    
    @pytest.mark.skipif(SessionsManager is None, reason="SessionsManager no disponible")
    def test_crear_sesion_exitosa(self):
        """Test crear nueva sesión exitosamente."""
        usuario_id = 1
        username = "test_user"
        ip_address = "192.168.1.100"
        user_agent = "Mozilla/5.0 Test Browser"
        
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = (2,)  # 2 sesiones activas (menos del límite)
        
        self.mock_db.connection.cursor.return_value = mock_cursor
        
        with patch.object(self.sessions_manager, '_generar_session_id', return_value='test_session_id'):
            resultado = self.sessions_manager.crear_sesion(usuario_id, username, ip_address, user_agent)
        
        # Verificaciones
        assert resultado['success'] is True
        assert 'session_id' in resultado
        assert resultado['session_id'] == 'test_session_id'
        assert 'exitosamente' in resultado['message']
        
        # Verificar que se ejecutó el INSERT
        mock_cursor.execute.assert_called()
        self.mock_db.connection.commit.assert_called()
    
    @pytest.mark.skipif(SessionsManager is None, reason="SessionsManager no disponible")
    def test_crear_sesion_con_limite_excedido(self):
        """Test crear sesión cuando se excede el límite de sesiones concurrentes."""
        usuario_id = 1
        username = "test_user"
        
        mock_cursor = Mock()
        # Primera consulta: 3 sesiones activas (límite alcanzado)
        # Segunda consulta: obtener sesión más antigua para cerrar
        mock_cursor.fetchone.side_effect = [
            (3,),  # Límite de sesiones alcanzado
            ('old_session_id',)  # Sesión más antigua
        ]
        
        self.mock_db.connection.cursor.return_value = mock_cursor
        
        with patch.object(self.sessions_manager, '_generar_session_id', return_value='new_session_id'):
            with patch.object(self.sessions_manager, 'cerrar_sesion') as mock_cerrar:
                resultado = self.sessions_manager.crear_sesion(usuario_id, username)
        
        # Verificaciones
        assert resultado['success'] is True
        mock_cerrar.assert_called_once_with('old_session_id')  # Debería cerrar sesión antigua
    
    @pytest.mark.skipif(SessionsManager is None, reason="SessionsManager no disponible")
    def test_validar_sesion_valida(self):
        """Test validar sesión que es válida y activa."""
        session_id = "valid_session_id"
        usuario_id = 1
        username = "test_user"
        now = datetime.datetime.now()
        created_at = now - datetime.timedelta(minutes=30)  # Sesión de 30 minutos
        last_activity = now - datetime.timedelta(minutes=10)  # Última actividad hace 10 minutos
        
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = (usuario_id, username, created_at, last_activity, True)
        
        self.mock_db.connection.cursor.return_value = mock_cursor
        
        resultado = self.sessions_manager.validar_sesion(session_id)
        
        # Verificaciones
        assert resultado['valid'] is True
        assert resultado['usuario_id'] == usuario_id
        assert resultado['username'] == username
        
        # Verificar que se actualizó la última actividad
        mock_cursor.execute.assert_called()
        self.mock_db.connection.commit.assert_called()
    
    @pytest.mark.skipif(SessionsManager is None, reason="SessionsManager no disponible")
    def test_validar_sesion_expirada(self):
        """Test validar sesión que ha expirado por inactividad."""
        session_id = "expired_session_id"
        now = datetime.datetime.now()
        # Última actividad hace 3 horas (excede timeout de 2 horas)
        last_activity = now - datetime.timedelta(hours=3)
        
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = (1, "test_user", now, last_activity, True)
        
        self.mock_db.connection.cursor.return_value = mock_cursor
        
        with patch.object(self.sessions_manager, 'cerrar_sesion') as mock_cerrar:
            resultado = self.sessions_manager.validar_sesion(session_id)
        
        # Verificaciones
        assert resultado['valid'] is False
        assert 'expirada' in resultado['message']
        mock_cerrar.assert_called_once_with(session_id)
    
    @pytest.mark.skipif(SessionsManager is None, reason="SessionsManager no disponible")
    def test_validar_sesion_inexistente(self):
        """Test validar sesión que no existe."""
        session_id = "nonexistent_session"
        
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = None  # Sesión no encontrada
        
        self.mock_db.connection.cursor.return_value = mock_cursor
        
        resultado = self.sessions_manager.validar_sesion(session_id)
        
        # Verificaciones
        assert resultado['valid'] is False
        assert 'no encontrada' in resultado['message']
    
    @pytest.mark.skipif(SessionsManager is None, reason="SessionsManager no disponible")
    def test_cerrar_sesion_exitosa(self):
        """Test cerrar sesión exitosamente."""
        session_id = "test_session_id"
        
        mock_cursor = Mock()
        mock_cursor.rowcount = 1  # Una fila afectada (sesión encontrada y cerrada)
        
        self.mock_db.connection.cursor.return_value = mock_cursor
        
        resultado = self.sessions_manager.cerrar_sesion(session_id)
        
        # Verificaciones
        assert resultado['success'] is True
        assert 'correctamente' in resultado['message']
        
        # Verificar query de actualización
        mock_cursor.execute.assert_called()
        call_args = mock_cursor.execute.call_args[0]
        assert 'is_active = 0' in call_args[0]
        assert 'closed_at = GETDATE()' in call_args[0]
        self.mock_db.connection.commit.assert_called()
    
    @pytest.mark.skipif(SessionsManager is None, reason="SessionsManager no disponible")
    def test_cerrar_sesion_inexistente(self):
        """Test cerrar sesión que no existe."""
        session_id = "nonexistent_session"
        
        mock_cursor = Mock()
        mock_cursor.rowcount = 0  # Ninguna fila afectada
        
        self.mock_db.connection.cursor.return_value = mock_cursor
        
        resultado = self.sessions_manager.cerrar_sesion(session_id)
        
        # Verificaciones
        assert resultado['success'] is False
        assert 'no encontrada' in resultado['message']
    
    @pytest.mark.skipif(SessionsManager is None, reason="SessionsManager no disponible")
    def test_cerrar_todas_sesiones_usuario(self):
        """Test cerrar todas las sesiones de un usuario específico."""
        usuario_id = 1
        
        mock_cursor = Mock()
        mock_cursor.rowcount = 3  # 3 sesiones cerradas
        
        self.mock_db.connection.cursor.return_value = mock_cursor
        
        resultado = self.sessions_manager.cerrar_todas_sesiones_usuario(usuario_id)
        
        # Verificaciones
        assert resultado['success'] is True
        assert resultado['sesiones_cerradas'] == 3
        assert '3 sesiones cerradas' in resultado['message']
    
    @pytest.mark.skipif(SessionsManager is None, reason="SessionsManager no disponible")
    def test_obtener_sesiones_usuario(self):
        """Test obtener todas las sesiones activas de un usuario."""
        usuario_id = 1
        now = datetime.datetime.now()
        
        # Mock de datos de sesiones
        sesiones_mock = [
            ('session1', usuario_id, 'test_user', '192.168.1.100', 'Browser1', now, now, True),
            ('session2', usuario_id, 'test_user', '192.168.1.101', 'Browser2', now, now, True)
        ]
        
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = sesiones_mock
        
        self.mock_db.connection.cursor.return_value = mock_cursor
        
        sesiones = self.sessions_manager.obtener_sesiones_usuario(usuario_id)
        
        # Verificaciones
        assert isinstance(sesiones, list)
        assert len(sesiones) == 2
        
        if SessionInfo:
            assert all(isinstance(sesion, SessionInfo) for sesion in sesiones)
            assert sesiones[0].session_id == 'session1'
            assert sesiones[1].session_id == 'session2'
    
    @pytest.mark.skipif(SessionsManager is None, reason="SessionsManager no disponible")
    def test_obtener_estadisticas_sesiones(self):
        """Test obtener estadísticas del sistema de sesiones."""
        mock_cursor = Mock()
        mock_cursor.fetchone.side_effect = [
            (5,),     # Sesiones activas
            (3,),     # Usuarios únicos conectados  
            (45.5,)   # Duración promedio en minutos
        ]
        mock_cursor.fetchall.return_value = [
            ('192.168.1.100', 10),
            ('192.168.1.101', 8),
            ('192.168.1.102', 5)
        ]
        
        self.mock_db.connection.cursor.return_value = mock_cursor
        
        stats = self.sessions_manager.obtener_estadisticas_sesiones()
        
        # Verificaciones
        assert isinstance(stats, dict)
        assert stats['sesiones_activas'] == 5
        assert stats['usuarios_conectados'] == 3
        assert stats['duracion_promedio_minutos'] == 45.5
        assert 'top_ips' in stats
        assert len(stats['top_ips']) == 3
        assert stats['top_ips'][0]['ip'] == '192.168.1.100'
        assert stats['top_ips'][0]['sesiones'] == 10
    
    @pytest.mark.skipif(SessionsManager is None, reason="SessionsManager no disponible")
    def test_generar_session_id_unico(self):
        """Test generar ID de sesión único y seguro."""
        session_id1 = self.sessions_manager._generar_session_id()
        session_id2 = self.sessions_manager._generar_session_id()
        
        # Verificaciones
        assert isinstance(session_id1, str)
        assert isinstance(session_id2, str)
        assert len(session_id1) > 20  # Debe ser suficientemente largo
        assert session_id1 != session_id2  # Deben ser únicos
        
        # No debe contener caracteres peligrosos
        import re
        assert re.match(r'^[a-zA-Z0-9_-]+$', session_id1)
    
    @pytest.mark.skipif(SessionsManager is None, reason="SessionsManager no disponible")
    def test_verificar_limite_sesiones_no_excedido(self):
        """Test verificar límite de sesiones cuando no se ha excedido."""
        usuario_id = 1
        
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = (2,)  # 2 sesiones activas (menos del límite de 3)
        
        self.mock_db.connection.cursor.return_value = mock_cursor
        
        puede_crear = self.sessions_manager._verificar_limite_sesiones(usuario_id)
        
        # Verificaciones
        assert puede_crear is True
    
    @pytest.mark.skipif(SessionsManager is None, reason="SessionsManager no disponible")
    def test_verificar_limite_sesiones_excedido(self):
        """Test verificar límite de sesiones cuando se ha excedido."""
        usuario_id = 1
        
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = (3,)  # 3 sesiones activas (límite alcanzado)
        
        self.mock_db.connection.cursor.return_value = mock_cursor
        
        puede_crear = self.sessions_manager._verificar_limite_sesiones(usuario_id)
        
        # Verificaciones
        assert puede_crear is False
    
    @pytest.mark.skipif(SessionsManager is None, reason="SessionsManager no disponible")
    def test_limpiar_sesiones_expiradas(self):
        """Test limpiar sesiones expiradas automáticamente."""
        mock_cursor = Mock()
        mock_cursor.rowcount = 2  # 2 sesiones expiradas limpiadas
        
        self.mock_db.connection.cursor.return_value = mock_cursor
        
        # Ejecutar limpieza
        self.sessions_manager._limpiar_sesiones_expiradas()
        
        # Verificaciones
        mock_cursor.execute.assert_called()
        call_args = mock_cursor.execute.call_args[0]
        assert 'is_active = 0' in call_args[0]
        assert 'last_activity <' in call_args[0]
        
        # Si se limpiaron sesiones, se debe hacer commit
        if mock_cursor.rowcount > 0:
            self.mock_db.connection.commit.assert_called()


if __name__ == "__main__":
    # Ejecutar tests específicos
    test_suite = TestSessionsManager()
    test_suite.setup_method()
    
    if SessionsManager:
        print("=== EJECUTANDO TESTS DE SESSIONS MANAGER ===")
        
        try:
            test_suite.test_generar_session_id_unico()
            print("✅ Test generar session ID - PASADO")
        except Exception as e:
            print(f"❌ Test generar session ID - FALLIDO: {e}")
        
        try:
            test_suite.test_verificar_limite_sesiones_no_excedido()
            print("✅ Test límite sesiones (no excedido) - PASADO")
        except Exception as e:
            print(f"❌ Test límite sesiones (no excedido) - FALLIDO: {e}")
        
        try:
            test_suite.test_verificar_limite_sesiones_excedido()
            print("✅ Test límite sesiones (excedido) - PASADO")
        except Exception as e:
            print(f"❌ Test límite sesiones (excedido) - FALLIDO: {e}")
        
        print("=== TESTS DE SESSIONS MANAGER COMPLETADOS ===")
    else:
        print("❌ SessionsManager no disponible para testing")