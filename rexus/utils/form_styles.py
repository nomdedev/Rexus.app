"""
Sistema de Estilos Unificado para Formularios - Rexus.app v2.0.0

Proporciona estilos consistentes y feedback visual para todos los formularios
de la aplicación, incluyendo estados de validación y efectos visuales.
"""

from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QWidget


class FormStyleManager:
    """Gestor de estilos para formularios con diseño moderno y consistente."""
    
    # Paleta de colores principal
    COLORS = {
        'primary': '#3498db',
        'primary_dark': '#2980b9',
        'primary_light': '#5dade2',
        'success': '#27ae60',
        'success_dark': '#229954',
        'success_light': '#58d68d',
        'error': '#e74c3c',
        'error_dark': '#c0392b',
        'error_light': '#ec7063',
        'warning': '#f39c12',
        'warning_dark': '#e67e22',
        'warning_light': '#f8c471',
        'info': '#17a2b8',
        'light': '#f8f9fa',
        'dark': '#2c3e50',
        'secondary': '#6c757d',
        'background': '#ffffff',
        'border': '#dee2e6',
        'border_focus': '#80bdff',
        'text': '#495057',
        'text_muted': '#6c757d',
        'shadow': 'rgba(0, 0, 0, 0.15)'
    }
    
    @staticmethod
    def get_dialog_style() -> str:
        """Estilo base para diálogos."""
        return f"""
            QDialog {{
                background-color: {FormStyleManager.COLORS['background']};
                border-radius: 12px;
                color: {FormStyleManager.COLORS['text']};
                font-family: 'Segoe UI', 'Arial', sans-serif;
                font-size: 14px;
            }}
            
            QDialog::title {{
                background-color: {FormStyleManager.COLORS['primary']};
                color: white;
                padding: 15px;
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
                font-weight: bold;
                font-size: 16px;
            }}
        """
    
    @staticmethod
    def get_form_input_style() -> str:
        """Estilo para campos de entrada (QLineEdit, QTextEdit, etc.)."""
        return f"""
            QLineEdit, QTextEdit, QPlainTextEdit {{
                border: 2px solid {FormStyleManager.COLORS['border']};
                border-radius: 8px;
                padding: 12px 16px;
                font-size: 14px;
                color: {FormStyleManager.COLORS['text']};
                background-color: {FormStyleManager.COLORS['background']};
                selection-background-color: {FormStyleManager.COLORS['primary_light']};
                transition: all 0.3s ease;
            }}
            
            QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
                border-color: {FormStyleManager.COLORS['border_focus']};
                background-color: #ffffff;
                box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.25);
            }}
            
            QLineEdit:hover, QTextEdit:hover, QPlainTextEdit:hover {{
                border-color: {FormStyleManager.COLORS['primary_light']};
            }}
            
            QLineEdit[state="valid"] {{
                border-color: {FormStyleManager.COLORS['success']};
                background-color: #f8fff9;
            }}
            
            QLineEdit[state="invalid"] {{
                border-color: {FormStyleManager.COLORS['error']};
                background-color: #fff8f8;
            }}
            
            QLineEdit[state="warning"] {{
                border-color: {FormStyleManager.COLORS['warning']};
                background-color: #fffdf8;
            }}
            
            QTextEdit {{
                min-height: 80px;
                max-height: 120px;
            }}
        """
    
    @staticmethod
    def get_combo_style() -> str:
        """Estilo para QComboBox."""
        return f"""
            QComboBox {{
                border: 2px solid {FormStyleManager.COLORS['border']};
                border-radius: 8px;
                padding: 12px 16px;
                font-size: 14px;
                color: {FormStyleManager.COLORS['text']};
                background-color: {FormStyleManager.COLORS['background']};
                min-width: 120px;
            }}
            
            QComboBox:focus {{
                border-color: {FormStyleManager.COLORS['border_focus']};
                box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.25);
            }}
            
            QComboBox:hover {{
                border-color: {FormStyleManager.COLORS['primary_light']};
            }}
            
            QComboBox::drop-down {{
                border: none;
                width: 30px;
            }}
            
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 7px solid {FormStyleManager.COLORS['text_muted']};
                margin-right: 5px;
            }}
            
            QComboBox QAbstractItemView {{
                border: 2px solid {FormStyleManager.COLORS['border']};
                border-radius: 8px;
                background-color: {FormStyleManager.COLORS['background']};
                selection-background-color: {FormStyleManager.COLORS['primary_light']};
                padding: 4px;
            }}
        """
    
    @staticmethod
    def get_spinbox_style() -> str:
        """Estilo para QSpinBox y QDoubleSpinBox."""
        return f"""
            QSpinBox, QDoubleSpinBox {{
                border: 2px solid {FormStyleManager.COLORS['border']};
                border-radius: 8px;
                padding: 12px 16px;
                font-size: 14px;
                color: {FormStyleManager.COLORS['text']};
                background-color: {FormStyleManager.COLORS['background']};
                min-width: 100px;
            }}
            
            QSpinBox:focus, QDoubleSpinBox:focus {{
                border-color: {FormStyleManager.COLORS['border_focus']};
                box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.25);
            }}
            
            QSpinBox:hover, QDoubleSpinBox:hover {{
                border-color: {FormStyleManager.COLORS['primary_light']};
            }}
            
            QSpinBox::up-button, QDoubleSpinBox::up-button {{
                border: none;
                width: 20px;
                margin-right: 2px;
            }}
            
            QSpinBox::down-button, QDoubleSpinBox::down-button {{
                border: none;
                width: 20px;
                margin-right: 2px;
            }}
        """
    
    @staticmethod
    def get_button_style() -> str:
        """Estilo para botones con diferentes variantes."""
        return f"""
            QPushButton {{
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: 600;
                text-align: center;
                cursor: pointer;
                transition: all 0.3s ease;
                min-width: 100px;
            }}
            
            /* Botón primario */
            QPushButton[buttonType="primary"] {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {FormStyleManager.COLORS['primary']}, 
                    stop:1 {FormStyleManager.COLORS['primary_dark']});
                color: white;
            }}
            
            QPushButton[buttonType="primary"]:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {FormStyleManager.COLORS['primary_light']}, 
                    stop:1 {FormStyleManager.COLORS['primary']});
                transform: translateY(-2px);
                box-shadow: 0 4px 12px {FormStyleManager.COLORS['shadow']};
            }}
            
            QPushButton[buttonType="primary"]:pressed {{
                background: {FormStyleManager.COLORS['primary_dark']};
                transform: translateY(0px);
            }}
            
            /* Botón de éxito */
            QPushButton[buttonType="success"] {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {FormStyleManager.COLORS['success']}, 
                    stop:1 {FormStyleManager.COLORS['success_dark']});
                color: white;
            }}
            
            QPushButton[buttonType="success"]:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {FormStyleManager.COLORS['success_light']}, 
                    stop:1 {FormStyleManager.COLORS['success']});
                transform: translateY(-2px);
                box-shadow: 0 4px 12px {FormStyleManager.COLORS['shadow']};
            }}
            
            /* Botón de error/cancelar */
            QPushButton[buttonType="danger"] {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {FormStyleManager.COLORS['error']}, 
                    stop:1 {FormStyleManager.COLORS['error_dark']});
                color: white;
            }}
            
            QPushButton[buttonType="danger"]:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {FormStyleManager.COLORS['error_light']}, 
                    stop:1 {FormStyleManager.COLORS['error']});
                transform: translateY(-2px);
                box-shadow: 0 4px 12px {FormStyleManager.COLORS['shadow']};
            }}
            
            /* Botón secundario */
            QPushButton[buttonType="secondary"], QPushButton {{
                background-color: {FormStyleManager.COLORS['light']};
                color: {FormStyleManager.COLORS['text']};
                border: 2px solid {FormStyleManager.COLORS['border']};
            }}
            
            QPushButton[buttonType="secondary"]:hover, QPushButton:hover {{
                background-color: {FormStyleManager.COLORS['border']};
                border-color: {FormStyleManager.COLORS['secondary']};
                transform: translateY(-1px);
            }}
            
            QPushButton:disabled {{
                background-color: {FormStyleManager.COLORS['border']};
                color: {FormStyleManager.COLORS['text_muted']};
                cursor: not-allowed;
            }}
        """
    
    @staticmethod
    def get_label_style() -> str:
        """Estilo para etiquetas y labels."""
        return f"""
            QLabel {{
                color: {FormStyleManager.COLORS['text']};
                font-size: 14px;
                font-weight: 500;
                margin-bottom: 6px;
            }}
            
            QLabel[labelType="title"] {{
                font-size: 24px;
                font-weight: bold;
                color: {FormStyleManager.COLORS['dark']};
                margin-bottom: 20px;
            }}
            
            QLabel[labelType="subtitle"] {{
                font-size: 18px;
                font-weight: 600;
                color: {FormStyleManager.COLORS['dark']};
                margin-bottom: 15px;
            }}
            
            QLabel[labelType="error"] {{
                color: {FormStyleManager.COLORS['error']};
                font-size: 12px;
                font-weight: 500;
                margin-top: 4px;
            }}
            
            QLabel[labelType="success"] {{
                color: {FormStyleManager.COLORS['success']};
                font-size: 12px;
                font-weight: 500;
                margin-top: 4px;
            }}
            
            QLabel[labelType="warning"] {{
                color: {FormStyleManager.COLORS['warning']};
                font-size: 12px;
                font-weight: 500;
                margin-top: 4px;
            }}
            
            QLabel[labelType="muted"] {{
                color: {FormStyleManager.COLORS['text_muted']};
                font-size: 12px;
                font-style: italic;
            }}
        """
    
    @staticmethod
    def get_group_style() -> str:
        """Estilo para QGroupBox."""
        return f"""
            QGroupBox {{
                font-weight: bold;
                font-size: 16px;
                color: {FormStyleManager.COLORS['dark']};
                border: 2px solid {FormStyleManager.COLORS['border']};
                border-radius: 12px;
                margin-top: 20px;
                padding-top: 15px;
                background-color: {FormStyleManager.COLORS['background']};
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 15px;
                padding: 5px 10px;
                background-color: {FormStyleManager.COLORS['primary']};
                color: white;
                border-radius: 6px;
                font-weight: 600;
            }}
        """
    
    @staticmethod
    def get_complete_form_style() -> str:
        """Estilo completo combinando todos los componentes."""
        return (
            FormStyleManager.get_dialog_style() +
            FormStyleManager.get_form_input_style() +
            FormStyleManager.get_combo_style() +
            FormStyleManager.get_spinbox_style() +
            FormStyleManager.get_button_style() +
            FormStyleManager.get_label_style() +
            FormStyleManager.get_group_style()
        )
    
    @staticmethod
    def apply_validation_state(widget: QWidget, state: str, message: str = ""):
        """
        Aplica estado de validación visual a un widget.
        
        Args:
            widget: Widget al que aplicar el estado
            state: 'valid', 'invalid', 'warning', o 'neutral'
            message: Mensaje opcional para mostrar
        """
        # Establecer propiedad CSS para el estado
        widget.setProperty("state", state)
        
        # Refrescar el estilo
        widget.style().polish(widget)
        
        # Si hay un mensaje, buscar o crear label de feedback
        if message and hasattr(widget.parent(), 'layout'):
            feedback_label_name = f"{widget.objectName()}_feedback"
            
            # Buscar label existente
            feedback_label = widget.parent().findChild(QWidget, feedback_label_name)
            
            if not feedback_label:
                from PyQt6.QtWidgets import QLabel
                feedback_label = QLabel()
                feedback_label.setObjectName(feedback_label_name)
                
                # Añadir al layout si es posible
                layout = widget.parent().layout()
                if layout:
                    # Encontrar la posición del widget y añadir el label después
                    for i in range(layout.count()):
                        if layout.itemAt(i).widget() == widget:
                            layout.insertWidget(i + 1, feedback_label)
                            break
            
            # Configurar el mensaje y estilo
            feedback_label.setText(message)
            if state == 'invalid':
                feedback_label.setProperty("labelType", "error")
            elif state == 'valid':
                feedback_label.setProperty("labelType", "success")
            elif state == 'warning':
                feedback_label.setProperty("labelType", "warning")
            else:
                feedback_label.setProperty("labelType", "muted")
            
            feedback_label.style().polish(feedback_label)
            feedback_label.setVisible(bool(message))


