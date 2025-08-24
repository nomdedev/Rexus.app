# -*- coding: utf-8 -*-
"""
Controlador de Pedidos de Compras - Rexus.app v2.0.0

Maneja la lógica de control entre el modelo y la vista para pedidos/órdenes de compra.
Coordina las operaciones CRUD y la interacción con otros módulos.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from decimal import Decimal

# Configurar logging
try:
from ....utils.app_logger import get_logger
logger = get_logger(__name__)
except ImportError:
logger = logging.getLogger(__name__)

try:
from ....ui.components.dialogs import show_info, show_error, show_warning, show_question
except ImportError:
def show_info(parent, title, message):
        logger.info(f"{title}: {message}")
def show_error(parent, title, message):
        logger.error(f"{title}: {message}")
def show_warning(parent, title, message):
        logger.warning(f"{title}: {message}")
def show_question(parent, title, message):
        logger.info(f"{title}: {message}")
return True

try:
from ...base.base_controller import BaseController
except ImportError:
class BaseController:
        def __init__(self, model=None, view=None):
        self.model = model
self.view = view


class PedidosComprasController(BaseController):
"""Controlador para el submódulo de pedidos de compras."""

def __init__(self, model=None, view=None, db_connection=None):
        """
Inicializa el controlador de pedidos.

Args:
        model: Modelo de pedidos
view: Vista de pedidos
db_connection: Conexión a base de datos
"""
super().__init__(model, view)
self.db_connection = db_connection
self.pedidos_cache = {}
logger.info("PedidosComprasController inicializado")

if self.view:
        self.conectar_signals()

def conectar_signals(self):
        """Conecta las señales de la vista con los métodos del controlador."""
try:
        # Señales básicas de pedidos
if self.view and hasattr(self.view, 'pedido_creado'):
                self.view.pedido_creado.connect(self.crear_pedido)
if self.view and hasattr(self.view, 'pedido_editado'):
                self.view.pedido_editado.connect(self.editar_pedido)
if self.view and hasattr(self.view, 'pedido_eliminado'):
                self.view.pedido_eliminado.connect(self.eliminar_pedido)

# Señales de detalles
if self.view and hasattr(self.view, 'detalle_agregado'):
                self.view.detalle_agregado.connect(self.agregar_detalle_pedido)
if self.view and hasattr(self.view, 'detalle_modificado'):
                self.view.detalle_modificado.connect(self.modificar_detalle_pedido)
if self.view and hasattr(self.view, 'detalle_eliminado'):
                self.view.detalle_eliminado.connect(self.eliminar_detalle_pedido)

# Señales de estado
if self.view and hasattr(self.view, 'pedido_enviado'):
                self.view.pedido_enviado.connect(self.enviar_pedido)
if self.view and hasattr(self.view, 'pedido_cancelado'):
                self.view.pedido_cancelado.connect(self.cancelar_pedido)
if self.view and hasattr(self.view, 'pedido_aprobado'):
                self.view.pedido_aprobado.connect(self.aprobar_pedido)

logger.debug("Señales de pedidos conectadas exitosamente")

except Exception as e:
        logger.error(f"Error conectando señales de pedidos: {e}")

# ===== MÉTODOS PRINCIPALES DE PEDIDOS =====

def crear_pedido(self, datos_pedido: Dict[str, Any]) -> bool:
        """
Crea un nuevo pedido de compra.

Args:
        datos_pedido: Datos del pedido a crear

Returns:
        True si se creó exitosamente
"""
try:
        logger.info("Creando nuevo pedido de compra")

if not self._validar_datos_pedido(datos_pedido):
                return False

if not self.model:
                show_error(self.view, "Error", "No hay conexión al modelo de datos")
return False

# Generar número de pedido
numero_pedido = self._generar_numero_pedido()
datos_pedido['numero_pedido'] = numero_pedido
datos_pedido['fecha_creacion'] = datetime.now()
datos_pedido['estado'] = 'BORRADOR'

if self.model and hasattr(self.model, 'crear_pedido'):
                if self.model:
                pedido_id = self.model.crear_pedido(datos_pedido)
else:
                pedido_id = None
else:
                pedido_id = None

if pedido_id:
                show_info(self.view, "Éxito", f"Pedido {numero_pedido} creado correctamente")
self.actualizar_vista_pedidos()
logger.info(f"Pedido creado con ID: {pedido_id}")
return True
else:
                show_error(self.view, "Error", "No se pudo crear el pedido")
return False

except Exception as e:
        logger.error(f"Error creando pedido: {e}")
show_error(self.view, "Error", f"Error al crear pedido: {str(e)}")
return False

def editar_pedido(self, pedido_id: int, datos_pedido: Dict[str, Any]) -> bool:
        """
