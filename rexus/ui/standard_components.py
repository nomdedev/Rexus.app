"""
Componentes estándar de UI para compatibilidad
Este archivo proporciona componentes básicos para la interfaz de usuario.
"""

from typing import Any, Dict, List, Optional
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QComboBox, QTableWidget, QTableWidgetItem, QHeaderView
from PyQt6.QtCore import Qt, pyqtSignal

class StandardComponents:
    """Clase que proporciona componentes estándar para la UI."""
    
    @staticmethod
    def create_form_layout() -> QVBoxLayout:
        """Crea un layout de formulario estándar."""
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        return layout
    
    @staticmethod
    def create_button(text: str, callback=None) -> QPushButton:
        """Crea un botón estándar."""
        button = QPushButton(text)
        button.setMinimumHeight(35)
        if callback:
            button.clicked.connect(callback)
        return button
    
    @staticmethod
    def create_label(text: str, bold: bool = False) -> QLabel:
        """Crea una etiqueta estándar."""
        label = QLabel(text)
        if bold:
            label.setStyleSheet("font-weight: bold;")
        return label
    
    @staticmethod
    def create_input(placeholder: str = "") -> QLineEdit:
        """Crea un campo de entrada estándar."""
        input_field = QLineEdit()
        input_field.setPlaceholderText(placeholder)
        input_field.setMinimumHeight(30)
        return input_field
    
    @staticmethod
    def create_combo(items: List[str]) -> QComboBox:
        """Crea un combo box estándar."""
        combo = QComboBox()
        combo.addItems(items)
        combo.setMinimumHeight(30)
        return combo
    
    @staticmethod
    def create_table(headers: List[str]) -> QTableWidget:
        """Crea una tabla estándar."""
        table = QTableWidget()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        
        # Configurar encabezados
        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        return table
    
    @staticmethod
    def populate_table(table: QTableWidget, data: List[Dict[str, Any]]):
        """Llena una tabla con datos."""
        table.setRowCount(len(data))
        
        for row, item in enumerate(data):
            for col, key in enumerate(item.keys()):
                table.setItem(row, col, QTableWidgetItem(str(item[key])))
    
    @staticmethod
    def clear_table(table: QTableWidget):
        """Limpia una tabla."""
        table.setRowCount(0)


class StandardForm(QWidget):
    """Formulario estándar con componentes básicos."""
    
    submitted = pyqtSignal(dict)
    
    def __init__(self, title: str, fields: List[Dict[str, Any]], parent=None):
        super().__init__(parent)
        self.title = title
        self.fields = fields
        self.widgets = {}
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz del formulario."""
        layout = StandardComponents.create_form_layout()
        
        # Título
        title_label = StandardComponents.create_label(self.title, bold=True)
        layout.addWidget(title_label)
        
        # Campos
        for field in self.fields:
            field_layout = QHBoxLayout()
            
            label = StandardComponents.create_label(field.get('label', ''))
            field_layout.addWidget(label)
            
            if field['type'] == 'text':
                widget = StandardComponents.create_input(field.get('placeholder', ''))
            elif field['type'] == 'combo':
                widget = StandardComponents.create_combo(field.get('options', []))
            else:
                widget = QWidget()
            
            self.widgets[field['name']] = widget
            field_layout.addWidget(widget)
            
            layout.addLayout(field_layout)
        
        # Botones
        button_layout = QHBoxLayout()
        
        save_button = StandardComponents.create_button("Guardar", self.on_save)
        button_layout.addWidget(save_button)
        
        cancel_button = StandardComponents.create_button("Cancelar", self.on_cancel)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def on_save(self):
        """Manejador del evento guardar."""
        data = {}
        for field in self.fields:
            widget = self.widgets[field['name']]
            if field['type'] == 'text':
                data[field['name']] = widget.text()
            elif field['type'] == 'combo':
                data[field['name']] = widget.currentText()
        
        self.submitted.emit(data)
    
    def on_cancel(self):
        """Manejador del evento cancelar."""
        self.close()
    
    def get_data(self) -> Dict[str, Any]:
        """Obtiene los datos del formulario."""
        data = {}
        for field in self.fields:
            widget = self.widgets[field['name']]
            if field['type'] == 'text':
                data[field['name']] = widget.text()
            elif field['type'] == 'combo':
                data[field['name']] = widget.currentText()
        return data
    
    def set_data(self, data: Dict[str, Any]):
        """Establece los datos del formulario."""
        for field in self.fields:
            widget = self.widgets[field['name']]
            value = data.get(field['name'])
            if value is not None:
                if field['type'] == 'text':
                    widget.setText(str(value))
                elif field['type'] == 'combo':
                    index = widget.findText(str(value))
                    if index >= 0:
                        widget.setCurrentIndex(index)