"""
Sistema de Mensajes de Error Contextualizados - Rexus.app
Proporciona mensajes de error específicos con sugerencias de solución
"""

from datetime import datetime
from enum import Enum
from typing import Dict, Optional


class ErrorCategory(Enum):
    """Categorías de errores para mejor organización."""

    DATABASE = "database"
    VALIDATION = "validation"
    AUTHENTICATION = "authentication"
    PERMISSION = "permission"
    NETWORK = "network"
    FILE_SYSTEM = "file_system"
    BUSINESS_LOGIC = "business_logic"
    USER_INPUT = "user_input"


class ErrorSeverity(Enum):
    """Niveles de severidad de errores."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ErrorCode(Enum):
    """Códigos de error específicos con prefijos por categoría."""

    # Database Errors (DB_xxx)
    DB_CONNECTION_FAILED = "DB_001"
    DB_QUERY_FAILED = "DB_002"
    DB_CONSTRAINT_VIOLATION = "DB_003"
    DB_DUPLICATE_KEY = "DB_004"
    DB_RECORD_NOT_FOUND = "DB_005"

    # Validation Errors (VAL_xxx)
    VAL_REQUIRED_FIELD = "VAL_001"
    VAL_INVALID_FORMAT = "VAL_002"
    VAL_OUT_OF_RANGE = "VAL_003"
    VAL_INVALID_LENGTH = "VAL_004"
    VAL_INVALID_TYPE = "VAL_005"

    # Authentication Errors (AUTH_xxx)
    AUTH_INVALID_CREDENTIALS = "AUTH_001"
    AUTH_USER_BLOCKED = "AUTH_002"
    AUTH_SESSION_EXPIRED = "AUTH_003"
    AUTH_TOO_MANY_ATTEMPTS = "AUTH_004"
    AUTH_WEAK_PASSWORD = "AUTH_005"  # nosec B105 - This is an error code, not a password

    # Permission Errors (PERM_xxx)
    PERM_ACCESS_DENIED = "PERM_001"
    PERM_INSUFFICIENT_PRIVILEGES = "PERM_002"
    PERM_MODULE_RESTRICTED = "PERM_003"

    # Network Errors (NET_xxx)
    NET_CONNECTION_TIMEOUT = "NET_001"
    NET_SERVER_UNAVAILABLE = "NET_002"
    NET_REQUEST_FAILED = "NET_003"

    # File System Errors (FS_xxx)
    FS_FILE_NOT_FOUND = "FS_001"
    FS_PERMISSION_DENIED = "FS_002"
    FS_DISK_FULL = "FS_003"
    FS_INVALID_PATH = "FS_004"

    # Business Logic Errors (BL_xxx)
    BL_INVALID_OPERATION = "BL_001"
    BL_STATE_CONFLICT = "BL_002"
    BL_RULE_VIOLATION = "BL_003"

    # User Input Errors (UI_xxx)
    UI_INVALID_SELECTION = "UI_001"
    UI_FORM_INCOMPLETE = "UI_002"
    UI_CONFLICTING_DATA = "UI_003"


class ContextualErrorManager:
    """Gestor centralizado de mensajes de error contextualizados."""

    # Diccionario de mensajes predefinidos
    ERROR_MESSAGES = {
        # Database Errors
        ErrorCode.DB_CONNECTION_FAILED: {
            "title": "Error de Conexión a Base de Datos",
            "message": "No se pudo establecer conexión con la base de datos.",
            "suggestion": "Verifique que el servidor de base de datos esté ejecutándose y la configuración de conexión sea correcta.",
            "technical_details": "Revise la cadena de conexión en config/rexus_config.json",
            "severity": ErrorSeverity.CRITICAL,
            "category": ErrorCategory.DATABASE,
        },
        ErrorCode.DB_DUPLICATE_KEY: {
            "title": "Registro Duplicado",
            "message": "Ya existe un registro con los mismos datos únicos.",
            "suggestion": "Verifique que el código, nombre o identificador no estén duplicados.",
            "technical_details": "Error de restricción UNIQUE en base de datos",
            "severity": ErrorSeverity.ERROR,
            "category": ErrorCategory.DATABASE,
        },
        ErrorCode.DB_RECORD_NOT_FOUND: {
            "title": "Registro No Encontrado",
            "message": "El registro solicitado no existe en la base de datos.",
            "suggestion": "Verifique que el ID o código ingresado sea correcto y que el registro no haya sido eliminado.",
            "technical_details": "Query no retornó resultados",
            "severity": ErrorSeverity.WARNING,
            "category": ErrorCategory.DATABASE,
        },
        # Validation Errors
        ErrorCode.VAL_REQUIRED_FIELD: {
            "title": "Campo Requerido",
            "message": "Este campo es obligatorio y no puede estar vacío.",
            "suggestion": "Complete el campo con la información solicitada.",
            "technical_details": "Validación de campo requerido falló",
            "severity": ErrorSeverity.ERROR,
            "category": ErrorCategory.VALIDATION,
        },
        ErrorCode.VAL_INVALID_FORMAT: {
            "title": "Formato Inválido",
            "message": "El formato ingresado no es válido para este campo.",
            "suggestion": "Verifique que el formato coincida con el ejemplo mostrado.",
            "technical_details": "Expresión regular o validación de formato falló",
            "severity": ErrorSeverity.ERROR,
            "category": ErrorCategory.VALIDATION,
        },
        ErrorCode.VAL_INVALID_LENGTH: {
            "title": "Longitud Inválida",
            "message": "El texto ingresado es muy corto o muy largo.",
            "suggestion": "Ajuste la longitud del texto según los límites indicados.",
            "technical_details": "Validación de longitud mín/máx falló",
            "severity": ErrorSeverity.ERROR,
            "category": ErrorCategory.VALIDATION,
        },
        # Authentication Errors
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
            ErrorSeverity.WARNING: "⚠️",
            ErrorSeverity.ERROR: "❌",
            ErrorSeverity.CRITICAL: "🚨",
        }

        icon = severity_icons.get(error_info["severity"], "❌")

        return f"{icon} {error_info['title']}\n\n{error_info['message']}\n\n💡 {error_info['suggestion']}"

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
