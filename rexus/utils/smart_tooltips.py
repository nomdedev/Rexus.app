"""
Sistema de Tooltips Informativos Globales - Rexus.app
Proporciona tooltips contextuales con información útil para usuarios
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

from PyQt6.QtCore import QPoint, QRect, QTimer
from PyQt6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QToolTip,
    QWidget,
)


class TooltipType(Enum):
    """Tipos de tooltips disponibles."""

    INFO = "info"  # Información general
    FORMAT = "format"  # Formato de datos requerido
    VALIDATION = "validation"  # Reglas de validación
    HELP = "help"  # Ayuda contextual
    SHORTCUT = "shortcut"  # Atajos de teclado
    EXAMPLE = "example"  # Ejemplos de uso
    WARNING = "warning"  # Advertencias
    FEATURE = "feature"  # Descripción de funcionalidad


@dataclass
class TooltipConfig:
    """Configuración para un tooltip específico."""

    text: str
    tooltip_type: TooltipType
    title: Optional[str] = None
    examples: Optional[List[str]] = None
    shortcuts: Optional[List[str]] = None
    delay_ms: int = 500
    duration_ms: int = 5000
    rich_text: bool = True
    position: str = "auto"  # auto, top, bottom, left, right


class SmartTooltip:
    """Tooltip inteligente con formato mejorado."""

    # Catálogo de tooltips por tipo de campo
    FIELD_TOOLTIPS = {
        # Campos de código/identificación
        "codigo": TooltipConfig(
            text="Código único del elemento",
            tooltip_type=TooltipType.FORMAT,
            title="Formato de Código",
            examples=["HRJ001", "VDR-2024-001", "USR123"],
            shortcuts=["Tab", "Enter"],
        ),
        "codigo_herraje": TooltipConfig(
            text="Código alfanumérico único del herraje (3-10 caracteres)",
            tooltip_type=TooltipType.FORMAT,
            title="Código de Herraje",
            examples=["HRJ001", "BIS45", "CER-123"],
            shortcuts=["Ctrl+F para buscar"],
        ),
        "descripcion": TooltipConfig(
            text="Descripción detallada del elemento",
            tooltip_type=TooltipType.INFO,
            title="Descripción",
            examples=["Bisagra ajustable 3 pulgadas", "Vidrio templado 6mm"],
            shortcuts=["Shift+Tab", "Enter"],
        ),
        # Campos numéricos
        "precio": TooltipConfig(
            text="Precio unitario en pesos argentinos (sin IVA)",
            tooltip_type=TooltipType.FORMAT,
            title="Formato de Precio",
            examples=["1250.50", "15.00", "0.75"],
            shortcuts=["Tab", "Ctrl+C copiar"],
        ),
        "stock": TooltipConfig(
            text="Cantidad disponible en el inventario",
            tooltip_type=TooltipType.VALIDATION,
            title="Control de Stock",
            examples=["100", "25", "0 (sin stock)"],
            shortcuts=["Ctrl+U actualizar stock"],
        ),
        "cantidad": TooltipConfig(
            text="Cantidad solicitada (debe ser mayor a 0)",
            tooltip_type=TooltipType.VALIDATION,
            title="Cantidad",
            examples=["1", "25", "100"],
            shortcuts=["+ / - para incrementar/decrementar"],
        ),
        # Campos de fecha
        "fecha": TooltipConfig(
            text="Fecha en formato DD/MM/AAAA",
            tooltip_type=TooltipType.FORMAT,
            title="Formato de Fecha",
            examples=["06/08/2025", "15/12/2024", "01/01/2025"],
            shortcuts=["F4 seleccionar fecha", "Hoy para fecha actual"],
        ),
        # Campos de usuario
        "usuario": TooltipConfig(
            text="Nombre de usuario alfanumérico (4-20 caracteres)",
            tooltip_type=TooltipType.FORMAT,
            title="Formato de Usuario",
            examples=["admin", "usuario123", "operador_01"],
            shortcuts=["Ctrl+L ver lista de usuarios"],
        ),
        "email": TooltipConfig(
            text="Dirección de correo electrónico válida",
            tooltip_type=TooltipType.FORMAT,
            title="Formato de Email",
            examples=["usuario@empresa.com", "admin@rexus.com"],
            shortcuts=["@ para autocompletar dominio"],
        ),
        # Campos específicos de módulos
        "tipo_herraje": TooltipConfig(
            text="Categoría del herraje según clasificación interna",
            tooltip_type=TooltipType.INFO,
            title="Tipos de Herraje",
            examples=["Bisagra", "Cerradura", "Manija", "Soporte"],
            shortcuts=["Ctrl+T filtrar por tipo"],
        ),
        "tipo_vidrio": TooltipConfig(
            text="Clasificación del vidrio según grosor y tratamiento",
            tooltip_type=TooltipType.INFO,
            title="Tipos de Vidrio",
            examples=["Templado 6mm", "Laminado 8mm", "Crudo 4mm"],
            shortcuts=["Ctrl+V ver catálogo completo"],
        ),
        "estado_obra": TooltipConfig(
            text="Estado actual de la obra en el flujo de trabajo",
            tooltip_type=TooltipType.INFO,
            title="Estados de Obra",
            examples=["Planificación", "En Proceso", "Finalizada", "Cancelada"],
            shortcuts=["Ctrl+E cambiar estado"],
        ),
        # Campos de búsqueda
        "busqueda": TooltipConfig(
            text="Buscar por código, descripción o cualquier campo visible",
            tooltip_type=TooltipType.HELP,
            title="Búsqueda Inteligente",
            examples=["HRJ", "bisagra", "precio:100-500"],
            shortcuts=["Ctrl+F enfocar", "Escape limpiar", "Enter buscar"],
        ),
        # Botones y acciones
        "btn_nuevo": TooltipConfig(
            text="Crear un nuevo registro",
            tooltip_type=TooltipType.SHORTCUT,
            title="Nuevo Registro",
            shortcuts=["Ctrl+N", "Insert"],
        ),
        "btn_editar": TooltipConfig(
            text="Editar el registro seleccionado",
            tooltip_type=TooltipType.SHORTCUT,
            title="Editar Registro",
            shortcuts=["Ctrl+E", "F2", "Doble clic"],
        ),
        "btn_eliminar": TooltipConfig(
            text="Eliminar el registro seleccionado (requiere confirmación)",
            tooltip_type=TooltipType.WARNING,
            title="Eliminar Registro",
            shortcuts=["Delete", "Ctrl+D"],
        ),
        "btn_guardar": TooltipConfig(
            text="Guardar los cambios realizados",
            tooltip_type=TooltipType.SHORTCUT,
            title="Guardar Cambios",
            shortcuts=["Ctrl+S", "Enter"],
        ),
        "btn_cancelar": TooltipConfig(
            text="Cancelar la operación actual y descartar cambios",
            tooltip_type=TooltipType.SHORTCUT,
            title="Cancelar Operación",
            shortcuts=["Escape", "Ctrl+Z"],
        ),
        # Filtros y combinaciones
        "filtro_tipo": TooltipConfig(
            text="Filtrar registros por tipo o categoría",
            tooltip_type=TooltipType.FEATURE,
            title="Filtro por Tipo",
            examples=["Todos", "Bisagras", "Cerraduras"],
            shortcuts=["Ctrl+T enfocar filtro"],
        ),
        "filtro_estado": TooltipConfig(
            text="Filtrar registros por estado actual",
            tooltip_type=TooltipType.FEATURE,
            title="Filtro por Estado",
            examples=["Todos", "Activos", "Inactivos"],
            shortcuts=["Ctrl+Shift+E filtro estado"],
        ),
    }

    # Tooltips especiales para tablas
    TABLE_TOOLTIPS = {
        "table_header": TooltipConfig(
            text="Haga clic para ordenar por esta columna",
            tooltip_type=TooltipType.FEATURE,
            title="Ordenamiento",
            shortcuts=[
                "Clic para orden ascendente",
                "Clic nuevamente para descendente",
            ],
        ),
        "table_row": TooltipConfig(
            text="Doble clic para editar, clic derecho para opciones",
            tooltip_type=TooltipType.HELP,
            title="Opciones de Fila",
            shortcuts=["F2 editar", "Delete eliminar", "Ctrl+C copiar"],
        ),
        "pagination": TooltipConfig(
            text="Navegación entre páginas de resultados",
            tooltip_type=TooltipType.FEATURE,
            title="Paginación",
            shortcuts=["Page Up/Down", "Ctrl+Home/End"],
        ),
    }

    @classmethod
    def get_tooltip(
        cls, field_name: str, field_type: str = "field"
    ) -> Optional[TooltipConfig]:
        """Obtiene la configuración de tooltip para un campo específico."""
        if field_type == "table":
            return cls.TABLE_TOOLTIPS.get(field_name)
        return cls.FIELD_TOOLTIPS.get(field_name)

    @classmethod
    def format_tooltip_text(cls, config: TooltipConfig) -> str:
        """Formatea el texto del tooltip con información adicional."""
        if not config.rich_text:
            return config.text

        html = "<div style='max-width: 300px;'>"

        # Título
        if config.title:
            html += f"<h4 style='margin: 0 0 8px 0; color: #333;'>{config.title}</h4>"

        # Texto principal
        html += f"<p style='margin: 0 0 8px 0;'>{config.text}</p>"

        # Ejemplos
        if config.examples:
            html += "<p style='margin: 0 0 8px 0; font-weight: bold;'>Ejemplos:</p>"
            html += "<ul style='margin: 0 0 8px 0; padding-left: 20px;'>"
            for example in config.examples:
                html += f"<li style='color: #0066cc;'><code>{example}</code></li>"
            html += "</ul>"

        # Atajos de teclado
        if config.shortcuts:
            html += "<p style='margin: 0 0 4px 0; font-weight: bold;'>Atajos:</p>"
            html += "<p style='margin: 0; font-size: 11px; color: #666;'>"
            html += " • ".join([f"<kbd>{s}</kbd>" for s in config.shortcuts])
            html += "</p>"

        html += "</div>"
        return html


class TooltipManager:
    """Gestor principal para tooltips del sistema."""

    def __init__(self):
        self.enabled = True
        self.custom_tooltips: Dict[str, TooltipConfig] = {}
        self.widget_tooltips: Dict[QWidget, TooltipConfig] = {}
        self.current_timer: Optional[QTimer] = None

    def enable_tooltips(self, enabled: bool = True):
        """Habilita o deshabilita los tooltips globalmente."""
        self.enabled = enabled

    def register_custom_tooltip(self, identifier: str, config: TooltipConfig):
        """Registra un tooltip personalizado."""
        self.custom_tooltips[identifier] = config

    def apply_smart_tooltips(self, widget: QWidget, module_name: str = ""):
        """Aplica tooltips inteligentes a un widget y sus hijos."""
        if not self.enabled:
            return

        # Aplicar a formularios
        if isinstance(widget, QWidget):
            self._apply_to_form_layout(widget, module_name)

        # Aplicar a widgets específicos
        self._apply_to_specific_widgets(widget, module_name)

    def _apply_to_form_layout(self, widget: QWidget, module_name: str):
        """Aplica tooltips a layouts de formulario."""
        form_layout = widget.findChild(QFormLayout)
        if not form_layout:
            return

        for i in range(form_layout.rowCount()):
            label_item = form_layout.itemAt(i, QFormLayout.ItemRole.LabelRole)
            field_item = form_layout.itemAt(i, QFormLayout.ItemRole.FieldRole)

            if label_item and field_item:
                label_widget = label_item.widget()
                field_widget = field_item.widget()

                if label_widget and field_widget:
                    # Detectar tipo de campo por el texto del label
                    if hasattr(label_widget, "text"):
                        label_text = getattr(label_widget, "text")()
                        field_name = self._detect_field_name(label_text.lower())
                        self._apply_tooltip_to_widget(
                            field_widget, field_name, module_name
                        )

    def _apply_to_specific_widgets(self, parent: QWidget, module_name: str):
        """Aplica tooltips a widgets específicos por tipo."""
        # Campos de entrada
        for line_edit in parent.findChildren(QLineEdit):
            object_name = line_edit.objectName()
            placeholder = line_edit.placeholderText()
            field_name = self._detect_field_name_from_widget(
                line_edit, object_name, placeholder
            )
            self._apply_tooltip_to_widget(line_edit, field_name, module_name)

        # Comboboxes
        for combo in parent.findChildren(QComboBox):
            object_name = combo.objectName()
            field_name = self._detect_field_name_from_widget(combo, object_name)
            self._apply_tooltip_to_widget(combo, field_name, module_name)

        # Botones
        for button in parent.findChildren(QPushButton):
            button_text = button.text().lower()
            field_name = self._detect_button_type(button_text)
            self._apply_tooltip_to_widget(button, field_name, module_name)

        # Tablas
        for table in parent.findChildren(QTableWidget):
            self._apply_table_tooltips(table)

    def _detect_field_name(self, label_text: str) -> str:
        """Detecta el tipo de campo basado en el texto del label."""
        label_text = label_text.lower().replace(":", "").strip()

        # Mapeo de palabras clave a tipos de campo
        field_mappings = {
            "código": "codigo",
            "codigo": "codigo",
            "descripción": "descripcion",
            "descripcion": "descripcion",
            "precio": "precio",
            "stock": "stock",
            "cantidad": "cantidad",
            "fecha": "fecha",
            "usuario": "usuario",
            "email": "email",
            "correo": "email",
            "tipo": "tipo_herraje",
            "categoria": "tipo_herraje",
            "categoría": "tipo_herraje",
            "estado": "estado_obra",
            "búsqueda": "busqueda",
            "busqueda": "busqueda",
            "buscar": "busqueda",
        }

        for keyword, field_name in field_mappings.items():
            if keyword in label_text:
                return field_name

        return "codigo"  # Por defecto

    def _detect_field_name_from_widget(
        self, widget: QWidget, object_name: str, placeholder: str = ""
    ) -> str:
        """Detecta el tipo de campo basado en el objeto y placeholder."""
        # Primero intentar por object name
        if object_name:
            name_lower = object_name.lower()
            if "codigo" in name_lower or "code" in name_lower:
                return "codigo"
            elif "descripcion" in name_lower or "desc" in name_lower:
                return "descripcion"
            elif "precio" in name_lower or "price" in name_lower:
                return "precio"
            elif "stock" in name_lower:
                return "stock"
            elif "cantidad" in name_lower or "qty" in name_lower:
                return "cantidad"
            elif "fecha" in name_lower or "date" in name_lower:
                return "fecha"
            elif "usuario" in name_lower or "user" in name_lower:
                return "usuario"
            elif "email" in name_lower or "mail" in name_lower:
                return "email"
            elif "busqueda" in name_lower or "search" in name_lower:
                return "busqueda"
            elif "tipo" in name_lower or "type" in name_lower:
                return "tipo_herraje"
            elif "filtro" in name_lower or "filter" in name_lower:
                return "filtro_tipo"

        # Intentar por placeholder
        if placeholder:
            return self._detect_field_name(placeholder)

        return "codigo"  # Por defecto

    def _detect_button_type(self, button_text: str) -> str:
        """Detecta el tipo de botón basado en su texto."""
        if "nuevo" in button_text or "agregar" in button_text or "+" in button_text:
            return "btn_nuevo"
        elif (
            "editar" in button_text or "modificar" in button_text or "✏" in button_text
        ):
            return "btn_editar"
        elif "eliminar" in button_text or "borrar" in button_text or "🗑" in button_text:
            return "btn_eliminar"
        elif "guardar" in button_text or "save" in button_text or "💾" in button_text:
            return "btn_guardar"
        elif "cancelar" in button_text or "cancel" in button_text:
            return "btn_cancelar"
        else:
            return "btn_nuevo"  # Por defecto

    def _apply_tooltip_to_widget(
        self, widget: QWidget, field_name: str, module_name: str
    ):
        """Aplica tooltip a un widget específico."""
        # Buscar tooltip personalizado primero
        custom_key = f"{module_name}_{field_name}"
        config = self.custom_tooltips.get(custom_key)

        if not config:
            config = SmartTooltip.get_tooltip(field_name)

        if config:
            tooltip_text = SmartTooltip.format_tooltip_text(config)
            widget.setToolTip(tooltip_text)
            widget.setToolTipDuration(config.duration_ms)

            # Guardar referencia para manejo posterior
            self.widget_tooltips[widget] = config

    def _apply_table_tooltips(self, table: QTableWidget):
        """Aplica tooltips específicos para tablas."""
        # Tooltip para la tabla en general
        table_config = SmartTooltip.get_tooltip("table_row", "table")
        if table_config:
            tooltip_text = SmartTooltip.format_tooltip_text(table_config)
            table.setToolTip(tooltip_text)

        # Tooltips para headers
        header_config = SmartTooltip.get_tooltip("table_header", "table")
        if header_config:
            header_tooltip = SmartTooltip.format_tooltip_text(header_config)
            horizontal_header = table.horizontalHeader()
            if horizontal_header:
                horizontal_header.setToolTip(header_tooltip)

    def show_contextual_tooltip(
        self,
        widget: QWidget,
        position: QPoint,
        text: str,
        tooltip_type: TooltipType = TooltipType.INFO,
    ):
        """Muestra un tooltip contextual en una posición específica."""
        if not self.enabled:
            return

        # Crear configuración temporal
        config = TooltipConfig(text=text, tooltip_type=tooltip_type, duration_ms=3000)

        formatted_text = SmartTooltip.format_tooltip_text(config)
        QToolTip.showText(position, formatted_text, widget, QRect(), config.duration_ms)

    def get_tooltip_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas de tooltips aplicados."""
        total_tooltips = len(self.widget_tooltips)
        types_count = {}

        for config in self.widget_tooltips.values():
            type_name = config.tooltip_type.value
            types_count[type_name] = types_count.get(type_name, 0) + 1

        return {
            "total_tooltips": total_tooltips,
            "by_type": types_count,
            "custom_tooltips": len(self.custom_tooltips),
            "enabled": self.enabled,
        }


