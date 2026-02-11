"""
Bus de Eventos de Dominio - Rexus.app
Sistema de integración entre módulos usando eventos

Características:
- Publicación/suscripción de eventos
- Integración asíncrona entre módulos
- Eventos de dominio (PedidoCreado, StockActualizado, etc.)
- Desacoplamiento de módulos
- Logging de eventos para auditoría
"""

import logging
import threading
from typing import Dict, List, Callable, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from collections import defaultdict

logger = logging.getLogger(__name__)


class EventType(Enum):
    """Tipos de eventos de dominio."""

    # Eventos de Pedidos
    PEDIDO_CREADO = "pedido.creado"
    PEDIDO_ACTUALIZADO = "pedido.actualizado"
    PEDIDO_CANCELADO = "pedido.cancelado"
    PEDIDO_ENTREGADO = "pedido.entregado"
    PEDIDO_CONFIRMADO = "pedido.confirmado"

    # Eventos de Inventario
    STOCK_ACTUALIZADO = "stock.actualizado"
    STOCK_RESERVADO = "stock.reservado"
    STOCK_LIBERADO = "stock.liberado"
    PRODUCTO_CREADO = "producto.creado"
    PRODUCTO_ACTUALIZADO = "producto.actualizado"
    STOCK_BAJO = "stock.bajo"

    # Eventos de Compras
    COMPRA_CREADA = "compra.creada"
    COMPRA_RECIBIDA = "compra.recibida"
    COMPRA_APROBADA = "compra.aprobada"
    PROVEEDOR_CREADO = "proveedor.creado"

    # Eventos de Obras
    OBRA_CREADA = "obra.creada"
    OBRA_ACTUALIZADA = "obra.actualizada"
    RECURSO_ASIGNADO = "recurso.asignado"
    PRESUPUESTO_ACTUALIZADO = "presupuesto.actualizado"

    # Eventos de Logística
    TRANSPORTE_CREADO = "transporte.creado"
    TRANSPORTE_ASIGNADO = "transporte.asignado"
    ENVIO_INICIADO = "envio.iniciado"
    ENVIO_ENTREGADO = "envio.entregado"

    # Eventos de Usuarios
    USUARIO_CREADO = "usuario.creado"
    USUARIO_ACTUALIZADO = "usuario.actualizado"
    USUARIO_BLOQUEADO = "usuario.bloqueado"
    LOGIN_EXITOSO = "login.exitoso"
    LOGIN_FALLIDO = "login.fallido"


