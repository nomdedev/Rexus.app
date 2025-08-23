"""
Modelo de Herrajes - Rexus.app v2.0.0
Versión simplificada y funcional

Maneja la lógica de negocio y acceso a datos para herrajes.
"""

import logging
                            return False

            cursor = self.db_connection.cursor()

            # Verificar si el herraje existe
            cursor.execute("SELECT id FROM herrajes WHERE codigo = ?", (codigo,))
            if not cursor.fetchone():
                logger.info(f"[ERROR HERRAJES] No se encontró herraje con código: {codigo}")
                return False

            # Eliminar registros relacionados primero (si existen)
            cursor.execute("DELETE FROM herrajes_obra WHERE herraje_id = (SELECT id FROM herrajes WHERE codigo = ?)", (codigo,))

            # Eliminar el herraje
            cursor.execute("DELETE FROM herrajes WHERE codigo = ?", (codigo,))
            rows_affected = cursor.rowcount
            self.db_connection.commit()

            if rows_affected > 0:
                logger.info(f"[HERRAJES] Herraje eliminado: {codigo}")
                return True
            else:
                logger.info(f"[ERROR HERRAJES] No se pudo eliminar herraje: {codigo}")
                return False

        except Exception as e:
            logger.info(f"[ERROR HERRAJES] Error eliminando herraje: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return False

    def obtener_herraje_por_codigo(self, codigo: str) -> Optional[Dict]:
        """Obtiene un herraje específico por su código."""
        try:
            if not self.db_connection:
                return None

            cursor = self.db_connection.cursor()
            cursor.execute("""
                SELECT codigo, nombre, descripcion, categoria, proveedor,
                       precio_unitario, stock_actual, stock_minimo, unidad_medida, activo
                FROM herrajes
                WHERE codigo = ? AND activo = 1
            """, (codigo,))

            row = cursor.fetchone()
            if row:
                return {
                    "codigo": row[0],
                    "nombre": row[1],
                    "descripcion": row[2],
                    "categoria": row[3],
                    "proveedor": row[4],
                    "precio_unitario": float(row[5]) if row[5] else 0.0,
                    "stock_actual": int(row[6]) if row[6] else 0,
                    "stock_minimo": int(row[7]) if row[7] else 0,
                    "unidad_medida": row[8] or "unidad",
                    "activo": bool(row[9])
                }
            return None

        except Exception as e:
            logger.info(f"[ERROR HERRAJES] Error obteniendo herraje por código: {e}")
            return None

    # === MÉTODOS DE PAGINACIÓN ===

    def obtener_datos_paginados(self, offset=0, limit=50, filtros=None):
        """
        Obtiene datos paginados de herrajes.

        Args:
            offset: Registro inicial
            limit: Cantidad de registros
            filtros: Filtros adicionales

        Returns:
            tuple: (datos, total_registros)
        """
        if not self.db_connection:
            # Fallback con datos demo
            datos_demo = self._get_herrajes_demo()
            return datos_demo[offset:offset+limit], len(datos_demo)

        try:
            cursor = self.db_connection.cursor()

            # Query principal con paginación
            query = """
                SELECT codigo, nombre, descripcion, categoria, proveedor,
                       precio_unitario, stock_actual, stock_minimo, unidad_medida, activo
                FROM herrajes
                WHERE activo = 1
            """
            
            params = []
            
            # Aplicar filtros si existen
            if filtros:
                if filtros.get('categoria') and filtros['categoria'] not in ['Todos', '📂 Todas las categorías']:
                    # Limpiar el emoji si existe
                    categoria = filtros['categoria']
                    if ' ' in categoria and categoria.startswith('📂'):
                        categoria = categoria.split(' ', 1)[1]
                    query += " AND categoria LIKE ?"
                    params.append(f"%{categoria}%")
                
                if filtros.get('busqueda'):
                    query += " AND (codigo LIKE ? OR nombre LIKE ? OR categoria LIKE ?)"
                    busqueda = f"%{filtros['busqueda']}%"
                    params.extend([busqueda, busqueda, busqueda])

            # Query de conteo
            count_query = query.replace(
                "SELECT codigo, nombre, descripcion, categoria, proveedor, precio_unitario, stock_actual, stock_minimo, unidad_medida, activo",
                "SELECT COUNT(*)"
            )
            
            cursor.execute(count_query, params)
            total_registros = cursor.fetchone()[0]

            # Query principal con paginación
            query += " ORDER BY codigo OFFSET ? ROWS FETCH NEXT ? ROWS ONLY"
            params.extend([offset, limit])
            
            cursor.execute(query, params)
            datos = []
            
            for row in cursor.fetchall():
                datos.append({
                    "codigo": row[0],
                    "nombre": row[1],
                    "descripcion": row[2],
                    "categoria": row[3],
                    "tipo": row[3],  # Alias para compatibilidad
                    "proveedor": row[4],
                    "precio_unitario": float(row[5]) if row[5] else 0.0,
                    "stock_actual": int(row[6]) if row[6] else 0,
                    "stock": int(row[6]) if row[6] else 0,  # Alias para compatibilidad
                    "stock_minimo": int(row[7]) if row[7] else 0,
                    "unidad_medida": row[8] or "unidad",
                    "activo": bool(row[9])
                })

            return datos, total_registros

        except Exception as e:
            logger.info(f"[ERROR HERRAJES] Error obteniendo datos paginados: {e}")
            # Fallback con datos demo en caso de error
            datos_demo = self._get_herrajes_demo()
            return datos_demo[offset:offset+limit], len(datos_demo)

    def obtener_total_registros(self, filtros=None):
        """
        Obtiene el total de registros de herrajes.

        Args:
            filtros: Filtros aplicados

        Returns:
            int: Total de registros
        """
        if not self.db_connection:
            return len(self._get_herrajes_demo())

        try:
            cursor = self.db_connection.cursor()
            
            query = "SELECT COUNT(*) FROM herrajes WHERE activo = 1"
            params = []
            
            # Aplicar filtros si existen
            if filtros:
                if filtros.get('categoria') and filtros['categoria'] not in ['Todos', '📂 Todas las categorías']:
                    categoria = filtros['categoria']
                    if ' ' in categoria and categoria.startswith('📂'):
                        categoria = categoria.split(' ', 1)[1]
                    query += " AND categoria LIKE ?"
                    params.append(f"%{categoria}%")
                
                if filtros.get('busqueda'):
                    query += " AND (codigo LIKE ? OR nombre LIKE ? OR categoria LIKE ?)"
                    busqueda = f"%{filtros['busqueda']}%"
                    params.extend([busqueda, busqueda, busqueda])
            
            cursor.execute(query, params)
            return cursor.fetchone()[0]

        except Exception as e:
            logger.info(f"[ERROR HERRAJES] Error obteniendo total de registros: {e}")
            return len(self._get_herrajes_demo())

    def _get_herrajes_demo(self):
        """Datos demo para cuando no hay conexión a base de datos."""
        return [
            {
                "codigo": "BIS-001",
                "nombre": "Bisagra Estándar 3\"",
                "categoria": "Bisagras",
                "tipo": "Bisagras",
                "proveedor": "Herrajes del Norte",
                "precio_unitario": 1250.00,
                "stock_actual": 150,
                "stock": 150,
                "activo": True
            },
            {
                "codigo": "CER-001", 
                "nombre": "Cerradura Multipunto",
                "categoria": "Cerraduras",
                "tipo": "Cerraduras",
                "proveedor": "Seguridad Total",
                "precio_unitario": 8500.00,
                "stock_actual": 25,
                "stock": 25,
                "activo": True
            },
            {
                "codigo": "MAN-001",
                "nombre": "Manija Acero Inoxidable",
                "categoria": "Manijas",
                "tipo": "Manijas", 
                "proveedor": "Diseño Moderno",
                "precio_unitario": 3200.00,
                "stock_actual": 75,
                "stock": 75,
                "activo": True
            },
            {
                "codigo": "TOR-001",
                "nombre": "Tornillo Autoperforante 4x40",
                "categoria": "Tornillería",
                "tipo": "Tornillería",
                "proveedor": "Ferretería Central",
                "precio_unitario": 25.00,
                "stock_actual": 0,
                "stock": 0,
                "activo": True
            }
        ]