Edita un pedido existente.

Args:
        pedido_id: ID del pedido a editar
datos_pedido: Nuevos datos del pedido

Returns:
        True si se editó exitosamente
"""
try:
        logger.info(f"Editando pedido {pedido_id}")

if not self._validar_datos_pedido(datos_pedido):
                return False

if not self.model:
                show_error(self.view, "Error", "No hay conexión al modelo de datos")
return False

# Verificar que el pedido existe y se puede editar
if not self._pedido_es_editable(pedido_id):
                show_warning(self.view, "Advertencia", "El pedido no se puede editar en su estado actual")
return False

datos_pedido['fecha_modificacion'] = datetime.now()
if self.model and hasattr(self.model, 'actualizar_pedido'):
                if self.model:
                success = self.model.actualizar_pedido(pedido_id, datos_pedido)
else:
                success = None
else:
                success = None

if success:
                show_info(self.view, "Éxito", "Pedido actualizado correctamente")
self.actualizar_vista_pedidos()
logger.info(f"Pedido {pedido_id} actualizado")
return True
else:
                show_error(self.view, "Error", "No se pudo actualizar el pedido")
return False

except Exception as e:
        logger.error(f"Error editando pedido: {e}")
show_error(self.view, "Error", f"Error al editar pedido: {str(e)}")
return False

def eliminar_pedido(self, pedido_id: int) -> bool:
        """
Elimina un pedido de compra.

Args:
        pedido_id: ID del pedido a eliminar

Returns:
        True si se eliminó exitosamente
"""
try:
        logger.info(f"Eliminando pedido {pedido_id}")

if not self.model:
                show_error(self.view, "Error", "No hay conexión al modelo de datos")
return False

# Verificar que el pedido se puede eliminar
if not self._pedido_es_eliminable(pedido_id):
                show_warning(self.view, "Advertencia", "El pedido no se puede eliminar en su estado actual")
return False

# Confirmar eliminación
if not show_question(self.view, "Confirmar", "¿Está seguro de eliminar este pedido?"):
                return False

if self.model and hasattr(self.model, 'eliminar_pedido'):
                if self.model:
                success = self.model.eliminar_pedido(pedido_id)
else:
                success = None
else:
                success = None

if success:
                show_info(self.view, "Éxito", "Pedido eliminado correctamente")
self.actualizar_vista_pedidos()
logger.info(f"Pedido {pedido_id} eliminado")
return True
else:
                show_error(self.view, "Error", "No se pudo eliminar el pedido")
return False

except Exception as e:
        logger.error(f"Error eliminando pedido: {e}")
show_error(self.view, "Error", f"Error al eliminar pedido: {str(e)}")
return False

def duplicar_pedido(self, pedido_id: int) -> bool:
        """
Duplica un pedido existente.

Args:
        pedido_id: ID del pedido a duplicar

Returns:
        True si se duplicó exitosamente
"""
try:
        logger.info(f"Duplicando pedido {pedido_id}")

if not self.model:
                show_error(self.view, "Error", "No hay conexión al modelo de datos")
return False

# Obtener datos del pedido original
if self.model and hasattr(self.model, 'obtener_pedido'):
                if self.model:
                pedido_original = self.model.obtener_pedido(pedido_id)
else:
                pedido_original = None
else:
                pedido_original = None
if not pedido_original:
                show_error(self.view, "Error", "Pedido original no encontrado")
return False

# Crear nuevo pedido basado en el original
nuevo_pedido = pedido_original.copy()
nuevo_pedido.pop('id', None)
nuevo_pedido['estado'] = 'BORRADOR'
nuevo_pedido['numero_pedido'] = self._generar_numero_pedido()
nuevo_pedido['fecha_creacion'] = datetime.now()
nuevo_pedido['fecha_modificacion'] = None

if self.model and hasattr(self.model, 'crear_pedido'):
                if self.model:
                nuevo_id = self.model.crear_pedido(nuevo_pedido)
else:
                nuevo_id = None
else:
                nuevo_id = None

if nuevo_id:
                # Duplicar detalles del pedido
self._duplicar_detalles_pedido(pedido_id, nuevo_id)
show_info(self.view, "Éxito", f"Pedido duplicado como {nuevo_pedido['numero_pedido']}")
self.actualizar_vista_pedidos()
return True
else:
                show_error(self.view, "Error", "No se pudo duplicar el pedido")
return False

except Exception as e:
        logger.error(f"Error duplicando pedido: {e}")
show_error(self.view, "Error", f"Error al duplicar pedido: {str(e)}")
return False

# ===== MÉTODOS DE DETALLES DE PEDIDOS =====

def agregar_detalle_pedido(self, pedido_id: int, detalle_data: Dict[str, Any]) -> bool:
        """
