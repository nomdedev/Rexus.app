"""
Tests para las utilidades de seguridad SQL del módulo utils.sql_seguro y utils.sanitizador_sql.
"""

import sys
import unittest
from pathlib import Path

# Agregar el directorio raíz al path para que se puedan importar los módulos
ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT_DIR))
sys.path.append(str(ROOT_DIR / "src"))

from src.utils.sql_security import (
    SQLSecurityError,
    SQLSecurityValidator,
    SecureSQLBuilder,
    validate_table_name,
    validate_column_name,
)
from src.utils.data_sanitizer import (
    DataSanitizer,
    data_sanitizer,
    sanitize_input,
)


class TestSqlSeguro(unittest.TestCase):
    """Clase para pruebas de sql_security.py"""

    def setUp(self):
        """Configurar el validador SQL para las pruebas."""
        self.validator = SQLSecurityValidator()
        self.builder = SecureSQLBuilder(self.validator)

    def test_validar_nombre_tabla(self):
        """Prueba validación de nombres de tablas."""
        # Comprobar que una tabla válida pasa la validación
        self.assertEqual(validate_table_name("usuarios"), "usuarios")

        # Comprobar que una tabla inválida lanza excepción
        with self.assertRaises(SQLSecurityError):
            validate_table_name("tabla_no_permitida")

        # Comprobar que una tabla con caracteres especiales lanza excepción
        with self.assertRaises(SQLSecurityError):
            validate_table_name("users; DROP TABLE users;")

    def test_validar_nombre_columna(self):
        """Prueba validación de nombres de columnas."""
        # Comprobar que una columna válida pasa la validación
        self.assertEqual(validate_column_name("id"), "id")
        self.assertEqual(validate_column_name("nombre_usuario"), "nombre_usuario")

        # Comprobar que una columna con caracteres especiales lanza excepción
        with self.assertRaises(SQLSecurityError):
            validate_column_name("id; DROP TABLE users;")

    def test_construir_select_seguro(self):
        """Prueba construcción de consultas SELECT seguras."""
        # SELECT simple
        query = self.builder.build_select_query("usuarios")
        self.assertEqual(query, "SELECT * FROM usuarios")

        # SELECT con columnas específicas
        query = self.builder.build_select_query("usuarios", ["id", "nombre", "email"])
        self.assertEqual(query, "SELECT id, nombre, email FROM usuarios")

        # SELECT con WHERE
        query = self.builder.build_select_query("usuarios", ["id", "nombre"], ["id = ?"])
        self.assertEqual(query, "SELECT id, nombre FROM usuarios WHERE id = ?")

        # Debe fallar con tabla no permitida
        with self.assertRaises(SQLSecurityError):
            self.builder.build_select_query("tabla_no_permitida")

    def test_construir_update_seguro(self):
        """Prueba construcción de consultas UPDATE seguras."""
        # UPDATE simple
        query = self.builder.build_update_query("usuarios", ["nombre = ?", "email = ?"], ["id = ?"])
        self.assertEqual(query, "UPDATE usuarios SET nombre = ?, email = ? WHERE id = ?")

        # Debe fallar con tabla no permitida
        with self.assertRaises(SQLSecurityError):
            self.builder.build_update_query("tabla_no_permitida", ["nombre = ?"], ["id = ?"])

    def test_construir_insert_seguro(self):
        """Prueba construcción de consultas INSERT seguras."""
        # INSERT simple
        query = self.builder.build_insert_query("usuarios", ["nombre", "email", "password_hash"])
        self.assertEqual(query, "INSERT INTO usuarios (nombre, email, password_hash) VALUES (?, ?, ?)")

        # Debe fallar con tabla no permitida
        with self.assertRaises(SQLSecurityError):
            self.builder.build_insert_query("tabla_no_permitida", ["nombre"])

    def test_validar_identificador_sql(self):
        """Prueba validación de identificadores SQL."""
        # Identificador válido
        self.assertEqual(self.validator.validate_sql_identifier("campo_valido"), "campo_valido")

        # Identificador con palabra reservada peligrosa
        with self.assertRaises(SQLSecurityError):
            self.validator.validate_sql_identifier("drop")

        # Identificador con caracteres especiales
        with self.assertRaises(SQLSecurityError):
            self.validator.validate_sql_identifier("campo; DROP")


