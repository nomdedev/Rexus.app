"""
Tests de integración de seguridad para módulos mejorados.
Verifica que las utilidades de seguridad funcionen correctamente en los módulos.
"""

import sys
import unittest
from pathlib import Path

# Agregar el directorio raíz al path
ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT_DIR))

from rexus.modules.usuarios.model import UsuariosModel
from rexus.modules.inventario.model import InventarioModel


class TestSecurityIntegration(unittest.TestCase):
    """Tests de integración para las utilidades de seguridad en módulos."""
    
    def setUp(self):
        """Configurar tests."""
        self.usuarios_model = UsuariosModel()
        self.inventario_model = InventarioModel()
    
    def test_usuarios_security_loaded(self):
        """Verificar que las utilidades de seguridad se cargan en usuarios."""
        self.assertTrue(self.usuarios_model.security_available)
        self.assertIsNotNone(self.usuarios_model.data_sanitizer)
        self.assertIsNotNone(self.usuarios_model.sql_validator)
    
    def test_inventario_security_loaded(self):
        """Verificar que las utilidades de seguridad se cargan en inventario."""
        self.assertTrue(self.inventario_model.security_available)
        self.assertIsNotNone(self.inventario_model.data_sanitizer)
        self.assertIsNotNone(self.inventario_model.sql_validator)
    
    def test_usuarios_data_sanitization(self):
        """Verificar que la sanitización funciona en el modelo usuarios."""
        if not self.usuarios_model.security_available:
            self.skipTest("Security utilities not available")
            
        # Test sanitización de datos de usuario maliciosos
        datos_maliciosos = {
            "usuario": "<script>alert('xss')</script>",
            "email": "user<script>@evil.com",
            "nombre_completo": "Usuario'; DROP TABLE usuarios; --",
            "telefono": "+1<iframe>234567890"
        }
        
        # La sanitización debe funcionar
        datos_limpios = self.usuarios_model.data_sanitizer.sanitize_form_data(datos_maliciosos)
        
        # Verificar que se han eliminado los elementos peligrosos
        self.assertNotIn("<script>", datos_limpios["usuario"])
        self.assertNotIn("<script>", datos_limpios["email"])
        self.assertNotIn("DROP TABLE", datos_limpios["nombre_completo"])
        self.assertNotIn("<iframe>", datos_limpios["telefono"])
    
    def test_sql_injection_prevention(self):
        """Verificar que se previenen inyecciones SQL."""
        if not self.usuarios_model.security_available:
            self.skipTest("Security utilities not available")
            
        # Test con entrada maliciosa
        entrada_maliciosa = "admin'; DROP TABLE usuarios; --"
        
        # La sanitización debe limpiar la entrada
        entrada_limpia = self.usuarios_model.data_sanitizer.sanitize_string(entrada_maliciosa)
        
        # Verificar que se bloquearon los patrones peligrosos
        self.assertIn("[BLOCKED]", entrada_limpia)
        self.assertNotIn("DROP TABLE", entrada_limpia)
    
    def test_xss_prevention(self):
        """Verificar que se previenen ataques XSS."""
        if not self.usuarios_model.security_available:
            self.skipTest("Security utilities not available")
            
        # Test con script malicioso
        script_malicioso = "<script>alert('XSS Attack')</script>"
        
        # La sanitización debe escapar el HTML
        resultado = self.usuarios_model.data_sanitizer.sanitize_string(script_malicioso)
        
        # Verificar que se escapó correctamente
        self.assertNotIn("<script>", resultado)
        self.assertIn("&lt;script&gt;", resultado)
    
    def test_email_validation(self):
        """Verificar que la validación de email funciona."""
        if not self.usuarios_model.security_available:
            self.skipTest("Security utilities not available")
            
        # Email válido
        email_valido = "usuario@example.com"
        resultado_valido = self.usuarios_model.data_sanitizer.sanitize_email(email_valido)
        self.assertEqual(resultado_valido, email_valido)
        
        # Email con caracteres peligrosos
        email_malicioso = "user<script>@evil.com"
        resultado_malicioso = self.usuarios_model.data_sanitizer.sanitize_email(email_malicioso)
        self.assertNotIn("<script>", resultado_malicioso)
    
    def test_numeric_validation(self):
        """Verificar que la validación numérica funciona."""
        if not self.inventario_model.security_available:
            self.skipTest("Security utilities not available")
            
        # Número válido
        resultado = self.inventario_model.data_sanitizer.sanitize_numeric("123.45")
        self.assertEqual(resultado, 123.45)
        
        # Valor no numérico
        resultado = self.inventario_model.data_sanitizer.sanitize_numeric("no-numero")
        self.assertIsNone(resultado)
        
        # Número con límites
        resultado = self.inventario_model.data_sanitizer.sanitize_numeric(150, min_val=0, max_val=100)
        self.assertEqual(resultado, 100)


if __name__ == "__main__":
    unittest.main()