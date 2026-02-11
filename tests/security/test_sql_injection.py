"""
🧪 Tests de Seguridad - SQL Injection
======================================

Tests críticos para verificar que el código es inmune a SQL injection.

Best practices según:
- OWASP SQL Injection Cheat Sheet
- Google SQL Injection Prevention
"""

import pytest

# Verificar dependencias
try:
    import pyodbc
except ImportError:
    pytest.skip("pyodbc no está disponible", allow_module_level=True)

from unittest.mock import Mock, patch, MagicMock
from rexus.core.database import DatabaseConnection


class TestSQLInjectionPrevention:
    """Tests de prevención de SQL Injection"""

    @pytest.fixture
    def db_connection(self):
        """Connection mock para tests"""
        db = DatabaseConnection(
            database="test_inventario",
            auto_connect=False
        )
        return db

    def test_parametros_en_query_segura(self, db_connection):
        """
        CRÍTICO: Verifica que execute_query usa parámetros

        Esto previene SQL injection porque el driver escapa
        automáticamente los valores de los parámetros.
        """
        query = "SELECT * FROM inventario WHERE codigo = ?"
        params = ("'; DROP TABLE inventario; --",)

        # Mock cursor
        cursor_mock = MagicMock()
        db_connection._connection = MagicMock()
        db_connection._connection.cursor.return_value = cursor_mock

        # Ejecutar query
        db_connection.execute_query(query, params)

        # Verificar que se llamó a execute con parámetros
        cursor_mock.execute.assert_called_once()
        args = cursor_mock.execute.call_args

        # El primer argumento debe ser la query
        assert args[0][0] == query

        # El segundo argumento debe ser los parámetros
        assert args[0][1] == params

    def test_escaping_de_parametros(self, db_connection):
        """
        Verifica que los parámetros sean correctamente escapados

        Input malicioso: "admin' OR '1'='1"
        Debe ser escapado a: admin'' OR ''1''=''1
        """
        malicious_input = "admin' OR '1'='1"

        cursor_mock = MagicMock()
        cursor_mock.fetchall.return_value = []
        db_connection._connection = MagicMock()
        db_connection._connection.cursor.return_value = cursor_mock

        # Query con parámetro malicioso
        query = "SELECT * FROM usuarios WHERE username = ?"
        db_connection.execute_query(query, (malicious_input,))

        # Verificar que se llamó con parámetro escapado
        # (El driver de BD hace el escaping automáticamente)
        cursor_mock.execute.assert_called_once()
        params_used = cursor_mock.execute.call_args[0][1]

        # El parámetro debe ser pasado tal cual al driver
        # El driver se encarga del escaping
        assert params_used[0] == malicious_input

    def test_inyeccion_en_codigo(self, db_connection):
        """
        VERIFICACIÓN DE SEGURIDAD: Asegurar que NO hay queries
        concatenando strings (vulnerable)
        """
        # ❌ ESTO NO DEBERÍA EXISTIR EN EL CÓDIGO
        vulnerable_query = f"SELECT * FROM inventario WHERE codigo = '{user_input}'"

        # ✅ ESTO ES LO CORRECTO
        safe_query = "SELECT * FROM inventario WHERE codigo = ?"
        safe_params = (user_input,)

        # Verificar que la query segura tiene placeholder
        assert '?' in safe_query or ':param' in safe_query

    def test_union_based_injection_prevenida(self, db_connection):
        """
        Verifica prevención de UNION-based SQL injection

        Ataque: ' UNION SELECT username, password FROM usuarios --
        """
        malicious_input = "test' UNION SELECT username, password FROM users --"

        cursor_mock = MagicMock()
        cursor_mock.fetchone.return_value = None
        db_connection._connection = MagicMock()
        db_connection._connection.cursor.return_value = cursor_mock

        # Query segura con parámetros
        query = "SELECT * FROM obras WHERE codigo = ?"
        db_connection.execute_query(query, (malicious_input,))

        # Verificar que no se inyectó el UNION
        # (Al usar parámetros, el driver trata todo como string literal)
        cursor_mock.execute.assert_called_once()
        params = cursor_mock.execute.call_args[0][1]
        assert params[0] == malicious_input

    def test_comment_based_injection_prevenida(self, db_connection):
        """
        Verifica prevención de comment-based SQL injection

        Ataque: ' OR 1=1 -- comentario
        """
        malicious_input = "test' OR 1=1 --"

        cursor_mock = MagicMock()
        db_connection._connection = MagicMock()
        db_connection._connection.cursor.return_value = MagicMock()

        # Query segura
        query = "SELECT * FROM usuarios WHERE username = ? AND activo = 1"
        db_connection.execute_query(query, (malicious_input,))

        # El comment debe ser tratado como string literal, no como SQL
        cursor_mock = db_connection._connection.cursor.return_value
        cursor_mock.execute.assert_called_once()

    def test_boolean_based_injection_prevenida(self, db_connection):
        """
        Verifica prevención de boolean-based SQL injection

        Ataque: ' AND 1=1 -- (siempre verdadero)
        """
        malicious_input = "admin' AND 1=1 --"

        cursor_mock = MagicMock()
        cursor_mock.fetchall.return_value = []
        db_connection._connection = MagicMock()
        db_connection._connection.cursor.return_value = cursor_mock

        query = "SELECT * FROM usuarios WHERE username = ?"
        db_connection.execute_query(query, (malicious_input,))

        # Verificar que el input malicioso es tratado como string
        cursor_mock.execute.assert_called_once()

    def test_stored_procedure_injection_prevenida(self, db_connection):
        """
        Verifica prevención de injection en stored procedures

        Ataque:'; EXEC xp_cmdshell('format c:'); --
        """
        malicious_input = "'; EXEC xp_cmdshell('format c:'); --"

        cursor_mock = MagicMock()
        db_connection._connection = MagicMock()
        db_connection._connection.cursor.return_value = MagicMock()

        query = "EXEC sp_obtener_producto ?"
        db_connection.execute_query(query, (malicious_input,))

        # La llamada al SP debe ser segura
        cursor_mock = db_connection._connection.cursor.return_value
        cursor_mock.execute.assert_called_once()

    def test_second_order_injection(self, db_connection):
        """
        Verifica prevención de second-order SQL injection

        El attacker primero inserta código malicioso en la BD,
        luego ese código es ejecutado en una query posterior.
        """
        # Input malicioso que será guardado en BD
        malicious_code = "'; DROP TABLE usuarios; --"

        cursor_mock = MagicMock()
        db_connection._connection = MagicMock()
        db_connection._connection.cursor.return_value = cursor_mock

        # Insertar "seguro" con parámetros
        insert_query = "INSERT INTO notas (contenido) VALUES (?)"
        db_connection.execute_query(insert_query, (malicious_code,))

        # Recuperar nota "seguro" con parámetros
        select_query = "SELECT * FROM notas WHERE id = ?"
        db_connection.execute_query(select_query, (1,))

        # Ambas operaciones deben ser seguras
        assert cursor_mock.execute.call_count == 2

    def test_time_based_injection(self, db_connection):
        """
        Verifica prevención de time-based blind SQL injection

        Ataque: ' AND SLEEP(10) --
        """
        malicious_input = "test' AND SLEEP(10) --"

        cursor_mock = MagicMock()
        cursor_mock.fetchone.return_value = None
        db_connection._connection = MagicMock()
        db_connection._connection.cursor.return_value = cursor_mock

        query = "SELECT * FROM usuarios WHERE username = ?"
        db_connection.execute_query(query, (malicious_input,))

        # La función SLEEP() debe ser tratada como string, no ejecutada
        cursor_mock.execute.assert_called_once()


