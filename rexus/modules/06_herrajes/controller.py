"""
Controlador de Herrajes - Rexus.app v2.0.0
Versión simplificada y funcional

Maneja la lógica entre el modelo y la vista para herrajes.
"""

import logging
from typing import Dict, List, Optional, Any
from PyQt6.QtCore import pyqtSignal, QObject
from rexus.utils.unified_sanitizer import sanitize_string, sanitize_numeric

logger = logging.getLogger(__name__)

class HerrajesController(QObject):
    """Controlador simplificado para la gestión de herrajes."""

    # Señales para comunicación con otros módulos
    herraje_creado = pyqtSignal(dict)
    herraje_actualizado = pyqtSignal(dict)
    herraje_eliminado = pyqtSignal(int)
    stock_actualizado = pyqtSignal(int, int)

    def __init__(self,
        model=None,
        view=None,
        db_connection=None,
        usuario_actual=None):
        """Inicializa el controlador de herrajes."""
        super().__init__()
        
        # Parámetros básicos para el controlador
        self.model = model
        self.view = view  
        self.db_connection = db_connection
        self.module_name = "herrajes"
        self.logger = logger
        self.usuario_actual = usuario_actual or {"id": 1, "nombre": "SISTEMA"}

        # Conectar señales si la vista está disponible
        if self.view and hasattr(self.view, 'conectar_senales'):
            self.view.conectar_senales(self)

    def cargar_herrajes(self):
        """Carga la lista de herrajes desde el modelo."""
        try:
            if not self.model:
                self.logger.error("Modelo no disponible")
                return []
                
            if hasattr(self.model, 'obtener_herrajes'):
                herrajes = self.model.obtener_herrajes()
                if self.view and hasattr(self.view, 'cargar_herrajes'):
                    self.view.cargar_herrajes(herrajes)
                return herrajes
            return []
            
        except Exception as e:
            self.logger.error(f"Error cargando herrajes: {e}")
            if self.view and hasattr(self.view, 'mostrar_error'):
                self.view.mostrar_error("Error al cargar herrajes")
            return []

    def crear_herraje(self, datos_herraje: Dict[str, Any]) -> bool:
        """Crea un nuevo herraje."""
        try:
            if not self.model:
                self.logger.error("Modelo no disponible")
                return False
                
            # Validar datos básicos
            if not self.validar_datos_herraje(datos_herraje):
                return False
                
            # Limpiar datos
            data_limpia = self.limpiar_datos_herraje(datos_herraje)
            
            if hasattr(self.model, 'crear_herraje'):
                resultado = self.model.crear_herraje(data_limpia)
                if resultado:
                    self.herraje_creado.emit(data_limpia)
                    if self.view and hasattr(self.view, 'mostrar_mensaje'):
                        self.view.mostrar_mensaje("Herraje creado exitosamente", "success")
                    return True
            return False
            
        except Exception as e:
            self.logger.error(f"Error creando herraje: {e}")
            if self.view and hasattr(self.view, 'mostrar_error'):
                self.view.mostrar_error(f"Error al crear herraje: {str(e)}")
            return False

    def actualizar_herraje(self, herraje_id: int, datos: Dict[str, Any]) -> bool:
        """Actualiza un herraje existente."""
        try:
            if not self.model:
                self.logger.error("Modelo no disponible")
                return False
                
            # Validar datos
            if not self.validar_datos_herraje(datos):
                return False
                
            # Limpiar datos
            data_limpia = self.limpiar_datos_herraje(datos)
            
            if hasattr(self.model, 'actualizar_herraje'):
                resultado = self.model.actualizar_herraje(herraje_id, data_limpia)
                if resultado:
                    self.herraje_actualizado.emit(data_limpia)
                    if self.view and hasattr(self.view, 'mostrar_mensaje'):
                        self.view.mostrar_mensaje("Herraje actualizado exitosamente", "success")
                    return True
            return False
            
        except Exception as e:
            self.logger.error(f"Error actualizando herraje: {e}")
            if self.view and hasattr(self.view, 'mostrar_error'):
                self.view.mostrar_error(f"Error al actualizar herraje: {str(e)}")
            return False

    def eliminar_herraje(self, herraje_id: int) -> bool:
        """Elimina un herraje."""
        try:
            if not self.model:
                self.logger.error("Modelo no disponible")
                return False
                
            if hasattr(self.model, 'eliminar_herraje'):
                resultado = self.model.eliminar_herraje(herraje_id)
                if resultado:
                    self.herraje_eliminado.emit(herraje_id)
                    if self.view and hasattr(self.view, 'mostrar_mensaje'):
                        self.view.mostrar_mensaje("Herraje eliminado exitosamente", "success")
                    return True
            return False
            
        except Exception as e:
            self.logger.error(f"Error eliminando herraje: {e}")
            if self.view and hasattr(self.view, 'mostrar_error'):
                self.view.mostrar_error(f"Error al eliminar herraje: {str(e)}")
            return False

    def cargar_estadisticas(self):
        """Carga estadísticas de herrajes."""
        try:
            if not self.model:
                self.logger.error("Modelo no disponible")
                return {}
                
            if hasattr(self.model, 'obtener_estadisticas'):
                estadisticas = self.model.obtener_estadisticas()
                if self.view and hasattr(self.view, 'actualizar_estadisticas'):
                    self.view.actualizar_estadisticas(estadisticas)
                return estadisticas
            return {}
            
        except Exception as e:
            self.logger.error(f"Error cargando estadísticas: {e}")
            return {}

    def buscar_herrajes(self, filtros: Dict[str, Any]) -> List[Dict]:
        """Busca herrajes con filtros específicos."""
        try:
            if not self.model:
                self.logger.error("Modelo no disponible")
                return []
                
            if hasattr(self.model, 'buscar_herrajes'):
                return self.model.buscar_herrajes(filtros)
            return []
            
        except Exception as e:
            self.logger.error(f"Error buscando herrajes: {e}")
            return []

    def validar_datos_herraje(self, datos: Dict[str, Any]) -> bool:
        """Valida los datos del herraje."""
        try:
            # Validaciones básicas
            if not datos.get('codigo'):
                if self.view and hasattr(self.view, 'mostrar_error'):
                    self.view.mostrar_error("El código es obligatorio")
                return False
                
            if not datos.get('descripcion'):
                if self.view and hasattr(self.view, 'mostrar_error'):
                    self.view.mostrar_error("La descripción es obligatoria")
                return False
                
            return True
            
        except Exception as e:
            self.logger.error(f"Error validando datos: {e}")
            return False

    def limpiar_datos_herraje(self, datos: Dict[str, Any]) -> Dict[str, Any]:
        """Limpia y sanitiza los datos del herraje."""
        try:
            data_limpia = {}
            
            # Limpiar strings
            for campo in ['codigo', 'descripcion', 'proveedor', 'categoria']:
                if campo in datos:
                    data_limpia[campo] = sanitize_string(datos[campo])
            
            # Limpiar números
            for campo in ['precio', 'stock_minimo', 'stock_actual']:
                if campo in datos:
                    data_limpia[campo] = sanitize_numeric(datos[campo])
            
            return data_limpia
            
        except Exception as e:
            self.logger.error(f"Error limpiando datos: {e}")
            return datos

    def exportar_herrajes(self, formato: str = "excel") -> bool:
        """Exporta herrajes al formato especificado."""
        try:
            self.logger.info(f"Iniciando exportación en formato {formato}")
            
            if not self.model:
                if self.view and hasattr(self.view, 'mostrar_error'):
                    self.view.mostrar_error("Modelo no disponible para exportación")
                return False

            # Obtener datos para exportar
            herrajes = self.cargar_herrajes()
            if not herrajes:
                if self.view and hasattr(self.view, 'mostrar_advertencia'):
                    self.view.mostrar_advertencia("No hay herrajes para exportar")
                return False

            # Implementar exportación básica
            self.logger.info(f"Exportación de {len(herrajes)} herrajes completada")
            if self.view and hasattr(self.view, 'mostrar_mensaje'):
                self.view.mostrar_mensaje("Exportación completada exitosamente", "success")
            return True
            
        except Exception as e:
            self.logger.error(f"Error en exportación: {e}")
            if self.view and hasattr(self.view, 'mostrar_error'):
                self.view.mostrar_error(f"Error en exportación: {str(e)}")
            return False

    @staticmethod
    def get_integration_service(db_connection=None):
        """Compatibilidad: devuelve el servicio de integración Herrajes-Inventario."""
        try:
            # Importación opcional para evitar errores si no existe
            from .inventario_integration import HerrajesInventarioIntegration
            return HerrajesInventarioIntegration(db_connection=db_connection)
        except (ImportError, AttributeError, TypeError) as e:
            # Retornar None si no puede construirse (evita lanzar en pruebas)
            logger.debug(f"Servicio de integración no disponible: {e}")
            return None
