# -*- coding: utf-8 -*-
"""
Patch de Autenticación para Tests - Rexus.app
============================================

Este módulo proporciona un sistema de bypass de autenticación específico para tests,
permitiendo que todos los decoradores de autenticación pasen sin verificaciones.

Resuelve los problemas críticos de autenticación identificados en la auditoría.
"""

import os
import sys
from unittest.mock import patch, MagicMock
from pathlib import Path

# Agregar directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Variable global para indicar modo testing
TESTING_MODE = True


class TestAuthManager:
    """AuthManager mock para tests que permite todos los accesos."""
    
    current_user = None
    
    @classmethod
    def set_testing_mode(cls, enabled=True):
        """Activar/desactivar modo testing."""
        global TESTING_MODE
        TESTING_MODE = enabled
    
    @classmethod
    def check_role(cls, role):
        """En modo testing, siempre retorna True."""
        return True
    
    @classmethod
    def check_permission(cls, permission):
        """En modo testing, siempre retorna True."""
        return True
    
    @classmethod
    def get_current_user(cls):
        """Retorna usuario mock con todos los permisos."""
        if cls.current_user is None:
            cls.current_user = MockUser()
        return cls.current_user
    
    @classmethod
    def set_current_user(cls, user):
        """Establece usuario actual."""
        cls.current_user = user


class MockUser:
    """Usuario mock con todos los permisos para tests."""
    
    def __init__(self, user_id=1, username="test_user"):
        self.id = user_id
        self.user_id = user_id
        self.username = username
        self.roles = ["admin", "manager", "user", "viewer"]
        self.permissions = [
            "view_dashboard", "view_inventory", "create_inventory", "update_inventory", "delete_inventory",
            "view_obras", "create_obras", "update_obras", "delete_obras",
            "view_users", "create_users", "update_users", "delete_users",
            "view_config", "update_config", "view_reports", "export_data",
            "view_inventario", "edit_inventario", "delete_inventario",
            "view_compras", "edit_compras", "delete_compras",
            "view_pedidos", "edit_pedidos", "delete_pedidos",
            "view_notificaciones", "edit_notificaciones", "admin_notificaciones",
            "view_vidrios", "edit_vidrios", "delete_vidrios"
        ]
        self.activo = True
        self.es_admin = True
    
    def tiene_permiso(self, permiso):
        return True
    
    def tiene_rol(self, rol):
        return True
    
    def get(self, key, default=None):
        return getattr(self, key, default)


def mock_auth_decorators():
    """Crea decoradores mock que no hacen verificaciones."""
    
    def passthrough_decorator(func):
        """Decorador que simplemente ejecuta la función."""
        return func
    
    return passthrough_decorator


def apply_auth_patches():
    """Aplica patches globales para autenticación en tests."""
    
    # Patch de AuthManager
    auth_manager_patch = patch('rexus.core.auth_manager.AuthManager', TestAuthManager)
    auth_manager_patch.start()
    
    # Patch de decoradores individuales
    admin_required_patch = patch('rexus.core.auth_manager.admin_required', mock_auth_decorators())
    admin_required_patch.start()
    
    manager_required_patch = patch('rexus.core.auth_manager.manager_required', mock_auth_decorators())
    manager_required_patch.start()
    
    auth_required_patch = patch('rexus.core.auth_manager.auth_required', mock_auth_decorators())
    auth_required_patch.start()
    
    # Patch de funciones de verificación específicas
    check_role_patch = patch('rexus.core.auth_manager.AuthManager.check_role', return_value=True)
    check_role_patch.start()
    
    check_permission_patch = patch('rexus.core.auth_manager.AuthManager.check_permission', return_value=True)
    check_permission_patch.start()
    
    # Patch de get_current_user
    get_user_patch = patch('rexus.core.auth_manager.AuthManager.get_current_user', return_value=MockUser())
    get_user_patch.start()
    
    # También patch en módulos que importan directamente
    try:
        from rexus.core import auth
        auth_patch = patch.object(auth, 'get_current_user', return_value=MockUser())
        auth_patch.start()
    except ImportError:
        pass
    
    # Patch en decoradores específicos donde aparecen
    decorators_to_patch = [
        'rexus.core.auth_decorators.admin_required',
        'rexus.core.auth_decorators.auth_required',
        'rexus.core.auth_decorators.permission_required',
        'rexus.modules.notificaciones.model.admin_required',
        'rexus.modules.notificaciones.model.auth_required',
        'rexus.modules.vidrios.model.auth_required',
        'rexus.modules.vidrios.submodules.productos_manager.auth_required',
        'rexus.modules.vidrios.submodules.productos_manager.permission_required',
        'rexus.modules.pedidos.model.auth_required',
        'rexus.modules.compras.model.auth_required',
        'rexus.modules.obras.model.auth_required',
        'rexus.modules.inventario.model.auth_required'
    ]
    
    for decorator_path in decorators_to_patch:
        try:
            decorator_patch = patch(decorator_path, mock_auth_decorators())
            decorator_patch.start()
        except (ImportError, AttributeError):
            # Ignorar si el decorador no existe
            pass
    
    print()
    return True


def setup_test_environment():
    """Configura el entorno completo de testing."""
    
    # Establecer variables de entorno
    os.environ['TESTING'] = 'true'
    os.environ['BYPASS_AUTH'] = 'true'
    
    # Aplicar patches de autenticación
    apply_auth_patches()
    
    # Configurar usuario mock global
    TestAuthManager.set_current_user(MockUser())
    
    print("[AUTH_PATCH] ✅ Entorno de testing configurado completamente")


# Auto-configurar cuando se importa el módulo
if os.getenv('TESTING', '').lower() == 'true':
    setup_test_environment()