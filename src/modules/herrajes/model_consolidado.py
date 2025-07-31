"""
Modelo de Herrajes Consolidado - Rexus.app v2.0.0

Actualizado para usar la nueva estructura de base de datos consolidada:
- Tabla principal: productos (con categoria = 'HERRAJE')
- Movimientos: movimientos_inventario (unificado)
- Asignaciones obra: productos_obra (unificado)
"""

from typing import Any, Dict, List, Optional, Tuple
from src.utils.sql_security import validate_table_name, SQLSecurityError
from src.utils.sql_loader import load_sql


class HerrajesModel:
    """Modelo para gestionar herrajes usando la estructura consolidada."""

    # Tipos de herrajes
    TIPOS_HERRAJES = {
        "BISAGRA": "Bisagra",
        "CERRADURA": "Cerradura",
        "MANIJA": "Manija",
        "TORNILLO": "Tornillo",
        "RIEL": "Riel",
        "SOPORTE": "Soporte",
        "PESTILLO": "Pestillo",
        "RUEDA": "Rueda",
        "GUIA": "Guía",
        "OTRO": "Otro",
    }

    # Estados de herrajes
    ESTADOS = {
        "ACTIVO": "Activo",
        "INACTIVO": "Inactivo",
        "DESCONTINUADO": "Descontinuado",
    }

    # Unidades de medida
    UNIDADES = {
        "UND": "Unidad",
        "PAR": "Par",
        "JUEGO": "Juego",
        "METRO": "Metro",
        "KILOGRAMO": "Kilogramo",
        "CAJA": "Caja",
    }

    def __init__(self, db_connection=None):
        """
        Inicializa el modelo de herrajes consolidado.

        Args:
            db_connection: Conexión a la base de datos
        """
        self.db_connection = db_connection
        
        # Usar tablas consolidadas
        self.tabla_productos = "productos"
        self.tabla_movimientos = "movimientos_inventario"
        self.tabla_productos_obra = "productos_obra"
        self.tabla_pedidos = "pedidos_consolidado"
        self.tabla_pedidos_detalle = "pedidos_detalle_consolidado"
        
        # Lista de tablas permitidas para prevenir SQL injection
        self._allowed_tables = {
            "productos", "movimientos_inventario", "productos_obra",
            "pedidos_consolidado", "pedidos_detalle_consolidado", "obras"
        }

        if not self.db_connection:
            print("[ERROR HERRAJES] No hay conexión a la base de datos. El módulo no funcionará correctamente.")
        
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

            # Verificar tabla principal productos
            cursor.execute(
                "SELECT * FROM sysobjects WHERE name=? AND xtype='U'",
                (self.tabla_productos,),
            )
            if cursor.fetchone():
                print(f"[HERRAJES] Tabla consolidada '{self.tabla_productos}' verificada correctamente.")
            else:
                print(f"[ADVERTENCIA] Tabla consolidada '{self.tabla_productos}' no existe. Usando tabla legacy.")
                # Fallback a tabla legacy
                self.tabla_productos = "herrajes"
                self._allowed_tables.add("herrajes")
                self._allowed_tables.add("herrajes_obra")
                self._allowed_tables.add("herrajes_inventario")
                self._allowed_tables.add("pedidos_herrajes")

            # Verificar tabla de movimientos consolidada
            cursor.execute(
                "SELECT * FROM sysobjects WHERE name=? AND xtype='U'",
                (self.tabla_movimientos,),
            )
            if cursor.fetchone():
                print(f"[HERRAJES] Tabla '{self.tabla_movimientos}' verificada correctamente.")
            else:
                print(f"[ADVERTENCIA] Tabla '{self.tabla_movimientos}' no existe. Funcionalidad limitada.")

            # Verificar tabla productos_obra consolidada
            cursor.execute(
                "SELECT * FROM sysobjects WHERE name=? AND xtype='U'",
                (self.tabla_productos_obra,),
            )
            if cursor.fetchone():
                print(f"[HERRAJES] Tabla '{self.tabla_productos_obra}' verificada correctamente.")
            else:
                print(f"[ADVERTENCIA] Tabla '{self.tabla_productos_obra}' no existe. Usando herrajes_obra legacy.")

            print(f"[HERRAJES] Verificación de tablas consolidadas completada.")

        except Exception as e:
            print(f"[ERROR HERRAJES] Error verificando tablas: {e}")

    def obtener_todos_herrajes(self, filtros=None):
        """
        Obtiene todos los herrajes desde la tabla productos consolidada.

        Args:
            filtros (dict): Filtros opcionales (tipo, proveedor, stock_min)

        Returns:
            List[Dict]: Lista de herrajes
        """
        if not self.db_connection:
            print("[ADVERTENCIA] Sin conexión a la base de datos. Mostrando datos demo.")
            return self._get_herrajes_demo()

        try:
            cursor = self.db_connection.cursor()
            tabla_productos = self._validate_table_name(self.tabla_productos)

            if tabla_productos == "productos":
                # Cargar query desde archivo SQL externo
                query = load_sql("herrajes", "select_all_herrajes")
            else:
                # Fallback a tabla legacy herrajes
                try:
                    query = load_sql("herrajes", "select_herrajes")
                except Exception as e:
                    print(f"[ERROR HERRAJES] Error cargando script SQL: {e}")
                    query = f"SELECT * FROM {tabla_productos} WHERE estado = 'ACTIVO'"

            params = []
            where_clauses = []

            if filtros:
                if filtros.get("tipo"):
                    if tabla_productos == "productos":
                        where_clauses.append("subcategoria = ?")
                    else:
                        where_clauses.append("tipo = ?")
                    params.append(filtros["tipo"])

                if filtros.get("proveedor"):
                    where_clauses.append("proveedor LIKE ?")
                    params.append(f"%{filtros['proveedor']}%")

                if filtros.get("stock_min"):
                    where_clauses.append("stock_actual >= ?")
                    params.append(filtros["stock_min"])

                if filtros.get("busqueda"):
                    where_clauses.append("(codigo LIKE ? OR descripcion LIKE ?)")
                    busqueda = f"%{filtros['busqueda']}%"
                    params.extend([busqueda, busqueda])

            if where_clauses:
                query += " AND " + " AND ".join(where_clauses)

            query += " ORDER BY codigo"

            cursor.execute(query, params)
            columnas = [column[0] for column in cursor.description]
            resultados = cursor.fetchall()

            herrajes = []
            for fila in resultados:
                herraje = dict(zip(columnas, fila))
                # Calcular estado del stock para herrajes
                if tabla_productos == "productos":
                    herraje["estado_stock"] = self._determinar_estado_stock(herraje)
                herrajes.append(herraje)

            print(f"[INFO HERRAJES] {len(herrajes)} herrajes obtenidos correctamente.")
            return herrajes

        except Exception as e:
            print(f"[ERROR HERRAJES] Error obteniendo herrajes: {e}")
            return self._get_herrajes_demo()

    def _determinar_estado_stock(self, herraje):
        """Determina el estado del stock específico para herrajes."""
        stock_actual = herraje.get("stock_actual", 0)
        stock_minimo = herraje.get("stock_minimo", 0)

        if stock_actual <= 0:
            return "AGOTADO"
        elif stock_actual <= stock_minimo:
            return "CRÍTICO"
        elif stock_actual <= stock_minimo * 1.2:  # Herrajes tienen margen menor
            return "BAJO"
        else:
            return "NORMAL"

    def obtener_herrajes_por_obra(self, obra_id):
        """
        Obtiene herrajes asignados a una obra usando tabla consolidada.

        Args:
            obra_id (int): ID de la obra

        Returns:
            List[Dict]: Lista de herrajes con cantidades asignadas
        """
        if not self.db_connection:
            return []

        try:
            cursor = self.db_connection.cursor()
            tabla_productos = self._validate_table_name(self.tabla_productos)
            tabla_productos_obra = self._validate_table_name(self.tabla_productos_obra)

            if tabla_productos_obra == "productos_obra":
                # Usar tabla consolidada
                query = f"""
                SELECT
                    p.id, p.codigo, p.descripcion, p.subcategoria as tipo, 
                    p.proveedor, p.precio_unitario, p.unidad_medida,
                    po.cantidad_requerida, po.cantidad_asignada, po.cantidad_utilizada,
                    po.cantidad_pendiente, po.estado, po.fecha_asignacion,
                    po.etapa_obra, po.ubicacion_obra, po.observaciones,
                    po.precio_unitario_real, po.costo_total_real
                FROM {tabla_productos} p
                INNER JOIN {tabla_productos_obra} po ON p.id = po.producto_id
                WHERE po.obra_id = ? AND p.categoria = 'HERRAJE' AND po.activo = 1
                ORDER BY p.codigo
                """
            else:
                # Fallback a tabla legacy
                query = f"""
                SELECT
                    h.id, h.codigo, h.descripcion, h.tipo, h.proveedor, 
                    h.precio_unitario, h.unidad_medida,
                    ho.cantidad_requerida, ho.cantidad_pedida as cantidad_asignada,
                    0 as cantidad_utilizada, 
                    (ho.cantidad_requerida - ISNULL(ho.cantidad_pedida, 0)) as cantidad_pendiente,
                    ho.estado, ho.fecha_asignacion, ho.observaciones
                FROM herrajes h
                INNER JOIN herrajes_obra ho ON h.id = ho.herraje_id
                WHERE ho.obra_id = ?
                ORDER BY h.codigo
                """

            cursor.execute(query, (obra_id,))
            columnas = [column[0] for column in cursor.description]
            resultados = cursor.fetchall()

            herrajes_obra = []
            for fila in resultados:
                herraje = dict(zip(columnas, fila))
                herrajes_obra.append(herraje)

            return herrajes_obra

        except Exception as e:
            print(f"[ERROR HERRAJES] Error obteniendo herrajes por obra: {e}")
            return []

    def asignar_herraje_obra(self, herraje_id, obra_id, cantidad_requerida, observaciones=None, etapa_obra=None):
        """
        Asigna un herraje a una obra usando tabla consolidada.

        Args:
            herraje_id (int): ID del herraje (producto)
            obra_id (int): ID de la obra
            cantidad_requerida (float): Cantidad requerida
            observaciones (str): Observaciones opcionales
            etapa_obra (str): Etapa de la obra

        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        if not self.db_connection:
            return False, "Sin conexión a la base de datos"

        try:
            cursor = self.db_connection.cursor()
            tabla_productos = self._validate_table_name(self.tabla_productos)
            tabla_productos_obra = self._validate_table_name(self.tabla_productos_obra)

            # Obtener información del herraje
            cursor.execute(f"""
                SELECT codigo, descripcion, categoria, stock_actual, precio_unitario
                FROM {tabla_productos}
                WHERE id = ? AND categoria = 'HERRAJE' AND activo = 1
            """, (herraje_id,))
            
            herraje = cursor.fetchone()
            if not herraje:
                return False, "Herraje no encontrado"

            codigo, descripcion, categoria, stock_actual, precio_unitario = herraje

            # Verificar stock disponible
            if stock_actual < cantidad_requerida:
                return False, f"Stock insuficiente. Disponible: {stock_actual}, Requerido: {cantidad_requerida}"

            if tabla_productos_obra == "productos_obra":
                # Usar tabla consolidada
                sql_insert = f"""
                INSERT INTO {tabla_productos_obra}
                (obra_id, producto_id, codigo_producto, descripcion_producto, categoria_producto,
                 cantidad_requerida, etapa_obra, estado, precio_unitario_presupuesto,
                 observaciones, fecha_creacion, activo, usuario_creacion)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'PLANIFICADO', ?, ?, GETDATE(), 1, 'SISTEMA')
                """

                cursor.execute(sql_insert, (
                    obra_id, herraje_id, codigo, descripcion, categoria,
                    cantidad_requerida, etapa_obra or 'GENERAL', precio_unitario,
                    observaciones
                ))
            else:
                # Fallback a tabla legacy
                sql_insert = """
                INSERT INTO herrajes_obra
                (herraje_id, obra_id, cantidad_requerida, estado, fecha_asignacion, observaciones)
                VALUES (?, ?, ?, 'PENDIENTE', GETDATE(), ?)
                """

                cursor.execute(sql_insert, (herraje_id, obra_id, cantidad_requerida, observaciones))

            self.db_connection.commit()
            print(f"[HERRAJES] Herraje {codigo} asignado a obra {obra_id}")
            return True, f"Herraje '{codigo}' asignado correctamente a la obra"

        except Exception as e:
            print(f"[ERROR HERRAJES] Error asignando herraje a obra: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return False, f"Error asignando herraje: {str(e)}"

    def crear_herraje(self, datos_herraje: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Crea un nuevo herraje en la tabla productos consolidada.

        Args:
            datos_herraje: Datos del herraje a crear

        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        if not self.db_connection:
            return False, "Sin conexión a la base de datos"

        try:
            cursor = self.db_connection.cursor()
            tabla_productos = self._validate_table_name(self.tabla_productos)

            # Verificar que el código no exista
            cursor.execute(f"""
                SELECT COUNT(*) FROM {tabla_productos} 
                WHERE codigo = ? AND categoria = 'HERRAJE'
            """, (datos_herraje["codigo"],))
            
            if cursor.fetchone()[0] > 0:
                return False, f"El código '{datos_herraje['codigo']}' ya existe en herrajes"

            if tabla_productos == "productos":
                # Insertar en tabla consolidada
                sql_insert = """
                INSERT INTO productos
                (codigo, descripcion, categoria, subcategoria, tipo,
                 stock_actual, stock_minimo, stock_maximo, precio_unitario, costo_unitario,
                 unidad_medida, ubicacion, color, material, marca, modelo, acabado,
                 proveedor, codigo_proveedor, tiempo_entrega_dias,
                 observaciones, codigo_qr, imagen_url, es_critico,
                 estado, activo, usuario_creacion, fecha_creacion)
                VALUES (?, ?, 'HERRAJE', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, GETDATE())
                """

                cursor.execute(sql_insert, (
                    datos_herraje["codigo"],
                    datos_herraje["descripcion"],
                    datos_herraje.get("tipo", "OTRO"),  # subcategoria
                    datos_herraje.get("subtipo", ""),   # tipo
                    datos_herraje.get("stock_actual", 0),
                    datos_herraje.get("stock_minimo", 5),  # Herrajes típicamente tienen stock mínimo menor
                    datos_herraje.get("stock_maximo", 500),
                    datos_herraje.get("precio_unitario", 0.00),
                    datos_herraje.get("costo_unitario", datos_herraje.get("precio_unitario", 0.00) * 0.6),
                    datos_herraje.get("unidad_medida", "UND"),
                    datos_herraje.get("ubicacion", ""),
                    datos_herraje.get("color", ""),
                    datos_herraje.get("material", "METAL"),
                    datos_herraje.get("marca", ""),
                    datos_herraje.get("modelo", ""),
                    datos_herraje.get("acabado", ""),
                    datos_herraje.get("proveedor", ""),
                    datos_herraje.get("codigo_proveedor", ""),
                    datos_herraje.get("tiempo_entrega_dias", 7),
                    datos_herraje.get("observaciones", ""),
                    datos_herraje.get("codigo_qr", ""),
                    datos_herraje.get("imagen_url", ""),
                    1 if datos_herraje.get("tipo") in ["BISAGRA", "CERRADURA", "PESTILLO"] else 0,  # es_critico
                    datos_herraje.get("estado", "ACTIVO"),
                    "SISTEMA"
                ))

                # Obtener ID del producto creado
                cursor.execute("SELECT @@IDENTITY")
                producto_id = cursor.fetchone()[0]

                # Registrar movimiento inicial si hay stock
                stock_inicial = datos_herraje.get("stock_actual", 0)
                if stock_inicial > 0:
                    self._registrar_movimiento_consolidado(
                        producto_id, "ENTRADA", stock_inicial, 
                        "Stock inicial de herraje", "SISTEMA"
                    )

            else:
                # Fallback a tabla legacy herrajes
                sql_insert = """
                INSERT INTO herrajes
                (codigo, descripcion, tipo, proveedor, precio_unitario, unidad_medida,
                 categoria, estado, stock_minimo, stock_actual, observaciones,
                 especificaciones, marca, modelo, color, material, dimensiones, peso)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """

                cursor.execute(sql_insert, (
                    datos_herraje["codigo"],
                    datos_herraje["descripcion"],
                    datos_herraje.get("tipo", "OTRO"),
                    datos_herraje.get("proveedor", ""),
                    datos_herraje.get("precio_unitario", 0.00),
                    datos_herraje.get("unidad_medida", "UND"),
                    datos_herraje.get("categoria", ""),
                    datos_herraje.get("estado", "ACTIVO"),
                    datos_herraje.get("stock_minimo", 5),
                    datos_herraje.get("stock_actual", 0),
                    datos_herraje.get("observaciones", ""),
                    datos_herraje.get("especificaciones", ""),
                    datos_herraje.get("marca", ""),
                    datos_herraje.get("modelo", ""),
                    datos_herraje.get("color", ""),
                    datos_herraje.get("material", "METAL"),
                    datos_herraje.get("dimensiones", ""),
                    datos_herraje.get("peso", 0.0)
                ))

            self.db_connection.commit()
            return True, f"Herraje '{datos_herraje['codigo']}' creado exitosamente"

        except Exception as e:
            print(f"[ERROR HERRAJES] Error creando herraje: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return False, f"Error creando herraje: {str(e)}"

    def _registrar_movimiento_consolidado(self, producto_id, tipo_movimiento, cantidad, motivo, usuario):
        """Registra un movimiento en el sistema consolidado."""
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
            print(f"[ERROR HERRAJES] Error registrando movimiento: {e}")

    def buscar_herrajes(self, termino_busqueda):
        """
        Busca herrajes por término usando tabla consolidada.

        Args:
            termino_busqueda (str): Término a buscar

        Returns:
            List[Dict]: Lista de herrajes que coinciden
        """
        if not termino_busqueda:
            return []

        filtros = {"busqueda": termino_busqueda}
        return self.obtener_todos_herrajes(filtros)

    def obtener_estadisticas(self):
        """
        Obtiene estadísticas de herrajes desde tabla consolidada.

        Returns:
            Dict: Estadísticas de herrajes
        """
        if not self.db_connection:
            return {
                "total_herrajes": 0,
                "proveedores_activos": 0,
                "valor_total_inventario": 0.0,
                "herrajes_por_proveedor": [],
            }

        try:
            cursor = self.db_connection.cursor()
            tabla_productos = self._validate_table_name(self.tabla_productos)

            estadisticas = {}

            if tabla_productos == "productos":
                # Usar tabla consolidada
                cursor.execute("""
                    SELECT COUNT(*) FROM productos 
                    WHERE categoria = 'HERRAJE' AND estado = 'ACTIVO' AND activo = 1
                """)
                estadisticas["total_herrajes"] = cursor.fetchone()[0]

                cursor.execute("""
                    SELECT COUNT(DISTINCT proveedor) FROM productos 
                    WHERE categoria = 'HERRAJE' AND estado = 'ACTIVO' AND activo = 1
                    AND proveedor IS NOT NULL AND proveedor != ''
                """)
                estadisticas["proveedores_activos"] = cursor.fetchone()[0]

                cursor.execute("""
                    SELECT SUM(stock_actual * precio_unitario) FROM productos 
                    WHERE categoria = 'HERRAJE' AND estado = 'ACTIVO' AND activo = 1
                """)
                resultado = cursor.fetchone()[0]
                estadisticas["valor_total_inventario"] = float(resultado or 0.0)

                # Herrajes por proveedor
                cursor.execute("""
                    SELECT proveedor, COUNT(*) as cantidad,
                           SUM(stock_actual * precio_unitario) as valor_total
                    FROM productos
                    WHERE categoria = 'HERRAJE' AND estado = 'ACTIVO' AND activo = 1
                    AND proveedor IS NOT NULL AND proveedor != ''
                    GROUP BY proveedor
                    ORDER BY cantidad DESC
                """)
                estadisticas["herrajes_por_proveedor"] = [
                    {
                        "proveedor": row[0], 
                        "cantidad": row[1],
                        "valor_total": float(row[2] or 0.0)
                    } 
                    for row in cursor.fetchall()
                ]

            else:
                # Fallback a tabla legacy
                cursor.execute("SELECT COUNT(*) FROM herrajes WHERE estado = 'ACTIVO'")
                estadisticas["total_herrajes"] = cursor.fetchone()[0]

                cursor.execute("""
                    SELECT COUNT(DISTINCT proveedor) FROM herrajes 
                    WHERE estado = 'ACTIVO' AND proveedor IS NOT NULL
                """)
                estadisticas["proveedores_activos"] = cursor.fetchone()[0]

                cursor.execute("""
                    SELECT SUM(precio_unitario) FROM herrajes WHERE estado = 'ACTIVO'
                """)
                resultado = cursor.fetchone()[0]
                estadisticas["valor_total_inventario"] = float(resultado or 0.0)

                cursor.execute("""
                    SELECT proveedor, COUNT(*) as cantidad
                    FROM herrajes
                    WHERE estado = 'ACTIVO' AND proveedor IS NOT NULL
                    GROUP BY proveedor
                    ORDER BY cantidad DESC
                """)
                estadisticas["herrajes_por_proveedor"] = [
                    {"proveedor": row[0], "cantidad": row[1], "valor_total": 0.0}
                    for row in cursor.fetchall()
                ]

            return estadisticas

        except Exception as e:
            print(f"[ERROR HERRAJES] Error obteniendo estadísticas: {e}")
            return {
                "total_herrajes": 0,
                "proveedores_activos": 0,
                "valor_total_inventario": 0.0,
                "herrajes_por_proveedor": [],
            }

    def obtener_herraje_por_id(self, herraje_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene un herraje por su ID desde tabla consolidada.

        Args:
            herraje_id: ID del herraje (producto)

        Returns:
            Dict con los datos del herraje o None si no existe
        """
        if not self.db_connection:
            return None

        try:
            cursor = self.db_connection.cursor()
            tabla_productos = self._validate_table_name(self.tabla_productos)

            if tabla_productos == "productos":
                sql_select = load_sql("herrajes", "select_by_id")
                cursor.execute(sql_select, (herraje_id,))
            else:
                cursor.execute("""
                    SELECT h.*, i.stock_actual, i.stock_reservado, 
                           i.ubicacion, i.fecha_ultima_entrada, i.fecha_ultima_salida
                    FROM herrajes h
                    LEFT JOIN herrajes_inventario i ON h.id = i.herraje_id
                    WHERE h.id = ? AND h.estado = 'ACTIVO'
                """, (herraje_id,))

            row = cursor.fetchone()
            if row:
                columns = [desc[0] for desc in cursor.description]
                return dict(zip(columns, row))
            return None

        except Exception as e:
            print(f"[ERROR HERRAJES] Error obteniendo herraje por ID: {e}")
            return None

    def obtener_proveedores(self) -> List[str]:
        """
        Obtiene la lista de proveedores únicos de herrajes.

        Returns:
            Lista de nombres de proveedores
        """
        if not self.db_connection:
            return ["Herrajes SA", "Seguridad Total", "Accesorios Pro"]

        try:
            cursor = self.db_connection.cursor()
            tabla_productos = self._validate_table_name(self.tabla_productos)

            if tabla_productos == "productos":
                cursor.execute("""
                    SELECT DISTINCT proveedor 
                    FROM productos 
                    WHERE categoria = 'HERRAJE' AND estado = 'ACTIVO' AND activo = 1
                    AND proveedor IS NOT NULL AND proveedor != ''
                    ORDER BY proveedor
                """)
            else:
                cursor.execute("""
                    SELECT DISTINCT proveedor 
                    FROM herrajes 
                    WHERE estado = 'ACTIVO' AND proveedor IS NOT NULL
                    ORDER BY proveedor
                """)

            return [row[0] for row in cursor.fetchall()]

        except Exception as e:
            print(f"[ERROR HERRAJES] Error obteniendo proveedores: {e}")
            return []

    def actualizar_stock(self, herraje_id: int, nuevo_stock: int, 
                        tipo_movimiento: str = "AJUSTE_POSITIVO") -> Tuple[bool, str]:
        """
        Actualiza el stock de un herraje usando sistema consolidado.

        Args:
            herraje_id: ID del herraje (producto)
            nuevo_stock: Nuevo stock actual
            tipo_movimiento: Tipo de movimiento

        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        if not self.db_connection:
            return False, "Sin conexión a la base de datos"

        try:
            cursor = self.db_connection.cursor()
            tabla_productos = self._validate_table_name(self.tabla_productos)

            # Obtener stock actual
            cursor.execute(f"""
                SELECT stock_actual FROM {tabla_productos} 
                WHERE id = ? AND categoria = 'HERRAJE'
            """, (herraje_id,))
            
            row = cursor.fetchone()
            if not row:
                return False, "Herraje no encontrado"

            stock_anterior = row[0]
            diferencia = nuevo_stock - stock_anterior

            if diferencia != 0:
                # Registrar movimiento
                self._registrar_movimiento_consolidado(
                    herraje_id, 
                    tipo_movimiento if diferencia > 0 else "AJUSTE_NEGATIVO",
                    abs(diferencia),
                    f"Actualización de stock: {stock_anterior} → {nuevo_stock}",
                    "SISTEMA"
                )

            # Actualizar stock
            cursor.execute(f"""
                UPDATE {tabla_productos}
                SET stock_actual = ?, fecha_actualizacion = GETDATE()
                WHERE id = ?
            """, (nuevo_stock, herraje_id))

            self.db_connection.commit()
            return True, "Stock de herraje actualizado exitosamente"

        except Exception as e:
            print(f"[ERROR HERRAJES] Error actualizando stock: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return False, f"Error actualizando stock: {str(e)}"

    def _get_herrajes_demo(self) -> List[Dict[str, Any]]:
        """Datos demo consolidados para herrajes."""
        return [
            {
                "id": 1,
                "codigo": "HERR001",
                "descripcion": "Bisagra de puerta estándar",
                "categoria": "HERRAJE",
                "subcategoria": "BISAGRA",
                "tipo": "Estructural",
                "stock_actual": 50,
                "stock_minimo": 10,
                "stock_maximo": 200,
                "stock_reservado": 5,
                "stock_disponible": 45,
                "precio_unitario": 15.50,
                "precio_promedio": 15.50,
                "costo_unitario": 9.30,
                "unidad_medida": "UND",
                "ubicacion": "Bodega C-1",
                "color": "Negro",
                "material": "Acero",
                "marca": "Stanley",
                "modelo": "ST-001",
                "acabado": "Pintado",
                "proveedor": "Herrajes SA",
                "codigo_proveedor": "HSA-001",
                "tiempo_entrega_dias": 7,
                "observaciones": "Bisagra estándar para puertas",
                "codigo_qr": "QR-HERR001",
                "imagen_url": "",
                "es_critico": True,
                "estado": "ACTIVO",
                "activo": True,
                "fecha_creacion": "2024-01-15",
                "fecha_actualizacion": "2024-01-15",
                "estado_stock": "NORMAL"
            },
            {
                "id": 2,
                "codigo": "HERR002",
                "descripcion": "Cerradura de seguridad",
                "categoria": "HERRAJE",
                "subcategoria": "CERRADURA",
                "tipo": "Seguridad",
                "stock_actual": 25,
                "stock_minimo": 5,
                "stock_maximo": 100,
                "stock_reservado": 2,
                "stock_disponible": 23,
                "precio_unitario": 85.00,
                "precio_promedio": 85.00,
                "costo_unitario": 51.00,
                "unidad_medida": "UND",
                "ubicacion": "Bodega C-2",
                "color": "Plateado",
                "material": "Acero inoxidable",
                "marca": "Yale",
                "modelo": "YL-200",
                "acabado": "Cromado",
                "proveedor": "Seguridad Total",
                "codigo_proveedor": "ST-002",
                "tiempo_entrega_dias": 10,
                "observaciones": "Cerradura de alta seguridad",
                "codigo_qr": "QR-HERR002",
                "imagen_url": "",
                "es_critico": True,
                "estado": "ACTIVO",
                "activo": True,
                "fecha_creacion": "2024-01-16",
                "fecha_actualizacion": "2024-01-16",
                "estado_stock": "NORMAL"
            },
            {
                "id": 3,
                "codigo": "HERR003",
                "descripcion": "Manija para ventana",
                "categoria": "HERRAJE",
                "subcategoria": "MANIJA",
                "tipo": "Accesorio",
                "stock_actual": 3,
                "stock_minimo": 15,
                "stock_maximo": 80,
                "stock_reservado": 0,
                "stock_disponible": 3,
                "precio_unitario": 22.75,
                "precio_promedio": 22.75,
                "costo_unitario": 13.65,
                "unidad_medida": "UND",
                "ubicacion": "Bodega C-3",
                "color": "Blanco",
                "material": "Aluminio",
                "marca": "VentTech",
                "modelo": "VT-MAN01",
                "acabado": "Anodizado",
                "proveedor": "Accesorios Pro",
                "codigo_proveedor": "AP-003",
                "tiempo_entrega_dias": 5,
                "observaciones": "Stock bajo - reponer urgente",
                "codigo_qr": "QR-HERR003",
                "imagen_url": "",
                "es_critico": False,
                "estado": "ACTIVO",
                "activo": True,
                "fecha_creacion": "2024-01-17",
                "fecha_actualizacion": "2024-01-17",
                "estado_stock": "CRÍTICO"
            }
        ]