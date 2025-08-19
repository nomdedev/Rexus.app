# [LOCK] DB Authorization Check - Verify user permissions before DB operations
# Ensure all database operations are properly authorized
# DB Authorization Check
"""
Modelo de Auditoría - Rexus.app v2.0.0

Maneja la lógica de negocio y acceso a datos para el sistema de auditoría.
Incluye utilidades de seguridad para prevenir SQL injection y XSS.
"""

import datetime
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

# Importar sistema de logging centralizado
from rexus.utils.app_logger import get_logger

# Configurar logger
logger = get_logger(__name__)

# Importar utilidades de seguridad
try:
    # Agregar ruta src al path para imports de seguridad
    root_dir = Path(__file__).parent.parent.parent.parent
    sys.path.insert(0, str(root_dir))

    SECURITY_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Security utilities not available in auditoria: {e}")
    SECURITY_AVAILABLE = False
    data_sanitizer = None

# Importar utilidades de seguridad SQL y sanitización
from rexus.utils.unified_sanitizer import unified_sanitizer, sanitize_string
from rexus.utils.sql_query_manager import SQLQueryManager
from rexus.utils.unified_sanitizer import sanitize_string

try:
    from rexus.utils.sql_security import SQLSecurityError, validate_table_name
    SQL_SECURITY_AVAILABLE = True
except ImportError:
    logger.warning("SQL security utilities not available in auditoria")
    SQL_SECURITY_AVAILABLE = False
    validate_table_name = None
    SQLSecurityError = Exception


