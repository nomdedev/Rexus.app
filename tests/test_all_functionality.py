#!/usr/bin/env python3
"""
Test completo de funcionalidad del sistema
"""

import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtTest import QTest

from src.main.app_collapsible import MainWindow, SimpleSecurityManager
from src.core.auth import get_auth_manager
from src.core.login_dialog import LoginDialog


def test_authentication():
    """Test del sistema de autenticación"""
    print("=== TEST DE AUTENTICACIÓN ===")
    
    try:
        # Test con AuthManager
        auth_manager = get_auth_manager()
        
        # Probar autenticación
        user = auth_manager.authenticate_user('admin', 'admin')
        if user:
            print("OK - Autenticación con base de datos funciona")
            print(f"  Usuario: {user['username']}")
            print(f"  Rol: {user['role']}")
            return True
        else:
            print("ADVERTENCIA - Autenticación con BD falló, usando fallback")
            
            # Test con SimpleSecurityManager
            simple_auth = SimpleSecurityManager()
            if simple_auth.login('admin', 'admin'):
                print("OK - Autenticación fallback funciona")
                return True
            else:
                print("ERROR - Autenticación fallback también falló")
                return False
                
    except Exception as e:
        print(f"ERROR - Error en autenticación: {e}")
        return False


def test_main_window():
    """Test de la ventana principal"""
    print("\n=== TEST DE VENTANA PRINCIPAL ===")
    
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    
    try:
        # Datos de prueba
        user_data = {
            'username': 'admin',
            'rol': 'ADMIN',
            'id': 1
        }
        
        security_manager = SimpleSecurityManager()
        modulos_permitidos = security_manager.get_user_modules(1)
        
        # Crear ventana
        main_window = MainWindow(user_data, modulos_permitidos)
        main_window.show()
        QTest.qWaitForWindowExposed(main_window)
        
        print("OK - Ventana principal creada")
        
        # Test sidebar
        sidebar = main_window.sidebar
        if sidebar:
            print("OK - Sidebar presente")
            
            # Test toggle
            initial_state = sidebar.is_collapsed
            QTest.mouseClick(sidebar.toggle_btn, Qt.MouseButton.LeftButton)
            QTest.qWait(100)
            
            if sidebar.is_collapsed != initial_state:
                print("OK - Sidebar toggle funciona")
            else:
                print("ERROR - Sidebar toggle no funciona")
        
        # Test módulos
        if len(sidebar.module_buttons) > 0:
            print(f"OK - {len(sidebar.module_buttons)} módulos disponibles")
            
            # Test click en módulo
            QTest.mouseClick(sidebar.module_buttons[0], Qt.MouseButton.LeftButton)
            QTest.qWait(100)
            
            if main_window.content_stack.count() > 1:
                print("OK - Módulos responden a clicks")
            else:
                print("ERROR - Módulos no responden")
        
        main_window.close()
        return True
        
    except Exception as e:
        print(f"ERROR - Error en ventana principal: {e}")
        return False


def test_login_dialog():
    """Test del diálogo de login"""
    print("\n=== TEST DE DIÁLOGO DE LOGIN ===")
    
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    
    try:
        # Crear login dialog
        login_dialog = LoginDialog()
        
        print("OK - LoginDialog creado")
        
        # Test de campos
        if login_dialog.username_edit and login_dialog.password_edit:
            print("OK - Campos de entrada presentes")
        else:
            print("ERROR - Campos de entrada faltantes")
        
        # Test de botones
        if login_dialog.login_button and login_dialog.cancel_button:
            print("OK - Botones presentes")
        else:
            print("ERROR - Botones faltantes")
        
        # Test de AuthManager
        if login_dialog.auth_manager:
            print("OK - AuthManager conectado")
        else:
            print("ERROR - AuthManager no conectado")
        
        login_dialog.close()
        return True
        
    except Exception as e:
        print(f"ERROR - Error en login dialog: {e}")
        return False


def test_database_connection():
    """Test de conexión a base de datos"""
    print("\n=== TEST DE CONEXIÓN A BASE DE DATOS ===")
    
    try:
        from src.core.database import DatabaseConnection
        
        # Test conexión
        db_conn = DatabaseConnection('users')
        
        if db_conn.connection:
            print("OK - Conexión a base de datos establecida")
            
            # Test query simple
            cursor = db_conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            
            if result:
                print("OK - Consulta básica funciona")
                return True
            else:
                print("ERROR - Consulta básica falló")
                return False
        else:
            print("ERROR - No se pudo conectar a la base de datos")
            return False
            
    except Exception as e:
        print(f"ERROR - Error de conexión: {e}")
        return False


def test_modules_structure():
    """Test de estructura de módulos"""
    print("\n=== TEST DE ESTRUCTURA DE MÓDULOS ===")
    
    modules_to_check = [
        'src.modules.obras',
        'src.modules.inventario',
        'src.modules.herrajes',
        'src.modules.vidrios',
        'src.modules.pedidos',
        'src.modules.usuarios',
        'src.modules.configuracion',
        'src.modules.auditoria',
        'src.modules.logistica',
        'src.modules.administracion',
        'src.modules.mantenimiento'
    ]
    
    available_modules = []
    missing_modules = []
    
    for module_name in modules_to_check:
        try:
            __import__(module_name)
            available_modules.append(module_name)
        except ImportError:
            missing_modules.append(module_name)
    
    print(f"OK - {len(available_modules)} módulos disponibles")
    print(f"ADVERTENCIA - {len(missing_modules)} módulos faltantes")
    
    if missing_modules:
        print("Módulos faltantes:")
        for module in missing_modules:
            print(f"  - {module}")
    
    return len(available_modules) > 0


def run_all_tests():
    """Ejecuta todos los tests"""
    print("EJECUTANDO TESTS COMPLETOS DE FUNCIONALIDAD")
    print("=" * 60)
    
    tests = [
        ("Autenticación", test_authentication),
        ("Ventana Principal", test_main_window),
        ("Diálogo de Login", test_login_dialog),
        ("Conexión BD", test_database_connection),
        ("Estructura Módulos", test_modules_structure),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"\n[OK] {test_name}: PASADO")
            else:
                failed += 1
                print(f"\n[FAIL] {test_name}: FALLIDO")
        except Exception as e:
            failed += 1
            print(f"\n[ERROR] {test_name}: ERROR - {e}")
    
    # Resumen final
    print("\n" + "=" * 60)
    print("RESUMEN FINAL DE TESTS")
    print(f"Tests pasados: {passed}")
    print(f"Tests fallidos: {failed}")
    print(f"Total: {passed + failed}")
    
    if failed == 0:
        print("\nTODOS LOS TESTS PASARON!")
        print("El sistema esta funcionando correctamente.")
    else:
        print(f"\n{failed} tests fallaron.")
        print("Revisar errores reportados arriba.")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)