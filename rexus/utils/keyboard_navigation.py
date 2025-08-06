"""
Sistema de Navegación por Teclado Completa - Rexus.app
Proporciona navegación consistente y accesible en todos los módulos
"""

from typing import Callable, Dict, List, Optional

from PyQt6.QtCore import QEvent, QObject, Qt
from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QWidget,
)


class KeyboardNavigationMode:
    """Modos de navegación por teclado."""

    FORM = "form"  # Navegación en formularios
    TABLE = "table"  # Navegación en tablas
    TREE = "tree"  # Navegación en árboles
    TAB = "tab"  # Navegación en tabs
    DIALOG = "dialog"  # Navegación en diálogos


class KeyboardAction:
    """Acciones estándar de navegación."""

    # Navegación básica
    NEXT_FIELD = "next_field"
    PREV_FIELD = "prev_field"
    FIRST_FIELD = "first_field"
    LAST_FIELD = "last_field"

    # Navegación en tablas
    NEXT_ROW = "next_row"
    PREV_ROW = "prev_row"
    FIRST_ROW = "first_row"
    LAST_ROW = "last_row"
    NEXT_COLUMN = "next_column"
    PREV_COLUMN = "prev_column"

    # Acciones CRUD
    NEW_RECORD = "new_record"
    EDIT_RECORD = "edit_record"
    DELETE_RECORD = "delete_record"
    SAVE_RECORD = "save_record"
    CANCEL_EDIT = "cancel_edit"

    # Búsqueda y filtros
    FOCUS_SEARCH = "focus_search"
    CLEAR_SEARCH = "clear_search"
    APPLY_FILTER = "apply_filter"
    CLEAR_FILTERS = "clear_filters"

    # General
    REFRESH = "refresh"
    HELP = "help"
    EXIT = "exit"


class StandardShortcuts:
    """Atajos de teclado estándar del sistema."""

    # Mapeo de acciones a atajos
    SHORTCUTS = {
        # Navegación básica
        KeyboardAction.NEXT_FIELD: ["Tab"],
        KeyboardAction.PREV_FIELD: ["Shift+Tab"],
        KeyboardAction.FIRST_FIELD: ["Ctrl+Home"],
        KeyboardAction.LAST_FIELD: ["Ctrl+End"],
        # Navegación en tablas
        KeyboardAction.NEXT_ROW: ["Down", "Ctrl+Down"],
        KeyboardAction.PREV_ROW: ["Up", "Ctrl+Up"],
        KeyboardAction.FIRST_ROW: ["Ctrl+Home"],
        KeyboardAction.LAST_ROW: ["Ctrl+End"],
        KeyboardAction.NEXT_COLUMN: ["Right", "Tab"],
        KeyboardAction.PREV_COLUMN: ["Left", "Shift+Tab"],
        # Acciones CRUD
        KeyboardAction.NEW_RECORD: ["Ctrl+N", "Insert"],
        KeyboardAction.EDIT_RECORD: ["Ctrl+E", "F2"],
        KeyboardAction.DELETE_RECORD: ["Delete", "Ctrl+D"],
        KeyboardAction.SAVE_RECORD: ["Ctrl+S"],
        KeyboardAction.CANCEL_EDIT: ["Escape"],
        # Búsqueda y filtros
        KeyboardAction.FOCUS_SEARCH: ["Ctrl+F", "F3"],
        KeyboardAction.CLEAR_SEARCH: ["Escape"],
        KeyboardAction.APPLY_FILTER: ["Enter"],
        KeyboardAction.CLEAR_FILTERS: ["Ctrl+R"],
        # General
        KeyboardAction.REFRESH: ["F5"],
        KeyboardAction.HELP: ["F1"],
        KeyboardAction.EXIT: ["Escape", "Alt+F4"],
    }

    @classmethod
    def get_shortcuts(cls, action: str) -> List[str]:
        """Obtiene los atajos para una acción específica."""
        return cls.SHORTCUTS.get(action, [])

    @classmethod
    def get_primary_shortcut(cls, action: str) -> str:
        """Obtiene el atajo principal para una acción."""
        shortcuts = cls.get_shortcuts(action)
        return shortcuts[0] if shortcuts else ""


