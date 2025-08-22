# -*- coding: utf-8 -*-
"""
Configuración Global de Tests - Rexus.app
========================================

Configuración simplificada y robusta para resolver problemas críticos de tests.
"""

import pytest
import sys
import os
import sqlite3
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Configurar encoding UTF-8 globalmente
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Agregar directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configurar variables de entorno para tests
os.environ['TESTING'] = 'true'
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['BYPASS_AUTH'] = 'true'


class MockUser:
    """Usuario mock para tests con todos los permisos necesarios."""
    
    def __init__(self, user_id=1, username="test_user", roles=None):
        self.id = user_id
        self.user_id = user_id
        self.username = username
        self.roles = roles or ["admin", "viewer", "editor", "user", "manager"]
        self.permissions = [
            "view_inventario", "edit_inventario", "delete_inventario",
            "view_obras", "edit_obras", "delete_obras",
            "view_compras", "edit_compras", "delete_compras",
            "view_pedidos", "edit_pedidos", "delete_pedidos",
            "view_notificaciones", "edit_notificaciones", "admin_notificaciones",
            "view_vidrios", "edit_vidrios", "delete_vidrios",
            "admin", "all_permissions", "view_dashboard", "view_inventory",
            "create_inventory", "update_inventory", "delete_inventory",
            "create_obras", "update_obras", "delete_obras", "view_users",
            "create_users", "update_users", "delete_users", "view_config",
            "update_config", "view_reports", "export_data"
        ]
        self.activo = True
        self.es_admin = True
    
    def tiene_permiso(self, permiso):
        return True
    
    def tiene_rol(self, rol):
        return True
    
    def get(self, key, default=None):
        return getattr(self, key, default)


class MockDatabase:
    """Base de datos mock para tests."""
    
    def __init__(self):
        self.connection = None
        self.cursor_mock = None
        self.setup_mock()
    
    def setup_mock(self):
        """Configurar mocks de base de datos."""
        self.connection = Mock()
        self.cursor_mock = Mock()
        
        # Configurar cursor mock con comportamientos estándar
        self.cursor_mock.fetchone.return_value = [1, "Test Item", 100.0, "Activo"]
        self.cursor_mock.fetchall.return_value = [
            [1, "Item 1", 50.0, "Activo"],
            [2, "Item 2", 75.0, "Activo"],
            [3, "Item 3", 125.0, "Activo"]
        ]
        self.cursor_mock.rowcount = 1
        self.cursor_mock.lastrowid = 1
        self.cursor_mock.description = [
            ['id'], ['nombre'], ['precio'], ['estado']
        ]
        
        # Configurar connection mock
        self.connection.cursor.return_value = self.cursor_mock
        self.connection.commit.return_value = None
        self.connection.rollback.return_value = None
        self.connection.close.return_value = None
        
    def get_connection(self):
        """Obtener conexión mock."""
        return self.connection
    
    def get_cursor(self):
        """Obtener cursor mock."""
        return self.cursor_mock


# Función de bypass simple para decoradores
def bypass_auth_decorator(func=None, *args, **kwargs):
    """Decorador que simplemente ejecuta la función sin verificaciones."""
    if func is None or isinstance(func, str):
        # Si se llama como @permission_required("algo"), retornamos un decorador
        def decorator(f):
            return f
        return decorator
    else:
        # Si se llama como @auth_required, aplicamos directamente
        return func

def bypass_permission_decorator(permission=None):
    """Decorador específico para permission_required que maneja parámetros."""
    def decorator(func):
        return func
    return decorator


# Global mock user instance
GLOBAL_MOCK_USER = MockUser()


