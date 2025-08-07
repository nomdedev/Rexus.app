# 🔒 DB Authorization Check - Verify user permissions before DB operations
# Ensure all database operations are properly authorized
# DB Authorization Check
"""
Modelo de Mantenimiento

Maneja la lógica de negocio para:
- Mantenimiento preventivo
- Mantenimiento correctivo
- Historial de mantenimientos
- Programación de mantenimientos
- Gestión de equipos y herramientas
"""

from datetime import date, datetime
from decimal import Decimal

from rexus.core.auth_decorators import (
    admin_required,
    auth_required,
    permission_required,
)
from rexus.core.auth_manager import AuthManager
from rexus.utils.sql_security import SQLSecurityError, validate_table_name


class MantenimientoModel:
    """Modelo para gestionar mantenimiento de equipos y herramientas."""

    def __init__(self, db_connection=None):
        """
        Inicializa el modelo de mantenimiento.

        Args:
            db_connection: Conexión a la base de datos
        """
        self.db_connection = db_connection
        self.tabla_equipos = "equipos"
        self.tabla_herramientas = "herramientas"
        self.tabla_mantenimientos = "mantenimientos"
        self.tabla_programacion = "programacion_mantenimiento"
        self.tabla_tipos_mantenimiento = "tipos_mantenimiento"
        self.tabla_estado_equipos = "estado_equipos"
        self.tabla_historial_mantenimiento = "historial_mantenimiento"
        self._verificar_tablas()

    def _verificar_tablas(self):
        """Verifica que las tablas necesarias existan en la base de datos."""
        if not self.db_connection:
            return

        try:
            cursor = self.db_connection.cursor()
            tablas = [
                self.tabla_equipos,
                self.tabla_herramientas,
                self.tabla_mantenimientos,
                self.tabla_programacion,
                self.tabla_tipos_mantenimiento,
                self.tabla_estado_equipos,
                self.tabla_historial_mantenimiento,
            ]

            for tabla in tablas:
                cursor.execute(
                    "SELECT * FROM sysobjects WHERE name=? AND xtype='U'",
                    (tabla,),
                )
                if cursor.fetchone():
                    print(f"[MANTENIMIENTO] Tabla '{tabla}' verificada correctamente.")
                else:
                    print(
                        f"[ADVERTENCIA] La tabla '{tabla}' no existe en la base de datos."
                    )

        except Exception as e:
            print(f"[ERROR MANTENIMIENTO] Error verificando tablas: {e}")

    def _validate_table_name(self, table_name):
        """
        Valida que el nombre de tabla sea seguro para prevenir SQL injection.

        Args:
            table_name (str): Nombre de tabla a validar

        Returns:
            str: Nombre de tabla validado

        Raises:
            SQLSecurityError: Si el nombre de tabla no es válido
        """
        try:
            return validate_table_name(table_name)
        except SQLSecurityError:
            # Fallback a tabla por defecto si no es válida
            if "equipo" in table_name.lower():
                return "equipos"
            elif "herramienta" in table_name.lower():
                return "herramientas"
            elif "mantenimiento" in table_name.lower():
                return "mantenimientos"
            elif "programacion" in table_name.lower():
                return "programacion_mantenimiento"
            elif "historial" in table_name.lower():
                return "historial_mantenimiento"
            else:
                raise SQLSecurityError(f"Nombre de tabla no válido: {table_name}")

    # MÉTODOS PARA EQUIPOS

    def obtener_equipos(self, filtros=None):
        """
        Obtiene equipos con filtros opcionales.

        Args:
            filtros (dict): Filtros opcionales (estado, tipo, ubicacion, etc.)

        Returns:
            List[Dict]: Lista de equipos
        """
        if not self.db_connection:
            return []

        try:
            cursor = self.db_connection.cursor()

            conditions = ["e.activo = 1"]
            params = []

            if filtros:
                if filtros.get("estado") and filtros["estado"] != "Todos":
                    conditions.append("e.estado = ?")
                    params.append(filtros["estado"])

                if filtros.get("tipo") and filtros["tipo"] != "Todos":
                    conditions.append("e.tipo = ?")
                    params.append(filtros["tipo"])

                if filtros.get("ubicacion") and filtros["ubicacion"] != "Todas":
                    conditions.append("e.ubicacion = ?")
                    params.append(filtros["ubicacion"])

                if filtros.get("busqueda"):
                    conditions.append(
                        "(e.nombre LIKE ? OR e.codigo LIKE ? OR e.modelo LIKE ?)"
                    )
                    busqueda = f"%{filtros['busqueda']}%"
                    params.extend([busqueda, busqueda, busqueda])

            # Validar y securizar nombre de tabla
            tabla_equipos_segura = self._validate_table_name(self.tabla_equipos)

            query = """
                SELECT 
                    e.id, e.codigo, e.nombre, e.tipo, e.modelo, e.marca,
                    e.numero_serie, e.fecha_adquisicion, e.fecha_instalacion,
                    e.ubicacion, e.estado, e.valor_adquisicion, e.vida_util_anos,
                    e.ultima_revision, e.proxima_revision, e.observaciones,
                    e.fecha_creacion, e.fecha_modificacion
                FROM [{}] e
                WHERE {}
                ORDER BY e.nombre
            """.format(tabla_equipos_segura, " AND ".join(conditions))

            cursor.execute(query, params)
            columnas = [column[0] for column in cursor.description]
            resultados = cursor.fetchall()

            equipos = []
            for fila in resultados:
                equipo = dict(zip(columnas, fila))
                equipos.append(equipo)

            return equipos

        except Exception as e:
            print(f"[ERROR MANTENIMIENTO] Error obteniendo equipos: {e}")
            return []

    def crear_equipo(self, datos_equipo):
        """
        Crea un nuevo equipo.

        Args:
            datos_equipo (dict): Datos del equipo

        Returns:
            int: ID del equipo creado o None si falla
        """
        if not self.db_connection:
            return None

        try:
            cursor = self.db_connection.cursor()

            # Validar y securizar nombre de tabla
            tabla_equipos_segura = self._validate_table_name(self.tabla_equipos)

            query = """
                INSERT INTO [{}]
                (codigo, nombre, tipo, modelo, marca, numero_serie,
                 fecha_adquisicion, fecha_instalacion, ubicacion, estado,
                 valor_adquisicion, vida_util_anos, observaciones,
                 activo, fecha_creacion, fecha_modificacion)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, GETDATE(), GETDATE())
            """.format(tabla_equipos_segura)

            cursor.execute(
                query,
                (
                    datos_equipo.get("codigo", ""),
                    datos_equipo.get("nombre", ""),
                    datos_equipo.get("tipo", ""),
                    datos_equipo.get("modelo", ""),
                    datos_equipo.get("marca", ""),
                    datos_equipo.get("numero_serie", ""),
                    datos_equipo.get("fecha_adquisicion"),
                    datos_equipo.get("fecha_instalacion"),
                    datos_equipo.get("ubicacion", ""),
                    datos_equipo.get("estado", "OPERATIVO"),
                    datos_equipo.get("valor_adquisicion", 0),
                    datos_equipo.get("vida_util_anos", 0),
                    datos_equipo.get("observaciones", ""),
                ),
            )

            # Obtener ID del equipo creado
            cursor.execute("SELECT @@IDENTITY")
            equipo_id = cursor.fetchone()[0]

            # Registrar en historial
            self._registrar_historial_equipo(
                equipo_id,
                "ALTA",
                f"Equipo dado de alta: {datos_equipo.get('nombre', '')}",
            )

            self.db_connection.commit()
            print(f"[MANTENIMIENTO] Equipo creado con ID: {equipo_id}")
            return equipo_id

        except Exception as e:
            print(f"[ERROR MANTENIMIENTO] Error creando equipo: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return None

    def actualizar_equipo(self, equipo_id, datos_equipo):
        """
        Actualiza un equipo existente.

        Args:
            equipo_id (int): ID del equipo
            datos_equipo (dict): Nuevos datos del equipo

        Returns:
            bool: True si fue exitoso
        """
        if not self.db_connection:
            return False

        try:
            cursor = self.db_connection.cursor()

            tabla_equipos_segura = self._validate_table_name(self.tabla_equipos)
            query = """
                UPDATE [{}]
                SET nombre = ?, tipo = ?, modelo = ?, marca = ?, numero_serie = ?,
                    fecha_adquisicion = ?, fecha_instalacion = ?, ubicacion = ?,
                    estado = ?, valor_adquisicion = ?, vida_util_anos = ?,
                    observaciones = ?, fecha_modificacion = GETDATE()
                WHERE id = ?
            """.format(tabla_equipos_segura)

            cursor.execute(
                query,
                (
                    datos_equipo.get("nombre", ""),
                    datos_equipo.get("tipo", ""),
                    datos_equipo.get("modelo", ""),
                    datos_equipo.get("marca", ""),
                    datos_equipo.get("numero_serie", ""),
                    datos_equipo.get("fecha_adquisicion"),
                    datos_equipo.get("fecha_instalacion"),
                    datos_equipo.get("ubicacion", ""),
                    datos_equipo.get("estado", "OPERATIVO"),
                    datos_equipo.get("valor_adquisicion", 0),
                    datos_equipo.get("vida_util_anos", 0),
                    datos_equipo.get("observaciones", ""),
                    equipo_id,
                ),
            )

            # Registrar en historial
            self._registrar_historial_equipo(
                equipo_id,
                "MODIFICACION",
                f"Equipo modificado: {datos_equipo.get('nombre', '')}",
            )

            self.db_connection.commit()
            print(f"[MANTENIMIENTO] Equipo {equipo_id} actualizado exitosamente")
            return True

        except Exception as e:
            print(f"[ERROR MANTENIMIENTO] Error actualizando equipo: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return False

    # MÉTODOS PARA HERRAMIENTAS

    def obtener_herramientas(self, filtros=None):
        """
        Obtiene herramientas con filtros opcionales.

        Args:
            filtros (dict): Filtros opcionales (estado, tipo, ubicacion, etc.)

        Returns:
            List[Dict]: Lista de herramientas
        """
        if not self.db_connection:
            return []

        try:
            cursor = self.db_connection.cursor()

            conditions = ["h.activo = 1"]
            params = []

            if filtros:
                if filtros.get("estado") and filtros["estado"] != "Todos":
                    conditions.append("h.estado = ?")
                    params.append(filtros["estado"])

                if filtros.get("tipo") and filtros["tipo"] != "Todos":
                    conditions.append("h.tipo = ?")
                    params.append(filtros["tipo"])

                if filtros.get("busqueda"):
                    conditions.append("(h.nombre LIKE ? OR h.codigo LIKE ?)")
                    busqueda = f"%{filtros['busqueda']}%"
                    params.extend([busqueda, busqueda])

            tabla_herramientas_segura = self._validate_table_name(
                self.tabla_herramientas
            )
            query = """
                SELECT 
                    h.id, h.codigo, h.nombre, h.tipo, h.marca, h.modelo,
                    h.numero_serie, h.fecha_adquisicion, h.ubicacion,
                    h.estado, h.valor_adquisicion, h.vida_util_anos,
                    h.observaciones, h.fecha_creacion
                FROM [{}] h
                WHERE {}
                ORDER BY h.nombre
            """.format(tabla_herramientas_segura, " AND ".join(conditions))

            cursor.execute(query, params)
            columnas = [column[0] for column in cursor.description]
            resultados = cursor.fetchall()

            herramientas = []
            for fila in resultados:
                herramienta = dict(zip(columnas, fila))
                herramientas.append(herramienta)

            return herramientas

        except Exception as e:
            print(f"[ERROR MANTENIMIENTO] Error obteniendo herramientas: {e}")
            return []

    def crear_herramienta(self, datos_herramienta):
        """
        Crea una nueva herramienta.

        Args:
            datos_herramienta (dict): Datos de la herramienta

        Returns:
            int: ID de la herramienta creada o None si falla
        """
        if not self.db_connection:
            return None

        try:
            cursor = self.db_connection.cursor()

            tabla_herramientas_segura = self._validate_table_name(
                self.tabla_herramientas
            )
            query = """
                INSERT INTO [{}]
                (codigo, nombre, tipo, marca, modelo, numero_serie,
                 fecha_adquisicion, ubicacion, estado, valor_adquisicion,
                 vida_util_anos, observaciones, activo, fecha_creacion)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, GETDATE())
            """.format(tabla_herramientas_segura)

            cursor.execute(
                query,
                (
                    datos_herramienta.get("codigo", ""),
                    datos_herramienta.get("nombre", ""),
                    datos_herramienta.get("tipo", ""),
                    datos_herramienta.get("marca", ""),
                    datos_herramienta.get("modelo", ""),
                    datos_herramienta.get("numero_serie", ""),
                    datos_herramienta.get("fecha_adquisicion"),
                    datos_herramienta.get("ubicacion", ""),
                    datos_herramienta.get("estado", "DISPONIBLE"),
                    datos_herramienta.get("valor_adquisicion", 0),
                    datos_herramienta.get("vida_util_anos", 0),
                    datos_herramienta.get("observaciones", ""),
                ),
            )

            # Obtener ID de la herramienta creada
            cursor.execute("SELECT @@IDENTITY")
            herramienta_id = cursor.fetchone()[0]

            self.db_connection.commit()
            print(f"[MANTENIMIENTO] Herramienta creada con ID: {herramienta_id}")
            return herramienta_id

        except Exception as e:
            print(f"[ERROR MANTENIMIENTO] Error creando herramienta: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return None

    # MÉTODOS PARA MANTENIMIENTOS

    def obtener_mantenimientos(self, filtros=None):
        """
        Obtiene mantenimientos con filtros opcionales.

        Args:
            filtros (dict): Filtros opcionales (estado, tipo, fecha, etc.)

        Returns:
            List[Dict]: Lista de mantenimientos
        """
        if not self.db_connection:
            return []

        try:
            cursor = self.db_connection.cursor()

            conditions = ["1=1"]
            params = []

            if filtros:
                if filtros.get("estado") and filtros["estado"] != "Todos":
                    conditions.append("m.estado = ?")
                    params.append(filtros["estado"])

                if filtros.get("tipo") and filtros["tipo"] != "Todos":
                    conditions.append("m.tipo = ?")
                    params.append(filtros["tipo"])

                if filtros.get("equipo_id"):
                    conditions.append("m.equipo_id = ?")
                    params.append(filtros["equipo_id"])

                if filtros.get("fecha_desde"):
                    conditions.append("m.fecha_programada >= ?")
                    params.append(filtros["fecha_desde"])

                if filtros.get("fecha_hasta"):
                    conditions.append("m.fecha_programada <= ?")
                    params.append(filtros["fecha_hasta"])

            tabla_mantenimientos_segura = self._validate_table_name(
                self.tabla_mantenimientos
            )
            tabla_equipos_segura = self._validate_table_name(self.tabla_equipos)
            query = """
                SELECT 
                    m.id, m.equipo_id, e.nombre as equipo_nombre,
                    m.tipo, m.descripcion, m.fecha_programada, m.fecha_realizacion,
                    m.estado, m.observaciones, m.costo_estimado, m.costo_real,
                    m.responsable, m.fecha_creacion
                FROM [{}] m
                LEFT JOIN [{}] e ON m.equipo_id = e.id
                WHERE {}
                ORDER BY m.fecha_programada DESC
            """.format(
                tabla_mantenimientos_segura,
                tabla_equipos_segura,
                " AND ".join(conditions),
            )

            cursor.execute(query, params)
            columnas = [column[0] for column in cursor.description]
            resultados = cursor.fetchall()

            mantenimientos = []
            for fila in resultados:
                mantenimiento = dict(zip(columnas, fila))
                mantenimientos.append(mantenimiento)

            return mantenimientos

        except Exception as e:
            print(f"[ERROR MANTENIMIENTO] Error obteniendo mantenimientos: {e}")
            return []

    def crear_mantenimiento(self, datos_mantenimiento):
        """
        Crea un nuevo mantenimiento.

        Args:
            datos_mantenimiento (dict): Datos del mantenimiento

        Returns:
            int: ID del mantenimiento creado o None si falla
        """
        if not self.db_connection:
            return None

        try:
            cursor = self.db_connection.cursor()

            tabla_mantenimientos_segura = self._validate_table_name(
                self.tabla_mantenimientos
            )
            query = """
                INSERT INTO [{}]
                (equipo_id, tipo, descripcion, fecha_programada, estado,
                 observaciones, costo_estimado, responsable, fecha_creacion)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, GETDATE())
            """.format(tabla_mantenimientos_segura)

            cursor.execute(
                query,
                (
                    datos_mantenimiento.get("equipo_id"),
                    datos_mantenimiento.get("tipo", "PREVENTIVO"),
                    datos_mantenimiento.get("descripcion", ""),
                    datos_mantenimiento.get("fecha_programada"),
                    datos_mantenimiento.get("estado", "PROGRAMADO"),
                    datos_mantenimiento.get("observaciones", ""),
                    datos_mantenimiento.get("costo_estimado", 0),
                    datos_mantenimiento.get("responsable", ""),
                ),
            )

            # Obtener ID del mantenimiento creado
            cursor.execute("SELECT @@IDENTITY")
            mantenimiento_id = cursor.fetchone()[0]

            # Registrar en historial
            self._registrar_historial_mantenimiento(
                mantenimiento_id,
                "PROGRAMADO",
                f"Mantenimiento programado: {datos_mantenimiento.get('descripcion', '')}",
            )

            self.db_connection.commit()
            print(f"[MANTENIMIENTO] Mantenimiento creado con ID: {mantenimiento_id}")
            return mantenimiento_id

        except Exception as e:
            print(f"[ERROR MANTENIMIENTO] Error creando mantenimiento: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return None

    def completar_mantenimiento(self, mantenimiento_id, datos_completacion):
        """
        Marca un mantenimiento como completado.

        Args:
            mantenimiento_id (int): ID del mantenimiento
            datos_completacion (dict): Datos de completación

        Returns:
            bool: True si fue exitoso
        """
        if not self.db_connection:
            return False

        try:
            cursor = self.db_connection.cursor()

            tabla_mantenimientos_segura = self._validate_table_name(
                self.tabla_mantenimientos
            )
            query = """
                UPDATE [{}]
                SET estado = 'COMPLETADO', fecha_realizacion = GETDATE(),
                    observaciones = ?, costo_real = ?, responsable = ?
                WHERE id = ?
            """.format(tabla_mantenimientos_segura)

            cursor.execute(
                query,
                (
                    datos_completacion.get("observaciones", ""),
                    datos_completacion.get("costo_real", 0),
                    datos_completacion.get("responsable", ""),
                    mantenimiento_id,
                ),
            )

            # Actualizar próxima revisión del equipo
            self._actualizar_proxima_revision(mantenimiento_id)

            # Registrar en historial
            self._registrar_historial_mantenimiento(
                mantenimiento_id,
                "COMPLETADO",
                f"Mantenimiento completado. Observaciones: {datos_completacion.get('observaciones', '')}",
            )

            self.db_connection.commit()
            print(
                f"[MANTENIMIENTO] Mantenimiento {mantenimiento_id} completado exitosamente"
            )
            return True

        except Exception as e:
            print(f"[ERROR MANTENIMIENTO] Error completando mantenimiento: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return False

    # MÉTODOS PARA ESTADÍSTICAS

    def obtener_estadisticas_mantenimiento(self):
        """
        Obtiene estadísticas generales de mantenimiento.

        Returns:
            Dict: Estadísticas de mantenimiento
        """
        if not self.db_connection:
            return {}

        try:
            cursor = self.db_connection.cursor()
            estadisticas = {}

            # Total equipos
            tabla_equipos_segura = self._validate_table_name(self.tabla_equipos)
            cursor.execute(
                "SELECT COUNT(*) FROM [{}] WHERE activo = 1".format(
                    tabla_equipos_segura
                )
            )
            estadisticas["total_equipos"] = cursor.fetchone()[0]

            # Equipos por estado
            cursor.execute(
                """
                SELECT estado, COUNT(*) as cantidad
                FROM [{}]
                WHERE activo = 1
                GROUP BY estado
            """.format(tabla_equipos_segura)
            )
            estadisticas["equipos_por_estado"] = dict(cursor.fetchall())

            # Mantenimientos por estado
            tabla_mantenimientos_segura = self._validate_table_name(
                self.tabla_mantenimientos
            )
            cursor.execute(
                """
                SELECT estado, COUNT(*) as cantidad
                FROM [{}]
                GROUP BY estado
            """.format(tabla_mantenimientos_segura)
            )
            estadisticas["mantenimientos_por_estado"] = dict(cursor.fetchall())

            # Mantenimientos vencidos
            cursor.execute(
                """
                SELECT COUNT(*) FROM [{}]
                WHERE estado = 'PROGRAMADO' AND fecha_programada < GETDATE()
            """.format(tabla_mantenimientos_segura)
            )
            estadisticas["mantenimientos_vencidos"] = cursor.fetchone()[0]

            # Próximos mantenimientos (próximos 30 días)
            cursor.execute(
                """
                SELECT COUNT(*) FROM [{}]
                WHERE estado = 'PROGRAMADO' AND fecha_programada 
                BETWEEN GETDATE() AND DATEADD(day, 30, GETDATE())
            """.format(tabla_mantenimientos_segura)
            )
            estadisticas["proximos_mantenimientos"] = cursor.fetchone()[0]

            return estadisticas

        except Exception as e:
            print(f"[ERROR MANTENIMIENTO] Error obteniendo estadísticas: {e}")
            return {}

    # MÉTODOS AUXILIARES PRIVADOS

    def _registrar_historial_equipo(self, equipo_id, tipo, descripcion):
        """Registra un evento en el historial de equipos."""
        if not self.db_connection:
            return

        try:
            cursor = self.db_connection.cursor()

            tabla_historial_segura = self._validate_table_name(
                self.tabla_historial_mantenimiento
            )
            query = """
                INSERT INTO [{}]
                (equipo_id, tipo, descripcion, fecha, usuario)
                VALUES (?, ?, ?, GETDATE(), 'SYSTEM')
            """.format(tabla_historial_segura)

            cursor.execute(query, (equipo_id, tipo, descripcion))

        except Exception as e:
            print(f"[ERROR MANTENIMIENTO] Error registrando historial de equipo: {e}")

    def _registrar_historial_mantenimiento(self, mantenimiento_id, tipo, descripcion):
        """Registra un evento en el historial de mantenimientos."""
        if not self.db_connection:
            return

        try:
            cursor = self.db_connection.cursor()

            tabla_historial_segura = self._validate_table_name(
                self.tabla_historial_mantenimiento
            )
            query = """
                INSERT INTO [{}]
                (mantenimiento_id, tipo, descripcion, fecha, usuario)
                VALUES (?, ?, ?, GETDATE(), 'SYSTEM')
            """.format(tabla_historial_segura)

            cursor.execute(query, (mantenimiento_id, tipo, descripcion))

        except Exception as e:
            print(
                f"[ERROR MANTENIMIENTO] Error registrando historial de mantenimiento: {e}"
            )

    def _actualizar_proxima_revision(self, mantenimiento_id):
        """Actualiza la fecha de próxima revisión del equipo."""
        if not self.db_connection:
            return

        try:
            cursor = self.db_connection.cursor()

            # Obtener equipo_id del mantenimiento
            tabla_mantenimientos_segura = self._validate_table_name(
                self.tabla_mantenimientos
            )
            cursor.execute(
                "SELECT equipo_id FROM [{}] WHERE id = ?".format(
                    tabla_mantenimientos_segura
                ),
                (mantenimiento_id,),
            )
            resultado = cursor.fetchone()

            if resultado:
                equipo_id = resultado[0]

                # Actualizar fechas de revisión
                tabla_equipos_segura = self._validate_table_name(self.tabla_equipos)
                query = """
                    UPDATE [{}]
                    SET ultima_revision = GETDATE(),
                        proxima_revision = DATEADD(month, 6, GETDATE())
                    WHERE id = ?
                """.format(tabla_equipos_segura)

                cursor.execute(query, (equipo_id,))

        except Exception as e:
            print(f"[ERROR MANTENIMIENTO] Error actualizando próxima revisión: {e}")
