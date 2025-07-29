"""
Vista de Administración de Usuarios - Rexus.app v2.0.0

Interface completa para gestionar usuarios, roles y permisos
"""

import sys
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QTableWidget,
    QTableWidgetItem, QPushButton, QLabel, QLineEdit, QComboBox,
    QFormLayout, QDialog, QDialogButtonBox, QMessageBox, QGroupBox,
    QCheckBox, QDateEdit, QSpinBox, QTextEdit, QFrame, QHeaderView,
    QAbstractItemView, QMenu, QApplication
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal
from PyQt6.QtGui import QFont, QIcon, QAction

from rexus.core.auth import get_auth_manager
from rexus.core.database import DatabaseConnection


class UserDialog(QDialog):
    """Diálogo para crear/editar usuarios"""
    
    def __init__(self, parent=None, user_data=None):
        super().__init__(parent)
        self.user_data = user_data
        self.auth_manager = get_auth_manager()
        self.init_ui()
        
        if user_data:
            self.load_user_data()
    
    def init_ui(self):
        """Inicializa la interfaz del diálogo"""
        self.setWindowTitle("Nuevo Usuario" if not self.user_data else "Editar Usuario")
        self.setFixedSize(500, 600)
        
        layout = QVBoxLayout(self)
        
        # Formulario principal
        form_layout = QFormLayout()
        
        # Datos básicos
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Nombre de usuario único")
        form_layout.addRow("Usuario:", self.username_edit)
        
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_edit.setPlaceholderText("Contraseña (mínimo 6 caracteres)")
        form_layout.addRow("Contraseña:", self.password_edit)
        
        self.confirm_password_edit = QLineEdit()
        self.confirm_password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password_edit.setPlaceholderText("Confirmar contraseña")
        form_layout.addRow("Confirmar:", self.confirm_password_edit)
        
        # Datos personales
        self.nombre_edit = QLineEdit()
        self.nombre_edit.setPlaceholderText("Nombre completo")
        form_layout.addRow("Nombre:", self.nombre_edit)
        
        self.apellido_edit = QLineEdit()
        self.apellido_edit.setPlaceholderText("Apellido")
        form_layout.addRow("Apellido:", self.apellido_edit)
        
        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText("email@ejemplo.com")
        form_layout.addRow("Email:", self.email_edit)
        
        # Rol
        self.role_combo = QComboBox()
        self.role_combo.addItems(["usuario", "supervisor", "admin"])
        form_layout.addRow("Rol:", self.role_combo)
        
        # Estado
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Activo", "Inactivo"])
        form_layout.addRow("Estado:", self.status_combo)
        
        layout.addLayout(form_layout)
        
        # Permisos por módulo
        permisos_group = QGroupBox("Permisos por Módulo")
        permisos_layout = QVBoxLayout(permisos_group)
        
        self.permisos_checks = {}
        modulos = [
            "inventario", "obras", "compras", "contabilidad", "usuarios",
            "herrajes", "vidrios", "logistica", "mantenimiento", "auditoria"
        ]
        
        for modulo in modulos:
            modulo_layout = QHBoxLayout()
            modulo_layout.addWidget(QLabel(modulo.capitalize()))
            
            # Checkboxes para diferentes permisos
            read_check = QCheckBox("Leer")
            write_check = QCheckBox("Escribir")
            delete_check = QCheckBox("Eliminar")
            
            modulo_layout.addWidget(read_check)
            modulo_layout.addWidget(write_check)
            modulo_layout.addWidget(delete_check)
            
            self.permisos_checks[modulo] = {
                'read': read_check,
                'write': write_check,
                'delete': delete_check
            }
            
            permisos_layout.addLayout(modulo_layout)
        
        layout.addWidget(permisos_group)
        
        # Botones
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        # Conectar eventos
        self.role_combo.currentTextChanged.connect(self.update_permissions_by_role)
    
    def load_user_data(self):
        """Carga los datos del usuario en el formulario"""
        if not self.user_data:
            return
        
        self.username_edit.setText(self.user_data['username'])
        self.username_edit.setEnabled(False)  # No permitir cambiar username
        
        self.password_edit.setPlaceholderText("Dejar vacío para mantener actual")
        self.confirm_password_edit.setPlaceholderText("Dejar vacío para mantener actual")
        
        self.nombre_edit.setText(self.user_data.get('nombre', ''))
        self.apellido_edit.setText(self.user_data.get('apellido', ''))
        self.email_edit.setText(self.user_data.get('email', ''))
        
        # Establecer rol
        role_index = self.role_combo.findText(self.user_data.get('role', 'usuario'))
        if role_index >= 0:
            self.role_combo.setCurrentIndex(role_index)
        
        # Establecer estado
        status_index = self.status_combo.findText(self.user_data.get('status', 'Activo'))
        if status_index >= 0:
            self.status_combo.setCurrentIndex(status_index)
    
    def update_permissions_by_role(self, role):
        """Actualiza permisos automáticamente según el rol"""
        for modulo, checks in self.permisos_checks.items():
            if role == 'admin':
                checks['read'].setChecked(True)
                checks['write'].setChecked(True)
                checks['delete'].setChecked(True)
            elif role == 'supervisor':
                checks['read'].setChecked(True)
                checks['write'].setChecked(True)
                checks['delete'].setChecked(False)
            else:  # usuario
                checks['read'].setChecked(True)
                checks['write'].setChecked(False)
                checks['delete'].setChecked(False)
    
    def validate_form(self):
        """Valida los datos del formulario"""
        username = self.username_edit.text().strip()
        password = self.password_edit.text()
        confirm_password = self.confirm_password_edit.text()
        
        if not username:
            QMessageBox.warning(self, "Error", "El nombre de usuario es requerido")
            return False
        
        # Solo validar contraseña si no es edición o si se ingresó nueva contraseña
        if not self.user_data or password:
            if len(password) < 6:
                QMessageBox.warning(self, "Error", "La contraseña debe tener al menos 6 caracteres")
                return False
            
            if password != confirm_password:
                QMessageBox.warning(self, "Error", "Las contraseñas no coinciden")
                return False
        
        email = self.email_edit.text().strip()
        if email and '@' not in email:
            QMessageBox.warning(self, "Error", "El email no tiene formato válido")
            return False
        
        return True
    
    def get_user_data(self):
        """Obtiene los datos del formulario"""
        return {
            'username': self.username_edit.text().strip(),
            'password': self.password_edit.text(),
            'nombre': self.nombre_edit.text().strip(),
            'apellido': self.apellido_edit.text().strip(),
            'email': self.email_edit.text().strip(),
            'role': self.role_combo.currentText(),
            'status': self.status_combo.currentText()
        }
    
    def accept(self):
        """Valida y acepta el diálogo"""
        if self.validate_form():
            super().accept()


