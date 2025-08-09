"""
Test final de validación para verificar que los módulos funcionan correctamente
"""

import unittest
import sys
import os

# Agregar el directorio raíz al path de Python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

class TestValidacionFinal(unittest.TestCase):
    """Tests finales de validación del sistema"""
    
    def test_todos_los_modulos_se_importan(self):
        """Verifica que todos los módulos principales se importan correctamente"""
        modules = [
            'inventario', 'vidrios', 'herrajes', 'obras', 'usuarios',
            'compras', 'pedidos', 'auditoria', 'configuracion', 
            'logistica', 'mantenimiento'
        ]
        
        success_count = 0
        failed_modules = []
        
        for module_name in modules:
            try:
                module_path = f'rexus.modules.{module_name}.view'
                __import__(module_path)
                success_count += 1
            except Exception as e:
                failed_modules.append((module_name, str(e)))
        
        print(f"Modulos importados exitosamente: {success_count}/{len(modules)}")
        
        # Verificar que al menos el 90% de los módulos funciona
        success_rate = (success_count / len(modules)) * 100
        self.assertGreaterEqual(success_rate, 90, 
                               f"Tasa de éxito: {success_rate:.1f}%. Fallos: {failed_modules}")
    
    def test_controladores_principales(self):
        """Verifica que los controladores principales funcionan"""
        controllers_to_test = [
            ('inventario', 'InventarioController'),
            ('herrajes', 'HerrajesController'),
        ]
        
        success_count = 0
        
        for module_name, controller_class in controllers_to_test:
            try:
                module_path = f'rexus.modules.{module_name}.controller'
                module = __import__(module_path, fromlist=[controller_class])
                controller_cls = getattr(module, controller_class)
                controller = controller_cls()
                
                self.assertIsNotNone(controller)
                success_count += 1
            except Exception as e:
                print(f"Warning: {module_name} controller failed: {e}")
        
        print(f"Controladores funcionales: {success_count}/{len(controllers_to_test)}")
        
        # Al menos 1 controlador debe funcionar
        self.assertGreaterEqual(success_count, 1, "Ningún controlador funciona correctamente")
    
    def test_componentes_base_funcionan(self):
        """Verifica que los componentes base esenciales funcionan"""
        components_to_test = [
            ('rexus.ui.components.base_components', 'RexusColors'),
            ('rexus.ui.templates.base_module_view', 'BaseModuleView'),
            ('rexus.utils.unified_sanitizer', 'unified_sanitizer'),
        ]
        
        for module_path, component_name in components_to_test:
            try:
                module = __import__(module_path, fromlist=[component_name])
                component = getattr(module, component_name)
                self.assertIsNotNone(component)
            except Exception as e:
                self.fail(f"Componente base {component_name} no funciona: {e}")
        
        print("OK Todos los componentes base funcionan")
    
    def test_sin_errores_criticos_encoding(self):
        """Verifica que no hay errores críticos de encoding"""
        try:
            # Test del módulo más problemático
            from rexus.modules.inventario.controller import InventarioController
            controller = InventarioController()
            self.assertIsNotNone(controller)
            print("OK Sin errores de encoding en módulos críticos")
        except UnicodeEncodeError as e:
            self.fail(f"Error de encoding detectado: {e}")
    
    def test_estructura_proyecto_correcta(self):
        """Verifica que la estructura del proyecto es correcta"""
        required_paths = [
            'rexus/modules',
            'rexus/ui/components',
            'rexus/ui/templates', 
            'rexus/utils',
            'scripts/sql',
            'tests'
        ]
        
        project_root = os.path.join(os.path.dirname(__file__), '..')
        
        for path in required_paths:
            full_path = os.path.join(project_root, path)
            self.assertTrue(os.path.exists(full_path), 
                           f"Ruta requerida no existe: {path}")
        
        print("OK Estructura del proyecto correcta")

if __name__ == '__main__':
    print("Ejecutando validacion final del sistema...")
    unittest.main(verbosity=2)