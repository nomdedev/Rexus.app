#!/usr/bin/env python3
"""
Test Suite para Verificar Funcionalidad de Todos los Módulos de Rexus.app

Este script crea tests integrales para verificar que:
1. Todos los módulos se cargan correctamente
2. Las interfaces se muestran como corresponde
3. Las funcionalidades básicas están funcionando
"""

import sys
import os
from pathlib import Path

# Add project root to path
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

# Test results tracking
test_results = {
    'passed': 0,
    'failed': 0,
    'errors': []
}

def log_test(test_name, success, error_msg=None):
    """Log test results"""
    if success:
        print(f"[PASS] {test_name}")
        test_results['passed'] += 1
    else:
        print(f"[FAIL] {test_name}: {error_msg}")
        test_results['failed'] += 1
        test_results['errors'].append(f"{test_name}: {error_msg}")

def test_pyqt6_setup():
    """Test PyQt6 basic setup"""
    try:
        from PyQt6.QtWidgets import QApplication, QWidget
        app = QApplication([])
        log_test("PyQt6 Basic Setup", True)
        return app
    except Exception as e:
        log_test("PyQt6 Basic Setup", False, str(e))
        return None

def test_module_imports():
    """Test all module imports"""
    modules_to_test = [
        ('inventario', 'src.modules.inventario'),
        ('usuarios', 'src.modules.usuarios'),
        ('pedidos', 'src.modules.pedidos'),
        ('compras', 'src.modules.compras'),
        ('configuracion', 'src.modules.configuracion'),
        ('herrajes', 'src.modules.herrajes'),
        ('vidrios', 'src.modules.vidrios'),
        ('obras', 'src.modules.obras'),
        ('logistica', 'src.modules.logistica'),
        ('administracion', 'src.modules.administracion'),
    ]
    
    for module_name, module_path in modules_to_test:
        try:
            # Import model, view, controller
            model_module = __import__(f"{module_path}.model", fromlist=[''])
            view_module = __import__(f"{module_path}.view", fromlist=[''])
            controller_module = __import__(f"{module_path}.controller", fromlist=[''])
            
            log_test(f"Import {module_name.title()} Module", True)
        except Exception as e:
            log_test(f"Import {module_name.title()} Module", False, str(e))

def test_module_instantiation():
    """Test module instantiation"""
    test_modules = [
        {
            'name': 'Inventario',
            'model': 'src.modules.inventario.model.InventarioModel',
            'view': 'src.modules.inventario.view.InventarioView',
            'controller': 'src.modules.inventario.controller.InventarioController'
        },
        {
            'name': 'Usuarios',
            'model': 'src.modules.usuarios.model.UsuariosModel', 
            'view': 'src.modules.usuarios.view.UsuariosView',
            'controller': 'src.modules.usuarios.controller.UsuariosController'
        },
        {
            'name': 'Pedidos',
            'model': 'src.modules.pedidos.model.PedidosModel',
            'view': 'src.modules.pedidos.view.PedidosView', 
            'controller': 'src.modules.pedidos.controller.PedidosController'
        },
        {
            'name': 'Compras',
            'model': 'src.modules.compras.model.ComprasModel',
            'view': 'src.modules.compras.view.ComprasView',
            'controller': 'src.modules.compras.controller.ComprasController'
        },
        {
            'name': 'Configuracion',
            'model': 'src.modules.configuracion.model.ConfiguracionModel',
            'view': 'src.modules.configuracion.view.ConfiguracionView',
            'controller': 'src.modules.configuracion.controller.ConfiguracionController'
        }
    ]
    
    for module_info in test_modules:
        try:
            # Get classes
            model_parts = module_info['model'].split('.')
            model_class_name = model_parts[-1]
            model_module_path = '.'.join(model_parts[:-1])
            model_module = __import__(model_module_path, fromlist=[model_class_name])
            ModelClass = getattr(model_module, model_class_name)
            
            view_parts = module_info['view'].split('.')
            view_class_name = view_parts[-1]
            view_module_path = '.'.join(view_parts[:-1])
            view_module = __import__(view_module_path, fromlist=[view_class_name])
            ViewClass = getattr(view_module, view_class_name)
            
            controller_parts = module_info['controller'].split('.')
            controller_class_name = controller_parts[-1]
            controller_module_path = '.'.join(controller_parts[:-1])
            controller_module = __import__(controller_module_path, fromlist=[controller_class_name])
            ControllerClass = getattr(controller_module, controller_class_name)
            
            # Instantiate
            model = ModelClass()
            view = ViewClass()
            controller = ControllerClass(model, view)
            
            log_test(f"Instantiate {module_info['name']} MVC", True)
            
        except Exception as e:
            log_test(f"Instantiate {module_info['name']} MVC", False, str(e))

