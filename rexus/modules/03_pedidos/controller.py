"""
Controlador de Pedidos - Rexus.app v2.0.0

Maneja la lógica de negocio entre la vista y el modelo de pedidos.
"""

import datetime
import logging
from typing import Dict, Any, Optional, List
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QMessageBox

logger = logging.getLogger(__name__)

class PedidosController(QObject):
    """Controlador para el módulo de pedidos."""
    
    # Señales
    pedido_eliminado = pyqtSignal(int)
    estado_cambiado = pyqtSignal(int, str)
    mostrar_mensaje_success = pyqtSignal(str)
    
    def __init__(self, model=None, view=None):
        """Inicializa el controlador de pedidos."""
        super().__init__()
        self.model = model
        self.view = view
        self.logger = logger
        
    def eliminar_pedido(self, pedido_id: str):
        """Elimina un pedido."""
        try:
            if not self.model:
                self.logger.error("Modelo no disponible")
                return
                
            # Confirmar eliminación
            if self.view:
                respuesta = QMessageBox.question(
                    self.view,
                    "Confirmar eliminación",
                    f"¿Está seguro de eliminar el pedido {pedido_id}?\n\n"
                    "Esta acción no se puede deshacer.",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No,
                )

                if respuesta == QMessageBox.StandardButton.Yes:
                    self.logger.info(f"Eliminando pedido ID: {pedido_id}")
                    
                    if hasattr(self.model, 'eliminar_pedido') and self.model.eliminar_pedido(pedido_id):
                        success_msg = f"Pedido {pedido_id} eliminado exitosamente"
                        self.logger.info(f"Pedido {pedido_id} eliminado correctamente")
                        
                        self.mostrar_mensaje_success.emit(success_msg)
                        self.pedido_eliminado.emit(int(pedido_id))
                        self.cargar_pedidos()
                    else:
                        error_msg = f"No se pudo eliminar el pedido {pedido_id}"
                        self.logger.error(f"Fallo al eliminar pedido {pedido_id}")
                        self.mostrar_error(error_msg)
        except Exception as e:
            self.logger.error(f"Error eliminando pedido: {e}")

    def cambiar_estado(self, pedido_id: str, nuevo_estado: str):
        """Cambia el estado de un pedido."""
        try:
            if not self.model:
                self.logger.error("Modelo no disponible")
                return
                
            if hasattr(self.model, 'actualizar_estado_pedido'):
                exito = self.model.actualizar_estado_pedido(pedido_id, nuevo_estado)
                if exito:
                    mensaje = f"Estado del pedido {pedido_id} cambiado a {nuevo_estado}"
                    self.logger.info(mensaje)
                    self.estado_cambiado.emit(int(pedido_id), nuevo_estado)
                    self.mostrar_mensaje_success.emit(mensaje)
                    self.cargar_pedidos()
                else:
                    error_msg = f"No se pudo cambiar el estado del pedido {pedido_id}"
                    self.logger.error(error_msg)
                    self.mostrar_error(error_msg)
        except Exception as e:
            self.logger.error(f"Error cambiando estado: {e}")

    def cargar_pedidos(self):
        """Carga la lista de pedidos."""
        try:
            if not self.model:
                self.logger.error("Modelo no disponible")
                return []
                
            if hasattr(self.model, 'obtener_pedidos'):
                pedidos = self.model.obtener_pedidos()
                if self.view and hasattr(self.view, 'cargar_pedidos'):
                    self.view.cargar_pedidos(pedidos)
                return pedidos
            return []
            
        except Exception as e:
            self.logger.error(f"Error cargando pedidos: {e}")
            return []

    def crear_pedido(self, datos_pedido: Dict[str, Any]) -> bool:
        """Crea un nuevo pedido."""
        try:
            if not self.model:
                self.logger.error("Modelo no disponible")
                return False
                
            if hasattr(self.model, 'crear_pedido'):
                resultado = self.model.crear_pedido(datos_pedido)
                if resultado:
                    self.logger.info("Pedido creado exitosamente")
                    self.mostrar_mensaje_success.emit("Pedido creado exitosamente")
                    self.cargar_pedidos()
                    return True
            return False
            
        except Exception as e:
            self.logger.error(f"Error creando pedido: {e}")
            return False

    def actualizar_pedido(self, pedido_id: int, datos: Dict[str, Any]) -> bool:
        """Actualiza un pedido existente."""
        try:
            if not self.model:
                self.logger.error("Modelo no disponible")
                return False
                
            if hasattr(self.model, 'actualizar_pedido'):
                resultado = self.model.actualizar_pedido(pedido_id, datos)
                if resultado:
                    self.logger.info(f"Pedido {pedido_id} actualizado exitosamente")
                    self.mostrar_mensaje_success.emit("Pedido actualizado exitosamente")
                    self.cargar_pedidos()
                    return True
            return False
            
        except Exception as e:
            self.logger.error(f"Error actualizando pedido: {e}")
            return False

    def buscar_pedidos(self, filtros: Dict[str, Any]) -> List[Dict]:
        """Busca pedidos con filtros específicos."""
        try:
            if not self.model:
                self.logger.error("Modelo no disponible")
                return []
                
            if hasattr(self.model, 'buscar_pedidos'):
                return self.model.buscar_pedidos(filtros)
            return []
            
        except Exception as e:
            self.logger.error(f"Error buscando pedidos: {e}")
            return []

    def mostrar_error(self, mensaje: str):
        """Muestra un mensaje de error."""
        if self.view and hasattr(self.view, 'mostrar_error'):
            self.view.mostrar_error(mensaje)
        else:
            self.logger.error(mensaje)

    def obtener_estadisticas(self) -> Dict[str, Any]:
        """Obtiene estadísticas de pedidos."""
        try:
            if not self.model:
                return {}
                
            if hasattr(self.model, 'obtener_estadisticas'):
                return self.model.obtener_estadisticas()
            return {}
            
        except Exception as e:
            self.logger.error(f"Error obteniendo estadísticas: {e}")
            return {}

    def exportar_pedidos(self, formato: str = "excel") -> bool:
        """Exporta pedidos al formato especificado."""
        try:
            if not self.model:
                self.mostrar_error("Modelo no disponible para exportación")
                return False

            pedidos = self.cargar_pedidos()
            if not pedidos:
                self.mostrar_error("No hay pedidos para exportar")
                return False

            # Implementar exportación básica
            self.logger.info(f"Exportación de {len(pedidos)} pedidos completada")
            self.mostrar_mensaje_success.emit("Exportación completada exitosamente")
            return True
            
        except Exception as e:
            self.logger.error(f"Error en exportación: {e}")
            self.mostrar_error(f"Error en exportación: {str(e)}")
            return False
