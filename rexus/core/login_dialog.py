"""
Rexus.app - Diálogo de Login

Implementación del diálogo de autenticación de usuarios.
Maneja el login visual y la validación de credenciales.
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
    Diálogo de login para autenticación de usuarios.
    Implementa la interfaz visual y lógica de autenticación.
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
        title_frame.setObjectName("title_frame")
        title_layout = QVBoxLayout(title_frame)

        title_label = QLabel("Rexus.app")
        title_label.setObjectName("title_label")
        title_font = QFont("Arial", 24, QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")

        subtitle_label = QLabel("Sistema de Gestión Empresarial")
        subtitle_label.setObjectName("subtitle_label")
        subtitle_font = QFont("Arial", 10)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("color: #7f8c8d;")

        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)

        layout.addWidget(title_frame)
        form_frame = QFrame()
        form_frame.setObjectName("form_frame")
        form_layout = QVBoxLayout(form_frame)
        form_layout.setSpacing(15)

        # Campo Usuario
        user_frame = QFrame()
        user_layout = QVBoxLayout(user_frame)
        user_layout.setContentsMargins(0, 0, 0, 0)

        user_label = QLabel("Usuario:")
        user_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        self.ui.user_input = QLineEdit()
        self.ui.user_input.setObjectName("user_input")
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

        # Campo Contraseña
        pass_frame = QFrame()
        pass_layout = QVBoxLayout(pass_frame)
        pass_layout.setContentsMargins(0, 0, 0, 0)

        pass_label = QLabel("Contraseña:")
        pass_label.setStyleSheet("font-weight: bold; color: #2c3c50;")
        self.ui.pass_input = QLineEdit()
        self.ui.pass_input.setObjectName("pass_input")
        self.ui.pass_input.setPlaceholderText("Ingrese su contraseña")
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
        self.ui.remember_check.setObjectName("remember_check")
        self.ui.remember_check.setStyleSheet("color: #7f8c8d;")
        form_layout.addWidget(self.ui.remember_check)

        layout.addWidget(form_frame)

        # Barra de progreso (oculta inicialmente)
        self.ui.progress_bar = QProgressBar()
        self.ui.progress_bar.setObjectName("progress_bar")
        self.ui.progress_bar.setVisible(False)
        self.ui.progress_bar.setFixedHeight(8)
        self.ui.progress_bar.setStyleSheet("""
            QProgressBar { border-radius: 6px; background: #e6e9ec; }
            QProgressBar::chunk { background: #3498db; }
        """)
        layout.addWidget(self.ui.progress_bar)

        # Botones
        buttons_frame = QFrame()
        buttons_layout = QHBoxLayout(buttons_frame)

        self.ui.cancel_btn = QPushButton("Cancelar")
        self.ui.cancel_btn.setObjectName("cancel_btn")
        self.ui.cancel_btn.setStyleSheet("""
            QPushButton { background-color: transparent; color: #e74c3c; padding: 8px 14px; border-radius: 8px; }
            QPushButton:hover { background-color: rgba(231,76,60,0.06); }
        """)

        self.ui.login_btn = QPushButton("Iniciar Sesión")
        self.ui.login_btn.setObjectName("login_btn")
        self.ui.login_btn.setStyleSheet("""
            QPushButton { background-color: #2d98da; color: white; padding: 8px 16px; border-radius: 8px; font-weight: 600; }
            QPushButton:hover { background-color: #247fb3; }
        """)

        buttons_layout.addWidget(self.ui.cancel_btn)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.ui.login_btn)

        layout.addWidget(buttons_frame)

        # Status label
        self.ui.status_label = QLabel("")
        self.ui.status_label.setObjectName("status_label")
        self.ui.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.ui.status_label.setStyleSheet("color: #e74c3c; font-size: 12px;")
        self.ui.status_label.setVisible(False)
        layout.addWidget(self.ui.status_label)

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
            permisos_result = sql_manager.ejecutar_consulta_archivo(
                'sql/09_usuarios/obtener_permisos_usuario.sql',
                (user_id,)
            )

            if permisos_result:
                permisos_list = [row[0] for row in permisos_result if row[0]]  # modulo es la primera columna
                if permisos_list:
                    return permisos_list

            return self._get_permissions_by_role(user_role)

        except Exception as e:
            log_error(f"Error obteniendo permisos para usuario {user_id}: {str(e)}")
            return self._get_permissions_by_role('USUARIO')

    def _get_permissions_by_role(self, role: str) -> list:
        """
        Obtiene permisos predeterminados por rol.
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
            sql_manager.execute_non_query("""
                UPDATE usuarios SET
                    intentos_fallidos = intentos_fallidos + 1,
                    bloqueado_hasta = CASE
                        WHEN intentos_fallidos + 1 >= 5
                        THEN DATEADD(MINUTE, 30, GETDATE())
                        ELSE bloqueado_hasta
                    END,
                    fecha_modificacion = GETDATE()
                WHERE id = ?
            """, (user_id,))
        except Exception as e:
            log_error(f"Error incrementando intentos fallidos: {str(e)}")

    def _update_last_access(self, user_id: int, sql_manager):
        """Actualiza último acceso y resetea intentos fallidos."""
        try:
            # Usar UPDATE directo en lugar de archivo SQL
            sql_manager.execute_non_query("""
                UPDATE usuarios SET 
                    intentos_fallidos = 0,
                    ultimo_acceso = GETDATE(),
                    fecha_modificacion = GETDATE()
                WHERE id = ?
            """, (user_id,))
        except Exception as e:
            log_error(f"Error actualizando último acceso: {str(e)}")

    def _setup_connections(self):
        """Configura las conexiones de señales."""
        if self.ui.login_btn:
            self.ui.login_btn.clicked.connect(self._handle_login)
        if self.ui.cancel_btn:
            self.ui.cancel_btn.clicked.connect(self.reject)
        if self.ui.user_input:
            self.ui.user_input.returnPressed.connect(self._handle_login)
        if self.ui.pass_input:
            self.ui.pass_input.returnPressed.connect(self._handle_login)

    def _load_styles(self):
        """Carga los estilos adicionales."""
        self.setStyleSheet("""
            QDialog { background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #f7f9fa, stop:1 #ecf0f1); }
            QFrame#card_frame { background: white; border-radius: 12px; }
        """)

    def _handle_login(self):
        """Maneja el proceso de login."""
        username = self.ui.user_input.text().strip() if self.ui.user_input else ''
        password = self.ui.pass_input.text() if self.ui.pass_input else ''

        if not username or not password:
            self._show_error("Por favor ingrese usuario y contraseña")
            return

        self._set_loading_state(True)
        if self.ui.status_label:
            self.ui.status_label.setVisible(False)

        QTimer.singleShot(100, lambda: self._process_login(username, password))

    def _get_permissions_by_role(self, role: str) -> list:
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
            permisos_result = sql_manager.ejecutar_consulta_archivo(
                'sql/09_usuarios/obtener_permisos_usuario.sql',
                (user_id,)
            )

            if permisos_result:
                permisos_list = [row[0] for row in permisos_result if row[0]]  # modulo es la primera columna
                if permisos_list:
                    return permisos_list

            return self._get_permissions_by_role(user_role)

        except Exception as e:
            log_error(f"Error obteniendo permisos para usuario {user_id}: {str(e)}")
            return self._get_permissions_by_role('USUARIO')

    def _get_permissions_by_role(self, role: str) -> list:
        """
        Obtiene permisos predeterminados por rol.
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
            sql_manager.execute_non_query("""
                UPDATE usuarios SET
                    intentos_fallidos = intentos_fallidos + 1,
                    bloqueado_hasta = CASE
                        WHEN intentos_fallidos + 1 >= 5
                        THEN DATEADD(MINUTE, 30, GETDATE())
                        ELSE bloqueado_hasta
                    END,
                    fecha_modificacion = GETDATE()
                WHERE id = ?
            """, (user_id,))
        except Exception as e:
            log_error(f"Error incrementando intentos fallidos: {str(e)}")

    def _update_last_access(self, user_id: int, sql_manager):
        """Actualiza último acceso y resetea intentos fallidos."""
        try:
            # Usar UPDATE directo en lugar de archivo SQL
            sql_manager.execute_non_query("""
                UPDATE usuarios SET 
                    intentos_fallidos = 0,
                    ultimo_acceso = GETDATE(),
                    fecha_modificacion = GETDATE()
                WHERE id = ?
            """, (user_id,))
        except Exception as e:
            log_error(f"Error actualizando último acceso: {str(e)}")

    def _setup_connections(self):
        """Configura las conexiones de señales."""
        if self.ui.login_btn:
            self.ui.login_btn.clicked.connect(self._handle_login)
        if self.ui.cancel_btn:
            self.ui.cancel_btn.clicked.connect(self.reject)
        if self.ui.user_input:
            self.ui.user_input.returnPressed.connect(self._handle_login)
        if self.ui.pass_input:
            self.ui.pass_input.returnPressed.connect(self._handle_login)

    def _load_styles(self):
        """Carga los estilos adicionales."""
        self.setStyleSheet("""
            QDialog { background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #f7f9fa, stop:1 #ecf0f1); }
            QFrame#card_frame { background: white; border-radius: 12px; }
        """)

    def _handle_login(self):
        """Maneja el proceso de login."""
        username = self.ui.user_input.text().strip() if self.ui.user_input else ''
        password = self.ui.pass_input.text() if self.ui.pass_input else ''

        if not username or not password:
            self._show_error("Por favor ingrese usuario y contraseña")
            return

        self._set_loading_state(True)
        if self.ui.status_label:
            self.ui.status_label.setVisible(False)

        QTimer.singleShot(100, lambda: self._process_login(username, password))

    def _validate_user_with_real_tables(self, username: str, password: str, sql_manager) -> Optional[dict]:
        """
        Valida las credenciales del usuario usando las tablas reales de la base de datos.

        Args:
            username: Nombre de usuario
            password: Contraseña
            sql_manager: Manejador SQL

        Returns:
            dict: Datos del usuario si la validación es exitosa, None en caso contrario
        """
        try:
            import hashlib
            # Hash de la contraseña usando SHA256
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            # Consulta para validar usuario y obtener datos
            user_query = sql_manager.ejecutar_consulta_archivo(
                'sql/09_usuarios/validar_usuario.sql',
                (username, password_hash)
            )

            if user_query and len(user_query) > 0:
                user_data = user_query[0]
                user_id = user_data[0]  # id
                usuario = user_data[1]  # usuario
                nombre_completo = user_data[2]  # nombre_completo
                email = user_data[3]  # email
                rol = user_data[4]  # rol

                if user_id:
                    # Obtener permisos del usuario
                    permisos = self._get_user_permissions(user_id, rol, sql_manager)

                    # Actualizar último acceso
                    self._update_last_access(user_id, sql_manager)

                    return {
                        'id': user_id,
                        'username': usuario,
                        'rol': rol,
                        'permisos': permisos,
                        'nombre': nombre_completo or '',
                        'email': email or ''
                    }

            # Si la validación falla, buscar el usuario para incrementar intentos fallidos
            try:
                user_search = sql_manager.execute_query('SELECT id FROM usuarios WHERE usuario = ?', (username,))
                if user_search:
                    user_id = user_search[0][0]
                    self._increment_failed_attempts(user_id, sql_manager)
            except Exception:
                pass  # Usuario no existe

            return None

        except Exception as e:
            log_error(f"Error validando usuario {username}: {str(e)}")
            return None

    def _process_login(self, username: str, password: str):
        """Procesa la autenticación del usuario."""
        try:
            from rexus.utils.sql_query_manager import SQLQueryManager

            sql_manager = SQLQueryManager()
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
        if self.ui.login_btn:
            self.ui.login_btn.setEnabled(not loading)
        if self.ui.cancel_btn:
            self.ui.cancel_btn.setEnabled(not loading)
        if self.ui.user_input:
            self.ui.user_input.setEnabled(not loading)
        if self.ui.pass_input:
            self.ui.pass_input.setEnabled(not loading)
        if self.ui.progress_bar:
            self.ui.progress_bar.setVisible(loading)

        if loading and self.ui.progress_bar:
            self.ui.progress_bar.setRange(0, 0)
        if loading and self.ui.login_btn:
            self.ui.login_btn.setText("Iniciando sesión...")
        if not loading and self.ui.progress_bar:
            self.ui.progress_bar.setRange(0, 100)
        if not loading and self.ui.login_btn:
            self.ui.login_btn.setText("Iniciar Sesión")

    def _show_error(self, message: str):
        """Muestra un mensaje de error."""
        if self.ui.status_label:
            self.ui.status_label.setText(message)
            self.ui.status_label.setVisible(True)

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
            sql_manager.execute_non_query("""
                UPDATE usuarios SET
                    intentos_fallidos = intentos_fallidos + 1,
                    bloqueado_hasta = CASE
                        WHEN intentos_fallidos + 1 >= 5
                        THEN DATEADD(MINUTE, 30, GETDATE())
                        ELSE bloqueado_hasta
                    END,
                    fecha_modificacion = GETDATE()
                WHERE id = ?
            """, (user_id,))
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
        # Hoja de estilos moderna y coherente para el diálogo
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f7f9fa, stop:1 #ecf0f1);
                font-family: 'Segoe UI', Arial, sans-serif;
            }

            /* Card central */
            QFrame#title_frame, QFrame#form_frame {
                background: transparent;
            }

            QLabel#title_label {
                color: #2c3e50;
                font-size: 26px;
                font-weight: 700;
            }

            QLabel#subtitle_label {
                color: #7f8c8d;
                font-size: 11px;
            }

            QLineEdit#user_input, QLineEdit#pass_input {
                background: white;
                padding: 10px 12px;
                border: 1px solid #dfe6e9;
                border-radius: 8px;
                font-size: 14px;
                color: #2c3e50;
            }

            QLineEdit#user_input:focus, QLineEdit#pass_input:focus {
                border: 1px solid #3498db;
                box-shadow: 0 4px 10px rgba(52,152,219,0.08);
            }

            QProgressBar#progress_bar {
                height: 8px;
                border-radius: 6px;
                background: #dcdde1;
            }
            QProgressBar#progress_bar::chunk { background: #3498db; }

            QPushButton#login_btn {
                background-color: #2d98da;
                color: white;
                padding: 10px 16px;
                border-radius: 8px;
                font-weight: 600;
                min-width: 120px;
            }
            QPushButton#login_btn:hover { background-color: #247fb3; }

            QPushButton#cancel_btn {
                background-color: transparent;
                color: #e74c3c;
                padding: 10px 16px;
                border-radius: 8px;
                border: 1px solid transparent;
                font-weight: 600;
            }
            QPushButton#cancel_btn:hover { background-color: rgba(231,76,60,0.06); }

            QCheckBox#remember_check { color: #7f8c8d; }

            QLabel#status_label { color: #e74c3c; font-size: 12px; }

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
