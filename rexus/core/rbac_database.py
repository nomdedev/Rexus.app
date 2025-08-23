"""
Sistema RBAC en Base de Datos - Rexus.app

Sistema completo de control de acceso basado en roles que utiliza la base de datos
para gestionar usuarios, roles, permisos y políticas de acceso de manera granular.

Este sistema permite:
- Gestión jerárquica de roles
- Permisos granulares por recurso y acción
- Políticas de acceso dinámicas
- Auditoría completa de accesos
- Herencia de permisos entre roles

Author: Rexus Development Team
Date: 2025-08-11
Version: 1.0.0
"""


import logging
logger = logging.getLogger(__name__)

import sqlite3
import json
            

# Instancia global del sistema RBAC
_rbac_system: Optional[RBACDatabase] = None


def init_rbac_system(db_path: str = "rbac.db") -> RBACDatabase:
    """Inicializa el sistema RBAC global."""
    global _rbac_system
    _rbac_system = RBACDatabase(db_path)
    return _rbac_system


def get_rbac_system() -> RBACDatabase:
    """Obtiene la instancia global del sistema RBAC."""
    if _rbac_system is None:
        raise RuntimeError("Sistema RBAC no está inicializado. Llame a init_rbac_system() primero.")
    return _rbac_system


def check_permission(user_id: int, resource: str, action: str,
                    context: Optional[Dict[str, Any]] = None) -> bool:
    """Función de conveniencia para verificar permisos."""
    rbac = get_rbac_system()
    result, _ = rbac.check_access(user_id, resource, action, context)
    return result == AccessResult.GRANTED


def require_permission(resource: str, action: str):
    """Decorador que requiere permisos específicos para ejecutar una función."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Esto requeriría contexto de usuario actual
            # En una implementación real, se obtendría del contexto de sesión
            user_id = kwargs.get('current_user_id')
            if not user_id:
                raise PermissionError("No se pudo determinar el usuario actual")

            if not check_permission(user_id, resource, action):
                raise PermissionError(f"Acceso denegado para {resource}:{action}")

            return func(*args, **kwargs)
        return wrapper
    return decorator
