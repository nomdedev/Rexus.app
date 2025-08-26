"""
Submódulo de Proyectos de Obras - Rexus.app

Gestiona CRUD de proyectos y obras principales.
Responsabilidades:
- Crear, leer, actualizar, eliminar proyectos de obra
- Gestión de estado y fases de proyecto
- Validaciones específicas de obras
- Control de fechas y presupuestos
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

        def sanitize_dict(self, data_dict):
            return dict(data_dict) if data_dict else {}


class ProyectosManager:
    """Gestor especializado para proyectos de obras."""

    def __init__(self, db_connection=None):
        """Inicializa el gestor de proyectos."""
        self.db_connection = db_connection
        self.sql_manager = SQLQueryManager()
        self.sanitizer = DataSanitizer()
        self.sql_path = "scripts/sql/obras/proyectos"

    def _validate_table_name(self, table_name: str) -> str:
        """Valida nombre de tabla contra lista blanca."""
        import re

        if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", table_name):
            raise ValueError(f"Nombre de tabla inválido: {table_name}")

        tablas_permitidas = {"obras", "detalles_obra", "fases_obra", "estados_obra"}
        if table_name not in tablas_permitidas:
            raise ValueError(f"Tabla no permitida: {table_name}")
        return table_name
    def obtener_obra_por_id(self, obra_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene una obra específica por ID."""
        if not self.db_connection or not obra_id:
            return None

        try:
            cursor = self.db_connection.cursor()

            # Usar SQL externo para consulta
            query = self.sql_manager.get_query(self.sql_path, "obtener_obra_por_id")
            cursor.execute(query, (obra_id,))

            row = cursor.fetchone()
            if not row:
                return None

            columns = [column[0] for column in cursor.description]
            obra = dict(zip(columns, row))

            # Agregar información adicional
            obra["detalles"] = self._obtener_detalles_obra(obra_id)
            obra["duracion_estimada"] = self._calcular_duracion_dias(obra)

            return obra

        except Exception as e:
            raise Exception(f"Error obteniendo obra: {str(e)}")
    def crear_obra(self, datos_obra: Dict[str, Any]) -> bool:
        """Crea un nuevo proyecto de obra con validaciones."""
        if not self.db_connection:
            return False

        try:
            # Validar y sanitizar datos
            datos_sanitizados = self._validar_datos_obra(datos_obra)

            cursor = self.db_connection.cursor()

            # Usar SQL externo para inserción
            query = self.sql_manager.get_query(self.sql_path, "insertar_obra")
            cursor.execute(
                query,
                (
                    datos_sanitizados.get("nombre"),
                    datos_sanitizados.get("descripcion"),
                    datos_sanitizados.get("cliente"),
                    datos_sanitizados.get("estado"),
                    datos_sanitizados.get("fecha_inicio"),
                    datos_sanitizados.get("fecha_fin_estimada"),
                    datos_sanitizados.get("presupuesto"),
                    datos_sanitizados.get("direccion"),
                    "",  # notas vacías por defecto
                ),
            )

            # Obtener ID de la obra recién creada
            obra_id = cursor.lastrowid

            # Crear fase inicial
            if obra_id:
                self._crear_fase_inicial(obra_id, cursor)

            self.db_connection.commit()
            return True

        except Exception as e:
            if self.db_connection:
                self.db_connection.rollback()
            logger.info(f"Error creando obra: {str(e)}")
            return False
    def actualizar_obra(self,
obra_id: int,
        datos_obra: Dict[str,
        Any]) -> bool:
        """Actualiza un proyecto de obra existente."""
        if not self.db_connection or not obra_id:
            return False

        try:
            # Validar y sanitizar datos
            datos_sanitizados = self._validar_datos_obra(datos_obra)
            datos_sanitizados["obra_id"] = obra_id

            cursor = self.db_connection.cursor()

            # Usar SQL externo para actualización
            query = self.sql_manager.get_query(self.sql_path, "actualizar_obra")
            cursor.execute(
                query,
                (
                    datos_sanitizados.get("nombre"),
                    datos_sanitizados.get("descripcion"),
                    datos_sanitizados.get("cliente"),
                    datos_sanitizados.get("estado"),
                    datos_sanitizados.get("fecha_inicio"),
                    datos_sanitizados.get("fecha_fin_estimada"),
                    None,  # fecha_fin_real
                    datos_sanitizados.get("presupuesto"),
                    None,  # costo_real
                    datos_sanitizados.get("direccion"),
                    "",  # notas
                    obra_id,
                ),
            )

            self.db_connection.commit()
            return cursor.rowcount > 0

        except Exception as e:
            if self.db_connection:
                self.db_connection.rollback()
            logger.info(f"Error actualizando obra: {str(e)}")
            return False
    def eliminar_obra(self, obra_id: int) -> bool:
        """Elimina una obra (soft delete)."""
        if not self.db_connection or not obra_id:
            return False

        try:
            cursor = self.db_connection.cursor()

            # Verificar que no tenga recursos asignados
            if self._tiene_recursos_asignados(obra_id):
                raise ValueError("No se puede eliminar obra con recursos asignados")

            # Usar SQL externo para eliminación
            query = self.sql_manager.get_query(self.sql_path, "eliminar_obra")
            cursor.execute(query, (obra_id,))

            self.db_connection.commit()
            return cursor.rowcount > 0

        except Exception as e:
            if self.db_connection:
                self.db_connection.rollback()
            logger.info(f"Error eliminando obra: {str(e)}")
            return False
    def cambiar_estado_obra(self, obra_id: int, nuevo_estado: str) -> bool:
        """Cambia el estado de una obra con validaciones."""
        if not self.db_connection or not obra_id:
            return False

        try:
            estado_sanitizado = sanitize_string(nuevo_estado)

            # Validar estado
            if not self._validar_estado_obra(estado_sanitizado):
                raise ValueError(f"Estado de obra inválido: {estado_sanitizado}")

            cursor = self.db_connection.cursor()

            # Actualizar estado
            query = self.sql_manager.get_query(self.sql_path, "cambiar_estado_obra")
            cursor.execute(query, (estado_sanitizado, obra_id))

            self.db_connection.commit()
            return cursor.rowcount > 0

        except Exception as e:
            if self.db_connection:
                self.db_connection.rollback()
            logger.info(f"Error cambiando estado de obra: {str(e)}")
            return False

    def _validar_datos_obra(self, datos: Dict[str, Any]) -> Dict[str, Any]:
        """Valida y sanitiza datos de obra."""
        # Campos requeridos
        campos_requeridos = ["nombre", "cliente", "fecha_inicio"]
        for campo in campos_requeridos:
            if campo not in datos or not datos[campo]:
                raise ValueError(f"Campo requerido faltante: {campo}")

        # Sanitizar datos
        datos_sanitizados = {}

        # Strings
        datos_sanitizados["nombre"] = sanitize_string(
            datos.get("nombre", "")
        )
        datos_sanitizados["descripcion"] = sanitize_string(
            datos.get("descripcion", "")
        )
        datos_sanitizados["cliente"] = sanitize_string(
            datos.get("cliente", "")
        )
        datos_sanitizados["direccion"] = sanitize_string(
            datos.get("direccion", "")
        )

        # Números
        datos_sanitizados["presupuesto"] = self.sanitizer.sanitize_numeric(
            datos.get("presupuesto", 0), min_val=0
        )

        # Fechas
        datos_sanitizados["fecha_inicio"] = datos.get("fecha_inicio")
        datos_sanitizados["fecha_fin_estimada"] = datos.get("fecha_fin_estimada")

        # Estado inicial
        datos_sanitizados["estado"] = sanitize_string(
            datos.get("estado", "PLANIFICACION")
        )

        # Validaciones específicas
        if not datos_sanitizados["nombre"]:
            raise ValueError("El nombre de la obra es requerido")

        if not datos_sanitizados["cliente"]:
            raise ValueError("El cliente es requerido")

        return datos_sanitizados

    def _obtener_detalles_obra(self, obra_id: int) -> List[Dict[str, Any]]:
        """Obtiene los detalles específicos de una obra."""
        if not self.db_connection:
            return []

        try:
            cursor = self.db_connection.cursor()

            query = self.sql_manager.get_query(self.sql_path, "obtener_detalles_obra")
            cursor.execute(query, (obra_id,))

            detalles = []
            columns = [column[0] for column in cursor.description]

            for row in cursor.fetchall():
                detalle = dict(zip(columns, row))
                detalles.append(detalle)

            return detalles

        except Exception as e:
            logger.info(f"Error obteniendo detalles de obra: {str(e)}")
            return []

    def _calcular_duracion_dias(self, obra: Dict[str, Any]) -> int:
        """Calcula la duración estimada en días."""
        try:
            fecha_inicio = obra.get("fecha_inicio")
            fecha_fin = obra.get("fecha_fin_estimada")

            if not fecha_inicio or not fecha_fin:
                return 0

            # Si son strings, convertir a datetime
            if isinstance(fecha_inicio, str):
                fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d")
            if isinstance(fecha_fin, str):
                fecha_fin = datetime.strptime(fecha_fin, "%Y-%m-%d")

            diferencia = fecha_fin - fecha_inicio
            return diferencia.days

        except (ValueError, TypeError, AttributeError) as e:
            # ValueError: fecha mal formateada en strptime
            # TypeError: tipos incompatibles para operaciones de fecha
            # AttributeError: objeto sin atributos de fecha
            return 0

    def _crear_fase_inicial(self, obra_id: int, cursor) -> None:
        """Crea la fase inicial de una obra."""
        try:
            query = self.sql_manager.get_query(self.sql_path, "crear_fase_inicial")
            cursor.execute(
                query,
                (
                    obra_id,
                    "Planificación",
                    "Fase inicial de planificación",
                    datetime.now(),
                ),
            )
        except Exception as e:
            logger.info(f"Error creando fase inicial: {str(e)}")

    def _tiene_recursos_asignados(self, obra_id: int) -> bool:
        """Verifica si la obra tiene recursos asignados."""
        if not self.db_connection:
            return False

        try:
            cursor = self.db_connection.cursor()

            query = self.sql_manager.get_query(
                self.sql_path, "verificar_recursos_asignados"
            )
            cursor.execute(query, (obra_id,))

            result = cursor.fetchone()
            return (result[0] if result else 0) > 0

        except (sqlite3.Error, AttributeError, TypeError) as e:
            # sqlite3.Error: errores de base de datos
            # AttributeError: cursor o conexión no válidos
            # TypeError: parámetros incorrectos
            return True  # Por seguridad, asumir que tiene recursos

    def _validar_estado_obra(self, estado: str) -> bool:
        """Valida que el estado de obra sea válido."""
        estados_validos = {
            "PLANIFICACION",
            "EN_PROGRESO",
            "EN_PAUSA",
            "COMPLETADA",
            "CANCELADA",
            "PENDIENTE_APROBACION",
        }
        return estado.upper() in estados_validos
    def obtener_estados_disponibles(self) -> List[str]:
        """Obtiene los estados de obra disponibles."""
        return [
            "PLANIFICACION",
            "PENDIENTE_APROBACION",
            "EN_PROGRESO",
            "EN_PAUSA",
            "COMPLETADA",
            "CANCELADA",
        ]
    def calcular_progreso_obra(self, obra_id: int) -> float:
        """Calcula el porcentaje de progreso de una obra."""
        if not self.db_connection or not obra_id:
            return 0.0

        try:
            cursor = self.db_connection.cursor()

            query = self.sql_manager.get_query(self.sql_path, "calcular_progreso_obra")
            cursor.execute(query, (obra_id,))

            result = cursor.fetchone()
            return float(result[0]) if result and result[0] else 0.0

        except Exception as e:
            logger.info(f"Error calculando progreso: {str(e)}")
            return 0.0
