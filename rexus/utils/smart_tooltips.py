"""
Sistema de Tooltips Inteligentes para Rexus.app

Proporciona tooltips contextuales y dinámicos para mejorar la experiencia del usuario.
"""


import logging
logger = logging.getLogger(__name__)

            OBRAS_TOOLTIPS = {
    'btn_nueva_obra': 'Crear una nueva obra o proyecto',
    'btn_editar_obra': 'Editar los datos de la obra seleccionada',
    'btn_eliminar_obra': 'Eliminar permanentemente la obra seleccionada',
    'input_codigo_obra': 'Código único de identificación de la obra',
    'input_nombre_obra': 'Nombre descriptivo de la obra',
    'combo_estado_obra': 'Estado actual de la obra (Activa, Pausada, Finalizada)',
    'fecha_inicio': 'Fecha de inicio planificada de la obra',
    'fecha_fin': 'Fecha de finalización estimada de la obra',
}

INVENTARIO_TOOLTIPS = {
    'btn_nuevo_item': 'Agregar un nuevo artículo al inventario',
    'btn_editar_item': 'Modificar los datos del artículo seleccionado',
    'input_codigo_item': 'Código único del artículo (SKU)',
    'input_stock_actual': 'Cantidad actual en stock',
    'input_stock_minimo': 'Cantidad mínima para alertas de reposición',
}

HERRAJES_TOOLTIPS = {
    'btn_nuevo_herraje': 'Agregar un nuevo herraje al catálogo',
    'input_codigo_herraje': 'Código único del herraje',
    'combo_categoria_herraje': 'Categoría del herraje (Bisagras, Cerraduras, etc.)',
    'input_precio_herraje': 'Precio unitario del herraje',
}