class TabOrderManager:
    """Gestor del orden de tabulación en formularios."""

    def __init__(self, parent_widget: QWidget):
        self.parent = parent_widget
        self.tab_order: List[QWidget] = []
        self.current_index = 0

    def add_widget(self, widget: QWidget, index: Optional[int] = None):
        """Añade un widget al orden de tabulación."""
        if widget and widget.isEnabled():
            if index is not None:
                self.tab_order.insert(index, widget)
            else:
                self.tab_order.append(widget)

    def remove_widget(self, widget: QWidget):
        """Remueve un widget del orden de tabulación."""
        if widget in self.tab_order:
            self.tab_order.remove(widget)

    def set_tab_order(self, widgets: List[QWidget]):
        """Establece el orden completo de tabulación."""
        self.tab_order = [w for w in widgets if w and w.isEnabled()]
        self._apply_qt_tab_order()

    def auto_detect_tab_order(self):
        """Detecta automáticamente el orden de tabulación basado en la posición."""
        focusable_widgets = []

        def collect_widgets(widget: QWidget):
            if self._is_focusable(widget):
                focusable_widgets.append(widget)

            for child in widget.findChildren(QWidget):
                if self._is_focusable(child):
                    focusable_widgets.append(child)

        collect_widgets(self.parent)

        # Ordenar por posición (top-left a bottom-right)
        focusable_widgets.sort(key=lambda w: (w.pos().y(), w.pos().x()))
        self.set_tab_order(focusable_widgets)

    def _is_focusable(self, widget: QWidget) -> bool:
        """Verifica si un widget puede recibir foco."""
        return (
            widget.isVisible()
            and widget.isEnabled()
            and widget.focusPolicy() != Qt.FocusPolicy.NoFocus
            and isinstance(widget, (QLineEdit, QComboBox, QPushButton, QTableWidget))
        )

    def _apply_qt_tab_order(self):
        """Aplica el orden de tabulación usando Qt."""
        for i in range(len(self.tab_order) - 1):
            QWidget.setTabOrder(self.tab_order[i], self.tab_order[i + 1])

    def next_widget(self) -> Optional[QWidget]:
        """Obtiene el siguiente widget en el orden."""
        if not self.tab_order:
            return None

        self.current_index = (self.current_index + 1) % len(self.tab_order)
        return self.tab_order[self.current_index]

    def prev_widget(self) -> Optional[QWidget]:
        """Obtiene el widget anterior en el orden."""
        if not self.tab_order:
            return None

        self.current_index = (self.current_index - 1) % len(self.tab_order)
        return self.tab_order[self.current_index]


class TableNavigationManager:
    """Gestor de navegación específico para tablas."""

    def __init__(self, table: QTableWidget):
        self.table = table
        self.setup_table_navigation()

    def setup_table_navigation(self):
        """Configura la navegación por teclado en la tabla."""
        # Permitir navegación por celdas
        self.table.setTabKeyNavigation(True)

        # Configurar selección por filas
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        # Instalar filtro de eventos para navegación avanzada
        self.table.installEventFilter(TableKeyEventFilter(self.table))

    def go_to_first_row(self):
        """Va a la primera fila."""
        if self.table.rowCount() > 0:
            self.table.setCurrentCell(0, self.table.currentColumn())

    def go_to_last_row(self):
        """Va a la última fila."""
        if self.table.rowCount() > 0:
            self.table.setCurrentCell(
                self.table.rowCount() - 1, self.table.currentColumn()
            )

    def go_to_first_column(self):
        """Va a la primera columna."""
        if self.table.columnCount() > 0:
            self.table.setCurrentCell(self.table.currentRow(), 0)

    def go_to_last_column(self):
        """Va a la última columna."""
        if self.table.columnCount() > 0:
            self.table.setCurrentCell(
                self.table.currentRow(), self.table.columnCount() - 1
            )


