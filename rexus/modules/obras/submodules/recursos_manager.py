"""
Submódulo de Recursos de Obras - Rexus.app

Gestiona asignación y control de recursos en obras.
Responsabilidades:
- Asignación de materiales a obras
- Control de inventario por obra
- Gestión de personal y equipos
- Seguimiento de costos de recursos
"""


import logging
logger = logging.getLogger(__name__)

import sqlite3
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


class RecursosManager:
    """Gestor especializado para recursos de obras."""

    def __init__(self, db_connection=None):
        """Inicializa el gestor de recursos."""
        self.db_connection = db_connection
        self.sql_manager = SQLQueryManager()
        self.sanitizer = DataSanitizer()
        self.sql_path = "scripts/sql/obras/recursos"
    def asignar_material_obra(
        self,
        obra_id: int,
        material_id: int,
        cantidad: int,
        tipo_material: str = "vidrio",
    ) -> bool:
        """Asigna material específico a una obra."""
        if not self.db_connection or not obra_id or not material_id:
            return False

        try:
            # Sanitizar datos
            obra_id_sanitizado = self.sanitizer.sanitize_integer(
                obra_id, min_val=1
            )
            material_id_sanitizado = self.sanitizer.sanitize_integer(
                material_id, min_val=1
            )
            cantidad_sanitizada = self.sanitizer.sanitize_integer(
                cantidad, min_val=1
            )
            tipo_sanitizado = sanitize_string(tipo_material)

            # Validar disponibilidad del material
            if not self._validar_disponibilidad_material(
                material_id_sanitizado, cantidad_sanitizada, tipo_sanitizado
            ):
                raise ValueError("Material no disponible en la cantidad solicitada")

            cursor = self.db_connection.cursor()

            # Usar SQL externo para asignación
            query = self.sql_manager.get_query(self.sql_path, "asignar_material_obra")
            cursor.execute(
                query,
                {
                    "obra_id": obra_id_sanitizado,
                    "material_id": material_id_sanitizado,
                    "cantidad": cantidad_sanitizada,
                    "tipo_material": tipo_sanitizado,
                    "fecha_asignacion": datetime.now(),
                },
            )

            # Actualizar stock del material
            self._actualizar_stock_material(
                material_id_sanitizado, cantidad_sanitizada, tipo_sanitizado, cursor
            )

            self.db_connection.commit()
            return True

        except Exception as e:
            if self.db_connection:
                self.db_connection.rollback()
            logger.info(f"Error asignando material a obra: {str(e)}")
            return False
    def obtener_materiales_obra(self, obra_id: int) -> List[Dict[str, Any]]:
        """Obtiene todos los materiales asignados a una obra."""
        if not self.db_connection or not obra_id:
            return []

        try:
            obra_id_sanitizado = self.sanitizer.sanitize_integer(
                obra_id, min_val=1
            )

            cursor = self.db_connection.cursor()

            query = self.sql_manager.get_query(self.sql_path, "obtener_materiales_obra")
            cursor.execute(query, {"obra_id": obra_id_sanitizado})

            materiales = []
            columns = [column[0] for column in cursor.description]

            for row in cursor.fetchall():
                material = dict(zip(columns, row))
                # Agregar cálculos adicionales
                material["costo_total"] = self._calcular_costo_material(material)
                materiales.append(material)

            return materiales

        except Exception as e:
            logger.info(f"Error obteniendo materiales de obra: {str(e)}")
            return []
    def liberar_material_obra(
        self, obra_id: int, material_id: int, cantidad: int
    ) -> bool:
        """Libera material de una obra y lo devuelve al inventario."""
        if not self.db_connection or not obra_id or not material_id:
            return False

        try:
            cursor = self.db_connection.cursor()

            # Verificar que el material esté asignado
            if not self._verificar_material_asignado(obra_id, material_id):
                raise ValueError("El material no está asignado a esta obra")

            # Liberar material
            query = self.sql_manager.get_query(self.sql_path, "liberar_material_obra")
            cursor.execute(
                query,
                {"obra_id": obra_id, "material_id": material_id, "cantidad": cantidad},
            )

            # Devolver al inventario
            self._devolver_stock_material(material_id, cantidad, cursor)

            self.db_connection.commit()
            return True

        except Exception as e:
            if self.db_connection:
                self.db_connection.rollback()
            logger.info(f"Error liberando material: {str(e)}")
            return False
    def asignar_personal_obra(
        self, obra_id: int, personal_id: int, rol: str, fecha_inicio: datetime = None
    ) -> bool:
        """Asigna personal a una obra."""
        if not self.db_connection or not obra_id or not personal_id:
            return False

        try:
            cursor = self.db_connection.cursor()

            query = self.sql_manager.get_query(self.sql_path, "asignar_personal_obra")
            cursor.execute(
                query,
                {
                    "obra_id": obra_id,
                    "personal_id": personal_id,
                    "rol": sanitize_string(rol),
                    "fecha_asignacion": fecha_inicio or datetime.now(),
                },
            )

            self.db_connection.commit()
            return cursor.rowcount > 0

        except Exception as e:
            if self.db_connection:
                self.db_connection.rollback()
            logger.info(f"Error asignando personal: {str(e)}")
            return False
    def obtener_resumen_recursos(self, obra_id: int) -> Dict[str, Any]:
        """Obtiene resumen completo de recursos de una obra."""
        if not self.db_connection or not obra_id:
            return {}

        try:
            cursor = self.db_connection.cursor()
            resumen: Dict[str, Any] = {"obra_id": obra_id}

            # Resumen de materiales
            query_materiales = self.sql_manager.get_query(
                self.sql_path, "resumen_materiales_obra"
            )
            cursor.execute(query_materiales, {"obra_id": obra_id})
            result = cursor.fetchone()
            if result:
                resumen["total_materiales"] = result[0] or 0
                resumen["costo_total_materiales"] = result[1] or 0.0

            # Resumen de personal
            query_personal = self.sql_manager.get_query(
                self.sql_path, "resumen_personal_obra"
            )
            cursor.execute(query_personal, {"obra_id": obra_id})
            result = cursor.fetchone()
            if result:
                resumen["total_personal"] = result[0] or 0

            # Costo total estimado
            resumen["costo_total_estimado"] = self._calcular_costo_total_obra(obra_id)

            return resumen

        except Exception as e:
            logger.info(f"Error obteniendo resumen de recursos: {str(e)}")
            return {}

    def _validar_disponibilidad_material(
        self, material_id: int, cantidad: int, tipo_material: str
    ) -> bool:
        """Valida si hay stock suficiente del material."""
        if not self.db_connection:
            return False

        try:
            cursor = self.db_connection.cursor()

            # Determinar tabla según tipo de material
            tabla_material = self._validate_table_name(
                self._obtener_tabla_material(tipo_material)
            )

            # Usar consulta preparada sin f-string
            if tabla_material == "vidrios":
                query = "SELECT stock FROM vidrios WHERE id = %s AND activo = 1"
            elif tabla_material == "inventario":
                query = "SELECT cantidad_disponible FROM inventario WHERE id = %s AND activo = 1"
            else:
                return False

            cursor.execute(query, (material_id,))
            result = cursor.fetchone()

            if not result:
                return False

            stock_actual = result[0] or 0
            return stock_actual >= cantidad

        except Exception as e:
            logger.info(f"Error validando disponibilidad: {str(e)}")
            return False

    def _actualizar_stock_material(
        self, material_id: int, cantidad: int, tipo_material: str, cursor
    ) -> None:
        """Actualiza el stock del material."""
        try:
            tabla_material = self._validate_table_name(
                self._obtener_tabla_material(tipo_material)
            )

            # Usar consulta preparada sin f-string
            if tabla_material == "vidrios":
                query = "UPDATE vidrios SET stock = stock - %s, fecha_modificacion = GETDATE() WHERE id = %s"
            elif tabla_material == "inventario":
                query = "UPDATE inventario SET cantidad_disponible = cantidad_disponible - %s, fecha_modificacion = GETDATE() WHERE id = %s"
            else:
                return

            cursor.execute(query, (cantidad, material_id))

        except Exception as e:
            logger.info(f"Error actualizando stock: {str(e)}")

    def _devolver_stock_material(self,
material_id: int,
        cantidad: int,
        cursor) -> None:
        """Devuelve material al inventario."""
        try:
            # Por simplicidad, asumir que es vidrio
            query = """
                UPDATE vidrios
                SET stock = stock + %(cantidad)s,
                    fecha_modificacion = GETDATE()
                WHERE id = %(material_id)s
            """

            cursor.execute(query, {"material_id": material_id, "cantidad": cantidad})

        except Exception as e:
            logger.info(f"Error devolviendo stock: {str(e)}")

    def _verificar_material_asignado(self, obra_id: int, material_id: int) -> bool:
        """Verifica si un material está asignado a una obra."""
        if not self.db_connection:
            return False

        try:
            cursor = self.db_connection.cursor()

            query = """
                SELECT COUNT(*)
                FROM obra_materiales
                WHERE obra_id = %(obra_id)s
                  AND material_id = %(material_id)s
                  AND cantidad_asignada > 0
            """

            cursor.execute(query, {"obra_id": obra_id, "material_id": material_id})

            result = cursor.fetchone()
            return (result[0] if result else 0) > 0

        except (sqlite3.Error, AttributeError, TypeError) as e:
            # sqlite3.Error: errores de base de datos
            # AttributeError: cursor no válido
            # TypeError: parámetros incorrectos
            return False

    def _calcular_costo_material(self, material: Dict[str, Any]) -> float:
        """Calcula el costo total de un material."""
        try:
            cantidad = material.get("cantidad_asignada", 0)
            precio = material.get("precio", 0)
            return float(cantidad) * float(precio)
        except (ValueError, TypeError) as e:
            # ValueError: conversión a float falló
            # TypeError: tipos incompatibles para operaciones matemáticas
            return 0.0

    def _calcular_costo_total_obra(self, obra_id: int) -> float:
        """Calcula el costo total estimado de una obra."""
        if not self.db_connection:
            return 0.0

        try:
            cursor = self.db_connection.cursor()

            query = self.sql_manager.get_query(
                self.sql_path, "calcular_costo_total_obra"
            )
            cursor.execute(query, {"obra_id": obra_id})

            result = cursor.fetchone()
            return float(result[0]) if result and result[0] else 0.0

        except Exception as e:
            logger.info(f"Error calculando costo total: {str(e)}")
            return 0.0

    def _validate_table_name(self, table_name: str) -> str:
        """Valida nombre de tabla contra lista blanca."""
        import re

        if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", table_name):
            raise ValueError(f"Nombre de tabla inválido: {table_name}")

        tablas_permitidas = {
            "vidrios",
            "inventario",
            "obra_materiales",
            "obra_personal",
            "personal",
        }
        if table_name not in tablas_permitidas:
            raise ValueError(f"Tabla no permitida: {table_name}")
        return table_name

    def _obtener_tabla_material(self, tipo_material: str) -> str:
        """Obtiene el nombre de tabla según el tipo de material."""
        tablas_material = {
            "vidrio": "vidrios",
            "herraje": "herrajes",
            "accesorio": "accesorios",
            "material": "materiales",
        }

        tabla = tablas_material.get(tipo_material.lower(), "vidrios")
        return self._validate_table_name(tabla)
