"""
Validador de Dependencias Críticas para Rexus.app
Verifica que todos los componentes críticos estén disponibles antes del arranque

Fecha: 15/08/2025
Objetivo: Validar dependencias críticas para evitar fallos en runtime
"""

import importlib
import inspect
import logging
import sys
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path

# Configurar logger
logger = logging.getLogger(__name__)


class DependencyValidationError(Exception):
    """Excepción para errores de validación de dependencias."""
    pass


class DependencyValidator:
    """
    Validador de dependencias críticas del sistema.
    
    Verifica:
    - Módulos de Python requeridos
    - Componentes internos críticos
    - Bases de datos requeridas
    - Archivos de configuración
    - Permisos de sistema
    """
    
    def __init__(self):
        self.validation_results = {}
        self.critical_errors = []
        self.warnings = []
        
        # Dependencias críticas del sistema
        self.critical_dependencies = {
            'python_modules': [
                'PyQt6',
                'PyQt6.QtCore',
                'PyQt6.QtWidgets',
                'PyQt6.QtGui',
                'sqlite3',
                'pathlib',
                'typing',
                'datetime'
            ],
            'optional_modules': [
                'dotenv',
                'requests',
                'pandas',
                'openpyxl'
            ],
            'rexus_core': [
                'rexus.core.database',
                'rexus.core.security',
                'rexus.core.module_manager',
                'rexus.utils.sql_query_manager',
                'rexus.utils.unified_sanitizer'
            ],
            'rexus_modules': [
                'rexus.modules.inventario',
                'rexus.modules.obras',
                'rexus.modules.usuarios',
                'rexus.modules.compras',
                'rexus.modules.pedidos'
            ]
        }
        
        # Archivos críticos requeridos
        self.critical_files = [
            'main.py',
            'requirements.txt',
            'rexus/main/app.py',
            'rexus/core/__init__.py',
            'rexus/utils/__init__.py'
        ]
        
        # Directorios críticos
        self.critical_directories = [
            'rexus/',
            'rexus/core/',
            'rexus/utils/',
            'rexus/modules/',
            'rexus/ui/'
        ]
    
    def validate_all(self) -> Dict[str, Any]:
        """
        Ejecuta todas las validaciones críticas.
        
        Returns:
            Dict con resultados de validación y errores encontrados
        """
        try:
            self._reset_validation_state()
            
            # Validaciones en orden de criticidad
            self._validate_python_environment()
            self._validate_critical_modules()
            self._validate_rexus_core_components()
            self._validate_file_structure()
            self._validate_database_components()
            self._validate_security_components()
            
            # Generar resumen
            return self._generate_validation_report()
            
        except Exception as e:
            self.critical_errors.append(f"Error durante validación: {e}")
            return self._generate_error_report()
    
    def _reset_validation_state(self):
        """Resetea el estado de validación."""
        self.validation_results = {}
        self.critical_errors = []
        self.warnings = []
    
    def _validate_python_environment(self):
        """Valida el entorno de Python."""
        results = {
            'python_version': sys.version,
            'python_executable': sys.executable,
            'platform': sys.platform
        }
        
        # Verificar versión mínima de Python
        if sys.version_info < (3, 8):
            self.critical_errors.append(
                f"Python {sys.version_info.major}.{sys.version_info.minor} "
                "no soportado. Se requiere Python 3.8 o superior."
            )
        
        self.validation_results['python_environment'] = results
    
    def _validate_critical_modules(self):
        """Valida módulos críticos de Python."""
        critical_results = {}
        optional_results = {}
        
        # Validar módulos críticos
        for module_name in self.critical_dependencies['python_modules']:
            try:
                module = importlib.import_module(module_name)
                critical_results[module_name] = {
                    'available': True,
                    'version': getattr(module, '__version__', 'unknown'),
                    'path': getattr(module, '__file__', 'unknown')
                }
            except ImportError as e:
                critical_results[module_name] = {
                    'available': False,
                    'error': str(e)
                }
                self.critical_errors.append(f"Módulo crítico faltante: {module_name}")
        
        # Validar módulos opcionales
        for module_name in self.critical_dependencies['optional_modules']:
            try:
                module = importlib.import_module(module_name)
                optional_results[module_name] = {
                    'available': True,
                    'version': getattr(module, '__version__', 'unknown')
                }
            except ImportError:
                optional_results[module_name] = {'available': False}
                self.warnings.append(f"Módulo opcional no disponible: {module_name}")
        
        self.validation_results['critical_modules'] = critical_results
        self.validation_results['optional_modules'] = optional_results
    
    def _validate_rexus_core_components(self):
        """Valida componentes core de Rexus."""
        core_results = {}
        module_results = {}
        
        # Validar componentes core
        for component in self.critical_dependencies['rexus_core']:
            try:
                module = importlib.import_module(component)
                core_results[component] = {
                    'available': True,
                    'path': getattr(module, '__file__', 'unknown'),
                    'functions': [name for name, obj in inspect.getmembers(module) 
                                if inspect.isfunction(obj) or inspect.isclass(obj)]
                }
            except ImportError as e:
                core_results[component] = {
                    'available': False,
                    'error': str(e)
                }
                self.critical_errors.append(f"Componente core faltante: {component}")
        
        # Validar módulos de negocio
        for module in self.critical_dependencies['rexus_modules']:
            try:
                imported_module = importlib.import_module(module)
                module_results[module] = {
                    'available': True,
                    'has_view': hasattr(imported_module, 'view') or self._check_view_file(module),
                    'has_model': hasattr(imported_module, 'model') or self._check_model_file(module)
                }
            except ImportError as e:
                module_results[module] = {
                    'available': False,
                    'error': str(e)
                }
                self.warnings.append(f"Módulo de negocio no disponible: {module}")
        
        self.validation_results['rexus_core'] = core_results
        self.validation_results['rexus_modules'] = module_results
    
    def _check_view_file(self, module_path: str) -> bool:
        """Verifica si existe archivo view.py para el módulo."""
        view_path = Path(module_path.replace('.', '/')) / 'view.py'
        return view_path.exists()
    
    def _check_model_file(self, module_path: str) -> bool:
        """Verifica si existe archivo model.py para el módulo."""
        model_path = Path(module_path.replace('.', '/')) / 'model.py'
        return model_path.exists()
    
    def _validate_file_structure(self):
        """Valida la estructura de archivos críticos."""
        file_results = {}
        directory_results = {}
        
        # Validar archivos críticos
        for file_path in self.critical_files:
            path = Path(file_path)
            file_results[file_path] = {
                'exists': path.exists(),
                'is_file': path.is_file() if path.exists() else False,
                'size': path.stat().st_size if path.exists() else 0,
                'readable': path.is_file() and path.stat().st_mode & 0o444 if path.exists() else False
            }
            
            if not path.exists():
                self.critical_errors.append(f"Archivo crítico faltante: {file_path}")
        
        # Validar directorios críticos
        for dir_path in self.critical_directories:
            path = Path(dir_path)
            directory_results[dir_path] = {
                'exists': path.exists(),
                'is_directory': path.is_dir() if path.exists() else False,
                'readable': path.is_dir() and path.stat().st_mode & 0o444 if path.exists() else False,
                'writable': path.is_dir() and path.stat().st_mode & 0o200 if path.exists() else False
            }
            
            if not path.exists():
                self.critical_errors.append(f"Directorio crítico faltante: {dir_path}")
        
        self.validation_results['file_structure'] = {
            'files': file_results,
            'directories': directory_results
        }
    
    def _validate_database_components(self):
        """Valida componentes de base de datos."""
        db_results = {}
        
        try:
            # Verificar disponibilidad de componentes de BD
            from rexus.core.database import get_inventario_connection
            db_results['inventario_connection'] = {'available': True}
        except ImportError:
            db_results['inventario_connection'] = {'available': False}
            self.warnings.append("Conexión de BD inventario no disponible")
        
        try:
            from rexus.core.database import get_users_connection
            db_results['users_connection'] = {'available': True}
        except ImportError:
            db_results['users_connection'] = {'available': False}
            self.warnings.append("Conexión de BD usuarios no disponible")
        
        try:
            from rexus.utils.sql_query_manager import SQLQueryManager
            sql_manager = SQLQueryManager()
            db_results['sql_query_manager'] = {
                'available': True,
                'has_get_query': hasattr(sql_manager, 'get_query')
            }
        except ImportError:
            db_results['sql_query_manager'] = {'available': False}
            self.critical_errors.append("SQLQueryManager no disponible")
        
        self.validation_results['database_components'] = db_results
    
    def _validate_security_components(self):
        """Valida componentes de seguridad."""
        security_results = {}
        
        try:
            from rexus.core.security import init_security_manager
            security_results['security_manager'] = {'available': True}
        except ImportError:
            security_results['security_manager'] = {'available': False}
            self.critical_errors.append("SecurityManager no disponible")
        
        try:
            from rexus.utils.unified_sanitizer import unified_sanitizer
            security_results['sanitizer'] = {
                'available': True,
                'has_sanitize_dict': hasattr(unified_sanitizer, 'sanitize_dict')
            }
        except ImportError:
            security_results['sanitizer'] = {'available': False}
            self.warnings.append("Sanitizador unificado no disponible")
        
        self.validation_results['security_components'] = security_results
    
    def _generate_validation_report(self) -> Dict[str, Any]:
        """Genera reporte final de validación."""
        total_critical_errors = len(self.critical_errors)
        total_warnings = len(self.warnings)
        
        return {
            'status': 'FAILED' if total_critical_errors > 0 else 'PASSED',
            'critical_errors_count': total_critical_errors,
            'warnings_count': total_warnings,
            'critical_errors': self.critical_errors,
            'warnings': self.warnings,
            'details': self.validation_results,
            'can_start_application': total_critical_errors == 0
        }
    
    def _generate_error_report(self) -> Dict[str, Any]:
        """Genera reporte de error cuando falla la validación."""
        return {
            'status': 'ERROR',
            'critical_errors_count': len(self.critical_errors),
            'warnings_count': len(self.warnings),
            'critical_errors': self.critical_errors,
            'warnings': self.warnings,
            'details': self.validation_results,
            'can_start_application': False
        }
    
    def validate_module_manager(self) -> bool:
        """
        Valida específicamente el module_manager que fue mencionado en la auditoría.
        
        Returns:
            bool: True si module_manager está disponible y funcional
        """
        try:
            from rexus.core.module_manager import ModuleManager
            
            # Verificar que tiene métodos críticos
            required_methods = ['create_module_safely', 'get_available_modules']
            for method in required_methods:
                if not hasattr(ModuleManager, method):
                    self.critical_errors.append(f"ModuleManager falta método crítico: {method}")
                    return False
            
            return True
            
        except ImportError as e:
            self.critical_errors.append(f"ModuleManager no disponible: {e}")
            return False
    
    def print_validation_summary(self, report: Dict[str, Any]):
        """Imprime resumen de validación usando logger."""
        logger.info("\n" + "="*60)
        logger.info("REPORTE DE VALIDACIÓN DE DEPENDENCIAS REXUS.APP")
        logger.info("="*60)
        logger.info(f"Estado: {report['status']}")
        logger.info(f"Errores Críticos: {report['critical_errors_count']}")
        logger.info(f"Advertencias: {report['warnings_count']}")
        logger.info(f"Puede Iniciar Aplicación: {'SÍ' if report['can_start_application'] else 'NO'}")
        
        if report['critical_errors']:
            logger.error("\nERRORES CRÍTICOS:")
            for error in report['critical_errors']:
                logger.error(f"  ❌ {error}")
        
        if report['warnings']:
            logger.warning("\nADVERTENCIAS:")
            for warning in report['warnings']:
                logger.warning(f"  ⚠️  {warning}")
        
        logger.info("\n" + "="*60)


# Función de conveniencia para validación rápida
def validate_system_dependencies() -> Tuple[bool, Dict[str, Any]]:
    """
    Valida todas las dependencias del sistema.
    
    Returns:
        Tuple[bool, Dict]: (puede_iniciar, reporte_detallado)
    """
    validator = DependencyValidator()
    report = validator.validate_all()
    return report['can_start_application'], report


def validate_critical_components() -> bool:
    """
    Validación rápida solo de componentes críticos.
    
    Returns:
        bool: True si todos los componentes críticos están disponibles
    """
    validator = DependencyValidator()
    
    # Solo validar lo absolutamente crítico
    validator._validate_python_environment()
    validator._validate_critical_modules()
    validator._validate_rexus_core_components()
    
    return len(validator.critical_errors) == 0


# Ejemplo de uso:
"""
# En app.py, antes de inicializar la aplicación:
from rexus.utils.dependency_validator import validate_system_dependencies

can_start, report = validate_system_dependencies()
if not can_start:
    logger.critical("No se puede iniciar la aplicación debido a dependencias faltantes:")
    for error in report['critical_errors']:
        logger.critical(f"- {error}")
    sys.exit(1)
else:
    logger.info("Todas las dependencias críticas están disponibles")
"""