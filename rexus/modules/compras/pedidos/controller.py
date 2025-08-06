"""
Controlador de Pedidos de Compras

Maneja la lógica de control entre el modelo y la vista para pedidos/órdenes de compra.
"""

from PyQt6.QtCore import QObject
from typing import Dict, List, Any
from rexus.core.auth_decorators import auth_required, permission_required
from rexus.ui.feedback import show_success, show_error, show_warning
from .model import PedidosModel


class ComprasPedidosController(QObject):
    """Controlador para gestionar pedidos de compra."""

    def __init__(self, model=None, view=None, db_connection=None, usuarios_model=None):
        """
        Inicializa el controlador de pedidos.

        Args:
            model: Modelo de pedidos (opcional)
            view: Vista de pedidos
            db_connection: Conexión a la base de datos
            usuarios_model: Modelo de usuarios para auth
        """
        super().__init__()
        self.view = view
        self.db_connection = db_connection
        self.usuarios_model = usuarios_model
        self.usuario_actual = "SISTEMA"
        
        # Inicializar modelo de pedidos
        self.pedidos_model = model or PedidosModel(db_connection)

    @auth_required
    def cargar_pedidos(self):
        """Carga todos los pedidos de compras."""
        try:
            pedidos = self.pedidos_model.obtener_todos_pedidos()
            if self.view and hasattr(self.view, 'actualizar_tabla_pedidos'):
                self.view.actualizar_tabla_pedidos(pedidos)
            print(f"[PEDIDOS] {len(pedidos)} pedidos cargados exitosamente")
            return pedidos
        except Exception as e:
            print(f"[ERROR PEDIDOS] Error cargando pedidos: {e}")
            if self.view:
                show_error(self.view, "Error", f"Error cargando pedidos: {e}")
            return []

    @auth_required
    @permission_required("crear_pedidos")
    def crear_nuevo_pedido(self, datos_pedido: Dict[str, Any]):
        """
        Crea un nuevo pedido de compra.

        Args:
            datos_pedido: Datos del pedido a crear
        """
        try:
            # Validar datos requeridos
            if not datos_pedido.get('proveedor_id'):
                show_error(self.view, "Error", "Debe seleccionar un proveedor")
                return False
            
            if not datos_pedido.get('fecha_pedido'):
                show_error(self.view, "Error", "Debe especificar la fecha del pedido")
                return False

            # Crear el pedido
            exito = self.pedidos_model.crear_pedido_compra(
                proveedor_id=datos_pedido['proveedor_id'],
                fecha_pedido=datos_pedido['fecha_pedido'],
                fecha_entrega_esperada=datos_pedido.get('fecha_entrega_esperada', ''),
                estado=datos_pedido.get('estado', 'PENDIENTE'),
                observaciones=datos_pedido.get('observaciones', ''),
                usuario_creacion=self.usuario_actual
            )

            if exito:
                show_success(self.view, "Éxito", "Pedido creado exitosamente")
                self.cargar_pedidos()  # Recargar lista
                return True
            else:
                show_error(self.view, "Error", "No se pudo crear el pedido")
                return False

        except Exception as e:
            print(f"[ERROR PEDIDOS] Error creando pedido: {e}")
            show_error(self.view, "Error", f"Error creando pedido: {e}")
            return False

    @auth_required
    def obtener_pedidos_por_estado(self, estado: str):
        """
        Obtiene pedidos filtrados por estado.

        Args:
            estado: Estado de los pedidos a obtener
        """
        try:
            pedidos = self.pedidos_model.obtener_pedidos_por_estado(estado)
            if self.view and hasattr(self.view, 'actualizar_tabla_pedidos'):
                self.view.actualizar_tabla_pedidos(pedidos)
            return pedidos
        except Exception as e:
            print(f"[ERROR PEDIDOS] Error obteniendo pedidos por estado: {e}")
            if self.view:
                show_error(self.view, "Error", f"Error obteniendo pedidos: {e}")
            return []

    @auth_required
    @permission_required("modificar_pedidos")
    def actualizar_estado_pedido(self, pedido_id: int, nuevo_estado: str):
        """
        Actualiza el estado de un pedido.

        Args:
            pedido_id: ID del pedido
            nuevo_estado: Nuevo estado del pedido
        """
        try:
            # Validar estado
            estados_validos = ["PENDIENTE", "ENVIADO", "RECIBIDO", "CANCELADO"]
            if nuevo_estado not in estados_validos:
                show_error(self.view, "Error", f"Estado '{nuevo_estado}' no válido")
                return False

            exito = self.pedidos_model.actualizar_estado_pedido(
                pedido_id=pedido_id,
                nuevo_estado=nuevo_estado,
                usuario_actualizacion=self.usuario_actual
            )

            if exito:
                show_success(self.view, "Éxito", f"Pedido actualizado a estado {nuevo_estado}")
                self.cargar_pedidos()  # Recargar lista
                return True
            else:
                show_error(self.view, "Error", "No se pudo actualizar el pedido")
                return False

        except Exception as e:
            print(f"[ERROR PEDIDOS] Error actualizando estado: {e}")
            show_error(self.view, "Error", f"Error actualizando pedido: {e}")
            return False

    @auth_required
    def agregar_detalle_a_pedido(self, pedido_id: int, detalle_data: Dict[str, Any]):
        """
        Agrega un detalle a un pedido existente.

        Args:
            pedido_id: ID del pedido
            detalle_data: Datos del detalle a agregar
        """
        try:
            # Validar datos del detalle
            if not detalle_data.get('producto_id'):
                show_error(self.view, "Error", "Debe especificar el producto")
                return False
                
            if not detalle_data.get('cantidad') or float(detalle_data['cantidad']) <= 0:
                show_error(self.view, "Error", "La cantidad debe ser mayor a 0")
                return False

            # Calcular subtotal si no viene calculado
            cantidad = float(detalle_data['cantidad'])
            precio_unitario = float(detalle_data.get('precio_unitario', 0))
            subtotal = detalle_data.get('subtotal', cantidad * precio_unitario)

            exito = self.pedidos_model.agregar_detalle_pedido(
                pedido_id=pedido_id,
                producto_id=detalle_data['producto_id'],
                cantidad=cantidad,
                precio_unitario=precio_unitario,
                subtotal=subtotal
            )

            if exito:
                show_success(self.view, "Éxito", "Detalle agregado al pedido")
                return True
            else:
                show_error(self.view, "Error", "No se pudo agregar el detalle")
                return False

        except Exception as e:
            print(f"[ERROR PEDIDOS] Error agregando detalle: {e}")
            show_error(self.view, "Error", f"Error agregando detalle: {e}")
            return False

    def set_usuario_actual(self, usuario: str):
        """
        Establece el usuario actual para las operaciones.

        Args:
            usuario: Nombre del usuario actual
        """
        self.usuario_actual = usuario
