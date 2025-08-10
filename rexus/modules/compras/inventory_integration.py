"""
MIT License

Copyright (c) 2024 Rexus.app

Integración de Inventario para el Módulo de Compras
Maneja la sincronización entre compras y el sistema de inventario
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from rexus.core.auth_decorators import auth_required
from rexus.utils.security import SecurityUtils
from rexus.utils.unified_sanitizer import unified_sanitizer, sanitize_string, sanitize_numeric

logger = logging.getLogger(__name__)


@dataclass
class InventoryItem:
    """Representa un item de inventario para sincronización."""
    codigo: str
    nombre: str
    categoria_id: Optional[int]
    cantidad: int
    precio_unitario: float
    proveedor_id: Optional[int]
    observaciones: Optional[str] = None


class InventoryIntegration:
    """Maneja la integración entre compras e inventario."""
    
    def __init__(self, compras_db, inventario_db):
        """
        Inicializa la integración de inventario.
        
        Args:
            compras_db: Conexión a la base de datos de compras
            inventario_db: Conexión a la base de datos de inventario
        """
        self.compras_db = compras_db
        self.inventario_db = inventario_db
        
    @auth_required
    def procesar_recepcion_completa(self, orden_id: int, items_recibidos: List[Dict]) -> bool:
        """
        Procesa la recepción completa de una orden actualizando inventario.
        
        Args:
            orden_id: ID de la orden de compra
            items_recibidos: Lista de items recibidos con cantidades
            
        Returns:
            bool: True si la integración fue exitosa
        """
        try:
            logger.info(f"Procesando recepción completa para orden {orden_id}")
            
            # Obtener detalles de la orden
            detalles_orden = self._obtener_detalles_orden(orden_id)
            if not detalles_orden:
                logger.error(f"No se encontraron detalles para orden {orden_id}")
                return False
            
            # Procesar cada item recibido
            items_procesados = 0
            for item_recibido in items_recibidos:
                if self._actualizar_stock_inventario(item_recibido, detalles_orden):
                    items_procesados += 1
                else:
                    logger.warning(f"Error procesando item: {item_recibido}")
            
            # Registrar historial de integración
            self._registrar_integracion_inventario(
                orden_id, 
                items_procesados, 
                len(items_recibidos)
            )
            
            logger.info(f"Recepción procesada: {items_procesados}/{len(items_recibidos)} items")
            return items_procesados == len(items_recibidos)
            
        except Exception as e:
            logger.error(f"Error procesando recepción completa: {e}", exc_info=True)
            return False
    
    def _obtener_detalles_orden(self, orden_id: int) -> Optional[List[Dict]]:
        """Obtiene los detalles de una orden de compra."""
        try:
            cursor = self.compras_db.cursor()
            cursor.execute("""
                SELECT 
                    dc.id,
                    dc.codigo_producto,
                    dc.descripcion,
                    dc.cantidad_solicitada,
                    dc.precio_unitario,
                    dc.subtotal,
                    c.proveedor_id
                FROM detalle_compras dc
                INNER JOIN compras c ON dc.compra_id = c.id
                WHERE dc.compra_id = ?
            """, (orden_id,))
            
            detalles = []
            for row in cursor.fetchall():
                detalles.append({
                    'detalle_id': row[0],
                    'codigo_producto': SecurityUtils.sanitize_string(row[1]),
                    'descripcion': SecurityUtils.sanitize_string(row[2]),
                    'cantidad_solicitada': row[3],
                    'precio_unitario': row[4],
                    'subtotal': row[5],
                    'proveedor_id': row[6]
                })
                
            return detalles
            
        except Exception as e:
            logger.error(f"Error obteniendo detalles de orden {orden_id}: {e}")
            return None
    
    def _actualizar_stock_inventario(self, item_recibido: Dict, detalles_orden: List[Dict]) -> bool:
        """Actualiza el stock en el sistema de inventario."""
        try:
            codigo_producto = item_recibido.get('codigo_producto')
            cantidad_recibida = item_recibido.get('cantidad_recibida', 0)
            
            if not codigo_producto or cantidad_recibida <= 0:
                logger.warning(f"Datos inválidos para actualización de stock: {item_recibido}")
                return False
            
            # Buscar detalle correspondiente
            detalle = next(
                (d for d in detalles_orden if d['codigo_producto'] == codigo_producto), 
                None
            )
            
            if not detalle:
                logger.warning(f"No se encontró detalle para producto {codigo_producto}")
                return False
            
            # Verificar si el producto existe en inventario
            if self._producto_existe_en_inventario(codigo_producto):
                return self._incrementar_stock_existente(codigo_producto, cantidad_recibida)
            else:
                return self._crear_nuevo_item_inventario(
                    codigo_producto, 
                    detalle, 
                    cantidad_recibida
                )
                
        except Exception as e:
            logger.error(f"Error actualizando stock: {e}", exc_info=True)
            return False
    
    def _producto_existe_en_inventario(self, codigo_producto: str) -> bool:
        """Verifica si un producto existe en el inventario."""
        try:
            cursor = self.inventario_db.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM inventario WHERE codigo = ?",
                (codigo_producto,)
            )
            count = cursor.fetchone()[0]
            return count > 0
            
        except Exception as e:
            logger.error(f"Error verificando existencia de producto {codigo_producto}: {e}")
            return False
    
    def _incrementar_stock_existente(self, codigo_producto: str, cantidad: int) -> bool:
        """Incrementa el stock de un producto existente."""
        try:
            cursor = self.inventario_db.cursor()
            cursor.execute("""
                UPDATE inventario 
                SET cantidad = cantidad + ?,
                    fecha_ultima_actualizacion = ?,
                    usuario_ultima_actualizacion = ?
                WHERE codigo = ?
            """, (
                cantidad,
                datetime.now(),
                "SISTEMA_COMPRAS",
                codigo_producto
            ))
            
            self.inventario_db.commit()
            logger.info(f"Stock incrementado para {codigo_producto}: +{cantidad}")
            return True
            
        except Exception as e:
            logger.error(f"Error incrementando stock para {codigo_producto}: {e}")
            return False
    
    def _crear_nuevo_item_inventario(self, codigo_producto: str, detalle: Dict, cantidad: int) -> bool:
        """Crea un nuevo item en el inventario."""
        try:
            cursor = self.inventario_db.cursor()
            cursor.execute("""
                INSERT INTO inventario (
                    codigo, descripcion, cantidad, precio_unitario,
                    categoria_id, proveedor_id, estado, 
                    fecha_creacion, usuario_creacion,
                    fecha_ultima_actualizacion, usuario_ultima_actualizacion
                ) VALUES (?, ?, ?, ?, ?, ?, 'ACTIVO', ?, ?, ?, ?)
            """, (
                codigo_producto,
                detalle['descripcion'],
                cantidad,
                detalle['precio_unitario'],
                None,  # categoria_id - se puede obtener de configuración
                detalle['proveedor_id'],
                datetime.now(),
                "SISTEMA_COMPRAS",
                datetime.now(),
                "SISTEMA_COMPRAS"
            ))
            
            self.inventario_db.commit()
            logger.info(f"Nuevo item creado en inventario: {codigo_producto} ({cantidad} unidades)")
            return True
            
        except Exception as e:
            logger.error(f"Error creando item en inventario {codigo_producto}: {e}")
            return False
    
    def _registrar_integracion_inventario(self, orden_id: int, items_procesados: int, total_items: int):
        """Registra el historial de integración con inventario."""
        try:
            cursor = self.compras_db.cursor()
            cursor.execute("""
                INSERT INTO integracion_inventario (
                    orden_id, items_procesados, total_items,
                    fecha_integracion, estado_integracion
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                orden_id,
                items_procesados,
                total_items,
                datetime.now(),
                'COMPLETADA' if items_procesados == total_items else 'PARCIAL'
            ))
            
            self.compras_db.commit()
            logger.info(f"Historial de integración registrado para orden {orden_id}")
            
        except Exception as e:
            logger.error(f"Error registrando historial de integración: {e}")
    
    @auth_required
    def verificar_disponibilidad_stock(self, items_solicitud: List[Dict]) -> Dict[str, Any]:
        """
        Verifica la disponibilidad de stock antes de crear una orden.
        
        Args:
            items_solicitud: Lista de items solicitados
            
        Returns:
            Dict con información de disponibilidad
        """
        try:
            resultado = {
                'disponible_completo': True,
                'items_verificados': [],
                'advertencias': []
            }
            
            for item in items_solicitud:
                codigo = item.get('codigo_producto')
                cantidad_solicitada = item.get('cantidad', 0)
                
                if not codigo:
                    continue
                    
                # Obtener stock actual
                stock_actual = self._obtener_stock_actual(codigo)
                
                item_verificado = {
                    'codigo_producto': codigo,
                    'cantidad_solicitada': cantidad_solicitada,
                    'stock_actual': stock_actual,
                    'disponible': stock_actual >= cantidad_solicitada
                }
                
                if not item_verificado['disponible']:
                    resultado['disponible_completo'] = False
                    resultado['advertencias'].append(
                        f"Stock insuficiente para {codigo}: disponible {stock_actual}, solicitado {cantidad_solicitada}"
                    )
                
                resultado['items_verificados'].append(item_verificado)
            
            return resultado
            
        except Exception as e:
            logger.error(f"Error verificando disponibilidad de stock: {e}")
            return {'disponible_completo': False, 'error': str(e)}
    
    def _obtener_stock_actual(self, codigo_producto: str) -> int:
        """Obtiene el stock actual de un producto."""
        try:
            cursor = self.inventario_db.cursor()
            cursor.execute(
                "SELECT cantidad FROM inventario WHERE codigo = ? AND estado = 'ACTIVO'",
                (codigo_producto,)
            )
            
            result = cursor.fetchone()
            return result[0] if result else 0
            
        except Exception as e:
            logger.error(f"Error obteniendo stock para {codigo_producto}: {e}")
            return 0
    
    @auth_required
    def generar_reporte_integracion(self, fecha_inicio: datetime, fecha_fin: datetime) -> List[Dict]:
        """
        Genera un reporte de integración con inventario.
        
        Args:
            fecha_inicio: Fecha de inicio del reporte
            fecha_fin: Fecha de fin del reporte
            
        Returns:
            Lista con datos del reporte
        """
        try:
            cursor = self.compras_db.cursor()
            cursor.execute("""
                SELECT 
                    ii.orden_id,
                    c.numero_orden,
                    c.proveedor,
                    ii.items_procesados,
                    ii.total_items,
                    ii.fecha_integracion,
                    ii.estado_integracion
                FROM integracion_inventario ii
                INNER JOIN compras c ON ii.orden_id = c.id
                WHERE ii.fecha_integracion BETWEEN ? AND ?
                ORDER BY ii.fecha_integracion DESC
            """, (fecha_inicio, fecha_fin))
            
            reporte = []
            for row in cursor.fetchall():
                reporte.append({
                    'orden_id': row[0],
                    'numero_orden': SecurityUtils.sanitize_string(row[1]),
                    'proveedor': SecurityUtils.sanitize_string(row[2]),
                    'items_procesados': row[3],
                    'total_items': row[4],
                    'fecha_integracion': row[5],
                    'estado_integracion': row[6],
                    'tasa_exito': (row[3] / row[4] * 100) if row[4] > 0 else 0
                })
            
            logger.info(f"Reporte de integración generado: {len(reporte)} registros")
            return reporte
            
        except Exception as e:
            logger.error(f"Error generando reporte de integración: {e}")
            return []
    
    def crear_tablas_integracion_si_no_existen(self):
        """Crea las tablas necesarias para la integración si no existen."""
        try:
            cursor = self.compras_db.cursor()
            
            # Tabla para historial de integración
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='integracion_inventario' AND xtype='U')
                CREATE TABLE integracion_inventario (
                    id INTEGER IDENTITY(1,1) PRIMARY KEY,
                    orden_id INTEGER NOT NULL,
                    items_procesados INTEGER NOT NULL,
                    total_items INTEGER NOT NULL,
                    fecha_integracion DATETIME NOT NULL,
                    estado_integracion VARCHAR(20) NOT NULL,
                    observaciones TEXT,
                    FOREIGN KEY (orden_id) REFERENCES compras(id)
                )
            """)
            
            # Índices para mejor rendimiento
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sysindexes WHERE name='IX_integracion_inventario_orden_id')
                CREATE INDEX IX_integracion_inventario_orden_id ON integracion_inventario(orden_id)
            """)
            
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sysindexes WHERE name='IX_integracion_inventario_fecha')
                CREATE INDEX IX_integracion_inventario_fecha ON integracion_inventario(fecha_integracion)
            """)
            
            self.compras_db.commit()
            logger.info("Tablas de integración verificadas/creadas exitosamente")
            
        except Exception as e:
            logger.error(f"Error creando tablas de integración: {e}")


# Instancia global para uso en el módulo de compras
_inventory_integration = None

def get_inventory_integration(compras_db, inventario_db):
    """Obtiene la instancia global de integración de inventario."""
    global _inventory_integration
    if _inventory_integration is None:
        _inventory_integration = InventoryIntegration(compras_db, inventario_db)
        _inventory_integration.crear_tablas_integracion_si_no_existen()
    return _inventory_integration


def integrar_recepcion_orden(orden_id: int, items_recibidos: List[Dict]) -> bool:
    """
    Función de conveniencia para integrar la recepción de una orden.
    
    Args:
        orden_id: ID de la orden
        items_recibidos: Items recibidos
        
    Returns:
        bool: Éxito de la integración
    """
    try:
        from rexus.core.database import get_inventario_connection
        
        # Obtener conexiones (esto se debe configurar según la arquitectura)
        # En un escenario real, estas conexiones vendrían del sistema principal
        compras_db = None  # Se debe obtener del contexto
        inventario_db = get_inventario_connection()
        
        if not compras_db or not inventario_db:
            logger.error("No se pudieron obtener las conexiones de base de datos")
            return False
        
        integration = get_inventory_integration(compras_db, inventario_db)
        return integration.procesar_recepcion_completa(orden_id, items_recibidos)
        
    except Exception as e:
        logger.error(f"Error en integración de recepción: {e}")
        return False