@dataclass
class DomainEvent:
    """Representa un evento de dominio."""

    event_type: EventType
    aggregate_id: str
    aggregate_type: str
    data: Dict[str, Any]
    occurred_at: datetime = field(default_factory=datetime.now)
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None  # ID del evento que causó este
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convierte el evento a diccionario."""
        return {
            "event_type": self.event_type.value,
            "aggregate_id": self.aggregate_id,
            "aggregate_type": self.aggregate_type,
            "data": self.data,
            "occurred_at": self.occurred_at.isoformat(),
            "correlation_id": self.correlation_id,
            "causation_id": self.causation_id,
            "metadata": self.metadata
        }


type EventHandler = Callable[[DomainEvent], None]


class EventBus:
    """
    Bus de eventos de dominio.

    Permite la integración desacoplada entre módulos mediante
    publicación/suscripción de eventos.

    Example:
        # Suscribirse a eventos
        event_bus.subscribe(EventType.PEDIDO_CREADO, handle_pedido_creado)

        # Publicar evento
        event_bus.publish(DomainEvent(
            event_type=EventType.PEDIDO_CREADO,
            aggregate_id="pedido-123",
            aggregate_type="pedido",
            data={"cliente_id": 456, "monto": 10000}
        ))
    """

    def __init__(self):
        """Inicializa el bus de eventos."""
        self._subscribers: Dict[EventType, List[EventHandler]] = defaultdict(list)
        self._event_history: List[DomainEvent] = []
        self._lock = threading.RLock()
        self._enabled = True

    def subscribe(self, event_type: EventType, handler: EventHandler) -> str:
        """
        Suscribe un handler a un tipo de evento.

        Args:
            event_type: Tipo de evento
            handler: Función handler

        Returns:
            ID de suscripción
        """
        with self._lock:
            self._subscribers[event_type].append(handler)
            sub_id = f"{event_type.value}_{len(self._subscribers[event_type])}"
            logger.info(f"Suscripción agregada: {sub_id} -> {handler.__name__}")
            return sub_id

    def unsubscribe(self, event_type: EventType, handler: EventHandler):
        """
        Desuscribe un handler de un tipo de evento.

        Args:
            event_type: Tipo de evento
            handler: Función handler
        """
        with self._lock:
            if event_type in self._subscribers:
                try:
                    self._subscribers[event_type].remove(handler)
                    logger.info(f"Handler desuscrito de {event_type.value}")
                except ValueError:
                    pass

    def publish(self, event: DomainEvent) -> bool:
        """
        Publica un evento en el bus.

        Args:
            event: Evento a publicar

        Returns:
            True si se publicó correctamente
        """
        if not self._enabled:
            logger.debug("EventBus deshabilitado, evento ignorado")
            return False

        try:
            # Guardar en historial
            with self._lock:
                self._event_history.append(event)

            # Notificar suscriptores
            handlers = self._subscribers.get(event.event_type, [])

            for handler in handlers:
                try:
                    handler(event)
                except Exception as e:
                    logger.error(
                        f"Error en handler {handler.__name__} "
                        f"para evento {event.event_type.value}: {e}",
                        exc_info=True
                    )

            # Loguear evento
            logger.info(
                f"Evento publicado: {event.event_type.value} | "
                f"Aggregate: {event.aggregate_type}/{event.aggregate_id}"
            )

            return True

        except Exception as e:
            logger.error(f"Error publicando evento: {e}", exc_info=True)
            return False

    def publish_async(self, event: DomainEvent):
        """
        Publica un evento de forma asíncrona.

        Args:
            event: Evento a publicar
        """
        import threading

        def _publish():
            self.publish(event)

        thread = threading.Thread(target=_publish, daemon=True)
        thread.start()

    def get_event_history(self, event_type: EventType = None,
                         limit: int = 100) -> List[DomainEvent]:
        """
        Obtiene el historial de eventos.

        Args:
            event_type: Filtrar por tipo (opcional)
            limit: Cantidad máxima de eventos

        Returns:
            Lista de eventos
        """
        with self._lock:
            history = self._event_history

            if event_type:
                history = [e for e in history if e.event_type == event_type]

            return history[-limit:]

    def clear_history(self):
        """Limpia el historial de eventos."""
        with self._lock:
            self._event_history.clear()

    def enable(self):
        """Habilita el bus de eventos."""
        self._enabled = True
        logger.info("EventBus habilitado")

    def disable(self):
        """Deshabilita el bus de eventos."""
        self._enabled = False
        logger.info("EventBus deshabilitado")


# Instancia global
_event_bus_instance: Optional[EventBus] = None


def get_event_bus() -> EventBus:
    """Obtiene la instancia singleton del EventBus."""
    global _event_bus_instance
    if _event_bus_instance is None:
        _event_bus_instance = EventBus()
        # Suscribir handlers por defecto
        _setup_default_handlers(_event_bus_instance)
    return _event_bus_instance


def _setup_default_handlers(event_bus: EventBus):
    """Configura handlers por defecto para integración entre módulos."""

    @event_bus.subscribe(EventType.PEDIDO_CREADO, _handle_pedido_creado)
    def _(event: DomainEvent):
        """Handler por defecto para pedido creado."""
        pass

    @event_bus.subscribe(EventType.STOCK_BAJO, _handle_stock_bajo)
    def _(event: DomainEvent):
        """Handler por defecto para stock bajo."""
        pass

    logger.info("Handlers por defecto configurados")


def _handle_pedido_creado(event: DomainEvent):
    """
    Maneja el evento de pedido creado.

    Integra con:
    - Inventario (reservar stock)
    - Logística (preparar envío)
    - Notificaciones (avisar al cliente)
    """
    try:
        from rexus.core.alerts_manager import trigger_alert, AlertSeverity

        pedido = event.data
        producto_id = pedido.get("producto_id")
        cantidad = pedido.get("cantidad", 0)

        # Notificar al inventario
        logger.info(
            f"Pedido {event.aggregate_id} creado. "
            f"Producto: {producto_id}, Cantidad: {cantidad}"
        )

        # Aquí se reservaría el stock en inventario
        # inventario.reservar_stock(producto_id, cantidad)

    except Exception as e:
        logger.error(f"Error en handler pedido_creado: {e}")


def _handle_stock_bajo(event: DomainEvent):
    """
    Maneja el evento de stock bajo.

    Integra con:
    - Alertas (notificar a compras)
    - Compras (sugerir reorder)
    """
    try:
        from rexus.core.alerts_manager import trigger_alert, AlertSeverity

        producto = event.data
        producto_id = producto.get("producto_id")
        stock_actual = producto.get("stock_actual", 0)
        stock_minimo = producto.get("stock_minimo", 0)

        # Disparar alerta
        trigger_alert(
            name="Stock Bajo",
            severity=AlertSeverity.HIGH,
            message=f"Producto {producto_id} tiene stock bajo ({stock_actual}/{stock_minimo})",
            source="inventario",
            labels={
                "producto_id": str(producto_id),
                "stock_actual": str(stock_actual),
                "stock_minimo": str(stock_minimo)
            }
        )

        logger.warning(f"Stock bajo para producto {producto_id}: {stock_actual}/{stock_minimo}")

    except Exception as e:
        logger.error(f"Error en handler stock_bajo: {e}")


# Funciones de conveniencia
def publish_event(event_type: EventType, aggregate_id: str,
                  aggregate_type: str, data: Dict, **kwargs) -> bool:
    """
    Publica un evento de forma simplificada.

    Args:
        event_type: Tipo de evento
        aggregate_id: ID del aggregate
        aggregate_type: Tipo del aggregate
        data: Datos del evento
        **kwargs: Metadata adicional

    Returns:
        True si se publicó correctamente
    """
    event = DomainEvent(
        event_type=event_type,
        aggregate_id=aggregate_id,
        aggregate_type=aggregate_type,
        data=data,
        **kwargs
    )
    return get_event_bus().publish(event)


def subscribe_event(event_type: EventType, handler: EventHandler) -> str:
    """
    Suscribe un handler a un evento.

    Args:
        event_type: Tipo de evento
        handler: Función handler

    Returns:
        ID de suscripción
    """
    return get_event_bus().subscribe(event_type, handler)


# Eventos de dominio específicos (funciones de conveniencia)

def publish_pedido_creado(pedido_id: str, pedido_data: Dict) -> bool:
    """Publica evento de pedido creado."""
    return publish_event(
        EventType.PEDIDO_CREADO,
        pedido_id,
        "pedido",
        pedido_data
    )


def publish_stock_actualizado(producto_id: str, stock_anterior: int,
                             stock_nuevo: int) -> bool:
    """Publica evento de stock actualizado."""
    return publish_event(
        EventType.STOCK_ACTUALIZADO,
        producto_id,
        "producto",
        {
            "producto_id": producto_id,
            "stock_anterior": stock_anterior,
            "stock_nuevo": stock_nuevo
        }
    )


def publish_stock_bajo(producto_id: str, stock_actual: int,
                      stock_minimo: int) -> bool:
    """Publica evento de stock bajo."""
    return publish_event(
        EventType.STOCK_BAJO,
        producto_id,
        "producto",
        {
            "producto_id": producto_id,
            "stock_actual": stock_actual,
            "stock_minimo": stock_minimo
        }
    )


def publish_compra_recibida(compra_id: str, compra_data: Dict) -> bool:
    """Publica evento de compra recibida."""
    return publish_event(
        EventType.COMPRA_RECIBIDA,
        compra_id,
        "compra",
        compra_data
    )


def publish_envio_entregado(envio_id: str, envio_data: Dict) -> bool:
    """Publica evento de envío entregado."""
    return publish_event(
        EventType.ENVIO_ENTREGADO,
        envio_id,
        "envio",
        envio_data
    )
