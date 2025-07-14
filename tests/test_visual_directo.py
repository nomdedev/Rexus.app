#!/usr/bin/env python3
"""
Test directo para probar el login y ver el estado visual del MainWindow
"""

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_login_y_mainwindow():
    """Test del flujo completo login -> MainWindow"""

    print("=" * 60)
    print("🔍 TEST VISUAL: LOGIN → MAINWINDOW")
    print("=" * 60)

    # Importar main directamente
    # Variables de control
    login_exitoso = False
    mainwindow_visible = False

    class TestMonitor(QObject):
        def __init__(self):
            super().__init__()
import os
import sys

from PyQt6.QtCore import QObject, Qt, QTimer, pyqtSignal
from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import QApplication, QMessageBox

from main import app, continuar_inicio

        def on_login_success(self, user):
            nonlocal login_exitoso, mainwindow_visible
            login_exitoso = True
            print(f"✅ LOGIN EXITOSO: {user.get('usuario', 'usuario_desconocido')}")

            # Buscar MainWindow
            for widget in QApplication.allWidgets():
                if widget.__class__.__name__ == "MainWindow" and widget.isVisible():
                    mainwindow_visible = True
                    print("✅ MAINWINDOW VISIBLE")
                    analizar_mainwindow_detallado(widget)
                    break

    monitor = TestMonitor()

    def iniciar_test():
        print("🔍 Buscando LoginView...")

        # Buscar LoginView
        login_view = None
        for widget in QApplication.allWidgets():
            if widget.__class__.__name__ == "LoginView":
                login_view = widget
                break

        if not login_view:
            print("❌ LoginView no encontrado")
            # Buscar MainWindow directamente por si ya está abierto
            for widget in QApplication.allWidgets():
                if widget.__class__.__name__ == "MainWindow" and widget.isVisible():
                    print("✅ MainWindow ya está visible, analizando...")
                    analizar_mainwindow_detallado(widget)
                    QTimer.singleShot(5000, app.quit)
                    return
            app.quit()
            return

        print("✅ LoginView encontrado")

        # Buscar controlador de login
        login_controller = None
        for obj in QApplication.allWidgets():
            if hasattr(obj, 'login_exitoso'):
                login_controller = obj
                break

        if login_controller:
            print("✅ LoginController encontrado")
            login_controller.login_exitoso.connect(monitor.on_login_success)

        # Precompletar campos con credenciales reales para test local
        if hasattr(login_view, 'usuario_input') and hasattr(login_view, 'password_input'):
            # SOLO PARA TEST LOCAL - usar credenciales reales
            login_view.usuario_input.setText("admin")  # Usuario real para test local
            login_view.password_input.setText("admin")  # Password real para test local
            print("✅ Campos completados con credenciales reales (solo para test local)")

        # Simular click en botón
        if hasattr(login_view, 'boton_login'):
            boton = login_view.boton_login
            print(f"✅ Botón: '{boton.text()}' - {boton.size().width()}x{boton.size().height()}")

            def hacer_click():
                print("🔥 HACIENDO CLICK EN LOGIN...")
                QTest.mouseClick(boton, Qt.MouseButton.LeftButton)

                # Verificar resultado
                QTimer.singleShot(3000, verificar_resultado)

            def verificar_resultado():
                print(f"📊 RESULTADO: Login: {login_exitoso}, MainWindow: {mainwindow_visible}")

                if not mainwindow_visible:
                    # Buscar MainWindow manualmente
                    for widget in QApplication.allWidgets():
                        if widget.__class__.__name__ == "MainWindow":
                            print(f"✅ MainWindow encontrado: visible={widget.isVisible()}")
                            if widget.isVisible():
                                analizar_mainwindow_detallado(widget)
                            break

                QTimer.singleShot(3000, app.quit)

            QTimer.singleShot(1000, hacer_click)
        else:
            print("❌ Botón de login no encontrado")
            app.quit()

    # Iniciar después del splash
    QTimer.singleShot(4000, iniciar_test)

    # Timeout de seguridad
    QTimer.singleShot(20000, lambda: (print("⏰ TIMEOUT"), app.quit()))

    print("🚀 Iniciando test...")
    return app.exec()

def analizar_mainwindow_detallado(main_window):
    """Análisis detallado del MainWindow"""
    print("\n" + "=" * 60)
    print("🔍 ANÁLISIS DETALLADO DEL MAINWINDOW")
    print("=" * 60)

    # Información básica
    print(f"📐 Tamaño: {main_window.size().width()}x{main_window.size().height()}")
    print(f"📍 Posición: ({main_window.pos().x()}, {main_window.pos().y()})")
    print(f"🎨 Título: {main_window.windowTitle()}")

    # Componentes principales
    componentes = {}

    # Sidebar
    if hasattr(main_window, 'sidebar') and main_window.sidebar:
        sidebar = main_window.sidebar
        componentes['sidebar'] = {
            'clase': sidebar.__class__.__name__,
            'tamaño': f"{sidebar.size().width()}x{sidebar.size().height()}",
            'visible': sidebar.isVisible()
        }

    # Header
    if hasattr(main_window, 'header') and main_window.header:
        header = main_window.header
        componentes['header'] = {
            'clase': header.__class__.__name__,
            'tamaño': f"{header.size().width()}x{header.size().height()}",
            'visible': header.isVisible()
        }

    # Module Stack
    if hasattr(main_window, 'module_stack') and main_window.module_stack:
        stack = main_window.module_stack
        componentes['module_stack'] = {
            'clase': stack.__class__.__name__,
            'tamaño': f"{stack.size().width()}x{stack.size().height()}",
            'páginas': stack.count(),
            'actual': stack.currentIndex(),
            'visible': stack.isVisible()
        }

    # Mostrar componentes
    print("\n🧩 COMPONENTES PRINCIPALES:")
    for nombre, info in componentes.items():
        print(f"  ✅ {nombre.upper()}:")
        for clave, valor in info.items():
            print(f"     {clave}: {valor}")

    # Verificar estilos
    stylesheet = main_window.styleSheet()
    print(f"\n🎨 STYLESHEET: {len(stylesheet)} caracteres")

    # Detectar problemas visuales
    print("\n⚠️ VERIFICACIÓN DE PROBLEMAS:")

    problemas = []

    # Verificar tamaños mínimos
    if main_window.size().width() < 800 or main_window.size().height() < 600:
        problemas.append("🔸 Ventana muy pequeña")

    # Verificar componentes críticos
    if 'sidebar' not in componentes:
        problemas.append("🔸 Sidebar no encontrado")
    elif not componentes['sidebar']['visible']:
        problemas.append("🔸 Sidebar no visible")

    if 'module_stack' not in componentes:
        problemas.append("🔸 Module Stack no encontrado")
    elif not componentes['module_stack']['visible']:
        problemas.append("🔸 Module Stack no visible")

    if problemas:
        print("❌ PROBLEMAS DETECTADOS:")
        for problema in problemas:
            print(f"  {problema}")
    else:
        print("✅ No se detectaron problemas obvios")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    result = test_login_y_mainwindow()
    sys.exit(result)
