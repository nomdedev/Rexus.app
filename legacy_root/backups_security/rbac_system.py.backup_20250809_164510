"""
Sistema de Control de Acceso Basado en Roles (RBAC) - Rexus.app v2.0.0

FUNCIONALIDADES DE SEGURIDAD:
[CHECK] Sistema granular de roles y permisos
[CHECK] Control de acceso a acciones sensibles
[CHECK] Jerarquía de roles con herencia de permisos
[CHECK] Validación de permisos en tiempo real
[CHECK] Gestión centralizada de autorizaciones
"""

from enum import Enum
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass


class Permission(Enum):
    """Permisos granulares del sistema."""
    # Permisos generales
    LOGIN = "login"
    LOGOUT = "logout"
    VIEW_DASHBOARD = "view_dashboard"
    
    # Gestión de usuarios
    VIEW_USERS = "view_users"
    CREATE_USER = "create_user"
    UPDATE_USER = "update_user"
    DELETE_USER = "delete_user"
    RESET_PASSWORD = "reset_password"
    LOCK_USER = "lock_user"
    UNLOCK_USER = "unlock_user"
    ASSIGN_ROLES = "assign_roles"
    
    # Inventario
    VIEW_INVENTORY = "view_inventory"
    CREATE_INVENTORY = "create_inventory"
    UPDATE_INVENTORY = "update_inventory"
    DELETE_INVENTORY = "delete_inventory"
    MANAGE_RESERVATIONS = "manage_reservations"
    VIEW_AVAILABILITY = "view_availability"
    EXPORT_INVENTORY = "export_inventory"
    
    # Obras
    VIEW_PROJECTS = "view_projects"
    CREATE_PROJECT = "create_project"
    UPDATE_PROJECT = "update_project"
    DELETE_PROJECT = "delete_project"
    MANAGE_SCHEDULE = "manage_schedule"
    VIEW_PRODUCTION = "view_production"
    APPROVE_PROJECT = "approve_project"
    
    # Administración/Contabilidad
    VIEW_ACCOUNTING = "view_accounting"
    CREATE_ENTRY = "create_entry"
    CREATE_RECEIPT = "create_receipt"
    PRINT_RECEIPT = "print_receipt"
    CREATE_DEPARTMENT = "create_department"
    CREATE_EMPLOYEE = "create_employee"
    GENERATE_REPORT = "generate_report"
    VIEW_AUDIT = "view_audit"
    APPROVE_TRANSACTIONS = "approve_transactions"
    
    # Compras y Pedidos
    VIEW_PURCHASES = "view_purchases"
    CREATE_ORDER = "create_order"
    APPROVE_ORDER = "approve_order"
    CANCEL_ORDER = "cancel_order"
    MANAGE_SUPPLIERS = "manage_suppliers"
    
    # Logística
    VIEW_LOGISTICS = "view_logistics"
    MANAGE_TRANSPORT = "manage_transport"
    SCHEDULE_DELIVERY = "schedule_delivery"
    TRACK_SHIPMENTS = "track_shipments"
    
    # Herrajes y Vidrios
    VIEW_HARDWARE = "view_hardware"
    MANAGE_HARDWARE = "manage_hardware"
    VIEW_GLASS = "view_glass"
    MANAGE_GLASS = "manage_glass"
    
    # Mantenimiento
    VIEW_MAINTENANCE = "view_maintenance"
    MANAGE_MAINTENANCE = "manage_maintenance"
    SCHEDULE_MAINTENANCE = "schedule_maintenance"
    
    # Configuración del sistema
    VIEW_CONFIG = "view_config"
    UPDATE_CONFIG = "update_config"
    MANAGE_SYSTEM = "manage_system"
    BACKUP_SYSTEM = "backup_system"
    RESTORE_SYSTEM = "restore_system"
    
    # Auditoría y seguridad
    VIEW_AUDIT_LOGS = "view_audit_logs"
    EXPORT_AUDIT = "export_audit"
    MANAGE_SECURITY = "manage_security"
    VIEW_SENSITIVE_DATA = "view_sensitive_data"


