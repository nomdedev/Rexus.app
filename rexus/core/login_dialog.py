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
        self.setFixedSize(500, 900)
        self.setWindowTitle("Rexus.app")
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.CustomizeWindowHint | 
                           Qt.WindowType.WindowTitleHint | Qt.WindowType.WindowCloseButtonHint)
    
    def setup_ui(self):
        """Configura la interfaz de usuario."""
        if not PYQT_AVAILABLE:
            return
            
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(80, 60, 80, 60)
        
        # Espaciador superior para centrar contenido
        main_layout.addStretch(2)
        
        # Logo/Imagen
        self.logo_label = QLabel()
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logo_label.setMinimumHeight(120)
        self.logo_label.setMaximumHeight(120)
        self.logo_label.setStyleSheet("""
            QLabel {
                background-color: #f8f9fa;
                border: 2px dashed #dee2e6;
                border-radius: 8px;
                color: #6c757d;
                font-size: 12px;
            }
        """)
        self.logo_label.setText("LOGO\nRexus.app")
        main_layout.addWidget(self.logo_label)
        
        # Formulario
        form_frame = QFrame()
        form_layout = QVBoxLayout(form_frame)
        form_layout.setSpacing(20)
        
        # Campo usuario
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Usuario")
        self.username_edit.setMinimumHeight(45)
        form_layout.addWidget(self.username_edit)
        
        # Campo contraseña
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_edit.setPlaceholderText("Contraseña")
        self.password_edit.setMinimumHeight(45)
        form_layout.addWidget(self.password_edit)
        
        
        main_layout.addWidget(form_frame)
        
        # Barra de progreso (oculta inicialmente)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMinimumHeight(2)
        main_layout.addWidget(self.progress_bar)
        
        # Botón de login
        self.login_button = QPushButton("Ingresar")
        self.login_button.setMinimumHeight(45)
        self.login_button.setDefault(True)
        main_layout.addWidget(self.login_button)
        
        # Mensaje de estado
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #e74c3c; font-size: 10px;")
        self.status_label.setVisible(False)
        main_layout.addWidget(self.status_label)
        
        # Espaciador inferior para centrar contenido
        main_layout.addStretch(3)
    
    def setup_connections(self):
        """Configura las conexiones de señales."""
        if not PYQT_AVAILABLE:
            return
            
        self.login_button.clicked.connect(self.handle_login)
        
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
                background-color: #ffffff;
                border: none;
            }
            QLabel {
                color: #333333;
                font-size: 14px;
                font-weight: 400;
                margin-bottom: 15px;
            }
            QLineEdit {
                border: 1px solid #e1e1e1;
                border-radius: 4px;
                padding: 12px 15px;
                background-color: #ffffff;
                font-size: 14px;
                color: #333333;
            }
            QLineEdit:focus {
                border-color: #4a90e2;
                outline: none;
            }
            QPushButton {
                background-color: #4a90e2;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 14px;
                font-weight: 400;
                padding: 12px;
            }
            QPushButton:hover {
                background-color: #357abd;
            }
            QPushButton:pressed {
                background-color: #2a5d87;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
            QProgressBar {
                border: none;
                background-color: #f0f0f0;
                border-radius: 1px;
                height: 2px;
            }
            QProgressBar::chunk {
                background-color: #4a90e2;
                border-radius: 1px;
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
            # Autenticación real con base de datos
            if self.authenticate_user(username, password):
                self.show_success("Login exitoso")
                self.save_remembered_user()  # Guardar usuario recordado
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
        Autentica al usuario usando la base de datos real.
        
        Args:
            username: Nombre de usuario
            password: Contraseña
            
        Returns:
            True si la autenticación es exitosa
        """
        try:
            from ..core.database import get_users_connection
            from ..core.user_management import UserManagementSystem
            
            # Obtener conexión a la base de datos
            db = get_users_connection()
            if not db or not db.connection:
                logger.error("No se pudo conectar a la base de datos de usuarios")
                return False
            
            # Buscar usuario en la base de datos
            query = """
                SELECT id, usuario, password_hash, nombre, apellido, rol, activo
                FROM usuarios 
                WHERE usuario = ? AND activo = 1
            """
            
            result = db.execute_query(query, (username,))
            
            if not result or len(result) == 0:
                logger.warning(f"Usuario no encontrado: {username}")
                return False
                
            user_data = result[0]
            stored_password_hash = user_data[2]
            
            # Verificar contraseña
            password_hash = UserManagementSystem.hash_password(password)
            
            if password_hash == stored_password_hash:
                # Actualizar datos del usuario para la sesión
                self.user_data = {
                    'user_id': user_data[0],
                    'username': user_data[1],
                    'nombre': user_data[3],
                    'apellido': user_data[4],
                    'role': user_data[5],
                    'authenticated': True
                }
                logger.info(f"Autenticación exitosa para: {username}")
                return True
            else:
                logger.warning(f"Contraseña incorrecta para usuario: {username}")
                return False
                
        except Exception as e:
            logger.error(f"Error en autenticación con BD: {e}")
            return False
    
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
        self.status_label.setStyleSheet("color: #e74c3c; font-size: 10px;")
        self.status_label.setVisible(True)
        logger.warning(f"Login error: {message}")
    
    def show_success(self, message: str):
        """Muestra mensaje de éxito."""
        if not PYQT_AVAILABLE:
            return
            
        self.status_label.setText(message)
        self.status_label.setStyleSheet("color: #27ae60; font-size: 10px;")
        self.status_label.setVisible(True)
        logger.info(f"Login success: {message}")
    
    def show_progress(self, message: str):
        """Muestra barra de progreso."""
        if not PYQT_AVAILABLE:
            return
            
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminada
        self.status_label.setText(message)
        self.status_label.setStyleSheet("color: #4a90e2; font-size: 10px;")
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
    
    def load_logo(self):
        """Carga el logo de la aplicación si existe."""
        try:
            # Buscar logo en diferentes ubicaciones
            logo_paths = [
                "resources/images/logo.png",
                "resources/images/rexus_logo.png",
                "assets/logo.png",
                "logo.png"
            ]
            
            for logo_path in logo_paths:
                if os.path.exists(logo_path):
                    pixmap = QPixmap(logo_path)
                    if not pixmap.isNull():
                        # Escalar el logo manteniendo proporción
                        scaled_pixmap = pixmap.scaled(
                            100, 100, 
                            Qt.AspectRatioMode.KeepAspectRatio, 
                            Qt.TransformationMode.SmoothTransformation
                        )
                        self.logo_label.setPixmap(scaled_pixmap)
                        self.logo_label.setText("")  # Limpiar texto placeholder
                        self.logo_label.setStyleSheet("""
                            QLabel {
                                background-color: transparent;
                                border: none;
                            }
                        """)
                        logger.info(f"Logo cargado desde: {logo_path}")
                        return
                        
        except Exception as e:
            logger.warning(f"No se pudo cargar el logo: {e}")
            
        # Si no se encuentra logo, mantener placeholder
        logger.info("No se encontró logo, usando placeholder")
    
    def load_remembered_user(self):
        """Carga usuario recordado si existe."""
        # En producción, cargar de configuración/registro
        remembered_user = os.getenv("REXUS_REMEMBERED_USER", "")
        if remembered_user:
            self.username_edit.setText(remembered_user)
            self.password_edit.setFocus()
    
    def save_remembered_user(self):
        """Guarda usuario recordado."""
        if self.user_data:
            # En producción, guardar en configuración segura
            logger.info(f"Usuario recordado: {self.user_data.get('username')}")

    def showEvent(self, event):
        """Evento al mostrar el diálogo."""
        if PYQT_AVAILABLE:
            super().showEvent(event)
            self.load_logo()  # Cargar logo al mostrar diálogo
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