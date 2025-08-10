"""
Submódulo de Productos Vidrios - Rexus.app

Gestiona CRUD de productos vidrios y validaciones específicas.
Responsabilidades:
- Crear, leer, actualizar, eliminar productos vidrios
- Validaciones de medidas y características
- Gestión de tipos y categorías de vidrio
"""

from typing import Any, Dict, List, Optional

# Imports de seguridad unificados
from rexus.core.auth_decorators import auth_required, permission_required
from rexus.utils.unified_sanitizer import unified_sanitizer, sanitize_string, sanitize_numeric

# SQLQueryManager unificado
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
            script_name = f"{path.replace('scripts/sql/', '')}/{filename}"
            return self.sql_loader.load_script(script_name)


# DataSanitizer unificado
try:
    from rexus.utils.unified_sanitizer import unified_sanitizer
    DataSanitizer = unified_sanitizer
except ImportError:
    class DataSanitizer:
        def sanitize_dict(self, data):
            return data if data else {}
            
        def sanitize_string(self, text):
            return str(text) if text else ""
            
        def sanitize_integer(self, value):
            return int(value) if value else 0

            def sanitize_numeric(self, value, min_val=None, max_val=None):
                return float(value) if value else 0.0

            def sanitize_integer(self, value, min_val=None, max_val=None):
                return int(value) if value else 0


