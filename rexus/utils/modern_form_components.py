"""
Componentes modernos para formularios con feedback visual mejorado
"""

import sys
from typing import Dict, List, Optional, Any, Callable
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtGui import QFont, QColor, QPalette, QPainter, QPixmap
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QLineEdit,
    QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit, QCheckBox,
    QPushButton, QFrame, QScrollArea, QDialog, QDialogButtonBox,
    QProgressBar, QApplication, QGraphicsDropShadowEffect, QGroupBox
)

class ModernFormField(QWidget):
    """Campo de formulario moderno con validación visual"""
    
    validation_changed = pyqtSignal(bool)  # Emite True si válido, False si inválido
    
    def __init__(self, label: str, widget: QWidget, required: bool = False, 
                 tooltip: str = "", validation_func: Optional[Callable] = None):
        super().__init__()
        self.label_text = label
        self.widget = widget
        self.required = required
        self.tooltip_text = tooltip
        self.validation_func = validation_func
        self.is_valid = True
        self.error_message = ""
        
        self.init_ui()
        self.setup_validation()
        
    def init_ui(self):
        """Inicializa la interfaz del campo"""
        layout = QVBoxLayout(self)
        layout.setSpacing(4)
        layout.setContentsMargins(0, 0, 0, 8)
        
        # Label con indicador de requerido
        label_layout = QHBoxLayout()
        label_layout.setContentsMargins(0, 0, 0, 0)
        
        self.label = QLabel(self.label_text)
        self.label.setStyleSheet("""
            QLabel {
                font-weight: 600;
                color: #2c3e50;
                font-size: 13px;
            }
        """)
        label_layout.addWidget(self.label)
        
        if self.required:
            required_label = QLabel("*")
            required_label.setStyleSheet("""
                QLabel {
                    color: #e74c3c;
                    font-weight: bold;
                    font-size: 14px;
                }
            """)
            label_layout.addWidget(required_label)
            
        label_layout.addStretch()
        
        # Status icon
        self.status_icon = QLabel()
        self.status_icon.setFixedSize(16, 16)
        self.status_icon.hide()
        label_layout.addWidget(self.status_icon)
        
        layout.addLayout(label_layout)
        
        # Widget container
        widget_container = QFrame()
        widget_container.setStyleSheet("""
            QFrame {
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                background-color: white;
                padding: 2px;
            }
            QFrame:focus-within {
                border-color: #3498db;
            }
        """)
        
        widget_layout = QHBoxLayout(widget_container)
        widget_layout.setContentsMargins(8, 4, 8, 4)
        widget_layout.addWidget(self.widget)
        
        layout.addWidget(widget_container)
        self.widget_container = widget_container
        
        # Error message label
        self.error_label = QLabel()
        self.error_label.setStyleSheet("""
            QLabel {
                color: #e74c3c;
                font-size: 11px;
                font-weight: 500;
                margin-left: 4px;
            }
        """)
        self.error_label.hide()
        layout.addWidget(self.error_label)
        
        # Tooltip
        if self.tooltip_text:
            self.widget.setToolTip(self.tooltip_text)
            
    def setup_validation(self):
        """Configura validación en tiempo real"""
        if hasattr(self.widget, 'textChanged'):
            self.widget.textChanged.connect(self.validate_realtime)
        elif hasattr(self.widget, 'valueChanged'):
            self.widget.valueChanged.connect(self.validate_realtime)
        elif hasattr(self.widget, 'currentTextChanged'):
            self.widget.currentTextChanged.connect(self.validate_realtime)
            
    def validate_realtime(self):
        """Valida el campo en tiempo real"""
        QTimer.singleShot(300, self.validate)  # Debounce 300ms
        
    def validate(self) -> bool:
        """Valida el campo y actualiza el estado visual"""
        value = self.get_value()
        
        # Validación de campo requerido
        if self.required and not value:
            self.set_error("Este campo es obligatorio")
            return False
            
        # Validación personalizada
        if self.validation_func:
            try:
                result = self.validation_func(value)
                if isinstance(result, tuple):
                    is_valid, message = result
                    if not is_valid:
                        self.set_error(message)
                        return False
                elif not result:
                    self.set_error("Valor inválido")
                    return False
            except Exception as e:
                self.set_error(f"Error de validación: {str(e)}")
                return False
                
        self.set_valid()
        return True
        
    def get_value(self):
        """Obtiene el valor del widget"""
        if hasattr(self.widget, 'text'):
            return self.widget.text().strip()
        elif hasattr(self.widget, 'value'):
            return self.widget.value()
        elif hasattr(self.widget, 'currentText'):
            return self.widget.currentText()
        elif hasattr(self.widget, 'isChecked'):
            return self.widget.isChecked()
        elif hasattr(self.widget, 'toPlainText'):
            return self.widget.toPlainText().strip()
        return None
        
    def set_error(self, message: str):
        """Establece estado de error"""
        self.is_valid = False
        self.error_message = message
        
        # Estilo de error
        self.widget_container.setStyleSheet("""
            QFrame {
                border: 2px solid #e74c3c;
                border-radius: 6px;
                background-color: #fdf2f2;
                padding: 2px;
            }
        """)
        
        # Mostrar mensaje de error
        self.error_label.setText(f"[WARN] {message}")
        self.error_label.show()
        
        # Ícono de error
        self.status_icon.setText("[ERROR]")
        self.status_icon.show()
        
        self.validation_changed.emit(False)
        
    def set_valid(self):
        """Establece estado válido"""
        self.is_valid = True
        self.error_message = ""
        
        # Estilo válido
        self.widget_container.setStyleSheet("""
            QFrame {
                border: 2px solid #27ae60;
                border-radius: 6px;
                background-color: #f8fff8;
                padding: 2px;
            }
        """)
        
        # Ocultar mensaje de error
        self.error_label.hide()
        
        # Ícono de éxito
        self.status_icon.setText("[CHECK]")
        self.status_icon.show()
        
        self.validation_changed.emit(True)
        
    def reset_validation(self):
        """Resetea el estado de validación"""
        self.is_valid = True
        self.error_message = ""
        
        # Estilo neutro
        self.widget_container.setStyleSheet("""
            QFrame {
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                background-color: white;
                padding: 2px;
            }
            QFrame:focus-within {
                border-color: #3498db;
            }
        """)
        
        self.error_label.hide()
        self.status_icon.hide()


