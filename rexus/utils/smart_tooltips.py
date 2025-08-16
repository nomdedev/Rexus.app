"""
Sistema de Tooltips Inteligentes para Rexus.app

Proporciona tooltips contextuales y dinámicos para mejorar la experiencia del usuario.
"""

from typing import Dict
from PyQt6.QtWidgets import QWidget, QToolTip, QLineEdit
from PyQt6.QtCore import QPoint, QTimer


class SmartTooltipsManager:
    """Gestor de tooltips inteligentes para widgets."""

    def __init__(self):
        self.tooltip_data = {}
        self.hover_timer = QTimer()
        self.hover_timer.setSingleShot(True)
        self.hover_timer.timeout.connect(self._show_delayed_tooltip)
        self.current_widget = None
        self.current_tooltip = ""

    def add_tooltip(self, widget: QWidget, text: str, delay: int = 500):
        """Añade un tooltip inteligente a un widget."""
        if widget and text:
            widget.setToolTip(text)
            self.tooltip_data[widget] = {
                'text': text,
                'delay': delay,
                'enhanced': True
            }

    def add_contextual_tooltip(self,
widget: QWidget,
        base_text: str,
        context_func=None):
        """Añade un tooltip que cambia según el contexto."""
        def get_contextual_text():
            if context_func and callable(context_func):
                try:
                    context = context_func()
                    return f"{base_text}\n{context}" if context else base_text
                except (AttributeError, RuntimeError, TypeError, ValueError):
                    return base_text
            return base_text

        self.tooltip_data[widget] = {
            'text': base_text,
            'context_func': get_contextual_text,
            'enhanced': True
        }

        widget.setToolTip(get_contextual_text())

    def _show_delayed_tooltip(self):
        """Muestra el tooltip después del delay."""
        if self.current_widget and self.current_tooltip:
            QToolTip.showText(self.current_widget.mapToGlobal(QPoint(0, 0)), self.current_tooltip)

    def remove_tooltip(self, widget: QWidget):
        """Elimina el tooltip de un widget."""
        if widget in self.tooltip_data:
            del self.tooltip_data[widget]
            widget.setToolTip("")

    def update_tooltip(self, widget: QWidget, new_text: str):
        """Actualiza el texto del tooltip de un widget."""
        if widget in self.tooltip_data:
            self.tooltip_data[widget]['text'] = new_text
            widget.setToolTip(new_text)


# Instancia global del gestor
_tooltip_manager = SmartTooltipsManager()


def setup_smart_tooltips(parent_widget: QWidget):
    """
    Configura tooltips inteligentes para un widget padre y sus hijos.

    Args:
        parent_widget: Widget padre que contendrá los tooltips
    """
    if not parent_widget:
        return

    # Configurar tooltips básicos para widgets comunes
    tooltips_config = {
        'btn_nuevo': 'Crear un nuevo elemento',
        'btn_editar': 'Editar el elemento seleccionado',
        'btn_eliminar': 'Eliminar el elemento seleccionado',
        'btn_actualizar': 'Actualizar la vista de datos',
        'btn_exportar': 'Exportar datos a archivo',
        'btn_buscar': 'Buscar elementos',
        'input_busqueda': 'Escriba para buscar elementos',
        'combo_categoria': 'Filtrar por categoría',
        'combo_estado': 'Filtrar por estado',
        'tabla_principal': 'Tabla de datos principal',
        'btn_guardar': 'Guardar cambios',
        'btn_cancelar': 'Cancelar operación',
    }

    # Aplicar tooltips a widgets encontrados
    for name, tooltip_text in tooltips_config.items():
        widget = getattr(parent_widget, name, None)
        if widget:
            add_tooltip(widget, tooltip_text)

    # Configurar tooltips contextuales para campos de entrada
    for child in parent_widget.findChildren(QLineEdit):
        if hasattr(child, 'objectName'):
            name = child.objectName()
            if name and not child.toolTip():
                if 'codigo' in name.lower():
                    add_tooltip(child, 'Ingrese un código único')
                elif 'nombre' in name.lower():
                    add_tooltip(child, 'Ingrese el nombre')
                elif 'descripcion' in name.lower():
                    add_tooltip(child, 'Ingrese una descripción detallada')
                elif 'precio' in name.lower():
                    add_tooltip(child, 'Ingrese el precio (solo números)')


def add_tooltip(widget: QWidget, text: str, delay: int = 500):
    """Añade un tooltip a un widget específico."""
    _tooltip_manager.add_tooltip(widget, text, delay)


def add_contextual_tooltip(widget: QWidget, base_text: str, context_func=None):
    """Añade un tooltip contextual a un widget."""
    _tooltip_manager.add_contextual_tooltip(widget, base_text, context_func)


def remove_tooltip(widget: QWidget):
    """Elimina el tooltip de un widget."""
    _tooltip_manager.remove_tooltip(widget)


def update_tooltip(widget: QWidget, new_text: str):
    """Actualiza el texto del tooltip de un widget."""
    _tooltip_manager.update_tooltip(widget, new_text)


# Funciones de conveniencia para tipos específicos de tooltips
def setup_form_tooltips(form_widget: QWidget, field_descriptions: Dict[str, str]):
    """
    Configura tooltips para campos de formulario.

    Args:
        form_widget: Widget del formulario
        field_descriptions: Diccionario con nombre_campo: descripción
    """
    for field_name, description in field_descriptions.items():
        field = getattr(form_widget, field_name, None)
        if field:
            add_tooltip(field, description)


def setup_table_tooltips(table_widget: QWidget):
    """Configura tooltips para elementos de tabla."""
    if table_widget:
        add_tooltip(table_widget,
                   "Haga clic para seleccionar, doble clic para editar")


def setup_button_tooltips(parent: QWidget, button_configs: Dict[str, str]):
    """
    Configura tooltips para botones.

    Args:
        parent: Widget padre
        button_configs: Diccionario con nombre_boton: tooltip
    """
    for button_name, tooltip_text in button_configs.items():
        button = getattr(parent, button_name, None)
        if button:
            add_tooltip(button, tooltip_text)


# Tooltips predefinidos para módulos comunes
OBRAS_TOOLTIPS = {
    'btn_nueva_obra': 'Crear una nueva obra o proyecto',
    'btn_editar_obra': 'Editar los datos de la obra seleccionada',
    'btn_eliminar_obra': 'Eliminar permanentemente la obra seleccionada',
    'input_codigo_obra': 'Código único de identificación de la obra',
    'input_nombre_obra': 'Nombre descriptivo de la obra',
    'combo_estado_obra': 'Estado actual de la obra (Activa, Pausada, Finalizada)',
    'fecha_inicio': 'Fecha de inicio planificada de la obra',
    'fecha_fin': 'Fecha de finalización estimada de la obra',
}

INVENTARIO_TOOLTIPS = {
    'btn_nuevo_item': 'Agregar un nuevo artículo al inventario',
    'btn_editar_item': 'Modificar los datos del artículo seleccionado',
    'input_codigo_item': 'Código único del artículo (SKU)',
    'input_stock_actual': 'Cantidad actual en stock',
    'input_stock_minimo': 'Cantidad mínima para alertas de reposición',
}

HERRAJES_TOOLTIPS = {
    'btn_nuevo_herraje': 'Agregar un nuevo herraje al catálogo',
    'input_codigo_herraje': 'Código único del herraje',
    'combo_categoria_herraje': 'Categoría del herraje (Bisagras, Cerraduras, etc.)',
    'input_precio_herraje': 'Precio unitario del herraje',
}
