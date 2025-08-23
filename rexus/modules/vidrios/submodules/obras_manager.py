"""
Submódulo de Obras Vidrios - Rexus.app

Gestiona asignaciones de vidrios a obras y pedidos por obra.
Responsabilidades:
- Asignar vidrios a obras específicas
- Crear y gestionar pedidos de vidrios por obra
- Seguimiento de consumo por proyecto
"""

            from rexus.utils.unified_sanitizer import unified_sanitizer, sanitize_string

# Sistema de logging centralizado
from rexus.utils.app_logger import get_logger
logger = get_logger()

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
            script_name = f
            return self.sql_loader.load_script(script_name)


# DataSanitizer unificado
try:
    from rexus.utils.unified_sanitizer import unified_sanitizer
    DataSanitizer = unified_sanitizer
except ImportError:
    class DataSanitizer:
        def sanitize_dict(self, data):
            return data if data else {}

        def sanitize_string(self, text):
            return str(text) if text else ""

        def sanitize_integer(self, value):
            return int(value) if value else 0

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
        self.sanitizer = DataSanitizer()
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
    def obtener_vidrios_por_obra(self, obra_id: int) -> List[Dict[str, Any]]:
        """Obtiene todos los vidrios asignados a una obra específica."""
        if not self.db_connection or not obra_id:
            return []

        try:
            cursor = self.db_connection.cursor()

            # Sanitizar obra_id
            obra_id_sanitizado = self.sanitizer.sanitize_integer(
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

        except Exception as e:                raise ValueError(f"Estado no válido: {nuevo_estado}")

            cursor = self.db_connection.cursor()

            query = self.sql_manager.get_query(
                self.sql_path, "actualizar_estado_pedido"
            )
            cursor.execute(
                query,
                {
                    "pedido_id": self.sanitizer.sanitize_integer(pedido_id),
                    "estado": estado_sanitizado,
                },
            )

            self.db_connection.commit()
            return cursor.rowcount > 0

        except Exception as e:
            if self.db_connection:
                self.db_connection.rollback()
                        return {}
    def obtener_vidrios_obra(self, obra_id: int) -> List[Dict[str, Any]]:
        """Obtiene todos los vidrios asignados a una obra específica."""
        if not self.db_connection or not obra_id:
            return []

        try:
            obra_id_sanitizado = self.sanitizer.sanitize_integer(
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
            return []
