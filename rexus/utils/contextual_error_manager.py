"""
Sistema de Mensajes de Error Contextualizados - Rexus.app
Proporciona mensajes de error específicos con sugerencias de solución
"""

import logging
from datetime import datetime
from typing import Dict, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Niveles de severidad para errores."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Categorías de errores."""
    AUTHENTICATION = "authentication"
    PERMISSION = "permission"
    USER_INPUT = "user_input"
    BUSINESS_LOGIC = "business_logic"
    SYSTEM = "system"
    DATABASE = "database"


class ErrorCode(Enum):
    """Códigos de error predefinidos."""
    # Authentication Errors
    AUTH_INVALID_CREDENTIALS = "auth_invalid_credentials"
    AUTH_USER_BLOCKED = "auth_user_blocked"
    AUTH_TOO_MANY_ATTEMPTS = "auth_too_many_attempts"
    AUTH_WEAK_PASSWORD = "auth_weak_password"

    # Permission Errors
    PERM_ACCESS_DENIED = "perm_access_denied"

    # User Input Errors
    UI_INVALID_SELECTION = "ui_invalid_selection"
    UI_FORM_INCOMPLETE = "ui_form_incomplete"


class ContextualErrorManager:
    """Gestor de errores contextualizados para la aplicación Rexus."""

    # Diccionario de mensajes de error predefinidos
    ERROR_MESSAGES = {
        ErrorCode.AUTH_INVALID_CREDENTIALS: {
            "title": "Credenciales Inválidas",
            "message": "Usuario o contraseña incorrectos.",
            "suggestion": "Verifique que el usuario y contraseña sean correctos. Use 'Olvidé mi contraseña' si es necesario.",
            "technical_details": "Autenticación falló en validación de hash",
            "severity": ErrorSeverity.ERROR,
            "category": ErrorCategory.AUTHENTICATION,
        },
        ErrorCode.AUTH_USER_BLOCKED: {
            "title": "Usuario Bloqueado",
            "message": "Su cuenta ha sido bloqueada temporalmente.",
            "suggestion": "Contacte al administrador del sistema para desbloquear su cuenta.",
            "technical_details": "Usuario marcado como bloqueado en base de datos",
            "severity": ErrorSeverity.ERROR,
            "category": ErrorCategory.AUTHENTICATION,
        },
        ErrorCode.AUTH_TOO_MANY_ATTEMPTS: {
            "title": "Demasiados Intentos",
            "message": "Ha excedido el número máximo de intentos de login.",
            "suggestion": "Espere 15 minutos antes de volver a intentar o contacte al administrador.",
            "technical_details": "Límite de intentos fallidos alcanzado",
            "severity": ErrorSeverity.WARNING,
            "category": ErrorCategory.AUTHENTICATION,
        },
        ErrorCode.AUTH_WEAK_PASSWORD: {
            "title": "Contraseña Débil",
            "message": "La contraseña no cumple con los requisitos de seguridad.",
            "suggestion": "Use al menos 8 caracteres con mayúsculas, minúsculas, números y símbolos.",
            "technical_details": "Validación de política de contraseñas falló",
            "severity": ErrorSeverity.ERROR,
            "category": ErrorCategory.AUTHENTICATION,
        },
        # Permission Errors
        ErrorCode.PERM_ACCESS_DENIED: {
            "title": "Acceso Denegado",
            "message": "No tiene permisos para realizar esta acción.",
            "suggestion": "Contacte al administrador para solicitar los permisos necesarios.",
            "technical_details": "Verificación de permisos falló",
            "severity": ErrorSeverity.ERROR,
            "category": ErrorCategory.PERMISSION,
        },
        # User Input Errors
        ErrorCode.UI_INVALID_SELECTION: {
            "title": "Selección Inválida",
            "message": "Debe seleccionar un elemento válido de la lista.",
            "suggestion": "Haga clic en un elemento de la tabla o lista antes de continuar.",
            "technical_details": "No hay elemento seleccionado o selección inválida",
            "severity": ErrorSeverity.WARNING,
            "category": ErrorCategory.USER_INPUT,
        },
        ErrorCode.UI_FORM_INCOMPLETE: {
            "title": "Formulario Incompleto",
            "message": "Faltan campos obligatorios por completar.",
            "suggestion": "Revise todos los campos marcados con (*) y complete la información faltante.",
            "technical_details": "Validación de formulario completo falló",
            "severity": ErrorSeverity.ERROR,
            "category": ErrorCategory.USER_INPUT,
        },
    }

    @classmethod
    def get_error_info(
        cls, error_code: ErrorCode, context: Optional[Dict] = None
    ) -> Dict:
        """
        Obtiene información completa del error con contexto adicional.

        Args:
            error_code: Código del error
            context: Información adicional específica del contexto

        Returns:
            Diccionario con información completa del error
        """
        base_info = cls.ERROR_MESSAGES.get(
            error_code,
            {
                "title": "Error Desconocido",
                "message": "Ha ocurrido un error no identificado.",
                "suggestion": "Contacte al soporte técnico con el código de error.",
                "technical_details": f"Código de error: {error_code.value}",
                "severity": ErrorSeverity.ERROR,
                "category": ErrorCategory.BUSINESS_LOGIC,
            },
        )

        # Agregar información de contexto
        error_info = base_info.copy()
        error_info.update(
            {
                "error_code": error_code.value,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "context": context or {},
            }
        )

        # Personalizar mensaje con contexto si está disponible
        if context:
            error_info["message"] = cls._personalize_message(
                error_info["message"], error_info["suggestion"], context
            )

        return error_info

    @classmethod
    def _personalize_message(cls, message: str, suggestion: str, context: Dict) -> str:
        """Personaliza el mensaje con información del contexto."""

        # Agregar información específica del campo si está disponible
        if "field_name" in context:
            field_name = context["field_name"]
            message = message.replace("Este campo", f"El campo '{field_name}'")
            suggestion = suggestion.replace("el campo", f"el campo '{field_name}'")

        # Agregar límites específicos para validaciones de longitud
        if "min_length" in context and "max_length" in context:
            min_len = context["min_length"]
            max_len = context["max_length"]
            suggestion += f" (Entre {min_len} y {max_len} caracteres)"

        # Agregar valor actual para debugging
        if "current_value" in context and context["current_value"]:
            current = str(context["current_value"])[:50]  # Truncar para seguridad
            suggestion += f" Valor actual: '{current}...'"

        return message

    @classmethod
    def format_user_message(
        cls, error_code: ErrorCode, context: Optional[Dict] = None
    ) -> str:
        """
        Formatea un mensaje amigable para mostrar al usuario.

        Args:
            error_code: Código del error
            context: Contexto adicional

        Returns:
            Mensaje formateado para el usuario
        """
        error_info = cls.get_error_info(error_code, context)

        severity_icons = {
            ErrorSeverity.INFO: "ℹ️",
            ErrorSeverity.WARNING: "[WARN]",
            ErrorSeverity.ERROR: "[ERROR]",
            ErrorSeverity.CRITICAL: "🚨",
        }

        icon = severity_icons.get(error_info["severity"], "[ERROR]")

        return f"{icon} {error_info['title']}\n\n{error_info['message']}\n\n[IDEA] {error_info['suggestion']}"

    @classmethod
    def format_technical_message(
        cls, error_code: ErrorCode, context: Optional[Dict] = None
    ) -> str:
        """
        Formatea un mensaje técnico para logs o debugging.

        Args:
            error_code: Código del error
            context: Contexto adicional

        Returns:
            Mensaje técnico completo
        """
        error_info = cls.get_error_info(error_code, context)

        return (
            f"[{error_info['timestamp']}] ERROR {error_info['error_code']}: "
            f"{error_info['title']} - {error_info['technical_details']}"
        )


# Instancia global para usar en toda la aplicación
error_manager = ContextualErrorManager()

# Funciones de conveniencia para uso rápido
def show_user_error(error_code: ErrorCode, context: Optional[Dict] = None) -> str:
    """Función rápida para obtener mensaje de usuario."""
    return error_manager.format_user_message(error_code, context)


def log_technical_error(error_code: ErrorCode, context: Optional[Dict] = None) -> str:
    """Función rápida para obtener mensaje técnico."""
    return error_manager.format_technical_message(error_code, context)


def get_error_details(error_code: ErrorCode, context: Optional[Dict] = None) -> Dict:
    """Función rápida para obtener detalles completos del error."""
    return error_manager.get_error_info(error_code, context)
