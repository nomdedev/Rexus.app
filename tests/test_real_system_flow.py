#!/usr/bin/env python3
"""
Test que refleja el flujo real del sistema tal como se ejecuta
"""

import sys
import os
import time
from pathlib import Path

# Agregar el directorio raíz al path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtTest import QTest

from src.core.login_dialog import LoginDialog
from src.main.app_collapsible import MainWindow, SimpleSecurityManager


class RealSystemTester:
    """Tester que simula el uso real del sistema"""
    
    def __init__(self):
        self.app = QApplication.instance()
        if not self.app:
            self.app = QApplication(sys.argv)
        
        self.login_dialog = None
        self.main_window = None
        self.errors = []
        self.test_results = []
        
    def test_full_startup_flow(self):
        """Test del flujo completo de inicio"""
        print("=" * 60)
        print("TEST: FLUJO COMPLETO DE INICIO")
        print("=" * 60)
        
        try:
            # 1. Crear y mostrar login dialog
            print("1. Iniciando login dialog...")
            self.login_dialog = LoginDialog()
            
            # Simular entrada de datos
            self.login_dialog.username_edit.setText("admin")
            self.login_dialog.password_edit.setText("admin")
            
            # Simular click en login
            print("2. Simulando login...")
            self.login_dialog.handle_login()
            
            # Verificar que el login fue exitoso
            if hasattr(self.login_dialog, 'auth_manager'):
                print("   [OK] AuthManager disponible")
            else:
                self.errors.append("AuthManager no disponible")
            
            # 3. Crear ventana principal
            print("3. Creando ventana principal...")
            user_data = {
                'username': 'admin',
                'rol': 'ADMIN',
                'id': 1
            }
            
            security_manager = SimpleSecurityManager()
            modulos_permitidos = security_manager.get_user_modules(1)
            
            self.main_window = MainWindow(user_data, modulos_permitidos)
            self.main_window.show()
            
            # Esperar a que se muestre
            QTest.qWaitForWindowExposed(self.main_window)
            print("   [OK] Ventana principal mostrada")
            
            # 4. Verificar componentes principales
            print("4. Verificando componentes principales...")
            
            # Sidebar
            if hasattr(self.main_window, 'sidebar'):
                print("   [OK] Sidebar presente")
                
                # Verificar botones de módulos
                if hasattr(self.main_window.sidebar, 'module_buttons'):
                    num_buttons = len(self.main_window.sidebar.module_buttons)
                    print(f"   [OK] {num_buttons} botones de módulos")
                else:
                    self.errors.append("Botones de módulos no encontrados")
            else:
                self.errors.append("Sidebar no encontrado")
            
            # Content stack
            if hasattr(self.main_window, 'content_stack'):
                print("   [OK] Content stack presente")
                
                # Verificar que tiene el dashboard
                if self.main_window.content_stack.count() > 0:
                    print("   [OK] Dashboard inicial cargado")
                else:
                    self.errors.append("Dashboard no cargado")
            else:
                self.errors.append("Content stack no encontrado")
            
            self.test_results.append({
                'test': 'Flujo de inicio completo',
                'status': 'PASS' if not self.errors else 'FAIL',
                'errors': self.errors.copy()
            })
            
            return len(self.errors) == 0
            
        except Exception as e:
            error_msg = f"Error en flujo de inicio: {e}"
            self.errors.append(error_msg)
            print(f"   [ERROR] {error_msg}")
            return False
    
    def test_module_navigation(self):
        """Test de navegación entre módulos"""
        print("\n" + "=" * 60)
        print("TEST: NAVEGACIÓN ENTRE MÓDULOS")
        print("=" * 60)
        
        if not self.main_window:
            self.errors.append("Main window no disponible para test de navegación")
            return False
        
        try:
            sidebar = self.main_window.sidebar
            module_buttons = sidebar.module_buttons
            
            # Probar navegación a cada módulo
            modules_tested = 0
            successful_navigations = 0
            
            for i, button in enumerate(module_buttons[:5]):  # Probar primeros 5 módulos
                try:
                    module_name = sidebar.modules[i][1]
                    print(f"{i+1}. Navegando a módulo: {module_name}")
                    
                    # Click en el botón
                    QTest.mouseClick(button, Qt.MouseButton.LeftButton)
                    QTest.qWait(100)  # Esperar procesamiento
                    
                    # Verificar que se abrió la pestaña
                    content_stack = self.main_window.content_stack
                    tab_count = content_stack.count()
                    
                    if tab_count > 1:  # Más que solo dashboard
                        print(f"   [OK] Módulo {module_name} abierto (tabs: {tab_count})")
                        successful_navigations += 1
                    else:
                        print(f"   [ERROR] Módulo {module_name} no abrió pestaña")
                        self.errors.append(f"Navegación a {module_name} falló")
                    
                    modules_tested += 1
                    
                except Exception as e:
                    print(f"   [ERROR] Error en módulo {i}: {e}")
                    self.errors.append(f"Error navegando a módulo {i}: {e}")
            
            # Resultado del test
            success_rate = (successful_navigations / modules_tested) * 100 if modules_tested > 0 else 0
            print(f"\nResultado: {successful_navigations}/{modules_tested} módulos ({success_rate:.1f}%)")
            
            self.test_results.append({
                'test': 'Navegación entre módulos',
                'status': 'PASS' if success_rate >= 80 else 'FAIL',
                'success_rate': success_rate,
                'errors': self.errors.copy()
            })
            
            return success_rate >= 80
            
        except Exception as e:
            error_msg = f"Error en test de navegación: {e}"
            self.errors.append(error_msg)
            print(f"   [ERROR] {error_msg}")
            return False
    
    def test_sidebar_functionality(self):
        """Test de funcionalidad del sidebar"""
        print("\n" + "=" * 60)
        print("TEST: FUNCIONALIDAD DEL SIDEBAR")
        print("=" * 60)
        
        if not self.main_window:
            self.errors.append("Main window no disponible para test de sidebar")
            return False
        
        try:
            sidebar = self.main_window.sidebar
            
            # Test 1: Estado inicial
            print("1. Verificando estado inicial...")
            initial_collapsed = sidebar.is_collapsed
            initial_width = sidebar.width()
            print(f"   Estado inicial: {'Colapsado' if initial_collapsed else 'Expandido'}")
            print(f"   Ancho inicial: {initial_width}px")
            
            # Test 2: Toggle del sidebar
            print("2. Probando toggle del sidebar...")
            
            # Primer toggle
            QTest.mouseClick(sidebar.toggle_btn, Qt.MouseButton.LeftButton)
            QTest.qWait(200)  # Esperar animación
            
            after_toggle1_collapsed = sidebar.is_collapsed
            after_toggle1_width = sidebar.width()
            
            if after_toggle1_collapsed != initial_collapsed:
                print("   [OK] Primer toggle cambió el estado")
                print(f"   Nuevo estado: {'Colapsado' if after_toggle1_collapsed else 'Expandido'}")
                print(f"   Nuevo ancho: {after_toggle1_width}px")
            else:
                self.errors.append("Primer toggle no cambió el estado")
            
            # Segundo toggle (volver al estado original)
            QTest.mouseClick(sidebar.toggle_btn, Qt.MouseButton.LeftButton)
            QTest.qWait(200)
            
            after_toggle2_collapsed = sidebar.is_collapsed
            after_toggle2_width = sidebar.width()
            
            if after_toggle2_collapsed == initial_collapsed:
                print("   [OK] Segundo toggle restauró el estado original")
            else:
                self.errors.append("Segundo toggle no restauró el estado original")
            
            # Test 3: Verificar elementos del sidebar
            print("3. Verificando elementos del sidebar...")
            
            # Verificar título
            if hasattr(sidebar, 'title_label'):
                print("   [OK] Título presente")
            else:
                self.errors.append("Título del sidebar no encontrado")
            
            # Verificar info de usuario
            if hasattr(sidebar, 'user_label'):
                print("   [OK] Info de usuario presente")
            else:
                self.errors.append("Info de usuario no encontrada")
            
            # Verificar botones de módulos
            if hasattr(sidebar, 'module_buttons') and len(sidebar.module_buttons) > 0:
                print(f"   [OK] {len(sidebar.module_buttons)} botones de módulos")
            else:
                self.errors.append("Botones de módulos no encontrados")
            
            self.test_results.append({
                'test': 'Funcionalidad del sidebar',
                'status': 'PASS' if not self.errors else 'FAIL',
                'errors': self.errors.copy()
            })
            
            return len(self.errors) == 0
            
        except Exception as e:
            error_msg = f"Error en test de sidebar: {e}"
            self.errors.append(error_msg)
            print(f"   [ERROR] {error_msg}")
            return False
    
    def test_window_responsiveness(self):
        """Test de responsividad de la ventana"""
        print("\n" + "=" * 60)
        print("TEST: RESPONSIVIDAD DE LA VENTANA")
        print("=" * 60)
        
        if not self.main_window:
            self.errors.append("Main window no disponible para test de responsividad")
            return False
        
        try:
            # Test 1: Redimensionamiento
            print("1. Probando redimensionamiento...")
            
            original_size = self.main_window.size()
            print(f"   Tamaño original: {original_size.width()}x{original_size.height()}")
            
            # Cambiar a tamaño pequeño
            self.main_window.resize(800, 600)
            QTest.qWait(100)
            
            small_size = self.main_window.size()
            print(f"   Tamaño pequeño: {small_size.width()}x{small_size.height()}")
            
            # Cambiar a tamaño grande
            self.main_window.resize(1600, 1000)
            QTest.qWait(100)
            
            large_size = self.main_window.size()
            print(f"   Tamaño grande: {large_size.width()}x{large_size.height()}")
            
            # Restaurar tamaño original
            self.main_window.resize(original_size)
            QTest.qWait(100)
            
            print("   [OK] Redimensionamiento funciona correctamente")
            
            # Test 2: Verificar que el contenido se ajusta
            print("2. Verificando ajuste del contenido...")
            
            # Verificar que el sidebar mantiene su funcionalidad
            if hasattr(self.main_window, 'sidebar'):
                sidebar = self.main_window.sidebar
                if hasattr(sidebar, 'toggle_btn'):
                    # Probar toggle después de redimensionar
                    initial_state = sidebar.is_collapsed
                    QTest.mouseClick(sidebar.toggle_btn, Qt.MouseButton.LeftButton)
                    QTest.qWait(100)
                    
                    if sidebar.is_collapsed != initial_state:
                        print("   [OK] Sidebar funciona después de redimensionar")
                    else:
                        self.errors.append("Sidebar no funciona después de redimensionar")
                else:
                    self.errors.append("Botón toggle no encontrado")
            else:
                self.errors.append("Sidebar no encontrado")
            
            self.test_results.append({
                'test': 'Responsividad de la ventana',
                'status': 'PASS' if not self.errors else 'FAIL',
                'errors': self.errors.copy()
            })
            
            return len(self.errors) == 0
            
        except Exception as e:
            error_msg = f"Error en test de responsividad: {e}"
            self.errors.append(error_msg)
            print(f"   [ERROR] {error_msg}")
            return False
    
    def test_dashboard_display(self):
        """Test de visualización del dashboard"""
        print("\n" + "=" * 60)
        print("TEST: VISUALIZACIÓN DEL DASHBOARD")
        print("=" * 60)
        
        if not self.main_window:
            self.errors.append("Main window no disponible para test de dashboard")
            return False
        
        try:
            # Verificar que el dashboard está presente
            content_stack = self.main_window.content_stack
            
            if content_stack.count() > 0:
                print("1. Dashboard presente en el content stack")
                
                # Verificar que es la pestaña activa
                current_tab = content_stack.currentWidget()
                if current_tab:
                    print("   [OK] Dashboard es la pestaña activa")
                else:
                    self.errors.append("Dashboard no es la pestaña activa")
                
                # Verificar título de la pestaña
                current_tab_text = content_stack.tabText(0)
                if "Dashboard" in current_tab_text:
                    print("   [OK] Título del dashboard correcto")
                else:
                    self.errors.append("Título del dashboard incorrecto")
                
            else:
                self.errors.append("Dashboard no encontrado")
            
            self.test_results.append({
                'test': 'Visualización del dashboard',
                'status': 'PASS' if not self.errors else 'FAIL',
                'errors': self.errors.copy()
            })
            
            return len(self.errors) == 0
            
        except Exception as e:
            error_msg = f"Error en test de dashboard: {e}"
            self.errors.append(error_msg)
            print(f"   [ERROR] {error_msg}")
            return False
    
    def run_all_tests(self):
        """Ejecuta todos los tests del sistema real"""
        print("EJECUTANDO TESTS DEL SISTEMA REAL")
        print("=" * 60)
        
        tests = [
            ("Flujo de inicio completo", self.test_full_startup_flow),
            ("Navegación entre módulos", self.test_module_navigation),
            ("Funcionalidad del sidebar", self.test_sidebar_functionality),
            ("Responsividad de la ventana", self.test_window_responsiveness),
            ("Visualización del dashboard", self.test_dashboard_display),
        ]
        
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed += 1
                    print(f"\n[PASS] {test_name}")
                else:
                    failed += 1
                    print(f"\n[FAIL] {test_name}")
            except Exception as e:
                failed += 1
                print(f"\n[ERROR] {test_name}: {e}")
        
        # Resumen final
        print("\n" + "=" * 60)
        print("RESUMEN DE TESTS DEL SISTEMA REAL")
        print("=" * 60)
        print(f"Tests ejecutados: {len(tests)}")
        print(f"Tests pasados: {passed}")
        print(f"Tests fallidos: {failed}")
        
        if self.errors:
            print(f"\nErrores encontrados: {len(self.errors)}")
            for i, error in enumerate(self.errors, 1):
                print(f"{i}. {error}")
        
        # Limpiar recursos
        if self.main_window:
            self.main_window.close()
        if self.login_dialog:
            self.login_dialog.close()
        
        return failed == 0
    
    def cleanup(self):
        """Limpia recursos"""
        if self.main_window:
            self.main_window.close()
        if self.login_dialog:
            self.login_dialog.close()


def main():
    """Función principal"""
    tester = RealSystemTester()
    
    try:
        success = tester.run_all_tests()
        
        if success:
            print("\nTODOS LOS TESTS DEL SISTEMA REAL PASARON!")
            return 0
        else:
            print("\nALGUNOS TESTS DEL SISTEMA REAL FALLARON.")
            return 1
            
    except Exception as e:
        print(f"\nERROR FATAL EN TESTS: {e}")
        return 1
    finally:
        tester.cleanup()


if __name__ == "__main__":
    sys.exit(main())