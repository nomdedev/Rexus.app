"""
Constantes para el módulo de Compras - Rexus.app v2.0.0

Centralización de mensajes, estados y configuraciones del módulo.
"""

# =============================================================================
# MENSAJES DE ERROR
# =============================================================================

class ErrorMessages:
    """Mensajes de error estandarizados"""
    
    # Errores de conexión
    CONNECTION_ERROR = "Error de conexión a la base de datos"
    NO_CONNECTION = "Sin conexión a la base de datos"
    CONNECTION_FAILED = "No se pudo establecer conexión con la base de datos"
    
    # Errores de validación
    VALIDATION_FAILED = "Error de validación de datos"
                INVALID_FORMAT = "Formato de datos inválido"
    INVALID_NUMBER = "El valor debe ser un número válido"
    INVALID_DATE = "Fecha inválida"
    
    # Errores de operaciones CRUD
    CREATE_FAILED = "Error al crear el registro"
    UPDATE_FAILED = "Error al actualizar el registro" 
    DELETE_FAILED = "Error al eliminar el registro"
    FETCH_FAILED = "Error al obtener los datos"
    
    # Errores específicos de compras
    ORDEN_NOT_FOUND = "Orden de compra no encontrada"
    PROVEEDOR_NOT_FOUND = "Proveedor no encontrado"
    ITEM_NOT_FOUND = "Item no encontrado"
    INSUFFICIENT_STOCK = "Stock insuficiente"
    INVALID_QUANTITY = "Cantidad inválida"
    INVALID_PRICE = "Precio inválido"


# =============================================================================
# MENSAJES DE ÉXITO
# =============================================================================

class SuccessMessages:
    """Mensajes de éxito estandarizados"""
    
    # Operaciones CRUD exitosas
    CREATED_SUCCESS = "Registro creado exitosamente"
    UPDATED_SUCCESS = "Registro actualizado exitosamente"
    DELETED_SUCCESS = "Registro eliminado exitosamente"
    SAVED_SUCCESS = "Datos guardados exitosamente"
    
    # Operaciones específicas de compras
    ORDEN_CREATED = "Orden de compra creada exitosamente"
    ORDEN_UPDATED = "Orden de compra actualizada"
    ORDEN_CANCELLED = "Orden de compra cancelada"
    ORDEN_APPROVED = "Orden de compra aprobada"
    ITEM_ADDED = "Item agregado a la orden"
    ITEM_REMOVED = "Item removido de la orden"


# =============================================================================
# MENSAJES DE ADVERTENCIA
# =============================================================================

class WarningMessages:
    """Mensajes de advertencia estandarizados"""
    
    # Advertencias generales
    CONFIRM_DELETE = "¿Está seguro de eliminar este registro?"
    UNSAVED_CHANGES = "Tiene cambios sin guardar. ¿Desea continuar?"
    DATA_WILL_BE_LOST = "Los datos se perderán si continúa"
    
    # Advertencias específicas
    LOW_STOCK = "Stock bajo para este producto"
    HIGH_COST = "El costo de esta orden es elevado"
    DUPLICATE_ORDER = "Ya existe una orden similar"
    PENDING_APPROVAL = "La orden requiere aprobación"


# =============================================================================
# MENSAJES INFORMATIVOS
# =============================================================================

class InfoMessages:
    """Mensajes informativos estandarizados"""
    
    # Información general
    LOADING_DATA = "Cargando datos..."
    PROCESSING = "Procesando solicitud..."
    SEARCH_RESULTS = "Resultados de búsqueda"
    NO_RESULTS = "No se encontraron resultados"
    
    # Información específica
    ORDEN_DETAILS = "Detalles de la orden de compra"
    PROVEEDOR_INFO = "Información del proveedor"
    TOTAL_ORDERS = "Total de órdenes"
    PENDING_ORDERS = "Órdenes pendientes"


# =============================================================================
# ESTADOS DE ÓRDENES
# =============================================================================

class OrderStatus:
    """Estados posibles de órdenes de compra"""
    
    DRAFT = "BORRADOR"
    PENDING = "PENDIENTE"
    SENT = "ENVIADA"
    CONFIRMED = "CONFIRMADA"
    PARTIAL = "PARCIAL"
    RECEIVED = "RECIBIDA"
    INVOICED = "FACTURADA"
    CANCELLED = "CANCELADA"
    
    # Lista de todos los estados
    ALL_STATUS = [DRAFT, PENDING, SENT, CONFIRMED, PARTIAL, RECEIVED, INVOICED, CANCELLED]
    
    # Estados activos
    ACTIVE_STATUS = [PENDING, SENT, CONFIRMED, PARTIAL]


