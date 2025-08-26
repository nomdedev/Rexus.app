"""
Constantes para el módulo de Inventario - Rexus.app

Centraliza strings, configuraciones y constantes para evitar 
duplicación y facilitar mantenimiento.
"""

class InventarioConstants:
    """Constantes del módulo de inventario."""

import logging
logger = logging.getLogger(__name__)


# Títulos y etiquetas
TITULO_MODULO = "[PACKAGE] Gestión de Inventario"

# Botones
BTN_NUEVO_PRODUCTO = "➕ Nuevo Producto"
BTN_EDITAR_PRODUCTO = "✏️ Editar"
BTN_ELIMINAR_PRODUCTO = "🗑️ Eliminar"
BTN_IMPORTAR = "📥 Importar"
BTN_EXPORTAR = "📤 Exportar"
BTN_ACTUALIZAR = "🔄 Actualizar"
BTN_BUSCAR = "[SEARCH] Buscar"
BTN_LIMPIAR = "🧹 Limpiar"

# Headers de tabla
HEADERS_PRODUCTOS = [
    "ID", "Código", "Descripción", "Categoría", "Stock Actual",
    "Stock Mínimo", "Stock Máximo", "Precio", "Ubicación", "Estado"
]

# Categorías de productos
CATEGORIAS = [
    "PERFIL", "VIDRIO", "HERRAJE", "ACCESORIO", 
    "HERRAMIENTA", "CONSUMIBLE", "MATERIAL"
]

# Estados de productos
ESTADOS_PRODUCTO = ["ACTIVO", "INACTIVO", "DESCONTINUADO"]

# Estados de stock
ESTADO_STOCK_NORMAL = "NORMAL"
ESTADO_STOCK_BAJO = "BAJO"
ESTADO_STOCK_CRITICO = "CRÍTICO"
ESTADO_STOCK_AGOTADO = "AGOTADO"

# Mensajes
MSG_PRODUCTO_CREADO = "Producto creado exitosamente"
MSG_PRODUCTO_ACTUALIZADO = "Producto actualizado exitosamente"
MSG_PRODUCTO_ELIMINADO = "Producto eliminado exitosamente"
MSG_ERROR_CREAR_PRODUCTO = "Error al crear el producto"
MSG_ERROR_ACTUALIZAR_PRODUCTO = "Error al actualizar el producto"
MSG_ERROR_ELIMINAR_PRODUCTO = "Error al eliminar el producto"
MSG_SELECCIONAR_PRODUCTO = "Seleccione un producto"
MSG_CONFIRMAR_ELIMINACION = "¿Está seguro de eliminar este producto?"

# Placeholders
PLACEHOLDER_BUSCAR = "[SEARCH] Buscar productos..."
PLACEHOLDER_CODIGO = "Ej: VID-001, PER-002"
PLACEHOLDER_DESCRIPCION = "Descripción del producto"
PLACEHOLDER_PRECIO = "0.00"
PLACEHOLDER_STOCK = "0"

# Configuraciones
STOCK_MINIMO_DEFAULT = 5
STOCK_MAXIMO_DEFAULT = 1000
PRECIO_DEFAULT = 0.0

# Colores por estado de stock
COLOR_STOCK_NORMAL = "#4CAF50"    # Verde
COLOR_STOCK_BAJO = "#FF9800"      # Naranja
COLOR_STOCK_CRITICO = "#F44336"   # Rojo
COLOR_STOCK_AGOTADO = "#9E9E9E"   # Gris

# Límites de stock
LIMITE_STOCK_BAJO = 10      # Menos de 10 = stock bajo
LIMITE_STOCK_CRITICO = 5    # Menos de 5 = stock crítico

# Formatos de exportación
FORMATOS_EXPORTACION = ["Excel (.xlsx)", "CSV (.csv)", "PDF (.pdf)"]

# Filtros
FILTROS_CATEGORIA = ["Todas"] + CATEGORIAS
FILTROS_ESTADO = ["Todos"] + ESTADOS_PRODUCTO
FILTROS_STOCK = ["Todos", "Stock Normal", "Stock Bajo", "Stock Crítico", "Agotado"]

# Configuraciones de tabla
FILAS_POR_PAGINA = 50
ANCHO_COLUMNA_CODIGO = 100
ANCHO_COLUMNA_DESCRIPCION = 250
ANCHO_COLUMNA_CATEGORIA = 120
ANCHO_COLUMNA_STOCK = 80
ANCHO_COLUMNA_PRECIO = 100

# Validaciones
MIN_LENGTH_CODIGO = 3
MAX_LENGTH_CODIGO = 20
MIN_LENGTH_DESCRIPCION = 5
MAX_LENGTH_DESCRIPCION = 255
MAX_PRECIO = 999999.99
MAX_STOCK = 999999