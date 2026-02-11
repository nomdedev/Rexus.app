"""
Servicio de Integración de Pedidos - Rexus.app
Integra el módulo de pedidos con inventario, logística y notificaciones

Características:
- Verificación de stock al crear pedido
- Reserva automática de stock
- Actualización de stock al confirmar/cancelar
- Notificaciones a logística
- Workflow de pedido a entrega
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class EstadoPedido(Enum):
    """Estados de un pedido."""
    BORRADOR = "borrador"
    PENDIENTE = "pendiente"
    CONFIRMADO = "confirmado"
    EN_PREPARACION = "en_preparacion"
    ENVIADO = "enviado"
    ENTREGADO = "entregado"
    CANCELADO = "cancelado"


@dataclass
class ResultadoOperacion:
    """Resultado de una operación de integración."""
    exitoso: bool
    mensaje: str
    datos: Dict = None
    errores: List[str] = None

    def __post_init__(self):
        if self.datos is None:
            self.datos = {}
        if self.errores is None:
            self.errores = []


class PedidoIntegracionService:
    """
    Servicio de integración para pedidos.

    Maneja la integración entre el módulo de pedidos y otros módulos:
    - Inventario: verificación, reserva y actualización de stock
    - Logística: asignación de transporte y seguimiento
    - Notificaciones: alertas al cliente y equipo

    Example:
        servicio = PedidoIntegracionService()

        # Crear pedido con integración
        resultado = servicio.crear_pedido({
            'cliente_id': 123,
            'items': [{'producto_id': 'P1', 'cantidad': 10}],
            'monto': 50000
        })

        if not resultado.exitoso:
            print(resultado.errores)
    """

    def __init__(self, inventario_model=None, logistica_model=None):
        """
        Inicializa el servicio.

        Args:
            inventario_model: Modelo de inventario (inyección de dependencia)
            logistica_model: Modelo de logística (inyección de dependencia)
        """
        self.inventario = inventario_model
        self.logistica = logistica_model

        # Suscribirse a eventos del bus
        self._setup_event_subscriptions()

    def _setup_event_subscriptions(self):
        """Configura suscripciones a eventos del EventBus."""
        try:
            from rexus.core.event_bus import (
                get_event_bus,
                EventType,
                subscribe_event
            )

            event_bus = get_event_bus()

            # Suscribirse a evento de compra recibida para actualizar stock
            @event_bus.subscribe(EventType.COMPRA_RECIBIDA, self._on_compra_recibida)
            def _(event):
                pass

            logger.info("Servicio de integración de pedidos suscrito a eventos")

        except Exception as e:
            logger.error(f"Error configurando suscripciones: {e}")

    def _on_compra_recibida(self, event):
        """
        Maneja el evento de compra recibida.

        Actualiza automáticamente el inventario cuando se recibe una compra.
        """
        try:
            data = event.data
            items = data.get("items", [])

            for item in items:
                producto_id = item.get("producto_id")
                cantidad_recibida = item.get("cantidad", 0)

                if producto_id and cantidad_recibida > 0:
                    self._actualizar_stock_inventario(
                        producto_id,
                        cantidad_recibida,
                        "compra_recibida",
                        f"Compra {event.aggregate_id}"
                    )

        except Exception as e:
            logger.error(f"Error manejando evento compra_recibida: {e}")

    def crear_pedido(self, pedido: Dict) -> ResultadoOperacion:
        """
        Crea un pedido con verificación de stock.

        Args:
            pedido: Datos del pedido

        Returns:
            Resultado de la operación
        """
        try:
            # 1. Validar datos del pedido
            validacion = self._validar_pedido(pedido)
            if not validacion["valido"]:
                return ResultadoOperacion(
                    exitoso=False,
                    mensaje="Validación fallida",
                    errores=validacion["errores"]
                )

            # 2. Verificar stock disponible
            verificacion = self._verificar_stock_disponible(pedido)
            if not verificacion.exitoso:
                return verificacion

            # 3. Reservar stock
            reserva = self._reservar_stock(pedido)
            if not reserva.exitoso:
                return reserva

            # 4. Crear el pedido (aquí se llamaría al modelo de pedidos)
            pedido_creado = self._crear_pedido_bd(pedido)
            if not pedido_creado:
                # Liberar reserva si falla la creación
                self._liberar_stock(pedido)
                return ResultadoOperacion(
                    exitoso=False,
                    mensaje="Error al crear pedido en base de datos"
                )

            # 5. Publicar evento de pedido creado
            self._publicar_evento_pedido_creado(pedido_creado, pedido)

            # 6. Notificar a logística si hay que preparar envío
            if pedido.get("requiere_envio", True):
                self._notificar_logistica(pedido_creado, pedido)

            return ResultadoOperacion(
                exitoso=True,
                mensaje="Pedido creado exitosamente",
                datos={"pedido_id": pedido_creado.get("id")}
            )

        except Exception as e:
            logger.error(f"Error creando pedido: {e}", exc_info=True)
            return ResultadoOperacion(
                exitoso=False,
                mensaje=f"Error creando pedido: {str(e)}"
            )

    def confirmar_pedido(self, pedido_id: str) -> ResultadoOperacion:
        """
        Confirma un pedido y actualiza el stock.

        Args:
            pedido_id: ID del pedido

        Returns:
            Resultado de la operación
        """
        try:
            # Obtener pedido de BD
            pedido = self._obtener_pedido_bd(pedido_id)
            if not pedido:
                return ResultadoOperacion(
                    exitoso=False,
                    mensaje="Pedido no encontrado"
                )

            # Actualizar stock (consumir la reserva)
            for item in pedido.get("items", []):
                self._consumir_reserva_stock(
                    item["producto_id"],
                    item["cantidad"],
                    pedido_id
                )

            # Actualizar estado del pedido
            self._actualizar_estado_pedido(pedido_id, EstadoPedido.CONFIRMADO.value)

            logger.info(f"Pedido {pedido_id} confirmado y stock actualizado")

            return ResultadoOperacion(
                exitoso=True,
                mensaje="Pedido confirmado exitosamente"
            )

        except Exception as e:
            logger.error(f"Error confirmando pedido: {e}", exc_info=True)
            return ResultadoOperacion(
                exitoso=False,
                mensaje=f"Error confirmando pedido: {str(e)}"
            )

    def cancelar_pedido(self, pedido_id: str, motivo: str = "") -> ResultadoOperacion:
        """
        Cancela un pedido y libera el stock reservado.

        Args:
            pedido_id: ID del pedido
            motivo: Motivo de cancelación

        Returns:
            Resultado de la operación
        """
        try:
            # Obtener pedido de BD
            pedido = self._obtener_pedido_bd(pedido_id)
            if not pedido:
                return ResultadoOperacion(
                    exitoso=False,
                    mensaje="Pedido no encontrado"
                )

            # Solo liberar stock si no estaba entregado
            estado = pedido.get("estado", "")
            if estado not in [EstadoPedido.ENTREGADO.value, EstadoPedido.CANCELADO.value]:
                # Liberar stock reservado
                self._liberar_stock(pedido)

            # Actualizar estado del pedido
            self._actualizar_estado_pedido(pedido_id, EstadoPedido.CANCELADO.value)

            # Publicar evento de cancelación
            self._publicar_evento_pedido_cancelado(pedido_id, motivo)

            logger.info(f"Pedido {pedido_id} cancelado: {motivo}")

            return ResultadoOperacion(
                exitoso=True,
                mensaje="Pedido cancelado exitosamente"
            )

        except Exception as e:
            logger.error(f"Error cancelando pedido: {e}", exc_info=True)
            return ResultadoOperacion(
                exitoso=False,
                mensaje=f"Error cancelando pedido: {str(e)}"
            )

    def _validar_pedido(self, pedido: Dict) -> Dict:
        """Valida los datos del pedido."""
        errores = []

        if not pedido.get("cliente_id"):
            errores.append("El cliente es requerido")

        if not pedido.get("items") or len(pedido.get("items", [])) == 0:
            errores.append("El pedido debe tener al menos un item")

        if pedido.get("monto", 0) <= 0:
            errores.append("El monto debe ser mayor a cero")

        return {
            "valido": len(errores) == 0,
            "errores": errores
        }

    def _verificar_stock_disponible(self, pedido: Dict) -> ResultadoOperacion:
        """Verifica que haya stock disponible para todos los items."""
        try:
            items = pedido.get("items", [])
            items_sin_stock = []

            for item in items:
                producto_id = item.get("producto_id")
                cantidad_solicitada = item.get("cantidad", 0)

                if self.inventario:
                    stock = self.inventario.obtener_stock(producto_id)
                    stock_disponible = stock - self._obtener_stock_reservado(producto_id)

                    if stock_disponible < cantidad_solicitada:
                        items_sin_stock.append({
                            "producto_id": producto_id,
                            "solicitado": cantidad_solicitada,
                            "disponible": stock_disponible
                        })

            if items_sin_stock:
                return ResultadoOperacion(
                    exitoso=False,
                    mensaje="Stock insuficiente",
                    errores=[
                        f"Producto {i['producto_id']}: "
                        f"solicitado {i['solicitado']}, disponible {i['disponible']}"
                        for i in items_sin_stock
                    ]
                )

            return ResultadoOperacion(exitoso=True, mensaje="Stock disponible")

        except Exception as e:
            logger.error(f"Error verificando stock: {e}")
            # Si falla la verificación, permitir continuar (modo tolerante)
            return ResultadoOperacion(exitoso=True, mensaje="Verificación de stock omitida")

    def _reservar_stock(self, pedido: Dict) -> ResultadoOperacion:
        """Reserva el stock para los items del pedido."""
        try:
            items = pedido.get("items", [])

            for item in items:
                producto_id = item.get("producto_id")
                cantidad = item.get("cantidad", 0)

                if self.inventario:
                    # Reservar stock en inventario
                    self.inventario.reservar_stock(
                        producto_id,
                        cantidad,
                        pedido_id=pedido.get("id")
                    )

                # Publicar evento de stock reservado
                self._publicar_evento_stock_reservado(producto_id, cantidad)

            return ResultadoOperacion(exitoso=True, mensaje="Stock reservado")

        except Exception as e:
            logger.error(f"Error reservando stock: {e}")
            return ResultadoOperacion(
                exitoso=False,
                mensaje=f"Error reservando stock: {str(e)}"
            )

    def _liberar_stock(self, pedido: Dict) -> bool:
        """Libera el stock reservado para un pedido."""
        try:
            items = pedido.get("items", [])

            for item in items:
                producto_id = item.get("producto_id")
                cantidad = item.get("cantidad", 0)

                if self.inventario:
                    self.inventario.liberar_stock(
                        producto_id,
                        cantidad,
                        pedido_id=pedido.get("id")
                    )

            return True

        except Exception as e:
            logger.error(f"Error liberando stock: {e}")
            return False

    def _consumir_reserva_stock(self, producto_id: str, cantidad: int, pedido_id: str):
        """Consume una reserva de stock (baja el stock real)."""
        try:
            if self.inventario:
                self.inventario.actualizar_stock(
                    producto_id,
                    -cantidad,  # Restar del stock
                    movimiento="venta",
                    referencia_id=pedido_id
                )

                # Publicar evento de stock actualizado
                self._publicar_evento_stock_actualizado(producto_id, cantidad, "venta")

        except Exception as e:
            logger.error(f"Error consumiendo reserva: {e}")

    def _actualizar_stock_inventario(self, producto_id: str, cantidad: int,
                                    tipo_movimiento: str, referencia: str):
        """Actualiza el stock de inventario."""
        try:
            if self.inventario:
                self.inventario.actualizar_stock(
                    producto_id,
                    cantidad,
                    movimiento=tipo_movimiento,
                    referencia_id=referencia
                )

                # Publicar evento
                if cantidad > 0:
                    self._publicar_evento_stock_actualizado(producto_id, cantidad, tipo_movimiento)

                    # Verificar si alcanzó stock mínimo
                    stock_actual = self.inventario.obtener_stock(producto_id)
                    stock_minimo = self.inventario.obtener_stock_minimo(producto_id)

                    if stock_actual <= stock_minimo:
                        self._publicar_evento_stock_bajo(producto_id, stock_actual, stock_minimo)

        except Exception as e:
            logger.error(f"Error actualizando stock: {e}")

    def _crear_pedido_bd(self, pedido: Dict) -> Optional[Dict]:
        """Crea el pedido en la base de datos."""
        # TODO: Implementar llamada real al modelo de pedidos
        # Aquí se llamaría a PedidosModel.crear_pedido(pedido)
        # Por ahora retorna un mock
        return {
            "id": f"PED-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "estado": EstadoPedido.PENDIENTE.value,
            "fecha_creacion": datetime.now().isoformat()
        }

    def _obtener_pedido_bd(self, pedido_id: str) -> Optional[Dict]:
        """Obtiene un pedido desde la base de datos."""
        # TODO: Implementar llamada real al modelo de pedidos
        return {"id": pedido_id, "items": [], "estado": EstadoPedido.PENDIENTE.value}

    def _actualizar_estado_pedido(self, pedido_id: str, estado: str):
        """Actualiza el estado de un pedido."""
        # TODO: Implementar llamada real
        logger.info(f"Pedido {pedido_id} actualizado a estado {estado}")

    def _obtener_stock_reservado(self, producto_id: str) -> int:
        """Obtiene el stock reservado de un producto."""
        # TODO: Implementar consulta real
        return 0

    def _notificar_logistica(self, pedido_creado: Dict, pedido: Dict):
        """Notifica al módulo de logística para preparar envío."""
        try:
            if self.logistica:
                self.logistica.preparar_envio(
                    pedido_id=pedido_creado["id"],
                    cliente_id=pedido.get("cliente_id"),
                    direccion_entrega=pedido.get("direccion_entrega")
                )

        except Exception as e:
            logger.error(f"Error notificando a logística: {e}")

    def _publicar_evento_pedido_creado(self, pedido_creado: Dict, pedido: Dict):
        """Publica evento de pedido creado."""
        try:
            from rexus.core.event_bus import publish_pedido_creado
            publish_pedido_creado(pedido_creado["id"], pedido)
        except Exception as e:
            logger.error(f"Error publicando evento: {e}")

    def _publicar_evento_pedido_cancelado(self, pedido_id: str, motivo: str):
        """Publica evento de pedido cancelado."""
        try:
            from rexus.core.event_bus import get_event_bus, EventType
            get_event_bus().publish(
                EventType.PEDIDO_CANCELADO,
                pedido_id,
                "pedido",
                {"motivo": motivo}
            )
        except Exception as e:
            logger.error(f"Error publicando evento: {e}")

    def _publicar_evento_stock_reservado(self, producto_id: str, cantidad: int):
        """Publica evento de stock reservado."""
        try:
            from rexus.core.event_bus import get_event_bus, EventType
            get_event_bus().publish(
                EventType.STOCK_RESERVADO,
                producto_id,
                "producto",
                {"cantidad": cantidad}
            )
        except Exception as e:
            logger.error(f"Error publicando evento: {e}")

    def _publicar_evento_stock_actualizado(self, producto_id: str, cantidad: int, tipo: str):
        """Publica evento de stock actualizado."""
        try:
            from rexus.core.event_bus import publish_stock_actualizado
            # Calcular stock anterior
            stock_anterior = self.inventario.obtener_stock(producto_id) - cantidad if self.inventario else 0
            stock_nuevo = self.inventario.obtener_stock(producto_id) if self.inventario else cantidad
            publish_stock_actualizado(producto_id, stock_anterior, stock_nuevo)
        except Exception as e:
            logger.error(f"Error publicando evento: {e}")

    def _publicar_evento_stock_bajo(self, producto_id: str, stock_actual: int, stock_minimo: int):
        """Publica evento de stock bajo."""
        try:
            from rexus.core.event_bus import publish_stock_bajo
            publish_stock_bajo(producto_id, stock_actual, stock_minimo)
        except Exception as e:
            logger.error(f"Error publicando evento: {e}")


# Instancia global
_pedido_service_instance: Optional[PedidoIntegracionService] = None


def get_pedido_integracion_service() -> PedidoIntegracionService:
    """Obtiene la instancia singleton del servicio."""
    global _pedido_service_instance
    if _pedido_service_instance is None:
        _pedido_service_instance = PedidoIntegracionService()
    return _pedido_service_instance
