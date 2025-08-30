"""
Widget de Mensajes de Error Modernos - Rexus.app
Componente visual para mostrar mensajes de error contextualizados
"""

import logging
from typing import Dict, Any
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont

logger = logging.getLogger(__name__)


class ErrorNotificationWidget(QWidget):
    """
    Widget moderno para mostrar notificaciones de error con contexto detallado
    """

    # Señales
    error_acknowledged = pyqtSignal(str)  # error_id
    error_details_requested = pyqtSignal(str)  # error_id
    error_resolved = pyqtSignal(str)  # error_id

    def __init__(self, parent=None):
        super().__init__(parent)
        self.error_history = []
        self.current_error_id = None
        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        """Configurar la interfaz de usuario"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Título
        title_label = QLabel("Notificaciones de Error")
        title_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout.addWidget(title_label)

        # Área de scroll para errores
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Widget contenedor para los errores
        self.errors_container = QWidget()
        self.errors_layout = QVBoxLayout(self.errors_container)
        self.errors_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        scroll_area.setWidget(self.errors_container)
        layout.addWidget(scroll_area)

        # Botones de acción
        buttons_layout = QHBoxLayout()

        self.btn_clear_all = QPushButton("Limpiar Todo")
        self.btn_clear_all.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)

        self.btn_export_errors = QPushButton("Exportar Errores")
        self.btn_export_errors.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #138496;
            }
        """)

        buttons_layout.addWidget(self.btn_clear_all)
        buttons_layout.addWidget(self.btn_export_errors)
        buttons_layout.addStretch()

        layout.addLayout(buttons_layout)

    def setup_connections(self):
        """Configurar conexiones de señales"""
        self.btn_clear_all.clicked.connect(self.clear_all_errors)
        self.btn_export_errors.clicked.connect(self.export_errors)

    def add_error(self, error_data: Dict[str, Any]) -> str:
        """
        Agregar un nuevo error al widget

        Args:
            error_data: Diccionario con información del error

        Returns:
            str: ID único del error
        """
        try:
            import uuid
            error_id = str(uuid.uuid4())

            # Crear widget de error
            error_widget = ErrorItemWidget(error_data, error_id, self)
            error_widget.error_acknowledged.connect(self._on_error_acknowledged)
            error_widget.error_details_requested.connect(self._on_error_details_requested)
            error_widget.error_resolved.connect(self._on_error_resolved)

            self.errors_layout.addWidget(error_widget)
            self.error_history.append({
                'id': error_id,
                'data': error_data,
                'widget': error_widget,
                'timestamp': error_data.get('timestamp', None)
            })

            self.current_error_id = error_id

            # Auto-scroll al nuevo error
            QTimer.singleShot(100, lambda: self._scroll_to_bottom())

            logger.info(f"Error agregado al widget: {error_id}")
            return error_id

        except Exception as e:
            logger.error(f"Error al agregar error al widget: {str(e)}")
            return ""

    def _scroll_to_bottom(self):
        """Desplazar al final de la lista de errores"""
        try:
            scroll_area = self.findChild(QScrollArea)
            if scroll_area:
                scrollbar = scroll_area.verticalScrollBar()
                scrollbar.setValue(scrollbar.maximum())
        except Exception as e:
            logger.error(f"Error al hacer scroll: {str(e)}")

    def remove_error(self, error_id: str):
        """Remover un error específico"""
        try:
            for i, error_info in enumerate(self.error_history):
                if error_info['id'] == error_id:
                    # Remover widget
                    error_info['widget'].setParent(None)
                    error_info['widget'].deleteLater()

                    # Remover de la historia
                    self.error_history.pop(i)
                    break

            logger.info(f"Error removido: {error_id}")

        except Exception as e:
            logger.error(f"Error al remover error {error_id}: {str(e)}")

    def clear_all_errors(self):
        """Limpiar todos los errores"""
        try:
            # Remover todos los widgets
            for error_info in self.error_history:
                error_info['widget'].setParent(None)
                error_info['widget'].deleteLater()

            self.error_history.clear()
            self.current_error_id = None

            logger.info("Todos los errores limpiados")

        except Exception as e:
            logger.error(f"Error al limpiar errores: {str(e)}")

    def export_errors(self):
        """Exportar errores a archivo"""
        try:
            from datetime import datetime
            import json

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"errors_export_{timestamp}.json"

            export_data = []
            for error_info in self.error_history:
                export_data.append({
                    'id': error_info['id'],
                    'timestamp': error_info.get('timestamp'),
                    'data': error_info['data']
                })

            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)

            logger.info(f"Errores exportados a: {filename}")

        except Exception as e:
            logger.error(f"Error al exportar errores: {str(e)}")

    def _on_error_acknowledged(self, error_id: str):
        """Manejador de error reconocido"""
        self.error_acknowledged.emit(error_id)

    def _on_error_details_requested(self, error_id: str):
        """Manejador de solicitud de detalles"""
        self.error_details_requested.emit(error_id)

    def _on_error_resolved(self, error_id: str):
        """Manejador de error resuelto"""
        self.error_resolved.emit(error_id)
        # Opcional: remover automáticamente errores resueltos
        # self.remove_error(error_id)