# =============================================================================
# PRIORIDADES
# =============================================================================

class Priority:
    """Niveles de prioridad"""
    
    LOW = "BAJA"
    NORMAL = "NORMAL"
    HIGH = "ALTA"
    URGENT = "URGENTE"
    
    ALL_PRIORITIES = [LOW, NORMAL, HIGH, URGENT]


# =============================================================================
# CONFIGURACIONES
# =============================================================================

class ComprasConfig:
    """Configuraciones del módulo de compras"""
    
    # Límites
    MAX_ITEMS_PER_ORDER = 100
    MAX_ORDER_VALUE = 1000000.0
    MIN_ORDER_VALUE = 0.01
    
    # Formatos
    CURRENCY_FORMAT = "$ {:.2f}"
    DATE_FORMAT = "%d/%m/%Y"
    DATETIME_FORMAT = "%d/%m/%Y %H:%M"
    
    # Paginación
    DEFAULT_PAGE_SIZE = 50
    MAX_PAGE_SIZE = 500
    
    # Validaciones
    MIN_DESCRIPTION_LENGTH = 5
    MAX_DESCRIPTION_LENGTH = 255
    MIN_QUANTITY = 0.01
    MAX_QUANTITY = 99999.99


# =============================================================================
# TÍTULOS DE VENTANAS Y DIÁLOGOS
# =============================================================================

class WindowTitles:
    """Títulos estandarizados para ventanas y diálogos"""
    
    # Títulos principales
    COMPRAS_MODULE = "Gestión de Compras"
    ORDEN_DIALOG = "Orden de Compra"
    PROVEEDOR_DIALOG = "Proveedor"
    ITEM_DIALOG = "Item de Compra"
    
    # Diálogos específicos
    NEW_ORDEN = "Nueva Orden de Compra"
    EDIT_ORDEN = "Editar Orden de Compra"
    VIEW_ORDEN = "Ver Orden de Compra"
    DELETE_CONFIRM = "Confirmar Eliminación"
    
    # Reportes
    REPORT_ORDERS = "Reporte de Órdenes"
    REPORT_SUPPLIERS = "Reporte de Proveedores"
    REPORT_EXPENSES = "Reporte de Gastos"


# =============================================================================
# ETIQUETAS DE CAMPOS
# =============================================================================

class FieldLabels:
    """Etiquetas estandarizadas para campos de formularios"""
    
    # Campos básicos
    ID = "ID"
    NAME = "Nombre"
    DESCRIPTION = "Descripción"
    DATE = "Fecha"
    STATUS = "Estado"
    PRIORITY = "Prioridad"
    
    # Campos específicos de compras
    ORDER_NUMBER = "Número de Orden"
    SUPPLIER = "Proveedor"
    DELIVERY_DATE = "Fecha de Entrega"
    TOTAL_AMOUNT = "Total"
    SUBTOTAL = "Subtotal"
    DISCOUNT = "Descuento"
    TAX = "Impuestos"
    
    # Campos de items
    ITEM_CODE = "Código"
    QUANTITY = "Cantidad"
    UNIT_PRICE = "Precio Unitario"
    LINE_TOTAL = "Total Línea"
    UNIT = "Unidad"
    CATEGORY = "Categoría"


# =============================================================================
# TOOLTIPS Y AYUDA
# =============================================================================

class Tooltips:
    """Textos de ayuda para elementos de la interfaz"""

import logging
logger = logging.getLogger(__name__)

    
    # Botones
    BTN_NEW = "Crear nueva orden de compra"
    BTN_EDIT = "Editar orden seleccionada"
    BTN_DELETE = "Eliminar orden seleccionada"
    BTN_DUPLICATE = "Duplicar orden seleccionada"
    BTN_EXPORT = "Exportar datos a Excel"
    BTN_PRINT = "Imprimir orden"
    
    # Campos
    FIELD_SUPPLIER = "Seleccione el proveedor para esta orden"
    FIELD_DELIVERY = "Fecha estimada de entrega"
    FIELD_PRIORITY = "Nivel de prioridad de la orden"
    FIELD_DISCOUNT = "Descuento aplicado (porcentaje o monto fijo)"