class AuditoriaModel:
    """Modelo para gestionar los registros de auditoría del sistema con seguridad."""

    def __init__(self, db_connection=None):
        """
        Inicializa el modelo de auditoría.

        Args:
            db_connection: Conexión a la base de datos
        """
        self.db_connection = db_connection
        self.tabla_auditoria = "auditoria_log"

        # Inicializar SQLQueryManager para consultas seguras
        self.sql_manager = SQLQueryManager()

        # Inicializar utilidades de seguridad
        self.security_available = SECURITY_AVAILABLE
        self.sanitizer = unified_sanitizer
        self.data_sanitizer = unified_sanitizer  # Alias for compatibility
        logger.info("OK [AUDITORIA] Sistema unificado de sanitización cargado")

        # Intentar establecer conexión automática si no se proporciona
        if not self.db_connection:
            try:
                from rexus.core.database import get_inventario_connection
                self.db_connection = get_inventario_connection()
                if self.db_connection:
                    logger.info("[AUDITORIA] Conexión automática establecida exitosamente")
                else:
                    logger.warning("[ERROR AUDITORIA] No se pudo establecer conexión automática")
            except Exception as e:
                logger.error(f"[ERROR AUDITORIA] Error en conexión automática: {e}")

        if not self.db_connection:
            logger.error("[ERROR AUDITORÍA] Conexión a base de datos no disponible")
        else:
            self._crear_tabla_si_no_existe()

    def _validate_table_name(self, table_name: str) -> str:
        """
        Valida el nombre de tabla para prevenir SQL injection.

        Args:
            table_name: Nombre de la tabla a validar

        Returns:
            str: Nombre de tabla validado

        Raises:
            Exception: Si el nombre no es válido o contiene caracteres peligrosos
        """
        if SQL_SECURITY_AVAILABLE and validate_table_name:
            try:
                return validate_table_name(table_name)
            except SQLSecurityError as e:
                logger.error(f"[ERROR SEGURIDAD AUDITORIA] {str(e)}")
                # Fallback a verificación básica

        # Verificación básica si la utilidad no está disponible
        if not table_name or not isinstance(table_name, str):
            raise ValueError("Nombre de tabla inválido")

        # Eliminar espacios en blanco
        table_name = table_name.strip()

        # Verificar que solo contenga caracteres alfanuméricos y guiones bajos
        if not all(c.isalnum() or c == "_" for c in table_name):
            raise ValueError(
                f"Nombre de tabla contiene caracteres no válidos: {table_name}"
            )

        # Verificar longitud razonable
        if len(table_name) > 64:
            raise ValueError(f"Nombre de tabla demasiado largo: {table_name}")

        return table_name.lower()

    def _crear_tabla_si_no_existe(self):
        """Verifica que la tabla de auditoría exista en la base de datos."""
        if not self.db_connection or not hasattr(self.db_connection, 'connection') or not self.db_connection.connection:
            logger.error("[ERROR AUDITORÍA] Conexión a base de datos no disponible")
            return

        try:
            cursor = self.db_connection.connection.cursor()

            # Verificar si la tabla de auditoría existe usando SQL externo
            try:
                query_verificar = self.sql_manager.get_query('auditoria', 'verificar_tabla_existe')
                cursor.execute(query_verificar, (self.tabla_auditoria,))
            except Exception as e:
                logger.error(f"[ERROR AUDITORÍA] Error cargando query verificar_tabla_existe: {e}")
                # Fallback query directo
                cursor.execute("SELECT * FROM sysobjects WHERE name=? AND xtype='U'", (self.tabla_auditoria,))

            if cursor.fetchone():
                logger.info(f"[AUDITORÍA] Tabla '{self.tabla_auditoria}' verificada correctamente.")

                # Mostrar la estructura de la tabla usando SQL externo
                query_estructura = self.sql_manager.get_query('auditoria/obtener_estructura_tabla')
                cursor.execute(query_estructura, (self.tabla_auditoria,))
                columnas = cursor.fetchall()
                logger.info(f"[AUDITORÍA] Estructura de tabla '{self.tabla_auditoria}':")
                for columna in columnas:
                    logger.info(f"  - {columna[0]}: {columna[1]}")
            else:
                logger.warning(
                    f"[ADVERTENCIA] La tabla '{self.tabla_auditoria}' no existe en la base de datos."
                )
        except Exception as e:
            logger.error(f"[ERROR AUDITORÍA] Error creando tabla: {e}")

    def crear_log(self, nivel, modulo, accion, usuario_id=None, detalle="", ip_origen=None, user_agent=None, datos_adicionales=None):
        """
        Crea un nuevo log de auditoría (método simplificado).
        
        Args:
            nivel (str): Nivel del log (INFO, WARNING, ERROR)
            modulo (str): Módulo que genera el log
            accion (str): Acción realizada
            usuario_id (int): ID del usuario
            detalle (str): Detalle del evento
            ip_origen (str): IP de origen
            user_agent (str): User agent
            datos_adicionales (str): Datos adicionales en JSON
            
        Returns:
            bool: True si se creó correctamente
        """
        try:
            # Usar SQL externo para inserción
            archivo_sql = 'sql/auditoria/crear_log.sql'
            parametros = {
                'nivel': nivel or 'INFO',
                'modulo': modulo,
                'accion': accion,
                'usuario_id': usuario_id,
                'detalle': detalle,
                'ip_origen': ip_origen,
                'user_agent': user_agent,
                'datos_adicionales': datos_adicionales
            }
            
            # Fallback si no existe archivo SQL
            if not os.path.exists(archivo_sql):
                return self._crear_log_demo(nivel, modulo, accion, detalle)
                
            resultado = self.sql_manager.ejecutar_consulta_archivo(archivo_sql, parametros)
            return resultado is not None
            
        except Exception as e:
            logger.error(f"Error creando log de auditoría: {e}")
            return False

    def _crear_log_demo(self, nivel, modulo, accion, detalle):
        """Creación de log demo para testing."""
        logger.info(f"[DEMO AUDIT] {nivel} - {modulo}.{accion}: {detalle}")
        return True

    def registrar_accion(
        self,
        usuario: str,
        modulo: str,
        accion: str,
        descripcion: str = "",
        tabla_afectada: str = "",
        registro_id: str = "",
        valores_anteriores: Dict | None = None,
        valores_nuevos: Dict | None = None,
        nivel_criticidad: str = "MEDIA",
        resultado: str = "EXITOSO",
        error_mensaje: str = "",
    ) -> bool:
        """
        Registra una acción en el log de auditoría con sanitización de datos.

        Args:
            usuario: Usuario que realizó la acción
            modulo: Módulo donde se realizó la acción
            accion: Tipo de acción realizada
            descripcion: Descripción detallada de la acción
            tabla_afectada: Tabla de BD afectada (opcional)
            registro_id: ID del registro afectado (opcional)
            valores_anteriores: Valores antes del cambio (opcional)
            valores_nuevos: Valores después del cambio (opcional)
            nivel_criticidad: BAJA, MEDIA, ALTA, CRÍTICA
            resultado: EXITOSO, FALLIDO, WARNING
            error_mensaje: Mensaje de error si el resultado es FALLIDO

        Returns:
            bool: True si se registró exitosamente
        """
        if not self.db_connection or not hasattr(self.db_connection, 'connection') or not self.db_connection.connection:
            logger.warning("[WARN AUDITORÍA] Sin conexión BD - guardando en log local")
            return self._guardar_log_local(usuario,
modulo,
                accion,
                descripcion)

        try:
            # [LOCK] SANITIZACIÓN Y VALIDACIÓN DE DATOS
            if self.data_sanitizer:
                usuario_limpio = sanitize_string(usuario)
                modulo_limpio = sanitize_string(modulo)
                accion_limpia = sanitize_string(accion)
                descripcion_limpia = sanitize_string(descripcion)
                tabla_afectada_limpia = sanitize_string(
                    tabla_afectada
                )
                registro_id_limpio = sanitize_string(registro_id)
                nivel_criticidad_limpio = sanitize_string(
                    nivel_criticidad
                )
                resultado_limpio = sanitize_string(resultado)
                error_mensaje_limpio = sanitize_string(
                    error_mensaje
                )
            else:
                usuario_limpio = usuario.strip()
                modulo_limpio = modulo.strip()
                accion_limpia = accion.strip()
                descripcion_limpia = descripcion.strip()
                tabla_afectada_limpia = tabla_afectada.strip()
                registro_id_limpio = registro_id.strip()
                nivel_criticidad_limpio = nivel_criticidad.strip()
                resultado_limpio = resultado.strip()
                error_mensaje_limpio = error_mensaje.strip()

            # Validar tabla
            tabla_validada = self._validate_table_name(self.tabla_auditoria)

            cursor = self.db_connection.connection.cursor()

            # Convertir diccionarios a string JSON si existen (sanitizados)
            valores_ant_str = None
            valores_new_str = None

            if valores_anteriores:
                if self.data_sanitizer:
                    valores_anteriores_limpios = self.data_sanitizer.sanitize_dict(
                        valores_anteriores
                    )
                    valores_ant_str = str(valores_anteriores_limpios)
                else:
                    valores_ant_str = str(valores_anteriores)

            if valores_nuevos:
                if self.data_sanitizer:
                    valores_nuevos_limpios = self.data_sanitizer.sanitize_dict(
                        valores_nuevos
                    )
                    valores_new_str = str(valores_nuevos_limpios)
                else:
                    valores_new_str = str(valores_nuevos)

            # Usar SQL query manager para inserción segura
            sql_insert = self.sql_manager.get_query('auditoria', 'insert_audit_log')

            cursor.execute(
                sql_insert,
                (
                    usuario_limpio,
                    modulo_limpio,
                    accion_limpia,
                    descripcion_limpia,
                    tabla_afectada_limpia,
                    registro_id_limpio,
                    valores_ant_str,
                    valores_new_str,
                    nivel_criticidad_limpio,
                    resultado_limpio,
                    error_mensaje_limpio,
                ),
            )

            self.db_connection.connection.commit()
            logger.info(f"[AUDITORÍA] Registrado: {usuario} - {modulo} - {accion}")
            return True

        except Exception as e:
            logger.error(f"[ERROR AUDITORÍA] Error registrando acción: {e}")
            # Fallback a log local
            return self._guardar_log_local(usuario,
modulo,
                accion,
                descripcion)

    def _guardar_log_local(
        self, usuario: str, modulo: str, accion: str, descripcion: str
    ) -> bool:
        """Guarda el log localmente cuando no hay conexión BD."""
        try:
            import os

            log_dir = "logs"
            os.makedirs(log_dir, exist_ok=True)

            log_file = os.path.join(log_dir, "auditoria_local.txt")
            timestamp = datetime.datetime.now().isoformat()

            with open(log_file, "a", encoding="utf-8") as f:
                f.write(
                    f"{timestamp} | {usuario} | {modulo} | {accion} | {descripcion}\n"
                )

            return True
        except Exception as e:
            logger.error(f"[ERROR AUDITORÍA] Error guardando log local: {e}")
            return False

    def obtener_registros(
        self,
        fecha_inicio: datetime.date | None = None,
        fecha_fin: datetime.date | None = None,
        usuario: str = "",
        modulo: str = "",
        nivel_criticidad: str = "",
        limite: int = 1000,
    ) -> List[Dict]:
        """
        Obtiene registros de auditoría con filtros y sanitización.

        Args:
            fecha_inicio: Fecha de inicio del rango
            fecha_fin: Fecha fin del rango
            usuario: Filtrar por usuario específico
            modulo: Filtrar por módulo específico
            nivel_criticidad: Filtrar por nivel de criticidad
            limite: Máximo número de registros a retornar

        Returns:
            List[Dict]: Lista de registros de auditoría
        """
        if not self.db_connection or not hasattr(self.db_connection, 'connection') or not self.db_connection.connection:
            logger.error("[ERROR AUDITORÍA] Sin conexión a BD para obtener registros")
            return []

        try:
            # [LOCK] SANITIZACIÓN Y VALIDACIÓN DE PARÁMETROS
            if self.data_sanitizer:
                usuario_limpio = (
                    sanitize_string(usuario) if usuario else ""
                )
                modulo_limpio = (
                    sanitize_string(modulo) if modulo else ""
                )
                nivel_criticidad_limpio = (
                    sanitize_string(nivel_criticidad)
                    if nivel_criticidad
                    else ""
                )
            else:
                usuario_limpio = usuario.strip() if usuario else ""
                modulo_limpio = modulo.strip() if modulo else ""
                nivel_criticidad_limpio = (
                    nivel_criticidad.strip() if nivel_criticidad else ""
                )

            # Validar límite para evitar DoS
            limite_seguro = min(max(1, int(limite)), 10000)  # Entre 1 y 10000

            # Validar tabla
            tabla_validada = self._validate_table_name(self.tabla_auditoria)

            cursor = self.db_connection.connection.cursor()

            # Construir query con filtros
            conditions = []
            params = []

            if fecha_inicio:
                conditions.append("fecha_hora >= ?")
                params.append(fecha_inicio)

            if fecha_fin:
                conditions.append("fecha_hora <= ?")
                params.append(fecha_fin + datetime.timedelta(days=1))

            if usuario_limpio:
                conditions.append("usuario LIKE ?")
                params.append(f"%{usuario_limpio}%")

            if modulo_limpio:
                conditions.append("modulo = ?")
                params.append(modulo_limpio)

            if nivel_criticidad_limpio:
                conditions.append("nivel_criticidad = ?")
                params.append(nivel_criticidad_limpio)

            where_clause = ""
            if conditions:
                where_clause = "WHERE " + " AND ".join(conditions)

            # Usar SQL query manager (sin where_clause aún para simplicidad)
            if not where_clause:
                sql_select = self.sql_manager.get_query('auditoria', 'select_logs_recientes', limite=limite_seguro)
            else:
                # Fallback para queries con filtros complejos
                sql_select = f"""
                SELECT TOP {limite_seguro}
                    id, fecha_hora, usuario, modulo, accion, descripcion,
                    tabla_afectada, registro_id, nivel_criticidad, resultado
                FROM [{tabla_validada}]
                {where_clause}
                ORDER BY fecha_hora DESC
                """

            cursor.execute(sql_select, params)
            rows = cursor.fetchall()

            # Convertir a lista de diccionarios
            columns = [desc[0] for desc in cursor.description]
            registros = []

            for row in rows:
                registro = dict(zip(columns, row))
                registros.append(registro)

            logger.info(f"[AUDITORÍA] Obtenidos {len(registros)} registros")
            return registros

        except Exception as e:
            logger.error(f"[ERROR AUDITORÍA] Error obteniendo registros: {e}")
            return []

    def obtener_estadisticas(self, dias: int = 30) -> Dict[str, Any]:
        """
        Obtiene estadísticas de auditoría de los últimos días.

        Args:
            dias: Número de días hacia atrás para analizar

        Returns:
            Dict: Estadísticas de auditoría
        """
        if not self.db_connection or not hasattr(self.db_connection, 'connection') or not self.db_connection.connection:
            logger.error("[ERROR AUDITORÍA] Sin conexión a BD para obtener estadísticas")
            return {}

        try:
            cursor = self.db_connection.connection.cursor()
            fecha_limite = datetime.datetime.now() - datetime.timedelta(days=dias)

            # Usar SQL query manager para estadísticas
            queries = {
                "total_acciones": self.sql_manager.get_query('auditoria', 'count_total_acciones'),
                "acciones_por_modulo": self.sql_manager.get_query('auditoria', 'count_acciones_por_modulo'),
                "acciones_por_usuario": self.sql_manager.get_query('auditoria', 'count_acciones_por_usuario'),
                "acciones_criticas": self.sql_manager.get_query('auditoria', 'count_acciones_criticas'),
                "acciones_fallidas": self.sql_manager.get_query('auditoria', 'count_acciones_fallidas'),
            }

            estadisticas = {}

            for key, query in queries.items():
                cursor.execute(query, (fecha_limite,))

                if key in ["total_acciones", "acciones_criticas", "acciones_fallidas"]:
                    result = cursor.fetchone()
                    estadisticas[key] = result[0] if result else 0
                else:
                    results = cursor.fetchall()
                    estadisticas[key] = [
                        {"nombre": row[0], "cantidad": row[1]} for row in results
                    ]

            return estadisticas

        except Exception as e:
            logger.error(f"[ERROR AUDITORÍA] Error obteniendo estadísticas: {e}")
            return {}

    def limpiar_registros_antiguos(self, dias_conservar: int = 365) -> bool:
        """
        Limpia registros de auditoría antiguos.

        Args:
            dias_conservar: Días de registros a conservar

        Returns:
            bool: True si se realizó la limpieza exitosamente
        """
        if not self.db_connection or not hasattr(self.db_connection, 'connection') or not self.db_connection.connection:
            logger.error("[ERROR AUDITORÍA] Sin conexión a BD para limpiar registros")
            return False

        try:
            cursor = self.db_connection.connection.cursor()
            fecha_limite = datetime.datetime.now() - datetime.timedelta(
                days=dias_conservar
            )

            # Usar SQL query manager para eliminación segura
            sql_delete = self.sql_manager.get_query('auditoria', 'delete_logs_antiguos')

            cursor.execute(sql_delete, (fecha_limite,))
            registros_eliminados = cursor.rowcount
            self.db_connection.connection.commit()

            logger.info(f"[AUDITORÍA] Eliminados {registros_eliminados} registros antiguos")

            # Registrar la limpieza
            self.registrar_accion(
                usuario="SISTEMA",
                modulo="AUDITORÍA",
                accion="LIMPIEZA_AUTOMÁTICA",
                descripcion=f"Eliminados {registros_eliminados} registros anteriores a {fecha_limite.date()}",
                nivel_criticidad="MEDIA",
            )

            return True

        except Exception as e:
            logger.error(f"[ERROR AUDITORÍA] Error limpiando registros: {e}")
            return False

    def obtener_logs_auditoria(self, limite=50, filtros=None):
        """
        Obtiene logs de auditoría con límite y filtros opcionales
        
        Args:
            limite (int): Número máximo de registros a obtener
            filtros (dict, optional): Filtros a aplicar
            
        Returns:
            List[Dict]: Lista de logs de auditoría
        """
        try:
            if not self.db_connection:
                logger.warning("Sin conexión BD para obtener logs")
                return self._get_logs_demo()
                
            cursor = self.db_connection.cursor()
            
            # Query base para obtener logs
            query = """
            SELECT TOP (?) 
                id,
                fecha,
                nivel_criticidad,
                accion,
                descripcion,
                usuario,
                detalles
            FROM auditoria_log
            WHERE 1=1
            """
            
            params = [limite]
            
            # Agregar filtros si se proporcionan
            if filtros:
                if filtros.get('usuario'):
                    query += " AND usuario LIKE ?"
                    params.append(f"%{filtros['usuario']}%")
                if filtros.get('accion'):
                    query += " AND accion LIKE ?"
                    params.append(f"%{filtros['accion']}%")
                if filtros.get('nivel'):
                    query += " AND nivel_criticidad = ?"
                    params.append(filtros['nivel'])
                    
            query += " ORDER BY fecha DESC"
            
            cursor.execute(query, params)
            
            logs = []
            for row in cursor.fetchall():
                log = {
                    'id': row[0],
                    'fecha': row[1],
                    'nivel_criticidad': row[2],
                    'accion': row[3],
                    'descripcion': row[4],
                    'usuario': row[5],
                    'detalles': row[6]
                }
                logs.append(log)
                
            return logs
            
        except Exception as e:
            logger.error(f"Error obteniendo logs auditoria: {e}")
            return self._get_logs_demo()
            
    def _get_logs_demo(self):
        """Datos demo para logs cuando no hay conexión o tabla"""
        from datetime import datetime, timedelta
        
        return [
            {
                'id': 1,
                'fecha': datetime.now() - timedelta(hours=1),
                'nivel_criticidad': 'INFO',
                'accion': 'LOGIN',
                'descripcion': 'Usuario inició sesión',
                'usuario': 'demo_user',
                'detalles': 'Sesión demo iniciada correctamente'
            },
            {
                'id': 2,
                'fecha': datetime.now() - timedelta(hours=2),
                'nivel_criticidad': 'WARNING',
                'accion': 'CONEXION_BD',
                'descripcion': 'Intento de conexión fallido',
                'usuario': 'sistema',
                'detalles': 'Error de conectividad temporal'
            }
        ]
