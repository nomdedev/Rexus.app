"""
Submódulo de Productos - Inventario Rexus.app

Gestiona CRUD de productos y validaciones básicas.
Responsabilidades:
- Crear, leer, actualizar productos
- Validaciones de stock
- Gestión de códigos y categorías
- Generación de QR
"""

from io import BytesIO
from typing import Any, Dict, List, Optional

import qrcode

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
            script_name = filename.replace(".sql", "")
            return self.sql_loader(script_name)

        def execute_query(self, query, params=None):
            # Placeholder para compatibilidad
            return None


# DataSanitizer unificado - Usar sistema unificado de sanitización
try:
    from rexus.utils.data_sanitizer import DataSanitizer
except ImportError:
    try:
        from rexus.utils.unified_sanitizer import DataSanitizer
    except ImportError:
        try:
            from rexus.core.data_sanitizer import DataSanitizer
        except ImportError:
            # Fallback seguro
            class DataSanitizer:
                def sanitize_dict(self, data):
                    """Sanitiza un diccionario de datos de forma segura."""
                    if not isinstance(data, dict):
                        return {}
                    
                    sanitized = {}
                    for key, value in data.items():
                        if isinstance(value, str):
                            # Sanitización básica de strings
                            sanitized[key] = str(value).strip()
                        else:
                            sanitized[key] = value
                    return sanitized

                def sanitize_text(self, text):
                    """Sanitiza texto de forma segura."""
                    return str(text).strip() if text else ""


