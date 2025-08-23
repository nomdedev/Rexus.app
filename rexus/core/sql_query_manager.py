"""
Gestor de consultas SQL centralizado y seguro para Rexus.app
Proporciona interfaz unificada para operaciones de base de datos con protección contra SQL injection.
"""

import logging
                    except Exception as e:            raise
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

        except Exception as e:            raise ValueError("Consulta SQL potencialmente insegura detectada")

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

        except Exception as e:            raise ValueError("Consulta SQL potencialmente insegura detectada")

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

        except Exception as e:            raise

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
        except Exception as e:            raise ValueError("Identificador inválido después de sanitización")

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
