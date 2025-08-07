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


class ConsultasManager:
    """Gestor especializado para consultas y estadísticas de usuarios."""

    def __init__(self, db_connection=None):
        """Inicializa el gestor de consultas."""
        self.db_connection = db_connection
        self.sql_manager = SQLQueryManager()
        self.data_sanitizer = DataSanitizer()
        self.sql_path = "scripts/sql/usuarios/consultas"

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

    @auth_required
    @permission_required("view_usuarios")
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
            print(f"Error obteniendo usuarios: {str(e)}")
            return []

    @auth_required
    @permission_required("view_usuarios")
    def buscar_usuarios(self, termino_busqueda: str) -> List[Dict[str, Any]]:
        """Búsqueda avanzada de usuarios por múltiples criterios."""
        if not self.db_connection or not termino_busqueda:
            return []

        try:
            termino_safe = self.data_sanitizer.sanitize_string(
                termino_busqueda, max_length=100
            )
            termino_like = f"%{termino_safe}%"

            cursor = self.db_connection.cursor()

            query = self.sql_manager.get_query(self.sql_path, "buscar_usuarios")
            cursor.execute(
                query, (termino_like, termino_like, termino_like, termino_like)
            )

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
            print(f"Error en búsqueda: {str(e)}")
            return []

    @auth_required
    @permission_required("view_usuarios")
    def obtener_usuarios_paginados(
        self,
        page: int = 1,
        per_page: int = 20,
        filtros: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Obtiene usuarios con paginación y filtros opcionales."""
        if not self.db_connection:
            return {"usuarios": [], "total": 0, "pages": 0}

        try:
            page_safe = max(1, self.data_sanitizer.sanitize_integer(page, min_val=1))
            per_page_safe = max(
                1, min(100, self.data_sanitizer.sanitize_integer(per_page, min_val=1))
            )

            offset = (page_safe - 1) * per_page_safe

            cursor = self.db_connection.cursor()

            # Construir condiciones WHERE según filtros
            where_conditions = ["1=1"]  # Condición base
            params = []

            if filtros:
                if filtros.get("rol"):
                    where_conditions.append("rol = %s")
                    params.append(self.data_sanitizer.sanitize_string(filtros["rol"]))

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
            print(f"Error en paginación: {str(e)}")
            return {"usuarios": [], "total": 0, "pages": 0}

    @auth_required
    @permission_required("view_usuarios")
    def obtener_estadisticas_usuarios(self) -> Dict[str, Any]:
        """Obtiene estadísticas completas del sistema de usuarios."""
        if not self.db_connection:
            return {}

        try:
            cursor = self.db_connection.cursor()
            estadisticas = {}

            # Estadísticas básicas
            query_basicas = self.sql_manager.get_query(
                self.sql_path, "estadisticas_basicas_usuarios"
            )
            cursor.execute(query_basicas)
            result = cursor.fetchone()

            if result:
                estadisticas.update(
                    {
                        "total_usuarios": result[0] or 0,
                        "usuarios_activos": result[1] or 0,
                        "usuarios_inactivos": result[2] or 0,
                        "nuevos_hoy": result[3] or 0,
                        "nuevos_esta_semana": result[4] or 0,
                        "nuevos_este_mes": result[5] or 0,
                    }
                )

            # Estadísticas por rol
            query_roles = self.sql_manager.get_query(
                self.sql_path, "estadisticas_por_rol"
            )
            cursor.execute(query_roles)

            roles_stats = {}
            for row in cursor.fetchall():
                roles_stats[row[0]] = row[1]

            estadisticas["distribucion_roles"] = roles_stats

            # Estadísticas de actividad (últimos 30 días)
            query_actividad = self.sql_manager.get_query(
                self.sql_path, "estadisticas_actividad_reciente"
            )
            cursor.execute(query_actividad)

            actividad = []
            for row in cursor.fetchall():
                actividad.append(
                    {
                        "fecha": row[0],
                        "logins_exitosos": row[1] or 0,
                        "intentos_fallidos": row[2] or 0,
                    }
                )

            estadisticas["actividad_reciente"] = actividad

            # Usuarios más activos
            query_activos = self.sql_manager.get_query(
                self.sql_path, "usuarios_mas_activos"
            )
            cursor.execute(query_activos)

            usuarios_activos = []
            for row in cursor.fetchall():
                usuarios_activos.append(
                    {
                        "username": row[0],
                        "total_logins": row[1] or 0,
                        "ultimo_acceso": row[2],
                    }
                )

            estadisticas["usuarios_mas_activos"] = usuarios_activos

            return estadisticas

        except Exception as e:
            print(f"Error obteniendo estadísticas: {str(e)}")
            return {}

    @auth_required
    @permission_required("view_usuarios")
    def obtener_usuarios_por_rol(self, rol: str) -> List[Dict[str, Any]]:
        """Obtiene usuarios filtrados por rol específico."""
        if not self.db_connection or not rol:
            return []

        try:
            rol_safe = self.data_sanitizer.sanitize_string(rol, max_length=20)
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
            print(f"Error obteniendo usuarios por rol: {str(e)}")
            return []

    @auth_required
    @permission_required("view_usuarios")
    def obtener_actividad_usuario(
        self, usuario_id: int, dias: int = 30
    ) -> Dict[str, Any]:
        """Obtiene el historial de actividad de un usuario específico."""
        if not self.db_connection or not usuario_id:
            return {"intentos_login": [], "estadisticas": {}}

        try:
            usuario_id_safe = self.data_sanitizer.sanitize_integer(
                usuario_id, min_val=1
            )
            dias_safe = max(
                1, min(365, self.data_sanitizer.sanitize_integer(dias, min_val=1))
            )

            cursor = self.db_connection.cursor()

            # Historial de intentos de login
            query_historial = self.sql_manager.get_query(
                self.sql_path, "historial_actividad_usuario"
            )
            fecha_limite = datetime.datetime.now() - datetime.timedelta(days=dias_safe)
            cursor.execute(query_historial, (usuario_id_safe, fecha_limite))

            intentos = []
            for row in cursor.fetchall():
                intentos.append(
                    {
                        "fecha": row[0],
                        "exitoso": bool(row[1]),
                        "ip_address": row[2] or "Unknown",
                    }
                )

            # Estadísticas resumidas
            query_stats = self.sql_manager.get_query(
                self.sql_path, "estadisticas_usuario"
            )
            cursor.execute(query_stats, (usuario_id_safe, fecha_limite))

            stats_row = cursor.fetchone()
            estadisticas = (
                {
                    "total_intentos": stats_row[0] or 0,
                    "intentos_exitosos": stats_row[1] or 0,
                    "intentos_fallidos": stats_row[2] or 0,
                    "dias_analizados": dias_safe,
                }
                if stats_row
                else {}
            )

            return {"intentos_login": intentos, "estadisticas": estadisticas}

        except Exception as e:
            print(f"Error obteniendo actividad de usuario: {str(e)}")
            return {"intentos_login": [], "estadisticas": {}}

    @auth_required
    @permission_required("admin")
    def generar_reporte_seguridad(self) -> Dict[str, Any]:
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
            print(f"Error generando reporte de seguridad: {str(e)}")
            return {}

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
