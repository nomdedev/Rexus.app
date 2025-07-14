"""
Tests para core.database
Cobertura: Conexiones, transacciones, DAL, edge cases, performance y concurrencia
"""
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

    BaseDatabaseConnection,
    DatabaseConnection,
    InventarioDatabaseConnection,
    UsuariosDatabaseConnection,
    AuditoriaDatabaseConnection,
    DataAccessLayer,
import os
import sys

import pyodbc
import pytest

from core.database import (
    MODULO_BASE_DATOS,
    MagicMock,
    Mock,
    call,
    from,
    get_connection_string,
    import,
    obtener_base_datos_para_modulo,
    patch,
    unittest.mock,
)


class TestGetConnectionString:
    """Tests para la función get_connection_string"""

    def test_get_connection_string_format(self):
        """Test que verifica el formato correcto del string de conexión"""
        # Arrange
        driver = "ODBC Driver 18 for SQL Server"
        database = "test_db"

        # Act
        with patch('core.database.DB_SERVER', 'test_server'), \
             patch('core.database.DB_USERNAME', 'test_user'), \
             patch('core.database.DB_PASSWORD', 'test_pass'):
            result = get_connection_string(driver, database)

        # Assert
        expected_parts = [
            "DRIVER={ODBC Driver 18 for SQL Server}",
            "SERVER=test_server",
            "DATABASE=test_db",
            "UID=test_user",
            "PWD=test_pass",
            "TrustServerCertificate=yes"
        ]
        for part in expected_parts:
            assert part in result

    def test_get_connection_string_with_special_characters(self):
        """Test que verifica manejo de caracteres especiales en credenciales"""
        # Arrange
        driver = "ODBC Driver 17 for SQL Server"
        database = "db-with-dash"

        # Act
        with patch('core.database.DB_SERVER', 'server.domain.com'), \
             patch('core.database.DB_USERNAME', 'user@domain'), \
             patch('core.database.DB_PASSWORD', 'pass;word=test'):
            result = get_connection_string(driver, database)

        # Assert
        assert "SERVER=server.domain.com" in result
        assert "UID=user@domain" in result
        assert "PWD=pass;word=test" in result


