"""Módulo de Administracion"""


import logging
logger = logging.getLogger(__name__)

from .controller import AdministracionController
# Comentado temporalmente hasta corregir sintaxis
# from .model import AdministracionModel
# from .view import AdministracionView

# Importar submódulos
try:
    from .recursos_humanos import RecursosHumanosModel, RecursosHumanosController
    logger.info("[ADMINISTRACION] Submódulo Recursos Humanos importado correctamente")
except ImportError as e:
    logger.warning(f"[ADMINISTRACION] Error importando Recursos Humanos: {e}")
    RecursosHumanosModel = None
    RecursosHumanosController = None

__all__ = ["AdministracionController", "RecursosHumanosModel", "RecursosHumanosController"]
# Comentado temporalmente: "AdministracionModel", "AdministracionView"
