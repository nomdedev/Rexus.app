"""
Decoradores de autorización para Rexus.app

Proporciona decoradores para verificar autenticación y permisos
en controladores y métodos críticos.
"""

import functools
from typing import List, Optional, Callable, Any
from PyQt6.QtWidgets import QMessageBox


class AuthenticationError(Exception):
    """Excepción para errores de autenticación"""
    pass


class AuthorizationError(Exception):
    """Excepción para errores de autorización"""
    pass


def auth_required(func: Callable) -> Callable:
    """
    Decorador que requiere autenticación para ejecutar el método.
    
    Args:
        func: Función a proteger
        
    Returns:
        Función decorada que verifica autenticación
        
    Raises:
        AuthenticationError: Si el usuario no está autenticado
    """
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        # Verificar si existe un usuario autenticado
        if not hasattr(self, 'current_user') or not self.current_user:
            # Intentar obtener usuario del contexto global
            try:
                from rexus.core.auth import get_current_user
                current_user = get_current_user()
                if not current_user:
                    raise AuthenticationError("Usuario no autenticado")
                # Asignar usuario al contexto si no existe
                if not hasattr(self, 'current_user'):
                    self.current_user = current_user
            except ImportError:
                raise AuthenticationError("Sistema de autenticación no disponible")
        
        # Registrar acceso para auditoría
        try:
            from rexus.core.security import SecurityManager
            security = SecurityManager()
            security.log_access_attempt(
                user_id=self.current_user.get('id'),
                resource=f"{self.__class__.__name__}.{func.__name__}",
                action="access",
                status="granted"
            )
        except Exception as e:
            print(f"[WARNING] Error registrando acceso: {e}")
        
        return func(self, *args, **kwargs)
    
    wrapper._auth_required = True
    return wrapper


def permission_required(permission: str):
    """
    Decorador que requiere un permiso específico para ejecutar el método.
    
    Args:
        permission: Nombre del permiso requerido
        
    Returns:
        Decorador que verifica el permiso
        
    Raises:
        AuthorizationError: Si el usuario no tiene el permiso requerido
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            # Primero verificar autenticación
            if not hasattr(func, '_auth_required'):
                # Aplicar auth_required automáticamente
                auth_func = auth_required(func)
                return auth_func(self, *args, **kwargs)
            
            # Verificar permiso específico
            try:
                from rexus.core.auth_manager import AuthManager
                auth_manager = AuthManager()
                
                user_role = self.current_user.get('role', 'user')
                if not auth_manager.has_permission(user_role, permission):
                    # Registrar intento no autorizado
                    try:
                        from rexus.core.security import SecurityManager
                        security = SecurityManager()
                        security.log_security_event(
                            event_type="authorization_denied",
                            user_id=self.current_user.get('id'),
                            details=f"Permiso '{permission}' denegado para rol '{user_role}'"
                        )
                    except Exception as e:
                        print(f"[WARNING] Error registrando evento de seguridad: {e}")
                    
                    raise AuthorizationError(f"Permiso '{permission}' requerido")
                
            except ImportError:
                print(f"[WARNING] Sistema de permisos no disponible - permitiendo acceso")
            
            return func(self, *args, **kwargs)
        
        wrapper._permission_required = permission
        wrapper._auth_required = True
        return wrapper
    
    return decorator


def role_required(*roles: str):
    """
    Decorador que requiere uno de los roles especificados.
    
    Args:
        *roles: Lista de roles permitidos
        
    Returns:
        Decorador que verifica roles
        
    Raises:
        AuthorizationError: Si el usuario no tiene ninguno de los roles requeridos
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            # Verificar autenticación primero
            if not hasattr(self, 'current_user') or not self.current_user:
                auth_func = auth_required(func)
                return auth_func(self, *args, **kwargs)
            
            # Verificar rol
            user_role = self.current_user.get('role', 'user')
            if user_role not in roles:
                # Registrar intento no autorizado
                try:
                    from rexus.core.security import SecurityManager
                    security = SecurityManager()
                    security.log_security_event(
                        event_type="role_access_denied",
                        user_id=self.current_user.get('id'),
                        details=f"Rol '{user_role}' no autorizado. Roles requeridos: {roles}"
                    )
                except Exception as e:
                    print(f"[WARNING] Error registrando evento de seguridad: {e}")
                
                raise AuthorizationError(f"Rol requerido: {' o '.join(roles)}")
            
            return func(self, *args, **kwargs)
        
        wrapper._roles_required = roles
        wrapper._auth_required = True
        return wrapper
    
    return decorator


