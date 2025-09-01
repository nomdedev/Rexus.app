"""
Gestor de consultas SQL centralizado y seguro para Rexus.app
Proporciona interfaz unificada para operaciones de base de datos con protección contra SQL injection.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple
from contextlib import contextmanager
import threading

logger = logging.getLogger(__name__)

class SQLQueryManager:
    """
    Gestor centralizado para consultas SQL seguras.
    Proporciona métodos seguros para ejecutar consultas con parámetros preparados.
    """

    def __init__(self, db_connection=None):
        """
        Inicializa el gestor de consultas SQL.

        Args:
            db_connection: Conexión a la base de datos (opcional)
        """
        self.db_connection = db_connection
        self._lock = threading.Lock()

    def set_connection(self, connection):
        """Establece la conexión a la base de datos."""
        with self._lock:
            self.db_connection = connection

    @contextmanager
    def get_cursor(self):
        """
        Context manager para obtener un cursor de base de datos.
        Maneja automáticamente el cierre del cursor.
        """
        if not self.db_connection:
            raise RuntimeError("No hay conexión de base de datos establecida")

        cursor = None
        try:
            cursor = self.db_connection.cursor()
            yield cursor
        except Exception as e:
            logger.error(f"Error en operación de base de datos: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            raise
        finally:
            if cursor:
                cursor.close()

    def execute_query(self,
query: str,
        params: Optional[Tuple] = None) -> List[Dict[str,
        Any]]:
        """
        Ejecuta una consulta SELECT segura con parámetros preparados.

        Args:
            query: Consulta SQL con placeholders (?)
            params: Parámetros para la consulta

        Returns:
            Lista de diccionarios con los resultados
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
            logger.error(f"Error ejecutando consulta: {query[:100]}... Error: {e}")
            raise

    def execute_non_query(self, query: str, params: Optional[Tuple] = None) -> int:
        """
        Ejecuta una consulta INSERT, UPDATE o DELETE segura.

        Args:
            query: Consulta SQL con placeholders (?)
            params: Parámetros para la consulta

        Returns:
            Número de filas afectadas
        """
        if not self._is_safe_query(query):
            raise ValueError("Consulta SQL potencialmente insegura detectada")

        params = params or ()

        try:
            with self.get_cursor() as cursor:
                cursor.execute(query, params)
                rows_affected = cursor.rowcount

                # Auto-commit para operaciones no-query
                if self.db_connection:
                    self.db_connection.commit()

                logger.debug(f"Query no-select ejecutada. Filas afectadas: {rows_affected}")
                return rows_affected

        except Exception as e:
            logger.error(f"Error ejecutando query no-select: {query[:100]}... Error: {e}")
            raise

    def execute_scalar(self, query: str, params: Optional[Tuple] = None) -> Any:
        """
        Ejecuta una consulta que retorna un valor único.

        Args:
            query: Consulta SQL con placeholders (?)
            params: Parámetros para la consulta

        Returns:
            Valor único del resultado
        """
        results = self.execute_query(query, params)

        if not results:
            return None

        # Retornar el primer valor de la primera fila
        first_row = results[0]
        return next(iter(first_row.values())) if first_row else None

    def execute_batch(self, query: str, params_list: List[Tuple]) -> int:
        """
        Ejecuta la misma consulta múltiples veces con diferentes parámetros.

        Args:
            query: Consulta SQL con placeholders (?)
            params_list: Lista de tuplas con parámetros

        Returns:
            Número total de filas afectadas
        """
        if not self._is_safe_query(query):
            raise ValueError("Consulta SQL potencialmente insegura detectada")

        total_affected = 0

        try:
            with self.get_cursor() as cursor:
                for params in params_list:
                    cursor.execute(query, params)
                    total_affected += cursor.rowcount

                # Commit batch operation
                if self.db_connection:
                    self.db_connection.commit()

                logger.debug(f"Batch ejecutado. Operaciones: {len(params_list)}, Filas afectadas: {total_affected}")
                return total_affected

        except Exception as e:
            logger.error(f"Error ejecutando batch: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            raise

    def exists(self,
table: str,
        where_clause: str,
        params: Optional[Tuple] = None) -> bool:
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

    def count(self,
table: str,
        where_clause: str = None,
        params: Optional[Tuple] = None) -> int:
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
            logger.error(f"Error obteniendo último ID: {e}")
            return None

    def _is_safe_query(self, query: str) -> bool:
        """
        Verifica que la consulta sea segura (uso básico de detección).

        Args:
            query: Consulta SQL a verificar

        Returns:
            True si la consulta parece segura
        """
        query_upper = query.upper().strip()

        # Verificar que no contenga múltiples statements
        if ';' in query and not query_upper.endswith(';'):
            logger.warning("Consulta con múltiples statements detectada")
            return False

        # Verificar comandos peligrosos
        dangerous_keywords = ['DROP', 'ALTER', 'CREATE', 'EXEC', 'EXECUTE']
        for keyword in dangerous_keywords:
            if keyword in query_upper:
                logger.warning(f"Comando peligroso detectado: {keyword}")
                return False

        return True

    def _sanitize_identifier(self, identifier: str) -> str:
        """
        Sanitiza identificadores de base de datos (nombres de tabla, columna).

        Args:
            identifier: Identificador a sanitizar

        Returns:
            Identificador sanitizado
        """
        # Remover caracteres peligrosos
        identifier = ''.join(char for char in identifier if char.isalnum() or char == '_')

        # Verificar que no esté vacío después de sanitizar
        if not identifier:
            raise ValueError("Identificador inválido después de sanitización")

        return identifier

    def begin_transaction(self):
        """Inicia una transacción explícita."""
        if self.db_connection:
            # SQLite usa BEGIN por defecto, pero podemos ser explícitos
            with self.get_cursor() as cursor:
                cursor.execute("BEGIN")

    def commit_transaction(self):
        """Confirma la transacción actual."""
        if self.db_connection:
            self.db_connection.commit()

    def rollback_transaction(self):
        """Revierte la transacción actual."""
        if self.db_connection:
            self.db_connection.rollback()

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
            self.rollback_transaction()
            logger.error(f"Transacción revertida debido a error: {e}")
            raise

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
