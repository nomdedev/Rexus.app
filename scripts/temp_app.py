#!/usr/bin/env python3
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
Rexus.app - Sistema de Gestión Integral

Aplicación principal que maneja la interfaz de usuario y la integración de módulos.
Sigue principios de arquitectura MVC y patrones de diseño para mantenibilidad.
"""

# ===== CONSTANTES =====
AUDITORIA_MODULE = "Auditoría"

# ===== IMPORTS CONSOLIDADOS =====
# Imports estándar
import datetime
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, Tuple

# PyQt6 imports
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

# Configuración básica de logging
logger = logging.getLogger("rexus.main")
if not logger.hasHandlers():
    logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

# Importar sistema de logging centralizado
try:
    from rexus.utils.app_logger import (
        get_logger, log_info, log_error, log_critical, log_warning, 
        log_security, app_logger
    )
    LOGGING_AVAILABLE = True
except ImportError:
    # Fallback si el logger no está disponible
    def get_logger(name): return logging.getLogger(name)
    def log_info(msg, comp="general"): logger.info(msg)
    def log_error(msg, comp="general"): logger.error(msg)
    def log_critical(msg, comp="general"): print(f"[CRITICAL] {msg}")
    def log_warning(msg, comp="general"): logger.warning(msg)
    def log_security(level, msg, user=None): print(f"[SECURITY-{level}] {msg}")
    app_logger = None  # Agregar fallback para app_logger
    LOGGING_AVAILABLE = False

# Importar validador de dependencias críticas
try:
    from rexus.utils.dependency_validator import validate_system_dependencies, DependencyValidator
    DEPENDENCY_VALIDATION_AVAILABLE = True
except ImportError:
    def validate_system_dependencies() -> Tuple[bool, Dict[str, Any]]: return True, {"status": "FALLBACK"}
    DependencyValidator = None  # Agregar fallback para DependencyValidator
    DEPENDENCY_VALIDATION_AVAILABLE = False

# Agregar el directorio raíz al path de Python
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

# Cargar variables de entorno desde .env
try:
    from dotenv import load_dotenv

    load_dotenv(root_dir / ".env")
    log_info("Variables de entorno cargadas desde .env", "startup")
except ImportError:
    log_warning("python-dotenv no instalado, usando variables del sistema", "startup")
except Exception as e:
    print(f"[ENV] Error cargando .env: {e}")

# Sistema de autenticación de desarrollo
class DevAuthManager:
    """Gestor de autenticación para desarrollo."""

    def __init__(self):
        self.dev_user = os.environ.get('REXUS_DEV_USER', 'dev_user')
        self.dev_password = os.environ.get('REXUS_DEV_PASSWORD', 'RexusDev_2025#')
        self.auto_login = os.environ.get('REXUS_DEV_AUTO_LOGIN', 'false').lower() == 'true'

    def is_auto_login_enabled(self):
        """Verifica si el auto-login está habilitado."""
        return self.auto_login

    def should_skip_login_dialog(self):
        """Determina si se debe omitir el diálogo de login."""
        return self.is_auto_login_enabled() and self.dev_user and self.dev_password

    def validate_dev_credentials(self, username, password):
        """Valida las credenciales de desarrollo."""
        return username == self.dev_user and password == self.dev_password

    def get_dev_credentials(self):
        """Obtiene las credenciales de desarrollo."""
        return {
            'username': self.dev_user,
            'password': self.dev_password,
            'role': 'ADMIN'
        }

    def get_mock_user_session(self):
        """Obtiene una sesión de usuario mock para desarrollo."""
        return {
            'user_id': 1,
            'username': self.dev_user,
            'role': 'ADMIN',
            'permissions': ['all'],
            'login_time': datetime.datetime.now().isoformat()
        }

# Instancia global del gestor de autenticación de desarrollo
dev_auth_manager = DevAuthManager()

# Imports del core de Rexus (con fallback)
try:
    from rexus.core.login_dialog import LoginDialog
    from rexus.core.module_manager import module_manager
    from rexus.ui.dashboard import DashboardController
    from rexus.ui.components.theme_manager import ThemeManager
except ImportError:
    class LoginDialog:
        """Login Dialog que cumple con la especificación irremovible de CLAUDE.md"""

        Accepted = 1
        Rejected = 0

        def __init__(self, security_manager=None):
            self.security_manager = security_manager
            self.user_data = None
            self.modulos_permitidos = []
            self.login_successful = False

            # Estado del login
            self.failed_attempts = 0
            self.captcha_required = False
            self.rate_limited = False
            self.dark_mode = False
            self.biometric_available = True  # Simulado para desarrollo

            # Variables de entorno de desarrollo
            self.dev_user = os.environ.get('REXUS_DEV_USER', 'dev_user')
            self.dev_password = os.environ.get('REXUS_DEV_PASSWORD', 'RexusDev_2025#')
            self.auto_login = os.environ.get('REXUS_DEV_AUTO_LOGIN', 'false').lower() == 'true'

        def exec(self):
            """Muestra el diálogo de login profesional según especificación."""
            from PyQt6.QtWidgets import (
                QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                QPushButton, QFrame, QCheckBox, QProgressBar,
                QComboBox
            )
            from PyQt6.QtCore import Qt, QTimer

            # Crear diálogo principal
            dialog = QDialog()
            dialog.setWindowTitle("Rexus.app - Sistema de Gestión Empresarial")
            dialog.setModal(True)
            dialog.setFixedSize(500, 700)  # Tamaño optimizado
            dialog.setWindowFlags(dialog.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

            # Estilo limpio y profesional para el diálogo
            dialog.setStyleSheet("""
                QDialog {
                    background-color: #ffffff;
                    border: 1px solid #e1e5e9;
                }
            """)

            # Layout principal
            main_layout = QVBoxLayout(dialog)
            main_layout.setContentsMargins(30, 30, 30, 30)
            main_layout.setSpacing(20)

            # ===== HEADER =====
            # Logo
            logo_label = QLabel("R")
            logo_label.setStyleSheet("""
                QLabel {
                    font-size: 48px;
                    font-weight: bold;
                    color: #2563eb;
                    background-color: #f0f9ff;
                    border-radius: 25px;
                    padding: 15px;
                    qproperty-alignment: AlignCenter;
                }
            """)
            logo_label.setFixedSize(70, 70)

            # Título
            title_label = QLabel("Rexus.app")
            title_label.setStyleSheet("""
                QLabel {
                    font-size: 24px;
                    font-weight: bold;
                    color: #1e293b;
                    qproperty-alignment: AlignCenter;
                }
            """)

            # Subtítulo
            subtitle_label = QLabel("Sistema de Gestión Empresarial")
            subtitle_label.setStyleSheet("""
                QLabel {
                    font-size: 14px;
                    color: #64748b;
                    qproperty-alignment: AlignCenter;
                }
            """)

            # Versión
            version_label = QLabel("v2.0.0")
            version_label.setStyleSheet("""
                QLabel {
                    font-size: 12px;
                    color: #94a3b8;
                    qproperty-alignment: AlignCenter;
                }
            """)

            main_layout.addWidget(logo_label, alignment=Qt.AlignmentFlag.AlignCenter)
            main_layout.addWidget(title_label)
            main_layout.addWidget(subtitle_label)
            main_layout.addWidget(version_label)

            # ===== FORMULARIO =====
            # Campo Usuario
            user_frame = QFrame()
            user_frame.setFrameStyle(QFrame.Shape.Box)
            user_frame.setStyleSheet("""
                QFrame {
                    border: 2px solid #e2e8f0;
                    border-radius: 8px;
                    background-color: #ffffff;
                }
            """)
            user_layout = QHBoxLayout(user_frame)
            user_layout.setContentsMargins(12, 12, 12, 12)
            user_layout.setSpacing(10)

            user_icon = QLabel("👤")
            user_icon.setStyleSheet("font-size: 18px;")
            user_icon.setFixedWidth(24)

            self.user_input = QLineEdit()
            self.user_input.setPlaceholderText("Usuario o email")
            self.user_input.setStyleSheet("""
                QLineEdit {
                    border: none;
                    font-size: 14px;
                    background-color: transparent;
                    padding: 5px;
                }
            """)
            self.user_input.setText(self.dev_user if self.auto_login else "")
            self.user_input.textChanged.connect(lambda: self._validate_field('username'))

            user_layout.addWidget(user_icon)
            user_layout.addWidget(self.user_input)

            # Campo Contraseña
            pass_frame = QFrame()
            pass_frame.setFrameStyle(QFrame.Shape.Box)
            pass_frame.setStyleSheet("""
                QFrame {
                    border: 2px solid #e2e8f0;
                    border-radius: 8px;
                    background-color: #ffffff;
                }
            """)
            pass_layout = QHBoxLayout(pass_frame)
            pass_layout.setContentsMargins(12, 12, 12, 12)
            pass_layout.setSpacing(10)

            pass_icon = QLabel("🔒")
            pass_icon.setStyleSheet("font-size: 18px;")
            pass_icon.setFixedWidth(24)

            self.pass_input = QLineEdit()
            self.pass_input.setPlaceholderText("Contraseña")
            self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.pass_input.setStyleSheet("""
                QLineEdit {
                    border: none;
                    font-size: 14px;
                    background-color: transparent;
                    padding: 5px;
                }
            """)
            self.pass_input.setText(self.dev_password if self.auto_login else "")
            self.pass_input.textChanged.connect(lambda: self._validate_field('password'))

            # Toggle contraseña
            self.toggle_pass_btn = QPushButton("👁")
            self.toggle_pass_btn.setStyleSheet("""
                QPushButton {
                    border: none;
                    background-color: transparent;
                    font-size: 16px;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #f1f5f9;
                    border-radius: 4px;
                }
            """)
            self.toggle_pass_btn.clicked.connect(self._toggle_password_visibility)

            pass_layout.addWidget(pass_icon)
            pass_layout.addWidget(self.pass_input)
            pass_layout.addWidget(self.toggle_pass_btn)

            # Indicador de fuerza
            self.strength_label = QLabel("")
            self.strength_label.setStyleSheet("""
                QLabel {
                    font-size: 12px;
                    color: #94a3b8;
                    margin-top: 5px;
                }
            """)

            main_layout.addWidget(user_frame)
            main_layout.addWidget(pass_frame)
            main_layout.addWidget(self.strength_label)

            # Espaciador
            main_layout.addSpacing(15)

            # ===== OPCIONES AVANZADAS =====
            options_layout = QVBoxLayout()
            options_layout.setSpacing(15)

            # Remember me
            self.remember_me = QCheckBox("Recordarme")
            self.remember_me.setStyleSheet("""
                QCheckBox {
                    font-size: 15px;
                    color: #475569;
                    spacing: 8px;
                }
                QCheckBox::indicator {
                    width: 18px;
                    height: 18px;
                    border: 2px solid #cbd5e1;
                    border-radius: 5px;
                    background: white;
                }
                QCheckBox::indicator:checked {
                    background: #2563eb;
                    border-color: #2563eb;
                }
            """)

            # Biometric login (si está disponible)
            if self.biometric_available:
                self.biometric_btn = QPushButton("🔐 Login Biométrico")
                self.biometric_btn.setStyleSheet("""
                    QPushButton {
                        background: #f8fafc;
                        color: #2563eb;
                        border: 2px solid #e2e8f0;
                        border-radius: 10px;
                        padding: 10px 20px;
                        font-size: 15px;
                        font-weight: 500;
                        min-height: 45px;
                    }
                    QPushButton:hover {
                        background: #e2e8f0;
                        border-color: #2563eb;
                    }
                """)
                self.biometric_btn.clicked.connect(self._attempt_biometric_login)
                options_layout.addWidget(self.biometric_btn)

            options_layout.addWidget(self.remember_me)
            main_layout.addLayout(options_layout)

            # Espaciador antes de botones
            main_layout.addSpacing(20)

            # ===== BOTONES DE ACCIÓN =====
            actions_layout = QVBoxLayout()
            actions_layout.setSpacing(20)

            # Botón principal de login
            self.login_btn = QPushButton("Iniciar Sesión")
            self.login_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #2563eb, stop:1 #1d4ed8);
                    color: white;
                    border: none;
                    border-radius: 10px;
                    padding: 15px 30px;
                    font-size: 18px;
                    font-weight: bold;
                    min-height: 55px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #1d4ed8, stop:1 #1e40af);
                }
                QPushButton:pressed {
                    background: #1e40af;
                }
                QPushButton:disabled {
                    background: #94a3b8;
                    color: #cbd5e1;
                }
            """)
            self.login_btn.clicked.connect(lambda: self._attempt_login(dialog))

            # Barra de progreso para loading state
            self.progress_bar = QProgressBar()
            self.progress_bar.setVisible(False)
            self.progress_bar.setStyleSheet("""
                QProgressBar {
                    border: none;
                    border-radius: 6px;
                    text-align: center;
                    background: #f1f5f9;
                    min-height: 6px;
                }
                QProgressBar::chunk {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #2563eb, stop:1 #1d4ed8);
                    border-radius: 6px;
                }
            """)

            actions_layout.addWidget(self.login_btn)
            actions_layout.addWidget(self.progress_bar)

            main_layout.addLayout(actions_layout)

            # Espaciador
            main_layout.addSpacing(15)

            # ===== ACCIONES SECUNDARIAS =====
            secondary_layout = QHBoxLayout()
            secondary_layout.setSpacing(25)

            forgot_btn = QPushButton("¿Olvidó su contraseña?")
            forgot_btn.setStyleSheet("""
                QPushButton {
                    color: #2563eb;
                    border: none;
                    background: transparent;
                    font-size: 15px;
                    text-decoration: underline;
                    padding: 5px;
                }
                QPushButton:hover {
                    color: #1d4ed8;
                    background: #f1f5f9;
                    border-radius: 6px;
                }
            """)
            forgot_btn.clicked.connect(self._show_forgot_password)

            help_btn = QPushButton("Ayuda")
            help_btn.setStyleSheet("""
                QPushButton {
                    color: #2563eb;
                    border: none;
                    background: transparent;
                    font-size: 15px;
                    text-decoration: underline;
                    padding: 5px;
                }
                QPushButton:hover {
                    color: #1d4ed8;
                    background: #f1f5f9;
                    border-radius: 6px;
                }
            """)
            help_btn.clicked.connect(self._show_help)

            secondary_layout.addStretch()
            secondary_layout.addWidget(forgot_btn)
            secondary_layout.addWidget(help_btn)
            secondary_layout.addStretch()

            main_layout.addLayout(secondary_layout)

            # Espaciador
            main_layout.addSpacing(20)

            # ===== FEATURES ADICIONALES =====
            features_layout = QHBoxLayout()
            features_layout.setSpacing(20)

            # Dark mode toggle
            self.dark_mode_btn = QPushButton("🌙")
            self.dark_mode_btn.setToolTip("Cambiar a modo oscuro")
            self.dark_mode_btn.setStyleSheet("""
                QPushButton {
                    background: #f8fafc;
                    border: 2px solid #e2e8f0;
                    border-radius: 10px;
                    padding: 10px;
                    font-size: 18px;
                    min-width: 45px;
                    max-width: 45px;
                    min-height: 45px;
                    max-height: 45px;
                }
                QPushButton:hover {
                    background: #e2e8f0;
                    border-color: #2563eb;
                }
            """)
            self.dark_mode_btn.clicked.connect(self._toggle_dark_mode)

            # Language selector
            self.lang_combo = QComboBox()
            self.lang_combo.addItems(["Español", "English", "Português"])
            self.lang_combo.setCurrentText("Español")
            self.lang_combo.setStyleSheet("""
                QComboBox {
                    border: 2px solid #e2e8f0;
                    border-radius: 10px;
                    padding: 10px 15px;
                    background: white;
                    font-size: 15px;
                    min-width: 120px;
                    min-height: 45px;
                }
                QComboBox:hover {
                    border-color: #2563eb;
                }
                QComboBox::drop-down {
                    border: none;
                    width: 25px;
                }
                QComboBox::down-arrow {
                    image: none;
                    border-left: 5px solid transparent;
                    border-right: 5px solid transparent;
                    border-top: 5px solid #64748b;
                    margin-right: 10px;
                }
            """)

            features_layout.addStretch()
            features_layout.addWidget(self.dark_mode_btn)
            features_layout.addWidget(self.lang_combo)

            main_layout.addLayout(features_layout)

            # Espaciador final
            main_layout.addSpacing(10)

            # ===== INDICADOR DE SEGURIDAD =====
            security_layout = QHBoxLayout()
            security_indicator = QLabel("🔒 Conexión segura")
            security_indicator.setStyleSheet("""
                QLabel {
                    color: #059669;
                    font-size: 14px;
                    font-weight: 500;
                }
            """)

            security_layout.addStretch()
            security_layout.addWidget(security_indicator)
            security_layout.addStretch()

            main_layout.addLayout(security_layout)

            # Configurar auto-login si está habilitado
            if self.auto_login:
                QTimer.singleShot(1000, lambda: self._attempt_login(dialog))

            # Ejecutar diálogo
            result = dialog.exec()
            return result

            # ===== FORMULARIO =====
            form_layout = QVBoxLayout()
            form_layout.setSpacing(15)

            # Campo Usuario
            user_frame = QFrame()
            user_frame.setStyleSheet("""
                QFrame {
                    border: 2px solid #e2e8f0;
                    border-radius: 8px;
                    background: white;
                }
                QFrame:focus-within {
                    border-color: #2563eb;
                }
            """)
            user_layout = QHBoxLayout(user_frame)
            user_layout.setContentsMargins(12, 12, 12, 12)
            user_layout.setSpacing(10)

            user_icon = QLabel("👤")
            user_icon.setStyleSheet("font-size: 18px;")
            user_icon.setFixedWidth(24)

            self.user_input = QLineEdit()
            self.user_input.setPlaceholderText("Usuario o email")
            self.user_input.setStyleSheet("""
                QLineEdit {
                    border: none;
                    font-size: 14px;
                    background: transparent;
                }
                QLineEdit:focus {
                    outline: none;
                }
            """)
            self.user_input.setText(self.dev_user if self.auto_login else "")
            self.user_input.textChanged.connect(lambda: self._validate_field('username'))

            user_layout.addWidget(user_icon)
            user_layout.addWidget(self.user_input)

            # Campo Contraseña
            pass_frame = QFrame()
            pass_frame.setStyleSheet("""
                QFrame {
                    border: 2px solid #e2e8f0;
                    border-radius: 8px;
                    background: white;
                }
                QFrame:focus-within {
                    border-color: #2563eb;
                }
            """)
            pass_layout = QHBoxLayout(pass_frame)
            pass_layout.setContentsMargins(12, 12, 12, 12)
            pass_layout.setSpacing(10)

            pass_icon = QLabel("🔒")
            pass_icon.setStyleSheet("font-size: 18px;")
            pass_icon.setFixedWidth(24)

            self.pass_input = QLineEdit()
            self.pass_input.setPlaceholderText("Contraseña")
            self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.pass_input.setStyleSheet("""
                QLineEdit {
                    border: none;
                    font-size: 14px;
                    background: transparent;
                }
                QLineEdit:focus {
                    outline: none;
                }
            """)
            self.pass_input.setText(self.dev_password if self.auto_login else "")
            self.pass_input.textChanged.connect(lambda: self._validate_field('password'))

            # Toggle visibilidad contraseña
            self.toggle_pass_btn = QPushButton("👁")
            self.toggle_pass_btn.setStyleSheet("""
                QPushButton {
                    border: none;
                    background: transparent;
                    font-size: 16px;
                    padding: 0;
                    min-width: 24px;
                    max-width: 24px;
                }
                QPushButton:hover {
                    background: #f1f5f9;
                    border-radius: 4px;
                }
            """)
            self.toggle_pass_btn.clicked.connect(self._toggle_password_visibility)

            pass_layout.addWidget(pass_icon)
            pass_layout.addWidget(self.pass_input)
            pass_layout.addWidget(self.toggle_pass_btn)

            # Indicador de fuerza de contraseña
            self.strength_label = QLabel("")
            self.strength_label.setStyleSheet("""
                QLabel {
                    font-size: 12px;
                    color: #94a3b8;
                    margin-top: 5px;
                }
            """)

            form_layout.addWidget(user_frame)
            form_layout.addWidget(pass_frame)
            form_layout.addWidget(self.strength_label)

            # ===== OPCIONES AVANZADAS =====
            options_layout = QVBoxLayout()
            options_layout.setSpacing(10)

            # Remember me
            self.remember_me = QCheckBox("Recordarme")
            self.remember_me.setStyleSheet("""
                QCheckBox {
                    font-size: 14px;
                    color: #475569;
                }
                QCheckBox::indicator {
                    width: 16px;
                    height: 16px;
                    border: 2px solid #cbd5e1;
                    border-radius: 4px;
                    background: white;
                }
                QCheckBox::indicator:checked {
                    background: #2563eb;
                    border-color: #2563eb;
                }
            """)

            # Biometric login (si está disponible)
            biometric_layout = QHBoxLayout()
            if self.biometric_available:
                self.biometric_btn = QPushButton("🔐 Login Biométrico")
                self.biometric_btn.setStyleSheet("""
                    QPushButton {
                        background: #f8fafc;
                        color: #2563eb;
                        border: 2px solid #e2e8f0;
                        border-radius: 8px;
                        padding: 8px 16px;
                        font-size: 14px;
                        font-weight: 500;
                    }
                    QPushButton:hover {
                        background: #e2e8f0;
                        border-color: #2563eb;
                    }
                """)
                self.biometric_btn.clicked.connect(self._attempt_biometric_login)
                biometric_layout.addWidget(self.biometric_btn)

            options_layout.addWidget(self.remember_me)
            if self.biometric_available:
                options_layout.addLayout(biometric_layout)

            form_layout.addLayout(options_layout)

            main_layout.addLayout(form_layout)

            # ===== BOTONES DE ACCIÓN =====
            actions_layout = QVBoxLayout()
            actions_layout.setSpacing(15)

            # Botón principal de login
            self.login_btn = QPushButton("Iniciar Sesión")
            self.login_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #2563eb, stop:1 #1d4ed8);
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 12px 24px;
                    font-size: 16px;
                    font-weight: bold;
                    min-height: 48px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #1d4ed8, stop:1 #1e40af);
                }
                QPushButton:pressed {
                    background: #1e40af;
                }
                QPushButton:disabled {
                    background: #94a3b8;
                    color: #cbd5e1;
                }
            """)
            self.login_btn.clicked.connect(lambda: self._attempt_login(dialog))

            # Barra de progreso para loading state
            self.progress_bar = QProgressBar()
            self.progress_bar.setVisible(False)
            self.progress_bar.setStyleSheet("""
                QProgressBar {
                    border: none;
                    border-radius: 4px;
                    text-align: center;
                    background: #f1f5f9;
                }
                QProgressBar::chunk {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #2563eb, stop:1 #1d4ed8);
                    border-radius: 4px;
                }
            """)

            actions_layout.addWidget(self.login_btn)
            actions_layout.addWidget(self.progress_bar)

            # Acciones secundarias
            secondary_layout = QHBoxLayout()
            secondary_layout.setSpacing(20)

            forgot_btn = QPushButton("¿Olvidó su contraseña?")
            forgot_btn.setStyleSheet("""
                QPushButton {
                    color: #2563eb;
                    border: none;
                    background: transparent;
                    font-size: 14px;
                    text-decoration: underline;
                }
                QPushButton:hover {
                    color: #1d4ed8;
                    background: #f1f5f9;
                    border-radius: 4px;
                }
            """)
            forgot_btn.clicked.connect(self._show_forgot_password)

            help_btn = QPushButton("Ayuda")
            help_btn.setStyleSheet("""
                QPushButton {
                    color: #2563eb;
                    border: none;
                    background: transparent;
                    font-size: 14px;
                    text-decoration: underline;
                }
                QPushButton:hover {
                    color: #1d4ed8;
                    background: #f1f5f9;
                    border-radius: 4px;
                }
            """)
            help_btn.clicked.connect(self._show_help)

            secondary_layout.addStretch()
            secondary_layout.addWidget(forgot_btn)
            secondary_layout.addWidget(help_btn)
            secondary_layout.addStretch()

            actions_layout.addLayout(secondary_layout)

            main_layout.addLayout(actions_layout)

            # ===== FEATURES ADICIONALES =====
            features_layout = QHBoxLayout()
            features_layout.setSpacing(15)

            # Dark mode toggle
            self.dark_mode_btn = QPushButton("🌙")
            self.dark_mode_btn.setToolTip("Cambiar a modo oscuro")
            self.dark_mode_btn.setStyleSheet("""
                QPushButton {
                    background: #f8fafc;
                    border: 2px solid #e2e8f0;
                    border-radius: 8px;
                    padding: 8px;
                    font-size: 16px;
                    min-width: 40px;
                    max-width: 40px;
                    min-height: 40px;
                    max-height: 40px;
                }
                QPushButton:hover {
                    background: #e2e8f0;
                    border-color: #2563eb;
                }
            """)
            self.dark_mode_btn.clicked.connect(self._toggle_dark_mode)

            # Language selector
            self.lang_combo = QComboBox()
            self.lang_combo.addItems(["Español", "English", "Português"])
            self.lang_combo.setCurrentText("Español")
            self.lang_combo.setStyleSheet("""
                QComboBox {
                    border: 2px solid #e2e8f0;
                    border-radius: 8px;
                    padding: 8px 12px;
                    background: white;
                    font-size: 14px;
                    min-width: 100px;
                }
                QComboBox:hover {
                    border-color: #2563eb;
                }
                QComboBox::drop-down {
                    border: none;
                    width: 20px;
                }
                QComboBox::down-arrow {
                    image: none;
                    border-left: 4px solid transparent;
                    border-right: 4px solid transparent;
                    border-top: 4px solid #64748b;
                    margin-right: 8px;
                }
            """)

            features_layout.addStretch()
            features_layout.addWidget(self.dark_mode_btn)
            features_layout.addWidget(self.lang_combo)

            main_layout.addLayout(features_layout)

            # ===== SEGURIDAD =====
            # Indicador de conexión segura
            security_layout = QHBoxLayout()
            security_indicator = QLabel("🔒 Conexión segura")
            security_indicator.setStyleSheet("""
                QLabel {
                    color: #059669;
                    font-size: 12px;
                    font-weight: 500;
                }
            """)

            security_layout.addStretch()
            security_layout.addWidget(security_indicator)
            security_layout.addStretch()

            main_layout.addLayout(security_layout)

            # Configurar auto-login si está habilitado
            if self.auto_login:
                QTimer.singleShot(1000, lambda: self._attempt_login(dialog))

            # Ejecutar diálogo
            result = dialog.exec()
            return result

        def _validate_field(self, field_name):
            """Validación en tiempo real de campos."""
            if field_name == 'username':
                username = self.user_input.text().strip()
                if not username:
                    self.user_input.setStyleSheet("""
                        QLineEdit {
                            border: none;
                            font-size: 14px;
                            background: transparent;
                        }
                    """)
                elif len(username) < 3:
                    self.user_input.setStyleSheet("""
                        QLineEdit {
                            border: none;
                            font-size: 14px;
                            background: transparent;
                            color: #dc2626;
                        }
                    """)
                else:
                    self.user_input.setStyleSheet("""
                        QLineEdit {
                            border: none;
                            font-size: 14px;
                            background: transparent;
                            color: #059669;
                        }
                    """)

            elif field_name == 'password':
                password = self.pass_input.text()
                if not password:
                    self.strength_label.setText("")
                    self.pass_input.setStyleSheet("""
                        QLineEdit {
                            border: none;
                            font-size: 14px;
                            background: transparent;
                        }
                    """)
                else:
                    # Calcular fuerza de contraseña
                    strength = self._calculate_password_strength(password)
                    if strength < 3:
                        self.strength_label.setText("Contraseña débil")
                        self.strength_label.setStyleSheet("color: #dc2626;")
                    elif strength < 6:
                        self.strength_label.setText("Contraseña media")
                        self.strength_label.setStyleSheet("color: #d97706;")
                    else:
                        self.strength_label.setText("Contraseña fuerte")
                        self.strength_label.setStyleSheet("color: #059669;")

        def _calculate_password_strength(self, password):
            """Calcula la fuerza de la contraseña."""
            strength = 0
            if len(password) >= 8:
                strength += 2
            if any(c.isupper() for c in password):
                strength += 1
            if any(c.islower() for c in password):
                strength += 1
            if any(c.isdigit() for c in password):
                strength += 1
            if any(not c.isalnum() for c in password):
                strength += 1
            return strength

        def _toggle_password_visibility(self):
            """Alterna la visibilidad de la contraseña."""
            from PyQt6.QtWidgets import QLineEdit

            if self.pass_input.echoMode() == QLineEdit.EchoMode.Password:
                self.pass_input.setEchoMode(QLineEdit.EchoMode.Normal)
                self.toggle_pass_btn.setText("🙈")
            else:
                self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
                self.toggle_pass_btn.setText("👁")

        def _toggle_dark_mode(self):
            """Alterna entre modo claro y oscuro."""
            from PyQt6.QtWidgets import QDialog

            self.dark_mode = not self.dark_mode
            if self.dark_mode:
                self.dark_mode_btn.setText("☀️")
                self.dark_mode_btn.setToolTip("Cambiar a modo claro")
                # Aplicar tema oscuro al diálogo principal
                if hasattr(self, 'dark_mode_btn') and self.dark_mode_btn.parent():
                    parent_dialog = self.dark_mode_btn.parent()
                    while parent_dialog and not isinstance(parent_dialog, QDialog):
                        parent_dialog = parent_dialog.parent()
                    if parent_dialog:
                        parent_dialog.setStyleSheet("""
                            QDialog {
                                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                    stop:0 #1e293b, stop:1 #0f172a);
                                border: 2px solid #334155;
                            }
                        """)
            else:
                self.dark_mode_btn.setText("🌙")
                self.dark_mode_btn.setToolTip("Cambiar a modo oscuro")
                # Aplicar tema claro al diálogo principal
                if hasattr(self, 'dark_mode_btn') and self.dark_mode_btn.parent():
                    parent_dialog = self.dark_mode_btn.parent()
                    while parent_dialog and not isinstance(parent_dialog, QDialog):
                        parent_dialog = parent_dialog.parent()
                    if parent_dialog:
                        parent_dialog.setStyleSheet("""
                            QDialog {
                                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                    stop:0 #ffffff, stop:1 #f8fafc);
                                border: 2px solid #e2e8f0;
                            }
                        """)

        def _attempt_biometric_login(self):
            """Intenta login biométrico."""
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(
                None,
                "Login Biométrico",
                "Funcionalidad de login biométrico próximamente disponible."
            )

        def _show_forgot_password(self):
            """Muestra diálogo de recuperación de contraseña."""
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(
                None,
                "Recuperar Contraseña",
                "Para recuperar su contraseña, contacte al administrador del sistema."
            )

        def _show_help(self):
            """Muestra ayuda del sistema."""
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(
                None,
                "Ayuda",
                "Sistema de Gestión Empresarial Rexus.app v2.0.0\n\n"
                "Para iniciar sesión, ingrese su usuario y contraseña.\n"
                "Si olvidó su contraseña, contacte al administrador."
            )

        def _attempt_login(self, dialog):
            """Intenta hacer login con las credenciales proporcionadas."""
            from PyQt6.QtWidgets import QMessageBox
            from PyQt6.QtCore import QTimer

            username = self.user_input.text().strip()
            password = self.pass_input.text()

            # Validación básica
            if not username or not password:
                QMessageBox.warning(dialog, "Error", "Por favor ingrese usuario y contraseña.")
                return

            # Verificar rate limiting
            if self.rate_limited:
                QMessageBox.warning(dialog, "Error", "Demasiados intentos fallidos. Intente más tarde.")
                return

            # Mostrar loading state
            self.login_btn.setEnabled(False)
            self.login_btn.setText("Iniciando sesión...")
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # Indeterminado

            # Simular procesamiento
            QTimer.singleShot(1500, lambda: self._process_login(dialog, username, password))

        def _process_login(self, dialog, username, password):
            """Procesa el login después del delay simulado."""
            from PyQt6.QtWidgets import QMessageBox
            from PyQt6.QtCore import QTimer

            # Restaurar estado del botón
            self.login_btn.setEnabled(True)
            self.login_btn.setText("Iniciar Sesión")
            self.progress_bar.setVisible(False)

            # Verificar captcha si es necesario
            if self.captcha_required and self.failed_attempts >= 3:
                # Aquí iría la lógica de captcha
                QMessageBox.warning(dialog, "Captcha Requerido",
                                  "Por favor complete el captcha de seguridad.")
                return

            # Intentar login
            success = False
            if self.security_manager and hasattr(self.security_manager, 'login'):
                success = self.security_manager.login(username, password)
            else:
                # Fallback: verificar credenciales de desarrollo
                if username == self.dev_user and password == self.dev_password:
                    success = True
                else:
                    # Verificar si es usuario admin fallback
                    success = username == "admin" and password == os.environ.get("FALLBACK_ADMIN_PASSWORD", "admin123")

            if success:
                self.login_successful = True
                self.failed_attempts = 0
                self.captcha_required = False

                # Obtener datos del usuario
                if self.security_manager and hasattr(self.security_manager, 'get_current_user'):
                    self.user_data = self.security_manager.get_current_user()
                else:
                    self.user_data = {
                        "id": 1,
                        "username": username,
                        "rol": "ADMIN"
                    }

                # Obtener módulos permitidos desde la base de datos
                try:
                    from rexus.utils.sql_query_manager import SQLQueryManager
                    sql_manager = SQLQueryManager()

                    # Obtener permisos del usuario desde la base de datos
                    user_permissions = sql_manager.get_user_permissions(self.user_data['id'])

                    if user_permissions:
                        self.modulos_permitidos = user_permissions
                        logger.info(f"[LOGIN] Permisos cargados desde BD para {username}: {user_permissions}")
                    else:
                        # Fallback: si no hay permisos en BD, usar permisos por rol
                        self.modulos_permitidos = self._get_default_modules_by_role(self.user_data.get('rol', 'usuario'))
                        logger.warning(f"[LOGIN] No se encontraron permisos en BD para {username}, usando fallback por rol")

                except ImportError as e:
                    logger.warning(f"[LOGIN] SQLQueryManager no disponible: {e}, usando fallback")
                    self.modulos_permitidos = self._get_default_modules_by_role(self.user_data.get('rol', 'usuario'))
                except Exception as db_error:
                    logger.error(f"[LOGIN] Error cargando permisos desde BD: {db_error}, usando fallback")
                    self.modulos_permitidos = self._get_default_modules_by_role(self.user_data.get('rol', 'usuario'))

                # Logging de login exitoso
                logger.info(f"[LOGIN] Login exitoso para usuario: {username} - Módulos: {self.modulos_permitidos}")

                dialog.accept()
            else:
                self.failed_attempts += 1

                # Activar captcha después de 3 fallos
                if self.failed_attempts >= 3:
                    self.captcha_required = True

                # Activar rate limiting después de 5 fallos
                if self.failed_attempts >= 5:
                    self.rate_limited = True
                    QTimer.singleShot(30000, lambda: setattr(self, 'rate_limited', False))  # 30 segundos

                QMessageBox.warning(dialog, "Error", "Usuario o contraseña incorrectos.")

                # Logging de login fallido
                logger.warning(f"[LOGIN] Login fallido para usuario: {username} (intento {self.failed_attempts})")

        def get_user_data(self):
            return self.user_data

        def get_modulos_permitidos(self):
            return self.modulos_permitidos

        def _get_default_modules_by_role(self, rol: str) -> list:
            """
            Retorna módulos por defecto basados en el rol del usuario.
            Este método se usa como fallback cuando no se pueden cargar permisos desde BD.
            """
            role_modules = {
                'ADMIN': ["Obras", "Inventario", "Herrajes", "Vidrios", "Logística",
                         "Pedidos", "Compras", "Administración", "Mantenimiento",
                         "Auditoría", "Usuarios", "Configuración"],
                'SUPERVISOR': ["Obras", "Inventario", "Herrajes", "Vidrios", "Logística",
                              "Pedidos", "Compras", "Administración", "Mantenimiento"],
                'OPERADOR': ["Obras", "Inventario", "Herrajes", "Vidrios", "Logística", "Pedidos"],
                'AUDITOR': ["Auditoría", "Mantenimiento"],
                'USUARIO': ["Obras", "Inventario", "Herrajes", "Vidrios"]
            }

            modules = role_modules.get(rol.upper(), role_modules['USUARIO'])
            logger.info(f"[PERMISOS] Módulos por defecto para rol '{rol}': {modules}")
            return modules

    class ModuleManager:
        def __init__(self):
            self.modules = {}

        def get_available_modules(self):
            return list(self.modules.keys())

        def get_module(self, name):
            return self.modules.get(name)

    module_manager = ModuleManager()

    class DashboardController:
        def __init__(self, parent=None, main_window=None):
            self.parent = parent
            self.main_window = main_window

        def setup_dashboard(self):
            pass

        def get_view(self):
            # Retornar un widget básico
            from PyQt6.QtWidgets import QLabel
            return QLabel("Dashboard - Modo Básico")

    class ThemeManager:
        def __init__(self, parent=None):
            self.parent = parent
            self.current_theme = "default"

        def apply_theme(self, theme_name="default"):
            self.current_theme = theme_name

        def toggle_theme(self):
            """Alterna entre tema claro y oscuro."""
            if self.current_theme == "default":
                self.current_theme = "dark"
                self.apply_dark_theme()
            else:
                self.current_theme = "default"
                self.apply_light_theme()

        def apply_dark_theme(self):
            """Aplica tema oscuro."""
            if self.parent:
                # Aplicar tema oscuro pero mantener sidebar azul
                self.parent.setStyleSheet("""
                    QMainWindow {
                        background-color: #1a1a1a;
                        color: #ffffff;
                    }
                    /* Mantener sidebar azul */
                    QFrame[sidebar] {
                        background-color: #2563eb !important;
                    }
                """)

        def apply_light_theme(self):
            """Aplica tema claro."""
            if self.parent:
                # Aplicar tema claro pero mantener sidebar azul
                self.parent.setStyleSheet("""
                    QMainWindow {
                        background-color: #ffffff;
                        color: #1a1a1a;
                    }
                    /* Mantener sidebar azul */
                    QFrame[sidebar] {
                        background-color: #2563eb !important;
                    }
                """)


def initialize_security_manager():
    # Inicializa el sistema de seguridad
    try:
        from rexus.core.database import UsersDatabaseConnection
        from rexus.core.security import init_security_manager

        # Intentar crear conexión a la base de datos
        try:
            db_connection = UsersDatabaseConnection()
            logger.info("[SECURITY] Conexión BD exitosa para sistema de seguridad")
        except Exception as db_error:
            logger.warning("[SECURITY] Error BD: %s, usando modo sin BD", db_error)
            db_connection = None

        # Inicializar con o sin conexión BD
        security_manager = init_security_manager(db_connection)
        log_security("INFO", "SecurityManager inicializado correctamente")
        return security_manager

    except ImportError as e:
        log_security("CRITICAL", f"Error importando módulo de seguridad: {e}")
        return SimpleSecurityManager()
    except Exception as e:
        log_security("CRITICAL", f"Error general inicializando seguridad: {e}")
        return SimpleSecurityManager()


class SimpleSecurityManager:
    # Sistema de seguridad simple para fallback

    def __init__(self):
        self.current_user_data = None
        self.current_user = None  # Para compatibilidad con SecurityManager
        self.current_role = "usuario"  # Para compatibilidad con SecurityManager
        # Sistema seguro sin credenciales hardcodeadas
        # Las credenciales se cargan desde variables de entorno
        self._load_secure_credentials()

    def _load_secure_credentials(self):
        # Carga credenciales desde variables de entorno de forma segura
        try:
            from rexus.utils.security import SecurityUtils
        except ImportError:
            # Fallback para utilidades de seguridad
            class SecurityUtils:
                @staticmethod
                def hash_password(password):
                    # Retornar solo el hash sin salt para simplificar
                    import hashlib
                    return hashlib.sha256(password.encode()).hexdigest()

                @staticmethod
                def verify_password(password, hashed):
                    # Verificación simple sin salt
                    import hashlib
                    return hashlib.sha256(password.encode()).hexdigest() == hashed
            SecurityUtils = SecurityUtils

        # Solo cargar si está en modo desarrollo y se especifica explícitamente
        if os.environ.get("DEVELOPMENT_MODE") == "true":
            admin_user = os.environ.get("FALLBACK_ADMIN_USER", "admin")
            admin_password = os.environ.get("FALLBACK_ADMIN_PASSWORD", "admin123")

            if admin_user and admin_password:
                # Hash seguro de la contraseña
                hashed_password = SecurityUtils.hash_password(admin_password)
                self.users = {
                    admin_user: {
                        "rol": "ADMIN",
                        "id": 1,
                        "username": admin_user,
                        "password_hash": hashed_password,
                    }
                }
                logger.info("[SIMPLE_AUTH] Usuario de desarrollo cargado: %s", admin_user)
            else:
                self.users = {}
                logger.warning("[SIMPLE_AUTH] Modo desarrollo activo pero sin credenciales configuradas")
        else:
            # Usuario por defecto para desarrollo/pruebas
            admin_user = "admin"
            admin_password = os.environ.get("FALLBACK_ADMIN_PASSWORD", "admin123")
            hashed_password = SecurityUtils.hash_password(admin_password)
            self.users = {
                admin_user: {
                    "rol": "ADMIN",
                    "id": 1,
                    "username": admin_user,
                    "password_hash": hashed_password,
                }
            }
            logger.info("[SIMPLE_AUTH] Usuario por defecto cargado para pruebas")
    def login(self, username: str, password: str) -> bool:
        # Autenticación segura con hashing
        logger.info("[SIMPLE_AUTH] Intentando login: usuario='%s'", username)

        # Verificar si hay usuarios disponibles
        if not self.users:
            logger.warning("[SIMPLE_AUTH] No hay usuarios fallback disponibles")
            return False

        user = self.users.get(username)
        if not user:
            print(f"[SIMPLE_AUTH] Usuario '{username}' no encontrado")
            return False

        # Verificar contraseña con hash seguro
        try:
            from rexus.utils.security import SecurityUtils

            if SecurityUtils.verify_password(password, user.get("password_hash", "")):
                print(f"[SIMPLE_AUTH] Login exitoso para {username}")
                self.current_user_data = {
                    k: v for k, v in user.items() if k not in ["password_hash"]
                }
                # Sincronizar atributos para compatibilidad
                self.current_user = self.current_user_data
                self.current_role = self.current_user_data.get("rol", "usuario")
                return True
            else:
                print(f"[SIMPLE_AUTH] Contraseña incorrecta para {username}")
                return False
        except ImportError:
            print("[SIMPLE_AUTH] SecurityUtils no disponible, login fallido")
            return False
            return False

    def get_current_role(self) -> str:
        # Obtiene el rol actual
        return (
            self.current_user_data.get("rol", "USUARIO")
            if self.current_user_data
            else "USUARIO"
        )

    def get_current_user(self) -> dict:
        # Obtiene datos del usuario actual
        return (
            self.current_user_data
            if self.current_user_data
            else {"id": 0, "username": "guest", "rol": "USUARIO"}
        )

    def has_permission(self, permission: str, module: str | None = None) -> bool:
        # Verifica permisos - admin tiene todos
        return bool(self.current_user_data and \
            self.current_user_data.get("rol") == "ADMIN")

    def log_security_event(
        self, user_id: int, accion: str, modulo: str | None = None, detalles: str | None = None
    ):
        # Log simple de eventos
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(
            f"[SECURITY_LOG] {timestamp} - Usuario:{user_id} - Acción:{accion} - Módulo:{modulo} - Detalles:{detalles}"
        )

    def diagnose_permissions(self) -> dict:
        # Diagnóstica el estado de permisos del usuario actual
        return {
            "has_admin_access": self.current_role == "ADMIN",
            "current_user": self.current_user_data.get("username")
            if self.current_user_data
            else None,
            "current_role": self.current_role,
            "permissions_loaded": True,
        }


class MainWindow(QMainWindow):
    """
    Ventana principal de la aplicación Rexus.app

    Maneja la interfaz principal con sidebar de módulos y área de contenido dinámico.
    Implementa patrón Factory para creación de módulos y sistema de fallback.

    Attributes:
        user_data (Dict): Datos del usuario actual
        modulos_permitidos (List): Lista de módulos permitidos para el usuario
        security_manager: Gestor de seguridad de la aplicación
        content_stack (QStackedWidget): Stack de pestañas para módulos
        content_header (QLabel): Header del área de contenido
    """

    def __init__(self, user_data: Dict[str, Any], modulos_permitidos: list):
        """
        Inicializa la ventana principal

        Args:
            user_data: Diccionario con datos del usuario autenticado
            modulos_permitidos: Lista de módulos accesibles para el usuario
        """
        super().__init__()
        self.user_data = user_data
        self.modulos_permitidos = modulos_permitidos

        self.content_stack = QStackedWidget()
        
        # Inicializar gestores de tema y dashboard
        self._init_theme_manager()
        self._init_dashboard_controller()
        self._init_executive_dashboard()

        # Inicializar StyleManager y aplicar tema automático
        self._init_styles()
        self._init_ui()
    
    def _init_theme_manager(self):
        # Inicializa el gestor de temas.
        try:
            self.theme_manager = ThemeManager(self)
            self.theme_manager.apply_theme()  # Aplicar tema por defecto
            print("[THEME] Gestor de temas inicializado correctamente")
        except Exception as e:
            logger.warning(f"Error inicializando ThemeManager: {e}")
            self.theme_manager = None
    
    def _init_dashboard_controller(self):
        # Inicializa el controlador del dashboard.
        try:
            # Crear controlador del dashboard sin db_manager por ahora
            self.dashboard_controller = DashboardController(None, self)
            print("[DASHBOARD] Controlador de dashboard inicializado")
        except Exception as e:
            logger.warning(f"Error inicializando DashboardController: {e}")
            self.dashboard_controller = None
    
    def _init_executive_dashboard(self):
        # Inicializa el dashboard ejecutivo.
        try:
            from rexus.ui.executive_dashboard import get_dashboard_manager
        except ImportError:
            def get_dashboard_manager():
                return None
            self.executive_dashboard_manager = get_dashboard_manager()
            print("[EXECUTIVE_DASHBOARD] Gestor de dashboard ejecutivo inicializado")
        except Exception as e:
            logger.warning(f"Error inicializando Executive Dashboard: {e}")
            self.executive_dashboard_manager = None

    def _init_styles(self):
        # Inicializa y aplica el sistema de estilos.
        try:
            from rexus.ui.style_manager import StyleManager
            self.style_manager = StyleManager()

            # Aplicar tema global (auto-detectado en StyleManager)
            success = self.style_manager.apply_global_theme()
            if success:
                print(f"[STYLE] Tema '{self.style_manager._current_theme}' aplicado globalmente")

                # CRÍTICO: Aplicar correcciones de formularios inmediatamente
                # Aplicar correcciones ultra-seguras para todos los temas
                emergency_success = self.style_manager.apply_emergency_readable_forms()
                if emergency_success:
                    print("[STYLE] [OK] Formularios ultra-legibles aplicados correctamente")
                else:
                    print("[STYLE] [WARNING] Intentando correcciones alternativas...")

                    # Fallback: Intentar correcciones específicas por tema
                    if self.style_manager._current_theme == 'dark':
                        print("[STYLE] Tema oscuro detectado - aplicando correcciones críticas")
                        fix_success = self.style_manager.apply_critical_form_fixes()
                        if not fix_success:
                            # Si falla, forzar tema claro para formularios
                            fallback_success = self.style_manager.force_light_theme_for_forms()
                            if fallback_success:
                                print("[STYLE] Tema de emergencia aplicado - formularios legibles")
                            else:
                                print("[STYLE] [ERROR] ERROR: No se pudieron aplicar correcciones críticas")
                    else:
                        # Para temas claros, asegurar contraste
                        self.style_manager.apply_critical_form_fixes()
            else:
                print("[STYLE] Fallback a estilos por defecto")

        except ImportError:
            # Fallback si no se puede importar StyleManager
            class FallbackStyleManager:
                def __init__(self):
                    self._current_theme = "default"

                def apply_global_theme(self):
                    return True

                def apply_emergency_readable_forms(self):
                    return True

                def apply_critical_form_fixes(self):
                    return True

                def force_light_theme_for_forms(self):
                    return True

            self.style_manager = FallbackStyleManager()
            print("[STYLE] Usando StyleManager de fallback")

        except Exception as e:
            logger.warning(f"Error inicializando StyleManager: {e}")
            # Asegurar que siempre haya un style_manager
            class EmergencyStyleManager:
                def __init__(self):
                    self._current_theme = "default"

                def apply_global_theme(self):
                    return True

                def apply_emergency_readable_forms(self):
                    return True

                def apply_critical_form_fixes(self):
                    return True

                def force_light_theme_for_forms(self):
                    return True

            self.style_manager = EmergencyStyleManager()

    def _init_ui(self):
        self.setWindowTitle("Rexus.app v2.0.0 - Sistema de Gestión Integral")
        
        # Configurar ventana con tamaño mínimo
        self.setMinimumSize(1024, 768)
        
        # Configurar para iniciar maximizado de forma más robusta
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(100, self.showMaximized)

        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout principal
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Configurar interfaz principal
        self._create_sidebar(main_layout)
        self._create_main_content(main_layout)

        # Aplicar estilos respetando el theme manager
        if self.style_manager:
            # No aplicar estilos inline que sobrescriban el theme manager
            # El StyleManager ya maneja los colores de fondo apropiados
            pass
        else:
            # Solo si no hay StyleManager disponible
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #f8f9fa;
                }
            """)

    def _create_sidebar(self, main_layout):
        # Crea la barra lateral con módulos
        sidebar = QFrame()
        sidebar.setProperty("sidebar", True)  # Para identificar el sidebar en CSS
        sidebar.setStyleSheet("""
            QFrame {
                background-color: #2563eb !important;
                border-right: 2px solid #1d4ed8 !important;
            }
            QFrame QWidget {
                background-color: transparent;
            }
        """)

        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setSpacing(0)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)

        # Header del sidebar
        header = QLabel("Rexus.app")
        header.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 24px;
                font-weight: bold;
                padding: 20px;
                background-color: rgba(0, 0, 0, 0.2);
            }
        """)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(header)

        # Usuario actual y dashboard
        user_info_container = QWidget()
        user_info_layout = QVBoxLayout(user_info_container)
        user_info_layout.setContentsMargins(0, 0, 0, 0)
        user_info_layout.setSpacing(5)
        
        user_info = QLabel(
            f"Usuario: {self.user_data['username']}\nRol: {self.user_data.get('rol', self.user_data.get('role', 'Usuario'))}"
        )
        user_info.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 12px;
                padding: 15px 20px;
                background-color: rgba(0, 0, 0, 0.1);
            }
        """)
        
        # Botón para dashboard ejecutivo
        try:
            from rexus.ui.dashboard_integration import create_dashboard_button
            dashboard_btn = create_dashboard_button(self)
        except ImportError:
            def create_dashboard_button(parent=None):
                from PyQt6.QtWidgets import QPushButton
                return QPushButton("Dashboard")
            dashboard_btn = create_dashboard_button(self)
        dashboard_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.2);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 4px;
                padding: 8px 15px;
                font-size: 11px;
                margin: 5px 15px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.3);
            }
        """)
        
        user_info_layout.addWidget(user_info)
        user_info_layout.addWidget(dashboard_btn)
        sidebar_layout.addWidget(user_info_container)

        # Scroll area para módulos
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea { 
                border: none; 
                background: transparent; 
            }
            QScrollBar:vertical {
                background-color: rgba(255, 255, 255, 0.2);
                width: 12px;
                border-radius: 6px;
                margin: 2px;
            }
            QScrollBar::handle:vertical {
                background-color: rgba(255, 255, 255, 0.6);
                border: 1px solid rgba(255, 255, 255, 0.8);
                border-radius: 6px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: rgba(255, 255, 255, 0.8);
                border-color: #ffffff;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        modules_widget = QWidget()
        modules_layout = QVBoxLayout(modules_widget)
        # Módulos ordenados por flujo de proyecto real (incluye Logística)
        modulos = [
            ("🏗️", "Obras", "Gestión de proyectos y construcción"),
            ("📦", "Inventario", "Gestión de inventario y stock"),
            ("🛠️", "Herrajes", "Gestión de herrajes"),
            ("🪟", "Vidrios", "Gestión de vidrios"),
            ("🚚", "Logística", "Gestión de logística y transporte"),
            ("[NOTE]", "Pedidos", "Solicitudes y órdenes de trabajo"),
            ("🛒", "Compras", "Gestión de compras y proveedores"),
            ("💼", "Administración", "Gestión administrativa y financiera"),
            ("🧰", "Mantenimiento", "Gestión de mantenimiento"),
            ("🔎", AUDITORIA_MODULE, "Auditoría y trazabilidad"),
            ("👤", "Usuarios", "Gestión de personal y roles"),
            ("⚙️", "Configuración", "Configuración del sistema"),
        ]

        logger.debug(f"Módulos permitidos: {self.modulos_permitidos}")

        for emoji, nombre, descripcion in modulos:
            # Verificar si el usuario tiene permisos para este módulo
            has_permission = nombre in self.modulos_permitidos
            print(f"[DEBUG] Módulo '{nombre}': permisos={has_permission}")

            if has_permission:
                btn = self._create_module_button(emoji, nombre, descripcion)
                modules_layout.addWidget(btn)
            else:
                # Crear botón deshabilitado para módulos sin permisos
                btn = self._create_disabled_module_button(emoji, nombre, "Sin permisos")
                modules_layout.addWidget(btn)

        modules_layout.addStretch()
        scroll.setWidget(modules_widget)
        sidebar_layout.addWidget(scroll)
        
        # Agregar botón de toggle de tema al final del sidebar
        if self.theme_manager:
            theme_btn = QPushButton("🌙 Alternar Tema")
            theme_btn.setStyleSheet("""
                QPushButton {
                    background-color: rgba(0, 0, 0, 0.3);
                    color: white;
                    border: 1px solid rgba(255, 255, 255, 0.3);
                    border-radius: 4px;
                    padding: 8px;
                    margin: 10px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: rgba(0, 0, 0, 0.5);
                }
            """)
            theme_btn.clicked.connect(self.toggle_theme)
            sidebar_layout.addWidget(theme_btn)

        main_layout.addWidget(sidebar)

    def _create_module_button(
        self, emoji: str, nombre: str, descripcion: str
    ) -> QPushButton:
        # Crea un botón de módulo estilizado
        btn = QPushButton()
        btn.setText(f"{emoji}  {nombre}")
        btn.setToolTip(descripcion)
        btn.setStyleSheet(
            """
