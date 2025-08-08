"""
Tests for PermissionsManager - Sistema de permisos RBAC refactorizado
Tests de roles, permisos granulares, y control de acceso
"""

import pytest
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# Agregar el directorio raíz al path
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

try:
    from rexus.modules.usuarios.submodules.permissions_manager import PermissionsManager, SystemModule, PermissionLevel
    from tests.obras.mock_auth_context import MockDatabaseContext
except ImportError as e:
    print(f"Error importando módulos: {e}")
    PermissionsManager = None
    SystemModule = None
    PermissionLevel = None


class TestPermissionsManager:
    """Suite de tests para PermissionsManager."""
    
    def setup_method(self):
        """Configuración para cada test."""
        self.mock_db = MockDatabaseContext()
        self.permissions_manager = PermissionsManager(self.mock_db.connection) if PermissionsManager else None
    
    @pytest.mark.skipif(PermissionsManager is None, reason="PermissionsManager no disponible")
    def test_obtener_permisos_usuario_admin(self):
        """Test obtener permisos de usuario administrador."""
        usuario_id = 1
        
        # Mock del cursor para usuario admin
        mock_cursor = Mock()
        mock_cursor.fetchone.side_effect = [
            ('admin',),  # Rol del usuario
        ]
        mock_cursor.fetchall.return_value = [
            ('inventario', 'read'),
            ('inventario', 'write')
        ]
        
        self.mock_db.connection.cursor.return_value = mock_cursor
        
        permisos = self.permissions_manager.obtener_permisos_usuario(usuario_id)
        
        # Verificaciones
        assert isinstance(permisos, list)
        assert len(permisos) > 0
        
        # Admin debería tener permisos de todos los módulos
        permisos_str = ' '.join(permisos)
        assert 'usuarios:admin' in permisos_str
        assert 'inventario:admin' in permisos_str
        assert 'obras:admin' in permisos_str
    
    @pytest.mark.skipif(PermissionsManager is None, reason="PermissionsManager no disponible")
    def test_obtener_permisos_usuario_viewer(self):
        """Test obtener permisos de usuario viewer (solo lectura)."""
        usuario_id = 2
        
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = ('viewer',)
        mock_cursor.fetchall.return_value = []  # Sin permisos específicos
        
        self.mock_db.connection.cursor.return_value = mock_cursor
        
        permisos = self.permissions_manager.obtener_permisos_usuario(usuario_id)
        
        # Verificaciones
        assert isinstance(permisos, list)
        
        # Viewer debería tener solo permisos de lectura básicos
        permisos_str = ' '.join(permisos)
        assert 'inventario:read' in permisos_str
        assert 'obras:read' in permisos_str
        assert 'compras:read' in permisos_str
        
        # No debería tener permisos de admin o usuarios
        assert 'usuarios:' not in permisos_str
        assert ':admin' not in permisos_str
    
    @pytest.mark.skipif(PermissionsManager is None, reason="PermissionsManager no disponible")
    def test_verificar_permiso_usuario_con_permiso(self):
        """Test verificar permiso específico que el usuario tiene."""
        usuario_id = 1
        
        # Mock para simular que el usuario tiene permisos de inventario
        with patch.object(self.permissions_manager, 'obtener_permisos_usuario', 
                         return_value=['inventario:read', 'inventario:write', 'obras:read']):
            
            # Test permiso específico
            tiene_permiso = self.permissions_manager.verificar_permiso_usuario(usuario_id, 'inventario', 'read')
            assert tiene_permiso is True
            
            # Test permiso de escritura
            tiene_permiso = self.permissions_manager.verificar_permiso_usuario(usuario_id, 'inventario', 'write')
            assert tiene_permiso is True
    
    @pytest.mark.skipif(PermissionsManager is None, reason="PermissionsManager no disponible")
    def test_verificar_permiso_usuario_sin_permiso(self):
        """Test verificar permiso específico que el usuario NO tiene."""
        usuario_id = 2
        
        # Mock para simular permisos limitados
        with patch.object(self.permissions_manager, 'obtener_permisos_usuario', 
                         return_value=['inventario:read', 'obras:read']):
            
            # Test permiso que no tiene
            tiene_permiso = self.permissions_manager.verificar_permiso_usuario(usuario_id, 'usuarios', 'admin')
            assert tiene_permiso is False
            
            # Test permiso de escritura sin tenerlo
            tiene_permiso = self.permissions_manager.verificar_permiso_usuario(usuario_id, 'inventario', 'write')
            assert tiene_permiso is False
    
    @pytest.mark.skipif(PermissionsManager is None, reason="PermissionsManager no disponible")
    def test_verificar_permiso_jerarquico(self):
        """Test verificar permisos jerárquicos (admin incluye write y read)."""
        usuario_id = 1
        
        # Mock para usuario con permisos de admin
        with patch.object(self.permissions_manager, 'obtener_permisos_usuario', 
                         return_value=['inventario:admin']):
            
            # Admin debería tener todos los permisos menores
            assert self.permissions_manager.verificar_permiso_usuario(usuario_id, 'inventario', 'admin') is True
            assert self.permissions_manager.verificar_permiso_usuario(usuario_id, 'inventario', 'write') is True
            assert self.permissions_manager.verificar_permiso_usuario(usuario_id, 'inventario', 'read') is True
    
    @pytest.mark.skipif(PermissionsManager is None, reason="PermissionsManager no disponible")
    def test_asignar_permiso_usuario_exitoso(self):
        """Test asignar permiso específico a usuario."""
        usuario_id = 2
        modulo = 'inventario'
        accion = 'write'
        
        mock_cursor = Mock()
        mock_cursor.fetchone.side_effect = [
            (1,),  # Usuario existe
            (0,)   # Permiso no existe previamente
        ]
        mock_cursor.rowcount = 1
        
        self.mock_db.connection.cursor.return_value = mock_cursor
        
        resultado = self.permissions_manager.asignar_permiso_usuario(usuario_id, modulo, accion)
        
        # Verificaciones
        assert resultado['success'] is True
        assert 'correctamente' in resultado['message']
    
    @pytest.mark.skipif(PermissionsManager is None, reason="PermissionsManager no disponible")
    def test_asignar_permiso_usuario_inexistente(self):
        """Test asignar permiso a usuario que no existe."""
        usuario_id = 999
        modulo = 'inventario'
        accion = 'write'
        
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = (0,)  # Usuario no existe
        
        self.mock_db.connection.cursor.return_value = mock_cursor
        
        resultado = self.permissions_manager.asignar_permiso_usuario(usuario_id, modulo, accion)
        
        # Verificaciones
        assert resultado['success'] is False
        assert 'no encontrado' in resultado['message']
    
    @pytest.mark.skipif(PermissionsManager is None, reason="PermissionsManager no disponible")
    def test_asignar_permiso_modulo_invalido(self):
        """Test asignar permiso con módulo inválido."""
        usuario_id = 1
        modulo = 'modulo_inexistente'
        accion = 'read'
        
        resultado = self.permissions_manager.asignar_permiso_usuario(usuario_id, modulo, accion)
        
        # Verificaciones
        assert resultado['success'] is False
        assert 'inválida' in resultado['message']
    
    @pytest.mark.skipif(PermissionsManager is None, reason="PermissionsManager no disponible")
    def test_revocar_permiso_usuario(self):
        """Test revocar permiso específico de usuario."""
        usuario_id = 2
        modulo = 'inventario'
        accion = 'write'
        
        mock_cursor = Mock()
        mock_cursor.rowcount = 1  # Permiso encontrado y revocado
        
        self.mock_db.connection.cursor.return_value = mock_cursor
        
        resultado = self.permissions_manager.revocar_permiso_usuario(usuario_id, modulo, accion)
        
        # Verificaciones
        assert resultado['success'] is True
        assert 'revocado correctamente' in resultado['message']
    
    @pytest.mark.skipif(PermissionsManager is None, reason="PermissionsManager no disponible")
    def test_revocar_permiso_inexistente(self):
        """Test revocar permiso que no existe."""
        usuario_id = 2
        modulo = 'inventario'
        accion = 'admin'
        
        mock_cursor = Mock()
        mock_cursor.rowcount = 0  # No se encontró permiso para revocar
        
        self.mock_db.connection.cursor.return_value = mock_cursor
        
        resultado = self.permissions_manager.revocar_permiso_usuario(usuario_id, modulo, accion)
        
        # Verificaciones
        assert resultado['success'] is False
        assert 'no encontrado' in resultado['message']
    
    @pytest.mark.skipif(PermissionsManager is None, reason="PermissionsManager no disponible")
    def test_cambiar_rol_usuario_exitoso(self):
        """Test cambiar rol de usuario exitosamente."""
        usuario_id = 2
        nuevo_rol = 'supervisor'
        
        mock_cursor = Mock()
        mock_cursor.rowcount = 1  # Usuario encontrado y actualizado
        
        self.mock_db.connection.cursor.return_value = mock_cursor
        
        resultado = self.permissions_manager.cambiar_rol_usuario(usuario_id, nuevo_rol)
        
        # Verificaciones
        assert resultado['success'] is True
        assert f'Rol cambiado a {nuevo_rol}' in resultado['message']
    
    @pytest.mark.skipif(PermissionsManager is None, reason="PermissionsManager no disponible")
    def test_cambiar_rol_invalido(self):
        """Test cambiar a rol inválido."""
        usuario_id = 2
        nuevo_rol = 'rol_inexistente'
        
        resultado = self.permissions_manager.cambiar_rol_usuario(usuario_id, nuevo_rol)
        
        # Verificaciones
        assert resultado['success'] is False
        assert 'inválido' in resultado['message']
        assert 'viewer' in resultado['message']  # Debería listar roles válidos
    
    @pytest.mark.skipif(PermissionsManager is None, reason="PermissionsManager no disponible")
    def test_obtener_modulos_permitidos(self):
        """Test obtener módulos permitidos para usuario."""
        usuario_data = {'id': 1}
        
        # Mock de permisos del usuario
        with patch.object(self.permissions_manager, 'obtener_permisos_usuario',
                         return_value=['inventario:read', 'obras:write', 'usuarios:admin']):
            
            modulos = self.permissions_manager.obtener_modulos_permitidos(usuario_data)
            
            # Verificaciones
            assert isinstance(modulos, list)
            assert 'inventario' in modulos
            assert 'obras' in modulos
            assert 'usuarios' in modulos
    
    @pytest.mark.skipif(PermissionsManager is None, reason="PermissionsManager no disponible")
    def test_obtener_estadisticas_permisos(self):
        """Test obtener estadísticas del sistema de permisos."""
        mock_cursor = Mock()
        mock_cursor.fetchall.side_effect = [
            [('admin', 1), ('supervisor', 2), ('operator', 3), ('viewer', 4)],  # Usuarios por rol
            [('inventario', 5), ('obras', 3), ('usuarios', 1)]  # Módulos más utilizados
        ]
        mock_cursor.fetchone.return_value = (15,)  # Permisos específicos
        
        self.mock_db.connection.cursor.return_value = mock_cursor
        
        stats = self.permissions_manager.obtener_estadisticas_permisos()
        
        # Verificaciones
        assert isinstance(stats, dict)
        assert 'usuarios_por_rol' in stats
        assert 'permisos_especificos' in stats
        assert 'modulos_mas_utilizados' in stats
        
        # Verificar estructura de datos
        assert isinstance(stats['usuarios_por_rol'], dict)
        assert stats['usuarios_por_rol']['admin'] == 1
        assert stats['permisos_especificos'] == 15
        assert len(stats['modulos_mas_utilizados']) > 0
    
    @pytest.mark.skipif(SystemModule is None, reason="SystemModule enum no disponible")
    def test_system_module_enum(self):
        """Test del enum de módulos del sistema."""
        # Verificar que contiene los módulos principales
        module_values = [module.value for module in SystemModule]
        
        assert 'usuarios' in module_values
        assert 'inventario' in module_values
        assert 'obras' in module_values
        assert 'auditoria' in module_values
    
    @pytest.mark.skipif(PermissionLevel is None, reason="PermissionLevel enum no disponible")
    def test_permission_level_enum(self):
        """Test del enum de niveles de permisos."""
        # Verificar jerarquía de permisos
        assert PermissionLevel.NONE.value == 0
        assert PermissionLevel.READ.value == 1
        assert PermissionLevel.WRITE.value == 2
        assert PermissionLevel.ADMIN.value == 3
        
        # Verificar orden jerárquico
        assert PermissionLevel.ADMIN.value > PermissionLevel.WRITE.value
        assert PermissionLevel.WRITE.value > PermissionLevel.READ.value


if __name__ == "__main__":
    # Ejecutar tests específicos
    test_suite = TestPermissionsManager()
    test_suite.setup_method()
    
    if PermissionsManager:
        print("=== EJECUTANDO TESTS DE PERMISSIONS MANAGER ===")
        
        try:
            test_suite.test_verificar_permiso_jerarquico()
            print("✅ Test permisos jerárquicos - PASADO")
        except Exception as e:
            print(f"❌ Test permisos jerárquicos - FALLIDO: {e}")
        
        try:
            test_suite.test_cambiar_rol_invalido()
            print("✅ Test rol inválido - PASADO")
        except Exception as e:
            print(f"❌ Test rol inválido - FALLIDO: {e}")
        
        if SystemModule:
            try:
                test_suite.test_system_module_enum()
                print("✅ Test enum módulos - PASADO")
            except Exception as e:
                print(f"❌ Test enum módulos - FALLIDO: {e}")
        
        print("=== TESTS DE PERMISSIONS MANAGER COMPLETADOS ===")
    else:
        print("❌ PermissionsManager no disponible para testing")