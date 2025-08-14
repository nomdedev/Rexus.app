"""
Modelo de Pedidos de Compras

Maneja la lógica de negocio y acceso a datos para órdenes de compra.
"""

from typing import Any, Dict, List
from datetime import datetime
from rexus.utils.security import SecurityUtils


class PedidosModel:
    """Modelo para gestionar pedidos/órdenes de compra."""

    def __init__(self, db_connection=None):
        """
        Inicializa el modelo de pedidos.

        Args:
            db_connection: Conexión a la base de datos
        """
        self.db_connection = db_connection
        self.tabla_pedidos = "pedidos_compra"
        self.tabla_detalle_pedidos = "detalle_pedidos_compra"
        self._crear_tablas_si_no_existen()

    def _crear_tablas_si_no_existen(self):
        """Verifica que las tablas de pedidos existan."""
        if not self.db_connection:
            return

        try:
            cursor = self.db_connection.cursor()

            # Verificar tabla pedidos_compra
            cursor.execute(
                "SELECT * FROM sysobjects WHERE name=? AND xtype='U'",
                (self.tabla_pedidos,),
            )
            if cursor.fetchone():
                print(f"[PEDIDOS] Tabla '{self.tabla_pedidos}' verificada.")
            else:
                print(f"[ADVERTENCIA] La tabla '{self.tabla_pedidos}' no existe.")

            # Verificar tabla detalle_pedidos_compra
            cursor.execute(
                "SELECT * FROM sysobjects WHERE name=? AND xtype='U'",
                (self.tabla_detalle_pedidos,),
            )
            if cursor.fetchone():
                print(f"[PEDIDOS] Tabla '{self.tabla_detalle_pedidos}' verificada.")
            else:
                print(f"[ADVERTENCIA] La tabla '{self.tabla_detalle_pedidos}' no existe.")

        except Exception as e:
            print(f"[ERROR PEDIDOS] Error verificando tablas: {e}")

    def crear_pedido_compra(
        self,
        proveedor_id: int,
        fecha_pedido: str,
        fecha_entrega_esperada: str,
        estado: str = "PENDIENTE",
        observaciones: str = "",
        usuario_creacion: str = "Sistema"
    ) -> bool:
        """
        Crea un nuevo pedido de compra.

        Args:
            proveedor_id: ID del proveedor
            fecha_pedido: Fecha del pedido
            fecha_entrega_esperada: Fecha esperada de entrega
            estado: Estado del pedido (PENDIENTE,
ENVIADO,
                RECIBIDO,
                CANCELADO)
            observaciones: Observaciones del pedido
            usuario_creacion: Usuario que crea el pedido

        Returns:
            bool: True si el pedido fue creado exitosamente
        """
        if not self.db_connection:
            return False

        try:
            cursor = self.db_connection.cursor()

            # Sanitizar datos de entrada
            proveedor_id = SecurityUtils.sanitize_input(str(proveedor_id))
            fecha_pedido = SecurityUtils.sanitize_input(fecha_pedido)
            fecha_entrega_esperada = SecurityUtils.sanitize_input(fecha_entrega_esperada)
            estado = SecurityUtils.sanitize_input(estado)
            observaciones = SecurityUtils.sanitize_input(observaciones)
            usuario_creacion = SecurityUtils.sanitize_input(usuario_creacion)

            query = f"""
                INSERT INTO [{self.tabla_pedidos}] (
                    proveedor_id, fecha_pedido, fecha_entrega_esperada,
                    estado, observaciones, usuario_creacion, fecha_creacion
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """

            cursor.execute(
                query,
                (
                    proveedor_id,
                    fecha_pedido,
                    fecha_entrega_esperada,
                    estado,
                    observaciones,
                    usuario_creacion,
                    datetime.now().isoformat()
                )
            )

            self.db_connection.commit()
            print(f"[PEDIDOS] Pedido creado exitosamente para proveedor {proveedor_id}")
            return True

        except Exception as e:
            print(f"[ERROR PEDIDOS] Error creando pedido: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return False

    def obtener_pedidos_por_estado(self, estado: str) -> List[Dict[str, Any]]:
        """
        Obtiene pedidos filtrados por estado.

        Args:
            estado: Estado de los pedidos a obtener

        Returns:
            List[Dict]: Lista de pedidos
        """
        if not self.db_connection:
            return []

        try:
            cursor = self.db_connection.cursor()
            estado = SecurityUtils.sanitize_input(estado)

            query = f"""
                SELECT
                    pc.id, pc.proveedor_id, pc.fecha_pedido, pc.fecha_entrega_esperada,
                    pc.estado, pc.observaciones, pc.usuario_creacion, pc.fecha_creacion,
                    prov.nombre as proveedor_nombre
                FROM [{self.tabla_pedidos}] pc
                LEFT JOIN [proveedores] prov ON pc.proveedor_id = prov.id
                WHERE pc.estado = ?
                ORDER BY pc.fecha_creacion DESC
            """

            cursor.execute(query, (estado,))
            columns = [column[0] for column in cursor.description]
            pedidos = []

            for row in cursor.fetchall():
                pedido = dict(zip(columns, row))
                pedidos.append(pedido)

            return pedidos

        except Exception as e:
            print(f"[ERROR PEDIDOS] Error obteniendo pedidos por estado: {e}")
            return []

    def actualizar_estado_pedido(self, pedido_id: int, nuevo_estado: str, usuario_actualizacion: str = "Sistema") -> bool:
        """
        Actualiza el estado de un pedido.

        Args:
            pedido_id: ID del pedido
            nuevo_estado: Nuevo estado del pedido
            usuario_actualizacion: Usuario que actualiza

        Returns:
            bool: True si se actualizó correctamente
        """
        if not self.db_connection:
            return False

        try:
            cursor = self.db_connection.cursor()

            # Sanitizar datos
            pedido_id = SecurityUtils.sanitize_input(str(pedido_id))
            nuevo_estado = SecurityUtils.sanitize_input(nuevo_estado)
            usuario_actualizacion = SecurityUtils.sanitize_input(usuario_actualizacion)

            query = f"""
                UPDATE [{self.tabla_pedidos}]
                SET estado = ?, usuario_actualizacion = ?, fecha_actualizacion = ?
                WHERE id = ?
            """

            cursor.execute(
                query,
                (nuevo_estado,
usuario_actualizacion,
                    datetime.now().isoformat(),
                    pedido_id)
            )

            self.db_connection.commit()
            print(f"[PEDIDOS] Estado del pedido {pedido_id} actualizado a {nuevo_estado}")
            return True

        except Exception as e:
            print(f"[ERROR PEDIDOS] Error actualizando estado pedido: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return False

    def obtener_todos_pedidos(self) -> List[Dict[str, Any]]:
        """
        Obtiene todos los pedidos de compra.

        Returns:
            List[Dict]: Lista de todos los pedidos
        """
        if not self.db_connection:
            return []

        try:
            cursor = self.db_connection.cursor()

            query = f"""
                SELECT
                    pc.id, pc.proveedor_id, pc.fecha_pedido, pc.fecha_entrega_esperada,
                    pc.estado, pc.observaciones, pc.usuario_creacion, pc.fecha_creacion,
                    prov.nombre as proveedor_nombre, prov.razon_social
                FROM [{self.tabla_pedidos}] pc
                LEFT JOIN [proveedores] prov ON pc.proveedor_id = prov.id
                ORDER BY pc.fecha_creacion DESC
            """

            cursor.execute(query)
            columns = [column[0] for column in cursor.description]
            pedidos = []

            for row in cursor.fetchall():
                pedido = dict(zip(columns, row))
                pedidos.append(pedido)

            return pedidos

        except Exception as e:
            print(f"[ERROR PEDIDOS] Error obteniendo todos los pedidos: {e}")
            return []

    def agregar_detalle_pedido(
        self,
        pedido_id: int,
        producto_id: int,
        cantidad: float,
        precio_unitario: float,
        subtotal: float
    ) -> bool:
        """
        Agrega un detalle a un pedido de compra.

        Args:
            pedido_id: ID del pedido
            producto_id: ID del producto
            cantidad: Cantidad solicitada
            precio_unitario: Precio por unidad
            subtotal: Subtotal del detalle

        Returns:
            bool: True si se agregó correctamente
        """
        if not self.db_connection:
            return False

        try:
            cursor = self.db_connection.cursor()

            # Sanitizar datos
            pedido_id = SecurityUtils.sanitize_input(str(pedido_id))
            producto_id = SecurityUtils.sanitize_input(str(producto_id))
            cantidad = SecurityUtils.sanitize_input(str(cantidad))
            precio_unitario = SecurityUtils.sanitize_input(str(precio_unitario))
            subtotal = SecurityUtils.sanitize_input(str(subtotal))

            query = f"""
                INSERT INTO [{self.tabla_detalle_pedidos}] (
                    pedido_id, producto_id, cantidad, precio_unitario, subtotal
                ) VALUES (?, ?, ?, ?, ?)
            """

            cursor.execute(query,
(pedido_id,
                producto_id,
                cantidad,
                precio_unitario,
                subtotal))
            self.db_connection.commit()
            print(f"[PEDIDOS] Detalle agregado al pedido {pedido_id}")
            return True

        except Exception as e:
            print(f"[ERROR PEDIDOS] Error agregando detalle pedido: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return False
