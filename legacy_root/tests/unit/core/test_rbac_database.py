"""
Tests para Sistema RBAC en Base de Datos - Rexus.app

Tests que validan el sistema completo de control de acceso basado en roles,
incluyendo gestión de usuarios, roles, permisos, políticas y auditoría.

Author: Rexus Testing Team
Date: 2025-08-11
Version: 1.0.0
"""

import pytest
import tempfile
import os
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

# Import the modules we're testing
try:
    from rexus.core.rbac_database import (
        RBACDatabase,
        Role,
        Permission,
        Policy,
        AccessAttempt,
        PermissionAction,
        AccessResult,
        init_rbac_system,
        get_rbac_system,
        check_permission,
        require_permission
    )
    RBAC_DATABASE_AVAILABLE = True
except ImportError:
    RBAC_DATABASE_AVAILABLE = False


@pytest.mark.skipif(not RBAC_DATABASE_AVAILABLE, reason="RBAC database modules not available")
class TestRBACDatabase:
    """Tests para la clase RBACDatabase."""
    
    def test_initialization(self):
        """Test que valida la inicialización del sistema RBAC."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp_file:
            db_path = tmp_file.name
        
        try:
            rbac = RBACDatabase(db_path)
            
            assert rbac.db_path == db_path
            assert isinstance(rbac.permission_cache, dict)
            assert rbac.cache_timeout.total_seconds() == 900  # 15 minutos
            
            # Verificar que se crearon las tablas
            with rbac._get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                
                expected_tables = [
                    'rbac_roles', 'rbac_permissions', 'rbac_user_roles',
                    'rbac_role_permissions', 'rbac_policies', 'rbac_access_log'
                ]
                
                for table in expected_tables:
                    assert table in tables
        finally:
            os.unlink(db_path)
    
    def test_create_default_roles(self):
        """Test que valida la creación de roles por defecto."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp_file:
            db_path = tmp_file.name
        
        try:
            rbac = RBACDatabase(db_path)
            
            with rbac._get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM rbac_roles ORDER BY id")
                roles = [row[0] for row in cursor.fetchall()]
                
                expected_roles = ["super_admin", "admin", "manager", "user", "viewer"]
                for role in expected_roles:
                    assert role in roles
        finally:
            os.unlink(db_path)
    
    def test_create_role(self):
        """Test que valida la creación de nuevos roles."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp_file:
            db_path = tmp_file.name
        
        try:
            rbac = RBACDatabase(db_path)
            
            role_id = rbac.create_role("test_role", "Role for testing", parent_id=1)
            
            assert isinstance(role_id, int)
            assert role_id > 0
            
            # Verificar que el rol se creó correctamente
            with rbac._get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name, description, parent_id FROM rbac_roles WHERE id = ?", (role_id,))
                role = cursor.fetchone()
                
                assert role is not None
                assert role[0] == "test_role"
                assert role[1] == "Role for testing"
                assert role[2] == 1
        finally:
            os.unlink(db_path)
    
    def test_create_permission(self):
        """Test que valida la creación de nuevos permisos."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp_file:
            db_path = tmp_file.name
        
        try:
            rbac = RBACDatabase(db_path)
            
            permission_id = rbac.create_permission("test_resource", "test_action", "Test permission")
            
            assert isinstance(permission_id, int)
            assert permission_id > 0
            
            # Verificar que el permiso se creó correctamente
            with rbac._get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT resource, action, description FROM rbac_permissions WHERE id = ?", 
                    (permission_id,)
                )
                permission = cursor.fetchone()
                
                assert permission is not None
                assert permission[0] == "test_resource"
                assert permission[1] == "test_action"
                assert permission[2] == "Test permission"
        finally:
            os.unlink(db_path)
    
    def test_assign_role_to_user(self):
        """Test que valida la asignación de roles a usuarios."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp_file:
            db_path = tmp_file.name
        
        try:
            rbac = RBACDatabase(db_path)
            
            user_id = 1
            role_id = 2  # admin role
            granted_by = 1
            
            success = rbac.assign_role_to_user(user_id, role_id, granted_by)
            
            assert success
            
            # Verificar que la asignación se guardó
            with rbac._get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT user_id, role_id, granted_by FROM rbac_user_roles WHERE user_id = ? AND role_id = ?",
                    (user_id, role_id)
                )
                assignment = cursor.fetchone()
                
                assert assignment is not None
                assert assignment[0] == user_id
                assert assignment[1] == role_id
                assert assignment[2] == granted_by
        finally:
            os.unlink(db_path)
    
    def test_assign_permission_to_role(self):
        """Test que valida la asignación de permisos a roles."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp_file:
            db_path = tmp_file.name
        
        try:
            rbac = RBACDatabase(db_path)
            
            # Crear un permiso de prueba
            permission_id = rbac.create_permission("test_resource", "test_action", "Test permission")
            role_id = 2  # admin role
            granted_by = 1
            
            success = rbac.assign_permission_to_role(role_id, permission_id, granted_by)
            
            assert success
            
            # Verificar que la asignación se guardó
            with rbac._get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT role_id, permission_id, granted_by FROM rbac_role_permissions WHERE role_id = ? AND permission_id = ?",
                    (role_id, permission_id)
                )
                assignment = cursor.fetchone()
                
                assert assignment is not None
                assert assignment[0] == role_id
                assert assignment[1] == permission_id
                assert assignment[2] == granted_by
        finally:
            os.unlink(db_path)
    
    def test_check_access_granted(self):
        """Test que valida el acceso concedido para usuarios con permisos."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp_file:
            db_path = tmp_file.name
        
        try:
            rbac = RBACDatabase(db_path)
            
            # Setup: crear usuario con permisos
            user_id = 1
            role_id = 2  # admin
            permission_id = rbac.create_permission("test_resource", "read", "Read test resource")
            
            rbac.assign_role_to_user(user_id, role_id, 1)
            rbac.assign_permission_to_role(role_id, permission_id, 1)
            
            # Test
            result, message = rbac.check_access(user_id, "test_resource", "read")
            
            assert result == AccessResult.GRANTED
            assert "concedido" in message.lower()
        finally:
            os.unlink(db_path)
    
    def test_check_access_denied(self):
        """Test que valida el acceso denegado para usuarios sin permisos."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp_file:
            db_path = tmp_file.name
        
        try:
            rbac = RBACDatabase(db_path)
            
            user_id = 1
            
            # Test acceso a recurso sin permisos
            result, message = rbac.check_access(user_id, "restricted_resource", "admin")
            
            assert result == AccessResult.DENIED
            assert "denegado" in message.lower() or "permisos" in message.lower()
        finally:
            os.unlink(db_path)
    
    def test_role_inheritance(self):
        """Test que valida la herencia de permisos entre roles."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp_file:
            db_path = tmp_file.name
        
        try:
            rbac = RBACDatabase(db_path)
            
            # Setup: crear jerarquía de roles
            parent_role_id = rbac.create_role("parent_role", "Parent role")
            child_role_id = rbac.create_role("child_role", "Child role", parent_id=parent_role_id)
            
            permission_id = rbac.create_permission("inherited_resource", "read", "Inherited permission")
            
            # Asignar permiso al rol padre
            rbac.assign_permission_to_role(parent_role_id, permission_id, 1)
            
            # Asignar rol hijo al usuario
            user_id = 1
            rbac.assign_role_to_user(user_id, child_role_id, 1)
            
            # Test: usuario debe tener acceso por herencia
            result, message = rbac.check_access(user_id, "inherited_resource", "read")
            
            assert result == AccessResult.GRANTED
        finally:
            os.unlink(db_path)
    
    def test_get_user_roles(self):
        """Test que valida la obtención de roles de usuario."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp_file:
            db_path = tmp_file.name
        
        try:
            rbac = RBACDatabase(db_path)
            
            user_id = 1
            role_id1 = 2  # admin
            role_id2 = 3  # manager
            
            rbac.assign_role_to_user(user_id, role_id1, 1)
            rbac.assign_role_to_user(user_id, role_id2, 1)
            
            roles = rbac.get_user_roles(user_id)
            
            assert len(roles) == 2
            assert all(isinstance(role, Role) for role in roles)
            
            role_names = [role.name for role in roles]
            assert "admin" in role_names
            assert "manager" in role_names
        finally:
            os.unlink(db_path)
    
    def test_get_role_permissions(self):
        """Test que valida la obtención de permisos de rol."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp_file:
            db_path = tmp_file.name
        
        try:
            rbac = RBACDatabase(db_path)
            
            role_id = 2  # admin
            permission_id1 = rbac.create_permission("resource1", "read", "Read resource 1")
            permission_id2 = rbac.create_permission("resource2", "write", "Write resource 2")
            
            rbac.assign_permission_to_role(role_id, permission_id1, 1)
            rbac.assign_permission_to_role(role_id, permission_id2, 1)
            
            permissions = rbac.get_role_permissions(role_id)
            
            assert len(permissions) >= 2  # Al menos los que acabamos de asignar
            assert all(isinstance(perm, Permission) for perm in permissions)
            
            # Verificar que nuestros permisos están incluidos
            permission_actions = [(p.resource, p.action) for p in permissions]
            assert ("resource1", "read") in permission_actions
            assert ("resource2", "write") in permission_actions
        finally:
            os.unlink(db_path)
    
    def test_access_statistics(self):
        """Test que valida las estadísticas de acceso."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp_file:
            db_path = tmp_file.name
        
        try:
            rbac = RBACDatabase(db_path)
            
            user_id = 1
            
            # Simular varios accesos
            rbac._log_access_attempt(user_id, "resource1", "read", AccessResult.GRANTED)
            rbac._log_access_attempt(user_id, "resource1", "read", AccessResult.GRANTED)
            rbac._log_access_attempt(user_id, "resource2", "write", AccessResult.DENIED)
            rbac._log_access_attempt(user_id, "resource3", "delete", AccessResult.GRANTED)
            
            stats = rbac.get_access_statistics(user_id=user_id)
            
            assert stats["total_accesses"] == 4
            assert "access_by_result" in stats
            assert "top_resources" in stats
            assert "period_days" in stats
            
            # Verificar conteos por resultado
            assert "GRANTED" in stats["access_by_result"]
            assert "DENIED" in stats["access_by_result"]
            assert stats["access_by_result"]["GRANTED"] == 3
            assert stats["access_by_result"]["DENIED"] == 1
        finally:
            os.unlink(db_path)
    
    def test_cleanup_expired_assignments(self):
        """Test que valida la limpieza de asignaciones expiradas."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp_file:
            db_path = tmp_file.name
        
        try:
            rbac = RBACDatabase(db_path)
            
            user_id = 1
            role_id = 2
            
            # Crear asignación con fecha de expiración pasada
            expired_date = (datetime.now() - timedelta(days=1)).isoformat()
            rbac.assign_role_to_user(user_id, role_id, 1, expires_at=expired_date)
            
            # Verificar que existe la asignación
            with rbac._get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT COUNT(*) FROM rbac_user_roles WHERE user_id = ? AND role_id = ? AND is_active = 1",
                    (user_id, role_id)
                )
                active_count_before = cursor.fetchone()[0]
                assert active_count_before == 1
            
            # Ejecutar limpieza
            expired_count = rbac.cleanup_expired_assignments()
            
            assert expired_count == 1
            
            # Verificar que la asignación fue desactivada
            with rbac._get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT COUNT(*) FROM rbac_user_roles WHERE user_id = ? AND role_id = ? AND is_active = 1",
                    (user_id, role_id)
                )
                active_count_after = cursor.fetchone()[0]
                assert active_count_after == 0
        finally:
            os.unlink(db_path)
    
    def test_permission_cache(self):
        """Test que valida el funcionamiento del caché de permisos."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp_file:
            db_path = tmp_file.name
        
        try:
            rbac = RBACDatabase(db_path)
            
            # Setup usuario con permiso
            user_id = 1
            role_id = 2
            permission_id = rbac.create_permission("cached_resource", "read", "Cached permission")
            
            rbac.assign_role_to_user(user_id, role_id, 1)
            rbac.assign_permission_to_role(role_id, permission_id, 1)
            
            # Primera verificación (debería usar DB y poblar caché)
            has_permission1 = rbac._check_user_permissions(user_id, "cached_resource", "read")
            
            # Segunda verificación (debería usar caché)
            has_permission2 = rbac._check_user_permissions(user_id, "cached_resource", "read")
            
            assert has_permission1 == has_permission2 == True
            
            # Verificar que está en caché
            cache_key = f"{user_id}:cached_resource:read"
            assert cache_key in rbac.permission_cache
        finally:
            os.unlink(db_path)


