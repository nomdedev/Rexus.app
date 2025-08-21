#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mock Factories - Creadores de Mocks Reutilizables
Para resolver problemas de inicialización de módulos
"""

import sys
import os
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from decimal import Decimal
from datetime import datetime, date

# Configurar path y encoding
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
os.environ['PYTHONIOENCODING'] = 'utf-8'


class MockDatabaseFactory:
    """Factory para crear mocks de base de datos."""
    
    @staticmethod
    def create_users_database():
        """Crear mock de base de datos de usuarios."""
        mock_db = Mock()
        mock_cursor = Mock()
        mock_db.cursor.return_value = mock_cursor
        
        # Datos de usuarios predefinidos
        users_data = [
            ('admin', 'hashed_admin_password', 'ADMIN', 'activo', 'Administrator', 'System'),
            ('user1', 'hashed_user1_password', 'USER', 'activo', 'Usuario', 'Uno'),
            ('manager1', 'hashed_manager_password', 'MANAGER', 'activo', 'Manager', 'Test')
        ]
        
        mock_cursor.fetchall.return_value = users_data
        mock_cursor.fetchone.return_value = users_data[0]
        mock_cursor.execute.return_value = None
        mock_cursor.rowcount = 1
        
        mock_db.commit.return_value = None
        mock_db.rollback.return_value = None
        mock_db.close.return_value = None
        
        return mock_db
    
    @staticmethod
    def create_inventario_database():
        """Crear mock de base de datos de inventario."""
        mock_db = Mock()
        mock_cursor = Mock()
        mock_db.cursor.return_value = mock_cursor
        
        # Datos de productos predefinidos
        productos_data = [
            (1, 'PROD001', 'Producto A', 'Categoría A', 100.00, 50, 10, 1),
            (2, 'PROD002', 'Producto B', 'Categoría B', 200.00, 25, 5, 1),
            (3, 'PROD003', 'Producto C', 'Categoría C', 300.00, 75, 15, 1)
        ]
        
        mock_cursor.fetchall.return_value = productos_data
        mock_cursor.fetchone.return_value = productos_data[0]
        mock_cursor.execute.return_value = None
        mock_cursor.rowcount = len(productos_data)
        
        mock_db.commit.return_value = None
        mock_db.close.return_value = None
        
        return mock_db
    
    @staticmethod
    def create_obras_database():
        """Crear mock de base de datos de obras."""
        mock_db = Mock()
        mock_cursor = Mock()
        mock_db.cursor.return_value = mock_cursor
        
        # Datos de obras predefinidos
        obras_data = [
            (1, 'OBR001', 'Obra Test 1', 'Cliente A', 'activa', '2025-08-01', '2025-12-31', 100000.00, 'Juan Pérez'),
            (2, 'OBR002', 'Obra Test 2', 'Cliente B', 'planificada', '2025-09-01', '2026-01-31', 150000.00, 'María García')
        ]
        
        mock_cursor.fetchall.return_value = obras_data
        mock_cursor.fetchone.return_value = obras_data[0]
        mock_cursor.execute.return_value = None
        mock_cursor.rowcount = len(obras_data)
        
        mock_db.commit.return_value = None
        mock_db.close.return_value = None
        
        return mock_db
    
    @staticmethod
    def create_compras_database():
        """Crear mock de base de datos de compras."""
        mock_db = Mock()
        mock_cursor = Mock()
        mock_db.cursor.return_value = mock_cursor
        
        # Datos de compras predefinidos
        compras_data = [
            (1, 'COMP001', 'Compra Test 1', '2025-08-21', 'pendiente', 50000.00, 'Proveedor A'),
            (2, 'COMP002', 'Compra Test 2', '2025-08-20', 'aprobada', 75000.00, 'Proveedor B')
        ]
        
        mock_cursor.fetchall.return_value = compras_data
        mock_cursor.fetchone.return_value = compras_data[0]
        mock_cursor.execute.return_value = None
        mock_cursor.rowcount = len(compras_data)
        
        mock_db.commit.return_value = None
        mock_db.close.return_value = None
        
        return mock_db


class MockControllerFactory:
    """Factory para crear mocks de controladores."""
    
    @staticmethod
    def create_usuarios_controller():
        """Crear mock funcional del controlador de usuarios."""
        mock_controller = Mock()
        
        # Métodos básicos
        mock_controller.listar_usuarios.return_value = [
            {'id': 1, 'usuario': 'admin', 'rol': 'ADMIN', 'estado': 'activo'},
            {'id': 2, 'usuario': 'user1', 'rol': 'USER', 'estado': 'activo'}
        ]
        
        mock_controller.crear_usuario.return_value = {'success': True, 'id': 3}
        mock_controller.actualizar_usuario.return_value = {'success': True}
        mock_controller.eliminar_usuario.return_value = {'success': True}
        mock_controller.autenticar_usuario.return_value = {
            'success': True, 
            'user': {'id': 1, 'usuario': 'admin', 'rol': 'ADMIN'}
        }
        
        # Estado del controlador
        mock_controller.db_connected = True
        mock_controller.initialized = True
        
        return mock_controller
    
    @staticmethod
    def create_inventario_controller():
        """Crear mock funcional del controlador de inventario."""
        mock_controller = Mock()
        
        # Métodos básicos
        mock_controller.listar_productos.return_value = [
            {'id': 1, 'codigo': 'PROD001', 'nombre': 'Producto A', 'stock': 50, 'precio': 100.00},
            {'id': 2, 'codigo': 'PROD002', 'nombre': 'Producto B', 'stock': 25, 'precio': 200.00}
        ]
        
        mock_controller.crear_producto.return_value = {'success': True, 'id': 3}
        mock_controller.actualizar_stock.return_value = {'success': True}
        mock_controller.generar_reporte_stock.return_value = {
            'productos': 2,
            'valor_total': 7500.00,
            'alertas': []
        }
        
        mock_controller.db_connected = True
        mock_controller.initialized = True
        
        return mock_controller
    
    @staticmethod
    def create_compras_controller():
        """Crear mock funcional del controlador de compras."""
        mock_controller = Mock()
        
        # Métodos básicos
        mock_controller.listar_compras.return_value = [
            {'id': 1, 'codigo': 'COMP001', 'proveedor': 'Proveedor A', 'total': 50000.00, 'estado': 'pendiente'},
            {'id': 2, 'codigo': 'COMP002', 'proveedor': 'Proveedor B', 'total': 75000.00, 'estado': 'aprobada'}
        ]
        
        mock_controller.crear_compra.return_value = {'success': True, 'id': 3}
        mock_controller.aprobar_compra.return_value = {'success': True}
        mock_controller.cancelar_compra.return_value = {'success': True}
        mock_controller.get_dashboard_data.return_value = {
            'compras_mes': 125000.00,
            'proveedores_activos': 5,
            'ordenes_pendientes': 3
        }
        
        mock_controller.db_connected = True
        mock_controller.initialized = True
        
        return mock_controller


class MockViewFactory:
    """Factory para crear mocks de vistas."""
    
    @staticmethod
    def create_base_view():
        """Crear mock base para vistas."""
        mock_view = Mock()
        
        # Métodos comunes de vistas
        mock_view.show.return_value = None
        mock_view.hide.return_value = None
        mock_view.update_data.return_value = None
        mock_view.refresh.return_value = None
        mock_view.validate_form.return_value = True
        mock_view.clear_form.return_value = None
        
        # Propiedades comunes
        mock_view.visible = True
        mock_view.enabled = True
        mock_view.form_valid = True
        
        return mock_view


class MockIntegrationFactory:
    """Factory para mocks de integración entre módulos."""
    
    @staticmethod
    def create_auth_manager():
        """Crear mock del gestor de autenticación."""
        mock_auth = Mock()
        
        mock_auth.authenticate.return_value = {
            'success': True,
            'user_id': 1,
            'username': 'admin',
            'role': 'ADMIN',
            'permissions': ['ALL']
        }
        
        mock_auth.check_permission.return_value = True
        mock_auth.get_current_user.return_value = {
            'id': 1,
            'username': 'admin',
            'role': 'ADMIN'
        }
        
        mock_auth.logout.return_value = {'success': True}
        mock_auth.is_authenticated = True
        
        return mock_auth
    
    @staticmethod  
    def create_database_manager():
        """Crear mock del gestor de base de datos."""
        mock_db_manager = Mock()
        
        mock_db_manager.get_connection.return_value = MockDatabaseFactory.create_inventario_database()
        mock_db_manager.test_connection.return_value = True
        mock_db_manager.is_connected = True
        mock_db_manager.connection_string = "mock://database"
        
        return mock_db_manager


# Context managers para usar en tests
class MockContext:
    """Context manager para aplicar mocks temporalmente."""
    
    def __init__(self, patches):
        self.patches = patches
        self.active_patches = []
    
    def __enter__(self):
        for patch_config in self.patches:
            patcher = patch(**patch_config)
            mock_obj = patcher.start()
            self.active_patches.append(patcher)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        for patcher in reversed(self.active_patches):
            patcher.stop()


def apply_global_mocks():
    """Aplicar mocks globales para resolver problemas de inicialización."""
    patches = [
        {
            'target': 'rexus.core.database.InventarioDatabaseConnection',
            'return_value': MockDatabaseFactory.create_inventario_database()
        },
        {
            'target': 'rexus.core.database.UsersDatabaseConnection',
            'return_value': MockDatabaseFactory.create_users_database()
        },
        {
            'target': 'rexus.core.auth_manager.AuthManager',
            'return_value': MockIntegrationFactory.create_auth_manager()
        }
    ]
    
    return MockContext(patches)