class ProductosManager:
    """Gestor especializado para productos del inventario."""

    def __init__(self, db_connection=None):
        """Inicializa el gestor de productos."""
        self.db_connection = db_connection
        self.sql_manager = SQLQueryManager()
        self.sanitizer = DataSanitizer()
        self.sql_path = "scripts/sql/inventario/productos"

    def _validate_table_name(self, table_name: str) -> str:
        """Valida nombre de tabla contra lista blanca."""
        tablas_permitidas = {"inventario", "productos", "categorias"}
        if table_name not in tablas_permitidas:
            raise ValueError(f"Tabla no permitida: {table_name}")
        return table_name

    @auth_required
    @permission_required("view_inventario")
    def obtener_producto_por_id(self, producto_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene un producto específico por ID."""
        if not self.db_connection or not producto_id:
            return None

        try:
            cursor = self.db_connection.cursor()

            # Usar SQL externo para consulta
            query = self.sql_manager.get_query(self.sql_path, "obtener_producto_por_id")
            cursor.execute(query, {"producto_id": producto_id})

            row = cursor.fetchone()
            if not row:
                return None

            columns = [column[0] for column in cursor.description]
            return dict(zip(columns, row))

        except Exception as e:
            raise Exception(f"Error obteniendo producto: {str(e)}")

    @auth_required
    @permission_required("view_inventario")
    def obtener_producto_por_codigo(self, codigo: str) -> Optional[Dict[str, Any]]:
        """Obtiene un producto por su código."""
        if not self.db_connection or not codigo:
            return None

        try:
            cursor = self.db_connection.cursor()

            # Sanitizar código de búsqueda
            codigo_sanitizado = sanitize_string(codigo)

            # Usar SQL externo para consulta
            query = self.sql_manager.get_query(
                self.sql_path, "obtener_producto_por_codigo"
            )
            cursor.execute(query, {"codigo": codigo_sanitizado})

            row = cursor.fetchone()
            if not row:
                return None

            columns = [column[0] for column in cursor.description]
            return dict(zip(columns, row))

        except Exception as e:
            raise Exception(f"Error obteniendo producto por código: {str(e)}")

    @auth_required
    @permission_required("create_producto")
    def crear_producto(
        self, datos_producto: Dict[str, Any], usuario: str = "SISTEMA"
    ) -> Optional[int]:
        """Crea un nuevo producto con validaciones completas."""
        if not self.db_connection:
            raise Exception("No hay conexión a la base de datos")

        try:
            # Validar y sanitizar datos
            if not isinstance(datos_producto, dict):
                raise ValueError("Los datos del producto deben ser un diccionario")

            datos_sanitizados = self.sanitizer.sanitize_dict(datos_producto)

            # Validar campos obligatorios
            if not datos_sanitizados.get("codigo"):
                raise ValueError("El código del producto es obligatorio")

            if not datos_sanitizados.get("descripcion"):
                raise ValueError("La descripción del producto es obligatoria")

            # Verificar que no existe producto duplicado
            if self.obtener_producto_por_codigo(datos_sanitizados["codigo"]):
                raise ValueError(
                    f"Ya existe un producto con código: {datos_sanitizados['codigo']}"
                )

            cursor = self.db_connection.cursor()

            # Usar SQL externo para inserción
            query = self.sql_manager.get_query(self.sql_path, "insertar_producto")

            # Generar QR si no existe
            qr_data = datos_sanitizados.get("qr_data")
            if not qr_data:
                qr_data = self._generar_qr_code(datos_sanitizados["codigo"])

            # Preparar parámetros
            params = {
                "codigo": datos_sanitizados["codigo"],
                "descripcion": datos_sanitizados["descripcion"],
                "categoria": datos_sanitizados.get("categoria", "GENERAL"),
                "unidad_medida": datos_sanitizados.get("unidad_medida", "UND"),
                "precio_compra": datos_sanitizados.get("precio_compra", 0),
                "precio_venta": datos_sanitizados.get("precio_venta", 0),
                "stock_actual": datos_sanitizados.get("stock_actual", 0),
                "stock_minimo": datos_sanitizados.get("stock_minimo", 0),
                "ubicacion": datos_sanitizados.get("ubicacion", ""),
                "observaciones": datos_sanitizados.get("observaciones", ""),
                "qr_data": qr_data,
                "usuario_creador": usuario,
            }

            cursor.execute(query, params)

            # Obtener ID del producto creado usando SCOPE_IDENTITY() seguro
            cursor.execute("SELECT SCOPE_IDENTITY()")
            producto_id = cursor.fetchone()[0]

            self.db_connection.commit()
            return int(producto_id)

        except Exception as e:
            self.db_connection.rollback()
            raise Exception(f"Error creando producto: {str(e)}")

    @auth_required
    @permission_required("update_producto")
    def actualizar_producto(
        self, producto_id: int, datos_producto: Dict[str, Any], usuario: str = "SISTEMA"
    ) -> bool:
        """Actualiza un producto existente."""
        if not self.db_connection:
            return False

        try:
            # Verificar que el producto existe
            producto_actual = self.obtener_producto_por_id(producto_id)
            if not producto_actual:
                raise ValueError(f"Producto {producto_id} no encontrado")

            # Sanitizar datos
            datos_sanitizados = self.sanitizer.sanitize_dict(datos_producto)

            cursor = self.db_connection.cursor()

            # Usar SQL externo para actualización
            query = self.sql_manager.get_query(self.sql_path, "actualizar_producto")

            # Preparar parámetros
            params = {
                "producto_id": producto_id,
                "descripcion": datos_sanitizados.get(
                    "descripcion", producto_actual["descripcion"]
                ),
                "categoria": datos_sanitizados.get(
                    "categoria", producto_actual["categoria"]
                ),
                "unidad_medida": datos_sanitizados.get(
                    "unidad_medida", producto_actual["unidad_medida"]
                ),
                "precio_compra": datos_sanitizados.get(
                    "precio_compra", producto_actual["precio_compra"]
                ),
                "precio_venta": datos_sanitizados.get(
                    "precio_venta", producto_actual["precio_venta"]
                ),
                "stock_minimo": datos_sanitizados.get(
                    "stock_minimo", producto_actual["stock_minimo"]
                ),
                "ubicacion": datos_sanitizados.get(
                    "ubicacion", producto_actual["ubicacion"]
                ),
                "observaciones": datos_sanitizados.get(
                    "observaciones", producto_actual["observaciones"]
                ),
                "usuario_modificador": usuario,
            }

            cursor.execute(query, params)
            self.db_connection.commit()
            return True

        except Exception as e:
            self.db_connection.rollback()
            raise Exception(f"Error actualizando producto: {str(e)}")

    def validar_stock_negativo(
        self, cantidad_nueva: float, producto_id: Optional[int] = None
    ) -> bool:
        """Valida que el stock no quede negativo."""
        if cantidad_nueva >= 0:
            return True

        if not producto_id:
            return False

        producto = self.obtener_producto_por_id(producto_id)
        if not producto:
            return False

        stock_actual = producto.get("stock_actual", 0)
        return (stock_actual + cantidad_nueva) >= 0

    @auth_required
    @permission_required("view_inventario")
    def obtener_categorias(self) -> List[str]:
        """Obtiene lista de categorías disponibles."""
        if not self.db_connection:
            return ["GENERAL", "HERRAMIENTAS", "MATERIALES", "SERVICIOS"]

        try:
            cursor = self.db_connection.cursor()

            # Usar SQL externo para consulta
            query = self.sql_manager.get_query(self.sql_path, "obtener_categorias")
            cursor.execute(query)

            categorias = [row[0] for row in cursor.fetchall() if row[0]]
            return categorias if categorias else ["GENERAL"]

        except Exception:
            return ["GENERAL", "HERRAMIENTAS", "MATERIALES", "SERVICIOS"]

    def _generar_qr_code(self, codigo: str) -> str:
        """Genera código QR para el producto."""
        try:
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(f"REXUS_PRODUCTO:{codigo}")
            qr.make(fit=True)

            # Crear imagen QR
            img = qr.make_image(fill_color="black", back_color="white")

            # Convertir a string base64 para almacenar
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            import base64

            qr_string = base64.b64encode(buffer.getvalue()).decode()

            return qr_string

        except Exception as e:
            print(f"[WARNING] No se pudo generar QR para {codigo}: {e}")
            return f"QR:{codigo}"