class LoadingOverlay(QWidget):
    """Overlay de carga para formularios"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(0, 0, 0, 0.5);
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Container para el loading
        container = QFrame()
        container.setFixedSize(200, 100)
        container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #bdc3c7;
            }
        """)
        
        # Agregar sombra
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 2)
        shadow.setColor(QColor(0, 0, 0, 80))
        container.setGraphicsEffect(shadow)
        
        container_layout = QVBoxLayout(container)
        container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Progress bar
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)  # Indeterminate
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                text-align: center;
                background-color: #ecf0f1;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 3px;
            }
        """)
        
        # Label de mensaje
        self.message_label = QLabel("Procesando...")
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.message_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: 600;
                color: #2c3e50;
                margin: 8px;
            }
        """)
        
        container_layout.addWidget(self.message_label)
        container_layout.addWidget(self.progress)
        
        layout.addWidget(container)
        
    def set_message(self, message: str):
        """Actualiza el mensaje de carga"""
        self.message_label.setText(message)
        
    def showEvent(self, event):
        """Al mostrar, ajustar al tamaño del padre"""
        if self.parent():
            self.resize(self.parent().size())
        super().showEvent(event)
        
    def resizeEvent(self, event):
        """Al redimensionar, mantener centrado"""
        if self.parent():
            self.resize(self.parent().size())
        super().resizeEvent(event)


