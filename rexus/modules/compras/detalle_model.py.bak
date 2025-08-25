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
INSERT INTO ordenes_compra_detalles 
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
FROM ordenes_compra_detalles
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
cursor.execute("SELECT orden_id FROM ordenes_compra_detalles WHERE id = ?", (item_id,))
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
UPDATE ordenes_compra_detalles 
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
cursor.execute("SELECT orden_id FROM ordenes_compra_detalles WHERE id = ?", (item_id,))
result = cursor.fetchone()
if not result:
                logger.error(f"Item {item_id} no encontrado")
return False

orden_id = result[0]

# Eliminar item
cursor.execute("DELETE FROM ordenes_compra_detalles WHERE id = ?", (item_id,))

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

# Calcular subtotal de todos los items
cursor.execute("""
SELECT COALESCE(SUM(subtotal), 0)
FROM ordenes_compra_detalles
WHERE orden_id = ?
""", (orden_id,))

subtotal_items = cursor.fetchone()[0]

# Obtener descuento e impuestos de la orden
cursor.execute("""
SELECT descuento, impuestos
FROM ordenes_compra
WHERE id = ?
""", (orden_id,))

result = cursor.fetchone()
if result:
                descuento_orden = result[0] or 0
impuestos_orden = result[1] or 0

# Calcular total final
total_final = subtotal_items - descuento_orden + impuestos_orden

# Actualizar orden
cursor.execute("""
UPDATE ordenes_compra 
SET subtotal = ?, total = ?, fecha_modificacion = CURRENT_TIMESTAMP
WHERE id = ?
""", (subtotal_items, total_final, orden_id))

self.db_connection.commit()
logger.debug(f"Totales recalculados para orden {orden_id}")

except Exception as e:
        logger.error(f"Error recalculando totales de orden: {e}")

def validar_item_compra(self, datos_item: Dict[str, Any]) -> bool:
        """
Valida los datos de un item de compra.

Args:
        datos_item: Datos del item a validar

Returns:
        True si los datos son válidos
"""
try:
        # Validar descripción
if not datos_item.get('descripcion', '').strip():
                logger.error("Descripción del item es requerida")
return False

# Validar cantidad
try:
                cantidad = float(datos_item.get('cantidad', 0))
if cantidad <= 0:
                logger.error("La cantidad debe ser mayor a 0")
return False
except ValueError:
                logger.error("Cantidad debe ser un número válido")
return False

# Validar precio unitario
try:
                precio = float(datos_item.get('precio_unitario', 0))
if precio <= 0:
                logger.error("El precio unitario debe ser mayor a 0")
return False
except ValueError:
                logger.error("Precio unitario debe ser un número válido")
return False

# Validar descuento porcentaje
try:
                descuento = float(datos_item.get('descuento_porcentaje', 0))
if descuento < 0 or descuento > 100:
                logger.error("El descuento debe estar entre 0 y 100%")
return False
except ValueError:
                logger.error("Descuento debe ser un número válido")
return False

return True

except Exception as e:
        logger.error(f"Error validando item de compra: {e}")
return False

def obtener_resumen_orden(self, orden_id: int) -> Dict[str, Any]:
        """
Obtiene un resumen de una orden con sus totales.

Args:
        orden_id: ID de la orden

Returns:
        Diccionario con resumen de la orden
"""
try:
        if not self.db_connection:
                return {}

cursor = self.db_connection.cursor()

# Obtener datos básicos de la orden
cursor.execute("""
SELECT numero_orden, subtotal, descuento, impuestos, total
FROM ordenes_compra
WHERE id = ?
""", (orden_id,))

orden_data = cursor.fetchone()
if not orden_data:
                return {}

# Obtener estadísticas de items
cursor.execute("""
SELECT COUNT(*) as total_items,
COALESCE(SUM(cantidad), 0) as total_cantidad,
COALESCE(SUM(subtotal), 0) as subtotal_items
FROM ordenes_compra_detalles
WHERE orden_id = ?
""", (orden_id,))

items_data = cursor.fetchone()

resumen = {
'orden_id': orden_id,
'numero_orden': orden_data[0],
'total_items': items_data[0] if items_data else 0,
'total_cantidad': float(items_data[1]) if items_data else 0.0,
'subtotal_items': float(items_data[2]) if items_data else 0.0,
'subtotal_orden': float(orden_data[1]) if orden_data[1] else 0.0,
'descuento': float(orden_data[2]) if orden_data[2] else 0.0,
'impuestos': float(orden_data[3]) if orden_data[3] else 0.0,
'total': float(orden_data[4]) if orden_data[4] else 0.0
}

return resumen

except Exception as e:
        logger.error(f"Error obteniendo resumen de orden: {e}")
return {}

def duplicar_items_orden(self, orden_origen_id: int, orden_destino_id: int) -> bool:
        """
Duplica todos los items de una orden a otra orden.

Args:
        orden_origen_id: ID de la orden origen
orden_destino_id: ID de la orden destino

Returns:
        True si se duplicaron exitosamente
"""
try:
        if not self.db_connection:
                logger.error("No hay conexión a BD disponible")
return False

cursor = self.db_connection.cursor()

# Obtener items de la orden origen
items_origen = self.obtener_items_orden(orden_origen_id)

if not items_origen:
                logger.warning(f"No hay items para duplicar en orden {orden_origen_id}")
return True

# Crear items en la orden destino
items_creados = 0
for item in items_origen:
                datos_item = {
'producto_id': item['producto_id'],
'codigo_producto': item['codigo_producto'],
'descripcion': item['descripcion'],
'cantidad': item['cantidad'],
'precio_unitario': item['precio_unitario'],
'descuento_porcentaje': item['descuento_porcentaje']
}

if self.crear_item_compra(orden_destino_id, datos_item):
                items_creados += 1

logger.info(f"Duplicados {items_creados} items de orden {orden_origen_id} a orden {orden_destino_id}")
return items_creados > 0

except Exception as e:
        logger.error(f"Error duplicando items de orden: {e}")
return False