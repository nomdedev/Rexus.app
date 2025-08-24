"""
Sistema de Control de Acceso Basado en Roles (RBAC) - Rexus.app v2.0.0

FUNCIONALIDADES DE SEGURIDAD:
[CHECK] Sistema granular de roles y permisos
[CHECK] Control de acceso a acciones sensibles
[CHECK] Jerarquía de roles con herencia de permisos
[CHECK] Validación de permisos en tiempo real
[CHECK] Gestión centralizada de autorizaciones
"""

import logging
import os
from enum import Enum
from typing import Set, Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime

# Sistema de logging
try:
    from ..utils.app_logger import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


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
    APPROVE_PAYMENT = "approve_payment"
    VIEW_REPORTS = "view_reports"
    MANAGE_BUDGETS = "manage_budgets"

    # Compras
    VIEW_PURCHASES = "view_purchases"
    CREATE_PURCHASE = "create_purchase"
    APPROVE_PURCHASE = "approve_purchase"
    MANAGE_SUPPLIERS = "manage_suppliers"
    VIEW_ORDERS = "view_orders"

    # Configuración del sistema
    VIEW_CONFIG = "view_config"
    MODIFY_CONFIG = "modify_config"
    MANAGE_BACKUPS = "manage_backups"
    VIEW_LOGS = "view_logs"
    MANAGE_SECURITY = "manage_security"

    # Auditoría
    VIEW_AUDIT = "view_audit"
    EXPORT_AUDIT = "export_audit"
    MANAGE_AUDIT = "manage_audit"


class Role(Enum):
    """Roles del sistema con jerarquía definida."""
    # Orden jerárquico ascendente
    GUEST = "GUEST"
    USER = "USER"
    OPERATOR = "OPERATOR"
    SPECIALIST = "SPECIALIST"
    SUPERVISOR = "SUPERVISOR"
    MANAGER = "MANAGER"
    ADMIN = "ADMIN"
    SUPER_ADMIN = "SUPER_ADMIN"
    
    # Roles especializados
    ACCOUNTANT = "ACCOUNTANT"


@dataclass
class RoleInfo:
    """Información detallada de un rol."""
    role: Role
    display_name: str
    description: str
    permissions: Set[Permission]
    inherits_from: Optional[Role] = None