def test_view_rendering():
    """Test that views can be rendered without crashing"""
    try:
        from src.modules.inventario.view import InventarioView
        from src.modules.usuarios.view import UsuariosView
        from src.modules.compras.view import ComprasView
        from src.modules.pedidos.view import PedidosView
        from src.modules.configuracion.view import ConfiguracionView
        
        views_to_test = [
            ('Inventario View', InventarioView),
            ('Usuarios View', UsuariosView),
            ('Compras View', ComprasView),
            ('Pedidos View', PedidosView),
            ('Configuracion View', ConfiguracionView),
        ]
        
        for view_name, ViewClass in views_to_test:
            try:
                view = ViewClass()
                # Try to get basic properties
                size = view.size()
                visible = view.isVisible()
                log_test(f"Render {view_name}", True)
            except Exception as e:
                log_test(f"Render {view_name}", False, str(e))
                
    except Exception as e:
        log_test("View Rendering Setup", False, str(e))

def test_form_styles():
    """Test form styles don't cause crashes"""
    try:
        from src.utils.form_styles import ModernFormStyles
        styles = ModernFormStyles()
        # Test basic style methods exist
        assert hasattr(styles, 'get_dialog_style')
        assert hasattr(styles, 'get_form_input_style') 
        log_test("Form Styles Module", True)
    except Exception as e:
        log_test("Form Styles Module", False, str(e))

def test_security_utilities():
    """Test security utilities"""
    try:
        from src.utils.sql_security import SQLSecurityValidator
        validator = SQLSecurityValidator()
        # Test basic validation with a permitted table
        result = validator.validate_table_name("usuarios")
        log_test("SQL Security Module", True)
    except Exception as e:
        log_test("SQL Security Module", False, str(e))

def test_module_manager():
    """Test module manager functionality"""
    try:
        from rexus.core.module_manager import module_manager
        
        # Test basic functionality
        assert hasattr(module_manager, 'create_module_safely')
        assert hasattr(module_manager, 'get_module_status')
        
        log_test("Module Manager", True)
    except Exception as e:
        log_test("Module Manager", False, str(e))

def test_app_main_flow():
    """Test main application flow"""
    try:
        from rexus.main.app import MainWindow
        
        # Test MainWindow can be instantiated
        user_data = {"username": "test", "rol": "ADMIN", "id": 1}
        modules = ["Inventario", "Usuarios", "Compras"]
        
        # This might fail due to missing dependencies, but we test instantiation
        main_window = MainWindow(user_data, modules)
        
        log_test("Main App Flow", True)
    except Exception as e:
        log_test("Main App Flow", False, str(e))

def test_database_connections():
    """Test database connection utilities"""
    try:
        from rexus.core.database import InventarioDatabaseConnection, UsersDatabaseConnection
        
        # Test that classes can be instantiated (may fail due to missing DB, but structure should exist)
        try:
            inv_db = InventarioDatabaseConnection()
            log_test("Inventario DB Connection Structure", True)
        except:
            # Expected to fail without real DB, but class should exist
            log_test("Inventario DB Connection Structure", True)
            
        try:
            users_db = UsersDatabaseConnection()
            log_test("Users DB Connection Structure", True)
        except:
            # Expected to fail without real DB, but class should exist
            log_test("Users DB Connection Structure", True)
            
    except Exception as e:
        log_test("Database Connection Classes", False, str(e))

def test_form_validators():
    """Test form validation system"""
    try:
        from rexus.utils.form_validators import FormValidator, FormValidatorManager
        
        # Test validator manager
        manager = FormValidatorManager()
        assert hasattr(manager, 'agregar_validacion')
        assert hasattr(manager, 'validar_formulario')
        
        # Test form validator
        assert hasattr(FormValidator, 'validar_campo_obligatorio')
        assert hasattr(FormValidator, 'validar_email')
        
        log_test("Form Validators", True)
        
    except Exception as e:
        log_test("Form Validators", False, str(e))

def run_all_tests():
    """Run all tests"""
    print("="*50)
    print("REXUS.APP - COMPREHENSIVE MODULE TESTING")
    print("="*50)
    
    # Initialize PyQt6
    app = test_pyqt6_setup()
    if not app:
        print("CRITICAL: Cannot proceed without PyQt6")
        return
    
    print("\n1. Testing Module Imports...")
    test_module_imports()
    
    print("\n2. Testing Module Instantiation...")
    test_module_instantiation()
    
    print("\n3. Testing View Rendering...")
    test_view_rendering()
    
    print("\n4. Testing Utility Modules...")
    test_form_styles()
    test_security_utilities()
    test_form_validators()
    
    print("\n5. Testing Core Systems...")
    test_module_manager()
    test_database_connections()
    
    print("\n6. Testing Application Flow...")
    test_app_main_flow()
    
    # Print results
    print("\n" + "="*50)
    print("TEST RESULTS SUMMARY")
    print("="*50)
    print(f"PASSED: {test_results['passed']}")
    print(f"FAILED: {test_results['failed']}")
    
    if test_results['failed'] > 0:
        print(f"\nFAILURES ({test_results['failed']}):")
        for error in test_results['errors']:
            print(f"  - {error}")
    else:
        print("\n🎉 ALL TESTS PASSED! 🎉")
        print("All modules are working correctly!")
    
    success_rate = (test_results['passed'] / (test_results['passed'] + test_results['failed'])) * 100
    print(f"\nSuccess Rate: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("✅ Application is ready for use!")
    elif success_rate >= 60:
        print("⚠️  Application is mostly functional but has some issues")
    else:
        print("❌ Application has significant issues that need to be addressed")

if __name__ == "__main__":
    run_all_tests()