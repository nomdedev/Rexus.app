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
        self.setWindowTitle("Rexus.app - Iniciar Sesión")
        self.setFixedSize(400, 550)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowCloseButtonHint)
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                           stop:0 #4a90e2, stop:1 #7b68ee);
                border-radius: 0px;
            }
        """)

        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Frame principal
        main_frame = QFrame()
        main_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 16px;
                border: none;
            }
        """)

        frame_layout = QVBoxLayout(main_frame)
        frame_layout.setSpacing(20)
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
        header_layout.setSpacing(10)

        # Logo simple y elegante
        logo_label = QLabel("🏢")
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_label.setStyleSheet("""
            QLabel {
                font-size: 48px;
                color: #4a90e2;
                margin-bottom: 10px;
            }
        """)
        header_layout.addWidget(logo_label)

        # Título principal
        title_label = QLabel("Rexus.app")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 28px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 5px;
            }
        """)
        header_layout.addWidget(title_label)

        # Subtítulo
        subtitle_label = QLabel("Sistema de Gestión Integral")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("""
            QLabel {
                font-size: 13px;
                color: #7f8c8d;
                margin-bottom: 20px;
            }
        """)
        header_layout.addWidget(subtitle_label)

        layout.addLayout(header_layout)

    def create_form(self, layout):
        """Crea el formulario de login."""
        form_layout = QVBoxLayout()
        form_layout.setSpacing(15)

        # Campo usuario
        user_label = QLabel("👤 Usuario")
        user_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: 600;
                color: #2c3e50;
                margin-bottom: 5px;
            }
        """)
        
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Ingrese su usuario")
        self.username_edit.setStyleSheet("""
            QLineEdit {
                padding: 12px 16px;
                border: 2px solid #ddd;
                border-radius: 8px;
                font-size: 14px;
                background-color: #f8f9fa;
                color: #2c3e50;
            }
            QLineEdit:focus {
                border-color: #4a90e2;
                background-color: #ffffff;
                outline: none;
            }
            QLineEdit:hover {
                border-color: #bbb;
            }
        """)
        self.username_edit.setFixedHeight(40)
        
        form_layout.addWidget(user_label)
        form_layout.addWidget(self.username_edit)

        # Campo contraseña
        password_label = QLabel("🔒 Contraseña")
        password_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: 600;
                color: #2c3e50;
                margin-bottom: 5px;
                margin-top: 10px;
            }
        """)
        
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("Ingrese su contraseña")
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_edit.setStyleSheet("""
            QLineEdit {
                padding: 12px 16px;
                border: 2px solid #ddd;
                border-radius: 8px;
                font-size: 14px;
                background-color: #f8f9fa;
                color: #2c3e50;
            }
            QLineEdit:focus {
                border-color: #4a90e2;
                background-color: #ffffff;
                outline: none;
            }
            QLineEdit:hover {
                border-color: #bbb;
            }
        """)
        self.password_edit.setFixedHeight(40)
        
        form_layout.addWidget(password_label)
        form_layout.addWidget(self.password_edit)

        # Checkbox recordar
        self.remember_checkbox = QCheckBox("Recordar usuario")
        self.remember_checkbox.setStyleSheet("""
            QCheckBox {
                font-size: 12px;
                color: #7f8c8d;
                margin-top: 10px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
            }
            QCheckBox::indicator:unchecked {
                border: 2px solid #ddd;
                border-radius: 3px;
                background-color: #f8f9fa;
            }
            QCheckBox::indicator:checked {
                border: 2px solid #4a90e2;
                border-radius: 3px;
                background-color: #4a90e2;
            }
        """)
        
        form_layout.addWidget(self.remember_checkbox)
        layout.addLayout(form_layout)

    def create_buttons(self, layout):
        """Crea los botones de acción."""
        buttons_layout = QVBoxLayout()
        buttons_layout.setSpacing(16)
        buttons_layout.setContentsMargins(0, 20, 0, 0)

        # Botón login principal
        self.login_button = QPushButton("Iniciar Sesión")
        self.login_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                          stop:0 #667eea, stop:1 #764ba2);
                color: white;
                border: none;
                padding: 20px 40px;
                border-radius: 16px;
                font-size: 17px;
                font-weight: 600;
                min-width: 300px;
                min-height: 48px;
                letter-spacing: 0.5px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                          stop:0 #5a67d8, stop:1 #667eea);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                          stop:0 #4c51bf, stop:1 #5a67d8);
            }
            QPushButton:disabled {
                background: #e2e8f0;
                color: #a0aec0;
            }
        """)
        self.login_button.setDefault(True)

        # Botón cancelar secundario
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #718096;
                border: 2px solid #e2e8f0;
                padding: 16px 40px;
                border-radius: 16px;
                font-size: 15px;
                font-weight: 500;
                min-width: 300px;
                min-height: 44px;
            }
            QPushButton:hover {
                border-color: #cbd5e0;
                background-color: #f7fafc;
                color: #4a5568;
            }
            QPushButton:pressed {
                background-color: #edf2f7;
                border-color: #a0aec0;
            }
        """)

        buttons_layout.addWidget(self.login_button)
        buttons_layout.addWidget(self.cancel_button)

        layout.addLayout(buttons_layout)

    def create_footer(self, layout):
        """Crea el footer con información adicional."""
        footer_layout = QVBoxLayout()
        footer_layout.setSpacing(12)

        # Separador elegante
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("""
            QFrame {
                color: #e1e8ed;
                margin: 20px 0 15px 0;
                max-height: 1px;
            }
        """)
        footer_layout.addWidget(separator)

        # Información de usuario por defecto con diseño moderno
        info_label = QLabel("👤 Usuario por defecto: admin\n🔒 Contraseña: admin")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #667eea;
                background-color: rgba(102, 126, 234, 0.08);
                padding: 15px 20px;
                border-radius: 10px;
                border: 1px solid rgba(102, 126, 234, 0.15);
                font-weight: 500;
                line-height: 1.4;
            }
        """)
        footer_layout.addWidget(info_label)

        # Versión con estilo minimalista
        version_label = QLabel("v1.1.3 - 2025")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_label.setStyleSheet("""
            QLabel {
                font-size: 11px;
                color: #95a5a6;
                margin-top: 10px;
                font-weight: 400;
            }
        """)
        footer_layout.addWidget(version_label)

        layout.addLayout(footer_layout)

    def apply_styles(self):
        """Aplica estilos al diálogo."""
        pass

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
