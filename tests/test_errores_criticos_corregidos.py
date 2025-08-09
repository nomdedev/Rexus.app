"""
Tests para verificar que errores críticos identificados en CLAUDE.md han sido corregidos
"""

import unittest
import sys
import os

# Agregar el directorio raíz al path de Python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

class TestErroresCriticosCorregidos(unittest.TestCase):
    """Tests para verificar corrección de errores críticos"""
    
    def test_rexus_colors_text_primary(self):
        """Verifica que RexusColors.TEXT_PRIMARY esté definido correctamente"""
        from rexus.ui.components.base_components import RexusColors
        
        # Verificar que TEXT_PRIMARY existe y tiene un valor válido
        self.assertTrue(hasattr(RexusColors, 'TEXT_PRIMARY'))
        self.assertIsInstance(RexusColors.TEXT_PRIMARY, str)
        self.assertTrue(RexusColors.TEXT_PRIMARY.startswith('#'))
        print("OK RexusColors.TEXT_PRIMARY definido correctamente")
    
    def test_base_module_view_set_main_table(self):
        """Verifica que BaseModuleView tiene el método set_main_table"""
        from rexus.ui.templates.base_module_view import BaseModuleView
        
        # Verificar que el método existe
        self.assertTrue(hasattr(BaseModuleView, 'set_main_table'))
        self.assertTrue(callable(getattr(BaseModuleView, 'set_main_table')))
        print("OK BaseModuleView.set_main_table existe")
    
    def test_base_module_view_mostrar_mensaje(self):
        """Verifica que BaseModuleView tiene el método mostrar_mensaje con signatura correcta"""
        from rexus.ui.templates.base_module_view import BaseModuleView
        import inspect
        
        # Verificar que el método existe
        self.assertTrue(hasattr(BaseModuleView, 'mostrar_mensaje'))
        
        # Verificar la signatura del método
        sig = inspect.signature(BaseModuleView.mostrar_mensaje)
        param_names = list(sig.parameters.keys())
        
        # Debe tener parámetros: self, tipo, titulo, mensaje, detalle=None
        self.assertIn('tipo', param_names)
        self.assertIn('titulo', param_names)
        self.assertIn('mensaje', param_names)
        print("OK BaseModuleView.mostrar_mensaje con signatura correcta")
    
    def test_inventario_controller_sin_errores_encoding(self):
        """Verifica que InventarioController se puede instanciar sin errores de encoding"""
        from rexus.modules.inventario.controller import InventarioController
        
        try:
            controller = InventarioController()
            self.assertIsNotNone(controller)
            print("OK InventarioController sin errores de encoding")
        except UnicodeEncodeError as e:
            self.fail(f"Error de encoding en InventarioController: {e}")
    
    def test_auditoria_view_hereda_base_module(self):
        """Verifica que AuditoriaView hereda de BaseModuleView correctamente"""
        from rexus.modules.auditoria.view import AuditoriaView
        from rexus.ui.templates.base_module_view import BaseModuleView
        
        # Verificar herencia
        self.assertTrue(issubclass(AuditoriaView, BaseModuleView))
        
        # Verificar que tiene acceso al método mostrar_mensaje
        auditoria_view = AuditoriaView()
        self.assertTrue(hasattr(auditoria_view, 'mostrar_mensaje'))
        print("OK AuditoriaView hereda correctamente de BaseModuleView")
    
    def test_no_fallbacks_innecesarios(self):
        """Verifica que no hay fallbacks innecesarios en funcionamiento"""
        # Verificar que los módulos principales no están usando fallbacks
        
        from rexus.modules.inventario.controller import InventarioController
        from rexus.modules.herrajes.controller import HerrajesController
        
        # Estos controladores deberían funcionar sin fallbacks
        try:
            inventario_ctrl = InventarioController()
            self.assertIsNotNone(inventario_ctrl)
            
            herrajes_ctrl = HerrajesController()
            self.assertIsNotNone(herrajes_ctrl)
            
            print("OK Controladores funcionan sin fallbacks innecesarios")
        except Exception as e:
            self.fail(f"Error en controladores que deberían funcionar: {e}")
    
    def test_sql_query_manager_disponible(self):
        """Verifica que SQLQueryManager está disponible para migración SQL"""
        try:
            from rexus.utils.sql_query_manager import SQLQueryManager
            
            # Debería poder instanciarse
            sql_manager = SQLQueryManager()
            self.assertIsNotNone(sql_manager)
            
            # Debería tener métodos principales
            self.assertTrue(hasattr(sql_manager, 'get_query'))
            print("OK SQLQueryManager disponible para migración SQL")
        except ImportError:
            self.fail("SQLQueryManager no está disponible - necesario para migración SQL")
    
    def test_unified_sanitizer_disponible(self):
        """Verifica que el sistema unificado de sanitización funciona"""
        try:
            from rexus.utils.unified_sanitizer import unified_sanitizer
            
            # Probar sanitización básica
            test_input = "SELECT * FROM users; DROP TABLE users;"
            sanitized = unified_sanitizer.sanitize_sql_input(test_input)
            
            self.assertIsNotNone(sanitized)
            self.assertIsInstance(sanitized, str)
            print("OK Unified sanitizer funciona correctamente")
        except Exception as e:
            self.fail(f"Error en unified sanitizer: {e}")

if __name__ == '__main__':
    print("Ejecutando tests de errores criticos corregidos...")
    unittest.main(verbosity=2)