class ModernFormDialog(QDialog):
    """Dialog base para formularios modernos"""
    
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.title = title
        self.fields: Dict[str, ModernFormField] = {}
        self.loading_overlay = None
        
        self.setModal(True)
        self.setWindowTitle(title)
        self.resize(600, 700)
        self.init_ui()
        self.apply_modern_styling()
        
    def init_ui(self):
        """Inicializa la interfaz base"""
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header = self.create_header()
        layout.addWidget(header)
        
        # Form area (scroll)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        
        self.form_widget = QWidget()
        self.form_layout = QVBoxLayout(self.form_widget)
        self.form_layout.setSpacing(12)
        
        self.scroll_area.setWidget(self.form_widget)
        layout.addWidget(self.scroll_area)
        
        # Footer buttons
        footer = self.create_footer()
        layout.addWidget(footer)
        
    def create_header(self) -> QWidget:
        """Crea el header del formulario"""
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3498db, stop:1 #2980b9);
                border-radius: 8px;
                padding: 16px;
                margin-bottom: 8px;
            }
        """)
        
        layout = QHBoxLayout(header)
        
        # Título
        title_label = QLabel(self.title)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: white;
                background: transparent;
            }
        """)
        layout.addWidget(title_label)
        
        layout.addStretch()
        
        return header
        
    def create_footer(self) -> QWidget:
        """Crea el footer con botones"""
        footer = QFrame()
        footer.setStyleSheet("""
            QFrame {
                border-top: 1px solid #bdc3c7;
                padding-top: 16px;
                margin-top: 16px;
            }
        """)
        
        layout = QHBoxLayout(footer)
        layout.addStretch()
        
        # Botón cancelar
        self.cancel_btn = QPushButton("[ERROR] Cancelar")
        self.cancel_btn.clicked.connect(self.reject)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px 24px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        
        # Botón guardar
        self.save_btn = QPushButton("[CHECK] Guardar")
        self.save_btn.clicked.connect(self.validate_and_save)
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px 24px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        
        layout.addWidget(self.cancel_btn)
        layout.addWidget(self.save_btn)
        
        return footer
        
    def add_field(self, key: str, label: str, widget: QWidget, 
                  required: bool = False, tooltip: str = "", 
                  validation_func: Optional[Callable] = None) -> ModernFormField:
        """Agrega un campo al formulario"""
        field = ModernFormField(label, widget, required, tooltip, validation_func)
        field.validation_changed.connect(self.on_validation_changed)
        
        self.fields[key] = field
        self.form_layout.addWidget(field)
        
        return field
        
    def add_section(self, title: str) -> QGroupBox:
        """Agrega una sección al formulario"""
        section = QGroupBox(title)
        section.setStyleSheet("""
            QGroupBox {
                font-weight: 600;
                font-size: 14px;
                color: #2c3e50;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 16px;
                padding-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                background-color: white;
            }
        """)
        
        self.form_layout.addWidget(section)
        return section
        
    def on_validation_changed(self, is_valid: bool):
        """Maneja cambios en la validación"""
        # Habilitar/deshabilitar botón de guardar
        all_valid = all(field.is_valid for field in self.fields.values())
        self.save_btn.setEnabled(all_valid)
        
    def validate_and_save(self):
        """Valida todos los campos y guarda si es válido"""
        # Validar todos los campos
        all_valid = True
        for field in self.fields.values():
            if not field.validate():
                all_valid = False
                
        if not all_valid:
            return
            
        # Mostrar loading
        self.show_loading("Guardando...")
        
        # Simular guardado (reemplazar con lógica real)
        QTimer.singleShot(1500, self.on_save_complete)
        
    def show_loading(self, message: str = "Procesando..."):
        """Muestra overlay de carga"""
        if not self.loading_overlay:
            self.loading_overlay = LoadingOverlay(self)
            
        self.loading_overlay.set_message(message)
        self.loading_overlay.show()
        self.save_btn.setEnabled(False)
        
    def hide_loading(self):
        """Oculta overlay de carga"""
        if self.loading_overlay:
            self.loading_overlay.hide()
        self.save_btn.setEnabled(True)
        
    def on_save_complete(self):
        """Maneja finalización del guardado"""
        self.hide_loading()
        self.accept()
        
    def get_form_data(self) -> Dict[str, Any]:
        """Obtiene todos los datos del formulario"""
        data = {}
        for key, field in self.fields.items():
            data[key] = field.get_value()
        return data
        
    def apply_modern_styling(self):
        """Aplica estilos modernos al diálogo"""
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QLineEdit, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit {
                font-size: 13px;
                padding: 8px;
                border: none;
                background-color: transparent;
            }
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus, 
            QSpinBox:focus, QDoubleSpinBox:focus, QDateEdit:focus {
                outline: none;
            }
        """)


# Funciones de validación comunes
class FormValidators:
    """Validadores comunes para formularios"""
    
    @staticmethod
    def required_field(value) -> tuple[bool, str]:
        """Valida que un campo no esté vacío"""
        if not value or (isinstance(value, str) and not value.strip()):
            return False, "Este campo es obligatorio"
        return True, ""
        
    @staticmethod
    def email_format(value) -> tuple[bool, str]:
        """Valida formato de email"""
        if not value:
            return True, ""  # Campo opcional
            
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, value):
            return False, "Formato de email inválido"
        return True, ""
        
    @staticmethod
    def numeric_range(value, min_val=None, max_val=None) -> tuple[bool, str]:
        """Valida rango numérico"""
        try:
            num_value = float(value) if isinstance(value, str) else value
            
            if min_val is not None and num_value < min_val:
                return False, f"El valor debe ser mayor o igual a {min_val}"
                
            if max_val is not None and num_value > max_val:
                return False, f"El valor debe ser menor o igual a {max_val}"
                
            return True, ""
        except (ValueError, TypeError):
            return False, "Debe ser un número válido"
            
    @staticmethod
    def code_format(value) -> tuple[bool, str]:
        """Valida formato de código (ej: ABC-123)"""
        if not value:
            return False, "Código es obligatorio"
            
        import re
        pattern = r'^[A-Z]{2,4}-\d{3,6}$'
        if not re.match(pattern, value.upper()):
            return False, "Formato: ABC-123456 (letras-números)"
        return True, ""