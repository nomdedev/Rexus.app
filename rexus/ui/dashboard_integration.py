"""
Rexus.app - Dashboard Integration

Módulo de integración para crear botones y componentes del dashboard.
Facilita la creación de interfaces modulares.
"""

from typing import Callable, Optional
from PyQt6.QtWidgets import QPushButton, QVBoxLayout, QWidget, QLabel
from PyQt6.QtCore import Qt

from rexus.utils.app_logger import log_info


def create_dashboard_button(
    text_or_parent=None,
    callback: Optional[Callable] = None,
    icon_path: Optional[str] = None,
    tooltip: Optional[str] = None,
    parent: Optional[QWidget] = None
) -> QPushButton:
    """
    Crea un botón estilizado para el dashboard.

    Esta función es flexible para manejar diferentes formas de llamada:
    - create_dashboard_button(text, callback, ...)
    - create_dashboard_button(parent)  # Para compatibilidad con código existente

    Args:
        text_or_parent: Texto del botón o widget padre (para compatibilidad)
        callback: Función a ejecutar al hacer clic
        icon_path: Ruta del ícono (opcional)
        tooltip: Texto de ayuda (opcional)
        parent: Widget padre (opcional)

    Returns:
        Botón configurado
    """
    # Detectar si se está llamando con el patrón antiguo (parent como primer argumento)
    if hasattr(text_or_parent, '__class__') and 'MainWindow' in str(type(text_or_parent)):
        # Patrón antiguo: create_dashboard_button(parent)
        actual_parent = text_or_parent
        actual_text = "Dashboard Ejecutivo"

        def default_callback():
            pass  # Callback vacío por defecto

        actual_callback = default_callback

    else:
        # Patrón nuevo: create_dashboard_button(text, callback, ...)
        actual_text = text_or_parent if isinstance(text_or_parent, str) else "Dashboard"
        actual_callback = callback
        actual_parent = parent

    button = QPushButton(actual_text, actual_parent)

    # Estilos del botón
    button.setStyleSheet("""
        QPushButton {
            background-color: #3498db;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 6px;
            font-size: 14px;
            font-weight: bold;
            min-width: 120px;
            min-height: 40px;
        }
        QPushButton:hover {
            background-color: #2980b9;
        }
        QPushButton:pressed {
            background-color: #21618c;
        }
        QPushButton:disabled {
            background-color: #bdc3c7;
        }
    """)

    # Conectar callback
    if actual_callback:
        button.clicked.connect(actual_callback)

    # Configurar tooltip si se proporciona
    if tooltip:
        button.setToolTip(tooltip)

    # Configurar ícono si se proporciona
    if icon_path:
        try:
            # Aquí se cargaría el ícono si existiera
            log_info(f"Ícono solicitado para botón: {icon_path}", "dashboard_integration")
        except Exception as e:
            log_info(f"No se pudo cargar ícono {icon_path}: {e}", "dashboard_integration")

    log_info(f"Botón del dashboard creado: {actual_text}", "dashboard_integration")
    return button


def create_module_card(
    title: str,
    description: str,
    callback: Callable,
    icon_path: Optional[str] = None
) -> QWidget:
    """
    Crea una tarjeta para representar un módulo.

    Args:
        title: Título del módulo
        description: Descripción del módulo
        callback: Función a ejecutar al hacer clic
        icon_path: Ruta del ícono (opcional)

    Returns:
        Widget de la tarjeta
    """
    card = QWidget()
    layout = QVBoxLayout(card)

    # Título
    title_label = QLabel(title)
    title_label.setStyleSheet("""
        QLabel {
            font-size: 16px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 5px;
        }
    """)
    title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

    # Descripción
    desc_label = QLabel(description)
    desc_label.setStyleSheet("""
        QLabel {
            font-size: 12px;
            color: #7f8c8d;
            margin-bottom: 10px;
        }
    """)
    desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    desc_label.setWordWrap(True)

    # Botón de acceso
    access_button = create_dashboard_button("Acceder", callback, icon_path, f"Acceder a {title}")

    layout.addWidget(title_label)
    layout.addWidget(desc_label)
    layout.addWidget(access_button)

    # Estilos de la tarjeta
    card.setStyleSheet("""
        QWidget {
            background-color: white;
            border: 2px solid #e1e8ed;
            border-radius: 8px;
            padding: 15px;
            margin: 5px;
        }
        QWidget:hover {
            border-color: #3498db;
        }
    """)

    log_info(f"Tarjeta de módulo creada: {title}", "dashboard_integration")
    return card


def create_status_indicator(
    label: str,
    status: str,
    status_color: str = "#27ae60"
) -> QWidget:
    """
    Crea un indicador de estado.

    Args:
        label: Etiqueta del indicador
        status: Texto del estado
        status_color: Color del estado

    Returns:
        Widget del indicador
    """
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.setContentsMargins(0, 0, 0, 0)

    # Etiqueta
    label_widget = QLabel(label)
    label_widget.setStyleSheet("font-weight: bold; font-size: 12px;")
    label_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)

    # Estado
    status_widget = QLabel(status)
    status_widget.setStyleSheet(f"""
        QLabel {{
            color: {status_color};
            font-weight: bold;
            font-size: 14px;
        }}
    """)
    status_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)

    layout.addWidget(label_widget)
    layout.addWidget(status_widget)

    return widget


def create_separator() -> QWidget:
    """
    Crea un separador visual.

    Returns:
        Widget separador
    """
    separator = QWidget()
    separator.setFixedHeight(1)
    separator.setStyleSheet("background-color: #e1e8ed; margin: 10px 0px;")
    return separator
