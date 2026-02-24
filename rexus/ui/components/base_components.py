"""
Componentes base para la UI de Rexus.app
Proporciona componentes fundamentales reutilizables en toda la aplicación.
"""

from PyQt6.QtWidgets import QLabel, QWidget, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QPalette


class RexusLabel(QLabel):
    """Etiqueta estándar de Rexus con estilo consistente."""
    
    def __init__(self, text="", parent=None, bold=False, color=None):
        super().__init__(text, parent)
        self.setup_style(bold, color)
    
    def setup_style(self, bold=False, color=None):
        """Configura el estilo de la etiqueta."""
        font = QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(10)
        
        if bold:
            font.setBold(True)
        
        self.setFont(font)
        
        if color:
            self.setStyleSheet(f"color: {color};")
        else:
            self.setStyleSheet("color: #2c3e50;")


class RexusFrame(QWidget):
    """Frame estándar de Rexus con estilo consistente."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_style()
    
    def setup_style(self):
        """Configura el estilo del frame."""
        self.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
                border: 1px solid #e1e8ed;
                border-radius: 8px;
                padding: 16px;
            }
        """)


class RexusButton(QWidget):
    """Botón estándar de Rexus con estilo consistente."""
    
    clicked = pyqtSignal()
    
    def __init__(self, text="", parent=None, primary=True):
        super().__init__(parent)
        self.text = text
        self.primary = primary
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz del botón."""
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        from PyQt6.QtWidgets import QPushButton
        self.button = QPushButton(self.text)
        self.button.clicked.connect(self.clicked.emit)
        
        if self.primary:
            self.button.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 10px 20px;
                    font-weight: bold;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
                QPushButton:pressed {
                    background-color: #2471a3;
                }
            """)
        else:
            self.button.setStyleSheet("""
                QPushButton {
                    background-color: #ffffff;
                    color: #3498db;
                    border: 1px solid #3498db;
                    border-radius: 6px;
                    padding: 10px 20px;
                    font-weight: bold;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #f8f9fa;
                }
                QPushButton:pressed {
                    background-color: #e9ecef;
                }
            """)
        
        layout.addWidget(self.button)
        self.setLayout(layout)


class RexusCard(QWidget):
    """Tarjeta estándar de Rexus con estilo consistente."""
    
    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.title = title
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz de la tarjeta."""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Título
        if self.title:
            title_label = RexusLabel(self.title, bold=True)
            title_label.setStyleSheet("""
                QLabel {
                    color: #2c3e50;
                    font-size: 14px;
                    font-weight: bold;
                    padding: 0 0 10px 0;
                    border-bottom: 1px solid #e1e8ed;
                }
            """)
            layout.addWidget(title_label)
        
        # Contenido
        self.content_widget = QWidget()
        self.content_widget.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
                border-radius: 8px;
                padding: 16px;
            }
        """)
        layout.addWidget(self.content_widget)
        
        self.setLayout(layout)
    
    def add_widget(self, widget):
        """Agrega un widget al contenido de la tarjeta."""
        if self.content_widget.layout():
            self.content_widget.layout().addWidget(widget)


class RexusSeparator(QWidget):
    """Separador estándar de Rexus."""
    
    def __init__(self, orientation="horizontal", parent=None):
        super().__init__(parent)
        self.orientation = orientation
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz del separador."""
        if self.orientation == "horizontal":
            self.setFixedHeight(1)
            self.setStyleSheet("""
                QWidget {
                    background-color: #e1e8ed;
                    margin: 10px 0;
                }
            """)
        else:
            self.setFixedWidth(1)
            self.setStyleSheet("""
                QWidget {
                    background-color: #e1e8ed;
                    margin: 0 10px;
                }
            """)


class RexusStatusBar(QWidget):
    """Barra de estado estándar de Rexus."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz de la barra de estado."""
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)
        
        self.status_label = RexusLabel("Listo")
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        
        self.info_label = RexusLabel("")
        layout.addWidget(self.info_label)
        
        self.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border-top: 1px solid #e1e8ed;
            }
        """)
        
        self.setLayout(layout)
    
    def set_status(self, text):
        """Establece el texto de estado."""
        self.status_label.setText(text)
    
    def set_info(self, text):
        """Establece el texto informativo."""
        self.info_label.setText(text)