def admin_required(func: Callable) -> Callable:
    """
    Decorador que requiere rol de administrador.
    
    Args:
        func: Función a proteger
        
    Returns:
        Función decorada que verifica rol admin
    """
    return role_required('admin')(func)


def handle_auth_error(func: Callable) -> Callable:
    """
    Decorador que maneja errores de autenticación y autorización
    mostrando mensajes de error apropiados al usuario.
    
    Args:
        func: Función a proteger
        
    Returns:
        Función decorada con manejo de errores
    """
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except AuthenticationError as e:
            QMessageBox.warning(
                None,
                "Acceso Denegado",
                f"Debe iniciar sesión para acceder a esta funcionalidad.\n\nDetalle: {str(e)}",
                QMessageBox.StandardButton.Ok
            )
            # Opcional: redirigir a login
            try:
                self.show_login()
            except AttributeError:
                pass
        except AuthorizationError as e:
            QMessageBox.warning(
                None,
                "Permisos Insuficientes",
                f"No tiene permisos para realizar esta acción.\n\nDetalle: {str(e)}",
                QMessageBox.StandardButton.Ok
            )
        except Exception as e:
            print(f"[ERROR] Error inesperado en método protegido: {e}")
            QMessageBox.critical(
                None,
                "Error",
                f"Error interno del sistema.\n\nContacte al administrador.",
                QMessageBox.StandardButton.Ok
            )
    
    return wrapper


def audit_action(action: str, resource: str = None):
    """
    Decorador que registra acciones para auditoría.
    
    Args:
        action: Acción realizada (create, read, update, delete)
        resource: Recurso afectado (opcional)
        
    Returns:
        Decorador que registra la acción
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            # Ejecutar función
            result = func(self, *args, **kwargs)
            
            # Registrar acción para auditoría
            try:
                from rexus.core.audit_system import AuditSystem
                audit = AuditSystem()
                
                user_id = None
                if hasattr(self, 'current_user') and self.current_user:
                    user_id = self.current_user.get('id')
                
                audit.log_action(
                    user_id=user_id,
                    action=action,
                    resource=resource or f"{self.__class__.__name__}.{func.__name__}",
                    details=f"Argumentos: {args}, Kwargs: {kwargs}",
                    status="success" if result else "failed"
                )
            except Exception as e:
                print(f"[WARNING] Error registrando auditoría: {e}")
            
            return result
        
        wrapper._audit_action = action
        wrapper._audit_resource = resource
        return wrapper
    
    return decorator


# Decoradores combinados para casos comunes
def secure_operation(permission: str = None, audit_action: str = None):
    """
    Decorador combinado que aplica autenticación, autorización, 
    manejo de errores y auditoría.
    
    Args:
        permission: Permiso requerido (opcional)
        audit_action: Acción para auditoría (opcional)
        
    Returns:
        Decorador combinado
    """
    def decorator(func: Callable) -> Callable:
        # Aplicar decoradores en orden
        decorated_func = func
        
        # 1. Auditoría (si se especifica)
        if audit_action:
            decorated_func = audit_action(audit_action)(decorated_func)
        
        # 2. Autorización (si se especifica)
        if permission:
            decorated_func = permission_required(permission)(decorated_func)
        else:
            # 3. Al menos autenticación
            decorated_func = auth_required(decorated_func)
        
        # 4. Manejo de errores
        decorated_func = handle_auth_error(decorated_func)
        
        return decorated_func
    
    return decorator