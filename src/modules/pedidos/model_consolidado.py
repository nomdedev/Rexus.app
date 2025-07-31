"""
Modelo de Pedidos Consolidado - Rexus.app v2.0.0

Actualizado para usar la nueva estructura de base de datos consolidada:
- Tabla principal: pedidos_consolidado (unificado)
- Detalle: pedidos_detalle_consolidado (unificado)
- Productos: productos (unificado)
- Movimientos: movimientos_inventario (unificado)
"""

import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from src.utils.sql_security import validate_table_name, load_sql_script, SQLSecurityError


class PedidosModel:
    """Modelo para gestión completa de pedidos usando estructura consolidada."""

    # Estados de pedidos
    ESTADOS = {
        "BORRADOR": "Borrador",
        "PENDIENTE": "Pendiente de Aprobación",
        "APROBADO": "Aprobado",
        "EN_PREPARACION": "En Preparación",
        "LISTO_ENTREGA": "Listo para Entrega",
        "EN_TRANSITO": "En Tránsito",
        "ENTREGADO": "Entregado",
        "CANCELADO": "Cancelado",
        "FACTURADO": "Facturado",
    }

    # Tipos de pedido unificados
    TIPOS_PEDIDO = {
        "COMPRA": "Compra a Proveedor",
        "VENTA": "Venta a Cliente",
        "INTERNO": "Transferencia Interna",
        "OBRA": "Pedido para Obra",
        "DEVOLUCION": "Devolución",
        "AJUSTE": "Ajuste de Inventario",
        "PRODUCCION": "Orden de Producción"
    }

    # Prioridades
    PRIORIDADES = {
        "BAJA": "Baja",
        "NORMAL": "Normal",
        "ALTA": "Alta",
        "URGENTE": "Urgente",
    }

    def __init__(self, db_connection=None):
        """Inicializa el modelo de pedidos consolidado."""
        self.db_connection = db_connection
        
        # Usar tablas consolidadas
        self.tabla_pedidos = "pedidos_consolidado"
        self.tabla_pedidos_detalle = "pedidos_detalle_consolidado"
        self.tabla_productos = "productos"
        self.tabla_movimientos = "movimientos_inventario"
        self.tabla_productos_obra = "productos_obra"
        
        # Lista de tablas permitidas para prevenir SQL injection
        self._allowed_tables = {
            "pedidos_consolidado", "pedidos_detalle_consolidado", "productos",
            "movimientos_inventario", "productos_obra", "obras", "clientes"
        }

        if not self.db_connection:
            print("[ERROR PEDIDOS] No hay conexión a la base de datos. El módulo no funcionará correctamente.")
        
        self._verificar_tablas()

    def _validate_table_name(self, table_name: str) -> str:
        """Valida que el nombre de tabla esté en la lista permitida."""
        return validate_table_name(table_name, self._allowed_tables)

    def _verificar_tablas(self):
        """Verifica que las tablas consolidadas necesarias existan en la base de datos."""
        if not self.db_connection:
            return

        try:
            cursor = self.db_connection.cursor()

            # Verificar tabla principal pedidos_consolidado
            cursor.execute(
                "SELECT * FROM sysobjects WHERE name=? AND xtype='U'",
                (self.tabla_pedidos,),
            )
            if cursor.fetchone():
                print(f"[PEDIDOS] Tabla consolidada '{self.tabla_pedidos}' verificada correctamente.")
            else:
                print(f"[ADVERTENCIA] Tabla consolidada '{self.tabla_pedidos}' no existe. Usando tabla legacy.")
                # Fallback a tabla legacy
                self.tabla_pedidos = "pedidos"
                self.tabla_pedidos_detalle = "pedidos_detalle"
                self._allowed_tables.add("pedidos")
                self._allowed_tables.add("pedidos_detalle")
                self._allowed_tables.add("pedidos_historial")
                self._allowed_tables.add("pedidos_entregas")

            # Verificar tabla de detalle consolidada
            cursor.execute(
                "SELECT * FROM sysobjects WHERE name=? AND xtype='U'",
                (self.tabla_pedidos_detalle,),
            )
            if cursor.fetchone():
                print(f"[PEDIDOS] Tabla '{self.tabla_pedidos_detalle}' verificada correctamente.")
            else:
                print(f"[ADVERTENCIA] Tabla '{self.tabla_pedidos_detalle}' no existe. Funcionalidad limitada.")

            # Verificar tabla productos consolidada
            cursor.execute(
                "SELECT * FROM sysobjects WHERE name=? AND xtype='U'",
                (self.tabla_productos,),
            )
            if cursor.fetchone():
                print(f"[PEDIDOS] Tabla '{self.tabla_productos}' verificada correctamente.")
            else:
                print(f"[ADVERTENCIA] Tabla '{self.tabla_productos}' no existe. Usando inventario_perfiles legacy.")
                self.tabla_productos = "inventario_perfiles"
                self._allowed_tables.add("inventario_perfiles")

            print(f"[PEDIDOS] Verificación de tablas consolidadas completada.")

        except Exception as e:
            print(f"[ERROR PEDIDOS] Error verificando tablas: {e}")

    def generar_numero_pedido(self, tipo_pedido: str = "COMPRA") -> str:
        """Genera un número único de pedido según el tipo."""
        try:
            año_actual = datetime.now().year
            prefijos = {
                "COMPRA": "CMP",
                "VENTA": "VTA", 
                "INTERNO": "INT",
                "OBRA": "OBR",
                "DEVOLUCION": "DEV",
                "AJUSTE": "AJS",
                "PRODUCCION": "PRD"
            }
            prefijo = prefijos.get(tipo_pedido, "PED")
            numero_base = f"{prefijo}-{año_actual}-"

            if self.db_connection:
                cursor = self.db_connection.cursor()
                tabla_pedidos = self._validate_table_name(self.tabla_pedidos)
                
                cursor.execute(f"""
                    SELECT MAX(CAST(SUBSTRING(numero_pedido, LEN(?)+1, LEN(numero_pedido)) AS INT))
                    FROM {tabla_pedidos}
                    WHERE numero_pedido LIKE ?
                """, (numero_base, f"{numero_base}%"))

                result = cursor.fetchone()
                ultimo_numero = result[0] if result and result[0] else 0
                nuevo_numero = ultimo_numero + 1

                return f"{numero_base}{nuevo_numero:05d}"
            else:
                # Fallback sin BD
                timestamp = datetime.now().strftime("%m%d%H%M")
                return f"{prefijo}-{año_actual}-{timestamp}"

        except Exception as e:
            print(f"[PEDIDOS] Error generando número: {e}")
            # Fallback con UUID
            return f"PED-{datetime.now().year}-{str(uuid.uuid4())[:8].upper()}"

    def crear_pedido(self, datos_pedido: Dict[str, Any]) -> Optional[int]:
        """Crea un nuevo pedido usando la estructura consolidada."""
        if not self.db_connection:
            return None

        try:
            cursor = self.db_connection.cursor()
            tabla_pedidos = self._validate_table_name(self.tabla_pedidos)
            tabla_pedidos_detalle = self._validate_table_name(self.tabla_pedidos_detalle)

            # Generar número de pedido
            tipo_pedido = datos_pedido.get("tipo_pedido", "COMPRA")
            numero_pedido = self.generar_numero_pedido(tipo_pedido)

            if tabla_pedidos == "pedidos_consolidado":
                # Usar tabla consolidada
                sql_insert = """
                INSERT INTO pedidos_consolidado (
                    numero_pedido, tipo_pedido, subtipo_pedido, cliente_id, proveedor_id, obra_id,
                    fecha_pedido, fecha_entrega_solicitada, fecha_entrega_estimada,
                    estado, prioridad, canal_venta, metodo_pago, condiciones_pago,
                    subtotal, descuento_porcentaje, descuento_monto, impuestos_porcentaje,
                    impuestos_monto, cargos_adicionales, total_final,
                    moneda, tasa_cambio, observaciones, notas_internas,
                    direccion_entrega, contacto_entrega, telefono_entrega, email_entrega,
                    requiere_transporte, transportista, costo_transporte,
                    usuario_creacion, fecha_creacion, activo
                ) VALUES (?, ?, ?, ?, ?, ?, GETDATE(), ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE(), 1)
                """

                cursor.execute(sql_insert, (
                    numero_pedido,
                    tipo_pedido,
                    datos_pedido.get("subtipo_pedido", ""),
                    datos_pedido.get("cliente_id"),
                    datos_pedido.get("proveedor_id"),
                    datos_pedido.get("obra_id"),
                    datos_pedido.get("fecha_entrega_solicitada"),
                    datos_pedido.get("fecha_entrega_estimada"),
                    "BORRADOR",
                    datos_pedido.get("prioridad", "NORMAL"),
                    datos_pedido.get("canal_venta", "DIRECTO"),
                    datos_pedido.get("metodo_pago", "EFECTIVO"),
                    datos_pedido.get("condiciones_pago", "CONTADO"),
                    0, 0, 0, 0, 0, 0, 0,  # Totales se calculan después
                    datos_pedido.get("moneda", "COP"),
                    datos_pedido.get("tasa_cambio", 1.0),
                    datos_pedido.get("observaciones", ""),
                    datos_pedido.get("notas_internas", ""),
                    datos_pedido.get("direccion_entrega", ""),
                    datos_pedido.get("contacto_entrega", ""),
                    datos_pedido.get("telefono_entrega", ""),
                    datos_pedido.get("email_entrega", ""),
                    datos_pedido.get("requiere_transporte", False),
                    datos_pedido.get("transportista", ""),
                    datos_pedido.get("costo_transporte", 0),
                    datos_pedido.get("usuario_creador", 1)
                ))
            else:
                # Fallback a tabla legacy
                sql_insert = """
                INSERT INTO pedidos (
                    numero_pedido, cliente_id, obra_id, fecha_entrega_solicitada,
                    tipo_pedido, prioridad, observaciones, direccion_entrega,
                    responsable_entrega, telefono_contacto, usuario_creador
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """

                cursor.execute(sql_insert, (
                    numero_pedido,
                    datos_pedido.get("cliente_id"),
                    datos_pedido.get("obra_id"),
                    datos_pedido.get("fecha_entrega_solicitada"),
                    datos_pedido.get("tipo_pedido", "MATERIAL"),
                    datos_pedido.get("prioridad", "NORMAL"),
                    datos_pedido.get("observaciones", ""),
                    datos_pedido.get("direccion_entrega", ""),
                    datos_pedido.get("responsable_entrega", ""),
                    datos_pedido.get("telefono_contacto", ""),
                    datos_pedido.get("usuario_creador", 1)
                ))

            # Obtener ID del pedido creado
            cursor.execute("SELECT @@IDENTITY")
            pedido_id = cursor.fetchone()[0]

            # Insertar detalles del pedido
            detalles = datos_pedido.get("detalles", [])
            subtotal = 0

            for detalle in detalles:
                cantidad = float(detalle.get("cantidad", 0))
                precio_unitario = float(detalle.get("precio_unitario", 0))
                descuento = float(detalle.get("descuento_linea", 0))
                subtotal_linea = (cantidad * precio_unitario) - descuento
                subtotal += subtotal_linea

                if tabla_pedidos_detalle == "pedidos_detalle_consolidado":
                    # Usar tabla consolidada
                    sql_detalle = """
                    INSERT INTO pedidos_detalle_consolidado (
                        pedido_id, producto_id, codigo_producto, descripcion_producto, categoria_producto,
                        cantidad_solicitada, cantidad_aprobada, cantidad_entregada, cantidad_facturada,
                        unidad_medida, precio_unitario, descuento_linea, subtotal_linea,
                        observaciones_linea, especificaciones_tecnicas, fecha_entrega_linea,
                        ubicacion_entrega, lote_requerido, estado_linea, fecha_creacion, activo
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, 0, 0, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'PENDIENTE', GETDATE(), 1)
                    """

                    cursor.execute(sql_detalle, (
                        pedido_id,
                        detalle.get("producto_id"),
                        detalle.get("codigo_producto", ""),
                        detalle.get("descripcion", ""),
                        detalle.get("categoria", ""),
                        cantidad,
                        cantidad,  # Por defecto, cantidad aprobada = solicitada
                        detalle.get("unidad_medida", "UND"),
                        precio_unitario,
                        descuento,
                        subtotal_linea,
                        detalle.get("observaciones_item", ""),
                        detalle.get("especificaciones_tecnicas", ""),
                        detalle.get("fecha_entrega_linea"),
                        detalle.get("ubicacion_entrega", ""),
                        detalle.get("lote_requerido", ""),
                        detalle.get("estado_linea", "PENDIENTE")
                    ))
                else:
                    # Fallback a tabla legacy
                    sql_detalle = """
                    INSERT INTO pedidos_detalle (
                        pedido_id, producto_id, codigo_producto, descripcion,
                        categoria, cantidad, unidad_medida, precio_unitario,
                        descuento_item, subtotal_item, observaciones_item
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """

                    cursor.execute(sql_detalle, (
                        pedido_id,
                        detalle.get("producto_id"),
                        detalle.get("codigo_producto", ""),
                        detalle.get("descripcion", ""),
                        detalle.get("categoria", ""),
                        cantidad,
                        detalle.get("unidad_medida", "UND"),
                        precio_unitario,
                        descuento,
                        subtotal_linea,
                        detalle.get("observaciones_item", "")
                    ))

            # Calcular totales
            descuento_general = float(datos_pedido.get("descuento", 0))
            impuestos_porcentaje = float(datos_pedido.get("impuestos_porcentaje", 19))
            impuestos_monto = (subtotal - descuento_general) * (impuestos_porcentaje / 100)
            cargos_adicionales = float(datos_pedido.get("cargos_adicionales", 0))
            total_final = subtotal - descuento_general + impuestos_monto + cargos_adicionales

            # Actualizar totales del pedido
            if tabla_pedidos == "pedidos_consolidado":
                sql_update = """
                UPDATE pedidos_consolidado 
                SET subtotal = ?, descuento_monto = ?, impuestos_porcentaje = ?, 
                    impuestos_monto = ?, cargos_adicionales = ?, total_final = ?
                WHERE id = ?
                """
                cursor.execute(sql_update, (
                    subtotal, descuento_general, impuestos_porcentaje,
                    impuestos_monto, cargos_adicionales, total_final, pedido_id
                ))
            else:
                sql_update = """
                UPDATE pedidos 
                SET subtotal = ?, descuento = ?, impuestos = ?, total = ?
                WHERE id = ?
                """
                cursor.execute(sql_update, (
                    subtotal, descuento_general, impuestos_monto, total_final, pedido_id
                ))

            # Registrar cambio de estado inicial
            self.registrar_cambio_estado(
                pedido_id, None, "BORRADOR", datos_pedido.get("usuario_creador", 1)
            )

            self.db_connection.commit()
            print(f"[PEDIDOS] Pedido {numero_pedido} creado exitosamente")
            return pedido_id

        except Exception as e:
            print(f"[PEDIDOS] Error creando pedido: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return None

    def obtener_pedidos(self, filtros: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Obtiene lista de pedidos usando tabla consolidada."""
        if not self.db_connection:
            return self._get_datos_demo()

        try:
            cursor = self.db_connection.cursor()
            tabla_pedidos = self._validate_table_name(self.tabla_pedidos)
            tabla_pedidos_detalle = self._validate_table_name(self.tabla_pedidos_detalle)

            where_clauses = ["p.activo = 1"]
            params = []

            if filtros:
                if filtros.get("estado"):
                    where_clauses.append("p.estado = ?")
                    params.append(filtros["estado"])

                if filtros.get("tipo_pedido"):
                    where_clauses.append("p.tipo_pedido = ?")
                    params.append(filtros["tipo_pedido"])

                if filtros.get("obra_id"):
                    where_clauses.append("p.obra_id = ?")
                    params.append(filtros["obra_id"])

                if filtros.get("fecha_desde"):
                    where_clauses.append("p.fecha_pedido >= ?")
                    params.append(filtros["fecha_desde"])

                if filtros.get("fecha_hasta"):
                    where_clauses.append("p.fecha_pedido <= ?")
                    params.append(filtros["fecha_hasta"])

                if filtros.get("busqueda"):
                    where_clauses.append("""
                        (p.numero_pedido LIKE ? OR 
                         p.observaciones LIKE ? OR
                         p.contacto_entrega LIKE ?)
                    """)
                    busqueda = f"%{filtros['busqueda']}%"
                    params.extend([busqueda, busqueda, busqueda])

            where_sql = " AND ".join(where_clauses)

            if tabla_pedidos == "pedidos_consolidado":
                # Usar tabla consolidada
                query = f"""
                SELECT 
                    p.id, p.numero_pedido, p.fecha_pedido, p.fecha_entrega_solicitada,
                    p.estado, p.tipo_pedido, p.subtipo_pedido, p.prioridad, p.total_final,
                    p.observaciones, p.contacto_entrega, p.obra_id, p.cliente_id, p.proveedor_id,
                    p.canal_venta, p.metodo_pago, p.moneda,
                    COUNT(pd.id) as cantidad_items,
                    SUM(pd.cantidad_solicitada) as total_cantidad,
                    SUM(pd.cantidad_solicitada - ISNULL(pd.cantidad_entregada, 0)) as cantidad_pendiente,
                    SUM(pd.subtotal_linea) as subtotal_items
                FROM {tabla_pedidos} p
                LEFT JOIN {tabla_pedidos_detalle} pd ON p.id = pd.pedido_id AND pd.activo = 1
                WHERE {where_sql}
                GROUP BY p.id, p.numero_pedido, p.fecha_pedido, p.fecha_entrega_solicitada,
                         p.estado, p.tipo_pedido, p.subtipo_pedido, p.prioridad, p.total_final,
                         p.observaciones, p.contacto_entrega, p.obra_id, p.cliente_id, p.proveedor_id,
                         p.canal_venta, p.metodo_pago, p.moneda
                ORDER BY p.fecha_pedido DESC
                """
            else:
                # Fallback a tabla legacy
                query = f"""
                SELECT 
                    p.id, p.numero_pedido, p.fecha_pedido, p.fecha_entrega_solicitada,
                    p.estado, p.tipo_pedido, '' as subtipo_pedido, p.prioridad, p.total,
                    p.observaciones, p.responsable_entrega as contacto_entrega, p.obra_id, 
                    p.cliente_id, NULL as proveedor_id, 'DIRECTO' as canal_venta, 
                    'EFECTIVO' as metodo_pago, 'COP' as moneda,
                    COUNT(pd.id) as cantidad_items,
                    SUM(pd.cantidad) as total_cantidad,
                    SUM(CASE WHEN pd.cantidad_pendiente > 0 THEN pd.cantidad_pendiente ELSE 0 END) as cantidad_pendiente,
                    SUM(pd.subtotal_item) as subtotal_items
                FROM {tabla_pedidos} p
                LEFT JOIN {tabla_pedidos_detalle} pd ON p.id = pd.pedido_id
                WHERE {where_sql}
                GROUP BY p.id, p.numero_pedido, p.fecha_pedido, p.fecha_entrega_solicitada,
                         p.estado, p.tipo_pedido, p.prioridad, p.total,
                         p.observaciones, p.responsable_entrega, p.obra_id, p.cliente_id
                ORDER BY p.fecha_pedido DESC
                """

            cursor.execute(query, params)
            columns = [desc[0] for desc in cursor.description]

            pedidos = []
            for row in cursor.fetchall():
                pedido = dict(zip(columns, row))
                pedido["fecha_pedido"] = (
                    pedido["fecha_pedido"].strftime("%Y-%m-%d %H:%M")
                    if pedido["fecha_pedido"]
                    else ""
                )
                pedido["fecha_entrega_solicitada"] = (
                    pedido["fecha_entrega_solicitada"].strftime("%Y-%m-%d")
                    if pedido["fecha_entrega_solicitada"]
                    else ""
                )
                pedido["estado_texto"] = self.ESTADOS.get(pedido["estado"], pedido["estado"])
                pedido["tipo_texto"] = self.TIPOS_PEDIDO.get(pedido["tipo_pedido"], pedido["tipo_pedido"])
                pedido["prioridad_texto"] = self.PRIORIDADES.get(pedido["prioridad"], pedido["prioridad"])
                
                # Campo unificado para mostrar total
                pedido["total"] = pedido.get("total_final") or pedido.get("total", 0)
                
                pedidos.append(pedido)

            return pedidos

        except Exception as e:
            print(f"[PEDIDOS] Error obteniendo pedidos: {e}")
            return self._get_datos_demo()

    def obtener_pedido_por_id(self, pedido_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene un pedido específico usando tabla consolidada."""
        if not self.db_connection:
            return None

        try:
            cursor = self.db_connection.cursor()
            tabla_pedidos = self._validate_table_name(self.tabla_pedidos)
            tabla_pedidos_detalle = self._validate_table_name(self.tabla_pedidos_detalle)

            # Obtener datos del pedido
            cursor.execute(f"""
                SELECT * FROM {tabla_pedidos} WHERE id = ? AND activo = 1
            """, (pedido_id,))

            pedido_data = cursor.fetchone()
            if not pedido_data:
                return None

            columns = [desc[0] for desc in cursor.description]
            pedido = dict(zip(columns, pedido_data))

            # Obtener detalles del pedido
            cursor.execute(f"""
                SELECT * FROM {tabla_pedidos_detalle} 
                WHERE pedido_id = ? AND activo = 1
                ORDER BY id
            """, (pedido_id,))

            detalle_columns = [desc[0] for desc in cursor.description]
            detalles = []
            for row in cursor.fetchall():
                detalle = dict(zip(detalle_columns, row))
                detalles.append(detalle)

            pedido["detalles"] = detalles

            # Obtener historial si existe
            try:
                cursor.execute("""
                    SELECT * FROM pedidos_historial 
                    WHERE pedido_id = ?
                    ORDER BY fecha_cambio DESC
                """, (pedido_id,))

                historial_columns = [desc[0] for desc in cursor.description]
                historial = []
                for row in cursor.fetchall():
                    hist = dict(zip(historial_columns, row))
                    historial.append(hist)

                pedido["historial"] = historial
            except:
                pedido["historial"] = []

            return pedido

        except Exception as e:
            print(f"[PEDIDOS] Error obteniendo pedido {pedido_id}: {e}")
            return None

    def actualizar_estado_pedido(self, pedido_id: int, nuevo_estado: str, usuario_id: int, observaciones: str = "") -> bool:
        """Actualiza el estado de un pedido usando tabla consolidada."""
        if not self.db_connection:
            return False

        try:
            cursor = self.db_connection.cursor()
            tabla_pedidos = self._validate_table_name(self.tabla_pedidos)

            # Obtener estado actual
            cursor.execute(f"SELECT estado FROM {tabla_pedidos} WHERE id = ?", (pedido_id,))
            result = cursor.fetchone()
            if not result:
                return False

            estado_anterior = result[0]

            # Validar transición de estado
            if not self._validar_transicion_estado(estado_anterior, nuevo_estado):
                print(f"[PEDIDOS] Transición inválida: {estado_anterior} -> {nuevo_estado}")
                return False

            # Actualizar estado
            if tabla_pedidos == "pedidos_consolidado":
                sql_update = """
                UPDATE pedidos_consolidado 
                SET estado = ?, fecha_modificacion = GETDATE(), usuario_modificacion = ?
                WHERE id = ?
                """
                cursor.execute(sql_update, (nuevo_estado, usuario_id, pedido_id))

                # Si se aprueba, registrar fecha y usuario
                if nuevo_estado == "APROBADO":
                    cursor.execute("""
                        UPDATE pedidos_consolidado 
                        SET usuario_aprobacion = ?, fecha_aprobacion = GETDATE()
                        WHERE id = ?
                    """, (usuario_id, pedido_id))
            else:
                # Fallback a tabla legacy
                cursor.execute("""
                    UPDATE pedidos 
                    SET estado = ?, fecha_modificacion = GETDATE()
                    WHERE id = ?
                """, (nuevo_estado, pedido_id))

                if nuevo_estado == "APROBADO":
                    cursor.execute("""
                        UPDATE pedidos 
                        SET usuario_aprobador = ?, fecha_aprobacion = GETDATE()
                        WHERE id = ?
                    """, (usuario_id, pedido_id))

            # Registrar en historial
            self.registrar_cambio_estado(pedido_id, estado_anterior, nuevo_estado, usuario_id, observaciones)

            self.db_connection.commit()
            return True

        except Exception as e:
            print(f"[PEDIDOS] Error actualizando estado: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return False

    def registrar_cambio_estado(self, pedido_id: int, estado_anterior: Optional[str], 
                              estado_nuevo: str, usuario_id: int, observaciones: str = ""):
        """Registra un cambio de estado en el historial."""
        if not self.db_connection:
            return

        try:
            cursor = self.db_connection.cursor()
            
            # Intentar usar tabla de historial si existe
            try:
                cursor.execute("""
                    INSERT INTO pedidos_historial (
                        pedido_id, estado_anterior, estado_nuevo, usuario_id, observaciones
                    ) VALUES (?, ?, ?, ?, ?)
                """, (pedido_id, estado_anterior, estado_nuevo, usuario_id, observaciones))
            except:
                # Si no existe tabla de historial, registrar en movimientos o historial general
                motivo = f"Cambio estado pedido: {estado_anterior or 'N/A'} → {estado_nuevo}"
                if observaciones:
                    motivo += f" | {observaciones}"
                
                try:
                    cursor.execute("""
                        INSERT INTO historial (accion, usuario, fecha, detalles)
                        VALUES (?, ?, GETDATE(), ?)
                    """, (f"PEDIDO_{estado_nuevo}", usuario_id, motivo))
                except:
                    print(f"[ADVERTENCIA] No se pudo registrar historial para pedido {pedido_id}")

        except Exception as e:
            print(f"[PEDIDOS] Error registrando historial: {e}")

    def _validar_transicion_estado(self, estado_actual: str, estado_nuevo: str) -> bool:
        """Valida si la transición de estado es válida."""
        transiciones_validas = {
            "BORRADOR": ["PENDIENTE", "CANCELADO"],
            "PENDIENTE": ["APROBADO", "CANCELADO"],
            "APROBADO": ["EN_PREPARACION", "CANCELADO"],
            "EN_PREPARACION": ["LISTO_ENTREGA", "CANCELADO"],
            "LISTO_ENTREGA": ["EN_TRANSITO", "ENTREGADO"],
            "EN_TRANSITO": ["ENTREGADO"],
            "ENTREGADO": ["FACTURADO"],
            "CANCELADO": [],  # Estado final
            "FACTURADO": [],  # Estado final
        }

        return estado_nuevo in transiciones_validas.get(estado_actual, [])

    def obtener_estadisticas(self) -> Dict[str, Any]:
        """Obtiene estadísticas usando tabla consolidada."""
        if not self.db_connection:
            return self._get_estadisticas_demo()

        try:
            cursor = self.db_connection.cursor()
            tabla_pedidos = self._validate_table_name(self.tabla_pedidos)

            stats = {}

            # Total pedidos
            cursor.execute(f"SELECT COUNT(*) FROM {tabla_pedidos} WHERE activo = 1")
            stats["total_pedidos"] = cursor.fetchone()[0]

            # Por estado
            cursor.execute(f"""
                SELECT estado, COUNT(*) 
                FROM {tabla_pedidos}
                WHERE activo = 1 
                GROUP BY estado
            """)
            stats["por_estado"] = {row[0]: row[1] for row in cursor.fetchall()}

            # Valor total
            if tabla_pedidos == "pedidos_consolidado":
                cursor.execute("""
                    SELECT SUM(total_final) FROM pedidos_consolidado 
                    WHERE activo = 1 AND estado != 'CANCELADO'
                """)
            else:
                cursor.execute("""
                    SELECT SUM(total) FROM pedidos 
                    WHERE activo = 1 AND estado != 'CANCELADO'
                """)
            
            result = cursor.fetchone()
            stats["valor_total"] = float(result[0]) if result[0] else 0.0

            # Pedidos urgentes
            cursor.execute(f"""
                SELECT COUNT(*) FROM {tabla_pedidos}
                WHERE activo = 1 AND prioridad = 'URGENTE' 
                AND estado NOT IN ('ENTREGADO', 'CANCELADO', 'FACTURADO')
            """)
            stats["urgentes_pendientes"] = cursor.fetchone()[0]

            # Pedidos del mes
            cursor.execute(f"""
                SELECT COUNT(*) FROM {tabla_pedidos}
                WHERE activo = 1 
                AND MONTH(fecha_pedido) = MONTH(GETDATE()) 
                AND YEAR(fecha_pedido) = YEAR(GETDATE())
            """)
            stats["pedidos_mes"] = cursor.fetchone()[0]

            return stats

        except Exception as e:
            print(f"[PEDIDOS] Error obteniendo estadísticas: {e}")
            return self._get_estadisticas_demo()

    def buscar_productos_inventario(self, busqueda: str) -> List[Dict[str, Any]]:
        """Busca productos en inventario usando tabla consolidada."""
        if not self.db_connection:
            return []

        try:
            cursor = self.db_connection.cursor()
            tabla_productos = self._validate_table_name(self.tabla_productos)

            if tabla_productos == "productos":
                cursor.execute("""
                    SELECT TOP 20
                        id, codigo, descripcion, categoria, stock_actual, precio_unitario, unidad_medida
                    FROM productos 
                    WHERE activo = 1 
                    AND (codigo LIKE ? OR descripcion LIKE ? OR categoria LIKE ?)
                    ORDER BY descripcion
                """, (f"%{busqueda}%", f"%{busqueda}%", f"%{busqueda}%"))
            else:
                cursor.execute("""
                    SELECT TOP 20
                        id, codigo, descripcion, categoria, stock_actual, precio_unitario, unidad_medida
                    FROM inventario_perfiles 
                    WHERE activo = 1 
                    AND (codigo LIKE ? OR descripcion LIKE ? OR categoria LIKE ?)
                    ORDER BY descripcion
                """, (f"%{busqueda}%", f"%{busqueda}%", f"%{busqueda}%"))

            columns = [desc[0] for desc in cursor.description]
            productos = []

            for row in cursor.fetchall():
                producto = dict(zip(columns, row))
                productos.append(producto)

            return productos

        except Exception as e:
            print(f"[PEDIDOS] Error buscando productos: {e}")
            return []

    def _get_datos_demo(self) -> List[Dict[str, Any]]:
        """Datos demo consolidados para pedidos."""
        return [
            {
                "id": 1,
                "numero_pedido": "CMP-2025-00001",
                "fecha_pedido": "2025-01-15 10:30",
                "fecha_entrega_solicitada": "2025-01-20",
                "estado": "PENDIENTE",
                "estado_texto": "Pendiente de Aprobación",
                "tipo_pedido": "COMPRA",
                "subtipo_pedido": "MATERIALES",
                "tipo_texto": "Compra a Proveedor",
                "prioridad": "NORMAL",
                "prioridad_texto": "Normal",
                "total": 1250.50,
                "total_final": 1250.50,
                "contacto_entrega": "Juan Pérez",
                "obra_id": 1,
                "cliente_id": None,
                "proveedor_id": 1,
                "canal_venta": "DIRECTO",
                "metodo_pago": "CREDITO",
                "moneda": "COP",
                "cantidad_items": 5,
                "total_cantidad": 25.0,
                "cantidad_pendiente": 25.0,
                "subtotal_items": 1050.42
            },
            {
                "id": 2,
                "numero_pedido": "VTA-2025-00001",
                "fecha_pedido": "2025-01-14 15:45",
                "fecha_entrega_solicitada": "2025-01-18",
                "estado": "APROBADO",
                "estado_texto": "Aprobado",
                "tipo_pedido": "VENTA",
                "subtipo_pedido": "VENTANAS",
                "tipo_texto": "Venta a Cliente",
                "prioridad": "ALTA",
                "prioridad_texto": "Alta",
                "total": 850.75,
                "total_final": 850.75,
                "contacto_entrega": "María González",
                "obra_id": 2,
                "cliente_id": 1,
                "proveedor_id": None,
                "canal_venta": "PRESENCIAL",
                "metodo_pago": "EFECTIVO",
                "moneda": "COP",
                "cantidad_items": 3,
                "total_cantidad": 15.0,
                "cantidad_pendiente": 0.0,
                "subtotal_items": 714.71
            }
        ]

    def _get_estadisticas_demo(self) -> Dict[str, Any]:
        """Estadísticas demo consolidadas."""
        return {
            "total_pedidos": 25,
            "por_estado": {
                "BORRADOR": 2,
                "PENDIENTE": 5,
                "APROBADO": 8,
                "EN_PREPARACION": 3,
                "ENTREGADO": 6,
                "CANCELADO": 1,
            },
            "valor_total": 45750.25,
            "urgentes_pendientes": 3,
            "pedidos_mes": 15,
        }