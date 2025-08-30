"""
Submódulo de Reportes - Inventario Rexus.app
Genera reportes específicos del inventario
"""

import logging
from typing import Optional, Dict, List, Any
from datetime import datetime

logger = logging.getLogger(__name__)

# Imports necesarios
try:
    from rexus.utils.unified_sanitizer import unified_sanitizer
    data_sanitizer = unified_sanitizer
except ImportError:
    class DataSanitizer:
        def sanitize_dict(self, data):
            return data if data else {}
        def sanitize_string(self, text):
            return str(text) if text else ""
        def sanitize_integer(self, value):
            return int(value) if value else 0
    data_sanitizer = DataSanitizer()

# Cache availability check
try:
    from rexus.utils.cache_manager import get_cache_manager
    CACHE_AVAILABLE = True
    def cache_inventory_report(report_type, ttl=300):
        def decorator(func):
            return func  # Simplified for now
        return decorator
except ImportError:
    CACHE_AVAILABLE = False
    def cache_inventory_report(report_type, ttl=300):
        def decorator(func):
            return func
        return decorator


class ReportesManager:
    """Gestor especializado para reportes de inventario."""

    def __init__(self, db_connection=None):
        """Inicializa el gestor de reportes."""
        self.db_connection = db_connection
        self.sanitizer = data_sanitizer
        
    @cache_inventory_report('stock', ttl=600)
    def generar_reporte_stock(
        self,
        filtros: Optional[Dict[str, Any]] = None,
        incluir_detalle: bool = True
    ) -> Dict[str, Any]:
        """Genera reporte completo de stock."""
        if not self.db_connection:
            return {
                'success': False,
                'error': 'No hay conexión a base de datos'
            }

        try:
            start_time = datetime.now()
            cursor = self.db_connection.cursor()

            # Query base para productos
            query = """
            SELECT
                id, codigo, descripcion, categoria, unidad_medida,
                precio_compra, precio_venta, stock_actual, stock_minimo,
                ubicacion, observaciones
            FROM inventario
            WHERE activo = 1
            """

            params = []

            # Aplicar filtros si existen
            if filtros:
                filtros_sanitizados = self.sanitizer.sanitize_dict(filtros)
                
                if filtros_sanitizados.get("categoria"):
                    query += " AND categoria = ?"
                    params.append(filtros_sanitizados["categoria"])
                    
                if filtros_sanitizados.get("stock_bajo"):
                    query += " AND stock_actual <= stock_minimo"

            query += " ORDER BY categoria, descripcion"

            cursor.execute(query, params)
            columns = [column[0] for column in cursor.description]

            productos = []
            for row in cursor.fetchall():
                producto = dict(zip(columns, row))
                
                # Calcular estado de stock
                if producto["stock_actual"] <= 0:
                    producto["estado_stock"] = "SIN_STOCK"
                elif producto["stock_actual"] <= producto["stock_minimo"]:
                    producto["estado_stock"] = "STOCK_BAJO"
                else:
                    producto["estado_stock"] = "NORMAL"
                    
                productos.append(producto)

            # Generar resumen
            total_productos = len(productos)
            sin_stock = len([p for p in productos if p["estado_stock"] == "SIN_STOCK"])
            stock_bajo = len([p for p in productos if p["estado_stock"] == "STOCK_BAJO"])
            
            valor_total = sum([
                (p.get("stock_actual", 0) * p.get("precio_compra", 0)) 
                for p in productos
            ])

            resumen = {
                'total_productos': total_productos,
                'productos_sin_stock': sin_stock,
                'productos_stock_bajo': stock_bajo,
                'productos_normal': total_productos - sin_stock - stock_bajo,
                'valor_total_inventario': valor_total,
                'fecha_generacion': datetime.now().isoformat(),
                'tiempo_ejecucion': (datetime.now() - start_time).total_seconds()
            }

            return {
                'success': True,
                'productos': productos,
                'resumen': resumen
            }
            
        except Exception as e:
            logger.error(f"Error generando reporte de stock: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    @cache_inventory_report('movimientos', ttl=900)
    def generar_reporte_movimientos(
        self, 
        fecha_inicio: Optional[datetime] = None, 
        fecha_fin: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Genera reporte de movimientos de inventario."""
        if not self.db_connection:
            return {
                'success': False,
                'error': 'No hay conexión a base de datos'
            }

        try:
            cursor = self.db_connection.cursor()

            query = """
            SELECT 
                m.id, m.tipo_movimiento, m.cantidad, m.fecha_movimiento,
                m.observaciones, p.codigo, p.descripcion
            FROM movimientos_inventario m
            JOIN inventario p ON m.producto_id = p.id
            WHERE 1=1
            """

            params = []

            # Filtros de fecha
            if fecha_inicio:
                query += " AND m.fecha_movimiento >= ?"
                params.append(fecha_inicio.isoformat())
                
            if fecha_fin:
                query += " AND m.fecha_movimiento <= ?"
                params.append(fecha_fin.isoformat())

            query += " ORDER BY m.fecha_movimiento DESC"

            cursor.execute(query, params)
            columns = [column[0] for column in cursor.description]

            movimientos = []
            for row in cursor.fetchall():
                movimientos.append(dict(zip(columns, row)))

            return {
                'success': True,
                'movimientos': movimientos,
                'total_movimientos': len(movimientos),
                'fecha_generacion': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generando reporte de movimientos: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def generar_reporte_valorizado(self) -> Dict[str, Any]:
        """Genera reporte valorizado del inventario."""
        if not self.db_connection:
            return {
                'success': False,
                'error': 'No hay conexión a base de datos'
            }

        try:
            cursor = self.db_connection.cursor()

            query = """
            SELECT
                categoria,
                COUNT(*) as cantidad_productos,
                SUM(stock_actual) as stock_total,
                SUM(stock_actual * precio_compra) as valor_compra,
                SUM(stock_actual * precio_venta) as valor_venta,
                AVG(precio_compra) as precio_compra_promedio,
                AVG(precio_venta) as precio_venta_promedio
            FROM inventario
            WHERE activo = 1 AND stock_actual > 0
            GROUP BY categoria
            ORDER BY valor_venta DESC
            """

            cursor.execute(query)
            columns = [column[0] for column in cursor.description]

            categorias = []
            for row in cursor.fetchall():
                categoria_data = dict(zip(columns, row))
                categoria_data['margen_promedio'] = (
                    categoria_data['precio_venta_promedio'] - categoria_data['precio_compra_promedio']
                ) if categoria_data['precio_compra_promedio'] > 0 else 0
                categorias.append(categoria_data)

            return {
                'success': True,
                'categorias': categorias,
                'fecha_generacion': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generando reporte valorizado: {e}")
            return {
                'success': False,
                'error': str(e)
            }