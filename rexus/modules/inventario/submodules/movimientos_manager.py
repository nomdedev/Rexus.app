"""
Submódulo de Movimientos - Inventario Rexus.app

Gestiona todos los movimientos de stock (entradas, salidas, transferencias).
Responsabilidades:
- Registrar movimientos de stock
- Validar operaciones de stock
- Generar reportes de movimientos
- Auditoría de cambios
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

# Imports de seguridad unificados
from rexus.core.auth_decorators import auth_required, permission_required
from rexus.utils.unified_sanitizer import unified_sanitizer, sanitize_string

# SQLQueryManager unificado
try:
    from rexus.core.sql_query_manager import SQLQueryManager
except ImportError:
    # Fallback al script loader
    from rexus.utils.sql_script_loader import sql_script_loader

    class SQLQueryManager:
        def __init__(self):
            self.sql_loader = sql_script_loader

        def get_query(self, path, filename):
            # Construir nombre del script sin extensión
            script_name = filename.replace(".sql", "")
            return self.sql_loader(script_name)

        def execute_query(self, query, params=None):
            # Placeholder para compatibilidad
            return None

# Importar utilidades de sanitización
from rexus.utils.unified_sanitizer import unified_sanitizer, sanitize_string


class MovimientosManager:
    """Gestor especializado para movimientos de inventario."""

    # Tipos de movimiento permitidos
    TIPOS_MOVIMIENTO = {
        "ENTRADA": "Entrada de Stock",
        "SALIDA": "Salida de Stock",
        "TRANSFERENCIA": "Transferencia entre ubicaciones",
        "AJUSTE": "Ajuste de inventario",
        "DEVOLUCION": "Devolución",
        "MERMA": "Merma/Pérdida",
    }

    def __init__(self, db_connection=None):
        """Inicializa el gestor de movimientos."""
        self.db_connection = db_connection
        self.sql_manager = SQLQueryManager()
        self.sanitizer = unified_sanitizer
        self.sql_path = "scripts/sql/inventario/movimientos"

    @auth_required
    @permission_required("create_movimiento")
    def registrar_movimiento(
        self,
        producto_id: int,
        tipo_movimiento: str,
        cantidad: float,
        observaciones: str = "",
        obra_id: Optional[int] = None,
        usuario: str = "SISTEMA",
    ) -> bool:
        """Registra un movimiento de inventario con validaciones."""
        if not self.db_connection:
            raise Exception("No hay conexión a la base de datos")

        try:
            # Validar tipo de movimiento
            if tipo_movimiento not in self.TIPOS_MOVIMIENTO:
                raise ValueError(f"Tipo de movimiento inválido: {tipo_movimiento}")

            # Validar cantidad
            if cantidad == 0:
                raise ValueError("La cantidad no puede ser cero")

            # Obtener stock actual
            stock_actual = self._obtener_stock_actual(producto_id)
            if stock_actual is None:
                raise ValueError(f"Producto {producto_id} no encontrado")

            # Validar stock para salidas
            if tipo_movimiento in ["SALIDA", "TRANSFERENCIA"] and \
                cantidad > 0:
                if stock_actual < cantidad:
                    raise ValueError(
                        f"Stock insuficiente. Disponible: {stock_actual}, Solicitado: {cantidad}"
                    )

            cursor = self.db_connection.cursor()

            # Calcular nuevo stock
            factor = (
                -1 if tipo_movimiento in ["SALIDA", "TRANSFERENCIA", "MERMA"] else 1
            )
            cantidad_real = cantidad * factor
            nuevo_stock = stock_actual + cantidad_real

            # Usar SQL externo para insertar movimiento
            try:
                query_movimiento = self.sql_manager.get_query(self.sql_path, "insertar_movimiento")
                if query_movimiento:
                    cursor.execute(query_movimiento, (
                        producto_id,
                        tipo_movimiento,
                        cantidad_real,
                        stock_actual,
                        nuevo_stock,
                        sanitize_string(observaciones),
                        obra_id,
                        usuario,
                    ))
                else:
                    # Fallback seguro con query parametrizada
                    cursor.execute(
                        """INSERT INTO movimientos_inventario (
                            producto_id, tipo_movimiento, cantidad, stock_anterior,
                            stock_nuevo, observaciones, obra_id, usuario, fecha_movimiento
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, GETDATE())""",
                        (
                            producto_id,
                            tipo_movimiento,
                            cantidad_real,
                            stock_actual,
                            nuevo_stock,
                            sanitize_string(observaciones),
                            obra_id,
                            usuario,
                        ),
                    )
            except Exception:
                # Fallback final con query parametrizada
                cursor.execute(
                    """INSERT INTO movimientos_inventario (
                        producto_id, tipo_movimiento, cantidad, stock_anterior,
                        stock_nuevo, observaciones, obra_id, usuario, fecha_movimiento
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, GETDATE())""",
                    (
                        producto_id,
                        tipo_movimiento,
                        cantidad_real,
                        stock_actual,
                        nuevo_stock,
                        sanitize_string(observaciones),
                        obra_id,
                        usuario,
                    ),
                )

            # Usar SQL externo para actualizar stock
            try:
                query_stock = self.sql_manager.get_query(self.sql_path, "actualizar_stock_producto")
                if query_stock:
                    cursor.execute(query_stock, (nuevo_stock, producto_id))
                else:
                    # Fallback seguro con query parametrizada
                    cursor.execute(
                        "UPDATE inventario SET stock_actual = ?, fecha_modificacion = GETDATE() WHERE id = ?",
                        (nuevo_stock, producto_id)
                    )
            except Exception:
                # Fallback final con query parametrizada
                cursor.execute(
                    "UPDATE inventario SET stock_actual = ?, fecha_modificacion = GETDATE() WHERE id = ?",
                    (nuevo_stock, producto_id)
                )

            self.db_connection.commit()
            return True

        except Exception as e:
            self.db_connection.rollback()
            raise Exception(f"Error registrando movimiento: {str(e)}")

    @auth_required
    @permission_required("view_movimientos")
    def obtener_movimientos(
        self,
        producto_id: Optional[int] = None,
        tipo_movimiento: Optional[str] = None,
        fecha_desde: Optional[datetime] = None,
        fecha_hasta: Optional[datetime] = None,
        limite: int = 100,
    ) -> List[Dict[str, Any]]:
        """Obtiene movimientos con filtros opcionales."""
        if not self.db_connection:
            return []

        try:
            cursor = self.db_connection.cursor()

            # Construir query base
            query = """
                SELECT
                    m.id, m.producto_id, m.tipo_movimiento, m.cantidad,
                    m.stock_anterior, m.stock_nuevo, m.observaciones,
                    m.obra_id, m.usuario, m.fecha_movimiento,
                    p.codigo, p.descripcion
                FROM movimientos_inventario m
                INNER JOIN inventario p ON m.producto_id = p.id
                WHERE 1=1
            """

            params = []

            # Aplicar filtros
            if producto_id:
                query += " AND m.producto_id = ?"
                params.append(producto_id)

            if tipo_movimiento:
                query += " AND m.tipo_movimiento = ?"
                params.append(tipo_movimiento)

            if fecha_desde:
                query += " AND m.fecha_movimiento >= ?"
                params.append(fecha_desde)

            if fecha_hasta:
                query += " AND m.fecha_movimiento <= ?"
                params.append(fecha_hasta)

            query += " ORDER BY m.fecha_movimiento DESC"

            if limite > 0:
                query += f" OFFSET 0 ROWS FETCH NEXT {limite} ROWS ONLY"

            cursor.execute(query, params)
            columns = [column[0] for column in cursor.description]

            resultados = []
            for row in cursor.fetchall():
                resultados.append(dict(zip(columns, row)))

            return resultados

        except Exception as e:
            raise Exception(f"Error obteniendo movimientos: {str(e)}")

    @auth_required
    @permission_required("view_reportes")
    def generar_reporte_movimientos(
        self, filtros: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Genera reporte estadístico de movimientos."""
        if not self.db_connection:
            return {}

        try:
            cursor = self.db_connection.cursor()

            # Query para estadísticas generales
            cursor.execute("""
                SELECT
                    tipo_movimiento,
                    COUNT(*) as total_movimientos,
                    SUM(ABS(cantidad)) as cantidad_total,
                    AVG(ABS(cantidad)) as cantidad_promedio
                FROM movimientos_inventario
                WHERE fecha_movimiento >= DATEADD(MONTH, -1, GETDATE())
                GROUP BY tipo_movimiento
            """)

            estadisticas = {}
            for row in cursor.fetchall():
                tipo, total, cantidad_total, promedio = row
                estadisticas[tipo] = {
                    "total_movimientos": total,
                    "cantidad_total": float(cantidad_total) if cantidad_total else 0,
                    "cantidad_promedio": float(promedio) if promedio else 0,
                }

            # Productos con más movimientos
            cursor.execute("""
                SELECT TOP 10
                    p.codigo, p.descripcion,
                    COUNT(m.id) as total_movimientos
                FROM inventario p
                INNER JOIN movimientos_inventario m ON p.id = m.producto_id
                WHERE m.fecha_movimiento >= DATEADD(MONTH, -1, GETDATE())
                GROUP BY p.id, p.codigo, p.descripcion
                ORDER BY COUNT(m.id) DESC
            """)

            productos_activos = []
            for row in cursor.fetchall():
                productos_activos.append(
                    {
                        "codigo": row[0],
                        "descripcion": row[1],
                        "total_movimientos": row[2],
                    }
                )

            return {
                "estadisticas_por_tipo": estadisticas,
                "productos_mas_activos": productos_activos,
                "fecha_generacion": datetime.now().isoformat(),
            }

        except Exception as e:
            raise Exception(f"Error generando reporte: {str(e)}")

    def _obtener_stock_actual(self, producto_id: int) -> Optional[float]:
        """Obtiene el stock actual de un producto."""
        if not self.db_connection:
            return None

        try:
            cursor = self.db_connection.cursor()
            cursor.execute(
                "SELECT stock_actual FROM inventario WHERE id = ?", (producto_id,)
            )

            row = cursor.fetchone()
            return float(row[0]) if row else None

        except Exception:
            return None

    @auth_required
    @permission_required("view_stock_bajo")
    def obtener_productos_stock_bajo(self) -> List[Dict[str, Any]]:
        """Obtiene productos con stock por debajo del mínimo."""
        if not self.db_connection:
            return []

        try:
            cursor = self.db_connection.cursor()

            cursor.execute("""
                SELECT
                    id, codigo, descripcion, categoria,
                    stock_actual, stock_minimo,
                    (stock_minimo - stock_actual) as faltante
                FROM inventario
                WHERE stock_actual <= stock_minimo
                    AND activo = 1
                ORDER BY (stock_minimo - stock_actual) DESC
            """)

            columns = [column[0] for column in cursor.description]

            resultados = []
            for row in cursor.fetchall():
                producto = dict(zip(columns, row))
                producto["estado"] = (
                    "CRÍTICO" if producto["stock_actual"] == 0 else "BAJO"
                )
                resultados.append(producto)

            return resultados

        except Exception as e:
            raise Exception(f"Error obteniendo productos con stock bajo: {str(e)}")
