"""
Modelo de Compras

Maneja la lógica de negocio y acceso a datos para el sistema de compras.
"""

import datetime
from typing import Any, Dict, List


class ComprasModel:
    """Modelo para gestionar las compras del sistema."""

    def __init__(self, db_connection=None):
        """
        Inicializa el modelo de compras.

        Args:
            db_connection: Conexión a la base de datos
        """
        self.db_connection = db_connection
        self.tabla_compras = "compras"
        self.tabla_detalle_compras = "detalle_compras"
        self._crear_tablas_si_no_existen()

    def _crear_tablas_si_no_existen(self):
        """Verifica que las tablas de compras existan en la base de datos."""
        if not self.db_connection:
            return

        try:
            cursor = self.db_connection.connection.cursor()

            # Verificar tabla compras
            cursor.execute(
                "SELECT * FROM sysobjects WHERE name=? AND xtype='U'",
                (self.tabla_compras,),
            )
            if cursor.fetchone():
                print(
                    f"[COMPRAS] Tabla '{self.tabla_compras}' verificada correctamente."
                )
            else:
                print(
                    f"[ADVERTENCIA] La tabla '{self.tabla_compras}' no existe en la base de datos."
                )

            # Verificar tabla detalle_compras
            cursor.execute(
                "SELECT * FROM sysobjects WHERE name=? AND xtype='U'",
                (self.tabla_detalle_compras,),
            )
            if cursor.fetchone():
                print(
                    f"[COMPRAS] Tabla '{self.tabla_detalle_compras}' verificada correctamente."
                )
            else:
                print(
                    f"[ADVERTENCIA] La tabla '{self.tabla_detalle_compras}' no existe en la base de datos."
                )

        except Exception as e:
            print(f"[ERROR COMPRAS] Error verificando tablas: {e}")

    def crear_compra(
        self,
        proveedor: str,
        numero_orden: str,
        fecha_pedido: datetime.date,
        fecha_entrega_estimada: datetime.date,
        estado: str = "PENDIENTE",
        observaciones: str = "",
        usuario_creacion: str = "",
        descuento: float = 0.0,
        impuestos: float = 0.0,
    ) -> bool:
        """
        Crea una nueva orden de compra.

        Args:
            proveedor: Nombre del proveedor
            numero_orden: Número de orden de compra
            fecha_pedido: Fecha del pedido
            fecha_entrega_estimada: Fecha estimada de entrega
            estado: Estado de la compra (PENDIENTE, APROBADA, RECIBIDA, CANCELADA)
            observaciones: Observaciones adicionales
            usuario_creacion: Usuario que crea la orden
            descuento: Descuento aplicado
            impuestos: Impuestos aplicados

        Returns:
            bool: True si se creó exitosamente
        """
        if not self.db_connection:
            print("[WARN COMPRAS] Sin conexión BD")
            return False

        try:
            cursor = self.db_connection.connection.cursor()

            sql_insert = """
            INSERT INTO compras
            (proveedor, numero_orden, fecha_pedido, fecha_entrega_estimada,
             estado, observaciones, usuario_creacion, descuento, impuestos,
             fecha_creacion, fecha_actualizacion)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE(), GETDATE())
            """

            cursor.execute(
                sql_insert,
                (
                    proveedor,
                    numero_orden,
                    fecha_pedido,
                    fecha_entrega_estimada,
                    estado,
                    observaciones,
                    usuario_creacion,
                    descuento,
                    impuestos,
                ),
            )

            self.db_connection.connection.commit()
            print(f"[COMPRAS] Orden creada: {numero_orden}")
            return True

        except Exception as e:
            print(f"[ERROR COMPRAS] Error creando orden: {e}")
            return False

    def obtener_todas_compras(self) -> List[Dict]:
        """
        Obtiene todas las órdenes de compra.

        Returns:
            List[Dict]: Lista de órdenes de compra
        """
        if not self.db_connection:
            return []

        try:
            cursor = self.db_connection.connection.cursor()

            sql_select = """
            SELECT
                c.id, c.proveedor, c.numero_orden, c.fecha_pedido,
                c.fecha_entrega_estimada, c.estado, c.observaciones,
                c.usuario_creacion, c.descuento, c.impuestos,
                c.fecha_creacion, c.fecha_actualizacion,
                ISNULL(SUM(dc.cantidad * dc.precio_unitario), 0) as total_sin_descuento,
                ISNULL(SUM(dc.cantidad * dc.precio_unitario), 0) - c.descuento + c.impuestos as total_final
            FROM compras c
            LEFT JOIN detalle_compras dc ON c.id = dc.compra_id
            GROUP BY c.id, c.proveedor, c.numero_orden, c.fecha_pedido,
                     c.fecha_entrega_estimada, c.estado, c.observaciones,
                     c.usuario_creacion, c.descuento, c.impuestos,
                     c.fecha_creacion, c.fecha_actualizacion
            ORDER BY c.fecha_creacion DESC
            """

            cursor.execute(sql_select)
            rows = cursor.fetchall()

            # Convertir a lista de diccionarios
            columns = [desc[0] for desc in cursor.description]
            compras = []

            for row in rows:
                compra = dict(zip(columns, row))
                compras.append(compra)

            print(f"[COMPRAS] Obtenidas {len(compras)} órdenes de compra")
            return compras

        except Exception as e:
            print(f"[ERROR COMPRAS] Error obteniendo compras: {e}")
            return []

    def actualizar_estado_compra(
        self, compra_id: int, nuevo_estado: str, usuario: str = ""
    ) -> bool:
        """
        Actualiza el estado de una orden de compra.

        Args:
            compra_id: ID de la orden de compra
            nuevo_estado: Nuevo estado
            usuario: Usuario que realiza la actualización

        Returns:
            bool: True si se actualizó exitosamente
        """
        if not self.db_connection:
            return False

        try:
            cursor = self.db_connection.connection.cursor()

            sql_update = """
            UPDATE compras
            SET estado = ?, fecha_actualizacion = GETDATE()
            WHERE id = ?
            """

            cursor.execute(sql_update, (nuevo_estado, compra_id))
            self.db_connection.connection.commit()

            print(
                f"[COMPRAS] Estado actualizado para compra {compra_id}: {nuevo_estado}"
            )
            return True

        except Exception as e:
            print(f"[ERROR COMPRAS] Error actualizando estado: {e}")
            return False

    def obtener_estadisticas_compras(self, dias: int = 30) -> Dict[str, Any]:
        """
        Obtiene estadísticas de compras.

        Args:
            dias: Número de días hacia atrás para analizar

        Returns:
            Dict: Estadísticas de compras
        """
        if not self.db_connection:
            return {}

        try:
            cursor = self.db_connection.connection.cursor()
            fecha_limite = datetime.datetime.now() - datetime.timedelta(days=dias)

            # Total de órdenes
            cursor.execute(
                """
                SELECT COUNT(*) FROM compras
                WHERE fecha_creacion >= ?
            """,
                (fecha_limite,),
            )
            total_ordenes = cursor.fetchone()[0]

            # Órdenes por estado
            cursor.execute(
                """
                SELECT estado, COUNT(*) as cantidad
                FROM compras
                WHERE fecha_creacion >= ?
                GROUP BY estado
                ORDER BY cantidad DESC
            """,
                (fecha_limite,),
            )
            ordenes_por_estado = [
                {"estado": row[0], "cantidad": row[1]} for row in cursor.fetchall()
            ]

            # Monto total
            cursor.execute(
                """
                SELECT
                    ISNULL(SUM(
                        ISNULL((SELECT SUM(dc.cantidad * dc.precio_unitario)
                                FROM detalle_compras dc
                                WHERE dc.compra_id = c.id), 0) - c.descuento + c.impuestos
                    ), 0) as total
                FROM compras c
                WHERE c.fecha_creacion >= ?
            """,
                (fecha_limite,),
            )
            monto_total = cursor.fetchone()[0] or 0

            # Proveedores más activos
            cursor.execute(
                """
                SELECT proveedor, COUNT(*) as cantidad
                FROM compras
                WHERE fecha_creacion >= ?
                GROUP BY proveedor
                ORDER BY cantidad DESC
            """,
                (fecha_limite,),
            )
            proveedores_activos = [
                {"proveedor": row[0], "cantidad": row[1]} for row in cursor.fetchall()
            ]

            return {
                "total_ordenes": total_ordenes,
                "ordenes_por_estado": ordenes_por_estado,
                "monto_total": monto_total,
                "proveedores_activos": proveedores_activos,
            }

        except Exception as e:
            print(f"[ERROR COMPRAS] Error obteniendo estadísticas: {e}")
            return {}

    def buscar_compras(
        self,
        proveedor: str = "",
        estado: str = "",
        fecha_inicio: datetime.date = None,
        fecha_fin: datetime.date = None,
        numero_orden: str = "",
    ) -> List[Dict]:
        """
        Busca órdenes de compra con filtros.

        Args:
            proveedor: Filtrar por proveedor
            estado: Filtrar por estado
            fecha_inicio: Fecha de inicio del rango
            fecha_fin: Fecha fin del rango
            numero_orden: Filtrar por número de orden

        Returns:
            List[Dict]: Lista de órdenes de compra filtradas
        """
        if not self.db_connection:
            return []

        try:
            cursor = self.db_connection.connection.cursor()

            # Construir query con filtros
            conditions = []
            params = []

            if proveedor:
                conditions.append("c.proveedor LIKE ?")
                params.append(f"%{proveedor}%")

            if estado:
                conditions.append("c.estado = ?")
                params.append(estado)

            if fecha_inicio:
                conditions.append("c.fecha_pedido >= ?")
                params.append(fecha_inicio)

            if fecha_fin:
                conditions.append("c.fecha_pedido <= ?")
                params.append(fecha_fin)

            if numero_orden:
                conditions.append("c.numero_orden LIKE ?")
                params.append(f"%{numero_orden}%")

            where_clause = ""
            if conditions:
                where_clause = "WHERE " + " AND ".join(conditions)

            sql_select = f"""
            SELECT
                c.id, c.proveedor, c.numero_orden, c.fecha_pedido,
                c.fecha_entrega_estimada, c.estado, c.observaciones,
                c.usuario_creacion, c.descuento, c.impuestos,
                c.fecha_creacion, c.fecha_actualizacion,
                ISNULL(SUM(dc.cantidad * dc.precio_unitario), 0) as total_sin_descuento,
                ISNULL(SUM(dc.cantidad * dc.precio_unitario), 0) - c.descuento + c.impuestos as total_final
            FROM compras c
            LEFT JOIN detalle_compras dc ON c.id = dc.compra_id
            {where_clause}
            GROUP BY c.id, c.proveedor, c.numero_orden, c.fecha_pedido,
                     c.fecha_entrega_estimada, c.estado, c.observaciones,
                     c.usuario_creacion, c.descuento, c.impuestos,
                     c.fecha_creacion, c.fecha_actualizacion
            ORDER BY c.fecha_creacion DESC
            """

            cursor.execute(sql_select, params)
            rows = cursor.fetchall()

            # Convertir a lista de diccionarios
            columns = [desc[0] for desc in cursor.description]
            compras = []

            for row in rows:
                compra = dict(zip(columns, row))
                compras.append(compra)

            print(f"[COMPRAS] Búsqueda retornó {len(compras)} órdenes")
            return compras

        except Exception as e:
            print(f"[ERROR COMPRAS] Error en búsqueda: {e}")
            return []