class TestBaseDatabaseConnection:
    """Tests unitarios para BaseDatabaseConnection"""

    @pytest.fixture
    def mock_pyodbc(self):
        """Mock para pyodbc"""
        with patch('core.database.pyodbc') as mock:
            mock.drivers.return_value = ["ODBC Driver 18 for SQL Server"]
            mock_conn = Mock()
            mock.connect.return_value = mock_conn
            yield mock

    @pytest.fixture
    def db_connection(self, mock_pyodbc):
        """Fixture que provee una instancia de BaseDatabaseConnection"""
        with patch('core.database.Logger'):
            return BaseDatabaseConnection("test_db")

    def test_init_sets_properties_correctly(self, db_connection):
        """Test que verifica la inicialización correcta"""
        # Assert
        assert db_connection.database == "test_db"
        assert db_connection.driver == "ODBC Driver 18 for SQL Server"
        assert db_connection.connection is None
        assert db_connection.timeout > 0
        assert db_connection.max_retries > 0

    def test_init_with_custom_timeout_and_retries(self, mock_pyodbc):
        """Test que verifica parámetros personalizados"""
        # Act
        with patch('core.database.Logger'):
            db = BaseDatabaseConnection("test_db", timeout=60, max_retries=5)

        # Assert
        assert db.timeout == 60
        assert db.max_retries == 5

    def test_detectar_driver_odbc_success(self):
        """Test que verifica detección exitosa de driver ODBC"""
        # Arrange
        with patch('core.database.pyodbc.drivers') as mock_drivers:
            mock_drivers.return_value = ["ODBC Driver 18 for SQL Server", "Other Driver"]

            # Act
            result = BaseDatabaseConnection.detectar_driver_odbc()

            # Assert
            assert result == "ODBC Driver 18 for SQL Server"

    def test_detectar_driver_odbc_fallback_to_17(self):
        """Test que verifica fallback a driver 17"""
        # Arrange
        with patch('core.database.pyodbc.drivers') as mock_drivers:
            mock_drivers.return_value = ["ODBC Driver 17 for SQL Server", "Other Driver"]

            # Act
            result = BaseDatabaseConnection.detectar_driver_odbc()

            # Assert
            assert result == "ODBC Driver 17 for SQL Server"

    def test_detectar_driver_odbc_no_compatible_driver(self):
        """Test que verifica error cuando no hay driver compatible"""
        # Arrange
        with patch('core.database.pyodbc.drivers') as mock_drivers:
            mock_drivers.return_value = ["Other Driver", "Another Driver"]

            # Act & Assert
            with pytest.raises(RuntimeError, match="No se encontró un controlador ODBC compatible"):
                BaseDatabaseConnection.detectar_driver_odbc()

    def test_conectar_success_first_attempt(self, db_connection, mock_pyodbc):
        """Test que verifica conexión exitosa en primer intento"""
        # Act
        db_connection.conectar()

        # Assert
        assert db_connection.connection is not None
        mock_pyodbc.connect.assert_called_once()

    def test_conectar_success_after_retries(self, db_connection, mock_pyodbc):
        """Test que verifica conexión exitosa después de reintentos"""
        # Arrange
        mock_pyodbc.connect.side_effect = [
            pyodbc.OperationalError("Connection failed"),
            pyodbc.OperationalError("Connection failed"),
            Mock()  # Éxito en el tercer intento
        ]

        # Act
        with patch('time.sleep'):  # Acelerar el test
            db_connection.conectar()

        # Assert
        assert db_connection.connection is not None
        assert mock_pyodbc.connect.call_count == 3

    def test_conectar_fails_after_max_retries(self, db_connection, mock_pyodbc):
        """Test que verifica fallo después de máximos reintentos"""
        # Arrange
        db_connection.max_retries = 2
        mock_pyodbc.connect.side_effect = pyodbc.OperationalError("Connection failed")

        # Act & Assert
        with patch('time.sleep'):  # Acelerar el test
            with pytest.raises(RuntimeError, match="No se pudo conectar a la base de datos"):
                db_connection.conectar()

        assert mock_pyodbc.connect.call_count == 2

    def test_cerrar_conexion_success(self, db_connection):
        """Test que verifica cierre correcto de conexión"""
        # Arrange
        mock_conn = Mock()
        db_connection.connection = mock_conn

        # Act
        db_connection.cerrar_conexion()

        # Assert
        mock_conn.close.assert_called_once()

    def test_cerrar_conexion_no_connection(self, db_connection):
        """Test que verifica comportamiento cuando no hay conexión"""
        # Arrange
        db_connection.connection = None

        # Act - No debe generar error
        db_connection.cerrar_conexion()

        # Assert - Método debe completarse sin errores
        assert True

    def test_ejecutar_query_select_success(self, db_connection):
        """Test que verifica ejecución exitosa de SELECT"""
        # Arrange
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [("row1",), ("row2",)]
        mock_conn.cursor.return_value = mock_cursor
        db_connection.connection = mock_conn

        # Act
        result = db_connection.ejecutar_query("SELECT * FROM test")

        # Assert
        assert result == [("row1",), ("row2",)]
        mock_cursor.execute.assert_called_once_with("SELECT * FROM test")
        mock_cursor.fetchall.assert_called_once()
        mock_conn.commit.assert_not_called()  # SELECT no hace commit

    def test_ejecutar_query_insert_success(self, db_connection):
        """Test que verifica ejecución exitosa de INSERT"""
        # Arrange
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        db_connection.connection = mock_conn

        # Act
        result = db_connection.ejecutar_query("INSERT INTO test VALUES (?)", ("value",))

        # Assert
        mock_cursor.execute.assert_called_once_with("INSERT INTO test VALUES (?)", ("value",))
        mock_conn.commit.assert_called_once()
        assert result is None  # INSERT no retorna datos

    def test_ejecutar_query_no_connection_error(self, db_connection):
        """Test que verifica error cuando no hay conexión"""
        # Arrange
        db_connection.connection = None

        # Act
        result = db_connection.ejecutar_query("SELECT * FROM test")

        # Assert
        assert result is None

    def test_ejecutar_query_operational_error(self, db_connection):
        """Test que verifica manejo de OperationalError"""
        # Arrange
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.execute.side_effect = pyodbc.OperationalError("Database error")
        mock_conn.cursor.return_value = mock_cursor
        db_connection.connection = mock_conn

        # Act
        result = db_connection.ejecutar_query("SELECT * FROM test")

        # Assert
        assert result is None

    def test_ejecutar_query_return_rowcount_success(self, db_connection):
        """Test que verifica ejecución con rowcount"""
        # Arrange
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.rowcount = 5
        mock_conn.cursor.return_value = mock_cursor
        db_connection.connection = mock_conn

        # Act
        result = db_connection.ejecutar_query_return_rowcount("UPDATE test SET value = ?", ("new_value",))

        # Assert
        assert result == 5
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()

    def test_ejecutar_query_return_rowcount_no_connection(self, db_connection, mock_pyodbc):
        """Test que verifica rowcount cuando no hay conexión activa"""
        # Arrange
        db_connection.connection = None
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.rowcount = 3
        mock_conn.cursor.return_value = mock_cursor
        mock_pyodbc.connect.return_value = mock_conn

        # Act
        result = db_connection.ejecutar_query_return_rowcount("UPDATE test SET value = ?", ("value",))

        # Assert
        assert result == 3

    def test_begin_transaction_success(self, db_connection):
        """Test que verifica inicio de transacción"""
        # Arrange
        mock_conn = Mock()
        db_connection.connection = mock_conn

        # Act
        db_connection.begin_transaction()

        # Assert
        assert mock_conn.autocommit is False

    def test_begin_transaction_no_connection(self, db_connection, mock_pyodbc):
        """Test que verifica inicio de transacción sin conexión previa"""
        # Arrange
        db_connection.connection = None
        mock_conn = Mock()
        mock_pyodbc.connect.return_value = mock_conn

        # Act
        db_connection.begin_transaction()

        # Assert
        mock_pyodbc.connect.assert_called_once()
        assert mock_conn.autocommit is False

    def test_commit_success(self, db_connection):
        """Test que verifica commit exitoso"""
        # Arrange
        mock_conn = Mock()
        db_connection.connection = mock_conn

        # Act
        db_connection.commit()

        # Assert
        mock_conn.commit.assert_called_once()
        assert mock_conn.autocommit is True

    def test_rollback_success(self, db_connection):
        """Test que verifica rollback exitoso"""
        # Arrange
        mock_conn = Mock()
        db_connection.connection = mock_conn

        # Act
        db_connection.rollback()

        # Assert
        mock_conn.rollback.assert_called_once()
        assert mock_conn.autocommit is True

    def test_transaction_context_manager_success(self, db_connection):
        """Test que verifica el context manager de transacciones exitosas"""
        # Arrange
        mock_conn = Mock()
        db_connection.connection = mock_conn

        # Act
        with db_connection.transaction():
            pass  # Transacción exitosa

        # Assert
        mock_conn.commit.assert_called_once()
        assert mock_conn.autocommit is True

    def test_transaction_context_manager_with_exception(self, db_connection):
        """Test que verifica rollback automático en caso de excepción"""
        # Arrange
        mock_conn = Mock()
        db_connection.connection = mock_conn

        # Act & Assert
        with pytest.raises(ValueError):
            with db_connection.transaction():
                raise ValueError("Test exception")

        # Assert
        mock_conn.rollback.assert_called_once()
        mock_conn.commit.assert_not_called()

    def test_transaction_context_manager_with_timeout_retries(self, db_connection):
        """Test que verifica reintentos en transacciones con timeout"""
        # Arrange
        mock_conn = Mock()
        mock_conn.commit.side_effect = [
            pyodbc.OperationalError("Timeout"),
            None  # Éxito en segundo intento
        ]
        db_connection.connection = mock_conn

        # Act
        with patch('time.time', side_effect=[0, 1, 2]):  # Simular tiempo
            with patch('time.sleep'):  # Acelerar el test
                with db_connection.transaction(timeout=30, retries=2):
                    pass

        # Assert
        assert mock_conn.commit.call_count == 2


