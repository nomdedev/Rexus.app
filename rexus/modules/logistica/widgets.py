"""
Widgets y componentes reutilizables para el módulo de Logística

Centraliza la creación de componentes UI comunes para evitar duplicación de código.
"""

from typing import Optional, List, Callable
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QPushButton, QLabel, QFrame, QTableWidget, QTableWidgetItem,
    QLineEdit, QComboBox, QGroupBox, QProgressBar, QTextEdit,
    QDateEdit, QHeaderView, QMessageBox
)
from PyQt6.QtCore import QDate

from .constants import UI_CONFIG, BUTTON_STYLES, ICONS
from .styles import BUTTON_STYLES


class LogisticaButton(QPushButton):
    """Botón estilizado para el módulo de logística."""
    
    def __init__(self, text: str, button_type: str = "info", icon: str = "", parent=None):
        super().__init__(parent)
        
        # Configurar texto con icono opcional
        if icon:
            self.setText(f"{icon} {text}")
        else:
            self.setText(text)
        
        # Aplicar estilo según el tipo
        if button_type in BUTTON_STYLES:
            self.setStyleSheet(BUTTON_STYLES[button_type])
        
        # Configurar tamaño mínimo
        self.setMinimumHeight(UI_CONFIG["heights"]["button_height"])


class LogisticaTable(QTableWidget):
    """Tabla estilizada para el módulo de logística."""
    
    def __init__(self, headers: List[str], parent=None):
        super().__init__(parent)
        
        # Configurar columnas
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)
        
        # Configurar comportamiento
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        # Configurar header
        header = self.horizontalHeader()
        if header:
            header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            # ID column fijo si existe
            if headers and headers[0].lower() == "id":
                header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
                self.setColumnWidth(0, UI_CONFIG["heights"]["table_column_id"])


class LogisticaGroupBox(QGroupBox):
    """GroupBox estilizado para el módulo de logística."""
    
    def __init__(self, title: str, parent=None):
        super().__init__(title, parent)
        
        # Configurar layout por defecto
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(UI_CONFIG["spacing"]["main_layout"])
        self.layout.setContentsMargins(
            UI_CONFIG["spacing"]["groupbox_margins"],
            UI_CONFIG["spacing"]["groupbox_margins"] + 10,  # Extra espacio para el título
            UI_CONFIG["spacing"]["groupbox_margins"],
            UI_CONFIG["spacing"]["groupbox_margins"]
        )
    
    def add_widget(self, widget: QWidget):
        """Añade un widget al layout del GroupBox."""
        self.layout.addWidget(widget)
    
    def add_layout(self, layout):
        """Añade un layout al layout del GroupBox."""
        self.layout.addLayout(layout)


class StatisticFrame(QFrame):
    """Frame para mostrar estadísticas con valor y título."""
    
    def __init__(self, title: str, value: str = "0", parent=None):
        super().__init__(parent)
        
        self.setObjectName("stat_frame")
        
        # Layout vertical
        layout = QVBoxLayout(self)
        layout.setSpacing(4)
        
        # Título
        self.title_label = QLabel(title)
        self.title_label.setObjectName("stat_title")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)
        
        # Valor
        self.value_label = QLabel(value)
        self.value_label.setObjectName("stat_value")
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.value_label)
        
        # Configurar tamaño fijo para uniformidad
        self.setFixedSize(120, 60)
    
    def update_value(self, value: str):
        """Actualiza el valor mostrado."""
        self.value_label.setText(value)


