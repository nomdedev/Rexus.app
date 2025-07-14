"""
Tests para el validador de datos HTTP y formularios del módulo utils.validador_http.
"""

# Agregar el directorio raíz al path para que se puedan importar los módulos
ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT_DIR))

# Importar módulos a probar
    validar_patron, validar_longitud, validar_rango_numerico,
    validar_fecha, validar_opciones, detectar_xss,
    sanitizar_html, sanitizar_url, sanitizar_json,
    FormValidator
)

# Importar excepciones
try:
except ImportError:
    # Definiciones alternativas si no están disponibles
    class InputValidationError(Exception):
        def __init__(self, mensaje, campo=None, valor=None):
            super().__init__(mensaje)
            self.campo = campo
import sys
from datetime import datetime
from pathlib import Path

from core.exceptions import InputValidationError, SecurityError
from utils.validador_http import (
    Exception,
    SecurityError,
    :,
    =,
    __init__,
    class,
    codigo=None,
    def,
    detalles=None,
    import,
    mensaje,
    self,
    self.valor,
    unittest,
    valor,
)

            super().__init__(mensaje)
            self.codigo = codigo
            self.detalles = detalles

class TestValidadorHTTP(unittest.TestCase):
    """Pruebas unitarias para validador_http.py"""

    def test_validar_patron(self):
        """Prueba validación de patrones predefinidos."""
        # Email válido
        self.assertTrue(validar_patron("usuario@ejemplo.com", "email"))

        # Email inválido
        with self.assertRaises(InputValidationError):
            validar_patron("usuario@", "email")

        # Teléfono válido
        self.assertTrue(validar_patron("+34 612 345 678", "telefono"))

        # Teléfono inválido
        with self.assertRaises(InputValidationError):
            validar_patron("abc123", "telefono")

        # Código postal válido
        self.assertTrue(validar_patron("28001", "codigo_postal"))

        # Código postal inválido
        with self.assertRaises(InputValidationError):
            validar_patron("123", "codigo_postal")

    def test_validar_longitud(self):
        """Prueba validación de longitud."""
        # Longitud correcta
        self.assertTrue(validar_longitud("test", min_len=2, max_len=10))

        # Demasiado corto
        with self.assertRaises(InputValidationError):
            validar_longitud("a", min_len=2)

        # Demasiado largo
        with self.assertRaises(InputValidationError):
            validar_longitud("texto muy largo", max_len=10)

        # Lista con longitud válida
        self.assertTrue(validar_longitud([1, 2, 3], min_len=1, max_len=5))

    def test_validar_rango_numerico(self):
        """Prueba validación de rangos numéricos."""
        # Entero dentro de rango
        self.assertEqual(validar_rango_numerico(5, minimo=0, maximo=10, tipo='int'), 5)

        # Float dentro de rango
        self.assertEqual(validar_rango_numerico(5.5, minimo=0, maximo=10), 5.5)

        # Conversión de string a número
        self.assertEqual(validar_rango_numerico("5.5", minimo=0, maximo=10), 5.5)

        # Fuera de rango (bajo)
        with self.assertRaises(InputValidationError):
            validar_rango_numerico(-1, minimo=0)

        # Fuera de rango (alto)
        with self.assertRaises(InputValidationError):
            validar_rango_numerico(11, minimo=0, maximo=10)

        # Valor no numérico
        with self.assertRaises(InputValidationError):
            validar_rango_numerico("abc", tipo='int')

    def test_validar_fecha(self):
        """Prueba validación de fechas."""
        # Fecha válida
        self.assertEqual(
            validar_fecha("2023-05-15"),
            datetime(2023, 5, 15)
        )

        # Fecha con formato personalizado
        self.assertEqual(
            validar_fecha("15/05/2023", formato='%d/%m/%Y'),
            datetime(2023, 5, 15)
        )

        # Fecha en rango válido
        self.assertEqual(
            validar_fecha(
                "2023-05-15",
                min_fecha="2023-01-01",
                max_fecha="2023-12-31"
            ),
            datetime(2023, 5, 15)
        )

        # Fecha fuera de rango (anterior)
        with self.assertRaises(InputValidationError):
            validar_fecha("2022-12-31", min_fecha="2023-01-01")

        # Fecha fuera de rango (posterior)
        with self.assertRaises(InputValidationError):
            validar_fecha("2024-01-01", max_fecha="2023-12-31")

        # Formato inválido
        with self.assertRaises(InputValidationError):
            validar_fecha("15-05-2023")  # Formato correcto es YYYY-MM-DD

    def test_validar_opciones(self):
        """Prueba validación de opciones permitidas."""
        # Opción válida
        self.assertEqual(validar_opciones("A", ["A", "B", "C"]), "A")

        # Opción inválida
        with self.assertRaises(InputValidationError):
            validar_opciones("D", ["A", "B", "C"])

    def test_detectar_xss(self):
        """Prueba detección de ataques XSS."""
        # Texto seguro
        self.assertTrue(detectar_xss("Texto normal sin scripts"))

        # Script malicioso
        with self.assertRaises(SecurityError):
            detectar_xss("<script>alert('XSS')</script>")

        # Evento JavaScript
        with self.assertRaises(SecurityError):
            detectar_xss("<img src='x' onerror='alert(1)'>")

        # URL JavaScript
        with self.assertRaises(SecurityError):
            detectar_xss("javascript:alert(1)")

    def test_sanitizar_html(self):
        """Prueba sanitización de HTML."""
        # Texto normal
        self.assertEqual(sanitizar_html("Texto normal"), "Texto normal")

        # HTML con tags
        self.assertEqual(
            sanitizar_html("<script>alert('XSS')</script>"),
            "&lt;script&gt;alert(&#x27;XSS&#x27;)&lt;/script&gt;"
        )

        # Caracteres especiales
        self.assertEqual(
            sanitizar_html("< > & ' \""),
            "&lt; &gt; &amp; &#x27; &quot;"
        )

    def test_sanitizar_url(self):
        """Prueba sanitización de URLs."""
        # URL segura (el query param se codifica por seguridad)
        resultado = sanitizar_url("https://ejemplo.com/ruta?param=valor")
        self.assertEqual(resultado, "https://ejemplo.com/ruta?param%3Dvalor")

        # URL con espacios y caracteres especiales
        resultado2 = sanitizar_url("https://ejemplo.com/mi página?q=texto con espacios")
        self.assertEqual(
            resultado2,
            "https://ejemplo.com/mi%20p%C3%A1gina?q%3Dtexto+con+espacios"
        )

        # URL con esquema no permitido
        with self.assertRaises(SecurityError):
            sanitizar_url("javascript:alert(1)")

    def test_sanitizar_json(self):
        """Prueba sanitización de JSON."""
        # JSON como string
        json_str = '{"nombre": "<script>alert(1)</script>", "valor": 123}'
        resultado = sanitizar_json(json_str)
        self.assertEqual(
            resultado["nombre"],
            "&lt;script&gt;alert(1)&lt;/script&gt;"
        )
        self.assertEqual(resultado["valor"], 123)

        # JSON como diccionario
        json_dict = {"html": "<img src=x onerror=alert(1)>"}
        resultado = sanitizar_json(json_dict)
        self.assertEqual(
            resultado["html"],
            "&lt;img src=x onerror=alert(1)&gt;"
        )

        # JSON inválido
        with self.assertRaises(InputValidationError):
            sanitizar_json("{nombre: valor}")


