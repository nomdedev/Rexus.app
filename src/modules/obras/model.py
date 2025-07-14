"""Modelo de Obras"""

import datetime
from typing import Any, Dict, List, Optional


class ObrasModel:
    def __init__(self, db_connection=None):
        self.db_connection = db_connection
        self.tabla_obras = "obras"
        self.tabla_detalles_obra = "detalles_obra"
        self._verificar_tablas()

    def _verificar_tablas(self):
        """Verifica que las tablas necesarias existan en la base de datos."""
        if not self.db_connection:
            return

        try:
            cursor = self.db_connection.connection.cursor()

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

    def crear_obra(self, datos_obra: Dict[str, Any]) -> tuple[bool, str]:
        """
        Crea una nueva obra en el sistema.

        Args:
            datos_obra: Diccionario con los datos de la obra

        Returns:
            tuple: (éxito, mensaje)
        """
        if not self.db_connection:
            return False, "Sin conexión a la base de datos"

        try:
            cursor = self.db_connection.connection.cursor()

            # Verificar que no existe una obra con el mismo código
            cursor.execute(
                "SELECT COUNT(*) FROM obras WHERE codigo = ?",
                (datos_obra.get("codigo"),),
            )
            if cursor.fetchone()[0] > 0:
                return (
                    False,
                    f"Ya existe una obra con el código {datos_obra.get('codigo')}",
                )

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
                    datos_obra.get("codigo"),
                    datos_obra.get("nombre"),
                    datos_obra.get("descripcion", ""),
                    datos_obra.get("cliente"),
                    datos_obra.get("direccion", ""),
                    datos_obra.get("telefono_contacto", ""),
                    datos_obra.get("email_contacto", ""),
                    datos_obra.get("fecha_inicio"),
                    datos_obra.get("fecha_fin_estimada"),
                    datos_obra.get("presupuesto_total", 0),
                    datos_obra.get("estado", "PLANIFICACION"),
                    datos_obra.get("tipo_obra", "CONSTRUCCION"),
                    datos_obra.get("prioridad", "MEDIA"),
                    datos_obra.get("responsable"),
                    datos_obra.get("observaciones", ""),
                    datos_obra.get("usuario_creacion", "SISTEMA"),
                ),
            )

            self.db_connection.connection.commit()

            print(f"[OBRAS] Obra creada exitosamente: {datos_obra.get('codigo')}")
            return True, f"Obra {datos_obra.get('codigo')} creada exitosamente"

        except Exception as e:
            print(f"[ERROR OBRAS] Error creando obra: {e}")
            return False, f"Error creando obra: {str(e)}"

    def obtener_todas_obras(self):
        """Obtiene todas las obras de la base de datos."""
        try:
            cursor = self.db_connection.connection.cursor()
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

            return cursor.fetchall()

        except Exception as e:
            print(f"Error obteniendo obras: {e}")
            return []

    def obtener_obra_por_id(self, obra_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene una obra específica por su ID."""
        if not self.db_connection:
            return None

        try:
            cursor = self.db_connection.connection.cursor()
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

    def obtener_obra_por_codigo(self, codigo: str) -> Optional[Dict[str, Any]]:
        """Obtiene una obra específica por su código."""
        if not self.db_connection:
            return None

        try:
            cursor = self.db_connection.connection.cursor()
            cursor.execute("SELECT * FROM obras WHERE codigo = ?", (codigo,))

            row = cursor.fetchone()
            if row:
                columnas = [column[0] for column in cursor.description]
                return dict(zip(columnas, row))
            return None

        except Exception as e:
            print(f"[ERROR OBRAS] Error obteniendo obra: {e}")
            return None

    def actualizar_obra(
        self, obra_id: int, datos_obra: Dict[str, Any]
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

        try:
            cursor = self.db_connection.connection.cursor()

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
                self.db_connection.connection.commit()
                return True, "Obra actualizada exitosamente"
            else:
                return False, "No se encontró la obra a actualizar"

        except Exception as e:
            print(f"[ERROR OBRAS] Error actualizando obra: {e}")
            return False, f"Error actualizando obra: {str(e)}"

    def cambiar_estado_obra(
        self, obra_id: int, nuevo_estado: str, usuario: str = "SISTEMA"
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

        try:
            cursor = self.db_connection.connection.cursor()

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
            self.db_connection.connection.commit()

            # Si se finaliza la obra, actualizar fecha de finalización
            if nuevo_estado == "FINALIZADA":
                cursor.execute(
                    "UPDATE obras SET fecha_fin_real = GETDATE() WHERE id = ?",
                    (obra_id,),
                )
                self.db_connection.connection.commit()

            return True, f"Estado cambiado de {estado_actual} a {nuevo_estado}"

        except Exception as e:
            print(f"[ERROR OBRAS] Error cambiando estado: {e}")
            return False, f"Error cambiando estado: {str(e)}"

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
            cursor = self.db_connection.connection.cursor()

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

            base_query = "SELECT * FROM obras"
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
            cursor = self.db_connection.connection.cursor()

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

    def eliminar_obra(self, obra_id: int, usuario: str = "SISTEMA") -> tuple[bool, str]:
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
            cursor = self.db_connection.connection.cursor()

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
            self.db_connection.connection.commit()

            return True, f"Obra {codigo_obra} eliminada exitosamente"

        except Exception as e:
            print(f"[ERROR OBRAS] Error eliminando obra: {e}")
            return False, f"Error eliminando obra: {str(e)}"
