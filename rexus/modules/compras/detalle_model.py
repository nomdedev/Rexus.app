"""
Modelo de Detalle de Compras

Maneja los detalles de productos/items en las órdenes de compra.
"""

            logger.error(f"[ERROR DETALLE COMPRAS] Error actualizando item: {e}")
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

            logger.info(f"Item {item_id} eliminado")
            return True

        except Exception as e:

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

            logger.info(f"Obtenidas {len(productos_por_categoria)} categorías")
            return productos_por_categoria

        except Exception as e:

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

            logger.info(f"Encontrados {len(productos)} productos similares")
            return productos

        except Exception as e:

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
