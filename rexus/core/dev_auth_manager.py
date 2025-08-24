"""
Gestor de Autenticación para Desarrollo - Rexus.app
Sistema simplificado para testing y desarrollo
"""

import logging
import os
import sys
from typing import Dict, Any, Optional

# Sistema de logging
try:
    from ..utils.app_logger import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class DevAuthManager:
    """Gestor de autenticación simplificado para desarrollo."""
    
    def __init__(self):
        """Inicializa el gestor de desarrollo."""
        self.dev_user = os.getenv("DEV_USER", "admin")
        self.dev_password = os.getenv("DEV_PASSWORD", "dev123")
        self.is_development = True
        
        logger.warning("DEV AUTH MANAGER ACTIVADO - SOLO PARA DESARROLLO")
    
    def authenticate(self, usuario: str, password: str) -> bool:
        """
        Autentica usuario en modo desarrollo.
        
        Args:
            usuario: Nombre de usuario
            password: Contraseña
            
        Returns:
            True si las credenciales son válidas para desarrollo
        """
        logger.info(f"Intento de autenticación dev: {usuario}")
        return (usuario == self.dev_user and password == self.dev_password)

    def get_mock_user_session(self) -> Dict[str, Any]:
        """
        Crea una sesión mock para desarrollo.

        Returns:
            Diccionario con datos de sesión simulada
        """
        return {
            'user_id': 1,
            'usuario': self.dev_user,
            'nombre_completo': 'Administrador de Desarrollo',
            'rol': 'admin',
            'permisos': ['all'],  # Permisos completos en desarrollo
            'session_token': 'dev_session_token',
            'is_dev_session': True,
            'login_time': 'development_mode'
        }
    
    def create_dev_session(self, usuario: str = None) -> Dict[str, Any]:
        """
        Crea sesión de desarrollo automáticamente.
        
        Args:
            usuario: Usuario opcional (usa dev_user por defecto)
            
        Returns:
            Sesión de desarrollo
        """
        session_user = usuario or self.dev_user
        
        return {
            'user_id': 1,
            'usuario': session_user,
            'nombre_completo': f'Usuario de Desarrollo: {session_user}',
            'rol': 'admin',
            'permisos': ['all'],
            'session_token': f'dev_token_{session_user}',
            'is_dev_session': True,
            'login_time': 'development_mode',
            'authenticated': True
        }
    
    def is_development_mode(self) -> bool:
        """Verifica si está en modo desarrollo."""
        return self.is_development
    
    def get_available_dev_users(self) -> Dict[str, Dict[str, Any]]:
        """
        Obtiene usuarios disponibles para desarrollo.
        
        Returns:
            Diccionario con usuarios de prueba
        """
        return {
            'admin': {
                'password': 'dev123',
                'rol': 'admin',
                'permisos': ['all']
            },
            'manager': {
                'password': 'dev456', 
                'rol': 'manager',
                'permisos': ['read', 'write', 'inventario', 'obras']
            },
            'user': {
                'password': 'dev789',
                'rol': 'user', 
                'permisos': ['read', 'inventario']
            }
        }
    
    def validate_dev_credentials(self, usuario: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Valida credenciales contra usuarios de desarrollo.
        
        Args:
            usuario: Nombre de usuario
            password: Contraseña
            
        Returns:
            Datos del usuario si es válido, None en caso contrario
        """
        dev_users = self.get_available_dev_users()
        
        if usuario in dev_users:
            user_data = dev_users[usuario]
            if password == user_data['password']:
                return {
                    'usuario': usuario,
                    'rol': user_data['rol'],
                    'permisos': user_data['permisos'],
                    'is_dev_user': True
                }
        
        return None
    
    def bypass_authentication(self) -> Dict[str, Any]:
        """
        Bypass completo de autenticación para desarrollo.
        
        Returns:
            Sesión con máximos privilegios
        """
        logger.warning("BYPASS DE AUTENTICACIÓN ACTIVADO - SOLO DESARROLLO")
        
        return {
            'user_id': 999,
            'usuario': 'dev_bypass',
            'nombre_completo': 'Usuario Bypass Desarrollo',
            'rol': 'super_admin',
            'permisos': ['all', 'bypass', 'dev_mode'],
            'session_token': 'bypass_dev_token',
            'is_dev_session': True,
            'is_bypass': True,
            'authenticated': True,
            'login_time': 'bypass_mode'
        }


# Instancia global para desarrollo
_dev_auth_manager: Optional[DevAuthManager] = None


def get_dev_auth_manager() -> DevAuthManager:
    """Obtiene la instancia global del gestor de desarrollo."""
    global _dev_auth_manager
    if _dev_auth_manager is None:
        _dev_auth_manager = DevAuthManager()
    return _dev_auth_manager


def init_dev_auth_manager() -> DevAuthManager:
    """Inicializa el gestor de desarrollo."""
    global _dev_auth_manager
    _dev_auth_manager = DevAuthManager()
    return _dev_auth_manager


def is_dev_mode() -> bool:
    """Verifica si el sistema está en modo desarrollo."""
    return os.getenv("REXUS_DEV_MODE", "false").lower() == "true"


def create_dev_session_quickly(usuario: str = "admin") -> Dict[str, Any]:
    """Función rápida para crear sesión de desarrollo."""
    manager = get_dev_auth_manager()
    return manager.create_dev_session(usuario)