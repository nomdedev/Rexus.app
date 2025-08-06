"""
Sistema de Mensajes de Error Contextualizados Mejorado - Rexus.app
Proporciona mensajes de error específicos con sugerencias de solución
"""

from dataclasses import dataclass
from enum import Enum
from typing import Callable, Dict, List, Optional

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class ErrorCategory(Enum):
    """Categorías de errores del sistema."""

    VALIDATION = "validation"
    DATABASE = "database"
    NETWORK = "network"
    SECURITY = "security"
    BUSINESS_LOGIC = "business_logic"
    USER_INPUT = "user_input"
    SYSTEM = "system"
    INTEGRATION = "integration"


class ErrorSeverity(Enum):
    """Niveles de severidad de errores."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ContextualError:
    """Representa un error contextualizado del sistema."""

    code: str
    category: ErrorCategory
    severity: ErrorSeverity
    title: str
    message: str
    details: Optional[str] = None
    suggestions: Optional[List[str]] = None
    help_url: Optional[str] = None
    module: Optional[str] = None
    action_required: bool = False
    auto_retry: bool = False


class ErrorCatalog:
    """Catálogo centralizado de errores del sistema."""

    # Errores de Validación (E1xxx)
    VALIDATION_ERRORS = {
        "E1001": ContextualError(
            code="E1001",
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.ERROR,
            title="Campo obligatorio vacío",
            message="El campo {field_name} es obligatorio y no puede estar vacío.",
            suggestions=[
                "Ingrese un valor válido en el campo {field_name}",
                "Revise que no haya espacios en blanco únicamente",
                "Verifique el formato requerido para este campo",
            ],
            help_url="help/validation/required_fields",
        ),
        "E1002": ContextualError(
            code="E1002",
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.ERROR,
            title="Formato de datos incorrecto",
            message="El formato del campo {field_name} no es válido. Se esperaba: {expected_format}",
            suggestions=[
                "Revise el formato correcto: {expected_format}",
                "Elimine caracteres especiales no permitidos",
                "Use el formato exacto como se muestra en el ejemplo",
            ],
            help_url="help/validation/data_formats",
        ),
        "E1003": ContextualError(
            code="E1003",
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.WARNING,
            title="Valor fuera de rango",
            message="El valor {value} está fuera del rango permitido ({min_value} - {max_value}).",
            suggestions=[
                "Ingrese un valor entre {min_value} y {max_value}",
                "Verifique las unidades de medida utilizadas",
                "Consulte los límites técnicos del sistema",
            ],
        ),
    }

    # Errores de Base de Datos (E2xxx)
    DATABASE_ERRORS = {
        "E2001": ContextualError(
            code="E2001",
            category=ErrorCategory.DATABASE,
            severity=ErrorSeverity.CRITICAL,
            title="Error de conexión a la base de datos",
            message="No se pudo conectar a la base de datos. Verifique la conectividad.",
            suggestions=[
                "Verifique que el servidor de base de datos esté funcionando",
                "Revise la configuración de red",
                "Contacte al administrador del sistema si persiste",
            ],
            action_required=True,
            auto_retry=True,
        ),
        "E2002": ContextualError(
            code="E2002",
            category=ErrorCategory.DATABASE,
            severity=ErrorSeverity.ERROR,
            title="Registro duplicado",
            message="Ya existe un registro con el {field_name}: {value}",
            suggestions=[
                "Use un {field_name} diferente y único",
                "Verifique si desea actualizar el registro existente",
                "Consulte la lista de registros existentes",
            ],
        ),
        "E2003": ContextualError(
            code="E2003",
            category=ErrorCategory.DATABASE,
            severity=ErrorSeverity.ERROR,
            title="Registro no encontrado",
            message="No se encontró el registro solicitado con ID: {record_id}",
            suggestions=[
                "Verifique que el ID sea correcto",
                "Actualice la lista de registros",
                "El registro puede haber sido eliminado por otro usuario",
            ],
        ),
    }

    # Errores de Seguridad (E4xxx)
    SECURITY_ERRORS = {
        "E4001": ContextualError(
            code="E4001",
            category=ErrorCategory.SECURITY,
            severity=ErrorSeverity.CRITICAL,
            title="Acceso denegado",
            message="No tiene permisos para realizar esta acción: {action}",
            suggestions=[
                "Contacte al administrador para obtener permisos",
                "Verifique que su sesión no haya expirado",
                "Inicie sesión con una cuenta con privilegios adecuados",
            ],
            action_required=True,
        ),
        "E4002": ContextualError(
            code="E4002",
            category=ErrorCategory.SECURITY,
            severity=ErrorSeverity.WARNING,
            title="Sesión expirada",
            message="Su sesión ha expirado por inactividad. Debe iniciar sesión nuevamente.",
            suggestions=[
                "Haga clic en 'Iniciar Sesión' para continuar",
                "Guarde su trabajo antes de que expire la sesión",
                "Configure recordatorios para sesiones largas",
            ],
            action_required=True,
        ),
    }

    # Errores de Lógica de Negocio (E7xxx)
    BUSINESS_LOGIC_ERRORS = {
        "E7001": ContextualError(
            code="E7001",
            category=ErrorCategory.BUSINESS_LOGIC,
            severity=ErrorSeverity.ERROR,
            title="Stock insuficiente",
            message="Stock insuficiente para {product_name}. Disponible: {available}, Solicitado: {requested}",
            suggestions=[
                "Reduzca la cantidad solicitada a {available} o menos",
                "Verifique la disponibilidad en otros almacenes",
                "Programe un pedido de reposición",
            ],
        ),
        "E7002": ContextualError(
            code="E7002",
            category=ErrorCategory.BUSINESS_LOGIC,
            severity=ErrorSeverity.WARNING,
            title="Precio fuera de rango normal",
            message="El precio {price} está fuera del rango normal para {product_type} ({min_price} - {max_price})",
            suggestions=[
                "Verifique que el precio sea correcto",
                "Confirme si se trata de un descuento especial",
                "Revise con el supervisor de precios",
            ],
        ),
    }

    @classmethod
    def get_all_errors(cls) -> Dict[str, ContextualError]:
        """Obtiene todos los errores del catálogo."""
        all_errors = {}
        all_errors.update(cls.VALIDATION_ERRORS)
        all_errors.update(cls.DATABASE_ERRORS)
        all_errors.update(cls.SECURITY_ERRORS)
        all_errors.update(cls.BUSINESS_LOGIC_ERRORS)
        return all_errors

    @classmethod
    def get_error(cls, error_code: str) -> Optional[ContextualError]:
        """Obtiene un error específico por su código."""
        return cls.get_all_errors().get(error_code)


class ContextualErrorDialog(QDialog):
    """Diálogo especializado para mostrar errores contextualizados."""

    retry_requested = pyqtSignal()
    help_requested = pyqtSignal(str)

    def __init__(
        self, error: ContextualError, context_data: Optional[Dict] = None, parent=None
    ):
        super().__init__(parent)
        self.error = error
        self.context_data = context_data or {}
        self.setup_ui()
        self.format_content()

    def setup_ui(self):
        """Configura la interfaz del diálogo."""
        self.setWindowTitle(f"Error {self.error.code}: {self.error.title}")
        self.setModal(True)
        self.resize(500, 400)

        layout = QVBoxLayout(self)

        # Header con icono y título
        header_frame = self.create_header()
        layout.addWidget(header_frame)

        # Mensaje principal
        message_label = QLabel()
        message_label.setWordWrap(True)
        message_label.setStyleSheet("font-size: 12px; margin: 10px;")
        self.message_label = message_label
        layout.addWidget(message_label)

        # Sugerencias
        if self.error.suggestions:
            suggestions_frame = self.create_suggestions()
            layout.addWidget(suggestions_frame)

        # Detalles técnicos (expandible)
        if self.error.details:
            details_frame = self.create_details()
            layout.addWidget(details_frame)

        # Botones de acción
        buttons_frame = self.create_buttons()
        layout.addWidget(buttons_frame)

    def create_header(self) -> QFrame:
        """Crea el header con icono y título."""
        frame = QFrame()
        layout = QHBoxLayout(frame)

        # Icono según severidad
        icon_label = QLabel()
        icon_name = self.get_severity_icon()
        # En un entorno real, cargaríamos iconos reales
        icon_label.setText(icon_name)
        icon_label.setStyleSheet("font-size: 24px; margin-right: 10px;")
        layout.addWidget(icon_label)

        # Título y código
        title_layout = QVBoxLayout()
        title_label = QLabel(self.error.title)
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(14)
        title_label.setFont(title_font)

        code_label = QLabel(
            f"Código: {self.error.code} | Categoría: {self.error.category.value}"
        )
        code_label.setStyleSheet("color: #666; font-size: 10px;")

        title_layout.addWidget(title_label)
        title_layout.addWidget(code_label)
        layout.addLayout(title_layout)

        layout.addStretch()

        # Color de fondo según severidad
        frame.setStyleSheet(
            f"background-color: {self.get_severity_color()}; padding: 10px; border-radius: 5px;"
        )

        return frame

    def create_suggestions(self) -> QFrame:
        """Crea el panel de sugerencias."""
        frame = QFrame()
        layout = QVBoxLayout(frame)

        suggestions_label = QLabel("💡 Sugerencias para resolver el problema:")
        suggestions_label.setStyleSheet("font-weight: bold; margin-bottom: 5px;")
        layout.addWidget(suggestions_label)

        for i, suggestion in enumerate(self.error.suggestions or [], 1):
            suggestion_text = self.format_text(suggestion)
            suggestion_label = QLabel(f"{i}. {suggestion_text}")
            suggestion_label.setWordWrap(True)
            suggestion_label.setStyleSheet("margin-left: 15px; margin-bottom: 3px;")
            layout.addWidget(suggestion_label)

        frame.setStyleSheet(
            "background-color: #f9f9f9; padding: 10px; border-radius: 5px; margin: 5px;"
        )
        return frame

    def create_details(self) -> QFrame:
        """Crea el panel de detalles técnicos."""
        frame = QFrame()
        layout = QVBoxLayout(frame)

        details_label = QLabel("🔧 Detalles técnicos:")
        details_label.setStyleSheet("font-weight: bold; margin-bottom: 5px;")
        layout.addWidget(details_label)

        details_text = QTextEdit()
        details_text.setPlainText(self.error.details or "Sin detalles adicionales")
        details_text.setMaximumHeight(80)
        details_text.setReadOnly(True)
        layout.addWidget(details_text)

        frame.setStyleSheet(
            "background-color: #f0f0f0; padding: 10px; border-radius: 5px; margin: 5px;"
        )
        return frame

    def create_buttons(self) -> QFrame:
        """Crea los botones de acción."""
        frame = QFrame()
        layout = QHBoxLayout(frame)

        # Botón de ayuda
        if self.error.help_url:
            help_button = QPushButton("❓ Ayuda")
            help_button.clicked.connect(
                lambda: self.help_requested.emit(self.error.help_url)
            )
            layout.addWidget(help_button)

        # Botón de reintentar
        if self.error.auto_retry:
            retry_button = QPushButton("🔄 Reintentar")
            retry_button.clicked.connect(self.retry_requested.emit)
            layout.addWidget(retry_button)

        layout.addStretch()

        # Botón de cerrar
        close_button = QPushButton("Cerrar")
        close_button.clicked.connect(self.accept)
        close_button.setDefault(True)
        layout.addWidget(close_button)

        return frame

    def get_severity_icon(self) -> str:
        """Obtiene el icono según la severidad."""
        icons = {
            ErrorSeverity.INFO: "ℹ️",
            ErrorSeverity.WARNING: "⚠️",
            ErrorSeverity.ERROR: "❌",
            ErrorSeverity.CRITICAL: "🚨",
        }
        return icons.get(self.error.severity, "❓")

    def get_severity_color(self) -> str:
        """Obtiene el color de fondo según la severidad."""
        colors = {
            ErrorSeverity.INFO: "#e3f2fd",
            ErrorSeverity.WARNING: "#fff3e0",
            ErrorSeverity.ERROR: "#ffebee",
            ErrorSeverity.CRITICAL: "#fce4ec",
        }
        return colors.get(self.error.severity, "#f5f5f5")

    def format_content(self):
        """Formatea el contenido con datos contextuales."""
        formatted_message = self.format_text(self.error.message)
        self.message_label.setText(formatted_message)

    def format_text(self, text: str) -> str:
        """Formatea texto con datos contextuales."""
        if not self.context_data:
            return text

        try:
            return text.format(**self.context_data)
        except (KeyError, ValueError):
            return text


class ContextualErrorManager(QObject):
    """Gestor principal para errores contextualizados."""

    error_occurred = pyqtSignal(str, str)  # error_code, module

    def __init__(self):
        super().__init__()
        self.error_history: List[Dict] = []
        self.error_handlers: Dict[str, Callable] = {}

    def show_error(
        self,
        error_code: str,
        context_data: Optional[Dict] = None,
        parent: Optional[QWidget] = None,
        module: Optional[str] = None,
    ) -> Optional[ContextualErrorDialog]:
        """Muestra un error contextualizado."""
        error = ErrorCatalog.get_error(error_code)

        if not error:
            # Error no encontrado, mostrar genérico
            self.show_generic_error(f"Error desconocido: {error_code}", parent)
            return None

        # Registrar en historial
        self.error_history.append(
            {
                "timestamp": "now",  # En producción usar datetime
                "code": error_code,
                "module": module,
                "context": context_data,
            }
        )

        # Emitir señal
        self.error_occurred.emit(error_code, module or "unknown")

        # Crear y mostrar diálogo
        dialog = ContextualErrorDialog(error, context_data, parent)

        # Conectar manejadores
        if error.auto_retry:
            dialog.retry_requested.connect(
                lambda: self.handle_retry(error_code, module)
            )

        if error.help_url:
            dialog.help_requested.connect(self.show_help)

        dialog.exec()
        return dialog

    def show_generic_error(self, message: str, parent: Optional[QWidget] = None):
        """Muestra un error genérico cuando no hay error contextualizado."""
        msg_box = QMessageBox(parent)
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle("Error del Sistema")
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()

    def register_error_handler(self, error_code: str, handler: Callable):
        """Registra un manejador personalizado para un tipo de error."""
        self.error_handlers[error_code] = handler

    def handle_retry(self, error_code: str, module: Optional[str] = None):
        """Maneja la acción de reintentar."""
        if error_code in self.error_handlers:
            self.error_handlers[error_code]()
        else:
            print(f"Reintentando operación para error {error_code} en módulo {module}")

    def show_help(self, help_url: str):
        """Muestra ayuda para un error."""
        print(f"Abriendo ayuda: {help_url}")
        # En producción abriría URL o ventana de ayuda

    def get_error_statistics(self) -> Dict:
        """Obtiene estadísticas de errores."""
        total_errors = len(self.error_history)
        categories = {}
        modules = {}

        for error_record in self.error_history:
            code = error_record["code"]
            module = error_record.get("module", "unknown")

            error = ErrorCatalog.get_error(code)
            if error:
                category = error.category.value
                categories[category] = categories.get(category, 0) + 1

            modules[module] = modules.get(module, 0) + 1

        return {
            "total_errors": total_errors,
            "by_category": categories,
            "by_module": modules,
        }


# Instancia global del gestor
contextual_error_manager = ContextualErrorManager()


# Funciones de conveniencia
def show_validation_error(
    field_name: str, expected_format: str = "", parent: Optional[QWidget] = None
):
    """Muestra un error de validación contextualizado."""
    context = {"field_name": field_name, "expected_format": expected_format}
    if expected_format:
        contextual_error_manager.show_error("E1002", context, parent)
    else:
        contextual_error_manager.show_error("E1001", context, parent)


def show_database_error(
    error_type: str = "connection",
    context: Optional[Dict] = None,
    parent: Optional[QWidget] = None,
):
    """Muestra un error de base de datos contextualizado."""
    error_codes = {"connection": "E2001", "duplicate": "E2002", "not_found": "E2003"}
    code = error_codes.get(error_type, "E2001")
    contextual_error_manager.show_error(code, context, parent)


def show_security_error(
    error_type: str = "access_denied",
    context: Optional[Dict] = None,
    parent: Optional[QWidget] = None,
):
    """Muestra un error de seguridad contextualizado."""
    error_codes = {"access_denied": "E4001", "session_expired": "E4002"}
    code = error_codes.get(error_type, "E4001")
    contextual_error_manager.show_error(code, context, parent)


def show_business_error(
    error_type: str = "stock",
    context: Optional[Dict] = None,
    parent: Optional[QWidget] = None,
):
    """Muestra un error de lógica de negocio contextualizado."""
    error_codes = {"stock": "E7001", "price": "E7002"}
    code = error_codes.get(error_type, "E7001")
    contextual_error_manager.show_error(code, context, parent)
