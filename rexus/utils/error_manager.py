"""
Sistema de Mensajes de Error Contextualizados - Rexus.app
Reemplaza mensajes genéricos por específicos con sugerencias de solución
"""

import logging
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class ErrorType(Enum):
    """Tipos de errores disponibles."""
    VALIDATION = "validation"
    SECURITY = "security"
    BUSINESS_RULE = "business_rule"
    SYSTEM = "system"
    NETWORK = "network"
    DATABASE = "database"


class ErrorSeverity(Enum):
    """Niveles de severidad de errores."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ErrorCode:
    """Códigos de error estandarizados."""
    # Errores de validación
    VALIDATION_REQUIRED_FIELD = "VALIDATION_REQUIRED_FIELD"
    VALIDATION_INVALID_FORMAT = "VALIDATION_INVALID_FORMAT"
    VALIDATION_INVALID_VALUE = "VALIDATION_INVALID_VALUE"

    # Errores de seguridad
    SECURITY_UNAUTHORIZED = "SECURITY_UNAUTHORIZED"
    SECURITY_FORBIDDEN = "SECURITY_FORBIDDEN"
    SECURITY_INVALID_CREDENTIALS = "SECURITY_INVALID_CREDENTIALS"

    # Errores de reglas de negocio
    BUSINESS_INSUFFICIENT_STOCK = "BUSINESS_INSUFFICIENT_STOCK"
    BUSINESS_INVALID_OPERATION = "BUSINESS_INVALID_OPERATION"

    # Errores de sistema
    SYSTEM_UNEXPECTED_ERROR = "SYSTEM_UNEXPECTED_ERROR"
    SYSTEM_SERVICE_UNAVAILABLE = "SYSTEM_SERVICE_UNAVAILABLE"

    # Errores de red
    NETWORK_CONNECTION_ERROR = "NETWORK_CONNECTION_ERROR"
    NETWORK_TIMEOUT = "NETWORK_TIMEOUT"

    # Errores de base de datos
    DATABASE_CONNECTION_ERROR = "DATABASE_CONNECTION_ERROR"
    DATABASE_QUERY_ERROR = "DATABASE_QUERY_ERROR"
    DATABASE_CONNECTION_FAILED = "DATABASE_CONNECTION_FAILED"


@dataclass
class ErrorMessage:
    """Mensaje de error contextualizado."""
    code: str
    title: str
    message: str
    suggestion: str
    error_type: ErrorType
    severity: ErrorSeverity
    technical_details: Optional[str] = None
    help_url: Optional[str] = None
    context_data: Optional[Dict[str, Any]] = None


class ErrorCatalog:
    """Catálogo de mensajes de error predefinidos."""

    def __init__(self):
        self.errors: Dict[str, ErrorMessage] = {}
        self._initialize_errors()

    def _initialize_errors(self):
        """Inicializa el catálogo de errores."""
        # Errores de validación
        self.errors[ErrorCode.VALIDATION_REQUIRED_FIELD] = ErrorMessage(
            code=ErrorCode.VALIDATION_REQUIRED_FIELD,
            title="Campo Requerido",
            message="Este campo es obligatorio y no puede estar vacío.",
            suggestion="Complete este campo con la información requerida.",
            error_type=ErrorType.VALIDATION,
            severity=ErrorSeverity.WARNING,
        )

        self.errors[ErrorCode.VALIDATION_INVALID_FORMAT] = ErrorMessage(
            code=ErrorCode.VALIDATION_INVALID_FORMAT,
            title="Formato Inválido",
            message="El formato de los datos ingresados no es válido.",
            suggestion="Verifique el formato requerido y corrija los datos.",
            error_type=ErrorType.VALIDATION,
            severity=ErrorSeverity.WARNING,
        )

        # Errores de seguridad
        self.errors[ErrorCode.SECURITY_UNAUTHORIZED] = ErrorMessage(
            code=ErrorCode.SECURITY_UNAUTHORIZED,
            title="Acceso No Autorizado",
            message="No tiene permisos para realizar esta acción.",
            suggestion="Contacte a su administrador para solicitar los permisos necesarios.",
            error_type=ErrorType.SECURITY,
            severity=ErrorSeverity.ERROR,
        )

        self.errors[ErrorCode.SECURITY_INVALID_CREDENTIALS] = ErrorMessage(
            code=ErrorCode.SECURITY_INVALID_CREDENTIALS,
            title="Credenciales Inválidas",
            message="Las credenciales proporcionadas son incorrectas.",
            suggestion="Verifique su usuario y contraseña.",
            error_type=ErrorType.SECURITY,
            severity=ErrorSeverity.WARNING,
        )

        # Errores de reglas de negocio
        self.errors[ErrorCode.BUSINESS_INSUFFICIENT_STOCK] = ErrorMessage(
            code=ErrorCode.BUSINESS_INSUFFICIENT_STOCK,
            title="Stock Insuficiente",
            message="No hay suficiente inventario para completar esta operación.",
            suggestion="Verifique la cantidad disponible o realice un pedido de reposición.",
            error_type=ErrorType.BUSINESS_RULE,
            severity=ErrorSeverity.WARNING,
        )

        # Errores de sistema
        self.errors[ErrorCode.SYSTEM_UNEXPECTED_ERROR] = ErrorMessage(
            code=ErrorCode.SYSTEM_UNEXPECTED_ERROR,
            title="Error Inesperado",
            message="Ha ocurrido un error inesperado en el sistema.",
            suggestion="Intente nuevamente. Si el problema persiste, contacte al soporte técnico.",
            error_type=ErrorType.SYSTEM,
            severity=ErrorSeverity.CRITICAL,
            technical_details="Revise los logs del sistema para más detalles",
        )

        self.errors[ErrorCode.SYSTEM_SERVICE_UNAVAILABLE] = ErrorMessage(
            code=ErrorCode.SYSTEM_SERVICE_UNAVAILABLE,
            title="Servicio No Disponible",
            message="El servicio solicitado no está disponible temporalmente.",
            suggestion="Intente nuevamente en unos minutos.",
            error_type=ErrorType.SYSTEM,
            severity=ErrorSeverity.ERROR,
        )

        # Errores de red
        self.errors[ErrorCode.NETWORK_CONNECTION_ERROR] = ErrorMessage(
            code=ErrorCode.NETWORK_CONNECTION_ERROR,
            title="Error de Conexión",
            message="No se pudo establecer conexión con el servidor.",
            suggestion="Verifique su conexión a internet e intente nuevamente.",
            error_type=ErrorType.NETWORK,
            severity=ErrorSeverity.ERROR,
        )

        # Errores de base de datos
        self.errors[ErrorCode.DATABASE_CONNECTION_ERROR] = ErrorMessage(
            code=ErrorCode.DATABASE_CONNECTION_ERROR,
            title="Error de Base de Datos",
            message="No se pudo conectar a la base de datos.",
            suggestion="Contacte al administrador del sistema.",
            error_type=ErrorType.DATABASE,
            severity=ErrorSeverity.CRITICAL,
        )

        self.errors[ErrorCode.DATABASE_CONNECTION_FAILED] = ErrorMessage(
            code=ErrorCode.DATABASE_CONNECTION_FAILED,
            title="Fallo de Conexión a Base de Datos",
            message="No se pudo establecer conexión con la base de datos.",
            suggestion="Verifique la configuración de conexión y el estado del servidor.",
            error_type=ErrorType.DATABASE,
            severity=ErrorSeverity.CRITICAL,
        )

    def get_error(self, code: str) -> Optional[ErrorMessage]:
        """Obtiene un mensaje de error por código."""
        return self.errors.get(code)

    def get_errors_by_type(self, error_type: ErrorType) -> List[ErrorMessage]:
        """Obtiene todos los errores de un tipo específico."""
        return [
            error for error in self.errors.values() if error.error_type == error_type
        ]

    def get_errors_by_severity(self, severity: ErrorSeverity) -> List[ErrorMessage]:
        """Obtiene todos los errores de una severidad específica."""
        return [
            error for error in self.errors.values() if error.severity == severity
        ]


class ErrorManager:
    """Gestor principal de errores contextualizados."""

    def __init__(self):
        self.catalog = ErrorCatalog()
        self.error_history: List[Dict[str, Any]] = []

    def show_error(
        self,
        parent: Optional[Any],
        error_code: str,
        context_data: Optional[Dict] = None,
        custom_message: str = "",
    ) -> Any:
        """
        Muestra un mensaje de error contextualizado.

        Args:
            parent: Widget padre para el diálogo
            error_code: Código del error del catálogo
            context_data: Datos adicionales para personalizar el mensaje
            custom_message: Mensaje personalizado adicional

        Returns:
            Resultado del diálogo
        """
        error = self.catalog.get_error(error_code)

        if not error:
            # Error no catalogado - usar mensaje genérico
            return self._show_generic_error(parent, error_code, custom_message)

        # Personalizar mensaje con datos del contexto
        message = self._customize_message(error, context_data, custom_message)

        # Registrar en historial
        self.error_history.append({
            'timestamp': __import__('datetime').datetime.now(),
            'code': error.code,
            'severity': error.severity.value,
            'context': context_data,
        })

        # Log del error
        log_message = f"Error {error.code}: {error.message}"
        if error.technical_details:
            log_message += f" - Detalles: {error.technical_details}"

        if error.severity == ErrorSeverity.CRITICAL:
            logger.critical(log_message)
        elif error.severity == ErrorSeverity.ERROR:
            logger.error(log_message)
        elif error.severity == ErrorSeverity.WARNING:
            logger.warning(log_message)
        else:
            logger.info(log_message)

        # Mostrar diálogo si se solicita
        if parent is not None:
            self._show_error_dialog(message, context_data)

        return message

    def show_validation_errors(
        self,
        parent: Optional[Any],
        validation_errors: List[Tuple[str, str]],
    ):
        """
        Muestra múltiples errores de validación en un solo diálogo.

        Args:
            parent: Widget padre
            validation_errors: Lista de tuplas (campo, código_error)
        """
        if not validation_errors:
            return

        # Construir mensaje consolidado
        error_messages = []
        for field_name, error_code in validation_errors:
            error = self.catalog.get_error(error_code)
            if error:
                error_messages.append(f"• {field_name}: {error.message}")
            else:
                error_messages.append(f"• {field_name}: Error de validación")

        # Mostrar diálogo
        if parent is not None:
            self._show_validation_dialog(parent, error_messages)

    def _customize_message(
        self, error: ErrorMessage, context_data: Optional[Dict], custom_message: str
    ) -> ErrorMessage:
        """Personaliza el mensaje con datos del contexto."""
        message = error.message
        suggestion = error.suggestion

        if context_data:
            # Reemplazar placeholders en el mensaje
            for key, value in context_data.items():
                placeholder = f"{{{key}}}"
                message = message.replace(placeholder, str(value))
                if suggestion:
                    suggestion = suggestion.replace(placeholder, str(value))

        if custom_message:
            message = f"{message}\n\n{custom_message}"

        # Crear copia personalizada
        return ErrorMessage(
            code=error.code,
            title=error.title,
            message=message,
            suggestion=suggestion,
            error_type=error.error_type,
            severity=error.severity,
            technical_details=error.technical_details,
            help_url=error.help_url,
        )

    def _show_error_dialog(self, error: ErrorMessage, context_data: Optional[Dict]):
        """Muestra un diálogo de error al usuario."""
        try:
            # Importar aquí para evitar dependencias circulares
            from PyQt6.QtWidgets import QMessageBox

            msg_box = QMessageBox()
            msg_box.setWindowTitle(f"Rexus - {error.title}")
            msg_box.setText(error.message)

            # Configurar detalles
            detailed_text = self._build_detailed_text(error, context_data)
            if detailed_text:
                msg_box.setDetailedText(detailed_text)

            # Configurar icono según severidad
            icon = self._get_icon_for_severity(error.severity)
            msg_box.setIcon(icon)

            # Configurar botones según severidad
            buttons = self._get_buttons_for_severity(error.severity)
            msg_box.setStandardButtons(buttons)

            # Mostrar diálogo
            msg_box.exec()

        except ImportError:
            # Fallback si no se puede importar PyQt6
            logger.warning("No se pudo mostrar diálogo de error - PyQt6 no disponible")

    def _show_validation_dialog(self, parent: Any, error_messages: List[str]):
        """Muestra diálogo de errores de validación."""
        try:
            from PyQt6.QtWidgets import QMessageBox

            msg_box = QMessageBox(parent)
            msg_box.setWindowTitle("Rexus - Errores de Validación")
            msg_box.setText("Se encontraron los siguientes errores:")
            msg_box.setDetailedText("\n".join(error_messages))
            msg_box.setIcon(QMessageBox.Icon.Warning)
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)

            msg_box.exec()

        except ImportError:
            logger.warning("No se pudo mostrar diálogo de validación - PyQt6 no disponible")

    def _build_detailed_text(
        self, error: ErrorMessage, context_data: Optional[Dict]
    ) -> str:
        """Construye el texto detallado del error."""
        details = []

        # Sugerencia de solución
        if error.suggestion:
            details.append(f"Sugerencia: {error.suggestion}")

        # Código de error
        details.append(f"Código: {error.code}")

        # Información técnica
        if error.technical_details:
            details.append(f"Detalles técnicos: {error.technical_details}")

        # Datos del contexto
        if context_data:
            context_info = []
            for key, value in context_data.items():
                context_info.append(f"  {key}: {value}")
            if context_info:
                details.append("Información adicional:\n" + "\n".join(context_info))

        # URL de ayuda
        if error.help_url:
            details.append(f"Más información: {error.help_url}")

        return "\n\n".join(details)

    def _show_generic_error(
        self, parent: Optional[Any], error_code: str, custom_message: str
    ):
        """Muestra un error genérico cuando no se encuentra en el catálogo."""
        try:
            from PyQt6.QtWidgets import QMessageBox

            msg_box = QMessageBox(parent)
            msg_box.setWindowTitle("Rexus - Error")
            msg_box.setText(custom_message or "Ha ocurrido un error en el sistema.")
            msg_box.setDetailedText(f"Código de error: {error_code}")
            msg_box.setIcon(QMessageBox.Icon.Critical)
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)

            msg_box.exec()

        except ImportError:
            logger.warning("No se pudo mostrar error genérico - PyQt6 no disponible")

    def _get_icon_for_severity(self, severity: ErrorSeverity):
        """Obtiene el icono apropiado según la severidad."""
        try:
            from PyQt6.QtWidgets import QMessageBox

            severity_icons = {
                ErrorSeverity.INFO: QMessageBox.Icon.Information,
                ErrorSeverity.WARNING: QMessageBox.Icon.Warning,
                ErrorSeverity.ERROR: QMessageBox.Icon.Critical,
                ErrorSeverity.CRITICAL: QMessageBox.Icon.Critical,
            }
            return severity_icons.get(severity, QMessageBox.Icon.Warning)
        except ImportError:
            return None

    def _get_buttons_for_severity(self, severity: ErrorSeverity):
        """Obtiene los botones apropiados según la severidad."""
        try:
            from PyQt6.QtWidgets import QMessageBox

            if severity == ErrorSeverity.CRITICAL:
                return QMessageBox.StandardButton.Ok
            else:
                return QMessageBox.StandardButton.Ok
        except ImportError:
            return None

    def get_recent_errors(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Obtiene los errores más recientes."""
        return self.error_history[-limit:]

    def clear_history(self):
        """Limpia el historial de errores."""
        self.error_history.clear()

    def get_error_stats(self) -> Dict[str, int]:
        """Obtiene estadísticas de errores."""
        stats = {}
        for entry in self.error_history:
            severity = entry['severity']
            stats[severity] = stats.get(severity, 0) + 1
        return stats


