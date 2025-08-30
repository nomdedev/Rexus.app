"""
Rexus.app - Sistema de Seguridad

Implementación del sistema de seguridad que maneja autenticación y autorización.
"""

import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class SecurityManager:
    """
    Gestor principal de seguridad que maneja autenticación y autorización.
    """

    def __init__(self, db_connection=None):
        """
        Inicializa el SecurityManager.

        Args:
            db_connection: Conexión opcional a la base de datos
        """
        self.db_connection = db_connection
        self.current_user = None
        self.current_role = "usuario"
        self._session_active = False

        logger.info("[SECURITY] SecurityManager inicializado")

    def authenticate_user(self, username: str, password: str) -> bool:
        """
        Autentica a un usuario con sus credenciales.

        Args:
            username: Nombre de usuario
            password: Contraseña

        Returns:
            True si la autenticación es exitosa
        """
        try:
            if self.db_connection:
                # Intentar autenticación con base de datos
                from rexus.utils.security import SecurityUtils

                # Obtener hash de la contraseña
                password_hash = SecurityUtils.hash_password(password)

                user_data = self.db_connection.validate_user_credentials(username, password_hash)
                if user_data:
                    self.current_user = user_data
                    self.current_role = user_data.get('rol', 'usuario')
                    self._session_active = True
                    logger.info(f"[SECURITY] Usuario autenticado: {username}")
                    return True
            else:
                # Fallback: autenticación básica
                fallback_password = __import__('os').getenv('FALLBACK_ADMIN_PASSWORD', 'admin123')
                if username == "admin" and password == fallback_password:
                    self.current_user = {
                        'id': 1,
                        'username': 'admin',
                        'rol': 'ADMIN'
                    }
                    self.current_role = 'ADMIN'
                    self._session_active = True
                    logger.info("[SECURITY] Usuario autenticado (fallback): admin")
                    return True

            logger.warning(f"[SECURITY] Fallo de autenticación para: {username}")
            return False

        except Exception as e:
            logger.error(f"[SECURITY] Error en autenticación: {e}")
            return False

    def authorize_module(self, module_name: str) -> bool:
        """
        Verifica si el usuario actual tiene permisos para acceder a un módulo.

        Args:
            module_name: Nombre del módulo

        Returns:
            True si tiene permisos
        """
        if not self._session_active or not self.current_user:
            return False

        try:
            if self.db_connection:
                # Verificar permisos en base de datos
                user_permissions = self.db_connection.get_user_permissions(self.current_user['id'])
                return module_name in user_permissions
            else:
                # Fallback: permisos por rol
                return self._check_role_permissions(module_name)

        except Exception as e:
            logger.error(f"[SECURITY] Error verificando permisos: {e}")
            return False

    def _check_role_permissions(self, module_name: str) -> bool:
        """
        Verifica permisos basados en el rol del usuario (fallback).
        """
        role_permissions = {
            'ADMIN': ["Obras", "Inventario", "Herrajes", "Vidrios", "Logística",
                     "Pedidos", "Compras", "Administración", "Mantenimiento",
                     "Auditoría", "Usuarios", "Configuración"],
            'SUPERVISOR': ["Obras", "Inventario", "Herrajes", "Vidrios", "Logística",
                          "Pedidos", "Compras", "Administración", "Mantenimiento"],
            'OPERADOR': ["Obras", "Inventario", "Herrajes", "Vidrios", "Logística", "Pedidos"],
            'AUDITOR': ["Auditoría", "Mantenimiento"],
            'USUARIO': ["Obras", "Inventario", "Herrajes", "Vidrios"]
        }

        user_role = self.current_role.upper()
        permissions = role_permissions.get(user_role, role_permissions['USUARIO'])
        return module_name in permissions

    def logout(self):
        """Cierra la sesión del usuario actual."""
        self.current_user = None
        self.current_role = "usuario"
        self._session_active = False
        logger.info("[SECURITY] Sesión cerrada")

    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """Retorna la información del usuario actual."""
        return self.current_user

    def is_session_active(self) -> bool:
        """Verifica si hay una sesión activa."""
        return self._session_active


def init_security_manager(db_connection=None) -> SecurityManager:
    """
    Función de inicialización del SecurityManager.

    Args:
        db_connection: Conexión opcional a la base de datos

    Returns:
        Instancia de SecurityManager
    """
    return SecurityManager(db_connection)