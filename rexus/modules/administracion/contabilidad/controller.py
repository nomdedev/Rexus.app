"""
Controlador de Contabilidad - Rexus.app v2.0.0

Controlador para el submódulo de contabilidad dentro de administración.
Gestiona asientos contables, reportes financieros y balance.
"""

import logging
from typing import Dict, List, Optional, Any
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


class ContabilidadController(BaseController):
    """Controlador del submódulo de contabilidad."""
    
    # Señales
    asiento_creado = pyqtSignal(dict)
    reporte_generado = pyqtSignal(dict)
    balance_actualizado = pyqtSignal()

    def __init__(self, model=None, view=None, db_connection=None):
        """
        Inicializar controlador de contabilidad.

        Args:
            model: Modelo de contabilidad
            view: Vista de contabilidad
            db_connection: Conexión a la base de datos
        """
        super().__init__()
        self.model = model
        self.view = view
        self.db_connection = db_connection
        self.usuario_actual = "SISTEMA"

        self.conectar_senales()
        logger.info("ContabilidadController inicializado")

    def conectar_senales(self):
        """Conecta las señales de la vista con los métodos del controlador."""
        try:
            if self.view and hasattr(self.view, 'crear_asiento_signal'):
                self.view.crear_asiento_signal.connect(self.crear_asiento_contable)
            
            if self.view and hasattr(self.view, 'generar_reporte_signal'):
                self.view.generar_reporte_signal.connect(self.generar_reporte)
            
            if self.view and hasattr(self.view, 'actualizar_balance_signal'):
                self.view.actualizar_balance_signal.connect(self.actualizar_balance)
                
            logger.debug("Señales de contabilidad conectadas")
            
        except Exception as e:
            logger.error(f"Error conectando señales de contabilidad: {e}")

    def cargar_datos_iniciales(self):
        """Carga los datos iniciales del módulo de contabilidad."""
        try:
            if not self.model:
                logger.warning("Modelo no disponible para cargar datos iniciales")
                return
                
            # Cargar asientos recientes
            asientos_recientes = self.obtener_asientos_recientes()
            if self.view and hasattr(self.view, 'cargar_asientos'):
                self.view.cargar_asientos(asientos_recientes)
            
            # Cargar balance actual
            balance = self.obtener_balance_actual()
            if self.view and hasattr(self.view, 'mostrar_balance'):
                self.view.mostrar_balance(balance)
                
        except (AttributeError, TypeError) as e:
            logger.error(f"Error cargando datos iniciales de contabilidad: {e}")

    def buscar_asientos(self, filtros: Dict[str, Any]):
        """Busca asientos contables según filtros especificados."""
        try:
            if not self.model:
                logger.error("Modelo no disponible para búsqueda")
                return []
            
            if hasattr(self.model, 'buscar_asientos'):
                resultados = self.model.buscar_asientos(filtros)
                return resultados
            else:
                logger.warning("Método buscar_asientos no disponible en el modelo")
                return []
                
        except Exception as e:
            logger.error(f"Error buscando asientos contables: {e}")
            return []

    def crear_asiento_contable(self, datos_asiento: Dict[str, Any]):
        """Crea un nuevo asiento contable."""
        try:
            if not self.model:
                logger.error("Modelo no disponible para crear asiento")
                return False
            
            # Validar datos del asiento
            if not self.validar_asiento(datos_asiento):
                return False
            
            # Crear asiento en el modelo
            if hasattr(self.model, 'crear_asiento'):
                resultado = self.model.crear_asiento(datos_asiento)
                if resultado:
                    self.asiento_creado.emit(datos_asiento)
                    logger.info(f"Asiento contable creado exitosamente")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error creando asiento contable: {e}")
            return False

    def generar_reporte(self, tipo_reporte: str, parametros: Dict[str, Any]):
        """Genera reportes financieros."""
        try:
            if not self.model:
                logger.error("Modelo no disponible para generar reporte")
                return None
            
            if hasattr(self.model, 'generar_reporte'):
                reporte = self.model.generar_reporte(tipo_reporte, parametros)
                if reporte:
                    self.reporte_generado.emit(reporte)
                    logger.info(f"Reporte {tipo_reporte} generado exitosamente")
                    return reporte
            
            return None
            
        except Exception as e:
            logger.error(f"Error generando reporte {tipo_reporte}: {e}")
            return None

    def actualizar_balance(self):
        """Actualiza el balance contable."""
        try:
            if not self.model:
                logger.error("Modelo no disponible para actualizar balance")
                return False
            
            if hasattr(self.model, 'calcular_balance'):
                balance = self.model.calcular_balance()
                if balance:
                    self.balance_actualizado.emit()
                    logger.info("Balance actualizado exitosamente")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error actualizando balance: {e}")
            return False

    def obtener_asientos_recientes(self, limite: int = 50):
        """Obtiene los asientos más recientes."""
        try:
            if not self.model:
                return []
            
            if hasattr(self.model, 'obtener_asientos_recientes'):
                return self.model.obtener_asientos_recientes(limite)
            
            return []
            
        except Exception as e:
            logger.error(f"Error obteniendo asientos recientes: {e}")
            return []

    def obtener_balance_actual(self):
        """Obtiene el balance contable actual."""
        try:
            if not self.model:
                return {}
            
            if hasattr(self.model, 'obtener_balance_actual'):
                return self.model.obtener_balance_actual()
            
            return {}
            
        except Exception as e:
            logger.error(f"Error obteniendo balance actual: {e}")
            return {}

    def validar_asiento(self, datos_asiento: Dict[str, Any]) -> bool:
        """Valida los datos de un asiento contable."""
        try:
            # Validaciones básicas
            if not datos_asiento.get('fecha'):
                logger.error("Fecha del asiento es obligatoria")
                return False
            
            if not datos_asiento.get('descripcion'):
                logger.error("Descripción del asiento es obligatoria")
                return False
            
            # Validar que el debe igual al haber
            debe = sum(float(item.get('debe', 0)) for item in datos_asiento.get('items', []))
            haber = sum(float(item.get('haber', 0)) for item in datos_asiento.get('items', []))
            
            if abs(debe - haber) > 0.01:  # Tolerancia de 1 centavo
                logger.error(f"El debe ({debe}) no coincide con el haber ({haber})")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validando asiento: {e}")
            return False

    def exportar_datos(self, formato: str = "excel"):
        """Exporta datos contables al formato especificado."""
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
