"""
Submódulo de Consultas - Inventario Rexus.app

Gestiona consultas complejas, búsquedas y paginación.
Responsabilidades:
- Búsquedas paginadas
- Filtros complejos
- Estadísticas de inventario
- Reportes y consultas optimizadas
"""

from typing import Any, Dict, List, Optional

# Imports de seguridad unificados
from rexus.core.auth_decorators import auth_required, permission_required
from rexus.utils.pagination import PaginatedTableMixin
from rexus.utils.unified_sanitizer import unified_sanitizer, sanitize_string
from rexus.utils.unified_sanitizer import sanitize_string

# DataSanitizer unificado
try:
    from rexus.utils.unified_sanitizer import unified_sanitizer
    # unified_sanitizer ya es una instancia, no se necesita instanciar
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

    @auth_required
    @permission_required("view_inventario")
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

            query_count = "SELECT COUNT(*) FROM inventario WHERE activo = 1"
            params = []

            # Aplicar filtros
            if filtros_sanitizados.get("categoria"):
                query_base += " AND categoria = ?"
                query_count += " AND categoria = ?"
                params.append(filtros_sanitizados["categoria"])

            if filtros_sanitizados.get("busqueda"):
                busqueda = f"%{filtros_sanitizados['busqueda']}%"
                query_base += " AND (codigo LIKE ? OR descripcion LIKE ?)"
                query_count += " AND (codigo LIKE ? OR descripcion LIKE ?)"
                params.extend([busqueda, busqueda])

            if filtros_sanitizados.get("stock_bajo"):
                query_base += " AND stock_actual <= stock_minimo"
                query_count += " AND stock_actual <= stock_minimo"

            if filtros_sanitizados.get("ubicacion"):
                query_base += " AND ubicacion LIKE ?"
                query_count += " AND ubicacion LIKE ?"
                params.append(f"%{filtros_sanitizados['ubicacion']}%")

            # Obtener total de registros
            cursor = self.db_connection.cursor()
            cursor.execute(query_count, params)
            total = cursor.fetchone()[0]

            # Aplicar ordenamiento y paginación
            query_base += f" ORDER BY {orden}"
            query_base += f" OFFSET {offset} ROWS FETCH NEXT {limit} ROWS ONLY"

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
            raise Exception(f"Error obteniendo productos paginados: {str(e)}")

    @auth_required
    @permission_required("view_inventario")
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
                    ubicacion, observaciones, qr_data, fecha_creacion
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
            raise Exception(f"Error obteniendo todos los productos: {str(e)}")

    @auth_required
    @permission_required("view_estadisticas")
    def obtener_estadisticas_inventario(self) -> Dict[str, Any]:
        """Obtiene estadísticas generales del inventario."""
        if not self.db_connection:
            return {}

        try:
            cursor = self.db_connection.cursor()

            # Estadísticas generales
            cursor.execute("""
                SELECT
                    COUNT(*) as total_productos,
                    COUNT(CASE WHEN stock_actual > 0 THEN 1 END) as productos_con_stock,
                    COUNT(CASE WHEN stock_actual = 0 THEN 1 END) as productos_sin_stock,
                    COUNT(CASE WHEN stock_actual <= stock_minimo THEN 1 END) as productos_stock_bajo,
                    SUM(stock_actual * precio_compra) as valor_total_compra,
                    SUM(stock_actual * precio_venta) as valor_total_venta,
                    AVG(stock_actual) as stock_promedio
                FROM inventario
                WHERE activo = 1
            """)

            row = cursor.fetchone()
            estadisticas_generales = {
                "total_productos": row[0] or 0,
                "productos_con_stock": row[1] or 0,
                "productos_sin_stock": row[2] or 0,
                "productos_stock_bajo": row[3] or 0,
                "valor_total_compra": float(row[4]) if row[4] else 0,
                "valor_total_venta": float(row[5]) if row[5] else 0,
                "stock_promedio": float(row[6]) if row[6] else 0,
            }

            # Estadísticas por categoría
            cursor.execute("""
                SELECT
                    categoria,
                    COUNT(*) as cantidad_productos,
                    SUM(stock_actual) as stock_total,
                    SUM(stock_actual * precio_venta) as valor_categoria
                FROM inventario
                WHERE activo = 1
                GROUP BY categoria
                ORDER BY cantidad_productos DESC
            """)

            estadisticas_categoria = []
            for row in cursor.fetchall():
                estadisticas_categoria.append(
                    {
                        "categoria": row[0],
                        "cantidad_productos": row[1],
                        "stock_total": float(row[2]) if row[2] else 0,
                        "valor_categoria": float(row[3]) if row[3] else 0,
                    }
                )

            # Productos más valiosos
            cursor.execute("""
                SELECT TOP 10
                    codigo, descripcion, stock_actual, precio_venta,
                    (stock_actual * precio_venta) as valor_total
                FROM inventario
                WHERE activo = 1 AND stock_actual > 0
                ORDER BY (stock_actual * precio_venta) DESC
            """)

            productos_valiosos = []
            for row in cursor.fetchall():
                productos_valiosos.append(
                    {
                        "codigo": row[0],
                        "descripcion": row[1],
                        "stock_actual": float(row[2]),
                        "precio_venta": float(row[3]),
                        "valor_total": float(row[4]),
                    }
                )

            return {
                "generales": estadisticas_generales,
                "por_categoria": estadisticas_categoria,
                "productos_valiosos": productos_valiosos,
                "fecha_calculo": "2025-08-06",  # Se puede hacer dinámico
            }

        except Exception as e:
            raise Exception(f"Error obteniendo estadísticas: {str(e)}")

    @auth_required
    @permission_required("view_inventario")
    def buscar_productos(
        self, termino_busqueda: str, limite: int = 20
    ) -> List[Dict[str, Any]]:
        """Búsqueda rápida de productos por código o descripción."""
        if not self.db_connection or not termino_busqueda:
            return []

        try:
            cursor = self.db_connection.cursor()

            # Sanitizar término de búsqueda
            termino = sanitize_string(termino_busqueda.strip())
            termino_like = f"%{termino}%"

            cursor.execute(
                f"""
                SELECT TOP {limite}
                    id, codigo, descripcion, categoria, stock_actual, precio_venta
                FROM inventario
                WHERE activo = 1
                    AND (codigo LIKE ? OR descripcion LIKE ?)
                ORDER BY
                    CASE
                        WHEN codigo = ? THEN 1
                        WHEN codigo LIKE ? THEN 2
                        WHEN descripcion LIKE ? THEN 3
                        ELSE 4
                    END,
                    descripcion ASC
            """,
                (termino_like,
termino_like,
                    termino,
                    f"{termino}%",
                    f"%{termino}%"),
            )

            columns = [column[0] for column in cursor.description]

            resultados = []
            for row in cursor.fetchall():
                producto = dict(zip(columns, row))
                producto["relevancia"] = self._calcular_relevancia(
                    termino, producto["codigo"], producto["descripcion"]
                )
                resultados.append(producto)

            return resultados

        except Exception as e:
            raise Exception(f"Error en búsqueda de productos: {str(e)}")

    def _calcular_relevancia(
        self, termino: str, codigo: str, descripcion: str
    ) -> float:
        """Calcula la relevancia de un resultado de búsqueda."""
        relevancia = 0.0
        termino_lower = termino.lower()
        codigo_lower = codigo.lower()
        descripcion_lower = descripcion.lower()

        # Coincidencia exacta en código = máxima relevancia
        if codigo_lower == termino_lower:
            relevancia = 1.0
        # Código empieza con el término
        elif codigo_lower.startswith(termino_lower):
            relevancia = 0.9
        # Código contiene el término
        elif termino_lower in codigo_lower:
            relevancia = 0.7
        # Descripción empieza con el término
        elif descripcion_lower.startswith(termino_lower):
            relevancia = 0.6
        # Descripción contiene el término
        elif termino_lower in descripcion_lower:
            relevancia = 0.4

        return relevancia
