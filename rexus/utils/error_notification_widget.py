"""
Widget de Mensajes de Error Modernos - Rexus.app
Componente visual para mostrar mensajes de error contextualizados
"""

import os
import sys
from typing import Optional

from PyQt6.QtCore import QPropertyAnimation, Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

# Importar nuestro sistema de errores
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from rexus.utils.contextual_error_manager import ErrorCode, ErrorSeverity, error_manager


class ErrorMessageWidget(QFrame):
    """Widget moderno para mostrar mensajes de error contextualizados."""

    # Señales
    dismissed = pyqtSignal()
    details_requested = pyqtSignal(dict)

    def __init__(
        self, error_code: ErrorCode, context: Optional[dict] = None, parent=None
    ):
        super().__init__(parent)
        self.error_code = error_code
        self.context = context or {}
        self.error_info = error_manager.get_error_info(error_code, context)

        self.setup_ui()
        self.setup_animations()

    def setup_ui(self):
        """Configura la interfaz del widget de error."""
        self.setFrameStyle(QFrame.Shape.Box)
        self.setLineWidth(2)

        # Layout principal
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(8)

        # Header con icono y título
        header_layout = QHBoxLayout()

        # Icono según severidad
        severity_icons = {
            ErrorSeverity.INFO: "ℹ️",
            ErrorSeverity.WARNING: "[WARN]",
            ErrorSeverity.ERROR: "[ERROR]",
            ErrorSeverity.CRITICAL: "🚨",
        }

        icon_label = QLabel(severity_icons.get(self.error_info["severity"], "[ERROR]"))
        icon_label.setFont(QFont("Segoe UI", 16))
        header_layout.addWidget(icon_label)

        # Título
        title_label = QLabel(self.error_info["title"])
        title_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        # Botón cerrar
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(20, 20)
        close_btn.setStyleSheet("""
            QPushButton {
                border: none;
                background: transparent;
                color: #6c757d;
                font-weight: bold;
            }
            QPushButton:hover {
                color: #dc3545;
                background: #f8f9fa;
                border-radius: 10px;
            }
        """)
        close_btn.clicked.connect(self.dismiss)
        header_layout.addWidget(close_btn)

        layout.addLayout(header_layout)

        # Mensaje principal
        message_label = QLabel(self.error_info["message"])
        message_label.setWordWrap(True)
        message_label.setFont(QFont("Segoe UI", 10))
        layout.addWidget(message_label)

        # Sugerencia
        suggestion_frame = QFrame()
        suggestion_frame.setStyleSheet("""
            QFrame {
                background-color: #e3f2fd;
                border: 1px solid #90caf9;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        suggestion_layout = QVBoxLayout(suggestion_frame)
        suggestion_layout.setContentsMargins(8, 8, 8, 8)

        suggestion_header = QLabel("💡 Sugerencia:")
        suggestion_header.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        suggestion_layout.addWidget(suggestion_header)

        suggestion_label = QLabel(self.error_info["suggestion"])
        suggestion_label.setWordWrap(True)
        suggestion_label.setFont(QFont("Segoe UI", 9))
        suggestion_layout.addWidget(suggestion_label)

        layout.addWidget(suggestion_frame)

        # Botones de acción
        buttons_layout = QHBoxLayout()

        # Código de error para soporte
        error_code_label = QLabel(f"Código: {self.error_info['error_code']}")
        error_code_label.setFont(QFont("Consolas", 8))
        error_code_label.setStyleSheet("color: #6c757d;")
        buttons_layout.addWidget(error_code_label)

        buttons_layout.addStretch()

        # Botón de detalles técnicos
        details_btn = QPushButton("🔧 Detalles Técnicos")
        details_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                padding: 4px 8px;
                border-radius: 3px;
                font-size: 8pt;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        details_btn.clicked.connect(self.show_technical_details)
        buttons_layout.addWidget(details_btn)

        # Botón OK
        ok_btn = QPushButton("OK")
        ok_btn.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 6px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        ok_btn.clicked.connect(self.dismiss)
        buttons_layout.addWidget(ok_btn)

        layout.addLayout(buttons_layout)

        # Aplicar estilos según severidad
        self.apply_severity_styles()

    def apply_severity_styles(self):
        """Aplica estilos según la severidad del error."""
        styles = {
            ErrorSeverity.INFO: {"border_color": "#17a2b8", "bg_color": "#d1ecf1"},
            ErrorSeverity.WARNING: {"border_color": "#ffc107", "bg_color": "#fff3cd"},
            ErrorSeverity.ERROR: {"border_color": "#dc3545", "bg_color": "#f8d7da"},
            ErrorSeverity.CRITICAL: {"border_color": "#721c24", "bg_color": "#f5c6cb"},
        }

        style = styles.get(self.error_info["severity"], styles[ErrorSeverity.ERROR])

        self.setStyleSheet(f"""
            ErrorMessageWidget {{
                background-color: {style["bg_color"]};
                border: 2px solid {style["border_color"]};
                border-radius: 8px;
            }}
        """)

    def setup_animations(self):
        """Configura animaciones para el widget."""
        self.slide_animation = QPropertyAnimation(self, b"geometry")
        self.slide_animation.setDuration(300)

        # Auto-dismiss para warnings e info después de 5 segundos
        if self.error_info["severity"] in [ErrorSeverity.INFO, ErrorSeverity.WARNING]:
            QTimer.singleShot(5000, self.dismiss)

    def dismiss(self):
        """Cierra el widget de error con animación."""
        self.dismissed.emit()
        self.hide()

    def show_technical_details(self):
        """Muestra detalles técnicos del error."""
        self.details_requested.emit(self.error_info)

        # Mostrar diálogo con detalles técnicos
        details_dialog = TechnicalDetailsDialog(self.error_info, self)
        details_dialog.show()  # Usar show() en lugar de exec()


class TechnicalDetailsDialog(QDialog):
    """Diálogo para mostrar detalles técnicos del error."""

    def __init__(self, error_info: dict, parent=None):
        super().__init__(parent)
        self.error_info = error_info
        self.setup_ui()

    def setup_ui(self):
        """Configura la interfaz del diálogo."""
        self.setWindowTitle("Detalles Técnicos del Error")
        self.setFixedSize(500, 400)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowCloseButtonHint)

        layout = QVBoxLayout(self)

        # Título
        title = QLabel("🔧 Información Técnica")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout.addWidget(title)

        # Área de texto con detalles
        details_text = QTextEdit()
        details_text.setReadOnly(True)
        details_text.setFont(QFont("Consolas", 9))

        # Formatear información técnica
        details_content = f"""
ERROR CODE: {self.error_info["error_code"]}
TIMESTAMP: {self.error_info["timestamp"]}
CATEGORY: {self.error_info["category"].value}
SEVERITY: {self.error_info["severity"].value}

TECHNICAL DETAILS:
{self.error_info["technical_details"]}

CONTEXT:
{self._format_context()}

USER MESSAGE:
{self.error_info["message"]}

SUGGESTION:
{self.error_info["suggestion"]}
        """.strip()

        details_text.setPlainText(details_content)
        layout.addWidget(details_text)

        # Botones
        buttons_layout = QHBoxLayout()

        copy_btn = QPushButton("📋 Copiar al Portapapeles")
        copy_btn.clicked.connect(lambda: self.copy_to_clipboard(details_content))
        buttons_layout.addWidget(copy_btn)

        buttons_layout.addStretch()

        close_btn = QPushButton("Cerrar")
        close_btn.clicked.connect(self.close)
        buttons_layout.addWidget(close_btn)

        layout.addLayout(buttons_layout)

        # Estilos
        self.setStyleSheet("""
            QWidget {
                background-color: white;
            }
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)

    def _format_context(self) -> str:
        """Formatea el contexto para mostrar."""
        if not self.error_info["context"]:
            return "No context available"

        lines = []
        for key, value in self.error_info["context"].items():
            lines.append(f"  {key}: {value}")
        return "\n".join(lines)

    def copy_to_clipboard(self, text: str):
        """Copia el texto al portapapeles."""
        clipboard = QApplication.clipboard()
        if clipboard:
            clipboard.setText(text)


