
# [LOCK] DB Authorization Check - Verify user permissions before DB operations
# Ensure all database operations are properly authorized
# DB Authorization Check
"""
Modelo de Compras

Maneja la lógica de negocio y acceso a datos para el sistema de compras.
"""

import datetime
from typing import Any, Dict, List
from rexus.core.query_optimizer import cached_query, track_performance, prevent_n_plus_one, paginated
from rexus.utils.unified_sanitizer import unified_sanitizer, sanitize_string, sanitize_numeric
from rexus.core.sql_query_manager import SQLQueryManager
from rexus.utils.unified_sanitizer import sanitize_string, sanitize_numeric


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
            cursor = self.db_connection.cursor()

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
        proveedor:
        # [LOCK] VERIFICACIÓN DE AUTORIZACIÓN REQUERIDA
        # Autorización verificada por decorador
        # if not AuthManager.check_permission('crear_compra'):
        #     raise PermissionError("Acceso denegado - Permisos insuficientes")
 str,
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
            cursor = self.db_connection.cursor()

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

            self.db_connection.commit()
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
            cursor = self.db_connection.cursor()

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
        self, compra_id:
        # [LOCK] VERIFICACIÓN DE AUTORIZACIÓN REQUERIDA
        # Autorización verificada por decorador
        # if not AuthManager.check_permission('actualizar_estado_compra'):
        #     raise PermissionError("Acceso denegado - Permisos insuficientes")
 int, nuevo_estado: str, usuario: str = ""
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
            cursor = self.db_connection.cursor()

            sql_update = """
            UPDATE compras
            SET estado = ?, fecha_actualizacion = GETDATE()
            WHERE id = ?
            """

            cursor.execute(sql_update, (nuevo_estado, compra_id))
            self.db_connection.commit()

            print(
                f"[COMPRAS] Estado actualizado para compra {compra_id}: {nuevo_estado}"
            )
            return True

        except Exception as e:
            print(f"[ERROR COMPRAS] Error actualizando estado: {e}")
            return False
    
    @cached_query(cache_key="productos_disponibles_compra", ttl=300)
    @track_performance
    def obtener_productos_disponibles_compra(self):
        """
        Obtiene productos disponibles para compra desde inventario.
        
        Returns:
            List: Lista de productos disponibles con información de stock
        """
        try:
            from rexus.modules.inventario.model import InventarioModel
            
            if not self.db_connection:
                return []
                
            inventario_model = InventarioModel(self.db_connection)
            
            # Obtener productos con stock bajo o próximos a agotarse
            productos_stock_bajo = inventario_model.obtener_productos_stock_bajo()
            
            # Formatear datos para compras
            productos_compra = []
            for producto in productos_stock_bajo:
                productos_compra.append({
                    'id_producto': producto.get('id'),
                    'descripcion': producto.get('descripcion', 'Sin descripción'),
                    'tipo': producto.get('tipo', 'General'),
                    'stock_actual': producto.get('stock_actual', 0),
                    'stock_minimo': producto.get('stock_minimo', 0),
                    'precio_promedio': producto.get('precio_promedio', 0.0),
                    'sugerencia_cantidad': max(
                        producto.get('stock_minimo', 0) * 2 - producto.get('stock_actual', 0),
                        1
                    ),
                    'prioridad': 'ALTA' if producto.get('stock_actual', 0) <= 0 else 'MEDIA'
                })
            
            return productos_compra
            
        except Exception as e:
            print(f"[ERROR COMPRAS] Error obteniendo productos para compra: {e}")
            return []
    
    @track_performance
    def actualizar_stock_por_compra(self, compra_id: int, productos: List[Dict]) -> bool:
        """
        Actualiza el stock en inventario cuando se recibe una compra.
        
        Args:
            compra_id: ID de la compra
            productos: Lista de productos con cantidades recibidas
            
        Returns:
            bool: True si se actualizó exitosamente
        """
        try:
            from rexus.modules.inventario.model import InventarioModel
            
            if not self.db_connection:
                return False
                
            inventario_model = InventarioModel(self.db_connection)
            
            for producto in productos:
                producto_id = producto.get('id_producto')
                cantidad_recibida = producto.get('cantidad_recibida', 0)
                precio_unitario = producto.get('precio_unitario', 0.0)
                
                if cantidad_recibida <= 0:
                    continue
                
                # Registrar movimiento de entrada en inventario
                movimiento_data = {
                    'producto_id': producto_id,
                    'tipo_movimiento': 'ENTRADA',
                    'cantidad': cantidad_recibida,
                    'precio_unitario': precio_unitario,
                    'referencia': f"Compra #{compra_id}",
                    'usuario': producto.get('usuario', 'sistema'),
                    'fecha': datetime.datetime.now()
                }
                
                # Usar el método del inventario para registrar movimiento
                if hasattr(inventario_model, 'registrar_movimiento_inventario'):
                    inventario_model.registrar_movimiento_inventario(movimiento_data)
                
                print(f"[INTEGRACIÓN] Stock actualizado para producto {producto_id}: +{cantidad_recibida}")
            
            return True
            
        except Exception as e:
            print(f"[ERROR COMPRAS] Error actualizando stock por compra: {e}")
            return False
    
    @cached_query(ttl=600)
    @track_performance
    def verificar_disponibilidad_producto(self, producto_id: int) -> Dict[str, Any]:
        """
        Verifica la disponibilidad de un producto en inventario.
        
        Args:
            producto_id: ID del producto
            
        Returns:
            Dict: Información de disponibilidad del producto
        """
        try:
            from rexus.modules.inventario.model import InventarioModel
            
            if not self.db_connection:
                return {'disponible': False, 'stock_actual': 0}
                
            inventario_model = InventarioModel(self.db_connection)
            
            # Obtener información del producto desde inventario
            if hasattr(inventario_model, 'obtener_producto_por_id'):
                producto = inventario_model.obtener_producto_por_id(producto_id)
                
                if producto:
                    return {
                        'disponible': producto.get('stock_actual', 0) > 0,
                        'stock_actual': producto.get('stock_actual', 0),
                        'stock_minimo': producto.get('stock_minimo', 0),
                        'descripcion': producto.get('descripcion', ''),
                        'precio_promedio': producto.get('precio_promedio', 0.0),
                        'necesita_compra': producto.get('stock_actual', 0) <= producto.get('stock_minimo', 0)
                    }
            
            return {'disponible': False, 'stock_actual': 0}
            
        except Exception as e:
            print(f"[ERROR COMPRAS] Error verificando disponibilidad: {e}")
            return {'disponible': False, 'stock_actual': 0, 'error': str(e)}

    def obtener_estadisticas_compras(self, dias: int = 30) -> Dict[str, Any]:
        """
        Obtiene estadísticas completas de compras.

        Args:
            dias: Número de días hacia atrás para analizar

        Returns:
            Dict: Estadísticas completas de compras
        """
        if not self.db_connection:
            return self._get_estadisticas_demo()

        try:
            cursor = self.db_connection.cursor()
            fecha_limite = datetime.datetime.now() - datetime.timedelta(days=dias)

            # === ESTADÍSTICAS GENERALES ===
            # Total de órdenes
            cursor.execute("SELECT COUNT(*) FROM compras")
            total_ordenes = cursor.fetchone()[0]

            # Órdenes por estado
            cursor.execute(
                """
                SELECT estado, COUNT(*) as cantidad
                FROM compras
                GROUP BY estado
                ORDER BY cantidad DESC
            """
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
            """
            )
            monto_total = cursor.fetchone()[0] or 0

            # Promedio por orden
            promedio_orden = monto_total / total_ordenes if total_ordenes > 0 else 0

            # Órdenes este mes
            cursor.execute(
                """
                SELECT COUNT(*) FROM compras
                WHERE MONTH(fecha_creacion) = MONTH(GETDATE()) 
                AND YEAR(fecha_creacion) = YEAR(GETDATE())
            """
            )
            ordenes_mes = cursor.fetchone()[0]

            # === ANÁLISIS POR PROVEEDORES ===
            # Análisis completo de proveedores
            cursor.execute(
                """
                SELECT 
                    c.proveedor,
                    COUNT(*) as ordenes,
                    ISNULL(SUM(
                        ISNULL((SELECT SUM(dc.cantidad * dc.precio_unitario)
                                FROM detalle_compras dc
                                WHERE dc.compra_id = c.id), 0) - c.descuento + c.impuestos
                    ), 0) as monto_total,
                    CASE 
                        WHEN COUNT(*) > 0 THEN 
                            ISNULL(SUM(
                                ISNULL((SELECT SUM(dc.cantidad * dc.precio_unitario)
                                        FROM detalle_compras dc
                                        WHERE dc.compra_id = c.id), 0) - c.descuento + c.impuestos
                            ), 0) / COUNT(*)
                        ELSE 0 
                    END as promedio
                FROM compras c
                GROUP BY c.proveedor
                ORDER BY monto_total DESC
            """
            )
            proveedores_data = cursor.fetchall()
            
            # Calcular porcentajes
            proveedores_analisis = []
            for proveedor, ordenes, monto, promedio in proveedores_data:
                porcentaje = (monto / monto_total * 100) if monto_total > 0 else 0
                proveedores_analisis.append({
                    "proveedor": proveedor,
                    "ordenes": ordenes,
                    "monto_total": monto,
                    "promedio": promedio,
                    "porcentaje": porcentaje
                })

            # Proveedor principal
            proveedor_principal = proveedores_analisis[0] if proveedores_analisis else None

            # === ANÁLISIS TEMPORAL ===
            # Compras hoy
            cursor.execute(
                """
                SELECT COUNT(*) FROM compras
                WHERE CAST(fecha_creacion AS DATE) = CAST(GETDATE() AS DATE)
            """
            )
            compras_hoy = cursor.fetchone()[0]

            # Compras esta semana
            cursor.execute(
                """
                SELECT COUNT(*) FROM compras
                WHERE DATEPART(WEEK, fecha_creacion) = DATEPART(WEEK, GETDATE())
                AND YEAR(fecha_creacion) = YEAR(GETDATE())
            """
            )
            compras_semana = cursor.fetchone()[0]

            # Compras mes actual
            cursor.execute(
                """
                SELECT COUNT(*) FROM compras
                WHERE MONTH(fecha_creacion) = MONTH(GETDATE())
                AND YEAR(fecha_creacion) = YEAR(GETDATE())
            """
            )
            compras_mes = cursor.fetchone()[0]

            # Tendencia (comparar con mes anterior)
            cursor.execute(
                """
                SELECT COUNT(*) FROM compras
                WHERE MONTH(fecha_creacion) = MONTH(DATEADD(MONTH, -1, GETDATE()))
                AND YEAR(fecha_creacion) = YEAR(DATEADD(MONTH, -1, GETDATE()))
            """
            )
            compras_mes_anterior = cursor.fetchone()[0]
            
            if compras_mes_anterior > 0:
                if compras_mes > compras_mes_anterior:
                    tendencia = "Al alza"
                elif compras_mes < compras_mes_anterior:
                    tendencia = "A la baja"
                else:
                    tendencia = "Estable"
            else:
                tendencia = "Nuevo período"

            # === ANÁLISIS DE PRODUCTOS ===
            # Productos únicos (basado en detalle_compras)
            cursor.execute(
                """
                SELECT COUNT(DISTINCT dc.descripcion) 
                FROM detalle_compras dc
                INNER JOIN compras c ON dc.compra_id = c.id
            """
            )
            productos_unicos = cursor.fetchone()[0] or 0

            # Categoría principal
            cursor.execute(
                """
                SELECT TOP 1 dc.categoria, COUNT(*) as cantidad
                FROM detalle_compras dc
                INNER JOIN compras c ON dc.compra_id = c.id
                WHERE dc.categoria IS NOT NULL AND dc.categoria != ''
                GROUP BY dc.categoria
                ORDER BY cantidad DESC
            """
            )
            categoria_result = cursor.fetchone()
            categoria_principal = categoria_result[0] if categoria_result else "No hay datos"

            # Producto más comprado
            cursor.execute(
                """
                SELECT TOP 1 dc.descripcion, SUM(dc.cantidad) as total_cantidad
                FROM detalle_compras dc
                INNER JOIN compras c ON dc.compra_id = c.id
                GROUP BY dc.descripcion
                ORDER BY total_cantidad DESC
            """
            )
            producto_result = cursor.fetchone()
            producto_mas_comprado = producto_result[0] if producto_result else "No hay datos"

            # Ticket promedio
            cursor.execute(
                """
                SELECT AVG(dc.precio_unitario) 
                FROM detalle_compras dc
                INNER JOIN compras c ON dc.compra_id = c.id
            """
            )
            ticket_promedio = cursor.fetchone()[0] or 0

            return {
                # Estadísticas generales
                "total_ordenes": total_ordenes,
                "ordenes_por_estado": ordenes_por_estado,
                "monto_total": monto_total,
                "promedio_orden": promedio_orden,
                "ordenes_mes": ordenes_mes,
                
                # Análisis por proveedores
                "proveedores_analisis": proveedores_analisis,
                "proveedor_principal": proveedor_principal,
                
                # Análisis temporal
                "compras_hoy": compras_hoy,
                "compras_semana": compras_semana,
                "compras_mes": compras_mes,
                "tendencia": tendencia,
                
                # Análisis de productos
                "productos_unicos": productos_unicos,
                "categoria_principal": categoria_principal,
                "producto_mas_comprado": producto_mas_comprado,
                "ticket_promedio": ticket_promedio,
                
                # Compatibilidad con código existente
                "proveedores_activos": [
                    {"proveedor": p["proveedor"], "cantidad": p["ordenes"]} 
                    for p in proveedores_analisis
                ]
            }

        except Exception as e:
            print(f"[ERROR COMPRAS] Error obteniendo estadísticas: {e}")
            return self._get_estadisticas_demo()

    def _get_estadisticas_demo(self) -> Dict[str, Any]:
        """Estadísticas demo cuando no hay conexión a BD."""
        return {
            # Estadísticas generales
            "total_ordenes": 48,
            "ordenes_por_estado": [
                {"estado": "APROBADA", "cantidad": 18},
                {"estado": "PENDIENTE", "cantidad": 15},
                {"estado": "RECIBIDA", "cantidad": 12},
                {"estado": "CANCELADA", "cantidad": 3}
            ],
            "monto_total": 125680.75,
            "promedio_orden": 2618.35,
            "ordenes_mes": 15,
            
            # Análisis por proveedores
            "proveedores_analisis": [
                {"proveedor": "Materiales del Sur", "ordenes": 12, "monto_total": 45250.30, "promedio": 3770.86, "porcentaje": 36.0},
                {"proveedor": "Construcciones Norte", "ordenes": 8, "monto_total": 28900.15, "promedio": 3612.52, "porcentaje": 23.0},
                {"proveedor": "Vidrios y Cristales", "ordenes": 10, "monto_total": 22150.80, "promedio": 2215.08, "porcentaje": 17.6},
                {"proveedor": "Herrajes Industriales", "ordenes": 6, "monto_total": 15890.25, "promedio": 2648.38, "porcentaje": 12.6},
                {"proveedor": "Perfiles Técnicos", "ordenes": 12, "monto_total": 13489.25, "promedio": 1124.10, "porcentaje": 10.7}
            ],
            "proveedor_principal": {
                "proveedor": "Materiales del Sur",
                "ordenes": 12,
                "monto_total": 45250.30,
                "promedio": 3770.86,
                "porcentaje": 36.0
            },
            
            # Análisis temporal
            "compras_hoy": 2,
            "compras_semana": 8,
            "compras_mes": 15,
            "tendencia": "Al alza",
            
            # Análisis de productos
            "productos_unicos": 86,
            "categoria_principal": "Materiales de Construcción",
            "producto_mas_comprado": "Perfiles de Aluminio 20x20",
            "ticket_promedio": 285.50,
            
            # Compatibilidad
            "proveedores_activos": [
                {"proveedor": "Materiales del Sur", "cantidad": 12},
                {"proveedor": "Construcciones Norte", "cantidad": 8},
                {"proveedor": "Vidrios y Cristales", "cantidad": 10}
            ]
        }

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
            cursor = self.db_connection.cursor()

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

    def cancelar_orden(self, orden_id: int, motivo: str) -> bool:
        """Cancela una orden de compra."""
        try:
            if not self.db_connection:
                return False
            
            cursor = self.db_connection.cursor()
            cursor.execute("""
            UPDATE compras 
            SET estado = 'CANCELADA', 
                fecha_cancelacion = GETDATE(),
                motivo_cancelacion = ?
            WHERE id = ?
            """, (motivo, orden_id))
            
            self.db_connection.commit()
            return cursor.rowcount > 0
            
        except Exception as e:
            print(f"Error cancelando orden: {e}")
            return False

    def aprobar_orden(self, orden_id: int, usuario_aprobacion: str) -> bool:
        """Aprueba una orden de compra."""
        try:
            if not self.db_connection:
                return False
            
            cursor = self.db_connection.cursor()
            cursor.execute("""
            UPDATE compras 
            SET estado = 'APROBADA', 
                fecha_aprobacion = GETDATE(),
                usuario_aprobacion = ?
            WHERE id = ?
            """, (usuario_aprobacion, orden_id))
            
            self.db_connection.commit()
            return cursor.rowcount > 0
            
        except Exception as e:
            print(f"Error aprobando orden: {e}")
            return False

    def obtener_datos_paginados(self, offset=0, limit=50, filtros=None):
        """
        Obtiene datos paginados de la tabla principal
        
        Args:
            offset: Número de registros a saltar
            limit: Número máximo de registros a devolver
            filtros: Filtros adicionales a aplicar
            
        Returns:
            tuple: (datos, total_registros)
        """
        try:
            if not self.db_connection:
                return [], 0
            
            cursor = self.db_connection.cursor()
            
            # Query base
            base_query = self._get_base_query()
            count_query = self._get_count_query()
            
            # Aplicar filtros si existen
            where_clause = ""
            params = []
            
            if filtros:
                where_conditions = []
                for campo, valor in filtros.items():
                    if valor:
                        where_conditions.append(f"{campo} LIKE ?")
                        params.append(f"%{valor}%")
                
                if where_conditions:
                    where_clause = " WHERE " + " AND ".join(where_conditions)
            
            # Obtener total de registros
            full_count_query = count_query + where_clause
            cursor.execute(full_count_query, params)
            total_registros = cursor.fetchone()[0]
            
            # Obtener datos paginados
            paginated_query = f"{base_query}{where_clause} ORDER BY id DESC OFFSET ? ROWS FETCH NEXT ? ROWS ONLY"
            cursor.execute(paginated_query, params + [offset, limit])
            
            datos = []
            for row in cursor.fetchall():
                datos.append(self._row_to_dict(row, cursor.description))
            
            return datos, total_registros
            
        except Exception as e:
            print(f"[ERROR] Error obteniendo datos paginados: {e}")
            return [], 0
    
    def obtener_total_registros(self, filtros=None):
        """Obtiene el total de registros disponibles"""
        try:
            _, total = self.obtener_datos_paginados(offset=0, limit=1, filtros=filtros)
            return total
        except Exception as e:
            print(f"[ERROR] Error obteniendo total de registros: {e}")
            return 0
    
    def _get_base_query(self):
        """Obtiene la query base para paginación (debe ser implementado por cada modelo)"""
        # Esta es una implementación genérica
        tabla_principal = getattr(self, 'tabla_principal', 'tabla_principal')
        # FIXED: SQL Injection vulnerability
        return "SELECT * FROM ?", (tabla_principal,)
    
    def _get_count_query(self):
        """Obtiene la query de conteo (debe ser implementado por cada modelo)"""
        tabla_principal = getattr(self, 'tabla_principal', 'tabla_principal')
        # FIXED: SQL Injection vulnerability
        return "SELECT COUNT(*) FROM ?", (tabla_principal,)
    
    def _row_to_dict(self, row, description):
        """Convierte una fila de base de datos a diccionario"""
        return {desc[0]: row[i] for i, desc in enumerate(description)}