class ProductosManager:
    """Gestor especializado para productos vidrios."""

    def __init__(self, db_connection=None):
        """Inicializa el gestor de productos vidrios."""
        self.db_connection = db_connection
        self.sql_manager = SQLQueryManager()
        self.sanitizer = DataSanitizer()
        self.sql_path = "scripts/sql/vidrios/productos"

    def _validate_table_name(self, table_name: str) -> str:
        """Valida nombre de tabla contra lista blanca."""
        import re

        if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", table_name):
            raise ValueError(f"Nombre de tabla inválido: {table_name}")

        tablas_permitidas = {"vidrios", "tipos_vidrio", "categorias_vidrio"}
        if table_name not in tablas_permitidas:
            raise ValueError(f"Tabla no permitida: {table_name}")
        return table_name

    @auth_required
    @permission_required("view_inventario")
    def obtener_vidrio_por_id(self, vidrio_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene un vidrio específico por ID."""
        if not self.db_connection or not vidrio_id:
            return None

        try:
            cursor = self.db_connection.cursor()

            # Usar SQL externo para consulta
            query = self.sql_manager.get_query(self.sql_path, "obtener_vidrio_por_id")
            cursor.execute(query, {"vidrio_id": vidrio_id})

            row = cursor.fetchone()
            if not row:
                return None

            columns = [column[0] for column in cursor.description]
            return dict(zip(columns, row))

        except Exception as e:
            raise Exception(f"Error obteniendo vidrio: {str(e)}")

    @auth_required
    @permission_required("add_inventario")
    def crear_vidrio(self, datos_vidrio: Dict[str, Any]) -> bool:
        """Crea un nuevo producto vidrio con validaciones."""
        if not self.db_connection:
            return False

        try:
            # Validar y sanitizar datos
            datos_sanitizados = self._validar_datos_vidrio(datos_vidrio)

            cursor = self.db_connection.cursor()

            # Usar SQL externo para inserción
            query = self.sql_manager.get_query(self.sql_path, "insertar_vidrio")
            cursor.execute(query, datos_sanitizados)

            self.db_connection.commit()
            return True

        except Exception as e:
            if self.db_connection:
                self.db_connection.rollback()
            print(f"Error creando vidrio: {str(e)}")
            return False

    @auth_required
    @permission_required("change_inventario")
    def actualizar_vidrio(self, vidrio_id: int, datos_vidrio: Dict[str, Any]) -> bool:
        """Actualiza un producto vidrio existente."""
        if not self.db_connection or not vidrio_id:
            return False

        try:
            # Validar y sanitizar datos
            datos_sanitizados = self._validar_datos_vidrio(datos_vidrio)
            datos_sanitizados["vidrio_id"] = vidrio_id

            cursor = self.db_connection.cursor()

            # Usar SQL externo para actualización
            query = self.sql_manager.get_query(self.sql_path, "actualizar_vidrio")
            cursor.execute(query, datos_sanitizados)

            self.db_connection.commit()
            return cursor.rowcount > 0

        except Exception as e:
            if self.db_connection:
                self.db_connection.rollback()
            print(f"Error actualizando vidrio: {str(e)}")
            return False

    @auth_required
    @permission_required("delete_inventario")
    def eliminar_vidrio(self, vidrio_id: int) -> bool:
        """Elimina un producto vidrio (soft delete)."""
        if not self.db_connection or not vidrio_id:
            return False

        try:
            cursor = self.db_connection.cursor()

            # Usar SQL externo para eliminación
            query = self.sql_manager.get_query(self.sql_path, "eliminar_vidrio")
            cursor.execute(query, {"vidrio_id": vidrio_id})

            self.db_connection.commit()
            return cursor.rowcount > 0

        except Exception as e:
            if self.db_connection:
                self.db_connection.rollback()
            print(f"Error eliminando vidrio: {str(e)}")
            return False

    def _validar_datos_vidrio(self, datos: Dict[str, Any]) -> Dict[str, Any]:
        """Valida y sanitiza datos de vidrio."""
        # Campos requeridos
        campos_requeridos = ["tipo", "espesor", "precio"]
        for campo in campos_requeridos:
            if campo not in datos or not datos[campo]:
                raise ValueError(f"Campo requerido faltante: {campo}")

        # Sanitizar datos
        datos_sanitizados = {}

        # Strings
        datos_sanitizados["tipo"] = sanitize_string(
            datos.get("tipo", "")
        )
        datos_sanitizados["descripcion"] = sanitize_string(
            datos.get("descripcion", "")
        )
        datos_sanitizados["proveedor"] = sanitize_string(
            datos.get("proveedor", "")
        )
        datos_sanitizados["codigo"] = sanitize_string(
            datos.get("codigo", "")
        )

        # Números
        datos_sanitizados["espesor"] = self.sanitizer.sanitize_numeric(
            datos.get("espesor", 0), min_val=0
        )
        datos_sanitizados["precio"] = self.sanitizer.sanitize_numeric(
            datos.get("precio", 0), min_val=0
        )
        datos_sanitizados["largo"] = self.sanitizer.sanitize_numeric(
            datos.get("largo", 0), min_val=0
        )
        datos_sanitizados["ancho"] = self.sanitizer.sanitize_numeric(
            datos.get("ancho", 0), min_val=0
        )

        # Enteros
        datos_sanitizados["stock"] = self.sanitizer.sanitize_integer(
            datos.get("stock", 0), min_val=0
        )
        datos_sanitizados["stock_minimo"] = self.sanitizer.sanitize_integer(
            datos.get("stock_minimo", 0), min_val=0
        )

        # Validaciones específicas
        if datos_sanitizados["precio"] <= 0:
            raise ValueError("El precio debe ser mayor a 0")

        if datos_sanitizados["espesor"] <= 0:
            raise ValueError("El espesor debe ser mayor a 0")

        if not datos_sanitizados["tipo"]:
            raise ValueError("El tipo de vidrio es requerido")

        return datos_sanitizados

    @auth_required
    @permission_required("view_inventario")
    def obtener_tipos_vidrio(self) -> List[str]:
        """Obtiene los tipos de vidrio disponibles."""
        if not self.db_connection:
            return []

        try:
            cursor = self.db_connection.cursor()

            # Usar SQL externo para consulta
            query = self.sql_manager.get_query(self.sql_path, "obtener_tipos_vidrio")
            cursor.execute(query)

            tipos = [row[0] for row in cursor.fetchall()]
            return tipos

        except Exception as e:
            print(f"Error obteniendo tipos de vidrio: {str(e)}")
            return []

    @auth_required
    @permission_required("view_inventario")
    def validar_codigo_unico(
        self, codigo: str, vidrio_id: Optional[int] = None
    ) -> bool:
        """Valida que el código de vidrio sea único."""
        if not self.db_connection or not codigo:
            return False

        try:
            cursor = self.db_connection.cursor()

            # Sanitizar código
            codigo_sanitizado = sanitize_string(codigo)

            # Usar SQL externo para validación
            if vidrio_id:
                query = self.sql_manager.get_query(
                    self.sql_path, "validar_codigo_actualizar"
                )
                cursor.execute(
                    query, {"codigo": codigo_sanitizado, "vidrio_id": vidrio_id}
                )
            else:
                query = self.sql_manager.get_query(
                    self.sql_path, "validar_codigo_nuevo"
                )
                cursor.execute(query, {"codigo": codigo_sanitizado})

            return cursor.fetchone() is None

        except Exception as e:
            print(f"Error validando código: {str(e)}")
            return False

    def calcular_area_vidrio(self, largo: float, ancho: float) -> float:
        """Calcula el área del vidrio en metros cuadrados."""
        try:
            largo_sanitizado = self.sanitizer.sanitize_numeric(largo, min_val=0)
            ancho_sanitizado = self.sanitizer.sanitize_numeric(ancho, min_val=0)

            if largo_sanitizado <= 0 or ancho_sanitizado <= 0:
                return 0.0

            return largo_sanitizado * ancho_sanitizado

        except Exception:
            return 0.0

    def calcular_precio_area(
        self, precio_metro: float, largo: float, ancho: float
    ) -> float:
        """Calcula el precio total basado en el área."""
        try:
            area = self.calcular_area_vidrio(largo, ancho)
            precio_sanitizado = self.sanitizer.sanitize_numeric(
                precio_metro, min_val=0
            )

            return area * precio_sanitizado

        except Exception:
            return 0.0

    @auth_required
    @permission_required("edit_inventario")
    def actualizar_stock(self, vidrio_id: int, nuevo_stock: int) -> bool:
        """Actualiza solo el stock de un vidrio."""
        if not self.db_connection or not vidrio_id:
            return False

        try:
            stock_sanitizado = self.sanitizer.sanitize_integer(
                nuevo_stock, min_val=0
            )

            cursor = self.db_connection.cursor()

            # Actualización específica de stock
            query = """
                UPDATE vidrios 
                SET stock = %(stock)s,
                    fecha_modificacion = GETDATE()
                WHERE id = %(vidrio_id)s AND activo = 1
            """

            cursor.execute(query, {"stock": stock_sanitizado, "vidrio_id": vidrio_id})

            self.db_connection.commit()
            return cursor.rowcount > 0

        except Exception as e:
            if self.db_connection:
                self.db_connection.rollback()
            print(f"Error actualizando stock: {str(e)}")
            return False

    @auth_required
    @permission_required("edit_inventario")
    def actualizar_precio(self, vidrio_id: int, nuevo_precio: float) -> bool:
        """Actualiza solo el precio de un vidrio."""
        if not self.db_connection or not vidrio_id:
            return False

        try:
            precio_sanitizado = self.sanitizer.sanitize_numeric(
                nuevo_precio, min_val=0
            )

            if precio_sanitizado <= 0:
                raise ValueError("El precio debe ser mayor a 0")

            cursor = self.db_connection.cursor()

            # Actualización específica de precio
            query = """
                UPDATE vidrios 
                SET precio = %(precio)s,
                    fecha_modificacion = GETDATE()
                WHERE id = %(vidrio_id)s AND activo = 1
            """

            cursor.execute(query, {"precio": precio_sanitizado, "vidrio_id": vidrio_id})

            self.db_connection.commit()
            return cursor.rowcount > 0

        except Exception as e:
            if self.db_connection:
                self.db_connection.rollback()
            print(f"Error actualizando precio: {str(e)}")
            return False

    @auth_required
    @permission_required("view_inventario")
    def validar_disponibilidad(self, vidrio_id: int, cantidad_requerida: int) -> bool:
        """Valida si hay stock suficiente para la cantidad requerida."""
        if not self.db_connection or not vidrio_id:
            return False

        try:
            cantidad_sanitizada = self.sanitizer.sanitize_integer(
                cantidad_requerida, min_val=1
            )

            cursor = self.db_connection.cursor()

            # Consultar stock actual
            query = """
                SELECT stock 
                FROM vidrios 
                WHERE id = %(vidrio_id)s AND activo = 1
            """

            cursor.execute(query, {"vidrio_id": vidrio_id})
            result = cursor.fetchone()

            if not result:
                return False

            stock_actual = result[0] or 0
            return stock_actual >= cantidad_sanitizada

        except Exception as e:
            print(f"Error validando disponibilidad: {str(e)}")
            return False
