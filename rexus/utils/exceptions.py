"""
Excepciones Personalizadas - Rexus.app
Define excepciones específicas para mejor manejo de errores

Ventajas de usar excepciones específicas:
- Mejor depuración
- Manejo granular de errores
- Mensajes más claros
- Logging categorizado
"""

from typing import Optional, Any


# ==========================================
# Excepciones de Base
# ==========================================

class RexusException(Exception):
    """Base exception para todas las excepciones de Rexus."""

    def __init__(self, message: str, error_code: str = None, details: dict = None):
        """
        Inicializa la excepción.

        Args:
            message: Mensaje de error
            error_code: Código de error único
            details: Detalles adicionales del error
        """
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> dict:
        """Convierte la excepción a diccionario para serialización."""
        return {
            'error_type': self.__class__.__name__,
            'error_code': self.error_code,
            'message': self.message,
            'details': self.details
        }


# ==========================================
# Excepciones de Base de Datos
# ==========================================

class DatabaseException(RexusException):
    """Base para excepciones de base de datos."""
    pass


class DatabaseConnectionError(DatabaseException):
    """Error al conectar a la base de datos."""

    def __init__(self, server: str, database: str, details: dict = None):
        message = f"No se pudo conectar a {server}/{database}"
        super().__init__(message, details=details or {'server': server, 'database': database})


class DatabaseQueryError(DatabaseException):
    """Error en una consulta SQL."""

    def __init__(self, query: str, reason: str, details: dict = None):
        message = f"Error en consulta SQL: {reason}"
        super().__init__(message, details=details or {'query': query[:100], 'reason': reason})


class DatabaseValidationError(DatabaseException):
    """Error de validación de datos de base de datos."""

    def __init__(self, field: str, value: Any, reason: str, details: dict = None):
        message = f"Validación fallida para '{field}': {reason}"
        super().__init__(message, details=details or {'field': field, 'value': str(value)[:50]})


class DatabaseConstraintError(DatabaseException):
    """Violación de restricción de base de datos."""

    def __init__(self, constraint: str, table: str, details: dict = None):
        message = f"Violación de restricción '{constraint}' en tabla '{table}'"
        super().__init__(message, details=details or {'constraint': constraint, 'table': table})


class DatabaseTimeoutError(DatabaseException):
    """Timeout en operación de base de datos."""

    def __init__(self, operation: str, timeout_seconds: int, details: dict = None):
        message = f"Timeout después de {timeout_seconds}s en: {operation}"
        super().__init__(message, details=details or {'operation': operation, 'timeout': timeout_seconds})


# ==========================================
# Excepciones de Seguridad
# ==========================================

class SecurityException(RexusException):
    """Base para excepciones de seguridad."""
    pass


class AuthenticationError(SecurityException):
    """Error de autenticación."""

    def __init__(self, username: str, reason: str, details: dict = None):
        message = f"Error de autenticación para '{username}': {reason}"
        super().__init__(message, details=details or {'username': username, 'reason': reason})


class AuthorizationError(SecurityException):
    """Error de autorización (permisos)."""

    def __init__(self, user: str, resource: str, action: str, details: dict = None):
        message = f"Usuario '{user}' no tiene permiso para '{action}' en '{resource}'"
        super().__init__(message, details=details or {'user': user, 'resource': resource, 'action': action})


class RateLimitExceededError(SecurityException):
    """Excedido el límite de rate limiting."""

    def __init__(self, resource: str, max_attempts: int, retry_after_seconds: int, details: dict = None):
        message = f"Límite excedido para '{resource}'. Máximo: {max_attempts}. Reintentar en {retry_after_seconds}s"
        super().__init__(message, details=details or {
            'resource': resource,
            'max_attempts': max_attempts,
            'retry_after': retry_after_seconds
        })


class PasswordValidationError(SecurityException):
    """Error de validación de contraseña."""

    def __init__(self, reason: str, details: dict = None):
        message = f"Contraseña no válida: {reason}"
        super().__init__(message, details=details or {'reason': reason})


