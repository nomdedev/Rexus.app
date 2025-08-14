"""
MIT License

Copyright (c) 2024 Rexus.app

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

"""
Mixin de Feedback Visual - Rexus.app
Versión: 2.0.0 - Enterprise Ready

Mixin que proporciona métodos de feedback visual consistentes
para todas las vistas de la aplicación.
"""

from typing import Optional
from PyQt6.QtWidgets import QWidget, QLabel, QMessageBox

from ..utils.feedback_manager import get_feedback_manager
from ..utils.theme_manager import ThemeManager
from ..core.logger import get_logger
from .advanced_feedback import (
    create_spinner, create_progress_bar, create_toast,
    create_loading_overlay, create_status_indicator
)

logger = get_logger("feedback_mixin")


class FeedbackMixin:
    """
    Mixin que proporciona métodos de feedback visual integrados con el tema.

    Para usar este mixin, simplemente herede de él en su clase de vista:

    class MiVista(QWidget, FeedbackMixin):
        def __init__(self):
            super().__init__()
            self.init_feedback()  # Importante: llamar esto

        def alguna_accion(self):
            self.mostrar_mensaje("Éxito", "Operación completada", "success")
    """

    def init_feedback(self, theme_manager: Optional[ThemeManager] = None):
        """
        Inicializar el sistema de feedback para esta vista.
        Debe llamarse en el __init__ de la vista.

        Args:
            theme_manager: Manager de temas (opcional)
        """
        self._feedback_manager = get_feedback_manager(theme_manager)
        self._status_labels = {}  # Cache de labels de estado
        self._feedback_timers = {}  # Timers para auto-hide
        self._theme_manager = theme_manager

        # Cache para componentes avanzados
        self._spinners = {}
        self._progress_bars = {}
        self._toasts = {}
        self._loading_overlays = {}
        self._status_indicators = {}

        logger.debug(f"Feedback inicializado para {self.__class__.__name__}")

    def mostrar_mensaje(self,
titulo: str,
        mensaje: str,
        tipo: str = "info") -> int:
        """
        Mostrar un mensaje de feedback visual.

        Args:
            titulo: Título del mensaje
            mensaje: Contenido del mensaje
            tipo: Tipo ('info', 'success', 'warning', 'error')

        Returns:
            Código de respuesta del diálogo
        """
        if not hasattr(self, '_feedback_manager'):
            logger.warning(f"Feedback no inicializado en {self.__class__.__name__}")
            self.init_feedback()

        return self._feedback_manager.show_message(self,
titulo,
            mensaje,
            tipo)

    def mostrar_confirmacion(self, titulo: str, mensaje: str,
                           botones: QMessageBox.StandardButton = None) -> int:
        """
        Mostrar un diálogo de confirmación.

        Args:
            titulo: Título del diálogo
            mensaje: Mensaje de confirmación
            botones: Botones a mostrar

        Returns:
            Botón presionado por el usuario
        """
        if not hasattr(self, '_feedback_manager'):
            self.init_feedback()

        return self._feedback_manager.show_confirmation(self,
titulo,
            mensaje,
            botones)

    def crear_status_label(self, nombre: str = "default") -> QLabel:
        """
        Crear y configurar un label de estado para feedback inline.

        Args:
            nombre: Nombre único para el label (permite múltiples labels)

        Returns:
            QLabel configurado con estilos del tema
        """
        if not hasattr(self, '_feedback_manager'):
            self.init_feedback()

        if nombre in self._status_labels:
            return self._status_labels[nombre]

        label = self._feedback_manager.create_status_label(self)
        self._status_labels[nombre] = label

        return label

    def mostrar_status(self, mensaje: str, tipo: str = "info", duration: int = 3000,
                      label_name: str = "default"):
        """
        Mostrar mensaje en un status label.

        Args:
            mensaje: Mensaje a mostrar
            tipo: Tipo de mensaje
            duration: Duración en ms (0 = permanente)
            label_name: Nombre del label a usar
        """
        if not hasattr(self, '_feedback_manager'):
            self.init_feedback()

        # Obtener o crear el label
        if label_name not in self._status_labels:
            self.crear_status_label(label_name)

        label = self._status_labels[label_name]

        # Mostrar el mensaje
        self._feedback_manager.show_status_message(label,
mensaje,
            tipo,
            duration)

    def ocultar_status(self, label_name: str = "default"):
        """
        Ocultar un status label específico.

        Args:
            label_name: Nombre del label a ocultar
        """
        if label_name in self._status_labels:
            self._status_labels[label_name].setVisible(False)

    def mostrar_cargando(self, mensaje: str = "Cargando...", label_name: str = "default"):
        """
        Mostrar indicador de carga.

        Args:
            mensaje: Mensaje de carga
            label_name: Nombre del label a usar
        """
        self.mostrar_status(f"🔄 {mensaje}", "info", 0, label_name)

    def ocultar_cargando(self, label_name: str = "default"):
        """
        Ocultar indicador de carga.

        Args:
            label_name: Nombre del label
        """
        self.ocultar_status(label_name)

    def mostrar_exito(self,
mensaje: str,
        duration: int = 3000,
        label_name: str = "default"):
        """Mostrar mensaje de éxito"""
        self.mostrar_status(mensaje, "success", duration, label_name)

    def mostrar_error(self,
mensaje: str,
        duration: int = 5000,
        label_name: str = "default"):
        """Mostrar mensaje de error"""
        self.mostrar_status(mensaje, "error", duration, label_name)

    def mostrar_advertencia(self,
mensaje: str,
        duration: int = 4000,
        label_name: str = "default"):
        """Mostrar mensaje de advertencia"""
        self.mostrar_status(mensaje, "warning", duration, label_name)

    def mostrar_info(self,
mensaje: str,
        duration: int = 3000,
        label_name: str = "default"):
        """Mostrar mensaje informativo"""
        self.mostrar_status(mensaje, "info", duration, label_name)

    # Métodos para componentes avanzados

    def crear_spinner(self, nombre: str = "default"):
        """
        Crear un spinner animado.

        Args:
            nombre: Nombre único para el spinner

        Returns:
            AnimatedSpinner configurado con el tema
        """
        if not hasattr(self, '_theme_manager'):
            self.init_feedback()

        if nombre in self._spinners:
            return self._spinners[nombre]

        spinner = create_spinner(self, self._theme_manager)
        self._spinners[nombre] = spinner

        return spinner

    def crear_progress_bar(self, nombre: str = "default"):
        """
        Crear una progress bar temática.

        Args:
            nombre: Nombre único para la progress bar

        Returns:
            ThemedProgressBar configurada con el tema
        """
        if not hasattr(self, '_theme_manager'):
            self.init_feedback()

        if nombre in self._progress_bars:
            return self._progress_bars[nombre]

        progress_bar = create_progress_bar(self, self._theme_manager)
        self._progress_bars[nombre] = progress_bar

        return progress_bar

    def crear_toast(self, nombre: str = "default"):
        """
        Crear una notificación toast.

        Args:
            nombre: Nombre único para el toast

        Returns:
            ToastNotification configurada con el tema
        """
        if not hasattr(self, '_theme_manager'):
            self.init_feedback()

        if nombre in self._toasts:
            return self._toasts[nombre]

        toast = create_toast(self, self._theme_manager)
        self._toasts[nombre] = toast

        return toast

    def crear_loading_overlay(self, nombre: str = "default"):
        """
        Crear un overlay de carga.

        Args:
            nombre: Nombre único para el overlay

        Returns:
            LoadingOverlay configurado con el tema
        """
        if not hasattr(self, '_theme_manager'):
            self.init_feedback()

        if nombre in self._loading_overlays:
            return self._loading_overlays[nombre]

        overlay = create_loading_overlay(self, self._theme_manager)
        self._loading_overlays[nombre] = overlay

        return overlay

    def crear_status_indicator(self, nombre: str = "default"):
        """
        Crear un indicador de estado.

        Args:
            nombre: Nombre único para el indicador

        Returns:
            StatusIndicator configurado con el tema
        """
        if not hasattr(self, '_theme_manager'):
            self.init_feedback()

        if nombre in self._status_indicators:
            return self._status_indicators[nombre]

        indicator = create_status_indicator(self, self._theme_manager)
        self._status_indicators[nombre] = indicator

        return indicator

    def mostrar_toast(self,
mensaje: str,
        tipo: str = "info",
        duration: int = 4000,
        toast_name: str = "default"):
        """
        Mostrar una notificación toast.

        Args:
            mensaje: Mensaje a mostrar
            tipo: Tipo de mensaje
            duration: Duración en ms
            toast_name: Nombre del toast a usar
        """
        if toast_name not in self._toasts:
            self.crear_toast(toast_name)

        toast = self._toasts[toast_name]
        toast.show_message(mensaje, tipo, duration)

    def mostrar_loading_overlay(self, mensaje: str = "Cargando...", overlay_name: str = "default"):
        """
        Mostrar overlay de carga.

        Args:
            mensaje: Mensaje de carga
            overlay_name: Nombre del overlay
        """
        if overlay_name not in self._loading_overlays:
            self.crear_loading_overlay(overlay_name)

        overlay = self._loading_overlays[overlay_name]
        overlay.show_loading(mensaje)

    def ocultar_loading_overlay(self, overlay_name: str = "default"):
        """
        Ocultar overlay de carga.

        Args:
            overlay_name: Nombre del overlay
        """
        if overlay_name in self._loading_overlays:
            self._loading_overlays[overlay_name].hide_loading()

    def iniciar_spinner(self, spinner_name: str = "default"):
        """
        Iniciar animación de spinner.

        Args:
            spinner_name: Nombre del spinner
        """
        if spinner_name not in self._spinners:
            self.crear_spinner(spinner_name)

        self._spinners[spinner_name].start()

    def detener_spinner(self, spinner_name: str = "default"):
        """
        Detener animación de spinner.

        Args:
            spinner_name: Nombre del spinner
        """
        if spinner_name in self._spinners:
            self._spinners[spinner_name].stop()

    def actualizar_progress(self, valor: int, progress_name: str = "default"):
        """
        Actualizar valor de progress bar.

        Args:
            valor: Valor del progreso (0-100)
            progress_name: Nombre de la progress bar
        """
        if progress_name not in self._progress_bars:
            self.crear_progress_bar(progress_name)

        self._progress_bars[progress_name].setValue(valor)

    def actualizar_status_indicator(self,
status: str,
        mensaje: str = "",
        indicator_name: str = "default"):
        """
        Actualizar indicador de estado.

        Args:
            status: Estado ('active', 'warning', 'error', 'inactive')
            mensaje: Mensaje descriptivo
            indicator_name: Nombre del indicador
        """
        if indicator_name not in self._status_indicators:
            self.crear_status_indicator(indicator_name)

        self._status_indicators[indicator_name].set_status(status, mensaje)


class FeedbackWidget(QWidget, FeedbackMixin):
    """
    Widget base que incluye automáticamente el feedback mixin.

    Útil para crear widgets que necesiten feedback sin herencia múltiple:

    class MiWidget(FeedbackWidget):
        def __init__(self):
            super().__init__()
            # El feedback ya está inicializado
            self.mostrar_mensaje("Info", "Widget listo")
    """

    def __init__(self, theme_manager: Optional[ThemeManager] = None, parent: QWidget = None):
        super().__init__(parent)
        self.init_feedback(theme_manager)


def add_feedback_to_widget(widget: QWidget, theme_manager: Optional[ThemeManager] = None) -> QWidget:
    """
    Agregar capacidades de feedback a un widget existente.

    Esta función es útil para agregar feedback a widgets que no pueden usar el mixin.

    Args:
        widget: Widget al que agregar feedback
        theme_manager: Manager de temas

    Returns:
        El mismo widget con métodos de feedback agregados
    """
    # Crear una instancia del mixin y copiar sus métodos al widget
    mixin = FeedbackMixin()
    mixin.init_feedback(theme_manager)

    # Copiar atributos del mixin al widget
    widget._feedback_manager = mixin._feedback_manager
    widget._status_labels = mixin._status_labels
    widget._feedback_timers = mixin._feedback_timers

    # Copiar métodos del mixin al widget
    widget.mostrar_mensaje = lambda titulo, mensaje, tipo="info": mixin.mostrar_mensaje.__func__(widget, titulo, mensaje, tipo)
    widget.mostrar_confirmacion = lambda titulo, mensaje, botones=None: mixin.mostrar_confirmacion.__func__(widget, titulo, mensaje, botones)
    widget.crear_status_label = lambda nombre="default": mixin.crear_status_label.__func__(widget, nombre)
    widget.mostrar_status = lambda mensaje, tipo="info", duration=3000, label_name="default": mixin.mostrar_status.__func__(widget, mensaje, tipo, duration, label_name)
    widget.mostrar_exito = lambda mensaje, duration=3000, label_name="default": mixin.mostrar_exito.__func__(widget, mensaje, duration, label_name)
    widget.mostrar_error = lambda mensaje, duration=5000, label_name="default": mixin.mostrar_error.__func__(widget, mensaje, duration, label_name)
    widget.mostrar_advertencia = lambda mensaje, duration=4000, label_name="default": mixin.mostrar_advertencia.__func__(widget, mensaje, duration, label_name)
    widget.mostrar_info = lambda mensaje, duration=3000, label_name="default": mixin.mostrar_info.__func__(widget, mensaje, duration, label_name)
    widget.mostrar_cargando = lambda mensaje="Cargando...", label_name="default": mixin.mostrar_cargando.__func__(widget, mensaje, label_name)
    widget.ocultar_cargando = lambda label_name="default": mixin.ocultar_cargando.__func__(widget, label_name)
    widget.ocultar_status = lambda label_name="default": mixin.ocultar_status.__func__(widget, label_name)

    logger.debug(f"Feedback agregado a {widget.__class__.__name__}")

    return widget
