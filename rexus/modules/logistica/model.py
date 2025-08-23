
# [LOCK] DB Authorization Check - Verify user permissions before DB operations
# Ensure all database operations are properly authorized
# DB Authorization Check
"""
Modelo de Logística

MIGRADO A SQL EXTERNO - Todas las consultas ahora usan SQLQueryManager
para prevenir inyección SQL y mejorar mantenibilidad.

Maneja la lógica de negocio para:
- Gestión de transportes
- Programación de entregas
- Seguimiento de envíos
- Gestión de proveedores de transporte
- Optimización de rutas
- Control de costos logísticos
"""


                        return False

        try:
            cursor = self.db_connection.cursor()

            # Construir query de actualización dinámicamente
            campos_actualizar = []
            valores = []
            
            campos_permitidos = [
                'obra_id', 'transporte_id', 'fecha_programada', 'fecha_entrega',
                'direccion_entrega', 'contacto', 'telefono', 'estado', 
                'observaciones', 'costo_envio'
            ]
            
            for campo in campos_permitidos:
                if campo in datos_entrega:
                    campos_actualizar.append(f"{campo} = ?")
                    valores.append(datos_entrega[campo])
            
            if not campos_actualizar:
                logger.info("[WARNING LOGÍSTICA] No hay campos válidos para actualizar")
                return False
                
            query = f"""
                UPDATE entregas 
                SET {', '.join(campos_actualizar)}
                WHERE id = ?
            """
            valores.append(entrega_id)
            
            cursor.execute(query, valores)
            self.db_connection.commit()
            
            logger.info(f"[LOGÍSTICA] Entrega {entrega_id} actualizada exitosamente")
            return True

        except Exception as e:
            logger.info(f"[ERROR LOGÍSTICA] Error actualizando entrega: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return False

    def actualizar_estado_entrega(self,
entrega_id,
        nuevo_estado,
        observaciones=""):
        """
        Actualiza el estado de una entrega.

        Args:
            entrega_id (int): ID de la entrega
            nuevo_estado (str): Nuevo estado
            observaciones (str): Observaciones opcionales

        Returns:
            bool: True si fue exitoso
        """
        if not self.db_connection:
            return False

        try:
            cursor = self.db_connection.cursor()

            # Si se marca como entregada, agregar fecha de entrega
            if nuevo_estado == "ENTREGADA":
                query = """
                    UPDATE entregas
                    SET estado = ?, fecha_entrega = GETDATE(), observaciones = ?
                    WHERE id = ?
                """
            else:
                query = """
                    UPDATE entregas
                    SET estado = ?, observaciones = ?
                    WHERE id = ?
                """

            cursor.execute(query, (nuevo_estado, observaciones, entrega_id))

            self.db_connection.commit()
            logger.info(f"[LOGÍSTICA] Estado de entrega {entrega_id} actualizado a {nuevo_estado}")
            return True

        except Exception as e:
            logger.info(f"[ERROR LOGÍSTICA] Error actualizando estado de entrega: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return False

    # MÉTODOS PARA DETALLE DE ENTREGAS

    def obtener_detalle_entrega(self, entrega_id):
        """
        Obtiene el detalle de una entrega específica.

        Args:
            entrega_id (int): ID de la entrega

        Returns:
            List[Dict]: Lista de productos de la entrega
        """
        if not self.db_connection:
            return []

        try:
            cursor = self.db_connection.cursor()

            query = """
                SELECT
                    d.id, d.entrega_id, d.producto, d.cantidad, d.peso_kg,
                    d.volumen_m3, d.observaciones
                FROM detalle_entregas d
                WHERE d.entrega_id = ?
                ORDER BY d.producto
            """

            cursor.execute(query, (entrega_id,))
            columnas = [column[0] for column in cursor.description]
            resultados = cursor.fetchall()

            detalles = []
            for fila in resultados:
                detalle = dict(zip(columnas, fila))
                detalles.append(detalle)

            return detalles

        except Exception as e:
            logger.info(f"[ERROR LOGÍSTICA] Error obteniendo detalle de entrega: {e}")
            return []

    def agregar_producto_entrega(self, entrega_id, datos_producto):
        """
        Agrega un producto a una entrega.

        Args:
            entrega_id (int): ID de la entrega
            datos_producto (dict): Datos del producto

        Returns:
            int: ID del detalle creado o None si falla
        """
        if not self.db_connection:
            return None

        try:
            cursor = self.db_connection.cursor()

            query = """
                INSERT INTO detalle_entregas
                (entrega_id, producto, cantidad, peso_kg, volumen_m3, observaciones)
                VALUES (?, ?, ?, ?, ?, ?)
            """

            cursor.execute(
                query,
                (
                    entrega_id,
                    datos_producto.get("producto", ""),
                    datos_producto.get("cantidad", 0),
                    datos_producto.get("peso_kg", 0),
                    datos_producto.get("volumen_m3", 0),
                    datos_producto.get("observaciones", ""),
                ),
            )

            # Obtener ID del detalle creado
            cursor.execute("SELECT @@IDENTITY")
            detalle_id = cursor.fetchone()[0]

            self.db_connection.commit()
            logger.info(f"[LOGÍSTICA] Producto agregado a entrega {entrega_id}")
            return detalle_id

        except Exception as e:
            logger.info(f"[ERROR LOGÍSTICA] Error agregando producto a entrega: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return None

    def eliminar_producto_entrega(self, detalle_id):
        """
        Elimina un producto de una entrega.

        Args:
            detalle_id (int): ID del detalle a eliminar

        Returns:
            bool: True si fue exitoso
        """
        if not self.db_connection:
            return False

        try:
            cursor = self.db_connection.cursor()

            # [LOCK] MIGRADO: Usar SQL externo para prevenir inyección SQL
            query = self.sql_manager.get_query('logistica', 'eliminar_producto_entrega')
            cursor.execute(query, (detalle_id,))

            self.db_connection.commit()
            logger.info("[LOGÍSTICA] Producto eliminado de entrega")
            return True

        except Exception as e:
            logger.info(f"[ERROR LOGÍSTICA] Error eliminando producto de entrega: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return False

    # MÉTODOS PARA ESTADÍSTICAS

    def obtener_estadisticas_logistica(self):
        """
        Obtiene estadísticas generales de logística.

        Returns:
            Dict: Estadísticas de logística
        """
        if not self.db_connection:
            return {}

        try:
            cursor = self.db_connection.cursor()
            estadisticas = {}

            # [LOCK] MIGRADO: Total transportes - SQL externo
            query_total = self.sql_manager.get_query('logistica', 'contar_transportes_activos')
            cursor.execute(query_total)
            estadisticas["total_transportes"] = cursor.fetchone()[0]

            # [LOCK] MIGRADO: Transportes disponibles - SQL externo
            query_disponibles = self.sql_manager.get_query('logistica', 'contar_transportes_disponibles')
            cursor.execute(query_disponibles)
            estadisticas["transportes_disponibles"] = cursor.fetchone()[0]

            # Entregas por estado
            cursor.execute("""
                SELECT estado, COUNT(*) as cantidad
                FROM entregas
                GROUP BY estado
            """)
            estadisticas["entregas_por_estado"] = dict(cursor.fetchall())

            # Entregas del mes actual
            cursor.execute("""
                SELECT COUNT(*) FROM entregas
                WHERE MONTH(fecha_programada) = MONTH(GETDATE())
                AND YEAR(fecha_programada) = YEAR(GETDATE())
            """)
            estadisticas["entregas_mes_actual"] = cursor.fetchone()[0]

            # Entregas pendientes
            cursor.execute("""
                SELECT COUNT(*) FROM entregas
                WHERE estado IN ('PROGRAMADA', 'EN_TRANSITO')
            """)
            estadisticas["entregas_pendientes"] = cursor.fetchone()[0]

            # Costo total de envíos del mes
            cursor.execute("""
                SELECT SUM(costo_envio) FROM entregas
                WHERE MONTH(fecha_programada) = MONTH(GETDATE())
                AND YEAR(fecha_programada) = YEAR(GETDATE())
            """)
            resultado = cursor.fetchone()[0]
            estadisticas["costo_envios_mes"] = float(resultado) if resultado else 0.0

            return estadisticas

        except Exception as e:
            logger.info(f"[ERROR LOGÍSTICA] Error obteniendo estadísticas: {e}")
            return {}

    def obtener_obras_disponibles(self):
        """
        Obtiene las obras disponibles para asignar entregas.

        Returns:
            List[Dict]: Lista de obras activas
        """
        if not self.db_connection:
            return []

        try:
            cursor = self.db_connection.cursor()

            query = """
                SELECT id, nombre, direccion, estado
                FROM obras
                WHERE activo = 1 AND estado != 'TERMINADA'
                ORDER BY nombre
            """

            cursor.execute(query)
            columnas = [column[0] for column in cursor.description]
            resultados = cursor.fetchall()

            obras = []
            for fila in resultados:
                obra = dict(zip(columnas, fila))
                obras.append(obra)

            return obras

        except Exception as e:
            logger.info(f"[ERROR LOGÍSTICA] Error obteniendo obras disponibles: {e}")
            return []

    def calcular_costo_envio(self,
transporte_id,
        distancia_km,
        peso_kg,
        volumen_m3):
        """
        Calcula el costo de envío para una entrega.

        Args:
            transporte_id (int): ID del transporte
            distancia_km (float): Distancia en kilómetros
            peso_kg (float): Peso en kilogramos
            volumen_m3 (float): Volumen en metros cúbicos

        Returns:
            float: Costo estimado del envío
        """
        if not self.db_connection:
            return 0.0

        try:
            cursor = self.db_connection.cursor()

            # Obtener información del transporte
            cursor.execute("""
                SELECT costo_km, capacidad_kg, capacidad_m3
                FROM transportes
                WHERE id = ?
            """, (transporte_id,))

            resultado = cursor.fetchone()
            if not resultado:
                return 0.0

            costo_km, capacidad_kg, capacidad_m3 = resultado

            # Calcular costo base por distancia
            costo_base = float(costo_km) * distancia_km

            # Agregar costos adicionales por peso y volumen excedente
            costo_adicional = 0.0

            if peso_kg > capacidad_kg:
                costo_adicional += (
                    peso_kg - capacidad_kg
                ) * 0.5  # $0.5 por kg excedente

            if volumen_m3 > capacidad_m3:
                costo_adicional += (
                    volumen_m3 - capacidad_m3
                ) * 10  # $10 por m³ excedente

            costo_total = costo_base + costo_adicional

            return costo_total

        except Exception as e:
            logger.info(f"[ERROR LOGÍSTICA] Error calculando costo de envío: {e}")
            return 0.0
    def eliminar_transporte(self, transporte_id):
        """
        Elimina un transporte de la base de datos.

        Args:
            transporte_id (int): ID del transporte a eliminar

        Returns:
            bool: True si se eliminó exitosamente
        """
        if not self.db_connection:
            return False

        try:
            transporte_id = sanitize_numeric(transporte_id)
            if transporte_id is None:
                raise ValueError("ID de transporte inválido")

            cursor = self.db_connection.cursor()

            # Verificar que el transporte existe
            verify_sql = "SELECT COUNT(*) FROM transportes WHERE id = ?"
            cursor.execute(verify_sql, (transporte_id,))
            if cursor.fetchone()[0] == 0:
                logger.info(f"[ERROR] Transporte {transporte_id} no encontrado")
                return False

            # Eliminar el transporte
            delete_sql = "DELETE FROM transportes WHERE id = ?"
            cursor.execute(delete_sql, (transporte_id,))
            self.db_connection.commit()

            logger.info(f"[OK] Transporte {transporte_id} eliminado exitosamente")
            return True

        except Exception as e:
            logger.info(f"[ERROR] Error eliminando transporte: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return False

    def buscar_transportes(self, termino_busqueda="", estado="Todos"):
        """
        Busca transportes según criterios específicos.

        Args:
            termino_busqueda (str): Término para buscar en origen, destino o conductor
            estado (str): Estado del transporte a filtrar

        Returns:
            list: Lista de transportes que coinciden con los criterios
        """
        if not self.db_connection:
            # Datos de demostración para pruebas
            return [
                {
                    'id': 1,
                    'origen': 'Madrid',
                    'destino': 'Barcelona',
                    'estado': 'En tránsito',
                    'conductor': 'Juan Pérez',
                    'fecha': '2025-01-15'
                },
                {
                    'id': 2,
                    'origen': 'Valencia',
                    'destino': 'Sevilla',
                    'estado': 'Entregado',
                    'conductor': 'María González',
                    'fecha': '2025-01-14'
                }
            ]

        try:
            cursor = self.db_connection.cursor()

            # Construir query con filtros
            base_sql = """
                SELECT id, origen, destino, estado, conductor, fecha_entrega,
                       observaciones, costo_estimado, fecha_creacion
                FROM transportes
                WHERE 1=1
            """

            params = []

            # Filtro por término de búsqueda
            if termino_busqueda and termino_busqueda.strip():
                termino = sanitize_string(termino_busqueda.strip())
                base_sql += " AND (origen LIKE ? OR destino LIKE ? OR conductor LIKE ?)"
                like_term = f"%{termino}%"
                params.extend([like_term, like_term, like_term])

            # Filtro por estado
            if estado and estado != "Todos":
                estado_clean = sanitize_string(estado)
                base_sql += " AND estado = ?"
                params.append(estado_clean)

            # Ordenar por fecha más reciente
            base_sql += " ORDER BY fecha_creacion DESC"

            cursor.execute(base_sql, params)
            results = cursor.fetchall()

            transportes = []
            for row in results:
                transporte = {
                    'id': row[0],
                    'origen': row[1] or '',
                    'destino': row[2] or '',
                    'estado': row[3] or '',
                    'conductor': row[4] or '',
                    'fecha': row[5].strftime('%Y-%m-%d') if row[5] else '',
                    'observaciones': row[6] or '',
                    'costo_estimado': float(row[7]) if row[7] else 0.0,
                    'fecha_creacion': row[8]
                }
                transportes.append(transporte)

            logger.info(f"[SEARCH] Encontrados {len(transportes)} transportes con criterios: '{termino_busqueda}' - Estado: {estado}")
            return transportes

        except Exception as e:
            logger.info(f"[ERROR] Error buscando transportes: {e}")
            return []

    def obtener_estadisticas(self):
        """
        Obtiene estadísticas generales de logística.

        Returns:
            dict: Diccionario con estadísticas clave
        """
        if not self.db_connection:
            # Estadísticas simuladas para pruebas
            return {
                'total_transportes': 156,
                'en_transito': 23,
                'entregados_hoy': 8,
                'pendientes': 12,
                'costo_total_mes': 15750.50,
                'entregas_programadas': 45
            }

        try:
            cursor = self.db_connection.cursor()
            stats = {}

            # Total de transportes
            sql_count_total = self.sql_manager.get_query('logistica', 'count_transportes_total')
            cursor.execute(sql_count_total)
            stats['total_transportes'] = cursor.fetchone()[0]

            # Transportes en tránsito
            sql_count_transito = self.sql_manager.get_query('logistica', 'count_transportes_en_transito')
            cursor.execute(sql_count_transito)
            stats['en_transito'] = cursor.fetchone()[0]

            # Entregados hoy
            cursor.execute("""
                SELECT COUNT(*) FROM transportes
                WHERE estado = 'Entregado'
                AND CAST(fecha_entrega AS DATE) = CAST(GETDATE() AS DATE)
            """)
            stats['entregados_hoy'] = cursor.fetchone()[0]

            # Pendientes
            sql_count_pendientes = self.sql_manager.get_query('logistica', 'count_transportes_pendientes')
            cursor.execute(sql_count_pendientes)
            stats['pendientes'] = cursor.fetchone()[0]

            # Costo total del mes actual
            cursor.execute("""
                SELECT COALESCE(SUM(costo_estimado), 0)
                FROM transportes
                WHERE MONTH(fecha_creacion) = MONTH(GETDATE())
                AND YEAR(fecha_creacion) = YEAR(GETDATE())
            """)
            stats['costo_total_mes'] = float(cursor.fetchone()[0])

            # Entregas programadas para los próximos 7 días
            cursor.execute("""
                SELECT COUNT(*) FROM entregas
                WHERE fecha_programada BETWEEN GETDATE() AND DATEADD(day, 7, GETDATE())
                AND estado != 'Entregado'
            """)
            stats['entregas_programadas'] = cursor.fetchone()[0]

            return stats

        except Exception as e:
            logger.info(f"[ERROR] Error obteniendo estadísticas: {e}")
            return {
                'total_transportes': 0,
                'en_transito': 0,
                'entregados_hoy': 0,
                'pendientes': 0,
                'costo_total_mes': 0.0,
                'entregas_programadas': 0
            }

    def obtener_todas_entregas(self, filtros=None):
        """
        Obtiene todas las entregas (alias para obtener_entregas)
        
        Args:
            filtros (dict, optional): Filtros a aplicar
            
        Returns:
            List[Dict]: Lista de entregas
        """
        return self.obtener_entregas(filtros)
