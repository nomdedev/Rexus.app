"""
Módulo de Gestión de Vidrios - Rexus.app (Refactorizado)

Este módulo maneja todo lo relacionado con el inventario de vidrios:
- Gestión de productos de vidrio (ProductosManager)
- Control de stock y validaciones
- Precios y proveedores
- Asignación a obras (ObrasManager)
- Búsquedas y estadísticas (ConsultasManager)

Arquitectura modular v2.0 con compatibilidad hacia atrás.
"""

# Exportar el modelo principal y vistas
from .model import ModeloVidrios
from .view import VidriosView

# Exportar modelo refactorizado
from .model_refactorizado import ModeloVidriosRefactorizado

# Exportar submódulos especializados
from .submodules.productos_manager import ProductosManager
from .submodules.obras_manager import ObrasManager
from .submodules.consultas_manager import ConsultasManager

__all__ = [
    # Compatibilidad hacia atrás
    'ModeloVidrios', 
    'VidriosView',
    
    # Nueva arquitectura modular
    'ModeloVidriosRefactorizado',
    'ProductosManager',
    'ObrasManager', 
    'ConsultasManager'
]

from .controller import VidriosController
from .model import VidriosModel
from .view import VidriosView

__all__ = ["VidriosModel", "VidriosView", "VidriosController"]