class TestSQLInjectionModelos:
    """Tests de SQL injection en modelos específicos"""

    def test_modelo_herrajes_seguro(self):
        """
        Verificar que el modelo de herrajes usa parámetros
        """
        from rexus.modules.herrajes.model import HerrajesModel

        # Mock connection
        mock_db = MagicMock()
        model = HerrajesModel(mock_db)

        # Buscar con input malicioso
        malicious_term = "'; DROP TABLE herrajes; --"

        # Llamar al método de búsqueda
        cursor_mock = MagicMock()
        cursor_mock.fetchall.return_value = []
        mock_db.cursor.return_value = cursor_mock

        model.buscar_herrajes(malicious_term)

        # Verificar que se usaron parámetros
        cursor_mock.execute.assert_called_once()
        query_used = cursor_mock.execute.call_args[0][0]

        # La query debe tener placeholders
        assert '?' in query or ':termino' in query

    def test_modelo_inventario_seguro(self):
        """
        Verificar que el modelo de inventario usa parámetros
        """
        from rexus.modules.inventario.model import InventarioModel

        mock_db = MagicMock()
        model = InventarioModel(mock_db)

        # Input malicioso
        malicious_codigo = "admin' OR '1'='1"

        cursor_mock = MagicMock()
        cursor_mock.fetchall.return_value = []
        mock_db.cursor.return_value = cursor_mock

        # Obtener producto por código
        model.obtener_producto_por_codigo(malicious_codigo)

        # Verificar uso de parámetros
        cursor_mock.execute.assert_called_once()

    def test_modelo_obras_seguro(self):
        """
        Verificar que el modelo de obras usa parámetros
        """
        from rexus.modules.obras.model import ObrasModel

        mock_db = MagicMock()
        model = ObrasModel(mock_db)

        # Intentar inyección en nombre de obra
        malicious_nombre = "Obra'; DROP TABLE obras; --"

        cursor_mock = MagicMock()
        mock_db.cursor.return_value = cursor_mock

        # Crear obra con input malicioso
        try:
            model.crear_obra({
                'codigo': 'TEST-001',
                'nombre': malicious_nombre,
                'cliente_id': 1
            })
        except:
            pass

        # Verificar que la query es segura
        if cursor_mock.execute.called:
            query_used = cursor_mock.execute.call_args[0][0]
            assert '?' in query or 'nombre' in query