# Instancia global del gestor
tooltip_manager = TooltipManager()


# Funciones de conveniencia
def setup_smart_tooltips(widget: QWidget, module_name: str = ""):
    """Configura tooltips inteligentes para un widget."""
    tooltip_manager.apply_smart_tooltips(widget, module_name)


def add_custom_tooltip(
    widget: QWidget,
    text: str,
    title: str = "",
    examples: Optional[List[str]] = None,
    shortcuts: Optional[List[str]] = None,
):
    """Añade un tooltip personalizado a un widget."""
    config = TooltipConfig(
        text=text,
        tooltip_type=TooltipType.INFO,
        title=title,
        examples=examples or [],
        shortcuts=shortcuts or [],
    )

    formatted_text = SmartTooltip.format_tooltip_text(config)
    widget.setToolTip(formatted_text)


def show_help_tooltip(widget: QWidget, text: str, position: Optional[QPoint] = None):
    """Muestra un tooltip de ayuda temporal."""
    if position is None:
        position = widget.mapToGlobal(QPoint(0, widget.height()))

    tooltip_manager.show_contextual_tooltip(widget, position, text, TooltipType.HELP)


def enable_tooltips(enabled: bool = True):
    """Habilita o deshabilita tooltips globalmente."""
    tooltip_manager.enable_tooltips(enabled)
