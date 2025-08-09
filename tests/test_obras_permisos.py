"""
Test específico para verificar el sistema de permisos del módulo obras
"""

import unittest
import sys
import os

# Agregar el directorio raíz al path de Python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

class TestObrasPermisos(unittest.TestCase):
    """Tests para el sistema de permisos de obras"""
    
    def test_verificacion_permisos_funciona(self):
        """Verifica que la verificación de permisos funciona correctamente"""
        from rexus.core.auth_manager import AuthManager, Permission, UserRole
        
        # Test con ADMIN (debería tener acceso)
        AuthManager.set_current_user_role(UserRole.ADMIN)
        resultado_admin = AuthManager.check_permission(Permission.VIEW_OBRAS)
        self.assertTrue(resultado_admin, "ADMIN debería tener acceso a obras")
        
        # Test con VIEWER (debería tener acceso)
        AuthManager.set_current_user_role(UserRole.VIEWER)  
        resultado_viewer = AuthManager.check_permission(Permission.VIEW_OBRAS)
        self.assertTrue(resultado_viewer, "VIEWER debería tener acceso a obras")
        
        # Test sin usuario autenticado (no debería tener acceso)
        AuthManager.current_user_role = None
        resultado_sin_usuario = AuthManager.check_permission(Permission.VIEW_OBRAS)
        self.assertFalse(resultado_sin_usuario, "Usuario no autenticado NO debería tener acceso")
        
        print("OK Sistema de permisos funciona correctamente")
    
    def test_metodo_verificacion_acceso_obras(self):
        """Verifica que el método _verificar_acceso_obras funciona"""
        from rexus.modules.obras.view import ObrasView
        from rexus.core.auth_manager import AuthManager, UserRole
        
        # Mock temporal - crear una vista sin inicializar completamente
        class TestObrasView(ObrasView):
            def __init__(self):
                # No llamar super().__init__() para evitar inicialización completa
                pass
        
        vista_test = TestObrasView()
        
        # Test con usuario autenticado (debería permitir acceso)
        AuthManager.set_current_user_role(UserRole.ADMIN)
        resultado_con_permisos = vista_test._verificar_acceso_obras()
        self.assertTrue(resultado_con_permisos, "Usuario con permisos debería tener acceso")
        
        # Test sin usuario autenticado
        AuthManager.current_user_role = None
        # Este test mostrará un diálogo de error, pero eso es el comportamiento esperado
        
        print("OK Método de verificación de acceso funciona")
    
    def test_configuracion_permisos_por_rol(self):
        """Verifica que la configuración de permisos por rol es correcta"""
        from rexus.core.auth_manager import AuthManager, Permission, UserRole
        
        # Verificar que ADMIN tiene todos los permisos
        AuthManager.set_current_user_role(UserRole.ADMIN)
        self.assertTrue(AuthManager.check_permission(Permission.VIEW_OBRAS))
        self.assertTrue(AuthManager.check_permission(Permission.CREATE_OBRAS))
        self.assertTrue(AuthManager.check_permission(Permission.UPDATE_OBRAS))
        self.assertTrue(AuthManager.check_permission(Permission.DELETE_OBRAS))
        
        # Verificar que VIEWER solo tiene permisos de visualización
        AuthManager.set_current_user_role(UserRole.VIEWER)
        self.assertTrue(AuthManager.check_permission(Permission.VIEW_OBRAS))
        self.assertFalse(AuthManager.check_permission(Permission.CREATE_OBRAS))
        self.assertFalse(AuthManager.check_permission(Permission.UPDATE_OBRAS))
        self.assertFalse(AuthManager.check_permission(Permission.DELETE_OBRAS))
        
        print("OK Configuración de permisos por rol es correcta")

if __name__ == '__main__':
    print("Ejecutando tests de permisos del modulo obras...")
    unittest.main(verbosity=2)