class TestSpecializedDatabaseConnections:
    """Tests para las clases especializadas de conexión de base de datos"""

    @pytest.fixture
    def mock_pyodbc(self):
        with patch('core.database.pyodbc') as mock:
            mock.drivers.return_value = ["ODBC Driver 18 for SQL Server"]
            yield mock

    def test_inventario_database_connection_init(self, mock_pyodbc):
        """Test de inicialización de InventarioDatabaseConnection"""
        with patch('core.database.Logger'):
            db = InventarioDatabaseConnection()
            assert db.database == "inventario"

    def test_usuarios_database_connection_init(self, mock_pyodbc):
        """Test de inicialización de UsuariosDatabaseConnection"""
        with patch('core.database.Logger'):
            db = UsuariosDatabaseConnection()
            assert db.database == "users"

    def test_auditoria_database_connection_init(self, mock_pyodbc):
        """Test de inicialización de AuditoriaDatabaseConnection"""
        with patch('core.database.Logger'):
            db = AuditoriaDatabaseConnection()
            assert db.database == "auditoria"


class TestDatabaseConnection:
    """Tests para la clase DatabaseConnection (legacy)"""

    @pytest.fixture
    def mock_pyodbc(self):
        with patch('core.database.pyodbc') as mock:
            mock.drivers.return_value = ["ODBC Driver 18 for SQL Server"]
            yield mock

    def test_init_properties(self, mock_pyodbc):
        """Test de inicialización de DatabaseConnection"""
        db = DatabaseConnection()
        assert db.database is None
        assert db.driver == "ODBC Driver 18 for SQL Server"

    def test_conectar_a_base_valid_database(self, mock_pyodbc):
        """Test de conexión a base válida"""
        db = DatabaseConnection()
        db.conectar_a_base("inventario")
        assert db.database == "inventario"

    def test_conectar_a_base_invalid_database(self, mock_pyodbc):
        """Test de error con base inválida"""
        db = DatabaseConnection()
        with pytest.raises(ValueError, match="La base de datos 'invalid' no es válida"):
            db.conectar_a_base("invalid")

    def test_listar_bases_de_datos_success(self, mock_pyodbc):
        """Test de listado exitoso de bases de datos"""
        # Arrange
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [("db1",), ("db2",), ("db3",)]
        mock_conn.cursor.return_value = mock_cursor
        mock_pyodbc.connect.return_value.__enter__.return_value = mock_conn

        # Act
        result = DatabaseConnection.listar_bases_de_datos()

        # Assert
        assert result == ["db1", "db2", "db3"]
        mock_cursor.execute.assert_called_once_with("SELECT name FROM sys.databases WHERE state = 0;")


