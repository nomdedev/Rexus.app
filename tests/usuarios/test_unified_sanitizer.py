"""
Tests for UnifiedDataSanitizer - Sistema unificado de sanitización de datos
Tests de seguridad, prevención de SQL injection, XSS, y validación de datos
"""

import pytest
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# Agregar el directorio raíz al path
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

try:
    from rexus.utils.unified_sanitizer import (
        UnifiedDataSanitizer, unified_sanitizer, 
        sanitize_string, sanitize_numeric, sanitize_email, sanitize_dict
    )
    
    UNIFIED_SANITIZER_AVAILABLE = True
except ImportError as e:
    print(f"Error importando UnifiedDataSanitizer: {e}")
    UnifiedDataSanitizer = None
    UNIFIED_SANITIZER_AVAILABLE = False


class TestUnifiedDataSanitizer:
    """Suite de tests para UnifiedDataSanitizer."""
    
    def setup_method(self):
        """Configuración para cada test."""
        self.sanitizer = UnifiedDataSanitizer() if UnifiedDataSanitizer else None
    
    @pytest.mark.skipif(not UNIFIED_SANITIZER_AVAILABLE, reason="UnifiedDataSanitizer no disponible")
    def test_sanitize_string_normal(self):
        """Test sanitizar string normal."""
        input_text = "Texto normal para sanitizar"
        result = self.sanitizer.sanitize_string(input_text)
        
        # Verificaciones
        assert isinstance(result, str)
        assert result == "Texto normal para sanitizar"
    
    @pytest.mark.skipif(not UNIFIED_SANITIZER_AVAILABLE, reason="UnifiedDataSanitizer no disponible")
    def test_sanitize_string_with_html(self):
        """Test sanitizar string con HTML peligroso."""
        input_text = "<script>alert('XSS')</script>Texto limpio<b>bold</b>"
        result = self.sanitizer.sanitize_string(input_text)
        
        # Verificaciones
        assert "<script>" not in result
        assert "alert" not in result
        assert "Texto limpio" in result
        # HTML básico debería ser escapado
        assert "&lt;b&gt;" in result or "bold" in result
    
    @pytest.mark.skipif(not UNIFIED_SANITIZER_AVAILABLE, reason="UnifiedDataSanitizer no disponible")
    def test_sanitize_string_with_sql_injection(self):
        """Test sanitizar string con patrones de SQL injection."""
        input_text = "'; DROP TABLE usuarios; --"
        result = self.sanitizer.sanitize_string(input_text)
        
        # Verificaciones
        assert "DROP" not in result.upper()
        assert "TABLE" not in result.upper()
        assert "--" not in result
    
    @pytest.mark.skipif(not UNIFIED_SANITIZER_AVAILABLE, reason="UnifiedDataSanitizer no disponible")
    def test_sanitize_string_with_control_chars(self):
        """Test sanitizar string con caracteres de control."""
        input_text = "Texto\x00con\x01caracteres\x02de\x03control"
        result = self.sanitizer.sanitize_string(input_text)
        
        # Verificaciones
        assert "\x00" not in result
        assert "\x01" not in result
        assert "\x02" not in result
        assert "\x03" not in result
        assert "Texto" in result
    
    @pytest.mark.skipif(not UNIFIED_SANITIZER_AVAILABLE, reason="UnifiedDataSanitizer no disponible")
    def test_sanitize_string_max_length(self):
        """Test sanitizar string respetando longitud máxima."""
        long_text = "A" * 2000  # Texto muy largo
        result = self.sanitizer.sanitize_string(long_text, max_length=100)
        
        # Verificaciones
        assert len(result) <= 100
        assert result.startswith("A")
    
    @pytest.mark.skipif(not UNIFIED_SANITIZER_AVAILABLE, reason="UnifiedDataSanitizer no disponible")
    def test_sanitize_string_none_input(self):
        """Test sanitizar valor None."""
        result = self.sanitizer.sanitize_string(None)
        
        # Verificaciones
        assert result == ""
    
    @pytest.mark.skipif(not UNIFIED_SANITIZER_AVAILABLE, reason="UnifiedDataSanitizer no disponible")
    def test_sanitize_numeric_integer(self):
        """Test sanitizar número entero."""
        result = self.sanitizer.sanitize_numeric("123", allow_decimal=False)
        
        # Verificaciones
        assert result == 123
        assert isinstance(result, int)
    
    @pytest.mark.skipif(not UNIFIED_SANITIZER_AVAILABLE, reason="UnifiedDataSanitizer no disponible")
    def test_sanitize_numeric_float(self):
        """Test sanitizar número decimal."""
        result = self.sanitizer.sanitize_numeric("123.45", allow_decimal=True)
        
        # Verificaciones
        assert result == 123.45
        assert isinstance(result, float)
    
    @pytest.mark.skipif(not UNIFIED_SANITIZER_AVAILABLE, reason="UnifiedDataSanitizer no disponible")
    def test_sanitize_numeric_with_noise(self):
        """Test sanitizar número con caracteres extra."""
        result = self.sanitizer.sanitize_numeric("abc123.45xyz", allow_decimal=True)
        
        # Verificaciones
        assert result == 123.45
    
    @pytest.mark.skipif(not UNIFIED_SANITIZER_AVAILABLE, reason="UnifiedDataSanitizer no disponible")
    def test_sanitize_numeric_invalid(self):
        """Test sanitizar valor no numérico."""
        result = self.sanitizer.sanitize_numeric("not_a_number")
        
        # Verificaciones
        assert result is None
    
    @pytest.mark.skipif(not UNIFIED_SANITIZER_AVAILABLE, reason="UnifiedDataSanitizer no disponible")
    def test_sanitize_numeric_with_range(self):
        """Test sanitizar número aplicando rango."""
        # Número mayor al máximo permitido
        result = self.sanitizer.sanitize_numeric("1000", min_val=1, max_val=100)
        
        # Verificaciones
        assert result == 100  # Debería limitarse al máximo
        
        # Número menor al mínimo permitido
        result = self.sanitizer.sanitize_numeric("-50", min_val=1, max_val=100)
        
        # Verificaciones
        assert result == 1  # Debería limitarse al mínimo
    
    @pytest.mark.skipif(not UNIFIED_SANITIZER_AVAILABLE, reason="UnifiedDataSanitizer no disponible")
    def test_sanitize_email_valid(self):
        """Test sanitizar email válido."""
        email = "usuario@ejemplo.com"
        result = self.sanitizer.sanitize_email(email)
        
        # Verificaciones
        assert result == "usuario@ejemplo.com"
    
    @pytest.mark.skipif(not UNIFIED_SANITIZER_AVAILABLE, reason="UnifiedDataSanitizer no disponible")
    def test_sanitize_email_invalid_format(self):
        """Test sanitizar email con formato inválido."""
        invalid_emails = [
            "email_sin_arroba",
            "email@",
            "@dominio.com",
            "email@dominio",
            "email.dominio.com",
            ""
        ]
        
        for email in invalid_emails:
            result = self.sanitizer.sanitize_email(email)
            assert result is None, f"Email inválido '{email}' debería retornar None"
    
    @pytest.mark.skipif(not UNIFIED_SANITIZER_AVAILABLE, reason="UnifiedDataSanitizer no disponible")
    def test_sanitize_email_too_long(self):
        """Test sanitizar email demasiado largo."""
        long_email = "a" * 250 + "@ejemplo.com"  # Excede límite RFC 5321
        result = self.sanitizer.sanitize_email(long_email)
        
        # Verificaciones
        assert result is None
    
    @pytest.mark.skipif(not UNIFIED_SANITIZER_AVAILABLE, reason="UnifiedDataSanitizer no disponible")
    def test_sanitize_email_case_normalization(self):
        """Test normalización de mayúsculas en email."""
        email = "USUARIO@EJEMPLO.COM"
        result = self.sanitizer.sanitize_email(email)
        
        # Verificaciones
        assert result == "usuario@ejemplo.com"
    
    @pytest.mark.skipif(not UNIFIED_SANITIZER_AVAILABLE, reason="UnifiedDataSanitizer no disponible")
    def test_sanitize_phone_valid(self):
        """Test sanitizar teléfono válido."""
        phone = "+1 (555) 123-4567"
        result = self.sanitizer.sanitize_phone(phone)
        
        # Verificaciones
        assert result is not None
        assert "555" in result
        assert "123" in result
        assert "4567" in result
    
    @pytest.mark.skipif(not UNIFIED_SANITIZER_AVAILABLE, reason="UnifiedDataSanitizer no disponible")
    def test_sanitize_phone_with_letters(self):
        """Test sanitizar teléfono con letras."""
        phone = "1-800-FLOWERS"  # Contiene letras
        result = self.sanitizer.sanitize_phone(phone)
        
        # Verificaciones - debería limpiar las letras
        assert result == "1-800-" or result is None
    
    @pytest.mark.skipif(not UNIFIED_SANITIZER_AVAILABLE, reason="UnifiedDataSanitizer no disponible")
    def test_sanitize_phone_too_short(self):
        """Test sanitizar teléfono demasiado corto."""
        phone = "123"
        result = self.sanitizer.sanitize_phone(phone)
        
        # Verificaciones
        assert result is None
    
    @pytest.mark.skipif(not UNIFIED_SANITIZER_AVAILABLE, reason="UnifiedDataSanitizer no disponible")
    def test_sanitize_url_valid(self):
        """Test sanitizar URL válida."""
        urls_validas = [
            "https://ejemplo.com",
            "http://www.ejemplo.com/path",
            "https://ejemplo.com:8080/path?param=value"
        ]
        
        for url in urls_validas:
            result = self.sanitizer.sanitize_url(url)
            assert result == url, f"URL válida '{url}' debería pasar sin cambios"
    
    @pytest.mark.skipif(not UNIFIED_SANITIZER_AVAILABLE, reason="UnifiedDataSanitizer no disponible")
    def test_sanitize_url_invalid_scheme(self):
        """Test sanitizar URL con esquema inválido."""
        urls_invalidas = [
            "javascript:alert('XSS')",
            "file:///etc/passwd",
            "data:text/html,<script>alert('XSS')</script>"
        ]
        
        for url in urls_invalidas:
            result = self.sanitizer.sanitize_url(url)
            assert result is None, f"URL inválida '{url}' debería retornar None"
    
    @pytest.mark.skipif(not UNIFIED_SANITIZER_AVAILABLE, reason="UnifiedDataSanitizer no disponible")
    def test_sanitize_url_too_long(self):
        """Test sanitizar URL demasiado larga."""
        long_url = "https://ejemplo.com/" + "a" * 2500
        result = self.sanitizer.sanitize_url(long_url)
        
        # Verificaciones
        assert result is None
    
    @pytest.mark.skipif(not UNIFIED_SANITIZER_AVAILABLE, reason="UnifiedDataSanitizer no disponible")
    def test_sanitize_sql_input(self):
        """Test sanitizar entrada SQL."""
        sql_dangerous = "'; DELETE FROM usuarios WHERE '1'='1"
        result = self.sanitizer.sanitize_sql_input(sql_dangerous)
        
        # Verificaciones
        assert "DELETE" not in result.upper()
        assert "WHERE" not in result.upper()
        assert "'1'=''1" in result  # Comillas escapadas
    
    @pytest.mark.skipif(not UNIFIED_SANITIZER_AVAILABLE, reason="UnifiedDataSanitizer no disponible")
    def test_sanitize_html_no_tags_allowed(self):
        """Test sanitizar HTML sin permitir tags."""
        html_input = "<p>Párrafo</p><script>alert('XSS')</script><b>Negrita</b>"
        result = self.sanitizer.sanitize_html(html_input)
        
        # Verificaciones
        assert "<script>" not in result
        assert "&lt;p&gt;" in result or "Párrafo" in result
        assert "&lt;b&gt;" in result or "Negrita" in result
    
    @pytest.mark.skipif(not UNIFIED_SANITIZER_AVAILABLE, reason="UnifiedDataSanitizer no disponible")
    def test_sanitize_html_with_allowed_tags(self):
        """Test sanitizar HTML permitiendo tags específicos."""
        html_input = "<p>Párrafo</p><script>alert('XSS')</script><b>Negrita</b>"
        result = self.sanitizer.sanitize_html(html_input, allowed_tags=['p', 'b'])
        
        # Verificaciones
        assert "<script>" not in result
        assert "alert" not in result
        # Tags peligrosos deberían ser removidos
    
    @pytest.mark.skipif(not UNIFIED_SANITIZER_AVAILABLE, reason="UnifiedDataSanitizer no disponible")
    def test_sanitize_dict_complete(self):
        """Test sanitizar diccionario completo."""
        input_dict = {
            "nombre": "Juan Pérez",
            "email": "JUAN@EJEMPLO.COM",
            "edad": "25",
            "descripcion": "<script>alert('XSS')</script>Descripción limpia",
            "telefono": "+1-555-123-4567",
            "precio": "99.99",
            "categoria": "Categoría normal"
        }
        
        string_fields = ['nombre', 'descripcion', 'categoria']
        numeric_fields = ['edad', 'precio']
        
        result = self.sanitizer.sanitize_dict(input_dict, string_fields, numeric_fields)
        
        # Verificaciones
        assert isinstance(result, dict)
        assert result['nombre'] == "Juan Pérez"
        assert isinstance(result['edad'], (int, float))
        assert isinstance(result['precio'], (int, float))
        assert "<script>" not in result.get('descripcion', '')
    
    @pytest.mark.skipif(not UNIFIED_SANITIZER_AVAILABLE, reason="UnifiedDataSanitizer no disponible")
    def test_sanitize_dict_nested(self):
        """Test sanitizar diccionario con subdiccionarios."""
        input_dict = {
            "usuario": {
                "nombre": "Juan",
                "config": {
                    "tema": "<script>dark</script>"
                }
            },
            "datos": ["item1", "item2<script>alert('XSS')</script>"]
        }
        
        result = self.sanitizer.sanitize_dict(input_dict)
        
        # Verificaciones
        assert isinstance(result, dict)
        assert isinstance(result['usuario'], dict)
        assert "<script>" not in str(result)
    
    @pytest.mark.skipif(not UNIFIED_SANITIZER_AVAILABLE, reason="UnifiedDataSanitizer no disponible")
    def test_convenience_functions(self):
        """Test funciones de conveniencia del módulo."""
        # Test sanitize_string
        result = sanitize_string("Texto de prueba")
        assert result == "Texto de prueba"
        
        # Test sanitize_numeric
        result = sanitize_numeric("123.45")
        assert result == 123.45
        
        # Test sanitize_email
        result = sanitize_email("test@example.com")
        assert result == "test@example.com"
        
        # Test sanitize_dict
        test_dict = {"key": "value"}
        result = sanitize_dict(test_dict)
        assert isinstance(result, dict)
        assert result['key'] == "value"
    
    @pytest.mark.skipif(not UNIFIED_SANITIZER_AVAILABLE, reason="UnifiedDataSanitizer no disponible")
    def test_xss_patterns_removal(self):
        """Test remoción de patrones XSS específicos."""
        xss_inputs = [
            "<script>alert('XSS')</script>",
            "<iframe src='javascript:alert(1)'></iframe>",
            "<object data='malicious'></object>",
            "<embed src='evil.swf'>",
            "<link rel='stylesheet' href='evil.css'>",
            "<meta http-equiv='refresh' content='0;url=evil.com'>",
            "javascript:alert('XSS')",
            "vbscript:msgbox('XSS')",
            "onload='alert(1)'",
            "onerror='alert(1)'",
            "onclick='alert(1)'",
            "onmouseover='alert(1)'"
        ]
        
        for xss_input in xss_inputs:
            result = self.sanitizer.sanitize_string(xss_input)
            # No debe contener el patrón peligroso original
            assert xss_input not in result
            # Verificar que se removieron elementos específicos
            assert "<script>" not in result
            assert "javascript:" not in result
            assert "onload=" not in result.lower()
    
    @pytest.mark.skipif(not UNIFIED_SANITIZER_AVAILABLE, reason="UnifiedDataSanitizer no disponible")
    def test_global_sanitizer_instance(self):
        """Test instancia global del sanitizador."""
        # Verificar que la instancia global está disponible
        assert unified_sanitizer is not None
        assert isinstance(unified_sanitizer, UnifiedDataSanitizer)
        
        # Verificar que funciona correctamente
        result = unified_sanitizer.sanitize_string("Texto de prueba")
        assert result == "Texto de prueba"


