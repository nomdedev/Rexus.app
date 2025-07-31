"""
Modelo de Inventario Consolidado

Actualizado para usar la nueva estructura de base de datos consolidada:
- Tabla principal: productos (reemplaza inventario_perfiles, herrajes, vidrios)
- Movimientos: movimientos_inventario (unificado)
- Asignaciones obra: productos_obra (unificado)
"""

import datetime
from io import BytesIO
from typing import Any, Dict, List
import qrcode
from PIL import Image


class InventarioModel:
    """Modelo para gestionar el inventario de productos consolidado."""

    def __init__(self, db_connection=None):
        """
        Inicializa el modelo de inventario consolidado.

        Args:
            db_connection: Conexión a la base de datos
        """
        self.db_connection = db_connection
        
        # Usar nuevas tablas consolidadas
        self.tabla_productos = "productos"
        self.tabla_movimientos = "movimientos_inventario"
        self.tabla_productos_obra = "productos_obra"
        
        # Lista de tablas permitidas para prevenir SQL injection
        self._allowed_tables = {
            "productos", "movimientos_inventario", "productos_obra", 
            "pedidos_consolidado", "pedidos_detalle_consolidado"
        }
        
        if not self.db_connection:
            print("[ERROR INVENTARIO] No hay conexión a la base de datos. El módulo no funcionará correctamente.")
        
        self._verificar_tablas()

    def _validate_table_name(self, table_name: str) -> str:
        """Valida que el nombre de tabla esté en la lista permitida."""
        if table_name in self._allowed_tables:
            return table_name
        raise ValueError(f"Table name '{table_name}' not allowed. Only {self._allowed_tables} are permitted.")

    def _verificar_tablas(self):
        """Verifica que las tablas consolidadas necesarias existan en la base de datos."""
        if not self.db_connection:
            return

        try:
            cursor = self.db_connection.cursor()

            # Verificar tabla principal productos (crítica)
            cursor.execute(
                "SELECT * FROM sysobjects WHERE name=? AND xtype='U'",
                (self.tabla_productos,),
            )
            if cursor.fetchone():
                print(f"[INVENTARIO] Tabla consolidada '{self.tabla_productos}' verificada correctamente.")
            else:
                print(f"[ADVERTENCIA] Tabla consolidada '{self.tabla_productos}' no existe. Usando tabla legacy.")
                # Fallback a tabla legacy
                self.tabla_productos = "inventario_perfiles"
                self._allowed_tables.add("inventario_perfiles")

            # Verificar tabla de movimientos
            cursor.execute(
                "SELECT * FROM sysobjects WHERE name=? AND xtype='U'",
                (self.tabla_movimientos,),
            )
            if cursor.fetchone():
                print(f"[INVENTARIO] Tabla '{self.tabla_movimientos}' verificada correctamente.")
            else:
                print(f"[ADVERTENCIA] Tabla '{self.tabla_movimientos}' no existe. Usando historial legacy.")
                self.tabla_movimientos = "historial"
                self._allowed_tables.add("historial")

            # Verificar tabla productos_obra
            cursor.execute(
                "SELECT * FROM sysobjects WHERE name=? AND xtype='U'",
                (self.tabla_productos_obra,),
            )
            if cursor.fetchone():
                print(f"[INVENTARIO] Tabla '{self.tabla_productos_obra}' verificada correctamente.")
            else:
                print(f"[ADVERTENCIA] Tabla '{self.tabla_productos_obra}' no existe. Funcionalidad limitada.")

            print(f"[INVENTARIO] Verificación de tablas consolidadas completada.")
            
        except Exception as e:
            print(f"[ERROR INVENTARIO] Error verificando tablas: {e}")
            raise

    def obtener_todos_productos(self, filtros=None):
        """
        Obtiene todos los productos desde la tabla productos consolidada.

        Args:
            filtros (dict): Filtros opcionales (categoria, estado, stock_bajo)

        Returns:
            List[Dict]: Lista de productos
        """
        if not self.db_connection:
            return self._get_productos_demo()

        try:
            cursor = self.db_connection.cursor()
            tabla_productos = self._validate_table_name(self.tabla_productos)
            
            # Query base para tabla consolidada
            if tabla_productos == "productos":
                query = """
                SELECT 
                    id, codigo, descripcion, categoria, subcategoria, tipo,
                    stock_actual, stock_minimo, stock_maximo, stock_reservado,
                    stock_disponible, precio_unitario, precio_promedio, costo_unitario,
                    unidad_medida, ubicacion, color, material, marca, modelo, acabado,
                    proveedor, codigo_proveedor, observaciones, codigo_qr, imagen_url,
                    estado, activo, fecha_creacion, fecha_actualizacion,
                    usuario_creacion, usuario_modificacion
                FROM productos
                WHERE activo = 1
                """
            else:
                # Fallback para tabla legacy
                query = """
                SELECT 
                    id, codigo, descripcion, tipo as categoria, acabado as subcategoria, '' as tipo,
                    stock_actual, stock_minimo, stock_maximo, 0 as stock_reservado,
                    stock_actual as stock_disponible, precio_unitario, precio_unitario as precio_promedio, 
                    precio_unitario * 0.7 as costo_unitario,
                    unidad_medida, ubicacion, color, '' as material, marca, '' as modelo, acabado,
                    proveedor, '' as codigo_proveedor, observaciones, codigo_qr, '' as imagen_url,
                    'ACTIVO' as estado, activo, fecha_creacion, fecha_modificacion,
                    usuario_creacion, usuario_modificacion
                FROM inventario_perfiles
                WHERE activo = 1
                """

            params = []
            where_clauses = []

            if filtros:
                if filtros.get("categoria"):
                    where_clauses.append("categoria = ?")
                    params.append(filtros["categoria"])
                
                if filtros.get("estado"):
                    where_clauses.append("estado = ?")
                    params.append(filtros["estado"])
                
                if filtros.get("stock_bajo"):
                    where_clauses.append("stock_actual <= stock_minimo")
                
                if filtros.get("busqueda"):
                    where_clauses.append("(descripcion LIKE ? OR codigo LIKE ?)")
                    busqueda = f"%{filtros['busqueda']}%"
                    params.extend([busqueda, busqueda])

            if where_clauses:
                query += " AND " + " AND ".join(where_clauses)

            query += " ORDER BY codigo"

            cursor.execute(query, params)
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]

            productos = []
            for row in rows:
                producto = dict(zip(columns, row))
                producto["estado_stock"] = self._determinar_estado_stock(producto)
                productos.append(producto)

            return productos

        except Exception as e:
            print(f"[ERROR INVENTARIO] Error obteniendo productos: {e}")
            return self._get_productos_demo()

    def _determinar_estado_stock(self, producto):
        """Determina el estado del stock (OK, BAJO, CRÍTICO, AGOTADO)."""
        stock_actual = float(producto.get("stock_actual", 0))
        stock_minimo = float(producto.get("stock_minimo", 0))

        if stock_actual <= 0:
            return "AGOTADO"
        elif stock_actual <= stock_minimo:
            return "CRÍTICO"
        elif stock_actual <= stock_minimo * 1.5:
            return "BAJO"
        else:
            return "OK"

    def obtener_producto_por_id(self, producto_id):
        """Obtiene un producto específico por ID desde tabla consolidada."""
        if not self.db_connection:
            return None

        try:
            cursor = self.db_connection.cursor()
            tabla_productos = self._validate_table_name(self.tabla_productos)

            if tabla_productos == "productos":
                sql_select = """
                SELECT * FROM productos WHERE id = ? AND activo = 1
                """
            else:
                sql_select = """
                SELECT * FROM inventario_perfiles WHERE id = ? AND activo = 1
                """

            cursor.execute(sql_select, (producto_id,))
            row = cursor.fetchone()

            if row:
                columns = [desc[0] for desc in cursor.description]
                return dict(zip(columns, row))

            return None

        except Exception as e:
            print(f"[ERROR INVENTARIO] Error obteniendo producto {producto_id}: {e}")
            return None

    def crear_producto(self, datos_producto, usuario="SISTEMA"):
        """
        Crea un nuevo producto en la tabla productos consolidada.

        Args:
            datos_producto (dict): Datos del producto
            usuario (str): Usuario que crea el producto

        Returns:
            int: ID del producto creado o None si hay error
        """
        if not self.db_connection:
            return None

        try:
            cursor = self.db_connection.cursor()
            tabla_productos = self._validate_table_name(self.tabla_productos)

            # Verificar que el código no exista
            if self.obtener_producto_por_codigo(datos_producto.get("codigo")):
                raise Exception(f"Ya existe un producto con código {datos_producto.get('codigo')}")

            # Generar código QR
            codigo_qr = self._generar_codigo_qr(datos_producto.get("codigo"))

            if tabla_productos == "productos":
                # Usar tabla consolidada
                sql_insert = """
                INSERT INTO productos
                (codigo, descripcion, categoria, subcategoria, tipo,
                 stock_actual, stock_minimo, stock_maximo, precio_unitario, costo_unitario,
                 unidad_medida, ubicacion, color, material, marca, modelo, acabado,
                 proveedor, codigo_proveedor, observaciones, codigo_qr, imagen_url,
                 estado, activo, usuario_creacion, fecha_creacion)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, GETDATE())
                """

                cursor.execute(sql_insert, (
                    datos_producto.get("codigo"),
                    datos_producto.get("descripcion"),
                    datos_producto.get("categoria", "MATERIAL"),
                    datos_producto.get("subcategoria", ""),
                    datos_producto.get("tipo", ""),
                    datos_producto.get("stock_actual", 0),
                    datos_producto.get("stock_minimo", 0),
                    datos_producto.get("stock_maximo", 1000),
                    datos_producto.get("precio_unitario", 0.00),
                    datos_producto.get("costo_unitario", 0.00),
                    datos_producto.get("unidad_medida", "UND"),
                    datos_producto.get("ubicacion", ""),
                    datos_producto.get("color", ""),
                    datos_producto.get("material", ""),
                    datos_producto.get("marca", ""),
                    datos_producto.get("modelo", ""),
                    datos_producto.get("acabado", ""),
                    datos_producto.get("proveedor", ""),
                    datos_producto.get("codigo_proveedor", ""),
                    datos_producto.get("observaciones", ""),
                    codigo_qr,
                    datos_producto.get("imagen_url", ""),
                    datos_producto.get("estado", "ACTIVO"),
                    usuario
                ))
            else:
                # Fallback tabla legacy
                sql_insert = """
                INSERT INTO inventario_perfiles
                (codigo, descripcion, tipo, acabado, stock_actual, stock_minimo,
                 stock_maximo, precio_unitario, ubicacion, proveedor, unidad_medida,
                 activo, usuario_creacion, observaciones, codigo_qr)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?, ?)
                """

                cursor.execute(sql_insert, (
                    datos_producto.get("codigo"),
                    datos_producto.get("descripcion"),
                    datos_producto.get("categoria", ""),
                    datos_producto.get("acabado", ""),
                    datos_producto.get("stock_actual", 0),
                    datos_producto.get("stock_minimo", 0),
                    datos_producto.get("stock_maximo", 1000),
                    datos_producto.get("precio_unitario", 0.00),
                    datos_producto.get("ubicacion", ""),
                    datos_producto.get("proveedor", ""),
                    datos_producto.get("unidad_medida", "UND"),
                    usuario,
                    datos_producto.get("observaciones", ""),
                    codigo_qr
                ))

            # Obtener ID del producto creado
            cursor.execute("SELECT @@IDENTITY")
            producto_id = cursor.fetchone()[0]

            self.db_connection.commit()

            # Registrar movimiento inicial si hay stock
            stock_inicial = datos_producto.get("stock_actual", 0)
            if stock_inicial > 0:
                self.registrar_movimiento(
                    producto_id=producto_id,
                    tipo_movimiento="ENTRADA",
                    cantidad=stock_inicial,
                    motivo="Stock inicial",
                    usuario=usuario
                )

            print(f"[INVENTARIO] Producto creado: {datos_producto.get('codigo')}")
            return producto_id

        except Exception as e:
            print(f"[ERROR INVENTARIO] Error creando producto: {e}")
            if self.db_connection:
                self.db_connection.connection.rollback()
            return None

    def registrar_movimiento(self, producto_id, tipo_movimiento, cantidad, motivo="", 
                           documento_referencia="", usuario="SISTEMA", obra_id=None):
        """
        Registra un movimiento de inventario usando el sistema consolidado.

        Args:
            producto_id (int): ID del producto
            tipo_movimiento (str): ENTRADA, SALIDA, AJUSTE_POSITIVO, AJUSTE_NEGATIVO, etc.
            cantidad (float): Cantidad del movimiento
            motivo (str): Motivo del movimiento
            documento_referencia (str): Documento de referencia
            usuario (str): Usuario que registra el movimiento
            obra_id (int): ID de obra si aplica

        Returns:
            bool: True si se registró exitosamente
        """
        if not self.db_connection:
            return False

        try:
            cursor = self.db_connection.cursor()
            tabla_movimientos = self._validate_table_name(self.tabla_movimientos)

            # Obtener producto y stock actual
            producto = self.obtener_producto_por_id(producto_id)
            if not producto:
                raise Exception("Producto no encontrado")

            stock_anterior = producto.get("stock_actual", 0)

            # Calcular nuevo stock según tipo de movimiento
            if tipo_movimiento in ["ENTRADA", "RECEPCION_COMPRA"]:
                stock_nuevo = stock_anterior + cantidad
            elif tipo_movimiento in ["SALIDA", "CONSUMO_OBRA"]:
                stock_nuevo = stock_anterior - cantidad
                if stock_nuevo < 0:
                    raise Exception("Stock insuficiente para la salida")
            elif tipo_movimiento == "AJUSTE_POSITIVO":
                stock_nuevo = stock_anterior + cantidad
            elif tipo_movimiento == "AJUSTE_NEGATIVO":
                stock_nuevo = stock_anterior - cantidad
                if stock_nuevo < 0:
                    raise Exception("El ajuste resultaría en stock negativo")
            else:
                raise Exception(f"Tipo de movimiento inválido: {tipo_movimiento}")

            if tabla_movimientos == "movimientos_inventario":
                # Usar tabla consolidada con procedimiento almacenado
                try:
                    cursor.execute("EXEC sp_registrar_movimiento ?, ?, ?, ?, ?, ?, ?", (
                        producto_id, tipo_movimiento, cantidad, motivo, 
                        documento_referencia, 1, obra_id  # TODO: obtener usuario_id real
                    ))
                    movimiento_id = cursor.fetchone()[0]
                    self.db_connection.commit()
                    print(f"[INVENTARIO] Movimiento registrado con ID: {movimiento_id}")
                    return True
                except Exception as proc_error:
                    print(f"[ADVERTENCIA] Error usando procedimiento, usando inserción manual: {proc_error}")
                    # Fallback a inserción manual
                    sql_insert = """
                    INSERT INTO movimientos_inventario
                    (producto_id, codigo_producto, descripcion_producto, categoria_producto,
                     tipo_movimiento, cantidad, unidad_medida, stock_anterior, stock_nuevo,
                     precio_unitario, documento_referencia, obra_id, motivo, observaciones,
                     usuario_movimiento, fecha_movimiento)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, GETDATE())
                    """

                    cursor.execute(sql_insert, (
                        producto_id,
                        producto.get("codigo", ""),
                        producto.get("descripcion", ""),
                        producto.get("categoria", ""),
                        tipo_movimiento,
                        cantidad,
                        producto.get("unidad_medida", "UND"),
                        stock_anterior,
                        stock_nuevo,
                        producto.get("precio_unitario", 0),
                        documento_referencia,
                        obra_id,
                        motivo,
                        f"Usuario: {usuario}",
                    ))
            else:
                # Fallback a tabla historial legacy
                cantidad_movimiento = cantidad if tipo_movimiento != "AJUSTE" else (stock_nuevo - stock_anterior)
                detalles = f"Producto ID: {producto_id}, {tipo_movimiento}: {cantidad_movimiento}, Stock anterior: {stock_anterior}, Stock nuevo: {stock_nuevo}, Motivo: {motivo}, Doc: {documento_referencia}"

                cursor.execute(
                    "INSERT INTO historial (accion, usuario, fecha, detalles) VALUES (?, ?, GETDATE(), ?)",
                    (f"INVENTARIO_{tipo_movimiento}", usuario, detalles)
                )

            # Actualizar stock en tabla productos
            tabla_productos = self._validate_table_name(self.tabla_productos)
            if tabla_productos == "productos":
                sql_update_stock = """
                UPDATE productos
                SET stock_actual = ?, fecha_ultimo_movimiento = GETDATE(), fecha_actualizacion = GETDATE()
                WHERE id = ?
                """
            else:
                sql_update_stock = """
                UPDATE inventario_perfiles
                SET stock_actual = ?, fecha_modificacion = GETDATE()
                WHERE id = ?
                """

            cursor.execute(sql_update_stock, (stock_nuevo, producto_id))

            self.db_connection.commit()
            print(f"[INVENTARIO] Movimiento registrado: {tipo_movimiento} - {cantidad}")
            return True

        except Exception as e:
            print(f"[ERROR INVENTARIO] Error registrando movimiento: {e}")
            if self.db_connection:
                self.db_connection.connection.rollback()
            return False

    def obtener_movimientos(self, producto_id=None, limite=100):
        """
        Obtiene el historial de movimientos desde el sistema consolidado.

        Args:
            producto_id (int): ID del producto específico (opcional)
            limite (int): Límite de registros

        Returns:
            List[Dict]: Lista de movimientos
        """
        if not self.db_connection:
            return []

        try:
            cursor = self.db_connection.cursor()
            tabla_movimientos = self._validate_table_name(self.tabla_movimientos)

            if tabla_movimientos == "movimientos_inventario":
                # Usar tabla consolidada
                sql_select = """
                SELECT 
                    id, producto_id, codigo_producto, descripcion_producto, categoria_producto,
                    tipo_movimiento, cantidad, unidad_medida, stock_anterior, stock_nuevo,
                    precio_unitario, documento_referencia, obra_id, motivo, observaciones,
                    usuario_movimiento, fecha_movimiento
                FROM movimientos_inventario
                WHERE activo = 1 AND estado = 'CONFIRMADO'
                """

                params = []
                if producto_id:
                    sql_select += " AND producto_id = ?"
                    params.append(producto_id)

                sql_select += f" ORDER BY fecha_movimiento DESC OFFSET 0 ROWS FETCH NEXT {limite} ROWS ONLY"

                cursor.execute(sql_select, params)
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]

                movimientos = []
                for row in rows:
                    movimiento = dict(zip(columns, row))
                    movimientos.append(movimiento)

                return movimientos

            else:
                # Fallback a tabla historial legacy
                sql_select = """
                SELECT id, accion, usuario, fecha, detalles
                FROM historial
                WHERE accion LIKE 'INVENTARIO_%'
                """

                params = []
                if producto_id:
                    sql_select += " AND detalles LIKE ?"
                    params.append(f"%Producto ID: {producto_id}%")

                sql_select += f" ORDER BY fecha DESC OFFSET 0 ROWS FETCH NEXT {limite} ROWS ONLY"

                cursor.execute(sql_select, params)
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]

                movimientos = []
                for row in rows:
                    movimiento = dict(zip(columns, row))
                    movimiento["tipo_movimiento"] = movimiento["accion"].replace("INVENTARIO_", "")
                    movimientos.append(movimiento)

                return movimientos

        except Exception as e:
            print(f"[ERROR INVENTARIO] Error obteniendo movimientos: {e}")
            return []

    def obtener_categorias(self):
        """Obtiene todas las categorías de productos desde tabla consolidada."""
        if not self.db_connection:
            return ["PERFIL", "HERRAJE", "VIDRIO", "MATERIAL"]

        try:
            cursor = self.db_connection.cursor()
            tabla_productos = self._validate_table_name(self.tabla_productos)

            if tabla_productos == "productos":
                sql_select = """
                SELECT DISTINCT categoria FROM productos
                WHERE categoria IS NOT NULL AND categoria != '' AND activo = 1
                ORDER BY categoria
                """
            else:
                sql_select = """
                SELECT DISTINCT tipo FROM inventario_perfiles
                WHERE tipo IS NOT NULL AND tipo != '' AND activo = 1
                ORDER BY tipo
                """

            cursor.execute(sql_select)
            rows = cursor.fetchall()

            return [row[0] for row in rows]

        except Exception as e:
            print(f"[ERROR INVENTARIO] Error obteniendo categorías: {e}")
            return ["PERFIL", "HERRAJE", "VIDRIO", "MATERIAL"]

    def buscar_productos(self, filtros):
        """
        Busca productos según los filtros especificados usando tabla consolidada.
        
        Args:
            filtros (dict): Filtros de búsqueda
            
        Returns:
            List[Dict]: Lista de productos encontrados
        """
        return self.obtener_todos_productos(filtros)

    def filtrar_inventario_tiempo_real(self, texto_busqueda=""):
        """
        Filtra el inventario en tiempo real mientras el usuario escribe.
        
        Args:
            texto_busqueda (str): Texto a buscar
            
        Returns:
            List[Dict]: Lista de productos filtrados
        """
        filtros = {"busqueda": texto_busqueda} if texto_busqueda else {}
        return self.obtener_todos_productos(filtros)

    def cargar_inventario(self):
        """Carga el inventario completo en la vista."""
        try:
            print("[INVENTARIO CONTROLLER] Iniciando carga completa de inventario consolidado...")
            productos = self.obtener_todos_productos()
            print(f"[INVENTARIO CONTROLLER] Inventario consolidado cargado: {len(productos)} productos")
            return productos
        except Exception as e:
            print(f"[INVENTARIO CONTROLLER] Error en cargar_inventario: {e}")
            return []

    def obtener_producto_por_codigo(self, codigo):
        """Obtiene un producto específico por código desde tabla consolidada."""
        if not self.db_connection:
            return None

        try:
            cursor = self.db_connection.cursor()
            tabla_productos = self._validate_table_name(self.tabla_productos)

            if tabla_productos == "productos":
                sql_select = """
                SELECT * FROM productos WHERE codigo = ? AND activo = 1
                """
            else:
                sql_select = """
                SELECT * FROM inventario_perfiles WHERE codigo = ? AND activo = 1
                """

            cursor.execute(sql_select, (codigo,))
            row = cursor.fetchone()

            if row:
                columns = [desc[0] for desc in cursor.description]
                return dict(zip(columns, row))

            return None

        except Exception as e:
            print(f"[ERROR INVENTARIO] Error obteniendo producto por código: {e}")
            return None

    def obtener_estadisticas_inventario(self):
        """Obtiene estadísticas generales del inventario consolidado."""
        if not self.db_connection:
            return {
                "total_productos": 4,
                "stock_bajo": 1,
                "valor_total": 2500.0,
                "movimientos_mes": 15
            }

        try:
            cursor = self.db_connection.cursor()
            tabla_productos = self._validate_table_name(self.tabla_productos)

            if tabla_productos == "productos":
                # Usar vista estadística si existe
                try:
                    cursor.execute("SELECT * FROM v_estadisticas_productos")
                    rows = cursor.fetchall()
                    if rows:
                        # Agregar estadísticas de todas las categorías
                        total_productos = sum(row[1] for row in rows)  # total_productos por categoría
                        total_activos = sum(row[2] for row in rows)    # activos por categoría
                        stock_bajo = sum(row[3] for row in rows)       # con_stock_bajo por categoría
                        valor_total = sum(row[5] for row in rows)      # valor_inventario_categoria
                        
                        return {
                            "total_productos": total_productos,
                            "productos_activos": total_activos,
                            "stock_bajo": stock_bajo,
                            "valor_total": float(valor_total)
                        }
                except:
                    pass  # Fallback a consultas manuales

                # Consultas manuales para tabla productos
                cursor.execute("SELECT COUNT(*) FROM productos WHERE activo = 1")
                total_productos = cursor.fetchone()[0]

                cursor.execute("""
                    SELECT COUNT(*) FROM productos
                    WHERE stock_actual <= stock_minimo AND activo = 1
                """)
                stock_bajo = cursor.fetchone()[0]

                cursor.execute("""
                    SELECT SUM(stock_actual * precio_unitario) FROM productos
                    WHERE activo = 1
                """)
                valor_total = cursor.fetchone()[0] or 0

            else:
                # Fallback tabla legacy
                cursor.execute("SELECT COUNT(*) FROM inventario_perfiles WHERE activo = 1")
                total_productos = cursor.fetchone()[0]

                cursor.execute("""
                    SELECT COUNT(*) FROM inventario_perfiles
                    WHERE stock_actual <= stock_minimo AND activo = 1
                """)
                stock_bajo = cursor.fetchone()[0]

                cursor.execute("""
                    SELECT SUM(stock_actual * ISNULL(precio_unitario, 0)) FROM inventario_perfiles
                    WHERE activo = 1
                """)
                valor_total = cursor.fetchone()[0] or 0

            # Movimientos del mes desde tabla consolidada
            tabla_movimientos = self._validate_table_name(self.tabla_movimientos)
            if tabla_movimientos == "movimientos_inventario":
                cursor.execute("""
                    SELECT COUNT(*) FROM movimientos_inventario
                    WHERE MONTH(fecha_movimiento) = MONTH(GETDATE())
                      AND YEAR(fecha_movimiento) = YEAR(GETDATE())
                      AND activo = 1
                """)
            else:
                cursor.execute("""
                    SELECT COUNT(*) FROM historial
                    WHERE accion LIKE 'INVENTARIO_%'
                      AND MONTH(fecha) = MONTH(GETDATE())
                      AND YEAR(fecha) = YEAR(GETDATE())
                """)
            
            movimientos_mes = cursor.fetchone()[0]

            return {
                "total_productos": total_productos,
                "stock_bajo": stock_bajo,
                "valor_total": float(valor_total),
                "movimientos_mes": movimientos_mes
            }

        except Exception as e:
            print(f"[ERROR INVENTARIO] Error obteniendo estadísticas: {e}")
            return {
                "total_productos": 0,
                "stock_bajo": 0,
                "valor_total": 0.0,
                "movimientos_mes": 0
            }

    def _generar_codigo_qr(self, codigo):
        """
        Genera un código QR para el producto.

        Args:
            codigo (str): Código del producto

        Returns:
            str: Nombre del archivo QR generado
        """
        try:
            # Crear directorio para QR si no existe
            import os

            qr_dir = "qr_codes"
            os.makedirs(qr_dir, exist_ok=True)

            # Generar QR
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(codigo)
            qr.make(fit=True)

            # Crear imagen
            img = qr.make_image(fill_color="black", back_color="white")

            # Guardar archivo
            filename = f"qr_{codigo}.png"
            filepath = os.path.join(qr_dir, filename)
            img.save(filepath)

            return filename

        except Exception as e:
            print(f"[ERROR INVENTARIO] Error generando QR: {e}")
            return ""

    def _get_productos_demo(self):
        """Datos demo consolidados para cuando no hay conexión a base de datos."""
        return [
            {
                "id": 1,
                "codigo": "PERF001",
                "descripcion": "Perfil de Aluminio 20x20",
                "categoria": "PERFIL",
                "subcategoria": "Aluminio",
                "tipo": "Estructural",
                "stock_actual": 150,
                "stock_minimo": 50,
                "stock_maximo": 200,
                "stock_reservado": 30,
                "stock_disponible": 120,
                "precio_unitario": 25.50,
                "precio_promedio": 25.50,
                "costo_unitario": 18.00,
                "unidad_medida": "MT",
                "ubicacion": "Bodega A-1",
                "color": "Natural",
                "material": "Aluminio",
                "marca": "AlumTech",
                "modelo": "AT-2020",
                "acabado": "Anodizado",
                "proveedor": "Aluminios del Valle",
                "codigo_proveedor": "ADV-001",
                "observaciones": "Perfil estándar para ventanas",
                "codigo_qr": "QR001",
                "imagen_url": "",
                "estado": "ACTIVO",
                "activo": True,
                "fecha_creacion": "2024-01-15",
                "fecha_actualizacion": "2024-01-15",
                "usuario_creacion": "admin",
                "usuario_modificacion": "admin",
                "estado_stock": "NORMAL"
            },
            {
                "id": 2,
                "codigo": "VID001",
                "descripcion": "Vidrio Templado 6mm",
                "categoria": "VIDRIO",
                "subcategoria": "Templado",
                "tipo": "Seguridad",
                "stock_actual": 25,
                "stock_minimo": 10,
                "stock_maximo": 50,
                "stock_reservado": 5,
                "stock_disponible": 20,
                "precio_unitario": 45.00,
                "precio_promedio": 45.00,
                "costo_unitario": 32.00,
                "unidad_medida": "M2",
                "ubicacion": "Bodega B-2",
                "color": "Transparente",
                "material": "Vidrio",
                "marca": "CristalMax",
                "modelo": "CM-T6",
                "acabado": "Templado",
                "proveedor": "Cristales Modernos",
                "codigo_proveedor": "CM-002",
                "observaciones": "Vidrio para puertas",
                "codigo_qr": "QR002",
                "imagen_url": "",
                "estado": "ACTIVO",
                "activo": True,
                "fecha_creacion": "2024-01-16",
                "fecha_actualizacion": "2024-01-16",
                "usuario_creacion": "admin",
                "usuario_modificacion": "admin",
                "estado_stock": "NORMAL"
            },
            {
                "id": 3,
                "codigo": "HERR001",
                "descripcion": "Bisagra Pesada 4x4",
                "categoria": "HERRAJE",
                "subcategoria": "Bisagras",
                "tipo": "Estructural",
                "stock_actual": 8,
                "stock_minimo": 20,
                "stock_maximo": 100,
                "stock_reservado": 0,
                "stock_disponible": 8,
                "precio_unitario": 15.75,
                "precio_promedio": 15.75,
                "costo_unitario": 9.50,
                "unidad_medida": "UND",
                "ubicacion": "Bodega C-1",
                "color": "Negro",
                "material": "Acero",
                "marca": "HerrajeTech",
                "modelo": "HT-BP44",
                "acabado": "Pintado",
                "proveedor": "Herrajes Industriales",
                "codigo_proveedor": "HI-003",
                "observaciones": "Stock bajo - reponer",
                "codigo_qr": "QR003",
                "imagen_url": "",
                "estado": "ACTIVO",
                "activo": True,
                "fecha_creacion": "2024-01-17",
                "fecha_actualizacion": "2024-01-17",
                "usuario_creacion": "admin",
                "usuario_modificacion": "admin",
                "estado_stock": "CRÍTICO"
            },
            {
                "id": 4,
                "codigo": "MAT001",
                "descripcion": "Sellante Silicona Transparente",
                "categoria": "MATERIAL",
                "subcategoria": "Sellantes",
                "tipo": "Silicona",
                "stock_actual": 0,
                "stock_minimo": 5,
                "stock_maximo": 30,
                "stock_reservado": 0,
                "stock_disponible": 0,
                "precio_unitario": 8.50,
                "precio_promedio": 8.50,
                "costo_unitario": 5.20,
                "unidad_medida": "UND",
                "ubicacion": "Bodega D-1",
                "color": "Transparente",
                "material": "Silicona",
                "marca": "SellMax",
                "modelo": "SM-T310",
                "acabado": "Transparente",
                "proveedor": "Químicos Especiales",
                "codigo_proveedor": "QE-004",
                "observaciones": "Agotado - pedido urgente",
                "codigo_qr": "QR004",
                "imagen_url": "",
                "estado": "ACTIVO",
                "activo": True,
                "fecha_creacion": "2024-01-18",
                "fecha_actualizacion": "2024-01-18",
                "usuario_creacion": "admin",
                "usuario_modificacion": "admin",
                "estado_stock": "AGOTADO"
            }
        ]