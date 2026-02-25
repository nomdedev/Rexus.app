"""Módulo de Administracion"""

from .controller import AdministracionController
from .model import AdministracionModel

try:
	from .view import AdministracionView
except Exception:
	AdministracionView = None

__all__ = ["AdministracionModel", "AdministracionView", "AdministracionController"]
