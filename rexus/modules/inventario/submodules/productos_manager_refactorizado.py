"""
Submódulo de Productos - Inventario Rexus.app v2.0.0

Gestiona CRUD de productos y validaciones básicas.
Responsabilidades:
- Crear, leer, actualizar productos
- Validaciones de stock y códigos
- Gestión de categorías
- Operaciones básicas de productos
"""

from typing import Any, Dict, List, Optional

# Imports de seguridad unificados
from rexus.core.auth_decorators import auth_required, permission_required
from rexus.utils.unified_sanitizer import unified_sanitizer, sanitize_string, sanitize_numeric

# SQLQueryManager unificado con fallback
try:
    from rexus.core.sql_query_manager import SQLQueryManager
except ImportError:
    # Fallback al script loader
    from rexus.utils.sql_script_loader import sql_script_loader

    class SQLQueryManager:
        def __init__(self):
            self.sql_loader = sql_script_loader

        def get_query(self, path, filename):
            # Construir nombre del script sin extensión
            script_name = filename.replace(".sql", "")
            return self.sql_loader.load_script(script_name)

        def execute_query(self, query, params=None):
            # Placeholder para compatibilidad
            return None


# DataSanitizer unificado
try:
    from rexus.utils.unified_sanitizer import unified_sanitizer
    DataSanitizer = unified_sanitizer
except ImportError:
    class DataSanitizer:
        def sanitize_dict(self, data):
            return data if data else {}

        def sanitize_text(self, text):
            return str(text) if text else ""

        def sanitize_integer(self, value):
            return int(value) if value else 0

            def sanitize_integer(self, value, min_val=None, max_val=None):
                return int(value) if value else 0


