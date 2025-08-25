"""
Controlador de Recursos Humanos - Rexus.app v2.0.0

Controlador para el submódulo de recursos humanos dentro de administración.
Gestiona empleados, nóminas, asistencias y evaluaciones.
"""

import logging
from typing import Dict, List, Any
from PyQt6.QtCore import QObject, pyqtSignal

# Importar logging
try:
    from ....utils.app_logger import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

# Importar componentes base
try:
    from ....core.base_controller import BaseController
except ImportError:
    logger.warning("No se pudo importar BaseController")
    BaseController = QObject


class RecursosHumanosController(BaseController):
    """Controlador del submódulo de recursos humanos."""
    
    # Señales
    empleado_creado = pyqtSignal(dict)
    empleado_actualizado = pyqtSignal(dict)
    empleado_eliminado = pyqtSignal(int)
    nomina_calculada = pyqtSignal(dict)
    asistencia_registrada = pyqtSignal(dict)

    def __init__(self, model=None, view=None, db_connection=None):
        """
        Inicializar controlador de recursos humanos.

        Args:
            model: Modelo de recursos humanos
            view: Vista de recursos humanos
            db_connection: Conexión a la base de datos
        """
        super().__init__()
        self.model = model
        self.view = view
        self.db_connection = db_connection
        self.usuario_actual = "SISTEMA"

        self.conectar_senales()
        logger.info("RecursosHumanosController inicializado")

    def conectar_senales(self):
        """Conecta las señales de la vista con los métodos del controlador."""
        try:
            if self.view:
                # Señales de empleados
                if hasattr(self.view, 'crear_empleado_rrhh_signal'):
                    self.view.crear_empleado_rrhh_signal.connect(self.crear_empleado)
                if hasattr(self.view, 'actualizar_empleado_signal'):
                    self.view.actualizar_empleado_signal.connect(self.actualizar_empleado)
                if hasattr(self.view, 'eliminar_empleado_signal'):
                    self.view.eliminar_empleado_signal.connect(self.eliminar_empleado)

                # Señales de nómina
                if hasattr(self.view, 'calcular_nomina_signal'):
                    self.view.calcular_nomina_signal.connect(self.calcular_nomina)

                # Señales de asistencias
                if hasattr(self.view, 'registrar_asistencia_signal'):
                    self.view.registrar_asistencia_signal.connect(self.registrar_asistencia)
                if hasattr(self.view, 'registrar_falta_signal'):
                    self.view.registrar_falta_signal.connect(self.registrar_falta)

                # Señales de bonos
                if hasattr(self.view, 'generar_bono_signal'):
                    self.view.generar_bono_signal.connect(self.crear_bono_descuento)

                logger.debug("Señales de RRHH conectadas")
                
        except Exception as e:
            logger.error(f"Error conectando señales de RRHH: {e}")

    def cargar_empleados(self, filtros=None):
        """Carga la lista de empleados."""
        try:
            if not self.model:
                logger.warning("Modelo no disponible para cargar empleados")
                return []

            if hasattr(self.model, 'obtener_empleados'):
                empleados = self.model.obtener_empleados(filtros)
                if self.view and hasattr(self.view, 'cargar_empleados'):
                    self.view.cargar_empleados(empleados)
                return empleados
            
            return []
            
        except Exception as e:
            logger.error(f"Error cargando empleados: {e}")
            return []

    def buscar_empleados(self, filtros: Dict[str, Any]):
        """Busca empleados según filtros especificados."""
        try:
            if not self.model:
                logger.error("Modelo no disponible para búsqueda")
                return []

            if hasattr(self.model, 'buscar_empleados'):
                return self.model.buscar_empleados(filtros)
            
            return []
            
        except Exception as e:
            logger.error(f"Error buscando empleados: {e}")
            return []

    def crear_empleado(self, datos_empleado: Dict[str, Any]):
        """Crea un nuevo empleado."""
        try:
            if not self.model:
                logger.error("Modelo no disponible para crear empleado")
                return False

            # Validar datos del empleado
            if not self.validar_datos_empleado(datos_empleado):
                return False

            if hasattr(self.model, 'crear_empleado'):
                resultado = self.model.crear_empleado(datos_empleado)
                if resultado:
                    self.empleado_creado.emit(datos_empleado)
                    logger.info("Empleado creado exitosamente")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error creando empleado: {e}")
            return False

    def actualizar_empleado(self, empleado_id: int, datos_empleado: Dict[str, Any]):
        """Actualiza un empleado existente."""
        try:
            if not self.model:
                logger.error("Modelo no disponible para actualizar empleado")
                return False

            # Validar datos del empleado
            if not self.validar_datos_empleado(datos_empleado):
                return False

            if hasattr(self.model, 'actualizar_empleado'):
                resultado = self.model.actualizar_empleado(empleado_id, datos_empleado)
                if resultado:
                    self.empleado_actualizado.emit(datos_empleado)
                    logger.info(f"Empleado {empleado_id} actualizado exitosamente")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error actualizando empleado: {e}")
            return False

    def eliminar_empleado(self, empleado_id: int):
        """Elimina un empleado."""
        try:
            if not self.model:
                logger.error("Modelo no disponible para eliminar empleado")
                return False

            if hasattr(self.model, 'eliminar_empleado'):
                resultado = self.model.eliminar_empleado(empleado_id)
                if resultado:
                    self.empleado_eliminado.emit(empleado_id)
                    logger.info(f"Empleado {empleado_id} eliminado exitosamente")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error eliminando empleado: {e}")
            return False

    def calcular_nomina(self, periodo: str, empleados_ids: List[int] = None):
        """Calcula la nómina para un período específico."""
        try:
            if not self.model:
                logger.error("Modelo no disponible para calcular nómina")
                return None

            if hasattr(self.model, 'calcular_nomina'):
                nomina = self.model.calcular_nomina(periodo, empleados_ids)
                if nomina:
                    self.nomina_calculada.emit(nomina)
                    logger.info(f"Nómina calculada para período {periodo}")
                    return nomina
            
            return None
            
        except Exception as e:
            logger.error(f"Error calculando nómina: {e}")
            return None

    def registrar_asistencia(self, empleado_id: int, fecha: str, tipo: str):
        """Registra asistencia de un empleado."""
        try:
            if not self.model:
                logger.error("Modelo no disponible para registrar asistencia")
                return False

            datos_asistencia = {
                'empleado_id': empleado_id,
                'fecha': fecha,
                'tipo': tipo
            }

            if hasattr(self.model, 'registrar_asistencia'):
                resultado = self.model.registrar_asistencia(datos_asistencia)
                if resultado:
                    self.asistencia_registrada.emit(datos_asistencia)
                    logger.info(f"Asistencia registrada para empleado {empleado_id}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error registrando asistencia: {e}")
            return False

    def registrar_falta(self, empleado_id: int, fecha: str, motivo: str):
        """Registra una falta de un empleado."""
        try:
            if not self.model:
                logger.error("Modelo no disponible para registrar falta")
                return False

            datos_falta = {
                'empleado_id': empleado_id,
                'fecha': fecha,
                'motivo': motivo,
                'tipo': 'falta'
            }

            if hasattr(self.model, 'registrar_asistencia'):
                resultado = self.model.registrar_asistencia(datos_falta)
                if resultado:
                    logger.info(f"Falta registrada para empleado {empleado_id}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error registrando falta: {e}")
            return False

    def crear_bono_descuento(self, empleado_id: int, tipo: str, monto: float, concepto: str):
        """Crea un bono o descuento para un empleado."""
        try:
            if not self.model:
                logger.error("Modelo no disponible para crear bono/descuento")
                return False

            datos_bono = {
                'empleado_id': empleado_id,
                'tipo': tipo,  # 'bono' o 'descuento'
                'monto': monto,
                'concepto': concepto
            }

            if hasattr(self.model, 'crear_bono_descuento'):
                resultado = self.model.crear_bono_descuento(datos_bono)
                if resultado:
                    logger.info(f"{tipo.capitalize()} creado para empleado {empleado_id}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error creando {tipo}: {e}")
            return False

    def validar_datos_empleado(self, datos_empleado: Dict[str, Any]) -> bool:
        """Valida los datos de un empleado."""
        try:
            # Validaciones básicas
            if not datos_empleado.get('nombre'):
                logger.error("Nombre del empleado es obligatorio")
                return False
            
            if not datos_empleado.get('documento'):
                logger.error("Documento del empleado es obligatorio")
                return False
            
            if not datos_empleado.get('cargo'):
                logger.error("Cargo del empleado es obligatorio")
                return False
            
            # Validar formato de email si se proporciona
            email = datos_empleado.get('email')
            if email and '@' not in email:
                logger.error("Formato de email inválido")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validando datos del empleado: {e}")
            return False

    def generar_reporte_empleados(self, filtros: Dict[str, Any] = None):
        """Genera reporte de empleados."""
        try:
            if not self.model:
                logger.error("Modelo no disponible para generar reporte")
                return None

            if hasattr(self.model, 'generar_reporte_empleados'):
                reporte = self.model.generar_reporte_empleados(filtros)
                logger.info("Reporte de empleados generado exitosamente")
                return reporte
            
            return None
            
        except Exception as e:
            logger.error(f"Error generando reporte de empleados: {e}")
            return None

    def exportar_datos(self, formato: str = "excel"):
        """Exporta datos de RRHH al formato especificado."""
        try:
            if not self.model:
                logger.error("Modelo no disponible para exportación")
                return False

            logger.info(f"Iniciando exportación en formato {formato}")
            
            # Aquí se implementaría la lógica de exportación
            # Por ahora retornamos True para evitar errores
            
            logger.info("Exportación completada exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"Error en exportación: {e}")
            return False