class FormAnimations:
    """Clase para manejar animaciones suaves en formularios."""
    
    @staticmethod
    def fade_in(widget: QWidget, duration: int = 300):
        """Animación de fade in."""
        widget.setStyleSheet("QWidget { background-color: rgba(255, 255, 255, 0); }")
        
        animation = QPropertyAnimation(widget, b"windowOpacity")
        animation.setDuration(duration)
        animation.setStartValue(0.0)
        animation.setEndValue(1.0)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        animation.start()
        
        return animation
    
    @staticmethod
    def shake_widget(widget: QWidget, duration: int = 500):
        """Animación de shake para errores."""
        from PyQt6.QtCore import QRect
        
        original_geometry = widget.geometry()
        
        animation = QPropertyAnimation(widget, b"geometry")
        animation.setDuration(duration)
        animation.setLoopCount(3)
        
        # Crear keyframes para el shake
        animation.setKeyValueAt(0.0, original_geometry)
        animation.setKeyValueAt(0.1, QRect(original_geometry.x() + 10, original_geometry.y(), 
                                          original_geometry.width(), original_geometry.height()))
        animation.setKeyValueAt(0.2, QRect(original_geometry.x() - 10, original_geometry.y(), 
                                          original_geometry.width(), original_geometry.height()))
        animation.setKeyValueAt(0.3, original_geometry)
        
        animation.setEasingCurve(QEasingCurve.Type.OutElastic)
        animation.start()
        
        return animation


def setup_form_widget(widget: QWidget, apply_animations: bool = True) -> None:
    """
    Configura un widget de formulario con estilos y comportamientos estándar.
    
    Args:
        widget: Widget a configurar
        apply_animations: Si aplicar animaciones o no
    """
    # Aplicar estilos
    widget.setStyleSheet(FormStyleManager.get_complete_form_style())
    
    # Configurar propiedades de botones
    from PyQt6.QtWidgets import QPushButton
    for button in widget.findChildren(QPushButton):
        button_text = button.text().lower()
        
        if any(word in button_text for word in ['guardar', 'crear', 'agregar', 'añadir']):
            button.setProperty("buttonType", "success")
        elif any(word in button_text for word in ['eliminar', 'borrar', 'cancelar']):
            button.setProperty("buttonType", "danger")
        elif any(word in button_text for word in ['aceptar', 'ok', 'confirmar']):
            button.setProperty("buttonType", "primary")
        else:
            button.setProperty("buttonType", "secondary")
    
    # Aplicar animación de entrada si está habilitada
    if apply_animations:
        FormAnimations.fade_in(widget)