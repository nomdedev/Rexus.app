# -*- coding: utf-8 -*-
"""
Integración de Inventario para el Módulo de Compras - Rexus.app v2.0.0

Maneja la sincronización entre compras y el sistema de inventario.
Procesa recepciones de órdenes, actualiza stock y mantiene trazabilidad.
"""

import logging
from typing import Dict, List, Any, Optional
from decimal import Decimal
from datetime import datetime

# Configurar logging
try:
from ...utils.app_logger import get_logger
logger = get_logger(__name__)
except ImportError:
logger = logging.getLogger(__name__)


class ComprasInventarioIntegration:
"""Maneja la integración entre el módulo de compras e inventario."""

def __init__(self, compras_db=None, inventario_db=None):
        """
Inicializa la integración.

Args:
        compras_db: Conexión a BD del módulo de compras
inventario_db: Conexión a BD del módulo de inventario
"""
self.compras_db = compras_db
self.inventario_db = inventario_db
logger.info("Integración Compras-Inventario inicializada")

def procesar_recepcion_orden(self, orden_id: int, items_recibidos: List[Dict[str, Any]]) -> bool:
        """
Procesa la recepción completa de una orden de compra.

Args:
        orden_id: ID de la orden de compra
items_recibidos: Lista de items recibidos con cantidades

Returns:
        True si se procesó exitosamente
"""
try:
        logger.info(f"Procesando recepción de orden {orden_id}")

if not self._validar_orden_activa(orden_id):
                logger.error(f"Orden {orden_id} no válida para recepción")
return False

success = True
for item in items_recibidos:
                if not self._procesar_item_recibido(orden_id, item):
                success = False
logger.error(f"Error procesando item {item.get('producto_id')}")

if success:
                self._actualizar_estado_orden(orden_id, "RECIBIDA")
logger.info(f"Orden {orden_id} procesada exitosamente")

return success

except Exception as e:
        logger.error(f"Error procesando recepción orden {orden_id}: {e}")
return False

def procesar_recepcion_parcial(self, orden_id: int, item_id: int, cantidad_recibida: float) -> bool:
        """
Procesa la recepción parcial de un item.

Args:
        orden_id: ID de la orden
item_id: ID del item recibido
cantidad_recibida: Cantidad recibida

Returns:
        True si se procesó exitosamente
"""
try:
        logger.info(f"Procesando recepción parcial: orden {orden_id}, item {item_id}")

item_data = self._obtener_datos_item(orden_id, item_id)
if not item_data:
                return False

# Actualizar inventario
success = self._actualizar_stock_inventario(
item_data['producto_id'], 
cantidad_recibida, 
'ENTRADA',
f"Recepción parcial orden {orden_id}"
)

if success:
                self._actualizar_cantidad_recibida(item_id, cantidad_recibida)
self._verificar_orden_completa(orden_id)

return success

except Exception as e:
        logger.error(f"Error en recepción parcial: {e}")
return False

def sincronizar_producto_inventario(self, producto_id: int) -> bool:
        """
Sincroniza un producto entre compras e inventario.

Args:
        producto_id: ID del producto a sincronizar

Returns:
        True si se sincronizó exitosamente
"""
try:
        # Obtener datos del producto desde inventario
producto_inventario = self._obtener_producto_inventario(producto_id)
if not producto_inventario:
                logger.warning(f"Producto {producto_id} no encontrado en inventario")
return False

# Actualizar datos en compras
return self._actualizar_producto_compras(producto_id, producto_inventario)

except Exception as e:
        logger.error(f"Error sincronizando producto {producto_id}: {e}")
return False

def generar_orden_desde_necesidades(self, necesidades: List[Dict[str, Any]]) -> Optional[int]:
        """
Genera una orden de compra basada en necesidades de inventario.

Args:
        necesidades: Lista de productos con cantidades necesarias

Returns:
        ID de la orden creada o None si falló
"""
try:
        logger.info("Generando orden desde necesidades de inventario")

# Validar necesidades
necesidades_validadas = self._validar_necesidades(necesidades)
if not necesidades_validadas:
                return None

# Crear orden de compra
orden_data = {
'tipo': 'AUTOMATICA',
'descripcion': 'Orden generada por necesidades de inventario',
'fecha': datetime.now(),
'estado': 'BORRADOR'
}

orden_id = self._crear_orden_compra(orden_data)
if not orden_id:
                return None

# Agregar items a la orden
for necesidad in necesidades_validadas:
                self._agregar_item_orden(orden_id, necesidad)

logger.info(f"Orden {orden_id} creada desde necesidades")
return orden_id

except Exception as e:
        logger.error(f"Error generando orden desde necesidades: {e}")
return None

def obtener_stock_disponible(self, producto_id: int) -> float:
        """
Obtiene el stock disponible de un producto desde inventario.

Args:
        producto_id: ID del producto

Returns:
        Cantidad disponible
"""
try:
        if not self.inventario_db:
                return 0.0

cursor = self.inventario_db.cursor()
cursor.execute("""
SELECT COALESCE(SUM(cantidad_disponible), 0)
FROM productos 
WHERE id = ? AND activo = 1
""", (producto_id,))

