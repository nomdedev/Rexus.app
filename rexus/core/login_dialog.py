"""
Rexus.app - DiÃ¡logo de Login

ImplementaciÃ³n del diÃ¡logo de autenticaciÃ³n de usuarios.
Maneja el login visual y la validaciÃ³n de credenciales.
"""

from typing import Optional, Callable
from PyQt6.QtCore import Qt
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QDialog
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout
from PyQt6.QtWidgets import QLabel, QLineEdit
from PyQt6.QtWidgets import QPushButton, QFrame
from PyQt6.QtWidgets import QCheckBox, QProgressBar
from PyQt6.QtGui import QFont

from rexus.utils.app_logger import log_error, log_security


class LoginDialog(QDialog):
    """
    DiÃ¡logo de login para autenticaciÃ³n de usuarios.
    Implementa la interfaz visual y lÃ³gica de autenticaciÃ³n.
    """

    class UIComponents:
        """Clase interna para agrupar componentes de UI."""
        def __init__(self):
            self.user_input: Optional[QLineEdit] = None
            self.pass_input: Optional[QLineEdit] = None
            self.login_btn: Optional[QPushButton] = None
            self.cancel_btn: Optional[QPushButton] = None
            self.remember_check: Optional[QCheckBox] = None
            self.status_label: Optional[QLabel] = None
            self.progress_bar: Optional[QProgressBar] = None

    def __init__(self, security_manager=None, parent=None):
        super().__init__(parent)
        self.user_data = None
        self.auth_callback = None
        self.db_connection = None
        self.security_manager = security_manager
        self.ui = self.UIComponents()  # Agrupar componentes UI

        self._setup_ui()
        self._setup_connections()
        self._load_styles()

    def _setup_ui(self):
        """Configura la interfaz de usuario del diÃ¡logo de login."""
        self.setWindowTitle("Rexus.app - Iniciar SesiÃ³n")
        self.setFixedSize(400, 500)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)

        # Layout principal
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Logo/TÃ­tulo
        title_frame = QFrame()
        title_layout = QVBoxLayout(title_frame)

        title_label = QLabel("Rexus.app")
        title_font = QFont("Arial", 24, QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")

        subtitle_label = QLabel("Sistema de GestiÃ³n Empresarial")
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
        self.ui.user_input = QLineEdit()
        self.ui.user_input.setPlaceholderText("Ingrese su nombre de usuario")
        self.ui.user_input.setStyleSheet("""
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
        user_layout.addWidget(self.ui.user_input)
        form_layout.addWidget(user_frame)

        # Campo ContraseÃ±a
        pass_frame = QFrame()
        pass_layout = QVBoxLayout(pass_frame)
        pass_layout.setContentsMargins(0, 0, 0, 0)

        pass_label = QLabel("ContraseÃ±a:")
        pass_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        self.ui.pass_input = QLineEdit()
        self.ui.pass_input.setPlaceholderText("Ingrese su contraseÃ±a")
        self.ui.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.ui.pass_input.setStyleSheet("""
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
        pass_layout.addWidget(self.ui.pass_input)
        form_layout.addWidget(pass_frame)

        # Checkbox recordar usuario
        self.ui.remember_check = QCheckBox("Recordar usuario")
        self.ui.remember_check.setStyleSheet("color: #7f8c8d;")
        form_layout.addWidget(self.ui.remember_check)

        layout.addWidget(form_frame)

        # Barra de progreso (oculta inicialmente)
        self.ui.progress_bar = QProgressBar()
        self.ui.progress_bar.setVisible(False)
        self.ui.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #3498db;
            }
        """)
        layout.addWidget(self.ui.progress_bar)

        # Botones
        buttons_frame = QFrame()
        buttons_layout = QHBoxLayout(buttons_frame)

        self.ui.login_btn = QPushButton("Iniciar SesiÃ³n")
        self.ui.login_btn.setStyleSheet("""
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

        self.ui.cancel_btn = QPushButton("Cancelar")
        self.ui.cancel_btn.setStyleSheet("""
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

        buttons_layout.addWidget(self.ui.cancel_btn)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.ui.login_btn)

        layout.addWidget(buttons_frame)

        # Status label
        self.ui.status_label = QLabel("")
        self.ui.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.ui.status_label.setStyleSheet("color: #e74c3c; font-size: 12px;")
        self.ui.status_label.setVisible(False)
        layout.addWidget(self.ui.status_label)

    def _validate_user_with_real_tables(self, username: str, password: str, sql_manager):
        """
        Valida usuario usando tablas reales de usuarios y permisos.

        Args:
            username: Nombre de usuario
            password: ContraseÃ±a en texto plano
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

            # 2. Verificar contraseÃ±a con mÃºltiples algoritmos soportados
            password_valid = self._verify_password(password, stored_password_hash)

            if not password_valid:
                # Incrementar intentos fallidos
                self._increment_failed_attempts(user_row['id'], sql_manager)
                log_security("LOGIN_FAILED",
                             f"ContraseÃ±a incorrecta para usuario {username}",
                             username)
                return None

            # 3. Verificar estado del usuario
            if user_row.get('estado') not in ['ACTIVO', 'PRIMERA_VEZ']:
                log_security("LOGIN_FAILED", f"Usuario {username} inactivo o bloqueado", username)
                return None

            # 4. Obtener permisos del usuario
            permisos = self._get_user_permissions(user_row['id'], user_row['rol'], sql_manager)

            # 5. Actualizar Ãºltimo acceso y resetear intentos fallidos
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

            log_security("LOGIN_SUCCESS",
                         f"Usuario {username} autenticado con {len(permisos)} permisos",
                         username)
            return user_data

        except Exception as e:
            log_error(f"Error en validaciÃ³n de usuario {username}: {str(e)}")
            return None

    def _verify_password(self, plain_password: str, stored_hash: str) -> bool:
        """
        Verifica contraseÃ±a usando mÃºltiples algoritmos soportados.

        Args:
            plain_password: ContraseÃ±a en texto plano
            stored_hash: Hash almacenado en BD

        Returns:
            bool: True si la contraseÃ±a es correcta
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
            md5_hash = hashlib.md5(plain_password.encode(), usedforsecurity=False).hexdigest()
            if stored_hash == md5_hash:
                return True

            # 4. Verificar texto plano (solo para migraciÃ³n - INSEGURO)
            if stored_hash == plain_password:
                log_security("LOGIN_WARNING", "Usuario usando contraseÃ±a en texto plano - MIGRAR URGENTE", "system")
                return True

            return False

        except Exception as e:
            log_error(f"Error verificando contraseÃ±a: {str(e)}")
            return False

    def _get_user_permissions(self, user_id: int, user_role: str, sql_manager) -> list:
        """
        Obtiene permisos del usuario desde tabla permisos_usuario o por rol.

        Args:
            user_id: ID del usuario
            user_role: Rol del usuario
            sql_manager: Manejador SQL

        Returns:
            list: Lista de mÃ³dulos permitidos
        """
        try:
            # 1. Intentar obtener permisos especÃ­ficos de la tabla
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
            # Fallback seguro: permisos mÃ­nimos
            return self._get_permissions_by_role('USUARIO')

    def _get_permissions_by_role(self, role: str) -> list:
        """
        Obtiene permisos predeterminados por rol.

        Args:
            role: Rol del usuario

        Returns:
            list: MÃ³dulos permitidos por rol
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
        """Actualiza Ãºltimo acceso y resetea intentos fallidos."""
        try:
            # Actualizar Ãºltimo acceso
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
            log_error(f"Error actualizando Ãºltimo acceso: {str(e)}")

    def get_modulos_permitidos(self) -> list:
        """
        Retorna lista de mÃ³dulos permitidos para el usuario autenticado.

        Returns:
            list: Lista de mÃ³dulos permitidos
        """
        if self.user_data and 'permisos' in self.user_data:
            return self.user_data['permisos']
        return []

    def _setup_connections(self):
        """Configura las conexiones de seÃ±ales."""
        self.ui.login_btn.clicked.connect(self._handle_login)
        self.ui.cancel_btn.clicked.connect(self.reject)
        self.ui.user_input.returnPressed.connect(self._handle_login)
        self.ui.pass_input.returnPressed.connect(self._handle_login)

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
        username = self.ui.user_input.text().strip()
        password = self.ui.pass_input.text()

        if not username or not password:
            self._show_error("Por favor ingrese usuario y contraseÃ±a")
            return

        # Mostrar progreso
        self._set_loading_state(True)
        self.ui.status_label.setVisible(False)

        # Procesar login en el siguiente ciclo de eventos
        QTimer.singleShot(100, lambda: self._process_login(username, password))

    def _process_login(self, username: str, password: str):
        """Procesa la autenticaciÃ³n del usuario."""
        try:
            # Importar aquÃ­ para evitar problemas de inicializaciÃ³n
            from rexus.utils.sql_query_manager import SQLQueryManager

            # Conectar a la base de datos
            sql_manager = SQLQueryManager()

            # NUEVA LÃ“GICA: Validar credenciales usando SQL externo y tablas reales
            user_data = self._validate_user_with_real_tables(username, password, sql_manager)

            if user_data:
                log_security("LOGIN_SUCCESS",
                             f"Usuario {username} autenticado correctamente",
                             username)
                self.user_data = user_data
                self._set_loading_state(False)
                self.accept()
            else:
                log_security("LOGIN_FAILED",
                             f"Intento de login fallido para usuario {username}",
                             username)
                self._show_error("Usuario o contraseÃ±a incorrectos")
                self._set_loading_state(False)

        except Exception as e:
            log_error(f"Error durante login: {str(e)}")
            self._show_error("Error de conexiÃ³n. Intente nuevamente.")
            self._set_loading_state(False)

    def _set_loading_state(self, loading: bool):
        """Cambia el estado de carga del diÃ¡logo."""
        self.ui.login_btn.setEnabled(not loading)
        self.ui.cancel_btn.setEnabled(not loading)
        self.ui.user_input.setEnabled(not loading)
        self.ui.pass_input.setEnabled(not loading)
        self.ui.progress_bar.setVisible(loading)

        if loading:
            self.ui.progress_bar.setRange(0, 0)  # Indeterminado
            self.ui.login_btn.setText("Iniciando sesiÃ³n...")
        else:
            self.ui.progress_bar.setRange(0, 100)
            self.ui.login_btn.setText("Iniciar SesiÃ³n")

    def _show_error(self, message: str):
        """Muestra un mensaje de error."""
        self.ui.status_label.setText(message)
        self.ui.status_label.setVisible(True)
        self.ui.status_label.setStyleSheet("color: #e74c3c; font-size: 12px;")

    def get_user_data(self) -> Optional[dict]:
        """Obtiene los datos del usuario autenticado."""
        return self.user_data

    def set_auth_callback(self, callback: Callable):
        """Establece una funciÃ³n de callback para la autenticaciÃ³n."""
        self.auth_callback = callback

    @staticmethod
    def show_login_dialog(parent=None) -> Optional[dict]:
        """
        MÃ©todo estÃ¡tico para mostrar el diÃ¡logo de login.

        Returns:
            Datos del usuario si la autenticaciÃ³n fue exitosa, None en caso contrario
        """
        dialog = LoginDialog(parent)
        result = dialog.exec()

        if result == QDialog.DialogCode.Accepted:
            return dialog.get_user_data()
        return None
