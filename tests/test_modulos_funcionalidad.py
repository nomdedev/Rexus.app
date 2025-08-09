"""
Tests de funcionalidad para módulos de Rexus.app
Verifica que los módulos principales funcionen correctamente
"""

import unittest
import sys
import os

# Agregar el directorio raíz al path de Python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

class TestModulosFuncionalidad(unittest.TestCase):
    """Tests para verificar la funcionalidad básica de los módulos"""
    
    def test_importacion_modulos(self):
        """Verifica que todos los módulos principales se puedan importar"""
        modules = [
            'inventario', 'vidrios', 'herrajes', 'obras', 'usuarios',
            'compras', 'pedidos', 'auditoria', 'configuracion', 
            'logistica', 'mantenimiento'
        ]
        
        failed_imports = []
        
        for module_name in modules:
            try:
                # Intentar importar la vista del módulo
                module_path = f'rexus.modules.{module_name}.view'
                __import__(module_path)
                print(f"OK {module_name}: OK")
            except Exception as e:
                failed_imports.append((module_name, str(e)))
                print(f"ERROR {module_name}: ERROR - {e}")
        
        self.assertEqual(len(failed_imports), 0, 
                        f"Falló importación de módulos: {failed_imports}")
    
    def test_controladores_basicos(self):
        """Verifica que los controladores se puedan instanciar"""
        # Test del controlador de inventario que tiene más complejidad
        try:
            from rexus.modules.inventario.controller import InventarioController
            controller = InventarioController()
            self.assertIsNotNone(controller)
            print("OK InventarioController: OK")
        except Exception as e:
            self.fail(f"Error instanciando InventarioController: {e}")
    
    def test_modelos_basicos(self):
        """Verifica que los modelos principales se puedan importar"""
        models = ['inventario', 'vidrios', 'herrajes', 'obras', 'usuarios']
        
        failed_models = []
        
        for model_name in models:
            try:
                module_path = f'rexus.modules.{model_name}.model'
                __import__(module_path)
                print(f"OK {model_name} model: OK")
            except Exception as e:
                failed_models.append((model_name, str(e)))
                print(f"ERROR {model_name} model: ERROR - {e}")
        
        self.assertEqual(len(failed_models), 0, 
                        f"Falló importación de modelos: {failed_models}")
    
    def test_base_module_view_methods(self):
        """Verifica que BaseModuleView tiene los métodos necesarios"""
        try:
            from rexus.ui.templates.base_module_view import BaseModuleView
            
            # Verificar métodos críticos
            required_methods = ['set_main_table', 'mostrar_mensaje']
            
            missing_methods = []
            for method in required_methods:
                if not hasattr(BaseModuleView, method):
                    missing_methods.append(method)
            
            self.assertEqual(len(missing_methods), 0, 
                           f"Métodos faltantes en BaseModuleView: {missing_methods}")
            print("OK BaseModuleView metodos: OK")
            
        except Exception as e:
            self.fail(f"Error verificando BaseModuleView: {e}")
    
    def test_rexus_colors_constants(self):
        """Verifica que RexusColors tiene las constantes necesarias"""
        try:
            from rexus.ui.components.base_components import RexusColors
            
            required_colors = ['TEXT_PRIMARY', 'BACKGROUND', 'BORDER_LIGHT']
            
            missing_colors = []
            for color in required_colors:
                if not hasattr(RexusColors, color):
                    missing_colors.append(color)
            
            self.assertEqual(len(missing_colors), 0, 
                           f"Colores faltantes en RexusColors: {missing_colors}")
            print("OK RexusColors constantes: OK")
            
        except Exception as e:
            self.fail(f"Error verificando RexusColors: {e}")

if __name__ == '__main__':
    print("Ejecutando tests de funcionalidad de modulos...")
    unittest.main(verbosity=2)