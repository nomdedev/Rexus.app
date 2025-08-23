"""
Sistema de Integración Principal - Rexus.app
Coordina todos los sistemas auxiliares y proporciona interfaz unificada
"""


import logging
logger = logging.getLogger(__name__)

                        "logistica": "teal",
            "mantenimiento": "gray",
            "configuracion": "indigo",
            "administracion": "navy",
            "auditoria": "brown",
            "vidrios": "cyan",
            "reportes": "lime",
        }

        theme_color = themes.get(module_name, "blue")
        widget.setProperty("module_theme", theme_color)

    def _setup_tooltips(self, widget: QWidget):
        """Configura tooltips para el widget."""
        if hasattr(widget, "setup_tooltips") and callable(
            getattr(widget, "setup_tooltips", None)
        ):
            getattr(widget, "setup_tooltips")()

    def _setup_accessibility(self, widget: QWidget):
        """Configura características de accesibilidad."""
        if hasattr(widget, "setup_accessibility") and callable(
            getattr(widget, "setup_accessibility", None)
        ):
            getattr(widget, "setup_accessibility")()


# Instancia global del sistema de integración
_system_integration_manager = None


def get_system_integration_manager() -> SystemIntegrationManager:
    """Obtiene la instancia global del gestor de integración."""
    global _system_integration_manager
    if _system_integration_manager is None:
        _system_integration_manager = SystemIntegrationManager()
    return _system_integration_manager


def setup_system_integration() -> SystemIntegrationManager:
    """Configura e inicializa el sistema de integración."""
    manager = get_system_integration_manager()
    return manager


def create_module(
    module_name: str, parent: Optional[QWidget] = None
) -> Optional[QWidget]:
    """Función de conveniencia para crear módulos."""
    manager = get_system_integration_manager()
    factory = ModuleFactory(manager)
    return factory.create_modernized_module(module_name, parent)