class TestModuloDatabaseMapping:
    """Tests para el mapeo de módulos a bases de datos"""

    def test_obtener_base_datos_para_modulo_existing(self):
        """Test de mapeo para módulos existentes"""
        assert obtener_base_datos_para_modulo("auditoria") == "auditoria"
        assert obtener_base_datos_para_modulo("inventario") == "inventario"
        assert obtener_base_datos_para_modulo("usuarios") == "users"

    def test_obtener_base_datos_para_modulo_nonexisting(self):
        """Test de mapeo para módulos no existentes"""
        assert obtener_base_datos_para_modulo("nonexistent") is None
        assert obtener_base_datos_para_modulo("") is None
        assert obtener_base_datos_para_modulo(None) is None


class TestDataAccessLayer:
    """Tests unitarios para DataAccessLayer"""

    @pytest.fixture
    def mock_db(self):
        """Mock de base de datos para DAL"""
        mock = Mock()
        mock.ejecutar_query.return_value = []
        assert mock is not None
    @pytest.fixture
    def dal(self, mock_db):
        """Fixture que provee una instancia de DataAccessLayer"""
        return DataAccessLayer(mock_db)

    def test_get_pedidos_por_estado(self, dal, mock_db):
        """Test de obtención de pedidos por estado"""
        # Arrange
        mock_db.ejecutar_query.return_value = [("pedido1", "activo"), ("pedido2", "activo")]

        # Act
        result = dal.get_pedidos_por_estado("activo")

        # Assert
        assert result == [("pedido1", "activo"), ("pedido2", "activo")]
        mock_db.ejecutar_query.assert_called_once_with(
            "SELECT * FROM pedidos WHERE estado = ?", ("activo",)
        )

    def test_insertar_material(self, dal, mock_db):
        """Test de inserción de material"""
        # Arrange
        material = ("Material Test", 100, "Proveedor Test")

        # Act
        dal.insertar_material(material)

        # Assert
        mock_db.ejecutar_query.assert_called_once_with(
            "INSERT INTO materiales (nombre, cantidad, proveedor) VALUES (?, ?, ?)",
            material
        )

    def test_get_usuarios_por_rol(self, dal, mock_db):
        """Test de obtención de usuarios por rol"""
        # Arrange
        mock_db.ejecutar_query.return_value = [("user1", "TEST_USER"), ("user2", "TEST_USER")]

        # Act
        result = dal.get_usuarios_por_rol("TEST_USER")

        # Assert
        assert result == [("user1", "TEST_USER"), ("user2", "TEST_USER")]
        mock_db.ejecutar_query.assert_called_once_with(
            "SELECT * FROM usuarios WHERE rol = ?", ("TEST_USER",)
        )

    def test_verificar_concurrencia_no_conflict(self, dal, mock_db):
        """Test de verificación de concurrencia sin conflicto"""
        # Arrange
        fecha_actualizacion = "2024-01-01T12:00:00"
        mock_db.ejecutar_query.return_value = [(fecha_actualizacion,)]

        # Act
        result = dal.verificar_concurrencia("test_table", 1, fecha_actualizacion)

        # Assert
        assert result is True
        mock_db.ejecutar_query.assert_called_once_with(
            "SELECT fecha_actualizacion FROM test_table WHERE id = ?", (1,)
        )

    def test_verificar_concurrencia_with_conflict(self, dal, mock_db):
        """Test de verificación de concurrencia con conflicto"""
        # Arrange
        fecha_original = "2024-01-01T12:00:00"
        fecha_actual = "2024-01-01T13:00:00"
        mock_db.ejecutar_query.return_value = [(fecha_actual,)]

        # Act
        result = dal.verificar_concurrencia("test_table", 1, fecha_original)

        # Assert
        assert result is False

    def test_verificar_concurrencia_no_record(self, dal, mock_db):
        """Test de verificación de concurrencia sin registro"""
        # Arrange
        mock_db.ejecutar_query.return_value = []

        # Act
        result = dal.verificar_concurrencia("test_table", 1, "2024-01-01T12:00:00")

        # Assert
        assert result is True  # Si no hay registro, se considera válido

    def test_actualizar_registro_success(self, dal, mock_db):
        """Test de actualización exitosa de registro"""
        # Arrange
        fecha_actualizacion = "2024-01-01T12:00:00"
        mock_db.ejecutar_query.return_value = [(fecha_actualizacion,)]
        datos = {"campo1": "valor1", "campo2": "valor2"}

        # Act
        with patch('core.database.datetime') as mock_datetime:
            mock_datetime.now.return_value.isoformat.return_value = "2024-01-01T13:00:00"
            dal.actualizar_registro("test_table", 1, datos, fecha_actualizacion)

        # Assert
        assert mock_db.ejecutar_query.call_count == 2  # Verificar + actualizar

    def test_actualizar_registro_concurrency_conflict(self, dal, mock_db):
        """Test de error por conflicto de concurrencia"""
        # Arrange
        fecha_original = "2024-01-01T12:00:00"
        fecha_actual = "2024-01-01T13:00:00"
        mock_db.ejecutar_query.return_value = [(fecha_actual,)]
        datos = {"campo1": "valor1"}

        # Act & Assert
        with pytest.raises(RuntimeError, match="Conflicto de concurrencia detectado"):
            dal.actualizar_registro("test_table", 1, datos, fecha_original)

    def test_verificar_integridad_with_problems(self, dal, mock_db):
        """Test de verificación de integridad con problemas"""
        # Arrange
        mock_db.ejecutar_query.side_effect = [
            [(1,), (2,)],  # 2 obras sin cliente
            [(1,)],        # 1 pedido sin productos
            [(1,), (2,), (3,)]  # 3 productos sin código
        ]

        # Act
        problemas = dal.verificar_integridad()

        # Assert
        assert len(problemas) == 3
        assert "Obras sin cliente: 2" in problemas
        assert "Pedidos sin productos: 1" in problemas
        assert "Productos sin código válido: 3" in problemas

    def test_verificar_integridad_no_problems(self, dal, mock_db):
        """Test de verificación de integridad sin problemas"""
        # Arrange
        mock_db.ejecutar_query.return_value = []  # Sin problemas

        # Act
        problemas = dal.verificar_integridad()

        # Assert
        assert problemas == []

    def test_registrar_auditoria(self, dal, mock_db):
        """Test de registro de auditoría"""
        # Act
        with patch('core.database.datetime') as mock_datetime:
            mock_datetime.now.return_value.isoformat.return_value = "2024-01-01T12:00:00"
            dal.registrar_auditoria("usuario_test", "accion_test", "detalles_test")

        # Assert
        mock_db.ejecutar_query.assert_called_once()
        call_args = mock_db.ejecutar_query.call_args
        assert "INSERT INTO auditoria" in call_args[0][0]
        assert call_args[0][1] == ("usuario_test", "accion_test", "detalles_test", "2024-01-01T12:00:00")

    def test_registrar_login_fallido(self, dal, mock_db):
        """Test de registro de login fallido"""
        # Act
        dal.registrar_login_fallido("192.168.1.1", "usuario", "2024-01-01T12:00:00", "fallido")

        # Assert
        mock_db.ejecutar_query.assert_called_once()
        call_args = mock_db.ejecutar_query.call_args
        assert "INSERT INTO login_fallidos" in call_args[0][0]
        assert call_args[0][1] == ("192.168.1.1", "usuario", "2024-01-01T12:00:00", "fallido")

    def test_actualizar_configuracion(self, dal, mock_db):
        """Test de actualización de configuración"""
        # Act
        dal.actualizar_configuracion("clave_test", "valor_test")

        # Assert
        mock_db.ejecutar_query.assert_called_once_with(
            "UPDATE configuracion SET valor = ? WHERE clave = ?",
            ("valor_test", "clave_test")
        )

    def test_obtener_metricas(self, dal, mock_db):
        """Test de obtención de métricas"""
        # Arrange
        mock_db.ejecutar_query.side_effect = [
            [(100,)],  # total_usuarios
            [(50,)],   # empresas_activas
            [(25,)],   # sesiones_activas
            [(1000,)]  # logs_sistema
        ]

        # Act
        metricas = dal.obtener_metricas()

        # Assert
        expected_metricas = {
            "total_usuarios": 100,
            "empresas_activas": 50,
            "sesiones_activas": 25,
            "logs_sistema": 1000
        }
        assert metricas == expected_metricas

    def test_obtener_actividad_reciente(self, dal, mock_db):
        """Test de obtención de actividad reciente"""
        # Arrange
        actividad = [
            ("usuario1", "login", "2024-01-01T12:00:00"),
            ("usuario2", "logout", "2024-01-01T11:00:00")
        ]
        mock_db.ejecutar_query.return_value = actividad

        # Act
        result = dal.obtener_actividad_reciente()

        # Assert
        assert result == actividad
        mock_db.ejecutar_query.assert_called_once()
        call_args = mock_db.ejecutar_query.call_args[0][0]
        assert "ORDER BY fecha DESC" in call_args
        assert "OFFSET 0 ROWS FETCH NEXT 10 ROWS ONLY" in call_args

    def test_sincronizar_datos_success(self, dal):
        """Test de sincronización exitosa"""
        # Act
        result = dal.sincronizar_datos()

        # Assert
        assert result == "Sincronización completada exitosamente."

    def test_detectar_plugins_success(self):
        """Test de detección exitosa de plugins"""
        # Arrange
        with patch('os.path.exists') as mock_exists, \
             patch('os.listdir') as mock_listdir, \
             patch('os.path.isdir') as mock_isdir:

            mock_exists.return_value = True
            mock_listdir.side_effect = [
                ["plugin1", "plugin2", "not_plugin"],  # Directorio modules
                ["controller.py", "view.py", "model.py"],  # plugin1
                ["controller.py", "view.py"],  # plugin2
                ["other_file.py"]  # not_plugin
            ]
            mock_isdir.return_value = True

            # Act
            plugins = DataAccessLayer.detectar_plugins()

            # Assert
            assert "plugin1" in plugins
            assert "plugin2" in plugins
            assert "not_plugin" not in plugins

    def test_detectar_plugins_path_not_exists(self):
        """Test de detección cuando no existe el directorio"""
        # Arrange
        with patch('os.path.exists') as mock_exists:
            mock_exists.return_value = False

            # Act
            plugins = DataAccessLayer.detectar_plugins()

            # Assert
            assert plugins == []

    def test_obtener_productos(self, dal, mock_db):
        """Test de obtención de productos"""
        # Arrange
        with patch('core.database.get_connection_string') as mock_conn_str, \
             patch('core.database.pyodbc.connect') as mock_connect:

            mock_conn_str.return_value = "test_connection_string"
            mock_conn = Mock()
            mock_cursor = Mock()

            # Simular datos y columnas
            mock_cursor.fetchall.return_value = [
                (1, "Producto1", 100),
                (2, "Producto2", 200)
            ]
            mock_cursor.description = [
                ("id", None), ("nombre", None), ("precio", None)
            ]
            mock_conn.cursor.return_value = mock_cursor
            mock_connect.return_value.__enter__.return_value = mock_conn

            # Act
            result = dal.obtener_productos()

            # Assert
            expected = [
                {"id": 1, "nombre": "Producto1", "precio": 100},
                {"id": 2, "nombre": "Producto2", "precio": 200}
            ]
            assert result == expected


