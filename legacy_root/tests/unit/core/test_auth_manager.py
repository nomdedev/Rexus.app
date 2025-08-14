"""
Tests unitarios para el Core de Autenticación de Rexus.app

Descripción:
    Tests que validan el sistema de autenticación, autorización y seguridad,
    replicando el comportamiento real de la aplicación para detectar bugs
    en la lógica de negocio crítica.

Scope:
    - Autenticación de usuarios (login/logout)
    - Verificación de permisos y roles
    - Gestión de sesiones
    - Seguridad y validaciones
    - Manejo de errores de autenticación

Dependencies:
    - pytest fixtures (mock_db_connection, sample_user_data)
    - Mocks para SecurityManager y AuthManager
    - Datos de prueba realistas

Author: Rexus Testing Team
Date: 2025-08-10
Version: 1.0.0
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta


class TestAuthManager:
    """
    Tests unitarios para AuthManager - Sistema de autenticación principal.

    Verifica que la autenticación, autorización y gestión de usuarios
    funcionan correctamente según las especificaciones del sistema.
    """

    def test_crear_auth_manager_con_db_connection_inicializa_correctamente(self, mock_db_connection):
        """
        Test que valida la inicialización correcta del AuthManager.

        Verifica que:
        - Se puede crear una instancia con conexión a DB
        - Los atributos se inicializan correctamente
        - No se lanzan excepciones durante la creación
        """
        # ARRANGE: Preparar dependencias
        from rexus.core.auth import AuthManager

        # ACT: Crear instancia del AuthManager
        auth_manager = AuthManager(db_connection=mock_db_connection)

        # ASSERT: Verificar inicialización correcta
        assert auth_manager is not None
        assert auth_manager.db_connection == mock_db_connection
        assert auth_manager.current_user is None
        assert auth_manager.current_role is None
        assert auth_manager.session_active is False

    def test_authenticate_user_con_credenciales_validas_retorna_datos_usuario(self, mock_db_connection, sample_user_data):
        """
        Test que valida la autenticación exitosa con credenciales válidas.

        Verifica que:
        - Las credenciales válidas permiten autenticación
        - Se retornan los datos correctos del usuario
        - Se actualiza el estado de sesión
        """
        # ARRANGE: Preparar mock de DB con usuario válido
        from rexus.core.auth import AuthManager

        # Configurar respuesta de la base de datos
        mock_db_connection.execute_query.return_value = [(
            sample_user_data['id'],
            sample_user_data['username'],
            'hashed_password',  # Hash de contraseña
            sample_user_data['rol'],
            'Activo',
            sample_user_data['nombre'],
            sample_user_data['apellido'],
            sample_user_data['email']
        )]

        auth_manager = AuthManager(db_connection=mock_db_connection)

        # Mock de verificación de contraseña
        with patch('rexus.utils.password_security.verify_password_secure', return_value=True):
            # ACT: Autenticar usuario
            resultado = auth_manager.authenticate_user(sample_user_data['username'], 'test_password')

        # ASSERT: Verificar autenticación exitosa
        assert resultado is not None
        assert resultado['username'] == sample_user_data['username']
        assert resultado['id'] == sample_user_data['id']
        assert 'password' not in resultado  # No debe contener contraseña
        assert auth_manager.session_active is True

    def test_authenticate_user_con_credenciales_invalidas_retorna_none(self, mock_db_connection):
        """
        Test que valida el rechazo de credenciales inválidas.

        Verifica que:
        - Las credenciales inválidas son rechazadas
        - No se establece sesión
        - Se retorna None apropiadamente
        """
        # ARRANGE: Preparar mock sin usuarios
        from rexus.core.auth import AuthManager

        mock_db_connection.execute_query.return_value = []  # Usuario no encontrado
        auth_manager = AuthManager(db_connection=mock_db_connection)

        # ACT: Intentar autenticar con credenciales inválidas
        resultado = auth_manager.authenticate_user('usuario_inexistente', 'password_incorrecta')

        # ASSERT: Verificar rechazo de autenticación
        assert resultado is None
        assert auth_manager.current_user is None
        assert auth_manager.session_active is False

    def test_authenticate_user_con_password_incorrecta_retorna_none(self, mock_db_connection, sample_user_data):
        """
        Test que valida el rechazo cuando la contraseña es incorrecta.

        Verifica que:
        - Usuario existe pero contraseña es incorrecta
        - La verificación de hash falla apropiadamente
        - No se establece sesión
        """
        # ARRANGE: Usuario existe pero password incorrecta
        from rexus.core.auth import AuthManager

        mock_db_connection.execute_query.return_value = [(
            sample_user_data['id'],
            sample_user_data['username'],
            'hashed_password',
            sample_user_data['rol'],
            'Activo',
            sample_user_data['nombre'],
            sample_user_data['apellido'],
            sample_user_data['email']
        )]

        auth_manager = AuthManager(db_connection=mock_db_connection)

        # Mock de verificación de contraseña que falla
        with patch('rexus.utils.password_security.verify_password_secure', return_value=False):
            # ACT: Autenticar con contraseña incorrecta
            resultado = auth_manager.authenticate_user(sample_user_data['username'], 'password_incorrecta')

        # ASSERT: Verificar rechazo
        assert resultado is None
        assert auth_manager.current_user is None

    def test_authenticate_user_con_usuario_inactivo_retorna_none(self, mock_db_connection, sample_user_data):
        """
        Test que valida el rechazo de usuarios inactivos.

        Verifica que:
        - Los usuarios con estado 'Inactivo' son rechazados
        - Aunque las credenciales sean correctas
        - Se mantiene la seguridad del sistema
        """
        # ARRANGE: Usuario inactivo
        from rexus.core.auth import AuthManager

        mock_db_connection.execute_query.return_value = [(
            sample_user_data['id'],
            sample_user_data['username'],
            'hashed_password',
            sample_user_data['rol'],
            'Inactivo',  # Usuario inactivo
            sample_user_data['nombre'],
            sample_user_data['apellido'],
            sample_user_data['email']
        )]

        auth_manager = AuthManager(db_connection=mock_db_connection)

        # ACT: Intentar autenticar usuario inactivo
        resultado = auth_manager.authenticate_user(sample_user_data['username'], 'test_password')

        # ASSERT: Verificar rechazo por usuario inactivo
        assert resultado is None

    @pytest.mark.parametrize("username,password,should_succeed", [
        ("admin", "admin", True),
        ("user", "user", True),
        ("", "password", False),          # Username vacío
        ("user", "", False),              # Password vacío
        (None, "password", False),        # Username None
        ("user", None, False),            # Password None
        ("user123", "pass123", False),    # Usuario inexistente
    ])
    def test_authenticate_user_con_diferentes_combinaciones_credenciales(
        self, mock_db_connection, username, password, should_succeed
    ):
        """
        Test parametrizado que valida diferentes combinaciones de credenciales.

        Cubre casos edge y validaciones de entrada para asegurar
        robustez del sistema de autenticación.
        """
        # ARRANGE: Configurar mock según caso
        from rexus.core.auth import AuthManager

        if should_succeed and username and password:
            # Usuario válido encontrado
            mock_db_connection.execute_query.return_value = [(
                1, username, 'hashed_password', 'USER', 'Activo', 'Test', 'User', 'test@test.com'
            )]
        else:
            # Usuario no encontrado o datos inválidos
            mock_db_connection.execute_query.return_value = []

        auth_manager = AuthManager(db_connection=mock_db_connection)

        # Mock de verificación de contraseña
        with patch('rexus.utils.password_security.verify_password_secure', return_value=should_succeed):
            # ACT: Intentar autenticación
            resultado = auth_manager.authenticate_user(username, password)

        # ASSERT: Verificar resultado esperado
        if should_succeed:
            assert resultado is not None
            assert resultado['username'] == username
        else:
            assert resultado is None

    def test_logout_limpia_sesion_correctamente(self, mock_db_connection, sample_user_data):
        """
        Test que valida la limpieza correcta de sesión al hacer logout.

        Verifica que:
        - Se limpia el usuario actual
        - Se limpia el rol actual
        - Se marca la sesión como inactiva
        """
        # ARRANGE: Usuario autenticado
        from rexus.core.auth import AuthManager

        auth_manager = AuthManager(db_connection=mock_db_connection)
        auth_manager.current_user = sample_user_data
        auth_manager.current_role = sample_user_data['rol']
        auth_manager.session_active = True

        # ACT: Hacer logout
        auth_manager.logout()

        # ASSERT: Verificar limpieza de sesión
        assert auth_manager.current_user is None
        assert auth_manager.current_role is None
        assert auth_manager.session_active is False

    def test_manejo_excepcion_database_durante_autenticacion(self, mock_db_connection):
        """
        Test que valida el manejo de excepciones de base de datos.

        Verifica que:
        - Las excepciones de DB se capturan apropiadamente
        - Se retorna None en caso de error
        - No se lanzan excepciones no controladas
        """
        # ARRANGE: Mock que lanza excepción
        from rexus.core.auth import AuthManager

        mock_db_connection.execute_query.side_effect = Exception("Error de conexión DB")
        auth_manager = AuthManager(db_connection=mock_db_connection)

        # ACT: Intentar autenticación con error de DB
        resultado = auth_manager.authenticate_user('user', 'password')

        # ASSERT: Verificar manejo de error
        assert resultado is None
        assert auth_manager.current_user is None


class TestSecurityManager:
    """
    Tests unitarios para SecurityManager - Sistema de seguridad integral.

    Verifica permisos, autorización, gestión de sesiones y eventos de seguridad.
    """

    def test_verificar_password_con_hash_valido_retorna_true(self):
        """
        Test que valida la verificación correcta de contraseñas.

        Verifica que:
        - Las contraseñas correctas se validan apropiadamente
        - El sistema de hashing funciona correctamente
        - Se mantiene la seguridad de las contraseñas
        """
        # ARRANGE: Preparar contraseña y hash válidos
        from rexus.core.security import SecurityManager

        password = "test_password_123"

        # Mock de verificación exitosa
        with patch('rexus.utils.password_security.verify_password_secure', return_value=True):
            security_manager = SecurityManager()

            # ACT: Verificar contraseña
            resultado = security_manager.verify_password(password, "fake_hash")

        # ASSERT: Verificar validación exitosa
        assert resultado is True

    def test_verificar_password_con_hash_invalido_retorna_false(self):
        """
        Test que valida el rechazo de contraseñas incorrectas.

        Verifica que:
        - Las contraseñas incorrectas son rechazadas
        - El sistema mantiene seguridad ante intentos maliciosos
        """
        # ARRANGE: Contraseña incorrecta
        from rexus.core.security import SecurityManager

        # Mock de verificación fallida
        with patch('rexus.utils.password_security.verify_password_secure', return_value=False):
            security_manager = SecurityManager()

            # ACT: Verificar contraseña incorrecta
            resultado = security_manager.verify_password("wrong_password", "hash")

        # ASSERT: Verificar rechazo
        assert resultado is False

    def test_login_exitoso_emite_senal_user_logged_in(self, mock_db_connection):
        """
        Test que valida que se emite la señal correcta al hacer login exitoso.

        Verifica que:
        - Se emite la señal user_logged_in
        - La señal contiene los datos correctos
        - Los componentes pueden reaccionar al evento
        """
        # ARRANGE: Mock de autenticación exitosa
        from rexus.core.security import SecurityManager

        with patch('rexus.core.auth.get_auth_manager') as mock_auth:
            mock_auth_instance = Mock()
            mock_auth_instance.authenticate_user.return_value = {
                'id': 1,
                'username': 'test_user',
                'role': 'USER'
            }
            mock_auth.return_value = mock_auth_instance

            security_manager = SecurityManager()

            # Mock de la señal
            with patch.object(security_manager, 'user_logged_in') as mock_signal:
                # ACT: Hacer login
                resultado = security_manager.login('test_user', 'password')

                # ASSERT: Verificar que se emitió la señal
                assert resultado is True
                mock_signal.emit.assert_called_once()

    def test_session_valida_dentro_tiempo_limite_retorna_true(self):
        """
        Test que valida el control de tiempo de sesión.

        Verifica que:
        - Las sesiones recientes son consideradas válidas
        - El tiempo de sesión se controla apropiadamente
        """
        # ARRANGE: Sesión reciente
        from rexus.core.security import SecurityManager

        security_manager = SecurityManager()
        security_manager.current_user = {'username': 'test'}
        security_manager.login_time = datetime.now() - timedelta(minutes=30)  # 30 min ago

        # ACT: Verificar validez de sesión
        resultado = security_manager.is_session_valid()

        # ASSERT: Verificar que la sesión es válida
        assert resultado is True

    def test_has_permission_con_usuario_admin_retorna_true_para_cualquier_permiso(self):
        """
        Test que valida que los administradores tienen todos los permisos.

        Verifica que:
        - Los usuarios ADMIN pueden acceder a cualquier funcionalidad
        - El sistema de permisos respeta la jerarquía de roles
        """
        # ARRANGE: Usuario administrador
        from rexus.core.security import SecurityManager

        security_manager = SecurityManager()
        security_manager.current_user = {'username': 'admin'}
        security_manager.current_role = 'ADMIN'

        # ACT & ASSERT: Verificar permisos variados
        assert security_manager.has_permission('CREATE_USER') is True
        assert security_manager.has_permission('DELETE_USER') is True
        assert security_manager.has_permission('VIEW_REPORTS') is True
        assert security_manager.has_permission('MANAGE_SYSTEM') is True


class TestAuthManagerIntegration:
    """
    Tests de integración para AuthManager con otros componentes del sistema.

    Verifica la interacción correcta entre autenticación y otros módulos.
    """

    def test_flujo_completo_login_logout_actualiza_estado_correctamente(self, mock_db_connection, sample_user_data):
        """
        Test de integración del flujo completo de autenticación.

        Verifica que:
        - Login -> estado autenticado
        - Operaciones permitidas durante sesión
        - Logout -> estado no autenticado
        """
        # ARRANGE: Sistema completo
        from rexus.core.auth import AuthManager, get_current_user, clear_current_user

        # Configurar respuesta de DB
        mock_db_connection.execute_query.return_value = [(
            sample_user_data['id'],
            sample_user_data['username'],
            'hashed_password',
            sample_user_data['rol'],
            'Activo',
            sample_user_data['nombre'],
            sample_user_data['apellido'],
            sample_user_data['email']
        )]

        auth_manager = AuthManager(db_connection=mock_db_connection)

        # Limpiar estado global
        clear_current_user()

        with patch('rexus.utils.password_security.verify_password_secure', return_value=True):
            # ACT: Flujo completo

            # 1. Verificar estado inicial
            assert get_current_user() is None

            # 2. Login
            user_data = auth_manager.authenticate_user(sample_user_data['username'], 'password')
            assert user_data is not None

            # 3. Verificar estado autenticado
            assert auth_manager.current_user is not None
            assert auth_manager.session_active is True

            # 4. Logout
            auth_manager.logout()

            # 5. Verificar estado final
            assert auth_manager.current_user is None
            assert auth_manager.session_active is False

    def test_integracion_con_security_manager_mantiene_consistencia(self, mock_db_connection):
        """
        Test de integración entre AuthManager y SecurityManager.

        Verifica que:
        - Los datos se sincronizan correctamente
        - No hay inconsistencias entre sistemas
        - Los permisos se aplican correctamente
        """
        # ARRANGE: Ambos managers
        from rexus.core.security import SecurityManager

        with patch('rexus.core.auth.get_auth_manager') as mock_auth:
            mock_auth_instance = Mock()
            mock_auth_instance.authenticate_user.return_value = {
                'id': 1,
                'username': 'test_user',
                'role': 'ADMIN'
            }
            mock_auth.return_value = mock_auth_instance

            security_manager = SecurityManager()

            # ACT: Login a través de SecurityManager
            resultado = security_manager.login('test_user', 'password')

            # ASSERT: Verificar sincronización
            assert resultado is True
            assert security_manager.current_user['username'] == 'test_user'
            assert security_manager.current_role == 'ADMIN'


# Configuración específica para tests de autenticación
@pytest.fixture(scope="function")
def clean_auth_state():
    """Limpia el estado de autenticación antes y después de cada test."""
    from rexus.core.auth import clear_current_user, reset_auth_manager

    # Limpiar antes del test
    clear_current_user()
    reset_auth_manager()

    yield

    # Limpiar después del test
    clear_current_user()
    reset_auth_manager()


@pytest.fixture(scope="function")
def mock_password_verification():
    """Mock para verificación de contraseñas que siempre retorna True."""
    with patch('rexus.utils.password_security.verify_password_secure', return_value=True):
        yield