class SecretNotFoundError(SecurityException):
    """Secret no encontrado en el gestor de secrets."""

    def __init__(self, key: str, details: dict = None):
        message = f"Secret '{key}' no encontrado"
        super().__init__(message, details=details or {'key': key})


class SQLInjectionWarning(SecurityException):
    """Advertencia de posible inyección SQL."""

    def __init__(self, input_value: str, reason: str, details: dict = None):
        message = f"Posible inyección SQL detectada: {reason}"
        super().__init__(message, details=details or {'input': input_value[:50], 'reason': reason})


# ==========================================
# Excepciones de Inventario
# ==========================================

class InventoryException(RexusException):
    """Base para excepciones de inventario."""
    pass


class ProductNotFoundError(InventoryException):
    """Producto no encontrado."""

    def __init__(self, product_id: int = None, code: str = None, details: dict = None):
        if product_id:
            message = f"Producto con ID {product_id} no encontrado"
            details = details or {'product_id': product_id}
        elif code:
            message = f"Producto con código '{code}' no encontrado"
            details = details or {'code': code}
        else:
            message = "Producto no encontrado"
            details = details or {}
        super().__init__(message, details=details)


class InsufficientStockError(InventoryException):
    """Stock insuficiente."""

    def __init__(self, product_id: int, requested: int, available: int, details: dict = None):
        message = f"Stock insuficiente para producto {product_id}. Solicitado: {requested}, Disponible: {available}"
        super().__init__(message, details=details or {
            'product_id': product_id,
            'requested': requested,
            'available': available
        })


class StockOperationError(InventoryException):
    """Error en operación de stock."""

    def __init__(self, operation: str, product_id: int, reason: str, details: dict = None):
        message = f"Error en operación '{operation}' para producto {product_id}: {reason}"
        super().__init__(message, details=details or {'operation': operation, 'product_id': product_id, 'reason': reason})


# ==========================================
# Excepciones de Pedidos
# ==========================================

class OrderException(RexusException):
    """Base para excepciones de pedidos."""
    pass


class OrderNotFoundError(OrderException):
    """Pedido no encontrado."""

    def __init__(self, order_id: int, details: dict = None):
        message = f"Pedido {order_id} no encontrado"
        super().__init__(message, details=details or {'order_id': order_id})


class OrderValidationError(OrderException):
    """Error de validación de pedido."""

    def __init__(self, field: str, value: Any, reason: str, details: dict = None):
        message = f"Validación de pedido fallida para '{field}': {reason}"
        super().__init__(message, details=details or {'field': field, 'value': str(value)[:50], 'reason': reason})


class OrderStatusTransitionError(OrderException):
    """Transición de estado inválida."""

    def __init__(self, order_id: int, current_status: str, new_status: str, details: dict = None):
        message = f"Transición inválida para pedido {order_id}: {current_status} -> {new_status}"
        super().__init__(message, details=details or {
            'order_id': order_id,
            'current_status': current_status,
            'new_status': new_status
        })


# ==========================================
# Excepciones de Configuración
# ==========================================

class ConfigurationException(RexusException):
    """Base para excepciones de configuración."""
    pass


class MissingConfigurationError(ConfigurationException):
    """Falta una configuración requerida."""

    def __init__(self, config_key: str, details: dict = None):
        message = f"Configuración requerida faltante: '{config_key}'"
        super().__init__(message, details=details or {'config_key': config_key})


class InvalidConfigurationError(ConfigurationException):
    """Valor de configuración inválido."""

    def __init__(self, config_key: str, value: Any, reason: str, details: dict = None):
        message = f"Valor inválido para '{config_key}': {reason}"
        super().__init__(message, details=details or {'config_key': config_key, 'value': str(value)[:50], 'reason': reason})


# ==========================================
# Excepciones de Archivos
# ==========================================

class FileException(RexusException):
    """Base para excepciones de archivos."""
    pass


class FileNotFoundError(FileException):
    """Archivo no encontrado."""

    def __init__(self, file_path: str, details: dict = None):
        message = f"Archivo no encontrado: '{file_path}'"
        super().__init__(message, details=details or {'file_path': file_path})


