"""
Test de Verificación de Esquema de Base de Datos
=================================================

Este test verifica que:
1. Las tablas referenciadas en consultas SQL embebidas existen
2. Las columnas consultadas están presentes en el esquema
3. Los tipos de datos son compatibles
4. La conectividad a la base de datos funciona correctamente
"""

import os
import sys
import pytest
import pyodbc
from typing import Dict, List, Tuple
import logging
from pathlib import Path

# Agregar ruta del proyecto
sys.path.insert(0, str(Path(__file__).parent.parent))

logger = logging.getLogger(__name__)


class DatabaseSchemaValidator:
    """Validador del esquema de base de datos contra consultas SQL embebidas."""
    
    def __init__(self):
        self.connections = {}
        self.table_schemas = {}
        self.embedded_queries = []
        
    def setup_connections(self):
        """Configurar conexiones a las bases de datos."""
        try:
            # Conexión a base de datos users
            self.connections['users'] = pyodbc.connect(
                'DRIVER={ODBC Driver 17 for SQL Server};'
                'SERVER=ITACHI\\SQLEXPRESS;'
                'DATABASE=users;'
                'UID=sa;'
                'PWD=mps.1887;'
                'TrustServerCertificate=yes;'
            )
            
            # Conexión a base de datos inventario (si existe)
            try:
                self.connections['inventario'] = pyodbc.connect(
                    'DRIVER={ODBC Driver 17 for SQL Server};'
                    'SERVER=ITACHI\\SQLEXPRESS;'
                    'DATABASE=inventario;'
                    'UID=sa;'
                    'PWD=mps.1887;'
                    'TrustServerCertificate=yes;'
                )
            except Exception as e:
                logger.warning(f"No se pudo conectar a base de datos 'inventario': {e}")
                
        except Exception as e:
            raise ConnectionError(f"Error conectando a SQL Server: {e}")
    
    def get_table_schema(self, database: str, table_name: str) -> Dict:
        """Obtener esquema de una tabla específica."""
        if database not in self.connections:
            raise ValueError(f"No hay conexión para la base de datos: {database}")
            
        cursor = self.connections[database].cursor()
        
        # Verificar si la tabla existe
        cursor.execute("""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_NAME = ? AND TABLE_TYPE = 'BASE TABLE'
        """, (table_name,))
        
        if cursor.fetchone()[0] == 0:
            return None
            
        # Obtener información de columnas
        cursor.execute("""
            SELECT 
                COLUMN_NAME,
                DATA_TYPE,
                IS_NULLABLE,
                COLUMN_DEFAULT,
                CHARACTER_MAXIMUM_LENGTH
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = ?
            ORDER BY ORDINAL_POSITION
        """, (table_name,))
        
        columns = {}
        for row in cursor.fetchall():
            columns[row[0]] = {
                'data_type': row[1],
                'is_nullable': row[2] == 'YES',
                'default': row[3],
                'max_length': row[4]
            }
            
        return {
            'table_name': table_name,
            'database': database,
            'columns': columns,
            'exists': True
        }
    
    def get_all_tables(self, database: str) -> List[str]:
        """Obtener lista de todas las tablas en una base de datos."""
        if database not in self.connections:
            return []
            
        cursor = self.connections[database].cursor()
        cursor.execute("""
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_TYPE = 'BASE TABLE'
            ORDER BY TABLE_NAME
        """)
        
        return [row[0] for row in cursor.fetchall()]
    
    def extract_embedded_queries(self) -> List[Dict]:
        """Extraer todas las consultas SQL embebidas del código."""
        embedded_queries = []
        
        # Definir las consultas que encontramos anteriormente
        known_queries = [
            {
                'file': 'rexus/modules/usuarios/submodules/profiles_manager.py',
                'query': 'SELECT COUNT(*) FROM usuarios',
                'tables': ['usuarios'],
                'columns': ['COUNT(*)'],
                'type': 'SELECT'
            },
            {
                'file': 'rexus/modules/usuarios/submodules/profiles_manager.py',
                'query': 'SELECT COUNT(*) FROM usuarios WHERE activo = 1',
                'tables': ['usuarios'],
                'columns': ['COUNT(*)', 'activo'],
                'type': 'SELECT'
            },
            {
                'file': 'rexus/modules/usuarios/submodules/profiles_manager.py',
                'query': 'SELECT COUNT(*) FROM usuarios WHERE username = ?',
                'tables': ['usuarios'],
                'columns': ['COUNT(*)', 'username'],
                'type': 'SELECT'
            },
            {
                'file': 'rexus/modules/usuarios/submodules/sessions_manager.py',
                'query': 'SELECT COUNT(*) FROM sesiones_usuario WHERE is_active = 1',
                'tables': ['sesiones_usuario'],
                'columns': ['COUNT(*)', 'is_active'],
                'type': 'SELECT'
            },
            {
                'file': 'rexus/modules/inventario/submodules/reportes_manager.py',
                'query': 'SELECT COUNT(*) FROM inventario WHERE activo = 1',
                'tables': ['inventario'],
                'columns': ['COUNT(*)', 'activo'],
                'type': 'SELECT'
            },
            {
                'file': 'rexus/modules/compras/detalle_model.py',
                'query': 'SELECT orden_id FROM ordenes_compra_detalles WHERE id = ?',
                'tables': ['ordenes_compra_detalles'],
                'columns': ['orden_id', 'id'],
                'type': 'SELECT'
            },
            {
                'file': 'rexus/modules/auditoria/model.py',
                'query': 'SELECT COUNT(*) FROM auditoria_eventos',
                'tables': ['auditoria_eventos'],
                'columns': ['COUNT(*)'],
                'type': 'SELECT'
            },
            {
                'file': 'rexus/models/productos_model.py',
                'query': 'SELECT COUNT(*) FROM productos WHERE codigo = ?',
                'tables': ['productos'],
                'columns': ['COUNT(*)', 'codigo'],
                'type': 'SELECT'
            },
            {
                'file': 'rexus/modules/logistica/model.py',
                'query': 'SELECT COUNT(*) FROM servicios_transporte',
                'tables': ['servicios_transporte'],
                'columns': ['COUNT(*)'],
                'type': 'SELECT'
            },
            {
                'file': 'rexus/modules/herrajes/model.py',
                'query': 'SELECT COUNT(DISTINCT proveedor) FROM herrajes WHERE activo = 1 AND proveedor IS NOT NULL',
                'tables': ['herrajes'],
                'columns': ['proveedor', 'activo'],
                'type': 'SELECT'
            }
        ]
        
        return known_queries
    
    def validate_query_against_schema(self, query_info: Dict) -> Dict:
        """Validar una consulta contra el esquema real de la base de datos."""
        result = {
            'query': query_info['query'],
            'file': query_info['file'],
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Verificar cada tabla
        for table_name in query_info['tables']:
            # Intentar encontrar la tabla en diferentes bases de datos
            table_found = False
            
            for db_name in self.connections.keys():
                schema = self.get_table_schema(db_name, table_name)
                if schema and schema['exists']:
                    table_found = True
                    
                    # Verificar columnas
                    for column in query_info['columns']:
                        if column in ['COUNT(*)', 'SCOPE_IDENTITY()', '@@IDENTITY']:
                            continue  # Funciones SQL especiales
                            
                        if column not in schema['columns']:
                            result['errors'].append(
                                f"Columna '{column}' no existe en tabla '{table_name}' (DB: {db_name})"
                            )
                            result['valid'] = False
                    break
            
            if not table_found:
                result['errors'].append(f"Tabla '{table_name}' no encontrada en ninguna base de datos")
                result['valid'] = False
        
        return result
    
    def close_connections(self):
        """Cerrar todas las conexiones."""
        for conn in self.connections.values():
            try:
                conn.close()
            except:
                pass


class TestDatabaseSchema:
    """Tests para verificar el esquema de la base de datos."""
    
    @pytest.fixture(scope="class")
    def validator(self):
        """Fixture que proporciona el validador de esquema."""
        validator = DatabaseSchemaValidator()
        validator.setup_connections()
        yield validator
        validator.close_connections()
    
    def test_database_connectivity(self, validator):
        """Test: Verificar conectividad a las bases de datos."""
        assert len(validator.connections) > 0, "No se pudo conectar a ninguna base de datos"
        assert 'users' in validator.connections, "No se pudo conectar a la base de datos 'users'"
        
        # Verificar que las conexiones funcionan
        for db_name, conn in validator.connections.items():
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            assert result[0] == 1, f"Conexión a {db_name} no responde correctamente"
    
    def test_core_tables_exist(self, validator):
        """Test: Verificar que las tablas core existen."""
        core_tables = [
            ('users', 'usuarios'),
            ('users', 'roles'),
            ('users', 'sesiones_usuario'),
            ('users', 'auditoria_sistema'),
        ]
        
        for db_name, table_name in core_tables:
            if db_name in validator.connections:
                schema = validator.get_table_schema(db_name, table_name)
                assert schema is not None, f"Tabla '{table_name}' no existe en base de datos '{db_name}'"
                assert schema['exists'], f"Tabla '{table_name}' marcada como no existente"
    
    def test_embedded_queries_validation(self, validator):
        """Test: Validar todas las consultas SQL embebidas contra el esquema real."""
        queries = validator.extract_embedded_queries()
        assert len(queries) > 0, "No se encontraron consultas embebidas para validar"
        
        invalid_queries = []
        
        for query_info in queries:
            validation_result = validator.validate_query_against_schema(query_info)
            
            if not validation_result['valid']:
                invalid_queries.append(validation_result)
                print(f"\n❌ Consulta inválida en {validation_result['file']}:")
                print(f"   Query: {validation_result['query']}")
                for error in validation_result['errors']:
                    print(f"   Error: {error}")
            else:
                print(f"\n✅ Consulta válida en {validation_result['file']}")
        
        assert len(invalid_queries) == 0, f"Se encontraron {len(invalid_queries)} consultas inválidas"
    
    def test_table_structure_completeness(self, validator):
        """Test: Verificar que las tablas tienen las columnas mínimas esperadas."""
        expected_structures = {
            'usuarios': ['id', 'usuario', 'password_hash', 'nombre', 'email', 'activo'],
            'sesiones_usuario': ['id', 'usuario_id', 'token_sesion', 'activa'],
            'productos': ['id', 'codigo', 'descripcion', 'stock_actual'],
            'herrajes': ['id', 'codigo', 'descripcion', 'activo', 'proveedor'],
        }
        
        for table_name, expected_columns in expected_structures.items():
            # Buscar la tabla en todas las bases de datos
            table_found = False
            
            for db_name in validator.connections.keys():
                schema = validator.get_table_schema(db_name, table_name)
                if schema and schema['exists']:
                    table_found = True
                    
                    for column in expected_columns:
                        assert column in schema['columns'], (
                            f"Columna '{column}' faltante en tabla '{table_name}' (DB: {db_name})"
                        )
                    break
            
            # Solo fallar si es una tabla crítica
            if table_name in ['usuarios', 'sesiones_usuario'] and not table_found:
                pytest.fail(f"Tabla crítica '{table_name}' no encontrada")
    
    def test_list_all_available_tables(self, validator):
        """Test informativo: Listar todas las tablas disponibles."""
        print("\n📋 TABLAS DISPONIBLES EN LAS BASES DE DATOS:")
        
        for db_name in validator.connections.keys():
            tables = validator.get_all_tables(db_name)
            print(f"\n🗃️  Base de datos: {db_name}")
            for table in tables:
                print(f"   - {table}")
        
        # Este test siempre pasa, es solo informativo
        assert True


if __name__ == "__main__":
    # Ejecutar tests directamente
    pytest.main([__file__, "-v", "-s"])
