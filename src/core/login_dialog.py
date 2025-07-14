"""
Diálogo de Login - Stock.App v1.1.3

Sistema de autenticación con interfaz moderna
"""

import os
import sys

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon, QPixmap
from PyQt6.QtWidgets import (
    QCheckBox,
    QDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from src.core.security import get_security_manager


class LoginDialog(QDialog):
    """Diálogo de login con diseño moderno."""

    # Señales
    login_successful = pyqtSignal(str, str)  # username, role
    login_failed = pyqtSignal(str)  # error_message

    def __init__(self, parent=None):
        super().__init__(parent)
        self.security_manager = get_security_manager()
        self.init_ui()

    def init_ui(self):
        """Inicializa la interfaz de usuario."""
        self.setWindowTitle("Stock.App v1.1.3 - Iniciar Sesión")
        self.setFixedSize(400, 500)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowCloseButtonHint)

        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)

        # Frame principal
        main_frame = QFrame()
        main_frame.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-radius: 15px;
                border: 2px solid #3498db;
            }
        """)

        frame_layout = QVBoxLayout(main_frame)
        frame_layout.setSpacing(25)
        frame_layout.setContentsMargins(30, 30, 30, 30)

        # Logo y título
        self.create_header(frame_layout)

        # Formulario de login
        self.create_form(frame_layout)

        # Botones
        self.create_buttons(frame_layout)

        # Información adicional
        self.create_footer(frame_layout)

        main_layout.addWidget(main_frame)

        # Aplicar estilos
        self.apply_styles()

        # Conectar eventos
        self.connect_events()

    def create_header(self, layout):
        """Crea el header con logo y título."""
        header_layout = QVBoxLayout()

        # Logo (placeholder)
        logo_label = QLabel("🏢")
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_label.setStyleSheet("""
            QLabel {
                font-size: 48px;
                color: #3498db;
                margin-bottom: 10px;
            }
        """)
        header_layout.addWidget(logo_label)

        # Título
        title_label = QLabel("Stock.App v1.1.3")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 5px;
            }
        """)
        header_layout.addWidget(title_label)

        # Subtítulo
        subtitle_label = QLabel("Sistema de Gestión de Inventario")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #7f8c8d;
                margin-bottom: 20px;
            }
        """)
        header_layout.addWidget(subtitle_label)

        layout.addLayout(header_layout)

    def create_form(self, layout):
        """Crea el formulario de login."""
        form_layout = QFormLayout()
        form_layout.setSpacing(15)

        # Campo usuario
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Ingrese su usuario")
        self.username_edit.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                font-size: 14px;
                background-color: #ecf0f1;
            }
            QLineEdit:focus {
                border-color: #3498db;
                background-color: #ffffff;
            }
        """)

        user_label = QLabel("👤 Usuario:")
        user_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #2c3e50;
            }
        """)

        form_layout.addRow(user_label, self.username_edit)

        # Campo contraseña
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("Ingrese su contraseña")
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_edit.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                font-size: 14px;
                background-color: #ecf0f1;
            }
            QLineEdit:focus {
                border-color: #3498db;
                background-color: #ffffff;
            }
        """)

        password_label = QLabel("🔒 Contraseña:")
        password_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #2c3e50;
            }
        """)

        form_layout.addRow(password_label, self.password_edit)

        # Checkbox recordar
        self.remember_checkbox = QCheckBox("Recordar usuario")
        self.remember_checkbox.setStyleSheet("""
            QCheckBox {
                font-size: 12px;
                color: #7f8c8d;
                margin-top: 10px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            QCheckBox::indicator:unchecked {
                border: 2px solid #bdc3c7;
                border-radius: 3px;
                background-color: #ecf0f1;
            }
            QCheckBox::indicator:checked {
                border: 2px solid #3498db;
                border-radius: 3px;
                background-color: #3498db;
            }
        """)

        form_layout.addRow("", self.remember_checkbox)

        layout.addLayout(form_layout)

    def create_buttons(self, layout):
        """Crea los botones de acción."""
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)

        # Botón cancelar
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
            QPushButton:pressed {
                background-color: #6c7b7d;
            }
        """)

        # Botón login
        self.login_button = QPushButton("Iniciar Sesión")
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        self.login_button.setDefault(True)

        buttons_layout.addWidget(self.cancel_button)
        buttons_layout.addWidget(self.login_button)

        layout.addLayout(buttons_layout)

    def create_footer(self, layout):
        """Crea el footer con información adicional."""
        footer_layout = QVBoxLayout()
        footer_layout.setSpacing(5)

        # Separador
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("""
            QFrame {
                color: #bdc3c7;
                margin: 10px 0;
            }
        """)
        footer_layout.addWidget(separator)

        # Información de usuario por defecto
        info_label = QLabel("👤 Usuario por defecto: admin\n🔒 Contraseña: admin123")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setStyleSheet("""
            QLabel {
                font-size: 11px;
                color: #7f8c8d;
                background-color: #f8f9fa;
                padding: 10px;
                border-radius: 5px;
                border: 1px solid #e9ecef;
            }
        """)
        footer_layout.addWidget(info_label)

        # Versión
        version_label = QLabel("v1.1.3 - 2025")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_label.setStyleSheet("""
            QLabel {
                font-size: 10px;
                color: #95a5a6;
                margin-top: 5px;
            }
        """)
        footer_layout.addWidget(version_label)

        layout.addLayout(footer_layout)

    def apply_styles(self):
        """Aplica estilos al diálogo."""
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
            }
        """)

    def connect_events(self):
        """Conecta los eventos."""
        self.login_button.clicked.connect(self.handle_login)
        self.cancel_button.clicked.connect(self.reject)
        self.username_edit.returnPressed.connect(self.handle_login)
        self.password_edit.returnPressed.connect(self.handle_login)

    def handle_login(self):
        """Maneja el proceso de login."""
        username = self.username_edit.text().strip()
        password = self.password_edit.text()

        # Validar campos
        if not username:
            self.show_error("Por favor ingrese su usuario")
            self.username_edit.setFocus()
            return

        if not password:
            self.show_error("Por favor ingrese su contraseña")
            self.password_edit.setFocus()
            return

        # Deshabilitar botón durante el proceso
        self.login_button.setEnabled(False)
        self.login_button.setText("Autenticando...")

        # Intentar login
        try:
            if self.security_manager and self.security_manager.login(
                username, password
            ):
                # Login exitoso
                role = self.security_manager.get_current_role()
                self.login_successful.emit(username, role)
                self.accept()
            else:
                # Login fallido
                error_msg = "Usuario o contraseña incorrectos"
                self.show_error(error_msg)
                self.login_failed.emit(error_msg)
                self.password_edit.clear()
                self.password_edit.setFocus()

        except Exception as e:
            error_msg = f"Error de autenticación: {str(e)}"
            self.show_error(error_msg)
            self.login_failed.emit(error_msg)

        finally:
            # Rehabilitar botón
            self.login_button.setEnabled(True)
            self.login_button.setText("Iniciar Sesión")

    def show_error(self, message):
        """Muestra un mensaje de error."""
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setWindowTitle("Error de Autenticación")
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #ffffff;
            }
            QMessageBox QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 80px;
            }
            QMessageBox QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        msg_box.exec()

    def keyPressEvent(self, event):
        """Maneja eventos de teclado."""
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
        else:
            super().keyPressEvent(event)