class FilePermissionError(FileException):
    """Sin permisos para acceder al archivo."""

    def __init__(self, file_path: str, operation: str, details: dict = None):
        message = f"Sin permisos para '{operation}' en archivo: '{file_path}'"
        super().__init__(message, details=details or {'file_path': file_path, 'operation': operation})


class FileCorruptionError(FileException):
    """Archivo corrupto o inválido."""

    def __init__(self, file_path: str, reason: str, details: dict = None):
        message = f"Archivo corrupto '{file_path}': {reason}"
        super().__init__(message, details=details or {'file_path': file_path, 'reason': reason})


# ==========================================
# Excepciones de API
# ==========================================

class APIException(RexusException):
    """Base para excepciones de API."""
    pass


class APIConnectionError(APIException):
    """Error de conexión a API."""

    def __init__(self, endpoint: str, reason: str, details: dict = None):
        message = f"Error conectando a API endpoint '{endpoint}': {reason}"
        super().__init__(message, details=details or {'endpoint': endpoint, 'reason': reason})


class APIResponseError(APIException):
    """Respuesta de API inválida."""

    def __init__(self, endpoint: str, status_code: int, reason: str, details: dict = None):
        message = f"Error en respuesta de API '{endpoint}' ({status_code}): {reason}"
        super().__init__(message, details=details or {'endpoint': endpoint, 'status_code': status_code, 'reason': reason})


class APITimeoutError(APIException):
    """Timeout en llamada a API."""

    def __init__(self, endpoint: str, timeout_seconds: int, details: dict = None):
        message = f"Timeout en API endpoint '{endpoint}' después de {timeout_seconds}s"
        super().__init__(message, details=details or {'endpoint': endpoint, 'timeout': timeout_seconds})


# ==========================================
# Excepciones de Backups
# ==========================================

class BackupException(RexusException):
    """Base para excepciones de backup."""
    pass


class BackupCreationError(BackupException):
    """Error al crear backup."""

    def __init__(self, database: str, reason: str, details: dict = None):
        message = f"Error creando backup de '{database}': {reason}"
        super().__init__(message, details=details or {'database': database, 'reason': reason})


class BackupRestoreError(BackupException):
    """Error al restaurar backup."""

    def __init__(self, backup_file: str, reason: str, details: dict = None):
        message = f"Error restaurando backup desde '{backup_file}': {reason}"
        super().__init__(message, details=details or {'backup_file': backup_file, 'reason': reason})


class BackupNotFoundError(BackupException):
    """Backup no encontrado."""

    def __init__(self, backup_file: str, details: dict = None):
        message = f"Backup no encontrado: '{backup_file}'"
        super().__init__(message, details=details or {'backup_file': backup_file})


# ==========================================
# Utilidades para manejo de excepciones
# ==========================================

def handle_exception(exception: Exception, context: str = None, raise_original: bool = False) -> dict:
    """
    Maneja una excepción y retorna un diccionario estructurado.

    Args:
        exception: La excepción a manejar
        context: Contexto donde ocurrió el error
        raise_original: Si re-lanzar la excepción original

    Returns:
        Diccionario con información del error

    Example:
        try:
            risky_operation()
        except Exception as e:
            error = handle_exception(e, context="processing_order")
            return {'success': False, 'error': error}
    """
    error_info = {
        'success': False,
        'context': context,
        'error_type': type(exception).__name__,
        'error_message': str(exception)
    }

    if isinstance(exception, RexusException):
        error_info.update(exception.to_dict())
    else:
        error_info['error_code'] = type(exception).__name__

    if raise_original:
        raise exception

    return error_info


def log_exception(logger, exception: Exception, context: str = None, level: str = "ERROR"):
    """
    Loguea una excepción con contexto.

    Args:
        logger: Logger a usar
        exception: La excepción a loguear
        context: Contexto donde ocurrió
        level: Nivel de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    log_func = getattr(logger, level.lower(), logger.error)

    if isinstance(exception, RexusException):
        log_func(
            f"[{exception.error_code}] {context or 'Error'}: {exception.message}",
            extra=exception.details
        )
    else:
        log_func(
            f"[{type(exception).__name__}] {context or 'Error'}: {str(exception)}",
            exc_info=True
        )
