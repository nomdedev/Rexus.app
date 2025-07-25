"""
Sistema de Seguridad Global - Stock.App v1.1.3

Sistema centralizado de autenticación, autorización y control de acceso
para toda la aplicación.
"""

import hashlib
import json
import os
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set

from PyQt6.QtCore import QObject, pyqtSignal


class SecurityManager(QObject):
    """Gestor centralizado de seguridad para toda la aplicación."""

    # Señales para notificar cambios de estado
    user_logged_in = pyqtSignal(str, str)  # username, role
    user_logged_out = pyqtSignal(str)  # username
    permissions_changed = pyqtSignal(str)  # username

    def __init__(self, db_connection=None):
        super().__init__()
        self.db_connection = db_connection
        self.current_user = None
        self.current_role = None
        self.session_id = None
        self.login_time = None
        self.permissions_cache = {}

        # Configuración de seguridad
        self.session_timeout = 3600  # 1 hora en segundos
        self.max_login_attempts = 3
        self.password_min_length = 6

        # Inicializar tablas de seguridad
        self.create_security_tables()
        self.load_default_permissions()

    def create_security_tables(self):
        """Crea las tablas necesarias para el sistema de seguridad."""
        if not self.db_connection:
            return

        try:
            cursor = self.db_connection.cursor()

            # Tabla de usuarios
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='usuarios' AND xtype='U')
                CREATE TABLE usuarios (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    username VARCHAR(50) NOT NULL UNIQUE,
                    password_hash VARCHAR(255) NOT NULL,
                    email VARCHAR(100),
                    nombre VARCHAR(100),
                    apellido VARCHAR(100),
                    rol VARCHAR(50) NOT NULL DEFAULT 'USUARIO',
                    activo BIT DEFAULT 1,
                    ultimo_login DATETIME,
                    intentos_fallidos INT DEFAULT 0,
                    bloqueado BIT DEFAULT 0,
                    fecha_creacion DATETIME DEFAULT GETDATE(),
                    fecha_actualizacion DATETIME DEFAULT GETDATE()
                )
            """)

            # Tabla de roles
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='roles' AND xtype='U')
                CREATE TABLE roles (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    nombre VARCHAR(50) NOT NULL UNIQUE,
                    descripcion TEXT,
                    activo BIT DEFAULT 1,
                    fecha_creacion DATETIME DEFAULT GETDATE()
                )
            """)

            # Tabla de permisos
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='permisos' AND xtype='U')
                CREATE TABLE permisos (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    nombre VARCHAR(100) NOT NULL UNIQUE,
                    modulo VARCHAR(50) NOT NULL,
                    descripcion TEXT,
                    activo BIT DEFAULT 1,
                    fecha_creacion DATETIME DEFAULT GETDATE()
                )
            """)

            # Tabla de permisos por rol
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='rol_permisos' AND xtype='U')
                CREATE TABLE rol_permisos (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    rol_id INT NOT NULL,
                    permiso_id INT NOT NULL,
                    fecha_creacion DATETIME DEFAULT GETDATE(),
                    FOREIGN KEY (rol_id) REFERENCES roles(id),
                    FOREIGN KEY (permiso_id) REFERENCES permisos(id),
                    UNIQUE(rol_id, permiso_id)
                )
            """)

            # Tabla de sesiones
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='sesiones' AND xtype='U')
                CREATE TABLE sesiones (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    session_id VARCHAR(100) NOT NULL UNIQUE,
                    usuario_id INT NOT NULL,
                    fecha_inicio DATETIME DEFAULT GETDATE(),
                    fecha_fin DATETIME,
                    activa BIT DEFAULT 1,
                    ip_address VARCHAR(45),
                    user_agent TEXT,
                    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
                )
            """)

            # Tabla de logs de seguridad
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='logs_seguridad' AND xtype='U')
                CREATE TABLE logs_seguridad (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    usuario_id INT,
                    accion VARCHAR(100) NOT NULL,
                    modulo VARCHAR(50),
                    detalles TEXT,
                    ip_address VARCHAR(45),
                    fecha DATETIME DEFAULT GETDATE(),
                    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
                )
            """)

            self.db_connection.commit()
            print("✅ Tablas de seguridad creadas exitosamente")

        except Exception as e:
            print(f"❌ Error creando tablas de seguridad: {e}")
            if self.db_connection:
                self.db_connection.rollback()

    def load_default_permissions(self):
        """Carga permisos y roles por defecto."""
        if not self.db_connection:
            return

        try:
            cursor = self.db_connection.cursor()

            # Crear roles por defecto
            default_roles = [
                ("ADMIN", "Administrador del sistema con acceso completo"),
                ("SUPERVISOR", "Supervisor con permisos de gestión"),
                ("USUARIO", "Usuario básico con permisos limitados"),
                ("CONTABILIDAD", "Especialista en contabilidad"),
                ("INVENTARIO", "Especialista en inventario"),
                ("OBRAS", "Especialista en obras"),
            ]

            for nombre, descripcion in default_roles:
                cursor.execute(
                    """
                    IF NOT EXISTS (SELECT * FROM roles WHERE nombre = ?)
                    INSERT INTO roles (nombre, descripcion) VALUES (?, ?)
                """,
                    (nombre, nombre, descripcion),
                )

            # Crear permisos por defecto
            default_permissions = [
                # Permisos generales
                ("login", "GENERAL", "Iniciar sesión en el sistema"),
                ("logout", "GENERAL", "Cerrar sesión"),
                ("view_dashboard", "GENERAL", "Ver dashboard principal"),
                # Permisos de inventario
                ("view_inventario", "INVENTARIO", "Ver inventario"),
                ("create_inventario", "INVENTARIO", "Crear productos en inventario"),
                ("update_inventario", "INVENTARIO", "Actualizar productos"),
                ("delete_inventario", "INVENTARIO", "Eliminar productos"),
                ("manage_reservas", "INVENTARIO", "Gestionar reservas"),
                ("view_disponibilidad", "INVENTARIO", "Ver disponibilidad"),
                # Permisos de contabilidad
                ("view_contabilidad", "CONTABILIDAD", "Ver módulo de contabilidad"),
                ("create_asiento", "CONTABILIDAD", "Crear asientos contables"),
                ("create_recibo", "CONTABILIDAD", "Crear recibos"),
                ("imprimir_recibo", "CONTABILIDAD", "Imprimir recibos"),
                ("create_departamento", "CONTABILIDAD", "Crear departamentos"),
                ("create_empleado", "CONTABILIDAD", "Crear empleados"),
                ("generar_reporte", "CONTABILIDAD", "Generar reportes"),
                ("view_auditoria", "CONTABILIDAD", "Ver auditoría contable"),
                # Permisos de obras
                ("view_obras", "OBRAS", "Ver obras"),
                ("create_obra", "OBRAS", "Crear obras"),
                ("update_obra", "OBRAS", "Actualizar obras"),
                ("delete_obra", "OBRAS", "Eliminar obras"),
                ("manage_cronograma", "OBRAS", "Gestionar cronograma"),
                ("view_produccion", "OBRAS", "Ver producción"),
                # Permisos de usuarios
                ("view_usuarios", "USUARIOS", "Ver usuarios"),
                ("create_usuario", "USUARIOS", "Crear usuarios"),
                ("update_usuario", "USUARIOS", "Actualizar usuarios"),
                ("delete_usuario", "USUARIOS", "Eliminar usuarios"),
                ("manage_roles", "USUARIOS", "Gestionar roles"),
                # Permisos de configuración
                ("view_configuracion", "CONFIGURACION", "Ver configuración"),
                ("update_configuracion", "CONFIGURACION", "Actualizar configuración"),
                ("manage_system", "CONFIGURACION", "Gestionar sistema"),
                # Permisos de auditoría
                ("view_auditoria_sistema", "AUDITORIA", "Ver auditoría del sistema"),
                ("export_auditoria", "AUDITORIA", "Exportar auditoría"),
                # Permisos de compras
                ("view_compras", "COMPRAS", "Ver compras"),
                ("create_pedido", "COMPRAS", "Crear pedidos"),
                ("approve_pedido", "COMPRAS", "Aprobar pedidos"),
                # Permisos de logística
                ("view_logistica", "LOGISTICA", "Ver logística"),
                ("manage_transporte", "LOGISTICA", "Gestionar transporte"),
                # Permisos de herrajes
                ("view_herrajes", "HERRAJES", "Ver herrajes"),
                ("manage_herrajes", "HERRAJES", "Gestionar herrajes"),
                # Permisos de mantenimiento
                ("view_mantenimiento", "MANTENIMIENTO", "Ver mantenimiento"),
                ("manage_mantenimiento", "MANTENIMIENTO", "Gestionar mantenimiento"),
            ]

            for nombre, modulo, descripcion in default_permissions:
                cursor.execute(
                    """
                    IF NOT EXISTS (SELECT * FROM permisos WHERE nombre = ?)
                    INSERT INTO permisos (nombre, modulo, descripcion) VALUES (?, ?, ?)
                """,
                    (nombre, nombre, modulo, descripcion),
                )

            self.db_connection.commit()

            # Asignar permisos a roles
            self.assign_default_role_permissions()

        except Exception as e:
            print(f"❌ Error cargando permisos por defecto: {e}")
            if self.db_connection:
                self.db_connection.rollback()

    def assign_default_role_permissions(self):
        """Asigna permisos por defecto a los roles."""
        try:
            cursor = self.db_connection.cursor()

            # Permisos para ADMIN (todos los permisos)
            cursor.execute("""
                INSERT INTO rol_permisos (rol_id, permiso_id)
                SELECT r.id, p.id
                FROM roles r, permisos p
                WHERE r.nombre = 'ADMIN' AND p.activo = 1
                AND NOT EXISTS (
                    SELECT 1 FROM rol_permisos rp
                    WHERE rp.rol_id = r.id AND rp.permiso_id = p.id
                )
            """)

            # Permisos para SUPERVISOR
            supervisor_permissions = [
                "login",
                "logout",
                "view_dashboard",
                "view_inventario",
                "create_inventario",
                "update_inventario",
                "manage_reservas",
                "view_disponibilidad",
                "view_contabilidad",
                "create_asiento",
                "create_recibo",
                "imprimir_recibo",
                "generar_reporte",
                "view_obras",
                "create_obra",
                "update_obra",
                "manage_cronograma",
                "view_produccion",
                "view_compras",
                "create_pedido",
                "approve_pedido",
                "view_logistica",
                "manage_transporte",
                "view_herrajes",
                "manage_herrajes",
                "view_auditoria_sistema",
            ]

            for perm in supervisor_permissions:
                cursor.execute(
                    """
                    INSERT INTO rol_permisos (rol_id, permiso_id)
                    SELECT r.id, p.id
                    FROM roles r, permisos p
                    WHERE r.nombre = 'SUPERVISOR' AND p.nombre = ?
                    AND NOT EXISTS (
                        SELECT 1 FROM rol_permisos rp
                        WHERE rp.rol_id = r.id AND rp.permiso_id = p.id
                    )
                """,
                    (perm,),
                )

            # Permisos para USUARIO básico
            usuario_permissions = [
                "login",
                "logout",
                "view_dashboard",
                "view_inventario",
                "view_disponibilidad",
                "view_obras",
                "view_produccion",
                "view_compras",
            ]

            for perm in usuario_permissions:
                cursor.execute(
                    """
                    INSERT INTO rol_permisos (rol_id, permiso_id)
                    SELECT r.id, p.id
                    FROM roles r, permisos p
                    WHERE r.nombre = 'USUARIO' AND p.nombre = ?
                    AND NOT EXISTS (
                        SELECT 1 FROM rol_permisos rp
                        WHERE rp.rol_id = r.id AND rp.permiso_id = p.id
                    )
                """,
                    (perm,),
                )

            # Permisos para CONTABILIDAD
            contabilidad_permissions = [
                "login",
                "logout",
                "view_dashboard",
                "view_contabilidad",
                "create_asiento",
                "create_recibo",
                "imprimir_recibo",
                "create_departamento",
                "create_empleado",
                "generar_reporte",
                "view_auditoria",
                "view_inventario",
                "view_obras",
            ]

            for perm in contabilidad_permissions:
                cursor.execute(
                    """
                    INSERT INTO rol_permisos (rol_id, permiso_id)
                    SELECT r.id, p.id
                    FROM roles r, permisos p
                    WHERE r.nombre = 'CONTABILIDAD' AND p.nombre = ?
                    AND NOT EXISTS (
                        SELECT 1 FROM rol_permisos rp
                        WHERE rp.rol_id = r.id AND rp.permiso_id = p.id
                    )
                """,
                    (perm,),
                )

            # Permisos para INVENTARIO
            inventario_permissions = [
                "login",
                "logout",
                "view_dashboard",
                "view_inventario",
                "create_inventario",
                "update_inventario",
                "manage_reservas",
                "view_disponibilidad",
                "view_obras",
                "view_compras",
                "view_logistica",
            ]

            for perm in inventario_permissions:
                cursor.execute(
                    """
                    INSERT INTO rol_permisos (rol_id, permiso_id)
                    SELECT r.id, p.id
                    FROM roles r, permisos p
                    WHERE r.nombre = 'INVENTARIO' AND p.nombre = ?
                    AND NOT EXISTS (
                        SELECT 1 FROM rol_permisos rp
                        WHERE rp.rol_id = r.id AND rp.permiso_id = p.id
                    )
                """,
                    (perm,),
                )

            # Permisos para OBRAS
            obras_permissions = [
                "login",
                "logout",
                "view_dashboard",
                "view_obras",
                "create_obra",
                "update_obra",
                "manage_cronograma",
                "view_produccion",
                "view_inventario",
                "view_disponibilidad",
                "view_compras",
                "view_logistica",
            ]

            for perm in obras_permissions:
                cursor.execute(
                    """
                    INSERT INTO rol_permisos (rol_id, permiso_id)
                    SELECT r.id, p.id
                    FROM roles r, permisos p
                    WHERE r.nombre = 'OBRAS' AND p.nombre = ?
                    AND NOT EXISTS (
                        SELECT 1 FROM rol_permisos rp
                        WHERE rp.rol_id = r.id AND rp.permiso_id = p.id
                    )
                """,
                    (perm,),
                )

            self.db_connection.commit()

        except Exception as e:
            print(f"❌ Error asignando permisos por defecto: {e}")
            if self.db_connection:
                self.db_connection.rollback()

    def create_default_admin(self):
        """Crea un usuario administrador por defecto."""
        try:
            cursor = self.db_connection.cursor()

            # Verificar si ya existe un admin
            cursor.execute("SELECT COUNT(*) FROM usuarios WHERE rol = 'ADMIN'")
            admin_count = cursor.fetchone()[0]

            if admin_count == 0:
                # Crear admin por defecto
                password_hash = self.hash_password("admin")
                cursor.execute(
                    """
                    INSERT INTO usuarios (username, password_hash, email, nombre, apellido, rol, activo)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        "admin",
                        password_hash,
                        "admin@stockapp.com",
                        "Administrador",
                        "Sistema",
                        "ADMIN",
                        1,
                    ),
                )

                self.db_connection.commit()
                print(
                    "✅ Usuario administrador creado - Usuario: admin, Contraseña: admin"
                )

        except Exception as e:
            print(f"❌ Error creando admin por defecto: {e}")
            if self.db_connection:
                self.db_connection.rollback()

    def hash_password(self, password: str) -> str:
        """Genera hash de contraseña usando SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()

    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verifica una contraseña contra su hash."""
        return hashlib.sha256(password.encode()).hexdigest() == password_hash

    def login(self, username: str, password: str) -> bool:
        """Autentica un usuario."""
        try:
            cursor = self.db_connection.cursor()

            # Obtener datos del usuario
            cursor.execute(
                """
                SELECT id, username, password_hash, rol, activo, bloqueado, intentos_fallidos
                FROM usuarios
                WHERE username = ?
            """,
                (username,),
            )

            user_data = cursor.fetchone()

            if not user_data:
                self.log_security_event(
                    None,
                    "LOGIN_FAILED",
                    "GENERAL",
                    f"Usuario no encontrado: {username}",
                )
                return False

            (
                user_id,
                username,
                password_hash,
                rol,
                activo,
                bloqueado,
                intentos_fallidos,
            ) = user_data

            # Verificar si el usuario está activo
            if not activo:
                self.log_security_event(
                    user_id, "LOGIN_FAILED", "GENERAL", f"Usuario inactivo: {username}"
                )
                return False

            # Verificar si el usuario está bloqueado
            if bloqueado:
                self.log_security_event(
                    user_id, "LOGIN_FAILED", "GENERAL", f"Usuario bloqueado: {username}"
                )
                return False

            # Verificar contraseña
            if not self.verify_password(password, password_hash):
                # Incrementar intentos fallidos
                intentos_fallidos += 1
                bloqueado = intentos_fallidos >= self.max_login_attempts

                cursor.execute(
                    """
                    UPDATE usuarios
                    SET intentos_fallidos = ?, bloqueado = ?
                    WHERE id = ?
                """,
                    (intentos_fallidos, bloqueado, user_id),
                )

                self.db_connection.commit()

                self.log_security_event(
                    user_id,
                    "LOGIN_FAILED",
                    "GENERAL",
                    f"Contraseña incorrecta: {username}",
                )
                return False

            # Login exitoso
            self.current_user = username
            self.current_role = rol
            self.login_time = datetime.now()
            self.session_id = str(uuid.uuid4())

            # Resetear intentos fallidos
            cursor.execute(
                """
                UPDATE usuarios
                SET intentos_fallidos = 0, bloqueado = 0, ultimo_login = GETDATE()
                WHERE id = ?
            """,
                (user_id,),
            )

            # Crear sesión
            cursor.execute(
                """
                INSERT INTO sesiones (session_id, usuario_id, activa)
                VALUES (?, ?, ?)
            """,
                (self.session_id, user_id, 1),
            )

            self.db_connection.commit()

            # Cargar permisos
            self.load_user_permissions(username)

            # Log y señal
            self.log_security_event(
                user_id, "LOGIN_SUCCESS", "GENERAL", f"Login exitoso: {username}"
            )
            self.user_logged_in.emit(username, rol)

            return True

        except Exception as e:
            print(f"❌ Error en login: {e}")
            return False

    def logout(self) -> bool:
        """Cierra la sesión actual."""
        try:
            if self.current_user and self.session_id:
                cursor = self.db_connection.cursor()

                # Cerrar sesión
                cursor.execute(
                    """
                    UPDATE sesiones
                    SET activa = 0, fecha_fin = GETDATE()
                    WHERE session_id = ?
                """,
                    (self.session_id,),
                )

                self.db_connection.commit()

                # Log
                self.log_security_event(
                    None, "LOGOUT", "GENERAL", f"Logout: {self.current_user}"
                )

                # Señal
                self.user_logged_out.emit(self.current_user)

                # Limpiar estado
                old_user = self.current_user
                self.current_user = None
                self.current_role = None
                self.session_id = None
                self.login_time = None
                self.permissions_cache = {}

                return True

        except Exception as e:
            print(f"❌ Error en logout: {e}")

        return False

    def load_user_permissions(self, username: str):
        """Carga los permisos del usuario en caché."""
        try:
            cursor = self.db_connection.cursor()

            cursor.execute(
                """
                SELECT DISTINCT p.nombre, p.modulo
                FROM usuarios u
                JOIN roles r ON u.rol = r.nombre
                JOIN rol_permisos rp ON r.id = rp.rol_id
                JOIN permisos p ON rp.permiso_id = p.id
                WHERE u.username = ? AND u.activo = 1 AND r.activo = 1 AND p.activo = 1
            """,
                (username,),
            )

            permissions = cursor.fetchall()

            # Organizar permisos por módulo
            self.permissions_cache = {}
            for perm_name, module in permissions:
                if module not in self.permissions_cache:
                    self.permissions_cache[module] = set()
                self.permissions_cache[module].add(perm_name)

        except Exception as e:
            print(f"❌ Error cargando permisos: {e}")
            self.permissions_cache = {}

    def has_permission(self, permission: str, module: str = None) -> bool:
        """Verifica si el usuario actual tiene un permiso específico."""
        if not self.current_user:
            return False

        if self.current_role == "ADMIN":
            return True

        if module:
            return (
                module in self.permissions_cache
                and permission in self.permissions_cache[module]
            )
        else:
            # Buscar en todos los módulos
            for module_perms in self.permissions_cache.values():
                if permission in module_perms:
                    return True
            return False

    def get_user_permissions(self, module: str = None) -> Set[str]:
        """Obtiene los permisos del usuario actual."""
        if not self.current_user:
            return set()

        if self.current_role == "ADMIN":
            # Admin tiene todos los permisos
            return set(["*"])

        if module:
            return self.permissions_cache.get(module, set())
        else:
            # Retornar todos los permisos
            all_perms = set()
            for module_perms in self.permissions_cache.values():
                all_perms.update(module_perms)
            return all_perms

    def is_session_valid(self) -> bool:
        """Verifica si la sesión actual es válida."""
        if not self.current_user or not self.session_id or not self.login_time:
            return False

        # Verificar timeout
        if datetime.now() - self.login_time > timedelta(seconds=self.session_timeout):
            self.logout()
            return False

        try:
            cursor = self.db_connection.cursor()
            cursor.execute(
                """
                SELECT activa FROM sesiones
                WHERE session_id = ? AND activa = 1
            """,
                (self.session_id,),
            )

            return cursor.fetchone() is not None

        except Exception as e:
            print(f"❌ Error verificando sesión: {e}")
            return False

    def log_security_event(
        self, usuario_id: int, accion: str, modulo: str, detalles: str
    ):
        """Registra un evento de seguridad."""
        try:
            cursor = self.db_connection.cursor()
            cursor.execute(
                """
                INSERT INTO logs_seguridad (usuario_id, accion, modulo, detalles)
                VALUES (?, ?, ?, ?)
            """,
                (usuario_id, accion, modulo, detalles),
            )

            self.db_connection.commit()

        except Exception as e:
            print(f"❌ Error logging evento de seguridad: {e}")

    def get_current_user(self) -> Optional[Dict]:
        """Obtiene los datos completos del usuario actual."""
        if not self.current_user:
            return None

        try:
            cursor = self.db_connection.cursor()
            cursor.execute(
                """
                SELECT id, username, email, nombre, apellido, rol, activo,
                       ultimo_login, fecha_creacion
                FROM usuarios
                WHERE username = ?
            """,
                (self.current_user,),
            )

            row = cursor.fetchone()
            if row:
                return {
                    "id": row[0],
                    "username": row[1],
                    "email": row[2],
                    "nombre": row[3],
                    "apellido": row[4],
                    "rol": row[5],
                    "activo": bool(row[6]),
                    "ultimo_login": row[7],
                    "fecha_creacion": row[8],
                }
            return None

        except Exception as e:
            print(f"❌ Error obteniendo datos del usuario actual: {e}")
            return None

    def get_user_modules(self, user_id: int) -> List[str]:
        """Obtiene los módulos a los que tiene acceso un usuario."""
        try:
            cursor = self.db_connection.cursor()
            cursor.execute(
                """
                SELECT DISTINCT p.modulo
                FROM usuarios u
                JOIN roles r ON u.rol = r.nombre
                JOIN rol_permisos rp ON r.id = rp.rol_id
                JOIN permisos p ON rp.permiso_id = p.id
                WHERE u.id = ? AND u.activo = 1 AND r.activo = 1 AND p.activo = 1
            """,
                (user_id,),
            )

            modules = [row[0] for row in cursor.fetchall()]

            # Si es admin, dar acceso a todos los módulos
            if self.current_role == "ADMIN":
                modules = [
                    "INVENTARIO",
                    "CONTABILIDAD",
                    "OBRAS",
                    "USUARIOS",
                    "AUDITORIA",
                    "GENERAL",
                ]

            return modules

        except Exception as e:
            print(f"❌ Error obteniendo módulos del usuario: {e}")
            return []

    def get_current_user_string(self) -> Optional[str]:
        """Obtiene el nombre del usuario actual (para compatibilidad)."""
        return self.current_user

    def get_current_role(self) -> Optional[str]:
        """Obtiene el rol actual."""
        return self.current_role

    def get_users(self) -> List[Dict]:
        """Obtiene la lista de usuarios."""
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                SELECT id, username, email, nombre, apellido, rol, activo,
                       ultimo_login, bloqueado, fecha_creacion
                FROM usuarios
                ORDER BY username
            """)

            users = []
            for row in cursor.fetchall():
                users.append(
                    {
                        "id": row[0],
                        "username": row[1],
                        "email": row[2],
                        "nombre": row[3],
                        "apellido": row[4],
                        "rol": row[5],
                        "activo": bool(row[6]),
                        "ultimo_login": row[7],
                        "bloqueado": bool(row[8]),
                        "fecha_creacion": row[9],
                    }
                )

            return users

        except Exception as e:
            print(f"❌ Error obteniendo usuarios: {e}")
            return []

    def create_user(
        self,
        username: str,
        password: str,
        email: str,
        nombre: str,
        apellido: str,
        rol: str,
    ) -> bool:
        """Crea un nuevo usuario."""
        try:
            cursor = self.db_connection.cursor()

            # Verificar si el usuario ya existe
            cursor.execute(
                "SELECT COUNT(*) FROM usuarios WHERE username = ?", (username,)
            )
            if cursor.fetchone()[0] > 0:
                return False

            # Crear usuario
            password_hash = self.hash_password(password)
            cursor.execute(
                """
                INSERT INTO usuarios (username, password_hash, email, nombre, apellido, rol, activo)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (username, password_hash, email, nombre, apellido, rol, 1),
            )

            self.db_connection.commit()

            # Log
            self.log_security_event(
                None, "USER_CREATED", "USUARIOS", f"Usuario creado: {username}"
            )

            return True

        except Exception as e:
            print(f"❌ Error creando usuario: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return False

    def update_user(self, user_id: int, **kwargs) -> bool:
        """Actualiza un usuario."""
        try:
            cursor = self.db_connection.cursor()

            # Construir query dinámicamente
            fields = []
            values = []

            for field, value in kwargs.items():
                if field == "password":
                    fields.append("password_hash = ?")
                    values.append(self.hash_password(value))
                elif field in [
                    "username",
                    "email",
                    "nombre",
                    "apellido",
                    "rol",
                    "activo",
                    "bloqueado",
                ]:
                    fields.append(f"{field} = ?")
                    values.append(value)

            if not fields:
                return False

            values.append(user_id)

            query = f"UPDATE usuarios SET {', '.join(fields)} WHERE id = ?"
            cursor.execute(query, values)

            self.db_connection.commit()

            # Log
            self.log_security_event(
                user_id, "USER_UPDATED", "USUARIOS", f"Usuario actualizado: {kwargs}"
            )

            return True

        except Exception as e:
            print(f"❌ Error actualizando usuario: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return False

    def get_security_logs(self, limit: int = 100) -> List[Dict]:
        """Obtiene logs de seguridad."""
        try:
            cursor = self.db_connection.cursor()
            cursor.execute(
                """
                SELECT ls.id, u.username, ls.accion, ls.modulo, ls.detalles,
                       ls.ip_address, ls.fecha
                FROM logs_seguridad ls
                LEFT JOIN usuarios u ON ls.usuario_id = u.id
                ORDER BY ls.fecha DESC
                OFFSET 0 ROWS FETCH NEXT ? ROWS ONLY
            """,
                (limit,),
            )

            logs = []
            for row in cursor.fetchall():
                logs.append(
                    {
                        "id": row[0],
                        "username": row[1],
                        "accion": row[2],
                        "modulo": row[3],
                        "detalles": row[4],
                        "ip_address": row[5],
                        "fecha": row[6],
                    }
                )

            return logs

        except Exception as e:
            print(f"❌ Error obteniendo logs de seguridad: {e}")
            return []


# Instancia global del gestor de seguridad
security_manager = None


def get_security_manager() -> SecurityManager:
    """Obtiene la instancia global del gestor de seguridad."""
    global security_manager
    return security_manager


def init_security_manager(db_connection) -> SecurityManager:
    """Inicializa el gestor de seguridad."""
    global security_manager
    security_manager = SecurityManager(db_connection)
    security_manager.create_default_admin()
    return security_manager


def initialize_security_manager(db_connection=None) -> SecurityManager:
    """Inicializa el gestor de seguridad - alias para init_security_manager."""
    if not db_connection:
        # Usar conexión por defecto
        from src.core.config import DATABASE_CONFIG
        from src.core.database import DatabaseConnection

        db_connection = DatabaseConnection(
            server=DATABASE_CONFIG["server"],
            database=DATABASE_CONFIG["databases"]["users"],
            username=DATABASE_CONFIG["username"],
            password=DATABASE_CONFIG["password"],
            trusted=False,
        )
        db_connection.connect()

    manager = init_security_manager(db_connection)
    # Forzar creación de admin cada vez
    try:
        manager.create_default_admin()
    except Exception as e:
        print(f"[SECURITY] Error creando admin por defecto: {e}")
    return manager
