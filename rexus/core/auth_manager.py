"""
AuthManager - Sistema de autorización para Rexus.app
Controla permisos y acceso a funcionalidades
"""

from enum import Enum
from typing import Dict, List, Optional


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
            Permission.VIEW_INVENTORY,
            Permission.CREATE_INVENTORY,
            Permission.UPDATE_INVENTORY,
            Permission.VIEW_OBRAS,
            Permission.CREATE_OBRAS,
            Permission.UPDATE_OBRAS,
            Permission.VIEW_USERS,
            Permission.CREATE_USERS,
            Permission.VIEW_CONFIG,
            Permission.VIEW_REPORTS,
            Permission.EXPORT_DATA,
        ],
        UserRole.USER: [
            Permission.VIEW_DASHBOARD,
            Permission.VIEW_INVENTORY,
            Permission.CREATE_INVENTORY,
            Permission.VIEW_OBRAS,
            Permission.CREATE_OBRAS,
            Permission.VIEW_REPORTS,
        ],
        UserRole.VIEWER: [
            Permission.VIEW_DASHBOARD,
            Permission.VIEW_INVENTORY,
            Permission.VIEW_OBRAS,
            Permission.VIEW_REPORTS,
        ],
    }

    current_user_role: Optional[UserRole] = None
    current_user: Optional[str] = None

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
            UserRole.ADMIN: 4,
        }

        current_level = role_hierarchy.get(cls.current_user_role, 0)
        required_level = role_hierarchy.get(required_role, 0)

        return current_level >= required_level

    @classmethod
    def authenticate_user(cls, username: str, password: str):
        """Autentica un usuario contra la base de datos con rate limiting"""
        try:
            # Importar conexión a base de datos y rate limiter
            import hashlib
            import datetime

            from rexus.core.database import get_users_connection
            from rexus.core.rate_limiter import get_rate_limiter
            from rexus.utils.password_security import (
                verify_password_secure,
            )

            # Verificar rate limiting antes de intentar autenticación
            rate_limiter = get_rate_limiter()
            is_blocked, locked_until = rate_limiter.is_blocked(username)

            if is_blocked:
                remaining_time = locked_until - datetime.datetime.now()
                minutes_remaining = max(1, int(remaining_time.total_seconds() / 60))
                error_msg = f"Usuario bloqueado por {minutes_remaining} minutos debido a demasiados intentos fallidos"
                print(f"[ERROR] Rate limit: {error_msg}")

                # Registrar intento en usuario bloqueado
                rate_limiter._log_security_event(username, "blocked_attempt", minutes_remaining)

                return {"error": error_msg, "blocked_until": locked_until}

            # Conectar a la base de datos de usuarios
            db = get_users_connection()

            if not db.connection:
                print("[ERROR] Error: No se pudo conectar a la base de datos de usuarios")
                return False

            # Buscar usuario en la base de datos
            result = db.execute_query(
                """
                SELECT usuario, password_hash, rol, estado, nombre, apellido, email
                FROM usuarios
                WHERE usuario = ? AND estado = 'activo'
            """,
                (username,),
            )

            if not result:
                # Usuario no encontrado - también registrar como intento fallido para prevenir enumeración
                rate_limiter.record_failed_attempt(username)

                lockout_info = rate_limiter.get_lockout_info(username)
                remaining_attempts = lockout_info['remaining_attempts']

                print(f"[ERROR] Usuario '{username}' no encontrado o inactivo")
                return {"error": "Credenciales incorrectas", "remaining_attempts": remaining_attempts}

            user_data = result[0]
            stored_hash = user_data[1]
            user_role = user_data[2]

            # Verificar contraseña usando el sistema de seguridad mejorado
            try:
                # Intentar verificación con sistema seguro (PBKDF2, bcrypt, argon2)
                password_valid = verify_password_secure(password, stored_hash)
            except (ValueError, TypeError, ImportError, AttributeError) as e:
                # Fallback para contraseñas SHA-256 legacy (durante migración)
                logger.warning(f"Error verificación segura, usando fallback legacy: {e}")
                password_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
                password_valid = password_hash == stored_hash

                # Log de advertencia para contraseñas legacy
                logger.warning(
                    f"Usuario '{username}' usando contraseña SHA-256 legacy. Migración recomendada."
                )

            # Verificar contraseña
            if password_valid:
                # Login exitoso - registrar en rate limiter
                rate_limiter.record_successful_attempt(username)

                # Mapear rol de la BD a enum
                role_mapping = {
                    "ADMIN": UserRole.ADMIN,
                    "MANAGER": UserRole.MANAGER,
                    "USER": UserRole.USER,
                    "VIEWER": UserRole.VIEWER,
                }

                cls.current_user = username
                cls.current_user_role = role_mapping.get(
                    user_role.upper(), UserRole.VIEWER
                )

                print(
                    f"[CHECK] Usuario autenticado: {username} (rol: {cls.current_user_role.value})"
                )

                # Actualizar última conexión
                db.execute_non_query(
                    """
                    UPDATE usuarios
                    SET ultima_conexion = GETDATE()
                    WHERE usuario = ?
                """,
                    (username,),
                )

                # Retornar información del usuario
                user_info = {
                    "username": user_data[0],
                    "role": user_role,
                    "nombre": user_data[4] if len(user_data) > 4 else "",
                    "apellido": user_data[5] if len(user_data) > 5 else "",
                    "email": user_data[6] if len(user_data) > 6 else "",
                    "authenticated": True,
                }
                return user_info
            else:
                # Login fallido - registrar intento fallido
                rate_limiter.record_failed_attempt(username)

                # Obtener información de rate limiting para el mensaje
                lockout_info = rate_limiter.get_lockout_info(username)
                remaining_attempts = lockout_info['remaining_attempts']

                if remaining_attempts > 0:
                    print(f"[ERROR] Contraseña incorrecta para usuario: {username} "
                          f"(quedan {remaining_attempts} intentos)")
                else:
                    print(f"[ERROR] Contraseña incorrecta para usuario: {username} - USUARIO BLOQUEADO")

                return {"error": "Credenciales incorrectas", "remaining_attempts": remaining_attempts}

        except Exception as e:
            print(f"[ERROR] Error en autenticación: {e}")
            import traceback

            traceback.print_exc()
            return False

    @classmethod
    def require_permission(cls, permission: Permission):
        """Decorador para requerir un permiso específico"""

        def decorator(func):
            def wrapper(*args, **kwargs):
                if not cls.check_permission(permission):
                    raise PermissionError(
                        f"Acceso denegado: se requiere permiso {permission.value}"
                    )
                return func(*args, **kwargs)

            return wrapper

        return decorator

    @classmethod
    def require_role(cls, role: UserRole):
        """Decorador para requerir un rol específico"""

        def decorator(func):
            def wrapper(*args, **kwargs):
                if not cls.check_role(role):
                    raise PermissionError(
                        f"Acceso denegado: se requiere rol {role.value} o superior"
                    )
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
