"""
Tests para verificar que las correcciones del módulo obras funcionan correctamente
"""

import unittest
import sys
import os

# Agregar el directorio raíz al path de Python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

class TestObrasCorreccion(unittest.TestCase):
    """Tests para verificar las correcciones en el módulo de obras"""
    
    def test_obras_model_importacion(self):
        """Verifica que el modelo de obras se puede importar sin errores"""
        try:
            from rexus.modules.obras.model import ObrasModel
            self.assertTrue(ObrasModel is not None)
            print("OK ObrasModel se importa correctamente")
        except Exception as e:
            self.fail(f"Error importando ObrasModel: {e}")
    
    def test_obras_view_importacion(self):
        """Verifica que la vista de obras se puede importar sin errores"""
        try:
            from rexus.modules.obras.view import ObrasView
            self.assertTrue(ObrasView is not None)
            print("OK ObrasView se importa correctamente")
        except Exception as e:
            self.fail(f"Error importando ObrasView: {e}")
    
    def test_verificacion_tablas_no_bloquea(self):
        """Verifica que la verificación de tablas no bloquea la instanciación del modelo"""
        try:
            from rexus.modules.obras.model import ObrasModel
            
            # Instanciar modelo sin conexión a BD (debería funcionar sin bloquear)
            modelo = ObrasModel(db_connection=None)
            self.assertIsNotNone(modelo)
            
            # Verificar que tiene los atributos necesarios
            self.assertTrue(hasattr(modelo, 'tabla_obras'))
            self.assertTrue(hasattr(modelo, 'tabla_detalles_obra'))
            print("OK Verificación de tablas no bloquea la instanciación")
            
        except Exception as e:
            self.fail(f"Error en verificación de tablas: {e}")
    
    def test_permisos_view_obras_existe(self):
        """Verifica que existe el permiso VIEW_OBRAS en el sistema de autenticación"""
        try:
            from rexus.core.auth_manager import Permission
            
            # Verificar que existe el permiso VIEW_OBRAS
            self.assertTrue(hasattr(Permission, 'VIEW_OBRAS'))
            self.assertEqual(Permission.VIEW_OBRAS.value, 'view_obras')
            print("OK Permiso VIEW_OBRAS existe y está configurado correctamente")
            
        except Exception as e:
            self.fail(f"Error verificando permisos: {e}")
    
    def test_auth_manager_check_permission(self):
        """Verifica que AuthManager tiene el método check_permission"""
        try:
            from rexus.core.auth_manager import AuthManager, Permission
            
            # Verificar que el método existe
            self.assertTrue(hasattr(AuthManager, 'check_permission'))
            self.assertTrue(callable(getattr(AuthManager, 'check_permission')))
            
            # Probar llamada al método (debería devolver False si no hay usuario autenticado)
            resultado = AuthManager.check_permission(Permission.VIEW_OBRAS)
            self.assertIsInstance(resultado, bool)
            print("OK AuthManager.check_permission funciona correctamente")
            
        except Exception as e:
            self.fail(f"Error verificando AuthManager: {e}")
    
    def test_obras_view_tiene_verificacion_acceso(self):
        """Verifica que ObrasView tiene el método de verificación de acceso"""
        try:
            from rexus.modules.obras.view import ObrasView
            
            # Verificar que el método de verificación existe
            self.assertTrue(hasattr(ObrasView, '_verificar_acceso_obras'))
            print("OK ObrasView tiene método de verificación de acceso")
            
        except Exception as e:
            self.fail(f"Error verificando método de acceso: {e}")
    
    def test_controller_obras_importacion(self):
        """Verifica que el controlador de obras se puede importar"""
        try:
            from rexus.modules.obras.controller import ObrasController
            self.assertTrue(ObrasController is not None)
            print("OK ObrasController se importa correctamente")
        except Exception as e:
            self.fail(f"Error importando ObrasController: {e}")

if __name__ == '__main__':
    print("Ejecutando tests de correcciones del modulo obras...")
    unittest.main(verbosity=2)