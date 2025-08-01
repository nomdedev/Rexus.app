#!/usr/bin/env python3
"""
Script de debugging para identificar problemas en la carga de módulos.
Simula la carga de módulos como lo haría la aplicación real.
"""

import sys
import os
from pathlib import Path

# Configurar entorno
root_dir = Path(__file__).parent
os.chdir(root_dir)
sys.path.insert(0, str(root_dir))

# Cargar variables de entorno
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("Variables de entorno cargadas desde .env")
except ImportError:
    print("Warning: python-dotenv no instalado")

def test_module_creation():
    """Prueba la creación de módulos individuales."""
    print("=== DEBUGGING DE CARGA DE MÓDULOS ===")
    print()
    
    try:
        # Importar dependencies necesarias
        from rexus.core.module_manager import ModuleManager
        from rexus.core.database import InventarioDatabaseConnection
        
        # Crear gestor de módulos
        module_manager = ModuleManager()
        
        # Crear conexión a BD (puede fallar, pero eso está OK)
        try:
            db_connection = InventarioDatabaseConnection()
            print("OK - Conexion a BD exitosa")
        except Exception as e:
            print(f"WARNING - Sin conexion BD (usando modo demo): {e}")
            db_connection = None
        
        print()
        
        # Módulos a probar
        modulos_a_probar = [
            {
                'name': 'Inventario',
                'model': 'rexus.modules.inventario.model.InventarioModel',
                'view': 'rexus.modules.inventario.view.InventarioView',
                'controller': 'rexus.modules.inventario.controller.InventarioController'
            },
            {
                'name': 'Herrajes',
                'model': 'rexus.modules.herrajes.model.HerrajesModel',
                'view': 'rexus.modules.herrajes.view.HerrajesView',
                'controller': 'rexus.modules.herrajes.controller.HerrajesController'
            },
            {
                'name': 'Configuración',
                'model': 'rexus.modules.configuracion.model.ConfiguracionModel',
                'view': 'rexus.modules.configuracion.view.ConfiguracionView',
                'controller': 'rexus.modules.configuracion.controller.ConfiguracionController'
            },
            {
                'name': 'Obras',
                'model': 'rexus.modules.obras.model.ObrasModel',
                'view': 'rexus.modules.obras.view.ObrasView',
                'controller': 'rexus.modules.obras.controller.ObrasController'
            }
        ]
        
        for modulo in modulos_a_probar:
            print(f"--- PROBANDO MÓDULO: {modulo['name']} ---")
            
            try:
                # Importar clases
                model_module, model_class_name = modulo['model'].rsplit('.', 1)
                view_module, view_class_name = modulo['view'].rsplit('.', 1)
                controller_module, controller_class_name = modulo['controller'].rsplit('.', 1)
                
                # Importar y obtener clases
                model_mod = __import__(model_module, fromlist=[model_class_name])
                model_class = getattr(model_mod, model_class_name)
                
                view_mod = __import__(view_module, fromlist=[view_class_name])
                view_class = getattr(view_mod, view_class_name)
                
                controller_mod = __import__(controller_module, fromlist=[controller_class_name])
                controller_class = getattr(controller_mod, controller_class_name)
                
                print(f"OK - Importaciones OK para {modulo['name']}")
                
                # Crear widget usando module_manager
                widget = module_manager.create_module_safely(
                    module_name=modulo['name'],
                    model_class=model_class,
                    view_class=view_class,
                    controller_class=controller_class,
                    db_connection=db_connection,
                    fallback_callback=None
                )
                
                if widget:
                    print(f"OK - {modulo['name']}: Widget creado exitosamente")
                else:
                    print(f"ERROR - {modulo['name']}: Widget es None")
                    
            except Exception as e:
                print(f"ERROR - {modulo['name']}: Error - {e}")
                import traceback
                traceback.print_exc()
            
            print()
        
        # Mostrar resumen
        print("=== RESUMEN DE CARGA DE MODULOS ===")
        for module_name, module_info in module_manager.loaded_modules.items():
            status = module_info.get('status', 'unknown')
            if status == 'loaded':
                print(f"OK - {module_name}: Cargado exitosamente")
            elif status == 'failed':
                error = module_info.get('error', 'Error desconocido')
                print(f"ERROR - {module_name}: Fallo - {error}")
                
    except Exception as e:
        print(f"Error general: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_module_creation()