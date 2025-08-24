"""
Controlador de Vidrios - Rexus.app v2.0.0

Maneja la lógica de negocio entre la vista y el modelo de vidrios.
"""

import logging
from typing import Dict, List, Optional, Any
from PyQt6.QtCore import QObject, pyqtSignal

logger = logging.getLogger(__name__)

class VidriosController(QObject):
    """Controlador para el módulo de vidrios."""
    
    # Señales
    vidrio_eliminado = pyqtSignal(int)
    vidrio_creado = pyqtSignal(dict)
    vidrio_actualizado = pyqtSignal(dict)
    
    def __init__(self, model=None, view=None):
        """Inicializa el controlador de vidrios."""
        super().__init__()
        self.model = model
        self.view = view
        self.logger = logger
        
    def eliminar_vidrio(self, vidrio_id: int) -> bool:
        """
        Elimina un vidrio (requiere permisos de administrador).
        
        Args:
            vidrio_id: ID del vidrio a eliminar
            
        Returns:
            bool: True si se eliminó exitosamente
        """
        try:
            if not self.model:
                self.logger.error("Modelo no disponible")
                return False
                
            if self.model and hasattr(self.model, 'eliminar_vidrio'):
                resultado = self.model.eliminar_vidrio(vidrio_id)
                
                if resultado:
                    self.logger.info(f"Vidrio {vidrio_id} eliminado exitosamente")
                    self.vidrio_eliminado.emit(vidrio_id)
                    
                    if self.view and hasattr(self.view, 'mostrar_mensaje'):
                        self.view.mostrar_mensaje("Vidrio eliminado exitosamente", "success")
                    
                    return True
                else:
                    self.logger.error(f"No se pudo eliminar el vidrio {vidrio_id}")
                    if self.view and hasattr(self.view, 'mostrar_error'):
                        self.view.mostrar_error("No se pudo eliminar el vidrio")
                    return False
            return False
            
        except Exception as e:
            self.logger.error(f"Error eliminando vidrio: {e}")
            if self.view and hasattr(self.view, 'mostrar_error'):
                self.view.mostrar_error(f"Error al eliminar vidrio: {str(e)}")
            return False

    def crear_vidrio(self, datos: Dict[str, Any]) -> bool:
        """Crea un nuevo vidrio."""
        try:
            if not self.model:
                self.logger.error("Modelo no disponible")
                return False
                
            # Validar datos básicos
            if not self.validar_datos_vidrio(datos):
                return False
                
            if self.model and hasattr(self.model, 'crear_vidrio'):
                vidrio_id = self.model.crear_vidrio(datos)
                
                if vidrio_id:
                    self.logger.info(f"Vidrio creado exitosamente: {vidrio_id}")
                    datos['id'] = vidrio_id
                    self.vidrio_creado.emit(datos)
                    
                    if self.view and hasattr(self.view, 'mostrar_mensaje'):
                        self.view.mostrar_mensaje("Vidrio creado exitosamente", "success")
                    
                    return True
                    
            self.logger.error("No se pudo crear el vidrio")
            if self.view and hasattr(self.view, 'mostrar_error'):
                self.view.mostrar_error("No se pudo crear el vidrio")
            return False
            
        except Exception as e:
            self.logger.error(f"Error creando vidrio: {e}")
            if self.view and hasattr(self.view, 'mostrar_error'):
                self.view.mostrar_error(f"Error al crear vidrio: {str(e)}")
            return False

    def actualizar_vidrio(self, vidrio_id: int, datos: Dict[str, Any]) -> bool:
        """Actualiza un vidrio existente."""
        try:
            if not self.model:
                self.logger.error("Modelo no disponible")
                return False
                
            if not self.validar_datos_vidrio(datos):
                return False
                
            if self.model and hasattr(self.model, 'actualizar_vidrio'):
                resultado = self.model.actualizar_vidrio(vidrio_id, datos)
                
                if resultado:
                    self.logger.info(f"Vidrio {vidrio_id} actualizado exitosamente")
                    datos['id'] = vidrio_id
                    self.vidrio_actualizado.emit(datos)
                    
                    if self.view and hasattr(self.view, 'mostrar_mensaje'):
                        self.view.mostrar_mensaje("Vidrio actualizado exitosamente", "success")
                    
                    return True
                    
            self.logger.error(f"No se pudo actualizar el vidrio {vidrio_id}")
            if self.view and hasattr(self.view, 'mostrar_error'):
                self.view.mostrar_error("No se pudo actualizar el vidrio")
            return False
            
        except Exception as e:
            self.logger.error(f"Error actualizando vidrio: {e}")
            if self.view and hasattr(self.view, 'mostrar_error'):
                self.view.mostrar_error(f"Error al actualizar vidrio: {str(e)}")
            return False

    def validar_datos_vidrio(self, datos: Dict[str, Any]) -> bool:
        """Valida los datos de un vidrio."""
        try:
            # Validaciones básicas
            if not datos.get('tipo'):
                if self.view and hasattr(self.view, 'mostrar_error'):
                    self.view.mostrar_error("El tipo de vidrio es requerido")
                return False
                
            if not datos.get('grosor'):
                if self.view and hasattr(self.view, 'mostrar_error'):
                    self.view.mostrar_error("El grosor es requerido")
                return False
                
            # Validar dimensiones
            ancho = datos.get('ancho', 0)
            alto = datos.get('alto', 0)
            
            if not isinstance(ancho, (int, float)) or ancho <= 0:
                if self.view and hasattr(self.view, 'mostrar_error'):
                    self.view.mostrar_error("El ancho debe ser un número mayor a 0")
                return False
                
            if not isinstance(alto, (int, float)) or alto <= 0:
                if self.view and hasattr(self.view, 'mostrar_error'):
                    self.view.mostrar_error("El alto debe ser un número mayor a 0")
                return False
                
            return True
            
        except Exception as e:
            self.logger.error(f"Error validando datos: {e}")
            return False

    def obtener_vidrio(self, vidrio_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene un vidrio por ID."""
        try:
            if not self.model:
                return None
                
            if self.model and hasattr(self.model, 'obtener_vidrio_por_id'):
                return self.model.obtener_vidrio_por_id(vidrio_id)
            return None
            
        except Exception as e:
            self.logger.error(f"Error obteniendo vidrio: {e}")
            return None

    def obtener_vidrios(self, filtros: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Obtiene lista de vidrios con filtros opcionales."""
        try:
            if not self.model:
                return []
                
            if self.model and hasattr(self.model, 'obtener_vidrios'):
                return self.model.obtener_vidrios(filtros)
            return []
            
        except Exception as e:
            self.logger.error(f"Error obteniendo vidrios: {e}")
            return []

    def obtener_tipos_vidrio(self) -> List[str]:
        """Obtiene los tipos de vidrio disponibles."""
        try:
            if self.model and hasattr(self.model, 'TIPOS_VIDRIO'):
                return list(self.model.TIPOS_VIDRIO.keys())
            return ['Transparente', 'Templado', 'Laminado', 'Reflectivo']
            
        except Exception as e:
            self.logger.error(f"Error obteniendo tipos de vidrio: {e}")
            return []

    def calcular_precio(self, datos: Dict[str, Any]) -> float:
        """Calcula el precio de un vidrio según sus especificaciones."""
        try:
            if not self.model:
                return 0.0
                
            if self.model and hasattr(self.model, 'calcular_precio'):
                return self.model.calcular_precio(datos)
            
            # Cálculo básico si no hay modelo
            ancho = datos.get('ancho', 0)
            alto = datos.get('alto', 0)
            grosor = datos.get('grosor', 0)
            
            area = ancho * alto / 10000  # Convertir a m²
            precio_base = area * 100 * grosor  # Precio aproximado
            
            return precio_base
            
        except Exception as e:
            self.logger.error(f"Error calculando precio: {e}")
            return 0.0