class TestDatabaseConnectionEdgeCases:
    """Tests para casos edge y situaciones especiales"""

    def test_multiple_connections_independence(self):
        """Test que verifica que múltiples conexiones son independientes"""
        with patch('core.database.pyodbc') as mock_pyodbc, \
             patch('core.database.Logger'):

            mock_pyodbc.drivers.return_value = ["ODBC Driver 18 for SQL Server"]

            # Act
            db1 = BaseDatabaseConnection("db1")
            db2 = BaseDatabaseConnection("db2")

            # Assert
            assert db1.database != db2.database
            assert db1 is not db2

    def test_connection_timeout_handling(self):
        """Test del manejo de timeouts de conexión"""
        with patch('core.database.pyodbc') as mock_pyodbc, \
             patch('core.database.Logger'), \
             patch('time.sleep'):

            mock_pyodbc.drivers.return_value = ["ODBC Driver 18 for SQL Server"]
            mock_pyodbc.connect.side_effect = [
                pyodbc.OperationalError("Timeout"),
                Mock()  # Éxito después del timeout
            ]

            db = BaseDatabaseConnection("test_db", max_retries=2)
            db.conectar()

            assert db.connection is not None

    def test_special_characters_in_query(self):
        """Test de queries con caracteres especiales"""
        with patch('core.database.pyodbc') as mock_pyodbc, \
             patch('core.database.Logger'):

            mock_pyodbc.drivers.return_value = ["ODBC Driver 18 for SQL Server"]
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_conn.cursor.return_value = mock_cursor

            db = BaseDatabaseConnection("test_db")
            db.connection = mock_conn

            # Query con caracteres especiales
            query = "SELECT * FROM test WHERE name LIKE '%test%' AND value = 'it''s working'"
            db.ejecutar_query(query)

            mock_cursor.execute.assert_called_once_with(query)

    def test_large_result_set_handling(self):
        """Test del manejo de conjuntos de resultados grandes"""
        with patch('core.database.pyodbc') as mock_pyodbc, \
             patch('core.database.Logger'):

            mock_pyodbc.drivers.return_value = ["ODBC Driver 18 for SQL Server"]
            mock_conn = Mock()
            mock_cursor = Mock()

            # Simular resultado grande
            large_result = [(f"row_{i}",) for i in range(10000)]
            mock_cursor.fetchall.return_value = large_result
            mock_conn.cursor.return_value = mock_cursor

            db = BaseDatabaseConnection("test_db")
            db.connection = mock_conn

            result = db.ejecutar_query("SELECT * FROM large_table")

            assert len(result) == 10000
            assert result[0] == ("row_0",)
            assert result[-1] == ("row_9999",)
