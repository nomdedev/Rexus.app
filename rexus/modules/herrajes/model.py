"""
Modelo de Herrajes - Rexus.app v2.0.0

Maneja la lógica de negocio y acceso a datos para herrajes.
Gestiona la compra por obra y asociación con proveedores.
Incluye utilidades de seguridad para prevenir SQL injection y XSS.
"""

import datetime
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Importar utilidades de seguridad
try:
    # Agregar ruta src al path para imports de seguridad
    root_dir = Path(__file__).parent.parent.parent.parent
    sys.path.insert(0, str(root_dir / "src"))
    
    from utils.data_sanitizer import DataSanitizer, data_sanitizer
    from utils.sql_security import SQLSecurityValidator, SecureSQLBuilder
    
    SECURITY_AVAILABLE = True
except ImportError as e:
    print(f"[WARNING] Security utilities not available in herrajes: {e}")
    SECURITY_AVAILABLE = False


class HerrajesModel:
    """Modelo para gestionar herrajes por obra y proveedor."""

    # Tipos de herrajes
    TIPOS_HERRAJES = {
        "BISAGRA": "Bisagra",
        "CERRADURA": "Cerradura",
        "MANIJA": "Manija",
        "TORNILLO": "Tornillo",
        "RIEL": "Riel",
        "SOPORTE": "Soporte",
        "OTRO": "Otro",
    }

    # Estados de herrajes
    ESTADOS = {
        "ACTIVO": "Activo",
        "INACTIVO": "Inactivo",
        "DESCONTINUADO": "Descontinuado",
    }

    # Unidades de medida
    UNIDADES = {
        "UNIDAD": "Unidad",
        "PAR": "Par",
        "JUEGO": "Juego",
        "METRO": "Metro",
        "KILOGRAMO": "Kilogramo",
    }

    def __init__(self, db_connection=None):
        """
        Inicializa el modelo de herrajes.

        Args:
            db_connection: Conexión a la base de datos
        """
        self.db_connection = db_connection
        self.tabla_herrajes = "herrajes"
        self.tabla_herrajes_obra = "herrajes_obra"
        self.tabla_pedidos_herrajes = "pedidos_herrajes"
        self.tabla_herrajes_inventario = "herrajes_inventario"
        
        # Inicializar utilidades de seguridad
        self.security_available = SECURITY_AVAILABLE
        if self.security_available:
            self.data_sanitizer = data_sanitizer
            self.sql_validator = SQLSecurityValidator()
            print("OK [HERRAJES] Utilidades de seguridad cargadas")
        else:
            self.data_sanitizer = None
            self.sql_validator = None
            print("WARNING [HERRAJES] Utilidades de seguridad no disponibles")
            
        if not self.db_connection:
            print(
                "[ERROR HERRAJES] No hay conexión a la base de datos. El módulo no funcionará correctamente."
            )
        # Las tablas deben crearse por el DBA, no por la aplicación
        self._verificar_tablas()

    # ELIMINADO: _crear_tablas_si_no_existen() por razones de seguridad
    # Las tablas deben ser creadas por el DBA usando scripts externos,
    # nunca por la aplicación en tiempo de ejecución.
    def _verificar_tablas(self):
        """Verifica que las tablas necesarias existan en la base de datos."""
        if not self.db_connection:
            return

        try:
            cursor = self.db_connection.cursor()

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
            # Retornar datos demo si no hay conexión
            return self._get_herrajes_demo()

        try:
            cursor = self.db_connection.cursor()

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

            query = (
                f"""
                SELECT
                    id, codigo, descripcion, proveedor, precio_unitario,
                    unidad_medida, categoria, estado, observaciones,
                    fecha_actualizacion
                FROM {self.tabla_herrajes}
                WHERE """
                + " AND ".join(conditions)
                + """
                ORDER BY codigo
            """
            )

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
            cursor = self.db_connection.cursor()

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
            cursor = self.db_connection.cursor()

            query = (
                """
                INSERT INTO """
                + self.tabla_herrajes_obra
                + """
                (herraje_id, obra_id, cantidad_requerida, fecha_asignacion, observaciones)
                VALUES (?, ?, ?, GETDATE(), ?)
            """
            )

            cursor.execute(
                query, (herraje_id, obra_id, cantidad_requerida, observaciones)
            )
            self.db_connection.commit()

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
            cursor = self.db_connection.cursor()

            # Crear pedido principal
            query_pedido = (
                """
                INSERT INTO """
                + self.tabla_pedidos_herrajes
                + """
                (obra_id, proveedor, fecha_pedido, estado, total_estimado)
                VALUES (?, ?, GETDATE(), 'PENDIENTE', ?)
            """
            )

            total_estimado = sum(
                item["cantidad"] * item["precio_unitario"] for item in herrajes_lista
            )
            cursor.execute(query_pedido, (obra_id, proveedor, total_estimado))

            # Obtener ID del pedido creado
            cursor.execute("SELECT @@IDENTITY")
            pedido_id = cursor.fetchone()[0]

            # Actualizar cantidades pedidas en herrajes_obra
            for herraje in herrajes_lista:
                query_update = (
                    """
                    UPDATE """
                    + self.tabla_herrajes_obra
                    + """
                    SET cantidad_pedida = cantidad_pedida + ?
                    WHERE herraje_id = ? AND obra_id = ?
                """
                )
                cursor.execute(
                    query_update, (herraje["cantidad"], herraje["herraje_id"], obra_id)
                )

            self.db_connection.commit()
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
            cursor = self.db_connection.cursor()

            estadisticas = {}

            # Total de herrajes
            cursor.execute("SELECT COUNT(*) FROM herrajes WHERE estado = 'ACTIVO'")
            estadisticas["total_herrajes"] = cursor.fetchone()[0]

            # Proveedores activos
            cursor.execute(
                "SELECT COUNT(DISTINCT proveedor) FROM herrajes WHERE estado = 'ACTIVO'"
            )
            estadisticas["proveedores_activos"] = cursor.fetchone()[0]

            # Valor total del inventario (estimado)
            cursor.execute(
                "SELECT SUM(precio_unitario) FROM herrajes WHERE estado = 'ACTIVO'"
            )
            resultado = cursor.fetchone()[0]
            estadisticas["valor_total_inventario"] = resultado or 0.0

            # Herrajes por proveedor
            cursor.execute("""
                SELECT proveedor, COUNT(*) as cantidad
                FROM herrajes
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
        Busca herrajes por término de búsqueda con sanitización de entrada.

        Args:
            termino_busqueda (str): Término a buscar

        Returns:
            List[Dict]: Lista de herrajes que coinciden
        """
        if not self.db_connection or not termino_busqueda:
            return []

        try:
            # 🔒 SANITIZACIÓN DE ENTRADA
            if self.security_available and termino_busqueda:
                termino_limpio = self.data_sanitizer.sanitize_string(termino_busqueda, max_length=100)
                if not termino_limpio:
                    return []
            else:
                termino_limpio = termino_busqueda

            cursor = self.db_connection.cursor()

            query = """
                SELECT
                    id, codigo, descripcion, proveedor, precio_unitario,
                    unidad_medida, categoria, estado
                FROM herrajes
                WHERE
                    (codigo LIKE ? OR
                     descripcion LIKE ? OR
                     proveedor LIKE ?)
                    AND estado = 'ACTIVO'
                ORDER BY codigo
            """

            termino = f"%{termino_limpio}%"
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

    def crear_herraje(self, datos_herraje: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Crea un nuevo herraje con sanitización completa de datos.

        Args:
            datos_herraje: Datos del herraje a crear

        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        if not self.db_connection:
            return False, "Sin conexión a la base de datos"

        try:
            # 🔒 SANITIZACIÓN Y VALIDACIÓN DE DATOS
            if self.security_available:
                # Sanitizar todos los datos de entrada
                datos_limpios = self.data_sanitizer.sanitize_form_data(datos_herraje)
                
                # Validaciones específicas
                if not datos_limpios.get("codigo"):
                    return False, "El código es requerido"
                if not datos_limpios.get("descripcion"):
                    return False, "La descripción es requerida"
                if not datos_limpios.get("proveedor"):
                    return False, "El proveedor es requerido"
                    
                # Validar precio si se proporciona
                precio_original = datos_herraje.get("precio_unitario")
                precio_sanitizado = datos_limpios.get("precio_unitario")
                
                if precio_original and precio_original != "" and precio_sanitizado is None:
                    return False, "Precio inválido"
                elif precio_sanitizado is None:
                    datos_limpios["precio_unitario"] = 0.0
                    
            else:
                # Sin utilidades de seguridad, usar datos originales con precaución
                datos_limpios = datos_herraje.copy()
                print("WARNING [HERRAJES] Creando herraje sin sanitización de seguridad")

            cursor = self.db_connection.cursor()

            # Verificar que el código no exista
            cursor.execute(
                "SELECT COUNT(*) FROM herrajes WHERE codigo = ?",
                (datos_limpios["codigo"],),
            )
            if cursor.fetchone()[0] > 0:
                return False, f"El código '{datos_limpios['codigo']}' ya existe"

            # Insertar herraje con datos sanitizados
            cursor.execute(
                """
                INSERT INTO """
                + self.tabla_herrajes
                + """ 
                (codigo, descripcion, tipo, proveedor, precio_unitario, unidad_medida, 
                 categoria, estado, stock_minimo, stock_actual, observaciones, 
                 especificaciones, marca, modelo, color, material, dimensiones, peso)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    datos_limpios["codigo"],
                    datos_limpios["descripcion"],
                    datos_limpios.get("tipo", "OTRO"),
                    datos_limpios["proveedor"],
                    datos_limpios.get("precio_unitario", 0.00),
                    datos_limpios.get("unidad_medida", "UNIDAD"),
                    datos_limpios.get("categoria", ""),
                    datos_limpios.get("estado", "ACTIVO"),
                    datos_limpios.get("stock_minimo", 0),
                    datos_limpios.get("stock_actual", 0),
                    datos_limpios.get("observaciones", ""),
                    datos_limpios.get("especificaciones", ""),
                    datos_limpios.get("marca", ""),
                    datos_limpios.get("modelo", ""),
                    datos_limpios.get("color", ""),
                    datos_limpios.get("material", ""),
                    datos_limpios.get("dimensiones", ""),
                    datos_limpios.get("peso", 0.0),
                ),
            )

            # Obtener ID del herraje creado
            cursor.execute("SELECT @@IDENTITY")
            herraje_id = cursor.fetchone()[0]

            # Crear entrada en inventario
            cursor.execute(
                """
                INSERT INTO """
                + self.tabla_herrajes_inventario
                + """ 
                (herraje_id, stock_actual, stock_reservado, ubicacion)
                VALUES (?, ?, 0, ?)
            """,
                (
                    herraje_id,
                    datos_herraje.get("stock_actual", 0),
                    datos_herraje.get("ubicacion", ""),
                ),
            )

            self.db_connection.commit()
            return True, f"Herraje '{datos_limpios['codigo']}' creado exitosamente"

        except Exception as e:
            print(f"[ERROR HERRAJES] Error creando herraje: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return False, f"Error creando herraje: {str(e)}"

    def actualizar_herraje(
        self, herraje_id: int, datos_herraje: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """
        Actualiza un herraje existente.

        Args:
            herraje_id: ID del herraje a actualizar
            datos_herraje: Nuevos datos del herraje

        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        if not self.db_connection:
            return False, "Sin conexión a la base de datos"

        try:
            cursor = self.db_connection.cursor()

            # Verificar que el herraje existe
            cursor.execute("SELECT COUNT(*) FROM herrajes WHERE id = ?", (herraje_id,))
            if cursor.fetchone()[0] == 0:
                return False, "Herraje no encontrado"

            # Actualizar herraje
            cursor.execute(
                """
                UPDATE """
                + self.tabla_herrajes
                + """
                SET descripcion = ?, tipo = ?, proveedor = ?, precio_unitario = ?, 
                    unidad_medida = ?, categoria = ?, estado = ?, stock_minimo = ?, 
                    stock_actual = ?, observaciones = ?, especificaciones = ?, 
                    marca = ?, modelo = ?, color = ?, material = ?, dimensiones = ?, 
                    peso = ?, fecha_actualizacion = GETDATE()
                WHERE id = ?
            """,
                (
                    datos_herraje["descripcion"],
                    datos_herraje.get("tipo", "OTRO"),
                    datos_herraje["proveedor"],
                    datos_herraje.get("precio_unitario", 0.00),
                    datos_herraje.get("unidad_medida", "UNIDAD"),
                    datos_herraje.get("categoria", ""),
                    datos_herraje.get("estado", "ACTIVO"),
                    datos_herraje.get("stock_minimo", 0),
                    datos_herraje.get("stock_actual", 0),
                    datos_herraje.get("observaciones", ""),
                    datos_herraje.get("especificaciones", ""),
                    datos_herraje.get("marca", ""),
                    datos_herraje.get("modelo", ""),
                    datos_herraje.get("color", ""),
                    datos_herraje.get("material", ""),
                    datos_herraje.get("dimensiones", ""),
                    datos_herraje.get("peso", 0.0),
                    herraje_id,
                ),
            )

            # Actualizar inventario
            cursor.execute(
                """
                UPDATE """
                + self.tabla_herrajes_inventario
                + """
                SET stock_actual = ?, ubicacion = ?
                WHERE herraje_id = ?
            """,
                (
                    datos_herraje.get("stock_actual", 0),
                    datos_herraje.get("ubicacion", ""),
                    herraje_id,
                ),
            )

            self.db_connection.commit()
            return True, "Herraje actualizado exitosamente"

        except Exception as e:
            print(f"[ERROR HERRAJES] Error actualizando herraje: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return False, f"Error actualizando herraje: {str(e)}"

    def eliminar_herraje(self, herraje_id: int) -> Tuple[bool, str]:
        """
        Elimina un herraje (eliminación lógica).

        Args:
            herraje_id: ID del herraje a eliminar

        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        if not self.db_connection:
            return False, "Sin conexión a la base de datos"

        try:
            cursor = self.db_connection.cursor()

            # Verificar que el herraje existe
            cursor.execute("SELECT codigo FROM herrajes WHERE id = ?", (herraje_id,))
            row = cursor.fetchone()
            if not row:
                return False, "Herraje no encontrado"

            codigo = row[0]

            # Verificar que no esté asignado a obras
            cursor.execute(
                """
                SELECT COUNT(*) FROM herrajes_obra 
                WHERE herraje_id = ? AND estado != 'COMPLETADO'
            """,
                (herraje_id,),
            )

            if cursor.fetchone()[0] > 0:
                return False, "No se puede eliminar herraje asignado a obras activas"

            # Eliminación lógica
            cursor.execute(
                """
                UPDATE """
                + self.tabla_herrajes
                + """
                SET activo = 0, estado = 'INACTIVO', fecha_actualizacion = GETDATE()
                WHERE id = ?
            """,
                (herraje_id,),
            )

            self.db_connection.commit()
            return True, f"Herraje '{codigo}' eliminado exitosamente"

        except Exception as e:
            print(f"[ERROR HERRAJES] Error eliminando herraje: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return False, f"Error eliminando herraje: {str(e)}"

    def obtener_herraje_por_id(self, herraje_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene un herraje por su ID.

        Args:
            herraje_id: ID del herraje

        Returns:
            Dict con los datos del herraje o None si no existe
        """
        if not self.db_connection:
            return None

        try:
            cursor = self.db_connection.cursor()

            cursor.execute(
                """
                SELECT h.*, i.stock_actual, i.stock_reservado, 
                       i.ubicacion, i.fecha_ultima_entrada, i.fecha_ultima_salida
                FROM herrajes h
                LEFT JOIN """
                + self.tabla_herrajes_inventario
                + """ i ON h.id = i.herraje_id
                WHERE h.id = ? AND h.estado = 'ACTIVO'
            """,
                (herraje_id,),
            )

            row = cursor.fetchone()
            if row:
                columns = [desc[0] for desc in cursor.description]
                return dict(zip(columns, row))
            return None

        except Exception as e:
            print(f"[ERROR HERRAJES] Error obteniendo herraje por ID: {e}")
            return None

    def obtener_proveedores(self) -> List[str]:
        """
        Obtiene la lista de proveedores únicos.

        Returns:
            Lista de nombres de proveedores
        """
        if not self.db_connection:
            return []

        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                SELECT DISTINCT proveedor 
                FROM herrajes 
                WHERE estado = 'ACTIVO' 
                ORDER BY proveedor
            """)
            return [row[0] for row in cursor.fetchall()]

        except Exception as e:
            print(f"[ERROR HERRAJES] Error obteniendo proveedores: {e}")
            return []

    def actualizar_stock(
        self, herraje_id: int, nuevo_stock: int, tipo_movimiento: str = "AJUSTE"
    ) -> Tuple[bool, str]:
        """
        Actualiza el stock de un herraje.

        Args:
            herraje_id: ID del herraje
            nuevo_stock: Nuevo stock actual
            tipo_movimiento: Tipo de movimiento (AJUSTE, ENTRADA, SALIDA)

        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        if not self.db_connection:
            return False, "Sin conexión a la base de datos"

        try:
            cursor = self.db_connection.cursor()

            # Actualizar stock en herrajes
            cursor.execute(
                """
                UPDATE """
                + self.tabla_herrajes
                + """
                SET stock_actual = ?, fecha_actualizacion = GETDATE()
                WHERE id = ?
            """,
                (nuevo_stock, herraje_id),
            )

            # Actualizar stock en inventario
            cursor.execute(
                """
                UPDATE """
                + self.tabla_herrajes_inventario
                + """
                SET stock_actual = ?, 
                    fecha_ultima_entrada = CASE WHEN ? IN ('ENTRADA', 'AJUSTE') THEN GETDATE() ELSE fecha_ultima_entrada END,
                    fecha_ultima_salida = CASE WHEN ? = 'SALIDA' THEN GETDATE() ELSE fecha_ultima_salida END
                WHERE herraje_id = ?
            """,
                (nuevo_stock, tipo_movimiento, tipo_movimiento, herraje_id),
            )

            self.db_connection.commit()
            return True, "Stock actualizado exitosamente"

        except Exception as e:
            print(f"[ERROR HERRAJES] Error actualizando stock: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return False, f"Error actualizando stock: {str(e)}"

    def _get_herrajes_demo(self) -> List[Dict[str, Any]]:
        """Datos demo cuando no hay conexión a BD."""
        return [
            {
                "id": 1,
                "codigo": "BIS-001",
                "descripcion": "Bisagra de puerta estándar",
                "tipo": "BISAGRA",
                "proveedor": "Herrajes SA",
                "precio_unitario": 15.50,
                "unidad_medida": "UNIDAD",
                "categoria": "Bisagras",
                "estado": "ACTIVO",
                "stock_actual": 50,
                "stock_minimo": 10,
                "marca": "Stanley",
                "modelo": "ST-001",
                "color": "Negro",
                "material": "Acero",
                "dimensiones": "10x8x2 cm",
                "peso": 0.2,
            },
            {
                "id": 2,
                "codigo": "CER-001",
                "descripcion": "Cerradura de seguridad",
                "tipo": "CERRADURA",
                "proveedor": "Seguridad Total",
                "precio_unitario": 85.00,
                "unidad_medida": "UNIDAD",
                "categoria": "Cerraduras",
                "estado": "ACTIVO",
                "stock_actual": 25,
                "stock_minimo": 5,
                "marca": "Yale",
                "modelo": "YL-200",
                "color": "Plateado",
                "material": "Acero inoxidable",
                "dimensiones": "15x10x5 cm",
                "peso": 0.8,
            },
        ]
