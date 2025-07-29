"""
Diálogo de Login - Rexus.app v2.0.0

Sistema de autenticación con interfaz minimalista y profesional
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

from rexus.core.auth import get_auth_manager


class LoginDialog(QDialog):
    """Diálogo de login minimalista y profesional."""

    # Señales
    login_successful = pyqtSignal(dict)  # Emitir dict completo del usuario
    login_failed = pyqtSignal(str)  # error_message

    def __init__(self, parent=None):
        super().__init__(parent)
        self.auth_manager = get_auth_manager()
        self.init_ui()

    def init_ui(self):
        """Inicializa la interfaz de usuario minimalista."""
        self.setWindowTitle("Rexus.app - Acceso")
        self.setFixedSize(500, 850)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowCloseButtonHint)

        # Estilo general minimalista
        self.setStyleSheet("""
            QDialog {
                background-color: #fafafa;
                border: 1px solid #e0e0e0;
            }
        """)

        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Contenedor principal
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: white;
                border: none;
            }
        """)

        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(40)
        container_layout.setContentsMargins(80, 120, 80, 120)

        # Header minimalista
        self.create_header(container_layout)

        # Formulario
        self.create_form(container_layout)

        # Botones
        self.create_buttons(container_layout)

        # Info credentials (más discreta)
        self.create_info(container_layout)

        main_layout.addWidget(container)

        # Conectar eventos
        self.connect_events()

    def create_header(self, layout):
        """Crea el header minimalista."""
        header_layout = QVBoxLayout()
        header_layout.setSpacing(8)
        header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Título principal
        title = QLabel("Rexus.app")
        title.setStyleSheet("""
            QLabel {
                font-size: 28px;
                font-weight: 300;
                color: #1a1a1a;
                letter-spacing: 1px;
            }
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Subtítulo
        subtitle = QLabel("Sistema de Gestión")
        subtitle.setStyleSheet("""
            QLabel {
                font-size: 13px;
                color: #666;
                font-weight: 400;
            }
        """)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        layout.addLayout(header_layout)

    def create_form(self, layout):
        """Crea el formulario minimalista."""
        form_layout = QVBoxLayout()
        form_layout.setSpacing(25)

        # Usuario
        user_container = QVBoxLayout()
        user_container.setSpacing(6)

        user_label = QLabel("Usuario")
        user_label.setStyleSheet("""
            QLabel {
                font-size: 11px;
                color: #555;
                font-weight: 500;
                letter-spacing: 0.5px;
            }
        """)

        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Ingrese su usuario")
        self.username_edit.setStyleSheet("""
            QLineEdit {
                padding: 12px 16px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 14px;
                background-color: #fafafa;
                color: #333;
            }
            QLineEdit:focus {
                border-color: #2196F3;
                background-color: white;
                outline: none;
            }
        """)
        self.username_edit.setFixedHeight(48)

        user_container.addWidget(user_label)
        user_container.addWidget(self.username_edit)
        form_layout.addLayout(user_container)

        # Contraseña
        pass_container = QVBoxLayout()
        pass_container.setSpacing(6)

        pass_label = QLabel("Contraseña")
        pass_label.setStyleSheet("""
            QLabel {
                font-size: 11px;
                color: #555;
                font-weight: 500;
                letter-spacing: 0.5px;
            }
        """)

        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("Ingrese su contraseña")
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_edit.setStyleSheet("""
            QLineEdit {
                padding: 12px 16px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 14px;
                background-color: #fafafa;
                color: #333;
            }
            QLineEdit:focus {
                border-color: #2196F3;
                background-color: white;
                outline: none;
            }
        """)
        self.password_edit.setFixedHeight(48)

        pass_container.addWidget(pass_label)
        pass_container.addWidget(self.password_edit)
        form_layout.addLayout(pass_container)

        layout.addLayout(form_layout)

    def create_buttons(self, layout):
        """Crea los botones minimalistas."""
        buttons_layout = QVBoxLayout()
        buttons_layout.setSpacing(12)
        buttons_layout.setContentsMargins(0, 20, 0, 0)

        # Botón principal
        self.login_button = QPushButton("Iniciar Sesión")
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 14px;
                border-radius: 4px;
                font-size: 14px;
                font-weight: 500;
                letter-spacing: 0.5px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
            QPushButton:disabled {
                background-color: #ccc;
                color: #999;
            }
        """)
        self.login_button.setFixedHeight(52)
        self.login_button.setDefault(True)

        # Botón secundario
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #666;
                border: 1px solid #ddd;
                padding: 12px;
                border-radius: 4px;
                font-size: 13px;
                font-weight: 400;
            }
            QPushButton:hover {
                background-color: #f5f5f5;
                border-color: #bbb;
            }
            QPushButton:pressed {
                background-color: #eeeeee;
            }
        """)
        self.cancel_button.setFixedHeight(46)

        buttons_layout.addWidget(self.login_button)
        buttons_layout.addWidget(self.cancel_button)
        layout.addLayout(buttons_layout)

    def create_info(self, layout):
        """Crea la información de credenciales de forma discreta."""
        info_layout = QVBoxLayout()
        info_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_layout.setContentsMargins(0, 20, 0, 0)

        # Línea separadora
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("""
            QFrame {
                color: #e0e0e0;
                max-height: 1px;
                border: none;
                background-color: #e0e0e0;
            }
        """)

        # Info discreta
        info_label = QLabel("Usuario de prueba: admin / admin")
        info_label.setStyleSheet("""
            QLabel {
                font-size: 11px;
                color: #999;
                text-align: center;
            }
        """)
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Versión
        version_label = QLabel("v2.0.0")
        version_label.setStyleSheet("""
            QLabel {
                font-size: 10px;
                color: #bbb;
                text-align: center;
            }
        """)
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        info_layout.addWidget(separator)
        info_layout.addSpacing(12)
        info_layout.addWidget(info_label)
        info_layout.addSpacing(4)
        info_layout.addWidget(version_label)

        layout.addLayout(info_layout)

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
        self.login_button.setText("Verificando...")

        # Intentar login
        try:
            user = self.auth_manager.authenticate_user(username, password)
            if user:
                # Login exitoso
                self.login_successful.emit(user)  # Emitir dict completo del usuario
                self.accept()
            else:
                # Login fallido
                error_msg = "Credenciales incorrectas"
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
        """Muestra un mensaje de error minimalista."""
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setWindowTitle("Error")
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: white;
                border: 1px solid #ddd;
            }
            QMessageBox QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 4px;
                font-weight: 500;
                min-width: 80px;
            }
            QMessageBox QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        msg_box.exec()

    def keyPressEvent(self, event):
        """Maneja eventos de teclado."""
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
        else:
            super().keyPressEvent(event)