Agrega un detalle a un pedido existente.

Args:
        pedido_id: ID del pedido
detalle_data: Datos del detalle a agregar

Returns:
        True si se agregó exitosamente
"""
try:
        logger.info(f"Agregando detalle a pedido {pedido_id}")

if not self._validar_datos_detalle(detalle_data):
                return False

if not self.model:
                show_error(self.view, "Error", "No hay conexión al modelo de datos")
return False

# Verificar que el pedido se puede modificar
if not self._pedido_es_editable(pedido_id):
                show_warning(self.view, "Advertencia", "El pedido no se puede modificar")
return False

# Calcular totales del detalle
self._calcular_totales_detalle(detalle_data)

if self.model and hasattr(self.model, 'agregar_detalle_pedido'):
                if self.model:
                detalle_id = self.model.agregar_detalle_pedido(pedido_id, detalle_data)
else:
                detalle_id = None
else:
                detalle_id = None

if detalle_id:
                # Recalcular totales del pedido
self._recalcular_totales_pedido(pedido_id)
show_info(self.view, "Éxito", "Detalle agregado correctamente")
self.actualizar_vista_detalles(pedido_id)
return True
else:
                show_error(self.view, "Error", "No se pudo agregar el detalle")
return False

except Exception as e:
        logger.error(f"Error agregando detalle: {e}")
show_error(self.view, "Error", f"Error al agregar detalle: {str(e)}")
return False

def modificar_detalle_pedido(self, detalle_id: int, detalle_data: Dict[str, Any]) -> bool:
        """
Modifica un detalle de pedido existente.

Args:
        detalle_id: ID del detalle a modificar
detalle_data: Nuevos datos del detalle

Returns:
        True si se modificó exitosamente
"""
try:
        logger.info(f"Modificando detalle {detalle_id}")

if not self._validar_datos_detalle(detalle_data):
                return False

if not self.model:
                show_error(self.view, "Error", "No hay conexión al modelo de datos")
return False

# Obtener pedido_id del detalle
pedido_id = self._obtener_pedido_id_detalle(detalle_id)
if not pedido_id:
                show_error(self.view, "Error", "Detalle no encontrado")
return False

# Verificar que el pedido se puede modificar
if not self._pedido_es_editable(pedido_id):
                show_warning(self.view, "Advertencia", "El pedido no se puede modificar")
return False

# Calcular totales del detalle
self._calcular_totales_detalle(detalle_data)

if self.model and hasattr(self.model, 'actualizar_detalle_pedido'):
                if self.model:
                success = self.model.actualizar_detalle_pedido(detalle_id, detalle_data)
else:
                success = None
else:
                success = None

if success:
                # Recalcular totales del pedido
self._recalcular_totales_pedido(pedido_id)
show_info(self.view, "Éxito", "Detalle modificado correctamente")
self.actualizar_vista_detalles(pedido_id)
return True
else:
                show_error(self.view, "Error", "No se pudo modificar el detalle")
return False

except Exception as e:
        logger.error(f"Error modificando detalle: {e}")
show_error(self.view, "Error", f"Error al modificar detalle: {str(e)}")
return False

def eliminar_detalle_pedido(self, detalle_id: int) -> bool:
        """
Elimina un detalle de pedido.

Args:
        detalle_id: ID del detalle a eliminar

Returns:
        True si se eliminó exitosamente