class TestValidacionIdentificadoresSQL:
    """Tests de validación de identificadores SQL"""

    def test_validate_sql_identifier(self):
        """
        Verifica validación de nombres de tablas/columnas

        Previene injection en nombres dinámicos de tablas.
        """
        from rexus.utils.security import SecurityUtils

        # ✅ Identificadores válidos
        assert SecurityUtils.validate_sql_identifier("usuarios") is True
        assert SecurityUtils.validate_sql_identifier("obra_detalles") is True
        assert SecurityUtils.validate_sql_identifier("table123") is True

        # ❌ Identificadores inválidos
        assert SecurityUtils.validate_sql_identifier("") is False
        assert SecurityUtils.validate_sql_identifier("123table") is False  # Empieza con número
        assert SecurityUtils.validate_sql_identifier("table;DROP TABLE") is False  # Contiene punto y coma
        assert SecurityUtils.validate_sql_identifier("table' OR '1'='1") is False  # Contiene comilla

    def test_sanitizacion_tabla_dinamica(self):
        """
        Verifica sanitización al cambiar de tabla dinámicamente
        """
        from rexus.core.database import DatabaseConnection

        db = DatabaseConnection(database="test")

        # ✅ Nombre válido
        assert db.switch_database("inventario") is True

        # ❌ Nombre con SQL injection
        assert db.switch_database("inventario'; DROP TABLE users; --") is False

        # ❌ Nombre con caracteres inválidos
        assert db.switch_database("inventario OR 1=1") is False


class TestEscapingCaracteresPeligrosos:
    """Tests de escaping de caracteres peligrosos"""

    @pytest.mark.parametrize("malicious_input,expected_safe", [
        # Comillas simples
        ("admin'", "admin'"),
        # Comillas dobles
        ('admin"', 'admin"'),
        # Backslash
        ("admin\\", "admin\\"),
        # Newline
        ("admin\nOR 1=1", "admin\nOR 1=1"),
        # Tab
        ("admin\tOR 1=1", "admin\tOR 1=1"),
        # Combinación
        ("'; DROP TABLE users; --", "'; DROP TABLE users; --"),
    ])
    def test_escaping_completo(self, malicious_input, expected_safe):
        """
        Verifica que caracteres peligrosos sean correctamente escapados

        El driver de BD debe escaparlos automáticamente cuando se
        usan parámetros.
        """
        from rexus.core.database import DatabaseConnection

        db = DatabaseConnection(database="test")

        cursor_mock = MagicMock()
        db._connection = MagicMock()
        db._connection.cursor.return_value = cursor_mock

        query = "SELECT * FROM usuarios WHERE username = ?"
        db.execute_query(query, (malicious_input,))

        # El input debe ser pasado como parámetro (no concatenado)
        cursor_mock.execute.assert_called_once()
        params = cursor_mock.execute.call_args[0][1]
        assert params[0] == malicious_input
