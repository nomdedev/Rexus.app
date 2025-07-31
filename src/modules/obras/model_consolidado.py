"""
Modelo de Obras Consolidado - Rexus.app v2.0.0

Actualizado para usar la nueva estructura de base de datos consolidada:
- Tabla principal: obras (sin cambios)
- Asignaciones: productos_obra (unificado para todos los productos)
- Productos: productos (unificado)
- Movimientos: movimientos_inventario (unificado)
- Pedidos: pedidos_consolidado (unificado)
"""

import datetime
from typing import Any, Dict, List, Optional, Tuple
from src.utils.sql_security import validate_table_name, load_sql_script, SQLSecurityError


class ObrasModel:
    """Modelo para gestión de obras usando estructura consolidada."""

    # Estados de obras
    ESTADOS = {
        "PLANIFICACION": "Planificación",
        "EN_PROCESO": "En Proceso",
        "PAUSADA": "Pausada",
        "FINALIZADA": "Finalizada",
        "CANCELADA": "Cancelada",
    }

    # Tipos de obra
    TIPOS_OBRA = {
        "CONSTRUCCION": "Construcción",
        "REMODELACION": "Remodelación",
        "MANTENIMIENTO": "Mantenimiento",
        "INSTALACION": "Instalación",
        "REPARACION": "Reparación",
        "OTRO": "Otro",
    }

    # Prioridades
    PRIORIDADES = {
        "BAJA": "Baja",
        "MEDIA": "Media",
        "ALTA": "Alta",
        "URGENTE": "Urgente",
    }

    # Etapas de obra
    ETAPAS = {
        "GENERAL": "General",
        "CIMENTACION": "Cimentación",
        "ESTRUCTURA": "Estructura",
        "MAMPOSTERIA": "Mamposterría",
        "CUBIERTA": "Cubierta",
        "INSTALACIONES": "Instalaciones",
        "ACABADOS": "Acabados",
        "ENTREGA": "Entrega",
    }

    def __init__(self, db_connection=None):
        """Inicializa el modelo de obras consolidado."""
        self.db_connection = db_connection
        
        # Usar tablas consolidadas
        self.tabla_obras = "obras"
        self.tabla_productos_obra = "productos_obra"
        self.tabla_productos = "productos"
        self.tabla_movimientos = "movimientos_inventario"
        self.tabla_pedidos = "pedidos_consolidado"
        
        # Lista de tablas permitidas para prevenir SQL injection
        self._allowed_tables = {
            "obras", "productos_obra", "productos", "movimientos_inventario", 
            "pedidos_consolidado", "pedidos_detalle_consolidado", "clientes"
        }

        if not self.db_connection:
            print("[ERROR OBRAS] No hay conexión a la base de datos. El módulo no funcionará correctamente.")
        
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

            # Verificar tabla de obras (sin cambios)
            cursor.execute(
                "SELECT * FROM sysobjects WHERE name=? AND xtype='U'",
                (self.tabla_obras,),
            )
            if cursor.fetchone():
                print(f"[OBRAS] Tabla '{self.tabla_obras}' verificada correctamente.")
            else:
                print(f"[ADVERTENCIA] La tabla '{self.tabla_obras}' no existe en la base de datos.")

            # Verificar tabla productos_obra consolidada
            cursor.execute(
                "SELECT * FROM sysobjects WHERE name=? AND xtype='U'",
                (self.tabla_productos_obra,),
            )
            if cursor.fetchone():
                print(f"[OBRAS] Tabla consolidada '{self.tabla_productos_obra}' verificada correctamente.")
            else:
                print(f"[ADVERTENCIA] Tabla consolidada '{self.tabla_productos_obra}' no existe. Usando tablas legacy.")
                # Fallback a tablas legacy específicas
                self._allowed_tables.add("detalles_obra")
                self._allowed_tables.add("herrajes_obra")
                self._allowed_tables.add("vidrios_obra")
                self._allowed_tables.add("materiales_por_obra")

            # Verificar tabla productos consolidada
            cursor.execute(
                "SELECT * FROM sysobjects WHERE name=? AND xtype='U'",
                (self.tabla_productos,),
            )
            if cursor.fetchone():
                print(f"[OBRAS] Tabla '{self.tabla_productos}' verificada correctamente.")
            else:
                print(f"[ADVERTENCIA] Tabla '{self.tabla_productos}' no existe. Usando inventario_perfiles legacy.")
                self.tabla_productos = "inventario_perfiles"
                self._allowed_tables.add("inventario_perfiles")
                self._allowed_tables.add("herrajes")
                self._allowed_tables.add("vidrios")

            print(f"[OBRAS] Verificación de tablas consolidadas completada.")

        except Exception as e:
            print(f"[ERROR OBRAS] Error verificando tablas: {e}")

    def crear_obra(self, datos_obra: Dict[str, Any]) -> Tuple[bool, str]:
        """Crea una nueva obra en el sistema."""
        if not self.db_connection:
            return False, "Sin conexión a la base de datos"

        try:
            cursor = self.db_connection.cursor()

            # Verificar que no existe una obra con el mismo código
            cursor.execute(
                "SELECT COUNT(*) FROM obras WHERE codigo = ?",
                (datos_obra.get("codigo"),),
            )
            if cursor.fetchone()[0] > 0:
                return (
                    False,
                    f"Ya existe una obra con el código {datos_obra.get('codigo')}",
                )

            sql_insert = """
            INSERT INTO obras
            (codigo, nombre, descripcion, cliente, direccion, telefono_contacto,
             email_contacto, fecha_inicio, fecha_fin_estimada, presupuesto_total,
             estado, tipo_obra, prioridad, responsable, observaciones, usuario_creacion)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

            cursor.execute(
                sql_insert,
                (
                    datos_obra.get("codigo"),
                    datos_obra.get("nombre"),
                    datos_obra.get("descripcion", ""),
                    datos_obra.get("cliente"),
                    datos_obra.get("direccion", ""),
                    datos_obra.get("telefono_contacto", ""),
                    datos_obra.get("email_contacto", ""),
                    datos_obra.get("fecha_inicio"),
                    datos_obra.get("fecha_fin_estimada"),
                    datos_obra.get("presupuesto_total", 0),
                    datos_obra.get("estado", "PLANIFICACION"),
                    datos_obra.get("tipo_obra", "CONSTRUCCION"),
                    datos_obra.get("prioridad", "MEDIA"),
                    datos_obra.get("responsable"),
                    datos_obra.get("observaciones", ""),
                    datos_obra.get("usuario_creacion", "SISTEMA"),
                ),
            )

            self.db_connection.commit()

            print(f"[OBRAS] Obra creada exitosamente: {datos_obra.get('codigo')}")
            return True, f"Obra {datos_obra.get('codigo')} creada exitosamente"

        except Exception as e:
            print(f"[ERROR OBRAS] Error creando obra: {e}")
            return False, f"Error creando obra: {str(e)}"

    def obtener_todas_obras(self) -> List[Dict[str, Any]]:
        """Obtiene todas las obras con información consolidada."""
        if not self.db_connection:
            return self._get_obras_demo()

        try:
            cursor = self.db_connection.cursor()
            tabla_obras = self._validate_table_name(self.tabla_obras)
            tabla_productos_obra = self._validate_table_name(self.tabla_productos_obra)

            # Query base para obras
            base_query = f"""
                SELECT
                    o.id, o.codigo, o.nombre, o.cliente, o.estado, o.responsable,
                    o.fecha_inicio, o.fecha_fin_estimada, o.presupuesto_total,
                    o.tipo_obra, o.prioridad, o.descripcion, o.direccion as ubicacion,
                    o.fecha_creacion as created_at, o.fecha_modificacion as updated_at
                FROM {tabla_obras} o
            """

            # Si existe tabla consolidada, agregar estadísticas de productos
            if tabla_productos_obra == "productos_obra":
                query = f"""
                {base_query}
                LEFT JOIN (
                    SELECT 
                        obra_id,
                        COUNT(*) as total_productos,
                        COUNT(CASE WHEN estado = 'PLANIFICADO' THEN 1 END) as productos_planificados,
                        COUNT(CASE WHEN estado = 'ASIGNADO' THEN 1 END) as productos_asignados,
                        COUNT(CASE WHEN estado = 'ENTREGADO' THEN 1 END) as productos_entregados,
                        SUM(cantidad_requerida * precio_unitario_presupuesto) as valor_productos_estimado,
                        SUM(cantidad_utilizada * precio_unitario_real) as valor_productos_real
                    FROM {tabla_productos_obra}
                    WHERE activo = 1
                    GROUP BY obra_id
                ) po ON o.id = po.obra_id
                ORDER BY o.fecha_inicio DESC
                """
            else:
                # Fallback sin estadísticas consolidadas
                query = f"{base_query} ORDER BY o.fecha_inicio DESC"

            cursor.execute(query)
            rows = cursor.fetchall()
            columnas = [column[0] for column in cursor.description]
            
            obras = []
            for row in rows:
                obra = dict(zip(columnas, row))
                
                # Calcular progreso si hay datos consolidados
                if 'productos_entregados' in obra and obra.get('total_productos', 0) > 0:
                    obra['progreso'] = round((obra.get('productos_entregados', 0) / obra.get('total_productos', 1)) * 100, 1)
                else:
                    obra['progreso'] = 0
                    
                obras.append(obra)
                
            return obras
            
        except Exception as e:
            print(f"[ERROR OBRAS] Error obteniendo obras: {e}")
            return self._get_obras_demo()

    def obtener_obra_por_id(self, obra_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene una obra específica con detalles consolidados."""
        if not self.db_connection:
            return None

        try:
            cursor = self.db_connection.cursor()
            tabla_obras = self._validate_table_name(self.tabla_obras)

            cursor.execute(f"""
                SELECT
                    id, codigo, nombre, cliente, estado, responsable,
                    fecha_inicio, fecha_fin_estimada, presupuesto_total,
                    tipo_obra, prioridad, descripcion, direccion as ubicacion,
                    fecha_creacion as created_at, fecha_modificacion as updated_at
                FROM {tabla_obras}
                WHERE id = ?
            """, (obra_id,))

            row = cursor.fetchone()
            if not row:
                return None

            columnas = [column[0] for column in cursor.description]
            obra = dict(zip(columnas, row))

            # Obtener productos asignados usando tabla consolidada
            obra["productos"] = self.obtener_productos_obra(obra_id)
            
            # Calcular estadísticas de la obra
            obra.update(self._calcular_estadisticas_obra(obra_id))

            return obra

        except Exception as e:
            print(f"[ERROR OBRAS] Error obteniendo obra {obra_id}: {e}")
            return None

    def obtener_productos_obra(self, obra_id: int) -> List[Dict[str, Any]]:
        """Obtiene todos los productos asignados a una obra usando tabla consolidada."""
        if not self.db_connection:
            return []

        try:
            cursor = self.db_connection.cursor()
            tabla_productos_obra = self._validate_table_name(self.tabla_productos_obra)
            tabla_productos = self._validate_table_name(self.tabla_productos)

            if tabla_productos_obra == "productos_obra":
                # Usar tabla consolidada
                query = f"""
                SELECT 
                    po.id, po.producto_id, po.codigo_producto, po.descripcion_producto,
                    po.categoria_producto, po.cantidad_requerida, po.cantidad_asignada,
                    po.cantidad_utilizada, po.cantidad_pendiente, po.estado,
                    po.etapa_obra, po.ubicacion_obra, po.fecha_asignacion,
                    po.precio_unitario_presupuesto, po.precio_unitario_real,
                    po.costo_total_estimado, po.costo_total_real,
                    po.observaciones, po.especificaciones_tecnicas,
                    p.unidad_medida, p.stock_actual, p.proveedor
                FROM {tabla_productos_obra} po
                LEFT JOIN {tabla_productos} p ON po.producto_id = p.id
                WHERE po.obra_id = ? AND po.activo = 1
                ORDER BY po.categoria_producto, po.codigo_producto
                """
                
                cursor.execute(query, (obra_id,))
                columnas = [column[0] for column in cursor.description]
                productos = []
                
                for row in cursor.fetchall():
                    producto = dict(zip(columnas, row))
                    productos.append(producto)
                    
                return productos
            else:
                # Fallback: combinar datos de tablas legacy
                productos = []
                
                # Obtener herrajes de la obra
                try:
                    cursor.execute("""
                        SELECT h.id, h.codigo, h.descripcion, 'HERRAJE' as categoria,
                               ho.cantidad_requerida, ho.cantidad_pedida as cantidad_asignada,
                               0 as cantidad_utilizada, 
                               (ho.cantidad_requerida - ISNULL(ho.cantidad_pedida, 0)) as cantidad_pendiente,
                               ho.estado, ho.fecha_asignacion, ho.observaciones
                        FROM herrajes h
                        INNER JOIN herrajes_obra ho ON h.id = ho.herraje_id
                        WHERE ho.obra_id = ?
                    """, (obra_id,))
                    
                    for row in cursor.fetchall():
                        columnas = [column[0] for column in cursor.description]
                        producto = dict(zip(columnas, row))
                        producto["etapa_obra"] = "GENERAL"
                        productos.append(producto)
                except:
                    pass

                # Obtener vidrios de la obra
                try:
                    cursor.execute("""
                        SELECT v.id, v.codigo, v.descripcion, 'VIDRIO' as categoria,
                               vo.metros_cuadrados_requeridos as cantidad_requerida,
                               vo.metros_cuadrados_pedidos as cantidad_asignada,
                               0 as cantidad_utilizada,
                               (vo.metros_cuadrados_requeridos - ISNULL(vo.metros_cuadrados_pedidos, 0)) as cantidad_pendiente,
                               'PENDIENTE' as estado, vo.fecha_asignacion, vo.observaciones
                        FROM vidrios v
                        INNER JOIN vidrios_obra vo ON v.id = vo.vidrio_id
                        WHERE vo.obra_id = ?
                    """, (obra_id,))
                    
                    for row in cursor.fetchall():
                        columnas = [column[0] for column in cursor.description]
                        producto = dict(zip(columnas, row))
                        producto["etapa_obra"] = "GENERAL"
                        productos.append(producto)
                except:
                    pass

                return productos

        except Exception as e:
            print(f"[ERROR OBRAS] Error obteniendo productos de obra: {e}")
            return []

    def asignar_producto_obra(self, obra_id: int, producto_id: int, cantidad_requerida: float, 
                            etapa_obra: str = "GENERAL", observaciones: str = "", 
                            usuario: str = "SISTEMA") -> Tuple[bool, str]:
        """Asigna un producto a una obra usando tabla consolidada."""
        if not self.db_connection:
            return False, "Sin conexión a la base de datos"

        try:
            cursor = self.db_connection.cursor()
            tabla_productos_obra = self._validate_table_name(self.tabla_productos_obra)
            tabla_productos = self._validate_table_name(self.tabla_productos)

            # Obtener información del producto
            cursor.execute(f"""
                SELECT codigo, descripcion, categoria, precio_unitario, unidad_medida, stock_actual
                FROM {tabla_productos}
                WHERE id = ? AND activo = 1
            """, (producto_id,))
            
            producto = cursor.fetchone()
            if not producto:
                return False, "Producto no encontrado"

            codigo, descripcion, categoria, precio_unitario, unidad_medida, stock_actual = producto

            # Verificar stock disponible
            if stock_actual < cantidad_requerida:
                return False, f"Stock insuficiente. Disponible: {stock_actual}, Requerido: {cantidad_requerida}"

            if tabla_productos_obra == "productos_obra":
                # Usar tabla consolidada
                sql_insert = f"""
                INSERT INTO {tabla_productos_obra}
                (obra_id, producto_id, codigo_producto, descripcion_producto, categoria_producto,
                 cantidad_requerida, etapa_obra, estado, precio_unitario_presupuesto,
                 costo_total_estimado, observaciones, fecha_creacion, activo, usuario_creacion)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'PLANIFICADO', ?, ?, ?, GETDATE(), 1, ?)
                """

                costo_estimado = cantidad_requerida * precio_unitario

                cursor.execute(sql_insert, (
                    obra_id, producto_id, codigo, descripcion, categoria,
                    cantidad_requerida, etapa_obra, precio_unitario,
                    costo_estimado, observaciones, usuario
                ))
            else:
                # Fallback: usar tablas legacy según categoría
                if categoria == "HERRAJE":
                    sql_insert = """
                    INSERT INTO herrajes_obra
                    (herraje_id, obra_id, cantidad_requerida, estado, fecha_asignacion, observaciones)
                    VALUES (?, ?, ?, 'PENDIENTE', GETDATE(), ?)
                    """
                    cursor.execute(sql_insert, (producto_id, obra_id, cantidad_requerida, observaciones))
                elif categoria == "VIDRIO":
                    sql_insert = """
                    INSERT INTO vidrios_obra
                    (vidrio_id, obra_id, metros_cuadrados_requeridos, fecha_asignacion, observaciones)
                    VALUES (?, ?, ?, GETDATE(), ?)
                    """
                    cursor.execute(sql_insert, (producto_id, obra_id, cantidad_requerida, observaciones))
                else:
                    # Para otras categorías, usar tabla genérica si existe
                    try:
                        sql_insert = """
                        INSERT INTO materiales_por_obra
                        (material_id, obra_id, cantidad_requerida, fecha_asignacion, observaciones)
                        VALUES (?, ?, ?, GETDATE(), ?)
                        """
                        cursor.execute(sql_insert, (producto_id, obra_id, cantidad_requerida, observaciones))
                    except:
                        return False, f"No se puede asignar producto de categoría {categoria} con estructura legacy"

            self.db_connection.commit()
            print(f"[OBRAS] Producto {codigo} asignado a obra {obra_id}")
            return True, f"Producto '{codigo}' asignado correctamente a la obra"

        except Exception as e:
            print(f"[ERROR OBRAS] Error asignando producto a obra: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return False, f"Error asignando producto: {str(e)}"

    def actualizar_cantidad_utilizada(self, asignacion_id: int, cantidad_utilizada: float, 
                                    precio_real: float = None, usuario: str = "SISTEMA") -> Tuple[bool, str]:
        """Actualiza la cantidad utilizada de un producto en obra."""
        if not self.db_connection:
            return False, "Sin conexión a la base de datos"

        try:
            cursor = self.db_connection.cursor()
            tabla_productos_obra = self._validate_table_name(self.tabla_productos_obra)

            if tabla_productos_obra == "productos_obra":
                # Obtener datos actuales
                cursor.execute(f"""
                    SELECT cantidad_requerida, cantidad_utilizada, precio_unitario_presupuesto, producto_id
                    FROM {tabla_productos_obra}
                    WHERE id = ? AND activo = 1
                """, (asignacion_id,))
                
                datos = cursor.fetchone()
                if not datos:
                    return False, "Asignación no encontrada"

                cantidad_requerida, cantidad_actual, precio_presupuesto, producto_id = datos

                # Validar que no exceda lo requerido
                if cantidad_utilizada > cantidad_requerida:
                    return False, f"Cantidad utilizada ({cantidad_utilizada}) no puede exceder la requerida ({cantidad_requerida})"

                # Usar precio real si se proporciona, sino usar el de presupuesto
                precio_unitario_real = precio_real if precio_real is not None else precio_presupuesto
                costo_total_real = cantidad_utilizada * precio_unitario_real

                # Calcular diferencia para ajustar stock
                diferencia = cantidad_utilizada - cantidad_actual

                # Actualizar asignación
                sql_update = f"""
                UPDATE {tabla_productos_obra}
                SET cantidad_utilizada = ?, precio_unitario_real = ?, costo_total_real = ?,
                    estado = CASE 
                        WHEN ? >= cantidad_requerida THEN 'COMPLETADO'
                        WHEN ? > 0 THEN 'EN_USO'
                        ELSE estado
                    END,
                    fecha_modificacion = GETDATE(), usuario_modificacion = ?
                WHERE id = ?
                """

                cursor.execute(sql_update, (
                    cantidad_utilizada, precio_unitario_real, costo_total_real,
                    cantidad_utilizada, cantidad_utilizada, usuario, asignacion_id
                ))

                # Registrar movimiento de consumo si hay diferencia
                if diferencia != 0:
                    self._registrar_movimiento_obra(
                        producto_id, "CONSUMO_OBRA", abs(diferencia), 
                        f"Consumo en obra - Asignación {asignacion_id}", usuario
                    )

                self.db_connection.commit()
                return True, f"Cantidad utilizada actualizada a {cantidad_utilizada}"
            else:
                return False, "Funcionalidad no disponible con estructura legacy"

        except Exception as e:
            print(f"[ERROR OBRAS] Error actualizando cantidad utilizada: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return False, f"Error actualizando cantidad: {str(e)}"

    def _registrar_movimiento_obra(self, producto_id: int, tipo_movimiento: str, cantidad: float, motivo: str, usuario: str):
        """Registra un movimiento de inventario relacionado con obra."""
        try:
            cursor = self.db_connection.cursor()
            tabla_movimientos = self._validate_table_name(self.tabla_movimientos)

            if tabla_movimientos == "movimientos_inventario":
                # Usar procedimiento almacenado si existe
                try:
                    cursor.execute("EXEC sp_registrar_movimiento ?, ?, ?, ?, ?, ?, ?", (
                        producto_id, tipo_movimiento, cantidad, motivo, "", 1, None
                    ))
                except:
                    # Fallback a inserción manual
                    cursor.execute(f"""
                        INSERT INTO {tabla_movimientos}
                        (producto_id, tipo_movimiento, cantidad, motivo, usuario_movimiento, fecha_movimiento)
                        VALUES (?, ?, ?, ?, 1, GETDATE())
                    """, (producto_id, tipo_movimiento, cantidad, motivo))

        except Exception as e:
            print(f"[ERROR OBRAS] Error registrando movimiento: {e}")

    def _calcular_estadisticas_obra(self, obra_id: int) -> Dict[str, Any]:
        """Calcula estadísticas consolidadas de una obra."""
        if not self.db_connection:
            return {}

        try:
            cursor = self.db_connection.cursor()
            tabla_productos_obra = self._validate_table_name(self.tabla_productos_obra)

            estadisticas = {
                "total_productos": 0,
                "productos_planificados": 0,
                "productos_asignados": 0,
                "productos_entregados": 0,
                "productos_completados": 0,
                "valor_presupuestado": 0.0,
                "valor_real": 0.0,
                "progreso_cantidad": 0.0,
                "progreso_valor": 0.0
            }

            if tabla_productos_obra == "productos_obra":
                cursor.execute(f"""
                    SELECT 
                        COUNT(*) as total_productos,
                        COUNT(CASE WHEN estado = 'PLANIFICADO' THEN 1 END) as productos_planificados,
                        COUNT(CASE WHEN estado = 'ASIGNADO' THEN 1 END) as productos_asignados,
                        COUNT(CASE WHEN estado = 'ENTREGADO' THEN 1 END) as productos_entregados,
                        COUNT(CASE WHEN estado = 'COMPLETADO' THEN 1 END) as productos_completados,
                        SUM(ISNULL(costo_total_estimado, 0)) as valor_presupuestado,
                        SUM(ISNULL(costo_total_real, 0)) as valor_real,
                        SUM(cantidad_requerida) as cantidad_total_requerida,
                        SUM(cantidad_utilizada) as cantidad_total_utilizada
                    FROM {tabla_productos_obra}
                    WHERE obra_id = ? AND activo = 1
                """, (obra_id,))

                row = cursor.fetchone()
                if row:
                    estadisticas.update({
                        "total_productos": row[0],
                        "productos_planificados": row[1],
                        "productos_asignados": row[2],
                        "productos_entregados": row[3],
                        "productos_completados": row[4],
                        "valor_presupuestado": float(row[5] or 0),
                        "valor_real": float(row[6] or 0),
                    })

                    # Calcular progreso
                    if row[8] and row[8] > 0:  # cantidad_total_requerida
                        estadisticas["progreso_cantidad"] = round((row[8] / row[7]) * 100, 1)  # cantidad_utilizada / requerida
                    
                    if estadisticas["valor_presupuestado"] > 0:
                        estadisticas["progreso_valor"] = round((estadisticas["valor_real"] / estadisticas["valor_presupuestado"]) * 100, 1)

            return estadisticas

        except Exception as e:
            print(f"[ERROR OBRAS] Error calculando estadísticas: {e}")
            return {}

    def cambiar_estado_obra(self, obra_id: int, nuevo_estado: str, usuario: str = "SISTEMA") -> Tuple[bool, str]:
        """Cambia el estado de una obra."""
        estados_validos = list(self.ESTADOS.keys())

        if nuevo_estado not in estados_validos:
            return (
                False,
                f"Estado no válido. Estados permitidos: {', '.join(estados_validos)}",
            )

        if not self.db_connection:
            return False, "Sin conexión a la base de datos"

        try:
            cursor = self.db_connection.cursor()

            # Obtener estado actual
            cursor.execute("SELECT estado FROM obras WHERE id = ?", (obra_id,))
            resultado = cursor.fetchone()
            if not resultado:
                return False, "Obra no encontrada"

            estado_actual = resultado[0]

            # Actualizar estado
            sql_update = """
            UPDATE obras
            SET estado = ?, fecha_modificacion = GETDATE(), usuario_modificacion = ?
            WHERE id = ?
            """

            cursor.execute(sql_update, (nuevo_estado, usuario, obra_id))
            self.db_connection.commit()

            # Si se finaliza la obra, actualizar fecha de finalización
            if nuevo_estado == "FINALIZADA":
                cursor.execute(
                    "UPDATE obras SET fecha_fin_real = GETDATE() WHERE id = ?",
                    (obra_id,),
                )
                self.db_connection.commit()

            return True, f"Estado cambiado de {estado_actual} a {nuevo_estado}"

        except Exception as e:
            print(f"[ERROR OBRAS] Error cambiando estado: {e}")
            return False, f"Error cambiando estado: {str(e)}"

    def obtener_estadisticas_obras(self) -> Dict[str, Any]:
        """Obtiene estadísticas generales de obras con datos consolidados."""
        if not self.db_connection:
            return self._get_estadisticas_demo()

        try:
            cursor = self.db_connection.cursor()
            tabla_obras = self._validate_table_name(self.tabla_obras)

            estadisticas = {}

            # Total de obras
            cursor.execute(f"SELECT COUNT(*) FROM {tabla_obras}")
            estadisticas["total_obras"] = cursor.fetchone()[0]

            # Obras por estado
            cursor.execute(f"""
                SELECT estado, COUNT(*) as cantidad
                FROM {tabla_obras}
                GROUP BY estado
                ORDER BY cantidad DESC
            """)
            estadisticas["obras_por_estado"] = [
                {"estado": row[0], "cantidad": row[1]} for row in cursor.fetchall()
            ]

            # Obras activas (en proceso y planificación)
            cursor.execute(f"""
                SELECT COUNT(*) FROM {tabla_obras}
                WHERE estado IN ('PLANIFICACION', 'EN_PROCESO')
            """)
            estadisticas["obras_activas"] = cursor.fetchone()[0]

            # Presupuesto total
            cursor.execute(f"SELECT SUM(presupuesto_total) FROM {tabla_obras}")
            resultado = cursor.fetchone()[0]
            estadisticas["presupuesto_total"] = float(resultado) if resultado else 0

            # Obras por responsable
            cursor.execute(f"""
                SELECT responsable, COUNT(*) as cantidad
                FROM {tabla_obras}
                WHERE responsable IS NOT NULL
                GROUP BY responsable
                ORDER BY cantidad DESC
            """)
            estadisticas["obras_por_responsable"] = [
                {"responsable": row[0], "cantidad": row[1]} for row in cursor.fetchall()
            ]

            return estadisticas

        except Exception as e:
            print(f"[ERROR OBRAS] Error obteniendo estadísticas: {e}")
            return self._get_estadisticas_demo()

    def _get_obras_demo(self) -> List[Dict[str, Any]]:
        """Datos demo consolidados para obras."""
        return [
            {
                "id": 1,
                "codigo": "OBR-2025-001",
                "nombre": "Casa Familiar Los Pinos",
                "cliente": "Juan Pérez",
                "estado": "EN_PROCESO",
                "responsable": "Ing. María González",
                "fecha_inicio": datetime.date(2025, 1, 15),
                "fecha_fin_estimada": datetime.date(2025, 6, 15),
                "presupuesto_total": 85000000.0,
                "tipo_obra": "CONSTRUCCION",
                "prioridad": "ALTA",
                "descripcion": "Construcción de casa unifamiliar de 120m2",
                "ubicacion": "Cra 15 #45-67, Bogotá",
                "created_at": datetime.datetime(2025, 1, 10, 10, 30),
                "updated_at": datetime.datetime(2025, 1, 20, 16, 45),
                "progreso": 35.5,
                "total_productos": 45,
                "productos_planificados": 20,
                "productos_asignados": 15,
                "productos_entregados": 10,
                "valor_productos_estimado": 12500000.0,
                "valor_productos_real": 8750000.0
            },
            {
                "id": 2,
                "codigo": "OBR-2025-002",
                "nombre": "Remodelación Oficina Central",
                "cliente": "Empresa XYZ S.A.S.",
                "estado": "PLANIFICACION",
                "responsable": "Arq. Carlos Rodríguez",
                "fecha_inicio": datetime.date(2025, 2, 1),
                "fecha_fin_estimada": datetime.date(2025, 4, 30),
                "presupuesto_total": 45000000.0,
                "tipo_obra": "REMODELACION",
                "prioridad": "MEDIA",
                "descripcion": "Remodelación de oficinas corporativas",
                "ubicacion": "Zona Rosa, Bogotá",
                "created_at": datetime.datetime(2025, 1, 18, 14, 20),
                "updated_at": datetime.datetime(2025, 1, 18, 14, 20),
                "progreso": 0.0,
                "total_productos": 28,
                "productos_planificados": 28,
                "productos_asignados": 0,
                "productos_entregados": 0,
                "valor_productos_estimado": 8500000.0,
                "valor_productos_real": 0.0
            }
        ]

    def _get_estadisticas_demo(self) -> Dict[str, Any]:
        """Estadísticas demo consolidadas."""
        return {
            "total_obras": 15,
            "obras_por_estado": [
                {"estado": "EN_PROCESO", "cantidad": 6},
                {"estado": "PLANIFICACION", "cantidad": 4},
                {"estado": "FINALIZADA", "cantidad": 3},
                {"estado": "PAUSADA", "cantidad": 2}
            ],
            "obras_activas": 10,
            "presupuesto_total": 485000000.0,
            "obras_por_responsable": [
                {"responsable": "Ing. María González", "cantidad": 4},
                {"responsable": "Arq. Carlos Rodríguez", "cantidad": 3},
                {"responsable": "Ing. Ana Martínez", "cantidad": 2}
            ]
        }