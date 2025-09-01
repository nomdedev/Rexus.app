"""
MIT License

Copyright (c) 2024 Rexus.app

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

"""
Utilidades para diálogos comunes - Rexus.app v2.0.0

Proporciona diálogos reutilizables para operaciones CRUD estándar.
"""

from typing import Any, Dict, List, Callable
from PyQt6.QtWidgets import (
    QDialog, QDialogButtonBox, QFormLayout, QVBoxLayout,
    QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QTextEdit,
    QCheckBox, QDateEdit, QGroupBox, QScrollArea,
    QWidget
)
from datetime import date

from .message_system import show_error, show_success, ask_question


class BaseFormDialog(QDialog):
    """Diálogo base para formularios CRUD."""

    def __init__(self, parent=None, title="Formulario", size=(600, 500)):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedSize(size[0], size[1])

        self.form_fields = {}
        self.init_ui()

    def init_ui(self):
        """Inicializa la interfaz base."""
        layout = QVBoxLayout(self)

        # Área de scroll para formularios largos
        self.scroll_area = QScrollArea()
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)

        self.scroll_area.setWidget(self.scroll_widget)
        self.scroll_area.setWidgetResizable(True)
        layout.addWidget(self.scroll_area)

        # Botones
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
                font-family: 'Segoe UI', sans-serif;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #2c3e50;
            }
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QTextEdit, QDateEdit {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                font-size: 14px;
            }
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus,
            QDoubleSpinBox:focus, QTextEdit:focus, QDateEdit:focus {
                border-color: #3498db;
            }
        """)

    def add_form_group(self,
title: str,
        fields: List[Dict[str,
        Any]]) -> QGroupBox:
        """
        Agrega un grupo de campos al formulario.

        Args:
            title: Título del grupo
            fields: Lista de diccionarios con información de campos

        Returns:
            QGroupBox creado
        """
        group = QGroupBox(title)
        form_layout = QFormLayout(group)

        for field_info in fields:
            field_name = field_info['name']
            field_label = field_info['label']
            field_type = field_info.get('type', 'text')
            field_required = field_info.get('required', False)
            field_options = field_info.get('options', [])
            field_default = field_info.get('default')

            # Crear el widget según el tipo
            if field_type == 'text':
                widget = QLineEdit()
                if field_default:
                    widget.setText(str(field_default))
            elif field_type == 'combo':
                widget = QComboBox()
                widget.addItems(field_options)
                if field_default and field_default in field_options:
                    widget.setCurrentText(field_default)
            elif field_type == 'int':
                widget = QSpinBox()
                widget.setMaximum(field_info.get('max', 99999))
                widget.setMinimum(field_info.get('min', 0))
                if field_default is not None:
                    widget.setValue(int(field_default))
            elif field_type == 'float':
                widget = QDoubleSpinBox()
                widget.setMaximum(field_info.get('max', 99999.99))
                widget.setMinimum(field_info.get('min', 0.0))
                widget.setDecimals(field_info.get('decimals', 2))
                if field_default is not None:
                    widget.setValue(float(field_default))
            elif field_type == 'textarea':
                widget = QTextEdit()
                widget.setMaximumHeight(field_info.get('height', 100))
                if field_default:
                    widget.setText(str(field_default))
            elif field_type == 'checkbox':
                widget = QCheckBox()
                if field_default:
                    widget.setChecked(bool(field_default))
            elif field_type == 'date':
                widget = QDateEdit()
                widget.setCalendarPopup(True)
                if field_default:
                    widget.setDate(field_default)
                else:
                    widget.setDate(date.today())
            else:
                widget = QLineEdit()

            # Marcar campos requeridos
            label_text = field_label
            if field_required:
                label_text += " *"
                widget.setStyleSheet(widget.styleSheet() + "border-left: 3px solid #e74c3c;")

            form_layout.addRow(label_text, widget)
            self.form_fields[field_name] = {
                'widget': widget,
                'type': field_type,
                'required': field_required,
                'label': field_label
            }

        self.scroll_layout.addWidget(group)
        return group

    def get_form_data(self) -> Dict[str, Any]:
        """Obtiene todos los datos del formulario."""
        data = {}

        for field_name, field_info in self.form_fields.items():
            widget = field_info['widget']
            field_type = field_info['type']

            if field_type == 'text':
                data[field_name] = widget.text()
            elif field_type == 'combo':
                data[field_name] = widget.currentText()
            elif field_type == 'int':
                data[field_name] = widget.value()
            elif field_type == 'float':
                data[field_name] = widget.value()
            elif field_type == 'textarea':
                data[field_name] = widget.toPlainText()
            elif field_type == 'checkbox':
                data[field_name] = widget.isChecked()
            elif field_type == 'date':
                data[field_name] = widget.date().toPython()
            else:
                data[field_name] = widget.text()

        return data

    def set_form_data(self, data: Dict[str, Any]):
        """Establece los datos del formulario."""
        for field_name, value in data.items():
            if field_name in self.form_fields:
                field_info = self.form_fields[field_name]
                widget = field_info['widget']
                field_type = field_info['type']

                if field_type == 'text':
                    widget.setText(str(value) if value is not None else "")
                elif field_type == 'combo':
                    widget.setCurrentText(str(value) if value is not None else "")
                elif field_type == 'int':
                    widget.setValue(int(value) if value is not None else 0)
                elif field_type == 'float':
                    widget.setValue(float(value) if value is not None else 0.0)
                elif field_type == 'textarea':
                    widget.setText(str(value) if value is not None else "")
                elif field_type == 'checkbox':
                    widget.setChecked(bool(value) if value is not None else False)
                elif field_type == 'date':
                    if value:
                        widget.setDate(value)

    def validate_form(self) -> tuple[bool, List[str]]:
        """
        Valida el formulario.

        Returns:
            tuple[bool, List[str]]: (es_válido, lista_errores)
        """
        errors = []

        for field_name, field_info in self.form_fields.items():
            if field_info['required']:
                widget = field_info['widget']
                field_type = field_info['type']
                label = field_info['label']

                is_empty = False

                if field_type in ['text', 'textarea']:
                    is_empty = not widget.text().strip() if hasattr(widget, 'text') else not widget.toPlainText().strip()
                elif field_type == 'combo':
                    is_empty = not widget.currentText().strip()

                if is_empty:
                    errors.append(f"El campo '{label}' es obligatorio")

        return len(errors) == 0, errors

    def accept(self):
        """Override para validar antes de aceptar."""
        is_valid, errors = self.validate_form()

        if not is_valid:
            error_message = "Errores de validación:\n\n• " + "\n• ".join(errors)
            show_error(self, "Errores de Validación", error_message)
            return

        super().accept()