class TestFormValidator(unittest.TestCase):
    """Pruebas unitarias para la clase FormValidator."""

    def setUp(self):
        """Configuración inicial para las pruebas."""
        self.validator = FormValidator()

    def test_validar_campo(self):
        """Prueba validación de campo individual."""
        # Validación de email
        campo_valido = self.validator.validar_campo(
            "email",
            "usuario@ejemplo.com",
            [{'funcion': 'validar_patron', 'params': {'tipo': 'email'}}]
        )
        self.assertTrue(campo_valido)
        # Verificar que el valor se guardó en datos_limpios
        self.assertIn("email", self.validator.datos_limpios)
        self.assertEqual(self.validator.datos_limpios["email"], "usuario@ejemplo.com")

        # Validación que debe fallar (email incorrecto)
        campo_invalido = self.validator.validar_campo(
            "email",
            "usuario@",
            [{'funcion': 'validar_patron', 'params': {'tipo': 'email'}}]
        )
        self.assertFalse(campo_invalido)
        self.assertIn("email", self.validator.errores)

    def test_validar_formulario(self):
        """Prueba validación de formulario completo."""
        # Reglas de validación
        reglas = {
            'nombre': [
                {'funcion': 'validar_longitud', 'params': {'min_len': 2, 'max_len': 50}},
                {'funcion': 'validar_patron', 'params': {'tipo': 'nombre'}}
            ],
            'email': [
                {'funcion': 'validar_patron', 'params': {'tipo': 'email'}}
            ],
            'edad': [
                {'funcion': 'validar_rango_numerico', 'params': {'minimo': 18, 'maximo': 120, 'tipo': 'int'}}
            ]
        }

        # Datos válidos
        datos_validos = {
            'nombre': 'María García',
            'email': 'maria@ejemplo.com',
            'edad': 25
        }

        es_valido = self.validator.validar_formulario(datos_validos, reglas)
        self.assertTrue(es_valido)
        self.assertEqual(len(self.validator.errores), 0)
        self.assertEqual(len(self.validator.datos_limpios), 3)

        # Datos inválidos
        datos_invalidos = {
            'nombre': 'M',  # demasiado corto
            'email': 'emailinvalido',
            'edad': 15  # menor que el mínimo
        }

        es_valido = self.validator.validar_formulario(datos_invalidos, reglas)
        self.assertFalse(es_valido)
        self.assertEqual(len(self.validator.errores), 3)

    def test_campos_requeridos(self):
        """Prueba validación de campos requeridos."""
        reglas = {
            'nombre': [
                {'requerido': True},
                {'funcion': 'validar_longitud', 'params': {'min_len': 2}}
            ],
            'direccion': [
                {'requerido': False},
                {'funcion': 'validar_longitud', 'params': {'min_len': 5}}
            ]
        }

        # Falta el campo requerido
        datos = {
            'direccion': 'Calle Principal 123'
        }

        es_valido = self.validator.validar_formulario(datos, reglas)
        self.assertFalse(es_valido)
        self.assertIn('nombre', self.validator.errores)

        # Campo presente pero vacío
        datos = {
            'nombre': '',
            'direccion': 'Calle Principal 123'
        }

        es_valido = self.validator.validar_formulario(datos, reglas)
        self.assertFalse(es_valido)
        self.assertIn('nombre', self.validator.errores)


if __name__ == '__main__':
    unittest.main()
