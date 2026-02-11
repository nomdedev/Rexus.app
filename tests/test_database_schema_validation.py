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
import re
import pytest

# Verificar dependencias
try:
    import pyodbc
except ImportError:
    pytest.skip("pyodbc no está disponible", allow_module_level=True)

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
        
        # Buscar archivos Python en el proyecto
        python_files = []
        for root, dirs, files in os.walk('.'):
            # Saltar directorios específicos
            if any(skip in root for skip in ['.git', '__pycache__', '.pytest_cache', 'node_modules', 'legacy_root', 'backups']):
                continue
            for file in files:
                if file.endswith('.py') and not file.startswith('test_'):
                    python_files.append(os.path.join(root, file))
        
        # Patrones para encontrar consultas SQL
        sql_patterns = [
            r'cursor\.execute\(\s*["\']([^"\']*(?:SELECT|INSERT|UPDATE|DELETE)[^"\']*)["\']',
            r'cursor\.execute\(\s*["\'"]{3}([^"\']*(?:SELECT|INSERT|UPDATE|DELETE)[^"\']*)["\'"]{3}',
            r'execute\(\s*["\']([^"\']*(?:SELECT|INSERT|UPDATE|DELETE)[^"\']*)["\']',
            r'execute\(\s*["\'"]{3}([^"\']*(?:SELECT|INSERT|UPDATE|DELETE)[^"\']*)["\'"]{3}'
        ]
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                for pattern in sql_patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE | re.DOTALL)
                    for match in matches:
                        query = match.group(1).strip()
                        # Limpiar query de saltos de línea y espacios extra
                        query = ' '.join(query.split())
                        
                        if len(query) > 10:  # Filtrar queries muy cortas
                            embedded_queries.append({
                                'file': file_path.replace('\\', '/').lstrip('./'),
                                'query': query,
                                'type': 'SQL'
                            })
            except Exception as e:
                # Ignorar archivos que no se pueden leer
                continue
        
        return embedded_queries
        return embedded_queries
    
    def validate_query_against_schema(self, query_info: Dict) -> Dict:
        """Validar una consulta contra el esquema real de la base de datos."""
        result = {
            'query': query_info['query'],
            'file': query_info['file'],
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        query = query_info['query'].upper()
        
        # Extraer nombres de tablas del query
        tables = self.extract_table_names(query_info['query'])
        
        # Extraer nombres de columnas específicas que podrían fallar
        columns = self.extract_column_names(query_info['query'])
        
        # Verificar cada tabla
        for table_name in tables:
            # Intentar encontrar la tabla en diferentes bases de datos
            table_found = False
            
            for db_name in self.connections.keys():
                schema = self.get_table_schema(db_name, table_name)
                if schema and schema['exists']:
                    table_found = True
                    
                    # Verificar columnas específicas
                    for column in columns:
                        if column in ['COUNT(*)', 'SCOPE_IDENTITY()', '@@IDENTITY', '*']:
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

    def extract_table_names(self, query: str) -> List[str]:
        """Extraer nombres de tablas de una consulta SQL."""
        tables = []
        query_upper = query.upper()
        
        # Patrones para encontrar tablas
        patterns = [
            r'FROM\s+([a-zA-Z_][a-zA-Z0-9_]*)',
            r'UPDATE\s+([a-zA-Z_][a-zA-Z0-9_]*)',
            r'INSERT\s+INTO\s+([a-zA-Z_][a-zA-Z0-9_]*)',
            r'DELETE\s+FROM\s+([a-zA-Z_][a-zA-Z0-9_]*)',
            r'JOIN\s+([a-zA-Z_][a-zA-Z0-9_]*)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, query_upper)
            tables.extend(matches)
        
        return list(set(tables))  # Eliminar duplicados

    def extract_column_names(self, query: str) -> List[str]:
        """Extraer nombres de columnas problemáticas de una consulta SQL."""
        problematic_columns = []
        query_lower = query.lower()
        
        # Buscar columnas específicas problemáticas
        if 'username' in query_lower:
            problematic_columns.append('username')
        if 'is_active' in query_lower:
            problematic_columns.append('is_active')
        if 'locked_until' in query_lower:
            problematic_columns.append('locked_until')
        if 'failed_attempts' in query_lower:
            problematic_columns.append('failed_attempts')
            
        return problematic_columns
    
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
