"""
Rexus.app - Diálogo de Login

Implementación del diálogo de autenticación de usuarios.
Maneja el login visual y la validación de credenciales.
"""

import sys
from typing import Optional, Callable
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QMessageBox, QCheckBox, QProgressBar
)
from PyQt6.QtGui import QFont, QIcon, QPixmap

from rexus.core.database import UsersDatabaseConnection
from rexus.utils.app_logger import log_info, log_error, log_security

class LoginDialog(QDialog):
    """
    Diálogo de login para autenticación de usuarios.
    Implementa la interfaz visual y lógica de autenticación.
    """

    def __init__(self, security_manager=None, parent=None):
        super().__init__(parent)
        self.user_data = None
        self.auth_callback = None
        self.db_connection = None
        self.security_manager = security_manager

        self._setup_ui()
        self._setup_connections()
        self._load_styles()

    def _setup_ui(self):
        """Configura la interfaz de usuario del diálogo de login."""
        self.setWindowTitle("Rexus.app - Iniciar Sesión")
        self.setFixedSize(400, 500)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)

        # Layout principal
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Logo/Título
        title_frame = QFrame()
        title_layout = QVBoxLayout(title_frame)

        title_label = QLabel("Rexus.app")
        title_font = QFont("Arial", 24, QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")

        subtitle_label = QLabel("Sistema de Gestión Empresarial")
        subtitle_font = QFont("Arial", 10)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("color: #7f8c8d;")

        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)
        layout.addWidget(title_frame)

        # Formulario de login
        form_frame = QFrame()
        form_layout = QVBoxLayout(form_frame)
        form_layout.setSpacing(15)

        # Campo Usuario
        user_frame = QFrame()
        user_layout = QVBoxLayout(user_frame)
        user_layout.setContentsMargins(0, 0, 0, 0)

        user_label = QLabel("Usuario:")
        user_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Ingrese su nombre de usuario")
        self.user_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)

        user_layout.addWidget(user_label)
        user_layout.addWidget(self.user_input)
        form_layout.addWidget(user_frame)

        # Campo Contraseña
        pass_frame = QFrame()
        pass_layout = QVBoxLayout(pass_frame)
        pass_layout.setContentsMargins(0, 0, 0, 0)

        pass_label = QLabel("Contraseña:")
        pass_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Ingrese su contraseña")
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pass_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)

        pass_layout.addWidget(pass_label)
        pass_layout.addWidget(self.pass_input)
        form_layout.addWidget(pass_frame)

        # Checkbox recordar usuario
        self.remember_check = QCheckBox("Recordar usuario")
        self.remember_check.setStyleSheet("color: #7f8c8d;")
        form_layout.addWidget(self.remember_check)

        layout.addWidget(form_frame)

        # Barra de progreso (oculta inicialmente)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #3498db;
            }
        """)
        layout.addWidget(self.progress_bar)

        # Botones
        buttons_frame = QFrame()
        buttons_layout = QHBoxLayout(buttons_frame)

        self.login_btn = QPushButton("Iniciar Sesión")
        self.login_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)

        self.cancel_btn = QPushButton("Cancelar")
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)

        buttons_layout.addWidget(self.cancel_btn)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.login_btn)

        layout.addWidget(buttons_frame)

        # Status label
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #e74c3c; font-size: 12px;")
        self.status_label.setVisible(False)
        layout.addWidget(self.status_label)

    def _validate_user_with_real_tables(self, username: str, password: str, sql_manager):
        """
        Valida usuario usando tablas reales de usuarios y permisos.
        
        Args:
            username: Nombre de usuario
            password: Contraseña en texto plano
            sql_manager: Manejador de consultas SQL
            
        Returns:
            dict con datos del usuario y permisos o None si falla
        """
        try:
            # 1. Obtener usuario de la tabla real
            user_result = sql_manager.ejecutar_consulta_archivo(
                'sql/09_usuarios/autenticar_usuario.sql',
                (username,)
            )
            
            if not user_result:
                log_security("LOGIN_FAILED", f"Usuario {username} no encontrado", username)
                return None
            
            user_row = user_result[0] if isinstance(user_result, list) else user_result
            stored_password_hash = user_row.get('password_hash', '')
            
            # 2. Verificar contraseña con múltiples algoritmos soportados
            password_valid = self._verify_password(password, stored_password_hash)
            
            if not password_valid:
                # Incrementar intentos fallidos
                self._increment_failed_attempts(user_row['id'], sql_manager)
                log_security("LOGIN_FAILED", f"Contraseña incorrecta para usuario {username}", username)
                return None
            
            # 3. Verificar estado del usuario
            if user_row.get('estado') not in ['ACTIVO', 'PRIMERA_VEZ']:
                log_security("LOGIN_FAILED", f"Usuario {username} inactivo o bloqueado", username)
                return None
            
            # 4. Obtener permisos del usuario
            permisos = self._get_user_permissions(user_row['id'], user_row['rol'], sql_manager)
            
            # 5. Actualizar último acceso y resetear intentos fallidos
            self._update_last_access(user_row['id'], sql_manager)
            
            # 6. Preparar datos del usuario completos
            user_data = {
                'id': user_row['id'],
                'usuario': user_row['usuario'],
                'nombre_completo': user_row.get('nombre_completo', ''),
                'email': user_row.get('email', ''),
                'telefono': user_row.get('telefono', ''),
                'rol': user_row['rol'],
                'estado': user_row['estado'],
                'ultimo_acceso': user_row.get('ultimo_acceso'),
                'permisos': permisos,
                'modulos_permitidos': permisos  # Compatibilidad
            }
            
            log_security("LOGIN_SUCCESS", f"Usuario {username} autenticado con {len(permisos)} permisos", username)
            return user_data
            
        except Exception as e:
            log_error(f"Error en validación de usuario {username}: {str(e)}")
            return None
    
    def _verify_password(self, plain_password: str, stored_hash: str) -> bool:
        """
        Verifica contraseña usando múltiples algoritmos soportados.
        
        Args:
            plain_password: Contraseña en texto plano
            stored_hash: Hash almacenado en BD
            
        Returns:
            bool: True si la contraseña es correcta
        """
        import hashlib
        import bcrypt
        
        if not stored_hash:
            return False
        
        try:
            # 1. Verificar bcrypt (preferido)
            if stored_hash.startswith('$2b$') or stored_hash.startswith('$2a$'):
                return bcrypt.checkpw(plain_password.encode('utf-8'), stored_hash.encode('utf-8'))
            
            # 2. Verificar SHA-256 (legacy)
            sha256_hash = hashlib.sha256(plain_password.encode()).hexdigest()
            if stored_hash == sha256_hash:
                return True
            
            # 3. Verificar MD5 (legacy - deprecado)
            md5_hash = hashlib.md5(plain_password.encode()).hexdigest()
            if stored_hash == md5_hash:
                return True
            
            # 4. Verificar texto plano (solo para migración - INSEGURO)
            if stored_hash == plain_password:
                log_security("LOGIN_WARNING", f"Usuario usando contraseña en texto plano - MIGRAR URGENTE", "system")
                return True
                
            return False
            
        except Exception as e:
            log_error(f"Error verificando contraseña: {str(e)}")
            return False
    
    def _get_user_permissions(self, user_id: int, user_role: str, sql_manager) -> list:
        """
        Obtiene permisos del usuario desde tabla permisos_usuario o por rol.
        
        Args:
            user_id: ID del usuario
            user_role: Rol del usuario
            sql_manager: Manejador SQL
            
        Returns:
            list: Lista de módulos permitidos
        """
        try:
            # 1. Intentar obtener permisos específicos de la tabla
            permisos_result = sql_manager.ejecutar_consulta_archivo(
                'sql/09_usuarios/obtener_permisos_usuario.sql',
                (user_id,)
            )
            
            if permisos_result:
                # Convertir resultado a lista de strings
                permisos_list = [row.get('modulo') for row in permisos_result if row.get('modulo')]
                if permisos_list:
                    return permisos_list
            
            # 2. Fallback: Asignar permisos por rol
            return self._get_permissions_by_role(user_role)
            
        except Exception as e:
            log_error(f"Error obteniendo permisos para usuario {user_id}: {str(e)}")
            # Fallback seguro: permisos mínimos
            return self._get_permissions_by_role('USUARIO')
    
    def _get_permissions_by_role(self, role: str) -> list:
        """
        Obtiene permisos predeterminados por rol.
        
        Args:
            role: Rol del usuario
            
        Returns:
            list: Módulos permitidos por rol
        """
        role_permissions = {
            'ADMINISTRADOR': [
                'usuarios', 'inventario', 'pedidos', 'compras', 'vidrios', 'herrajes',
                'obras', 'logistica', 'mantenimiento', 'configuracion', 'auditoria',
                'administracion', 'notificaciones'
            ],
            'SUPERVISOR': [
                'inventario', 'pedidos', 'compras', 'vidrios', 'herrajes',
                'obras', 'logistica', 'mantenimiento', 'notificaciones'
            ],
            'VENDEDOR': [
                'pedidos', 'vidrios', 'herrajes', 'inventario'
            ],
            'USUARIO': [
                'inventario', 'pedidos', 'vidrios'
            ]
        }
        
        return role_permissions.get(role.upper(), role_permissions['USUARIO'])
    
    def _increment_failed_attempts(self, user_id: int, sql_manager):
        """Incrementa contador de intentos fallidos."""
        try:
            sql_manager.ejecutar_consulta_archivo(
                'sql/09_usuarios/incrementar_intentos_fallidos.sql',
                (user_id,)
            )
        except Exception as e:
            log_error(f"Error incrementando intentos fallidos: {str(e)}")
    
    def _update_last_access(self, user_id: int, sql_manager):
        """Actualiza último acceso y resetea intentos fallidos."""
        try:
            # Actualizar último acceso
            sql_manager.ejecutar_consulta_archivo(
                'sql/09_usuarios/actualizar_ultimo_acceso.sql',
                (user_id,)
            )
            
            # Resetear intentos fallidos
            sql_manager.ejecutar_consulta_archivo(
                'sql/09_usuarios/resetear_intentos_fallidos.sql',
                (user_id,)
            )
        except Exception as e:
            log_error(f"Error actualizando último acceso: {str(e)}")

    def get_modulos_permitidos(self) -> list:
        """
        Retorna lista de módulos permitidos para el usuario autenticado.
        
        Returns:
            list: Lista de módulos permitidos
        """
        if self.user_data and 'permisos' in self.user_data:
            return self.user_data['permisos']
        return []

    def _setup_connections(self):
        """Configura las conexiones de señales."""
        self.login_btn.clicked.connect(self._handle_login)
        self.cancel_btn.clicked.connect(self.reject)
        self.user_input.returnPressed.connect(self._handle_login)
        self.pass_input.returnPressed.connect(self._handle_login)

    def _load_styles(self):
        """Carga los estilos adicionales."""
        self.setStyleSheet("""
            QDialog {
                background-color: #ecf0f1;
            }
            QFrame {
                background-color: transparent;
            }
        """)

    def _handle_login(self):
        """Maneja el proceso de login."""
        username = self.user_input.text().strip()
        password = self.pass_input.text()

        if not username or not password:
            self._show_error("Por favor ingrese usuario y contraseña")
            return

        # Mostrar progreso
        self._set_loading_state(True)
        self.status_label.setVisible(False)

        # Procesar login en el siguiente ciclo de eventos
        QTimer.singleShot(100, lambda: self._process_login(username, password))

    def _process_login(self, username: str, password: str):
        """Procesa la autenticación del usuario."""
        try:
            # Importar aquí para evitar problemas de inicialización
            from rexus.core.database import UsersDatabaseConnection
            from rexus.utils.sql_query_manager import SQLQueryManager
            import hashlib
            import bcrypt

            # Conectar a la base de datos
            db = UsersDatabaseConnection()
            sql_manager = SQLQueryManager()

            # NUEVA LÓGICA: Validar credenciales usando SQL externo y tablas reales
            user_data = self._validate_user_with_real_tables(username, password, sql_manager)

            if user_data:
                log_security("LOGIN_SUCCESS", f"Usuario {username} autenticado correctamente", username)
                self.user_data = user_data
                self._set_loading_state(False)
                self.accept()
            else:
                log_security("LOGIN_FAILED", f"Intento de login fallido para usuario {username}", username)
                self._show_error("Usuario o contraseña incorrectos")
                self._set_loading_state(False)

        except Exception as e:
            log_error(f"Error durante login: {str(e)}")
            self._show_error("Error de conexión. Intente nuevamente.")
            self._set_loading_state(False)

    def _set_loading_state(self, loading: bool):
        """Cambia el estado de carga del diálogo."""
        self.login_btn.setEnabled(not loading)
        self.cancel_btn.setEnabled(not loading)
        self.user_input.setEnabled(not loading)
        self.pass_input.setEnabled(not loading)
        self.progress_bar.setVisible(loading)

        if loading:
            self.progress_bar.setRange(0, 0)  # Indeterminado
            self.login_btn.setText("Iniciando sesión...")
        else:
            self.progress_bar.setRange(0, 100)
            self.login_btn.setText("Iniciar Sesión")

    def _show_error(self, message: str):
        """Muestra un mensaje de error."""
        self.status_label.setText(message)
        self.status_label.setVisible(True)
        self.status_label.setStyleSheet("color: #e74c3c; font-size: 12px;")

    def get_user_data(self) -> Optional[dict]:
        """Obtiene los datos del usuario autenticado."""
        return self.user_data

    def set_auth_callback(self, callback: Callable):
        """Establece una función de callback para la autenticación."""
        self.auth_callback = callback

    @staticmethod
    def show_login_dialog(parent=None) -> Optional[dict]:
        """
        Método estático para mostrar el diálogo de login.

        Returns:
            Datos del usuario si la autenticación fue exitosa, None en caso contrario
        """
        dialog = LoginDialog(parent)
        result = dialog.exec()

        if result == QDialog.DialogCode.Accepted:
            return dialog.get_user_data()
        return None
