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
    logger.critical()
    for error in report['critical_errors']:
        logger.critical(f"- {error}")
    sys.exit(1)
else:
    logger.info("Todas las dependencias críticas están disponibles")
"""