"""
Sistema de Mensajes de Error Contextualizados - Rexus.app
Reemplaza mensajes genéricos por específicos con sugerencias de solución
"""


import logging
logger = logging.getLogger(__name__)

                        error_type=ErrorType.SECURITY,
            severity=ErrorSeverity.WARNING,
        )

        # Errores de Reglas de Negocio
        self.errors[ErrorCode.BUSINESS_INSUFFICIENT_STOCK] = ErrorMessage(
            code=ErrorCode.BUSINESS_INSUFFICIENT_STOCK,
            title="Stock Insuficiente",
            message="No hay suficiente inventario para completar esta operación.",
            suggestion="Verifique la cantidad disponible o realice un pedido de reposición.",
            error_type=ErrorType.BUSINESS_RULE,
            severity=ErrorSeverity.WARNING,
        )

        # Errores de Sistema
        self.errors[ErrorCode.SYSTEM_UNEXPECTED_ERROR] = ErrorMessage(
            code=ErrorCode.SYSTEM_UNEXPECTED_ERROR,
            title="Error Inesperado",
            message="Ha ocurrido un error inesperado en el sistema.",
            suggestion="Intente nuevamente. Si el problema persiste, contacte al soporte técnico.",
            error_type=ErrorType.SYSTEM,
            severity=ErrorSeverity.CRITICAL,
            technical_details="Revise los logs del sistema para más detalles",
        )

    def get_error(self, code: str) -> Optional[ErrorMessage]:
        """Obtiene un mensaje de error por código."""
        return self.errors.get(code)

    def get_errors_by_type(self, error_type: ErrorType) -> List[ErrorMessage]:
        """Obtiene todos los errores de un tipo específico."""
        return [
            error for error in self.errors.values() if error.error_type == error_type
        ]


class ErrorManager:
    """Gestor principal de errores contextualizados."""

    def __init__(self):
        self.catalog = ErrorCatalog()

    def show_error(
        self,
        parent: QWidget,
        error_code: str,
        context_data: Optional[Dict] = None,
        custom_message: str = "",
    ) -> QMessageBox.StandardButton:
        """
        Muestra un mensaje de error contextualizado.

        Args:
            parent: Widget padre para el diálogo
            error_code: Código del error del catálogo
            context_data: Datos adicionales para personalizar el mensaje
            custom_message: Mensaje personalizado adicional

        Returns:
            Botón presionado por el usuario
        """
        error = self.catalog.get_error(error_code)

        if not error:
            # Error no catalogado - usar mensaje genérico
            return self._show_generic_error(parent, error_code, custom_message)

        # Personalizar mensaje con datos del contexto
        message = self._customize_message(error, context_data, custom_message)

        # Crear y configurar el mensaje
        msg_box = QMessageBox(parent)
        msg_box.setWindowTitle(f"Rexus - {error.title}")
        msg_box.setText(message.message)

        # Configurar detalles y sugerencias
        detailed_text = self._build_detailed_text(message, context_data)
        if detailed_text:
            msg_box.setDetailedText(detailed_text)

        # Configurar icono según severidad
        icon = self._get_icon_for_severity(message.severity)
        msg_box.setIcon(icon)

        # Configurar botones según severidad
        buttons = self._get_buttons_for_severity(message.severity)
        msg_box.setStandardButtons(buttons)

        # Mostrar y retornar resultado
        result = msg_box.exec()
        return QMessageBox.StandardButton(result)

    def show_validation_errors(
        self,
        parent: QWidget,
        validation_errors: List[Tuple[str,
str]],
            # [(field_name, error_code), ...]
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

        msg_box = QMessageBox(parent)
        msg_box.setWindowTitle("Rexus - Errores de Validación")
        msg_box.setText("Se encontraron los siguientes errores:")
        msg_box.setDetailedText("\n".join(error_messages))
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)

        msg_box.exec()

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

    def _build_detailed_text(
        self, error: ErrorMessage, context_data: Optional[Dict]
    ) -> str:
        """Construye el texto detallado del error."""
        details = []

        # Sugerencia de solución
        if error.suggestion:
            details.append(f"[IDEA] Sugerencia: {error.suggestion}")

        # Código de error
        details.append(f"[SEARCH] Código: {error.code}")

        # Información técnica
        if error.technical_details:
            details.append(f"[TOOL] Detalles técnicos: {error.technical_details}")

        # Datos del contexto
        if context_data:
            context_info = []
            for key, value in context_data.items():
                context_info.append(f"  {key}: {value}")
            if context_info:
                details.append("📋 Información adicional:\n" + "\n".join(context_info))

        # URL de ayuda
        if error.help_url:
            details.append(f"📖 Más información: {error.help_url}")

        return "\n\n".join(details)

    def _show_generic_error(
        self, parent: QWidget, error_code: str, custom_message: str
    ) -> QMessageBox.StandardButton:
        """Muestra un error genérico cuando no se encuentra en el catálogo."""
        msg_box = QMessageBox(parent)
        msg_box.setWindowTitle("Rexus - Error")
        msg_box.setText(custom_message or "Ha ocurrido un error en el sistema.")
        msg_box.setDetailedText(f"Código de error: {error_code}")
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)

        result = msg_box.exec()
        return QMessageBox.StandardButton(result)

    def _get_icon_for_severity(self, severity: ErrorSeverity) -> QMessageBox.Icon:
        """Obtiene el icono apropiado según la severidad."""
        severity_icons = {
            ErrorSeverity.INFO: QMessageBox.Icon.Information,
            ErrorSeverity.WARNING: QMessageBox.Icon.Warning,
            ErrorSeverity.ERROR: QMessageBox.Icon.Critical,
            ErrorSeverity.CRITICAL: QMessageBox.Icon.Critical,
        }
        return severity_icons.get(severity, QMessageBox.Icon.Warning)

    def _get_buttons_for_severity(
        self, severity: ErrorSeverity
    ) -> QMessageBox.StandardButton:
        """Obtiene los botones apropiados según la severidad."""
        if severity == ErrorSeverity.CRITICAL:
            return QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Help
        else:
            return QMessageBox.StandardButton.Ok


# Instancia global del gestor de errores
error_manager = ErrorManager()


# Funciones de utilidad para uso rápido
def show_error(parent: QWidget, error_code: str, **kwargs):
    """Función de utilidad para mostrar errores rápidamente."""
    return error_manager.show_error(parent, error_code, **kwargs)


def show_validation_errors(parent: QWidget, errors: List[Tuple[str, str]]):
    """Función de utilidad para mostrar errores de validación."""
    return error_manager.show_validation_errors(parent, errors)


def show_database_error(parent: QWidget, operation: str = ""):
    """Función específica para errores de base de datos."""
    context = {"operation": operation} if operation else None
    return error_manager.show_error(
        parent, ErrorCode.DATABASE_CONNECTION_FAILED, context_data=context
    )


def show_permission_error(parent: QWidget, action: str = ""):
    """Función específica para errores de permisos."""
    context = {"action": action} if action else None
    return error_manager.show_error(
        parent, ErrorCode.SECURITY_UNAUTHORIZED, context_data=context
    )