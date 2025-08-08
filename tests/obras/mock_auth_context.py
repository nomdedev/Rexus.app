"""
Sistema de contexto de autenticación mock para tests
Permite ejecutar tests sin necesidad de autenticación real
"""
import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Agregar el directorio raíz al path
ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))


class MockAuthContext:
    """Contexto de autenticación mock para testing."""
    
    def __init__(self, user_id='test_user', is_admin=True):
        self.user_id = user_id
        self.is_admin = is_admin
        self.permissions = ['view_obras', 'add_obras', 'change_obras', 'delete_obras', 'edit_obras'] if is_admin else ['view_obras']
    
    def __enter__(self):
        """Entrada del contexto."""
        # Mock del sistema de autenticación
        self.auth_patcher = patch('rexus.core.auth.get_current_user')
        self.auth_mock = self.auth_patcher.start()
        self.auth_mock.return_value = {
            'id': self.user_id,
            'username': self.user_id,
            'is_admin': self.is_admin,
            'permissions': self.permissions
        }
        
        # Mock de decoradores de autenticación
        self.auth_required_patcher = patch('rexus.core.auth_decorators.auth_required')
        self.admin_required_patcher = patch('rexus.core.auth_decorators.admin_required')
        self.permission_required_patcher = patch('rexus.core.auth_decorators.permission_required')
        
        # Los decoradores simplemente retornan la función original
        self.auth_required_mock = self.auth_required_patcher.start()
        self.auth_required_mock.side_effect = lambda func: func
        
        self.admin_required_mock = self.admin_required_patcher.start()
        self.admin_required_mock.side_effect = lambda func: func
        
        self.permission_required_mock = self.permission_required_patcher.start()
        self.permission_required_mock.side_effect = lambda perm: lambda func: func
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Salida del contexto."""
        self.auth_patcher.stop()
        self.auth_required_patcher.stop()
        self.admin_required_patcher.stop()
        self.permission_required_patcher.stop()


class MockDatabaseContext:
    """Contexto de base de datos mock para testing."""
    
    def __init__(self):
        self.mock_connection = Mock()
        self.mock_cursor = Mock()
        self._setup_cursor_behavior()
    
    def _setup_cursor_behavior(self):
        """Configura el comportamiento del cursor mock."""
        # Datos de ejemplo para obras
        self.sample_obras = [
            (1, 'Obra Test 1', '', '', '', 'Cliente Test 1', 'EN_PROCESO', '', '', '', '', '', '', '', '', '', '', '', '', '', 'OBR-001', 'Responsable 1', '2024-01-01', '2024-12-31', 100000.0, '', ''),
            (2, 'Obra Test 2', '', '', '', 'Cliente Test 2', 'PLANIFICACION', '', '', '', '', '', '', '', '', '', '', '', '', '', 'OBR-002', 'Responsable 2', '2024-02-01', '2024-11-30', 150000.0, '', ''),
        ]
        
        # Configurar comportamiento del cursor para diferentes operaciones
        def mock_fetchone(*args, **kwargs):
            # Para verificar duplicados, simular que NO existe la obra (count = 0)
            if hasattr(self.mock_cursor, '_last_sql') and 'count_duplicados_codigo' in self.mock_cursor._last_sql:
                return (0,)  # No hay duplicados
            # Para verificar existencia de tabla
            return (1,)  # La tabla existe
        
        def mock_execute(sql, params=None):
            # Guardar el SQL ejecutado para contexto
            self.mock_cursor._last_sql = str(sql).lower() if sql else ''
            return None
        
        self.mock_cursor.fetchone = Mock(side_effect=mock_fetchone)
        self.mock_cursor.execute = Mock(side_effect=mock_execute)
        self.mock_cursor.fetchall.return_value = self.sample_obras
        self.mock_cursor.rowcount = 1
        self.mock_cursor.description = [
            ('id',), ('nombre',), ('descripcion',), ('cliente',), ('direccion',), 
            ('telefono_contacto',), ('estado',), ('activo',), ('created_at',), 
            ('updated_at',), ('codigo',), ('responsable',), ('fecha_inicio',), 
            ('fecha_fin_estimada',), ('presupuesto_total',)
        ]
        
        # Configurar conexión
        self.mock_connection.cursor.return_value = self.mock_cursor
        self.mock_connection.commit = Mock()
        self.mock_connection.rollback = Mock()
    
    def __enter__(self):
        """Entrada del contexto."""
        # Mock de la conexión a base de datos
        self.db_patcher = patch('rexus.core.database.get_inventario_connection')
        self.db_mock = self.db_patcher.start()
        
        # Mock que retorna una conexión simulada
        mock_db_conn = Mock()
        mock_db_conn.connection = self.mock_connection
        self.db_mock.return_value = mock_db_conn
        
        # Mock del SQL script loader
        self.sql_loader_patcher = patch('rexus.utils.sql_script_loader.sql_script_loader')
        self.sql_loader_mock = self.sql_loader_patcher.start()
        
        # Configurar el mock del script loader
        mock_loader = Mock()
        mock_loader.load_script.return_value = "SELECT COUNT(*) FROM obras WHERE codigo = ?"
        self.sql_loader_mock = mock_loader
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Salida del contexto."""
        self.db_patcher.stop()
        self.sql_loader_patcher.stop()


def setup_test_context():
    """
    Configuración completa del contexto de testing.
    Retorna un contexto que puede ser usado con 'with'.
    """
    class TestContext:
        def __init__(self):
            self.auth_context = MockAuthContext()
            self.db_context = MockDatabaseContext()
        
        def __enter__(self):
            self.auth_context.__enter__()
            self.db_context.__enter__()
            return self
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            self.auth_context.__exit__(exc_type, exc_val, exc_tb)
            self.db_context.__exit__(exc_type, exc_val, exc_tb)
    
    return TestContext()


if __name__ == "__main__":
    print("[INFO] Mock Auth Context - Sistema de testing")
    print("=" * 50)
    
    # Ejemplo de uso
    with setup_test_context() as context:
        print("[OK] Contexto de testing configurado correctamente")
        
        # Simulación de importaciones que funcionarían dentro del contexto
        try:
            from rexus.modules.obras.model import ObrasModel
            from rexus.modules.obras.controller import ObrasController
            print("[OK] Módulos de obras importados exitosamente")
            
            # Crear instancia con mock
            model = ObrasModel(db_connection=context.db_context.mock_connection)
            print("[OK] ObrasModel instanciado con mock DB")
            
            # Test básico
            obras = model.obtener_todas_obras()
            print(f"[OK] Test básico completado - {len(obras)} obras obtenidas")
            
        except Exception as e:
            print(f"[ERROR] Error en test básico: {e}")
    
    print("=" * 50)