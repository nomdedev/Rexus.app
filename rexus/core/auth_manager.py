"""
AuthManager - Sistema de autorización para Rexus.app
Controla permisos y acceso a funcionalidades
"""

from typing import Dict, List, Optional
from enum import Enum

class UserRole(Enum):
    """Roles de usuario disponibles"""
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"
    VIEWER = "viewer"

class Permission(Enum):
    """Permisos disponibles en el sistema"""
    # Permisos generales
    VIEW_DASHBOARD = "view_dashboard"
    
    # Permisos de inventario
    VIEW_INVENTORY = "view_inventory"
    CREATE_INVENTORY = "create_inventory"
    UPDATE_INVENTORY = "update_inventory"
    DELETE_INVENTORY = "delete_inventory"
    
    # Permisos de obras
    VIEW_OBRAS = "view_obras"
    CREATE_OBRAS = "create_obras"
    UPDATE_OBRAS = "update_obras"
    DELETE_OBRAS = "delete_obras"
    
    # Permisos de usuarios
    VIEW_USERS = "view_users"
    CREATE_USERS = "create_users"
    UPDATE_USERS = "update_users"
    DELETE_USERS = "delete_users"
    
    # Permisos de configuración
    VIEW_CONFIG = "view_config"
    UPDATE_CONFIG = "update_config"
    
    # Permisos de reportes
    VIEW_REPORTS = "view_reports"
    EXPORT_DATA = "export_data"

class AuthManager:
    """Gestor de autorización y permisos"""
    
    # Mapeo de roles a permisos
    ROLE_PERMISSIONS: Dict[UserRole, List[Permission]] = {
        UserRole.ADMIN: list(Permission),  # Admin tiene todos los permisos
        UserRole.MANAGER: [
            Permission.VIEW_DASHBOARD,
            Permission.VIEW_INVENTORY, Permission.CREATE_INVENTORY, 
            Permission.UPDATE_INVENTORY,
            Permission.VIEW_OBRAS, Permission.CREATE_OBRAS, 
            Permission.UPDATE_OBRAS,
            Permission.VIEW_USERS, Permission.CREATE_USERS,
            Permission.VIEW_CONFIG, Permission.VIEW_REPORTS,
            Permission.EXPORT_DATA
        ],
        UserRole.USER: [
            Permission.VIEW_DASHBOARD,
            Permission.VIEW_INVENTORY, Permission.CREATE_INVENTORY,
            Permission.VIEW_OBRAS, Permission.CREATE_OBRAS,
            Permission.VIEW_REPORTS
        ],
        UserRole.VIEWER: [
            Permission.VIEW_DASHBOARD,
            Permission.VIEW_INVENTORY,
            Permission.VIEW_OBRAS,
            Permission.VIEW_REPORTS
        ]
    }
    
    current_user_role: Optional[UserRole] = None
    
    @classmethod
    def set_current_user_role(cls, role: UserRole):
        """Establece el rol del usuario actual"""
        cls.current_user_role = role
    
    @classmethod
    def check_permission(cls, permission: Permission) -> bool:
        """Verifica si el usuario actual tiene el permiso especificado"""
        if cls.current_user_role is None:
            return False
        
        return permission in cls.ROLE_PERMISSIONS.get(cls.current_user_role, [])
    
    @classmethod
    def check_role(cls, required_role: UserRole) -> bool:
        """Verifica si el usuario actual tiene el rol requerido o superior"""
        if cls.current_user_role is None:
            return False
        
        role_hierarchy = {
            UserRole.VIEWER: 1,
            UserRole.USER: 2,
            UserRole.MANAGER: 3,
            UserRole.ADMIN: 4
        }
        
        current_level = role_hierarchy.get(cls.current_user_role, 0)
        required_level = role_hierarchy.get(required_role, 0)
        
        return current_level >= required_level
    
    @classmethod
    def require_permission(cls, permission: Permission):
        """Decorador para requerir un permiso específico"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                if not cls.check_permission(permission):
                    raise PermissionError(f"Acceso denegado: se requiere permiso {permission.value}")
                return func(*args, **kwargs)
            return wrapper
        return decorator
    
    @classmethod
    def require_role(cls, role: UserRole):
        """Decorador para requerir un rol específico"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                if not cls.check_role(role):
                    raise PermissionError(f"Acceso denegado: se requiere rol {role.value} o superior")
                return func(*args, **kwargs)
            return wrapper
        return decorator

# Decoradores de conveniencia
def admin_required(func):
    """Decorador que requiere rol de administrador"""
    return AuthManager.require_role(UserRole.ADMIN)(func)

def manager_required(func):
    """Decorador que requiere rol de manager o superior"""
    return AuthManager.require_role(UserRole.MANAGER)(func)

def auth_required(func):
    """Decorador que requiere cualquier usuario autenticado"""
    return AuthManager.require_role(UserRole.VIEWER)(func)