class ProductosManager:
    """Gestor especializado para productos del inventario."""

    def __init__(self, db_connection=None):
        """Inicializa el gestor de productos."""
        self.db_connection = db_connection
        self.sql_manager = None  # SQLQueryManager()
        self.sanitizer = DataSanitizer()

    def _validate_table_name(self, table_name: str) -> str:
        """Valida nombre de tabla contra lista blanca."""
        tablas_permitidas = {"inventario", "productos", "categorias"}
        if table_name not in tablas_permitidas:
            raise ValueError(f"Tabla no permitida: {table_name}")
        return table_name

    @auth_required
    @permission_required("create_producto")
    def crear_producto(
        self, datos_producto: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Crea un nuevo producto en el inventario."""
        if not self.db_connection:
            print("[WARN] Sin conexión a BD - Modo simulación")
            return {"id": 1, "mensaje": "Producto creado (simulación)"}

        try:
            # Sanitizar datos
            datos_limpios = self.sanitizer.sanitize_dict(datos_producto)

            # Validaciones básicas
            if not datos_limpios.get("codigo"):
                raise ValueError("Código de producto requerido")

            if not datos_limpios.get("descripcion"):
                raise ValueError("Descripción de producto requerida")

            # Verificar unicidad del código
            if self._verificar_codigo_existe(datos_limpios["codigo"]):
                raise ValueError(f"El código {datos_limpios['codigo']} ya existe")

            # Preparar datos para inserción
            params = {
                "codigo": datos_limpios["codigo"],
                "descripcion": datos_limpios["descripcion"],
                "categoria": datos_limpios.get("categoria", "General"),
                "stock_actual": self.sanitizer.sanitize_integer(
                    datos_limpios.get("stock_inicial", 0)
                ),
                "stock_minimo": self.sanitizer.sanitize_integer(
                    datos_limpios.get("stock_minimo", 0)
                ),
                "precio_unitario": float(datos_limpios.get("precio_unitario", 0.0)),
                "ubicacion": datos_limpios.get("ubicacion", "Sin asignar"),
                "activo": 1,
            }

            # Ejecutar inserción (usar SQL externa en producción)
            query = """
                INSERT INTO inventario (
                    codigo, descripcion, categoria, stock_actual, 
                    stock_minimo, precio_unitario, ubicacion, activo,
                    fecha_creacion, fecha_modificacion
                ) VALUES (
                    %(codigo)s, %(descripcion)s, %(categoria)s, %(stock_actual)s,
                    %(stock_minimo)s, %(precio_unitario)s, %(ubicacion)s, %(activo)s,
                    CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                )
            """

            cursor = self.db_connection.cursor()
            cursor.execute(query, params)
            self.db_connection.commit()
            producto_id = cursor.lastrowid
            cursor.close()

            return {
                "id": producto_id,
                "codigo": params["codigo"],
                "mensaje": "Producto creado exitosamente",
            }

        except Exception as e:
            if self.db_connection:
                self.db_connection.rollback()
            print(f"[ERROR] Error creando producto: {str(e)}")
            return None

    @auth_required
    @permission_required("view_inventario")
    def obtener_producto_por_id(self, producto_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene un producto por su ID."""
        if not self.db_connection:
            return {
                "id": producto_id,
                "codigo": "PROD001",
                "descripcion": "Producto simulado",
                "stock_actual": 10,
            }

        try:
            query = """
                SELECT id, codigo, descripcion, categoria, stock_actual,
                       stock_minimo, precio_unitario, ubicacion, activo,
                       fecha_creacion, fecha_modificacion
                FROM inventario 
                WHERE id = %s AND activo = 1
            """

            cursor = self.db_connection.cursor(dictionary=True)
            cursor.execute(query, (producto_id,))
            resultado = cursor.fetchone()
            cursor.close()

            return resultado

        except Exception as e:
            print(f"[ERROR] Error obteniendo producto: {str(e)}")
            return None

    @auth_required
    @permission_required("update_producto")
    def actualizar_producto(
        self, producto_id: int, datos_actualizacion: Dict[str, Any]
    ) -> bool:
        """Actualiza la información de un producto."""
        if not self.db_connection:
            print("[WARN] Sin conexión a BD - Simulando actualización")
            return True

        try:
            # Sanitizar datos
            datos_limpios = self.sanitizer.sanitize_dict(datos_actualizacion)

            # Construir campos a actualizar
            campos_actualizables = [
                "descripcion",
                "categoria",
                "stock_minimo",
                "precio_unitario",
                "ubicacion",
            ]

            campos_set = []
            params = {}

            for campo in campos_actualizables:
                if campo in datos_limpios:
                    campos_set.append(f"{campo} = %({campo})s")
                    params[campo] = datos_limpios[campo]

            if not campos_set:
                print("[WARN] No hay campos para actualizar")
                return False

            # Agregar timestamp de modificación
            campos_set.append("fecha_modificacion = CURRENT_TIMESTAMP")
            params["producto_id"] = producto_id

            query = f"""
                UPDATE inventario 
                SET {", ".join(campos_set)}
                WHERE id = %(producto_id)s AND activo = 1
            """

            cursor = self.db_connection.cursor()
            cursor.execute(query, params)
            filas_afectadas = cursor.rowcount
            self.db_connection.commit()
            cursor.close()

            return filas_afectadas > 0

        except Exception as e:
            if self.db_connection:
                self.db_connection.rollback()
            print(f"[ERROR] Error actualizando producto: {str(e)}")
            return False

    @auth_required
    @permission_required("delete_producto")
    def eliminar_producto(self, producto_id: int) -> bool:
        """Elimina un producto (soft delete)."""
        if not self.db_connection:
            print("[WARN] Sin conexión a BD - Simulando eliminación")
            return True

        try:
            query = """
                UPDATE inventario 
                SET activo = 0, fecha_modificacion = CURRENT_TIMESTAMP
                WHERE id = %s
            """

            cursor = self.db_connection.cursor()
            cursor.execute(query, (producto_id,))
            filas_afectadas = cursor.rowcount
            self.db_connection.commit()
            cursor.close()

            return filas_afectadas > 0

        except Exception as e:
            if self.db_connection:
                self.db_connection.rollback()
            print(f"[ERROR] Error eliminando producto: {str(e)}")
            return False

    @auth_required
    @permission_required("view_inventario")
    def obtener_producto_por_codigo(self, codigo: str) -> Optional[Dict[str, Any]]:
        """Obtiene un producto por su código."""
        if not self.db_connection:
            return {
                "id": 1,
                "codigo": codigo,
                "descripcion": "Producto simulado",
                "stock_actual": 10,
            }

        try:
            query = """
                SELECT id, codigo, descripcion, categoria, stock_actual,
                       stock_minimo, precio_unitario, ubicacion, activo
                FROM inventario 
                WHERE codigo = %s AND activo = 1
            """

            cursor = self.db_connection.cursor(dictionary=True)
            cursor.execute(query, (codigo,))
            resultado = cursor.fetchone()
            cursor.close()

            return resultado

        except Exception as e:
            print(f"[ERROR] Error obteniendo producto por código: {str(e)}")
            return None

    @auth_required
    @permission_required("update_stock")
    def actualizar_stock(
        self, producto_id: int, nuevo_stock: int, motivo: str = "Ajuste manual"
    ) -> bool:
        """Actualiza el stock de un producto."""
        if not self.db_connection:
            print("[WARN] Sin conexión a BD - Simulando actualización de stock")
            return True

        try:
            # Validar stock no negativo
            if nuevo_stock < 0:
                raise ValueError("El stock no puede ser negativo")

            query = """
                UPDATE inventario 
                SET stock_actual = %s, fecha_modificacion = CURRENT_TIMESTAMP
                WHERE id = %s AND activo = 1
            """

            cursor = self.db_connection.cursor()
            cursor.execute(query, (nuevo_stock, producto_id))
            filas_afectadas = cursor.rowcount
            self.db_connection.commit()
            cursor.close()

            if filas_afectadas > 0:
                print(
                    f"[CHECK] Stock actualizado para producto {producto_id}: {nuevo_stock}"
                )
                return True

            return False

        except Exception as e:
            if self.db_connection:
                self.db_connection.rollback()
            print(f"[ERROR] Error actualizando stock: {str(e)}")
            return False

    def _verificar_codigo_existe(self, codigo: str) -> bool:
        """Verifica si un código de producto ya existe."""
        if not self.db_connection:
            return False  # En modo simulación, permitir cualquier código

        try:
            query = "SELECT COUNT(*) as count FROM inventario WHERE codigo = %s AND activo = 1"
            cursor = self.db_connection.cursor(dictionary=True)
            cursor.execute(query, (codigo,))
            resultado = cursor.fetchone()
            cursor.close()

            return resultado["count"] > 0

        except Exception as e:
            print(f"[ERROR] Error verificando código: {str(e)}")
            return False

    @auth_required
    @permission_required("view_inventario")
    def obtener_categorias(self) -> List[str]:
        """Obtiene lista de categorías disponibles."""
        if not self.db_connection:
            return ["General", "Herramientas", "Materiales", "Equipos"]

        try:
            query = """
                SELECT DISTINCT categoria 
                FROM inventario 
                WHERE activo = 1 AND categoria IS NOT NULL
                ORDER BY categoria
            """

            cursor = self.db_connection.cursor()
            cursor.execute(query)
            resultados = cursor.fetchall()
            cursor.close()

            return [row[0] for row in resultados if row[0]]

        except Exception as e:
            print(f"[ERROR] Error obteniendo categorías: {str(e)}")
            return ["General"]

    def validar_datos_producto(self, datos: Dict[str, Any]) -> List[str]:
        """Valida los datos de un producto y retorna lista de errores."""
        errores = []

        # Código requerido
        if not datos.get("codigo"):
            errores.append("Código de producto es requerido")
        elif len(datos["codigo"]) > 20:
            errores.append("Código no puede exceder 20 caracteres")

        # Descripción requerida
        if not datos.get("descripcion"):
            errores.append("Descripción es requerida")
        elif len(datos["descripcion"]) > 200:
            errores.append("Descripción no puede exceder 200 caracteres")

        # Validar stock inicial
        if "stock_inicial" in datos:
            try:
                stock = int(datos["stock_inicial"])
                if stock < 0:
                    errores.append("Stock inicial no puede ser negativo")
            except (ValueError, TypeError):
                errores.append("Stock inicial debe ser un número entero")

        # Validar precio
        if "precio_unitario" in datos:
            try:
                precio = float(datos["precio_unitario"])
                if precio < 0:
                    errores.append("Precio unitario no puede ser negativo")
            except (ValueError, TypeError):
                errores.append("Precio unitario debe ser un número")

        return errores
