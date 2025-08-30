"""
Rexus.app - Gestor de Módulos

Módulo para gestionar los diferentes módulos del sistema.
Maneja la carga, configuración y acceso a los módulos disponibles.
"""

from typing import List, Dict, Any, Optional
import importlib

from rexus.utils.app_logger import log_info, log_error


class ModuleManager:
    """
    Gestor centralizado de módulos del sistema.
    Maneja la carga dinámica y configuración de módulos.
    """

    def __init__(self):
        self.modules = {}
        self.module_config = {}
        self._load_module_config()

    def _load_module_config(self):
        """Carga la configuración de módulos disponibles."""
        # Configuración básica de módulos
        self.module_config = {
            'dashboard': {
                'name': 'Dashboard',
                'description': 'Panel principal del sistema',
                'enabled': True,
                'icon': 'dashboard.png'
            },
            'inventory': {
                'name': 'Inventario',
                'description': 'Gestión de inventario y productos',
                'enabled': True,
                'icon': 'inventory.png'
            },
            'sales': {
                'name': 'Ventas',
                'description': 'Gestión de ventas y pedidos',
                'enabled': True,
                'icon': 'sales.png'
            },
            'purchases': {
                'name': 'Compras',
                'description': 'Gestión de compras y proveedores',
                'enabled': True,
                'icon': 'purchases.png'
            },
            'accounting': {
                'name': 'Contabilidad',
                'description': 'Módulo de contabilidad y finanzas',
                'enabled': True,
                'icon': 'accounting.png'
            },
            'reports': {
                'name': 'Reportes',
                'description': 'Sistema de reportes y análisis',
                'enabled': True,
                'icon': 'reports.png'
            },
            'administration': {
                'name': 'Administración',
                'description': 'Módulo administrativo del sistema',
                'enabled': True,
                'icon': 'admin.png'
            },
            'maintenance': {
                'name': 'Mantenimiento',
                'description': 'Módulo de mantenimiento del sistema',
                'enabled': True,
                'icon': 'maintenance.png'
            }
        }

        log_info("Configuración de módulos cargada", "module_manager")

    def get_available_modules(self, user_permissions: Optional[List[str]] = None
                              ) -> List[Dict[str, Any]]:
        """
        Obtiene la lista de módulos disponibles para un usuario.

        Args:
            user_permissions: Lista de permisos del usuario (opcional)

        Returns:
            Lista de módulos disponibles con su configuración
        """
        available_modules = []

        for module_key, config in self.module_config.items():
            if config.get('enabled', False):
                # Si se especifican permisos, verificar que el usuario tenga acceso
                if user_permissions and module_key not in user_permissions:
                    continue

                module_info = config.copy()
                module_info['key'] = module_key
                available_modules.append(module_info)

        log_info(f"Módulos disponibles: {len(available_modules)}", "module_manager")
        return available_modules

    def get_module_config(self, module_key: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene la configuración de un módulo específico.

        Args:
            module_key: Clave del módulo

        Returns:
            Configuración del módulo o None si no existe
        """
        return self.module_config.get(module_key)

    def is_module_enabled(self, module_key: str) -> bool:
        """
        Verifica si un módulo está habilitado.

        Args:
            module_key: Clave del módulo

        Returns:
            True si el módulo está habilitado
        """
        config = self.get_module_config(module_key)
        return config.get('enabled', False) if config else False

    def load_module(self, module_key: str) -> Optional[Any]:
        """
        Carga dinámicamente un módulo.

        Args:
            module_key: Clave del módulo a cargar

        Returns:
            Instancia del módulo o None si falla la carga
        """
        if module_key in self.modules:
            return self.modules[module_key]

        try:
            # Intentar importar el módulo
            module_path = f"rexus.modules.{module_key}"
            module = importlib.import_module(module_path)

            # Obtener la clase principal del módulo
            module_class = getattr(module, f"{module_key.capitalize()}Module", None)
            if module_class:
                instance = module_class()
                self.modules[module_key] = instance
                log_info(f"Módulo {module_key} cargado exitosamente", "module_manager")
                return instance

            log_error(f"No se encontró la clase principal en el módulo "
                      f"{module_key}", "module_manager")

        except ImportError as e:
            log_error(f"Error importando módulo {module_key}: {e}", "module_manager")
        except (AttributeError, TypeError, ValueError) as e:
            log_error(f"Error cargando módulo {module_key}: {e}", "module_manager")

        return None

    def get_module_names(self) -> List[str]:
        """
        Obtiene la lista de nombres de módulos disponibles.

        Returns:
            Lista de nombres de módulos
        """
        return list(self.module_config.keys())

    def get_enabled_modules(self) -> List[str]:
        """
        Obtiene la lista de módulos habilitados.

        Returns:
            Lista de claves de módulos habilitados
        """
        return [key for key, config in self.module_config.items()
                if config.get('enabled', False)]

    def enable_module(self, module_key: str) -> bool:
        """
        Habilita un módulo.

        Args:
            module_key: Clave del módulo

        Returns:
            True si se pudo habilitar
        """
        if module_key in self.module_config:
            self.module_config[module_key]['enabled'] = True
            log_info(f"Módulo {module_key} habilitado", "module_manager")
            return True
        return False

    def disable_module(self, module_key: str) -> bool:
        """
        Deshabilita un módulo.

        Args:
            module_key: Clave del módulo

        Returns:
            True si se pudo deshabilitar
        """
        if module_key in self.module_config:
            self.module_config[module_key]['enabled'] = False
            log_info(f"Módulo {module_key} deshabilitado", "module_manager")
            return True
        return False


# Instancia global del gestor de módulos
module_manager = ModuleManager()