class TableKeyEventFilter(QObject):
    """Filtro de eventos para navegación avanzada en tablas."""

    def __init__(self, table: QTableWidget):
        super().__init__()
        self.table = table

    def eventFilter(self, a0: Optional[QObject], a1: Optional[QEvent]) -> bool:
        if a1 and a0 and a1.type() == QEvent.Type.KeyPress and a0 == self.table:
            # Cast seguro ya que verificamos el tipo
            key_event = a1
            if hasattr(key_event, "key"):  # Verificación adicional de seguridad
                return self.handle_key_press(key_event)
        return super().eventFilter(a0, a1)

    def handle_key_press(self, event) -> bool:
        """Maneja eventos de teclado específicos para la tabla."""
        key = event.key()
        modifiers = event.modifiers()

        # Ctrl+Home: Ir a primera celda
        if key == Qt.Key.Key_Home and modifiers == Qt.KeyboardModifier.ControlModifier:
            self.table.setCurrentCell(0, 0)
            return True

        # Ctrl+End: Ir a última celda
        if key == Qt.Key.Key_End and modifiers == Qt.KeyboardModifier.ControlModifier:
            last_row = self.table.rowCount() - 1
            last_col = self.table.columnCount() - 1
            self.table.setCurrentCell(last_row, last_col)
            return True

        # Page Up/Down: Navegación por páginas
        if key == Qt.Key.Key_PageUp:
            current_row = max(0, self.table.currentRow() - 10)
            self.table.setCurrentCell(current_row, self.table.currentColumn())
            return True

        if key == Qt.Key.Key_PageDown:
            current_row = min(self.table.rowCount() - 1, self.table.currentRow() + 10)
            self.table.setCurrentCell(current_row, self.table.currentColumn())
            return True

        return False


class KeyboardNavigationManager:
    """Gestor principal de navegación por teclado."""

    def __init__(self, parent: QWidget):
        self.parent = parent
        self.tab_manager = TabOrderManager(parent)
        self.shortcuts: Dict[str, QShortcut] = {}
        self.actions: Dict[str, Callable] = {}
        self.mode = KeyboardNavigationMode.FORM

        # Configurar atajos básicos
        self.setup_basic_shortcuts()

    def setup_basic_shortcuts(self):
        """Configura los atajos básicos del sistema."""
        # Navegación básica
        self.register_action(KeyboardAction.FOCUS_SEARCH, self._focus_search_field)
        self.register_action(KeyboardAction.REFRESH, self._refresh_data)
        self.register_action(KeyboardAction.HELP, self._show_help)

    def register_action(
        self,
        action: str,
        callback: Callable,
        custom_shortcuts: Optional[List[str]] = None,
    ):
        """Registra una acción con sus atajos de teclado."""
        shortcuts = custom_shortcuts or StandardShortcuts.get_shortcuts(action)

        self.actions[action] = callback

        for shortcut_str in shortcuts:
            shortcut = QShortcut(QKeySequence(shortcut_str), self.parent)
            shortcut.activated.connect(callback)
            self.shortcuts[f"{action}_{shortcut_str}"] = shortcut

    def unregister_action(self, action: str):
        """Desregistra una acción y sus atajos."""
        if action in self.actions:
            del self.actions[action]

        # Remover atajos asociados
        keys_to_remove = [
            k for k in self.shortcuts.keys() if k.startswith(f"{action}_")
        ]
        for key in keys_to_remove:
            shortcut = self.shortcuts[key]
            shortcut.deleteLater()
            del self.shortcuts[key]

    def set_mode(self, mode: str):
        """Establece el modo de navegación actual."""
        self.mode = mode

        if mode == KeyboardNavigationMode.FORM:
            self.tab_manager.auto_detect_tab_order()
        elif mode == KeyboardNavigationMode.TABLE:
            self._setup_table_mode()

    def _setup_table_mode(self):
        """Configura el modo de navegación para tablas."""
        # Buscar tabla principal en el widget
        table = self.parent.findChild(QTableWidget)
        if table:
            TableNavigationManager(table)

    def add_custom_shortcut(
        self, key_sequence: str, callback: Callable, description: str = ""
    ):
        """Añade un atajo personalizado."""
        shortcut = QShortcut(QKeySequence(key_sequence), self.parent)
        shortcut.activated.connect(callback)
        self.shortcuts[f"custom_{key_sequence}"] = shortcut

    def get_shortcuts_help(self) -> Dict[str, str]:
        """Obtiene la ayuda de atajos disponibles."""
        help_text = {}

        for action, callback in self.actions.items():
            shortcuts = StandardShortcuts.get_shortcuts(action)
            if shortcuts:
                shortcut_text = " / ".join(shortcuts)
                action_name = action.replace("_", " ").title()
                help_text[action_name] = shortcut_text

        return help_text

    def _focus_search_field(self):
        """Enfoca el campo de búsqueda."""
        search_field = self.parent.findChild(QLineEdit, "campo_busqueda")
        if search_field:
            search_field.setFocus()
            search_field.selectAll()

    def _refresh_data(self):
        """Actualiza los datos del módulo."""
        if hasattr(self.parent, "actualizar_datos") and callable(
            getattr(self.parent, "actualizar_datos")
        ):
            getattr(self.parent, "actualizar_datos")()

    def _show_help(self):
        """Muestra la ayuda de atajos de teclado."""
        if hasattr(self.parent, "mostrar_ayuda_atajos") and callable(
            getattr(self.parent, "mostrar_ayuda_atajos")
        ):
            getattr(self.parent, "mostrar_ayuda_atajos")()


