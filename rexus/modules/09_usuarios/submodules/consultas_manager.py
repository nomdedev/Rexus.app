"""
Submódulo de Consultas de Usuarios - Rexus.app

Gestiona consultas, búsquedas, estadísticas y reportes de usuarios.
Responsabilidades:
- Búsquedas avanzadas de usuarios
- Estadísticas del sistema de usuarios
- Paginación y filtros
- Reportes y análisis de uso
"""

import datetime
            from rexus.utils.unified_sanitizer import unified_sanitizer, sanitize_string

# Sistema de logging centralizado
from rexus.utils.app_logger import get_logger, log_error, log_info, log_warning

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


class ConsultasManager:
    """Gestor especializado para consultas y estadísticas de usuarios."""

    def __init__(self, db_connection=None):
        """Inicializa el gestor de consultas."""
        self.db_connection = db_connection
        self.sql_manager = SQLQueryManager()
        self.sanitizer = DataSanitizer()
        self.sql_path = "scripts/sql/usuarios/consultas"
        self.logger = get_logger("usuarios.consultas_manager")

    def _validate_table_name(self, table_name: str) -> str:
        """Valida nombre de tabla contra lista blanca."""
        import re

        if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", table_name):
            raise ValueError(f"Nombre de tabla inválido: {table_name}")

        tablas_permitidas = {
            "usuarios",
            "intentos_login",
            "sesiones_usuario",
            "auditoria_usuarios",
        }
        if table_name not in tablas_permitidas:
            raise ValueError(f"Tabla no permitida: {table_name}")
        return table_name
    def obtener_todos_usuarios(
        self, incluir_inactivos: bool = False
    ) -> List[Dict[str, Any]]:
        """Obtiene todos los usuarios del sistema."""
        if not self.db_connection:
            return []

        try:
            cursor = self.db_connection.cursor()

            if incluir_inactivos:
                query = self.sql_manager.get_query(
                    self.sql_path, "obtener_todos_usuarios_completo"
                )
            else:
                query = self.sql_manager.get_query(
                    self.sql_path, "obtener_todos_usuarios_activos"
                )

            cursor.execute(query)

            usuarios = []
            columns = [desc[0] for desc in cursor.description]

            for row in cursor.fetchall():
                usuario = dict(zip(columns, row))
                # Limpiar datos sensibles
                if "password_hash" in usuario:
                    del usuario["password_hash"]
                if "salt" in usuario:
                    del usuario["salt"]
                usuarios.append(usuario)

            return usuarios

        except Exception as e:
            self.    def obtener_usuarios_paginados(
        self,
        page: int = 1,
        per_page: int = 20,
        filtros: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Obtiene usuarios con paginación y filtros opcionales."""
        if not self.db_connection:
            return {"usuarios": [], "total": 0, "pages": 0}

        try:
            page_safe = max(1, self.sanitizer.sanitize_integer(page, min_val=1))
            per_page_safe = max(
                1,
min(100,
                    self.sanitizer.sanitize_integer(per_page,
                    min_val=1))
            )

            offset = (page_safe - 1) * per_page_safe

            cursor = self.db_connection.cursor()

            # Construir condiciones WHERE según filtros
            where_conditions = ["1=1"]  # Condición base
            params = []

            if filtros:
                if filtros.get("rol"):
                    where_conditions.append("rol = %s")
                    params.append(sanitize_string(filtros["rol"]))

                if filtros.get("activo") is not None:
                    where_conditions.append("activo = %s")
                    params.append(bool(filtros["activo"]))

                if filtros.get("fecha_desde"):
                    where_conditions.append("fecha_creacion >= %s")
                    params.append(filtros["fecha_desde"])

                if filtros.get("fecha_hasta"):
                    where_conditions.append("fecha_creacion <= %s")
                    params.append(filtros["fecha_hasta"])

            where_clause = " AND ".join(where_conditions)

            # Contar total de registros
            count_query = f"""
                SELECT COUNT(*)
                FROM usuarios
                WHERE {where_clause}
            """
            cursor.execute(count_query, params)
            total_registros = cursor.fetchone()[0]

            # Obtener registros paginados
            query = f"""
                SELECT id, username, email, rol, activo, fecha_creacion,
                       ultimo_acceso, nombre, apellido
                FROM usuarios
                WHERE {where_clause}
                ORDER BY fecha_creacion DESC
                LIMIT %s OFFSET %s
            """
            params.extend([per_page_safe, offset])
            cursor.execute(query, params)

            usuarios = []
            columns = [desc[0] for desc in cursor.description]

            for row in cursor.fetchall():
                usuario = dict(zip(columns, row))
                usuarios.append(usuario)

            total_pages = (total_registros + per_page_safe - 1) // per_page_safe

            return {
                "usuarios": usuarios,
                "total": total_registros,
                "pages": total_pages,
                "current_page": page_safe,
                "per_page": per_page_safe,
                "has_next": page_safe < total_pages,
                "has_prev": page_safe > 1,
            }

        except Exception as e:
            self.    def obtener_usuarios_por_rol(self, rol: str) -> List[Dict[str, Any]]:
        """Obtiene usuarios filtrados por rol específico."""
        if not self.db_connection or not rol:
            return []

        try:
            rol_safe = sanitize_string(rol, max_length=20)
            cursor = self.db_connection.cursor()

            query = self.sql_manager.get_query(
                self.sql_path, "obtener_usuarios_por_rol"
            )
            cursor.execute(query, (rol_safe,))

            usuarios = []
            columns = [desc[0] for desc in cursor.description]

            for row in cursor.fetchall():
                usuario = dict(zip(columns, row))
                # Limpiar datos sensibles
                if "password_hash" in usuario:
                    del usuario["password_hash"]
                if "salt" in usuario:
                    del usuario["salt"]
                usuarios.append(usuario)

            return usuarios

        except Exception as e:
            self.    def generar_reporte_seguridad(self) -> Dict[str, Any]:
        """Genera un reporte de seguridad del sistema de usuarios."""
        if not self.db_connection:
            return {}

        try:
            cursor = self.db_connection.cursor()
            reporte = {}

            # Cuentas con múltiples intentos fallidos
            query_fallos = self.sql_manager.get_query(
                self.sql_path, "cuentas_con_fallos_recientes"
            )
            cursor.execute(query_fallos)

            cuentas_riesgo = []
            for row in cursor.fetchall():
                cuentas_riesgo.append(
                    {
                        "username": row[0],
                        "intentos_fallidos": row[1],
                        "ultimo_intento": row[2],
                    }
                )

            reporte["cuentas_riesgo"] = cuentas_riesgo

            # Cuentas bloqueadas actualmente
            query_bloqueadas = self.sql_manager.get_query(
                self.sql_path, "cuentas_bloqueadas_actuales"
            )
            cursor.execute(query_bloqueadas)

            cuentas_bloqueadas = []
            for row in cursor.fetchall():
                cuentas_bloqueadas.append(
                    {
                        "username": row[0],
                        "fecha_bloqueo": row[1],
                        "expira_bloqueo": row[2],
                    }
                )

            reporte["cuentas_bloqueadas"] = cuentas_bloqueadas

            # Usuarios sin actividad reciente
            query_inactivos = self.sql_manager.get_query(
                self.sql_path, "usuarios_inactivos_prolongado"
            )
            cursor.execute(query_inactivos)

            usuarios_inactivos = []
            for row in cursor.fetchall():
                usuarios_inactivos.append(
                    {
                        "username": row[0],
                        "ultimo_acceso": row[1],
                        "dias_inactivo": row[2],
                    }
                )

            reporte["usuarios_inactivos"] = usuarios_inactivos

            # Resumen del reporte
            reporte["resumen"] = {
                "fecha_generacion": datetime.datetime.now(),
                "total_cuentas_riesgo": len(cuentas_riesgo),
                "total_bloqueadas": len(cuentas_bloqueadas),
                "total_inactivos": len(usuarios_inactivos),
                "nivel_alerta": self._calcular_nivel_alerta(reporte),
            }

            return reporte

        except Exception as e:

    def _calcular_nivel_alerta(self, reporte: Dict[str, Any]) -> str:
        """Calcula el nivel de alerta de seguridad."""
        cuentas_riesgo = len(reporte.get("cuentas_riesgo", []))
        cuentas_bloqueadas = len(reporte.get("cuentas_bloqueadas", []))

        if cuentas_riesgo > 10 or cuentas_bloqueadas > 5:
            return "ALTO"
        elif cuentas_riesgo > 5 or cuentas_bloqueadas > 2:
            return "MEDIO"
        else:
            return "BAJO"
