"""Controlador de Mantenimiento"""

import logging
from datetime import datetime, date, timedelta
from typing import Dict, List

from PyQt6.QtCore import QObject, pyqtSignal

# Importar logging centralizado
try:
    from rexus.utils.app_logger import get_logger
    logger = get_logger("mantenimiento.controller")
except ImportError:
    class DummyLogger:
        def info(self, msg): logger.debug(f"[INFO] {msg}")
        def warning(self, msg): logger.warning(f"[WARNING] {msg}")
        def error(self, msg): logger.error(f"[ERROR] {msg}")
        def debug(self, msg): logger.debug(f"[DEBUG] {msg}")
    logger = DummyLogger()


from rexus.core.auth_decorators import auth_required
from rexus.utils.message_system import show_success, show_error
from rexus.modules.mantenimiento.programacion_model import ProgramacionMantenimientoModel

logger = logging.getLogger(__name__)


class MantenimientoController(QObject):
    """Controlador para el módulo de mantenimiento."""

    # Señales
    datos_actualizados = pyqtSignal()
    alerta_mantenimiento = pyqtSignal(dict)

    def __init__(self,
model=None,
        view=None,
        db_connection=None,
        usuarios_model=None):
        super().__init__()
        self.model = model
        self.view = view
        self.db_connection = db_connection
        self.usuarios_model = usuarios_model
        self.usuario_actual = "SISTEMA"

        # Inicializar modelo de programación
        self.programacion_model = ProgramacionMantenimientoModel(db_connection)

        # Conectar señales
        self.conectar_señales()

        # Cargar datos iniciales
        self.cargar_datos_iniciales()

    def conectar_señales(self):
        """Conecta las señales entre vista y controlador."""
        if self.view:
            # Conectar señales de la vista si existen
            pass

    def cargar_datos_iniciales(self):
        """Carga los datos iniciales del módulo."""
        try:
            # Verificar mantenimientos pendientes
            self.verificar_mantenimientos_pendientes()

            # Cargar equipos y herramientas
            if self.view:
                equipos = self.model.obtener_todos_equipos() if self.model else []
                self.view.cargar_equipos(equipos)

            logger.info("Datos iniciales de mantenimiento cargados exitosamente")

        except Exception as e:
            logger.error(f"Error cargando datos iniciales: {e}")

    @auth_required
    def crear_equipo(self, datos_equipo: Dict) -> bool:
        """
        Crea un nuevo equipo en el sistema.

        Args:
            datos_equipo: Diccionario con datos del equipo

        Returns:
            bool: True si se creó exitosamente
        """
        try:
            if not self.validar_datos_equipo(datos_equipo):
                return False

            exito = self.model.crear_equipo(**datos_equipo)

            if exito:
                show_success(self.view, "Éxito", "Equipo creado exitosamente")
                self.datos_actualizados.emit()

                # Crear programación automática si corresponde
                if datos_equipo.get('requiere_mantenimiento_programado'):
                    self._crear_programacion_automatica(datos_equipo)

                return True
            else:
                show_error(self.view, "Error", "No se pudo crear el equipo")
                return False

        except Exception as e:
            logger.error(f"Error creando equipo: {e}")
            show_error(self.view, "Error", f"Error creando equipo: {str(e)}")
            return False

    @auth_required
    def programar_mantenimiento(self, equipo_id: int, tipo_mantenimiento: str,
                               fecha_programada: date, observaciones: str = "") -> bool:
        """
        Programa un mantenimiento para un equipo.

        Args:
            equipo_id: ID del equipo
            tipo_mantenimiento: Tipo de mantenimiento
            fecha_programada: Fecha programada
            observaciones: Observaciones adicionales

        Returns:
            bool: True si se programó exitosamente
        """
        try:
            datos_programacion = {
                'equipo_id': equipo_id,
                'tipo_mantenimiento': tipo_mantenimiento,
                'fecha_programada': fecha_programada,
                'observaciones': observaciones,
                'estado': 'PROGRAMADO',
                'usuario_creacion': self.usuario_actual,
                'fecha_creacion': datetime.now()
            }

            exito = self.programacion_model.crear_programacion(**datos_programacion)

            if exito:
                show_success(self.view, "Éxito", "Mantenimiento programado exitosamente")
                self.datos_actualizados.emit()
                return True
            else:
                show_error(self.view, "Error", "No se pudo programar el mantenimiento")
                return False

        except Exception as e:
            logger.error(f"Error programando mantenimiento: {e}")
            show_error(self.view, "Error", f"Error programando mantenimiento: {str(e)}")
            return False

    @auth_required
    def ejecutar_mantenimiento(self, programacion_id: int, datos_ejecucion: Dict) -> bool:
        """
        Ejecuta un mantenimiento programado.

        Args:
            programacion_id: ID de la programación
            datos_ejecucion: Datos de la ejecución del mantenimiento

        Returns:
            bool: True si se ejecutó exitosamente
        """
        try:
            # Validar datos de ejecución
            if not self._validar_datos_ejecucion(datos_ejecucion):
                return False

            # Registrar ejecución del mantenimiento
            exito = self.model.ejecutar_mantenimiento(programacion_id, datos_ejecucion)

            if exito:
                # Actualizar estado de programación
                self.programacion_model.actualizar_estado_programacion(
                    programacion_id, 'EJECUTADO'
                )

                # Verificar si requiere reprogramación
                if datos_ejecucion.get('requiere_seguimiento'):
                    self._reprogramar_mantenimiento(programacion_id, datos_ejecucion)

                show_success(self.view, "Éxito", "Mantenimiento ejecutado exitosamente")
                self.datos_actualizados.emit()
                return True
            else:
                show_error(self.view, "Error", "No se pudo ejecutar el mantenimiento")
                return False

        except Exception as e:
            logger.error(f"Error ejecutando mantenimiento: {e}")
            show_error(self.view, "Error", f"Error ejecutando mantenimiento: {str(e)}")
            return False

    def verificar_mantenimientos_pendientes(self):
        """Verifica y alerta sobre mantenimientos pendientes."""
        try:
            # Obtener mantenimientos vencidos
            vencidos = self.programacion_model.obtener_mantenimientos_vencidos()

            # Obtener mantenimientos próximos a vencer (7 días)
            proximos = self.programacion_model.obtener_mantenimientos_proximos(7)

            # Emitir alertas
            if vencidos:
                for mantenimiento in vencidos:
                    self.alerta_mantenimiento.emit({
                        'tipo': 'VENCIDO',
                        'mantenimiento': mantenimiento
                    })

            if proximos:
                for mantenimiento in proximos:
                    self.alerta_mantenimiento.emit({
                        'tipo': 'PROXIMO',
                        'mantenimiento': mantenimiento
                    })

            logger.info(f"Verificación completada: {len(vencidos)} vencidos, {len(proximos)} próximos")

        except Exception as e:
            logger.error(f"Error verificando mantenimientos pendientes: {e}")

    @auth_required
    def generar_reporte_historial(self, equipo_id: int, fecha_inicio: date,
                                 fecha_fin: date) -> List[Dict]:
        """
        Genera reporte de historial de mantenimiento.

        Args:
            equipo_id: ID del equipo
            fecha_inicio: Fecha de inicio del reporte
            fecha_fin: Fecha de fin del reporte

        Returns:
            Lista con historial de mantenimientos
        """
        try:
            historial = self.model.obtener_historial_mantenimiento(
                equipo_id, fecha_inicio, fecha_fin
            )

            logger.info(f"Reporte generado: {len(historial)} registros")
            return historial

        except Exception as e:
            logger.error(f"Error generando reporte: {e}")
            return []

    def _crear_programacion_automatica(self, datos_equipo: Dict):
        """Crea programación automática basada en los datos del equipo."""
        try:
            frecuencia_dias = datos_equipo.get('frecuencia_mantenimiento_dias', 30)
            fecha_proxima = date.today() + timedelta(days=frecuencia_dias)

            self.programar_mantenimiento(
                equipo_id=datos_equipo.get('id'),
                tipo_mantenimiento='PREVENTIVO',
                fecha_programada=fecha_proxima,
                observaciones='Mantenimiento preventivo programado automáticamente'
            )

        except Exception as e:
            logger.error(f"Error creando programación automática: {e}")

    def _reprogramar_mantenimiento(self, programacion_id: int, datos_ejecucion: Dict):
        """Reprograma un mantenimiento basado en los resultados de la ejecución."""
        try:
            dias_siguiente = datos_ejecucion.get('dias_proximo_mantenimiento', 30)
            fecha_proxima = date.today() + timedelta(days=dias_siguiente)

            # Obtener datos de la programación original
            programacion = self.programacion_model.obtener_programacion(programacion_id)
            if programacion:
                self.programar_mantenimiento(
                    equipo_id=programacion['equipo_id'],
                    tipo_mantenimiento=programacion['tipo_mantenimiento'],
                    fecha_programada=fecha_proxima,
                    observaciones=f"Reprogramado automáticamente después de ejecución"
                )

        except Exception as e:
            logger.error(f"Error reprogramando mantenimiento: {e}")

    def validar_datos_equipo(self, datos: Dict) -> bool:
        """Valida los datos de un equipo."""
        errores = []

        if not datos.get('nombre', '').strip():
            errores.append("El nombre del equipo es obligatorio")

        if not datos.get('codigo', '').strip():
            errores.append("El código del equipo es obligatorio")

        if errores:
            show_error(self.view, "Datos inválidos", "\n".join(errores))
            return False

        return True

    def _validar_datos_ejecucion(self, datos: Dict) -> bool:
        """Valida los datos de ejecución de mantenimiento."""
        errores = []

        if not datos.get('tecnico_asignado', '').strip():
            errores.append("El técnico asignado es obligatorio")

        if not datos.get('observaciones_ejecucion', '').strip():
            errores.append("Las observaciones de ejecución son obligatorias")

        if errores:
            show_error(self.view, "Datos inválidos", "\n".join(errores))
            return False

        return True
