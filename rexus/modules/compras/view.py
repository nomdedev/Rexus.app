"""
Vista de Compras - Rexus.app v2.0.0
Re-exporta la vista completa para compatibilidad.
"""

from .view_complete import ComprasViewComplete, OrdenCompraDialog

# Re-exportar para compatibilidad
ComprasView = ComprasViewComplete

__all__ = ['ComprasView', 'ComprasViewComplete', 'OrdenCompraDialog']