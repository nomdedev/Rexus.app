#!/usr/bin/env python3
"""
Test Runtime Errors - Detecta errores específicos al ejecutar funcionalidades
"""

import sys
import traceback

def test_inventario_functionality():
    """Testa funcionalidades específicas del inventario."""
    print("\n" + "="*50)
    print("TESTING INVENTARIO FUNCTIONALITY")
    print("="*50)
    
    errors = []
    
    try:
        from rexus.modules.inventario.model import InventarioModel
        from rexus.modules.inventario.view import InventarioView
        from rexus.modules.inventario.controller import InventarioController
        
        print("1. Testing model methods...")
        model = InventarioModel()
        
        # Test métodos específicos que causan errores
        try:
            # Este método parece causar AttributeError
            if hasattr(model, 'consultas_manager'):
                if hasattr(model.consultas_manager, 'obtener_productos_paginados_inicial'):
                    print("  - obtener_productos_paginados_inicial: EXISTE")
                else:
                    errors.append("ConsultasManager NO tiene método 'obtener_productos_paginados_inicial'")
                    print("  - obtener_productos_paginados_inicial: FALTA")
            else:
                errors.append("InventarioModel NO tiene atributo 'consultas_manager'")
        except Exception as e:
            errors.append(f"Error testando consultas_manager: {e}")
        
        print("2. Testing view instantiation...")
        try:
            view = InventarioView()
            print("  - InventarioView instantiated OK")
            
            # Test si tiene funcionalidad de obras
            if hasattr(view, 'tab_widget') or hasattr(view, 'pestañas_obras'):
                print("  - Tiene pestañas de obras: SI")
            else:
                errors.append("InventarioView NO tiene pestañas para obras")
                print("  - Tiene pestañas de obras: NO")
                
            # Test botones específicos
            buttons_to_check = ['btn_separar', 'btn_separar_obra', 'btn_separar_material']
            for btn_name in buttons_to_check:
                if hasattr(view, btn_name):
                    print(f"  - Botón {btn_name}: EXISTE")
                else:
                    print(f"  - Botón {btn_name}: FALTA")
                    
        except Exception as e:
            errors.append(f"Error instantiating InventarioView: {e}")
            print(f"  ERROR: {e}")
        
        print("3. Testing controller functionality...")
        try:
            controller = InventarioController()
            print("  - InventarioController instantiated OK")
            
            # Test métodos específicos
            methods_to_check = ['separar_material_obra', 'cargar_inventario_paginado', 'conectar_senales']
            for method_name in methods_to_check:
                if hasattr(controller, method_name):
                    print(f"  - Método {method_name}: EXISTE")
                else:
                    print(f"  - Método {method_name}: FALTA")
                    
        except Exception as e:
            errors.append(f"Error instantiating InventarioController: {e}")
            print(f"  ERROR: {e}")
        
    except Exception as e:
        errors.append(f"Error importing inventario modules: {e}")
        print(f"IMPORT ERROR: {e}")
    
    return errors

def test_compras_functionality():
    """Testa funcionalidades específicas de compras."""
    print("\n" + "="*50)
    print("TESTING COMPRAS FUNCTIONALITY")
    print("="*50)
    
    errors = []
    
    try:
        from rexus.modules.compras.model import ComprasModel
        from rexus.modules.compras.controller import ComprasController
        
        # Test views diferentes
        view_modules = [
            ('view', 'ComprasView'),
            ('view_complete', 'ComprasViewComplete'),
        ]
        
        for view_module, view_class in view_modules:
            try:
                module = __import__(f'rexus.modules.compras.{view_module}', fromlist=[view_class])
                view_cls = getattr(module, view_class)
                print(f"  - {view_class}: EXISTE")
            except Exception as e:
                errors.append(f"Error importing {view_class}: {e}")
                print(f"  - {view_class}: ERROR - {e}")
        
        print("Testing model methods...")
        model = ComprasModel()
        
        # Test métodos que causan problemas SQL
        sql_methods = ['obtener_todas_compras', 'obtener_estadisticas_compras']
        for method_name in sql_methods:
            if hasattr(model, method_name):
                print(f"  - Método {method_name}: EXISTE")
                try:
                    # Intentar ejecutar sin conexión real
                    print(f"    (Testing {method_name} execution would require DB)")
                except Exception as e:
                    errors.append(f"Error in {method_name}: {e}")
            else:
                errors.append(f"ComprasModel NO tiene método '{method_name}'")
        
    except Exception as e:
        errors.append(f"Error testing compras: {e}")
        print(f"ERROR: {e}")
    
    return errors

