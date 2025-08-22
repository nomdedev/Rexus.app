"""
Submódulo de Consultas Vidrios - Rexus.app

Gestiona búsquedas, filtros y estadísticas de vidrios.
Responsabilidades:
- Búsquedas avanzadas de vidrios
- Filtros por múltiples criterios
- Estadísticas e informes
- Paginación de resultados
"""

from typing import Any, Dict, List, Optional

# Imports de seguridad unificados
from rexus.core.auth_decorators import auth_required, permission_required
from rexus.utils.unified_sanitizer import unified_sanitizer, sanitize_string

# Sistema de logging centralizado
from rexus.utils.app_logger import get_logger
logger = get_logger("vidrios.consultas_manager")

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
    """Gestor especializado para consultas y búsquedas de vidrios."""

    def __init__(self, db_connection=None):
        """Inicializa el gestor de consultas de vidrios."""
        self.db_connection = db_connection
        self.sql_manager = SQLQueryManager()
        self.sanitizer = DataSanitizer()
        self.sql_path = "scripts/sql/vidrios/consultas"

    def obtener_todos_vidrios(
        self, filtros: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Obtiene todos los vidrios con filtros opcionales."""
        if not self.db_connection:
            return []

        try:
            cursor = self.db_connection.cursor()

            # Aplicar filtros si existen
            if filtros:
                filtros_sanitizados = self._sanitizar_filtros(filtros)
                query = self.sql_manager.get_query(
                    self.sql_path, "obtener_vidrios_filtrados"
                )
                cursor.execute(query, filtros_sanitizados)
            else:
                query = self.sql_manager.get_query(
                    self.sql_path, "obtener_todos_vidrios"
                )
                cursor.execute(query)

            vidrios = []
            columns = [column[0] for column in cursor.description]

            for row in cursor.fetchall():
                vidrio = dict(zip(columns, row))
                vidrios.append(vidrio)

            return vidrios

        except Exception as e:
            logger.error(f"Error obteniendo vidrios: {str(e)}")
            return []

    def buscar_vidrios(self, termino_busqueda: str) -> List[Dict[str, Any]]:
        """Búsqueda avanzada de vidrios por múltiples campos."""
        if not self.db_connection or not termino_busqueda:
            return []

        try:
            cursor = self.db_connection.cursor()

            # Sanitizar término de búsqueda
            termino_sanitizado = sanitize_string(termino_busqueda)
            termino_like = f"%{termino_sanitizado}%"

            query = self.sql_manager.get_query(self.sql_path, "buscar_vidrios")
            cursor.execute(
                query,
                {
                    "termino": termino_like,
                    "termino_codigo": termino_like,
                    "termino_tipo": termino_like,
                    "termino_descripcion": termino_like,
                    "termino_proveedor": termino_like,
                },
            )

            resultados = []
            columns = [column[0] for column in cursor.description]

            for row in cursor.fetchall():
                vidrio = dict(zip(columns, row))
                # Calcular relevancia de búsqueda
                vidrio["relevancia"] = self._calcular_relevancia(
                    vidrio, termino_sanitizado
                )
                resultados.append(vidrio)

            # Ordenar por relevancia
            resultados.sort(key=lambda x: x["relevancia"], reverse=True)
            return resultados

        except Exception as e:
            logger.error(f"Error en búsqueda de vidrios: {str(e)}")
            return []
    def obtener_estadisticas_vidrios(self) -> Dict[str, Any]:
        """Obtiene estadísticas completas del inventario de vidrios."""
        if not self.db_connection:
            return {}

        try:
            cursor = self.db_connection.cursor()
            estadisticas = {}

            # Total de vidrios
            query_total = self.sql_manager.get_query(
                self.sql_path, "contar_total_vidrios"
            )
            cursor.execute(query_total)
            result = cursor.fetchone()
            estadisticas["total_vidrios"] = result[0] if result else 0

            # Valor total del inventario
            query_valor = self.sql_manager.get_query(
                self.sql_path, "calcular_valor_total"
            )
            cursor.execute(query_valor)
            result = cursor.fetchone()
            estadisticas["valor_total"] = result[0] if result else 0.0

            # Vidrios por tipo
            query_tipos = self.sql_manager.get_query(self.sql_path, "vidrios_por_tipo")
            cursor.execute(query_tipos)
            estadisticas["por_tipo"] = {}
            for row in cursor.fetchall():
                estadisticas["por_tipo"][row[0]] = row[1]

            # Vidrios con stock bajo
            query_stock_bajo = self.sql_manager.get_query(
                self.sql_path, "vidrios_stock_bajo"
            )
            cursor.execute(query_stock_bajo)
            result = cursor.fetchone()
            estadisticas["stock_bajo"] = result[0] if result else 0

            # Proveedores únicos
            query_proveedores = self.sql_manager.get_query(
                self.sql_path, "contar_proveedores"
            )
            cursor.execute(query_proveedores)
            result = cursor.fetchone()
            estadisticas["total_proveedores"] = result[0] if result else 0

            return estadisticas

        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {str(e)}")
            return {}
    def obtener_vidrios_paginados(
        self,
        page: int = 1,
        per_page: int = 20,
        filtros: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Obtiene vidrios con paginación."""
        if not self.db_connection:
            return {"vidrios": [], "total": 0, "page": page, "per_page": per_page}

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
                    self.sql_path, "contar_vidrios_filtrados"
                )
                cursor.execute(query_count, filtros_sanitizados)
            else:
                query_count = self.sql_manager.get_query(
                    self.sql_path, "contar_total_vidrios"
                )
                cursor.execute(query_count)

            total = cursor.fetchone()[0] if cursor.fetchone() else 0

            # Obtener registros paginados
            if filtros:
                filtros_sanitizados.update({"offset": offset, "limit": per_page})
                query_data = self.sql_manager.get_query(
                    self.sql_path, "obtener_vidrios_paginados_filtrados"
                )
                cursor.execute(query_data, filtros_sanitizados)
            else:
                query_data = self.sql_manager.get_query(
                    self.sql_path, "obtener_vidrios_paginados"
                )
                cursor.execute(query_data, {"offset": offset, "limit": per_page})

            vidrios = []
            columns = [column[0] for column in cursor.description]

            for row in cursor.fetchall():
                vidrio = dict(zip(columns, row))
                vidrios.append(vidrio)

            return {
                "vidrios": vidrios,
                "total": total,
                "page": page,
                "per_page": per_page,
                "total_pages": (total + per_page - 1) // per_page,
            }

        except Exception as e:
            logger.error(f"Error obteniendo vidrios paginados: {str(e)}")
            return {"vidrios": [], "total": 0, "page": page, "per_page": per_page}
    def obtener_vidrios_stock_bajo(self) -> List[Dict[str, Any]]:
        """Obtiene vidrios con stock por debajo del mínimo."""
        if not self.db_connection:
            return []

        try:
            cursor = self.db_connection.cursor()

            query = self.sql_manager.get_query(
                self.sql_path, "obtener_vidrios_stock_bajo"
            )
            cursor.execute(query)

            vidrios = []
            columns = [column[0] for column in cursor.description]

            for row in cursor.fetchall():
                vidrio = dict(zip(columns, row))
                # Calcular diferencia de stock
                vidrio["deficit_stock"] = vidrio.get("stock_minimo", 0) - vidrio.get(
                    "stock", 0
                )
                vidrios.append(vidrio)

            # Ordenar por déficit más alto
            vidrios.sort(key=lambda x: x.get("deficit_stock", 0), reverse=True)
            return vidrios

        except Exception as e:
            logger.error(f"Error obteniendo vidrios con stock bajo: {str(e)}")
            return []

    def _sanitizar_filtros(self, filtros: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitiza y valida filtros de búsqueda."""
        filtros_sanitizados = {}

        # Filtros de texto
        campos_texto = ["tipo", "proveedor", "codigo", "descripcion"]
        for campo in campos_texto:
            if campo in filtros and filtros[campo]:
                filtros_sanitizados[campo] = sanitize_string(
                    filtros[campo]
                )

        # Filtros numéricos
        campos_numericos = ["espesor_min", "espesor_max", "precio_min", "precio_max"]
        for campo in campos_numericos:
            if campo in filtros and filtros[campo] is not None:
                filtros_sanitizados[campo] = self.sanitizer.sanitize_numeric(
                    filtros[campo], min_val=0
                )

        # Filtros de stock
        if "solo_stock_bajo" in filtros and filtros["solo_stock_bajo"]:
            filtros_sanitizados["solo_stock_bajo"] = True

        if "activo" in filtros:
            filtros_sanitizados["activo"] = 1 if filtros["activo"] else 0
        else:
            filtros_sanitizados["activo"] = 1  # Por defecto solo activos

        return filtros_sanitizados

    def _calcular_relevancia(self,
vidrio: Dict[str,
        Any],
        termino: str) -> int:
        """Calcula la relevancia de un vidrio en la búsqueda."""
        relevancia = 0
        termino_lower = termino.lower()

        # Coincidencia exacta en código (máxima relevancia)
        codigo = str(vidrio.get("codigo", "")).lower()
        if codigo == termino_lower:
            relevancia += 100
        elif termino_lower in codigo:
            relevancia += 50

        # Coincidencia en tipo
        tipo = str(vidrio.get("tipo", "")).lower()
        if termino_lower in tipo:
            relevancia += 30

        # Coincidencia en descripción
        descripcion = str(vidrio.get("descripcion", "")).lower()
        if termino_lower in descripcion:
            relevancia += 20

        # Coincidencia en proveedor
        proveedor = str(vidrio.get("proveedor", "")).lower()
        if termino_lower in proveedor:
            relevancia += 10

        return relevancia
    def obtener_reporte_proveedores(self) -> List[Dict[str, Any]]:
        """Genera reporte de vidrios por proveedor."""
        if not self.db_connection:
            return []

        try:
            cursor = self.db_connection.cursor()

            query = self.sql_manager.get_query(self.sql_path, "reporte_proveedores")
            cursor.execute(query)

            proveedores = []
            columns = [column[0] for column in cursor.description]

            for row in cursor.fetchall():
                proveedor = dict(zip(columns, row))
                proveedores.append(proveedor)

            return proveedores

        except Exception as e:
            logger.error(f"Error generando reporte de proveedores: {str(e)}")
            return []