result = cursor.fetchone()
return float(result[0]) if result else 0.0

except Exception as e:
        logger.error(f"Error obteniendo stock de producto {producto_id}: {e}")
return 0.0

def verificar_disponibilidad_items(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
Verifica la disponibilidad de una lista de items.

Args:
        items: Lista de items con producto_id y cantidad

Returns:
        Diccionario con disponibilidad de cada item
"""
try:
        disponibilidad = {}

for item in items:
                producto_id = item.get('producto_id')
cantidad_necesaria = float(item.get('cantidad', 0))

if not producto_id:
                continue

stock_disponible = self.obtener_stock_disponible(producto_id)
disponibilidad[producto_id] = {
'producto_id': producto_id,
'cantidad_necesaria': cantidad_necesaria,
'stock_disponible': stock_disponible,
'disponible': stock_disponible >= cantidad_necesaria,
'faltante': max(0, cantidad_necesaria - stock_disponible)
}

return disponibilidad

except Exception as e:
        logger.error(f"Error verificando disponibilidad: {e}")
return {}

# ===== MÉTODOS PRIVADOS =====

def _validar_orden_activa(self, orden_id: int) -> bool:
        """Valida que una orden esté activa y pueda recibirse."""
try:
        if not self.compras_db:
                return False

cursor = self.compras_db.cursor()
cursor.execute("""
SELECT estado FROM ordenes_compra 
WHERE id = ? AND activo = 1
""", (orden_id,))

result = cursor.fetchone()
if not result:
                return False

estado = result[0]
return estado in ['ENVIADA', 'CONFIRMADA', 'PARCIAL']

except Exception as e:
        logger.error(f"Error validando orden {orden_id}: {e}")
return False

def _procesar_item_recibido(self, orden_id: int, item: Dict[str, Any]) -> bool:
        """Procesa un item recibido individual."""
try:
        producto_id = item.get('producto_id')
cantidad = float(item.get('cantidad_recibida', 0))

if not producto_id or cantidad <= 0:
                return False

# Actualizar stock en inventario
return self._actualizar_stock_inventario(
producto_id, 
cantidad, 
'ENTRADA',
f"Recepción orden {orden_id}"
)

except Exception as e:
        logger.error(f"Error procesando item recibido: {e}")
return False

def _actualizar_stock_inventario(self, producto_id: int, cantidad: float, tipo: str, descripcion: str) -> bool:
        """Actualiza el stock en el módulo de inventario."""
try:
        if not self.inventario_db:
                logger.warning("No hay conexión a BD de inventario")
return False

cursor = self.inventario_db.cursor()

# Registrar movimiento
cursor.execute("""
INSERT INTO movimientos_inventario 
(producto_id, tipo, cantidad, descripcion, fecha)
VALUES (?, ?, ?, ?, ?)
""", (producto_id, tipo, cantidad, descripcion, datetime.now()))

# Actualizar stock del producto
if tipo == 'ENTRADA':
                cursor.execute("""
UPDATE productos 
SET cantidad_disponible = cantidad_disponible + ?
WHERE id = ?
""", (cantidad, producto_id))
elif tipo == 'SALIDA':
                cursor.execute("""
UPDATE productos 
SET cantidad_disponible = cantidad_disponible - ?
WHERE id = ? AND cantidad_disponible >= ?
""", (cantidad, producto_id, cantidad))

self.inventario_db.commit()
return True

except Exception as e:
        logger.error(f"Error actualizando stock inventario: {e}")
return False

def _actualizar_estado_orden(self, orden_id: int, nuevo_estado: str):
        """Actualiza el estado de una orden de compra."""
try:
        if not self.compras_db:
                return

cursor = self.compras_db.cursor()
cursor.execute("""
UPDATE ordenes_compra 
SET estado = ?, fecha_recepcion = ?
WHERE id = ?
""", (nuevo_estado, datetime.now(), orden_id))

self.compras_db.commit()

except Exception as e:
        logger.error(f"Error actualizando estado orden {orden_id}: {e}")

def _obtener_datos_item(self, orden_id: int, item_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene los datos de un item de orden."""
try:
        if not self.compras_db:
                return None

cursor = self.compras_db.cursor()
cursor.execute("""
SELECT producto_id, cantidad, precio_unitario
FROM ordenes_compra_detalles
WHERE orden_id = ? AND id = ?
""", (orden_id, item_id))

result = cursor.fetchone()
if result:
                return {
'producto_id': result[0],
'cantidad': result[1],
'precio_unitario': result[2]
}

return None

except Exception as e:
        logger.error(f"Error obteniendo datos item {item_id}: {e}")
return None

def _actualizar_cantidad_recibida(self, item_id: int, cantidad: float):
        """Actualiza la cantidad recibida de un item."""
try:
        if not self.compras_db:
                return

cursor = self.compras_db.cursor()
cursor.execute("""
UPDATE ordenes_compra_detalles 
SET cantidad_recibida = COALESCE(cantidad_recibida, 0) + ?
WHERE id = ?
""", (cantidad, item_id))

self.compras_db.commit()

except Exception as e:
        logger.error(f"Error actualizando cantidad recibida item {item_id}: {e}")

def _verificar_orden_completa(self, orden_id: int):
        """Verifica si una orden está completamente recibida."""
try:
        if not self.compras_db:
                return

cursor = self.compras_db.cursor()
cursor.execute("""
SELECT COUNT(*) as total,
COUNT(CASE WHEN cantidad_recibida >= cantidad THEN 1 END) as completos
FROM ordenes_compra_detalles
WHERE orden_id = ?
""", (orden_id,))

result = cursor.fetchone()
if result and result[0] == result[1] and result[0] > 0:
                self._actualizar_estado_orden(orden_id, "RECIBIDA")
elif result and result[1] > 0:
                self._actualizar_estado_orden(orden_id, "PARCIAL")

except Exception as e:
        logger.error(f"Error verificando orden completa {orden_id}: {e}")

def _obtener_producto_inventario(self, producto_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene los datos de un producto desde inventario."""
try:
        if not self.inventario_db:
                return None

cursor = self.inventario_db.cursor()
cursor.execute("""
SELECT id, codigo, nombre, descripcion, precio_unitario, categoria
FROM productos
WHERE id = ? AND activo = 1
""", (producto_id,))

result = cursor.fetchone()
if result:
                return {
'id': result[0],
'codigo': result[1],
'nombre': result[2],
'descripcion': result[3],
'precio_unitario': result[4],
'categoria': result[5]
}

return None

except Exception as e:
        logger.error(f"Error obteniendo producto inventario {producto_id}: {e}")
return None

def _actualizar_producto_compras(self, producto_id: int, datos_producto: Dict[str, Any]) -> bool:
        """Actualiza los datos de un producto en el módulo de compras."""
try:
        if not self.compras_db:
                return False

cursor = self.compras_db.cursor()
cursor.execute("""
UPDATE productos_compras 
SET codigo = ?, nombre = ?, descripcion = ?, precio_referencia = ?, categoria = ?
WHERE producto_id = ?
""", (
datos_producto['codigo'],
datos_producto['nombre'],
datos_producto['descripcion'],
datos_producto['precio_unitario'],
datos_producto['categoria'],
producto_id
))

self.compras_db.commit()
return True

except Exception as e:
        logger.error(f"Error actualizando producto compras {producto_id}: {e}")
return False

def _validar_necesidades(self, necesidades: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Valida las necesidades de inventario."""
necesidades_validadas = []

for necesidad in necesidades:
        if (necesidad.get('producto_id') and 
necesidad.get('cantidad', 0) > 0):
                necesidades_validadas.append(necesidad)

return necesidades_validadas

def _crear_orden_compra(self, orden_data: Dict[str, Any]) -> Optional[int]:
        """Crea una nueva orden de compra."""
try:
        if not self.compras_db:
                return None

cursor = self.compras_db.cursor()
cursor.execute("""
INSERT INTO ordenes_compra (tipo, descripcion, fecha, estado)
VALUES (?, ?, ?, ?)
""", (
orden_data['tipo'],
orden_data['descripcion'],
orden_data['fecha'],
orden_data['estado']
))

orden_id = cursor.lastrowid
self.compras_db.commit()
return orden_id

except Exception as e:
        logger.error(f"Error creando orden compra: {e}")
return None

def _agregar_item_orden(self, orden_id: int, item_data: Dict[str, Any]):
        """Agrega un item a una orden de compra."""
try:
        if not self.compras_db:
                return

cursor = self.compras_db.cursor()
cursor.execute("""
INSERT INTO ordenes_compra_detalles 
(orden_id, producto_id, cantidad, precio_unitario)
VALUES (?, ?, ?, ?)
""", (
orden_id,
item_data['producto_id'],
item_data['cantidad'],
item_data.get('precio_unitario', 0)
))

self.compras_db.commit()

except Exception as e:
        logger.error(f"Error agregando item a orden {orden_id}: {e}")


def get_inventory_integration(compras_db, inventario_db):
"""
Factory function para obtener instancia de integración.

Args:
        compras_db: Conexión BD de compras
inventario_db: Conexión BD de inventario

Returns:
        Instancia de ComprasInventarioIntegration
"""
return ComprasInventarioIntegration(compras_db, inventario_db)


def procesar_recepcion_completa(orden_id: int, items_recibidos: List[Dict[str, Any]], 
compras_db=None, inventario_db=None) -> bool:
"""
Función de conveniencia para procesar recepción completa.

Args:
        orden_id: ID de la orden
items_recibidos: Items recibidos
compras_db: Conexión BD compras
inventario_db: Conexión BD inventario

Returns:
        True si se procesó exitosamente
"""
try:
        if not compras_db or not inventario_db:
        logger.error("Faltan conexiones de BD para integración")
return False

integration = get_inventory_integration(compras_db, inventario_db)
return integration.procesar_recepcion_orden(orden_id, items_recibidos)

except Exception as e:
        logger.error(f"Error en recepción completa: {e}")
return False