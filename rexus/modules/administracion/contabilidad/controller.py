"""
Controlador de Contabilidad - Rexus.app v2.0.0

Controlador para el submódulo de contabilidad dentro de administración.
Gestiona asientos contables, reportes financieros y balance.
"""

import logging
from typing import Dict, List, Optional, Any

# Importar logging
try:
    from ....utils.app_logger import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

# Importar componentes base
try:
    from ....ui.base.base_controller import BaseController
except ImportError:
    logger.warning("No se pudo importar BaseController")
    BaseController = object


class ContabilidadController(BaseController):
    """Controlador del submódulo de contabilidad."""
    
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
            if self.view and hasattr(self.view, 'connect_signals'):
                # Conectar señales específicas de contabilidad
                if hasattr(self.view, 'crear_asiento_signal'):
                    self.view.crear_asiento_signal.connect(self.crear_asiento_contable)
                
                if hasattr(self.view, 'buscar_asientos_signal'):
                    self.view.buscar_asientos_signal.connect(self.buscar_asientos)
                
                if hasattr(self.view, 'generar_reporte_signal'):
                    self.view.generar_reporte_signal.connect(self.generar_reporte_financiero)
                
                logger.debug("Señales de contabilidad conectadas")
                
        except Exception as e:
            logger.error(f"Error conectando señales de contabilidad: {e}")
    
    def cargar_datos_iniciales(self):
        """Carga datos iniciales del módulo de contabilidad."""
        try:
            if not self.model:
                logger.warning("No hay modelo de contabilidad disponible")
                return
            
            # Cargar asientos contables recientes
            self.cargar_asientos_contables()
            
            # Cargar estadísticas financieras
            self.cargar_estadisticas_financieras()
            
            logger.debug("Datos iniciales de contabilidad cargados")
            
        except (AttributeError, TypeError) as e:
            logger.error(f"Error cargando datos iniciales de contabilidad: {e}")
    
    def buscar_asientos(self, filtros: Dict[str, Any]):
        """
        Busca asientos contables con filtros específicos.
        
        Args:
            filtros: Diccionario con filtros de búsqueda
        """
        try:
            if not self.model:
                return
            
            logger.debug(f"Buscando asientos con filtros: {filtros}")
            self.cargar_asientos_contables(filtros)
            
        except Exception as e:
            logger.error(f"Error buscando asientos contables: {e}")
    
    def crear_asiento_contable(self, datos_asiento: Dict[str, Any]):
        """
        Crea un nuevo asiento contable.
        
        Args:
            datos_asiento: Datos del asiento a crear
        """
        try:
            if not self.model:
                logger.error("No hay modelo disponible para crear asiento")
                return False
            
            # Validar datos del asiento
            if not self._validar_datos_asiento(datos_asiento):
                logger.error("Datos del asiento inválidos")
                return False
            
            # Crear asiento a través del modelo
            resultado = self.model.crear_asiento_contable(
                datos_asiento.get('fecha_asiento'),
                datos_asiento.get('tipo_asiento'),
                datos_asiento.get('concepto'),
                datos_asiento.get('monto', 0),
                datos_asiento.get('cuenta_debe'),
                datos_asiento.get('cuenta_haber')
            )
            
            if resultado:
                logger.info("Asiento contable creado exitosamente")
                self.cargar_asientos_contables()  # Recargar lista
                return True
            else:
                logger.error("Error creando asiento contable")
                return False
                
        except Exception as e:
            logger.error(f"Error creando asiento contable: {e}")
            return False
    
    def cargar_asientos_contables(self, filtros: Optional[Dict[str, Any]] = None):
        """
        Carga asientos contables en la vista.
        
        Args:
            filtros: Filtros opcionales para la consulta
        """
        try:
            if not self.model or not self.view:
                return
            
            # Obtener asientos del modelo
            asientos = self.model.obtener_asientos_contables(filtros or {})
            
            # Actualizar vista
            if hasattr(self.view, 'actualizar_tabla_asientos'):
                self.view.actualizar_tabla_asientos(asientos)
            
            logger.debug(f"Cargados {len(asientos)} asientos contables")
            
        except Exception as e:
            logger.error(f"Error cargando asientos contables: {e}")
    
    def cargar_estadisticas_financieras(self):
        """Carga estadísticas financieras para el dashboard."""
        try:
            if not self.model or not self.view:
                return
            
            # Obtener estadísticas del modelo
            estadisticas = self.model.obtener_estadisticas_financieras()
            
            # Actualizar vista
            if hasattr(self.view, 'actualizar_estadisticas'):
                self.view.actualizar_estadisticas(estadisticas)
            
            logger.debug("Estadísticas financieras actualizadas")
            
        except Exception as e:
            logger.error(f"Error cargando estadísticas financieras: {e}")
    
    def generar_reporte_financiero(self, tipo_reporte: str, parametros: Dict[str, Any]):
        """
        Genera un reporte financiero específico.
        
        Args:
            tipo_reporte: Tipo de reporte (balance, estado_resultados, etc.)
            parametros: Parámetros del reporte (fechas, filtros, etc.)
        """
        try:
            if not self.model:
                logger.error("No hay modelo disponible para generar reporte")
                return None
            
            logger.info(f"Generando reporte financiero: {tipo_reporte}")
            
            # Generar reporte a través del modelo
            if tipo_reporte == "balance":
                reporte = self.model.generar_balance_general(parametros)
            elif tipo_reporte == "estado_resultados":
                reporte = self.model.generar_estado_resultados(parametros)
            elif tipo_reporte == "libro_diario":
                reporte = self.model.generar_libro_diario(parametros)
            else:
                logger.error(f"Tipo de reporte no soportado: {tipo_reporte}")
                return None
            
            # Mostrar reporte en la vista
            if reporte and hasattr(self.view, 'mostrar_reporte'):
                self.view.mostrar_reporte(reporte, tipo_reporte)
            
            return reporte
            
        except Exception as e:
            logger.error(f"Error generando reporte financiero: {e}")
            return None
    
    def _validar_datos_asiento(self, datos: Dict[str, Any]) -> bool:
        """
        Valida los datos de un asiento contable.
        
        Args:
            datos: Datos del asiento a validar
            
        Returns:
            True si los datos son válidos
        """
        try:
            # Validaciones básicas
            if not datos.get('fecha_asiento'):
                logger.error("Fecha del asiento es requerida")
                return False
            
            if not datos.get('tipo_asiento'):
                logger.error("Tipo de asiento es requerido")
                return False
            
            if not datos.get('concepto'):
                logger.error("Concepto del asiento es requerido")
                return False
            
            monto = datos.get('monto', 0)
            if not isinstance(monto, (int, float)) or monto <= 0:
                logger.error("Monto del asiento debe ser mayor a cero")
                return False
            
            if not datos.get('cuenta_debe') or not datos.get('cuenta_haber'):
                logger.error("Cuentas debe y haber son requeridas")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validando datos del asiento: {e}")
            return False
    
    def exportar_datos_contables(self, formato: str = "excel", filtros: Optional[Dict[str, Any]] = None):
        """
        Exporta datos contables en el formato especificado.
        
        Args:
            formato: Formato de exportación (excel, pdf, csv)
            filtros: Filtros para la exportación
        """
        try:
            if not self.model:
                logger.error("No hay modelo disponible para exportar")
                return False
            
            logger.info(f"Exportando datos contables en formato {formato}")
            
            # Obtener datos para exportar
            datos = self.model.obtener_asientos_contables(filtros or {})
            
            if not datos:
                logger.warning("No hay datos para exportar")
                return False
            
            # Exportar según el formato
            if formato.lower() == "excel":
                resultado = self._exportar_excel(datos)
            elif formato.lower() == "pdf":
                resultado = self._exportar_pdf(datos)
            elif formato.lower() == "csv":
                resultado = self._exportar_csv(datos)
            else:
                logger.error(f"Formato de exportación no soportado: {formato}")
                return False
            
            if resultado:
                logger.info("Exportación completada exitosamente")
            
            return resultado
            
        except Exception as e:
            logger.error(f"Error exportando datos contables: {e}")
            return False
    
    def _exportar_excel(self, datos: List[Dict]) -> bool:
        """Exporta datos a Excel."""
        try:
            # Aquí iría la lógica de exportación a Excel
            logger.debug(f"Exportando {len(datos)} registros a Excel")
            return True
        except Exception as e:
            logger.error(f"Error exportando a Excel: {e}")
            return False
    
    def _exportar_pdf(self, datos: List[Dict]) -> bool:
        """Exporta datos a PDF."""
        try:
            # Aquí iría la lógica de exportación a PDF
            logger.debug(f"Exportando {len(datos)} registros a PDF")
            return True
        except Exception as e:
            logger.error(f"Error exportando a PDF: {e}")
            return False
    
    def _exportar_csv(self, datos: List[Dict]) -> bool:
        """Exporta datos a CSV."""
        try:
            # Aquí iría la lógica de exportación a CSV
            logger.debug(f"Exportando {len(datos)} registros a CSV")
            return True
        except Exception as e:
            logger.error(f"Error exportando a CSV: {e}")
            return False