# Instancia global del gestor de errores
_error_manager = None


def get_error_manager() -> ErrorManager:
    """Obtiene la instancia global del gestor de errores."""
    global _error_manager
    if _error_manager is None:
        _error_manager = ErrorManager()
    return _error_manager


def show_error(parent: Any, error_code: str, **kwargs) -> ErrorMessage:
    """Función de conveniencia para mostrar errores."""
    manager = get_error_manager()
    return manager.show_error(parent, error_code, **kwargs)


def show_validation_errors(parent: Any, errors: List[Tuple[str, str]]):
    """Función de conveniencia para mostrar errores de validación."""
    manager = get_error_manager()
    return manager.show_validation_errors(parent, errors)


def show_database_error(parent: Any, operation: str = ""):
    """Función específica para errores de base de datos."""
    context = {"operation": operation} if operation else None
    manager = get_error_manager()
    return manager.show_error(
        parent, ErrorCode.DATABASE_CONNECTION_FAILED, context_data=context
    )


def show_permission_error(parent: Any, action: str = ""):
    """Función específica para errores de permisos."""
    context = {"action": action} if action else None
    manager = get_error_manager()
    return manager.show_error(
        parent, ErrorCode.SECURITY_UNAUTHORIZED, context_data=context
    )


def get_error(code: str) -> Optional[ErrorMessage]:
    """Función de conveniencia para obtener errores."""
    manager = get_error_manager()
    return manager.catalog.get_error(code)