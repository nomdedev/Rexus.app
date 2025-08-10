"""
Modelos de datos para el módulo de Logística

Modelos de tabla para mejor gestión de datos en las interfaces.
"""

from .entregas_model import EntregasTableModel
from .servicios_model import ServiciosTableModel

__all__ = [
    'EntregasTableModel',
    'ServiciosTableModel'
]