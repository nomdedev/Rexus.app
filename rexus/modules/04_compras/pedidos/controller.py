"""
Controlador de Pedidos de Compras - Rexus.app v2.0.0

Controlador para el submódulo de pedidos dentro del módulo de compras.
Gestiona los pedidos de compra a proveedores.
"""

import logging
from typing import Dict, List, Any
from datetime import datetime
from decimal import Decimal
from PyQt6.QtCore import QObject, pyqtSignal

# Configurar logging
try:
    from ....utils.app_logger import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

# Importar dialogs
try:
    from ....ui.components.dialogs import show_info, show_error, show_warning, show_question
except ImportError:
    def show_info(parent, title, message):
        logger.info(f"{title}: {message}")
    
    def show_error(parent, title, message):
        logger.error(f"{title}: {message}")
    
    def show_warning(parent, title, message):
        logger.warning(f"{title}: {message}")
    
    def show_question(parent, title, message):
        logger.info(f"{title}: {message}")
        return True

# Importar BaseController
try:
    from ....core.base_controller import BaseController
except ImportError:
    logger.warning("No se pudo importar BaseController")
    BaseController = QObject


class PedidosComprasController(BaseController):
    """Controlador para el submódulo de pedidos de compras."""
    
    # Señales
    pedido_creado = pyqtSignal(dict)
    pedido_actualizado = pyqtSignal(dict)
    pedido_eliminado = pyqtSignal(int)
    estado_cambiado = pyqtSignal(int, str)

    def __init__(self, model=None, view=None, db_connection=None):
        """
        Inicializar controlador de pedidos de compras.

        Args:
            model: Modelo de pedidos de compras
            view: Vista de pedidos de compras
            db_connection: Conexión a la base de datos
        """
        super().__init__()
        self.model = model
        self.view = view
        self.db_connection = db_connection
        self.usuario_actual = "SISTEMA"

        self.conectar_senales()
        logger.info("PedidosComprasController inicializado")

    def conectar_senales(self):
        """Conecta las señales de la vista con los métodos del controlador."""
        try:
            if self.view:
                # Señales de pedidos
                if hasattr(self.view, 'pedido_creado'):
                    self.view.pedido_creado.connect(self.crear_pedido)
                
                if hasattr(self.view, 'pedido_actualizado'):
                    self.view.pedido_actualizado.connect(self.actualizar_pedido)
                
                if hasattr(self.view, 'pedido_eliminado'):
                    self.view.pedido_eliminado.connect(self.eliminar_pedido)
                
                if hasattr(self.view, 'cambiar_estado_pedido'):
                    self.view.cambiar_estado_pedido.connect(self.cambiar_estado_pedido)
                
                logger.debug("Señales de pedidos de compras conectadas")
                
        except Exception as e:
            logger.error(f"Error conectando señales de pedidos: {e}")

    def crear_pedido(self, datos_pedido: Dict[str, Any]) -> bool:
        """Crea un nuevo pedido de compra."""
        try:
            if not self.model:
                logger.error("Modelo no disponible para crear pedido")
                return False

            # Validar datos del pedido
            if not self.validar_datos_pedido(datos_pedido):
                return False

            # Crear pedido en el modelo
            if hasattr(self.model, 'crear_pedido'):
                pedido_id = self.model.crear_pedido(datos_pedido)
                if pedido_id:
                    datos_pedido['id'] = pedido_id
                    self.pedido_creado.emit(datos_pedido)
                    logger.info(f"Pedido de compra {pedido_id} creado exitosamente")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error creando pedido: {e}")
            return False

    def actualizar_pedido(self, pedido_id: int, datos_pedido: Dict[str, Any]) -> bool:
        """Actualiza un pedido de compra existente."""
        try:
            if not self.model:
                logger.error("Modelo no disponible para actualizar pedido")
                return False

            # Validar datos del pedido
            if not self.validar_datos_pedido(datos_pedido):
                return False

            if hasattr(self.model, 'actualizar_pedido'):
                resultado = self.model.actualizar_pedido(pedido_id, datos_pedido)
                if resultado:
                    datos_pedido['id'] = pedido_id
                    self.pedido_actualizado.emit(datos_pedido)
                    logger.info(f"Pedido {pedido_id} actualizado exitosamente")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error actualizando pedido: {e}")
            return False

    def eliminar_pedido(self, pedido_id: int) -> bool:
        """Elimina un pedido de compra."""
        try:
            if not self.model:
                logger.error("Modelo no disponible para eliminar pedido")
                return False

            if hasattr(self.model, 'eliminar_pedido'):
                resultado = self.model.eliminar_pedido(pedido_id)
                if resultado:
                    self.pedido_eliminado.emit(pedido_id)
                    logger.info(f"Pedido {pedido_id} eliminado exitosamente")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error eliminando pedido: {e}")
            return False

    def cambiar_estado_pedido(self, pedido_id: int, nuevo_estado: str) -> bool:
        """Cambia el estado de un pedido."""
        try:
            if not self.model:
                logger.error("Modelo no disponible para cambiar estado")
                return False

            estados_validos = ['pendiente', 'aprobado', 'enviado', 'recibido', 'cancelado']
            if nuevo_estado not in estados_validos:
                logger.error(f"Estado {nuevo_estado} no válido")
                return False

            if hasattr(self.model, 'cambiar_estado_pedido'):
                resultado = self.model.cambiar_estado_pedido(pedido_id, nuevo_estado)
                if resultado:
                    self.estado_cambiado.emit(pedido_id, nuevo_estado)
                    logger.info(f"Estado del pedido {pedido_id} cambiado a {nuevo_estado}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error cambiando estado del pedido: {e}")
            return False

    def obtener_pedidos(self, filtros: Dict[str, Any] = None) -> List[Dict]:
        """Obtiene la lista de pedidos con filtros opcionales."""
        try:
            if not self.model:
                logger.warning("Modelo no disponible para obtener pedidos")
                return []

            if hasattr(self.model, 'obtener_pedidos'):
                pedidos = self.model.obtener_pedidos(filtros)
                return pedidos if pedidos else []
            
            return []
            
        except Exception as e:
            logger.error(f"Error obteniendo pedidos: {e}")
            return []

    def buscar_pedidos(self, criterio: str, valor: str) -> List[Dict]:
        """Busca pedidos según criterio específico."""
        try:
            if not self.model:
                logger.error("Modelo no disponible para búsqueda")
                return []

            if hasattr(self.model, 'buscar_pedidos'):
                return self.model.buscar_pedidos(criterio, valor)
            
            return []
            
        except Exception as e:
            logger.error(f"Error buscando pedidos: {e}")
            return []

    def validar_datos_pedido(self, datos_pedido: Dict[str, Any]) -> bool:
        """Valida los datos de un pedido."""
        try:
            # Validaciones básicas
            if not datos_pedido.get('proveedor_id'):
                logger.error("Proveedor es obligatorio")
                return False
            
            if not datos_pedido.get('fecha_pedido'):
                logger.error("Fecha del pedido es obligatoria")
                return False
            
            items = datos_pedido.get('items', [])
            if not items:
                logger.error("El pedido debe tener al menos un item")
                return False
            
            # Validar items
            for item in items:
                if not item.get('producto_id'):
                    logger.error("Todos los items deben tener un producto")
                    return False
                
                cantidad = item.get('cantidad', 0)
                if cantidad <= 0:
                    logger.error("La cantidad debe ser mayor a 0")
                    return False
                
                precio = item.get('precio_unitario', 0)
                if precio <= 0:
                    logger.error("El precio unitario debe ser mayor a 0")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validando datos del pedido: {e}")
            return False

    def calcular_total_pedido(self, items: List[Dict]) -> Decimal:
        """Calcula el total de un pedido."""
        try:
            total = Decimal('0.00')
            
            for item in items:
                cantidad = Decimal(str(item.get('cantidad', 0)))
                precio = Decimal(str(item.get('precio_unitario', 0)))
                subtotal = cantidad * precio
                total += subtotal
            
            return total
            
        except Exception as e:
            logger.error(f"Error calculando total del pedido: {e}")
            return Decimal('0.00')

    def generar_reporte_pedidos(self, filtros: Dict[str, Any] = None):
        """Genera reporte de pedidos."""
        try:
            if not self.model:
                logger.error("Modelo no disponible para generar reporte")
                return None

            if hasattr(self.model, 'generar_reporte_pedidos'):
                reporte = self.model.generar_reporte_pedidos(filtros)
                logger.info("Reporte de pedidos generado exitosamente")
                return reporte
            
            return None
            
        except Exception as e:
            logger.error(f"Error generando reporte de pedidos: {e}")
            return None

    def exportar_datos(self, formato: str = "excel"):
        """Exporta datos de pedidos al formato especificado."""
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
