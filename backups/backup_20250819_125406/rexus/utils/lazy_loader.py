#!/usr/bin/env python3
"""
Sistema de Carga Bajo Demanda para Rexus
Optimiza la carga de módulos y componentes
"""

import importlib
import sys
import time
from typing import Any, Dict, Optional
from functools import wraps

class LazyLoader:
    """Cargador lazy para módulos y componentes"""

    def __init__(self):
        self._loaded_modules: Dict[str, Any] = {}
        self._loading_stats: Dict[str, Dict] = {}

    def load_module(self, module_path: str, reload: bool = False) -> Optional[Any]:
        """Carga un módulo bajo demanda"""
        if module_path in self._loaded_modules and not reload:
            return self._loaded_modules[module_path]

        try:
            start_time = time.time()

            if reload and module_path in sys.modules:
                module = importlib.reload(sys.modules[module_path])
            else:
                module = importlib.import_module(module_path)

            load_time = time.time() - start_time

            self._loaded_modules[module_path] = module
            self._loading_stats[module_path] = {
                'load_time': load_time,
                'loaded_at': time.time(),
                'reload_count': self._loading_stats.get(module_path, {}).get('reload_count', 0) + (1 if reload else 0)
            }

            return module

        except ImportError as e:
            print(f"Error cargando módulo {module_path}: {e}")
            return None

    def load_class(self,
module_path: str,
        class_name: str,
        *args,
        **kwargs) -> Optional[Any]:
        """Carga una clase específica bajo demanda"""
        module = self.load_module(module_path)
        if module and hasattr(module, class_name):
            cls = getattr(module, class_name)
            return cls(*args, **kwargs) if args or kwargs else cls
        return None

    def preload_critical_modules(self, module_list: list):
        """Precarga módulos críticos"""
        print("Precargando módulos críticos...")
        for module_path in module_list:
            self.load_module(module_path)

    def get_loading_stats(self) -> Dict:
        """Obtiene estadísticas de carga"""
        return {
            'loaded_modules': len(self._loaded_modules),
            'total_load_time': sum(stats['load_time'] for stats in self._loading_stats.values()),
            'modules_detail': self._loading_stats
        }

# Instancia global del lazy loader
lazy_loader = LazyLoader()

def lazy_import(module_path: str):
    """Decorador para importación lazy"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            module = lazy_loader.load_module(module_path)
            if module:
                return func(module, *args, **kwargs)
            else:
                raise ImportError(f"No se pudo cargar el módulo {module_path}")
        return wrapper
    return decorator

def preload_essential_modules():
    """Precarga módulos esenciales del sistema"""
    essential_modules = [
        "rexus.utils.security",
        "rexus.utils.logging_config",
        "rexus.utils.error_handler",
        "rexus.core.auth_manager"
    ]
    lazy_loader.preload_critical_modules(essential_modules)

def get_loader_stats() -> Dict:
    """Función utilitaria para obtener estadísticas del loader"""
    return lazy_loader.get_loading_stats()
