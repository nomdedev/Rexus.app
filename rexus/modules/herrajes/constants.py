# Constantes para el módulo de Herrajes
            
class HerrajesConstants:
    """Constantes para el módulo de Herrajes"""

import logging
logger = logging.getLogger(__name__)


    # Mensajes de funcionalidad
    FUNCIONALIDAD_NO_DISPONIBLE = "Funcionalidad no disponible"
    SELECCION_REQUERIDA = "Selección requerida"
    
    # Mensajes específicos
    MENSAJE_CREACION_PENDIENTE = "La creación de herrajes aún no está implementada."
    MENSAJE_EDICION_PENDIENTE = "La edición de herrajes aún no está implementada."
    MENSAJE_ELIMINACION_PENDIENTE = "La eliminación de herrajes aún no está implementada."
    MENSAJE_EXPORTACION_PENDIENTE = "La exportación de herrajes aún no está implementada."
    MENSAJE_CARGA_OBRA_PENDIENTE = "La carga de herrajes por obra aún no está implementada."
    
    # Mensajes de selección
    SELECCIONAR_HERRAJE_EDITAR = "Por favor seleccione un herraje para editar."
    SELECCIONAR_HERRAJE_ELIMINAR = "Por favor seleccione un herraje para eliminar."
    SELECCIONAR_OBRA = "Por favor seleccione una obra."
    
    # Estilos repetidos para QTableWidget
    TABLA_STYLE = """
        QTableWidget {
            gridline-color: #e1e4e8;
            background-color: #ffffff;
            alternate-background-color: #f8f9fa;
            selection-background-color: #e3f2fd;
            border: 1px solid #d1d5da;
        }
        QTableWidget::item {
            padding: 8px;
            border-bottom: 1px solid #eaecef;
        }
        QTableWidget::item:selected {
            background-color: #e3f2fd;
            color: #1976d2;
        }
        QHeaderView::section {
            background-color: #f6f8fa;
            padding: 8px;
            border: 1px solid #d1d5da;
            font-weight: bold;
        }
    """