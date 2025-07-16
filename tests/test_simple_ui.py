#!/usr/bin/env python3
"""
Tests simples de UI sin Unicode emojis
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


def test_basic_functionality():
    """Test básico de funcionalidad"""
    print("Iniciando tests básicos...")
    
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    
    # Crear datos de prueba
    user_data = {
        'username': 'admin',
        'rol': 'ADMIN',
        'id': 1
    }
    
    security_manager = SimpleSecurityManager()
    modulos_permitidos = security_manager.get_user_modules(1)
    
    errors = []
    
    try:
        # Test 1: Crear ventana principal
        print("Test 1: Creando ventana principal...")
        main_window = MainWindow(user_data, modulos_permitidos)
        main_window.show()
        QTest.qWaitForWindowExposed(main_window)
        print("OK - Ventana principal creada")
        
        # Test 2: Probar toggle del sidebar
        print("Test 2: Probando toggle del sidebar...")
        sidebar = main_window.sidebar
        initial_state = sidebar.is_collapsed
        
        # Click en toggle
        QTest.mouseClick(sidebar.toggle_btn, Qt.MouseButton.LeftButton)
        QTest.qWait(100)
        
        if sidebar.is_collapsed != initial_state:
            print("OK - Sidebar toggle funcionando")
        else:
            errors.append("Sidebar toggle no funciona")
        
        # Test 3: Probar botones de módulos
        print("Test 3: Probando botones de módulos...")
        module_buttons = sidebar.module_buttons
        
        if len(module_buttons) > 0:
            # Click en primer módulo
            QTest.mouseClick(module_buttons[0], Qt.MouseButton.LeftButton)
            QTest.qWait(100)
            
            if main_window.content_stack.count() > 1:
                print("OK - Módulos responden a clicks")
            else:
                errors.append("Módulos no responden a clicks")
        else:
            errors.append("No hay botones de módulos")
        
        # Test 4: Probar redimensionamiento
        print("Test 4: Probando redimensionamiento...")
        original_size = main_window.size()
        main_window.resize(800, 600)
        QTest.qWait(100)
        
        if main_window.size() != original_size:
            print("OK - Redimensionamiento funciona")
        else:
            errors.append("Redimensionamiento no funciona")
        
        # Cerrar ventana
        main_window.close()
        
        # Resumen
        print("\n" + "=" * 40)
        print("RESUMEN DE TESTS:")
        print(f"Total de tests: 4")
        print(f"Errores encontrados: {len(errors)}")
        
        if errors:
            print("\nERRORES:")
            for i, error in enumerate(errors, 1):
                print(f"{i}. {error}")
        else:
            print("Todos los tests pasaron correctamente!")
        
        return len(errors) == 0
        
    except Exception as e:
        print(f"Error fatal durante tests: {e}")
        return False


if __name__ == "__main__":
    success = test_basic_functionality()
    sys.exit(0 if success else 1)