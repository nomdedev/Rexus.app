"""
Servicio de Integración Pedidos-Inventario - Rexus.app
Sincroniza automáticamente el inventario con los pedidos

Características:
- Reserva automática de stock al crear pedido
- Actualización de stock al confirmar pedido
- Liberación de stock al cancelar pedido
- Notificaciones de stock bajo
- Historial de movimientos
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class StockOperation(Enum):
    """Tipos de operaciones sobre stock."""
    RESERVE = "reserve"
    COMMIT = "commit"
    RELEASE = "release"
    ADJUST = "adjust"


class StockError(Exception):
    """Excepción para errores de stock."""
    pass


class InsufficientStockError(StockError):
    """Excepción para stock insuficiente."""
    pass


@dataclass
class StockMovement:
    """Representa un movimiento de stock."""
    id: str
    product_id: int
    operation: StockOperation
    quantity: int
    reference_type: str  # 'pedido', 'ajuste', 'devolucion', etc.
    reference_id: int
    stock_before: int
    stock_after: int
    created_at: datetime
    notes: str = None


class InventoryIntegrationService:
    """
    Servicio de integración entre pedidos e inventario.

    Gestiona automáticamente el stock cuando ocurren eventos de pedidos.
    """

    def __init__(self, db_connection=None):
        """
        Inicializa el servicio de integración.

        Args:
            db_connection: Conexión a la base de datos
        """
        self.db_connection = db_connection
        self._movements_history: List[StockMovement] = []

    def get_available_stock(self, product_id: int) -> int:
        """
        Obtiene el stock disponible de un producto.

        Args:
            product_id: ID del producto

        Returns:
            Cantidad disponible
        """
        if not self.db_connection:
            logger.error("No hay conexión a base de datos")
            return 0

        try:
            cursor = self.db_connection.cursor()

            cursor.execute("""
                SELECT stock
                FROM inventario
                WHERE id = ?
            """, (product_id,))

            result = cursor.fetchone()
            cursor.close()

            if result:
                return result[0]
            return 0

        except Exception as e:
            logger.error(f"Error obteniendo stock del producto {product_id}: {e}")
            return 0

    def get_reserved_stock(self, product_id: int) -> int:
        """
        Obtiene el stock reservado de un producto.

        Args:
            product_id: ID del producto

        Returns:
            Cantidad reservada
        """
        if not self.db_connection:
            return 0

        try:
            cursor = self.db_connection.cursor()

            cursor.execute("""
                SELECT COALESCE(SUM(cantidad), 0)
                FROM stock_reservado
                WHERE producto_id = ?
                AND estado = 'reservado'
            """, (product_id,))

            result = cursor.fetchone()
            cursor.close()

            if result:
                return result[0]
            return 0

        except Exception as e:
            logger.error(f"Error obteniendo stock reservado del producto {product_id}: {e}")
            return 0

    def reserve_stock(self,
                     product_id: int,
                     quantity: int,
                     reference_type: str,
                     reference_id: int,
                     notes: str = None) -> StockMovement:
        """
        Reserva stock para un pedido.

        Args:
            product_id: ID del producto
            quantity: Cantidad a reservar
            reference_type: Tipo de referencia (ej: 'pedido')
            reference_id: ID de referencia
            notes: Notas adicionales

        Returns:
            StockMovement con el resultado

        Raises:
            InsufficientStockError: Si no hay stock suficiente
        """
        if not self.db_connection:
            raise StockError("No hay conexión a base de datos")

        # Obtener stock actual
        stock_actual = self.get_available_stock(product_id)
        stock_reservado = self.get_reserved_stock(product_id)
        stock_disponible = stock_actual - stock_reservado

        # Verificar stock suficiente
        if stock_disponible < quantity:
            raise InsufficientStockError(
                f"Stock insuficiente para producto {product_id}. "
                f"Disponible: {stock_disponible}, Solicitado: {quantity}"
            )

        try:
            cursor = self.db_connection.cursor()

            # Insertar reserva
            cursor.execute("""
                INSERT INTO stock_reservado
                (producto_id, cantidad, referencia_tipo, referencia_id, estado, created_at)
                VALUES (?, ?, ?, ?, 'reservado', GETDATE())
            """, (product_id, quantity, reference_type, reference_id))

            self.db_connection.commit()
            cursor.close()

            # Registrar movimiento
            movement = StockMovement(
                id=f"reserve_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                product_id=product_id,
                operation=StockOperation.RESERVE,
                quantity=quantity,
                reference_type=reference_type,
                reference_id=reference_id,
                stock_before=stock_actual,
                stock_after=stock_actual,  # El stock no cambia, solo se reserva
                created_at=datetime.now(),
                notes=notes
            )

            self._movements_history.append(movement)

            logger.info(
                f"Stock reservado: producto={product_id}, cantidad={quantity}, "
                f"referencia={reference_type}:{reference_id}"
            )

            return movement

        except Exception as e:
            self.db_connection.rollback()
            logger.error(f"Error reservando stock: {e}")
            raise StockError(f"Error reservando stock: {e}")

    def commit_stock(self,
                    product_id: int,
                    quantity: int,
                    reference_type: str,
                    reference_id: int,
                    notes: str = None) -> StockMovement:
        """
        Confirma una reserva y actualiza el stock.

        Args:
            product_id: ID del producto
            quantity: Cantidad a confirmar
            reference_type: Tipo de referencia
            reference_id: ID de referencia
            notes: Notas adicionales

        Returns:
            StockMovement con el resultado
        """
        if not self.db_connection:
            raise StockError("No hay conexión a base de datos")

        try:
            cursor = self.db_connection.cursor()

            # Obtener stock antes
            stock_antes = self.get_available_stock(product_id)

            # Actualizar stock
            nuevo_stock = stock_antes - quantity

            cursor.execute("""
                UPDATE inventario
                SET stock = ?,
                    updated_at = GETDATE()
                WHERE id = ?
            """, (nuevo_stock, product_id))

            # Actualizar reserva
            cursor.execute("""
                UPDATE stock_reservado
                SET estado = 'consumido',
                    consumido_at = GETDATE()
                WHERE producto_id = ?
                AND referencia_tipo = ?
                AND referencia_id = ?
                AND estado = 'reservado'
            """, (product_id, reference_type, reference_id))

            self.db_connection.commit()
            cursor.close()

            # Registrar movimiento
            movement = StockMovement(
                id=f"commit_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                product_id=product_id,
                operation=StockOperation.COMMIT,
                quantity=quantity,
                reference_type=reference_type,
                reference_id=reference_id,
                stock_before=stock_antes,
                stock_after=nuevo_stock,
                created_at=datetime.now(),
                notes=notes
            )

            self._movements_history.append(movement)

            logger.info(
                f"Stock confirmado: producto={product_id}, cantidad={quantity}, "
                f"stock_anterior={stock_antes}, stock_nuevo={nuevo_stock}"
            )

            # Verificar si el stock está bajo
            if nuevo_stock < 10:  # Umbral configurable
                self._notify_low_stock(product_id, nuevo_stock)

            return movement

        except Exception as e:
            self.db_connection.rollback()
            logger.error(f"Error confirmando stock: {e}")
            raise StockError(f"Error confirmando stock: {e}")

    def release_stock(self,
                     product_id: int,
                     quantity: int,
                     reference_type: str,
                     reference_id: int,
                     notes: str = None) -> StockMovement:
        """
        Libera una reserva de stock.

        Args:
            product_id: ID del producto
            quantity: Cantidad a liberar
            reference_type: Tipo de referencia
            reference_id: ID de referencia
            notes: Notas adicionales

        Returns:
            StockMovement con el resultado
        """
        if not self.db_connection:
            raise StockError("No hay conexión a base de datos")

        try:
            cursor = self.db_connection.cursor()

            # Liberar reserva
            cursor.execute("""
                UPDATE stock_reservado
                SET estado = 'liberado',
                    liberado_at = GETDATE()
                WHERE producto_id = ?
                AND referencia_tipo = ?
                AND referencia_id = ?
                AND estado = 'reservado'
            """, (product_id, reference_type, reference_id))

            self.db_connection.commit()
            cursor.close()

            # Registrar movimiento
            movement = StockMovement(
                id=f"release_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                product_id=product_id,
                operation=StockOperation.RELEASE,
                quantity=quantity,
                reference_type=reference_type,
                reference_id=reference_id,
                stock_before=self.get_available_stock(product_id),
                stock_after=self.get_available_stock(product_id),  # Stock no cambia
                created_at=datetime.now(),
                notes=notes
            )

            self._movements_history.append(movement)

            logger.info(
                f"Stock liberado: producto={product_id}, cantidad={quantity}, "
                f"referencia={reference_type}:{reference_id}"
            )

            return movement

        except Exception as e:
            self.db_connection.rollback()
            logger.error(f"Error liberando stock: {e}")
            raise StockError(f"Error liberando stock: {e}")

    def adjust_stock(self,
                    product_id: int,
                     quantity: int,
                    reason: str,
                    notes: str = None) -> StockMovement:
        """
        Ajusta el stock directamente (para correcciones o devoluciones).

        Args:
            product_id: ID del producto
            quantity: Cantidad a ajustar (positiva o negativa)
            reason: Razón del ajuste
            notes: Notas adicionales

        Returns:
            StockMovement con el resultado
        """
        if not self.db_connection:
            raise StockError("No hay conexión a base de datos")

        try:
            cursor = self.db_connection.cursor()

            # Obtener stock antes
            stock_antes = self.get_available_stock(product_id)

            # Calcular nuevo stock
            nuevo_stock = stock_antes + quantity

            if nuevo_stock < 0:
                raise InsufficientStockError(
                    f"El ajuste resultaría en stock negativo: {nuevo_stock}"
                )

            # Actualizar stock
            cursor.execute("""
                UPDATE inventario
                SET stock = ?,
                    updated_at = GETDATE()
                WHERE id = ?
            """, (nuevo_stock, product_id))

            # Registrar movimiento en historial
            cursor.execute("""
                INSERT INTO stock_movements
                (producto_id, operacion, cantidad, razon, notas, stock_antes, stock_despues, created_at)
                VALUES (?, 'ajuste', ?, ?, ?, ?, ?, GETDATE())
            """, (product_id, quantity, reason, notes, stock_antes, nuevo_stock))

            self.db_connection.commit()
            cursor.close()

            # Registrar movimiento
            movement = StockMovement(
                id=f"adjust_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                product_id=product_id,
                operation=StockOperation.ADJUST,
                quantity=quantity,
                reference_type="ajuste",
                reference_id=0,
                stock_before=stock_antes,
                stock_after=nuevo_stock,
                created_at=datetime.now(),
                notes=f"Ajuste: {reason}. {notes or ''}"
            )

            self._movements_history.append(movement)

            logger.info(
                f"Stock ajustado: producto={product_id}, cantidad={quantity}, "
                f"razon={reason}, stock_anterior={stock_antes}, stock_nuevo={nuevo_stock}"
            )

            # Verificar si el stock está bajo
            if nuevo_stock < 10:
                self._notify_low_stock(product_id, nuevo_stock)

            return movement

        except Exception as e:
            self.db_connection.rollback()
            logger.error(f"Error ajustando stock: {e}")
            raise StockError(f"Error ajustando stock: {e}")

    def _notify_low_stock(self, product_id: int, current_stock: int):
        """
        Notifica stock bajo.

        Args:
            product_id: ID del producto
            current_stock: Stock actual
        """
        try:
            from rexus.core.alerts_manager import trigger_alert, AlertSeverity

            trigger_alert(
                name="Stock Bajo",
                severity=AlertSeverity.HIGH,
                message=f"El producto {product_id} tiene stock bajo ({current_stock} unidades)",
                source="inventory_integration",
                labels={"product_id": str(product_id), "current_stock": str(current_stock)}
            )

        except ImportError:
            logger.warning("No se pudo importar AlertManager para notificar stock bajo")

    def get_movements_history(self,
                             product_id: int = None,
                             limit: int = 100) -> List[StockMovement]:
        """
        Obtiene el historial de movimientos.

        Args:
            product_id: Filtrar por producto (opcional)
            limit: Límite de registros

        Returns:
            Lista de movimientos
        """
        if not self.db_connection:
            return self._movements_history[-limit:]

        try:
            cursor = self.db_connection.cursor()

            if product_id:
                cursor.execute("""
                    SELECT TOP (?)
                        id, producto_id, operacion, cantidad,
                        referencia_tipo, referencia_id,
                        stock_antes, stock_despues, created_at, notas
                    FROM stock_movements
                    WHERE producto_id = ?
                    ORDER BY created_at DESC
                """, (limit, product_id))
            else:
                cursor.execute("""
                    SELECT TOP (?)
                        id, producto_id, operacion, cantidad,
                        referencia_tipo, referencia_id,
                        stock_antes, stock_despues, created_at, notas
                    FROM stock_movements
                    ORDER BY created_at DESC
                """, (limit,))

            movements = []
            for row in cursor.fetchall():
                movements.append(StockMovement(
                    id=row[0],
                    product_id=row[1],
                    operation=StockOperation(row[2]),
                    quantity=row[3],
                    reference_type=row[4],
                    reference_id=row[5],
                    stock_before=row[6],
                    stock_after=row[7],
                    created_at=row[8],
                    notes=row[9]
                ))

            cursor.close()
            return movements

        except Exception as e:
            logger.error(f"Error obteniendo historial de movimientos: {e}")
            return []

    def process_pedido(self, pedido_id: int, items: List[dict]) -> dict:
        """
        Procesa un pedido completo: reserva stock para todos los items.

        Args:
            pedido_id: ID del pedido
            items: Lista de items {'producto_id': int, 'cantidad': int}

        Returns:
            Diccionario con resultado del procesamiento
        """
        result = {
            'pedido_id': pedido_id,
            'items_reservados': [],
            'items_fallidos': [],
            'success': True
        }

        try:
            for item in items:
                product_id = item.get('producto_id')
                cantidad = item.get('cantidad')

                if not product_id or not cantidad:
                    result['items_fallidos'].append({
                        'item': item,
                        'error': 'Datos inválidos'
                    })
                    result['success'] = False
                    continue

                try:
                    movement = self.reserve_stock(
                        product_id=product_id,
                        quantity=cantidad,
                        reference_type='pedido',
                        reference_id=pedido_id
                    )

                    result['items_reservados'].append({
                        'producto_id': product_id,
                        'cantidad': cantidad,
                        'movement_id': movement.id
                    })

                except InsufficientStockError as e:
                    result['items_fallidos'].append({
                        'item': item,
                        'error': str(e)
                    })
                    result['success'] = False

                except StockError as e:
                    result['items_fallidos'].append({
                        'item': item,
                        'error': str(e)
                    })
                    result['success'] = False

            # Si falló algún item, liberar los reservados
            if not result['success'] and result['items_reservados']:
                logger.info(f"Fallo en pedido {pedido_id}, liberando reservas...")
                for item_res in result['items_reservados']:
                    try:
                        self.release_stock(
                            product_id=item_res['producto_id'],
                            quantity=item_res['cantidad'],
                            reference_type='pedido',
                            reference_id=pedido_id
                        )
                    except Exception as e:
                        logger.error(f"Error liberando reserva: {e}")

            return result

        except Exception as e:
            logger.error(f"Error procesando pedido {pedido_id}: {e}")
            result['success'] = False
            result['error'] = str(e)
            return result

    def confirm_pedido(self, pedido_id: int) -> dict:
        """
        Confirma un pedido: consume las reservas y actualiza el stock.

        Args:
            pedido_id: ID del pedido

        Returns:
            Diccionario con resultado de la confirmación
        """
        result = {
            'pedido_id': pedido_id,
            'items_confirmados': [],
            'items_fallidos': [],
            'success': True
        }

        if not self.db_connection:
            result['success'] = False
            result['error'] = 'No hay conexión a base de datos'
            return result

        try:
            cursor = self.db_connection.cursor()

            # Obtener items reservados del pedido
            cursor.execute("""
                SELECT producto_id, cantidad
                FROM stock_reservado
                WHERE referencia_tipo = 'pedido'
                AND referencia_id = ?
                AND estado = 'reservado'
            """, (pedido_id,))

            items = cursor.fetchall()
            cursor.close()

            for item in items:
                product_id, cantidad = item

                try:
                    movement = self.commit_stock(
                        product_id=product_id,
                        cantidad=cantidad,
                        reference_type='pedido',
                        reference_id=pedido_id
                    )

                    result['items_confirmados'].append({
                        'producto_id': product_id,
                        'cantidad': cantidad
                    })

                except Exception as e:
                    result['items_fallidos'].append({
                        'producto_id': product_id,
                        'error': str(e)
                    })
                    result['success'] = False

            return result

        except Exception as e:
            logger.error(f"Error confirmando pedido {pedido_id}: {e}")
            result['success'] = False
            result['error'] = str(e)
            return result

    def cancel_pedido(self, pedido_id: int) -> dict:
        """
        Cancela un pedido: libera todas las reservas.

        Args:
            pedido_id: ID del pedido

        Returns:
            Diccionario con resultado de la cancelación
        """
        result = {
            'pedido_id': pedido_id,
            'items_liberados': [],
            'success': True
        }

        if not self.db_connection:
            result['success'] = False
            result['error'] = 'No hay conexión a base de datos'
            return result

        try:
            cursor = self.db_connection.cursor()

            # Obtener items reservados del pedido
            cursor.execute("""
                SELECT producto_id, cantidad
                FROM stock_reservado
                WHERE referencia_tipo = 'pedido'
                AND referencia_id = ?
                AND estado = 'reservado'
            """, (pedido_id,))

            items = cursor.fetchall()
            cursor.close()

            for item in items:
                product_id, cantidad = item

                try:
                    movement = self.release_stock(
                        product_id=product_id,
                        quantity=cantidad,
                        reference_type='pedido',
                        reference_id=pedido_id
                    )

                    result['items_liberados'].append({
                        'producto_id': product_id,
                        'cantidad': cantidad
                    })

                except Exception as e:
                    logger.error(f"Error liberando stock de producto {product_id}: {e}")

            return result

        except Exception as e:
            logger.error(f"Error cancelando pedido {pedido_id}: {e}")
            result['success'] = False
            result['error'] = str(e)
            return result


# Instancia global
_inventory_service_instance = None


def get_inventory_service() -> InventoryIntegrationService:
    """Obtiene la instancia singleton del servicio de integración."""
    global _inventory_service_instance
    if _inventory_service_instance is None:
        from rexus.core.database import get_connection
        db = get_connection("inventario")
        _inventory_service_instance = InventoryIntegrationService(db.connection)
    return _inventory_service_instance
