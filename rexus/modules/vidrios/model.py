                def eliminar_vidrio(self, vidrio_id):
        """
        Elimina un vidrio (marca como inactivo) con validación de entrada.

        Args:
            vidrio_id (int): ID del vidrio a eliminar

        Returns:
            tuple: (bool, str) - (éxito, mensaje)
        """
        if not self.db_connection:
            return False, "No hay conexión a la base de datos"

        try:
            # Validar ID
            vidrio_id_limpio = self.data_sanitizer.sanitize_integer(
                vidrio_id, min_val=1
            )
            if vidrio_id_limpio is None:
                return False, "ID de vidrio inválido"

            cursor = self.db_connection.connection.cursor()

            # FIXED: Verificar si el vidrio existe usando consulta parametrizada segura
            cursor.execute("""
                SELECT id, tipo, especificaciones FROM vidrios WHERE id = ?
            """, (vidrio_id_limpio,))

            vidrio_info = cursor.fetchone()
            if not vidrio_info:
                return False, f"Vidrio con ID {vidrio_id_limpio} no encontrado"

            tipo, _ = vidrio_info

            # FIXED: Verificar si el vidrio está asignado a alguna obra usando consulta parametrizada segura
            cursor.execute("""
                SELECT COUNT(*) FROM vidrios_obra WHERE vidrio_id = ?
            """, (vidrio_id_limpio,))

            if cursor.fetchone()[0] > 0:
                logger.warning(f"El vidrio {vidrio_id_limpio} está asignado a obras, se marcará como inactivo")
                # FIXED: Marcar como inactivo en lugar de eliminar usando consulta parametrizada segura
                cursor.execute("""
                    UPDATE vidrios SET estado = 'INACTIVO', fecha_actualizacion = GETDATE() 
                    WHERE id = ?
                """, (vidrio_id_limpio,))
                mensaje = (
                    f"Vidrio '{tipo}' marcado como inactivo (estaba asignado a obras)"
                )
            else:
                # FIXED: Eliminar completamente si no está asignado usando consulta parametrizada segura
                cursor.execute("""
                    DELETE FROM vidrios WHERE id = ?
                """, (vidrio_id_limpio,))
                mensaje = f"Vidrio '{tipo}' eliminado completamente"

            self.db_connection.connection.commit()
            logger.info(mensaje)
            return True, mensaje

        except Exception as e:
                self.db_connection.connection.rollback()
            return False, f"Error eliminando vidrio: {str(e)}"

    def obtener_vidrio_por_id(self, vidrio_id):
        """
        Obtiene un vidrio específico por su ID con validación.

        Args:
            vidrio_id (int): ID del vidrio

        Returns:
            tuple: (bool, dict) - (éxito, datos del vidrio o None)
        """
        if not self.db_connection:
            return False, None

        try:
            # Validar ID
            vidrio_id_limpio = self.data_sanitizer.sanitize_integer(
                vidrio_id, min_val=1
            )
            if vidrio_id_limpio is None:
                return False, None

            cursor = self.db_connection.connection.cursor()

            # FIXED: Usar consulta parametrizada segura en lugar de script_content
            cursor.execute("""
                SELECT id, tipo as tipo, especificaciones as especificaciones, tipo, proveedor, espesor, 
                       color, precio_m2, estado, dimensiones as dimensiones, propiedades as propiedades,
                       fecha_creacion, fecha_actualizacion as fecha_actualizacion
                FROM vidrios 
                WHERE id = ?
            """, (vidrio_id_limpio,))
            columnas = [column[0] for column in cursor.description]
            resultado = cursor.fetchone()

            if resultado:
                vidrio_data = dict(zip(columnas, resultado))
                return True, vidrio_data
            return False, None

        except Exception as e:

    def obtener_datos_paginados(self, offset=0, limit=50, filtros=None):
        """
        Obtiene datos paginados de vidrios.

        Args:
            offset: Registro inicial
            limit: Cantidad de registros
            filtros: Filtros adicionales

        Returns:
            tuple: (datos, total_registros)
        """
        if not self.db_connection:
            # Fallback con datos demo
            datos_demo = self._get_vidrios_demo()
            return datos_demo[offset:offset+limit], len(datos_demo)

        try:
            cursor = self.db_connection.connection.cursor()

            # Query principal con paginación
            query = """
                SELECT id, tipo as tipo, especificaciones as especificaciones, tipo, espesor, 
                       proveedor, precio_m2, color, propiedades as propiedades, estado,
                       dimensiones_disponibles, propiedades as propiedades
                FROM vidrios
                WHERE activo = 1
            """
            
            params = []
            
            # Aplicar filtros si existen
            if filtros:
                if filtros.get('tipo') and filtros['tipo'] != 'Todos':
                    query += " AND tipo = ?"
                    params.append(filtros['tipo'])
                
                if filtros.get('busqueda'):
                    query += " AND (tipo LIKE ? OR especificaciones LIKE ? OR tipo LIKE ?)"
                    busqueda = f"%{filtros['busqueda']}%"
                    params.extend([busqueda, busqueda, busqueda])

            # Query de conteo
            count_query = query.replace(
                "SELECT id, tipo as tipo, especificaciones as especificaciones, tipo, espesor, proveedor, precio_m2, color, propiedades as propiedades, estado, dimensiones_disponibles, propiedades as observaciones",
                "SELECT COUNT(*)"
            )
            
            cursor.execute(count_query, params)
            total_registros = cursor.fetchone()[0]

            # Query principal con paginación
            query += " ORDER BY id DESC OFFSET ? ROWS FETCH NEXT ? ROWS ONLY"
            params.extend([offset, limit])
            
            cursor.execute(query, params)
            columnas = [column[0] for column in cursor.description]
            datos = []
            
            for row in cursor.fetchall():
                datos.append(dict(zip(columnas, row)))

            return datos, total_registros

        except Exception as e:
            datos_demo = self._get_vidrios_demo()
            return datos_demo[offset:offset+limit], len(datos_demo)

    def obtener_total_registros(self, filtros=None):
        """
        Obtiene el total de registros de vidrios.

        Args:
            filtros: Filtros aplicados

        Returns:
            int: Total de registros
        """
        if not self.db_connection:
            return len(self._get_vidrios_demo())

        try:
            cursor = self.db_connection.connection.cursor()
            
            query = "SELECT COUNT(*) FROM vidrios WHERE activo = 1"
            params = []
            
            # Aplicar filtros si existen
            if filtros:
                if filtros.get('tipo') and filtros['tipo'] != 'Todos':
                    query += " AND tipo = ?"
                    params.append(filtros['tipo'])
                
                if filtros.get('busqueda'):
                    query += " AND (tipo LIKE ? OR especificaciones LIKE ? OR tipo LIKE ?)"
                    busqueda = f"%{filtros['busqueda']}%"
                    params.extend([busqueda, busqueda, busqueda])
            
            cursor.execute(query, params)
            return cursor.fetchone()[0]

        except Exception as e:

    def _get_vidrios_demo(self):
        """Datos demo para cuando no hay conexión a base de datos."""
        return [
            {
                "id": 1,
                "codigo": "VT-001",
                "descripcion": "Vidrio Templado 6mm Transparente",
                "tipo": "Templado",
                "espesor": 6,
                "proveedor": "Cristales Modernos",
                "precio_m2": 45.00,
                "color": "Transparente",
                "tratamiento": "Templado",
                "estado": "ACTIVO",
                "dimensiones_disponibles": "2.0x3.0m, 1.5x2.5m",
                "observaciones": "Vidrio para puertas principales",
            },
            {
                "id": 2,
                "codigo": "VL-002",
                "descripcion": "Vidrio Laminado 8mm Bronce",
                "tipo": "Laminado",
                "espesor": 8,
                "proveedor": "Vidrios Industriales",
                "precio_m2": 62.50,
                "color": "Bronce",
                "tratamiento": "Laminado",
                "estado": "ACTIVO",
                "dimensiones_disponibles": "2.5x3.5m, 2.0x3.0m",
                "observaciones": "Vidrio de seguridad para fachadas",
            },
            {
                "id": 3,
                "codigo": "VC-003",
                "descripcion": "Vidrio Común 4mm Transparente",
                "tipo": "Común",
                "espesor": 4,
                "proveedor": "Distribuidora Central",
                "precio_m2": 18.75,
                "color": "Transparente",
                "tratamiento": "Ninguno",
                "estado": "ACTIVO",
                "dimensiones_disponibles": "1.5x2.0m, 1.0x1.5m",
                "observaciones": "Vidrio estándar para ventanas",
            },
            {
                "id": 4,
                "codigo": "VE-004",
                "descripción": "Espejo 5mm Plata",
                "tipo": "Espejo",
                "espesor": 5,
                "proveedor": "Espejos Decorativos",
                "precio_m2": 35.00,
                "color": "Plata",
                "tratamiento": "Espejado",
                "estado": "ACTIVO",
                "dimensiones_disponibles": "1.0x2.0m, 0.8x1.5m",
                "observaciones": "Espejo decorativo para baños",
            },
            {
                "id": 5,
                "codigo": "VT-005",
                "descripcion": "Vidrio Templado 10mm Azul",
                "tipo": "Templado",
                "espesor": 10,
                "proveedor": "Cristales Modernos",
                "precio_m2": 78.00,
                "color": "Azul",
                "tratamiento": "Templado",
                "estado": "ACTIVO",
                "dimensiones_disponibles": "3.0x4.0m, 2.5x3.0m",
                "observaciones": "Vidrio especial para divisiones",
            },
        ]


# ====== ALIAS PARA COMPATIBILIDAD ======
# Alias para mantener compatibilidad con imports existentes
ModeloVidrios = VidriosModel
