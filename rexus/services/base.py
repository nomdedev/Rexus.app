"""
Base Service - Servicio Base Abstracto

Proporciona la funcionalidad común para todos los servicios de negocio,
incluyendo logging, manejo de errores y coordinación de repositorios.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class ServiceResult:
    """Resultado de una operación de servicio."""
    success: bool
    data: Any = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class ValidationError:
    """Error de validación."""
    field: str
    message: str
    code: str = "VALIDATION_ERROR"


class BaseService(ABC):
    """
    Servicio base abstracto con funcionalidad común.

    Proporciona:
    - Logging estructurado
    - Manejo de errores estandarizado
    - Validaciones comunes
    - Transacciones entre repositorios
    """

    def __init__(self, repository=None, cache_manager=None):
        """
        Inicializa el servicio.

        Args:
            repository: Repositorio principal (opcional)
            cache_manager: Gestor de caché (opcional)
        """
        self.repository = repository
        self.cache_manager = cache_manager
        self._logger = logger

    # ==================== MÉTODOS DE VALIDACIÓN ====================

    def validate_required(self, data: Dict[str, Any], fields: List[str]) -> List[ValidationError]:
        """
        Valida que los campos requeridos estén presentes y no vacíos.

        Args:
            data: Datos a validar
            fields: Campos requeridos

        Returns:
            Lista de errores de validación
        """
        errors = []
        for field in fields:
            if field not in data or not data[field]:
                errors.append(ValidationError(
                    field=field,
                    message=f"El campo '{field}' es requerido",
                    code="REQUIRED_FIELD"
                ))
        return errors

    def validate_length(self, value: str, min_length: int = 0,
                       max_length: int = None, field_name: str = "campo") -> List[ValidationError]:
        """
        Valida la longitud de un string.

        Args:
            value: Valor a validar
            min_length: Longitud mínima
            max_length: Longitud máxima
            field_name: Nombre del campo para mensajes

        Returns:
            Lista de errores de validación
        """
        errors = []
        if not value:
            return errors

        if len(value) < min_length:
            errors.append(ValidationError(
                field=field_name,
                message=f"El campo '{field_name}' debe tener al menos {min_length} caracteres",
                code="MIN_LENGTH"
            ))

        if max_length and len(value) > max_length:
            errors.append(ValidationError(
                field=field_name,
                message=f"El campo '{field_name}' no puede exceder {max_length} caracteres",
                code="MAX_LENGTH"
            ))

        return errors

    def validate_numeric(self, value: Any, min_value: float = None,
                        max_value: float = None, field_name: str = "campo") -> List[ValidationError]:
        """
        Valida que un valor sea numérico y esté en rango.

        Args:
            value: Valor a validar
            min_value: Valor mínimo
            max_value: Valor máximo
            field_name: Nombre del campo

        Returns:
            Lista de errores de validación
        """
        errors = []

        if not isinstance(value, (int, float)):
            errors.append(ValidationError(
                field=field_name,
                message=f"El campo '{field_name}' debe ser numérico",
                code="INVALID_TYPE"
            ))
            return errors

        if min_value is not None and value < min_value:
            errors.append(ValidationError(
                field=field_name,
                message=f"El campo '{field_name}' debe ser al menos {min_value}",
                code="MIN_VALUE"
            ))

        if max_value is not None and value > max_value:
            errors.append(ValidationError(
                field=field_name,
                message=f"El campo '{field_name}' no puede exceder {max_value}",
                code="MAX_VALUE"
            ))

        return errors

    # ==================== MÉTODOS DE CACHÉ ====================

    def _cache_get(self, key: str) -> Optional[Any]:
        """Obtiene un valor del caché."""
        if self.cache_manager:
            return self.cache_manager.get(key)
        return None

    def _cache_set(self, key: str, value: Any, ttl: int = 3600):
        """Guarda un valor en el caché."""
        if self.cache_manager:
            self.cache_manager.set(key, value, ttl)

    def _cache_delete(self, key: str):
        """Elimina un valor del caché."""
        if self.cache_manager:
            self.cache_manager.delete(key)

    def _cache_invalidate_pattern(self, pattern: str):
        """Invalida todas las keys que coinciden con un patrón."""
        if self.cache_manager:
            self.cache_manager.invalidate_pattern(pattern)

    # ==================== MÉTODOS DE LOGGING ====================

    def _log_operation(self, operation: str, details: Dict[str, Any] = None):
        """
        Registra una operación del servicio.

        Args:
            operation: Tipo de operación
            details: Detalles adicionales
        """
        log_data = {
            'service': self.__class__.__name__,
            'operation': operation,
            'timestamp': datetime.now().isoformat(),
            **(details or {})
        }
        self._logger.info(f"Service operation: {log_data}")

    def _log_error(self, operation: str, error: Exception, details: Dict[str, Any] = None):
        """
        Registra un error del servicio.

        Args:
            operation: Operación que falló
            error: Excepción ocurrida
            details: Detalles adicionales
        """
        log_data = {
            'service': self.__class__.__name__,
            'operation': operation,
            'error': str(error),
            'error_type': type(error).__name__,
            'timestamp': datetime.now().isoformat(),
            **(details or {})
        }
        self._logger.error(f"Service error: {log_data}", exc_info=error)

    # ==================== MÉTODOS DE UTILIDAD ====================

    def create_result(self, success: bool, data: Any = None,
                     error: str = None, **metadata) -> ServiceResult:
        """
        Crea un resultado de servicio estandarizado.

        Args:
            success: Si la operación fue exitosa
            data: Datos del resultado
            error: Mensaje de error (si falló)
            **metadata: Metadatos adicionales

        Returns:
            ServiceResult con la información
        """
        return ServiceResult(
            success=success,
            data=data,
            error=error,
            metadata=metadata if metadata else None
        )

    def execute_safely(self, operation: str, callable_func, *args, **kwargs) -> ServiceResult:
        """
        Ejecuta una función de manera segura con manejo de errores.

        Args:
            operation: Nombre de la operación para logging
            callable_func: Función a ejecutar
            *args: Argumentos posicionales
            **kwargs: Argumentos nominales

        Returns:
            ServiceResult con el resultado
        """
        try:
            result = callable_func(*args, **kwargs)
            return self.create_result(success=True, data=result)
        except Exception as e:
            self._log_error(operation, e)
            return self.create_result(
                success=False,
                error=str(e),
                exception_type=type(e).__name__
            )
