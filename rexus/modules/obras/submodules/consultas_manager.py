"""
Submódulo de Consultas de Obras - Rexus.app

Gestiona búsquedas, filtros y estadísticas de obras.
Responsabilidades:
- Búsquedas avanzadas de obras
- Filtros por múltiples criterios
- Estadísticas e informes de obras
- Reportes de productividad
"""

from datetime import datetime, timedelta
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
            script_name = f"{path.replace('scripts/sql/', '')}/{filename}"
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


class ConsultasManager:
    """Gestor especializado para consultas y búsquedas de obras."""

    def __init__(self, db_connection=None):
        """Inicializa el gestor de consultas de obras."""
        self.db_connection = db_connection
        self.sql_manager = SQLQueryManager()
        self.sanitizer = DataSanitizer()
        self.sql_path = "scripts/sql/obras/consultas"

    @auth_required
    @permission_required("view_obras")
    def obtener_todas_obras(
        self, filtros: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Obtiene todas las obras con filtros opcionales."""
        if not self.db_connection:
            return []

        try:
            cursor = self.db_connection.cursor()

            # Aplicar filtros si existen
            if filtros:
                filtros_sanitizados = self._sanitizar_filtros(filtros)
                query = self.sql_manager.get_query(
                    self.sql_path, "obtener_obras_filtradas"
                )
                cursor.execute(query, filtros_sanitizados)
            else:
                query = self.sql_manager.get_query(self.sql_path, "obtener_todas_obras")
                cursor.execute(query)

            obras = []
            columns = [column[0] for column in cursor.description]

            for row in cursor.fetchall():
                obra = dict(zip(columns, row))
                # Agregar cálculos adicionales
                obra["progreso"] = self._calcular_progreso_obra(obra["id"])
                obra["dias_restantes"] = self._calcular_dias_restantes(obra)
                obras.append(obra)

            return obras

        except Exception as e:
            print(f"Error obteniendo obras: {str(e)}")
            return []

    @auth_required
    @permission_required("view_obras")
    def buscar_obras(self, termino_busqueda: str) -> List[Dict[str, Any]]:
        """Búsqueda avanzada de obras por múltiples campos."""
        if not self.db_connection or not termino_busqueda:
            return []

        try:
            cursor = self.db_connection.cursor()

            # Sanitizar término de búsqueda
            termino_sanitizado = sanitize_string(termino_busqueda)
            termino_like = f"%{termino_sanitizado}%"

            query = self.sql_manager.get_query(self.sql_path, "buscar_obras")
            cursor.execute(
                query,
                {
                    "termino": termino_like,
                    "termino_nombre": termino_like,
                    "termino_cliente": termino_like,
                    "termino_direccion": termino_like,
                },
            )

            resultados = []
            columns = [column[0] for column in cursor.description]

            for row in cursor.fetchall():
                obra = dict(zip(columns, row))
                # Calcular relevancia de búsqueda
                obra["relevancia"] = self._calcular_relevancia(obra, termino_sanitizado)
                resultados.append(obra)

            # Ordenar por relevancia
            resultados.sort(key=lambda x: x["relevancia"], reverse=True)
            return resultados

        except Exception as e:
            print(f"Error en búsqueda de obras: {str(e)}")
            return []

    @auth_required
    @permission_required("view_obras")
    def obtener_estadisticas_obras(self) -> Dict[str, Any]:
        """Obtiene estadísticas completas de obras."""
        if not self.db_connection:
            return {}

        try:
            cursor = self.db_connection.cursor()
            estadisticas = {}

            # Total de obras
            query_total = self.sql_manager.get_query(
                self.sql_path, "contar_total_obras"
            )
            cursor.execute(query_total)
            result = cursor.fetchone()
            estadisticas["total_obras"] = result[0] if result else 0

            # Obras por estado
            query_estados = self.sql_manager.get_query(
                self.sql_path, "obras_por_estado"
            )
            cursor.execute(query_estados)
            estadisticas["por_estado"] = {}
            for row in cursor.fetchall():
                estadisticas["por_estado"][row[0]] = row[1]

            # Valor total de obras
            query_valor = self.sql_manager.get_query(
                self.sql_path, "calcular_valor_total_obras"
            )
            cursor.execute(query_valor)
            result = cursor.fetchone()
            estadisticas["valor_total"] = result[0] if result else 0.0

            # Obras activas
            query_activas = self.sql_manager.get_query(
                self.sql_path, "contar_obras_activas"
            )
            cursor.execute(query_activas)
            result = cursor.fetchone()
            estadisticas["obras_activas"] = result[0] if result else 0

            # Promedio de duración
            query_duracion = self.sql_manager.get_query(
                self.sql_path, "promedio_duracion_obras"
            )
            cursor.execute(query_duracion)
            result = cursor.fetchone()
            estadisticas["duracion_promedio_dias"] = result[0] if result else 0

            return estadisticas

        except Exception as e:
            print(f"Error obteniendo estadísticas: {str(e)}")
            return {}

    @auth_required
    @permission_required("view_obras")
    def obtener_obras_paginadas(
        self,
        page: int = 1,
        per_page: int = 20,
        filtros: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Obtiene obras con paginación."""
        if not self.db_connection:
            return {"obras": [], "total": 0, "page": page, "per_page": per_page}

        try:
            # Sanitizar parámetros de paginación
            page = max(1, self.sanitizer.sanitize_integer(page, min_val=1))
            per_page = max(
                1,
min(100,
                    self.sanitizer.sanitize_integer(per_page,
                    min_val=1))
            )

            offset = (page - 1) * per_page

            cursor = self.db_connection.cursor()

            # Contar total de registros
            if filtros:
                filtros_sanitizados = self._sanitizar_filtros(filtros)
                query_count = self.sql_manager.get_query(
                    self.sql_path, "contar_obras_filtradas"
                )
                cursor.execute(query_count, filtros_sanitizados)
            else:
                query_count = self.sql_manager.get_query(
                    self.sql_path, "contar_total_obras"
                )
                cursor.execute(query_count)

            total = cursor.fetchone()[0] if cursor.fetchone() else 0

            # Obtener registros paginados
            if filtros:
                filtros_sanitizados.update({"offset": offset, "limit": per_page})
                query_data = self.sql_manager.get_query(
                    self.sql_path, "obtener_obras_paginadas_filtradas"
                )
                cursor.execute(query_data, filtros_sanitizados)
            else:
                query_data = self.sql_manager.get_query(
                    self.sql_path, "obtener_obras_paginadas"
                )
                cursor.execute(query_data, {"offset": offset, "limit": per_page})

            obras = []
            columns = [column[0] for column in cursor.description]

            for row in cursor.fetchall():
                obra = dict(zip(columns, row))
                obras.append(obra)

            return {
                "obras": obras,
                "total": total,
                "page": page,
                "per_page": per_page,
                "total_pages": (total + per_page - 1) // per_page,
            }

        except Exception as e:
            print(f"Error obteniendo obras paginadas: {str(e)}")
            return {"obras": [], "total": 0, "page": page, "per_page": per_page}

    @auth_required
    @permission_required("view_obras")
    def obtener_obras_vencidas(self) -> List[Dict[str, Any]]:
        """Obtiene obras que han superado su fecha de finalización."""
        if not self.db_connection:
            return []

        try:
            cursor = self.db_connection.cursor()

            query = self.sql_manager.get_query(self.sql_path, "obtener_obras_vencidas")
            cursor.execute(query, {"fecha_actual": datetime.now().date()})

            obras = []
            columns = [column[0] for column in cursor.description]

            for row in cursor.fetchall():
                obra = dict(zip(columns, row))
                # Calcular días de retraso
                obra["dias_retraso"] = self._calcular_dias_retraso(obra)
                obras.append(obra)

            # Ordenar por días de retraso (mayor primero)
            obras.sort(key=lambda x: x.get("dias_retraso", 0), reverse=True)
            return obras

        except Exception as e:
            print(f"Error obteniendo obras vencidas: {str(e)}")
            return []

    @auth_required
    @permission_required("view_obras")
    def obtener_reporte_productividad(
        self, fecha_inicio: datetime = None, fecha_fin: datetime = None
    ) -> Dict[str, Any]:
        """Genera reporte de productividad en un período."""
        if not self.db_connection:
            return {}

        try:
            cursor = self.db_connection.cursor()

            # Fechas por defecto (último mes)
            if not fecha_fin:
                fecha_fin = datetime.now()
            if not fecha_inicio:
                fecha_inicio = fecha_fin - timedelta(days=30)

            query = self.sql_manager.get_query(self.sql_path, "reporte_productividad")
            cursor.execute(
                query,
                {"fecha_inicio": fecha_inicio.date(), "fecha_fin": fecha_fin.date()},
            )

            reporte = {}
            columns = [column[0] for column in cursor.description]

            result = cursor.fetchone()
            if result:
                reporte = dict(zip(columns, result))

            # Agregar métricas calculadas
            reporte["obras_completadas_promedio"] = (
                self._calcular_promedio_obras_completadas(fecha_inicio, fecha_fin)
            )

            return reporte

        except Exception as e:
            print(f"Error generando reporte de productividad: {str(e)}")
            return {}

    def _sanitizar_filtros(self, filtros: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitiza y valida filtros de búsqueda."""
        filtros_sanitizados = {}

        # Filtros de texto
        campos_texto = ["estado", "cliente", "nombre"]
        for campo in campos_texto:
            if campo in filtros and filtros[campo]:
                filtros_sanitizados[campo] = sanitize_string(
                    filtros[campo]
                )

        # Filtros numéricos
        campos_numericos = ["presupuesto_min", "presupuesto_max"]
        for campo in campos_numericos:
            if campo in filtros and filtros[campo] is not None:
                filtros_sanitizados[campo] = self.sanitizer.sanitize_numeric(
                    filtros[campo], min_val=0
                )

        # Filtros de fecha
        if "fecha_inicio_desde" in filtros and filtros["fecha_inicio_desde"]:
            filtros_sanitizados["fecha_inicio_desde"] = filtros["fecha_inicio_desde"]

        if "fecha_inicio_hasta" in filtros and filtros["fecha_inicio_hasta"]:
            filtros_sanitizados["fecha_inicio_hasta"] = filtros["fecha_inicio_hasta"]

        # Filtro de activo
        if "activo" in filtros:
            filtros_sanitizados["activo"] = 1 if filtros["activo"] else 0
        else:
            filtros_sanitizados["activo"] = 1  # Por defecto solo activas

        return filtros_sanitizados

    def _calcular_relevancia(self, obra: Dict[str, Any], termino: str) -> int:
        """Calcula la relevancia de una obra en la búsqueda."""
        relevancia = 0
        termino_lower = termino.lower()

        # Coincidencia exacta en nombre (máxima relevancia)
        nombre = str(obra.get("nombre", "")).lower()
        if nombre == termino_lower:
            relevancia += 100
        elif termino_lower in nombre:
            relevancia += 50

        # Coincidencia en cliente
        cliente = str(obra.get("cliente", "")).lower()
        if termino_lower in cliente:
            relevancia += 30

        # Coincidencia en dirección
        direccion = str(obra.get("direccion", "")).lower()
        if termino_lower in direccion:
            relevancia += 20

        return relevancia

    def _calcular_progreso_obra(self, obra_id: int) -> float:
        """Calcula el progreso de una obra específica."""
        if not self.db_connection:
            return 0.0

        try:
            cursor = self.db_connection.cursor()

            query = self.sql_manager.get_query(self.sql_path, "calcular_progreso_obra")
            cursor.execute(query, {"obra_id": obra_id})

            result = cursor.fetchone()
            return float(result[0]) if result and result[0] else 0.0

        except Exception:
            return 0.0

    def _calcular_dias_restantes(self, obra: Dict[str, Any]) -> int:
        """Calcula los días restantes hasta la fecha de finalización."""
        try:
            fecha_fin = obra.get("fecha_fin_estimada")
            if not fecha_fin:
                return 0

            # Si es string, convertir a datetime
            if isinstance(fecha_fin, str):
                fecha_fin = datetime.strptime(fecha_fin, "%Y-%m-%d").date()
            elif isinstance(fecha_fin, datetime):
                fecha_fin = fecha_fin.date()

            hoy = datetime.now().date()
            diferencia = fecha_fin - hoy
            return max(0, diferencia.days)

        except Exception:
            return 0

    def _calcular_dias_retraso(self, obra: Dict[str, Any]) -> int:
        """Calcula los días de retraso de una obra."""
        try:
            fecha_fin = obra.get("fecha_fin_estimada")
            if not fecha_fin:
                return 0

            # Si es string, convertir a datetime
            if isinstance(fecha_fin, str):
                fecha_fin = datetime.strptime(fecha_fin, "%Y-%m-%d").date()
            elif isinstance(fecha_fin, datetime):
                fecha_fin = fecha_fin.date()

            hoy = datetime.now().date()
            diferencia = hoy - fecha_fin
            return max(0, diferencia.days)

        except Exception:
            return 0

    def _calcular_promedio_obras_completadas(
        self, fecha_inicio: datetime, fecha_fin: datetime
    ) -> float:
        """Calcula el promedio de obras completadas por día."""
        try:
            if not self.db_connection:
                return 0.0

            cursor = self.db_connection.cursor()

            query = """
                SELECT COUNT(*)
                FROM obras
                WHERE estado = 'COMPLETADA'
                  AND fecha_finalizacion BETWEEN %(fecha_inicio)s AND %(fecha_fin)s
            """

            cursor.execute(
                query,
                {"fecha_inicio": fecha_inicio.date(), "fecha_fin": fecha_fin.date()},
            )

            total_obras = cursor.fetchone()[0] or 0
            dias_periodo = (fecha_fin - fecha_inicio).days

            return total_obras / max(1, dias_periodo)

        except Exception:
            return 0.0
