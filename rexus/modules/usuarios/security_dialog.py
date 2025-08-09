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

Diálogo de Configuración de Seguridad Avanzada
Interfaz para 2FA, cambio de contraseñas y configuraciones de seguridad
"""

import base64
import json
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTabWidget, QWidget, QTextEdit, QCheckBox, QSpinBox, QGroupBox,
    QFormLayout, QProgressBar, QMessageBox, QScrollArea, QFrame
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QPixmap, QFont, QPalette
from rexus.utils.unified_sanitizer import unified_sanitizer, sanitize_string, sanitize_numeric

from .security_features import UserSecurityManager, create_security_manager


class SecurityConfigDialog(QDialog):
    """Diálogo principal de configuración de seguridad."""
    
    security_updated = pyqtSignal(str, str)  # username, action
    
    def __init__(self, usuarios_model, current_username: str, parent=None):
        super().__init__(parent)
        self.usuarios_model = usuarios_model
        self.current_username = current_username
        self.security_manager = create_security_manager(usuarios_model)
        
        self.setup_ui()
        self.load_user_security_status()
        
    def setup_ui(self):
        """Configura la interfaz de usuario."""
        self.setWindowTitle("Configuración de Seguridad Avanzada")
        self.setModal(True)
        self.resize(600, 700)
        
        # Layout principal
        layout = QVBoxLayout(self)
        
        # Header
        header = self.create_header()
        layout.addWidget(header)
        
        # Tabs de configuración
        tabs = QTabWidget()
        
        # Tab 1: Contraseña
        tabs.addTab(self.create_password_tab(), "🔐 Contraseña")
        
        # Tab 2: Two-factor Authentication
        tabs.addTab(self.create_2fa_tab(), "📱 2FA")
        
        # Tab 3: Seguridad de cuenta
        tabs.addTab(self.create_account_security_tab(), "🛡️ Seguridad")
        
        # Tab 4: Actividad
        tabs.addTab(self.create_activity_tab(), "📊 Actividad")
        
        layout.addWidget(tabs)
        
        # Botones
        buttons_layout = QHBoxLayout()
        
        self.btn_save = QPushButton("💾 Guardar Cambios")
        self.btn_save.clicked.connect(self.save_changes)
        
        self.btn_cancel = QPushButton("❌ Cancelar")
        self.btn_cancel.clicked.connect(self.reject)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.btn_save)
        buttons_layout.addWidget(self.btn_cancel)
        
        layout.addLayout(buttons_layout)
        
        # Aplicar estilos
        self.apply_styles()
    
    def create_header(self) -> QWidget:
        """Crea el header del diálogo."""
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2980b9, stop:1 #3498db);
                border-radius: 8px;
                margin-bottom: 10px;
            }
        """)
        
        layout = QVBoxLayout(header)
        
        title = QLabel("🔒 Configuración de Seguridad Avanzada")
        title.setStyleSheet("color: white; font-size: 18px; font-weight: bold; padding: 10px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        subtitle = QLabel(f"Usuario: {self.current_username}")
        subtitle.setStyleSheet("color: #ecf0f1; font-size: 12px; padding: 0 10px 10px 10px;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(title)
        layout.addWidget(subtitle)
        
        return header
    
    def create_password_tab(self) -> QWidget:
        """Crea la pestaña de configuración de contraseña."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Grupo de cambio de contraseña
        password_group = QGroupBox("Cambiar Contraseña")
        password_layout = QFormLayout(password_group)
        
        self.current_password = QLineEdit()
        self.current_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.current_password.setPlaceholderText("Contraseña actual")
        
        self.new_password = QLineEdit()
        self.new_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_password.setPlaceholderText("Nueva contraseña")
        self.new_password.textChanged.connect(self.validate_password_strength)
        
        self.confirm_password = QLineEdit()
        self.confirm_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password.setPlaceholderText("Confirmar nueva contraseña")
        
        # Indicador de fortaleza
        self.password_strength = QProgressBar()
        self.password_strength.setMaximum(8)
        self.password_strength.setTextVisible(False)
        
        self.strength_label = QLabel("Fortaleza: No evaluada")
        self.strength_requirements = QTextEdit()
        self.strength_requirements.setMaximumHeight(100)
        self.strength_requirements.setReadOnly(True)
        
        password_layout.addRow("Contraseña actual:", self.current_password)
        password_layout.addRow("Nueva contraseña:", self.new_password)
        password_layout.addRow("Confirmar contraseña:", self.confirm_password)
        password_layout.addRow("Fortaleza:", self.password_strength)
        password_layout.addRow("", self.strength_label)
        password_layout.addRow("Requisitos:", self.strength_requirements)
        
        layout.addWidget(password_group)
        layout.addStretch()
        
        return widget
    
    def create_2fa_tab(self) -> QWidget:
        """Crea la pestaña de configuración 2FA."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Estado actual de 2FA
        status_group = QGroupBox("Estado de Two-Factor Authentication")
        status_layout = QVBoxLayout(status_group)
        
        self.tfa_status = QLabel("Estado: Verificando...")
        self.tfa_status.setStyleSheet("font-weight: bold;")
        
        status_layout.addWidget(self.tfa_status)
        layout.addWidget(status_group)
        
        # Configuración de 2FA
        self.tfa_config_group = QGroupBox("Configurar 2FA")
        tfa_layout = QVBoxLayout(self.tfa_config_group)
        
        # Instrucciones
        instructions = QLabel("""
        <b>Pasos para configurar 2FA:</b><br>
        1. Instale una app de autenticación (Google Authenticator, Authy, etc.)<br>
        2. Escanee el código QR o ingrese la clave manualmente<br>
        3. Ingrese el código de 6 dígitos para verificar
        """)
        instructions.setWordWrap(True)
        tfa_layout.addWidget(instructions)
        
        # QR Code y clave manual
        self.qr_label = QLabel("Código QR aparecerá aquí")
        self.qr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.qr_label.setMinimumHeight(200)
        self.qr_label.setStyleSheet("border: 2px dashed #bdc3c7; border-radius: 8px;")
        
        self.manual_key_label = QLabel("Clave manual: Generar primero")
        self.manual_key_label.setWordWrap(True)
        self.manual_key_label.setStyleSheet("font-family: monospace; background: #ecf0f1; padding: 8px; border-radius: 4px;")
        
        # Botones de 2FA
        tfa_buttons = QHBoxLayout()
        
        self.btn_generate_2fa = QPushButton("🔄 Generar 2FA")
        self.btn_generate_2fa.clicked.connect(self.generate_2fa)
        
        self.btn_disable_2fa = QPushButton("❌ Deshabilitar 2FA")
        self.btn_disable_2fa.clicked.connect(self.disable_2fa)
        
        tfa_buttons.addWidget(self.btn_generate_2fa)
        tfa_buttons.addWidget(self.btn_disable_2fa)
        
        # Verificación
        verify_layout = QHBoxLayout()
        self.tfa_code_input = QLineEdit()
        self.tfa_code_input.setPlaceholderText("Código de 6 dígitos")
        self.tfa_code_input.setMaxLength(6)
        
        self.btn_verify_2fa = QPushButton("✅ Verificar")
        self.btn_verify_2fa.clicked.connect(self.verify_2fa)
        
        verify_layout.addWidget(QLabel("Código de verificación:"))
        verify_layout.addWidget(self.tfa_code_input)
        verify_layout.addWidget(self.btn_verify_2fa)
        
        tfa_layout.addWidget(QLabel("1. Código QR:"))
        tfa_layout.addWidget(self.qr_label)
        tfa_layout.addWidget(QLabel("2. Clave manual (alternativa):"))
        tfa_layout.addWidget(self.manual_key_label)
        tfa_layout.addLayout(tfa_buttons)
        tfa_layout.addWidget(QFrame())  # Separador
        tfa_layout.addLayout(verify_layout)
        
        layout.addWidget(self.tfa_config_group)
        layout.addStretch()
        
        return widget
    
    def create_account_security_tab(self) -> QWidget:
        """Crea la pestaña de seguridad de cuenta."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Estado de bloqueo
        lockout_group = QGroupBox("Estado de Bloqueo de Cuenta")
        lockout_layout = QFormLayout(lockout_group)
        
        self.lockout_status = QLabel("Estado: Verificando...")
        self.failed_attempts = QLabel("Intentos fallidos: 0")
        self.lockout_time = QLabel("Bloqueado hasta: N/A")
        
        self.btn_unlock = QPushButton("🔓 Desbloquear Cuenta")
        self.btn_unlock.clicked.connect(self.unlock_account)
        
        lockout_layout.addRow("Estado:", self.lockout_status)
        lockout_layout.addRow("Intentos fallidos:", self.failed_attempts)
        lockout_layout.addRow("Bloqueado hasta:", self.lockout_time)
        lockout_layout.addRow("", self.btn_unlock)
        
        # Configuración de seguridad
        settings_group = QGroupBox("Configuración de Seguridad")
        settings_layout = QFormLayout(settings_group)
        
        self.auto_logout = QCheckBox("Cerrar sesión automáticamente")
        self.auto_logout.setChecked(True)
        
        self.session_timeout = QSpinBox()
        self.session_timeout.setRange(15, 480)  # 15 minutos a 8 horas
        self.session_timeout.setValue(60)
        self.session_timeout.setSuffix(" minutos")
        
        settings_layout.addRow("Logout automático:", self.auto_logout)
        settings_layout.addRow("Timeout de sesión:", self.session_timeout)
        
        layout.addWidget(lockout_group)
        layout.addWidget(settings_group)
        layout.addStretch()
        
        return widget
    
    def create_activity_tab(self) -> QWidget:
        """Crea la pestaña de actividad de seguridad."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Información de actividad
        activity_group = QGroupBox("Actividad Reciente")
        activity_layout = QVBoxLayout(activity_group)
        
        self.activity_info = QTextEdit()
        self.activity_info.setReadOnly(True)
        self.activity_info.setMaximumHeight(200)
        
        activity_layout.addWidget(self.activity_info)
        
        # Dashboard de seguridad
        dashboard_group = QGroupBox("Dashboard de Seguridad del Sistema")
        dashboard_layout = QVBoxLayout(dashboard_group)
        
        self.security_dashboard = QTextEdit()
        self.security_dashboard.setReadOnly(True)
        self.security_dashboard.setMaximumHeight(150)
        
        dashboard_layout.addWidget(self.security_dashboard)
        
        layout.addWidget(activity_group)
        layout.addWidget(dashboard_group)
        layout.addStretch()
        
        return widget
    
    def apply_styles(self):
        """Aplica estilos al diálogo."""
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QPushButton {
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3498db;
                color: white;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
    
    def load_user_security_status(self):
        """Carga el estado actual de seguridad del usuario."""
        try:
            status = self.security_manager.get_user_security_status(self.current_username)
            
            # Actualizar estado de 2FA
            if status.get('2fa_enabled', False):
                self.tfa_status.setText("Estado: ✅ Habilitado")
                self.tfa_status.setStyleSheet("color: green; font-weight: bold;")
                self.tfa_config_group.setEnabled(False)
                self.btn_disable_2fa.setEnabled(True)
            else:
                self.tfa_status.setText("Estado: ❌ Deshabilitado")
                self.tfa_status.setStyleSheet("color: red; font-weight: bold;")
                self.btn_disable_2fa.setEnabled(False)
            
            # Actualizar estado de bloqueo
            if status.get('is_locked', False):
                self.lockout_status.setText("🔒 Bloqueado")
                self.lockout_status.setStyleSheet("color: red; font-weight: bold;")
                locked_until = status.get('locked_until')
                if locked_until:
                    self.lockout_time.setText(f"Hasta: {locked_until.strftime('%H:%M:%S')}")
            else:
                self.lockout_status.setText("🔓 Desbloqueado")
                self.lockout_status.setStyleSheet("color: green; font-weight: bold;")
                self.btn_unlock.setEnabled(False)
            
            self.failed_attempts.setText(f"Intentos fallidos: {status.get('failed_attempts', 0)}")
            
            # Información de actividad
            activity_text = f"""
Último login: {status.get('last_login', 'Nunca')}
IP del último login: {status.get('last_login_ip', 'Desconocida')}
Cuenta creada: {status.get('account_created', 'Desconocida')}
Estado de cuenta: {status.get('account_status', 'activo')}
            """.strip()
            
            self.activity_info.setPlainText(activity_text)
            
            # Dashboard de seguridad
            dashboard = self.security_manager.get_security_dashboard()
            dashboard_text = f"""
Total usuarios: {dashboard.get('total_users', 0)}
Usuarios bloqueados: {dashboard.get('locked_users', 0)}
Usuarios con 2FA: {dashboard.get('users_with_2fa', 0)}
Tasa adopción 2FA: {dashboard.get('2fa_adoption_rate', 0):.1f}%
Intentos fallidos recientes: {dashboard.get('recent_failed_attempts', 0)}
            """.strip()
            
            self.security_dashboard.setPlainText(dashboard_text)
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error cargando estado de seguridad: {e}")
    
    def validate_password_strength(self):
        """Valida la fortaleza de la contraseña en tiempo real."""
        password = self.new_password.text()
        if not password:
            self.password_strength.setValue(0)
            self.strength_label.setText("Fortaleza: No evaluada")
            self.strength_requirements.clear()
            return
        
        result = self.security_manager.validate_password_strength(password)
        
        # Actualizar barra de progreso
        self.password_strength.setValue(result['score'])
        
        # Actualizar etiqueta de fortaleza
        strength = result['strength']
        color_map = {
            'Muy débil': 'red',
            'Débil': 'orange', 
            'Media': 'yellow',
            'Fuerte': 'green'
        }
        color = color_map.get(strength, 'gray')
        self.strength_label.setText(f"Fortaleza: {strength}")
        self.strength_label.setStyleSheet(f"color: {color}; font-weight: bold;")
        
        # Actualizar requisitos
        if result['issues']:
            requirements_text = "Requisitos faltantes:\n• " + "\n• ".join(result['issues'])
        else:
            requirements_text = "✅ Todos los requisitos cumplidos"
        
        self.strength_requirements.setPlainText(requirements_text)
    
    def generate_2fa(self):
        """Genera nueva configuración 2FA."""
        try:
            result = self.security_manager.setup_2fa(self.current_username)
            
            if result['success']:
                # Mostrar QR code
                qr_data = base64.b64decode(result['qr_code'])
                pixmap = QPixmap()
                pixmap.loadFromData(qr_data)
                
                scaled_pixmap = pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                self.qr_label.setPixmap(scaled_pixmap)
                
                # Mostrar clave manual
                self.manual_key_label.setText(f"Clave manual: {result['manual_entry_key']}")
                
                # Habilitar verificación
                self.tfa_config_group.setEnabled(True)
                self.btn_verify_2fa.setEnabled(True)
                
                QMessageBox.information(
                    self, 
                    "2FA Generado", 
                    "Configuración 2FA generada. Escanee el código QR y verifique con un código."
                )
            else:
                QMessageBox.warning(self, "Error", f"Error generando 2FA: {result.get('error', 'Error desconocido')}")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error generando 2FA: {e}")
    
    def verify_2fa(self):
        """Verifica la configuración 2FA."""
        code = self.tfa_code_input.text().strip()
        if len(code) != 6:
            QMessageBox.warning(self, "Error", "Ingrese un código de 6 dígitos")
            return
        
        try:
            success = self.security_manager.verify_2fa_setup(self.current_username, code)
            
            if success:
                QMessageBox.information(
                    self, 
                    "2FA Habilitado", 
                    "✅ Two-Factor Authentication habilitado exitosamente"
                )
                self.security_updated.emit(self.current_username, "2FA_ENABLED")
                self.load_user_security_status()  # Recargar estado
            else:
                QMessageBox.warning(self, "Error", "Código incorrecto. Verifique e intente nuevamente.")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error verificando 2FA: {e}")
    
    def disable_2fa(self):
        """Deshabilita 2FA."""
        reply = QMessageBox.question(
            self,
            "Confirmar",
            "¿Está seguro de que desea deshabilitar Two-Factor Authentication?\n\nEsto reducirá la seguridad de su cuenta.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                success = self.security_manager.disable_2fa(self.current_username)
                
                if success:
                    QMessageBox.information(self, "2FA Deshabilitado", "Two-Factor Authentication deshabilitado")
                    self.security_updated.emit(self.current_username, "2FA_DISABLED")
                    self.load_user_security_status()
                else:
                    QMessageBox.warning(self, "Error", "Error deshabilitando 2FA")
                    
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error deshabilitando 2FA: {e}")
    
    def unlock_account(self):
        """Desbloquea la cuenta del usuario."""
        reply = QMessageBox.question(
            self,
            "Confirmar",
            "¿Desbloquear cuenta manualmente?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                success = self.security_manager.unlock_user(self.current_username)
                
                if success:
                    QMessageBox.information(self, "Cuenta Desbloqueada", "Cuenta desbloqueada exitosamente")
                    self.security_updated.emit(self.current_username, "ACCOUNT_UNLOCKED")
                    self.load_user_security_status()
                else:
                    QMessageBox.warning(self, "Error", "Error desbloqueando cuenta")
                    
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error desbloqueando cuenta: {e}")
    
    def save_changes(self):
        """Guarda los cambios de configuración."""
        try:
            changes_made = False
            
            # Cambio de contraseña
            if self.new_password.text():
                if not self.current_password.text():
                    QMessageBox.warning(self, "Error", "Ingrese su contraseña actual")
                    return
                
                if self.new_password.text() != self.confirm_password.text():
                    QMessageBox.warning(self, "Error", "Las contraseñas no coinciden")
                    return
                
                # Validar contraseña actual
                if not self.usuarios_model.validar_usuario(self.current_username, self.current_password.text()):
                    QMessageBox.warning(self, "Error", "Contraseña actual incorrecta")
                    return
                
                # Validar fortaleza de nueva contraseña
                result = self.security_manager.validate_password_strength(self.new_password.text())
                if not result['valid']:
                    QMessageBox.warning(
                        self, 
                        "Contraseña Débil", 
                        "La contraseña no cumple los requisitos de seguridad:\n• " + "\n• ".join(result['issues'])
                    )
                    return
                
                # Cambiar contraseña
                if hasattr(self.usuarios_model, 'cambiar_password'):
                    success = self.usuarios_model.cambiar_password(self.current_username, self.new_password.text())
                    if success:
                        changes_made = True
                        self.security_updated.emit(self.current_username, "PASSWORD_CHANGED")
                    else:
                        QMessageBox.warning(self, "Error", "Error cambiando contraseña")
                        return
            
            if changes_made:
                QMessageBox.information(self, "Éxito", "Configuración de seguridad actualizada")
            
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error guardando cambios: {e}")


def show_security_config(usuarios_model, username: str, parent=None) -> bool:
    """
    Muestra el diálogo de configuración de seguridad.
    
    Returns:
        bool: True si se realizaron cambios
    """
    dialog = SecurityConfigDialog(usuarios_model, username, parent)
    return dialog.exec() == QDialog.DialogCode.Accepted


if __name__ == "__main__":
    # Test del diálogo
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # Mock del modelo de usuarios para testing
    class MockUsuariosModel:
        def obtener_usuario_por_nombre(self, username):
            return {
                'id': 1,
                'username': username,
                'configuracion_personal': '{}',
                'ultimo_login': '2025-01-01 10:00:00',
                'fecha_creacion': '2024-12-01'
            }
        
        def obtener_todos_usuarios(self):
            return [{'id': 1, 'username': 'admin'}]
    
    dialog = SecurityConfigDialog(MockUsuariosModel(), "admin")
    dialog.show()
    
    sys.exit(app.exec())