class ConfirmDeleteDialog:
    """Utilidad para diálogos de confirmación de eliminación."""

    @staticmethod
    def confirm_delete(parent, item_name: str, item_type: str = "elemento") -> bool:
        """
        Muestra un diálogo de confirmación para eliminar un elemento.

        Args:
            parent: Widget padre
            item_name: Nombre del elemento a eliminar
            item_type: Tipo de elemento (por defecto "elemento")

        Returns:
            bool: True si el usuario confirma la eliminación
        """
        return ask_question(
            parent,
            "Confirmar eliminación",
            f"¿Está seguro que desea eliminar el {item_type} '{item_name}'?\n\n"
            "Esta acción no se puede deshacer."
        )


class CrudDialogManager:
    """Gestor de diálogos CRUD estándar."""

    def __init__(self, parent_widget, controller=None):
        self.parent = parent_widget
        self.controller = controller

    def show_create_dialog(self, form_config: Dict[str, Any],
                          create_callback: Callable[[Dict], bool]) -> bool:
        """
        Muestra un diálogo de creación.

        Args:
            form_config: Configuración del formulario
            create_callback: Función callback para crear el elemento

        Returns:
            bool: True si se creó exitosamente
        """
        dialog = BaseFormDialog(
            self.parent,
            form_config.get('title', 'Crear Elemento'),
            form_config.get('size', (600, 500))
        )

        # Agregar grupos de campos
        for group in form_config.get('groups', []):
            dialog.add_form_group(group['title'], group['fields'])

        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_form_data()
            try:
                success = create_callback(data)
                if success:
                    show_success(
                        self.parent,
                        "Creación Exitosa",
                        f"{form_config.get('item_name', 'Elemento')} creado exitosamente."
                    )
                    return True
                else:
                    show_error(
                        self.parent,
                        "Error al Crear",
                        f"No se pudo crear el {form_config.get('item_name', 'elemento')}."
                    )
            except Exception as e:
                show_error(
                    self.parent,
                    "Error al Crear",
                    f"Error creando {form_config.get('item_name', 'elemento')}: {str(e)}"
                )

        return False

    def show_edit_dialog(self, form_config: Dict[str, Any],
                        current_data: Dict[str, Any],
                        update_callback: Callable[[Dict], bool]) -> bool:
        """
        Muestra un diálogo de edición.

        Args:
            form_config: Configuración del formulario
            current_data: Datos actuales del elemento
            update_callback: Función callback para actualizar el elemento

        Returns:
            bool: True si se actualizó exitosamente
        """
        dialog = BaseFormDialog(
            self.parent,
            form_config.get('title', 'Editar Elemento'),
            form_config.get('size', (600, 500))
        )

        # Agregar grupos de campos
        for group in form_config.get('groups', []):
            dialog.add_form_group(group['title'], group['fields'])

        # Cargar datos actuales
        dialog.set_form_data(current_data)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_form_data()
            try:
                success = update_callback(data)
                if success:
                    show_success(
                        self.parent,
                        "Actualización Exitosa",
                        f"{form_config.get('item_name', 'Elemento')} actualizado exitosamente."
                    )
                    return True
                else:
                    show_error(
                        self.parent,
                        "Error al Actualizar",
                        f"No se pudo actualizar el {form_config.get('item_name', 'elemento')}."
                    )
            except Exception as e:
                show_error(
                    self.parent,
                    "Error al Actualizar",
                    f"Error actualizando {form_config.get('item_name', 'elemento')}: {str(e)}"
                )

        return False

    def confirm_and_delete(self, item_name: str, item_type: str,
                          delete_callback: Callable[[], bool]) -> bool:
        """
        Confirma y ejecuta una eliminación.

        Args:
            item_name: Nombre del elemento
            item_type: Tipo de elemento
            delete_callback: Función callback para eliminar

        Returns:
            bool: True si se eliminó exitosamente
        """
        if ConfirmDeleteDialog.confirm_delete(self.parent, item_name, item_type):
            try:
                success = delete_callback()
                if success:
                    show_success(
                        self.parent,
                        "Eliminación Exitosa",
                        f"{item_type.capitalize()} eliminado exitosamente."
                    )
                    return True
                else:
                    show_error(
                        self.parent,
                        "Error al Eliminar",
                        f"No se pudo eliminar el {item_type}."
                    )
            except Exception as e:
                show_error(
                    self.parent,
                    "Error al Eliminar",
                    f"Error eliminando {item_type}: {str(e)}"
                )

        return False


def create_standard_form_config(title: str, item_name: str,
                               groups: List[Dict], size: tuple = (600, 500)) -> Dict:
    """
    Crea una configuración estándar para formularios.

    Args:
        title: Título del formulario
        item_name: Nombre del elemento (para mensajes)
        groups: Lista de grupos de campos
        size: Tamaño del diálogo

    Returns:
        Dict: Configuración del formulario
    """
    return {
        'title': title,
        'item_name': item_name,
        'groups': groups,
        'size': size
    }
