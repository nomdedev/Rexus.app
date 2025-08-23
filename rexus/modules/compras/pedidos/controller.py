"""
Controlador de Pedidos de Compras

Maneja la lógica de control entre el modelo y la vista para pedidos/órdenes de compra.
"""


import logging
logger = logging.getLogger(__name__)

                def agregar_detalle_a_pedido(self,
pedido_id: int,
        detalle_data: Dict[str,
        Any]):
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
            logger.info(f"[ERROR PEDIDOS] Error agregando detalle: {e}")
            show_error(self.view, "Error", f"Error agregando detalle: {e}")
            return False

    def set_usuario_actual(self, usuario: str):
        """
        Establece el usuario actual para las operaciones.

        Args:
            usuario: Nombre del usuario actual
        """
        self.usuario_actual = usuario