class ErrorNotificationManager(QWidget):
    """Manager para mostrar notificaciones de error de forma no intrusiva."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.error_widgets = []
        self.setup_ui()

    def setup_ui(self):
        """Configura el contenedor de notificaciones."""
        self.setFixedWidth(400)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)

        self.error_layout = QVBoxLayout(self)
        self.error_layout.setContentsMargins(10, 10, 10, 10)
        self.error_layout.setSpacing(5)
        self.error_layout.addStretch()

        # Posicionar en esquina superior derecha
        if self.parent():
            parent_widget = self.parent()
            try:
                parent_rect = parent_widget.geometry()
                self.move(parent_rect.width() - 420, 10)
            except Exception:
                self.move(100, 10)  # Posición por defecto

    def show_error(self, error_code: ErrorCode, context: Optional[dict] = None):
        """Muestra un nuevo error en la cola de notificaciones."""
        error_widget = ErrorMessageWidget(error_code, context, self)
        error_widget.dismissed.connect(lambda: self.remove_error_widget(error_widget))

        # Insertar al principio de la lista (arriba)
        self.error_layout.insertWidget(0, error_widget)
        self.error_widgets.append(error_widget)

        # Limitar número de errores visibles
        if len(self.error_widgets) > 3:
            oldest = self.error_widgets.pop(0)
            oldest.dismiss()

        # Ajustar tamaño
        self.adjustSize()

    def remove_error_widget(self, widget: ErrorMessageWidget):
        """Remueve un widget de error de la cola."""
        if widget in self.error_widgets:
            self.error_widgets.remove(widget)
            widget.deleteLater()
            self.adjustSize()


# Funciones de conveniencia para mostrar errores
def show_error_notification(
    parent_widget: QWidget, error_code: ErrorCode, context: Optional[dict] = None
):
    """Función rápida para mostrar notificación de error."""
    if not hasattr(parent_widget, "_error_manager"):
        setattr(
            parent_widget, "_error_manager", ErrorNotificationManager(parent_widget)
        )

    error_manager = getattr(parent_widget, "_error_manager")
    error_manager.show_error(error_code, context)
    error_manager.show()
    error_manager.raise_()


if __name__ == "__main__":
    # Prueba del sistema de errores
    app = QApplication(sys.argv)

    # Crear ventana de prueba
    window = QWidget()
    window.setWindowTitle("Prueba de Sistema de Errores")
    window.resize(800, 600)

    layout = QVBoxLayout(window)

    # Botones para probar diferentes tipos de errores
    btn_db_error = QPushButton("🔴 Error de BD")
    btn_db_error.clicked.connect(
        lambda: show_error_notification(window, ErrorCode.DB_CONNECTION_FAILED)
    )
    layout.addWidget(btn_db_error)

    btn_validation_error = QPushButton("[WARN] Error de Validación")
    btn_validation_error.clicked.connect(
        lambda: show_error_notification(
            window, ErrorCode.VAL_REQUIRED_FIELD, {"field_name": "Nombre de Usuario"}
        )
    )
    layout.addWidget(btn_validation_error)

    btn_auth_error = QPushButton("[LOCK] Error de Autenticación")
    btn_auth_error.clicked.connect(
        lambda: show_error_notification(window, ErrorCode.AUTH_INVALID_CREDENTIALS)
    )
    layout.addWidget(btn_auth_error)

    window.show()
    sys.exit(app.exec())
