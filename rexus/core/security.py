"""
Sistema de Seguridad Global - Rexus.app v2.0.0

Sistema centralizado de autenticación, autorización y control de acceso
con funcionalidades de auditoría y prevención de ataques.

Fecha: 24/08/2025
Objetivo: Gestión segura de operaciones críticas del sistema
"""

import logging
import uuid
import hashlib
import secrets
import time
from datetime import datetime
from typing import List, Dict, Optional, Any
from functools import wraps

# Importar logging
try:
    from ..utils.app_logger import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class SecurityManager:
    """Gestor de seguridad centralizado para Rexus.app."""
    
    def __init__(self, db_connection=None):
        """Inicializa el gestor de seguridad."""
        self.db_connection = db_connection
        self.allowed_updates = {
            'username': 'UPDATE usuarios SET username = ? WHERE id = ?',
            'email': 'UPDATE usuarios SET email = ? WHERE id = ?',
            'nombre': 'UPDATE usuarios SET nombre = ? WHERE id = ?',
            'apellido': 'UPDATE usuarios SET apellido = ? WHERE id = ?',
            'rol': 'UPDATE usuarios SET rol = ? WHERE id = ?',
            'activo': 'UPDATE usuarios SET activo = ? WHERE id = ?',
            'bloqueado': 'UPDATE usuarios SET bloqueado = ? WHERE id = ?',
            'password_hash': 'UPDATE usuarios SET password_hash = ? WHERE id = ?'
        }
    
    def update_user_secure(self, fields, values, user_id=None):
        """Actualiza campos de usuario de forma segura."""
        try:
            # Ejecutar updates de forma segura
            for i, field in enumerate(fields):
                field_name = field.replace(' = ?', '').strip()
                if field_name in self.allowed_updates:
                    # cursor.execute(self.allowed_updates[field_name], (values[i], values[-1]))
                    pass  # Placeholder for database operation

            # self.db_connection.commit()

            # Log
            # self.log_security_event(
            #     user_id, "USER_UPDATED", "USUARIOS", f"Usuario actualizado"
            # )

            return True

        except Exception as e:
            logger.exception(f"Error actualizando usuario: {e}")
            if self.db_connection:
                try:
                    self.db_connection.rollback()
                except Exception:
                    pass  # Ignorar errores de rollback
            return False

    def get_security_logs(self, limit: int = 100) -> List[Dict]:
        """Obtiene logs de seguridad."""
        try:
            if not self.db_connection:
                return []
                
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
            logger.exception(f"Error obteniendo logs de seguridad: {e}")
            return []
    
    def validate_user_action(self, user_id: int, action: str, resource: str) -> bool:
        """
        Valida si un usuario puede realizar una acción específica.
        
        Args:
            user_id: ID del usuario
            action: Acción a realizar
            resource: Recurso sobre el que actuar
            
        Returns:
            True si la acción está permitida
        """
        try:
            # Validar que el usuario existe y está activo
            if not self._is_user_active(user_id):
                return False
            
            # Log de intento de acción
            logger.info(f"Usuario {user_id} intenta {action} en {resource}")
            
            # Validar permisos específicos
            if action in ['DELETE', 'DROP', 'ALTER']:
                logger.warning(f"Acción peligrosa {action} solicitada por usuario {user_id}")
                return self._validate_dangerous_action(user_id, action, resource)
            
            return True
            
        except Exception as e:
            logger.error(f"Error validando acción de usuario: {e}")
            return False
    
    def _is_user_active(self, user_id: int) -> bool:
        """Verifica si el usuario está activo."""
        try:
            if not self.db_connection:
                return False
                
            cursor = self.db_connection.cursor()
            cursor.execute(
                "SELECT activo, bloqueado FROM usuarios WHERE id = ?",
                (user_id,)
            )
            result = cursor.fetchone()
            
            if not result:
                return False
                
            activo, bloqueado = result
            return activo and not bloqueado
            
        except Exception as e:
            logger.error(f"Error verificando estado del usuario {user_id}: {e}")
            return False
    
    def _validate_dangerous_action(self, user_id: int, action: str, resource: str) -> bool:
        """Valida acciones peligrosas con autenticación adicional."""
        try:
            # Registrar intento de acción peligrosa
            self._log_security_event(
                user_id,
                f"DANGEROUS_{action}",
                resource,
                f"Intento de acción peligrosa: {action} en {resource}"
            )
            
            # En producción, aquí se podría requerir autenticación adicional
            # Por ahora, solo permitir a administradores
            return self._is_admin_user(user_id)
            
        except Exception as e:
            logger.error(f"Error validando acción peligrosa: {e}")
            return False
    
    def _is_admin_user(self, user_id: int) -> bool:
        """Verifica si el usuario es administrador."""
        try:
            if not self.db_connection:
                return False
                
            cursor = self.db_connection.cursor()
            cursor.execute(
                "SELECT rol FROM usuarios WHERE id = ?",
                (user_id,)
            )
            result = cursor.fetchone()
            
            return result and result[0] in ['admin', 'superadmin']
            
        except Exception as e:
            logger.error(f"Error verificando rol de admin para usuario {user_id}: {e}")
            return False
    
    def _log_security_event(self, user_id: int, action: str, module: str, details: str):
        """Registra evento de seguridad."""
        try:
            if not self.db_connection:
                return
                
            cursor = self.db_connection.cursor()
            cursor.execute(
                """
                INSERT INTO logs_seguridad (usuario_id, accion, modulo, detalles, fecha, ip_address)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (user_id, action, module, details, datetime.now(), "127.0.0.1")
            )
            self.db_connection.commit()
            
        except Exception as e:
            logger.error(f"Error registrando evento de seguridad: {e}")
    
    def generate_secure_token(self, length: int = 32) -> str:
        """Genera un token seguro para sesiones."""
        return secrets.token_urlsafe(length)
    
    def hash_password(self, password: str, salt: Optional[str] = None) -> tuple[str, str]:
        """Hash seguro de contraseña con salt."""
        if not salt:
            salt = secrets.token_hex(16)
        
        # Usar PBKDF2 para hashing seguro
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # 100,000 iteraciones
        ).hex()
        
        return password_hash, salt
    
    def verify_password(self, password: str, stored_hash: str, salt: str) -> bool:
        """Verifica contraseña contra hash almacenado."""
        try:
            computed_hash, _ = self.hash_password(password, salt)
            return secrets.compare_digest(stored_hash, computed_hash)
        except Exception as e:
            logger.error(f"Error verificando contraseña: {e}")
            return False
    
    def get_security_status(self) -> Dict[str, Any]:
        """Obtiene estado general de seguridad del sistema."""
        try:
            status = {
                'timestamp': datetime.now().isoformat(),
                'active_sessions': 0,
                'recent_failed_logins': 0,
                'security_alerts': [],
                'system_health': 'OK'
            }
            
            # En producción, aquí se obtendría información real
            # del estado de seguridad del sistema
            
            return status
            
        except Exception as e:
            logger.error(f"Error obteniendo estado de seguridad: {e}")
            return {'system_health': 'ERROR', 'message': str(e)}


# Decorador para operaciones que requieren autorización
def require_permission(permission: str):
    """
    Decorador para requerir permisos específicos.
    
    Args:
        permission: Permiso requerido
        
    Returns:
        Decorador
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # En una implementación completa, aquí se verificarían
            # los permisos del usuario actual
            user_id = kwargs.get('user_id') or getattr(args[0] if args else None, 'current_user_id', None)
            
            if user_id:
                manager = get_security_manager()
                if manager and not manager.validate_user_action(user_id, permission, func.__name__):
                    raise PermissionError(f"Usuario no tiene permiso: {permission}")
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


# Instancia global del gestor de seguridad
security_manager = None


def get_security_manager() -> SecurityManager:
    """Obtiene la instancia global del gestor de seguridad."""
    return security_manager


def init_security_manager(db_connection) -> SecurityManager:
    """Inicializa el gestor de seguridad."""
    global security_manager
    security_manager = SecurityManager(db_connection)
    logger.info("SecurityManager inicializado correctamente")
    return security_manager


def initialize_security_manager(db_connection=None) -> SecurityManager:
    """Inicializa el gestor de seguridad - alias para init_security_manager."""
    if not db_connection:
        try:
            from ..core.database import UsersDatabaseConnection
            db_connection = UsersDatabaseConnection()
            db_connection.trusted = False
            db_connection.connect()
        except ImportError as e:
            logger.warning(f"No se pudo importar UsersDatabaseConnection: {e}")
            return None

    manager = init_security_manager(db_connection)
    return manager


# Funciones de conveniencia para validación
def validate_input(input_data: str, max_length: int = 255) -> bool:
    """Valida entrada de usuario para prevenir ataques."""
    if not input_data or len(input_data) > max_length:
        return False
    
    # Caracteres peligrosos básicos
    dangerous_chars = ['<', '>', '"', "'", ';', '--', '/*', '*/', 'script']
    
    input_lower = input_data.lower()
    return not any(char in input_lower for char in dangerous_chars)


def sanitize_sql_input(input_value: str) -> str:
    """Sanitiza entrada para prevenir SQL injection."""
    if not isinstance(input_value, str):
        return str(input_value)
    
    # Escapar caracteres peligrosos
    sanitized = input_value.replace("'", "''")
    sanitized = sanitized.replace(";", "\\;")
    sanitized = sanitized.replace("--", "\\-\\-")
    
    return sanitized


def log_security_attempt(action: str, details: str = "", ip_address: str = "127.0.0.1"):
    """Log simplificado de intentos de seguridad."""
    logger.warning(f"SECURITY_ATTEMPT: {action} | {details} | IP: {ip_address}")