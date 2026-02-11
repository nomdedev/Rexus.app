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

__version__ = "1.1.3"
__author__ = "Stock App Team"

# Alias para módulos con nombres numéricos (compatibilidad con tests)
# Esto permite importar como: from rexus.modules.obras import ObrasModel
# en lugar de: from rexus.modules.01_obras import ObrasModel

import sys
import importlib

# Importar usando importlib para nombres con números al inicio
def _import_numeric_module(name):
    """Importa un módulo con nombre numérico."""
    try:
        return importlib.import_module(f'.{name}', package='rexus.modules')
    except ImportError:
        return None

# Crear alias en el namespace del módulo
obras = _import_numeric_module('01_obras')
inventario = _import_numeric_module('02_inventario')
herrajes = _import_numeric_module('03_herrajes')
vidrios = _import_numeric_module('04_vidrios')
logistica = _import_numeric_module('05_logistica')
pedidos = _import_numeric_module('06_pedidos')
compras = _import_numeric_module('07_compras')
administracion = _import_numeric_module('08_administracion')
mantenimiento = _import_numeric_module('09_mantenimiento')
auditoria = _import_numeric_module('10_auditoria')
usuarios = _import_numeric_module('11_usuarios')
configuracion = _import_numeric_module('12_configuracion')
notificaciones = _import_numeric_module('13_notificaciones')
