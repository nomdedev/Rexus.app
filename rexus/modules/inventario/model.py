                            return []
                
            cursor = self.db_connection.cursor()
            
            if producto_id:
                # Usar método existente para producto específico
                return self.obtener_lotes_producto(producto_id)
            else:
                # Obtener todos los lotes
                if self.sql_manager:
                    # Intentar usar SQL externo
                    try:
                        sql = self.sql_manager.get_query('inventario', 'obtener_todos_lotes')
                        cursor.execute(sql, {
                            'activos_solo': activos_solo
                        })
                    except:
                        # Fallback con query manual
                        sql = """
                        SELECT 
                            l.id,
                            l.producto_id,
                            l.numero_lote,
                            l.cantidad,
                            l.fecha_vencimiento,
                            l.ubicacion,
                            l.estado,
                            l.fecha_ingreso,
                            p.nombre as producto_nombre,
                            p.codigo as producto_codigo
                        FROM lotes_inventario l
                        LEFT JOIN productos p ON l.producto_id = p.id
                        WHERE l.activo = ?
                        ORDER BY l.fecha_ingreso DESC
                        """
                        cursor.execute(sql, (1 if activos_solo else 0,))
                else:
                    # Query manual sin SQL Manager
                    sql = """
                    SELECT 
                        l.id,
                        l.producto_id,
                        l.numero_lote,
                        l.cantidad,
                        l.fecha_vencimiento,
                        l.ubicacion,
                        l.estado,
                        l.fecha_ingreso,
                        p.nombre as producto_nombre,
                        p.codigo as producto_codigo
                    FROM lotes_inventario l
                    LEFT JOIN productos p ON l.producto_id = p.id
                    WHERE l.activo = ?
                    ORDER BY l.fecha_ingreso DESC
                    """
                    cursor.execute(sql, (1 if activos_solo else 0,))
                
                # Procesar resultados
                lotes = []
                for row in cursor.fetchall():
                    lote = {
                        'id': row[0],
                        'producto_id': row[1], 
                        'numero_lote': row[2],
                        'cantidad': row[3],
                        'fecha_vencimiento': row[4],
                        'ubicacion': row[5],
                        'estado': row[6],
                        'fecha_ingreso': row[7],
                        'producto_nombre': row[8] if len(row) > 8 else None,
                        'producto_codigo': row[9] if len(row) > 9 else None
                    }
                    lotes.append(lote)
                    
                return lotes
                
        except Exception as e:

    def _get_productos_demo(self):
        """Datos demo para productos cuando no hay conexión"""
        return [
            {
                'id': 1,
                'codigo': 'PROD001',
                'nombre': 'Producto Demo 1',
                'categoria': 'DEMO',
                'cantidad_disponible': 10,
                'precio_unitario': 100.0
            },
            {
                'id': 2,
                'codigo': 'PROD002', 
                'nombre': 'Producto Demo 2',
                'categoria': 'DEMO',
                'cantidad_disponible': 5,
                'precio_unitario': 200.0
            }
        ]
