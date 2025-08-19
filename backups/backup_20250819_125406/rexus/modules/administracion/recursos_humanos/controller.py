"""
Controlador de Recursos Humanos

Maneja la lógica de control para:
- Gestión de empleados
- Cálculo de nómina
- Control de asistencias
- Bonos y descuentos
- Historial laboral
"""

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QMessageBox
from datetime import datetime
import csv
import os

from rexus.utils.app_logger import get_logger

# Configurar logger
logger = get_logger(__name__)


class RecursosHumanosController(QObject):

    # Señales para empleados
    empleado_agregado = pyqtSignal(dict)
    empleado_actualizado = pyqtSignal(dict)
    empleado_eliminado = pyqtSignal(int)

    # Señales para nómina
    nomina_calculada = pyqtSignal(list)
    nomina_guardada = pyqtSignal(bool)

    # Señales para asistencias
    asistencia_registrada = pyqtSignal(dict)

    # Señales para bonos
    bono_creado = pyqtSignal(dict)

    # Señales para reportes
    reporte_generado = pyqtSignal(str)

    def __init__(self, model=None, view=None, db_connection=None):
        super().__init__()
        self.model = model
        self.view = view
        self.db_connection = db_connection
        self.usuario_actual = "ADMIN"
        self.conectar_senales()

    def conectar_senales(self):
        """Conecta las señales de la vista con los métodos del controlador."""
        if self.view:
            # Señales de empleados
            self.view.crear_empleado_rrhh_signal.connect(self.crear_empleado)
            self.view.actualizar_empleado_signal.connect(self.actualizar_empleado)
            self.view.eliminar_empleado_signal.connect(self.eliminar_empleado)

            # Señales de nómina
            self.view.calcular_nomina_signal.connect(self.calcular_nomina)

            # Señales de asistencias
            self.view.registrar_asistencia_signal.connect(self.registrar_asistencia)
            self.view.registrar_falta_signal.connect(self.registrar_falta)

            # Señales de bonos
            self.view.generar_bono_signal.connect(self.crear_bono_descuento)

    # MÉTODOS PARA EMPLEADOS

    def cargar_empleados(self, filtros=None):
        """Carga la lista de empleados en la vista."""
        if not self.model:
            return

        try:
            empleados = self.model.obtener_todos_empleados(filtros)
            if self.view:
                self.view.actualizar_tabla_empleados(empleados)

            # Cargar estadísticas
            estadisticas = self.model.obtener_estadisticas_empleados()
            if self.view:
                self.view.actualizar_estadisticas_empleados(estadisticas)

        except Exception as e:
            self.mostrar_error(f"Error cargando empleados: {e}")

    def buscar_empleados(self, filtros):
        """Busca empleados con filtros específicos."""
        self.cargar_empleados(filtros)

    def crear_empleado(self, datos_empleado):
        """Crea un nuevo empleado."""
        if not self.model:
            return

        try:
            # Validar datos requeridos
            if not self._validar_datos_empleado(datos_empleado):
                return

            empleado_id = self.model.crear_empleado(datos_empleado)
            if empleado_id:
                self.mostrar_mensaje("Empleado creado exitosamente")
                self.cargar_empleados()
                self.empleado_agregado.emit(datos_empleado)
            else:
                self.mostrar_error("Error al crear empleado")

        except Exception as e:
            self.mostrar_error(f"Error creando empleado: {e}")

    def actualizar_empleado(self, empleado_id, datos_empleado):
        """Actualiza un empleado existente."""
        if not self.model:
            return

        try:
            # Validar datos requeridos
            if not self._validar_datos_empleado(datos_empleado):
                return

            if self.model.actualizar_empleado(empleado_id, datos_empleado):
                self.mostrar_mensaje("Empleado actualizado exitosamente")
                self.cargar_empleados()
                self.empleado_actualizado.emit(datos_empleado)
            else:
                self.mostrar_error("Error al actualizar empleado")

        except Exception as e:
            self.mostrar_error(f"Error actualizando empleado: {e}")

    def eliminar_empleado(self, empleado_id):
        """Elimina un empleado."""
        if not self.model:
            return

        try:
            # Confirmar eliminación
            if not self._confirmar_eliminacion("¿Está seguro de eliminar este empleado?"):
                return

            if self.model.eliminar_empleado(empleado_id):
                self.mostrar_mensaje("Empleado eliminado exitosamente")
                self.cargar_empleados()
                self.empleado_eliminado.emit(empleado_id)
            else:
                self.mostrar_error("Error al eliminar empleado")

        except Exception as e:
            self.mostrar_error(f"Error eliminando empleado: {e}")

    def importar_empleados_csv(self, archivo_csv):
        """Importa empleados desde un archivo CSV."""
        if not self.model:
            return

        try:
            empleados_importados = 0
            empleados_error = 0

            with open(archivo_csv, 'r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)

                for row in reader:
                    try:
                        # Mapear columnas del CSV a campos del empleado
                        datos_empleado = {
                            'codigo': row.get('codigo', ''),
                            'nombre': row.get('nombre', ''),
                            'apellido': row.get('apellido', ''),
                            'dni': row.get('dni', ''),
                            'telefono': row.get('telefono', ''),
                            'email': row.get('email', ''),
                            'direccion': row.get('direccion', ''),
                            'fecha_nacimiento': row.get('fecha_nacimiento'),
                            'fecha_ingreso': row.get('fecha_ingreso'),
                            'salario_base': float(row.get('salario_base', 0)),
                            'cargo': row.get('cargo', ''),
                            'departamento_id': int(row.get('departamento_id', 1)),
                            'estado': row.get('estado', 'ACTIVO')
                        }

                        if self.model.crear_empleado(datos_empleado):
                            empleados_importados += 1
                        else:
                            empleados_error += 1

                    except Exception as e:
                        empleados_error += 1
                        logger.error(f"Error importando empleado {row}: {e}")

            self.mostrar_mensaje(f"Importación completada: {empleados_importados} empleados importados, {empleados_error} errores")
            self.cargar_empleados()

        except Exception as e:
            self.mostrar_error(f"Error importando empleados: {e}")

    # MÉTODOS PARA NÓMINA

    def calcular_nomina(self, parametros):
        """Calcula la nómina para un período específico."""
        if not self.model:
            return

        try:
            mes = parametros.get('mes', datetime.now().month)
            anio = parametros.get('anio', datetime.now().year)
            empleado_id = parametros.get('empleado_id')

            nomina_calculada = self.model.calcular_nomina(mes, anio, empleado_id)

            if nomina_calculada:
                if self.view:
                    self.view.actualizar_tabla_nomina(nomina_calculada)
                self.nomina_calculada.emit(nomina_calculada)
                self.mostrar_mensaje(f"Nómina calculada para {len(nomina_calculada)} empleados")
            else:
                self.mostrar_error("No se pudo calcular la nómina")

        except Exception as e:
            self.mostrar_error(f"Error calculando nómina: {e}")

    def guardar_nomina(self, nomina_data):
        """Guarda los cálculos de nómina."""
        if not self.model:
            return

        try:
            if self.model.guardar_nomina(nomina_data):
                self.mostrar_mensaje("Nómina guardada exitosamente")
                self.nomina_guardada.emit(True)
            else:
                self.mostrar_error("Error al guardar nómina")
                self.nomina_guardada.emit(False)

        except Exception as e:
            self.mostrar_error(f"Error guardando nómina: {e}")
            self.nomina_guardada.emit(False)

    def generar_recibos_sueldo(self, nomina_data):
        """Genera recibos de sueldo."""
        if not nomina_data:
            self.mostrar_error("No hay datos de nómina para generar recibos")
            return

        try:
            # Crear directorio para recibos si no existe
            directorio_recibos = os.path.join(os.getcwd(), "recibos_sueldo")
            os.makedirs(directorio_recibos, exist_ok=True)

            recibos_generados = 0

            for empleado_nomina in nomina_data:
                try:
                    nombre_archivo = f"recibo_{empleado_nomina['empleado_id']}_{empleado_nomina['mes']}_{empleado_nomina['anio']}.pdf"
                    ruta_archivo = os.path.join(directorio_recibos, nombre_archivo)

                    # Aquí iría la lógica para generar el PDF del recibo
                    # Por ahora, crear un archivo de texto como ejemplo
                    self._generar_recibo_texto(empleado_nomina, ruta_archivo.replace('.pdf', '.txt'))

                    recibos_generados += 1

                except Exception as e:
                    logger.error(f"Error generando recibo para empleado {empleado_nomina['empleado_id']}: {e}")

            self.mostrar_mensaje(f"Se generaron {recibos_generados} recibos de sueldo")

        except Exception as e:
            self.mostrar_error(f"Error generando recibos: {e}")

    # MÉTODOS PARA ASISTENCIAS

    def registrar_asistencia(self, datos_asistencia):
        """Registra asistencia de un empleado."""
        if not self.model:
            return

        try:
            # Validar datos de asistencia
            if not self._validar_datos_asistencia(datos_asistencia):
                return

            if self.model.registrar_asistencia(datos_asistencia):
                self.mostrar_mensaje("Asistencia registrada exitosamente")
                self.cargar_asistencias()
                self.asistencia_registrada.emit(datos_asistencia)
            else:
                self.mostrar_error("Error al registrar asistencia")

        except Exception as e:
            self.mostrar_error(f"Error registrando asistencia: {e}")

    def registrar_falta(self, datos_falta):
        """Registra una falta de empleado."""
        if not self.model:
            return

        try:
            # Configurar como falta
            datos_falta['tipo'] = 'FALTA'
            datos_falta['horas_trabajadas'] = 0
            datos_falta['horas_extra'] = 0

            if self.model.registrar_asistencia(datos_falta):
                self.mostrar_mensaje("Falta registrada exitosamente")
                self.cargar_asistencias()
            else:
                self.mostrar_error("Error al registrar falta")

        except Exception as e:
            self.mostrar_error(f"Error registrando falta: {e}")

    def cargar_asistencias(self, filtros=None):
        """Carga las asistencias en la vista."""
        if not self.model:
            return

        try:
            fecha_desde = filtros.get('fecha_desde') if filtros else None
            fecha_hasta = filtros.get('fecha_hasta') if filtros else None
            empleado_id = filtros.get('empleado_id') if filtros else None

            asistencias = self.model.obtener_asistencias(fecha_desde, fecha_hasta, empleado_id)

            if self.view:
                self.view.actualizar_tabla_asistencias(asistencias)

        except Exception as e:
            self.mostrar_error(f"Error cargando asistencias: {e}")

    def buscar_asistencias(self, filtros):
        """Busca asistencias con filtros específicos."""
        self.cargar_asistencias(filtros)

    # MÉTODOS PARA BONOS Y DESCUENTOS

    def crear_bono_descuento(self, datos_bono):
        """Crea un bono o descuento."""
        if not self.model:
            return

        try:
            # Validar datos del bono
            if not self._validar_datos_bono(datos_bono):
                return

            if self.model.crear_bono_descuento(datos_bono):
                tipo = datos_bono.get('tipo', 'BONO')
                self.mostrar_mensaje(f"{tipo} creado exitosamente")
                self.cargar_bonos_descuentos()
                self.bono_creado.emit(datos_bono)
            else:
                self.mostrar_error("Error al crear bono/descuento")

        except Exception as e:
            self.mostrar_error(f"Error creando bono/descuento: {e}")

    def cargar_bonos_descuentos(self, filtros=None):
        """Carga los bonos y descuentos en la vista."""
        if not self.model:
            return

        try:
            empleado_id = filtros.get('empleado_id') if filtros else None
            mes = filtros.get('mes') if filtros else None
            anio = filtros.get('anio') if filtros else None

            bonos = self.model.obtener_bonos_descuentos(empleado_id, mes, anio)

            if self.view:
                self.view.actualizar_tabla_bonos(bonos)

        except Exception as e:
            self.mostrar_error(f"Error cargando bonos/descuentos: {e}")

    # MÉTODOS PARA HISTORIAL

    def cargar_historial_laboral(self, filtros=None):
        """Carga el historial laboral en la vista."""
        if not self.model:
            return

        try:
            empleado_id = filtros.get('empleado_id') if filtros else None
            tipo = filtros.get('tipo') if filtros else None

            historial = self.model.obtener_historial_laboral(empleado_id, tipo)

            if self.view:
                self.view.actualizar_tabla_historial(historial)

        except Exception as e:
            self.mostrar_error(f"Error cargando historial: {e}")

    def buscar_historial(self, filtros):
        """Busca historial laboral con filtros específicos."""
        self.cargar_historial_laboral(filtros)

    # MÉTODOS PARA REPORTES

    def generar_reporte_empleados(self, formato='PDF'):
        """Genera reporte de empleados."""
        if not self.model:
            return

        try:
            empleados = self.model.obtener_todos_empleados()

            if formato == 'CSV':
                self._generar_reporte_csv(empleados, 'empleados')
            elif formato == 'Excel':
                self._generar_reporte_excel(empleados, 'empleados')
            else:
                self._generar_reporte_pdf(empleados, 'empleados')

            self.mostrar_mensaje(f"Reporte de empleados generado en formato {formato}")

        except Exception as e:
            self.mostrar_error(f"Error generando reporte: {e}")

    def generar_reporte_nomina(self, mes, anio, formato='PDF'):
        """Genera reporte de nómina."""
        if not self.model:
            return

        try:
            nomina = self.model.calcular_nomina(mes, anio)

            if formato == 'CSV':
                self._generar_reporte_csv(nomina, f'nomina_{mes}_{anio}')
            elif formato == 'Excel':
                self._generar_reporte_excel(nomina, f'nomina_{mes}_{anio}')
            else:
                self._generar_reporte_pdf(nomina, f'nomina_{mes}_{anio}')

            self.mostrar_mensaje(f"Reporte de nómina generado en formato {formato}")

        except Exception as e:
            self.mostrar_error(f"Error generando reporte de nómina: {e}")

    # MÉTODOS AUXILIARES PRIVADOS

    def _validar_datos_empleado(self, datos):
        """Valida los datos de un empleado."""
        campos_requeridos = ['nombre', 'apellido', 'dni', 'fecha_ingreso', 'salario_base']

        for campo in campos_requeridos:
            if not datos.get(campo):
                self.mostrar_error(f"El campo {campo} es requerido")
                return False

        # Validar salario
        try:
            salario = float(datos.get('salario_base', 0))
            if salario <= 0:
                self.mostrar_error("El salario debe ser mayor a 0")
                return False
        except ValueError:
            self.mostrar_error("El salario debe ser un número válido")
            return False

        return True

    def _validar_datos_asistencia(self, datos):
        """Valida los datos de asistencia."""
        campos_requeridos = ['empleado_id', 'fecha']

        for campo in campos_requeridos:
            if not datos.get(campo):
                self.mostrar_error(f"El campo {campo} es requerido")
                return False

        return True

    def _validar_datos_bono(self, datos):
        """Valida los datos de un bono/descuento."""
        campos_requeridos = ['empleado_id', 'tipo', 'concepto', 'monto']

        for campo in campos_requeridos:
            if not datos.get(campo):
                self.mostrar_error(f"El campo {campo} es requerido")
                return False

        # Validar monto
        try:
            monto = float(datos.get('monto', 0))
            if monto <= 0:
                self.mostrar_error("El monto debe ser mayor a 0")
                return False
        except ValueError:
            self.mostrar_error("El monto debe ser un número válido")
            return False

        return True

    def _confirmar_eliminacion(self, mensaje):
        """Confirma una eliminación."""
        if self.view:
            reply = QMessageBox.question(
                self.view, "Confirmar Eliminación", mensaje,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            return reply == QMessageBox.StandardButton.Yes
        return True

    def _generar_recibo_texto(self, empleado_nomina, ruta_archivo):
        """Genera un recibo de sueldo en formato texto."""
        with open(ruta_archivo, 'w', encoding='utf-8') as file:
            file.write("=" * 50 + "\n")
            file.write("RECIBO DE SUELDO\n")
            file.write("=" * 50 + "\n\n")
            file.write(f"Empleado: {empleado_nomina['empleado']}\n")
            file.write(f"Período: {empleado_nomina['mes']}/{empleado_nomina['anio']}\n")
            file.write(f"Salario Base: ${empleado_nomina['salario_base']:,.2f}\n")
            file.write(f"Días Trabajados: {empleado_nomina['dias_trabajados']}\n")
            file.write(f"Horas Extra: {empleado_nomina['horas_extra']}\n")
            file.write(f"Bonos: ${empleado_nomina['bonos']:,.2f}\n")
            file.write(f"Descuentos: ${empleado_nomina['descuentos']:,.2f}\n")
            file.write(f"Faltas: {empleado_nomina['faltas']}\n")
            file.write("-" * 30 + "\n")
            file.write(f"Total Bruto: ${empleado_nomina['bruto']:,.2f}\n")
            file.write(f"Total Descuentos: ${empleado_nomina['total_descuentos']:,.2f}\n")
            file.write(f"TOTAL NETO: ${empleado_nomina['neto']:,.2f}\n")
            file.write("=" * 50 + "\n")

    def _generar_reporte_csv(self, datos, nombre_archivo):
        """Genera un reporte en formato CSV."""
        if not datos:
            return

        ruta_archivo = f"{nombre_archivo}.csv"

        with open(ruta_archivo, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=datos[0].keys())
            writer.writeheader()
            writer.writerows(datos)

    def _generar_reporte_excel(self, datos, nombre_archivo):
        """Genera un reporte en formato Excel."""
        # Aquí iría la lógica para generar Excel usando openpyxl
        # Por ahora, generar CSV
        self._generar_reporte_csv(datos, nombre_archivo)

    def _generar_reporte_pdf(self, datos, nombre_archivo):
        """Genera un reporte en formato PDF."""
        # Aquí iría la lógica para generar PDF usando reportlab
        # Por ahora, generar texto
        ruta_archivo = f"{nombre_archivo}.txt"

        with open(ruta_archivo, 'w', encoding='utf-8') as file:
            file.write(f"REPORTE: {nombre_archivo.upper()}\n")
            file.write("=" * 50 + "\n\n")

            for item in datos:
                for key, value in item.items():
                    file.write(f"{key}: {value}\n")
                file.write("-" * 30 + "\n")

    def mostrar_mensaje(self, mensaje):
        """Muestra un mensaje informativo."""
        if self.view:
            QMessageBox.information(self.view, "Recursos Humanos", mensaje)

    def mostrar_error(self, mensaje):
        """Muestra un mensaje de error."""
        if self.view:
            QMessageBox.critical(self.view, "Error - Recursos Humanos", mensaje)
        logger.error(f"RRHH: {mensaje}")

    def actualizar_datos(self):
        """Actualiza todos los datos de la interfaz."""
        self.cargar_empleados()
        self.cargar_asistencias()
        self.cargar_bonos_descuentos()
        self.cargar_historial_laboral()
