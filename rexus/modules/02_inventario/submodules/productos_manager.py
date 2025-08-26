"""
Submódulo de Productos - Inventario Rexus.app

Gestiona CRUD de productos y validaciones básicas.
Responsabilidades:
- Crear, leer, actualizar productos
- Validaciones de stock
- Gestión de códigos y categorías
- Generación de QR
"""


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

except (sqlite3.Error, AttributeError, TypeError):
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
        logger.warning(f"[WARNING] No se pudo generar QR para {codigo}: {e}")
return f"QR:{codigo}"
