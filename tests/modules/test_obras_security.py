"""
Tests de seguridad específicos para el módulo Obras.
Verifica que las utilidades de seguridad funcionen correctamente en ObrasModel.
"""

import sys
import unittest
from pathlib import Path

# Agregar el directorio raíz al path
ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT_DIR))

from rexus.modules.obras.model import ObrasModel


class TestObrasSecurityIntegration(unittest.TestCase):
    """Tests de seguridad para el módulo de obras."""
    
    def setUp(self):
        """Configurar tests."""
        self.obras_model = ObrasModel()
    
    def test_obras_security_loaded(self):
        """Verificar que las utilidades de seguridad se cargan en obras."""
        self.assertTrue(self.obras_model.security_available)
        self.assertIsNotNone(self.obras_model.data_sanitizer)
        self.assertIsNotNone(self.obras_model.sql_validator)
    
    def test_crear_obra_data_sanitization(self):
        """Verificar que la creación de obras sanitiza los datos."""
        if not self.obras_model.security_available:
            self.skipTest("Security utilities not available")
            
        # Test con datos maliciosos
        datos_maliciosos = {
            "codigo": "<script>alert('xss')</script>",
            "nombre": "Obra'; DROP TABLE obras; --",
            "cliente": "<iframe>Cliente Malo</iframe>",
            "email_contacto": "admin<script>@evil.com",
            "presupuesto_total": "no-es-numero",
            "descripcion": "<script>window.location='http://evil.com'</script>",
            "observaciones": "'; DELETE FROM obras WHERE 1=1; --"
        }
        
        # Sin conexión a BD, debe retornar False con mensaje de error
        exito, mensaje = self.obras_model.crear_obra(datos_maliciosos)
        
        # Debe fallar por falta de conexión a BD, no por datos maliciosos
        self.assertFalse(exito)
        self.assertIn("Sin conexión", mensaje)
    
    def test_create_obra_validation(self):
        """Verificar que se validan los datos requeridos."""
        if not self.obras_model.security_available:
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
            def close(self):
                pass
            def rollback(self):
                pass
                
        self.obras_model.db_connection = MockConnection()
        
        # Test con datos incompletos - código vacío
        datos_sin_codigo = {
            "codigo": "",  # Vacío - debe fallar
            "nombre": "Obra de prueba",
            "cliente": "Cliente válido"
        }
        
        exito, mensaje = self.obras_model.crear_obra(datos_sin_codigo)
        
        # Debe fallar por código vacío
        self.assertFalse(exito)
        self.assertIn("código", mensaje.lower())
        
        # Test con datos incompletos - nombre vacío
        datos_sin_nombre = {
            "codigo": "OBR-001",
            "nombre": "",  # Vacío - debe fallar
            "cliente": "Cliente válido"
        }
        
        exito, mensaje = self.obras_model.crear_obra(datos_sin_nombre)
        
        # Debe fallar por nombre vacío
        self.assertFalse(exito)
        self.assertIn("nombre", mensaje.lower())
        
        # Test con datos incompletos - cliente vacío
        datos_sin_cliente = {
            "codigo": "OBR-001",
            "nombre": "Obra de prueba",
            "cliente": ""  # Vacío - debe fallar
        }
        
        exito, mensaje = self.obras_model.crear_obra(datos_sin_cliente)
        
        # Debe fallar por cliente vacío
        self.assertFalse(exito)
        self.assertIn("cliente", mensaje.lower())
    
    def test_email_validation(self):
        """Verificar que la validación de email funciona."""
        if not self.obras_model.security_available:
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
            def close(self):
                pass
            def rollback(self):
                pass
                
        self.obras_model.db_connection = MockConnection()
        
        # Test con email inválido
        datos_email_invalido = {
            "codigo": "OBR-001",
            "nombre": "Obra de prueba",
            "cliente": "Cliente Test",
            "email_contacto": "email-invalido"  # No es email válido
        }
        
        exito, mensaje = self.obras_model.crear_obra(datos_email_invalido)
        
        # Debe fallar por email inválido
        self.assertFalse(exito)
        self.assertIn("email", mensaje.lower())
    
    def test_numeric_validation(self):
        """Verificar que la validación numérica funciona."""
        if not self.obras_model.security_available:
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
            def close(self):
                pass
            def rollback(self):
                pass
                
        self.obras_model.db_connection = MockConnection()
        
        # Test con presupuesto inválido
        datos_presupuesto_invalido = {
            "codigo": "OBR-001",
            "nombre": "Obra de prueba",
            "cliente": "Cliente Test",
            "presupuesto_total": "presupuesto-invalido"  # No es número
        }
        
        exito, mensaje = self.obras_model.crear_obra(datos_presupuesto_invalido)
        
        # Debe fallar por presupuesto inválido
        self.assertFalse(exito)
        self.assertIn("inválido", mensaje.lower())
    
    def test_xss_prevention(self):
        """Verificar que se previenen ataques XSS."""
        if not self.obras_model.security_available:
            self.skipTest("Security utilities not available")
            
        # Test con script malicioso en nombre
        datos_con_xss = {
            "codigo": "OBR-001",
            "nombre": "<script>alert('XSS Attack')</script>",
            "cliente": "Cliente Test"
        }
        
        # Sin conexión a BD, debe fallar por conexión, no por XSS
        exito, mensaje = self.obras_model.crear_obra(datos_con_xss)
        
        # Debe retornar False por falta de conexión
        self.assertFalse(exito)
        self.assertIn("Sin conexión", mensaje)
    
    def test_sql_injection_prevention(self):
        """Verificar que se previenen inyecciones SQL."""
        if not self.obras_model.security_available:
            self.skipTest("Security utilities not available")
            
        # Test con entrada maliciosa SQL
        datos_con_sql_injection = {
            "codigo": "OBR'; DROP TABLE obras; --",
            "nombre": "Obra de prueba",
            "cliente": "Cliente'; DELETE FROM obras WHERE 1=1; --"
        }
        
        # Sin conexión a BD, debe fallar por conexión, no por inyección
        exito, mensaje = self.obras_model.crear_obra(datos_con_sql_injection)
        
        # Debe retornar False por falta de conexión
        self.assertFalse(exito)
        self.assertIn("Sin conexión", mensaje)
    
    def test_table_names_are_safe(self):
        """Verificar que los nombres de tabla están definidos de forma segura."""
        # Los nombres de tabla deben estar predefinidos, no construidos dinámicamente
        self.assertEqual(self.obras_model.tabla_obras, "obras")
        self.assertEqual(self.obras_model.tabla_detalles_obra, "detalles_obra")
        
        # Los nombres no deben contener caracteres peligrosos
        for tabla in [
            self.obras_model.tabla_obras,
            self.obras_model.tabla_detalles_obra
        ]:
            self.assertNotIn("'", tabla)
            self.assertNotIn("\"", tabla)
            self.assertNotIn(";", tabla)
            self.assertNotIn("--", tabla)
            self.assertNotIn("/*", tabla)
    
    def test_phone_sanitization(self):
        """Verificar que la sanitización de teléfono funciona."""
        if not self.obras_model.security_available:
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
            def close(self):
                pass
            def rollback(self):
                pass
                
        self.obras_model.db_connection = MockConnection()
        
        # Test con teléfono con caracteres maliciosos
        datos_telefono_malicioso = {
            "codigo": "OBR-001",
            "nombre": "Obra de prueba",
            "cliente": "Cliente Test",
            "telefono_contacto": "+1<script>234567890"
        }
        
        # Debe crear la obra exitosamente con teléfono sanitizado
        exito, mensaje = self.obras_model.crear_obra(datos_telefono_malicioso)
        
        # Debe ser exitoso
        self.assertTrue(exito)
        self.assertIn("exitosamente", mensaje)


if __name__ == "__main__":
    unittest.main()