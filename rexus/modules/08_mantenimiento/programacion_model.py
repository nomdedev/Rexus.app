"""
Modelo de Programación de Mantenimiento

Maneja la programación automática y calendario de mantenimientos.
"""


import logging
logger = logging.getLogger(__name__)

                        },
            'vencidos': 2,
            'proximos_7_dias': 4,
            'proximos_30_dias': 8
        }

    def obtener_mantenimientos_vencidos(self) -> List[Dict]:
        """Obtiene mantenimientos vencidos."""
        if not self.db_connection:
            return []

        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                SELECT p.id, p.equipo_id, e.nombre as equipo_nombre, p.tipo_mantenimiento,
                       p.descripcion, p.fecha_proximo, p.responsable
                FROM programacion_mantenimiento p
                INNER JOIN equipos e ON p.equipo_id = e.id
                WHERE p.activo = 1 AND p.fecha_proximo < GETDATE()
                ORDER BY p.fecha_proximo ASC
            """)

            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

        except Exception as e:
            logger.info(f"[ERROR] Error obteniendo mantenimientos vencidos: {e}")
            return []

    def obtener_mantenimientos_proximos(self, dias: int) -> List[Dict]:
        """Obtiene mantenimientos próximos a vencer en N días."""
        if not self.db_connection:
            return []

        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                SELECT p.id, p.equipo_id, e.nombre as equipo_nombre, p.tipo_mantenimiento,
                       p.descripcion, p.fecha_proximo, p.responsable,
                       DATEDIFF(day, GETDATE(), p.fecha_proximo) as dias_hasta
                FROM programacion_mantenimiento p
                INNER JOIN equipos e ON p.equipo_id = e.id
                WHERE p.activo = 1
                AND p.fecha_proximo BETWEEN GETDATE() AND DATEADD(day, ?, GETDATE())
                ORDER BY p.fecha_proximo ASC
            """, (dias,))

            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

        except Exception as e:
            logger.info(f"[ERROR] Error obteniendo mantenimientos próximos: {e}")
            return []

    def actualizar_estado_programacion(self, programacion_id: int, nuevo_estado: str) -> bool:
        """Actualiza el estado de una programación."""
        if not self.db_connection:
            return False

        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                UPDATE programacion_mantenimiento
                SET estado = ?, fecha_actualizacion = GETDATE()
                WHERE id = ?
            """, (nuevo_estado, programacion_id))

            self.db_connection.commit()
            return cursor.rowcount > 0

        except Exception as e:
            logger.info(f"[ERROR] Error actualizando estado programación: {e}")
            return False

    def obtener_programacion(self, programacion_id: int) -> Optional[Dict]:
        """Obtiene una programación por ID."""
        if not self.db_connection:
            return None

        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                SELECT p.*, e.nombre as equipo_nombre
                FROM programacion_mantenimiento p
                INNER JOIN equipos e ON p.equipo_id = e.id
                WHERE p.id = ?
            """, (programacion_id,))

            row = cursor.fetchone()
            if row:
                columns = [desc[0] for desc in cursor.description]
                return dict(zip(columns, row))
            return None

        except Exception as e:
            logger.info(f"[ERROR] Error obteniendo programación: {e}")
            return None
