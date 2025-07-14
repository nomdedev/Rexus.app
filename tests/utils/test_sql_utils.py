"""
Tests para las utilidades de seguridad SQL del módulo utils.sql_seguro y utils.sanitizador_sql.
"""

# Agregar el directorio raíz al path para que se puedan importar los módulos
ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT_DIR))

# Importar módulos a probar
    validar_nombre_tabla, validar_nombre_columna,
    construir_select_seguro, construir_update_seguro,
    construir_insert_seguro, construir_delete_seguro,
    TABLAS_PERMITIDAS, COLUMNAS_PERMITIDAS
)

    escapar_string_sql, sanitizar_numerico,
    sanitizar_fecha_sql, sanitizar_lista_valores,
    validar_consulta_sql, detectar_vulnerabilidades_consulta
)

# Importar excepciones
class TestSqlSeguro(unittest.TestCase):
    """Clase para pruebas de sql_seguro.py"""

    def test_validar_nombre_tabla(self):
        """Prueba validación de nombres de tablas."""
        # Comprobar que una tabla válida pasa la validación
import sys
from pathlib import Path

from core.exceptions import InputValidationError, SecurityError
from utils.sanitizador_sql import (
    "users",
    from,
    import,
    self.assertEqual,
    unittest,
    utils.sql_seguro,
    validar_nombre_tabla,
)

        # Comprobar que una tabla inválida lanza excepción
        with self.assertRaises(SecurityError):
            validar_nombre_tabla("tabla_no_permitida")

        # Comprobar que una tabla con caracteres especiales lanza excepción
        with self.assertRaises(SecurityError):
            validar_nombre_tabla("users; DROP TABLE users;")

    def test_validar_nombre_columna(self):
        """Prueba validación de nombres de columnas."""
        # Comprobar que una columna válida pasa la validación
        self.assertEqual(validar_nombre_columna("users", "id"), "id")

        # Comprobar que una columna inválida lanza excepción
        with self.assertRaises(SecurityError):
            validar_nombre_columna("users", "columna_no_permitida")

    def test_construir_select_seguro(self):
        """Prueba construcción de consultas SELECT seguras."""
        # SELECT simple
        query, _ = construir_select_seguro("users")
        self.assertEqual(query, "SELECT * FROM [users]")

        # SELECT con columnas específicas
        query, _ = construir_select_seguro("users", ["id", "nombre", "email"])
        self.assertEqual(query, "SELECT [id], [nombre], [email] FROM [users]")

        # SELECT con WHERE
        query, _ = construir_select_seguro("users", ["id", "nombre"], "id = ?")
        self.assertEqual(query, "SELECT [id], [nombre] FROM [users] WHERE id = ?")

        # Debe fallar con tabla no permitida
        with self.assertRaises(SecurityError):
            construir_select_seguro("tabla_no_permitida")

    def test_construir_update_seguro(self):
        """Prueba construcción de consultas UPDATE seguras."""
        # UPDATE simple
        query, _ = construir_update_seguro("users", ["nombre", "email"], "id = ?")
        self.assertEqual(query, "UPDATE [users] SET [nombre] = ?, [email] = ? WHERE id = ?")

        # Debe fallar con tabla no permitida
        with self.assertRaises(SecurityError):
            construir_update_seguro("tabla_no_permitida", ["nombre"])

    def test_construir_insert_seguro(self):
        """Prueba construcción de consultas INSERT seguras."""
        # INSERT simple
        query, _ = construir_insert_seguro("users", ["nombre", "email", "password_hash"])
        self.assertEqual(
            query,
            "INSERT INTO [users] ([nombre], [email], [password_hash]) VALUES (?, ?, ?)"
        )

        # Debe fallar con tabla no permitida
        with self.assertRaises(SecurityError):
            construir_insert_seguro("tabla_no_permitida", ["nombre"])

    def test_construir_delete_seguro(self):
        """Prueba construcción de consultas DELETE seguras."""
        # DELETE con WHERE
        query, _ = construir_delete_seguro("users", "id = ?")
        self.assertEqual(query, "DELETE FROM [users] WHERE id = ?")

        # DELETE sin WHERE debe fallar (protección)
        with self.assertRaises(SecurityError):
            construir_delete_seguro("users")

        # Debe fallar con tabla no permitida
        with self.assertRaises(SecurityError):
            construir_delete_seguro("tabla_no_permitida", "id = ?")


