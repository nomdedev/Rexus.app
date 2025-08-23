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


import logging
logger = logging.getLogger(__name__)

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
