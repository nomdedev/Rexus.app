"""
Sistema de Loading Manager para Rexus.app
Proporciona indicadores de carga unificados para toda la aplicación
"""

from typing import Optional

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QFrame, QLabel, QProgressBar, QVBoxLayout, QWidget


class LoadingManager:
    """Gestor centralizado de indicadores de carga."""

    def __init__(self):
        self.loading_widgets = {}

    def show_loading(self, parent_widget: QWidget, mensaje: str = "Cargando..."):
        """Muestra indicador de carga en el widget especificado."""
        if parent_widget in self.loading_widgets:
            return  # Ya está mostrando loading

        # Crear overlay de loading
        loading_overlay = self._create_loading_overlay(parent_widget, mensaje)
        self.loading_widgets[parent_widget] = loading_overlay
        loading_overlay.show()

    def hide_loading(self, parent_widget: Optional[QWidget] = None):
        """Oculta indicador de carga."""
        if parent_widget:
            if parent_widget in self.loading_widgets:
                overlay = self.loading_widgets[parent_widget]
                # Limpiar timer si existe
                timer = overlay.property("timer")
                if timer:
                    timer.stop()
                    timer.deleteLater()
                overlay.hide()
                overlay.deleteLater()
                del self.loading_widgets[parent_widget]
        else:
            # Ocultar todos los loading
            for widget, overlay in list(self.loading_widgets.items()):
                timer = overlay.property("timer")
                if timer:
                    timer.stop()
                    timer.deleteLater()
                overlay.hide()
                overlay.deleteLater()
            self.loading_widgets.clear()

    def _create_loading_overlay(self, parent: QWidget, mensaje: str) -> QWidget:
        """Crea un overlay de loading sobre el widget padre."""
        overlay = QFrame(parent)
        overlay.setStyleSheet("""
            QFrame {
                background-color: rgba(0, 0, 0, 0.7);
                border-radius: 8px;
            }
        """)
        overlay.setGeometry(parent.rect())

        # Layout central
        layout = QVBoxLayout(overlay)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Spinner simple (usando texto animado)
        spinner_label = QLabel("⏳")
        spinner_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 32px;
                font-weight: bold;
            }
        """)
        spinner_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(spinner_label)

        # Mensaje
        message_label = QLabel(mensaje)
        message_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 14px;
                font-weight: bold;
                margin-top: 10px;
            }
        """)
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(message_label)

        # Barra de progreso indeterminada
        progress = QProgressBar()
        progress.setRange(0, 0)  # Modo indeterminado
        progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid white;
                border-radius: 5px;
                text-align: center;
                color: white;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #007bff;
                border-radius: 3px;
            }
        """)
        layout.addWidget(progress)

        # Animar el spinner
        timer = QTimer()
        spinner_chars = ["⏳", "⌛", "⏳", "⌛"]
        counter = [0]  # Usar lista para modificar en lambda

        def animate_spinner():
            spinner_label.setText(spinner_chars[counter[0] % len(spinner_chars)])
            counter[0] += 1

        timer.timeout.connect(animate_spinner)
        timer.start(500)  # Cambiar cada 500ms

        # Guardar timer en el overlay para limpiarlo después
        overlay.setProperty("timer", timer)

        return overlay


# Instancia global para usar en toda la aplicación
loading_manager = LoadingManager()


class QuickLoading:
    """Métodos rápidos para mostrar/ocultar loading."""

    @staticmethod
    def show(widget: QWidget, mensaje: str = "Cargando..."):
        """Muestra loading rápido."""
        loading_manager.show_loading(widget, mensaje)

    @staticmethod
    def hide(widget: Optional[QWidget] = None):
        """Oculta loading rápido."""
        loading_manager.hide_loading(widget)