@pytest.mark.skipif(not RBAC_DATABASE_AVAILABLE, reason="RBAC database modules not available")
class TestRBACGlobalFunctions:
    """Tests para las funciones globales del sistema RBAC."""
    
    def test_init_and_get_rbac_system(self):
        """Test que valida la inicialización global del sistema RBAC."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp_file:
            db_path = tmp_file.name
        
        try:
            # Inicializar sistema
            rbac = init_rbac_system(db_path)
            
            assert rbac is not None
            assert isinstance(rbac, RBACDatabase)
            
            # Obtener instancia global
            global_rbac = get_rbac_system()
            
            assert global_rbac is rbac
        finally:
            os.unlink(db_path)
    
    def test_check_permission_global(self):
        """Test que valida la función global de verificación de permisos."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp_file:
            db_path = tmp_file.name
        
        try:
            init_rbac_system(db_path)
            rbac = get_rbac_system()
            
            # Setup usuario con permiso
            user_id = 1
            role_id = 2
            permission_id = rbac.create_permission("global_resource", "read", "Global permission")
            
            rbac.assign_role_to_user(user_id, role_id, 1)
            rbac.assign_permission_to_role(role_id, permission_id, 1)
            
            # Test función global
            has_permission = check_permission(user_id, "global_resource", "read")
            
            assert has_permission == True
            
            # Test permiso no otorgado
            no_permission = check_permission(user_id, "restricted_resource", "admin")
            
            assert no_permission == False
        finally:
            os.unlink(db_path)
    
    def test_require_permission_decorator(self):
        """Test que valida el decorador de permisos requeridos."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp_file:
            db_path = tmp_file.name
        
        try:
            init_rbac_system(db_path)
            rbac = get_rbac_system()
            
            # Setup usuario con permiso
            user_id = 1
            role_id = 2
            permission_id = rbac.create_permission("decorator_resource", "execute", "Decorator permission")
            
            rbac.assign_role_to_user(user_id, role_id, 1)
            rbac.assign_permission_to_role(role_id, permission_id, 1)
            
            @require_permission("decorator_resource", "execute")
            def protected_function(**kwargs):
                return "success"
            
            # Test con permisos (debe funcionar)
            result = protected_function(current_user_id=user_id)
            assert result == "success"
            
            # Test sin permisos (debe fallar)
            @require_permission("restricted_resource", "admin")
            def restricted_function(**kwargs):
                return "restricted"
            
            with pytest.raises(PermissionError):
                restricted_function(current_user_id=user_id)
        finally:
            os.unlink(db_path)


@pytest.mark.skipif(not RBAC_DATABASE_AVAILABLE, reason="RBAC database modules not available")
class TestRBACIntegration:
    """Tests de integración para el sistema RBAC."""
    
    def test_complete_rbac_workflow(self):
        """Test que valida el flujo completo de RBAC."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp_file:
            db_path = tmp_file.name
        
        try:
            init_rbac_system(db_path)
            rbac = get_rbac_system()
            
            # 1. Crear estructura organizacional
            ceo_role_id = rbac.create_role("ceo", "Chief Executive Officer")
            manager_role_id = rbac.create_role("department_manager", "Department Manager", parent_id=ceo_role_id)
            employee_role_id = rbac.create_role("employee", "Regular Employee", parent_id=manager_role_id)
            
            # 2. Definir permisos
            perm_admin_id = rbac.create_permission("system", "admin", "Full system administration")
            perm_manage_id = rbac.create_permission("department", "manage", "Manage department")
            perm_read_id = rbac.create_permission("documents", "read", "Read documents")
            
            # 3. Asignar permisos a roles
            rbac.assign_permission_to_role(ceo_role_id, perm_admin_id, 1)
            rbac.assign_permission_to_role(manager_role_id, perm_manage_id, 1)
            rbac.assign_permission_to_role(employee_role_id, perm_read_id, 1)
            
            # 4. Asignar roles a usuarios
            ceo_user = 1
            manager_user = 2
            employee_user = 3
            
            rbac.assign_role_to_user(ceo_user, ceo_role_id, 1)
            rbac.assign_role_to_user(manager_user, manager_role_id, 1)
            rbac.assign_role_to_user(employee_user, employee_role_id, 1)
            
            # 5. Verificar accesos - CEO debe tener todos los permisos por herencia
            assert check_permission(ceo_user, "system", "admin")
            assert check_permission(ceo_user, "department", "manage")
            assert check_permission(ceo_user, "documents", "read")
            
            # 6. Verificar accesos - Manager debe tener permisos limitados
            assert not check_permission(manager_user, "system", "admin")
            assert check_permission(manager_user, "department", "manage")
            assert check_permission(manager_user, "documents", "read")
            
            # 7. Verificar accesos - Employee solo lectura
            assert not check_permission(employee_user, "system", "admin")
            assert not check_permission(employee_user, "department", "manage")
            assert check_permission(employee_user, "documents", "read")
            
            # 8. Verificar estadísticas
            stats = rbac.get_access_statistics()
            assert stats["total_accesses"] > 0
            
        finally:
            os.unlink(db_path)
    
    def test_temporal_role_assignments(self):
        """Test que valida asignaciones temporales de roles."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp_file:
            db_path = tmp_file.name
        
        try:
            init_rbac_system(db_path)
            rbac = get_rbac_system()
            
            user_id = 1
            temp_role_id = rbac.create_role("temp_admin", "Temporary Administrator")
            perm_id = rbac.create_permission("temp_resource", "admin", "Temporary admin access")
            
            rbac.assign_permission_to_role(temp_role_id, perm_id, 1)
            
            # Asignar rol temporal (ya expirado para test)
            expired_date = (datetime.now() - timedelta(hours=1)).isoformat()
            rbac.assign_role_to_user(user_id, temp_role_id, 1, expires_at=expired_date)
            
            # El usuario no debería tener acceso debido a expiración
            assert not check_permission(user_id, "temp_resource", "admin")
            
            # Limpiar asignaciones expiradas
            expired_count = rbac.cleanup_expired_assignments()
            assert expired_count == 1
            
        finally:
            os.unlink(db_path)
    
    @patch('rexus.utils.secure_logger.log_security_event')
    def test_security_audit_integration(self, mock_log):
        """Test que valida la integración con auditoría de seguridad."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp_file:
            db_path = tmp_file.name
        
        try:
            init_rbac_system(db_path)
            rbac = get_rbac_system()
            
            user_id = 1
            role_id = rbac.create_role("audit_test_role", "Role for audit test")
            
            # Las operaciones deben generar logs de seguridad
            rbac.assign_role_to_user(user_id, role_id, 1)
            
            # Verificar que se loguearon eventos de seguridad
            mock_log.assert_called()
            
            # Verificar tipos de eventos logueados
            call_args_list = mock_log.call_args_list
            event_types = [call[0][0] for call in call_args_list]
            
            assert "RBAC_SYSTEM_INITIALIZED" in event_types
            assert "ROLE_CREATED" in event_types
            assert "ROLE_ASSIGNED" in event_types
            
        finally:
            os.unlink(db_path)