if __name__ == "__main__":
    # Ejecutar tests específicos
    test_suite = TestUnifiedDataSanitizer()
    test_suite.setup_method()
    
    if UNIFIED_SANITIZER_AVAILABLE:
        print("=== EJECUTANDO TESTS DE UNIFIED DATA SANITIZER ===")
        
        try:
            test_suite.test_sanitize_string_with_sql_injection()
            print("✅ Test SQL injection - PASADO")
        except Exception as e:
            print(f"❌ Test SQL injection - FALLIDO: {e}")
        
        try:
            test_suite.test_sanitize_string_with_html()
            print("✅ Test XSS prevention - PASADO")
        except Exception as e:
            print(f"❌ Test XSS prevention - FALLIDO: {e}")
        
        try:
            test_suite.test_sanitize_email_valid()
            print("✅ Test email válido - PASADO")
        except Exception as e:
            print(f"❌ Test email válido - FALLIDO: {e}")
        
        try:
            test_suite.test_sanitize_numeric_integer()
            print("✅ Test número entero - PASADO")
        except Exception as e:
            print(f"❌ Test número entero - FALLIDO: {e}")
        
        try:
            test_suite.test_xss_patterns_removal()
            print("✅ Test patrones XSS - PASADO")
        except Exception as e:
            print(f"❌ Test patrones XSS - FALLIDO: {e}")
        
        try:
            test_suite.test_convenience_functions()
            print("✅ Test funciones de conveniencia - PASADO")
        except Exception as e:
            print(f"❌ Test funciones de conveniencia - FALLIDO: {e}")
        
        print("=== TESTS DE UNIFIED DATA SANITIZER COMPLETADOS ===")
    else:
        print("❌ UnifiedDataSanitizer no disponible para testing")