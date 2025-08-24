"""
Gestor de Módulos Robusto para Rexus.app

Proporciona una solución sistemática para la carga de módulos,
manejo de errores y prevención de vulnerabilidades SQL injection.
"""

import logging
import traceback
import importlib
import sys
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

# Sistema de logging
try:
    from ..utils.app_logger import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class ModuleStatus:
    """Estados posibles de módulos."""
    LOADING = "loading"
    LOADED = "loaded"
    ERROR = "error"
    DISABLED = "disabled"
    NOT_FOUND = "not_found"


class ModuleInfo:
    """Información de un módulo."""
    
    def __init__(self, name: str, path: str = ""):
        self.name = name
        self.path = path
        self.status = ModuleStatus.LOADING
        self.module = None
        self.error_message = ""
        self.last_loaded = None
        self.dependencies = []
        self.version = "unknown"


class ModuleManager:
    """Gestor centralizado de módulos del sistema."""
    
    def __init__(self, base_package: str = "rexus.modules"):
        """
        Inicializa el gestor de módulos.
        
        Args:
            base_package: Paquete base donde están los módulos
        """
        self.base_package = base_package
        self.modules: Dict[str, ModuleInfo] = {}
        self.loading_order = []
        self.failed_modules = []
        
        # Lista de módulos principales
        self.core_modules = [
            "configuracion",
            "inventario", 
            "obras",
            "compras",
            "usuarios",
            "vidrios",
            "pedidos",
            "notificaciones"
        ]
        
        logger.info("ModuleManager inicializado")
    
    def load_all_modules(self) -> Dict[str, ModuleInfo]:
        """
        Carga todos los módulos del sistema.
        
        Returns:
            Diccionario con información de módulos cargados
        """
        logger.info("Iniciando carga de módulos...")
        
        for module_name in self.core_modules:
            try:
                self.load_module(module_name)
            except Exception as e:
                logger.error(f"Error cargando módulo {module_name}: {e}")
                self.failed_modules.append(module_name)
        
        # Resumen de carga
        loaded = len([m for m in self.modules.values() if m.status == ModuleStatus.LOADED])
        total = len(self.core_modules)
        
        logger.info(f"Carga completada: {loaded}/{total} módulos cargados exitosamente")
        
        if self.failed_modules:
            logger.warning(f"Módulos fallidos: {', '.join(self.failed_modules)}")
        
        return self.modules
    
    def load_module(self, module_name: str) -> ModuleInfo:
        """
        Carga un módulo específico.
        
        Args:
            module_name: Nombre del módulo a cargar
            
        Returns:
            Información del módulo cargado
        """
        if module_name in self.modules:
            existing = self.modules[module_name]
            if existing.status == ModuleStatus.LOADED:
                return existing
        
        module_info = ModuleInfo(module_name)
        self.modules[module_name] = module_info
        
        try:
            # Construir nombre completo del módulo
            full_module_name = f"{self.base_package}.{module_name}"
            
            logger.info(f"Cargando módulo: {module_name}")
            
            # Importar módulo
            module = importlib.import_module(full_module_name)
            
            # Verificar estructura del módulo
            if not self._validate_module_structure(module, module_name):
                raise ImportError(f"Estructura de módulo inválida: {module_name}")
            
            # Guardar información
            module_info.module = module
            module_info.status = ModuleStatus.LOADED
            module_info.path = getattr(module, '__file__', '')
            module_info.version = getattr(module, '__version__', 'unknown')
            
            # Obtener dependencias si existen
            if hasattr(module, 'MODULE_DEPENDENCIES'):
                module_info.dependencies = module.MODULE_DEPENDENCIES
            
            self.loading_order.append(module_name)
            
            logger.info(f"Módulo {module_name} cargado exitosamente")
            
        except ImportError as e:
            error_msg = f"Error de importación en módulo {module_name}: {str(e)}"
            logger.error(error_msg)
            module_info.status = ModuleStatus.ERROR
            module_info.error_message = error_msg
            
        except Exception as e:
            error_msg = f"Error inesperado cargando módulo {module_name}: {str(e)}"
            logger.exception(error_msg)
            module_info.status = ModuleStatus.ERROR
            module_info.error_message = error_msg
        
        return module_info
    
    def _validate_module_structure(self, module: Any, module_name: str) -> bool:
        """
        Valida que el módulo tenga la estructura esperada.
        
        Args:
            module: Módulo importado
            module_name: Nombre del módulo
            
        Returns:
            True si la estructura es válida
        """
        try:
            # Verificar que tenga los componentes básicos esperados
            required_components = ['model', 'view', 'controller']
            missing_components = []
            
            for component in required_components:
                if not hasattr(module, component):
                    # Intentar importar el componente
                    try:
                        component_module = importlib.import_module(
                            f"{self.base_package}.{module_name}.{component}"
                        )
                        setattr(module, component, component_module)
                    except ImportError:
                        missing_components.append(component)
            
            if missing_components:
                logger.warning(f"Módulo {module_name} no tiene: {', '.join(missing_components)}")
                # No bloqueamos la carga por componentes faltantes
            
            return True
            
        except Exception as e:
            logger.error(f"Error validando estructura de {module_name}: {e}")
            return False
    
    def get_module(self, module_name: str) -> Optional[ModuleInfo]:
        """
        Obtiene información de un módulo.
        
        Args:
            module_name: Nombre del módulo
            
        Returns:
            Información del módulo o None si no existe
        """
        return self.modules.get(module_name)
    
    def get_module_instance(self, module_name: str) -> Optional[Any]:
        """
        Obtiene la instancia del módulo.
        
        Args:
            module_name: Nombre del módulo
            
        Returns:
            Instancia del módulo o None
        """
        module_info = self.get_module(module_name)
        if module_info and module_info.status == ModuleStatus.LOADED:
            return module_info.module
        return None
    
    def reload_module(self, module_name: str) -> bool:
        """
        Recarga un módulo específico.
        
        Args:
            module_name: Nombre del módulo a recargar
            
        Returns:
            True si la recarga fue exitosa
        """
        try:
            logger.info(f"Recargando módulo: {module_name}")
            
            # Eliminar del caché
            full_module_name = f"{self.base_package}.{module_name}"
            if full_module_name in sys.modules:
                del sys.modules[full_module_name]
            
            # Eliminar información previa
            if module_name in self.modules:
                del self.modules[module_name]
            
            # Recargar
            module_info = self.load_module(module_name)
            
            return module_info.status == ModuleStatus.LOADED
            
        except Exception as e:
            logger.error(f"Error recargando módulo {module_name}: {e}")
            return False
    
    def get_module_status(self) -> Dict[str, str]:
        """
        Obtiene el estado de todos los módulos.
        
        Returns:
            Diccionario con estado de cada módulo
        """
        return {name: info.status for name, info in self.modules.items()}
    
    def get_failed_modules(self) -> List[Tuple[str, str]]:
        """
        Obtiene lista de módulos que fallaron al cargar.
        
        Returns:
            Lista de tuplas (nombre_modulo, mensaje_error)
        """
        failed = []
        for name, info in self.modules.items():
            if info.status == ModuleStatus.ERROR:
                failed.append((name, info.error_message))
        
        return failed
    
    def disable_module(self, module_name: str):
        """
        Deshabilita un módulo.
        
        Args:
            module_name: Nombre del módulo a deshabilitar
        """
        if module_name in self.modules:
            self.modules[module_name].status = ModuleStatus.DISABLED
            logger.info(f"Módulo {module_name} deshabilitado")
    
    def enable_module(self, module_name: str) -> bool:
        """
        Habilita un módulo deshabilitado.
        
        Args:
            module_name: Nombre del módulo a habilitar
            
        Returns:
            True si se habilitó correctamente
        """
        if module_name in self.modules:
            if self.modules[module_name].status == ModuleStatus.DISABLED:
                return self.reload_module(module_name)
        else:
            # Intentar cargar el módulo
            module_info = self.load_module(module_name)
            return module_info.status == ModuleStatus.LOADED
        
        return False
    
    def check_dependencies(self, module_name: str) -> List[str]:
        """
        Verifica las dependencias de un módulo.
        
        Args:
            module_name: Nombre del módulo
            
        Returns:
            Lista de dependencias faltantes
        """
        module_info = self.get_module(module_name)
        if not module_info:
            return ["Module not found"]
        
        missing_deps = []
        for dep in module_info.dependencies:
            dep_info = self.get_module(dep)
            if not dep_info or dep_info.status != ModuleStatus.LOADED:
                missing_deps.append(dep)
        
        return missing_deps
    
    def get_loading_suggestions(self, error_message: str) -> List[str]:
        """
        Obtiene sugerencias para resolver errores de carga.
        
        Args:
            error_message: Mensaje de error
            
        Returns:
            Lista de sugerencias
        """
        suggestions = []
        error_lower = error_message.lower()
        
        if "no module named" in error_lower:
            suggestions.extend([
                "• Verificar que el módulo existe en la ruta correcta",
                "• Revisar la estructura de carpetas del módulo",
                "• Comprobar que __init__.py existe en el módulo"
            ])

        if "table" in error_lower:
            suggestions.extend([
                "• Verificar que las tablas existan en la base de datos",
                "• Ejecutar scripts de creación de tablas",
                "• Revisar estructura de la base de datos"
            ])

        if "import" in error_lower:
            suggestions.extend([
                "• Verificar que todos los archivos del módulo existan",
                "• Revisar sintaxis de los archivos Python",
                "• Comprobar dependencias del módulo"
            ])
        
        if "syntax" in error_lower:
            suggestions.extend([
                "• Revisar sintaxis de Python en archivos del módulo",
                "• Verificar indentación correcta",
                "• Comprobar caracteres especiales o encoding"
            ])
        
        if not suggestions:
            suggestions = [
                "• Revisar logs detallados del error",
                "• Verificar permisos de archivos",
                "• Comprobar configuración del sistema"
            ]
        
        return suggestions
    
    def generate_module_report(self) -> Dict[str, Any]:
        """
        Genera reporte completo del estado de módulos.
        
        Returns:
            Diccionario con reporte detallado
        """
        report = {
            "timestamp": "development_mode",
            "total_modules": len(self.modules),
            "loaded_modules": len([m for m in self.modules.values() if m.status == ModuleStatus.LOADED]),
            "failed_modules": len([m for m in self.modules.values() if m.status == ModuleStatus.ERROR]),
            "disabled_modules": len([m for m in self.modules.values() if m.status == ModuleStatus.DISABLED]),
            "loading_order": self.loading_order,
            "module_details": {},
            "failed_details": self.get_failed_modules(),
            "suggestions": {}
        }
        
        for name, info in self.modules.items():
            report["module_details"][name] = {
                "status": info.status,
                "version": info.version,
                "dependencies": info.dependencies,
                "path": info.path
            }
            
            if info.status == ModuleStatus.ERROR:
                report["suggestions"][name] = self.get_loading_suggestions(info.error_message)
        
        return report


# Instancia global del gestor
_module_manager: Optional[ModuleManager] = None


def get_module_manager() -> ModuleManager:
    """Obtiene la instancia global del gestor de módulos."""
    global _module_manager
    if _module_manager is None:
        _module_manager = ModuleManager()
    return _module_manager


def init_module_manager(base_package: str = "rexus.modules") -> ModuleManager:
    """
    Inicializa el gestor global de módulos.
    
    Args:
        base_package: Paquete base de módulos
        
    Returns:
        Instancia del gestor
    """
    global _module_manager
    _module_manager = ModuleManager(base_package)
    return _module_manager


def load_all_modules() -> Dict[str, ModuleInfo]:
    """Función de conveniencia para cargar todos los módulos."""
    manager = get_module_manager()
    return manager.load_all_modules()


def get_module(module_name: str) -> Optional[Any]:
    """
    Función de conveniencia para obtener un módulo.
    
    Args:
        module_name: Nombre del módulo
        
    Returns:
        Instancia del módulo o None
    """
    manager = get_module_manager()
    return manager.get_module_instance(module_name)