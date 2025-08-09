"""
Submódulo de Movimientos - Inventario Rexus.app v2.0.0

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

# DataSanitizer unificado
try:
    from rexus.utils.unified_sanitizer import unified_sanitizer
    DataSanitizer = unified_sanitizer
except ImportError:
    class DataSanitizer:
        def sanitize_dict(self, data):
            return data if data else {}

        def sanitize_text(self, text):
            return str(text) if text else ""

        def sanitize_integer(self, value):
            return int(value) if value else 0


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
        self.sanitizer = DataSanitizer()

    @auth_required
    @permission_required("create_movimiento")
    def registrar_movimiento(
        self, datos_movimiento: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Registra un movimiento de inventario."""
        if not self.db_connection:
            print("⚠️ Sin conexión a BD - Modo simulación")
            return {"id": 1, "mensaje": "Movimiento registrado (simulación)"}

        try:
            # Sanitizar datos
            datos_limpios = self.sanitizer.sanitize_dict(datos_movimiento)

            # Validaciones básicas
            if not datos_limpios.get("producto_id"):
                raise ValueError("ID de producto requerido")

            if not datos_limpios.get("tipo_movimiento"):
                raise ValueError("Tipo de movimiento requerido")

            if datos_limpios["tipo_movimiento"] not in self.TIPOS_MOVIMIENTO:
                raise ValueError(
                    f"Tipo de movimiento inválido: {datos_limpios['tipo_movimiento']}"
                )

            # Validar cantidad
            cantidad = self.sanitizer.sanitize_integer(
                datos_limpios.get("cantidad", 0)
            )
            if cantidad <= 0:
                raise ValueError("La cantidad debe ser mayor a 0")

            # Obtener stock actual del producto
            stock_actual = self._obtener_stock_actual(datos_limpios["producto_id"])
            if stock_actual is None:
                raise ValueError("Producto no encontrado")

            # Calcular nuevo stock
            nuevo_stock = self._calcular_nuevo_stock(
                stock_actual, cantidad, datos_limpios["tipo_movimiento"]
            )

            if nuevo_stock < 0:
                raise ValueError(
                    f"Stock insuficiente. Stock actual: {stock_actual}, intentando retirar: {cantidad}"
                )

            # Preparar datos para inserción
            params = {
                "producto_id": datos_limpios["producto_id"],
                "tipo_movimiento": datos_limpios["tipo_movimiento"],
                "cantidad": cantidad,
                "stock_anterior": stock_actual,
                "stock_nuevo": nuevo_stock,
                "motivo": datos_limpios.get("motivo", "Sin especificar"),
                "usuario": datos_limpios.get("usuario", "Sistema"),
                "obra_id": datos_limpios.get("obra_id"),
                "referencia": datos_limpios.get("referencia", ""),
            }

            # Iniciar transacción
            self.db_connection.start_transaction()

            # Insertar movimiento
            movimiento_id = self._insertar_movimiento(params)

            # Actualizar stock del producto
            self._actualizar_stock_producto(datos_limpios["producto_id"], nuevo_stock)

            # Confirmar transacción
            self.db_connection.commit()

            return {
                "id": movimiento_id,
                "stock_anterior": stock_actual,
                "stock_nuevo": nuevo_stock,
                "mensaje": "Movimiento registrado exitosamente",
            }

        except Exception as e:
            if self.db_connection:
                self.db_connection.rollback()
            print(f"❌ Error registrando movimiento: {str(e)}")
            return None

    @auth_required
    @permission_required("view_movimientos")
    def obtener_movimientos_producto(
        self, producto_id: int, limite: int = 20
    ) -> List[Dict[str, Any]]:
        """Obtiene el historial de movimientos de un producto."""
        if not self.db_connection:
            return [
                {
                    "id": 1,
                    "tipo_movimiento": "ENTRADA",
                    "cantidad": 10,
                    "stock_anterior": 0,
                    "stock_nuevo": 10,
                    "fecha": datetime.now().isoformat(),
                    "motivo": "Simulación",
                }
            ]

        try:
            query = """
                SELECT id, tipo_movimiento, cantidad, stock_anterior, stock_nuevo,
                       motivo, usuario, obra_id, referencia, fecha_movimiento
                FROM movimientos_inventario 
                WHERE producto_id = %s 
                ORDER BY fecha_movimiento DESC
                LIMIT %s
            """

            cursor = self.db_connection.cursor(dictionary=True)
            cursor.execute(query, (producto_id, limite))
            resultados = cursor.fetchall()
            cursor.close()

            return resultados or []

        except Exception as e:
            print(f"❌ Error obteniendo movimientos: {str(e)}")
            return []

    @auth_required
    @permission_required("view_movimientos")
    def obtener_movimientos_obra(self, obra_id: int) -> List[Dict[str, Any]]:
        """Obtiene movimientos asociados a una obra específica."""
        if not self.db_connection:
            return []

        try:
            query = """
                SELECT m.id, m.tipo_movimiento, m.cantidad, m.motivo, 
                       m.fecha_movimiento, i.codigo, i.descripcion
                FROM movimientos_inventario m
                INNER JOIN inventario i ON m.producto_id = i.id
                WHERE m.obra_id = %s
                ORDER BY m.fecha_movimiento DESC
            """

            cursor = self.db_connection.cursor(dictionary=True)
            cursor.execute(query, (obra_id,))
            resultados = cursor.fetchall()
            cursor.close()

            return resultados or []

        except Exception as e:
            print(f"❌ Error obteniendo movimientos de obra: {str(e)}")
            return []

    @auth_required
    @permission_required("view_movimientos")
    def obtener_estadisticas_movimientos(
        self, fecha_inicio: str = None, fecha_fin: str = None
    ) -> Dict[str, Any]:
        """Obtiene estadísticas de movimientos en un período."""
        if not self.db_connection:
            return {
                "total_movimientos": 100,
                "por_tipo": {"ENTRADA": 60, "SALIDA": 40},
                "productos_mas_activos": [],
            }

        try:
            # Construir cláusula WHERE para fechas
            where_clause = "WHERE 1=1"
            params = []

            if fecha_inicio:
                where_clause += " AND DATE(fecha_movimiento) >= %s"
                params.append(fecha_inicio)

            if fecha_fin:
                where_clause += " AND DATE(fecha_movimiento) <= %s"
                params.append(fecha_fin)

            # Total de movimientos
            query_total = (
                f"SELECT COUNT(*) as total FROM movimientos_inventario {where_clause}"
            )
            cursor = self.db_connection.cursor(dictionary=True)
            cursor.execute(query_total, params)
            total_movimientos = cursor.fetchone()["total"]

            # Movimientos por tipo
            query_por_tipo = f"""
                SELECT tipo_movimiento, COUNT(*) as cantidad
                FROM movimientos_inventario {where_clause}
                GROUP BY tipo_movimiento
                ORDER BY cantidad DESC
            """
            cursor.execute(query_por_tipo, params)
            por_tipo = {
                row["tipo_movimiento"]: row["cantidad"] for row in cursor.fetchall()
            }

            # Productos más activos
            query_productos = f"""
                SELECT i.codigo, i.descripcion, COUNT(*) as movimientos
                FROM movimientos_inventario m
                INNER JOIN inventario i ON m.producto_id = i.id
                {where_clause}
                GROUP BY m.producto_id, i.codigo, i.descripcion
                ORDER BY movimientos DESC
                LIMIT 10
            """
            cursor.execute(query_productos, params)
            productos_activos = cursor.fetchall()
            cursor.close()

            return {
                "total_movimientos": total_movimientos,
                "por_tipo": por_tipo,
                "productos_mas_activos": productos_activos,
            }

        except Exception as e:
            print(f"❌ Error obteniendo estadísticas: {str(e)}")
            return {"total_movimientos": 0, "por_tipo": {}, "productos_mas_activos": []}

    def _obtener_stock_actual(self, producto_id: int) -> Optional[int]:
        """Obtiene el stock actual de un producto."""
        try:
            query = "SELECT stock_actual FROM inventario WHERE id = %s AND activo = 1"
            cursor = self.db_connection.cursor()
            cursor.execute(query, (producto_id,))
            resultado = cursor.fetchone()
            cursor.close()

            return resultado[0] if resultado else None

        except Exception as e:
            print(f"❌ Error obteniendo stock: {str(e)}")
            return None

    def _calcular_nuevo_stock(
        self, stock_actual: int, cantidad: int, tipo_movimiento: str
    ) -> int:
        """Calcula el nuevo stock basado en el tipo de movimiento."""
        if tipo_movimiento in ["ENTRADA", "DEVOLUCION"]:
            return stock_actual + cantidad
        elif tipo_movimiento in ["SALIDA", "MERMA", "TRANSFERENCIA"]:
            return stock_actual - cantidad
        elif tipo_movimiento == "AJUSTE":
            # Para ajustes, la cantidad es el nuevo stock
            return cantidad
        else:
            raise ValueError(f"Tipo de movimiento no reconocido: {tipo_movimiento}")

    def _insertar_movimiento(self, params: Dict[str, Any]) -> int:
        """Inserta un registro de movimiento."""
        query = """
            INSERT INTO movimientos_inventario (
                producto_id, tipo_movimiento, cantidad, stock_anterior, stock_nuevo,
                motivo, usuario, obra_id, referencia, fecha_movimiento
            ) VALUES (
                %(producto_id)s, %(tipo_movimiento)s, %(cantidad)s, %(stock_anterior)s, %(stock_nuevo)s,
                %(motivo)s, %(usuario)s, %(obra_id)s, %(referencia)s, CURRENT_TIMESTAMP
            )
        """

        cursor = self.db_connection.cursor()
        cursor.execute(query, params)
        movimiento_id = cursor.lastrowid
        cursor.close()

        return movimiento_id

    def _actualizar_stock_producto(self, producto_id: int, nuevo_stock: int) -> None:
        """Actualiza el stock de un producto."""
        query = """
            UPDATE inventario 
            SET stock_actual = %s, fecha_modificacion = CURRENT_TIMESTAMP
            WHERE id = %s
        """

        cursor = self.db_connection.cursor()
        cursor.execute(query, (nuevo_stock, producto_id))
        cursor.close()

    @auth_required
    @permission_required("create_movimiento")
    def entrada_stock(
        self, producto_id: int, cantidad: int, motivo: str = "Entrada manual"
    ) -> Optional[Dict[str, Any]]:
        """Atajo para registrar entrada de stock."""
        return self.registrar_movimiento(
            {
                "producto_id": producto_id,
                "tipo_movimiento": "ENTRADA",
                "cantidad": cantidad,
                "motivo": motivo,
            }
        )

    @auth_required
    @permission_required("create_movimiento")
    def salida_stock(
        self,
        producto_id: int,
        cantidad: int,
        obra_id: int = None,
        motivo: str = "Salida manual",
    ) -> Optional[Dict[str, Any]]:
        """Atajo para registrar salida de stock."""
        return self.registrar_movimiento(
            {
                "producto_id": producto_id,
                "tipo_movimiento": "SALIDA",
                "cantidad": cantidad,
                "obra_id": obra_id,
                "motivo": motivo,
            }
        )

    def validar_datos_movimiento(self, datos: Dict[str, Any]) -> List[str]:
        """Valida los datos de un movimiento y retorna lista de errores."""
        errores = []

        # Producto ID requerido
        if not datos.get("producto_id"):
            errores.append("ID de producto es requerido")

        # Tipo de movimiento válido
        if not datos.get("tipo_movimiento"):
            errores.append("Tipo de movimiento es requerido")
        elif datos["tipo_movimiento"] not in self.TIPOS_MOVIMIENTO:
            errores.append(
                f"Tipo de movimiento inválido. Tipos válidos: {list(self.TIPOS_MOVIMIENTO.keys())}"
            )

        # Cantidad válida
        if "cantidad" not in datos:
            errores.append("Cantidad es requerida")
        else:
            try:
                cantidad = int(datos["cantidad"])
                if cantidad <= 0:
                    errores.append("La cantidad debe ser mayor a 0")
            except (ValueError, TypeError):
                errores.append("La cantidad debe ser un número entero")

        return errores
