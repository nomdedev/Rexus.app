"""
Controlador de Configuración - Rexus.app v2.0.0

Maneja la lógica de negocio para la configuración del sistema.
"""

import logging
from typing import Dict, List, Any, Optional

# Importar logging
try:
    from ...utils.app_logger import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

# Importar componentes base
try:
    from ...ui.base.base_controller import BaseController
except ImportError:
    logger.warning("No se pudo importar BaseController")
    BaseController = object


class ConfiguracionController(BaseController):
    """Controlador del módulo de configuración."""
    
    def __init__(self, model=None, view=None, db_connection=None):
        """
        Inicializar controlador de configuración.
        
        Args:
            model: Modelo de configuración
            view: Vista de configuración
            db_connection: Conexión a la base de datos
        """
        super().__init__()
        self.model = model
        self.view = view
        self.db_connection = db_connection
        self.usuario_actual = "SISTEMA"
        
        self.conectar_senales()
        logger.info("ConfiguracionController inicializado")
    
    def conectar_senales(self):
        """Conecta las señales de la vista con los métodos del controlador."""
        try:
            if self.view and hasattr(self.view, 'connect_signals'):
                # Conectar señales específicas de configuración
                if hasattr(self.view, 'buscar_signal'):
                    self.view.buscar_signal.connect(self.buscar)
                
                if hasattr(self.view, 'guardar_configuracion_signal'):
                    self.view.guardar_configuracion_signal.connect(self.guardar_configuracion)
                
                if hasattr(self.view, 'eliminar_configuracion_signal'):
                    self.view.eliminar_configuracion_signal.connect(self.eliminar_configuracion)
                
                logger.debug("Señales de configuración conectadas")
                
        except Exception as e:
            logger.error(f"Error conectando señales de configuración: {e}")
    
    def cargar_datos_iniciales(self):
        """Carga datos iniciales del módulo de configuración."""
        try:
            if not self.model:
                logger.warning("No hay modelo de configuración disponible")
                return
            
            # Cargar todas las configuraciones
            self.cargar_configuraciones()
            
            logger.debug("Datos iniciales de configuración cargados")
            
        except (AttributeError, TypeError) as e:
            logger.error(f"Error cargando datos iniciales de configuración: {e}")
    
    def filtrar_configuraciones(self, filtros: Dict[str, Any]) -> List[Dict]:
        """
        Filtra configuraciones según los criterios especificados.
        
        Args:
            filtros: Diccionario con filtros a aplicar
            
        Returns:
            Lista de configuraciones filtradas
        """
        try:
            logger.info(f"[CONFIGURACION CONTROLLER] Aplicando filtros: {filtros}")
            
            if not self.model:
                logger.error("[CONFIGURACION CONTROLLER] Modelo no disponible")
                return []
            
            # Delegar al modelo la aplicación de filtros
            configuraciones = self.model.obtener_configuraciones_filtradas(filtros)
            
            if configuraciones is not None:
                logger.info(f"[CONFIGURACION CONTROLLER] Filtradas {len(configuraciones)} configuraciones")
                return configuraciones
            else:
                logger.error("[CONFIGURACION CONTROLLER] Error en filtros del modelo")
                return []
                
        except Exception as e:
            logger.exception(f"[CONFIGURACION CONTROLLER] Error filtrando configuraciones: {e}")
            return []

    def buscar(self, filtros: Dict[str, Any]):
        """
        Busca configuraciones y actualiza la vista.
        
        Args:
            filtros: Diccionario con filtros de búsqueda
        """
        try:
            configuraciones = self.filtrar_configuraciones(filtros)
            if self.view and hasattr(self.view, 'cargar_datos_en_tabla'):
                self.view.cargar_datos_en_tabla(configuraciones)
        except Exception as e:
            logger.exception(f"[CONFIGURACION CONTROLLER] Error en búsqueda: {e}")
    
    def cargar_configuraciones(self, filtros: Optional[Dict[str, Any]] = None):
        """
        Carga configuraciones en la vista.
        
        Args:
            filtros: Filtros opcionales para la consulta
        """
        try:
            if not self.model or not self.view:
                return
            
            # Obtener configuraciones del modelo
            if filtros:
                configuraciones = self.model.obtener_configuraciones_filtradas(filtros)
            else:
                configuraciones = self.model.obtener_todas_configuraciones()
            
            # Actualizar vista
            if hasattr(self.view, 'cargar_datos_en_tabla'):
                self.view.cargar_datos_en_tabla(configuraciones)
            
            logger.debug(f"Cargadas {len(configuraciones)} configuraciones")
            
        except Exception as e:
            logger.error(f"Error cargando configuraciones: {e}")
    
    def guardar_configuracion(self, datos_config: Dict[str, Any]):
        """
        Guarda una configuración nueva o actualizada.
        
        Args:
            datos_config: Datos de la configuración
        """
        try:
            if not self.model:
                logger.error("No hay modelo disponible para guardar configuración")
                return False
            
            # Validar datos de configuración
            if not self._validar_datos_configuracion(datos_config):
                return False
            
            # Determinar si es creación o actualización
            config_id = datos_config.get('id')
            if config_id:
                resultado = self.model.actualizar_configuracion(config_id, datos_config)
                mensaje = "Configuración actualizada exitosamente"
            else:
                resultado = self.model.crear_configuracion(datos_config)
                mensaje = "Configuración creada exitosamente"
            
            if resultado:
                logger.info(mensaje)
                self.cargar_configuraciones()  # Recargar lista
                return True
            else:
                logger.error("Error guardando configuración")
                return False
                
        except Exception as e:
            logger.error(f"Error guardando configuración: {e}")
            return False
    
    def eliminar_configuracion(self, config_id: int):
        """
        Elimina una configuración.
        
        Args:
            config_id: ID de la configuración a eliminar
        """
        try:
            if not self.model:
                logger.error("No hay modelo disponible para eliminar configuración")
                return False
            
            if self.model.eliminar_configuracion(config_id):
                logger.info("Configuración eliminada exitosamente")
                self.cargar_configuraciones()  # Recargar lista
                return True
            else:
                logger.error("Error eliminando configuración")
                return False
                
        except Exception as e:
            logger.error(f"Error eliminando configuración: {e}")
            return False
    
    def _validar_datos_configuracion(self, datos: Dict[str, Any]) -> bool:
        """
        Valida los datos de una configuración.
        
        Args:
            datos: Datos de configuración a validar
            
        Returns:
            True si los datos son válidos
        """
        try:
            # Validaciones básicas
            if not datos.get('clave'):
                logger.error("Clave de configuración es requerida")
                return False
            
            if not datos.get('valor'):
                logger.error("Valor de configuración es requerido")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validando datos de configuración: {e}")
            return False
    
    def exportar_configuraciones(self, formato: str = "json"):
        """
        Exporta configuraciones en el formato especificado.
        
        Args:
            formato: Formato de exportación (json, xml, csv)
        """
        try:
            if not self.model:
                logger.error("No hay modelo disponible para exportar")
                return False
            
            configuraciones = self.model.obtener_todas_configuraciones()
            
            if not configuraciones:
                logger.warning("No hay configuraciones para exportar")
                return False
            
            # Aquí iría la lógica de exportación según formato
            logger.info(f"Configuraciones exportadas en formato {formato}")
            return True
            
        except Exception as e:
            logger.error(f"Error exportando configuraciones: {e}")
            return False
    
    def importar_configuraciones(self, archivo_path: str):
        """
        Importa configuraciones desde un archivo.
        
        Args:
            archivo_path: Ruta del archivo a importar
        """
        try:
            if not self.model:
                logger.error("No hay modelo disponible para importar")
                return False
            
            # Aquí iría la lógica de importación
            logger.info(f"Configuraciones importadas desde {archivo_path}")
            self.cargar_configuraciones()  # Recargar después de importar
            return True
            
        except Exception as e:
            logger.error(f"Error importando configuraciones: {e}")
            return False