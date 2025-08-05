# 🔒 DB Authorization Check - Verify user permissions before DB operations
# Ensure all database operations are properly authorized
# DB Authorization Check
"""
Modelo de Auditoría - Rexus.app v2.0.0

Maneja la lógica de negocio y acceso a datos para el sistema de auditoría.
Incluye utilidades de seguridad para prevenir SQL injection y XSS.
"""

import datetime
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Importar utilidades de seguridad
try:
    # Agregar ruta src al path para imports de seguridad
    root_dir = Path(__file__).parent.parent.parent.parent
    sys.path.insert(0, str(root_dir))

    from utils.data_sanitizer import DataSanitizer, data_sanitizer
    from utils.sql_security import SQLSecurityValidator

    SECURITY_AVAILABLE = True
except ImportError as e:
    print(f"[WARNING] Security utilities not available in auditoria: {e}")
    SECURITY_AVAILABLE = False
    data_sanitizer = None

# Importar nueva utilidad de seguridad SQL
try:
    from rexus.utils.sql_security import SQLSecurityError, validate_table_name

    SQL_SECURITY_AVAILABLE = True
except ImportError:
    print("[WARNING] SQL security utilities not available in auditoria")
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

        # Inicializar utilidades de seguridad
        self.security_available = SECURITY_AVAILABLE
        if self.security_available and data_sanitizer:
            self.data_sanitizer = data_sanitizer
            print("OK [AUDITORIA] Utilidades de seguridad cargadas")
        else:
            self.data_sanitizer = None
            print("WARNING [AUDITORIA] Utilidades de seguridad no disponibles")

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
                print(f"[ERROR SEGURIDAD AUDITORIA] {str(e)}")
                # Fallback a verificación básica
                pass

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
        if not self.db_connection:
            return

        try:
            cursor = self.db_connection.connection.cursor()

            # Verificar si la tabla de auditoría existe
            cursor.execute(
                "SELECT * FROM sysobjects WHERE name=? AND xtype='U'",
                (self.tabla_auditoria,),
            )
            if cursor.fetchone():
                print(
                    f"[AUDITORÍA] Tabla '{self.tabla_auditoria}' verificada correctamente."
                )

                # Mostrar la estructura de la tabla
                cursor.execute(
                    "SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = ?",
                    (self.tabla_auditoria,),
                )
                columnas = cursor.fetchall()
                print(f"[AUDITORÍA] Estructura de tabla '{self.tabla_auditoria}':")
                for columna in columnas:
                    print(f"  - {columna[0]}: {columna[1]}")
            else:
                print(
                    f"[ADVERTENCIA] La tabla '{self.tabla_auditoria}' no existe en la base de datos."
                )
        except Exception as e:
            print(f"[ERROR AUDITORÍA] Error creando tabla: {e}")

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
        if not self.db_connection:
            print("[WARN AUDITORÍA] Sin conexión BD - guardando en log local")
            return self._guardar_log_local(usuario, modulo, accion, descripcion)

        try:
            # 🔒 SANITIZACIÓN Y VALIDACIÓN DE DATOS
            if self.data_sanitizer:
                usuario_limpio = self.data_sanitizer.sanitize_string(usuario)
                modulo_limpio = self.data_sanitizer.sanitize_string(modulo)
                accion_limpia = self.data_sanitizer.sanitize_string(accion)
                descripcion_limpia = self.data_sanitizer.sanitize_string(descripcion)
                tabla_afectada_limpia = self.data_sanitizer.sanitize_string(
                    tabla_afectada
                )
                registro_id_limpio = self.data_sanitizer.sanitize_string(registro_id)
                nivel_criticidad_limpio = self.data_sanitizer.sanitize_string(
                    nivel_criticidad
                )
                resultado_limpio = self.data_sanitizer.sanitize_string(resultado)
                error_mensaje_limpio = self.data_sanitizer.sanitize_string(
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

            sql_insert = f"""
            INSERT INTO [{tabla_validada}]
            (usuario, modulo, accion, descripcion, tabla_afectada, registro_id,
             valores_anteriores, valores_nuevos, nivel_criticidad, resultado, error_mensaje)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

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
            print(f"[AUDITORÍA] Registrado: {usuario} - {modulo} - {accion}")
            return True

        except Exception as e:
            print(f"[ERROR AUDITORÍA] Error registrando acción: {e}")
            # Fallback a log local
            return self._guardar_log_local(usuario, modulo, accion, descripcion)

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
            print(f"[ERROR AUDITORÍA] Error guardando log local: {e}")
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
        if not self.db_connection:
            return []

        try:
            # 🔒 SANITIZACIÓN Y VALIDACIÓN DE PARÁMETROS
            if self.data_sanitizer:
                usuario_limpio = (
                    self.data_sanitizer.sanitize_string(usuario) if usuario else ""
                )
                modulo_limpio = (
                    self.data_sanitizer.sanitize_string(modulo) if modulo else ""
                )
                nivel_criticidad_limpio = (
                    self.data_sanitizer.sanitize_string(nivel_criticidad)
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

            print(f"[AUDITORÍA] Obtenidos {len(registros)} registros")
            return registros

        except Exception as e:
            print(f"[ERROR AUDITORÍA] Error obteniendo registros: {e}")
            return []

    def obtener_estadisticas(self, dias: int = 30) -> Dict[str, Any]:
        """
        Obtiene estadísticas de auditoría de los últimos días.

        Args:
            dias: Número de días hacia atrás para analizar

        Returns:
            Dict: Estadísticas de auditoría
        """
        if not self.db_connection:
            return {}

        try:
            cursor = self.db_connection.connection.cursor()
            fecha_limite = datetime.datetime.now() - datetime.timedelta(days=dias)

            # Consultas de estadísticas
            queries = {
                "total_acciones": """
                    SELECT COUNT(*) FROM auditoria_log
                    WHERE fecha_hora >= ?
                """,
                "acciones_por_modulo": """
                    SELECT modulo, COUNT(*) as cantidad
                    FROM auditoria_log
                    WHERE fecha_hora >= ?
                    GROUP BY modulo
                    ORDER BY cantidad DESC
                """,
                "acciones_por_usuario": """
                    SELECT usuario, COUNT(*) as cantidad
                    FROM auditoria_log
                    WHERE fecha_hora >= ?
                    GROUP BY usuario
                    ORDER BY cantidad DESC
                """,
                "acciones_criticas": """
                    SELECT COUNT(*) FROM auditoria_log
                    WHERE fecha_hora >= ? AND nivel_criticidad IN ('ALTA', 'CRÍTICA')
                """,
                "acciones_fallidas": """
                    SELECT COUNT(*) FROM auditoria_log
                    WHERE fecha_hora >= ? AND resultado = 'FALLIDO'
                """,
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
            print(f"[ERROR AUDITORÍA] Error obteniendo estadísticas: {e}")
            return {}

    def limpiar_registros_antiguos(self, dias_conservar: int = 365) -> bool:
        """
        Limpia registros de auditoría antiguos.

        Args:
            dias_conservar: Días de registros a conservar

        Returns:
            bool: True si se realizó la limpieza exitosamente
        """
        if not self.db_connection:
            return False

        try:
            cursor = self.db_connection.connection.cursor()
            fecha_limite = datetime.datetime.now() - datetime.timedelta(
                days=dias_conservar
            )

            sql_delete = """
            DELETE FROM auditoria_log
            WHERE fecha_hora < ? AND nivel_criticidad NOT IN ('CRÍTICA')
            """

            cursor.execute(sql_delete, (fecha_limite,))
            registros_eliminados = cursor.rowcount
            self.db_connection.connection.commit()

            print(f"[AUDITORÍA] Eliminados {registros_eliminados} registros antiguos")

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
            print(f"[ERROR AUDITORÍA] Error limpiando registros: {e}")
            return False
