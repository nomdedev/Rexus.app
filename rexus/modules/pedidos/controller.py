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
                    
 if self.model and hasattr(self.model, 'eliminar_pedido'):
     self.model.eliminar_pedido(pedido_id)
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
                
            if self.model and hasattr(self.model, 'actualizar_estado_pedido'):
                exito = self.model.actualizar_estado_pedido(pedido_id, nuevo_estado)
                if exito:
                    mensaje = f"Estado del pedido {pedido_id} cambiado a {nuevo_estado}"
                    self.logger.info(mensaje)
                    
                    # Emitir señales
                    self.cargar_pedidos()
                    self.estado_cambiado.emit(int(pedido_id), nuevo_estado)
                    
                    if hasattr(self, 'mostrar_mensaje_success'):
                        self.mostrar_mensaje_success.emit(mensaje)
                else:
                    error_msg = f"No se pudo cambiar el estado del pedido {pedido_id}"
                    self.mostrar_error(error_msg)
        except Exception as e:
            self.logger.error(f"Error cambiando estado: {e}")
            self.mostrar_error(f"Error al cambiar estado: {str(e)}")

    def obtener_estadisticas(self) -> Dict[str, Any]:
        """Obtiene estadísticas de pedidos."""
        try:
            if not self.model:
                return {}
                
            if self.model and hasattr(self.model, 'obtener_estadisticas'):
                stats = self.model.obtener_estadisticas()
                return stats if stats else {}
            return {}
        except Exception as e:
            self.logger.error(f"Error obteniendo estadísticas: {e}")
            return {}

    def validar_datos_pedido(self, datos: Dict[str, Any]) -> bool:
        """Valida los datos de un pedido antes de crear/modificar."""
        try:
            # Validaciones básicas
            if not datos.get('cliente_id'):
                self.mostrar_error("Cliente es requerido")
                return False
                
            if not datos.get('productos') or len(datos['productos']) == 0:
                self.mostrar_error("Debe agregar al menos un producto")
                return False
                
            # Validar fechas
            fecha_pedido = datos.get('fecha_pedido')
            if fecha_pedido and isinstance(fecha_pedido, str):
                try:
                    fecha_pedido = datetime.datetime.strptime(fecha_pedido, '%Y-%m-%d').date()
                except ValueError:
                    self.mostrar_error("Formato de fecha inválido")
                    return False
                    
            # Validar total
            total = datos.get('total', 0)
            if not isinstance(total, (int, float)) or total <= 0:
                self.mostrar_error("El total debe ser mayor a 0")
                return False
                
            return True
        except Exception as e:
            self.logger.error(f"Error validando datos: {e}")
            return False

    def crear_pedido(self, datos: Dict[str, Any]) -> bool:
        """Crea un nuevo pedido."""
        try:
            if not self.model:
                self.mostrar_error("Modelo no disponible")
                return False
                
            if not self.validar_datos_pedido(datos):
                return False
                
            # Validar fecha de entrega
            fecha_entrega = datos.get('fecha_entrega')
            if fecha_entrega and isinstance(fecha_entrega, str):
                try:
                    fecha_entrega = datetime.datetime.strptime(fecha_entrega, '%Y-%m-%d').date()
                    if fecha_entrega < datetime.date.today():
                        self.mostrar_error("La fecha de entrega no puede ser anterior a hoy")
                        return False
                except ValueError:
                    self.mostrar_error("Formato de fecha de entrega inválido")
                    return False
                    
            if self.model and hasattr(self.model, 'crear_pedido'):
                pedido_id = self.model.crear_pedido(datos)
                if pedido_id:
                    self.logger.info(f"Pedido creado exitosamente: {pedido_id}")
                    self.cargar_pedidos()
                    return True
                    
            self.mostrar_error("No se pudo crear el pedido")
            return False
        except Exception as e:
            self.logger.error(f"Error creando pedido: {e}")
            self.mostrar_error(f"Error al crear pedido: {str(e)}")
            return False

    def obtener_pedido(self, pedido_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene un pedido por ID."""
        try:
            if not self.model:
                return None
                
            if self.model and hasattr(self.model, 'obtener_pedido_por_id'):
                return self.model.obtener_pedido_por_id(pedido_id)
            return None
        except Exception as e:
            self.logger.error(f"Error obteniendo pedido: {e}")
            return None

    def buscar_productos_inventario(self, busqueda: str) -> List[Dict[str, Any]]:
        """Busca productos en el inventario."""
        try:
            if not self.model:
                return []
                
            if self.model and hasattr(self.model, 'buscar_productos_inventario'):
                return self.model.buscar_productos_inventario(busqueda)
            return []
        except Exception as e:
            self.logger.error(f"Error buscando productos: {e}")
            return []

    def obtener_estados_validos(self) -> List[str]:
        """Obtiene la lista de estados válidos."""
        try:
            if self.model and hasattr(self.model, 'ESTADOS'):
                return list(self.model.ESTADOS.keys())
            return ['Pendiente', 'En Proceso', 'Completado', 'Cancelado']
        except Exception as e:
            self.logger.error(f"Error obteniendo estados: {e}")
            return []

    def obtener_tipos_pedido(self) -> List[str]:
        """Obtiene la lista de tipos de pedido."""
        try:
            if self.model and hasattr(self.model, 'TIPOS_PEDIDO'):
                return list(self.model.TIPOS_PEDIDO.keys())
            return ['Normal', 'Urgente', 'Express']
        except Exception as e:
            self.logger.error(f"Error obteniendo tipos: {e}")
            return []

    def obtener_prioridades(self) -> List[str]:
        """Obtiene la lista de prioridades."""
        try:
            if self.model and hasattr(self.model, 'PRIORIDADES'):
                return list(self.model.PRIORIDADES.keys())
            return ['Baja', 'Media', 'Alta', 'Crítica']
        except Exception as e:
            self.logger.error(f"Error obteniendo prioridades: {e}")
            return []

    def cargar_pedidos(self, page: int = 1, per_page: int = 50):
        """Carga los pedidos para la vista."""
        try:
            if not self.model:
                self.logger.error("Modelo no disponible")
                return
                
            if self.model and hasattr(self.model, 'obtener_pedidos_paginados'):
                pedidos = self.model.obtener_pedidos_paginados(page, per_page)
                if self.view and hasattr(self.view, 'actualizar_lista_pedidos'):
                    self.view.actualizar_lista_pedidos(pedidos)
        except Exception as e:
            self.logger.error(f"Error cargando pedidos: {e}")

    def cargar_pagina(self, page: int, per_page: int = 50):
        """Carga una página específica de pedidos."""
        try:
            if not self.model:
                return
                
            offset = (page - 1) * per_page
            if self.model and hasattr(self.model, 'obtener_pedidos_paginados'):
                pedidos = self.model.obtener_pedidos_paginados(offset, per_page)
                
                if self.view and hasattr(self.view, 'actualizar_tabla'):
                    self.view.actualizar_tabla(pedidos)
                    
        except Exception as e:
            self.logger.error(f"Error cargando página: {e}")
            self.mostrar_error(f"Error cargando página: {str(e)}")

    def obtener_total_registros(self) -> int:
        """Obtiene el total de registros disponibles"""
        try:
            if not self.model:
                return 0
                
            if self.model and hasattr(self.model, 'obtener_total_registros'):
                return self.model.obtener_total_registros()
            return 0
        except Exception as e:
            self.logger.error(f"Error obteniendo total de registros: {e}")
            return 0

    def mostrar_error(self, mensaje: str):
        """Muestra un mensaje de error con logging."""
        try:
            self.logger.error(mensaje)
            if self.view and hasattr(self.view, 'mostrar_error'):
                self.view.mostrar_error(mensaje)
        except Exception as e:
            self.logger.error(f"Error mostrando mensaje de error: {e}")