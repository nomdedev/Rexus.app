"""
Controller de Notificaciones - Rexus.app v2.0.0

Controlador para gestionar notificaciones del sistema.
Coordina entre el modelo y la vista siguiendo el patrón MVC.
"""

import logging
from typing import Dict, List, Optional, Any
from PyQt6.QtCore import QObject, pyqtSignal

logger = logging.getLogger(__name__)

class NotificacionesController(QObject):
    """Controlador para el módulo de notificaciones."""
    
    # Señales
    notificacion_eliminada = pyqtSignal(int)
    nueva_notificacion = pyqtSignal(dict)
    
    def __init__(self, model=None, view=None):
        """Inicializa el controlador de notificaciones."""
        super().__init__()
        self.model = model
        self.view = view
        self.logger = logger
        
    def eliminar_notificacion(self, notificacion_id: int) -> bool:
        """
        Elimina una notificación (solo administradores).

        Args:
            notificacion_id: ID de la notificación

        Returns:
            bool: True si se eliminó exitosamente
        """
        try:
            if not self.model:
                self.logger.error("Modelo no disponible")
                return False
                
            if hasattr(self.model, 'eliminar_notificacion'):
                resultado = self.model.eliminar_notificacion(notificacion_id)

                if resultado:
                    if self.view and hasattr(self.view, 'mostrar_mensaje'):
                        self.view.mostrar_mensaje("Notificación eliminada exitosamente", "success")
                    if self.view and hasattr(self.view, 'remover_notificacion_de_lista'):
                        self.view.remover_notificacion_de_lista(notificacion_id)
                    
                    self.notificacion_eliminada.emit(notificacion_id)

                return resultado
            return False

        except Exception as e:
            self.logger.error(f"Error eliminando notificación: {str(e)}")
            if self.view and hasattr(self.view, 'mostrar_error'):
                self.view.mostrar_error(f"Error al eliminar notificación: {str(e)}")
            return False

    def crear_notificacion(self, datos: Dict[str, Any]) -> bool:
        """Crea una nueva notificación."""
        try:
            if not self.model:
                self.logger.error("Modelo no disponible")
                return False
                
            # Validar datos básicos
            if not datos.get('titulo') or not datos.get('mensaje'):
                self.logger.error("Titulo y mensaje son requeridos")
                return False
                
            if hasattr(self.model, 'crear_notificacion'):
                notificacion_id = self.model.crear_notificacion(datos)
                
                if notificacion_id:
                    self.logger.info(f"Notificación creada: {notificacion_id}")
                    self.nueva_notificacion.emit(datos)
                    return True
                    
            return False
            
        except Exception as e:
            self.logger.error(f"Error creando notificación: {e}")
            return False

    def marcar_como_leida(self, notificacion_id: int) -> bool:
        """Marca una notificación como leída."""
        try:
            if not self.model:
                return False
                
            if hasattr(self.model, 'marcar_como_leida'):
                return self.model.marcar_como_leida(notificacion_id)
            return False
            
        except Exception as e:
            self.logger.error(f"Error marcando notificación como leída: {e}")
            return False

    def obtener_notificaciones(self, usuario_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Obtiene las notificaciones del usuario."""
        try:
            if not self.model:
                return []
                
            if hasattr(self.model, 'obtener_notificaciones'):
                return self.model.obtener_notificaciones(usuario_id)
            return []
            
        except Exception as e:
            self.logger.error(f"Error obteniendo notificaciones: {e}")
            return []

    def obtener_notificaciones_no_leidas(self, usuario_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Obtiene las notificaciones no leídas."""
        try:
            if not self.model:
                return []
                
            if hasattr(self.model, 'obtener_notificaciones_no_leidas'):
                return self.model.obtener_notificaciones_no_leidas(usuario_id)
            return []
            
        except Exception as e:
            self.logger.error(f"Error obteniendo notificaciones no leídas: {e}")
            return []

    def contar_no_leidas(self, usuario_id: Optional[int] = None) -> int:
        """Cuenta las notificaciones no leídas."""
        try:
            if not self.model:
                return 0
                
            if hasattr(self.model, 'contar_no_leidas'):
                return self.model.contar_no_leidas(usuario_id)
            return 0
            
        except Exception as e:
            self.logger.error(f"Error contando notificaciones no leídas: {e}")
            return 0
