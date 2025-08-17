"""
Test para verificar el manejo de None en form_validators.py

Tests que verifican que todos los validadores manejan correctamente:
- Valores None
- Tipos no-string
- Conversión automática a string
"""

import pytest
from unittest.mock import Mock

from rexus.utils.form_validators import (
    FormValidator,
    validacion_direccion,
    validacion_codigo_producto
)


class TestFormValidatorsNoneHandling:
    """Test suite para manejo de None en validadores."""

    def setup_method(self):
        """Setup para cada test."""
        self.mock_campo = Mock()

    def test_validar_campo_obligatorio_none(self):
        """Test que validar_campo_obligatorio maneja None."""
        resultado, mensaje = FormValidator.validar_campo_obligatorio(
            self.mock_campo, None, "Test Campo"
        )
        assert not resultado
        assert "obligatorio" in mensaje

    def test_validar_campo_obligatorio_int(self):
        """Test que validar_campo_obligatorio maneja int."""
        resultado, mensaje = FormValidator.validar_campo_obligatorio(
            self.mock_campo, 123, "Test Campo"
        )
        assert resultado
        assert mensaje == ""

    def test_validar_email_none(self):
        """Test que validar_email maneja None."""
        resultado, mensaje = FormValidator.validar_email(self.mock_campo, None)
        assert not resultado
        assert "obligatorio" in mensaje

    def test_validar_email_int(self):
        """Test que validar_email maneja int."""
        resultado, mensaje = FormValidator.validar_email(self.mock_campo, 123)
        assert not resultado  # 123 no es un email válido
        assert "inválido" in mensaje

    def test_validar_telefono_none(self):
        """Test que validar_telefono maneja None."""
        resultado, mensaje = FormValidator.validar_telefono(self.mock_campo, None)
        assert resultado  # Teléfono es opcional
        assert mensaje == ""

    def test_validar_telefono_int(self):
        """Test que validar_telefono maneja int."""
        resultado, mensaje = FormValidator.validar_telefono(self.mock_campo, 1234567890)
        assert resultado  # Número válido convertido a string
        assert mensaje == ""

    def test_validar_numero_none(self):
        """Test que validar_numero maneja None."""
        resultado, mensaje = FormValidator.validar_numero(self.mock_campo, None)
        assert not resultado
        assert "requerido" in mensaje

    def test_validar_numero_int(self):
        """Test que validar_numero maneja int."""
        resultado, mensaje = FormValidator.validar_numero(self.mock_campo, 123)
        assert resultado
        assert mensaje == ""

    def test_validar_numero_float(self):
        """Test que validar_numero maneja float."""
        resultado, mensaje = FormValidator.validar_numero(self.mock_campo, 123.45)
        assert resultado
        assert mensaje == ""

    def test_validar_longitud_texto_none(self):
        """Test que validar_longitud_texto maneja None."""
        resultado, mensaje = FormValidator.validar_longitud_texto(
            self.mock_campo, None, min_len=1
        )
        assert not resultado  # Texto vacío no cumple min_len=1
        assert "Mínimo" in mensaje

    def test_validar_longitud_texto_int(self):
        """Test que validar_longitud_texto maneja int."""
        resultado, mensaje = FormValidator.validar_longitud_texto(
            self.mock_campo, 12345, min_len=3, max_len=10
        )
        assert resultado  # "12345" tiene 5 caracteres, está en rango
        assert mensaje == ""

    def test_validacion_direccion_none(self):
        """Test que validacion_direccion maneja None."""
        resultado, mensaje = validacion_direccion(self.mock_campo, None)
        assert not resultado
        assert "obligatoria" in mensaje

    def test_validacion_direccion_int(self):
        """Test que validacion_direccion maneja int."""
        # Un número como dirección necesita al menos 10 caracteres
        resultado, mensaje = validacion_direccion(self.mock_campo, 1234567890123)
        assert resultado
        assert mensaje == ""

    def test_validacion_codigo_producto_none(self):
        """Test que validacion_codigo_producto maneja None."""
        resultado, mensaje = validacion_codigo_producto(self.mock_campo, None)
        assert not resultado
        assert "obligatorio" in mensaje

    def test_validacion_codigo_producto_int(self):
        """Test que validacion_codigo_producto maneja int."""
        # Un int no será formato válido de código
        resultado, mensaje = validacion_codigo_producto(self.mock_campo, 123456)
        assert not resultado
        assert "inválido" in mensaje

    def test_validacion_codigo_producto_formato_valido(self):
        """Test código producto con formato válido."""
        resultado, mensaje = validacion_codigo_producto(self.mock_campo, "VID-1234")
        assert resultado
        assert mensaje == ""

    def test_types_conversion_edge_cases(self):
        """Test casos extremos de conversión de tipos."""
        # Test con list
        resultado, mensaje = FormValidator.validar_campo_obligatorio(
            self.mock_campo, [1, 2, 3], "Test"
        )
        assert resultado  # Se convierte a "[1, 2, 3]"

        # Test con dict
        resultado, mensaje = FormValidator.validar_campo_obligatorio(
            self.mock_campo, {"key": "value"}, "Test"
        )
        assert resultado  # Se convierte a "{'key': 'value'}"

        # Test con bool
        resultado, mensaje = FormValidator.validar_campo_obligatorio(
            self.mock_campo, True, "Test"
        )
        assert resultado  # Se convierte a "True"

        # Test con False (caso especial)
        resultado, mensaje = FormValidator.validar_campo_obligatorio(
            self.mock_campo, False, "Test"
        )
        assert resultado  # Se convierte a "False", no está vacío

    def test_empty_string_vs_none(self):
        """Test diferencia entre string vacío y None."""
        # None
        resultado_none, _ = FormValidator.validar_campo_obligatorio(
            self.mock_campo, None, "Test"
        )
        
        # String vacío
        resultado_empty, _ = FormValidator.validar_campo_obligatorio(
            self.mock_campo, "", "Test"
        )
        
        # Whitespace
        resultado_space, _ = FormValidator.validar_campo_obligatorio(
            self.mock_campo, "   ", "Test"
        )
        
        # Todos deberían fallar para campo obligatorio
        assert not resultado_none
        assert not resultado_empty
        assert not resultado_space

    def test_numeric_validation_ranges(self):
        """Test validación numérica con rangos."""
        # Test con número como string en rango
        resultado, mensaje = FormValidator.validar_numero(
            self.mock_campo, "50", min_val=10, max_val=100
        )
        assert resultado
        assert mensaje == ""

        # Test con número fuera de rango
        resultado, mensaje = FormValidator.validar_numero(
            self.mock_campo, "150", min_val=10, max_val=100
        )
        assert not resultado
        assert "máximo" in mensaje.lower()

        # Test con número como int en rango
        resultado, mensaje = FormValidator.validar_numero(
            self.mock_campo, 75, min_val=10, max_val=100
        )
        assert resultado
        assert mensaje == ""


if __name__ == "__main__":
    pytest.main([__file__, "-v"])