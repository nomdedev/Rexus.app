# 🔒 DB Authorization Check - Verify user permissions before DB operations
# Ensure all database operations are properly authorized
# DB Authorization Check
"""
Modelo de Obras - Rexus.app v2.0.0

Maneja la lógica de negocio y acceso a datos para obras.
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
    print(f"[WARNING] Security utilities not available in obras: {e}")
    SECURITY_AVAILABLE = False
    data_sanitizer = None

# Importar nueva utilidad de seguridad SQL
try:
    from rexus.utils.sql_security import SQLSecurityError, validate_table_name

    SQL_SECURITY_AVAILABLE = True
except ImportError:
    print("[WARNING] SQL security utilities not available in obras")
    SQL_SECURITY_AVAILABLE = False
    validate_table_name = None
    SQLSecurityError = Exception


class ObrasModel:
    def __init__(self, db_connection=None):
        self.db_connection = db_connection
        self.tabla_obras = "obras"
        self.tabla_detalles_obra = "detalles_obra"

        # Inicializar utilidades de seguridad
        self.security_available = SECURITY_AVAILABLE
        if self.security_available:
            self.data_sanitizer = data_sanitizer
            self.sql_validator = SQLSecurityValidator()
            print("OK [OBRAS] Utilidades de seguridad cargadas")
        else:
            self.data_sanitizer = None
            self.sql_validator = None
            print("WARNING [OBRAS] Utilidades de seguridad no disponibles")

        self._verificar_tablas()

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
        if SQL_SECURITY_AVAILABLE:
            try:
                return validate_table_name(table_name)
            except SQLSecurityError as e:
                print(f"[ERROR SEGURIDAD OBRAS] {str(e)}")
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

    def validar_obra_duplicada(
        self, codigo_obra: str, id_obra_actual: Optional[int] = None
    ) -> bool:
        """
        Valida si existe una obra duplicada por código.

        Args:
            codigo_obra: Código de obra a verificar
            id_obra_actual: ID de la obra actual (para edición)

        Returns:
            bool: True si existe duplicado, False si no
        """
        if not self.db_connection or not codigo_obra:
            return False

        try:
            # Sanitizar datos
            codigo_limpio = codigo_obra.strip().upper()
            if self.data_sanitizer:
                codigo_limpio = self.data_sanitizer.sanitize_string(codigo_limpio)

            # Validar tabla
            tabla_validada = self._validate_table_name(self.tabla_obras)

            cursor = self.db_connection.cursor()

            if id_obra_actual:
                # Para edición, excluir la obra actual
                query = (
                    "SELECT COUNT(*) FROM ["
                    + tabla_validada
                    + "] WHERE UPPER(codigo) = ? AND id != ?"
                )
                cursor.execute(query, (codigo_limpio, id_obra_actual))
            else:
                # Para nueva obra
                query = (
                    "SELECT COUNT(*) FROM ["
                    + tabla_validada
                    + "] WHERE UPPER(codigo) = ?"
                )
                cursor.execute(query, (codigo_limpio,))

            count = cursor.fetchone()[0]
            return count > 0

        except Exception as e:
            print(f"[ERROR OBRAS] Error validando obra duplicada: {e}")
            return False

    def _verificar_tablas(self):
        """Verifica que las tablas necesarias existan en la base de datos."""
        if not self.db_connection:
            return

        cursor = None
        try:
            cursor = self.db_connection.cursor()

            # Verificar tabla de obras
            cursor.execute(
                "SELECT * FROM sysobjects WHERE name=? AND xtype='U'",
                (self.tabla_obras,),
            )
            if cursor.fetchone():
                print(f"[OBRAS] Tabla '{self.tabla_obras}' verificada correctamente.")

                # Mostrar estructura
                cursor.execute(
                    "SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = ?",
                    (self.tabla_obras,),
                )
                columnas = cursor.fetchall()
                print(f"[OBRAS] Estructura de tabla '{self.tabla_obras}':")
                for columna in columnas:
                    print(f"  - {columna[0]}: {columna[1]}")
            else:
                print(
                    f"[ADVERTENCIA] La tabla '{self.tabla_obras}' no existe en la base de datos."
                )

            # Verificar tabla de detalles de obra
            cursor.execute(
                "SELECT * FROM sysobjects WHERE name=? AND xtype='U'",
                (self.tabla_detalles_obra,),
            )
            if cursor.fetchone():
                print(
                    f"[OBRAS] Tabla '{self.tabla_detalles_obra}' verificada correctamente."
                )
            else:
                print(
                    f"[ADVERTENCIA] La tabla '{self.tabla_detalles_obra}' no existe en la base de datos."
                )

        except Exception as e:
            print(f"[ERROR OBRAS] Error verificando tablas: {e}")
        finally:
            if cursor:
                cursor.close()

    def crear_obra(
        self,
        datos_obra:
        # 🔒 VERIFICACIÓN DE AUTORIZACIÓN REQUERIDA
        # TODO: Implementar @auth_required o verificación manual
        # if not AuthManager.check_permission('crear_obra'):
        #     raise PermissionError("Acceso denegado - Permisos insuficientes")
        Dict[str, Any],
    ) -> tuple[bool, str]:
        """
        Crea una nueva obra en el sistema con sanitización completa de datos.

        Args:
            datos_obra: Diccionario con los datos de la obra

        Returns:
            tuple: (éxito, mensaje)
        """
        if not self.db_connection:
            return False, "Sin conexión a la base de datos"

        cursor = None
        try:
            # 🔒 SANITIZACIÓN Y VALIDACIÓN DE DATOS
            if self.security_available and self.data_sanitizer:
                # Sanitizar todos los datos de entrada
                datos_limpios = self.data_sanitizer.sanitize_dict(datos_obra)

                # Validaciones específicas
                if not datos_limpios.get("codigo"):
                    return False, "El código de obra es requerido"
                if not datos_limpios.get("nombre"):
                    return False, "El nombre de obra es requerido"
                if not datos_limpios.get("cliente"):
                    return False, "El cliente es requerido"

                # Validar email si se proporciona
                if datos_limpios.get("email_contacto"):
                    try:
                        email_limpio = self.data_sanitizer.sanitize_string(
                            datos_limpios["email_contacto"]
                        )
                        if (
                            not email_limpio
                            or len(email_limpio) < 5
                            or "@" not in email_limpio
                        ):
                            return False, "Formato de email inválido"
                        datos_limpios["email_contacto"] = email_limpio
                    except Exception:
                        return False, "Formato de email inválido"

                # Validar teléfono si se proporciona
                if datos_limpios.get("telefono_contacto"):
                    telefono_limpio = self.data_sanitizer.sanitize_string(
                        datos_limpios["telefono_contacto"]
                    )
                    datos_limpios["telefono_contacto"] = telefono_limpio

                # Validar presupuesto
                presupuesto_original = datos_obra.get("presupuesto_total")
                if presupuesto_original and presupuesto_original != "":
                    try:
                        # Usar float manualmente para presupuesto
                        presupuesto_limpio = float(presupuesto_original)
                        if presupuesto_limpio < 0:
                            return False, "El presupuesto no puede ser negativo"
                        datos_limpios["presupuesto_total"] = presupuesto_limpio
                    except (ValueError, TypeError):
                        return False, "Presupuesto inválido"
                else:
                    datos_limpios["presupuesto_total"] = 0.0
            else:
                # Fallback sin sanitización avanzada
                datos_limpios = dict(datos_obra)
                print(
                    "[WARNING OBRAS] Sanitización no disponible, usando datos básicos"
                )

                # Validaciones básicas
                if not datos_limpios.get("codigo"):
                    return False, "El código de obra es requerido"
                if not datos_limpios.get("nombre"):
                    return False, "El nombre de obra es requerido"
                if not datos_limpios.get("cliente"):
                    return False, "El cliente es requerido"

            cursor = self.db_connection.cursor()

            # Verificar que no existe una obra con el mismo código
            cursor.execute(
                "SELECT COUNT(*) FROM obras WHERE codigo = ?",
                (datos_limpios.get("codigo"),),
            )
            if cursor.fetchone()[0] > 0:
                return (
                    False,
                    f"Ya existe una obra con el código {datos_limpios.get('codigo')}",
                )

            # Insertar obra con datos sanitizados
            sql_insert = """
            INSERT INTO obras
            (codigo, nombre, descripcion, cliente, direccion, telefono_contacto,
             email_contacto, fecha_inicio, fecha_fin_estimada, presupuesto_total,
             estado, tipo_obra, prioridad, responsable, observaciones, usuario_creacion)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

            cursor.execute(
                sql_insert,
                (
                    datos_limpios.get("codigo"),
                    datos_limpios.get("nombre"),
                    datos_limpios.get("descripcion", ""),
                    datos_limpios.get("cliente"),
                    datos_limpios.get("direccion", ""),
                    datos_limpios.get("telefono_contacto", ""),
                    datos_limpios.get("email_contacto", ""),
                    datos_limpios.get("fecha_inicio"),
                    datos_limpios.get("fecha_fin_estimada"),
                    datos_limpios.get("presupuesto_total", 0),
                    datos_limpios.get("estado", "PLANIFICACION"),
                    datos_limpios.get("tipo_obra", "CONSTRUCCION"),
                    datos_limpios.get("prioridad", "MEDIA"),
                    datos_limpios.get("responsable"),
                    datos_limpios.get("observaciones", ""),
                    datos_limpios.get("usuario_creacion", "SISTEMA"),
                ),
            )

            self.db_connection.commit()

            print(f"[OBRAS] Obra creada exitosamente: {datos_limpios.get('codigo')}")
            return True, f"Obra {datos_limpios.get('codigo')} creada exitosamente"

        except Exception as e:
            print(f"[ERROR OBRAS] Error creando obra: {e}")
            if self.db_connection:
                try:
                    self.db_connection.rollback()
                except:
                    pass
            return False, f"Error creando obra: {str(e)}"
        finally:
            if cursor:
                cursor.close()

    def obtener_todas_obras(self):
        """Obtiene todas las obras de la base de datos como lista de diccionarios."""
        cursor = None
        try:
            cursor = self.db_connection.cursor()
            cursor.execute(
                """
                SELECT
                    id, codigo, nombre, cliente, estado, responsable,
                    fecha_inicio, fecha_fin_estimada, presupuesto_total,
                    tipo_obra, progreso, descripcion, ubicacion,
                    created_at, updated_at
                FROM obras
                ORDER BY fecha_inicio DESC
                """
            )
            rows = cursor.fetchall()
            columnas = [column[0] for column in cursor.description]
            return [dict(zip(columnas, row)) for row in rows]
        except Exception as e:
            print(f"Error obteniendo obras: {e}")
            return []
        finally:
            if cursor:
                cursor.close()

    def obtener_obra_por_id(self, obra_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene una obra específica por su ID."""
        if not self.db_connection:
            return None

        cursor = None
        try:
            cursor = self.db_connection.cursor()
            cursor.execute(
                """
                SELECT
                    id, codigo, nombre, cliente, estado, responsable,
                    fecha_inicio, fecha_fin_estimada, presupuesto_total,
                    tipo_obra, progreso, descripcion, ubicacion,
                    created_at, updated_at
                FROM obras
                WHERE id = ?
            """,
                (obra_id,),
            )

            return cursor.fetchone()

        except Exception as e:
            print(f"Error obteniendo obra {obra_id}: {e}")
            return None
        finally:
            if cursor:
                cursor.close()

    def obtener_obra_por_codigo(self, codigo: str) -> Optional[Dict[str, Any]]:
        """Obtiene una obra específica por su código."""
        if not self.db_connection:
            return None

        cursor = None
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("SELECT * FROM obras WHERE codigo = ?", (codigo,))

            row = cursor.fetchone()
            if row:
                columnas = [column[0] for column in cursor.description]
                return dict(zip(columnas, row))
            return None

        except Exception as e:
            print(f"[ERROR OBRAS] Error obteniendo obra: {e}")
            return None
        finally:
            if cursor:
                cursor.close()

    def actualizar_obra(
        self,
        obra_id:
        # 🔒 VERIFICACIÓN DE AUTORIZACIÓN REQUERIDA
        # TODO: Implementar @auth_required o verificación manual
        # if not AuthManager.check_permission('actualizar_obra'):
        #     raise PermissionError("Acceso denegado - Permisos insuficientes")
        int,
        datos_obra: Dict[str, Any],
    ) -> tuple[bool, str]:
        """
        Actualiza los datos de una obra.

        Args:
            obra_id: ID de la obra a actualizar
            datos_obra: Diccionario con los nuevos datos

        Returns:
            tuple: (éxito, mensaje)
        """
        if not self.db_connection:
            return False, "Sin conexión a la base de datos"

        cursor = None
        try:
            cursor = self.db_connection.cursor()

            sql_update = """
            UPDATE obras
            SET nombre = ?, descripcion = ?, cliente = ?, direccion = ?,
                telefono_contacto = ?, email_contacto = ?, fecha_fin_estimada = ?,
                presupuesto_total = ?, estado = ?, tipo_obra = ?, prioridad = ?,
                responsable = ?, observaciones = ?, fecha_modificacion = GETDATE(),
                usuario_modificacion = ?
            WHERE id = ?
            """

            cursor.execute(
                sql_update,
                (
                    datos_obra.get("nombre"),
                    datos_obra.get("descripcion"),
                    datos_obra.get("cliente"),
                    datos_obra.get("direccion"),
                    datos_obra.get("telefono_contacto"),
                    datos_obra.get("email_contacto"),
                    datos_obra.get("fecha_fin_estimada"),
                    datos_obra.get("presupuesto_total"),
                    datos_obra.get("estado"),
                    datos_obra.get("tipo_obra"),
                    datos_obra.get("prioridad"),
                    datos_obra.get("responsable"),
                    datos_obra.get("observaciones"),
                    datos_obra.get("usuario_modificacion", "SISTEMA"),
                    obra_id,
                ),
            )

            if cursor.rowcount > 0:
                self.db_connection.commit()
                return True, "Obra actualizada exitosamente"
            else:
                return False, "No se encontró la obra a actualizar"

        except Exception as e:
            print(f"[ERROR OBRAS] Error actualizando obra: {e}")
            if self.db_connection:
                try:
                    self.db_connection.rollback()
                except:
                    pass
            return False, f"Error actualizando obra: {str(e)}"
        finally:
            if cursor:
                cursor.close()

    def cambiar_estado_obra(
        self,
        obra_id:
        # 🔒 VERIFICACIÓN DE AUTORIZACIÓN REQUERIDA
        # TODO: Implementar @auth_required o verificación manual
        # if not AuthManager.check_permission('cambiar_estado_obra'):
        #     raise PermissionError("Acceso denegado - Permisos insuficientes")
        int,
        nuevo_estado: str,
        usuario: str = "SISTEMA",
    ) -> tuple[bool, str]:
        """
        Cambia el estado de una obra.

        Args:
            obra_id: ID de la obra
            nuevo_estado: Nuevo estado (PLANIFICACION, EN_PROCESO, PAUSADA, FINALIZADA, CANCELADA)
            usuario: Usuario que realiza el cambio

        Returns:
            tuple: (éxito, mensaje)
        """
        estados_validos = [
            "PLANIFICACION",
            "EN_PROCESO",
            "PAUSADA",
            "FINALIZADA",
            "CANCELADA",
        ]

        if nuevo_estado not in estados_validos:
            return (
                False,
                f"Estado no válido. Estados permitidos: {', '.join(estados_validos)}",
            )

        if not self.db_connection:
            return False, "Sin conexión a la base de datos"

        cursor = None
        try:
            cursor = self.db_connection.cursor()

            # Obtener estado actual
            cursor.execute("SELECT estado FROM obras WHERE id = ?", (obra_id,))
            resultado = cursor.fetchone()
            if not resultado:
                return False, "Obra no encontrada"

            estado_actual = resultado[0]

            # Actualizar estado
            sql_update = """
            UPDATE obras
            SET estado = ?, fecha_modificacion = GETDATE(), usuario_modificacion = ?
            WHERE id = ?
            """

            cursor.execute(sql_update, (nuevo_estado, usuario, obra_id))
            self.db_connection.commit()

            # Si se finaliza la obra, actualizar fecha de finalización
            if nuevo_estado == "FINALIZADA":
                cursor.execute(
                    "UPDATE obras SET fecha_fin_real = GETDATE() WHERE id = ?",
                    (obra_id,),
                )
                self.db_connection.commit()

            return True, f"Estado cambiado de {estado_actual} a {nuevo_estado}"

        except Exception as e:
            print(f"[ERROR OBRAS] Error cambiando estado: {e}")
            if self.db_connection:
                try:
                    self.db_connection.rollback()
                except:
                    pass
            return False, f"Error cambiando estado: {str(e)}"
        finally:
            if cursor:
                cursor.close()

    def obtener_obras_filtradas(
        self,
        estado: str = "",
        responsable: str = "",
        fecha_inicio: Optional[datetime.date] = None,
        fecha_fin: Optional[datetime.date] = None,
    ) -> List[Dict[str, Any]]:
        """
        Obtiene obras con filtros aplicados.

        Args:
            estado: Filtrar por estado específico
            responsable: Filtrar por responsable
            fecha_inicio: Filtrar desde fecha
            fecha_fin: Filtrar hasta fecha

        Returns:
            List: Lista de obras que cumplen los filtros
        """
        if not self.db_connection:
            return []

        try:
            cursor = self.db_connection.cursor()

            conditions = []
            params = []

            if estado:
                conditions.append("estado = ?")
                params.append(estado)

            if responsable:
                conditions.append("responsable LIKE ?")
                params.append(f"%{responsable}%")

            if fecha_inicio:
                conditions.append("fecha_inicio >= ?")
                params.append(fecha_inicio)

            if fecha_fin:
                conditions.append("fecha_inicio <= ?")
                params.append(fecha_fin)

            where_clause = ""
            if conditions:
                where_clause = "WHERE " + " AND ".join(conditions)

            # SECURITY: Validar nombre de tabla para prevenir SQL injection
            tabla_segura = "obras"
            if SQL_SECURITY_AVAILABLE:
                try:
                    from rexus.utils.sql_security import sql_validator

                    if tabla_segura not in sql_validator.ALLOWED_TABLES:
                        sql_validator.add_allowed_table(tabla_segura)
                    tabla_validada = validate_table_name(tabla_segura)
                except SQLSecurityError as e:
                    print(f"[SECURITY ERROR] Tabla no válida: {e}")
                    return []
            else:
                tabla_validada = tabla_segura

            base_query = f"SELECT * FROM [{tabla_validada}]"
            if where_clause:
                sql_select = (
                    base_query + " " + where_clause + " ORDER BY fecha_inicio DESC"
                )
            else:
                sql_select = base_query + " ORDER BY fecha_inicio DESC"

            cursor.execute(sql_select, params)
            columnas = [column[0] for column in cursor.description]
            obras = []

            for row in cursor.fetchall():
                obra = dict(zip(columnas, row))
                obras.append(obra)

            return obras

        except Exception as e:
            print(f"[ERROR OBRAS] Error obteniendo obras filtradas: {e}")
            return []

    def obtener_estadisticas_obras(self) -> Dict[str, Any]:
        """Obtiene estadísticas generales de obras."""
        if not self.db_connection:
            return {}

        try:
            cursor = self.db_connection.cursor()

            estadisticas = {}

            # Total de obras
            cursor.execute("SELECT COUNT(*) FROM obras")
            estadisticas["total_obras"] = cursor.fetchone()[0]

            # Obras por estado
            cursor.execute(
                """
                SELECT estado, COUNT(*) as cantidad
                FROM obras
                GROUP BY estado
                ORDER BY cantidad DESC
            """
            )
            estadisticas["obras_por_estado"] = [
                {"estado": row[0], "cantidad": row[1]} for row in cursor.fetchall()
            ]

            # Obras activas (en proceso y planificación)
            cursor.execute(
                """
                SELECT COUNT(*) FROM obras
                WHERE estado IN ('PLANIFICACION', 'EN_PROCESO')
            """
            )
            estadisticas["obras_activas"] = cursor.fetchone()[0]

            # Presupuesto total
            cursor.execute("SELECT SUM(presupuesto_total) FROM obras")
            resultado = cursor.fetchone()[0]
            estadisticas["presupuesto_total"] = resultado if resultado else 0

            # Obras por responsable
            cursor.execute(
                """
                SELECT responsable, COUNT(*) as cantidad
                FROM obras
                GROUP BY responsable
                ORDER BY cantidad DESC
            """
            )
            estadisticas["obras_por_responsable"] = [
                {"responsable": row[0], "cantidad": row[1]} for row in cursor.fetchall()
            ]

            return estadisticas

        except Exception as e:
            print(f"[ERROR OBRAS] Error obteniendo estadísticas: {e}")
            return {}

    def eliminar_obra(
        self,
        obra_id:
        # 🔒 VERIFICACIÓN DE AUTORIZACIÓN REQUERIDA
        # TODO: Implementar @auth_required o verificación manual
        # if not AuthManager.check_permission('eliminar_obra'):
        #     raise PermissionError("Acceso denegado - Permisos insuficientes")
        int,
        usuario: str = "SISTEMA",
    ) -> tuple[bool, str]:
        """
        Elimina una obra del sistema (solo si no tiene movimientos asociados).

        Args:
            obra_id: ID de la obra a eliminar
            usuario: Usuario que realiza la eliminación

        Returns:
            tuple: (éxito, mensaje)
        """
        if not self.db_connection:
            return False, "Sin conexión a la base de datos"

        try:
            cursor = self.db_connection.cursor()

            # Verificar si la obra existe
            cursor.execute("SELECT codigo, estado FROM obras WHERE id = ?", (obra_id,))
            resultado = cursor.fetchone()
            if not resultado:
                return False, "Obra no encontrada"

            codigo_obra, estado = resultado

            # Verificar si tiene detalles asociados
            cursor.execute(
                "SELECT COUNT(*) FROM detalles_obra WHERE obra_id = ?", (obra_id,)
            )
            if cursor.fetchone()[0] > 0:
                return (
                    False,
                    "No se puede eliminar la obra porque tiene detalles asociados",
                )

            # Solo permitir eliminar obras en estado PLANIFICACION o CANCELADA
            if estado not in ["PLANIFICACION", "CANCELADA"]:
                return False, f"No se puede eliminar una obra en estado {estado}"

            # Eliminar la obra
            cursor.execute("DELETE FROM obras WHERE id = ?", (obra_id,))
            self.db_connection.commit()

            return True, f"Obra {codigo_obra} eliminada exitosamente"

        except Exception as e:
            print(f"[ERROR OBRAS] Error eliminando obra: {e}")
            return False, f"Error eliminando obra: {str(e)}"