"""
try:
        logger.info(f"Eliminando detalle {detalle_id}")

if not self.model:
                show_error(self.view, "Error", "No hay conexión al modelo de datos")
return False

# Obtener pedido_id del detalle
pedido_id = self._obtener_pedido_id_detalle(detalle_id)
if not pedido_id:
                show_error(self.view, "Error", "Detalle no encontrado")
return False

# Verificar que el pedido se puede modificar
if not self._pedido_es_editable(pedido_id):
                show_warning(self.view, "Advertencia", "El pedido no se puede modificar")
return False

# Confirmar eliminación
if not show_question(self.view, "Confirmar", "¿Está seguro de eliminar este detalle?"):
                return False

if self.model and hasattr(self.model, 'eliminar_detalle_pedido'):
                if self.model:
                success = self.model.eliminar_detalle_pedido(detalle_id)
else:
                success = None
else:
                success = None

if success:
                # Recalcular totales del pedido
self._recalcular_totales_pedido(pedido_id)
show_info(self.view, "Éxito", "Detalle eliminado correctamente")
self.actualizar_vista_detalles(pedido_id)
return True
else:
                show_error(self.view, "Error", "No se pudo eliminar el detalle")
return False

except Exception as e:
        logger.error(f"Error eliminando detalle: {e}")
show_error(self.view, "Error", f"Error al eliminar detalle: {str(e)}")
return False

# ===== MÉTODOS DE CAMBIO DE ESTADO =====

def enviar_pedido(self, pedido_id: int) -> bool:
        """
Envía un pedido al proveedor.

Args:
        pedido_id: ID del pedido a enviar

Returns:
        True si se envió exitosamente
"""
try:
        logger.info(f"Enviando pedido {pedido_id}")

if not self.model:
                show_error(self.view, "Error", "No hay conexión al modelo de datos")
return False

# Validar que el pedido se puede enviar
if not self._pedido_es_enviable(pedido_id):
                show_warning(self.view, "Advertencia", "El pedido no se puede enviar en su estado actual")
return False

# Actualizar estado
datos_actualizacion = {
'estado': 'ENVIADO',
'fecha_envio': datetime.now()
}

if self.model and hasattr(self.model, 'actualizar_pedido'):
                if self.model:
                success = self.model.actualizar_pedido(pedido_id, datos_actualizacion)
else:
                success = None
else:
                success = None

if success:
                show_info(self.view, "Éxito", "Pedido enviado correctamente")
self.actualizar_vista_pedidos()
logger.info(f"Pedido {pedido_id} enviado")
return True
else:
                show_error(self.view, "Error", "No se pudo enviar el pedido")
return False

except Exception as e:
        logger.error(f"Error enviando pedido: {e}")
show_error(self.view, "Error", f"Error al enviar pedido: {str(e)}")
return False

def cancelar_pedido(self, pedido_id: int, motivo: str = "") -> bool:
        """
Cancela un pedido.

Args:
        pedido_id: ID del pedido a cancelar
motivo: Motivo de cancelación

Returns:
        True si se canceló exitosamente
"""
try:
        logger.info(f"Cancelando pedido {pedido_id}")

if not self.model:
                show_error(self.view, "Error", "No hay conexión al modelo de datos")
return False

# Confirmar cancelación
if not show_question(self.view, "Confirmar", "¿Está seguro de cancelar este pedido?"):
                return False

# Actualizar estado
datos_actualizacion = {
'estado': 'CANCELADO',
'fecha_cancelacion': datetime.now(),
'motivo_cancelacion': motivo
}

if self.model and hasattr(self.model, 'actualizar_pedido'):
                if self.model:
                success = self.model.actualizar_pedido(pedido_id, datos_actualizacion)
else:
                success = None
else:
                success = None

if success:
                show_info(self.view, "Éxito", "Pedido cancelado correctamente")
self.actualizar_vista_pedidos()
logger.info(f"Pedido {pedido_id} cancelado")
return True
else:
                show_error(self.view, "Error", "No se pudo cancelar el pedido")
return False

except Exception as e:
        logger.error(f"Error cancelando pedido: {e}")
show_error(self.view, "Error", f"Error al cancelar pedido: {str(e)}")
return False

def aprobar_pedido(self, pedido_id: int) -> bool:
        """
Aprueba un pedido.

Args:
        pedido_id: ID del pedido a aprobar

Returns:
        True si se aprobó exitosamente
