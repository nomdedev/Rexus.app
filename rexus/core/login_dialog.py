"""
MIT License

Copyright (c) 2024 Rexus.app

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

"""
Diálogo de Login - Rexus.app v2.0.0

Sistema de autenticación con interfaz minimalista y profesional
"""

import logging
import os
import sys
from typing import Optional, Dict, Any

# Sistema de logging
try:
    from ..utils.app_logger import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

try:
    from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                                 QLineEdit, QPushButton, QFrame, QMessageBox,
                                 QCheckBox, QProgressBar, QSizePolicy)
    from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QThread, pyqtSlot
    from PyQt6.QtGui import QFont, QIcon, QPixmap, QPalette, QColor
    PYQT_AVAILABLE = True
except ImportError:
    logger.warning("PyQt6 no disponible - usando fallback")
    PYQT_AVAILABLE = False
    
    # Fallback classes
    class QDialog:
        def __init__(self, *args, **kwargs): pass
    class pyqtSignal: 
        def __init__(self, *args): pass
        def emit(self, *args): pass


class LoginDialog(QDialog):
    """Diálogo de login moderno y seguro."""
    
    # Señales
    login_successful = pyqtSignal(dict) if PYQT_AVAILABLE else None
    login_failed = pyqtSignal(str) if PYQT_AVAILABLE else None
    
    def __init__(self, parent=None):
        """Inicializa el diálogo de login."""
        super().__init__(parent) if PYQT_AVAILABLE else None
        
        if not PYQT_AVAILABLE:
            return
            
        self.user_data = None
        self.failed_attempts = 0
        self.max_attempts = 5
        
        self.setup_ui()
        self.setup_connections()
        self.setup_styling()
        
        # Configuraciones de ventana
        self.setModal(True)
        self.setFixedSize(400, 300)
        self.setWindowTitle("Rexus.app - Iniciar Sesión")
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.CustomizeWindowHint | 
                           Qt.WindowType.WindowTitleHint | Qt.WindowType.WindowCloseButtonHint)
    
    def setup_ui(self):
        """Configura la interfaz de usuario."""
        if not PYQT_AVAILABLE:
            return
            
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(40, 40, 40, 40)
        
        # Título
        title_label = QLabel("Iniciar Sesión")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        main_layout.addWidget(title_label)
        
        # Subtítulo
        subtitle_label = QLabel("Acceso al Sistema Rexus")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("color: #666; font-size: 12px;")
        main_layout.addWidget(subtitle_label)
        
        # Formulario
        form_frame = QFrame()
        form_layout = QVBoxLayout(form_frame)
        form_layout.setSpacing(15)
        
        # Campo usuario
        self.username_label = QLabel("Usuario:")
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Ingrese su nombre de usuario")
        self.username_edit.setMinimumHeight(35)
        
        form_layout.addWidget(self.username_label)
        form_layout.addWidget(self.username_edit)
        
        # Campo contraseña
        self.password_label = QLabel("Contraseña:")
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_edit.setPlaceholderText("Ingrese su contraseña")
        self.password_edit.setMinimumHeight(35)
        
        form_layout.addWidget(self.password_label)
        form_layout.addWidget(self.password_edit)
        
        # Checkbox recordar
        self.remember_checkbox = QCheckBox("Recordar usuario")
        form_layout.addWidget(self.remember_checkbox)
        
        main_layout.addWidget(form_frame)
        
        # Barra de progreso (oculta inicialmente)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMinimumHeight(5)
        main_layout.addWidget(self.progress_bar)
        
        # Botones
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.setMinimumHeight(40)
        
        self.login_button = QPushButton("Iniciar Sesión")
        self.login_button.setMinimumHeight(40)
        self.login_button.setDefault(True)
        
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.login_button)
        
        main_layout.addLayout(button_layout)
        
        # Mensaje de estado
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #d32f2f; font-size: 11px;")
        self.status_label.setVisible(False)
        main_layout.addWidget(self.status_label)
    
    def setup_connections(self):
        """Configura las conexiones de señales."""
        if not PYQT_AVAILABLE:
            return
            
        self.login_button.clicked.connect(self.handle_login)
        self.cancel_button.clicked.connect(self.reject)
        
        # Enter en los campos
        self.username_edit.returnPressed.connect(self.password_edit.setFocus)
        self.password_edit.returnPressed.connect(self.handle_login)
        
        # Limpiar estado al escribir
        self.username_edit.textChanged.connect(self.clear_status)
        self.password_edit.textChanged.connect(self.clear_status)
    
    def setup_styling(self):
        """Configura el estilo visual."""
        if not PYQT_AVAILABLE:
            return
            
        # Estilo general del diálogo
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
                border-radius: 8px;
            }
            QLabel {
                color: #333;
            }
            QLineEdit {
                border: 2px solid #ddd;
                border-radius: 4px;
                padding: 8px;
                background-color: white;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #2196F3;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
            QPushButton:disabled {
                background-color: #ccc;
            }
            QCheckBox {
                color: #666;
                font-size: 12px;
            }
            QProgressBar {
                border: none;
                background-color: #e0e0e0;
                border-radius: 2px;
            }
            QProgressBar::chunk {
                background-color: #2196F3;
                border-radius: 2px;
            }
        """)
        
        # Estilo específico para botón cancelar
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #757575;
                color: white;
            }
            QPushButton:hover {
                background-color: #616161;
            }
            QPushButton:pressed {
                background-color: #424242;
            }
        """)
    
    def handle_login(self):
        """Maneja el intento de login."""
        if not PYQT_AVAILABLE:
            return
            
        username = self.username_edit.text().strip()
        password = self.password_edit.text().strip()
        
        # Validaciones básicas
        if not username:
            self.show_error("Ingrese su nombre de usuario")
            self.username_edit.setFocus()
            return
        
        if not password:
            self.show_error("Ingrese su contraseña")
            self.password_edit.setFocus()
            return
        
        # Verificar intentos fallidos
        if self.failed_attempts >= self.max_attempts:
            self.show_error(f"Demasiados intentos fallidos. Reinicie la aplicación.")
            return
        
        # Deshabilitar botón y mostrar progreso
        self.login_button.setEnabled(False)
        self.show_progress("Autenticando...")
        
        try:
            # Simular autenticación (en producción usar auth_manager real)
            if self.authenticate_user(username, password):
                self.user_data = {
                    'username': username,
                    'user_id': 1,
                    'role': 'admin',
                    'authenticated': True
                }
                
                self.show_success("Login exitoso")
                QTimer.singleShot(500, self.accept_login)
                
            else:
                self.failed_attempts += 1
                remaining = self.max_attempts - self.failed_attempts
                
                if remaining > 0:
                    error_msg = f"Credenciales incorrectas. {remaining} intentos restantes."
                else:
                    error_msg = "Credenciales incorrectas. Contacte al administrador."
                
                self.show_error(error_msg)
                if self.login_failed:
                    self.login_failed.emit(error_msg)
                self.password_edit.clear()
                self.password_edit.setFocus()

        except Exception as e:
            error_msg = f"Error de autenticación: {str(e)}"
            self.show_error(error_msg)
            if self.login_failed:
                self.login_failed.emit(error_msg)

        finally:
            # Rehabilitar botón
            self.login_button.setEnabled(True)
            self.hide_progress()
    
    def authenticate_user(self, username: str, password: str) -> bool:
        """
        Autentica al usuario (mock para desarrollo).
        
        Args:
            username: Nombre de usuario
            password: Contraseña
            
        Returns:
            True si la autenticación es exitosa
        """
        # Mock de autenticación para desarrollo
        valid_credentials = {
            'admin': 'admin123',
            'user': 'user123',
            'manager': 'manager123'
        }
        
        return username in valid_credentials and valid_credentials[username] == password
    
    def accept_login(self):
        """Acepta el login y emite señal."""
        if self.login_successful and self.user_data:
            self.login_successful.emit(self.user_data)
        self.accept()
    
    def show_error(self, message: str):
        """Muestra mensaje de error."""
        if not PYQT_AVAILABLE:
            return
            
        self.status_label.setText(message)
        self.status_label.setStyleSheet("color: #d32f2f; font-size: 11px;")
        self.status_label.setVisible(True)
        logger.warning(f"Login error: {message}")
    
    def show_success(self, message: str):
        """Muestra mensaje de éxito."""
        if not PYQT_AVAILABLE:
            return
            
        self.status_label.setText(message)
        self.status_label.setStyleSheet("color: #388e3c; font-size: 11px;")
        self.status_label.setVisible(True)
        logger.info(f"Login success: {message}")
    
    def show_progress(self, message: str):
        """Muestra barra de progreso."""
        if not PYQT_AVAILABLE:
            return
            
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminada
        self.status_label.setText(message)
        self.status_label.setStyleSheet("color: #1976D2; font-size: 11px;")
        self.status_label.setVisible(True)
    
    def hide_progress(self):
        """Oculta barra de progreso."""
        if not PYQT_AVAILABLE:
            return
            
        self.progress_bar.setVisible(False)
    
    def clear_status(self):
        """Limpia mensaje de estado."""
        if not PYQT_AVAILABLE:
            return
            
        self.status_label.setVisible(False)
        self.hide_progress()
    
    def get_user_data(self) -> Optional[Dict[str, Any]]:
        """Obtiene datos del usuario autenticado."""
        return self.user_data
    
    def reset_failed_attempts(self):
        """Reinicia contador de intentos fallidos."""
        self.failed_attempts = 0
    
    def load_remembered_user(self):
        """Carga usuario recordado si existe."""
        # En producción, cargar de configuración/registro
        remembered_user = os.getenv("REXUS_REMEMBERED_USER", "")
        if remembered_user:
            self.username_edit.setText(remembered_user)
            self.remember_checkbox.setChecked(True)
            self.password_edit.setFocus()
    
    def save_remembered_user(self):
        """Guarda usuario si está marcado recordar."""
        if self.remember_checkbox.isChecked() and self.user_data:
            # En producción, guardar en configuración segura
            logger.info(f"Usuario recordado: {self.user_data.get('username')}")

    def showEvent(self, event):
        """Evento al mostrar el diálogo."""
        if PYQT_AVAILABLE:
            super().showEvent(event)
            self.load_remembered_user()
            if not self.username_edit.text():
                self.username_edit.setFocus()
            else:
                self.password_edit.setFocus()
    
    def keyPressEvent(self, event):
        """Manejo de eventos de teclado."""
        if not PYQT_AVAILABLE:
            return
            
        # Escape para cancelar
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
        else:
            super().keyPressEvent(event)


def show_login_dialog(parent=None) -> Optional[Dict[str, Any]]:
    """
    Muestra diálogo de login y retorna datos del usuario.
    
    Args:
        parent: Widget padre
        
    Returns:
        Datos del usuario si login exitoso, None si cancelado
    """
    if not PYQT_AVAILABLE:
        logger.error("PyQt6 no disponible - no se puede mostrar diálogo")
        return None
    
    dialog = LoginDialog(parent)
    result = dialog.exec()
    
    if result == QDialog.DialogCode.Accepted:
        return dialog.get_user_data()
    
    return None


# Función de conveniencia para testing
def test_login_dialog():
    """Test básico del diálogo de login."""
    try:
        if PYQT_AVAILABLE:
            from PyQt6.QtWidgets import QApplication
            app = QApplication([])
            
            user_data = show_login_dialog()
            if user_data:
                logger.info(f"Login exitoso: {user_data}")
            else:
                logger.info("Login cancelado")
            
            return user_data
        else:
            logger.error("PyQt6 no disponible para testing")
            return None
            
    except Exception as e:
        logger.error(f"Error en test de login: {e}")
        return None