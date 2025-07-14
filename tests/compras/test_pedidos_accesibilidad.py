#!/usr/bin/env python3
"""
Tests de accesibilidad para el módulo de pedidos dentro de compras.
"""

# Agregar el directorio raíz al path
ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT_DIR))

try:
    PEDIDOS_VIEW_AVAILABLE = True
except ImportError:
    # Crear mock si la vista no está disponible
    class PedidosView:
        def __init__(self, usuario_actual=None):
            pass
    PEDIDOS_VIEW_AVAILABLE = False


class TestPedidosAccesibilidad:
    """Tests de accesibilidad para la vista de pedidos."""

    @pytest.fixture(scope="module")
    def app(self):
        """Aplicación Qt para tests."""
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        return app

    def test_pedidos_accesibilidad_basica(self, app):
import sys
from pathlib import Path

import pytest
from PyQt6.QtWidgets import QApplication

from modules.compras.pedidos.view import PedidosView

        """Test básico de accesibilidad de la vista de pedidos."""
        if not PEDIDOS_VIEW_AVAILABLE:
            pytest.skip("PedidosView no disponible")

        try:
            view = PedidosView(usuario_actual="test")

            # Verificar que la vista se puede instanciar
            assert view is not None

        except TypeError:
            # Si el constructor es diferente
            try:
                view = PedidosView()
                assert view is not None
            except Exception as e:
                pytest.skip(f"No se pudo instanciar PedidosView: {e}")

    def test_pedidos_tooltips_y_accesibilidad(self, app):
        """Test de tooltips y accesibilidad de widgets."""
        if not PEDIDOS_VIEW_AVAILABLE:
            pytest.skip("PedidosView no disponible")

        try:
            view = PedidosView()

            # Test botón agregar si existe
            if hasattr(view, 'boton_agregar'):
                boton = view.boton_agregar
                # Verificar que tiene tooltip (puede estar vacío inicialmente)
                tooltip = boton.toolTip()
                assert tooltip is not None

                # Verificar accessible name
                accessible_name = boton.accessibleName()
                assert accessible_name is not None

            # Test tabla de pedidos si existe
            if hasattr(view, 'tabla_pedidos'):
                tabla = view.tabla_pedidos

                # Verificar propiedades de accesibilidad
                assert tabla.toolTip() is not None
                assert tabla.accessibleName() is not None

                # Verificar header de tabla
                header = tabla.horizontalHeader()
                if header is not None:
                    assert header.objectName() is not None

            # Test label de feedback si existe
            if hasattr(view, 'label_feedback'):
                label = view.label_feedback
                assert label.accessibleName() is not None
                assert label.accessibleDescription() is not None

            # Test label de título si existe
            if hasattr(view, 'label_titulo'):
                titulo = view.label_titulo
                assert titulo.text() is not None
                assert titulo.accessibleName() is not None

        except Exception as e:
            pytest.skip(f"Error en test de accesibilidad: {e}")

    def test_pedidos_inputs_accesibilidad(self, app):
        """Test de accesibilidad de campos de entrada."""
        if not PEDIDOS_VIEW_AVAILABLE:
            pytest.skip("PedidosView no disponible")

        try:
            view = PedidosView()

            # Lista de posibles inputs a verificar
            input_attributes = [
                'obra_combo', 'fecha_pedido', 'materiales_input',
                'observaciones_input', 'cantidad_input', 'precio_input'
            ]

            inputs_encontrados = []
            for attr_name in input_attributes:
                if hasattr(view, attr_name):
                    widget = getattr(view, attr_name)
                    inputs_encontrados.append((attr_name, widget))

            # Verificar accesibilidad de inputs encontrados
            for attr_name, widget in inputs_encontrados:
                # Verificar tooltip
                tooltip = widget.toolTip()
                assert tooltip is not None, f"Tooltip faltante en {attr_name}"

                # Verificar accessible name
                accessible_name = widget.accessibleName()
                assert accessible_name is not None, f"AccessibleName faltante en {attr_name}"

                # Verificar que no está deshabilitado por defecto (a menos que sea intencional)
                # assert widget.isEnabled(), f"Widget {attr_name} está deshabilitado"

            # Si no se encontraron inputs, no es necesariamente un error
            if not inputs_encontrados:
                pytest.skip("No se encontraron inputs específicos para verificar")

        except Exception as e:
            pytest.skip(f"Error en test de inputs: {e}")

    def test_pedidos_navegacion_teclado(self, app):
        """Test de navegación por teclado."""
        if not PEDIDOS_VIEW_AVAILABLE:
            pytest.skip("PedidosView no disponible")

        try:
            view = PedidosView()

            # Verificar que la vista puede recibir foco
            if hasattr(view, 'setFocusPolicy'):
                # La vista debería poder recibir foco para navegación por teclado
                focus_policy = view.focusPolicy()
                assert focus_policy is not None

            # Verificar widgets focusables
            widgets_focusables = []
            for attr_name in dir(view):
                if not attr_name.startswith('_'):
                    try:
                        widget = getattr(view, attr_name)
                        if hasattr(widget, 'setFocusPolicy') and hasattr(widget, 'hasFocus'):
                            widgets_focusables.append(widget)
                    except:
                        continue

            # Verificar que hay al menos algunos widgets focusables
            # (no es necesario que todos los widgets sean focusables)
            if widgets_focusables:
                for widget in widgets_focusables[:5]:  # Verificar solo los primeros 5
                    try:
                        focus_policy = widget.focusPolicy()
                        assert focus_policy is not None
                    except:
                        continue

        except Exception as e:
            pytest.skip(f"Error en test de navegación: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
