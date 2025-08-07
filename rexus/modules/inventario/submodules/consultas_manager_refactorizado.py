"""
Submódulo de Consultas - Inventario Rexus.app v2.0.0

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

# DataSanitizer unificado
try:
    from rexus.utils.data_sanitizer import DataSanitizer
except ImportError:
    try:
        from utils.data_sanitizer import DataSanitizer
    except ImportError:

        class DataSanitizer:
            def sanitize_dict(self, data):
                return data if data else {}

            def sanitize_text(self, text):
                return str(text) if text else ""

            def sanitize_integer(self, value, min_val=None, max_val=None):
                return int(value) if value else 0


class ConsultasManager:
    """Gestor especializado para consultas y búsquedas de inventario."""

    def __init__(self, db_connection=None):
        """Inicializa el gestor de consultas."""
        self.db_connection = db_connection
        self.data_sanitizer = DataSanitizer()

    def obtener_productos_paginados_inicial(
        self,
        offset: int = 0,
        limit: int = 50,
        filtros: Optional[Dict[str, Any]] = None,
        orden: str = "descripcion ASC",
    ) -> Dict[str, Any]:
        """Obtiene productos con paginación sin autenticación para carga inicial."""
        if not self.db_connection:
            return {
                "items": [
                    {
                        "id": 1,
                        "codigo": "PROD001",
                        "descripcion": "Producto simulado 1",
                        "stock_actual": 10,
                    },
                    {
                        "id": 2,
                        "codigo": "PROD002",
                        "descripcion": "Producto simulado 2",
                        "stock_actual": 5,
                    },
                ],
                "total": 2,
                "offset": offset,
                "limit": limit,
            }

        # Resto de la implementación sin decoradores
        try:
            # Hacer consulta real a la base de datos
            if self.db_connection:
                cursor = self.db_connection.cursor()

                # Construir consulta SQL básica
                query = """
                    SELECT id, codigo, descripcion, stock_actual, categoria, precio_unitario
                    FROM inventario_perfiles 
                    WHERE activo = 1
                    ORDER BY codigo ASC
                    OFFSET ? ROWS FETCH NEXT ? ROWS ONLY
                """

                cursor.execute(query, (offset, limit))
                rows = cursor.fetchall()

                # Convertir resultados a lista de diccionarios
                productos_reales = []
                for row in rows:
                    productos_reales.append(
                        {
                            "id": row[0],
                            "codigo": row[1] if row[1] else f"PROD{row[0]:03d}",
                            "descripcion": row[2] if row[2] else f"Producto {row[0]}",
                            "stock_actual": row[3] if row[3] else 0,
                            "categoria": row[4] if row[4] else "Sin categoría",
                            "precio_unitario": row[5] if row[5] else 0.0,
                        }
                    )

                # Obtener total de registros
                cursor.execute(
                    "SELECT COUNT(*) FROM inventario_perfiles WHERE activo = 1"
                )
                total_row = cursor.fetchone()
                total = total_row[0] if total_row else 0

                print(
                    f"[CONSULTAS MANAGER] Cargados {len(productos_reales)} productos reales de BD (total: {total})"
                )

                return {
                    "items": productos_reales,
                    "total": total,
                    "offset": offset,
                    "limit": limit,
                }

            # Si no hay conexión, usar datos simulados como fallback
            productos_simulados = [
                {
                    "id": i,
                    "codigo": f"PROD{i:03d}",
                    "descripcion": f"Producto {i}",
                    "stock_actual": i * 5,
                }
                for i in range(1, 11)
            ]

            return {
                "items": productos_simulados[offset : offset + limit],
                "total": len(productos_simulados),
                "offset": offset,
                "limit": limit,
            }
        except Exception as e:
            return {
                "items": [],
                "total": 0,
                "offset": offset,
                "limit": limit,
                "error": str(e),
            }

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
            return {
                "items": [
                    {
                        "id": 1,
                        "codigo": "PROD001",
                        "descripcion": "Producto simulado 1",
                        "stock_actual": 10,
                    },
                    {
                        "id": 2,
                        "codigo": "PROD002",
                        "descripcion": "Producto simulado 2",
                        "stock_actual": 5,
                    },
                ],
                "total": 2,
                "offset": offset,
                "limit": limit,
            }

        try:
            # Sanitizar filtros
            filtros_limpios = (
                self.data_sanitizer.sanitize_dict(filtros) if filtros else {}
            )

            # Construir cláusula WHERE
            where_conditions = ["activo = 1"]
            params = []

            if filtros_limpios.get("codigo"):
                where_conditions.append("codigo LIKE %s")
                params.append(f"%{filtros_limpios['codigo']}%")

            if filtros_limpios.get("descripcion"):
                where_conditions.append("descripcion LIKE %s")
                params.append(f"%{filtros_limpios['descripcion']}%")

            if filtros_limpios.get("categoria"):
                where_conditions.append("categoria = %s")
                params.append(filtros_limpios["categoria"])

            if filtros_limpios.get("stock_bajo"):
                where_conditions.append("stock_actual <= stock_minimo")

            where_clause = " AND ".join(where_conditions)

            # Validar orden
            orden_permitido = self._validar_orden(orden)

            # Consulta de conteo
            query_count = (
                f"SELECT COUNT(*) as total FROM inventario WHERE {where_clause}"
            )
            cursor = self.db_connection.cursor(dictionary=True)
            cursor.execute(query_count, params)
            total = cursor.fetchone()["total"]

            # Consulta de datos
            query_data = f"""
                SELECT id, codigo, descripcion, categoria, stock_actual, 
                       stock_minimo, precio_unitario, ubicacion, fecha_creacion
                FROM inventario 
                WHERE {where_clause}
                ORDER BY {orden_permitido}
                LIMIT %s OFFSET %s
            """
            params.extend([limit, offset])
            cursor.execute(query_data, params)
            items = cursor.fetchall()
            cursor.close()

            return {
                "items": items,
                "total": total,
                "offset": offset,
                "limit": limit,
                "has_next": (offset + limit) < total,
                "has_prev": offset > 0,
            }

        except Exception as e:
            print(f"❌ Error en consulta paginada: {str(e)}")
            return {"items": [], "total": 0, "offset": offset, "limit": limit}

    @auth_required
    @permission_required("view_inventario")
    def buscar_productos(
        self, termino_busqueda: str, limite: int = 20
    ) -> List[Dict[str, Any]]:
        """Busca productos por código o descripción."""
        if not self.db_connection:
            return [
                {
                    "id": 1,
                    "codigo": "PROD001",
                    "descripcion": f"Resultado simulado para: {termino_busqueda}",
                }
            ]

        try:
            termino_limpio = self.data_sanitizer.sanitize_text(termino_busqueda).strip()
            if not termino_limpio:
                return []

            query = """
                SELECT id, codigo, descripcion, categoria, stock_actual, 
                       stock_minimo, precio_unitario, ubicacion
                FROM inventario 
                WHERE activo = 1 
                AND (codigo LIKE %s OR descripcion LIKE %s)
                ORDER BY 
                    CASE 
                        WHEN codigo = %s THEN 1
                        WHEN codigo LIKE %s THEN 2
                        WHEN descripcion LIKE %s THEN 3
                        ELSE 4
                    END,
                    codigo ASC
                LIMIT %s
            """

            termino_like = f"%{termino_limpio}%"
            termino_start = f"{termino_limpio}%"
            params = [
                termino_like,
                termino_like,
                termino_limpio,
                termino_start,
                termino_like,
                limite,
            ]

            cursor = self.db_connection.cursor(dictionary=True)
            cursor.execute(query, params)
            resultados = cursor.fetchall()
            cursor.close()

            return resultados

        except Exception as e:
            print(f"❌ Error en búsqueda: {str(e)}")
            return []

    @auth_required
    @permission_required("view_inventario")
    def obtener_productos_stock_bajo(self) -> List[Dict[str, Any]]:
        """Obtiene productos con stock por debajo del mínimo."""
        if not self.db_connection:
            return [
                {
                    "id": 1,
                    "codigo": "PROD001",
                    "descripcion": "Producto stock bajo",
                    "stock_actual": 2,
                    "stock_minimo": 5,
                }
            ]

        try:
            query = """
                SELECT id, codigo, descripcion, categoria, stock_actual, 
                       stock_minimo, ubicacion, fecha_modificacion
                FROM inventario 
                WHERE activo = 1 
                AND stock_actual <= stock_minimo
                ORDER BY (stock_actual - stock_minimo) ASC, codigo ASC
            """

            cursor = self.db_connection.cursor(dictionary=True)
            cursor.execute(query)
            resultados = cursor.fetchall()
            cursor.close()

            return resultados

        except Exception as e:
            print(f"❌ Error obteniendo productos con stock bajo: {str(e)}")
            return []

    @auth_required
    @permission_required("view_inventario")
    def obtener_estadisticas_inventario(self) -> Dict[str, Any]:
        """Obtiene estadísticas generales del inventario."""
        if not self.db_connection:
            return {
                "total_productos": 100,
                "total_valor": 15000.0,
                "productos_stock_bajo": 5,
                "productos_sin_stock": 2,
                "categorias": {"Herramientas": 30, "Materiales": 50, "Equipos": 20},
            }

        try:
            stats = {}

            # Total de productos
            cursor = self.db_connection.cursor(dictionary=True)
            cursor.execute("SELECT COUNT(*) as total FROM inventario WHERE activo = 1")
            stats["total_productos"] = cursor.fetchone()["total"]

            # Valor total del inventario
            cursor.execute("""
                SELECT SUM(stock_actual * precio_unitario) as valor_total 
                FROM inventario WHERE activo = 1
            """)
            result = cursor.fetchone()
            stats["total_valor"] = float(result["valor_total"] or 0)

            # Productos con stock bajo
            cursor.execute("""
                SELECT COUNT(*) as stock_bajo 
                FROM inventario 
                WHERE activo = 1 AND stock_actual <= stock_minimo
            """)
            stats["productos_stock_bajo"] = cursor.fetchone()["stock_bajo"]

            # Productos sin stock
            cursor.execute("""
                SELECT COUNT(*) as sin_stock 
                FROM inventario 
                WHERE activo = 1 AND stock_actual = 0
            """)
            stats["productos_sin_stock"] = cursor.fetchone()["sin_stock"]

            # Productos por categoría
            cursor.execute("""
                SELECT categoria, COUNT(*) as cantidad
                FROM inventario 
                WHERE activo = 1 AND categoria IS NOT NULL
                GROUP BY categoria
                ORDER BY cantidad DESC
            """)
            categorias = cursor.fetchall()
            stats["categorias"] = {
                cat["categoria"]: cat["cantidad"] for cat in categorias
            }

            cursor.close()
            return stats

        except Exception as e:
            print(f"❌ Error obteniendo estadísticas: {str(e)}")
            return {
                "total_productos": 0,
                "total_valor": 0.0,
                "productos_stock_bajo": 0,
                "productos_sin_stock": 0,
                "categorias": {},
            }

    @auth_required
    @permission_required("view_inventario")
    def obtener_productos_por_categoria(self, categoria: str) -> List[Dict[str, Any]]:
        """Obtiene productos de una categoría específica."""
        if not self.db_connection:
            return [
                {
                    "id": 1,
                    "codigo": "PROD001",
                    "descripcion": f"Producto de {categoria}",
                    "categoria": categoria,
                }
            ]

        try:
            categoria_limpia = self.data_sanitizer.sanitize_text(categoria)

            query = """
                SELECT id, codigo, descripcion, categoria, stock_actual, 
                       stock_minimo, precio_unitario, ubicacion
                FROM inventario 
                WHERE activo = 1 AND categoria = %s
                ORDER BY descripcion ASC
            """

            cursor = self.db_connection.cursor(dictionary=True)
            cursor.execute(query, (categoria_limpia,))
            resultados = cursor.fetchall()
            cursor.close()

            return resultados

        except Exception as e:
            print(f"❌ Error obteniendo productos por categoría: {str(e)}")
            return []

    @auth_required
    @permission_required("view_inventario")
    def generar_reporte_valorizado(self) -> List[Dict[str, Any]]:
        """Genera reporte valorizado del inventario."""
        if not self.db_connection:
            return [
                {
                    "codigo": "PROD001",
                    "descripcion": "Producto simulado",
                    "stock_actual": 10,
                    "precio_unitario": 100.0,
                    "valor_stock": 1000.0,
                }
            ]

        try:
            query = """
                SELECT 
                    codigo,
                    descripcion,
                    categoria,
                    stock_actual,
                    precio_unitario,
                    (stock_actual * precio_unitario) as valor_stock,
                    ubicacion
                FROM inventario 
                WHERE activo = 1 
                ORDER BY valor_stock DESC, codigo ASC
            """

            cursor = self.db_connection.cursor(dictionary=True)
            cursor.execute(query)
            resultados = cursor.fetchall()
            cursor.close()

            return resultados

        except Exception as e:
            print(f"❌ Error generando reporte valorizado: {str(e)}")
            return []

    def _validar_orden(self, orden: str) -> str:
        """Valida y limpia el parámetro de orden para evitar inyección SQL."""
        # Campos permitidos para ordenamiento
        campos_permitidos = [
            "codigo",
            "descripcion",
            "categoria",
            "stock_actual",
            "stock_minimo",
            "precio_unitario",
            "fecha_creacion",
            "fecha_modificacion",
        ]

        # Direcciones permitidas
        direcciones_permitidas = ["ASC", "DESC"]

        # Parsear orden
        partes = orden.strip().split()
        if len(partes) != 2:
            return "descripcion ASC"  # Default seguro

        campo, direccion = partes

        # Validar campo
        if campo not in campos_permitidos:
            campo = "descripcion"

        # Validar dirección
        if direccion.upper() not in direcciones_permitidas:
            direccion = "ASC"

        return f"{campo} {direccion.upper()}"

    @auth_required
    @permission_required("view_inventario")
    def obtener_productos_filtro_avanzado(
        self, filtros: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Aplica filtros avanzados para búsqueda de productos."""
        if not self.db_connection:
            return []

        try:
            filtros_limpios = self.data_sanitizer.sanitize_dict(filtros)

            where_conditions = ["activo = 1"]
            params = []

            # Filtro por rango de stock
            if filtros_limpios.get("stock_min"):
                where_conditions.append("stock_actual >= %s")
                params.append(int(filtros_limpios["stock_min"]))

            if filtros_limpios.get("stock_max"):
                where_conditions.append("stock_actual <= %s")
                params.append(int(filtros_limpios["stock_max"]))

            # Filtro por rango de precio
            if filtros_limpios.get("precio_min"):
                where_conditions.append("precio_unitario >= %s")
                params.append(float(filtros_limpios["precio_min"]))

            if filtros_limpios.get("precio_max"):
                where_conditions.append("precio_unitario <= %s")
                params.append(float(filtros_limpios["precio_max"]))

            # Filtro por ubicación
            if filtros_limpios.get("ubicacion"):
                where_conditions.append("ubicacion LIKE %s")
                params.append(f"%{filtros_limpios['ubicacion']}%")

            # Filtro por fecha de creación
            if filtros_limpios.get("fecha_desde"):
                where_conditions.append("DATE(fecha_creacion) >= %s")
                params.append(filtros_limpios["fecha_desde"])

            if filtros_limpios.get("fecha_hasta"):
                where_conditions.append("DATE(fecha_creacion) <= %s")
                params.append(filtros_limpios["fecha_hasta"])

            where_clause = " AND ".join(where_conditions)

            query = f"""
                SELECT id, codigo, descripcion, categoria, stock_actual, 
                       stock_minimo, precio_unitario, ubicacion, fecha_creacion
                FROM inventario 
                WHERE {where_clause}
                ORDER BY fecha_creacion DESC
            """

            cursor = self.db_connection.cursor(dictionary=True)
            cursor.execute(query, params)
            resultados = cursor.fetchall()
            cursor.close()

            return resultados

        except Exception as e:
            print(f"❌ Error en filtro avanzado: {str(e)}")
            return []