"""
try:
        logger.info(f"Aprobando pedido {pedido_id}")

if not self.model:
                show_error(self.view, "Error", "No hay conexión al modelo de datos")
return False

# Validar que el pedido se puede aprobar
if not self._pedido_es_aprobable(pedido_id):
                show_warning(self.view, "Advertencia", "El pedido no se puede aprobar en su estado actual")
return False

# Actualizar estado
datos_actualizacion = {
'estado': 'APROBADO',
'fecha_aprobacion': datetime.now()
}

if self.model and hasattr(self.model, 'actualizar_pedido'):
                if self.model:
                success = self.model.actualizar_pedido(pedido_id, datos_actualizacion)
else:
                success = None
else:
                success = None

if success:
                show_info(self.view, "Éxito", "Pedido aprobado correctamente")
self.actualizar_vista_pedidos()
logger.info(f"Pedido {pedido_id} aprobado")
return True
else:
                show_error(self.view, "Error", "No se pudo aprobar el pedido")
return False

except Exception as e:
        logger.error(f"Error aprobando pedido: {e}")
show_error(self.view, "Error", f"Error al aprobar pedido: {str(e)}")
return False

# ===== MÉTODOS DE ACTUALIZACIÓN DE VISTA =====

def actualizar_vista_pedidos(self):
        """Actualiza la vista de pedidos."""
try:
        if self.view and hasattr(self.view, 'cargar_pedidos'):
                pedidos = self._cargar_pedidos()
self.view.cargar_pedidos(pedidos)
logger.debug("Vista de pedidos actualizada")

except Exception as e:
        logger.error(f"Error actualizando vista pedidos: {e}")

def actualizar_vista_detalles(self, pedido_id: int):
        """Actualiza la vista de detalles de un pedido."""
try:
        if self.view and hasattr(self.view, 'cargar_detalles'):
                detalles = self._cargar_detalles_pedido(pedido_id)
self.view.cargar_detalles(detalles)
logger.debug(f"Vista de detalles actualizada para pedido {pedido_id}")

except Exception as e:
        logger.error(f"Error actualizando vista detalles: {e}")

def cargar_pedidos_iniciales(self) -> List[Dict[str, Any]]:
        """
Carga los pedidos iniciales para la vista.

Returns:
        Lista de pedidos