class Role(Enum):
    """Roles del sistema con jerarquía."""
    # Roles jerárquicos (mayor a menor autoridad)
    SUPER_ADMIN = "SUPER_ADMIN"
    ADMIN = "ADMIN"
    SUPERVISOR = "SUPERVISOR"
    SPECIALIST = "SPECIALIST"
    OPERATOR = "OPERATOR"
    USER = "USER"
    GUEST = "GUEST"
    
    # Roles especializados
    ACCOUNTANT = "ACCOUNTANT"
    INVENTORY_MANAGER = "INVENTORY_MANAGER"
    PROJECT_MANAGER = "PROJECT_MANAGER"
    LOGISTICS_MANAGER = "LOGISTICS_MANAGER"


@dataclass
class RoleDefinition:
    """Definición de un rol con sus permisos."""
    name: Role
    display_name: str
    description: str
    permissions: Set[Permission]
    inherits_from: Optional[Role] = None


class RBACSystem:
    """Sistema de Control de Acceso Basado en Roles."""

    def __init__(self, db_connection=None):
        self.db_connection = db_connection
        self._initialize_roles()
        self._create_rbac_tables()

    def _initialize_roles(self):
        """Inicializa las definiciones de roles y permisos."""
        
        # Permisos básicos para todos los usuarios
        basic_permissions = {
            Permission.LOGIN,
            Permission.LOGOUT,
            Permission.VIEW_DASHBOARD
        }
        
        # Permisos de solo lectura
        read_permissions = basic_permissions | {
            Permission.VIEW_INVENTORY,
            Permission.VIEW_AVAILABILITY,
            Permission.VIEW_PROJECTS,
            Permission.VIEW_PRODUCTION,
            Permission.VIEW_PURCHASES,
            Permission.VIEW_LOGISTICS
        }
        
        # Permisos operativos
        operator_permissions = read_permissions | {
            Permission.CREATE_INVENTORY,
            Permission.UPDATE_INVENTORY,
            Permission.MANAGE_RESERVATIONS,
            Permission.CREATE_PROJECT,
            Permission.UPDATE_PROJECT,
            Permission.CREATE_ORDER
        }
        
        # Permisos de especialista
        specialist_permissions = operator_permissions | {
            Permission.DELETE_INVENTORY,
            Permission.DELETE_PROJECT,
            Permission.APPROVE_ORDER,
            Permission.MANAGE_SUPPLIERS,
            Permission.MANAGE_TRANSPORT,
            Permission.GENERATE_REPORT
        }
        
        # Permisos de supervisor
        supervisor_permissions = specialist_permissions | {
            Permission.VIEW_USERS,
            Permission.APPROVE_PROJECT,
            Permission.APPROVE_TRANSACTIONS,
            Permission.MANAGE_HARDWARE,
            Permission.MANAGE_GLASS,
            Permission.MANAGE_MAINTENANCE,
            Permission.EXPORT_INVENTORY,
            Permission.VIEW_AUDIT
        }
        
        # Permisos de administrador
        admin_permissions = supervisor_permissions | {
            Permission.CREATE_USER,
            Permission.UPDATE_USER,
            Permission.RESET_PASSWORD,
            Permission.LOCK_USER,
            Permission.UNLOCK_USER,
            Permission.VIEW_CONFIG,
            Permission.UPDATE_CONFIG,
            Permission.VIEW_AUDIT_LOGS,
            Permission.EXPORT_AUDIT,
            Permission.BACKUP_SYSTEM
        }
        
        # Permisos de super administrador
        super_admin_permissions = admin_permissions | {
            Permission.DELETE_USER,
            Permission.ASSIGN_ROLES,
            Permission.MANAGE_SYSTEM,
            Permission.RESTORE_SYSTEM,
            Permission.MANAGE_SECURITY,
            Permission.VIEW_SENSITIVE_DATA
        }
        
        # Permisos especializados
        accountant_permissions = read_permissions | {
            Permission.VIEW_ACCOUNTING,
            Permission.CREATE_ENTRY,
            Permission.CREATE_RECEIPT,
            Permission.PRINT_RECEIPT,
            Permission.CREATE_DEPARTMENT,
            Permission.CREATE_EMPLOYEE,
            Permission.GENERATE_REPORT,
            Permission.VIEW_AUDIT
        }
        
        inventory_manager_permissions = operator_permissions | {
            Permission.DELETE_INVENTORY,
            Permission.EXPORT_INVENTORY,
            Permission.MANAGE_SUPPLIERS
        }
        
        project_manager_permissions = specialist_permissions | {
            Permission.APPROVE_PROJECT,
            Permission.MANAGE_SCHEDULE,
            Permission.DELETE_PROJECT
        }
        
        logistics_manager_permissions = specialist_permissions | {
            Permission.SCHEDULE_DELIVERY,
            Permission.TRACK_SHIPMENTS,
            Permission.MANAGE_TRANSPORT
        }

        # Definir roles
        self.role_definitions = {
            Role.GUEST: RoleDefinition(
                Role.GUEST, "Invitado", "Acceso muy limitado solo para demostración",
                basic_permissions
            ),
            Role.USER: RoleDefinition(
                Role.USER, "Usuario", "Usuario básico con permisos de lectura",
                read_permissions
            ),
            Role.OPERATOR: RoleDefinition(
                Role.OPERATOR, "Operador", "Operador con permisos básicos de creación",
                operator_permissions
            ),
            Role.SPECIALIST: RoleDefinition(
                Role.SPECIALIST, "Especialista", "Especialista con permisos avanzados",
                specialist_permissions
            ),
            Role.SUPERVISOR: RoleDefinition(
                Role.SUPERVISOR, "Supervisor", "Supervisor con permisos de gestión",
                supervisor_permissions
            ),
            Role.ADMIN: RoleDefinition(
                Role.ADMIN, "Administrador", "Administrador del sistema",
                admin_permissions
            ),
            Role.SUPER_ADMIN: RoleDefinition(
                Role.SUPER_ADMIN, "Super Administrador", "Control total del sistema",
                super_admin_permissions
            ),
            
            # Roles especializados
            Role.ACCOUNTANT: RoleDefinition(
                Role.ACCOUNTANT, "Contable", "Especialista en contabilidad",
                accountant_permissions
            ),
            Role.INVENTORY_MANAGER: RoleDefinition(
                Role.INVENTORY_MANAGER, "Gestor de Inventario", "Gestión completa de inventario",
                inventory_manager_permissions
            ),
            Role.PROJECT_MANAGER: RoleDefinition(
                Role.PROJECT_MANAGER, "Gestor de Proyectos", "Gestión completa de obras/proyectos",
                project_manager_permissions
            ),
            Role.LOGISTICS_MANAGER: RoleDefinition(
                Role.LOGISTICS_MANAGER, "Gestor de Logística", "Gestión completa de logística",
                logistics_manager_permissions
            )
        }

    def _create_rbac_tables(self):
        """Crea las tablas necesarias para RBAC."""
        if not self.db_connection:
            return

        try:
            cursor = self.db_connection.connection.cursor()

            # Tabla de roles
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='rbac_roles' AND xtype='U')
                CREATE TABLE rbac_roles (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    nombre NVARCHAR(50) UNIQUE NOT NULL,
                    display_name NVARCHAR(100) NOT NULL,
                    descripcion NVARCHAR(255),
                    activo BIT DEFAULT 1,
                    fecha_creacion DATETIME DEFAULT GETDATE()
                )
            """)

            # Tabla de permisos
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='rbac_permissions' AND xtype='U')
                CREATE TABLE rbac_permissions (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    nombre NVARCHAR(100) UNIQUE NOT NULL,
                    display_name NVARCHAR(100) NOT NULL,
                    modulo NVARCHAR(50) NOT NULL,
                    descripcion NVARCHAR(255),
                    es_sensible BIT DEFAULT 0,
                    activo BIT DEFAULT 1,
                    fecha_creacion DATETIME DEFAULT GETDATE()
                )
            """)

            # Tabla de roles-permisos
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='rbac_role_permissions' AND xtype='U')
                CREATE TABLE rbac_role_permissions (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    role_id INT NOT NULL,
                    permission_id INT NOT NULL,
                    granted_by INT NULL,
                    fecha_asignacion DATETIME DEFAULT GETDATE(),
                    FOREIGN KEY (role_id) REFERENCES rbac_roles(id),
                    FOREIGN KEY (permission_id) REFERENCES rbac_permissions(id),
                    FOREIGN KEY (granted_by) REFERENCES usuarios(id),
                    UNIQUE(role_id, permission_id)
                )
            """)

            # Tabla de usuarios-roles
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='rbac_user_roles' AND xtype='U')
                CREATE TABLE rbac_user_roles (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    usuario_id INT NOT NULL,
                    role_id INT NOT NULL,
                    assigned_by INT NOT NULL,
                    fecha_asignacion DATETIME DEFAULT GETDATE(),
                    fecha_expiracion DATETIME NULL,
                    activo BIT DEFAULT 1,
                    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
                    FOREIGN KEY (role_id) REFERENCES rbac_roles(id),
                    FOREIGN KEY (assigned_by) REFERENCES usuarios(id),
                    UNIQUE(usuario_id, role_id)
                )
            """)

            # Índices
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_rbac_user_roles_usuario ON rbac_user_roles(usuario_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_rbac_role_permissions_role ON rbac_role_permissions(role_id)")

            self.db_connection.connection.commit()
            print("[CHECK] [RBAC] Tablas de control de acceso creadas/verificadas")

        except Exception as e:
            print(f"[ERROR] [RBAC] Error creando tablas RBAC: {e}")
            if self.db_connection:
                self.db_connection.connection.rollback()

    def has_permission(self, usuario_id: int, permission: Permission, 
                       audit_access: bool = True) -> bool:
        """
        Verifica si un usuario tiene un permiso específico.
        
        Args:
            usuario_id: ID del usuario
            permission: Permiso a verificar
            audit_access: Si auditar el acceso a permisos sensibles
        """
        if not self.db_connection:
            return False

        try:
            cursor = self.db_connection.connection.cursor()

            # Obtener roles activos del usuario
            cursor.execute("""
                SELECT r.nombre
                FROM rbac_user_roles ur
                JOIN rbac_roles r ON ur.role_id = r.id
                WHERE ur.usuario_id = ? AND ur.activo = 1 
                AND (ur.fecha_expiracion IS NULL OR ur.fecha_expiracion > GETDATE())
                AND r.activo = 1
            """, (usuario_id,))

            user_roles = [row[0] for row in cursor.fetchall()]

            # Verificar permisos en cada rol
            for role_name in user_roles:
                try:
                    role = Role(role_name)
                    if role in self.role_definitions:
                        role_permissions = self.role_definitions[role].permissions
                        if permission in role_permissions:
                            # Auditar acceso a permisos sensibles
                            if audit_access and self._is_sensitive_permission(permission):
                                self._audit_permission_check(usuario_id, permission, True)
                            return True
                except ValueError:
                    # Rol no válido, continuar con otros roles
                    continue

            # Auditar denegación de permisos sensibles
            if audit_access and self._is_sensitive_permission(permission):
                self._audit_permission_check(usuario_id, permission, False)

            return False

        except Exception as e:
            print(f"[ERROR] [RBAC] Error verificando permiso: {e}")
            return False

    def get_user_permissions(self, usuario_id: int) -> Set[Permission]:
        """Obtiene todos los permisos de un usuario."""
        if not self.db_connection:
            return set()

        try:
            cursor = self.db_connection.connection.cursor()

            # Obtener roles del usuario
            cursor.execute("""
                SELECT r.nombre
                FROM rbac_user_roles ur
                JOIN rbac_roles r ON ur.role_id = r.id
                WHERE ur.usuario_id = ? AND ur.activo = 1 
                AND (ur.fecha_expiracion IS NULL OR ur.fecha_expiracion > GETDATE())
                AND r.activo = 1
            """, (usuario_id,))

            user_roles = [row[0] for row in cursor.fetchall()]
            all_permissions = set()

            # Combinar permisos de todos los roles
            for role_name in user_roles:
                try:
                    role = Role(role_name)
                    if role in self.role_definitions:
                        all_permissions.update(self.role_definitions[role].permissions)
                except ValueError:
                    continue

            return all_permissions

        except Exception as e:
            print(f"[ERROR] [RBAC] Error obteniendo permisos de usuario: {e}")
            return set()

    def assign_role_to_user(self, usuario_id: int, role: Role, 
                            assigned_by: int) -> bool:
        """Asigna un rol a un usuario."""
        if not self.db_connection:
            return False

        try:
            cursor = self.db_connection.connection.cursor()

            # Verificar que el rol existe
            cursor.execute("SELECT id FROM rbac_roles WHERE nombre = ?", (role.value,))
            role_row = cursor.fetchone()
            
            if not role_row:
                print(f"[ERROR] [RBAC] Rol no encontrado: {role.value}")
                return False

            role_id = role_row[0]

            # Insertar asignación de rol
            cursor.execute("""
                INSERT INTO rbac_user_roles (usuario_id, role_id, assigned_by)
                VALUES (?, ?, ?)
            """, (usuario_id, role_id, assigned_by))

            self.db_connection.connection.commit()

            # Auditar asignación de rol
            self._audit_role_assignment(usuario_id, role, assigned_by, "ASSIGNED")

            print(f"[CHECK] [RBAC] Rol {role.value} asignado a usuario {usuario_id}")
            return True

        except Exception as e:
            print(f"[ERROR] [RBAC] Error asignando rol: {e}")
            if self.db_connection:
                self.db_connection.connection.rollback()
            return False

    def revoke_role_from_user(self, usuario_id: int, role: Role, 
                              revoked_by: int) -> bool:
        """Revoca un rol de un usuario."""
        if not self.db_connection:
            return False

        try:
            cursor = self.db_connection.connection.cursor()

            # Desactivar el rol del usuario
            cursor.execute("""
                UPDATE rbac_user_roles 
                SET activo = 0 
                WHERE usuario_id = ? AND role_id = (
                    SELECT id FROM rbac_roles WHERE nombre = ?
                )
            """, (usuario_id, role.value))

            self.db_connection.connection.commit()

            # Auditar revocación de rol
            self._audit_role_assignment(usuario_id, role, revoked_by, "REVOKED")

            print(f"[CHECK] [RBAC] Rol {role.value} revocado de usuario {usuario_id}")
            return True

        except Exception as e:
            print(f"[ERROR] [RBAC] Error revocando rol: {e}")
            if self.db_connection:
                self.db_connection.connection.rollback()
            return False

    def _is_sensitive_permission(self, permission: Permission) -> bool:
        """Determina si un permiso es sensible y requiere auditoría."""
        sensitive_permissions = {
            Permission.DELETE_USER,
            Permission.ASSIGN_ROLES,
            Permission.MANAGE_SECURITY,
            Permission.VIEW_SENSITIVE_DATA,
            Permission.BACKUP_SYSTEM,
            Permission.RESTORE_SYSTEM,
            Permission.MANAGE_SYSTEM,
            Permission.VIEW_AUDIT_LOGS,
            Permission.APPROVE_TRANSACTIONS,
            Permission.RESET_PASSWORD
        }
        return permission in sensitive_permissions

    def _audit_permission_check(self, usuario_id: int, permission: Permission, 
                                granted: bool):
        """Audita verificaciones de permisos sensibles."""
        try:
            from rexus.core.audit_system import get_audit_system, AuditEvent, AuditLevel
            
            audit = get_audit_system()
            if audit:
                audit.log_event(
                    event_type=AuditEvent.PERMISSION_GRANTED if granted else AuditEvent.UNAUTHORIZED_ACCESS,
                    level=AuditLevel.SECURITY,
                    modulo="RBAC",
                    accion=f"Verificación de permiso: {permission.value}",
                    resultado="SUCCESS" if granted else "DENIED",
                    usuario_id=usuario_id,
                    permiso_verificado=permission.value,
                    acceso_concedido=granted
                )
        except Exception as e:
            print(f"[ERROR] [RBAC] Error auditando verificación de permiso: {e}")

    def _audit_role_assignment(self, usuario_id: int, role: Role, 
                               assigned_by: int, action: str):
        """Audita asignaciones/revocaciones de roles."""
        try:
            from rexus.core.audit_system import get_audit_system, AuditEvent, AuditLevel
            
            audit = get_audit_system()
            if audit:
                audit.log_event(
                    event_type=AuditEvent.ROLE_ASSIGNED if action == "ASSIGNED" else AuditEvent.ROLE_REMOVED,
                    level=AuditLevel.CRITICAL,
                    modulo="RBAC",
                    accion=f"Rol {action.lower()}: {role.value}",
                    resultado="SUCCESS",
                    usuario_id=assigned_by,
                    usuario_afectado=usuario_id,
                    rol_modificado=role.value,
                    accion_realizada=action
                )
        except Exception as e:
            print(f"[ERROR] [RBAC] Error auditando asignación de rol: {e}")

    def initialize_default_roles(self):
        """Inicializa los roles por defecto en la base de datos."""
        if not self.db_connection:
            return

        try:
            cursor = self.db_connection.connection.cursor()

            # Insertar roles
            for role_def in self.role_definitions.values():
                cursor.execute("""
                    IF NOT EXISTS (SELECT * FROM rbac_roles WHERE nombre = ?)
                    INSERT INTO rbac_roles (nombre, display_name, descripcion)
                    VALUES (?, ?, ?)
                """, (role_def.name.value, role_def.name.value, 
                      role_def.display_name, role_def.description))

            # Insertar permisos
            for permission in Permission:
                # Determinar módulo basado en el nombre del permiso
                modulo = self._get_permission_module(permission)
                es_sensible = self._is_sensitive_permission(permission)
                
                cursor.execute("""
                    IF NOT EXISTS (SELECT * FROM rbac_permissions WHERE nombre = ?)
                    INSERT INTO rbac_permissions (nombre, display_name, modulo, es_sensible)
                    VALUES (?, ?, ?, ?)
                """, (permission.value, permission.value, permission.value, modulo, es_sensible))

            self.db_connection.connection.commit()
            print("[CHECK] [RBAC] Roles y permisos por defecto inicializados")

        except Exception as e:
            print(f"[ERROR] [RBAC] Error inicializando roles por defecto: {e}")
            if self.db_connection:
                self.db_connection.connection.rollback()

    def _get_permission_module(self, permission: Permission) -> str:
        """Determina el módulo de un permiso basado en su nombre."""
        permission_name = permission.value.lower()
        
        if any(word in permission_name for word in ['user', 'usuario', 'role', 'rol']):
            return "USUARIOS"
        elif any(word in permission_name for word in ['inventory', 'inventario']):
            return "INVENTARIO"
        elif any(word in permission_name for word in ['project', 'proyecto', 'obra']):
            return "OBRAS"
        elif any(word in permission_name for word in ['accounting', 'contabilidad', 'entry', 'receipt']):
            return "ADMINISTRACION"
        elif any(word in permission_name for word in ['purchase', 'compra', 'order', 'pedido']):
            return "COMPRAS"
        elif any(word in permission_name for word in ['logistics', 'logistica', 'transport']):
            return "LOGISTICA"
        elif any(word in permission_name for word in ['hardware', 'herraje', 'glass', 'vidrio']):
            return "MATERIALES"
        elif any(word in permission_name for word in ['maintenance', 'mantenimiento']):
            return "MANTENIMIENTO"
        elif any(word in permission_name for word in ['config', 'configuracion', 'system', 'sistema']):
            return "CONFIGURACION"
        elif any(word in permission_name for word in ['audit', 'auditoria', 'security', 'seguridad']):
            return "AUDITORIA"
        else:
            return "GENERAL"


# Instancia global del sistema RBAC
_rbac_system = None


def get_rbac_system() -> RBACSystem:
    """Obtiene la instancia global del sistema RBAC."""
    return _rbac_system


def init_rbac_system(db_connection) -> RBACSystem:
    """Inicializa el sistema RBAC."""
    global _rbac_system
    _rbac_system = RBACSystem(db_connection)
    return _rbac_system