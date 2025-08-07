"""
Submódulo de Obras Vidrios - Rexus.app

Gestiona asignaciones de vidrios a obras y pedidos por obra.
Responsabilidades:
- Asignar vidrios a obras específicas
- Crear y gestionar pedidos de vidrios por obra
- Seguimiento de consumo por proyecto
"""

from typing import Any, Dict, List, Optional

# Imports de seguridad unificados
from rexus.core.auth_decorators import auth_required, permission_required

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
            script_name = f"{path.replace('scripts/sql/', '')}/{filename}"
            return self.sql_loader.load_script(script_name)


# DataSanitizer unificado
try:
    from rexus.utils.data_sanitizer import DataSanitizer
except ImportError:

    class DataSanitizer:
        def sanitize_string(self, text, max_length=None):
            return str(text) if text else ""

        def sanitize_integer(self, value, min_val=None, max_val=None):
            return int(value) if value else 0

        def sanitize_numeric(self, value, min_val=None, max_val=None):
            return float(value) if value else 0.0


class ObrasManager:
    """Gestor especializado para vidrios en obras."""

    def __init__(self, db_connection=None):
        """Inicializa el gestor de vidrios por obra."""
        self.db_connection = db_connection
        self.sql_manager = SQLQueryManager()
        self.data_sanitizer = DataSanitizer()
        self.sql_path = "scripts/sql/vidrios/obras"

    def _validate_table_name(self, table_name: str) -> str:
        """Valida nombre de tabla contra lista blanca."""
        import re

        if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", table_name):
            raise ValueError(f"Nombre de tabla inválido: {table_name}")

        tablas_permitidas = {"vidrios_obra", "pedidos_vidrios", "obras"}
        if table_name not in tablas_permitidas:
            raise ValueError(f"Tabla no permitida: {table_name}")
        return table_name

    @auth_required
    @permission_required("view_inventario")
    def obtener_vidrios_por_obra(self, obra_id: int) -> List[Dict[str, Any]]:
        """Obtiene todos los vidrios asignados a una obra específica."""
        if not self.db_connection or not obra_id:
            return []

        try:
            cursor = self.db_connection.cursor()

            # Sanitizar obra_id
            obra_id_sanitizado = self.data_sanitizer.sanitize_integer(
                obra_id, min_val=1
            )

            # Usar SQL externo para consulta
            query = self.sql_manager.get_query(
                self.sql_path, "obtener_vidrios_por_obra"
            )
            cursor.execute(query, {"obra_id": obra_id_sanitizado})

            vidrios = []
            columns = [column[0] for column in cursor.description]

            for row in cursor.fetchall():
                vidrio = dict(zip(columns, row))
                vidrios.append(vidrio)

            return vidrios

        except Exception as e:
            print(f"Error obteniendo vidrios por obra: {str(e)}")
            return []

    @auth_required
    @permission_required("add_inventario")
    def asignar_vidrio_obra(
        self, obra_id: int, vidrio_id: int, cantidad: int, observaciones: str = ""
    ) -> bool:
        """Asigna un vidrio específico a una obra."""
        if not self.db_connection or not obra_id or not vidrio_id:
            return False

        try:
            # Validar y sanitizar datos
            datos_asignacion = self._validar_datos_asignacion(
                {
                    "obra_id": obra_id,
                    "vidrio_id": vidrio_id,
                    "cantidad": cantidad,
                    "observaciones": observaciones,
                }
            )

            cursor = self.db_connection.cursor()

            # Verificar si ya existe asignación
            query_verificar = self.sql_manager.get_query(
                self.sql_path, "verificar_asignacion_existente"
            )
            cursor.execute(
                query_verificar,
                {
                    "obra_id": datos_asignacion["obra_id"],
                    "vidrio_id": datos_asignacion["vidrio_id"],
                },
            )

            if cursor.fetchone():
                # Actualizar cantidad existente
                query = self.sql_manager.get_query(
                    self.sql_path, "actualizar_asignacion_vidrio"
                )
                cursor.execute(query, datos_asignacion)
            else:
                # Crear nueva asignación
                query = self.sql_manager.get_query(
                    self.sql_path, "insertar_asignacion_vidrio"
                )
                cursor.execute(query, datos_asignacion)

            self.db_connection.commit()
            return True

        except Exception as e:
            if self.db_connection:
                self.db_connection.rollback()
            print(f"Error asignando vidrio a obra: {str(e)}")
            return False

    @auth_required
    @permission_required("add_inventario")
    def crear_pedido_obra(
        self, obra_id: int, proveedor: str, vidrios_lista: List[Dict[str, Any]]
    ) -> Optional[int]:
        """Crea un pedido de vidrios para una obra específica."""
        if not self.db_connection or not obra_id or not vidrios_lista:
            return None

        try:
            cursor = self.db_connection.cursor()

            # Validar datos del pedido
            datos_pedido = {
                "obra_id": self.data_sanitizer.sanitize_integer(obra_id, min_val=1),
                "proveedor": self.data_sanitizer.sanitize_string(proveedor),
                "estado": "PENDIENTE",
                "fecha_pedido": "GETDATE()",
                "total": 0.0,
            }

            # Calcular total del pedido
            total = 0.0
            for vidrio in vidrios_lista:
                cantidad = self.data_sanitizer.sanitize_integer(
                    vidrio.get("cantidad", 0)
                )
                precio = self.data_sanitizer.sanitize_numeric(vidrio.get("precio", 0))
                total += cantidad * precio

            datos_pedido["total"] = total

            # Crear pedido principal
            query_pedido = self.sql_manager.get_query(
                self.sql_path, "crear_pedido_obra"
            )
            cursor.execute(query_pedido, datos_pedido)

            # Obtener ID del pedido creado
            pedido_id = (
                cursor.lastrowid or cursor.execute("SELECT @@IDENTITY").fetchone()[0]
            )

            # Insertar detalles del pedido
            for vidrio in vidrios_lista:
                detalle = {
                    "pedido_id": pedido_id,
                    "vidrio_id": self.data_sanitizer.sanitize_integer(
                        vidrio.get("vidrio_id", 0)
                    ),
                    "cantidad": self.data_sanitizer.sanitize_integer(
                        vidrio.get("cantidad", 0)
                    ),
                    "precio_unitario": self.data_sanitizer.sanitize_numeric(
                        vidrio.get("precio", 0)
                    ),
                    "subtotal": self.data_sanitizer.sanitize_integer(
                        vidrio.get("cantidad", 0)
                    )
                    * self.data_sanitizer.sanitize_numeric(vidrio.get("precio", 0)),
                }

                query_detalle = self.sql_manager.get_query(
                    self.sql_path, "insertar_detalle_pedido"
                )
                cursor.execute(query_detalle, detalle)

            self.db_connection.commit()
            return pedido_id

        except Exception as e:
            if self.db_connection:
                self.db_connection.rollback()
            print(f"Error creando pedido de obra: {str(e)}")
            return None

    @auth_required
    @permission_required("view_inventario")
    def obtener_pedidos_obra(self, obra_id: int) -> List[Dict[str, Any]]:
        """Obtiene todos los pedidos de una obra específica."""
        if not self.db_connection or not obra_id:
            return []

        try:
            cursor = self.db_connection.cursor()

            obra_id_sanitizado = self.data_sanitizer.sanitize_integer(
                obra_id, min_val=1
            )

            query = self.sql_manager.get_query(self.sql_path, "obtener_pedidos_obra")
            cursor.execute(query, {"obra_id": obra_id_sanitizado})

            pedidos = []
            columns = [column[0] for column in cursor.description]

            for row in cursor.fetchall():
                pedido = dict(zip(columns, row))
                pedidos.append(pedido)

            return pedidos

        except Exception as e:
            print(f"Error obteniendo pedidos de obra: {str(e)}")
            return []

    @auth_required
    @permission_required("change_inventario")
    def actualizar_estado_pedido(self, pedido_id: int, nuevo_estado: str) -> bool:
        """Actualiza el estado de un pedido de vidrios."""
        if not self.db_connection or not pedido_id:
            return False

        try:
            # Validar estado
            estados_validos = [
                "PENDIENTE",
                "CONFIRMADO",
                "EN_TRANSITO",
                "ENTREGADO",
                "CANCELADO",
            ]
            estado_sanitizado = self.data_sanitizer.sanitize_string(
                nuevo_estado
            ).upper()

            if estado_sanitizado not in estados_validos:
                raise ValueError(f"Estado no válido: {nuevo_estado}")

            cursor = self.db_connection.cursor()

            query = self.sql_manager.get_query(
                self.sql_path, "actualizar_estado_pedido"
            )
            cursor.execute(
                query,
                {
                    "pedido_id": self.data_sanitizer.sanitize_integer(pedido_id),
                    "estado": estado_sanitizado,
                },
            )

            self.db_connection.commit()
            return cursor.rowcount > 0

        except Exception as e:
            if self.db_connection:
                self.db_connection.rollback()
            print(f"Error actualizando estado de pedido: {str(e)}")
            return False

    def _validar_datos_asignacion(self, datos: Dict[str, Any]) -> Dict[str, Any]:
        """Valida y sanitiza datos de asignación de vidrio a obra."""
        # Campos requeridos
        campos_requeridos = ["obra_id", "vidrio_id", "cantidad"]
        for campo in campos_requeridos:
            if campo not in datos or datos[campo] is None:
                raise ValueError(f"Campo requerido faltante: {campo}")

        # Sanitizar datos
        datos_sanitizados = {}

        datos_sanitizados["obra_id"] = self.data_sanitizer.sanitize_integer(
            datos["obra_id"], min_val=1
        )
        datos_sanitizados["vidrio_id"] = self.data_sanitizer.sanitize_integer(
            datos["vidrio_id"], min_val=1
        )
        datos_sanitizados["cantidad"] = self.data_sanitizer.sanitize_integer(
            datos["cantidad"], min_val=1
        )
        datos_sanitizados["observaciones"] = self.data_sanitizer.sanitize_string(
            datos.get("observaciones", "")
        )

        # Validaciones específicas
        if datos_sanitizados["cantidad"] <= 0:
            raise ValueError("La cantidad debe ser mayor a 0")

        return datos_sanitizados

    @auth_required
    @permission_required("view_inventario")
    def obtener_resumen_obra(self, obra_id: int) -> Dict[str, Any]:
        """Obtiene resumen de vidrios y pedidos de una obra."""
        if not self.db_connection or not obra_id:
            return {}

        try:
            obra_id_sanitizado = self.data_sanitizer.sanitize_integer(
                obra_id, min_val=1
            )

            # Obtener estadísticas de la obra
            resumen = {
                "obra_id": obra_id_sanitizado,
                "total_vidrios_asignados": 0,
                "total_pedidos": 0,
                "total_valor_pedidos": 0.0,
                "vidrios_por_tipo": {},
                "pedidos_por_estado": {},
            }

            cursor = self.db_connection.cursor()

            # Total vidrios asignados
            query_vidrios = self.sql_manager.get_query(
                self.sql_path, "contar_vidrios_obra"
            )
            cursor.execute(query_vidrios, {"obra_id": obra_id_sanitizado})
            result = cursor.fetchone()
            if result:
                resumen["total_vidrios_asignados"] = result[0] or 0

            # Total pedidos y valor
            query_pedidos = self.sql_manager.get_query(
                self.sql_path, "resumen_pedidos_obra"
            )
            cursor.execute(query_pedidos, {"obra_id": obra_id_sanitizado})
            result = cursor.fetchone()
            if result:
                resumen["total_pedidos"] = result[0] or 0
                resumen["total_valor_pedidos"] = result[1] or 0.0

            return resumen

        except Exception as e:
            print(f"Error obteniendo resumen de obra: {str(e)}")
            return {}

    @auth_required
    @permission_required("view_obras")
    def obtener_vidrios_obra(self, obra_id: int) -> List[Dict[str, Any]]:
        """Obtiene todos los vidrios asignados a una obra específica."""
        if not self.db_connection or not obra_id:
            return []

        try:
            obra_id_sanitizado = self.data_sanitizer.sanitize_integer(
                obra_id, min_val=1
            )

            cursor = self.db_connection.cursor()

            # Query para obtener vidrios de la obra
            query = """
                SELECT v.id, v.codigo, v.tipo, v.descripcion, 
                       ov.cantidad_asignada, ov.fecha_asignacion,
                       v.precio, (v.precio * ov.cantidad_asignada) as subtotal
                FROM vidrios v
                INNER JOIN obras_vidrios ov ON v.id = ov.vidrio_id
                WHERE ov.obra_id = %(obra_id)s 
                  AND v.activo = 1
                ORDER BY ov.fecha_asignacion DESC
            """

            cursor.execute(query, {"obra_id": obra_id_sanitizado})

            vidrios = []
            columns = [column[0] for column in cursor.description]

            for row in cursor.fetchall():
                vidrio = dict(zip(columns, row))
                vidrios.append(vidrio)

            return vidrios

        except Exception as e:
            print(f"Error obteniendo vidrios de obra: {str(e)}")
            return []
