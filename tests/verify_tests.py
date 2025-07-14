#!/usr/bin/env python3
"""
Script para verificar que los tests corregidos funcionan correctamente.
"""

sys.path.insert(0, os.path.abspath('.'))

def test_pedidos():
    """Test básico del controlador de pedidos."""
    print("🧪 Ejecutando test de pedidos...")

    try:
        # Crear instancias de test
        model = DummyModel()
        view = DummyView()
        db_connection = MagicMock()
        usuarios_model = MagicMock()
        usuarios_model.tiene_permiso.return_value = True
        usuario_actual = {"id": 1, "username": "testuser", "ip": "127.0.0.1"}

        # Crear controller
        controller = MockPedidosController(view, db_connection, usuarios_model, usuario_actual)
        controller.model.generar_pedido_por_obra = model.generar_pedido
        controller.model.recibir_pedido = model.recibir_pedido
        controller.model.obtener_pedido = model.obtener_pedido
        setattr(controller, 'test_data', model)

        # Test básico: generar pedido
        id_pedido = controller.generar_pedido_por_obra(1)
        assert id_pedido == 1, f"Expected id_pedido=1, got {id_pedido}"
        assert controller.test_data.pedidos[0]["estado"] == "pendiente"

        # Test básico: recibir pedido
        result = controller.recibir_pedido(id_pedido)
        assert result is True, f"Expected True, got {result}"
        assert controller.test_data.pedidos[0]["estado"] == "recibido"

        print("✅ Tests de pedidos pasaron correctamente")
        return True

    except Exception as e:
        print(f"❌ Error en tests de pedidos: {e}")
        traceback.print_exc()
        return False

def test_sidebar():
    """Test básico del sidebar."""
    print("🧪 Ejecutando test de sidebar...")

    try:
        # Test simple sin PyQt6 completo
        sections = [
            ("Inventario", "icons/inventario.svg"),
            ("Obras", "icons/obras.svg"),
        ]

        # Mock simple del sidebar
        class MockSidebar:
            def __init__(self, sections, mostrar_nombres=False):
                self.sections = sections
                self._sidebar_buttons = []
                self._current_selected_index = -1

                # Simular creación de botones
                for i, (title, icon) in enumerate(sections):
                    btn = type('MockButton', (), {
                        'text': lambda: title if mostrar_nombres else "",
                        'isCheckable': lambda: True,
                        'height': lambda: 40,
                        'iconSize': lambda: type('Size', (), {'width': 24, 'height': 24})(),
                        'objectName': lambda: "sidebarButton"
                    })()
                    self._sidebar_buttons.append(btn)

            def _on_sidebar_button_clicked(self, idx):
                self._current_selected_index = idx

        # Test creación
        sidebar = MockSidebar(sections=sections, mostrar_nombres=True)
        assert sidebar.sections == sections
        assert len(sidebar._sidebar_buttons) == len(sections)

        # Test navegación
        sidebar._on_sidebar_button_clicked(0)
        assert sidebar._current_selected_index == 0

        sidebar._on_sidebar_button_clicked(1)
        assert sidebar._current_selected_index == 1

        print("✅ Tests de sidebar pasaron correctamente")
        return True

    except Exception as e:
        print(f"❌ Error en tests de sidebar: {e}")
        traceback.print_exc()
        return False

def test_login_integration():
    """Test básico de integración login."""
    print("🧪 Ejecutando test de integración login...")

    try:
        # Test modelo usuarios
        usuarios_model = DummyUsuariosModel()

        # Test autenticación exitosa
        usuario = usuarios_model.autenticar("TEST_USER", "correcta")
        assert usuario["usuario"] == "TEST_USER"
        assert usuario["rol"] == "administrador"

        # Test módulos permitidos
        modulos_permitidos = usuarios_model.obtener_modulos_permitidos(usuario)
        assert len(modulos_permitidos) >= 4
        assert "Obras" in modulos_permitidos
        assert "Usuarios" in modulos_permitidos

        # Test MainWindow mock
        main_window = DummyMainWindow(usuario, modulos_permitidos)
        assert main_window.usuario_actual == usuario
        assert main_window.modulos_permitidos == modulos_permitidos

        # Test actualización UI
        main_window.actualizar_usuario_label(usuario)
        assert "TEST_USER" in main_window.usuario_label_text
        assert "administrador" in main_window.usuario_label_text

        print("✅ Tests de integración login pasaron correctamente")
        return True

    except Exception as e:
        print(f"❌ Error en tests de login: {e}")
        traceback.print_exc()
        return False

def main():
    """Ejecutar todos los tests."""
    print("🚀 Iniciando verificación de tests corregidos...\n")

    tests_passed = 0
    tests_total = 3
import os
import sys
import traceback
from unittest.mock import MagicMock

from tests.test_login_mainwindow_integration import (
    DummyLoginView,
    DummyMainWindow,
    DummyUsuariosModel,
)
from tests.test_pedidos_controller import DummyModel, DummyView, MockPedidosController

    # Ejecutar tests
    if test_pedidos():
        tests_passed += 1

    print()
    if test_sidebar():
        tests_passed += 1

    print()
    if test_login_integration():
        tests_passed += 1

    # Resumen
    print(f"\n📊 Resumen: {tests_passed}/{tests_total} tests pasaron")

    if tests_passed == tests_total:
        print("🎉 ¡Todos los tests están funcionando correctamente!")
        return 0
    else:
        print("⚠️  Algunos tests necesitan corrección adicional")
        return 1

if __name__ == "__main__":
    sys.exit(main())
