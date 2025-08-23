# Componentes optimizados para el módulo Obras
"""
Componentes UI/UX mejorados para el módulo de Obras.

Incluye:
- OptimizedTableWidget: Tabla optimizada con soporte para temas y paginación
- EnhancedLabel: Etiquetas mejoradas con animaciones y estados dinámicos
"""


import logging
logger = logging.getLogger(__name__)

from .optimized_table_widget import OptimizedTableWidget, EnhancedTableContainer
from .enhanced_label_widget import EnhancedLabel, StatusIndicatorLabel, MetricDisplayLabel

__all__ = [
    'OptimizedTableWidget',
    'EnhancedTableContainer',
    'EnhancedLabel',
    'StatusIndicatorLabel',
    'MetricDisplayLabel'
]
