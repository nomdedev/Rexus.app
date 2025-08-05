"""
Modelo de Detalle de Compras

Maneja los detalles de productos/items en las órdenes de compra.
"""

from typing import Any, Dict, List
from rexus.utils.security import SecurityUtils


class DetalleComprasModel:
    """Modelo para gestionar los detalles de las compras."""

    def __init__(self, db_connection=None):
        """
        Inicializa el modelo de detalle de compras.

        Args:
            db_connection: Conexión a la base de datos
        """
        self.db_connection = db_connection
        self.tabla_detalle = "detalle_compras"
        self._crear_tabla_si_no_existe()

    def _crear_tabla_si_no_existe(self):
        """Verifica que la tabla de detalle de compras exista."""
        if not self.db_connection:
            return

        try:
            cursor = self.db_connection.cursor()
            cursor.execute(
                "SELECT * FROM sysobjects WHERE name=? AND xtype='U'",
                (self.tabla_detalle,),
            )
            if cursor.fetchone():
                print(f"[DETALLE COMPRAS] Tabla '{self.tabla_detalle}' verificada.")
            else:
                print(f"[ADVERTENCIA] La tabla '{self.tabla_detalle}' no existe.")

        except Exception as e:
            print(f"[ERROR DETALLE COMPRAS] Error verificando tabla: {e}")

    def agregar_item_compra(
        self,
        compra_id: int,
        descripcion: str,
        categoria: str = "",
        cantidad: int = 1,
        precio_unitario: float = 0.0,
        unidad: str = "UN",
        observaciones: str = "",
        usuario_creacion: str = ""
    ) -> bool:
        """
        Agrega un item/producto a una orden de compra.

        Args:
            compra_id: ID de la orden de compra
            descripcion: Descripción del producto
            categoria: Categoría del producto
            cantidad: Cantidad solicitada
            precio_unitario: Precio unitario
            unidad: Unidad de medida
            observaciones: Observaciones adicionales
            usuario_creacion: Usuario que agrega el item

        Returns:
            bool: True si se agregó exitosamente
        """
        if not self.db_connection:
            print("[WARN DETALLE COMPRAS] Sin conexión BD")
            return False

        try:
            # Sanitizar datos de entrada
            descripcion_sanitizada = SecurityUtils.sanitize_sql_input(descripcion)
            categoria_sanitizada = SecurityUtils.sanitize_sql_input(categoria)
            unidad_sanitizada = SecurityUtils.sanitize_sql_input(unidad)
            observaciones_sanitizadas = SecurityUtils.sanitize_sql_input(observaciones)
            usuario_sanitizado = SecurityUtils.sanitize_sql_input(usuario_creacion)

            cursor = self.db_connection.cursor()

            sql_insert = """
            INSERT INTO detalle_compras
            (compra_id, descripcion, categoria, cantidad, precio_unitario, 
             unidad, observaciones, usuario_creacion, fecha_creacion)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, GETDATE())
            """

            cursor.execute(
                sql_insert,
                (
                    compra_id,
                    descripcion_sanitizada,
                    categoria_sanitizada,
                    cantidad,
                    precio_unitario,
                    unidad_sanitizada,
                    observaciones_sanitizadas,
                    usuario_sanitizado,
                ),
            )

            self.db_connection.commit()
            print(f"[DETALLE COMPRAS] Item agregado a compra {compra_id}: {descripcion}")
            return True

        except Exception as e:
            print(f"[ERROR DETALLE COMPRAS] Error agregando item: {e}")
            return False

    def obtener_items_compra(self, compra_id: int) -> List[Dict]:
        """
        Obtiene todos los items de una orden de compra.

        Args:
            compra_id: ID de la orden de compra

        Returns:
            List[Dict]: Lista de items de la compra
        """
        if not self.db_connection:
            return self._get_items_demo(compra_id)

        try:
            cursor = self.db_connection.cursor()

            sql_select = """
            SELECT 
                id, compra_id, descripcion, categoria, cantidad, 
                precio_unitario, unidad, observaciones, usuario_creacion,
                fecha_creacion,
                (cantidad * precio_unitario) as subtotal
            FROM detalle_compras
            WHERE compra_id = ?
            ORDER BY fecha_creacion ASC
            """

            cursor.execute(sql_select, (compra_id,))
            rows = cursor.fetchall()

            # Convertir a lista de diccionarios
            columns = [desc[0] for desc in cursor.description]
            items = []

            for row in rows:
                item = dict(zip(columns, row))
                items.append(item)

            print(f"[DETALLE COMPRAS] Obtenidos {len(items)} items para compra {compra_id}")
            return items

        except Exception as e:
            print(f"[ERROR DETALLE COMPRAS] Error obteniendo items: {e}")
            return self._get_items_demo(compra_id)

    def actualizar_item_compra(
        self,
        item_id: int,
        descripcion: str = None,
        categoria: str = None,
        cantidad: int = None,
        precio_unitario: float = None,
        unidad: str = None,
        observaciones: str = None
    ) -> bool:
        """
        Actualiza un item de compra existente.

        Args:
            item_id: ID del item
            descripcion: Nueva descripción (opcional)
            categoria: Nueva categoría (opcional)
            cantidad: Nueva cantidad (opcional)
            precio_unitario: Nuevo precio (opcional)
            unidad: Nueva unidad (opcional)
            observaciones: Nuevas observaciones (opcional)

        Returns:
            bool: True si se actualizó exitosamente
        """
        if not self.db_connection:
            return False

        try:
            cursor = self.db_connection.cursor()

            # Construir query dinámico solo con campos a actualizar
            updates = []
            params = []

            if descripcion is not None:
                updates.append("descripcion = ?")
                params.append(SecurityUtils.sanitize_sql_input(descripcion))

            if categoria is not None:
                updates.append("categoria = ?")
                params.append(SecurityUtils.sanitize_sql_input(categoria))

            if cantidad is not None:
                updates.append("cantidad = ?")
                params.append(cantidad)

            if precio_unitario is not None:
                updates.append("precio_unitario = ?")
                params.append(precio_unitario)

            if unidad is not None:
                updates.append("unidad = ?")
                params.append(SecurityUtils.sanitize_sql_input(unidad))

            if observaciones is not None:
                updates.append("observaciones = ?")
                params.append(SecurityUtils.sanitize_sql_input(observaciones))

            if not updates:
                return False

            updates.append("fecha_actualizacion = GETDATE()")
            params.append(item_id)

            sql_update = f"""
            UPDATE detalle_compras 
            SET {', '.join(updates)}
            WHERE id = ?
            """

            cursor.execute(sql_update, params)
            self.db_connection.commit()

            print(f"[DETALLE COMPRAS] Item {item_id} actualizado")
            return True

        except Exception as e:
            print(f"[ERROR DETALLE COMPRAS] Error actualizando item: {e}")
            return False

    def eliminar_item_compra(self, item_id: int) -> bool:
        """
        Elimina un item de una compra.

        Args:
            item_id: ID del item a eliminar

        Returns:
            bool: True si se eliminó exitosamente
        """
        if not self.db_connection:
            return False

        try:
            cursor = self.db_connection.cursor()

            sql_delete = "DELETE FROM detalle_compras WHERE id = ?"
            cursor.execute(sql_delete, (item_id,))
            self.db_connection.commit()

            print(f"[DETALLE COMPRAS] Item {item_id} eliminado")
            return True

        except Exception as e:
            print(f"[ERROR DETALLE COMPRAS] Error eliminando item: {e}")
            return False

    def obtener_resumen_compra(self, compra_id: int) -> Dict[str, Any]:
        """
        Obtiene un resumen financiero de una orden de compra.

        Args:
            compra_id: ID de la orden de compra

        Returns:
            Dict: Resumen con totales y estadísticas
        """
        if not self.db_connection:
            return self._get_resumen_demo(compra_id)

        try:
            cursor = self.db_connection.cursor()

            # Obtener resumen de items
            sql_resumen = """
            SELECT 
                COUNT(*) as total_items,
                SUM(cantidad) as total_cantidad,
                SUM(cantidad * precio_unitario) as subtotal,
                AVG(precio_unitario) as precio_promedio,
                MIN(precio_unitario) as precio_minimo,
                MAX(precio_unitario) as precio_maximo
            FROM detalle_compras
            WHERE compra_id = ?
            """

            cursor.execute(sql_resumen, (compra_id,))
            resumen_row = cursor.fetchone()

            if resumen_row:
                # Obtener datos de la compra principal
                cursor.execute(
                    "SELECT descuento, impuestos FROM compras WHERE id = ?",
                    (compra_id,)
                )
                compra_row = cursor.fetchone()

                descuento = compra_row[0] if compra_row else 0.0
                impuestos = compra_row[1] if compra_row else 0.0

                subtotal = resumen_row[2] or 0.0
                total_con_descuento = subtotal - descuento
                total_final = total_con_descuento + impuestos

                return {
                    "compra_id": compra_id,
                    "total_items": resumen_row[0] or 0,
                    "total_cantidad": resumen_row[1] or 0,
                    "subtotal": subtotal,
                    "descuento": descuento,
                    "impuestos": impuestos,
                    "total_con_descuento": total_con_descuento,
                    "total_final": total_final,
                    "precio_promedio": resumen_row[3] or 0.0,
                    "precio_minimo": resumen_row[4] or 0.0,
                    "precio_maximo": resumen_row[5] or 0.0
                }

            return self._get_resumen_demo(compra_id)

        except Exception as e:
            print(f"[ERROR DETALLE COMPRAS] Error obteniendo resumen: {e}")
            return self._get_resumen_demo(compra_id)

    def obtener_productos_por_categoria(self) -> Dict[str, List[Dict]]:
        """
        Obtiene productos agrupados por categoría.

        Returns:
            Dict: Productos agrupados por categoría
        """
        if not self.db_connection:
            return self._get_productos_por_categoria_demo()

        try:
            cursor = self.db_connection.cursor()

            sql_select = """
            SELECT 
                categoria,
                descripcion,
                COUNT(*) as veces_comprado,
                AVG(precio_unitario) as precio_promedio,
                SUM(cantidad) as cantidad_total
            FROM detalle_compras
            WHERE categoria IS NOT NULL AND categoria != ''
            GROUP BY categoria, descripcion
            ORDER BY categoria, veces_comprado DESC
            """

            cursor.execute(sql_select)
            rows = cursor.fetchall()

            # Agrupar por categoría
            productos_por_categoria = {}

            for row in rows:
                categoria = row[0]
                if categoria not in productos_por_categoria:
                    productos_por_categoria[categoria] = []

                productos_por_categoria[categoria].append({
                    "descripcion": row[1],
                    "veces_comprado": row[2],
                    "precio_promedio": row[3],
                    "cantidad_total": row[4]
                })

            print(f"[DETALLE COMPRAS] Obtenidas {len(productos_por_categoria)} categorías")
            return productos_por_categoria

        except Exception as e:
            print(f"[ERROR DETALLE COMPRAS] Error obteniendo productos por categoría: {e}")
            return self._get_productos_por_categoria_demo()

    def buscar_productos_similares(self, descripcion: str, limite: int = 10) -> List[Dict]:
        """
        Busca productos similares basado en la descripción.

        Args:
            descripcion: Descripción a buscar
            limite: Número máximo de resultados

        Returns:
            List[Dict]: Lista de productos similares
        """
        if not self.db_connection:
            return []

        try:
            # Sanitizar búsqueda
            descripcion_sanitizada = SecurityUtils.sanitize_sql_input(descripcion)

            cursor = self.db_connection.cursor()

            sql_search = """
            SELECT 
                descripcion,
                categoria,
                AVG(precio_unitario) as precio_promedio,
                COUNT(*) as frecuencia_compra
            FROM detalle_compras
            WHERE descripcion LIKE ?
            GROUP BY descripcion, categoria
            ORDER BY frecuencia_compra DESC, precio_promedio ASC
            """

            # Usar LIKE para búsqueda parcial
            patron_busqueda = f"%{descripcion_sanitizada}%"
            cursor.execute(sql_search, (patron_busqueda,))
            rows = cursor.fetchmany(limite)

            productos = []
            for row in rows:
                productos.append({
                    "descripcion": row[0],
                    "categoria": row[1],
                    "precio_promedio": row[2],
                    "frecuencia_compra": row[3]
                })

            print(f"[DETALLE COMPRAS] Encontrados {len(productos)} productos similares")
            return productos

        except Exception as e:
            print(f"[ERROR DETALLE COMPRAS] Error buscando productos similares: {e}")
            return []

    def _get_items_demo(self, compra_id: int) -> List[Dict]:
        """Items demo para testing."""
        return [
            {
                "id": 1,
                "compra_id": compra_id,
                "descripcion": "Perfil de Aluminio 20x20",
                "categoria": "Perfiles",
                "cantidad": 50,
                "precio_unitario": 12.50,
                "unidad": "MT",
                "observaciones": "Color anodizado natural",
                "subtotal": 625.00
            },
            {
                "id": 2,
                "compra_id": compra_id,
                "descripcion": "Vidrio Templado 6mm",
                "categoria": "Vidrios",
                "cantidad": 10,
                "precio_unitario": 85.00,
                "unidad": "M2",
                "observaciones": "Transparente, bordes pulidos",
                "subtotal": 850.00
            },
            {
                "id": 3,
                "compra_id": compra_id,
                "descripcion": "Bisagra Acero Inoxidable",
                "categoria": "Herrajes",
                "cantidad": 20,
                "precio_unitario": 15.75,
                "unidad": "UN",
                "observaciones": "Carga pesada",
                "subtotal": 315.00
            }
        ]

    def _get_resumen_demo(self, compra_id: int) -> Dict[str, Any]:
        """Resumen demo para testing."""
        return {
            "compra_id": compra_id,
            "total_items": 3,
            "total_cantidad": 80,
            "subtotal": 1790.00,
            "descuento": 50.00,
            "impuestos": 261.00,
            "total_con_descuento": 1740.00,
            "total_final": 2001.00,
            "precio_promedio": 37.75,
            "precio_minimo": 12.50,
            "precio_maximo": 85.00
        }

    def _get_productos_por_categoria_demo(self) -> Dict[str, List[Dict]]:
        """Productos por categoría demo."""
        return {
            "Perfiles": [
                {"descripcion": "Perfil Aluminio 20x20", "veces_comprado": 15, "precio_promedio": 12.50, "cantidad_total": 750},
                {"descripcion": "Perfil Aluminio 30x30", "veces_comprado": 8, "precio_promedio": 18.75, "cantidad_total": 320}
            ],
            "Vidrios": [
                {"descripcion": "Vidrio Templado 6mm", "veces_comprado": 12, "precio_promedio": 85.00, "cantidad_total": 240},
                {"descripcion": "Vidrio Laminado 8mm", "veces_comprado": 6, "precio_promedio": 95.50, "cantidad_total": 120}
            ],
            "Herrajes": [
                {"descripcion": "Bisagra Acero Inox", "veces_comprado": 25, "precio_promedio": 15.75, "cantidad_total": 500},
                {"descripcion": "Cerradura Multipunto", "veces_comprado": 10, "precio_promedio": 125.00, "cantidad_total": 40}
            ]
        }