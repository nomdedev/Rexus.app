"""
Modelo de Programación de Mantenimiento

Maneja la programación automática y calendario de mantenimientos.
"""

from datetime import date, timedelta
from typing import Dict, List, Optional, Any
from rexus.utils.security import SecurityUtils


class ProgramacionMantenimientoModel:
    """Modelo para gestionar la programación automática de mantenimientos."""

    def __init__(self, db_connection=None):
        """
        Inicializa el modelo de programación de mantenimiento.

        Args:
            db_connection: Conexión a la base de datos
        """
        self.db_connection = db_connection
        self.tabla_programacion = "programacion_mantenimiento"
        self.tabla_plantillas = "plantillas_mantenimiento"
        self._crear_tablas_si_no_existen()

    def _crear_tablas_si_no_existen(self):
        """Verifica que las tablas de programación existan."""
        if not self.db_connection:
            return

        try:
            cursor = self.db_connection.cursor()
            tablas = [self.tabla_programacion, self.tabla_plantillas]

            for tabla in tablas:
                cursor.execute(
                    "SELECT * FROM sysobjects WHERE name=? AND xtype='U'",
                    (tabla,),
                )
                if cursor.fetchone():
                    print(f"[PROGRAMACION] Tabla '{tabla}' verificada.")
                else:
                    print(f"[ADVERTENCIA] Tabla '{tabla}' no existe.")

        except Exception as e:
            print(f"[ERROR PROGRAMACION] Error verificando tablas: {e}")

    def crear_programacion(
        self,
        equipo_id: int,
        tipo_mantenimiento: str,
        frecuencia_dias: int,
        descripcion: str = "",
        fecha_inicio: date = None,
        activo: bool = True,
        responsable: str = "",
        costo_estimado: float = 0.0,
        observaciones: str = ""
    ) -> bool:
        """
        Crea una nueva programación de mantenimiento.

        Args:
            equipo_id: ID del equipo
            tipo_mantenimiento: Tipo (PREVENTIVO, CORRECTIVO, PREDICTIVO)
            frecuencia_dias: Frecuencia en días
            descripcion: Descripción del mantenimiento
            fecha_inicio: Fecha de inicio (por defecto hoy)
            activo: Si está activo
            responsable: Responsable del mantenimiento
            costo_estimado: Costo estimado
            observaciones: Observaciones adicionales

        Returns:
            bool: True si se creó exitosamente
        """
        if not self.db_connection:
            print("[WARN PROGRAMACION] Sin conexión BD")
            return False

        try:
            if fecha_inicio is None:
                fecha_inicio = date.today()

            # Sanitizar datos
            descripcion_sanitizada = SecurityUtils.sanitize_sql_input(descripcion)
            responsable_sanitizado = SecurityUtils.sanitize_sql_input(responsable)
            observaciones_sanitizadas = SecurityUtils.sanitize_sql_input(observaciones)

            cursor = self.db_connection.cursor()

            sql_insert = """
            INSERT INTO programacion_mantenimiento
            (equipo_id, tipo_mantenimiento, frecuencia_dias, descripcion,
             fecha_inicio, fecha_proximo, activo, responsable, costo_estimado,
             observaciones, fecha_creacion, fecha_actualizacion)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE(), GETDATE())
            """

            # Calcular próxima fecha
            fecha_proximo = fecha_inicio + timedelta(days=frecuencia_dias)

            cursor.execute(
                sql_insert,
                (
                    equipo_id,
                    tipo_mantenimiento,
                    frecuencia_dias,
                    descripcion_sanitizada,
                    fecha_inicio,
                    fecha_proximo,
                    1 if activo else 0,
                    responsable_sanitizado,
                    costo_estimado,
                    observaciones_sanitizadas,
                ),
            )

            self.db_connection.commit()
            print(f"[PROGRAMACION] Programación creada para equipo {equipo_id}")
            return True

        except Exception as e:
            print(f"[ERROR PROGRAMACION] Error creando programación: {e}")
            return False

    def obtener_programaciones_activas(self) -> List[Dict]:
        """
        Obtiene todas las programaciones activas.

        Returns:
            List[Dict]: Lista de programaciones activas
        """
        if not self.db_connection:
            return self._get_programaciones_demo()

        try:
            cursor = self.db_connection.cursor()

            sql_select = """
            SELECT
                p.id, p.equipo_id, e.nombre as equipo_nombre, e.codigo as equipo_codigo,
                p.tipo_mantenimiento, p.frecuencia_dias, p.descripcion,
                p.fecha_inicio, p.fecha_proximo, p.responsable, p.costo_estimado,
                p.observaciones, p.fecha_creacion,
                DATEDIFF(day, GETDATE(), p.fecha_proximo) as dias_hasta_proximo
            FROM programacion_mantenimiento p
            INNER JOIN equipos e ON p.equipo_id = e.id
            WHERE p.activo = 1 AND e.activo = 1
            ORDER BY p.fecha_proximo ASC
            """

            cursor.execute(sql_select)
            rows = cursor.fetchall()

            columns = [desc[0] for desc in cursor.description]
            programaciones = []

            for row in rows:
                programacion = dict(zip(columns, row))

                # Determinar estado basado en días hasta próximo
                dias_hasta = programacion.get('dias_hasta_proximo', 0)
                if dias_hasta < 0:
                    programacion['estado'] = 'VENCIDO'
                elif dias_hasta <= 7:
                    programacion['estado'] = 'URGENTE'
                elif dias_hasta <= 30:
                    programacion['estado'] = 'PRÓXIMO'
                else:
                    programacion['estado'] = 'PROGRAMADO'

                programaciones.append(programacion)

            print(f"[PROGRAMACION] Obtenidas {len(programaciones)} programaciones activas")
            return programaciones

        except Exception as e:
            print(f"[ERROR PROGRAMACION] Error obteniendo programaciones: {e}")
            return self._get_programaciones_demo()

    def generar_mantenimientos_pendientes(self) -> List[Dict]:
        """
        Genera mantenimientos para programaciones que lo requieren.

        Returns:
            List[Dict]: Lista de mantenimientos generados
        """
        if not self.db_connection:
            return []

        try:
            cursor = self.db_connection.cursor()

            # Buscar programaciones que necesitan generar mantenimiento
            sql_pendientes = """
            SELECT
                p.id, p.equipo_id, p.tipo_mantenimiento, p.descripcion,
                p.responsable, p.costo_estimado, p.frecuencia_dias
            FROM programacion_mantenimiento p
            WHERE p.activo = 1
            AND p.fecha_proximo <= GETDATE()
            AND NOT EXISTS (
                SELECT 1 FROM mantenimientos m
                WHERE m.equipo_id = p.equipo_id
                AND m.estado IN ('PROGRAMADO', 'EN_PROGRESO')
                AND m.fecha_programada >= p.fecha_proximo
            )
            """

            cursor.execute(sql_pendientes)
            pendientes = cursor.fetchall()

            mantenimientos_generados = []

            for programacion in pendientes:
                prog_id, equipo_id, tipo, descripcion, responsable, costo, frecuencia = programacion

                # Crear mantenimiento
                sql_crear_mant = """
                INSERT INTO mantenimientos
                (equipo_id, tipo, descripcion, fecha_programada, estado,
                 responsable, costo_estimado, fecha_creacion, programacion_id)
                VALUES (?, ?, ?, GETDATE(), 'PROGRAMADO', ?, ?, GETDATE(), ?)
                """

                cursor.execute(sql_crear_mant, (
                    equipo_id, tipo, descripcion, responsable, costo, prog_id
                ))

                # Actualizar próxima fecha en programación
                sql_actualizar_prog = """
                UPDATE programacion_mantenimiento
                SET fecha_proximo = DATEADD(day, ?, fecha_proximo),
                    fecha_actualizacion = GETDATE()
                WHERE id = ?
                """

                cursor.execute(sql_actualizar_prog, (frecuencia, prog_id))

                mantenimientos_generados.append({
                    'equipo_id': equipo_id,
                    'tipo': tipo,
                    'descripcion': descripcion,
                    'programacion_id': prog_id
                })

            self.db_connection.commit()
            print(f"[PROGRAMACION] Generados {len(mantenimientos_generados)} mantenimientos")
            return mantenimientos_generados

        except Exception as e:
            print(f"[ERROR PROGRAMACION] Error generando mantenimientos: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return []

    def obtener_calendario_mantenimiento(self, fecha_inicio: date, fecha_fin: date) -> List[Dict]:
        """
        Obtiene calendario de mantenimientos para un rango de fechas.

        Args:
            fecha_inicio: Fecha inicio del calendario
            fecha_fin: Fecha fin del calendario

        Returns:
            List[Dict]: Lista de eventos del calendario
        """
        if not self.db_connection:
            return self._get_calendario_demo(fecha_inicio, fecha_fin)

        try:
            cursor = self.db_connection.cursor()

            sql_calendario = """
            SELECT
                m.id, m.equipo_id, e.nombre as equipo_nombre,
                m.tipo, m.descripcion, m.fecha_programada, m.estado,
                m.responsable, m.costo_estimado,
                p.frecuencia_dias
            FROM mantenimientos m
            INNER JOIN equipos e ON m.equipo_id = e.id
            LEFT JOIN programacion_mantenimiento p ON m.programacion_id = p.id
            WHERE m.fecha_programada BETWEEN ? AND ?

            UNION ALL

            SELECT
                NULL as id, p.equipo_id, e.nombre as equipo_nombre,
                p.tipo_mantenimiento as tipo, p.descripcion, p.fecha_proximo as fecha_programada,
                'PROGRAMADO' as estado, p.responsable, p.costo_estimado,
                p.frecuencia_dias
            FROM programacion_mantenimiento p
            INNER JOIN equipos e ON p.equipo_id = e.id
            WHERE p.activo = 1
            AND p.fecha_proximo BETWEEN ? AND ?
            AND NOT EXISTS (
                SELECT 1 FROM mantenimientos m
                WHERE m.equipo_id = p.equipo_id
                AND m.fecha_programada = p.fecha_proximo
            )

            ORDER BY fecha_programada ASC
            """

            cursor.execute(sql_calendario,
(fecha_inicio,
                fecha_fin,
                fecha_inicio,
                fecha_fin))
            rows = cursor.fetchall()

            columns = [desc[0] for desc in cursor.description]
            eventos = []

            for row in rows:
                evento = dict(zip(columns, row))

                # Agregar información adicional para el calendario
                evento['es_programacion'] = evento['id'] is None
                evento['color'] = self._get_color_por_tipo_estado(
                    evento['tipo'], evento['estado']
                )

                eventos.append(evento)

            print(f"[PROGRAMACION] Obtenidos {len(eventos)} eventos de calendario")
            return eventos

        except Exception as e:
            print(f"[ERROR PROGRAMACION] Error obteniendo calendario: {e}")
            return self._get_calendario_demo(fecha_inicio, fecha_fin)

    def crear_plantilla_mantenimiento(
        self,
        nombre: str,
        tipo_mantenimiento: str,
        descripcion: str,
        frecuencia_sugerida: int,
        tareas: List[str],
        tiempo_estimado: int = 0,
        costo_estimado: float = 0.0,
        requisitos: str = ""
    ) -> bool:
        """
        Crea una plantilla reutilizable de mantenimiento.

        Args:
            nombre: Nombre de la plantilla
            tipo_mantenimiento: Tipo de mantenimiento
            descripcion: Descripción
            frecuencia_sugerida: Frecuencia sugerida en días
            tareas: Lista de tareas a realizar
            tiempo_estimado: Tiempo estimado en horas
            costo_estimado: Costo estimado
            requisitos: Requisitos especiales

        Returns:
            bool: True si se creó exitosamente
        """
        if not self.db_connection:
            return False

        try:
            # Sanitizar datos
            nombre_sanitizado = SecurityUtils.sanitize_sql_input(nombre)
            descripcion_sanitizada = SecurityUtils.sanitize_sql_input(descripcion)
            requisitos_sanitizados = SecurityUtils.sanitize_sql_input(requisitos)

            # Convertir lista de tareas a JSON
            import json
            tareas_json = json.dumps(tareas, ensure_ascii=False)

            cursor = self.db_connection.cursor()

            sql_insert = """
            INSERT INTO plantillas_mantenimiento
            (nombre, tipo_mantenimiento, descripcion, frecuencia_sugerida,
             tareas_json, tiempo_estimado, costo_estimado, requisitos,
             activo, fecha_creacion)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, GETDATE())
            """

            cursor.execute(sql_insert, (
                nombre_sanitizado,
                tipo_mantenimiento,
                descripcion_sanitizada,
                frecuencia_sugerida,
                tareas_json,
                tiempo_estimado,
                costo_estimado,
                requisitos_sanitizados
            ))

            self.db_connection.commit()
            print(f"[PROGRAMACION] Plantilla '{nombre}' creada exitosamente")
            return True

        except Exception as e:
            print(f"[ERROR PROGRAMACION] Error creando plantilla: {e}")
            return False

    def obtener_plantillas_mantenimiento(self) -> List[Dict]:
        """
        Obtiene todas las plantillas de mantenimiento disponibles.

        Returns:
            List[Dict]: Lista de plantillas
        """
        if not self.db_connection:
            return self._get_plantillas_demo()

        try:
            cursor = self.db_connection.cursor()

            sql_select = """
            SELECT
                id, nombre, tipo_mantenimiento, descripcion, frecuencia_sugerida,
                tareas_json, tiempo_estimado, costo_estimado, requisitos,
                fecha_creacion
            FROM plantillas_mantenimiento
            WHERE activo = 1
            ORDER BY nombre ASC
            """

            cursor.execute(sql_select)
            rows = cursor.fetchall()

            columns = [desc[0] for desc in cursor.description]
            plantillas = []

            for row in rows:
                plantilla = dict(zip(columns, row))

                # Parsear JSON de tareas
                try:
                    import json
                    plantilla['tareas'] = json.loads(plantilla['tareas_json'])
                except (json.JSONDecodeError, TypeError) as e:
                    print(f"[WARNING PROGRAMACION] Error parsing tasks JSON: {e}")
                    plantilla['tareas'] = []

                del plantilla['tareas_json']
                plantillas.append(plantilla)

            print(f"[PROGRAMACION] Obtenidas {len(plantillas)} plantillas")
            return plantillas

        except Exception as e:
            print(f"[ERROR PROGRAMACION] Error obteniendo plantillas: {e}")
            return self._get_plantillas_demo()

    def aplicar_plantilla_a_equipo(self,
plantilla_id: int,
        equipo_id: int,
        responsable: str = "") -> bool:
        """
        Aplica una plantilla de mantenimiento a un equipo específico.

        Args:
            plantilla_id: ID de la plantilla
            equipo_id: ID del equipo
            responsable: Responsable del mantenimiento

        Returns:
            bool: True si se aplicó exitosamente
        """
        if not self.db_connection:
            return False

        try:
            cursor = self.db_connection.cursor()

            # Obtener datos de la plantilla
            cursor.execute(
                "SELECT * FROM plantillas_mantenimiento WHERE id = ? AND activo = 1",
                (plantilla_id,)
            )
            plantilla = cursor.fetchone()

            if not plantilla:
                print(f"[ERROR PROGRAMACION] Plantilla {plantilla_id} no encontrada")
                return False

            # Crear programación basada en la plantilla
            exito = self.crear_programacion(
                equipo_id=equipo_id,
                tipo_mantenimiento=plantilla[2],  # tipo_mantenimiento
                frecuencia_dias=plantilla[4],      # frecuencia_sugerida
                descripcion=plantilla[3],          # descripcion
                responsable=responsable,
                costo_estimado=plantilla[7],       # costo_estimado
                observaciones=f"Creado desde plantilla: {plantilla[1]}"  # nombre
            )

            if exito:
                print(f"[PROGRAMACION] Plantilla aplicada a equipo {equipo_id}")

            return exito

        except Exception as e:
            print(f"[ERROR PROGRAMACION] Error aplicando plantilla: {e}")
            return False

    def obtener_estadisticas_programacion(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de la programación de mantenimientos.

        Returns:
            Dict: Estadísticas de programación
        """
        if not self.db_connection:
            return self._get_estadisticas_demo()

        try:
            cursor = self.db_connection.cursor()
            stats = {}

            # Total programaciones activas
            cursor.execute("SELECT COUNT(*) FROM programacion_mantenimiento WHERE activo = 1")
            stats['total_programaciones'] = cursor.fetchone()[0]

            # Programaciones por tipo
            cursor.execute("""
                SELECT tipo_mantenimiento, COUNT(*)
                FROM programacion_mantenimiento
                WHERE activo = 1
                GROUP BY tipo_mantenimiento
            """)
            stats['por_tipo'] = dict(cursor.fetchall())

            # Mantenimientos vencidos
            cursor.execute("""
                SELECT COUNT(*) FROM programacion_mantenimiento
                WHERE activo = 1 AND fecha_proximo < GETDATE()
            """)
            stats['vencidos'] = cursor.fetchone()[0]

            # Próximos 7 días
            cursor.execute("""
                SELECT COUNT(*) FROM programacion_mantenimiento
                WHERE activo = 1
                AND fecha_proximo BETWEEN GETDATE() AND DATEADD(day, 7, GETDATE())
            """)
            stats['proximos_7_dias'] = cursor.fetchone()[0]

            # Próximos 30 días
            cursor.execute("""
                SELECT COUNT(*) FROM programacion_mantenimiento
                WHERE activo = 1
                AND fecha_proximo BETWEEN GETDATE() AND DATEADD(day, 30, GETDATE())
            """)
            stats['proximos_30_dias'] = cursor.fetchone()[0]

            return stats

        except Exception as e:
            print(f"[ERROR PROGRAMACION] Error obteniendo estadísticas: {e}")
            return self._get_estadisticas_demo()

    def _get_color_por_tipo_estado(self, tipo: str, estado: str) -> str:
        """Obtiene color para el calendario basado en tipo y estado."""
        colores = {
            'PREVENTIVO': '#28a745',    # Verde
            'CORRECTIVO': '#dc3545',    # Rojo
            'PREDICTIVO': '#007bff',    # Azul
        }

        if estado == 'VENCIDO':
            return '#dc3545'  # Rojo para vencidos
        elif estado == 'URGENTE':
            return '#fd7e14'  # Naranja para urgentes

        return colores.get(tipo, '#6c757d')  # Gris por defecto

    def _get_programaciones_demo(self) -> List[Dict]:
        """Programaciones demo para testing."""
        return [
            {
                'id': 1,
                'equipo_id': 1,
                'equipo_nombre': 'Compresor Principal',
                'equipo_codigo': 'COMP-001',
                'tipo_mantenimiento': 'PREVENTIVO',
                'frecuencia_dias': 90,
                'descripcion': 'Revisión general y cambio de filtros',
                'fecha_proximo': date.today() + timedelta(days=5),
                'responsable': 'Juan Técnico',
                'costo_estimado': 250.00,
                'dias_hasta_proximo': 5,
                'estado': 'PRÓXIMO'
            },
            {
                'id': 2,
                'equipo_id': 2,
                'equipo_nombre': 'Pulidora Industrial',
                'equipo_codigo': 'PUL-002',
                'tipo_mantenimiento': 'PREVENTIVO',
                'frecuencia_dias': 60,
                'descripcion': 'Lubricación y ajuste de rodamientos',
                'fecha_proximo': date.today() - timedelta(days=2),
                'responsable': 'María Mantenimiento',
                'costo_estimado': 150.00,
                'dias_hasta_proximo': -2,
                'estado': 'VENCIDO'
            }
        ]

    def _get_calendario_demo(self, fecha_inicio: date, fecha_fin: date) -> List[Dict]:
        """Calendario demo para testing."""
        eventos = []
        fecha_actual = fecha_inicio

        while fecha_actual <= fecha_fin:
            if fecha_actual.weekday() == 1:  # Martes
                eventos.append({
                    'id': len(eventos) + 1,
                    'equipo_id': 1,
                    'equipo_nombre': 'Equipo Demo',
                    'tipo': 'PREVENTIVO',
                    'descripcion': 'Mantenimiento semanal',
                    'fecha_programada': fecha_actual,
                    'estado': 'PROGRAMADO',
                    'responsable': 'Técnico Demo',
                    'color': '#28a745',
                    'es_programacion': False
                })

            fecha_actual += timedelta(days=1)

        return eventos

    def _get_plantillas_demo(self) -> List[Dict]:
        """Plantillas demo para testing."""
        return [
            {
                'id': 1,
                'nombre': 'Mantenimiento Compresor',
                'tipo_mantenimiento': 'PREVENTIVO',
                'descripcion': 'Mantenimiento preventivo para compresores',
                'frecuencia_sugerida': 90,
                'tareas': [
                    'Revisar presión de trabajo',
                    'Cambiar filtros de aire',
                    'Verificar niveles de aceite',
                    'Inspeccionar mangueras',
                    'Limpiar serpentines'
                ],
                'tiempo_estimado': 4,
                'costo_estimado': 250.00,
                'requisitos': 'Herramientas básicas, filtros nuevos'
            },
            {
                'id': 2,
                'nombre': 'Mantenimiento Motor Eléctrico',
                'tipo_mantenimiento': 'PREVENTIVO',
                'descripcion': 'Mantenimiento preventivo para motores eléctricos',
                'frecuencia_sugerida': 180,
                'tareas': [
                    'Medir resistencia de bobinados',
                    'Verificar rodamientos',
                    'Limpiar contactos',
                    'Revisar ventilación',
                    'Probar arranque'
                ],
                'tiempo_estimado': 3,
                'costo_estimado': 180.00,
                'requisitos': 'Multímetro, lubricantes'
            }
        ]

    def _get_estadisticas_demo(self) -> Dict[str, Any]:
        """Estadísticas demo para testing."""
        return {
            'total_programaciones': 15,
            'por_tipo': {
                'PREVENTIVO': 10,
                'CORRECTIVO': 3,
                'PREDICTIVO': 2
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
            print(f"[ERROR] Error obteniendo mantenimientos vencidos: {e}")
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
            print(f"[ERROR] Error obteniendo mantenimientos próximos: {e}")
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
            print(f"[ERROR] Error actualizando estado programación: {e}")
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
            print(f"[ERROR] Error obteniendo programación: {e}")
            return None
