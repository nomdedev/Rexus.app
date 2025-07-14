#!/usr/bin/env python3
"""
Script para probar la aplicación visualmente después de la limpieza de credenciales
"""

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_visual_actual():
    """Test para ver el estado visual actual después de limpieza"""

    print("=" * 60)
    print("👁️ TEST VISUAL: ESTADO ACTUAL DE LA APLICACIÓN")
    print("=" * 60)

    # Obtener la aplicación existente
    app = QApplication.instance()
    if not app:
        print("❌ No hay aplicación PyQt6 ejecutándose")
        return

    print("✅ Aplicación PyQt6 encontrada")

    # Buscar LoginView
    login_view = None
    main_window = None

    for widget in QApplication.allWidgets():
        if widget.__class__.__name__ == "LoginView":
            login_view = widget
            print("✅ LoginView encontrado")
        elif widget.__class__.__name__ == "MainWindow":
            main_window = widget
            print("✅ MainWindow encontrado")

    if login_view and login_view.isVisible():
        print("📱 LOGIN VIEW ACTIVO")
        print("   - Realizando login automático...")

        # Precompletar credenciales de prueba (ya limpias)
        if hasattr(login_view, "usuario_input") and hasattr(
            login_view, "password_input"
        ):
            login_view.usuario_input.setText("TEST_USER")
            login_view.password_input.setText("TEST_PASS")
            print("   ✅ Campos completados con credenciales de prueba")

        # Buscar botón de login
        if hasattr(login_view, "boton_login"):
            boton = login_view.boton_login
            print(f"   ✅ Botón encontrado: '{boton.text()}'")
            print(
                f"   📐 Tamaño del botón: {boton.size().width()}x{boton.size().height()}"
            )
            print(
                f"   🎯 Estado: {'Habilitado' if boton.isEnabled() else 'Deshabilitado'}"
            )

            # Simular click
            print("   🔥 Simulando click...")
            QTest.mouseClick(boton, Qt.MouseButton.LeftButton)

            # Esperar a que aparezca MainWindow
            def verificar_mainwindow():
                for widget in QApplication.allWidgets():
                    if widget.__class__.__name__ == "MainWindow" and widget.isVisible():
                        print("🎉 ¡MainWindow mostrado exitosamente!")
                        analizar_mainwindow_visual(widget)
                        return
                print("⚠️ MainWindow no aparece aún...")

            QTimer.singleShot(3000, verificar_mainwindow)

    elif main_window and main_window.isVisible():
        print("🏠 MAIN WINDOW YA ACTIVO")
        analizar_mainwindow_visual(main_window)

    else:
        print(
            "❓ Estado desconocido - no se encontró ni LoginView ni MainWindow visible"
        )


def analizar_mainwindow_visual(main_window):
    """Analiza visualmente el MainWindow"""
    print("\n" + "=" * 60)
    print("🔍 ANÁLISIS VISUAL DEL MAINWINDOW")
    print("=" * 60)

    # Información básica
    print(
        f"📐 Tamaño de ventana: {main_window.size().width()}x{main_window.size().height()}"
    )
    print(f"📍 Posición: ({main_window.pos().x()}, {main_window.pos().y()})")
    print(f"👁️ Visible: {main_window.isVisible()}")

    # Buscar componentes principales
    componentes_encontrados = []

    # Sidebar
    if hasattr(main_window, "sidebar") and main_window.sidebar:
        sidebar = main_window.sidebar
        componentes_encontrados.append(f"✅ Sidebar ({sidebar.__class__.__name__})")
        print(
            f"   📐 Tamaño sidebar: {sidebar.size().width()}x{sidebar.size().height()}"
        )

    # Header
    if hasattr(main_window, "header") and main_window.header:
        header = main_window.header
        componentes_encontrados.append(f"✅ Header ({header.__class__.__name__})")
        print(f"   📐 Tamaño header: {header.size().width()}x{header.size().height()}")

    # Stack de módulos
    if hasattr(main_window, "module_stack") and main_window.module_stack:
        stack = main_window.module_stack
        componentes_encontrados.append(f"✅ Module Stack ({stack.count()} páginas)")
        print(f"   📐 Tamaño stack: {stack.size().width()}x{stack.size().height()}")
        print(f"   📄 Página actual: {stack.currentIndex()}")

    print("\n🧩 COMPONENTES ENCONTRADOS:")
    for comp in componentes_encontrados:
        print(f"  {comp}")

    # Verificar temas
    stylesheet = main_window.styleSheet()
    if stylesheet:
        print(f"\n🎨 Stylesheet aplicado: {len(stylesheet)} caracteres")
    else:
        print("\n⚠️ Sin stylesheet aplicado")

    # Buscar problemas visuales comunes
    print("\n🔍 VERIFICACIÓN DE PROBLEMAS VISUALES:")

    # Verificar si los widgets tienen tamaño mínimo
    widgets_problema = []
    try:
        for child in main_window.findChildren(QWidget):
            if hasattr(child, "size"):
                size = child.size()
                if size.width() < 10 or size.height() < 10:
                    widgets_problema.append(
                        f"   ⚠️ Widget muy pequeño: {child.__class__.__name__} ({size.width()}x{size.height()})"
                    )
    except Exception as e:
        widgets_problema.append(f"   ❌ Error verificando widgets: {e}")

    if widgets_problema:
        print("⚠️ Widgets con tamaños problemáticos encontrados:")
        for problema in widgets_problema[:5]:  # Mostrar solo los primeros 5
            print(problema)
    else:
        print("✅ No se detectaron widgets con tamaños problemáticos")

    print("\n" + "=" * 60)


def main():
    """Función principal"""
    try:
        test_visual_actual()
    except Exception as e:
        print(f"❌ Error durante el test visual: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main()

import os
import sys
import traceback

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import QApplication, QMessageBox, QWidget
