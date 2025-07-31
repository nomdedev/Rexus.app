"""
Modelo de Vidrios Consolidado - Rexus.app v2.0.0

Actualizado para usar la nueva estructura de base de datos consolidada:
- Tabla principal: productos (con categoria = 'VIDRIO')
- Movimientos: movimientos_inventario (unificado)
- Asignaciones obra: productos_obra (unificado)
"""

from typing import Any, Dict, List, Optional, Tuple
from src.utils.sql_security import validate_table_name, load_sql_script, SQLSecurityError


class VidriosModel:
    """Modelo para gestionar vidrios usando la estructura consolidada."""

    # Tipos de vidrios
    TIPOS_VIDRIOS = {
        "TEMPLADO": "Templado",
        "LAMINADO": "Laminado",
        "COMUN": "Común",
        "ESPEJO": "Espejo",
        "DVH": "Doble Vidriado Hermético",
        "ACUSTICO": "Acústico",
        "REFLECTIVO": "Reflectivo",
        "POLARIZADO": "Polarizado",
        "ANTIREFLEJO": "Antireflejo",
        "DECORATIVO": "Decorativo",
        "OTRO": "Otro",
    }

    # Estados de vidrios
    ESTADOS = {
        "ACTIVO": "Activo",
        "INACTIVO": "Inactivo",
        "DESCONTINUADO": "Descontinuado",
    }

    # Espesores comunes
    ESPESORES = [3, 4, 5, 6, 8, 10, 12, 15, 19, 20, 25]

    # Unidades de medida para vidrios
    UNIDADES = {
        "M2": "Metro cuadrado",
        "UND": "Unidad",
        "PLANCHA": "Plancha",
        "ML": "Metro lineal",
    }

    def __init__(self, db_connection=None):
        """
        Inicializa el modelo de vidrios consolidado.

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
            print("[ERROR VIDRIOS] No hay conexión a la base de datos. El módulo no funcionará correctamente.")
        
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
                print(f"[VIDRIOS] Tabla consolidada '{self.tabla_productos}' verificada correctamente.")
            else:
                print(f"[ADVERTENCIA] Tabla consolidada '{self.tabla_productos}' no existe. Usando tabla legacy.")
                # Fallback a tabla legacy
                self.tabla_productos = "vidrios"
                self._allowed_tables.add("vidrios")
                self._allowed_tables.add("vidrios_obra")
                self._allowed_tables.add("pedidos_vidrios")

            # Verificar tabla de movimientos consolidada
            cursor.execute(
                "SELECT * FROM sysobjects WHERE name=? AND xtype='U'",
                (self.tabla_movimientos,),
            )
            if cursor.fetchone():
                print(f"[VIDRIOS] Tabla '{self.tabla_movimientos}' verificada correctamente.")
            else:
                print(f"[ADVERTENCIA] Tabla '{self.tabla_movimientos}' no existe. Funcionalidad limitada.")

            # Verificar tabla productos_obra consolidada
            cursor.execute(
                "SELECT * FROM sysobjects WHERE name=? AND xtype='U'",
                (self.tabla_productos_obra,),
            )
            if cursor.fetchone():
                print(f"[VIDRIOS] Tabla '{self.tabla_productos_obra}' verificada correctamente.")
            else:
                print(f"[ADVERTENCIA] Tabla '{self.tabla_productos_obra}' no existe. Usando vidrios_obra legacy.")

            print(f"[VIDRIOS] Verificación de tablas consolidadas completada.")

        except Exception as e:
            print(f"[ERROR VIDRIOS] Error verificando tablas: {e}")

    def obtener_todos_vidrios(self, filtros=None):
        """
        Obtiene todos los vidrios desde la tabla productos consolidada.

        Args:
            filtros (dict): Filtros opcionales (tipo, proveedor, espesor, color)

        Returns:
            List[Dict]: Lista de vidrios
        """
        if not self.db_connection:
            print("[ADVERTENCIA] Sin conexión a la base de datos. Mostrando datos demo.")
            return self._get_vidrios_demo()

        try:
            cursor = self.db_connection.cursor()
            tabla_productos = self._validate_table_name(self.tabla_productos)

            if tabla_productos == "productos":
                # Usar tabla consolidada filtrando por categoría VIDRIO
                query = """
                SELECT 
                    id, codigo, descripcion, categoria, subcategoria, tipo,
                    stock_actual, stock_minimo, stock_maximo, stock_reservado, stock_disponible,
                    precio_unitario, precio_promedio, costo_unitario, unidad_medida,
                    ubicacion, color, material, marca, modelo, acabado,
                    proveedor, codigo_proveedor, tiempo_entrega_dias,
                    observaciones, codigo_qr, imagen_url, propiedades_especiales,
                    estado, activo, fecha_creacion, fecha_actualizacion
                FROM productos
                WHERE categoria = 'VIDRIO' AND activo = 1
                """
            else:
                # Fallback a tabla legacy vidrios
                try:
                    script_path = "scripts/sql/select_vidrios.sql"
                    query = load_sql_script(script_path)
                except SQLSecurityError as e:
                    print(f"[ERROR VIDRIOS] Error cargando script SQL: {e}")
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

                if filtros.get("espesor"):
                    if tabla_productos == "productos":
                        where_clauses.append("JSON_VALUE(propiedades_especiales, '$.espesor') = ?")
                    else:
                        where_clauses.append("espesor = ?")
                    params.append(str(filtros["espesor"]))

                if filtros.get("color"):
                    where_clauses.append("color LIKE ?")
                    params.append(f"%{filtros['color']}%")

                if filtros.get("busqueda"):
                    where_clauses.append("(codigo LIKE ? OR descripcion LIKE ?)")
                    busqueda = f"%{filtros['busqueda']}%"
                    params.extend([busqueda, busqueda])

            if where_clauses:
                query += " AND " + " AND ".join(where_clauses)

            query += " ORDER BY subcategoria, codigo"

            cursor.execute(query, params)
            columnas = [column[0] for column in cursor.description]
            resultados = cursor.fetchall()

            vidrios = []
            for fila in resultados:
                vidrio = dict(zip(columnas, fila))
                # Calcular estado del stock para vidrios
                if tabla_productos == "productos":
                    vidrio["estado_stock"] = self._determinar_estado_stock(vidrio)
                    # Extraer propiedades específicas de vidrio desde JSON
                    vidrio = self._extraer_propiedades_vidrio(vidrio)
                vidrios.append(vidrio)

            print(f"[INFO VIDRIOS] {len(vidrios)} vidrios obtenidos correctamente.")
            return vidrios

        except Exception as e:
            print(f"[ERROR VIDRIOS] Error obteniendo vidrios: {e}")
            return self._get_vidrios_demo()

    def _determinar_estado_stock(self, vidrio):
        """Determina el estado del stock específico para vidrios."""
        stock_actual = vidrio.get("stock_actual", 0)
        stock_minimo = vidrio.get("stock_minimo", 0)

        if stock_actual <= 0:
            return "AGOTADO"
        elif stock_actual <= stock_minimo:
            return "CRÍTICO"
        elif stock_actual <= stock_minimo * 1.3:  # Vidrios tienen margen medio
            return "BAJO"
        else:
            return "NORMAL"

    def _extraer_propiedades_vidrio(self, vidrio):
        """Extrae propiedades específicas de vidrio desde propiedades_especiales JSON."""
        try:
            import json
            propiedades = vidrio.get("propiedades_especiales", "{}")
            if propiedades:
                props = json.loads(propiedades)
                vidrio["espesor"] = props.get("espesor", 0)
                vidrio["templado"] = props.get("templado", False)
                vidrio["laminado"] = props.get("laminado", False)
                vidrio["dvh"] = props.get("dvh", False)
                vidrio["tratamiento"] = props.get("tratamiento", "")
                vidrio["dimensiones_disponibles"] = props.get("dimensiones_disponibles", "")
        except:
            # Si no puede parsear JSON, usar valores por defecto
            vidrio["espesor"] = 0
            vidrio["templado"] = False
            vidrio["laminado"] = False
            vidrio["dvh"] = False
            vidrio["tratamiento"] = ""
            vidrio["dimensiones_disponibles"] = ""
        
        return vidrio

    def obtener_vidrios_por_obra(self, obra_id):
        """
        Obtiene vidrios asignados a una obra usando tabla consolidada.

        Args:
            obra_id (int): ID de la obra

        Returns:
            List[Dict]: Lista de vidrios con cantidades asignadas
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
                    p.proveedor, p.precio_unitario, p.unidad_medida, p.color,
                    JSON_VALUE(p.propiedades_especiales, '$.espesor') as espesor,
                    po.cantidad_requerida, po.cantidad_asignada, po.cantidad_utilizada,
                    po.cantidad_pendiente, po.estado, po.fecha_asignacion,
                    po.etapa_obra, po.ubicacion_obra, po.observaciones,
                    po.precio_unitario_real, po.costo_total_real
                FROM {tabla_productos} p
                INNER JOIN {tabla_productos_obra} po ON p.id = po.producto_id
                WHERE po.obra_id = ? AND p.categoria = 'VIDRIO' AND po.activo = 1
                ORDER BY p.codigo
                """
            else:
                # Fallback a tabla legacy
                query = f"""
                SELECT
                    v.id, v.codigo, v.descripcion, v.tipo, v.proveedor, 
                    v.precio_m2 as precio_unitario, 'M2' as unidad_medida, v.color, v.espesor,
                    vo.metros_cuadrados_requeridos as cantidad_requerida, 
                    vo.metros_cuadrados_pedidos as cantidad_asignada,
                    0 as cantidad_utilizada, 
                    (vo.metros_cuadrados_requeridos - ISNULL(vo.metros_cuadrados_pedidos, 0)) as cantidad_pendiente,
                    'PENDIENTE' as estado, vo.fecha_asignacion, vo.observaciones
                FROM vidrios v
                INNER JOIN vidrios_obra vo ON v.id = vo.vidrio_id
                WHERE vo.obra_id = ?
                ORDER BY v.codigo
                """

            cursor.execute(query, (obra_id,))
            columnas = [column[0] for column in cursor.description]
            resultados = cursor.fetchall()

            vidrios_obra = []
            for fila in resultados:
                vidrio = dict(zip(columnas, fila))
                vidrios_obra.append(vidrio)

            return vidrios_obra

        except Exception as e:
            print(f"[ERROR VIDRIOS] Error obteniendo vidrios por obra: {e}")
            return []

    def asignar_vidrio_obra(self, vidrio_id, obra_id, cantidad_requerida, observaciones=None, etapa_obra=None):
        """
        Asigna un vidrio a una obra usando tabla consolidada.

        Args:
            vidrio_id (int): ID del vidrio (producto)
            obra_id (int): ID de la obra
            cantidad_requerida (float): Cantidad requerida (m2)
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

            # Obtener información del vidrio
            cursor.execute(f"""
                SELECT codigo, descripcion, categoria, stock_actual, precio_unitario
                FROM {tabla_productos}
                WHERE id = ? AND categoria = 'VIDRIO' AND activo = 1
            """, (vidrio_id,))
            
            vidrio = cursor.fetchone()
            if not vidrio:
                return False, "Vidrio no encontrado"

            codigo, descripcion, categoria, stock_actual, precio_unitario = vidrio

            # Verificar stock disponible
            if stock_actual < cantidad_requerida:
                return False, f"Stock insuficiente. Disponible: {stock_actual} m2, Requerido: {cantidad_requerida} m2"

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
                    obra_id, vidrio_id, codigo, descripcion, categoria,
                    cantidad_requerida, etapa_obra or 'GENERAL', precio_unitario,
                    observaciones
                ))
            else:
                # Fallback a tabla legacy
                sql_insert = """
                INSERT INTO vidrios_obra
                (vidrio_id, obra_id, metros_cuadrados_requeridos, fecha_asignacion, observaciones)
                VALUES (?, ?, ?, GETDATE(), ?)
                """

                cursor.execute(sql_insert, (vidrio_id, obra_id, cantidad_requerida, observaciones))

            self.db_connection.commit()
            print(f"[VIDRIOS] Vidrio {codigo} asignado a obra {obra_id}")
            return True, f"Vidrio '{codigo}' asignado correctamente a la obra"

        except Exception as e:
            print(f"[ERROR VIDRIOS] Error asignando vidrio a obra: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return False, f"Error asignando vidrio: {str(e)}"

    def crear_vidrio(self, datos_vidrio: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Crea un nuevo vidrio en la tabla productos consolidada.

        Args:
            datos_vidrio: Datos del vidrio a crear

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
                WHERE codigo = ? AND categoria = 'VIDRIO'
            """, (datos_vidrio["codigo"],))
            
            if cursor.fetchone()[0] > 0:
                return False, f"El código '{datos_vidrio['codigo']}' ya existe en vidrios"

            if tabla_productos == "productos":
                # Crear propiedades específicas del vidrio en JSON
                propiedades_especiales = {
                    "espesor": datos_vidrio.get("espesor", 0),
                    "templado": datos_vidrio.get("templado", False),
                    "laminado": datos_vidrio.get("laminado", False),
                    "dvh": datos_vidrio.get("dvh", False),
                    "tratamiento": datos_vidrio.get("tratamiento", ""),
                    "dimensiones_disponibles": datos_vidrio.get("dimensiones_disponibles", "")
                }

                import json
                propiedades_json = json.dumps(propiedades_especiales)

                # Insertar en tabla consolidada
                sql_insert = """
                INSERT INTO productos
                (codigo, descripcion, categoria, subcategoria, tipo,
                 stock_actual, stock_minimo, stock_maximo, precio_unitario, costo_unitario,
                 unidad_medida, ubicacion, color, material, marca, modelo, acabado,
                 proveedor, codigo_proveedor, tiempo_entrega_dias,
                 observaciones, codigo_qr, imagen_url, propiedades_especiales,
                 estado, activo, usuario_creacion, fecha_creacion)
                VALUES (?, ?, 'VIDRIO', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, GETDATE())
                """

                cursor.execute(sql_insert, (
                    datos_vidrio["codigo"],
                    datos_vidrio["descripcion"],
                    datos_vidrio.get("tipo", "COMUN"),  # subcategoria
                    datos_vidrio.get("subtipo", ""),   # tipo
                    datos_vidrio.get("stock_actual", 0),
                    datos_vidrio.get("stock_minimo", 10),  # Vidrios típicamente tienen stock mínimo medio
                    datos_vidrio.get("stock_maximo", 1000),
                    datos_vidrio.get("precio_unitario", 0.00),
                    datos_vidrio.get("costo_unitario", datos_vidrio.get("precio_unitario", 0.00) * 0.7),
                    datos_vidrio.get("unidad_medida", "M2"),
                    datos_vidrio.get("ubicacion", ""),
                    datos_vidrio.get("color", "Transparente"),
                    datos_vidrio.get("material", "VIDRIO"),
                    datos_vidrio.get("marca", ""),
                    datos_vidrio.get("modelo", ""),
                    datos_vidrio.get("acabado", ""),
                    datos_vidrio.get("proveedor", ""),
                    datos_vidrio.get("codigo_proveedor", ""),
                    datos_vidrio.get("tiempo_entrega_dias", 15),  # Vidrios suelen tardar más
                    datos_vidrio.get("observaciones", ""),
                    datos_vidrio.get("codigo_qr", ""),
                    datos_vidrio.get("imagen_url", ""),
                    propiedades_json,
                    datos_vidrio.get("estado", "ACTIVO"),
                    "SISTEMA"
                ))

                # Obtener ID del producto creado
                cursor.execute("SELECT @@IDENTITY")
                producto_id = cursor.fetchone()[0]

                # Registrar movimiento inicial si hay stock
                stock_inicial = datos_vidrio.get("stock_actual", 0)
                if stock_inicial > 0:
                    self._registrar_movimiento_consolidado(
                        producto_id, "ENTRADA", stock_inicial, 
                        "Stock inicial de vidrio", "SISTEMA"
                    )

            else:
                # Fallback a tabla legacy vidrios
                sql_insert = """
                INSERT INTO vidrios
                (codigo, descripcion, tipo, espesor, proveedor, precio_m2, 
                 color, tratamiento, dimensiones_disponibles, estado, observaciones)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """

                cursor.execute(sql_insert, (
                    datos_vidrio["codigo"],
                    datos_vidrio["descripcion"],
                    datos_vidrio.get("tipo", "COMUN"),
                    datos_vidrio.get("espesor", 6),
                    datos_vidrio.get("proveedor", ""),
                    datos_vidrio.get("precio_unitario", 0.00),
                    datos_vidrio.get("color", "Transparente"),
                    datos_vidrio.get("tratamiento", ""),
                    datos_vidrio.get("dimensiones_disponibles", ""),
                    datos_vidrio.get("estado", "ACTIVO"),
                    datos_vidrio.get("observaciones", "")
                ))

            self.db_connection.commit()
            return True, f"Vidrio '{datos_vidrio['codigo']}' creado exitosamente"

        except Exception as e:
            print(f"[ERROR VIDRIOS] Error creando vidrio: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return False, f"Error creando vidrio: {str(e)}"

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
            print(f"[ERROR VIDRIOS] Error registrando movimiento: {e}")

    def buscar_vidrios(self, termino_busqueda):
        """
        Busca vidrios por término usando tabla consolidada.

        Args:
            termino_busqueda (str): Término a buscar

        Returns:
            List[Dict]: Lista de vidrios que coinciden
        """
        if not termino_busqueda:
            return []

        filtros = {"busqueda": termino_busqueda}
        return self.obtener_todos_vidrios(filtros)

    def obtener_estadisticas(self):
        """
        Obtiene estadísticas de vidrios desde tabla consolidada.

        Returns:
            Dict: Estadísticas de vidrios
        """
        if not self.db_connection:
            return {
                "total_vidrios": 0,
                "tipos_disponibles": 0,
                "proveedores_activos": 0,
                "valor_total_inventario": 0.0,
                "vidrios_por_tipo": [],
            }

        try:
            cursor = self.db_connection.cursor()
            tabla_productos = self._validate_table_name(self.tabla_productos)

            estadisticas = {}

            if tabla_productos == "productos":
                # Usar tabla consolidada
                cursor.execute("""
                    SELECT COUNT(*) FROM productos 
                    WHERE categoria = 'VIDRIO' AND estado = 'ACTIVO' AND activo = 1
                """)
                estadisticas["total_vidrios"] = cursor.fetchone()[0]

                cursor.execute("""
                    SELECT COUNT(DISTINCT subcategoria) FROM productos 
                    WHERE categoria = 'VIDRIO' AND estado = 'ACTIVO' AND activo = 1
                    AND subcategoria IS NOT NULL AND subcategoria != ''
                """)
                estadisticas["tipos_disponibles"] = cursor.fetchone()[0]

                cursor.execute("""
                    SELECT COUNT(DISTINCT proveedor) FROM productos 
                    WHERE categoria = 'VIDRIO' AND estado = 'ACTIVO' AND activo = 1
                    AND proveedor IS NOT NULL AND proveedor != ''
                """)
                estadisticas["proveedores_activos"] = cursor.fetchone()[0]

                cursor.execute("""
                    SELECT SUM(stock_actual * precio_unitario) FROM productos 
                    WHERE categoria = 'VIDRIO' AND estado = 'ACTIVO' AND activo = 1
                """)
                resultado = cursor.fetchone()[0]
                estadisticas["valor_total_inventario"] = float(resultado or 0.0)

                # Vidrios por tipo
                cursor.execute("""
                    SELECT subcategoria, COUNT(*) as cantidad,
                           SUM(stock_actual * precio_unitario) as valor_total
                    FROM productos
                    WHERE categoria = 'VIDRIO' AND estado = 'ACTIVO' AND activo = 1
                    AND subcategoria IS NOT NULL AND subcategoria != ''
                    GROUP BY subcategoria
                    ORDER BY cantidad DESC
                """)
                estadisticas["vidrios_por_tipo"] = [
                    {
                        "tipo": row[0], 
                        "cantidad": row[1],
                        "valor_total": float(row[2] or 0.0)
                    } 
                    for row in cursor.fetchall()
                ]

            else:
                # Fallback a tabla legacy
                cursor.execute("SELECT COUNT(*) FROM vidrios WHERE estado = 'ACTIVO'")
                estadisticas["total_vidrios"] = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(DISTINCT tipo) FROM vidrios WHERE estado = 'ACTIVO'")
                estadisticas["tipos_disponibles"] = cursor.fetchone()[0]

                cursor.execute("""
                    SELECT COUNT(DISTINCT proveedor) FROM vidrios 
                    WHERE estado = 'ACTIVO' AND proveedor IS NOT NULL
                """)
                estadisticas["proveedores_activos"] = cursor.fetchone()[0]

                cursor.execute("""
                    SELECT SUM(precio_m2) FROM vidrios WHERE estado = 'ACTIVO'
                """)
                resultado = cursor.fetchone()[0]
                estadisticas["valor_total_inventario"] = float(resultado or 0.0)

                cursor.execute("""
                    SELECT tipo, COUNT(*) as cantidad
                    FROM vidrios
                    WHERE estado = 'ACTIVO' AND tipo IS NOT NULL
                    GROUP BY tipo
                    ORDER BY cantidad DESC
                """)
                estadisticas["vidrios_por_tipo"] = [
                    {"tipo": row[0], "cantidad": row[1], "valor_total": 0.0}
                    for row in cursor.fetchall()
                ]

            return estadisticas

        except Exception as e:
            print(f"[ERROR VIDRIOS] Error obteniendo estadísticas: {e}")
            return {
                "total_vidrios": 0,
                "tipos_disponibles": 0,
                "proveedores_activos": 0,
                "valor_total_inventario": 0.0,
                "vidrios_por_tipo": [],
            }

    def obtener_vidrio_por_id(self, vidrio_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene un vidrio por su ID desde tabla consolidada.

        Args:
            vidrio_id: ID del vidrio (producto)

        Returns:
            Dict con los datos del vidrio o None si no existe
        """
        if not self.db_connection:
            return None

        try:
            cursor = self.db_connection.cursor()
            tabla_productos = self._validate_table_name(self.tabla_productos)

            if tabla_productos == "productos":
                cursor.execute("""
                    SELECT * FROM productos 
                    WHERE id = ? AND categoria = 'VIDRIO' AND activo = 1
                """, (vidrio_id,))
            else:
                cursor.execute("""
                    SELECT * FROM vidrios 
                    WHERE id = ? AND estado = 'ACTIVO'
                """, (vidrio_id,))

            row = cursor.fetchone()
            if row:
                columns = [desc[0] for desc in cursor.description]
                vidrio = dict(zip(columns, row))
                
                # Extraer propiedades específicas si es tabla consolidada
                if tabla_productos == "productos":
                    vidrio = self._extraer_propiedades_vidrio(vidrio)
                
                return vidrio
            return None

        except Exception as e:
            print(f"[ERROR VIDRIOS] Error obteniendo vidrio por ID: {e}")
            return None

    def obtener_proveedores(self) -> List[str]:
        """
        Obtiene la lista de proveedores únicos de vidrios.

        Returns:
            Lista de nombres de proveedores
        """
        if not self.db_connection:
            return ["Cristales Modernos", "Vidrios Industriales", "Distribuidora Central"]

        try:
            cursor = self.db_connection.cursor()
            tabla_productos = self._validate_table_name(self.tabla_productos)

            if tabla_productos == "productos":
                cursor.execute("""
                    SELECT DISTINCT proveedor 
                    FROM productos 
                    WHERE categoria = 'VIDRIO' AND estado = 'ACTIVO' AND activo = 1
                    AND proveedor IS NOT NULL AND proveedor != ''
                    ORDER BY proveedor
                """)
            else:
                cursor.execute("""
                    SELECT DISTINCT proveedor 
                    FROM vidrios 
                    WHERE estado = 'ACTIVO' AND proveedor IS NOT NULL
                    ORDER BY proveedor
                """)

            return [row[0] for row in cursor.fetchall()]

        except Exception as e:
            print(f"[ERROR VIDRIOS] Error obteniendo proveedores: {e}")
            return []

    def actualizar_stock(self, vidrio_id: int, nuevo_stock: int, 
                        tipo_movimiento: str = "AJUSTE_POSITIVO") -> Tuple[bool, str]:
        """
        Actualiza el stock de un vidrio usando sistema consolidado.

        Args:
            vidrio_id: ID del vidrio (producto)
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
                WHERE id = ? AND categoria = 'VIDRIO'
            """, (vidrio_id,))
            
            row = cursor.fetchone()
            if not row:
                return False, "Vidrio no encontrado"

            stock_anterior = row[0]
            diferencia = nuevo_stock - stock_anterior

            if diferencia != 0:
                # Registrar movimiento
                self._registrar_movimiento_consolidado(
                    vidrio_id, 
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
            """, (nuevo_stock, vidrio_id))

            self.db_connection.commit()
            return True, "Stock de vidrio actualizado exitosamente"

        except Exception as e:
            print(f"[ERROR VIDRIOS] Error actualizando stock: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return False, f"Error actualizando stock: {str(e)}"

    def _get_vidrios_demo(self) -> List[Dict[str, Any]]:
        """Datos demo consolidados para vidrios."""
        return [
            {
                "id": 1,
                "codigo": "VID001",
                "descripcion": "Vidrio Templado 6mm Transparente",
                "categoria": "VIDRIO",
                "subcategoria": "TEMPLADO",
                "tipo": "Seguridad",
                "stock_actual": 25,
                "stock_minimo": 10,
                "stock_maximo": 50,
                "stock_reservado": 5,
                "stock_disponible": 20,
                "precio_unitario": 45.00,
                "precio_promedio": 45.00,
                "costo_unitario": 31.50,
                "unidad_medida": "M2",
                "ubicacion": "Bodega B-2",
                "color": "Transparente",
                "material": "Vidrio",
                "marca": "CristalMax",
                "modelo": "CM-T6",
                "acabado": "Templado",
                "proveedor": "Cristales Modernos",
                "codigo_proveedor": "CM-002",
                "tiempo_entrega_dias": 15,
                "observaciones": "Vidrio para puertas principales",
                "codigo_qr": "QR-VID001",
                "imagen_url": "",
                "estado": "ACTIVO",
                "activo": True,
                "fecha_creacion": "2024-01-16",
                "fecha_actualizacion": "2024-01-16",
                "usuario_creacion": "admin",
                "usuario_modificacion": "admin",
                "estado_stock": "NORMAL",
                "espesor": 6,
                "templado": True,
                "laminado": False,
                "dvh": False,
                "tratamiento": "Templado",
                "dimensiones_disponibles": "2.0x3.0m, 1.5x2.5m"
            },
            {
                "id": 2,
                "codigo": "VID002",
                "descripcion": "Vidrio Laminado 8mm Bronce",
                "categoria": "VIDRIO",
                "subcategoria": "LAMINADO",
                "tipo": "Seguridad",
                "stock_actual": 15,
                "stock_minimo": 8,
                "stock_maximo": 40,
                "stock_reservado": 3,
                "stock_disponible": 12,
                "precio_unitario": 62.50,
                "precio_promedio": 62.50,
                "costo_unitario": 43.75,
                "unidad_medida": "M2",
                "ubicacion": "Bodega B-3",
                "color": "Bronce",
                "material": "Vidrio",
                "marca": "SecureGlass",
                "modelo": "SG-L8",
                "acabado": "Laminado",
                "proveedor": "Vidrios Industriales",
                "codigo_proveedor": "VI-003",
                "tiempo_entrega_dias": 20,
                "observaciones": "Vidrio de seguridad para fachadas",
                "codigo_qr": "QR-VID002",
                "imagen_url": "",
                "estado": "ACTIVO",
                "activo": True,
                "fecha_creacion": "2024-01-17",
                "fecha_actualizacion": "2024-01-17",
                "usuario_creacion": "admin",
                "usuario_modificacion": "admin",
                "estado_stock": "NORMAL",
                "espesor": 8,
                "templado": False,
                "laminado": True,
                "dvh": False,
                "tratamiento": "Laminado PVB",
                "dimensiones_disponibles": "2.5x3.5m, 2.0x3.0m"
            },
            {
                "id": 3,
                "codigo": "VID003",
                "descripcion": "DVH 4+9+4mm Low-E",
                "categoria": "VIDRIO",
                "subcategoria": "DVH",
                "tipo": "Aislante",
                "stock_actual": 5,
                "stock_minimo": 12,
                "stock_maximo": 30,
                "stock_reservado": 0,
                "stock_disponible": 5,
                "precio_unitario": 95.00,
                "precio_promedio": 95.00,
                "costo_unitario": 66.50,
                "unidad_medida": "M2",
                "ubicacion": "Bodega B-1",
                "color": "Transparente",
                "material": "Vidrio",
                "marca": "ThermalMax",
                "modelo": "TM-DVH17",
                "acabado": "DVH Low-E",
                "proveedor": "Cristales Térmicos",
                "codigo_proveedor": "CT-004",
                "tiempo_entrega_dias": 25,
                "observaciones": "Stock bajo - DVH especial",
                "codigo_qr": "QR-VID003",
                "imagen_url": "",
                "estado": "ACTIVO",
                "activo": True,
                "fecha_creacion": "2024-01-18",
                "fecha_actualizacion": "2024-01-18",
                "usuario_creacion": "admin",
                "usuario_modificacion": "admin",
                "estado_stock": "CRÍTICO",
                "espesor": 17,
                "templado": False,
                "laminado": False,
                "dvh": True,
                "tratamiento": "Low-E + Argón",
                "dimensiones_disponibles": "1.5x2.0m, 1.2x1.8m"
            }
        ]