@pytest.fixture(autouse=True)
def setup_auth_bypass():
    """Fixture que configura bypass de autenticación para todos los tests."""
    
    # Lista de paths que necesitan ser parcheados
    auth_patches = [
        'rexus.core.auth_manager.admin_required',
        'rexus.core.auth_manager.auth_required', 
        'rexus.core.auth_manager.manager_required',
        'rexus.core.auth_manager.AuthManager.check_role',
        'rexus.core.auth_manager.AuthManager.check_permission',
        'rexus.core.auth_manager.AuthManager.get_current_user',
        # También parchear auth_decorators que usa módulo Vidrios
        'rexus.core.auth_decorators.auth_required',
        'rexus.core.auth_decorators.admin_required',
        'rexus.core.auth_decorators.permission_required',
        'rexus.core.auth.get_current_user',
    ]
    
    # Aplicar patches
    patches = []
    
    # Patch para decoradores - los hace pasar directamente
    decorator_patches = [
        'rexus.core.auth_manager.admin_required',
        'rexus.core.auth_manager.auth_required', 
        'rexus.core.auth_manager.manager_required',
        'rexus.core.auth_decorators.auth_required',
        'rexus.core.auth_decorators.admin_required',
    ]
    
    for auth_path in decorator_patches:
        try:
            patcher = patch(auth_path, bypass_auth_decorator)
            patches.append(patcher)
            patcher.start()
        except:
            pass
    
    # Patch específico para permission_required que maneja parámetros
    try:
        permission_patch = patch('rexus.core.auth_decorators.permission_required', bypass_permission_decorator)
        patches.append(permission_patch)
        permission_patch.start()
    except:
        pass
    
    # Patch para métodos de verificación - retornan True
    try:
        check_role_patch = patch('rexus.core.auth_manager.AuthManager.check_role', return_value=True)
        patches.append(check_role_patch)
        check_role_patch.start()
    except:
        pass
    
    try:
        check_permission_patch = patch('rexus.core.auth_manager.AuthManager.check_permission', return_value=True)  
        patches.append(check_permission_patch)
        check_permission_patch.start()
    except:
        pass
    
    # Patch para get_current_user - retorna usuario mock
    user_patches = [
        'rexus.core.auth_manager.AuthManager.get_current_user',
        'rexus.core.auth.get_current_user',
    ]
    
    for user_path in user_patches:
        try:
            get_user_patch = patch(user_path, return_value=GLOBAL_MOCK_USER)
            patches.append(get_user_patch)
            get_user_patch.start()
        except:
            pass
    
    yield GLOBAL_MOCK_USER
    
    # Cleanup
    for patcher in patches:
        try:
            patcher.stop()
        except:
            pass


@pytest.fixture
def mock_db():
    """Fixture que proporciona una base de datos mock estándar."""
    return MockDatabase()


@pytest.fixture
def mock_db_connection(mock_db):
    """Fixture que proporciona solo la conexión mock."""
    return mock_db.get_connection()


@pytest.fixture
def mock_cursor(mock_db):
    """Fixture que proporciona solo el cursor mock."""
    return mock_db.get_cursor()


@pytest.fixture
def clean_database():
    """Fixture que proporciona una base de datos limpia para tests."""
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()
    
    # Crear tablas básicas para tests
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY,
            codigo TEXT UNIQUE,
            nombre TEXT,
            precio REAL,
            estado TEXT DEFAULT 'ACTIVO'
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS obras (
            id INTEGER PRIMARY KEY,
            nombre TEXT,
            cliente TEXT,
            estado TEXT DEFAULT 'ACTIVO',
            fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notificaciones (
            id INTEGER PRIMARY KEY,
            titulo TEXT,
            mensaje TEXT,
            tipo TEXT DEFAULT 'info',
            prioridad INTEGER DEFAULT 2,
            activa INTEGER DEFAULT 1,
            fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    yield conn
    conn.close()


@pytest.fixture
def sample_data():
    """Fixture que proporciona datos de muestra estándar para tests."""
    return {
        'usuario': {
            'id': 1,
            'username': 'test_user',
            'email': 'test@rexus.app',
            'activo': True
        },
        'producto': {
            'codigo': 'TEST-001',
            'nombre': 'Producto de Prueba',
            'precio': 99.99,
            'categoria': 'TEST',
            'stock': 100
        },
        'obra': {
            'nombre': 'Obra de Prueba',
            'cliente': 'Cliente Test',
            'direccion': 'Dirección Test 123',
            'estado': 'ACTIVO'
        },
        'notificacion': {
            'titulo': 'Notificación de Prueba',
            'mensaje': 'Este es un mensaje de prueba',
            'tipo': 'info',
            'prioridad': 2
        }
    }


def pytest_configure(config):
    """Configuración global de pytest."""
    config.addinivalue_line("markers", "slow: marca tests que son lentos")
    config.addinivalue_line("markers", "integration: marca tests de integración")
    config.addinivalue_line("markers", "e2e: marca tests end-to-end")


# Configurar logging
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('requests').setLevel(logging.WARNING)

print("[CONFTEST] ✅ Configuración global de tests cargada")
print("[CONFTEST] ✅ Sistema de bypass de autenticación activado")
print("[CONFTEST] ✅ Encoding UTF-8 configurado")