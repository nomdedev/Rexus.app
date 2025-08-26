"""
Modelo de Detalle de Compras - Rexus.app v2.0.0

Maneja los detalles de productos/items en las órdenes de compra.
Gestiona cantidades, precios, descuentos y cálculos de subtotales.
"""

import logging
from decimal import Decimal
from typing import Dict, List, Any, Optional

# Importar logging
try:
    from ...utils.app_logger import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class DetalleComprasModel:
    """Modelo para gestionar detalles de órdenes de compra."""

    def __init__(self, db_connection=None):
        """
        Inicializar modelo de detalles de compras.

        Args:
            db_connection: Conexión a la base de datos
        """
        self.db_connection = db_connection
        logger.info("DetalleComprasModel inicializado")

    def crear_item_compra(self, orden_id: int, datos_item: Dict[str, Any]) -> Optional[int]:
        """
        Crea un nuevo item en una orden de compra.

        Args:
            orden_id: ID de la orden de compra
            datos_item: Datos del item

        Returns:
            ID del item creado o None si falló
        """
        try:
            if not self.db_connection:
                logger.error("No hay conexión a BD disponible")
                return None

            cursor = self.db_connection.cursor()

            # Calcular valores
            cantidad = Decimal(str(datos_item.get('cantidad', 0)))
            precio_unitario = Decimal(str(datos_item.get('precio_unitario', 0)))
            descuento_porcentaje = Decimal(str(datos_item.get('descuento_porcentaje', 0)))

            descuento_monto = (cantidad * precio_unitario * descuento_porcentaje / 100)
            subtotal = (cantidad * precio_unitario) - descuento_monto

            cursor.execute("""
                INSERT INTO detalle_compras 
                (orden_id, producto_id, codigo_producto, descripcion, cantidad,
                precio_unitario, descuento_porcentaje, descuento_monto, subtotal)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                orden_id,
                datos_item.get('producto_id'),
                datos_item.get('codigo_producto', ''),
                datos_item.get('descripcion', ''),
                cantidad,
                precio_unitario,
                descuento_porcentaje,
                descuento_monto,
                subtotal
            ))

            self.db_connection.commit()
            item_id = cursor.lastrowid

            # Actualizar total de la orden
            self._recalcular_totales_orden(orden_id)

            logger.info(f"Item de compra creado con ID {item_id}")
            return item_id

        except Exception as e:
            logger.error(f"Error creando item de compra: {e}")
            return None

    def obtener_items_orden(self, orden_id: int) -> List[Dict[str, Any]]:
        """
        Obtiene todos los items de una orden de compra.

        Args:
            orden_id: ID de la orden

        Returns:
            Lista de items
        """
        try:
            if not self.db_connection:
                return []

            cursor = self.db_connection.cursor()
            cursor.execute("""
                SELECT id, producto_id, codigo_producto, descripcion, cantidad,
                       precio_unitario, descuento_porcentaje, descuento_monto, subtotal
                FROM detalle_compras
                WHERE orden_id = ?
                ORDER BY id
            """, (orden_id,))

            items = []
            for row in cursor.fetchall():
                item = {
                    'id': row[0],
                    'producto_id': row[1],
                    'codigo_producto': row[2],
                    'descripcion': row[3],
                    'cantidad': float(row[4]),
                    'precio_unitario': float(row[5]),
                    'descuento_porcentaje': float(row[6]),
                    'descuento_monto': float(row[7]),
                    'subtotal': float(row[8])
                }
                items.append(item)

            return items

        except Exception as e:
            logger.error(f"Error obteniendo items de orden: {e}")
            return []

    def actualizar_item_compra(self, item_id: int, datos_item: Dict[str, Any]) -> bool:
        """
        Actualiza un item de compra existente.

        Args:
            item_id: ID del item
            datos_item: Nuevos datos del item

        Returns:
            True si se actualizó exitosamente
        """
        try:
            if not self.db_connection:
                logger.error("No hay conexión a BD disponible")
                return False

            cursor = self.db_connection.cursor()

            # Obtener orden_id antes de actualizar
            cursor.execute("SELECT orden_id FROM detalle_compras WHERE id = ?", (item_id,))
            result = cursor.fetchone()
            if not result:
                logger.error(f"Item {item_id} no encontrado")
                return False

            orden_id = result[0]

            # Calcular nuevos valores
            cantidad = Decimal(str(datos_item.get('cantidad', 0)))
            precio_unitario = Decimal(str(datos_item.get('precio_unitario', 0)))
            descuento_porcentaje = Decimal(str(datos_item.get('descuento_porcentaje', 0)))

            descuento_monto = (cantidad * precio_unitario * descuento_porcentaje / 100)
            subtotal = (cantidad * precio_unitario) - descuento_monto

            cursor.execute("""
                UPDATE detalle_compras 
                SET producto_id = ?, codigo_producto = ?, descripcion = ?, cantidad = ?,
                    precio_unitario = ?, descuento_porcentaje = ?, descuento_monto = ?, subtotal = ?
                WHERE id = ?
            """, (
                datos_item.get('producto_id'),
                datos_item.get('codigo_producto', ''),
                datos_item.get('descripcion', ''),
                cantidad,
                precio_unitario,
                descuento_porcentaje,
                descuento_monto,
                subtotal,
                item_id
            ))

            self.db_connection.commit()

            # Recalcular totales de la orden
            self._recalcular_totales_orden(orden_id)

            logger.info(f"Item {item_id} actualizado exitosamente")
            return True

        except Exception as e:
            logger.error(f"Error actualizando item de compra: {e}")
            return False

    def eliminar_item_compra(self, item_id: int) -> bool:
        """
        Elimina un item de una orden de compra.

        Args:
            item_id: ID del item a eliminar

        Returns:
            True si se eliminó exitosamente
        """
        try:
            if not self.db_connection:
                logger.error("No hay conexión a BD disponible")
                return False

            cursor = self.db_connection.cursor()

            # Obtener orden_id antes de eliminar
            cursor.execute("SELECT orden_id FROM detalle_compras WHERE id = ?", (item_id,))
            result = cursor.fetchone()
            if not result:
                logger.error(f"Item {item_id} no encontrado")
                return False

            orden_id = result[0]

            # Eliminar item
            cursor.execute("DELETE FROM detalle_compras WHERE id = ?", (item_id,))

            if cursor.rowcount > 0:
                self.db_connection.commit()

                # Recalcular totales de la orden
                self._recalcular_totales_orden(orden_id)

                logger.info(f"Item {item_id} eliminado exitosamente")
                return True
            else:
                logger.warning(f"No se pudo eliminar el item {item_id}")
                return False

        except Exception as e:
            logger.error(f"Error eliminando item de compra: {e}")
            return False

    def _recalcular_totales_orden(self, orden_id: int):
        """
        Recalcula los totales de una orden basándose en sus items.

        Args:
            orden_id: ID de la orden
        """
        try:
            cursor = self.db_connection.cursor()

            # Calcular totales de items
            cursor.execute("""
                SELECT 
                    COALESCE(SUM(subtotal), 0) as subtotal_total,
                    COALESCE(SUM(descuento_monto), 0) as descuento_total
                FROM detalle_compras 
                WHERE orden_id = ?
            """, (orden_id,))

            result = cursor.fetchone()
            subtotal_total = result[0] if result else 0
            descuento_total = result[1] if result else 0

            # Calcular impuestos (asumiendo 21% IVA)
            impuesto_porcentaje = Decimal('21.0')
            impuesto_monto = subtotal_total * impuesto_porcentaje / 100
            total = subtotal_total + impuesto_monto

            # Actualizar orden
            cursor.execute("""
                UPDATE ordenes_compra 
                SET subtotal = ?, descuento_total = ?, impuesto_porcentaje = ?, 
                    impuesto_monto = ?, total = ?
                WHERE id = ?
            """, (
                float(subtotal_total),
                float(descuento_total),
                float(impuesto_porcentaje),
                float(impuesto_monto),
                float(total),
                orden_id
            ))

            logger.info(f"Totales recalculados para orden {orden_id}")

        except Exception as e:
            logger.error(f"Error recalculando totales de orden {orden_id}: {e}")