def test_administracion_functionality():
    """Testa funcionalidades de administración."""
    print("\n" + "="*50)
    print("TESTING ADMINISTRACION FUNCTIONALITY") 
    print("="*50)
    
    errors = []
    
    try:
        from rexus.modules.administracion.model import AdministracionModel
        from rexus.modules.administracion.view import AdministracionViewFuncional
        from rexus.modules.administracion.controller import AdministracionController
        
        print("Testing model...")
        model = AdministracionModel()
        
        # Test métodos específicos de administración
        admin_methods = [
            'obtener_estadisticas_generales',
            'obtener_usuarios_sistema', 
            'generar_reporte_actividad',
            'obtener_configuracion_sistema'
        ]
        
        for method_name in admin_methods:
            if hasattr(model, method_name):
                print(f"  - Método {method_name}: EXISTE")
            else:
                errors.append(f"AdministracionModel NO tiene método '{method_name}'")
                print(f"  - Método {method_name}: FALTA")
        
        print("Testing view...")
        view = AdministracionViewFuncional()
        print("  - AdministracionViewFuncional instantiated OK")
        
        # Test si tiene herramientas administrativas específicas
        admin_tools = ['panel_usuarios', 'panel_sistema', 'panel_reportes', 'panel_configuracion']
        for tool_name in admin_tools:
            if hasattr(view, tool_name):
                print(f"  - Panel {tool_name}: EXISTE")
            else:
                print(f"  - Panel {tool_name}: FALTA")
        
    except Exception as e:
        errors.append(f"Error testing administracion: {e}")
        print(f"ERROR: {e}")
    
    return errors

def test_auditoria_functionality():
    """Testa funcionalidades de auditoría."""
    print("\n" + "="*50)
    print("TESTING AUDITORIA FUNCTIONALITY")
    print("="*50)
    
    errors = []
    
    try:
        from rexus.modules.auditoria.model import AuditoriaModel
        from rexus.modules.auditoria.view import AuditoriaView
        from rexus.modules.auditoria.controller import AuditoriaController
        
        print("Testing model...")
        model = AuditoriaModel()
        
        # Test métodos de auditoría
        audit_methods = [
            'obtener_registros_auditoria',
            'registrar_evento',
            'obtener_estadisticas_auditoria',
            'filtrar_registros',
            'exportar_auditoria'
        ]
        
        for method_name in audit_methods:
            if hasattr(model, method_name):
                print(f"  - Método {method_name}: EXISTE")
            else:
                errors.append(f"AuditoriaModel NO tiene método '{method_name}'")
                print(f"  - Método {method_name}: FALTA")
        
        print("Testing view...")
        view = AuditoriaView()
        print("  - AuditoriaView instantiated OK")
        
        # Test características específicas de auditoría
        audit_features = ['tabla_auditoria', 'filtros_avanzados', 'exportar_reportes']
        for feature_name in audit_features:
            if hasattr(view, feature_name):
                print(f"  - Feature {feature_name}: EXISTE")
            else:
                print(f"  - Feature {feature_name}: FALTA")
        
    except Exception as e:
        errors.append(f"Error testing auditoria: {e}")
        print(f"ERROR: {e}")
    
    return errors

def main():
    """Función principal."""
    print("TEST DE ERRORES RUNTIME - REXUS.APP")
    print("="*60)
    
    all_errors = {}
    
    # Test cada módulo
    tests = [
        ("INVENTARIO", test_inventario_functionality),
        ("COMPRAS", test_compras_functionality),
        ("ADMINISTRACION", test_administracion_functionality),
        ("AUDITORIA", test_auditoria_functionality)
    ]
    
    for module_name, test_func in tests:
        try:
            errors = test_func()
            if errors:
                all_errors[module_name] = errors
        except Exception as e:
            all_errors[module_name] = [f"Test function error: {e}"]
    
    # Resumen final
    print("\n" + "="*60)
    print("RESUMEN DE PROBLEMAS FUNCIONALES")
    print("="*60)
    
    if all_errors:
        total_errors = sum(len(errors) for errors in all_errors.values())
        print(f"TOTAL PROBLEMAS ENCONTRADOS: {total_errors}")
        
        for module, errors in all_errors.items():
            print(f"\n{module} ({len(errors)} problemas):")
            for i, error in enumerate(errors, 1):
                print(f"  {i}. {error}")
    else:
        print("NO SE ENCONTRARON PROBLEMAS FUNCIONALES")
    
    # Guardar resultados
    with open("runtime_test_results.txt", "w", encoding="utf-8") as f:
        f.write("RESULTADOS TEST RUNTIME - REXUS.APP\n")
        f.write("="*50 + "\n\n")
        
        if all_errors:
            for module, errors in all_errors.items():
                f.write(f"\n{module}:\n")
                f.write("-" * len(module) + "\n")
                for i, error in enumerate(errors, 1):
                    f.write(f"{i}. {error}\n")
        else:
            f.write("NO PROBLEMS FOUND\n")
    
    print(f"\nResultados guardados en: runtime_test_results.txt")
    return all_errors

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"ERROR EN TEST: {e}")
        traceback.print_exc()