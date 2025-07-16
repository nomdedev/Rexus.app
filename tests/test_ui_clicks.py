#!/usr/bin/env python3
"""
Tests de clicks e interacción UI para detectar errores
"""

import sys
import os
import time
from pathlib import Path
from unittest.mock import patch, MagicMock

# Agregar el directorio raíz al path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtTest import QTest
from PyQt6.QtGui import QCloseEvent

from src.main.app_collapsible import MainWindow, CollapsibleSidebar, SimpleSecurityManager


class TestUIClicks:
    """Clase para testing de clicks e interacción UI"""
    
    def __init__(self):
        self.app = QApplication.instance()
        if not self.app:
            self.app = QApplication(sys.argv)
        
        self.security_manager = SimpleSecurityManager()
        self.user_data = {
            'username': 'admin',
            'rol': 'ADMIN',
            'id': 1
        }
        self.modulos_permitidos = self.security_manager.get_user_modules(1)
        
        self.main_window = None
        self.errors_found = []
        
    def setup_main_window(self):
        """Configura la ventana principal para testing"""
        try:
            self.main_window = MainWindow(self.user_data, self.modulos_permitidos)
            self.main_window.show()
            QTest.qWaitForWindowExposed(self.main_window)
            return True
        except Exception as e:
            self.errors_found.append(f"Error al crear MainWindow: {e}")
            return False
    
    def test_sidebar_toggle(self):
        """Test del botón toggle del sidebar"""
        print("🧪 Testing sidebar toggle...")
        
        if not self.main_window:
            self.errors_found.append("MainWindow no disponible para test de sidebar")
            return False
        
        try:
            sidebar = self.main_window.sidebar
            toggle_btn = sidebar.toggle_btn
            
            # Estado inicial (expandido)
            initial_collapsed = sidebar.is_collapsed
            initial_width = sidebar.width()
            
            # Hacer click en toggle
            QTest.mouseClick(toggle_btn, Qt.MouseButton.LeftButton)
            QTest.qWait(100)  # Esperar animación
            
            # Verificar que cambió el estado
            if sidebar.is_collapsed == initial_collapsed:
                self.errors_found.append("Sidebar toggle no cambió el estado")
                return False
            
            # Verificar que cambió el ancho
            if sidebar.width() == initial_width:
                self.errors_found.append("Sidebar toggle no cambió el ancho")
                return False
            
            # Hacer click nuevamente para volver al estado original
            QTest.mouseClick(toggle_btn, Qt.MouseButton.LeftButton)
            QTest.qWait(100)
            
            # Verificar que volvió al estado original
            if sidebar.is_collapsed != initial_collapsed:
                self.errors_found.append("Sidebar toggle no volvió al estado original")
                return False
            
            print("✅ Sidebar toggle funciona correctamente")
            return True
            
        except Exception as e:
            self.errors_found.append(f"Error en test de sidebar toggle: {e}")
            return False
    
    def test_module_buttons_click(self):
        """Test de clicks en botones de módulos"""
        print("🧪 Testing module buttons...")
        
        if not self.main_window:
            self.errors_found.append("MainWindow no disponible para test de módulos")
            return False
        
        try:
            sidebar = self.main_window.sidebar
            module_buttons = sidebar.module_buttons
            
            success_count = 0
            total_modules = len(module_buttons)
            
            for i, btn in enumerate(module_buttons):
                try:
                    # Obtener nombre del módulo
                    module_name = sidebar.modules[i][1]
                    
                    # Hacer click en el botón
                    QTest.mouseClick(btn, Qt.MouseButton.LeftButton)
                    QTest.qWait(50)  # Esperar procesamiento
                    
                    # Verificar que se abrió una pestaña
                    content_stack = self.main_window.content_stack
                    if content_stack.count() > 1:  # Más de dashboard
                        success_count += 1
                        print(f"✅ Módulo {module_name} se abrió correctamente")
                    else:
                        self.errors_found.append(f"Módulo {module_name} no abrió pestaña")
                        
                except Exception as e:
                    self.errors_found.append(f"Error al clickear módulo {i}: {e}")
            
            if success_count == total_modules:
                print(f"✅ Todos los {total_modules} módulos respondieron correctamente")
                return True
            else:
                print(f"⚠️ {success_count}/{total_modules} módulos funcionaron")
                return False
                
        except Exception as e:
            self.errors_found.append(f"Error en test de módulos: {e}")
            return False
    
    def test_tab_switching(self):
        """Test de cambio entre pestañas"""
        print("🧪 Testing tab switching...")
        
        if not self.main_window:
            self.errors_found.append("MainWindow no disponible para test de tabs")
            return False
        
        try:
            content_stack = self.main_window.content_stack
            
            # Abrir algunas pestañas primero
            self.main_window.show_module("Obras")
            self.main_window.show_module("Inventario")
            QTest.qWait(100)
            
            # Verificar que se crearon las pestañas
            if content_stack.count() < 3:  # Dashboard + 2 módulos
                self.errors_found.append("No se crearon las pestañas esperadas")
                return False
            
            # Test de cambio de pestañas
            success_count = 0
            for i in range(content_stack.count()):
                try:
                    content_stack.setCurrentIndex(i)
                    QTest.qWait(50)
                    
                    if content_stack.currentIndex() == i:
                        success_count += 1
                    else:
                        self.errors_found.append(f"Error al cambiar a pestaña {i}")
                        
                except Exception as e:
                    self.errors_found.append(f"Error al cambiar pestaña {i}: {e}")
            
            if success_count == content_stack.count():
                print(f"✅ Cambio de pestañas funciona correctamente ({success_count} pestañas)")
                return True
            else:
                print(f"⚠️ {success_count}/{content_stack.count()} pestañas funcionaron")
                return False
                
        except Exception as e:
            self.errors_found.append(f"Error en test de tabs: {e}")
            return False
    
    def test_window_resize(self):
        """Test de redimensionamiento de ventana"""
        print("🧪 Testing window resize...")
        
        if not self.main_window:
            self.errors_found.append("MainWindow no disponible para test de resize")
            return False
        
        try:
            # Tamaño inicial
            initial_size = self.main_window.size()
            
            # Cambiar tamaño
            self.main_window.resize(800, 600)
            QTest.qWait(100)
            
            # Verificar que cambió
            if self.main_window.size() == initial_size:
                self.errors_found.append("Window resize no funcionó")
                return False
            
            # Restaurar tamaño
            self.main_window.resize(initial_size)
            QTest.qWait(100)
            
            print("✅ Window resize funciona correctamente")
            return True
            
        except Exception as e:
            self.errors_found.append(f"Error en test de resize: {e}")
            return False
    
    def test_keyboard_shortcuts(self):
        """Test de atajos de teclado"""
        print("🧪 Testing keyboard shortcuts...")
        
        try:
            # Test de tecla ESC (si está implementada)
            QTest.keyClick(self.main_window, Qt.Key.Key_Escape)
            QTest.qWait(50)
            
            # Test de teclas de navegación
            QTest.keyClick(self.main_window, Qt.Key.Key_Tab)
            QTest.qWait(50)
            
            print("✅ Keyboard shortcuts procesados sin errores")
            return True
            
        except Exception as e:
            self.errors_found.append(f"Error en test de keyboard: {e}")
            return False
    
    def test_memory_leaks(self):
        """Test básico de memory leaks"""
        print("🧪 Testing memory leaks...")
        
        try:
            # Crear y destruir múltiples módulos
            for i in range(10):
                self.main_window.show_module("Obras")
                self.main_window.show_module("Inventario")
                QTest.qWait(10)
            
            # Cerrar todas las pestañas excepto dashboard
            content_stack = self.main_window.content_stack
            while content_stack.count() > 1:
                content_stack.removeTab(content_stack.count() - 1)
                QTest.qWait(10)
            
            print("✅ Memory leak test completado")
            return True
            
        except Exception as e:
            self.errors_found.append(f"Error en test de memory: {e}")
            return False
    
    def test_error_handling(self):
        """Test de manejo de errores"""
        print("🧪 Testing error handling...")
        
        try:
            # Intentar acciones que podrían causar errores
            
            # Click en área vacía
            QTest.mouseClick(self.main_window, Qt.MouseButton.LeftButton)
            QTest.qWait(50)
            
            # Click derecho
            QTest.mouseClick(self.main_window, Qt.MouseButton.RightButton)
            QTest.qWait(50)
            
            # Doble click
            QTest.mouseDClick(self.main_window, Qt.MouseButton.LeftButton)
            QTest.qWait(50)
            
            print("✅ Error handling test completado")
            return True
            
        except Exception as e:
            self.errors_found.append(f"Error en test de error handling: {e}")
            return False
    
    def run_all_tests(self):
        """Ejecuta todos los tests"""
        print("Iniciando tests de UI clicks...")
        print("=" * 50)
        
        # Setup
        if not self.setup_main_window():
            print("❌ Error en setup, abortando tests")
            return False
        
        # Lista de tests
        tests = [
            ("Sidebar Toggle", self.test_sidebar_toggle),
            ("Module Buttons", self.test_module_buttons_click),
            ("Tab Switching", self.test_tab_switching),
            ("Window Resize", self.test_window_resize),
            ("Keyboard Shortcuts", self.test_keyboard_shortcuts),
            ("Memory Leaks", self.test_memory_leaks),
            ("Error Handling", self.test_error_handling),
        ]
        
        # Ejecutar tests
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            try:
                print(f"\n📋 {test_name}:")
                if test_func():
                    passed += 1
                else:
                    failed += 1
                    print(f"❌ {test_name} falló")
            except Exception as e:
                failed += 1
                print(f"❌ {test_name} falló con excepción: {e}")
        
        # Cleanup
        if self.main_window:
            self.main_window.close()
        
        # Resumen
        print("\n" + "=" * 50)
        print("RESUMEN DE TESTS:")
        print(f"Pasados: {passed}")
        print(f"Fallidos: {failed}")
        print(f"Total: {passed + failed}")
        
        if self.errors_found:
            print("\nERRORES ENCONTRADOS:")
            for i, error in enumerate(self.errors_found, 1):
                print(f"{i}. {error}")
        
        return failed == 0
    
    def cleanup(self):
        """Limpia recursos"""
        if self.main_window:
            self.main_window.close()
            self.main_window = None


def main():
    """Función principal para ejecutar tests"""
    tester = TestUIClicks()
    
    try:
        success = tester.run_all_tests()
        
        if success:
            print("\n🎉 ¡Todos los tests pasaron!")
            return 0
        else:
            print("\n⚠️ Algunos tests fallaron. Revisar errores.")
            return 1
            
    except Exception as e:
        print(f"\n💥 Error fatal en tests: {e}")
        return 1
    finally:
        tester.cleanup()


if __name__ == "__main__":
    sys.exit(main())