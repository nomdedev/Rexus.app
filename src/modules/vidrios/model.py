"""
Modelo de Vidrios

Maneja la lógica de negocio y acceso a datos para vidrios.
Gestiona la compra por obra y asociación con proveedores.
"""


class VidriosModel:
    """Modelo para gestionar vidrios por obra y proveedor."""

    def __init__(self, db_connection=None):
        """
        Inicializa el modelo de vidrios.

        Args:
            db_connection: Conexión a la base de datos
        """
        self.db_connection = db_connection
        self.tabla_vidrios = "vidrios"  # Tabla principal de vidrios en DB inventario
        self.tabla_vidrios_obra = "vidrios_obra"  # Tabla para asociar vidrios con obras
        self.tabla_pedidos_vidrios = "pedidos_vidrios"  # Tabla para pedidos por obra
        self._verificar_tablas()

    def _verificar_tablas(self):
        """Verifica que las tablas necesarias existan en la base de datos."""
        if not self.db_connection:
            return

        try:
            cursor = self.db_connection.connection.cursor()

            # Verificar tabla principal de vidrios
            cursor.execute(
                "SELECT * FROM sysobjects WHERE name=? AND xtype='U'",
                (self.tabla_vidrios,),
            )
            if cursor.fetchone():
                print(
                    f"[VIDRIOS] Tabla '{self.tabla_vidrios}' verificada correctamente."
                )

                # Obtener estructura de la tabla
                cursor.execute(
                    "SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = ?",
                    (self.tabla_vidrios,),
                )
                columnas = cursor.fetchall()
                print(f"[VIDRIOS] Estructura de tabla '{self.tabla_vidrios}':")
                for columna in columnas:
                    print(f"  - {columna[0]}: {columna[1]}")
            else:
                print(
                    f"[ADVERTENCIA] La tabla '{self.tabla_vidrios}' no existe en la base de datos."
                )

            # Verificar tabla de vidrios por obra
            cursor.execute(
                "SELECT * FROM sysobjects WHERE name=? AND xtype='U'",
                (self.tabla_vidrios_obra,),
            )
            if cursor.fetchone():
                print(
                    f"[VIDRIOS] Tabla '{self.tabla_vidrios_obra}' verificada correctamente."
                )
            else:
                print(
                    f"[ADVERTENCIA] La tabla '{self.tabla_vidrios_obra}' no existe en la base de datos."
                )

        except Exception as e:
            print(f"[ERROR VIDRIOS] Error verificando tablas: {e}")

    def obtener_todos_vidrios(self, filtros=None):
        """
        Obtiene todos los vidrios disponibles.

        Args:
            filtros (dict): Filtros opcionales (proveedor, tipo, espesor)

        Returns:
            List[Dict]: Lista de vidrios
        """
        if not self.db_connection:
            return []

        try:
            cursor = self.db_connection.connection.cursor()

            # Construir query con filtros
            conditions = ["1=1"]  # Condición base
            params = []

            if filtros:
                if filtros.get("proveedor"):
                    conditions.append("proveedor LIKE ?")
                    params.append(f"%{filtros['proveedor']}%")

                if filtros.get("tipo"):
                    conditions.append("tipo LIKE ?")
                    params.append(f"%{filtros['tipo']}%")

                if filtros.get("espesor"):
                    conditions.append("espesor = ?")
                    params.append(filtros["espesor"])

            query = f"""
                SELECT
                    id, codigo, descripcion, tipo, espesor, proveedor,
                    precio_m2, color, tratamiento, dimensiones_disponibles,
                    estado, observaciones, fecha_actualizacion
                FROM {self.tabla_vidrios}
                WHERE """ + " AND ".join(conditions) + """
                ORDER BY tipo, espesor
            """

            cursor.execute(query, params)
            columnas = [column[0] for column in cursor.description]
            resultados = cursor.fetchall()

            vidrios = []
            for fila in resultados:
                vidrio = dict(zip(columnas, fila))
                vidrios.append(vidrio)

            return vidrios

        except Exception as e:
            print(f"[ERROR VIDRIOS] Error obteniendo vidrios: {e}")
            return []

    def obtener_vidrios_por_obra(self, obra_id):
        """
        Obtiene vidrios asociados a una obra específica.

        Args:
            obra_id (int): ID de la obra

        Returns:
            List[Dict]: Lista de vidrios con cantidades y medidas asignadas
        """
        if not self.db_connection:
            return []

        try:
            cursor = self.db_connection.connection.cursor()

            query = f"""
                SELECT
                    v.id, v.codigo, v.descripcion, v.tipo, v.espesor, v.proveedor,
                    v.precio_m2, vo.metros_cuadrados_requeridos, vo.metros_cuadrados_pedidos,
                    vo.medidas_especificas, vo.fecha_asignacion, vo.observaciones as obs_obra
                FROM {self.tabla_vidrios} v
                INNER JOIN {self.tabla_vidrios_obra} vo ON v.id = vo.vidrio_id
                WHERE vo.obra_id = ?
                ORDER BY v.tipo, v.espesor
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

    def asignar_vidrio_obra(
        self,
        vidrio_id,
        obra_id,
        metros_cuadrados,
        medidas_especificas=None,
        observaciones=None,
    ):
        """
        Asigna un vidrio a una obra específica.

        Args:
            vidrio_id (int): ID del vidrio
            obra_id (int): ID de la obra
            metros_cuadrados (float): Metros cuadrados requeridos
            medidas_especificas (str): Medidas específicas
            observaciones (str): Observaciones opcionales

        Returns:
            bool: True si fue exitoso
        """
        if not self.db_connection:
            return False

        try:
            cursor = self.db_connection.connection.cursor()

            query = f"""
                INSERT INTO {self.tabla_vidrios_obra}
                (vidrio_id, obra_id, metros_cuadrados_requeridos, medidas_especificas, fecha_asignacion, observaciones)
                VALUES (?, ?, ?, ?, GETDATE(), ?)
            """

            cursor.execute(
                query,
                (
                    vidrio_id,
                    obra_id,
                    metros_cuadrados,
                    medidas_especificas,
                    observaciones,
                ),
            )
            self.db_connection.connection.commit()

            print(f"[VIDRIOS] Vidrio {vidrio_id} asignado a obra {obra_id}")
            return True

        except Exception as e:
            print(f"[ERROR VIDRIOS] Error asignando vidrio a obra: {e}")
            return False

    def crear_pedido_obra(self, obra_id, proveedor, vidrios_lista):
        """
        Crea un pedido de vidrios para una obra específica.

        Args:
            obra_id (int): ID de la obra
            proveedor (str): Nombre del proveedor
            vidrios_lista (List[Dict]): Lista de vidrios con cantidades

        Returns:
            int: ID del pedido creado o None si falla
        """
        if not self.db_connection:
            return None

        try:
            cursor = self.db_connection.connection.cursor()

            # Crear pedido principal
            query_pedido = f"""
                INSERT INTO {self.tabla_pedidos_vidrios}
                (obra_id, proveedor, fecha_pedido, estado, total_estimado)
                VALUES (?, ?, GETDATE(), 'PENDIENTE', ?)
            """

            total_estimado = sum(
                item["metros_cuadrados"] * item["precio_m2"] for item in vidrios_lista
            )
            cursor.execute(query_pedido, (obra_id, proveedor, total_estimado))

            # Obtener ID del pedido creado
            cursor.execute("SELECT @@IDENTITY")
            pedido_id = cursor.fetchone()[0]

            # Actualizar cantidades pedidas en vidrios_obra
            for vidrio in vidrios_lista:
                query_update = f"""
                    UPDATE {self.tabla_vidrios_obra}
                    SET metros_cuadrados_pedidos = metros_cuadrados_pedidos + ?
                    WHERE vidrio_id = ? AND obra_id = ?
                """
                cursor.execute(
                    query_update,
                    (vidrio["metros_cuadrados"], vidrio["vidrio_id"], obra_id),
                )

            self.db_connection.connection.commit()
            print(f"[VIDRIOS] Pedido {pedido_id} creado para obra {obra_id}")
            return pedido_id

        except Exception as e:
            print(f"[ERROR VIDRIOS] Error creando pedido: {e}")
            return None

    def obtener_estadisticas(self):
        """
        Obtiene estadísticas generales de vidrios.

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
            cursor = self.db_connection.connection.cursor()

            estadisticas = {}

            # Total de vidrios
            cursor.execute(
                f"SELECT COUNT(*) FROM {self.tabla_vidrios} WHERE estado = 'ACTIVO'"
            )
            estadisticas["total_vidrios"] = cursor.fetchone()[0]

            # Tipos de vidrio disponibles
            cursor.execute(
                f"SELECT COUNT(DISTINCT tipo) FROM {self.tabla_vidrios} WHERE estado = 'ACTIVO'"
            )
            estadisticas["tipos_disponibles"] = cursor.fetchone()[0]

            # Proveedores activos
            cursor.execute(
                f"SELECT COUNT(DISTINCT proveedor) FROM {self.tabla_vidrios} WHERE estado = 'ACTIVO'"
            )
            estadisticas["proveedores_activos"] = cursor.fetchone()[0]

            # Valor total del inventario (estimado por m2)
            cursor.execute(
                f"SELECT SUM(precio_m2) FROM {self.tabla_vidrios} WHERE estado = 'ACTIVO'"
            )
            resultado = cursor.fetchone()[0]
            estadisticas["valor_total_inventario"] = resultado or 0.0

            # Vidrios por tipo
            cursor.execute(f"""
                SELECT tipo, COUNT(*) as cantidad
                FROM {self.tabla_vidrios}
                WHERE estado = 'ACTIVO'
                GROUP BY tipo
                ORDER BY cantidad DESC
            """)
            estadisticas["vidrios_por_tipo"] = [
                {"tipo": row[0], "cantidad": row[1]} for row in cursor.fetchall()
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

    def buscar_vidrios(self, termino_busqueda):
        """
        Busca vidrios por término de búsqueda.

        Args:
            termino_busqueda (str): Término a buscar

        Returns:
            List[Dict]: Lista de vidrios que coinciden
        """
        if not self.db_connection or not termino_busqueda:
            return []

        try:
            cursor = self.db_connection.connection.cursor()

            query = f"""
                SELECT
                    id, codigo, descripcion, tipo, espesor, proveedor,
                    precio_m2, color, tratamiento, estado
                FROM {self.tabla_vidrios}
                WHERE
                    (codigo LIKE ? OR
                     descripcion LIKE ? OR
                     tipo LIKE ? OR
                     proveedor LIKE ?)
                    AND estado = 'ACTIVO'
                ORDER BY tipo, espesor
            """

            termino = f"%{termino_busqueda}%"
            cursor.execute(query, (termino, termino, termino, termino))
            columnas = [column[0] for column in cursor.description]
            resultados = cursor.fetchall()

            vidrios = []
            for fila in resultados:
                vidrio = dict(zip(columnas, fila))
                vidrios.append(vidrio)

            return vidrios

        except Exception as e:
            print(f"[ERROR VIDRIOS] Error buscando vidrios: {e}")
            return []

    def crear_vidrio(self, datos_vidrio):
        """
        Crea un nuevo vidrio en la base de datos.

        Args:
            datos_vidrio (dict): Datos del vidrio a crear

        Returns:
            int: ID del vidrio creado o None si falla
        """
        if not self.db_connection:
            return None

        try:
            cursor = self.db_connection.connection.cursor()

            query = f"""
                INSERT INTO {self.tabla_vidrios}
                (codigo, descripcion, tipo, espesor, proveedor, precio_m2, 
                 color, tratamiento, dimensiones_disponibles, estado, observaciones, fecha_actualizacion)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE())
            """

            cursor.execute(query, (
                datos_vidrio.get('codigo', ''),
                datos_vidrio.get('descripcion', ''),
                datos_vidrio.get('tipo', ''),
                datos_vidrio.get('espesor', 0),
                datos_vidrio.get('proveedor', ''),
                datos_vidrio.get('precio_m2', 0),
                datos_vidrio.get('color', ''),
                datos_vidrio.get('tratamiento', ''),
                datos_vidrio.get('dimensiones_disponibles', ''),
                datos_vidrio.get('estado', 'ACTIVO'),
                datos_vidrio.get('observaciones', '')
            ))

            # Obtener ID del vidrio creado
            cursor.execute("SELECT @@IDENTITY")
            vidrio_id = cursor.fetchone()[0]

            self.db_connection.connection.commit()
            print(f"[VIDRIOS] Vidrio creado con ID: {vidrio_id}")
            return vidrio_id

        except Exception as e:
            print(f"[ERROR VIDRIOS] Error creando vidrio: {e}")
            if self.db_connection:
                self.db_connection.connection.rollback()
            return None

    def actualizar_vidrio(self, vidrio_id, datos_vidrio):
        """
        Actualiza un vidrio existente.

        Args:
            vidrio_id (int): ID del vidrio a actualizar
            datos_vidrio (dict): Nuevos datos del vidrio

        Returns:
            bool: True si fue exitoso
        """
        if not self.db_connection:
            return False

        try:
            cursor = self.db_connection.connection.cursor()

            query = f"""
                UPDATE {self.tabla_vidrios}
                SET codigo = ?, descripcion = ?, tipo = ?, espesor = ?, proveedor = ?,
                    precio_m2 = ?, color = ?, tratamiento = ?, dimensiones_disponibles = ?,
                    estado = ?, observaciones = ?, fecha_actualizacion = GETDATE()
                WHERE id = ?
            """

            cursor.execute(query, (
                datos_vidrio.get('codigo', ''),
                datos_vidrio.get('descripcion', ''),
                datos_vidrio.get('tipo', ''),
                datos_vidrio.get('espesor', 0),
                datos_vidrio.get('proveedor', ''),
                datos_vidrio.get('precio_m2', 0),
                datos_vidrio.get('color', ''),
                datos_vidrio.get('tratamiento', ''),
                datos_vidrio.get('dimensiones_disponibles', ''),
                datos_vidrio.get('estado', 'ACTIVO'),
                datos_vidrio.get('observaciones', ''),
                vidrio_id
            ))

            self.db_connection.connection.commit()
            print(f"[VIDRIOS] Vidrio {vidrio_id} actualizado exitosamente")
            return True

        except Exception as e:
            print(f"[ERROR VIDRIOS] Error actualizando vidrio: {e}")
            if self.db_connection:
                self.db_connection.connection.rollback()
            return False

    def eliminar_vidrio(self, vidrio_id):
        """
        Elimina un vidrio (marca como inactivo).

        Args:
            vidrio_id (int): ID del vidrio a eliminar

        Returns:
            bool: True si fue exitoso
        """
        if not self.db_connection:
            return False

        try:
            cursor = self.db_connection.connection.cursor()

            # Verificar si el vidrio está asignado a alguna obra
            cursor.execute(
                f"SELECT COUNT(*) FROM {self.tabla_vidrios_obra} WHERE vidrio_id = ?",
                (vidrio_id,)
            )
            
            if cursor.fetchone()[0] > 0:
                print(f"[ADVERTENCIA] El vidrio {vidrio_id} está asignado a obras, se marcará como inactivo")
                # Marcar como inactivo en lugar de eliminar
                query = f"""
                    UPDATE {self.tabla_vidrios}
                    SET estado = 'INACTIVO', fecha_actualizacion = GETDATE()
                    WHERE id = ?
                """
                cursor.execute(query, (vidrio_id,))
            else:
                # Eliminar completamente si no está asignado
                query = f"DELETE FROM {self.tabla_vidrios} WHERE id = ?"
                cursor.execute(query, (vidrio_id,))

            self.db_connection.connection.commit()
            print(f"[VIDRIOS] Vidrio {vidrio_id} eliminado exitosamente")
            return True

        except Exception as e:
            print(f"[ERROR VIDRIOS] Error eliminando vidrio: {e}")
            if self.db_connection:
                self.db_connection.connection.rollback()
            return False

    def obtener_vidrio_por_id(self, vidrio_id):
        """
        Obtiene un vidrio específico por su ID.

        Args:
            vidrio_id (int): ID del vidrio

        Returns:
            dict: Datos del vidrio o None si no existe
        """
        if not self.db_connection:
            return None

        try:
            cursor = self.db_connection.connection.cursor()

            query = f"""
                SELECT
                    id, codigo, descripcion, tipo, espesor, proveedor,
                    precio_m2, color, tratamiento, dimensiones_disponibles,
                    estado, observaciones, fecha_actualizacion
                FROM {self.tabla_vidrios}
                WHERE id = ?
            """

            cursor.execute(query, (vidrio_id,))
            columnas = [column[0] for column in cursor.description]
            resultado = cursor.fetchone()

            if resultado:
                return dict(zip(columnas, resultado))
            return None

        except Exception as e:
            print(f"[ERROR VIDRIOS] Error obteniendo vidrio por ID: {e}")
            return None
    
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
                "observaciones": "Vidrio para puertas principales"
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
                "observaciones": "Vidrio de seguridad para fachadas"
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
                "observaciones": "Vidrio estándar para ventanas"
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
                "observaciones": "Espejo decorativo para baños"
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
                "observaciones": "Vidrio especial para divisiones"
            }
        ]
