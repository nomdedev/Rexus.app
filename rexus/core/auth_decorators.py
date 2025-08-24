"""
Decoradores de autorización para Rexus.app

Proporciona decoradores para verificar autenticación y permisos
en controladores y métodos críticos.
"""

import functools
import logging
from typing import Optional, List, Callable, Any

# Sistema de logging
try:
    from ..utils.app_logger import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class AuthenticationError(Exception):
    """Error de autenticación."""
    pass


class AuthorizationError(Exception):
    """Error de autorización."""
    pass


def login_required(func: Callable) -> Callable:
    """
    Decorador que requiere que el usuario esté autenticado.
    
    Args:
        func: Función a decorar
        
    Returns:
        Función decorada con verificación de login
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            # Intentar obtener sesión actual
            current_user = get_current_user()
            
            if not current_user or not current_user.get('authenticated', False):
                logger.warning("Intento de acceso sin autenticación")
                raise AuthenticationError("Usuario no autenticado")
            
            # Agregar usuario a kwargs para la función
            kwargs['current_user'] = current_user
            return func(*args, **kwargs)
            
        except AuthenticationError:
            logger.error(f"Error de autenticación en {func.__name__}")
            raise
        except Exception as e:
            logger.exception(f"Error inesperado en login_required: {e}")
            raise AuthenticationError("Error de verificación de autenticación")
    
    return wrapper


def permission_required(permission: str, resource: str = None):
    """
    Decorador que requiere un permiso específico.
    
    Args:
        permission: Permiso requerido (e.g., 'read', 'write', 'delete')
        resource: Recurso opcional (e.g., 'inventario', 'usuarios')
        
    Returns:
        Decorador que verifica el permiso
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # Verificar autenticación primero
                current_user = get_current_user()
                if not current_user or not current_user.get('authenticated', False):
                    raise AuthenticationError("Usuario no autenticado")
                
                # Verificar permiso específico
                if not has_permission(current_user, permission, resource):
                    logger.warning(f"Usuario {current_user.get('username')} sin permiso {permission} para {resource}")
                    raise AuthorizationError(f"Sin permiso para {permission} en {resource}")
                
                # Agregar información de usuario
                kwargs['current_user'] = current_user
                return func(*args, **kwargs)
                
            except (AuthenticationError, AuthorizationError):
                logger.error(f"Error de autorización en {func.__name__}")
                raise
            except Exception as e:
                logger.exception(f"Error inesperado en permission_required: {e}")
                raise AuthorizationError("Error de verificación de permisos")
        
        return wrapper
    return decorator


def role_required(roles: List[str]):
    """
    Decorador que requiere uno de los roles especificados.
    
    Args:
        roles: Lista de roles permitidos
        
    Returns:
        Decorador que verifica el rol
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                current_user = get_current_user()
                if not current_user or not current_user.get('authenticated', False):
                    raise AuthenticationError("Usuario no autenticado")
                
                user_role = current_user.get('role')
                if user_role not in roles:
                    logger.warning(f"Usuario {current_user.get('username')} con rol {user_role} intentó acceso que requiere {roles}")
                    raise AuthorizationError(f"Se requiere uno de estos roles: {roles}")
                
                kwargs['current_user'] = current_user
                return func(*args, **kwargs)
                
            except (AuthenticationError, AuthorizationError):
                raise
            except Exception as e:
                logger.exception(f"Error inesperado en role_required: {e}")
                raise AuthorizationError("Error de verificación de rol")
        
        return wrapper
    return decorator


def admin_required(func: Callable) -> Callable:
    """
    Decorador que requiere rol de administrador.
    
    Args:
        func: Función a decorar
        
    Returns:
        Función decorada con verificación de admin
    """
    return role_required(['ADMIN', 'SUPER_ADMIN'])(func)


def handle_auth_error(func: Callable) -> Callable:
    """
    Decorador para manejo centralizado de errores de autenticación.
    
    Args:
        func: Función a decorar
        
    Returns:
        Función decorada con manejo de errores
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except AuthenticationError as e:
            logger.error(f"Error de autenticación: {e}")
            # En una aplicación real, esto podría redirigir al login
            return {'error': 'authentication_required', 'message': str(e)}
        except AuthorizationError as e:
            logger.error(f"Error de autorización: {e}")
            return {'error': 'access_denied', 'message': str(e)}
        except Exception as e:
            logger.exception(f"Error inesperado en manejo de auth: {e}")
            return {'error': 'internal_error', 'message': 'Error interno del sistema'}
    
    return wrapper


