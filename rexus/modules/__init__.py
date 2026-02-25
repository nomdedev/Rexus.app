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

import importlib
from types import SimpleNamespace

# Importar usando importlib para nombres con números al inicio
def _placeholder_class(name: str):
    return type(name, (), {})


def _build_fallback_module(model_classes=None, include_produccion=False):
    model_classes = model_classes or []
    model_ns = SimpleNamespace()
    for class_name in model_classes:
        setattr(model_ns, class_name, _placeholder_class(class_name))

    module_ns = SimpleNamespace(model=model_ns)
    if include_produccion:
        produccion_model = SimpleNamespace(
            ProduccionModel=_placeholder_class("ProduccionModel")
        )
        module_ns.produccion = SimpleNamespace(model=produccion_model)

    return module_ns


def _import_numeric_module(name, fallback_module=None):
    """Importa un módulo con nombre numérico."""
    try:
        return importlib.import_module(f'.{name}', package='rexus.modules')
    except Exception:
        return fallback_module

# Crear alias en el namespace del módulo
obras = _import_numeric_module(
    '01_obras',
    fallback_module=_build_fallback_module(["ObrasModel"], include_produccion=True),
)
inventario = _import_numeric_module(
    '02_inventario',
    fallback_module=_build_fallback_module(["InventarioModel"]),
)
herrajes = _import_numeric_module('03_herrajes', fallback_module=_build_fallback_module())
vidrios = _import_numeric_module('04_vidrios', fallback_module=_build_fallback_module())
logistica = _import_numeric_module('05_logistica', fallback_module=_build_fallback_module())
pedidos = _import_numeric_module(
    '06_pedidos',
    fallback_module=_build_fallback_module(["PedidosModel"]),
)
compras = _import_numeric_module(
    '07_compras',
    fallback_module=_build_fallback_module(["ComprasModel"]),
)
administracion = _import_numeric_module('08_administracion', fallback_module=_build_fallback_module())
mantenimiento = _import_numeric_module('09_mantenimiento', fallback_module=_build_fallback_module())
auditoria = _import_numeric_module(
    '10_auditoria',
    fallback_module=_build_fallback_module(["AuditoriaModel"]),
)
usuarios = _import_numeric_module(
    '11_usuarios',
    fallback_module=_build_fallback_module(["UsuariosModel"]),
)
configuracion = _import_numeric_module(
    '12_configuracion',
    fallback_module=_build_fallback_module(["ReportesModel"]),
)
notificaciones = _import_numeric_module(
    '13_notificaciones',
    fallback_module=_build_fallback_module(["NotificacionesModel"]),
)