class UsersAdminView(QWidget):
    """Vista completa de administración de usuarios"""
    
    # Señales
    user_created = pyqtSignal(dict)
    user_updated = pyqtSignal(dict)
    user_deleted = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.auth_manager = get_auth_manager()
        self.current_user = self.auth_manager.get_current_user() if self.auth_manager else None
        self.init_ui()
        self.load_users()
        self.setup_permissions()
    
    def init_ui(self):
        """Inicializa la interfaz principal"""
        layout = QVBoxLayout(self)
        
        # Título
        title = QLabel("Administración de Usuarios")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Tabs
        tabs = QTabWidget()
        
        # Tab 1: Usuarios
        users_tab = self.create_users_tab()
        tabs.addTab(users_tab, "Usuarios")
        
        # Tab 2: Roles y Permisos
        roles_tab = self.create_roles_tab()
        tabs.addTab(roles_tab, "Roles y Permisos")
        
        # Tab 3: Estadísticas
        stats_tab = self.create_stats_tab()
        tabs.addTab(stats_tab, "Estadísticas")
        
        layout.addWidget(tabs)
    
    def create_users_tab(self):
        """Crea la pestaña de gestión de usuarios"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Barra de herramientas
        toolbar = QHBoxLayout()
        
        # Botones
        new_btn = QPushButton("Nuevo Usuario")
        new_btn.clicked.connect(self.create_user)
        toolbar.addWidget(new_btn)
        
        edit_btn = QPushButton("Editar")
        edit_btn.clicked.connect(self.edit_user)
        toolbar.addWidget(edit_btn)
        
        delete_btn = QPushButton("Eliminar")
        delete_btn.clicked.connect(self.delete_user)
        toolbar.addWidget(delete_btn)
        
        toolbar.addStretch()
        
        # Búsqueda
        search_label = QLabel("Buscar:")
        toolbar.addWidget(search_label)
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Nombre, usuario o email...")
        self.search_edit.textChanged.connect(self.filter_users)
        toolbar.addWidget(self.search_edit)
        
        refresh_btn = QPushButton("Actualizar")
        refresh_btn.clicked.connect(self.load_users)
        toolbar.addWidget(refresh_btn)
        
        layout.addLayout(toolbar)
        
        # Tabla de usuarios
        self.users_table = QTableWidget()
        self.users_table.setColumnCount(7)
        self.users_table.setHorizontalHeaderLabels([
            "ID", "Usuario", "Nombre", "Apellido", "Email", "Rol", "Estado"
        ])
        
        # Configurar tabla
        header = self.users_table.horizontalHeader()
        if header is not None:
            header.setStretchLastSection(True)
            header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        
        self.users_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.users_table.setAlternatingRowColors(True)
        self.users_table.setSortingEnabled(True)
        
        # Menú contextual
        self.users_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.users_table.customContextMenuRequested.connect(self.show_context_menu)
        
        layout.addWidget(self.users_table)
        
        return tab
    
    def create_roles_tab(self):
        """Crea la pestaña de roles y permisos"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Información sobre roles
        info_label = QLabel("Roles del Sistema")
        info_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(info_label)
        
        # Descripción de roles
        roles_info = QTextEdit()
        roles_info.setReadOnly(True)
        roles_info.setMaximumHeight(200)
        roles_info.setPlainText("""
ROLES DISPONIBLES:

• ADMIN: Acceso completo a todos los módulos
  - Puede crear, editar y eliminar usuarios
  - Acceso a configuración del sistema
  - Puede generar reportes de auditoría

• SUPERVISOR: Acceso de lectura/escritura
  - Puede ver y modificar datos en la mayoría de módulos
  - No puede gestionar usuarios
  - Acceso limitado a configuración

• USUARIO: Acceso de solo lectura
  - Puede ver información en los módulos asignados
  - No puede modificar datos críticos
  - Acceso básico a reportes
        """)
        layout.addWidget(roles_info)
        
        # Permisos por módulo
        permisos_group = QGroupBox("Matriz de Permisos por Rol")
        permisos_layout = QVBoxLayout(permisos_group)
        
        # Crear tabla de permisos
        permisos_table = QTableWidget()
        permisos_table.setColumnCount(4)
        permisos_table.setHorizontalHeaderLabels(["Módulo", "Admin", "Supervisor", "Usuario"])
        
        modulos = [
            "Inventario", "Obras", "Compras", "Contabilidad", "Usuarios",
            "Herrajes", "Vidrios", "Logística", "Mantenimiento", "Auditoría"
        ]
        
        permisos_table.setRowCount(len(modulos))
        
        for i, modulo in enumerate(modulos):
            permisos_table.setItem(i, 0, QTableWidgetItem(modulo))
            permisos_table.setItem(i, 1, QTableWidgetItem("Completo"))
            permisos_table.setItem(i, 2, QTableWidgetItem("Lectura/Escritura"))
            permisos_table.setItem(i, 3, QTableWidgetItem("Solo Lectura"))
        
        permisos_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        permisos_table.horizontalHeader().setStretchLastSection(True)
        
        permisos_layout.addWidget(permisos_table)
        layout.addWidget(permisos_group)
        
        return tab
    
    def create_stats_tab(self):
        """Crea la pestaña de estadísticas"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Título
        title = QLabel("Estadísticas de Usuarios")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Estadísticas básicas
        stats_layout = QHBoxLayout()
        
        # Total usuarios
        total_group = QGroupBox("Total Usuarios")
        total_layout = QVBoxLayout(total_group)
        self.total_users_label = QLabel("0")
        self.total_users_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        self.total_users_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        total_layout.addWidget(self.total_users_label)
        stats_layout.addWidget(total_group)
        
        # Usuarios activos
        active_group = QGroupBox("Usuarios Activos")
        active_layout = QVBoxLayout(active_group)
        self.active_users_label = QLabel("0")
        self.active_users_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        self.active_users_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        active_layout.addWidget(self.active_users_label)
        stats_layout.addWidget(active_group)
        
        # Usuarios por rol
        roles_group = QGroupBox("Por Rol")
        roles_layout = QVBoxLayout(roles_group)
        self.roles_stats_label = QLabel("Admin: 0\nSupervisor: 0\nUsuario: 0")
        self.roles_stats_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        roles_layout.addWidget(self.roles_stats_label)
        stats_layout.addWidget(roles_group)
        
        layout.addLayout(stats_layout)
        
        # Actividad reciente
        activity_group = QGroupBox("Actividad Reciente")
        activity_layout = QVBoxLayout(activity_group)
        
        self.activity_table = QTableWidget()
        self.activity_table.setColumnCount(3)
        self.activity_table.setHorizontalHeaderLabels(["Usuario", "Último Login", "Estado"])
        self.activity_table.setMaximumHeight(200)
        
        activity_layout.addWidget(self.activity_table)
        layout.addWidget(activity_group)
        
        layout.addStretch()
        
        return tab
    
    def setup_permissions(self):
        """Configura los permisos según el rol del usuario actual"""
        if not self.current_user:
            return
        
        # Solo admin puede crear usuarios y gestionar permisos
        is_admin = self.current_user.get('role') == 'admin'
        
        # Buscar botones en la pestaña de usuarios
        users_tab = self.findChild(QWidget)
        if users_tab:
            # Buscar botones por su texto
            for button in users_tab.findChildren(QPushButton):
                if button.text() in ["Nuevo Usuario", "Editar", "Eliminar"]:
                    button.setEnabled(is_admin)
                    if not is_admin:
                        button.setToolTip("Solo los administradores pueden gestionar usuarios")
        
        # Deshabilitar pestañas para no-admin
        if hasattr(self, 'tabs'):
            # Pestaña de roles y permisos solo para admin
            if self.tabs.count() > 1:
                self.tabs.setTabEnabled(1, is_admin)
                if not is_admin:
                    self.tabs.setTabToolTip(1, "Solo administradores pueden gestionar roles y permisos")
    
    def load_users(self):
        """Carga la lista de usuarios"""
        users = self.auth_manager.get_all_users()
        
        self.users_table.setRowCount(len(users))
        
        for i, user in enumerate(users):
            self.users_table.setItem(i, 0, QTableWidgetItem(str(user['id'])))
            self.users_table.setItem(i, 1, QTableWidgetItem(user['username']))
            self.users_table.setItem(i, 2, QTableWidgetItem(user.get('nombre', '')))
            self.users_table.setItem(i, 3, QTableWidgetItem(user.get('apellido', '')))
            self.users_table.setItem(i, 4, QTableWidgetItem(user.get('email', '')))
            self.users_table.setItem(i, 5, QTableWidgetItem(user['role']))
            self.users_table.setItem(i, 6, QTableWidgetItem(user['status']))
        
        # Actualizar estadísticas
        self.update_stats(users)
    
    def update_stats(self, users):
        """Actualiza las estadísticas"""
        total = len(users)
        active = len([u for u in users if u['status'] == 'Activo'])
        
        roles_count = {}
        for user in users:
            role = user['role']
            roles_count[role] = roles_count.get(role, 0) + 1
        
        self.total_users_label.setText(str(total))
        self.active_users_label.setText(str(active))
        
        roles_text = f"Admin: {roles_count.get('admin', 0)}\n"
        roles_text += f"Supervisor: {roles_count.get('supervisor', 0)}\n"
        roles_text += f"Usuario: {roles_count.get('usuario', 0)}"
        self.roles_stats_label.setText(roles_text)
        
        # Actualizar tabla de actividad
        self.activity_table.setRowCount(min(10, len(users)))
        for i, user in enumerate(users[:10]):
            self.activity_table.setItem(i, 0, QTableWidgetItem(user['username']))
            login_str = str(user.get('ultimo_login', 'Nunca'))
            if login_str != 'Nunca' and login_str != 'None':
                login_str = login_str.split('.')[0]  # Remover microsegundos
            self.activity_table.setItem(i, 1, QTableWidgetItem(login_str))
            self.activity_table.setItem(i, 2, QTableWidgetItem(user['status']))
    
    def filter_users(self, text):
        """Filtra usuarios por texto de búsqueda"""
        for i in range(self.users_table.rowCount()):
            show = False
            for j in range(1, self.users_table.columnCount()):  # Excluir columna ID
                item = self.users_table.item(i, j)
                if item and text.lower() in item.text().lower():
                    show = True
                    break
            self.users_table.setRowHidden(i, not show)
    
    def create_user(self):
        """Crea un nuevo usuario"""
        # Verificar permisos
        if not self.current_user or self.current_user.get('role') != 'admin':
            QMessageBox.warning(self, "Acceso Denegado", 
                              "Solo los administradores pueden crear nuevos usuarios")
            return
        
        dialog = UserDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            user_data = dialog.get_user_data()
            
            # Crear usuario
            success = self.auth_manager.create_user(
                username=user_data['username'],
                password=user_data['password'],
                role=user_data['role'],
                nombre=user_data['nombre'],
                apellido=user_data['apellido'],
                email=user_data['email']
            )
            
            if success:
                QMessageBox.information(self, "Éxito", "Usuario creado exitosamente")
                self.load_users()
                self.user_created.emit(user_data)
            else:
                QMessageBox.warning(self, "Error", "No se pudo crear el usuario")
    
    def edit_user(self):
        """Edita el usuario seleccionado"""
        # Verificar permisos
        if not self.current_user or self.current_user.get('role') != 'admin':
            QMessageBox.warning(self, "Acceso Denegado", 
                              "Solo los administradores pueden editar usuarios")
            return
        
        current_row = self.users_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Error", "Seleccione un usuario para editar")
            return
        
        # Obtener datos del usuario
        user_id = int(self.users_table.item(current_row, 0).text())
        user_data = {
            'id': user_id,
            'username': self.users_table.item(current_row, 1).text(),
            'nombre': self.users_table.item(current_row, 2).text(),
            'apellido': self.users_table.item(current_row, 3).text(),
            'email': self.users_table.item(current_row, 4).text(),
            'role': self.users_table.item(current_row, 5).text(),
            'status': self.users_table.item(current_row, 6).text()
        }
        
        dialog = UserDialog(self, user_data)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_data = dialog.get_user_data()
            
            # Actualizar usuario
            success = self.auth_manager.update_user(
                user_id=user_id,
                username=new_data['username'] if new_data['username'] != user_data['username'] else None,
                role=new_data['role'],
                nombre=new_data['nombre'],
                apellido=new_data['apellido'],
                email=new_data['email'],
                status=new_data['status']
            )
            
            # Cambiar contraseña si se especificó
            if new_data['password']:
                self.auth_manager.change_password(user_id, new_data['password'])
            
            if success:
                QMessageBox.information(self, "Éxito", "Usuario actualizado exitosamente")
                self.load_users()
                self.user_updated.emit(new_data)
            else:
                QMessageBox.warning(self, "Error", "No se pudo actualizar el usuario")
    
    def delete_user(self):
        """Elimina el usuario seleccionado"""
        # Verificar permisos
        if not self.current_user or self.current_user.get('role') != 'admin':
            QMessageBox.warning(self, "Acceso Denegado", 
                              "Solo los administradores pueden eliminar usuarios")
            return
        
        current_row = self.users_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Error", "Seleccione un usuario para eliminar")
            return
        
        username = self.users_table.item(current_row, 1).text()
        
        # Confirmar eliminación
        reply = QMessageBox.question(
            self, "Confirmar", 
            f"¿Está seguro de que desea eliminar el usuario '{username}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            user_id = int(self.users_table.item(current_row, 0).text())
            
            # Cambiar estado a inactivo en lugar de eliminar
            success = self.auth_manager.update_user(user_id, status='Inactivo')
            
            if success:
                QMessageBox.information(self, "Éxito", "Usuario desactivado exitosamente")
                self.load_users()
                self.user_deleted.emit(user_id)
            else:
                QMessageBox.warning(self, "Error", "No se pudo desactivar el usuario")
    
    def show_context_menu(self, position):
        """Muestra menú contextual en la tabla"""
        if self.users_table.itemAt(position):
            menu = QMenu()
            
            edit_action = menu.addAction("Editar")
            edit_action.triggered.connect(self.edit_user)
            
            delete_action = menu.addAction("Desactivar")
            delete_action.triggered.connect(self.delete_user)
            
            menu.exec(self.users_table.mapToGlobal(position))


# Ejemplo de uso
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Crear vista de administración
    admin_view = UsersAdminView()
    admin_view.show()
    
    sys.exit(app.exec())