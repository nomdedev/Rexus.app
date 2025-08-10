"""
Pestañas del módulo de Logística

Componentes separados para cada pestaña de la interfaz.
"""

from .tab_entregas import TabEntregas
from .tab_servicios import TabServicios  
from .tab_mapa import TabMapa
from .tab_estadisticas import TabEstadisticas

__all__ = [
    'TabEntregas',
    'TabServicios',
    'TabMapa', 
    'TabEstadisticas'
]