class RBACSystem:
    """Sistema de Control de Acceso Basado en Roles."""
    
    def __init__(self):
        """Inicializa el sistema RBAC."""
        self.role_hierarchy = {}
        self.role_permissions = {}
        self.user_roles = {}
        self.user_custom_permissions = {}
        
        self._initialize_roles()
        logger.info("Sistema RBAC inicializado")
    
    def _initialize_roles(self):
        """Inicializa la configuración de roles y permisos."""
        
        # Definir permisos por rol
        role_definitions = {
            Role.GUEST: RoleInfo(
                Role.GUEST, "Invitado", "Acceso muy limitado solo para demostración",
                {Permission.LOGIN, Permission.VIEW_DASHBOARD}
            ),
            
            Role.USER: RoleInfo(
                Role.USER, "Usuario", "Usuario básico con permisos de lectura",
                {
                    Permission.LOGIN, Permission.LOGOUT, Permission.VIEW_DASHBOARD,
                    Permission.VIEW_INVENTORY, Permission.VIEW_PROJECTS,
                    Permission.VIEW_AVAILABILITY
                }
            ),
            
            Role.OPERATOR: RoleInfo(
                Role.OPERATOR, "Operador", "Operador con permisos básicos de creación",
                {
                    Permission.CREATE_INVENTORY, Permission.UPDATE_INVENTORY,
                    Permission.MANAGE_RESERVATIONS, Permission.VIEW_ORDERS
                },
                inherits_from=Role.USER
            ),
            
            Role.SPECIALIST: RoleInfo(
                Role.SPECIALIST, "Especialista", "Especialista con permisos avanzados",
                {
                    Permission.CREATE_PROJECT, Permission.UPDATE_PROJECT,
                    Permission.MANAGE_SCHEDULE, Permission.VIEW_PRODUCTION,
                    Permission.EXPORT_INVENTORY
                },
                inherits_from=Role.OPERATOR
            ),
            
            Role.SUPERVISOR: RoleInfo(
                Role.SUPERVISOR, "Supervisor", "Supervisor con permisos de gestión",
                {
                    Permission.DELETE_INVENTORY, Permission.APPROVE_PROJECT,
                    Permission.VIEW_PURCHASES, Permission.CREATE_PURCHASE,
                    Permission.VIEW_REPORTS
                },
                inherits_from=Role.SPECIALIST
            ),
            
            Role.MANAGER: RoleInfo(
                Role.MANAGER, "Manager", "Gerente con permisos amplios",
                {
                    Permission.DELETE_PROJECT, Permission.APPROVE_PURCHASE,
                    Permission.MANAGE_SUPPLIERS, Permission.VIEW_ACCOUNTING,
                    Permission.MANAGE_BUDGETS, Permission.VIEW_USERS
                },
                inherits_from=Role.SUPERVISOR
            ),
            
            Role.ADMIN: RoleInfo(
                Role.ADMIN, "Administrador", "Administrador del sistema",
                {
                    Permission.CREATE_USER, Permission.UPDATE_USER,
                    Permission.ASSIGN_ROLES, Permission.VIEW_CONFIG,
                    Permission.MODIFY_CONFIG, Permission.VIEW_LOGS,
                    Permission.VIEW_AUDIT, Permission.EXPORT_AUDIT
                },
                inherits_from=Role.MANAGER
            ),
            
            Role.SUPER_ADMIN: RoleInfo(
                Role.SUPER_ADMIN, "Super Administrador", "Control total del sistema",
                {
                    Permission.DELETE_USER, Permission.LOCK_USER,
                    Permission.UNLOCK_USER, Permission.RESET_PASSWORD,
                    Permission.MANAGE_BACKUPS, Permission.MANAGE_SECURITY,
                    Permission.MANAGE_AUDIT
                },
                inherits_from=Role.ADMIN
            ),
            
            Role.ACCOUNTANT: RoleInfo(
                Role.ACCOUNTANT, "Contable", "Especialista en contabilidad",
                {
                    Permission.VIEW_ACCOUNTING, Permission.CREATE_ENTRY,
                    Permission.CREATE_RECEIPT, Permission.APPROVE_PAYMENT,
                    Permission.VIEW_REPORTS, Permission.MANAGE_BUDGETS
                },
                inherits_from=Role.USER
            )
        }
        
        # Procesar definiciones
        for role_info in role_definitions.values():
            self.role_hierarchy[role_info.role] = role_info
            
            # Calcular permisos efectivos (incluir herencia)
            effective_permissions = set(role_info.permissions)
            
            if role_info.inherits_from:
                parent_permissions = self._get_role_permissions(role_info.inherits_from)
                effective_permissions.update(parent_permissions)
            
            self.role_permissions[role_info.role] = effective_permissions
    
    def _get_role_permissions(self, role: Role) -> Set[Permission]:
        """Obtiene permisos de un rol (con herencia)."""
        if role in self.role_permissions:
            return self.role_permissions[role]
        
        # Calcular permisos si no están en caché
        role_info = self.role_hierarchy.get(role)
        if not role_info:
            return set()
        
        permissions = set(role_info.permissions)
        if role_info.inherits_from:
            parent_permissions = self._get_role_permissions(role_info.inherits_from)
            permissions.update(parent_permissions)
        
        self.role_permissions[role] = permissions
        return permissions
    
    def assign_role_to_user(self, user_id: int, role: Role):
        """
        Asigna un rol a un usuario.
        
        Args:
            user_id: ID del usuario
            role: Rol a asignar
        """
        self.user_roles[user_id] = role
        logger.info(f"Rol {role.value} asignado al usuario {user_id}")
        
        # Log de auditoría
        self._log_permission_change(
            user_id=user_id,
            action="ROLE_ASSIGNED",
            details={
                "role": role.value,
                "granted_permissions": [p.value for p in self._get_role_permissions(role)]
            }
        )
    
    def grant_permission_to_user(self, user_id: int, permission: Permission):
        """
        Otorga un permiso específico a un usuario.
        
        Args:
            user_id: ID del usuario
            permission: Permiso a otorgar
        """
        if user_id not in self.user_custom_permissions:
            self.user_custom_permissions[user_id] = set()
        
        self.user_custom_permissions[user_id].add(permission)
        logger.info(f"Permiso {permission.value} otorgado al usuario {user_id}")
        
        self._log_permission_change(
            user_id=user_id,
            action="PERMISSION_GRANTED",
            details={"permission": permission.value}
        )
    
    def revoke_permission_from_user(self, user_id: int, permission: Permission):
        """
        Revoca un permiso específico de un usuario.
        
        Args:
            user_id: ID del usuario
            permission: Permiso a revocar
        """
        if user_id in self.user_custom_permissions:
            self.user_custom_permissions[user_id].discard(permission)
            logger.info(f"Permiso {permission.value} revocado del usuario {user_id}")
            
            self._log_permission_change(
                user_id=user_id,
                action="PERMISSION_REVOKED",
                details={"permission": permission.value}
            )
    
    def user_has_permission(self, user_id: int, permission: Permission) -> bool:
        """
        Verifica si un usuario tiene un permiso específico.
        
        Args:
            user_id: ID del usuario
            permission: Permiso a verificar
            
        Returns:
            True si el usuario tiene el permiso
        """
        # Verificar permisos del rol
        user_role = self.user_roles.get(user_id)
        if user_role:
            role_permissions = self._get_role_permissions(user_role)
            if permission in role_permissions:
                return True
        
        # Verificar permisos personalizados
        user_permissions = self.user_custom_permissions.get(user_id, set())
        has_permission = permission in user_permissions
        
        # Log de acceso si es denegado
        if not has_permission:
            self._log_access_attempt(
                user_id=user_id,
                permission=permission.value,
                granted=False
            )
        
        return has_permission
    
    def get_user_permissions(self, user_id: int) -> Set[Permission]:
        """
        Obtiene todos los permisos de un usuario.
        
        Args:
            user_id: ID del usuario
            
        Returns:
            Conjunto de permisos del usuario
        """
        permissions = set()
        
        # Permisos del rol
        user_role = self.user_roles.get(user_id)
        if user_role:
            permissions.update(self._get_role_permissions(user_role))
        
        # Permisos personalizados
        custom_permissions = self.user_custom_permissions.get(user_id, set())
        permissions.update(custom_permissions)
        
        return permissions
    
    def get_user_role(self, user_id: int) -> Optional[Role]:
        """
        Obtiene el rol de un usuario.
        
        Args:
            user_id: ID del usuario
            
        Returns:
            Rol del usuario o None
        """
        return self.user_roles.get(user_id)
    
    def remove_user(self, user_id: int):
        """
        Elimina un usuario del sistema RBAC.
        
        Args:
            user_id: ID del usuario a eliminar
        """
        self.user_roles.pop(user_id, None)
        self.user_custom_permissions.pop(user_id, None)
        
        logger.info(f"Usuario {user_id} eliminado del sistema RBAC")
        
        self._log_permission_change(
            user_id=user_id,
            action="USER_REMOVED",
            details={}
        )
    
    def get_role_info(self, role: Role) -> Optional[RoleInfo]:
        """
        Obtiene información detallada de un rol.
        
        Args:
            role: Rol a consultar
            
        Returns:
            Información del rol o None
        """
        return self.role_hierarchy.get(role)
    
    def get_available_roles(self) -> List[Role]:
        """
        Obtiene lista de roles disponibles.
        
        Returns:
            Lista de roles del sistema
        """
        return list(self.role_hierarchy.keys())
    
    def _log_permission_change(self, user_id: int, action: str, details: Dict[str, Any]):
        """Log cambios de permisos para auditoría."""
        try:
            # En una implementación completa, esto se integraría con el sistema de auditoría
            logger.info(f"RBAC Change - Usuario: {user_id}, Acción: {action}, Detalles: {details}")
        except Exception as e:
            logger.error(f"Error logging permission change: {e}")
    
    def _log_access_attempt(self, user_id: int, permission: str, granted: bool):
        """Log intentos de acceso para auditoría."""
        try:
            status = "GRANTED" if granted else "DENIED"
            logger.warning(f"Access {status} - Usuario: {user_id}, Permiso: {permission}")
        except Exception as e:
            logger.error(f"Error logging access attempt: {e}")
    
    def get_permission_module(self, permission: Permission) -> str:
        """
        Obtiene el módulo al que pertenece un permiso.
        
        Args:
            permission: Permiso a clasificar
            
        Returns:
            Nombre del módulo
        """
        permission_name = permission.value.lower()
        
        if any(word in permission_name for word in ['user', 'usuario']):
            return "USUARIOS"
        elif any(word in permission_name for word in ['inventory', 'inventario']):
            return "INVENTARIO"
        elif any(word in permission_name for word in ['project', 'proyecto', 'obra']):
            return "OBRAS"
        elif any(word in permission_name for word in ['accounting', 'contabilidad', 'entry', 'receipt']):
            return "ADMINISTRACION"
        elif any(word in permission_name for word in ['purchase', 'compra', 'supplier', 'pedido']):
            return "COMPRAS"
        elif any(word in permission_name for word in ['logistics', 'logistica', 'transport']):
            return "LOGISTICA"
        elif any(word in permission_name for word in ['hardware', 'herraje', 'vidrio']):
            return "MATERIALES"
        elif any(word in permission_name for word in ['maintenance', 'mantenimiento']):
            return "MANTENIMIENTO"
        elif any(word in permission_name for word in ['config', 'configuracion', 'system', 'sistema']):
            return "CONFIGURACION"
        elif any(word in permission_name for word in ['audit', 'auditoria', 'security', 'seguridad']):
            return "AUDITORIA"
        else:
            return "GENERAL"
    
    def generate_permissions_report(self, user_id: int = None) -> Dict[str, Any]:
        """
        Genera reporte de permisos.
        
        Args:
            user_id: ID de usuario específico (opcional)
            
        Returns:
            Reporte detallado de permisos
        """
        if user_id:
            # Reporte para usuario específico
            user_role = self.get_user_role(user_id)
            user_permissions = self.get_user_permissions(user_id)
            
            return {
                "user_id": user_id,
                "role": user_role.value if user_role else None,
                "total_permissions": len(user_permissions),
                "permissions_by_module": self._group_permissions_by_module(user_permissions),
                "custom_permissions": [p.value for p in self.user_custom_permissions.get(user_id, set())]
            }
        else:
            # Reporte general del sistema
            return {
                "total_roles": len(self.role_hierarchy),
                "total_users": len(self.user_roles),
                "roles": {role.value: info.display_name for role, info in self.role_hierarchy.items()},
                "users_by_role": self._get_users_by_role()
            }
    
    def _group_permissions_by_module(self, permissions: Set[Permission]) -> Dict[str, List[str]]:
        """Agrupa permisos por módulo."""
        modules = {}
        for perm in permissions:
            module = self.get_permission_module(perm)
            if module not in modules:
                modules[module] = []
            modules[module].append(perm.value)
        return modules
    
    def _get_users_by_role(self) -> Dict[str, int]:
        """Obtiene conteo de usuarios por rol."""
        role_counts = {}
        for role in self.user_roles.values():
            role_name = role.value
            role_counts[role_name] = role_counts.get(role_name, 0) + 1
        return role_counts


# Instancia global del sistema RBAC
_rbac_system: Optional[RBACSystem] = None


def get_rbac_system() -> RBACSystem:
    """Obtiene la instancia global del sistema RBAC."""
    global _rbac_system
    if _rbac_system is None:
        _rbac_system = RBACSystem()
    return _rbac_system


def init_rbac_system() -> RBACSystem:
    """Inicializa el sistema global RBAC."""
    global _rbac_system
    _rbac_system = RBACSystem()
    return _rbac_system


# Funciones de conveniencia
def user_has_permission(user_id: int, permission: Permission) -> bool:
    """Función de conveniencia para verificar permisos."""
    rbac = get_rbac_system()
    return rbac.user_has_permission(user_id, permission)


def assign_role(user_id: int, role: Role):
    """Función de conveniencia para asignar roles."""
    rbac = get_rbac_system()
    rbac.assign_role_to_user(user_id, role)


def get_user_role(user_id: int) -> Optional[Role]:
    """Función de conveniencia para obtener rol de usuario."""
    rbac = get_rbac_system()
    return rbac.get_user_role(user_id)