class ErrorItemWidget(QFrame):
    """
    Widget individual para mostrar un error específico
    """

    # Señales
    error_acknowledged = pyqtSignal(str)
    error_details_requested = pyqtSignal(str)
    error_resolved = pyqtSignal(str)

    def __init__(self, error_data: Dict[str, Any], error_id: str, parent=None):
        super().__init__(parent)
        self.error_data = error_data
        self.error_id = error_id
        self.setup_ui()

    def setup_ui(self):
        """Configurar interfaz del item de error"""
        self.setFrameStyle(QFrame.Shape.Box)
        self.setLineWidth(1)
        self.setStyleSheet("""
            ErrorItemWidget {
                background-color: #fff3cd;
                border: 1px solid #ffeaa7;
                border-radius: 5px;
                margin: 2px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)

        # Título del error
        title = self.error_data.get('title', 'Error')
        title_label = QLabel(f"⚠️ {title}")
        title_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #856404;")
        layout.addWidget(title_label)

        # Mensaje del error
        message = self.error_data.get('message', 'Error desconocido')
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_label.setStyleSheet("color: #856404;")
        layout.addWidget(message_label)

        # Información adicional si existe
        if 'details' in self.error_data:
            details_label = QLabel(f"Detalles: {self.error_data['details']}")
            details_label.setWordWrap(True)
            details_label.setStyleSheet("color: #6c757d; font-size: 11px;")
            layout.addWidget(details_label)

        # Timestamp si existe
        if 'timestamp' in self.error_data:
            from datetime import datetime
            try:
                dt = datetime.fromisoformat(self.error_data['timestamp'])
                time_label = QLabel(f"Hora: {dt.strftime('%H:%M:%S')}")
                time_label.setStyleSheet("color: #6c757d; font-size: 10px;")
                layout.addWidget(time_label)
            except Exception:
                pass

        # Botones de acción
        buttons_layout = QHBoxLayout()

        self.btn_acknowledge = QPushButton("Reconocido")
        self.btn_acknowledge.setStyleSheet("""
            QPushButton {
                background-color: #ffc107;
                color: #212529;
                border: none;
                padding: 4px 8px;
                border-radius: 3px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #e0a800;
            }
        """)

        self.btn_details = QPushButton("Detalles")
        self.btn_details.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8;
                color: white;
                border: none;
                padding: 4px 8px;
                border-radius: 3px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #138496;
            }
        """)

        self.btn_resolve = QPushButton("Resolver")
        self.btn_resolve.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 4px 8px;
                border-radius: 3px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)

        buttons_layout.addWidget(self.btn_acknowledge)
        buttons_layout.addWidget(self.btn_details)
        buttons_layout.addWidget(self.btn_resolve)
        buttons_layout.addStretch()

        layout.addLayout(buttons_layout)

        # Conectar señales
        self.btn_acknowledge.clicked.connect(lambda: self.error_acknowledged.emit(self.error_id))
        self.btn_details.clicked.connect(lambda: self.error_details_requested.emit(self.error_id))
        self.btn_resolve.clicked.connect(lambda: self.error_resolved.emit(self.error_id))


# Función de utilidad para crear notificación de error rápida
def show_error_notification(parent, title: str, message: str, details: str = None) -> ErrorNotificationWidget:
    """
    Función de utilidad para mostrar una notificación de error rápidamente

    Args:
        parent: Widget padre
        title: Título del error
        message: Mensaje del error
        details: Detalles adicionales (opcional)

    Returns:
        ErrorNotificationWidget: Widget de notificación creado
    """
    try:
        from datetime import datetime

        error_data = {
            'title': title,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }

        if details:
            error_data['details'] = details

        widget = ErrorNotificationWidget(parent)
        widget.add_error(error_data)

        return widget

    except Exception as e:
        logger.error(f"Error al crear notificación: {str(e)}")
        return None