class FilterPanel(QWidget):
    """Panel de filtros reutilizable."""
    
    filter_changed = pyqtSignal(dict)  # Emite los filtros actuales
    
    def __init__(self, filters_config: dict, parent=None):
        """
        Args:
            filters_config: Diccionario con configuración de filtros
                           {"search": True, "combo_estado": ["option1", "option2"]}
        """
        super().__init__(parent)
        
        self.filters = {}
        self.setup_ui(filters_config)
    
    def setup_ui(self, config: dict):
        """Configura la interfaz según la configuración."""
        layout = QHBoxLayout(self)
        layout.setSpacing(UI_CONFIG["spacing"]["main_layout"])
        
        # Campo de búsqueda
        if config.get("search", False):
            layout.addWidget(QLabel("Buscar:"))
            
            self.search_input = QLineEdit()
            self.search_input.setPlaceholderText("Buscar...")
            self.search_input.setFixedWidth(UI_CONFIG["widget_widths"]["search_input"])
            self.search_input.textChanged.connect(self._on_filter_changed)
            layout.addWidget(self.search_input)
            
            self.filters["search"] = self.search_input
        
        # Combos de filtro
        for key, options in config.items():
            if key != "search" and isinstance(options, list):
                layout.addWidget(QLabel(f"{key.replace('_', ' ').title()}:"))
                
                combo = QComboBox()
                combo.addItems(options)
                combo.setFixedWidth(UI_CONFIG["widget_widths"]["combo_estado"])
                combo.currentTextChanged.connect(self._on_filter_changed)
                layout.addWidget(combo)
                
                self.filters[key] = combo
        
        layout.addStretch()
    
    def _on_filter_changed(self):
        """Emite señal cuando cambian los filtros."""
        current_filters = {}
        
        for key, widget in self.filters.items():
            if isinstance(widget, QLineEdit):
                current_filters[key] = widget.text()
            elif isinstance(widget, QComboBox):
                current_filters[key] = widget.currentText()
        
        self.filter_changed.emit(current_filters)
    
    def get_filters(self) -> dict:
        """Retorna los filtros actuales."""
        current_filters = {}
        
        for key, widget in self.filters.items():
            if isinstance(widget, QLineEdit):
                current_filters[key] = widget.text()
            elif isinstance(widget, QComboBox):
                current_filters[key] = widget.currentText()
        
        return current_filters


class FormBuilder:
    """Constructor de formularios para evitar duplicación."""
    
    @staticmethod
    def create_form_layout(fields_config: dict) -> tuple[QFormLayout, dict]:
        """
        Crea un layout de formulario con los campos especificados.
        
        Args:
            fields_config: Diccionario con configuración de campos
                          {"field_name": {"type": "line_edit", "placeholder": "...", "width": 200}}
        
        Returns:
            Tupla con (layout, widgets_dict)
        """
        layout = QFormLayout()
        widgets = {}
        
        for field_name, config in fields_config.items():
            widget_type = config.get("type", "line_edit")
            label = config.get("label", field_name.replace("_", " ").title())
            
            # Crear widget según el tipo
            if widget_type == "line_edit":
                widget = QLineEdit()
                if "placeholder" in config:
                    widget.setPlaceholderText(config["placeholder"])
                if "width" in config:
                    widget.setFixedWidth(config["width"])
                elif field_name in UI_CONFIG["widget_widths"]:
                    widget.setFixedWidth(UI_CONFIG["widget_widths"][field_name])
                    
            elif widget_type == "combo_box":
                widget = QComboBox()
                if "options" in config:
                    widget.addItems(config["options"])
                if "width" in config:
                    widget.setFixedWidth(config["width"])
                elif field_name in UI_CONFIG["widget_widths"]:
                    widget.setFixedWidth(UI_CONFIG["widget_widths"][field_name])
                    
            elif widget_type == "date_edit":
                widget = QDateEdit()
                widget.setDate(QDate.currentDate())
                widget.setCalendarPopup(True)
                if "width" in config:
                    widget.setFixedWidth(config["width"])
                elif field_name in UI_CONFIG["widget_widths"]:
                    widget.setFixedWidth(UI_CONFIG["widget_widths"][field_name])
                    
            elif widget_type == "text_edit":
                widget = QTextEdit()
                if "placeholder" in config:
                    widget.setPlaceholderText(config["placeholder"])
                if "height" in config:
                    widget.setMaximumHeight(config["height"])
                elif field_name in UI_CONFIG["heights"]:
                    widget.setMaximumHeight(UI_CONFIG["heights"][field_name])
            else:
                continue  # Tipo no soportado
            
            layout.addRow(f"{label}:", widget)
            widgets[field_name] = widget
        
        return layout, widgets


class NotificationManager:
    """Gestor centralizado de notificaciones."""
    
    @staticmethod
    def show_success(parent: QWidget, title: str, message: str):
        """Muestra mensaje de éxito."""
        msg = QMessageBox(parent)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.exec()
    
    @staticmethod
    def show_error(parent: QWidget, title: str, message: str):
        """Muestra mensaje de error."""
        msg = QMessageBox(parent)
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.exec()
    
    @staticmethod
    def show_warning(parent: QWidget, title: str, message: str):
        """Muestra mensaje de advertencia."""
        msg = QMessageBox(parent)
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.exec()
    
    @staticmethod
    def ask_confirmation(parent: QWidget, title: str, message: str) -> bool:
        """Muestra diálogo de confirmación."""
        reply = QMessageBox.question(
            parent, title, message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        return reply == QMessageBox.StandardButton.Yes