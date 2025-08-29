"""
Módulos principales de la aplicación Stock App.

Este paquete contiene todos los módulos funcionales de la aplicación:
- Auditoría
- Compras/Pedidos
- Configuración
- Contabilidad
- Herrajes
- Inventario
- Logística
- Mantenimiento
- Obras y Producción
- Pedidos
- Usuarios
- Vidrios
"""

import logging
import importlib
import sys

logger = logging.getLogger(__name__)

# Mapeo de nombres limpios a nombres con números para compatibilidad
MODULE_MAPPING = {
    'usuarios': '09_usuarios',
    'obras': '01_obras',
    'inventario': '02_inventario',
    'pedidos': '03_pedidos',
    'compras': '04_compras',
    'logistica': '05_logistica',
    'herrajes': '06_herrajes',
    'vidrios': '07_vidrios',
    'mantenimiento': '08_mantenimiento',
    'configuracion': '10_configuracion',
    'auditoria': '11_auditoria',
    'administracion': '12_administracion',
    'notificaciones': '13_notificaciones',
}

def __getattr__(name):
    """Permite importar módulos usando nombres limpios."""
    if name in MODULE_MAPPING:
        actual_name = MODULE_MAPPING[name]
        try:
            module = importlib.import_module(f'.{actual_name}', package=__name__)
            # Agregar el módulo al espacio de nombres para futuras importaciones
            sys.modules[f'{__name__}.{name}'] = module
            return module
        except ImportError as e:
            logger.error(f"No se pudo importar el módulo {name} ({actual_name}): {e}")
            raise
    raise AttributeError(f"Módulo '{name}' no encontrado")


__version__ = "1.1.3"
__author__ = "Stock App Team"
