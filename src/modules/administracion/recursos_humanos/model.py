"""
Modelo de Recursos Humanos

Maneja la lógica de negocio para:
- Gestión de empleados
- Cálculo de nómina
- Control de asistencias
- Bonos y descuentos
- Historial laboral
"""

from datetime import datetime, date
from decimal import Decimal
import calendar


class RecursosHumanosModel:
    """Modelo para gestionar recursos humanos."""

    def __init__(self, db_connection=None):
        """
        Inicializa el modelo de recursos humanos.

        Args:
            db_connection: Conexión a la base de datos
        """
        self.db_connection = db_connection
        self.tabla_empleados = "empleados"
        self.tabla_departamentos = "departamentos"
        self.tabla_asistencias = "asistencias"
        self.tabla_nomina = "nomina"
        self.tabla_bonos = "bonos_descuentos"
        self.tabla_historial = "historial_laboral"
        self._verificar_tablas()

    def _verificar_tablas(self):
        """Verifica que las tablas necesarias existan en la base de datos."""
        if not self.db_connection:
            return

        try:
            cursor = self.db_connection.cursor()
            tablas = [
                self.tabla_empleados,
                self.tabla_departamentos,
                self.tabla_asistencias,
                self.tabla_nomina,
                self.tabla_bonos,
                self.tabla_historial
            ]

            for tabla in tablas:
                cursor.execute(
                    "SELECT * FROM sysobjects WHERE name=? AND xtype='U'",
                    (tabla,),
                )
                if cursor.fetchone():
                    print(f"[RRHH] Tabla '{tabla}' verificada correctamente.")
                else:
                    print(f"[ADVERTENCIA] La tabla '{tabla}' no existe en la base de datos.")

        except Exception as e:
            print(f"[ERROR RRHH] Error verificando tablas: {e}")

    # MÉTODOS PARA EMPLEADOS

    def obtener_todos_empleados(self, filtros=None):
        """
        Obtiene todos los empleados con filtros opcionales.

        Args:
            filtros (dict): Filtros opcionales (departamento, estado, etc.)

        Returns:
            List[Dict]: Lista de empleados
        """
        if not self.db_connection:
            return []

        try:
            cursor = self.db_connection.cursor()

            conditions = ["e.activo = 1"]
            params = []

            if filtros:
                if filtros.get("departamento") and filtros["departamento"] != "Todos":
                    conditions.append("d.nombre = ?")
                    params.append(filtros["departamento"])

                if filtros.get("estado") and filtros["estado"] != "Todos":
                    conditions.append("e.estado = ?")
                    params.append(filtros["estado"])

                if filtros.get("busqueda"):
                    conditions.append("(e.nombre LIKE ? OR e.apellido LIKE ? OR e.dni LIKE ?)")
                    busqueda = f"%{filtros['busqueda']}%"
                    params.extend([busqueda, busqueda, busqueda])

            query = f"""
                SELECT 
                    e.id, e.codigo, e.nombre, e.apellido, e.dni, e.telefono,
                    e.email, e.direccion, e.fecha_nacimiento, e.fecha_ingreso,
                    e.salario_base, e.cargo, e.estado, d.nombre as departamento,
                    e.fecha_creacion, e.fecha_modificacion
                FROM {self.tabla_empleados} e
                LEFT JOIN {self.tabla_departamentos} d ON e.departamento_id = d.id
                WHERE {" AND ".join(conditions)}
                ORDER BY e.apellido, e.nombre
            """

            cursor.execute(query, params)
            columnas = [column[0] for column in cursor.description]
            resultados = cursor.fetchall()

            empleados = []
            for fila in resultados:
                empleado = dict(zip(columnas, fila))
                empleados.append(empleado)

            return empleados

        except Exception as e:
            print(f"[ERROR RRHH] Error obteniendo empleados: {e}")
            return []

    def crear_empleado(self, datos_empleado):
        """
        Crea un nuevo empleado.

        Args:
            datos_empleado (dict): Datos del empleado

        Returns:
            int: ID del empleado creado o None si falla
        """
        if not self.db_connection:
            return None

        try:
            cursor = self.db_connection.cursor()

            query = f"""
                INSERT INTO {self.tabla_empleados}
                (codigo, nombre, apellido, dni, telefono, email, direccion,
                 fecha_nacimiento, fecha_ingreso, salario_base, cargo, 
                 departamento_id, estado, activo, fecha_creacion, fecha_modificacion)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, GETDATE(), GETDATE())
            """

            cursor.execute(query, (
                datos_empleado.get('codigo', ''),
                datos_empleado.get('nombre', ''),
                datos_empleado.get('apellido', ''),
                datos_empleado.get('dni', ''),
                datos_empleado.get('telefono', ''),
                datos_empleado.get('email', ''),
                datos_empleado.get('direccion', ''),
                datos_empleado.get('fecha_nacimiento'),
                datos_empleado.get('fecha_ingreso'),
                datos_empleado.get('salario_base', 0),
                datos_empleado.get('cargo', ''),
                datos_empleado.get('departamento_id'),
                datos_empleado.get('estado', 'ACTIVO')
            ))

            # Obtener ID del empleado creado
            cursor.execute("SELECT @@IDENTITY")
            empleado_id = cursor.fetchone()[0]

            # Registrar en historial
            self._registrar_historial(empleado_id, 'CONTRATACION', 
                                    f"Empleado contratado como {datos_empleado.get('cargo', '')}")

            self.db_connection.commit()
            print(f"[RRHH] Empleado creado con ID: {empleado_id}")
            return empleado_id

        except Exception as e:
            print(f"[ERROR RRHH] Error creando empleado: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return None

    def actualizar_empleado(self, empleado_id, datos_empleado):
        """
        Actualiza un empleado existente.

        Args:
            empleado_id (int): ID del empleado
            datos_empleado (dict): Nuevos datos del empleado

        Returns:
            bool: True si fue exitoso
        """
        if not self.db_connection:
            return False

        try:
            cursor = self.db_connection.cursor()

            # Obtener datos actuales para historial
            cursor.execute(f"SELECT salario_base, cargo, departamento_id FROM {self.tabla_empleados} WHERE id = ?", (empleado_id,))
            datos_actuales = cursor.fetchone()

            query = f"""
                UPDATE {self.tabla_empleados}
                SET nombre = ?, apellido = ?, dni = ?, telefono = ?, email = ?, 
                    direccion = ?, fecha_nacimiento = ?, salario_base = ?, 
                    cargo = ?, departamento_id = ?, estado = ?, fecha_modificacion = GETDATE()
                WHERE id = ?
            """

            cursor.execute(query, (
                datos_empleado.get('nombre', ''),
                datos_empleado.get('apellido', ''),
                datos_empleado.get('dni', ''),
                datos_empleado.get('telefono', ''),
                datos_empleado.get('email', ''),
                datos_empleado.get('direccion', ''),
                datos_empleado.get('fecha_nacimiento'),
                datos_empleado.get('salario_base', 0),
                datos_empleado.get('cargo', ''),
                datos_empleado.get('departamento_id'),
                datos_empleado.get('estado', 'ACTIVO'),
                empleado_id
            ))

            # Registrar cambios en historial
            if datos_actuales:
                if datos_actuales[0] != datos_empleado.get('salario_base', 0):
                    self._registrar_historial(empleado_id, 'CAMBIO_SALARIO', 
                                            f"Salario cambiado de ${datos_actuales[0]} a ${datos_empleado.get('salario_base', 0)}")
                
                if datos_actuales[1] != datos_empleado.get('cargo', ''):
                    self._registrar_historial(empleado_id, 'PROMOCION', 
                                            f"Cargo cambiado de {datos_actuales[1]} a {datos_empleado.get('cargo', '')}")

            self.db_connection.commit()
            print(f"[RRHH] Empleado {empleado_id} actualizado exitosamente")
            return True

        except Exception as e:
            print(f"[ERROR RRHH] Error actualizando empleado: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return False

    def eliminar_empleado(self, empleado_id):
        """
        Elimina un empleado (marca como inactivo).

        Args:
            empleado_id (int): ID del empleado

        Returns:
            bool: True si fue exitoso
        """
        if not self.db_connection:
            return False

        try:
            cursor = self.db_connection.cursor()

            query = f"""
                UPDATE {self.tabla_empleados}
                SET activo = 0, estado = 'INACTIVO', fecha_modificacion = GETDATE()
                WHERE id = ?
            """

            cursor.execute(query, (empleado_id,))
            
            # Registrar en historial
            self._registrar_historial(empleado_id, 'DESPIDO', "Empleado dado de baja")

            self.db_connection.commit()
            print(f"[RRHH] Empleado {empleado_id} eliminado exitosamente")
            return True

        except Exception as e:
            print(f"[ERROR RRHH] Error eliminando empleado: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return False

    # MÉTODOS PARA NÓMINA

    def calcular_nomina(self, mes, anio, empleado_id=None):
        """
        Calcula la nómina para un período específico.

        Args:
            mes (int): Mes (1-12)
            anio (int): Año
            empleado_id (int): ID específico del empleado o None para todos

        Returns:
            List[Dict]: Lista con cálculos de nómina
        """
        if not self.db_connection:
            return []

        try:
            cursor = self.db_connection.cursor()

            # Obtener empleados activos
            empleados_query = f"""
                SELECT e.id, e.nombre, e.apellido, e.salario_base, e.cargo,
                       d.nombre as departamento
                FROM {self.tabla_empleados} e
                LEFT JOIN {self.tabla_departamentos} d ON e.departamento_id = d.id
                WHERE e.activo = 1 AND e.estado = 'ACTIVO'
            """
            
            if empleado_id:
                empleados_query += " AND e.id = ?"
                cursor.execute(empleados_query, (empleado_id,))
            else:
                cursor.execute(empleados_query)

            empleados = cursor.fetchall()
            resultados_nomina = []

            for empleado in empleados:
                emp_id = empleado[0]
                nombre_completo = f"{empleado[1]} {empleado[2]}"
                salario_base = float(empleado[3])

                # Calcular días trabajados
                dias_trabajados = self._calcular_dias_trabajados(emp_id, mes, anio)
                
                # Calcular horas extra
                horas_extra = self._calcular_horas_extra(emp_id, mes, anio)
                
                # Obtener bonos del período
                bonos = self._obtener_bonos_periodo(emp_id, mes, anio)
                
                # Obtener descuentos del período
                descuentos = self._obtener_descuentos_periodo(emp_id, mes, anio)
                
                # Calcular faltas
                faltas = self._calcular_faltas(emp_id, mes, anio)

                # Días del mes
                dias_mes = calendar.monthrange(anio, mes)[1]
                
                # Cálculos
                salario_diario = salario_base / dias_mes
                salario_por_dias = salario_diario * dias_trabajados
                valor_horas_extra = horas_extra * (salario_base / 240)  # 240 horas mensuales aprox
                descuento_faltas = faltas * salario_diario
                
                bruto = salario_por_dias + valor_horas_extra + bonos
                total_descuentos = descuentos + descuento_faltas
                neto = bruto - total_descuentos

                resultado = {
                    'empleado_id': emp_id,
                    'empleado': nombre_completo,
                    'salario_base': salario_base,
                    'dias_trabajados': dias_trabajados,
                    'dias_mes': dias_mes,
                    'horas_extra': horas_extra,
                    'bonos': bonos,
                    'descuentos': descuentos,
                    'faltas': faltas,
                    'bruto': bruto,
                    'total_descuentos': total_descuentos,
                    'neto': neto,
                    'mes': mes,
                    'anio': anio
                }

                resultados_nomina.append(resultado)

            return resultados_nomina

        except Exception as e:
            print(f"[ERROR RRHH] Error calculando nómina: {e}")
            return []

    def guardar_nomina(self, nomina_data):
        """
        Guarda los cálculos de nómina en la base de datos.

        Args:
            nomina_data (List[Dict]): Datos de nómina calculados

        Returns:
            bool: True si fue exitoso
        """
        if not self.db_connection:
            return False

        try:
            cursor = self.db_connection.cursor()

            for nomina in nomina_data:
                # Verificar si ya existe registro para ese empleado/período
                cursor.execute(f"""
                    SELECT id FROM {self.tabla_nomina} 
                    WHERE empleado_id = ? AND mes = ? AND anio = ?
                """, (nomina['empleado_id'], nomina['mes'], nomina['anio']))

                if cursor.fetchone():
                    # Actualizar registro existente
                    query = f"""
                        UPDATE {self.tabla_nomina}
                        SET salario_base = ?, dias_trabajados = ?, horas_extra = ?,
                            bonos = ?, descuentos = ?, faltas = ?, bruto = ?,
                            total_descuentos = ?, neto = ?, fecha_calculo = GETDATE()
                        WHERE empleado_id = ? AND mes = ? AND anio = ?
                    """
                    cursor.execute(query, (
                        nomina['salario_base'], nomina['dias_trabajados'], nomina['horas_extra'],
                        nomina['bonos'], nomina['descuentos'], nomina['faltas'],
                        nomina['bruto'], nomina['total_descuentos'], nomina['neto'],
                        nomina['empleado_id'], nomina['mes'], nomina['anio']
                    ))
                else:
                    # Crear nuevo registro
                    query = f"""
                        INSERT INTO {self.tabla_nomina}
                        (empleado_id, mes, anio, salario_base, dias_trabajados, horas_extra,
                         bonos, descuentos, faltas, bruto, total_descuentos, neto, fecha_calculo)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE())
                    """
                    cursor.execute(query, (
                        nomina['empleado_id'], nomina['mes'], nomina['anio'],
                        nomina['salario_base'], nomina['dias_trabajados'], nomina['horas_extra'],
                        nomina['bonos'], nomina['descuentos'], nomina['faltas'],
                        nomina['bruto'], nomina['total_descuentos'], nomina['neto']
                    ))

            self.db_connection.commit()
            print(f"[RRHH] Nómina guardada exitosamente para {len(nomina_data)} empleados")
            return True

        except Exception as e:
            print(f"[ERROR RRHH] Error guardando nómina: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return False

    # MÉTODOS PARA ASISTENCIAS

    def registrar_asistencia(self, datos_asistencia):
        """
        Registra asistencia de un empleado.

        Args:
            datos_asistencia (dict): Datos de asistencia

        Returns:
            bool: True si fue exitoso
        """
        if not self.db_connection:
            return False

        try:
            cursor = self.db_connection.cursor()

            query = f"""
                INSERT INTO {self.tabla_asistencias}
                (empleado_id, fecha, hora_entrada, hora_salida, horas_trabajadas,
                 horas_extra, tipo, observaciones, fecha_registro)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, GETDATE())
            """

            cursor.execute(query, (
                datos_asistencia.get('empleado_id'),
                datos_asistencia.get('fecha'),
                datos_asistencia.get('hora_entrada'),
                datos_asistencia.get('hora_salida'),
                datos_asistencia.get('horas_trabajadas', 0),
                datos_asistencia.get('horas_extra', 0),
                datos_asistencia.get('tipo', 'NORMAL'),
                datos_asistencia.get('observaciones', '')
            ))

            self.db_connection.commit()
            print(f"[RRHH] Asistencia registrada para empleado {datos_asistencia.get('empleado_id')}")
            return True

        except Exception as e:
            print(f"[ERROR RRHH] Error registrando asistencia: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return False

    def obtener_asistencias(self, fecha_desde=None, fecha_hasta=None, empleado_id=None):
        """
        Obtiene registros de asistencia.

        Args:
            fecha_desde (date): Fecha desde
            fecha_hasta (date): Fecha hasta  
            empleado_id (int): ID específico del empleado

        Returns:
            List[Dict]: Lista de asistencias
        """
        if not self.db_connection:
            return []

        try:
            cursor = self.db_connection.cursor()

            conditions = ["1=1"]
            params = []

            if fecha_desde:
                conditions.append("a.fecha >= ?")
                params.append(fecha_desde)

            if fecha_hasta:
                conditions.append("a.fecha <= ?")
                params.append(fecha_hasta)

            if empleado_id:
                conditions.append("a.empleado_id = ?")
                params.append(empleado_id)

            query = f"""
                SELECT a.id, a.empleado_id, CONCAT(e.nombre, ' ', e.apellido) as empleado,
                       a.fecha, a.hora_entrada, a.hora_salida, a.horas_trabajadas,
                       a.horas_extra, a.tipo, a.observaciones
                FROM {self.tabla_asistencias} a
                JOIN {self.tabla_empleados} e ON a.empleado_id = e.id
                WHERE {" AND ".join(conditions)}
                ORDER BY a.fecha DESC, a.hora_entrada
            """

            cursor.execute(query, params)
            columnas = [column[0] for column in cursor.description]
            resultados = cursor.fetchall()

            asistencias = []
            for fila in resultados:
                asistencia = dict(zip(columnas, fila))
                asistencias.append(asistencia)

            return asistencias

        except Exception as e:
            print(f"[ERROR RRHH] Error obteniendo asistencias: {e}")
            return []

    # MÉTODOS PARA BONOS Y DESCUENTOS

    def crear_bono_descuento(self, datos_bono):
        """
        Crea un bono o descuento.

        Args:
            datos_bono (dict): Datos del bono/descuento

        Returns:
            bool: True si fue exitoso
        """
        if not self.db_connection:
            return False

        try:
            cursor = self.db_connection.cursor()

            query = f"""
                INSERT INTO {self.tabla_bonos}
                (empleado_id, tipo, concepto, monto, fecha_aplicacion,
                 mes_aplicacion, anio_aplicacion, estado, observaciones, fecha_creacion)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE())
            """

            cursor.execute(query, (
                datos_bono.get('empleado_id'),
                datos_bono.get('tipo'),  # 'BONO' o 'DESCUENTO'
                datos_bono.get('concepto'),
                datos_bono.get('monto'),
                datos_bono.get('fecha_aplicacion'),
                datos_bono.get('mes_aplicacion'),
                datos_bono.get('anio_aplicacion'),
                datos_bono.get('estado', 'PENDIENTE'),
                datos_bono.get('observaciones', '')
            ))

            self.db_connection.commit()
            print(f"[RRHH] {datos_bono.get('tipo')} creado exitosamente")
            return True

        except Exception as e:
            print(f"[ERROR RRHH] Error creando bono/descuento: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return False

    def obtener_bonos_descuentos(self, empleado_id=None, mes=None, anio=None):
        """
        Obtiene bonos y descuentos.

        Args:
            empleado_id (int): ID específico del empleado
            mes (int): Mes específico
            anio (int): Año específico

        Returns:
            List[Dict]: Lista de bonos/descuentos
        """
        if not self.db_connection:
            return []

        try:
            cursor = self.db_connection.cursor()

            conditions = ["1=1"]
            params = []

            if empleado_id:
                conditions.append("b.empleado_id = ?")
                params.append(empleado_id)

            if mes:
                conditions.append("b.mes_aplicacion = ?")
                params.append(mes)

            if anio:
                conditions.append("b.anio_aplicacion = ?")
                params.append(anio)

            query = f"""
                SELECT b.id, b.empleado_id, CONCAT(e.nombre, ' ', e.apellido) as empleado,
                       b.tipo, b.concepto, b.monto, b.fecha_aplicacion,
                       b.mes_aplicacion, b.anio_aplicacion, b.estado, b.observaciones
                FROM {self.tabla_bonos} b
                JOIN {self.tabla_empleados} e ON b.empleado_id = e.id
                WHERE {" AND ".join(conditions)}
                ORDER BY b.fecha_aplicacion DESC
            """

            cursor.execute(query, params)
            columnas = [column[0] for column in cursor.description]
            resultados = cursor.fetchall()

            bonos = []
            for fila in resultados:
                bono = dict(zip(columnas, fila))
                bonos.append(bono)

            return bonos

        except Exception as e:
            print(f"[ERROR RRHH] Error obteniendo bonos/descuentos: {e}")
            return []

    # MÉTODOS PARA HISTORIAL

    def obtener_historial_laboral(self, empleado_id=None, tipo=None):
        """
        Obtiene el historial laboral.

        Args:
            empleado_id (int): ID específico del empleado
            tipo (str): Tipo específico de evento

        Returns:
            List[Dict]: Lista de eventos del historial
        """
        if not self.db_connection:
            return []

        try:
            cursor = self.db_connection.cursor()

            conditions = ["1=1"]
            params = []

            if empleado_id:
                conditions.append("h.empleado_id = ?")
                params.append(empleado_id)

            if tipo and tipo != "Todos":
                conditions.append("h.tipo = ?")
                params.append(tipo)

            query = f"""
                SELECT h.id, h.empleado_id, CONCAT(e.nombre, ' ', e.apellido) as empleado,
                       h.tipo, h.descripcion, h.fecha, h.valor_anterior,
                       h.valor_nuevo, h.usuario_creacion
                FROM {self.tabla_historial} h
                JOIN {self.tabla_empleados} e ON h.empleado_id = e.id
                WHERE {" AND ".join(conditions)}
                ORDER BY h.fecha DESC
            """

            cursor.execute(query, params)
            columnas = [column[0] for column in cursor.description]
            resultados = cursor.fetchall()

            historial = []
            for fila in resultados:
                evento = dict(zip(columnas, fila))
                historial.append(evento)

            return historial

        except Exception as e:
            print(f"[ERROR RRHH] Error obteniendo historial: {e}")
            return []

    def obtener_estadisticas_empleados(self):
        """
        Obtiene estadísticas generales de empleados.

        Returns:
            Dict: Estadísticas de empleados
        """
        if not self.db_connection:
            return {}

        try:
            cursor = self.db_connection.cursor()

            estadisticas = {}

            # Total empleados activos
            cursor.execute(f"SELECT COUNT(*) FROM {self.tabla_empleados} WHERE activo = 1")
            estadisticas['total_empleados'] = cursor.fetchone()[0]

            # Empleados por estado
            cursor.execute(f"""
                SELECT estado, COUNT(*) as cantidad
                FROM {self.tabla_empleados}
                WHERE activo = 1
                GROUP BY estado
            """)
            estadisticas['por_estado'] = dict(cursor.fetchall())

            # Empleados por departamento
            cursor.execute(f"""
                SELECT d.nombre, COUNT(e.id) as cantidad
                FROM {self.tabla_empleados} e
                LEFT JOIN {self.tabla_departamentos} d ON e.departamento_id = d.id
                WHERE e.activo = 1
                GROUP BY d.nombre
            """)
            estadisticas['por_departamento'] = dict(cursor.fetchall())

            # Nómina total del mes actual
            mes_actual = datetime.now().month
            anio_actual = datetime.now().year
            cursor.execute(f"""
                SELECT SUM(neto) FROM {self.tabla_nomina}
                WHERE mes = ? AND anio = ?
            """, (mes_actual, anio_actual))
            resultado = cursor.fetchone()[0]
            estadisticas['nomina_mensual'] = float(resultado) if resultado else 0.0

            return estadisticas

        except Exception as e:
            print(f"[ERROR RRHH] Error obteniendo estadísticas: {e}")
            return {}

    def obtener_estadisticas_rh(self):
        """
        Alias para obtener_estadisticas_empleados para compatibilidad.
        
        Returns:
            Dict: Estadísticas de recursos humanos
        """
        return self.obtener_estadisticas_empleados()

    # MÉTODOS AUXILIARES PRIVADOS

    def _registrar_historial(self, empleado_id, tipo, descripcion, valor_anterior=None, valor_nuevo=None):
        """Registra un evento en el historial laboral."""
        if not self.db_connection:
            return

        try:
            cursor = self.db_connection.cursor()

            query = f"""
                INSERT INTO {self.tabla_historial}
                (empleado_id, tipo, descripcion, fecha, valor_anterior, valor_nuevo, usuario_creacion)
                VALUES (?, ?, ?, GETDATE(), ?, ?, 'SYSTEM')
            """

            cursor.execute(query, (empleado_id, tipo, descripcion, valor_anterior, valor_nuevo))

        except Exception as e:
            print(f"[ERROR RRHH] Error registrando historial: {e}")

    def _calcular_dias_trabajados(self, empleado_id, mes, anio):
        """Calcula los días trabajados por un empleado en un mes."""
        if not self.db_connection:
            return 0

        try:
            cursor = self.db_connection.cursor()

            query = f"""
                SELECT COUNT(DISTINCT fecha) FROM {self.tabla_asistencias}
                WHERE empleado_id = ? AND MONTH(fecha) = ? AND YEAR(fecha) = ?
                AND tipo != 'FALTA'
            """

            cursor.execute(query, (empleado_id, mes, anio))
            resultado = cursor.fetchone()
            return resultado[0] if resultado else 0

        except Exception as e:
            print(f"[ERROR RRHH] Error calculando días trabajados: {e}")
            return 0

    def _calcular_horas_extra(self, empleado_id, mes, anio):
        """Calcula las horas extra de un empleado en un mes."""
        if not self.db_connection:
            return 0

        try:
            cursor = self.db_connection.cursor()

            query = f"""
                SELECT SUM(horas_extra) FROM {self.tabla_asistencias}
                WHERE empleado_id = ? AND MONTH(fecha) = ? AND YEAR(fecha) = ?
            """

            cursor.execute(query, (empleado_id, mes, anio))
            resultado = cursor.fetchone()
            return float(resultado[0]) if resultado and resultado[0] else 0.0

        except Exception as e:
            print(f"[ERROR RRHH] Error calculando horas extra: {e}")
            return 0.0

    def _obtener_bonos_periodo(self, empleado_id, mes, anio):
        """Obtiene el total de bonos para un empleado en un período."""
        if not self.db_connection:
            return 0.0

        try:
            cursor = self.db_connection.cursor()

            query = f"""
                SELECT SUM(monto) FROM {self.tabla_bonos}
                WHERE empleado_id = ? AND mes_aplicacion = ? AND anio_aplicacion = ?
                AND tipo = 'BONO' AND estado = 'APLICADO'
            """

            cursor.execute(query, (empleado_id, mes, anio))
            resultado = cursor.fetchone()
            return float(resultado[0]) if resultado and resultado[0] else 0.0

        except Exception as e:
            print(f"[ERROR RRHH] Error obteniendo bonos: {e}")
            return 0.0

    def _obtener_descuentos_periodo(self, empleado_id, mes, anio):
        """Obtiene el total de descuentos para un empleado en un período."""
        if not self.db_connection:
            return 0.0

        try:
            cursor = self.db_connection.cursor()

            query = f"""
                SELECT SUM(monto) FROM {self.tabla_bonos}
                WHERE empleado_id = ? AND mes_aplicacion = ? AND anio_aplicacion = ?
                AND tipo = 'DESCUENTO' AND estado = 'APLICADO'
            """

            cursor.execute(query, (empleado_id, mes, anio))
            resultado = cursor.fetchone()
            return float(resultado[0]) if resultado and resultado[0] else 0.0

        except Exception as e:
            print(f"[ERROR RRHH] Error obteniendo descuentos: {e}")
            return 0.0

    def _calcular_faltas(self, empleado_id, mes, anio):
        """Calcula las faltas de un empleado en un mes."""
        if not self.db_connection:
            return 0

        try:
            cursor = self.db_connection.cursor()

            query = f"""
                SELECT COUNT(*) FROM {self.tabla_asistencias}
                WHERE empleado_id = ? AND MONTH(fecha) = ? AND YEAR(fecha) = ?
                AND tipo = 'FALTA'
            """

            cursor.execute(query, (empleado_id, mes, anio))
            resultado = cursor.fetchone()
            return resultado[0] if resultado else 0

        except Exception as e:
            print(f"[ERROR RRHH] Error calculando faltas: {e}")
            return 0