def audit_access(resource: str = None, action: str = None):
    """
    Decorador que audita accesos a recursos.
    
    Args:
        resource: Recurso accedido
        action: Acción realizada
        
    Returns:
        Decorador que registra el acceso
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            current_user = get_current_user()
            user_info = f"Usuario: {current_user.get('username', 'Unknown')}" if current_user else "Usuario: No autenticado"
            
            logger.info(f"[AUDIT] {user_info} - Recurso: {resource} - Acción: {action} - Función: {func.__name__}")
            
            try:
                result = func(*args, **kwargs)
                logger.info(f"[AUDIT] Acceso exitoso - {user_info} - {resource}:{action}")
                return result
            except Exception as e:
                logger.error(f"[AUDIT] Error en acceso - {user_info} - {resource}:{action} - Error: {e}")
                raise
        
        return wrapper
    return decorator


def rate_limit(max_calls: int = 100, time_window: int = 3600):
    """
    Decorador básico de rate limiting.
    
    Args:
        max_calls: Máximo número de llamadas
        time_window: Ventana de tiempo en segundos
        
    Returns:
        Decorador que limita la tasa de llamadas
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Implementación básica - en producción usaría Redis o similar
            current_user = get_current_user()
            user_id = current_user.get('id', 'anonymous') if current_user else 'anonymous'
            
            # Por ahora solo loggeamos - implementación completa requiere storage persistente
            logger.info(f"[RATE_LIMIT] Usuario {user_id} llamó {func.__name__}")
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


# Funciones auxiliares
def get_current_user() -> Optional[dict]:
    """
    Obtiene el usuario actual de la sesión.
    
    Returns:
        Diccionario con información del usuario o None
    """
    try:
        # En una implementación real, esto obtendría de la sesión actual
        # Por ahora retornamos un mock para evitar errores
        from ..core.auth_manager import get_current_session
        session = get_current_session()
        return session.get('user') if session else None
    except ImportError:
        # Fallback si auth_manager no está disponible
        return None
    except Exception as e:
        logger.error(f"Error obteniendo usuario actual: {e}")
        return None


def has_permission(user: dict, permission: str, resource: str = None) -> bool:
    """
    Verifica si un usuario tiene un permiso específico.
    
    Args:
        user: Diccionario con información del usuario
        permission: Permiso a verificar
        resource: Recurso opcional
        
    Returns:
        True si tiene el permiso, False en caso contrario
    """
    try:
        # Verificación básica de rol
        user_role = user.get('role', '').upper()
        
        # Los administradores tienen todos los permisos
        if user_role in ['ADMIN', 'SUPER_ADMIN']:
            return True
        
        # Verificar permisos específicos del usuario
        user_permissions = user.get('permissions', [])
        
        if resource:
            # Buscar permiso específico para el recurso
            required_perm = f"{resource}:{permission}"
            if required_perm in user_permissions:
                return True
        
        # Verificar permiso general
        if permission in user_permissions:
            return True
        
        # Verificar por rol
        role_permissions = get_role_permissions(user_role)
        if resource:
            required_perm = f"{resource}:{permission}"
            if required_perm in role_permissions:
                return True
        
        return permission in role_permissions
        
    except Exception as e:
        logger.error(f"Error verificando permisos: {e}")
        return False


def get_role_permissions(role: str) -> List[str]:
    """
    Obtiene los permisos de un rol específico.
    
    Args:
        role: Rol del usuario
        
    Returns:
        Lista de permisos del rol
    """
    # Definición básica de permisos por rol
    role_permissions = {
        'ADMIN': ['*'],  # Todos los permisos
        'SUPER_ADMIN': ['*'],  # Todos los permisos
        'MANAGER': ['read', 'write', 'inventario:read', 'inventario:write', 'obras:read', 'obras:write'],
        'USER': ['read', 'inventario:read', 'obras:read'],
        'VIEWER': ['read']
    }
    
    return role_permissions.get(role.upper(), [])