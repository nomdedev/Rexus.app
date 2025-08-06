"""
Sistema de Integración Principal - Rexus.app
Coordina todos los sistemas auxiliares y proporciona interfaz unificada
"""

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QWidget


@dataclass
class ModuleInfo:
    """Información de un módulo del sistema."""

    name: str
    display_name: str
    widget_class: Optional[type]
    controller_class: Optional[type] = None
    icon_path: Optional[str] = None
    description: str = ""
    keyboard_enabled: bool = True
    error_enabled: bool = True
    loading_enabled: bool = True


class SystemEvent:
    """Eventos del sistema."""

    MODULE_LOADED = "module_loaded"
    MODULE_UNLOADED = "module_unloaded"
    ERROR_OCCURRED = "error_occurred"
    DATA_UPDATED = "data_updated"
    USER_ACTION = "user_action"
    NAVIGATION_CHANGED = "navigation_changed"


class SystemIntegrationManager(QObject):
    """Gestor principal de integración del sistema."""

    # Señales del sistema
    module_loaded = pyqtSignal(str)  # module_name
    module_unloaded = pyqtSignal(str)  # module_name
    error_occurred = pyqtSignal(str, str, str)  # module, error_code, message
    data_updated = pyqtSignal(str, dict)  # module, data
    user_action = pyqtSignal(str, str, dict)  # module, action, data

    def __init__(self):
        super().__init__()
        self.modules: Dict[str, ModuleInfo] = {}
        self.active_modules: Dict[str, QWidget] = {}
        self.system_config = {}
        self.event_handlers: Dict[str, List[Callable]] = {}

        # Sistemas auxiliares
        self.loading_manager = None
        self.error_manager = None
        self.navigation_manager = None

        self.setup_system()

    def setup_system(self):
        """Configura el sistema principal."""
        self.register_system_modules()
        self.setup_event_handlers()
        self.load_system_config()

    def register_system_modules(self):
        """Registra todos los módulos del sistema."""
        # Módulos principales
        modules_config = [
            ModuleInfo(
                name="herrajes",
                display_name="Gestión de Herrajes",
                widget_class=None,  # Se carga dinámicamente
                icon_path="resources/icons/herrajes.png",
                description="Gestión completa de herrajes y componentes",
                keyboard_enabled=True,
                error_enabled=True,
                loading_enabled=True,
            ),
            ModuleInfo(
                name="usuarios",
                display_name="Gestión de Usuarios",
                widget_class=None,
                icon_path="resources/icons/users.png",
                description="Administración de usuarios y permisos",
                keyboard_enabled=True,
                error_enabled=True,
                loading_enabled=True,
            ),
            ModuleInfo(
                name="inventario",
                display_name="Control de Inventario",
                widget_class=None,
                icon_path="resources/icons/inventory.png",
                description="Control de stock y inventarios",
                keyboard_enabled=True,
                error_enabled=True,
                loading_enabled=True,
            ),
            ModuleInfo(
                name="obras",
                display_name="Gestión de Obras",
                widget_class=None,
                icon_path="resources/icons/works.png",
                description="Administración de obras y proyectos",
                keyboard_enabled=True,
                error_enabled=True,
                loading_enabled=True,
            ),
            ModuleInfo(
                name="pedidos",
                display_name="Gestión de Pedidos",
                widget_class=None,
                icon_path="resources/icons/orders.png",
                description="Procesamiento de pedidos y ventas",
                keyboard_enabled=True,
                error_enabled=True,
                loading_enabled=True,
            ),
            ModuleInfo(
                name="logistica",
                display_name="Logística",
                widget_class=None,
                icon_path="resources/icons/logistics.png",
                description="Gestión logística y distribución",
                keyboard_enabled=True,
                error_enabled=True,
                loading_enabled=True,
            ),
            ModuleInfo(
                name="mantenimiento",
                display_name="Mantenimiento",
                widget_class=None,
                icon_path="resources/icons/maintenance.png",
                description="Mantenimiento del sistema",
                keyboard_enabled=True,
                error_enabled=True,
                loading_enabled=True,
            ),
            ModuleInfo(
                name="configuracion",
                display_name="Configuración",
                widget_class=None,
                icon_path="resources/icons/settings.png",
                description="Configuración del sistema",
                keyboard_enabled=True,
                error_enabled=True,
                loading_enabled=True,
            ),
            ModuleInfo(
                name="administracion",
                display_name="Administración",
                widget_class=None,
                icon_path="resources/icons/admin.png",
                description="Administración general del sistema",
                keyboard_enabled=True,
                error_enabled=True,
                loading_enabled=True,
            ),
            ModuleInfo(
                name="auditoria",
                display_name="Auditoría",
                widget_class=None,
                icon_path="resources/icons/audit.png",
                description="Auditoría y seguimiento",
                keyboard_enabled=True,
                error_enabled=True,
                loading_enabled=True,
            ),
            ModuleInfo(
                name="vidrios",
                display_name="Gestión de Vidrios",
                widget_class=None,
                icon_path="resources/icons/glass.png",
                description="Gestión de vidrios y cristales",
                keyboard_enabled=True,
                error_enabled=True,
                loading_enabled=True,
            ),
            ModuleInfo(
                name="reportes",
                display_name="Reportes",
                widget_class=None,
                icon_path="resources/icons/reports.png",
                description="Generación de reportes",
                keyboard_enabled=True,
                error_enabled=True,
                loading_enabled=True,
            ),
        ]

        for module_info in modules_config:
            self.modules[module_info.name] = module_info

    def setup_event_handlers(self):
        """Configura los manejadores de eventos del sistema."""
        self.register_event_handler(SystemEvent.MODULE_LOADED, self._on_module_loaded)
        self.register_event_handler(SystemEvent.ERROR_OCCURRED, self._on_error_occurred)
        self.register_event_handler(SystemEvent.DATA_UPDATED, self._on_data_updated)

    def load_system_config(self):
        """Carga la configuración del sistema."""
        self.system_config = {
            "keyboard_navigation_enabled": True,
            "error_management_enabled": True,
            "loading_indicators_enabled": True,
            "tooltips_enabled": True,
            "auto_save_enabled": False,
            "theme": "modern",
            "language": "es",
            "debug_mode": False,
        }

    def register_event_handler(self, event_type: str, handler: Callable):
        """Registra un manejador para un tipo de evento."""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)

    def emit_system_event(self, event_type: str, **kwargs):
        """Emite un evento del sistema."""
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    handler(**kwargs)
                except Exception as e:
                    print(f"Error en manejador de evento {event_type}: {e}")

    def load_module(
        self, module_name: str, parent_widget: Optional[QWidget] = None
    ) -> Optional[QWidget]:
        """Carga un módulo específico."""
        if module_name not in self.modules:
            self.emit_system_event(
                SystemEvent.ERROR_OCCURRED,
                module=module_name,
                error_code="MODULE_NOT_FOUND",
                message=f"Módulo {module_name} no encontrado",
            )
            return None

        try:
            module_info = self.modules[module_name]

            # Cargar dinámicamente el widget del módulo
            widget = self._load_module_widget(module_name, module_info, parent_widget)

            if widget:
                # Configurar sistemas auxiliares
                self._setup_module_systems(widget, module_info)

                # Registrar módulo activo
                self.active_modules[module_name] = widget

                # Emitir evento
                self.module_loaded.emit(module_name)
                self.emit_system_event(
                    SystemEvent.MODULE_LOADED, module=module_name, widget=widget
                )

                return widget

        except Exception as e:
            self.emit_system_event(
                SystemEvent.ERROR_OCCURRED,
                module=module_name,
                error_code="LOAD_ERROR",
                message=f"Error cargando módulo: {e}",
            )

        return None

    def _load_module_widget(
        self, module_name: str, module_info: ModuleInfo, parent: Optional[QWidget]
    ) -> Optional[QWidget]:
        """Carga el widget de un módulo específico."""
        try:
            # Importación dinámica basada en estructura del proyecto
            if module_name == "herrajes":
                from rexus.modules.herrajes.view_simple import HerrajesViewSimple

                return HerrajesViewSimple()
            elif module_name == "usuarios":
                from rexus.modules.usuarios.view_modern import UsuariosViewModern

                return UsuariosViewModern()
            else:
                # Para otros módulos, usar importación genérica
                module_path = f"rexus.modules.{module_name}.view"
                view_module = __import__(
                    module_path, fromlist=[f"{module_name.title()}View"]
                )
                view_class = getattr(view_module, f"{module_name.title()}View")
                return view_class()

        except ImportError as e:
            print(f"No se pudo importar el módulo {module_name}: {e}")
            return None

    def _setup_module_systems(self, widget: QWidget, module_info: ModuleInfo):
        """Configura los sistemas auxiliares para un módulo."""
        # Configurar navegación por teclado
        if module_info.keyboard_enabled and hasattr(
            widget, "setup_keyboard_navigation"
        ):
            try:
                getattr(widget, "setup_keyboard_navigation")()
            except Exception as e:
                print(f"Error configurando navegación en {module_info.name}: {e}")

        # Configurar manejo de errores
        if module_info.error_enabled and hasattr(widget, "setup_error_handling"):
            try:
                getattr(widget, "setup_error_handling")()
            except Exception as e:
                print(f"Error configurando errores en {module_info.name}: {e}")

        # Configurar indicadores de carga
        if module_info.loading_enabled and hasattr(widget, "loading_manager"):
            try:
                # El loading_manager ya debería estar configurado en el widget
                pass
            except Exception as e:
                print(f"Error configurando loading en {module_info.name}: {e}")

    def unload_module(self, module_name: str):
        """Descarga un módulo específico."""
        if module_name in self.active_modules:
            widget = self.active_modules[module_name]

            # Limpiar recursos del módulo
            self._cleanup_module(widget)

            # Remover de módulos activos
            del self.active_modules[module_name]

            # Emitir evento
            self.module_unloaded.emit(module_name)
            self.emit_system_event(SystemEvent.MODULE_UNLOADED, module=module_name)

    def _cleanup_module(self, widget: QWidget):
        """Limpia los recursos de un módulo."""
        try:
            # Limpiar timers, conexiones, etc.
            if hasattr(widget, "cleanup") and callable(
                getattr(widget, "cleanup", None)
            ):
                getattr(widget, "cleanup")()

            # Cerrar y eliminar widget
            widget.close()
            widget.deleteLater()

        except Exception as e:
            print(f"Error limpiando módulo: {e}")

    def get_module_info(self, module_name: str) -> Optional[ModuleInfo]:
        """Obtiene información de un módulo."""
        return self.modules.get(module_name)

    def get_active_modules(self) -> List[str]:
        """Obtiene la lista de módulos activos."""
        return list(self.active_modules.keys())

    def is_module_loaded(self, module_name: str) -> bool:
        """Verifica si un módulo está cargado."""
        return module_name in self.active_modules

    def get_system_status(self) -> Dict[str, Any]:
        """Obtiene el estado del sistema."""
        return {
            "modules_registered": len(self.modules),
            "modules_active": len(self.active_modules),
            "active_modules": list(self.active_modules.keys()),
            "system_config": self.system_config,
            "keyboard_enabled": self.system_config.get(
                "keyboard_navigation_enabled", True
            ),
            "error_management_enabled": self.system_config.get(
                "error_management_enabled", True
            ),
            "loading_enabled": self.system_config.get(
                "loading_indicators_enabled", True
            ),
        }

    # Manejadores de eventos internos
    def _on_module_loaded(self, module: str, widget: Optional[QWidget] = None):
        """Manejador para cuando se carga un módulo."""
        print(f"Módulo {module} cargado exitosamente")

    def _on_error_occurred(self, module: str, error_code: str, message: str):
        """Manejador para errores del sistema."""
        print(f"Error en {module} [{error_code}]: {message}")

    def _on_data_updated(self, module: str, data: dict):
        """Manejador para actualizaciones de datos."""
        print(f"Datos actualizados en {module}: {len(data)} elementos")