# Fixtures para tests de RBAC
@pytest.fixture
def temp_rbac_db():
    """Fixture que proporciona base de datos temporal para RBAC."""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp_file:
        db_path = tmp_file.name
    
    yield db_path
    
    if os.path.exists(db_path):
        os.unlink(db_path)


@pytest.fixture
def rbac_with_sample_data(temp_rbac_db):
    """Fixture que proporciona sistema RBAC con datos de prueba."""
    rbac = RBACDatabase(temp_rbac_db)
    
    # Crear estructura básica
    admin_role = rbac.create_role("test_admin", "Test Administrator")
    user_role = rbac.create_role("test_user", "Test User")
    
    read_perm = rbac.create_permission("test_resource", "read", "Read test resource")
    write_perm = rbac.create_permission("test_resource", "write", "Write test resource")
    
    rbac.assign_permission_to_role(admin_role, read_perm, 1)
    rbac.assign_permission_to_role(admin_role, write_perm, 1)
    rbac.assign_permission_to_role(user_role, read_perm, 1)
    
    return rbac


@pytest.fixture
def rbac_test_data():
    """Fixture con datos de prueba para tests de RBAC."""
    return {
        'users': [
            {'id': 1, 'name': 'admin_user'},
            {'id': 2, 'name': 'manager_user'},
            {'id': 3, 'name': 'regular_user'},
            {'id': 4, 'name': 'guest_user'}
        ],
        'roles': [
            {'name': 'system_admin', 'description': 'System Administrator'},
            {'name': 'content_manager', 'description': 'Content Manager'},
            {'name': 'regular_user', 'description': 'Regular User'},
            {'name': 'guest', 'description': 'Guest User'}
        ],
        'permissions': [
            {'resource': 'users', 'action': 'create'},
            {'resource': 'users', 'action': 'read'},
            {'resource': 'users', 'action': 'update'},
            {'resource': 'users', 'action': 'delete'},
            {'resource': 'content', 'action': 'create'},
            {'resource': 'content', 'action': 'read'},
            {'resource': 'content', 'action': 'update'},
            {'resource': 'system', 'action': 'admin'}
        ]
    }