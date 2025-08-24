"""
Gestor de consultas SQL centralizado y seguro para Rexus.app v2.0.0

Proporciona interfaz unificada para operaciones de base de datos con
protección completa contra SQL injection y gestión segura de transacciones.

Fecha: 24/08/2025
Objetivo: Operaciones SQL seguras y centralizadas
"""

import logging
import re
from contextlib import contextmanager
from typing import Dict, List, Optional, Tuple, Any, Union

# Importar logging
try:
    from ..utils.app_logger import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class SQLQueryManager:
    """Gestor centralizado y seguro de consultas SQL para Rexus.app."""
    
    def __init__(self, db_connection=None):
        """
        Inicializa el gestor de consultas SQL.
        
        Args:
            db_connection: Conexión a la base de datos
        """
        self.db_connection = db_connection
        self._transaction_active = False
        
        # Patrones peligrosos para validación
        self.dangerous_patterns = [
            r'drop\s+table',
            r'delete\s+from.*where\s+1\s*=\s*1',
            r'truncate\s+table',
            r'alter\s+table',
            r'create\s+table',
            r'union\s+select',
            r'--\s*$',
            r'/\*.*?\*/',
            r'xp_cmdshell',
            r'sp_executesql',
            r'exec\s*\(',
            r'eval\s*\(',
        ]
        
        logger.info("SQLQueryManager inicializado")
    
    def set_connection(self, db_connection):
        """
        Establece la conexión a la base de datos.
        
        Args:
            db_connection: Conexión a la base de datos
        """
        self.db_connection = db_connection
        logger.info("Conexión de base de datos establecida")
    
    @contextmanager
    def get_cursor(self):
        """
        Context manager para obtener y gestionar cursores de base de datos.
        
        Yields:
            Cursor de la base de datos
        """
        if not self.db_connection:
            raise ValueError("No hay conexión de base de datos establecida")
        
        cursor = None
        try:
            cursor = self.db_connection.cursor()
            yield cursor
        except Exception as e:
            logger.error(f"Error en operación de base de datos: {e}")
            if self.db_connection:
                try:
                    self.db_connection.rollback()
                except Exception:
                    pass  # Ignorar errores de rollback
            raise
        finally:
            if cursor:
                try:
                    cursor.close()
                except Exception:
                    pass  # Ignorar errores de cierre
    
    def _is_safe_query(self, query: str) -> bool:
        """
        Verifica que una consulta SQL sea segura.
        
        Args:
            query: Consulta SQL a verificar
            
        Returns:
            True si la consulta es segura
        """
        if not query or not isinstance(query, str):
            return False
        
        query_lower = query.lower().strip()
        
        # Verificar patrones peligrosos
        for pattern in self.dangerous_patterns:
            if re.search(pattern, query_lower, re.IGNORECASE | re.MULTILINE):
                logger.warning(f"Patrón peligroso detectado en query: {pattern}")
                return False
        
        return True
    
    def _sanitize_identifier(self, identifier: str) -> str:
        """
        Sanitiza identificadores SQL (nombres de tabla, columna, etc.).
        
        Args:
            identifier: Identificador a sanitizar
            
        Returns:
            Identificador sanitizado
            
        Raises:
            ValueError: Si el identificador no es válido
        """
        if not identifier or not isinstance(identifier, str):
            raise ValueError("Identificador inválido o vacío")
        
        # Solo permitir letras, números, guiones bajos y puntos
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_.]*$', identifier):
            raise ValueError(f"Identificador contiene caracteres inválidos: {identifier}")
        
        # Límite de longitud
        if len(identifier) > 64:
            raise ValueError("Identificador demasiado largo")
        
        # Lista de palabras reservadas básicas
        reserved_words = {
            'select', 'insert', 'update', 'delete', 'drop', 'create', 'alter',
            'table', 'from', 'where', 'order', 'group', 'having', 'union',
            'exec', 'execute', 'sp_executesql', 'xp_cmdshell'
        }
        
        if identifier.lower() in reserved_words:
            raise ValueError(f"No se puede usar palabra reservada como identificador: {identifier}")
        
        return identifier
    
    def execute_query(self, query: str, params: Optional[Tuple] = None) -> List[Dict[str, Any]]:
        """
        Ejecuta una consulta SELECT segura con parámetros preparados.
        
        Args:
            query: Consulta SQL con placeholders (?)
            params: Parámetros para la consulta
            
        Returns:
            Lista de diccionarios con los resultados
            
        Raises:
            ValueError: Si la consulta no es segura
        """
        if not self._is_safe_query(query):
            raise ValueError("Consulta SQL potencialmente insegura detectada")
        
        params = params or ()
        
        try:
            with self.get_cursor() as cursor:
                cursor.execute(query, params)
                
                # Obtener nombres de columnas
                columns = [description[0] for description in cursor.description] if cursor.description else []
                
                # Convertir resultados a diccionarios
                results = []
                for row in cursor.fetchall():
                    results.append(dict(zip(columns, row)))
                
                logger.debug(f"Query ejecutada exitosamente. Resultados: {len(results)}")
                return results
                
        except Exception as e:
            logger.error(f"Error ejecutando consulta SELECT: {e}")
            raise
    
    def execute_non_query(self, query: str, params: Optional[Tuple] = None) -> int:
        """
        Ejecuta una consulta INSERT/UPDATE/DELETE segura.
        
        Args:
            query: Consulta SQL con placeholders (?)
            params: Parámetros para la consulta
            
        Returns:
            Número de filas afectadas
            
        Raises:
            ValueError: Si la consulta no es segura
        """
        if not self._is_safe_query(query):
            raise ValueError("Consulta SQL potencialmente insegura detectada")
        
        params = params or ()
        
        try:
            with self.get_cursor() as cursor:
                cursor.execute(query, params)
                rows_affected = cursor.rowcount
                
                # Auto-commit para operaciones no-query (si no hay transacción activa)
                if self.db_connection and not self._transaction_active:
                    self.db_connection.commit()
                
                logger.debug(f"Query no-select ejecutada. Filas afectadas: {rows_affected}")
                return rows_affected
                
        except Exception as e:
            logger.error(f"Error ejecutando consulta no-select: {e}")
            raise
    
    def execute_scalar(self, query: str, params: Optional[Tuple] = None) -> Any:
        """
        Ejecuta una consulta que retorna un valor único.
        
        Args:
            query: Consulta SQL con placeholders (?)
            params: Parámetros para la consulta
            
        Returns:
            Valor único del resultado o None
        """
        results = self.execute_query(query, params)
        
        if results and len(results) > 0:
            first_row = results[0]
            if first_row:
                # Retornar el primer valor de la primera fila
                return list(first_row.values())[0]
        
        return None
    
    def execute_batch(self, query: str, params_list: List[Tuple]) -> int:
        """
        Ejecuta una consulta múltiples veces con diferentes parámetros.
        
        Args:
            query: Consulta SQL con placeholders (?)
            params_list: Lista de tuplas de parámetros
            
        Returns:
            Total de filas afectadas
        """
        if not self._is_safe_query(query):
            raise ValueError("Consulta SQL potencialmente insegura detectada")
        
        total_affected = 0
        
        try:
            with self.get_cursor() as cursor:
                for params in params_list:
                    cursor.execute(query, params)
                    total_affected += cursor.rowcount
                
                # Commit batch operation (si no hay transacción activa)
                if self.db_connection and not self._transaction_active:
                    self.db_connection.commit()
                
                logger.debug(f"Batch ejecutado. Operaciones: {len(params_list)}, Filas afectadas: {total_affected}")
                return total_affected
                
        except Exception as e:
            logger.error(f"Error ejecutando batch: {e}")
            raise
    
    def exists(self, table: str, where_clause: str, params: Optional[Tuple] = None) -> bool:
        """
        Verifica si existe al menos un registro que cumple la condición.
        
        Args:
            table: Nombre de la tabla
            where_clause: Cláusula WHERE con placeholders (?)
            params: Parámetros para la cláusula WHERE
            
        Returns:
            True si existe al menos un registro
        """
        # Sanitizar nombre de tabla
        table = self._sanitize_identifier(table)
        
        query = f"SELECT 1 FROM {table} WHERE {where_clause} LIMIT 1"
        result = self.execute_scalar(query, params)
        
        return result is not None
    
    def count(self, table: str, where_clause: str = None, params: Optional[Tuple] = None) -> int:
        """
        Cuenta registros en una tabla.
        
        Args:
            table: Nombre de la tabla
            where_clause: Cláusula WHERE opcional
            params: Parámetros para la cláusula WHERE
            
        Returns:
            Número de registros
        """
        # Sanitizar nombre de tabla
        table = self._sanitize_identifier(table)
        
        query = f"SELECT COUNT(*) FROM {table}"
        if where_clause:
            query += f" WHERE {where_clause}"
        
        result = self.execute_scalar(query, params)
        return result or 0
    
    def get_last_insert_id(self) -> Optional[int]:
        """
        Obtiene el ID del último registro insertado.
        
        Returns:
            ID del último registro insertado
        """
        try:
            with self.get_cursor() as cursor:
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"Error obteniendo último ID insertado: {e}")
            return None
    
    def begin_transaction(self):
        """Inicia una transacción explícita."""
        if self.db_connection:
            try:
                with self.get_cursor() as cursor:
                    cursor.execute("BEGIN")
                self._transaction_active = True
                logger.debug("Transacción iniciada")
            except Exception as e:
                logger.error(f"Error iniciando transacción: {e}")
                raise
    
    def commit_transaction(self):
        """Confirma la transacción actual."""
        if self.db_connection:
            try:
                self.db_connection.commit()
                self._transaction_active = False
                logger.debug("Transacción confirmada")
            except Exception as e:
                logger.error(f"Error confirmando transacción: {e}")
                raise
    
    def rollback_transaction(self):
        """Revierte la transacción actual."""
        if self.db_connection:
            try:
                self.db_connection.rollback()
                self._transaction_active = False
                logger.debug("Transacción revertida")
            except Exception as e:
                logger.error(f"Error revirtiendo transacción: {e}")
                raise
    
    @contextmanager
    def transaction(self):
        """
        Context manager para transacciones.
        Auto-commit en éxito, auto-rollback en error.
        """
        try:
            self.begin_transaction()
            yield
            self.commit_transaction()
        except Exception as e:
            try:
                self.rollback_transaction()
            except Exception:
                pass  # Ignorar errores de rollback
            logger.error(f"Transacción revertida debido a error: {e}")
            raise
    
    def table_exists(self, table_name: str) -> bool:
        """
        Verifica si una tabla existe en la base de datos.
        
        Args:
            table_name: Nombre de la tabla
            
        Returns:
            True si la tabla existe
        """
        table_name = self._sanitize_identifier(table_name)
        
        try:
            # Query compatible con SQLite y SQL Server
            query = """
            SELECT COUNT(*) 
            FROM sqlite_master 
            WHERE type='table' AND name=?
            UNION ALL
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_NAME=?
            """
            
            result = self.execute_scalar(query, (table_name, table_name))
            return (result or 0) > 0
            
        except Exception as e:
            logger.error(f"Error verificando existencia de tabla {table_name}: {e}")
            return False
    
    def get_table_info(self, table_name: str) -> List[Dict[str, Any]]:
        """
        Obtiene información de las columnas de una tabla.
        
        Args:
            table_name: Nombre de la tabla
            
        Returns:
            Lista de información de columnas
        """
        table_name = self._sanitize_identifier(table_name)
        
        try:
            # Para SQLite
            query = f"PRAGMA table_info({table_name})"
            return self.execute_query(query)
        except Exception as e:
            logger.error(f"Error obteniendo información de tabla {table_name}: {e}")
            return []
    
    def validate_query_safety(self, query: str) -> Dict[str, Any]:
        """
        Valida la seguridad de una consulta y retorna detalles.
        
        Args:
            query: Consulta a validar
            
        Returns:
            Diccionario con resultado de validación
        """
        result = {
            'is_safe': True,
            'issues': [],
            'warnings': [],
            'query_type': 'unknown'
        }
        
        if not query or not isinstance(query, str):
            result['is_safe'] = False
            result['issues'].append('Consulta vacía o inválida')
            return result
        
        query_lower = query.lower().strip()
        
        # Detectar tipo de consulta
        if query_lower.startswith('select'):
            result['query_type'] = 'select'
        elif query_lower.startswith(('insert', 'update', 'delete')):
            result['query_type'] = 'modify'
        elif query_lower.startswith(('create', 'drop', 'alter')):
            result['query_type'] = 'ddl'
        
        # Verificar patrones peligrosos
        for pattern in self.dangerous_patterns:
            if re.search(pattern, query_lower, re.IGNORECASE):
                result['is_safe'] = False
                result['issues'].append(f'Patrón peligroso detectado: {pattern}')
        
        # Advertencias para consultas DDL
        if result['query_type'] == 'ddl':
            result['warnings'].append('Consulta DDL detectada - revisar cuidadosamente')
        
        return result
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas del gestor SQL.
        
        Returns:
            Estadísticas del sistema
        """
        return {
            'has_connection': self.db_connection is not None,
            'transaction_active': self._transaction_active,
            'dangerous_patterns_count': len(self.dangerous_patterns)
        }


# Instancia global para uso conveniente
_global_sql_manager = None


def get_sql_manager() -> SQLQueryManager:
    """
    Obtiene la instancia global del gestor SQL.
    
    Returns:
        Instancia global de SQLQueryManager
    """
    global _global_sql_manager
    if _global_sql_manager is None:
        _global_sql_manager = SQLQueryManager()
    return _global_sql_manager


def set_global_connection(connection):
    """
    Establece la conexión global de base de datos.
    
    Args:
        connection: Conexión a la base de datos
    """
    manager = get_sql_manager()
    manager.set_connection(connection)


# Funciones de conveniencia para uso directo
def safe_execute(query: str, params: Optional[Tuple] = None) -> List[Dict[str, Any]]:
    """Ejecuta una consulta SELECT usando el gestor global."""
    return get_sql_manager().execute_query(query, params)


def safe_execute_non_query(query: str, params: Optional[Tuple] = None) -> int:
    """Ejecuta una consulta INSERT/UPDATE/DELETE usando el gestor global."""
    return get_sql_manager().execute_non_query(query, params)


def safe_execute_scalar(query: str, params: Optional[Tuple] = None) -> Any:
    """Ejecuta una consulta que retorna un valor único usando el gestor global."""
    return get_sql_manager().execute_scalar(query, params)


def safe_table_exists(table_name: str) -> bool:
    """Verifica si una tabla existe usando el gestor global."""
    return get_sql_manager().table_exists(table_name)


def safe_count(table: str, where_clause: str = None, params: Optional[Tuple] = None) -> int:
    """Cuenta registros usando el gestor global."""
    return get_sql_manager().count(table, where_clause, params)