class TestDataSanitizer(unittest.TestCase):
    """Clase para pruebas de data_sanitizer.py"""

    def setUp(self):
        """Configurar el sanitizador para las pruebas."""
        self.sanitizer = DataSanitizer()

    def test_sanitize_string(self):
        """Prueba sanitización de strings."""
        # String normal
        self.assertEqual(self.sanitizer.sanitize_string("texto normal"), "texto normal")

        # String con HTML
        result = self.sanitizer.sanitize_string("<script>alert('xss')</script>", allow_html=False)
        self.assertNotIn("<script>", result)

        # String vacío
        self.assertEqual(self.sanitizer.sanitize_string(""), "")

        # String muy largo
        long_text = "a" * 2000
        result = self.sanitizer.sanitize_string(long_text, max_length=100)
        self.assertEqual(len(result), 100)

    def test_sanitize_numeric(self):
        """Prueba sanitización de valores numéricos."""
        # Entero válido
        self.assertEqual(self.sanitizer.sanitize_numeric("123"), 123.0)

        # Float válido
        self.assertEqual(self.sanitizer.sanitize_numeric("123.45"), 123.45)

        # Valor inválido
        self.assertIsNone(self.sanitizer.sanitize_numeric("no-numero"))

        # Con límites
        result = self.sanitizer.sanitize_numeric(150, min_val=0, max_val=100)
        self.assertEqual(result, 100)

    def test_sanitize_email(self):
        """Prueba sanitización de emails."""
        # Email válido
        self.assertEqual(self.sanitizer.sanitize_email("user@example.com"), "user@example.com")

        # Email con caracteres peligrosos
        result = self.sanitizer.sanitize_email("user<script>@example.com")
        self.assertNotIn("<script>", result)

        # Email vacío
        self.assertEqual(self.sanitizer.sanitize_email(""), "")

    def test_sanitize_phone(self):
        """Prueba sanitización de teléfonos."""
        # Teléfono válido
        self.assertEqual(self.sanitizer.sanitize_phone("+1-234-567-8900"), "+1-234-567-8900")

        # Teléfono con caracteres no válidos
        result = self.sanitizer.sanitize_phone("+1<script>2345678900")
        self.assertNotIn("<script>", result)

        # Teléfono vacío
        self.assertEqual(self.sanitizer.sanitize_phone(""), "")

    def test_sanitize_filename(self):
        """Prueba sanitización de nombres de archivo."""
        # Nombre válido
        self.assertEqual(self.sanitizer.sanitize_filename("documento.pdf"), "documento.pdf")

        # Nombre con caracteres peligrosos
        result = self.sanitizer.sanitize_filename("archivo<script>.exe")
        self.assertNotIn("<script>", result)

        # Nombre vacío
        self.assertEqual(self.sanitizer.sanitize_filename(""), "untitled")

    def test_sanitize_form_data(self):
        """Prueba sanitización de datos de formulario."""
        form_data = {
            "nombre": "Juan Pérez",
            "email": "juan@example.com",
            "telefono": "+1-234-567-8900",
            "precio": "123.45"
        }
        
        result = self.sanitizer.sanitize_form_data(form_data)
        
        self.assertIn("nombre", result)
        self.assertEqual(result["email"], "juan@example.com")
        self.assertEqual(result["telefono"], "+1-234-567-8900")

    def test_sql_injection_detection(self):
        """Prueba detección de SQL injection."""
        # Texto con SQL injection
        malicious_input = "'; DROP TABLE users; --"
        result = self.sanitizer.sanitize_string(malicious_input)
        
        # Verificar que se detectó y bloqueó
        self.assertIn("[BLOCKED]", result)

    def test_convenience_functions(self):
        """Prueba funciones de conveniencia."""
        # Email
        result = sanitize_input("user@example.com", "email")
        self.assertEqual(result, "user@example.com")

        # Numérico
        result = sanitize_input("123.45", "numeric")
        self.assertEqual(result, 123.45)

        # Teléfono
        result = sanitize_input("+1-234-567-8900", "phone")
        self.assertEqual(result, "+1-234-567-8900")


if __name__ == "__main__":
    unittest.main()