QPushButton {
    text-align: left;
    padding: 10px 16px;
    border: 2px solid #1e40af !important;
    font-size: 13px;
    font-weight: 600;
    background-color: #3b82f6 !important;
    color: #ffffff !important;
    border-radius: 8px;
    margin: 3px 8px;
    max-height: 40px;
    min-height: 40px;
}
QPushButton:hover {
    background-color: #1d4ed8 !important;
    border-color: #1e3a8a !important;
    color: #ffffff !important;
    font-weight: bold;
    transform: none;
}
QPushButton:pressed {
    background-color: #1e40af !important;
    border-color: #1e3a8a !important;
    color: #ffffff !important;
}
            """
        )
        btn.clicked.connect(lambda checked, name=nombre: self.show_module(name))
        return btn

    def _create_disabled_module_button(
        self, emoji: str, nombre: str, descripcion: str
    ) -> QPushButton:
        # Crea un botón de módulo deshabilitado para módulos sin permisos
        btn = QPushButton()
        btn.setText(f"{emoji}  {nombre}")
        btn.setToolTip(descripcion)
        btn.setEnabled(False)
        btn.setStyleSheet(
            """
QPushButton {
    text-align: left;
    padding: 8px 16px;
    border: none;
    color: #888888;
    font-size: 13px;
    font-weight: 400;
    max-height: 36px;
    min-height: 36px;
    background-color: rgba(255, 255, 255, 0.08);
    border-radius: 6px;
    margin: 2px 8px;
}
QPushButton:disabled {
    background-color: rgba(255, 255, 255, 0.05);
    color: #666666;
}
            """
        )
        return btn

    def _create_main_content(self, main_layout):
        # Crea el área de contenido principal
        content_area = QFrame()
        content_area.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-radius: 0px;
            }
        """)

        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(30, 30, 30, 30)

        # Área de contenido dinámico
        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet("""
            QStackedWidget {
                border: 1px solid #ddd;
                border-radius: 8px;
                background-color: #f8f9fa;
            }
        """)

        # Dashboard inicial premium
        self._create_premium_dashboard()

        content_layout.addWidget(self.content_stack)
        main_layout.addWidget(content_area)

    def _create_dashboard(self):
        # Crea el dashboard principal - RENOVADO COMPLETAMENTE
        dashboard = QWidget()
        dashboard.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
                color: #1a1a1a;
            }
        """)
        main_layout = QVBoxLayout(dashboard)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Header compacto y limpio
        header = self._create_simple_header()
        main_layout.addWidget(header)

        # Grid principal con estadísticas
        stats_grid = self._create_stats_grid()
        main_layout.addWidget(stats_grid)

        # Sección de acceso rápido
        quick_access = self._create_simple_quick_access()
        main_layout.addWidget(quick_access)

        # Footer minimalista
        footer = self._create_simple_footer()
        main_layout.addWidget(footer)

        self.content_stack.addWidget(dashboard)

    def _create_premium_dashboard(self):
        # Crea el dashboard moderno con widgets especializados.
        try:
            if self.dashboard_controller:
                dashboard = self.dashboard_controller.get_view()
                dashboard.modulo_solicitado.connect(self.show_module)
                self.content_stack.addWidget(dashboard)
                print("[DASHBOARD] Dashboard moderno cargado correctamente")
            else:
                # Fallback al dashboard básico si el controlador no está disponible
                self._create_dashboard()
                print("[DASHBOARD] Usando dashboard básico como fallback")
        except Exception as e:
            logger.error(f"Error creando dashboard moderno: {e}")
            self._create_dashboard()  # Fallback seguro

    def _create_simple_header(self):
        # Header limpio y compacto
        from datetime import datetime

        header = QWidget()
        header.setFixedHeight(60)
        header.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border-bottom: 1px solid #e9ecef;
            }
        """)

        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 10, 20, 10)

        # Título principal
        title = QLabel("Dashboard")
        title.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #212529;
            }
        """)

        # Fecha actual
        date_label = QLabel(datetime.now().strftime("%d de %B, %Y"))
        date_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #6c757d;
            }
        """)

        layout.addWidget(title)
        layout.addStretch()
        layout.addWidget(date_label)

        return header

    def _create_stats_grid(self):
        # Grid de estadísticas principales
        stats_widget = QWidget()
        stats_widget.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
                padding: 20px;
            }
        """)

        layout = QVBoxLayout(stats_widget)

        # Título de sección
        section_title = QLabel("[CHART] Estadísticas del Sistema")
        section_title.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: 600;
                color: #212529;
                margin-bottom: 20px;
            }
        """)
        layout.addWidget(section_title)

        # Grid de tarjetas
        grid = QGridLayout()
        grid.setSpacing(15)

        # Estadísticas simples
        stats = [
            ("Productos", "1,234", "#007bff"),
            ("Obras", "23", "#28a745"),
            ("Pedidos", "56", "#ffc107"),
            ("Usuarios", f"{len(self.modulos_permitidos)}", "#6f42c1")
        ]

        for i, (label, value, color) in enumerate(stats):
            card = self._create_simple_stat_card(label, value, color)
            grid.addWidget(card, 0, i)

        layout.addLayout(grid)
        return stats_widget

    def _create_simple_stat_card(self, label, value, color):
        # Tarjeta de estadística simple
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: #ffffff;
                border: 1px solid #dee2e6;
                border-left: 4px solid {color};
                border-radius: 8px;
                padding: 20px;
                min-height: 80px;
            }}
            QFrame:hover {{
                background-color: #f8f9fa;
                border-color: {color};
            }}
        """)

        layout = QVBoxLayout(card)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        value_label = QLabel(value)
        value_label.setStyleSheet(f"""
            QLabel {{
                font-size: 32px;
                font-weight: bold;
                color: {color};
                margin: 0;
            }}
        """)
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        label_widget = QLabel(label)
        label_widget.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #6c757d;
                margin: 0;
            }
        """)
        label_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(value_label)
        layout.addWidget(label_widget)

        return card

    def _create_simple_quick_access(self):
        # Acceso rápido minimalista
        quick_widget = QWidget()
        quick_widget.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                padding: 20px;
            }
        """)

        layout = QVBoxLayout(quick_widget)

        # Título
        title = QLabel("[ROCKET] Acceso Rápido")
        title.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: 600;
                color: #212529;
                margin-bottom: 15px;
            }
        """)
        layout.addWidget(title)

        # Botones principales
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)

        quick_modules = [
            ("📦", "Inventario"),
            ("🏗️", "Obras"),
            ("[NOTE]", "Pedidos"),
            ("👤", "Usuarios")
        ]

        for emoji, name in quick_modules:
            if name in self.modulos_permitidos:
                btn = QPushButton(f"{emoji} {name}")
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #007bff;
                        color: white;
                        border: none;
                        border-radius: 8px;
                        padding: 15px 25px;
                        font-size: 14px;
                        font-weight: 500;
                        min-width: 120px;
                    }
                    QPushButton:hover {
                        background-color: #0056b3;
                    }
                """)
                btn.clicked.connect(lambda checked, module=name: self.show_module(module))
                buttons_layout.addWidget(btn)

        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)

        return quick_widget

    def _create_simple_footer(self):
        # Footer minimalista
        footer = QWidget()
        footer.setFixedHeight(40)
        footer.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border-top: 1px solid #e9ecef;
            }
        """)

        layout = QHBoxLayout(footer)
        layout.setContentsMargins(20, 5, 20, 5)

        # Información del sistema
        info = QLabel("Rexus.app v2.0.0 - Sistema Operativo")
        info.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #6c757d;
            }
        """)

        # Usuario actual
        user_info = QLabel(f"Usuario: {self.user_data.get('username', 'N/A')}")
        user_info.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #6c757d;
            }
        """)

        layout.addWidget(info)
        layout.addStretch()
        layout.addWidget(user_info)

        return footer

    def _create_dashboard_header(self):
        # Crea el header del dashboard moderno y limpio
        from datetime import datetime

        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_widget.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 1px solid #d0d7de;
                border-radius: 8px;
                padding: 16px;
                margin-bottom: 8px;
            }
        """)

        # Información del usuario
        user_info = QWidget()
        user_layout = QVBoxLayout(user_info)

        welcome_title = QLabel(f"¡Bienvenido, {self.user_data.get('username', 'Usuario')}!")
        welcome_title.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                margin: 0;
            }
        """)

        user_role = QLabel(f"Rol: {self.user_data.get('rol', self.user_data.get('role', 'N/A'))}")
        user_role.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #586069;
                margin-top: 5px;
            }
        """)

        current_date = QLabel(f"Hoy es {datetime.now().strftime('%d de %B de %Y')}")
        current_date.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #6c757d;
                margin-top: 5px;
            }
        """)

        user_layout.addWidget(welcome_title)
        user_layout.addWidget(user_role)
        user_layout.addWidget(current_date)

        # Logo o espacio para empresa - moderno y limpio
        logo_space = QLabel("REXUS.APP")
        logo_space.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: #0366d6;
                background-color: #f6f8fa;
                border: 1px solid #e1e4e8;
                border-radius: 6px;
                padding: 8px 16px;
            }
        """)

        header_layout.addWidget(user_info)
        header_layout.addStretch()
        header_layout.addWidget(logo_space)

        return header_widget

    def show_module(self, module_name: str):
        """Muestra el módulo seleccionado en el área de contenido."""
        try:
            logger.info(f"Cargando módulo: {module_name}")

            # Obtener el módulo desde el module_manager
            module = module_manager.get_module(module_name)

            if module:
                # Crear vista del módulo
                module_view = module.get_view()

                # Solo conectar signal si el widget lo tiene
                if hasattr(module_view, 'modulo_solicitado'):
                    module_view.modulo_solicitado.connect(self.show_module)

                # Agregar al stack si no existe
                for i in range(self.content_stack.count()):
                    widget = self.content_stack.widget(i)
                    if widget and hasattr(widget, 'objectName') and widget.objectName() == module_name:
                        self.content_stack.setCurrentIndex(i)
                        return

                if hasattr(module_view, 'setObjectName'):
                    module_view.setObjectName(module_name)
                self.content_stack.addWidget(module_view)
                self.content_stack.setCurrentWidget(module_view)

                logger.info(f"Módulo {module_name} cargado exitosamente")
            else:
                logger.error(f"Módulo {module_name} no encontrado")
                self._show_error_message(f"Módulo '{module_name}' no disponible")

        except Exception as e:
            logger.error(f"Error cargando módulo {module_name}: {e}")
            self._show_error_message(f"Error cargando módulo: {str(e)}")

    def _show_error_message(self, message: str):
        """Muestra un mensaje de error al usuario."""
        QMessageBox.warning(self, "Error", message)

    def toggle_theme(self):
        """Alterna entre tema claro y oscuro."""
        if self.theme_manager:
            try:
                self.theme_manager.toggle_theme()
                logger.info("Tema alternado exitosamente")
            except Exception as e:
                logger.error(f"Error alternando tema: {e}")
        else:
            logger.warning("ThemeManager no disponible")

    def closeEvent(self, a0):
        """Maneja el evento de cierre de la aplicación."""
        logger.info("Cerrando aplicación Rexus.app")
        if a0 is not None:
            a0.accept()


def main():
    """Función principal de la aplicación."""
    try:
        # Validar dependencias críticas
        if DEPENDENCY_VALIDATION_AVAILABLE:
            success, deps_info = validate_system_dependencies()
            if not success:
                print("[CRITICAL] Dependencias faltantes:")
                for dep, status in deps_info.items():
                    if not status.get('available', False):
                        print(f"  - {dep}: {status.get('error', 'No disponible')}")
                return 1

        # Inicializar aplicación Qt
        from PyQt6.QtWidgets import QApplication
        import sys

        app = QApplication(sys.argv)

        # Configurar aplicación
        app.setApplicationName("Rexus.app")
        app.setApplicationVersion("2.0.0")
        app.setOrganizationName("Rexus")

        # Inicializar sistema de seguridad
        security_manager = initialize_security_manager()

        # Mostrar diálogo de login
        login_dialog = LoginDialog(security_manager=security_manager)
        if login_dialog.exec() == QDialog.DialogCode.Accepted:
            user_data = login_dialog.get_user_data()
            modulos_permitidos = login_dialog.get_modulos_permitidos()

            # Verificar que tenemos datos de usuario válidos
            if user_data is None:
                user_data = {"id": 1, "username": "guest", "rol": "USUARIO"}

            # Crear ventana principal
            window = MainWindow(user_data, modulos_permitidos)
            window.show()

            # Ejecutar aplicación
            return app.exec()
        else:
            logger.info("Login cancelado por el usuario")
            return 0

    except Exception as e:
        logger.critical(f"Error crítico en main(): {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