class ModuleFactory:
    """Factory para crear módulos del sistema."""

    def __init__(self, integration_manager: SystemIntegrationManager):
        self.integration_manager = integration_manager

    def create_module(
        self, module_name: str, parent: Optional[QWidget] = None
    ) -> Optional[QWidget]:
        """Crea una instancia de un módulo."""
        return self.integration_manager.load_module(module_name, parent)

    def create_modernized_module(
        self, module_name: str, parent: Optional[QWidget] = None
    ) -> Optional[QWidget]:
        """Crea un módulo con todas las mejoras aplicadas."""
        widget = self.create_module(module_name, parent)

        if widget:
            # Aplicar mejoras adicionales
            self._apply_modern_features(widget, module_name)

        return widget

    def _apply_modern_features(self, widget: QWidget, module_name: str):
        """Aplica características modernas a un módulo."""
        # Aplicar theme moderno
        self._apply_modern_theme(widget, module_name)

        # Configurar tooltips
        self._setup_tooltips(widget)

        # Configurar accesibilidad
        self._setup_accessibility(widget)

    def _apply_modern_theme(self, widget: QWidget, module_name: str):
        """Aplica el theme moderno específico del módulo."""
        # Themes por módulo (ya implementados en herrajes y usuarios)
        themes = {
            "herrajes": "blue",
            "usuarios": "green",
            "inventario": "orange",
            "obras": "purple",
            "pedidos": "red",
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