class TestSanitizadorSQL(unittest.TestCase):
    """Clase para pruebas de sanitizador_sql.py"""

    def test_escapar_string_sql(self):
        """Prueba función de escape para strings SQL."""
        # Comprobar escape de comillas simples
        self.assertEqual(escapar_string_sql("Let's test"), "Let''s test")

        # Comprobar con valor None
        self.assertIsNone(escapar_string_sql(None))

        # Comprobar con un valor numérico
        self.assertEqual(escapar_string_sql(123), "123")

    def test_sanitizar_numerico(self):
        """Prueba sanitización de valores numéricos."""
        # Entero válido
        self.assertEqual(sanitizar_numerico("123", "int"), 123)

        # Float válido
        self.assertEqual(sanitizar_numerico("123.45", "float"), 123.45)

        # Valor inválido
        with self.assertRaises(Exception):
            sanitizar_numerico("no-numero", "int")

    def test_sanitizar_fecha_sql(self):
        """Prueba sanitización de fechas para SQL."""
        # Fecha válida
        self.assertEqual(sanitizar_fecha_sql("2023-05-15"), "2023-05-15")

        # Fecha inválida
        with self.assertRaises(Exception):
            sanitizar_fecha_sql("15/05/2023")  # Formato incorrecto

    def test_sanitizar_lista_valores(self):
        """Prueba sanitización de listas de valores para SQL IN()."""
        # Lista de strings
        valores = ["uno", "dos's", "tres"]
        resultado = sanitizar_lista_valores(valores, "str")
        self.assertEqual(resultado, ["uno", "dos''s", "tres"])

        # Lista de enteros
        valores = ["1", 2, "3"]
        resultado = sanitizar_lista_valores(valores, "int")
        self.assertEqual(resultado, [1, 2, 3])

    def test_validar_consulta_sql(self):
        """Prueba validación de consultas SQL potencialmente peligrosas."""
        # Consulta segura
        self.assertTrue(validar_consulta_sql("SELECT id, nombre FROM users WHERE id = ?"))

        # Consulta peligrosa (SQL Injection) - debe lanzar SecurityError
        with self.assertRaises(SecurityError) as context:
            validar_consulta_sql("SELECT * FROM users WHERE id = 1 OR 1=1")
        self.assertIn("OR 1=1", str(context.exception))

        # Consulta peligrosa (DROP TABLE) - debe lanzar SecurityError
        with self.assertRaises(SecurityError) as context:
            validar_consulta_sql("DROP TABLE users")
        # Verificar que se detectó el patrón DROP
        self.assertTrue("DROP" in str(context.exception) or "drop" in str(context.exception).lower())

    def test_detectar_vulnerabilidades_consulta(self):
        """Prueba detección de vulnerabilidades en consultas SQL."""
        # Consulta segura
        vulnerabilidades = detectar_vulnerabilidades_consulta("SELECT id FROM users WHERE username = ?")
        self.assertEqual(len(vulnerabilidades), 0)

        # Consulta con SELECT *
        vulnerabilidades = detectar_vulnerabilidades_consulta("SELECT * FROM users")
        self.assertEqual(len(vulnerabilidades), 1)
        self.assertEqual(vulnerabilidades[0]['tipo'], 'buena_practica')

        # Consulta con UNION
        vulnerabilidades = detectar_vulnerabilidades_consulta(
            "SELECT id FROM users UNION SELECT password FROM users"
        )
        self.assertTrue(any(v['tipo'] == 'patron_peligroso' for v in vulnerabilidades))


if __name__ == '__main__':
    unittest.main()
