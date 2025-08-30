"""
Submódulo de Consultas - Inventario Rexus.app

Gestiona consultas complejas, búsquedas y paginación.
Responsabilidades:
- Búsquedas paginadas
- Filtros complejos
- Estadísticas de inventario
- Reportes y consultas optimizadas
"""

import logging
from typing import Optional, Dict, List, Any

logger = logging.getLogger(__name__)

# Imports necesarios
try:
    from rexus.utils.pagination import PaginatedTableMixin
except ImportError:
    PaginatedTableMixin = object

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
        def sanitize_text(self, text):
            return str(text) if text else ""
    data_sanitizer = DataSanitizer()


class ConsultasManager(PaginatedTableMixin):
    """Gestor especializado para consultas y búsquedas de inventario."""

    def __init__(self, db_connection=None):
        """Inicializa el gestor de consultas."""
        self.db_connection = db_connection
        self.sanitizer = data_sanitizer
        
    def obtener_productos_paginados(
        self,
        offset: int = 0,
        limit: int = 50,
        filtros: Optional[Dict[str, Any]] = None,
        orden: str = "descripcion ASC",
    ) -> Dict[str, Any]:
        """Obtiene productos con paginación y filtros."""
        if not self.db_connection:
            return {"items": [], "total": 0, "offset": offset, "limit": limit}

        try:
            # Sanitizar filtros
            filtros_sanitizados = {}
            if filtros:
                filtros_sanitizados = self.sanitizer.sanitize_dict(filtros)

            # Construir query base
            query_base = """
            SELECT
                id, codigo, descripcion, categoria, unidad_medida,
                precio_compra, precio_venta, stock_actual, stock_minimo,
                ubicacion, observaciones, fecha_creacion, fecha_modificacion
            FROM inventario
            WHERE activo = 1
            """

            # Parámetros para las consultas
            params = []
            
            # Aplicar filtros
            if filtros_sanitizados.get("categoria"):
                query_base += " AND categoria = ?"
                params.append(filtros_sanitizados["categoria"])

            if filtros_sanitizados.get("busqueda"):
                busqueda = f"%{filtros_sanitizados['busqueda']}%"
                query_base += " AND (codigo LIKE ? OR descripcion LIKE ?)"
                params.extend([busqueda, busqueda])

            if filtros_sanitizados.get("stock_bajo"):
                query_base += " AND stock_actual <= stock_minimo"

            if filtros_sanitizados.get("ubicacion"):
                query_base += " AND ubicacion LIKE ?"
                params.append(f"%{filtros_sanitizados['ubicacion']}%")

            # Obtener total de registros
            query_count = query_base.replace(
                "id, codigo, descripcion, categoria, unidad_medida, precio_compra, precio_venta, stock_actual, stock_minimo, ubicacion, observaciones, fecha_creacion, fecha_modificacion",
                "COUNT(*)"
            )
            cursor = self.db_connection.cursor()
            cursor.execute(query_count, params)
            total = cursor.fetchone()[0]

            # Aplicar ordenamiento y paginación
            query_base += f" ORDER BY {orden}"
            query_base += f" LIMIT {limit} OFFSET {offset}"

            # Ejecutar consulta principal
            cursor.execute(query_base, params)
            columns = [column[0] for column in cursor.description]
            
            items = []
            for row in cursor.fetchall():
                producto = dict(zip(columns, row))
                
                # Calcular estado de stock
                if producto["stock_actual"] <= 0:
                    producto["estado_stock"] = "SIN_STOCK"
                elif producto["stock_actual"] <= producto["stock_minimo"]:
                    producto["estado_stock"] = "STOCK_BAJO"
                else:
                    producto["estado_stock"] = "NORMAL"
                    
                items.append(producto)

            return {
                "items": items,
                "total": total,
                "offset": offset,
                "limit": limit,
                "pages": (total + limit - 1) // limit,
                "current_page": (offset // limit) + 1,
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo productos paginados: {str(e)}")
            return {"items": [], "total": 0, "offset": offset, "limit": limit}

    def obtener_todos_productos(
        self, filtros: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Obtiene todos los productos (sin paginación) para reportes."""
        if not self.db_connection:
            return []

        try:
            cursor = self.db_connection.cursor()

            query = """
            SELECT
                id, codigo, descripcion, categoria, unidad_medida,
                precio_compra, precio_venta, stock_actual, stock_minimo,
                ubicacion, observaciones, fecha_creacion
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

            query += " ORDER BY descripcion ASC"

            cursor.execute(query, params)
            columns = [column[0] for column in cursor.description]

            resultados = []
            for row in cursor.fetchall():
                resultados.append(dict(zip(columns, row)))

            return resultados

        except Exception as e:
            logger.error(f"Error obteniendo todos los productos: {str(e)}")
            return []

    def buscar_productos(
        self, termino_busqueda: str, limite: int = 20
    ) -> List[Dict[str, Any]]:
        """Búsqueda rápida de productos por código o descripción."""
        if not self.db_connection or not termino_busqueda:
            return []

        try:
            cursor = self.db_connection.cursor()

            # Sanitizar término de búsqueda
            termino = self.sanitizer.sanitize_string(termino_busqueda.strip())
            termino_like = f"%{termino}%"

            query = f"""
            SELECT 
                id, codigo, descripcion, categoria, stock_actual, precio_venta
            FROM inventario
            WHERE activo = 1
            AND (codigo LIKE ? OR descripcion LIKE ?)
            ORDER BY descripcion ASC
            LIMIT {limite}
            """

            cursor.execute(query, (termino_like, termino_like))
            columns = [column[0] for column in cursor.description]

            resultados = []
            for row in cursor.fetchall():
                resultados.append(dict(zip(columns, row)))

            return resultados

        except Exception as e:
            logger.error(f"Error en búsqueda de productos: {str(e)}")
            return []