class AccessibilityHelper:
    """Utilidades para mejorar la accesibilidad."""

    @staticmethod
    def set_accessible_description(widget: QWidget, description: str):
        """Establece una descripción accesible para un widget."""
        widget.setAccessibleDescription(description)

    @staticmethod
    def set_accessible_name(widget: QWidget, name: str):
        """Establece un nombre accesible para un widget."""
        widget.setAccessibleName(name)

    @staticmethod
    def make_form_accessible(form_layout: QFormLayout):
        """Hace un formulario más accesible."""
        for i in range(form_layout.rowCount()):
            label_item = form_layout.itemAt(i, QFormLayout.ItemRole.LabelRole)
            field_item = form_layout.itemAt(i, QFormLayout.ItemRole.FieldRole)

            if label_item and field_item:
                label_widget = label_item.widget()
                field_widget = field_item.widget()

                if label_widget and field_widget:
                    # Asociar label con campo - verificar si es QLabel
                    if hasattr(label_widget, "setBuddy") and callable(
                        getattr(label_widget, "setBuddy", None)
                    ):
                        getattr(label_widget, "setBuddy")(field_widget)

                    # Establecer nombres accesibles
                    if hasattr(label_widget, "text") and callable(
                        getattr(label_widget, "text", None)
                    ):
                        label_text = getattr(label_widget, "text")()
                        field_widget.setAccessibleName(label_text)

    @staticmethod
    def announce_to_screen_reader(message: str):
        """Anuncia un mensaje a lectores de pantalla."""
        # En un entorno real, esto se integraría con APIs de accesibilidad
        print(f"[Screen Reader] {message}")


# Función de utilidad para configurar navegación en un widget
def setup_keyboard_navigation(
    widget: QWidget, mode: str = KeyboardNavigationMode.FORM
) -> KeyboardNavigationManager:
    """Configura la navegación por teclado en un widget."""
    manager = KeyboardNavigationManager(widget)
    manager.set_mode(mode)
    return manager


# Función para crear atajos estándar de CRUD
def setup_crud_shortcuts(
    widget: QWidget, callbacks: Dict[str, Callable]
) -> KeyboardNavigationManager:
    """Configura atajos estándar para operaciones CRUD."""
    manager = setup_keyboard_navigation(widget)

    crud_actions = {
        KeyboardAction.NEW_RECORD: callbacks.get("new"),
        KeyboardAction.EDIT_RECORD: callbacks.get("edit"),
        KeyboardAction.DELETE_RECORD: callbacks.get("delete"),
        KeyboardAction.SAVE_RECORD: callbacks.get("save"),
        KeyboardAction.CANCEL_EDIT: callbacks.get("cancel"),
    }

    for action, callback in crud_actions.items():
        if callback:
            manager.register_action(action, callback)

    return manager
