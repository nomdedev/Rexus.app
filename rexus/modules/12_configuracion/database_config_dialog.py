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
Diálogo de Configuración de Base de Datos - Rexus.app v2.0.0

Permite configurar las conexiones a base de datos del sistema
"""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QGroupBox,
    QSpinBox, QCheckBox, QTabWidget, QWidget,
    QMessageBox, QTextEdit, QComboBox
)

from rexus.core.database import DatabaseConnection

class DatabaseConfigDialog(QDialog):
    """Diálogo para configurar conexiones de base de datos"""

    config_saved = pyqtSignal(dict)  # Emite la nueva configuración

    def __init__(self, parent=None, current_config=None):
        super().__init__(parent)
        self.current_config = current_config or {}
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Configuración de Base de Datos - Rexus.app")
        self.setFixedSize(650, 750)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowCloseButtonHint)

        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)

        # Título
        title = QLabel("⚙️ Configuración de Base de Datos")
        title.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 10px;
            }
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)

        # Subtítulo
        subtitle = QLabel("Configure las conexiones a las bases de datos del sistema")
        subtitle.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #7f8c8d;
                margin-bottom: 20px;
            }
        """)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(subtitle)

        # Tabs para diferentes configuraciones
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #ddd;
                border-radius: 8px;
                background-color: #f8f9fa;
            }
            QTabBar::tab {
                background-color: #e9ecef;
                color: #495057;
                padding: 12px 20px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: 500;
            }
            QTabBar::tab:selected {
                background-color: #ffffff;
                color: #2c3e50;
                font-weight: bold;
            }
        """)

        # Tab: Configuración General
        self.create_general_tab()

        # Tab: Base de Datos Users
        self.create_users_db_tab()

        # Tab: Base de Datos Inventario
        self.create_inventario_db_tab()

        # Tab: Base de Datos Auditoría
        self.create_auditoria_db_tab()

        # Tab: Prueba de Conexión
        self.create_test_tab()

        main_layout.addWidget(self.tab_widget)

        # Botones
        self.create_buttons(main_layout)

        # Cargar valores actuales
        self.load_current_config()

    def create_general_tab(self):
        """Crea la pestaña de configuración general"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Configuración del servidor
        server_group = QGroupBox("🖥️ Configuración del Servidor")
        server_group.setStyleSheet(self.get_group_style())
        server_layout = QFormLayout(server_group)
        server_layout.setSpacing(15)

        self.server_input = QLineEdit()
        self.server_input.setPlaceholderText("Ej: localhost\\SQLEXPRESS")
        self.server_input.setStyleSheet(self.get_input_style())

        self.server_alt_input = QLineEdit()
        self.server_alt_input.setPlaceholderText("Ej: localhost")
        self.server_alt_input.setStyleSheet(self.get_input_style())

        self.port_input = QSpinBox()
        self.port_input.setRange(1, 65535)
        self.port_input.setValue(1433)
        self.port_input.setStyleSheet(self.get_input_style())

        self.driver_combo = QComboBox()
        self.driver_combo.addItems([
            "ODBC Driver 17 for SQL Server",
            "ODBC Driver 18 for SQL Server",
            "SQL Server",
            "SQL Server Native Client 11.0"
        ])
        self.driver_combo.setStyleSheet(self.get_input_style())

        server_layout.addRow("Servidor Principal:", self.server_input)
        server_layout.addRow("Servidor Alternativo:", self.server_alt_input)
        server_layout.addRow("Puerto:", self.port_input)
        server_layout.addRow("Driver ODBC:", self.driver_combo)

        layout.addWidget(server_group)

        # Configuración de autenticación
        auth_group = QGroupBox("🔐 Autenticación")
        auth_group.setStyleSheet(self.get_group_style())
        auth_layout = QFormLayout(auth_group)
        auth_layout.setSpacing(15)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Usuario de SQL Server")
        self.username_input.setStyleSheet(self.get_input_style())

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Contraseña")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setStyleSheet(self.get_input_style())

        self.trusted_checkbox = QCheckBox("Usar autenticación de Windows")
        self.trusted_checkbox.setStyleSheet("""
            QCheckBox {
                font-size: 14px;
                color: #4a5568;
                font-weight: 500;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
            }
            QCheckBox::indicator:unchecked {
                border: 2px solid #e2e8f0;
                border-radius: 6px;
                background-color: #ffffff;
            }
            QCheckBox::indicator:checked {
                border: 2px solid #667eea;
                border-radius: 6px;
                background-color: #667eea;
            }
        """)

        # Conectar checkbox para habilitar/deshabilitar credenciales
        self.trusted_checkbox.toggled.connect(self.toggle_credentials)

        auth_layout.addRow("Usuario:", self.username_input)
        auth_layout.addRow("Contraseña:", self.password_input)
        auth_layout.addRow("", self.trusted_checkbox)

        layout.addWidget(auth_group)

        # Configuración avanzada
        advanced_group = QGroupBox("⚡ Configuración Avanzada")
        advanced_group.setStyleSheet(self.get_group_style())
        advanced_layout = QFormLayout(advanced_group)
        advanced_layout.setSpacing(15)

        self.timeout_input = QSpinBox()
        self.timeout_input.setRange(5, 300)
        self.timeout_input.setValue(30)
        self.timeout_input.setSuffix(" segundos")
        self.timeout_input.setStyleSheet(self.get_input_style())

        self.pool_size_input = QSpinBox()
        self.pool_size_input.setRange(1, 100)
        self.pool_size_input.setValue(10)
        self.pool_size_input.setStyleSheet(self.get_input_style())

        advanced_layout.addRow("Timeout de conexión:", self.timeout_input)
        advanced_layout.addRow("Tamaño del pool:", self.pool_size_input)

        layout.addWidget(advanced_group)
        layout.addStretch()

        self.tab_widget.addTab(tab, "⚙️ General")

    def create_users_db_tab(self):
        """Crea la pestaña para configurar la BD de usuarios"""
        tab = self.create_database_tab(
            "users",
            "👥 Base de Datos de Usuarios",
            "Configuración para autenticación y permisos",
            ["usuarios", "roles", "permisos", "sesiones"]
        )
        self.tab_widget.addTab(tab, "👥 Users DB")

    def create_inventario_db_tab(self):
        """Crea la pestaña para configurar la BD de inventario"""
        tab = self.create_database_tab(
            "inventario",
            "📦 Base de Datos de Inventario",
            "Configuración para módulos de negocio",
            ["inventario_perfiles", "obras", "pedidos", "herrajes", "vidrios"]
        )
        self.tab_widget.addTab(tab, "📦 Inventario DB")

    def create_auditoria_db_tab(self):
        """Crea la pestaña para configurar la BD de auditoría"""
        tab = self.create_database_tab(
            "auditoria",
            "[SEARCH] Base de Datos de Auditoría",
            "Configuración para logs y trazabilidad",
            ["auditoria", "logs_usuarios", "eventos_sistema"]
        )
        self.tab_widget.addTab(tab, "[SEARCH] Auditoría DB")

    def create_database_tab(self, db_key, title, description, tables):
        """Crea una pestaña genérica para configuración de BD"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header = QLabel(title)
        header.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 5px;
            }
        """)
        layout.addWidget(header)

        desc = QLabel(description)
        desc.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #7f8c8d;
                margin-bottom: 20px;
            }
        """)
        layout.addWidget(desc)

        # Configuración de BD
        config_group = QGroupBox("[CHART] Configuración de Base de Datos")
        config_group.setStyleSheet(self.get_group_style())
        config_layout = QFormLayout(config_group)
        config_layout.setSpacing(15)

        # Input para nombre de BD
        db_input = QLineEdit()
        db_input.setPlaceholderText(f"Nombre de la base de datos {db_key}")
        db_input.setStyleSheet(self.get_input_style())
        setattr(self, f"{db_key}_db_input", db_input)

        config_layout.addRow("Nombre de BD:", db_input)
        layout.addWidget(config_group)

        # Información de tablas
        tables_group = QGroupBox("📋 Tablas Principales")
        tables_group.setStyleSheet(self.get_group_style())
        tables_layout = QVBoxLayout(tables_group)

        tables_text = QTextEdit()
        tables_text.setPlainText("\\n".join([f"• {table}" for table in tables]))
        tables_text.setMaximumHeight(120)
        tables_text.setReadOnly(True)
        tables_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                background-color: #f8f9fa;
                font-size: 12px;
                color: #4a5568;
                padding: 10px;
            }
        """)

        tables_layout.addWidget(tables_text)
        layout.addWidget(tables_group)

        layout.addStretch()
        return tab

    def create_test_tab(self):
        """Crea la pestaña de prueba de conexión"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header = QLabel("[TOOL] Prueba de Conexión")
        header.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 5px;
            }
        """)
        layout.addWidget(header)

        desc = QLabel("Pruebe las conexiones a las bases de datos configuradas")
        desc.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #7f8c8d;
                margin-bottom: 20px;
            }
        """)
        layout.addWidget(desc)

        # Botones de prueba
        test_group = QGroupBox("🧪 Pruebas de Conexión")
        test_group.setStyleSheet(self.get_group_style())
        test_layout = QVBoxLayout(test_group)
        test_layout.setSpacing(15)

        # Botones para cada BD
        self.test_users_btn = QPushButton("🧪 Probar BD Users")
        self.test_inventario_btn = QPushButton("🧪 Probar BD Inventario")
        self.test_auditoria_btn = QPushButton("🧪 Probar BD Auditoría")
        self.test_all_btn = QPushButton("[ROCKET] Probar Todas las Conexiones")

        for btn in [self.test_users_btn, self.test_inventario_btn,
                   self.test_auditoria_btn, self.test_all_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #667eea;
                    color: white;
                    border: none;
                    padding: 12px 20px;
                    border-radius: 8px;
                    font-size: 14px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background-color: #5a67d8;
                }
                QPushButton:pressed {
                    background-color: #4c51bf;
                }
            """)
            test_layout.addWidget(btn)

        # Conectar eventos
        self.test_users_btn.clicked.connect(lambda: self.test_connection("users"))
        self.test_inventario_btn.clicked.connect(lambda: self.test_connection("inventario"))
        self.test_auditoria_btn.clicked.connect(lambda: self.test_connection("auditoria"))
        self.test_all_btn.clicked.connect(self.test_all_connections)

        layout.addWidget(test_group)

        # Área de resultados
        results_group = QGroupBox("[CHART] Resultados de Pruebas")
        results_group.setStyleSheet(self.get_group_style())
        results_layout = QVBoxLayout(results_group)

        self.results_text = QTextEdit()
        self.results_text.setPlaceholderText("Los resultados de las pruebas aparecerán aquí...")
        self.results_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                background-color: #f8f9fa;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 11px;
                color: #4a5568;
                padding: 15px;
            }
        """)

        results_layout.addWidget(self.results_text)
        layout.addWidget(results_group)

        self.tab_widget.addTab(tab, "🧪 Pruebas")

    def create_buttons(self, main_layout):
        """Crea los botones del diálogo"""
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)

        # Botón guardar
        save_btn = QPushButton("💾 Guardar Configuración")
        save_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                          stop:0 #667eea, stop:1 #764ba2);
                color: white;
                border: none;
                padding: 12px 30px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
                min-width: 150px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                          stop:0 #5a67d8, stop:1 #667eea);
            }
        """)
        save_btn.clicked.connect(self.save_config)

        # Botón cancelar
        cancel_btn = QPushButton("[ERROR] Cancelar")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #718096;
                border: 2px solid #e2e8f0;
                padding: 12px 30px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 500;
                min-width: 150px;
            }
            QPushButton:hover {
                border-color: #cbd5e0;
                background-color: #f7fafc;
                color: #4a5568;
            }
        """)
        cancel_btn.clicked.connect(self.reject)

        buttons_layout.addStretch()
        buttons_layout.addWidget(cancel_btn)
        buttons_layout.addWidget(save_btn)

        main_layout.addLayout(buttons_layout)

    def get_group_style(self):
        """Estilo para los grupos"""
        return """
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #2c3e50;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
                background-color: white;
            }
        """

    def get_input_style(self):
        """Estilo para los inputs"""
        return """
            QLineEdit, QSpinBox, QComboBox {
                padding: 12px 16px;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                font-size: 14px;
                background-color: #ffffff;
                color: #2d3748;
                min-height: 20px;
            }
            QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
                border-color: #667eea;
                outline: none;
            }
            QLineEdit:hover, QSpinBox:hover, QComboBox:hover {
                border-color: #cbd5e0;
            }
        """

    def toggle_credentials(self, checked):
        """Habilita/deshabilita campos de credenciales"""
        self.username_input.setEnabled(not checked)
        self.password_input.setEnabled(not checked)

    def load_current_config(self):
        """Carga la configuración actual"""
        if not self.current_config:
            return

        # Configuración general
        self.server_input.setText(self.current_config.get("server", ""))
        self.server_alt_input.setText(self.current_config.get("server_alternate", ""))
        self.port_input.setValue(self.current_config.get("port", 1433))
        self.username_input.setText(self.current_config.get("username", ""))
        self.password_input.setText(self.current_config.get("password", ""))

        # Bases de datos
        databases = self.current_config.get("databases", {})
        if hasattr(self, 'users_db_input'):
            self.users_db_input.setText(databases.get("users", ""))
        if hasattr(self, 'inventario_db_input'):
            self.inventario_db_input.setText(databases.get("inventario", ""))
        if hasattr(self, 'auditoria_db_input'):
            self.auditoria_db_input.setText(databases.get("auditoria", ""))

    def save_config(self):
        """Guarda la configuración"""
        config = {
            "driver": self.driver_combo.currentText(),
            "server": self.server_input.text().strip(),
            "server_alternate": self.server_alt_input.text().strip(),
            "port": self.port_input.value(),
            "username": self.username_input.text().strip(),
            "password": self.password_input.text(),
            "trusted": self.trusted_checkbox.isChecked(),
            "timeout": self.timeout_input.value(),
            "pool_size": self.pool_size_input.value(),
            "databases": {
                "users": getattr(self, 'users_db_input', None) and \
                    self.users_db_input.text().strip(),
                "inventario": getattr(self, 'inventario_db_input', None) and \
                    self.inventario_db_input.text().strip(),
                "auditoria": getattr(self, 'auditoria_db_input', None) and \
                    self.auditoria_db_input.text().strip(),
            }
        }

        # Validaciones básicas
        if not config["server"]:
            QMessageBox.warning(self, "Error", "Debe especificar un servidor")
            return

        if not config["trusted"] and \
            (not config["username"] or not config["password"]):
            QMessageBox.warning(self, "Error", "Debe especificar usuario y contraseña o usar autenticación de Windows")
            return

        # Emitir señal con la nueva configuración
        self.config_saved.emit(config)

        QMessageBox.information(self, "Éxito", "Configuración guardada correctamente")
        self.accept()

    def test_connection(self, db_type):
        """Prueba la conexión a una base de datos específica"""
        self.results_text.append(f"\\n[SEARCH] Probando conexión a BD {db_type}...")

        try:
            # Configuración de prueba
            server = self.server_input.text().strip()
            username = self.username_input.text().strip()
            password = self.password_input.text()
            trusted = self.trusted_checkbox.isChecked()

            db_name = ""
            if db_type == "users" and hasattr(self, 'users_db_input'):
                db_name = self.users_db_input.text().strip()
            elif db_type == "inventario" and \
                hasattr(self, 'inventario_db_input'):
                db_name = self.inventario_db_input.text().strip()
            elif db_type == "auditoria" and \
                hasattr(self, 'auditoria_db_input'):
                db_name = self.auditoria_db_input.text().strip()

            if not server:
                self.results_text.append("[ERROR] Error: Servidor no especificado")
                return

            if not db_name:
                self.results_text.append(f"[ERROR] Error: Nombre de BD {db_type} no especificado")
                return

            # Intentar conexión
            test_conn = DatabaseConnection(
                server=server,
                database=db_name,
                username=username,
                password=password,
                trusted=trusted
            )

            if test_conn.connect():
                self.results_text.append(f"[CHECK] Conexión exitosa a BD {db_type}")
                test_conn.disconnect()
            else:
                self.results_text.append(f"[ERROR] Error conectando a BD {db_type}")

        except Exception as e:
            self.results_text.append(f"[ERROR] Error: {str(e)}")

        # Scroll al final
        self.results_text.verticalScrollBar().setValue(
            self.results_text.verticalScrollBar().maximum()
        )

    def test_all_connections(self):
        """Prueba todas las conexiones"""
        self.results_text.clear()
        self.results_text.append("[ROCKET] Iniciando prueba de todas las conexiones...")

        for db_type in ["users", "inventario", "auditoria"]:
            self.test_connection(db_type)

        self.results_text.append("\\n[CHECK] Pruebas completadas")
