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
                WHERE {" AND ".join(conditions)}
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
