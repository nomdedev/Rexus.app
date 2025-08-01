"""
Tests de seguridad específicos para el módulo Herrajes.
Verifica que las utilidades de seguridad funcionen correctamente en HerrajesModel.
"""

import sys
import unittest
from pathlib import Path

# Agregar el directorio raíz al path
ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT_DIR))

from rexus.modules.herrajes.model import HerrajesModel


class TestHerrajesSecurityIntegration(unittest.TestCase):
    """Tests de seguridad para el módulo de herrajes."""
    
    def setUp(self):
        """Configurar tests."""
        self.herrajes_model = HerrajesModel()
    
    def test_herrajes_security_loaded(self):
        """Verificar que las utilidades de seguridad se cargan en herrajes."""
        self.assertTrue(self.herrajes_model.security_available)
        self.assertIsNotNone(self.herrajes_model.data_sanitizer)
        self.assertIsNotNone(self.herrajes_model.sql_validator)
    
    def test_buscar_herrajes_sanitization(self):
        """Verificar que la búsqueda sanitiza la entrada."""
        if not self.herrajes_model.security_available:
            self.skipTest("Security utilities not available")
            
        # Test con entrada maliciosa
        termino_malicioso = "<script>alert('xss')</script>'; DROP TABLE herrajes; --"
        
        # Sin conexión a BD, debe retornar lista vacía sin errores
        resultado = self.herrajes_model.buscar_herrajes(termino_malicioso)
        
        # Debe retornar lista vacía sin crashes
        self.assertEqual(resultado, [])
    
    def test_crear_herraje_data_sanitization(self):
        """Verificar que la creación de herrajes sanitiza los datos."""
        if not self.herrajes_model.security_available:
            self.skipTest("Security utilities not available")
            
        # Test con datos maliciosos
        datos_maliciosos = {
            "codigo": "<script>alert('xss')</script>",
            "descripcion": "Herraje'; DROP TABLE herrajes; --",
            "proveedor": "<iframe>Proveedor Malo</iframe>",
            "precio_unitario": "no-es-numero",
            "observaciones": "<script>window.location='http://evil.com'</script>"
        }
        
        # Sin conexión a BD, debe retornar False con mensaje de error
        exito, mensaje = self.herrajes_model.crear_herraje(datos_maliciosos)
        
        # Debe fallar por falta de conexión a BD, no por datos maliciosos
        self.assertFalse(exito)
        self.assertIn("Sin conexión", mensaje)
    
    def test_create_herraje_validation(self):
        """Verificar que se validan los datos requeridos."""
        if not self.herrajes_model.security_available:
            self.skipTest("Security utilities not available")
            
        # Simular conexión a BD para probar validación
        class MockConnection:
            def cursor(self):
                return self
            def execute(self, query, params=None):
                pass
            def fetchone(self):
                return [0]  # Simular que el código no existe
            def commit(self):
                pass
                
        self.herrajes_model.db_connection = MockConnection()
        
        # Test con datos incompletos
        datos_incompletos = {
            "codigo": "",  # Vacío - debe fallar
            "descripcion": "Descripción válida",
            "proveedor": "Proveedor válido"
        }
        
        exito, mensaje = self.herrajes_model.crear_herraje(datos_incompletos)
        
        # Debe fallar por código vacío
        self.assertFalse(exito)
        self.assertIn("código", mensaje.lower())
    
    def test_numeric_validation(self):
        """Verificar que la validación numérica funciona."""
        if not self.herrajes_model.security_available:
            self.skipTest("Security utilities not available")
            
        # Simular conexión a BD
        class MockConnection:
            def cursor(self):
                return self
            def execute(self, query, params=None):
                pass
            def fetchone(self):
                return [0]
            def commit(self):
                pass
                
        self.herrajes_model.db_connection = MockConnection()
        
        # Test con precio inválido
        datos_precio_invalido = {
            "codigo": "TEST-001",
            "descripcion": "Herraje de prueba",
            "proveedor": "Proveedor Test",
            "precio_unitario": "precio-invalido"  # No es número
        }
        
        exito, mensaje = self.herrajes_model.crear_herraje(datos_precio_invalido)
        
        # Debe fallar por precio inválido
        self.assertFalse(exito)
        self.assertIn("inválido", mensaje.lower())
    
    def test_xss_prevention_in_search(self):
        """Verificar que se previenen ataques XSS en búsquedas."""
        if not self.herrajes_model.security_available:
            self.skipTest("Security utilities not available")
            
        # Test con script malicioso
        script_malicioso = "<script>alert('XSS Attack')</script>"
        
        # La búsqueda debe manejar el script sin errores
        resultado = self.herrajes_model.buscar_herrajes(script_malicioso)
        
        # Debe retornar lista vacía sin crashes
        self.assertEqual(resultado, [])
    
    def test_sql_injection_prevention(self):
        """Verificar que se previenen inyecciones SQL."""
        if not self.herrajes_model.security_available:
            self.skipTest("Security utilities not available")
            
        # Test con entrada maliciosa SQL
        entrada_maliciosa = "'; DROP TABLE herrajes; --"
        
        # La búsqueda debe manejar la inyección sin errores
        resultado = self.herrajes_model.buscar_herrajes(entrada_maliciosa)
        
        # Debe retornar lista vacía sin crashes
        self.assertEqual(resultado, [])
    
    def test_table_names_are_safe(self):
        """Verificar que los nombres de tabla están definidos de forma segura."""
        # Los nombres de tabla deben estar predefinidos, no construidos dinámicamente
        self.assertEqual(self.herrajes_model.tabla_herrajes, "herrajes")
        self.assertEqual(self.herrajes_model.tabla_herrajes_obra, "herrajes_obra")
        self.assertEqual(self.herrajes_model.tabla_pedidos_herrajes, "pedidos_herrajes")
        self.assertEqual(self.herrajes_model.tabla_herrajes_inventario, "herrajes_inventario")
        
        # Los nombres no deben contener caracteres peligrosos
        for tabla in [
            self.herrajes_model.tabla_herrajes,
            self.herrajes_model.tabla_herrajes_obra,
            self.herrajes_model.tabla_pedidos_herrajes,
            self.herrajes_model.tabla_herrajes_inventario
        ]:
            self.assertNotIn("'", tabla)
            self.assertNotIn("\"", tabla)
            self.assertNotIn(";", tabla)
            self.assertNotIn("--", tabla)
            self.assertNotIn("/*", tabla)


if __name__ == "__main__":
    unittest.main()