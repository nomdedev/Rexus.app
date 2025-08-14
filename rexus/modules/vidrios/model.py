from rexus.core.auth_decorators import (
    admin_required,
    auth_required,
)

# [LOCK] DB Authorization Check - Verify user permissions before DB operations
# Ensure all database operations are properly authorized
# DB Authorization Check
"""
Modelo de Vidrios - Rexus.app v2.0.0

Maneja la lógica de negocio y acceso a datos para vidrios.
Gestiona la compra por obra y asociación con proveedores.
Incluye utilidades de seguridad integradas.
"""

# Constantes del módulo
NO_CONNECTION_MSG = "No hay conexión a la base de datos"
DB_ERROR_MSG = "Error en la base de datos"
INVALID_DATA_MSG = "Datos inválidos"


# Importar utilidades requeridas
from rexus.utils.sql_script_loader import sql_script_loader
from rexus.utils.unified_sanitizer import sanitize_string

# Importar sistema unificado de sanitización
try:
    from rexus.utils.unified_sanitizer import unified_sanitizer as data_sanitizer
    SANITIZER_AVAILABLE = True
    print("OK [VIDRIOS] Sistema unificado de sanitización cargado")
except ImportError:
    try:
        data_sanitizer = DataSanitizer()
        SANITIZER_AVAILABLE = True
        print("OK [VIDRIOS] DataSanitizer legacy cargado")
    except ImportError:
        print("ERROR [VIDRIOS] No se pudo cargar ningún sistema de sanitización")
        SANITIZER_AVAILABLE = False
        data_sanitizer = None


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

        # Configurar cargador de scripts SQL
        self.sql_loader = sql_script_loader

        # Inicializar utilidades de seguridad
        self.sanitizer_available = SANITIZER_AVAILABLE
        if self.sanitizer_available:
            self.data_sanitizer = data_sanitizer
            print("OK [VIDRIOS] Sanitizador inicializado correctamente")
        else:
            self.data_sanitizer = None
            print("WARNING [VIDRIOS] Sin sistema de sanitización - funcionalidad limitada")

        if not self.db_connection:
            print(
                "[ERROR VIDRIOS] No hay conexión a la base de datos. El módulo no funcionará correctamente."
            )
        self._verificar_tablas()

    def _sanitizar_entrada_segura(self, value, tipo='string', **kwargs):
        """
        Sanitiza entrada de forma segura manejando la disponibilidad del sanitizador.

        Args:
            value: Valor a sanitizar
            tipo: Tipo de sanitización ('string', 'numeric', 'integer')
            **kwargs: Argumentos adicionales (max_length, min_val, max_val)

        Returns:
            Valor sanitizado o fallback seguro
        """
        if not self.sanitizer_available or not self.data_sanitizer:
            # Fallback seguro básico
            if tipo == 'string':
                if value is None:
                    return ""
                result = str(value).strip()
                max_length = kwargs.get('max_length')
                if max_length:
                    result = result[:max_length]
                return result
            elif tipo == 'numeric':
                try:
                    result = float(value) if value is not None else 0.0
                    min_val = kwargs.get('min_val')
                    max_val = kwargs.get('max_val')
                    if min_val is not None and result < min_val:
                        result = min_val
                    if max_val is not None and result > max_val:
                        result = max_val
                    return result
                except (ValueError, TypeError):
                    return 0.0
            elif tipo == 'integer':
                try:
                    result = int(float(value)) if value is not None else 0
                    min_val = kwargs.get('min_val')
                    max_val = kwargs.get('max_val')
                    if min_val is not None and result < min_val:
                        result = min_val
                    if max_val is not None and result > max_val:
                        result = max_val
                    return result
                except (ValueError, TypeError):
                    return 0
            else:
                return value

        # Usar sanitizador disponible
        try:
            if tipo == 'string':
                return sanitize_string(value, kwargs.get('max_length'))
            elif tipo == 'numeric':
                return self.data_sanitizer.sanitize_numeric(value, kwargs.get('min_val'), kwargs.get('max_val'))
            elif tipo == 'integer':
                return self.data_sanitizer.sanitize_integer(value, kwargs.get('min_val'), kwargs.get('max_val'))
            else:
                return value
        except Exception as e:
            print(f"[ERROR VIDRIOS] Error en sanitización: {e}")
            # Fallback en caso de error
            return self._sanitizar_entrada_segura(value, tipo, **kwargs)

    def _sanitizar_datos_vidrio(self, datos_vidrio: dict) -> dict:
        """
        Sanitiza todos los datos de un vidrio de forma centralizada.

        Args:
            datos_vidrio: Diccionario con datos del vidrio a sanitizar

        Returns:
            Diccionario con datos sanitizados
        """
        datos_limpios = {}

        # Sanitizar strings con longitudes apropiadas
        datos_limpios["codigo"] = self._sanitizar_entrada_segura(
            datos_vidrio.get("codigo", ""), 'string', max_length=20
        )
        datos_limpios["descripcion"] = self._sanitizar_entrada_segura(
            datos_vidrio.get("descripcion", ""), 'string', max_length=200
        )
        datos_limpios["tipo"] = self._sanitizar_entrada_segura(
            datos_vidrio.get("tipo", ""), 'string', max_length=50
        )
        datos_limpios["proveedor"] = self._sanitizar_entrada_segura(
            datos_vidrio.get("proveedor", ""), 'string', max_length=100
        )
        datos_limpios["color"] = self._sanitizar_entrada_segura(
            datos_vidrio.get("color", ""), 'string', max_length=50
        )
        datos_limpios["tratamiento"] = self._sanitizar_entrada_segura(
            datos_vidrio.get("tratamiento", ""), 'string', max_length=50
        )
        datos_limpios["dimensiones_especiales"] = self._sanitizar_entrada_segura(
            datos_vidrio.get("dimensiones_especiales",
""),
                'string',
                max_length=100
        )
        datos_limpios["estado"] = self._sanitizar_entrada_segura(
            datos_vidrio.get("estado", "ACTIVO"), 'string', max_length=20
        )
        datos_limpios["observaciones"] = self._sanitizar_entrada_segura(
            datos_vidrio.get("observaciones", ""), 'string', max_length=500
        )

        # Sanitizar valores numéricos
        datos_limpios["espesor"] = self._sanitizar_entrada_segura(
            datos_vidrio.get("espesor", 0), 'numeric', min_val=0, max_val=100
        )

        # Manejar precios (pueden ser múltiples)
        for campo_precio in ["precio_unitario", "precio_metro2", "precio_compra"]:
            if campo_precio in datos_vidrio:
                precio_limpio = self._sanitizar_entrada_segura(
                    datos_vidrio[campo_precio], 'numeric', min_val=0, max_val=999999.99
                )
                datos_limpios[campo_precio] = precio_limpio

        return datos_limpios

    def _validate_table_name(self, table_name: str) -> str:
        """
        Valida el nombre de tabla para prevenir SQL injection.

        Args:
            table_name: Nombre de tabla a validar

        Returns:
            Nombre de tabla validado

        Raises:
            ValueError: Si el nombre de tabla no es válido
        """
        import re

        # Solo permitir nombres alfanuméricos y underscore
        if not re.match(r"^[a-zA-Z_]\w*$", table_name):
            raise ValueError(f"Nombre de tabla inválido: {table_name}")

        # Lista blanca de tablas permitidas
        allowed_tables = {"vidrios", "vidrios_obra", "pedidos_vidrios"}
        if table_name not in allowed_tables:
            raise ValueError(f"Tabla no permitida: {table_name}")

        return table_name

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

            # Usar script SQL externo
            script_content = self.sql_loader.load_script(
                "vidrios/select_vidrios_filtered"
            )
            # Construir query completa con filtros dinámicos
            where_clause = " AND ".join(conditions)
            query = script_content.replace("WHERE 1=1", f"WHERE {where_clause}")
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

            # Usar script SQL externo
            script_content = self.sql_loader.load_script(
                "vidrios/select_vidrios_por_obra"
            )
            cursor.execute(script_content, (obra_id,))
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

    @auth_required
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

            query = """
                INSERT INTO vidrios_obra
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

    @auth_required
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
            query_pedido = """
                INSERT INTO pedidos_vidrios
                (obra_id, proveedor, fecha_pedido, estado, total_estimado)
                VALUES (?, ?, GETDATE(), 'PENDIENTE', ?)
            """

            total_estimado = sum(
                item["metros_cuadrados"] * item["precio_m2"] for item in vidrios_lista
            )
            cursor.execute(query_pedido, (obra_id, proveedor, total_estimado))

            # Obtener ID del pedido creado
            cursor.execute("SELECT SCOPE_IDENTITY()")
            pedido_id = cursor.fetchone()[0]

            # Actualizar cantidades pedidas en vidrios_obra
            for vidrio in vidrios_lista:
                # Usar script SQL externo
                script_content = self.sql_loader.load_script(
                    "vidrios/update_metros_pedidos"
                )
                cursor.execute(
                    script_content,
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
            cursor.execute("SELECT COUNT(*) FROM vidrios WHERE estado = 'ACTIVO'")
            estadisticas["total_vidrios"] = cursor.fetchone()[0]

            # Tipos de vidrio disponibles
            cursor.execute(
                "SELECT COUNT(DISTINCT tipo) FROM vidrios WHERE estado = 'ACTIVO'"
            )
            estadisticas["tipos_disponibles"] = cursor.fetchone()[0]

            # Proveedores activos
            cursor.execute(
                "SELECT COUNT(DISTINCT proveedor) FROM vidrios WHERE estado = 'ACTIVO'"
            )
            estadisticas["proveedores_activos"] = cursor.fetchone()[0]

            # Valor total del inventario (estimado por m2)
            cursor.execute("SELECT SUM(precio_m2) FROM vidrios WHERE estado = 'ACTIVO'")
            resultado = cursor.fetchone()[0]
            estadisticas["valor_total_inventario"] = resultado or 0.0

            # Vidrios por tipo usando script SQL externo
            script_content = self.sql_loader.load_script(
                "vidrios/select_estadisticas_tipos"
            )
            cursor.execute(script_content)
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
        Busca vidrios por término de búsqueda con sanitización de entrada.

        Args:
            termino_busqueda (str): Término a buscar

        Returns:
            tuple: (bool, list) - (éxito, lista de vidrios que coinciden)
        """
        if not self.db_connection or not termino_busqueda:
            return True, []

        try:
            # Sanitizar término de búsqueda
            termino_limpio = self._sanitizar_entrada_segura(
                termino_busqueda, 'string', max_length=100
            )

            if not termino_limpio:
                return False, []

            print(f"[VIDRIOS] Búsqueda sanitizada: '{termino_limpio}'")

            cursor = self.db_connection.connection.cursor()

            termino = f"%{termino_limpio}%"

            # Usar script SQL externo
            script_content = self.sql_loader.load_script("vidrios/buscar_vidrios")
            cursor.execute(script_content,
(termino,
                termino,
                termino,
                termino))
            columnas = [column[0] for column in cursor.description]
            resultados = cursor.fetchall()

            vidrios = []
            for fila in resultados:
                vidrio = dict(zip(columnas, fila))
                vidrios.append(vidrio)

            print(
                f"[VIDRIOS] Encontrados {len(vidrios)} vidrios para '{termino_limpio}'"
            )
            return True, vidrios

        except Exception as e:
            print(f"[ERROR VIDRIOS] Error buscando vidrios: {e}")
            return False, []

    @auth_required
    def crear_vidrio(self, datos_vidrio):
        """
        Crea un nuevo vidrio en la base de datos con sanitización completa.

        Args:
            datos_vidrio (dict): Datos del vidrio a crear

        Returns:
            tuple: (bool, str, int) - (éxito, mensaje, ID del vidrio creado)
        """
        if not self.db_connection:
            return False, NO_CONNECTION_MSG, None

        try:
            # Sanitizar y validar todos los datos usando función centralizada
            datos_limpios = self._sanitizar_datos_vidrio(datos_vidrio)

            # Validación específica de precio que no está en la función centralizada
            precio_original = datos_vidrio.get("precio_m2")
            if precio_original and precio_original != "":
                precio_limpio = self._sanitizar_entrada_segura(
                    precio_original, 'numeric', min_val=0
                )
                if precio_limpio is None:
                    return False, "Precio por m2 inválido", None
                datos_limpios["precio_m2"] = precio_limpio
            else:
                datos_limpios["precio_m2"] = 0.0

            # Validaciones de campos obligatorios
            if not datos_limpios["codigo"]:
                return False, "El código del vidrio es obligatorio", None
            if not datos_limpios["descripcion"]:
                return False, "La descripción del vidrio es obligatoria", None
            if not datos_limpios["tipo"]:
                return False, "El tipo de vidrio es obligatorio", None
            if not datos_limpios["proveedor"]:
                return False, "El proveedor es obligatorio", None

            print(
                f"[VIDRIOS] Creando vidrio: {datos_limpios['codigo']} - {datos_limpios['descripcion']}"
            )

            cursor = self.db_connection.connection.cursor()

            # Usar script SQL externo
            script_content = self.sql_loader.load_script("vidrios/insert_vidrio_nuevo")
            cursor.execute(
                script_content,
                (
                    datos_limpios["codigo"],
                    datos_limpios["descripcion"],
                    datos_limpios["tipo"],
                    datos_limpios["espesor"],
                    datos_limpios["proveedor"],
                    datos_limpios["precio_m2"],
                    datos_limpios["color"],
                    datos_limpios["tratamiento"],
                    datos_limpios["dimensiones_disponibles"],
                    datos_limpios["estado"],
                    datos_limpios["observaciones"],
                ),
            )

            # Obtener ID del vidrio creado
            cursor.execute("SELECT SCOPE_IDENTITY()")
            vidrio_id = cursor.fetchone()[0]

            self.db_connection.connection.commit()
            print(f"[VIDRIOS] Vidrio creado exitosamente con ID: {vidrio_id}")
            return (
                True,
                f"Vidrio '{datos_limpios['codigo']}' creado exitosamente",
                vidrio_id,
            )

        except Exception as e:
            print(f"[ERROR VIDRIOS] Error creando vidrio: {e}")
            if self.db_connection:
                self.db_connection.connection.rollback()
            return False, f"Error creando vidrio: {str(e)}", None

    @auth_required
    def actualizar_vidrio(self, vidrio_id, datos_vidrio):
        """
        Actualiza un vidrio existente con sanitización completa.

        Args:
            vidrio_id (int): ID del vidrio a actualizar
            datos_vidrio (dict): Nuevos datos del vidrio

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

            # Sanitizar y validar todos los datos igual que en crear_vidrio
            datos_limpios = {}

            datos_limpios["codigo"] = sanitize_string(
                datos_vidrio.get("codigo", ""), max_length=20
            )
            datos_limpios["descripcion"] = sanitize_string(
                datos_vidrio.get("descripcion", ""), max_length=200
            )
            datos_limpios["tipo"] = sanitize_string(
                datos_vidrio.get("tipo", ""), max_length=50
            )
            datos_limpios["proveedor"] = sanitize_string(
                datos_vidrio.get("proveedor", ""), max_length=100
            )
            datos_limpios["color"] = sanitize_string(
                datos_vidrio.get("color", ""), max_length=50
            )
            datos_limpios["tratamiento"] = sanitize_string(
                datos_vidrio.get("tratamiento", ""), max_length=100
            )
            datos_limpios["dimensiones_disponibles"] = (
                sanitize_string(
                    datos_vidrio.get("dimensiones_disponibles", ""), max_length=200
                )
            )
            datos_limpios["estado"] = sanitize_string(
                datos_vidrio.get("estado", "ACTIVO"), max_length=20
            )
            datos_limpios["observaciones"] = sanitize_string(
                datos_vidrio.get("observaciones", ""), max_length=500
            )

            datos_limpios["espesor"] = self.data_sanitizer.sanitize_numeric(
                datos_vidrio.get("espesor", 0), min_val=0, max_val=50
            )

            # Validar precio
            precio_original = datos_vidrio.get("precio_m2")
            if precio_original and precio_original != "":
                precio_limpio = self.data_sanitizer.sanitize_numeric(
                    precio_original, min_val=0
                )
                if precio_limpio is None:
                    return False, "Precio por m2 inválido"
                datos_limpios["precio_m2"] = precio_limpio
            else:
                datos_limpios["precio_m2"] = 0.0

            # Validaciones de campos obligatorios
            if not datos_limpios["codigo"]:
                return False, "El código del vidrio es obligatorio"
            if not datos_limpios["descripcion"]:
                return False, "La descripción del vidrio es obligatoria"

            print(
                f"[VIDRIOS] Actualizando vidrio ID {vidrio_id_limpio}: {datos_limpios['codigo']}"
            )

            cursor = self.db_connection.connection.cursor()

            # Usar script SQL externo
            script_content = self.sql_loader.load_script("vidrios/update_vidrio")
            cursor.execute(
                script_content,
                (
                    datos_limpios["codigo"],
                    datos_limpios["descripcion"],
                    datos_limpios["tipo"],
                    datos_limpios["espesor"],
                    datos_limpios["proveedor"],
                    datos_limpios["precio_m2"],
                    datos_limpios["color"],
                    datos_limpios["tratamiento"],
                    datos_limpios["dimensiones_disponibles"],
                    datos_limpios["estado"],
                    datos_limpios["observaciones"],
                    vidrio_id_limpio,
                ),
            )

            self.db_connection.connection.commit()
            print(f"[VIDRIOS] Vidrio {vidrio_id_limpio} actualizado exitosamente")
            return True, f"Vidrio '{datos_limpios['codigo']}' actualizado exitosamente"

        except Exception as e:
            print(f"[ERROR VIDRIOS] Error actualizando vidrio: {e}")
            if self.db_connection:
                self.db_connection.connection.rollback()
            return False, f"Error actualizando vidrio: {str(e)}"

    @admin_required
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

            # Verificar si el vidrio existe usando script SQL externo
            script_content = self.sql_loader.load_script("vidrios/select_vidrio_info")
            cursor.execute(script_content, (vidrio_id_limpio,))

            vidrio_info = cursor.fetchone()
            if not vidrio_info:
                return False, f"Vidrio con ID {vidrio_id_limpio} no encontrado"

            codigo, _ = vidrio_info

            # Verificar si el vidrio está asignado a alguna obra usando script SQL externo
            script_content = self.sql_loader.load_script("vidrios/count_vidrio_obras")
            cursor.execute(script_content, (vidrio_id_limpio,))

            if cursor.fetchone()[0] > 0:
                print(
                    f"[ADVERTENCIA] El vidrio {vidrio_id_limpio} está asignado a obras, se marcará como inactivo"
                )
                # Marcar como inactivo en lugar de eliminar usando script SQL externo
                script_content = self.sql_loader.load_script(
                    "vidrios/update_vidrio_inactivo"
                )
                cursor.execute(script_content, (vidrio_id_limpio,))
                mensaje = (
                    f"Vidrio '{codigo}' marcado como inactivo (estaba asignado a obras)"
                )
            else:
                # Eliminar completamente si no está asignado usando script SQL externo
                script_content = self.sql_loader.load_script("vidrios/delete_vidrio")
                cursor.execute(script_content, (vidrio_id_limpio,))
                mensaje = f"Vidrio '{codigo}' eliminado completamente"

            self.db_connection.connection.commit()
            print(f"[VIDRIOS] {mensaje}")
            return True, mensaje

        except Exception as e:
            print(f"[ERROR VIDRIOS] Error eliminando vidrio: {e}")
            if self.db_connection:
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

            # Usar script SQL externo
            script_content = self.sql_loader.load_script("vidrios/select_vidrio_por_id")
            cursor.execute(script_content, (vidrio_id_limpio,))
            columnas = [column[0] for column in cursor.description]
            resultado = cursor.fetchone()

            if resultado:
                vidrio_data = dict(zip(columnas, resultado))
                return True, vidrio_data
            return False, None

        except Exception as e:
            print(f"[ERROR VIDRIOS] Error obteniendo vidrio por ID: {e}")
            return False, None

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
