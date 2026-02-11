"""
Producto Repository - Repositorio para Productos de Inventario

Implementa el patrón Repository para el acceso a datos de productos.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from rexus.repositories.base import BaseRepository, RepositoryConfig

logger = logging.getLogger(__name__)


class ProductoRepository(BaseRepository):
    """
    Repositorio para managing productos de inventario.

    Proporciona métodos especializados para operaciones de productos
    más allá del CRUD básico.
    """

    def __init__(self, db_connection, sql_manager=None):
        super().__init__(
            db_connection=db_connection,
            sql_manager=sql_manager,
            config=RepositoryConfig(
                table_name='inventario_perfiles',
                primary_key='id',
                soft_delete=True,
                timestamps=True
            )
        )

    # ==================== IMPLEMENTACIÓN CRUD ====================

    def find_by_id(self, id: int) -> Optional[Dict[str, Any]]:
        """Busca un producto por ID."""
        try:
            cursor = self._execute_query(
                f"SELECT * FROM [{self.config.table_name}] WHERE {self.config.primary_key} = ? AND activo = 1",
                (id,)
            )
            row = cursor.fetchone()
            return self._row_to_dict(row) if row else None
        except Exception as e:
            logger.error(f"Error buscando producto por ID {id}: {e}")
            return None

    def find_all(self, filters: Dict[str, Any] = None, limit: int = None,
                 offset: int = None, order_by: str = None) -> List[Dict[str, Any]]:
        """Busca productos con filtros opcionales."""
        try:
            query = f"SELECT * FROM [{self.config.table_name}] WHERE activo = 1"
            params = []

            # Aplicar filtros
            if filters:
                if 'categoria' in filters:
                    query += " AND categoria = ?"
                    params.append(filters['categoria'])
                if 'nombre' in filters:
                    query += " AND descripcion LIKE ?"
                    params.append(f"%{filters['nombre']}%")
                if 'stock_bajo' in filters and filters['stock_bajo']:
                    query += " AND stock_actual <= stock_minimo"

            # Ordenamiento
            if order_by:
                query += f" ORDER BY {order_by}"
            else:
                query += " ORDER BY descripcion ASC"

            # Paginación
            if limit:
                query += " OFFSET ? ROWS FETCH NEXT ? ROWS ONLY"
                params.append(offset or 0)
                params.append(limit)

            cursor = self._execute_query(query, tuple(params) if params else None)
            rows = cursor.fetchall()
            return [self._row_to_dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error buscando productos: {e}")
            return []

    def create(self, entity: Dict[str, Any]) -> Dict[str, Any]:
        """Crea un nuevo producto."""
        try:
            query = f"""
                INSERT INTO [{self.config.table_name}]
                (descripcion, categoria, stock_actual, stock_minimo, precio_unitario, activo, fecha_creacion)
                VALUES (?, ?, ?, ?, ?, 1, GETDATE())
            """
            cursor = self._execute_query(query, (
                entity.get('descripcion'),
                entity.get('categoria'),
                entity.get('stock_actual', 0),
                entity.get('stock_minimo', 10),
                entity.get('precio_unitario', 0.0)
            ))
            self.db_connection.connection.commit()

            # Obtener el ID generado
            cursor.execute("SELECT @@IDENTITY")
            entity['id'] = cursor.fetchone()[0]
            entity['activo'] = 1

            self._log_operation('create', {'entity_id': entity['id']})
            return entity
        except Exception as e:
            logger.error(f"Error creando producto: {e}")
            self.db_connection.connection.rollback()
            raise

    def update(self, entity: Dict[str, Any]) -> Dict[str, Any]:
        """Actualiza un producto existente."""
        try:
            query = f"""
                UPDATE [{self.config.table_name}]
                SET descripcion = ?, categoria = ?, stock_actual = ?,
                    stock_minimo = ?, precio_unitario = ?, fecha_modificacion = GETDATE()
                WHERE {self.config.primary_key} = ? AND activo = 1
            """
            self._execute_query(query, (
                entity.get('descripcion'),
                entity.get('categoria'),
                entity.get('stock_actual'),
                entity.get('stock_minimo'),
                entity.get('precio_unitario'),
                entity['id']
            ))
            self.db_connection.connection.commit()

            self._log_operation('update', {'entity_id': entity['id']})
            return entity
        except Exception as e:
            logger.error(f"Error actualizando producto {entity['id']}: {e}")
            self.db_connection.connection.rollback()
            raise

    def delete(self, id: int) -> bool:
        """Elimina un producto (soft delete)."""
        try:
            query = f"""
                UPDATE [{self.config.table_name}]
                SET activo = 0, fecha_modificacion = GETDATE()
                WHERE {self.config.primary_key} = ? AND activo = 1
            """
            cursor = self._execute_query(query, (id,))
            self.db_connection.connection.commit()

            affected = cursor.rowcount
            self._log_operation('delete', {'entity_id': id, 'affected': affected})
            return affected > 0
        except Exception as e:
            logger.error(f"Error eliminando producto {id}: {e}")
            self.db_connection.connection.rollback()
            return False

    # ==================== MÉTODOS ESPECIALIZADOS ====================

    def find_by_categoria(self, categoria: str) -> List[Dict[str, Any]]:
        """Busca productos por categoría."""
        return self.find_all(filters={'categoria': categoria})

    def find_low_stock(self) -> List[Dict[str, Any]]:
        """Busca productos con stock bajo."""
        return self.find_all(filters={'stock_bajo': True})

    def update_stock(self, producto_id: int, cantidad: int) -> bool:
        """
        Actualiza el stock de un producto.

        Args:
            producto_id: ID del producto
            cantidad: Cantidad a agregar (puede ser negativa)

        Returns:
            True si se actualizó correctamente
        """
        try:
            query = f"""
                UPDATE [{self.config.table_name}]
                SET stock_actual = stock_actual + ?, fecha_modificacion = GETDATE()
                WHERE {self.config.primary_key} = ? AND activo = 1
            """
            cursor = self._execute_query(query, (cantidad, producto_id))
            self.db_connection.connection.commit()

            self._log_operation('update_stock', {'producto_id': producto_id, 'cantidad': cantidad})
            return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error actualizando stock del producto {producto_id}: {e}")
            self.db_connection.connection.rollback()
            return False

    def get_total_value(self) -> float:
        """
        Calcula el valor total del inventario.

        Returns:
            Valor total del inventario
        """
        try:
            cursor = self._execute_query(f"""
                SELECT COALESCE(SUM(stock_actual * precio_unitario), 0)
                FROM [{self.config.table_name}]
                WHERE activo = 1
            """)
            return float(cursor.fetchone()[0] or 0.0)
        except Exception as e:
            logger.error(f"Error calculando valor total: {e}")
            return 0.0

    def get_statistics(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas del inventario.

        Returns:
            Diccionario con estadísticas
        """
        try:
            cursor = self._execute_query(f"""
                WITH
                total_productos AS (
                    SELECT COUNT(*) AS total FROM [{self.config.table_name}] WHERE activo = 1
                ),
                valor_total AS (
                    SELECT COALESCE(SUM(stock_actual * precio_unitario), 0) AS valor
                    FROM [{self.config.table_name}] WHERE activo = 1
                ),
                stock_bajo AS (
                    SELECT COUNT(*) AS bajo_count
                    FROM [{self.config.table_name}]
                    WHERE stock_actual <= stock_minimo AND activo = 1
                )
                SELECT t.total, v.valor, s.bajo_count
                FROM total_productos t CROSS JOIN valor_total v CROSS JOIN stock_bajo s
            """)
            row = cursor.fetchone()
            return {
                'total_productos': row[0],
                'valor_total': float(row[1]),
                'stock_bajo': row[2]
            }
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return {
                'total_productos': 0,
                'valor_total': 0.0,
                'stock_bajo': 0
            }

    # ==================== MÉTODOS DE UTILIDAD ====================

    def _row_to_dict(self, row) -> Dict[str, Any]:
        """Convierte una fila de BD a diccionario."""
        if not row:
            return None

        # Asumiendo que el cursor tiene descripcion
        columns = [desc[0] for desc in row.cursor_description] if hasattr(row, 'cursor_description') else []
        return dict(zip(columns, row)) if columns else dict(row)