"""
try:
        pedidos = self._cargar_pedidos()
if self.view and hasattr(self.view, 'cargar_pedidos'):
                self.view.cargar_pedidos(pedidos)
return pedidos
except Exception as e:
        logger.error(f"Error cargando pedidos iniciales: {e}")
return []

# ===== MÉTODOS PRIVADOS =====

def _validar_datos_pedido(self, datos: Dict[str, Any]) -> bool:
        """Valida los datos de un pedido."""
try:
        # Validar proveedor
if not datos.get('proveedor_id'):
                show_error(self.view, "Error", "Debe seleccionar un proveedor")
return False

# Validar fecha de entrega
if not datos.get('fecha_entrega'):
                show_error(self.view, "Error", "Debe especificar fecha de entrega")
return False

return True

except Exception as e:
        logger.error(f"Error validando datos pedido: {e}")
return False

def _validar_datos_detalle(self, datos: Dict[str, Any]) -> bool:
        """Valida los datos de un detalle."""
try:
        # Validar producto
if not datos.get('producto_id'):
                show_error(self.view, "Error", "Debe seleccionar un producto")
return False

# Validar cantidad
try:
                cantidad = float(datos.get('cantidad', 0))
if cantidad <= 0:
                show_error(self.view, "Error", "La cantidad debe ser mayor a cero")
return False
except ValueError:
                show_error(self.view, "Error", "Cantidad inválida")
return False

# Validar precio
try:
                precio = float(datos.get('precio_unitario', 0))
if precio <= 0:
                show_error(self.view, "Error", "El precio debe ser mayor a cero")
return False
except ValueError:
                show_error(self.view, "Error", "Precio inválido")
return False

return True

except Exception as e:
        logger.error(f"Error validando datos detalle: {e}")
return False

def _generar_numero_pedido(self) -> str:
        """Genera un número único de pedido."""
try:
        if not self.model:
                return f"PED{datetime.now().strftime('%Y%m%d%H%M%S')}"

if self.model:
                contador = self.model.obtener_contador_pedidos()
else:
                contador = []
return f"PED{contador:06d}"

except Exception as e:
        logger.error(f"Error generando número pedido: {e}")
return f"PED{datetime.now().strftime('%Y%m%d%H%M%S')}"

def _pedido_es_editable(self, pedido_id: int) -> bool:
        """Verifica si un pedido se puede editar."""
try:
        if not self.model:
                return False

if self.model:
                pedido = self.model.obtener_pedido(pedido_id)
else:
                pedido = None
if not pedido:
                return False

estados_editables = ['BORRADOR', 'PENDIENTE']
return pedido.get('estado') in estados_editables

except Exception as e:
        logger.error(f"Error verificando si pedido es editable: {e}")
return False

def _pedido_es_eliminable(self, pedido_id: int) -> bool:
        """Verifica si un pedido se puede eliminar."""
try:
        if not self.model:
                return False

if self.model:
                pedido = self.model.obtener_pedido(pedido_id)
else:
                pedido = None
if not pedido:
                return False

estados_eliminables = ['BORRADOR']
return pedido.get('estado') in estados_eliminables

except Exception as e:
        logger.error(f"Error verificando si pedido es eliminable: {e}")
return False

def _pedido_es_enviable(self, pedido_id: int) -> bool:
        """Verifica si un pedido se puede enviar."""
try:
        if not self.model:
                return False

if self.model:
                pedido = self.model.obtener_pedido(pedido_id)
else:
                pedido = None
if not pedido:
                return False

estados_enviables = ['BORRADOR', 'PENDIENTE']
return pedido.get('estado') in estados_enviables

except Exception as e:
        logger.error(f"Error verificando si pedido es enviable: {e}")
return False

def _pedido_es_aprobable(self, pedido_id: int) -> bool:
        """Verifica si un pedido se puede aprobar."""
try:
        if not self.model:
                return False

if self.model:
                pedido = self.model.obtener_pedido(pedido_id)
else:
                pedido = None
if not pedido:
                return False

estados_aprobables = ['PENDIENTE']
return pedido.get('estado') in estados_aprobables

except Exception as e:
        logger.error(f"Error verificando si pedido es aprobable: {e}")
return False

def _calcular_totales_detalle(self, detalle_data: Dict[str, Any]):
        """Calcula los totales de un detalle."""
try:
        cantidad = Decimal(str(detalle_data.get('cantidad', 0)))
precio_unitario = Decimal(str(detalle_data.get('precio_unitario', 0)))
descuento_porcentaje = Decimal(str(detalle_data.get('descuento_porcentaje', 0)))

subtotal = cantidad * precio_unitario
descuento_monto = subtotal * descuento_porcentaje / 100
total = subtotal - descuento_monto

detalle_data['subtotal'] = float(subtotal)
detalle_data['descuento_monto'] = float(descuento_monto)
detalle_data['total'] = float(total)

except Exception as e:
        logger.error(f"Error calculando totales detalle: {e}")

def _recalcular_totales_pedido(self, pedido_id: int):
        """Recalcula los totales de un pedido."""
try:
        if not self.model:
                return

if self.model:
                self.model.recalcular_totales_pedido(pedido_id)

except Exception as e:
        logger.error(f"Error recalculando totales pedido: {e}")

def _duplicar_detalles_pedido(self, pedido_origen_id: int, pedido_destino_id: int):
        """Duplica los detalles de un pedido a otro."""
try:
        if not self.model:
                return

if self.model:
                self.model.duplicar_detalles_pedido(pedido_origen_id, pedido_destino_id)

except Exception as e:
        logger.error(f"Error duplicando detalles: {e}")

def _obtener_pedido_id_detalle(self, detalle_id: int) -> Optional[int]:
        """Obtiene el ID del pedido al que pertenece un detalle."""
try:
        if not self.model:
                return None

if self.model:
                return self.model.obtener_pedido_id_detalle(detalle_id)
return None

except Exception as e:
        logger.error(f"Error obteniendo pedido ID del detalle: {e}")
return None

def _cargar_pedidos(self) -> List[Dict[str, Any]]:
        """Carga todos los pedidos."""
try:
        if not self.model:
                return []

if self.model:
                return self.model.obtener_pedidos()
return []

except Exception as e:
        logger.error(f"Error cargando pedidos: {e}")
return []

def _cargar_detalles_pedido(self, pedido_id: int) -> List[Dict[str, Any]]:
        """Carga los detalles de un pedido."""
try:
        if not self.model:
                return []

if self.model:
                return self.model.obtener_detalles_pedido(pedido_id)
return None

except Exception as e:
        logger.error(f"Error cargando detalles del pedido: {e}")
return []