"""
Modelo de Herrajes

Maneja la lógica de negocio y acceso a datos para herrajes.
Gestiona la compra por obra y asociación con proveedores.
"""


class HerrajesModel:
    """Modelo para gestionar herrajes por obra y proveedor."""

    def __init__(self, db_connection=None):
        """
        Inicializa el modelo de herrajes.

        Args:
            db_connection: Conexión a la base de datos
        """
        self.db_connection = db_connection
        self.tabla_herrajes = "herrajes"  # Tabla principal de herrajes en DB inventario
        self.tabla_herrajes_obra = (
            "herrajes_obra"  # Tabla para asociar herrajes con obras
        )
        self.tabla_pedidos_herrajes = "pedidos_herrajes"  # Tabla para pedidos por obra
        self._verificar_tablas()

    def _verificar_tablas(self):
        """Verifica que las tablas necesarias existan en la base de datos."""
        if not self.db_connection:
            return

        try:
            cursor = self.db_connection.connection.cursor()

            # Verificar tabla principal de herrajes
            cursor.execute(
                "SELECT * FROM sysobjects WHERE name=? AND xtype='U'",
                (self.tabla_herrajes,),
            )
            if cursor.fetchone():
                print(
                    f"[HERRAJES] Tabla '{self.tabla_herrajes}' verificada correctamente."
                )

                # Obtener estructura de la tabla
                cursor.execute(
                    "SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = ?",
                    (self.tabla_herrajes,),
                )
                columnas = cursor.fetchall()
                print(f"[HERRAJES] Estructura de tabla '{self.tabla_herrajes}':")
                for columna in columnas:
                    print(f"  - {columna[0]}: {columna[1]}")
            else:
                print(
                    f"[ADVERTENCIA] La tabla '{self.tabla_herrajes}' no existe en la base de datos."
                )

            # Verificar tabla de herrajes por obra
            cursor.execute(
                "SELECT * FROM sysobjects WHERE name=? AND xtype='U'",
                (self.tabla_herrajes_obra,),
            )
            if cursor.fetchone():
                print(
                    f"[HERRAJES] Tabla '{self.tabla_herrajes_obra}' verificada correctamente."
                )
            else:
                print(
                    f"[ADVERTENCIA] La tabla '{self.tabla_herrajes_obra}' no existe en la base de datos."
                )

        except Exception as e:
            print(f"[ERROR HERRAJES] Error verificando tablas: {e}")

    def obtener_todos_herrajes(self, filtros=None):
        """
        Obtiene todos los herrajes disponibles.

        Args:
            filtros (dict): Filtros opcionales (proveedor, codigo, descripcion)

        Returns:
            List[Dict]: Lista de herrajes
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

                if filtros.get("codigo"):
                    conditions.append("codigo LIKE ?")
                    params.append(f"%{filtros['codigo']}%")

                if filtros.get("descripcion"):
                    conditions.append("descripcion LIKE ?")
                    params.append(f"%{filtros['descripcion']}%")

            query = f"""
                SELECT
                    id, codigo, descripcion, proveedor, precio_unitario,
                    unidad_medida, categoria, estado, observaciones,
                    fecha_actualizacion
                FROM {self.tabla_herrajes}
                WHERE {" AND ".join(conditions)}
                ORDER BY codigo
            """

            cursor.execute(query, params)
            columnas = [column[0] for column in cursor.description]
            resultados = cursor.fetchall()

            herrajes = []
            for fila in resultados:
                herraje = dict(zip(columnas, fila))
                herrajes.append(herraje)

            return herrajes

        except Exception as e:
            print(f"[ERROR HERRAJES] Error obteniendo herrajes: {e}")
            return []

    def obtener_herrajes_por_obra(self, obra_id):
        """
        Obtiene herrajes asociados a una obra específica.

        Args:
            obra_id (int): ID de la obra

        Returns:
            List[Dict]: Lista de herrajes con cantidades asignadas
        """
        if not self.db_connection:
            return []

        try:
            cursor = self.db_connection.connection.cursor()

            query = f"""
                SELECT
                    h.id, h.codigo, h.descripcion, h.proveedor, h.precio_unitario,
                    h.unidad_medida, ho.cantidad_requerida, ho.cantidad_pedida,
                    ho.fecha_asignacion, ho.observaciones as obs_obra
                FROM {self.tabla_herrajes} h
                INNER JOIN {self.tabla_herrajes_obra} ho ON h.id = ho.herraje_id
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

    def asignar_herraje_obra(
        self, herraje_id, obra_id, cantidad_requerida, observaciones=None
    ):
        """
        Asigna un herraje a una obra específica.

        Args:
            herraje_id (int): ID del herraje
            obra_id (int): ID de la obra
            cantidad_requerida (float): Cantidad requerida
            observaciones (str): Observaciones opcionales

        Returns:
            bool: True si fue exitoso
        """
        if not self.db_connection:
            return False

        try:
            cursor = self.db_connection.connection.cursor()

            query = f"""
                INSERT INTO {self.tabla_herrajes_obra}
                (herraje_id, obra_id, cantidad_requerida, fecha_asignacion, observaciones)
                VALUES (?, ?, ?, GETDATE(), ?)
            """

            cursor.execute(
                query, (herraje_id, obra_id, cantidad_requerida, observaciones)
            )
            self.db_connection.connection.commit()

            print(f"[HERRAJES] Herraje {herraje_id} asignado a obra {obra_id}")
            return True

        except Exception as e:
            print(f"[ERROR HERRAJES] Error asignando herraje a obra: {e}")
            return False

    def crear_pedido_obra(self, obra_id, proveedor, herrajes_lista):
        """
        Crea un pedido de herrajes para una obra específica.

        Args:
            obra_id (int): ID de la obra
            proveedor (str): Nombre del proveedor
            herrajes_lista (List[Dict]): Lista de herrajes con cantidades

        Returns:
            int: ID del pedido creado o None si falla
        """
        if not self.db_connection:
            return None

        try:
            cursor = self.db_connection.connection.cursor()

            # Crear pedido principal
            query_pedido = f"""
                INSERT INTO {self.tabla_pedidos_herrajes}
                (obra_id, proveedor, fecha_pedido, estado, total_estimado)
                VALUES (?, ?, GETDATE(), 'PENDIENTE', ?)
            """

            total_estimado = sum(
                item["cantidad"] * item["precio_unitario"] for item in herrajes_lista
            )
            cursor.execute(query_pedido, (obra_id, proveedor, total_estimado))

            # Obtener ID del pedido creado
            cursor.execute("SELECT @@IDENTITY")
            pedido_id = cursor.fetchone()[0]

            # Actualizar cantidades pedidas en herrajes_obra
            for herraje in herrajes_lista:
                query_update = f"""
                    UPDATE {self.tabla_herrajes_obra}
                    SET cantidad_pedida = cantidad_pedida + ?
                    WHERE herraje_id = ? AND obra_id = ?
                """
                cursor.execute(
                    query_update, (herraje["cantidad"], herraje["herraje_id"], obra_id)
                )

            self.db_connection.connection.commit()
            print(f"[HERRAJES] Pedido {pedido_id} creado para obra {obra_id}")
            return pedido_id

        except Exception as e:
            print(f"[ERROR HERRAJES] Error creando pedido: {e}")
            return None

    def obtener_estadisticas(self):
        """
        Obtiene estadísticas generales de herrajes.

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
            cursor = self.db_connection.connection.cursor()

            estadisticas = {}

            # Total de herrajes
            cursor.execute(
                f"SELECT COUNT(*) FROM {self.tabla_herrajes} WHERE estado = 'ACTIVO'"
            )
            estadisticas["total_herrajes"] = cursor.fetchone()[0]

            # Proveedores activos
            cursor.execute(
                f"SELECT COUNT(DISTINCT proveedor) FROM {self.tabla_herrajes} WHERE estado = 'ACTIVO'"
            )
            estadisticas["proveedores_activos"] = cursor.fetchone()[0]

            # Valor total del inventario (estimado)
            cursor.execute(
                f"SELECT SUM(precio_unitario) FROM {self.tabla_herrajes} WHERE estado = 'ACTIVO'"
            )
            resultado = cursor.fetchone()[0]
            estadisticas["valor_total_inventario"] = resultado or 0.0

            # Herrajes por proveedor
            cursor.execute(f"""
                SELECT proveedor, COUNT(*) as cantidad
                FROM {self.tabla_herrajes}
                WHERE estado = 'ACTIVO'
                GROUP BY proveedor
                ORDER BY cantidad DESC
            """)
            estadisticas["herrajes_por_proveedor"] = [
                {"proveedor": row[0], "cantidad": row[1]} for row in cursor.fetchall()
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

    def buscar_herrajes(self, termino_busqueda):
        """
        Busca herrajes por término de búsqueda.

        Args:
            termino_busqueda (str): Término a buscar

        Returns:
            List[Dict]: Lista de herrajes que coinciden
        """
        if not self.db_connection or not termino_busqueda:
            return []

        try:
            cursor = self.db_connection.connection.cursor()

            query = f"""
                SELECT
                    id, codigo, descripcion, proveedor, precio_unitario,
                    unidad_medida, categoria, estado
                FROM {self.tabla_herrajes}
                WHERE
                    (codigo LIKE ? OR
                     descripcion LIKE ? OR
                     proveedor LIKE ?)
                    AND estado = 'ACTIVO'
                ORDER BY codigo
            """

            termino = f"%{termino_busqueda}%"
            cursor.execute(query, (termino, termino, termino))
            columnas = [column[0] for column in cursor.description]
            resultados = cursor.fetchall()

            herrajes = []
            for fila in resultados:
                herraje = dict(zip(columnas, fila))
                herrajes.append(herraje)

            return herrajes

        except Exception as e:
            print(f"[ERROR HERRAJES] Error buscando herrajes: {e}")
            return []
