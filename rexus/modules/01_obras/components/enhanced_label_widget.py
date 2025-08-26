"""
QLabel Mejorado para Módulo Obras
Versión optimizada con soporte para temas, animaciones y estados dinámicos

Fecha: 13/08/2025
Objetivo: Completar UI/UX del módulo Obras con componente de etiquetas mejorado
"""


import logging
logger = logging.getLogger(__name__)

from PyQt6.QtWidgets import (
    QLabel, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QColor
from typing import Optional, Dict, Any, Union
import datetime


class EnhancedLabel(QLabel):
    """
    QLabel mejorado con soporte para temas, animaciones y estados dinámicos.

    Características:
    - Soporte automático para tema oscuro/claro
    - Animaciones de hover y cambio de estado
    - Tipos especializados (status, metric, header, info)
    - Iconos integrados y colores dinámicos
    - Efectos visuales (sombras, gradientes)
    """

    # Señales personalizadas
    clicked = pyqtSignal()
    hover_enter = pyqtSignal()
    hover_leave = pyqtSignal()

    def __init__(self,
text: str = "",
        label_type: str = "default",
        parent=None):
        super().__init__(text, parent)

        # Configuración
        self.label_type = label_type
        self.is_clickable = False
        self.is_animated = True
        self.current_theme = "light"
        self.icon_text = ""

        # Animaciones
        self.fade_animation = None
        self.scale_animation = None

        # Configuraciones por tipo
        self.type_configs = {
            'default': {
                'font_size': 13,
                'font_weight': 'normal',
                'color': '#374151',
                'bg_color': 'transparent',
                'border': 'none',
                'padding': '4px 8px',
                'border_radius': '4px'
            },
            'header': {
                'font_size': 18,
                'font_weight': 'bold',
                'color': '#1f2937',
                'bg_color': 'transparent',
                'border': 'none',
                'padding': '8px 0px',
                'border_radius': '0px'
            },
            'subheader': {
                'font_size': 14,
                'font_weight': '600',
                'color': '#4b5563',
                'bg_color': 'transparent',
                'border': 'none',
                'padding': '4px 0px',
                'border_radius': '0px'
            },
            'metric': {
                'font_size': 24,
                'font_weight': 'bold',
                'color': '#059669',
                'bg_color': '#f0fdf4',
                'border': '1px solid #bbf7d0',
                'padding': '12px 16px',
                'border_radius': '8px'
            },
            'status': {
                'font_size': 12,
                'font_weight': '600',
                'color': '#ffffff',
                'bg_color': '#3b82f6',
                'border': 'none',
                'padding': '4px 12px',
                'border_radius': '12px'
            },
            'info': {
                'font_size': 12,
                'font_weight': 'normal',
                'color': '#6b7280',
                'bg_color': '#f9fafb',
                'border': '1px solid #e5e7eb',
                'padding': '6px 10px',
                'border_radius': '6px'
            },
            'warning': {
                'font_size': 13,
                'font_weight': '600',
                'color': '#d97706',
                'bg_color': '#fef3c7',
                'border': '1px solid #fde68a',
                'padding': '8px 12px',
                'border_radius': '6px'
            },
            'error': {
                'font_size': 13,
                'font_weight': '600',
                'color': '#dc2626',
                'bg_color': '#fecaca',
                'border': '1px solid #fca5a5',
                'padding': '8px 12px',
                'border_radius': '6px'
            },
            'success': {
                'font_size': 13,
                'font_weight': '600',
                'color': '#059669',
                'bg_color': '#d1fae5',
                'border': '1px solid #a7f3d0',
                'padding': '8px 12px',
                'border_radius': '6px'
            }
        }

        # Estados específicos para obras
        self.obra_status_colors = {
            'EN_PROCESO': {'color': '#059669', 'bg': '#d1fae5', 'icon': '🚧'},
            'PLANIFICACION': {'color': '#d97706', 'bg': '#fef3c7', 'icon': '[CLIPBOARD]'},
            'PAUSADA': {'color': '#dc2626', 'bg': '#fecaca', 'icon': '⏸️'},
            'FINALIZADA': {'color': '#3730a3', 'bg': '#e0e7ff', 'icon': '[OK]'},
            'CANCELADA': {'color': '#6b7280', 'bg': '#f3f4f6', 'icon': '[ERROR]'},
            'VENCIDA': {'color': '#dc2626', 'bg': '#fee2e2', 'icon': '[WARNING]'},
            'PROXIMA_VENCER': {'color': '#d97706', 'bg': '#fde68a', 'icon': '⏰'},
            'EN_TIEMPO': {'color': '#059669', 'bg': '#dcfce7', 'icon': '🟢'}
        }

        self._apply_type_style()
        self._setup_interactions()

    def _apply_type_style(self):
        """Aplica el estilo según el tipo de etiqueta."""
        if self.label_type not in self.type_configs:
            self.label_type = 'default'

        config = self.type_configs[self.label_type]

        # Configurar fuente
        font = QFont()
        font.setPointSize(config['font_size'])

        if config['font_weight'] == 'bold':
            font.setBold(True)
        elif config['font_weight'] == '600':
            font.setWeight(QFont.Weight.DemiBold)

        self.setFont(font)

        # Aplicar estilos CSS
        style = f"""
            QLabel {{
                color: {config['color']};
                background-color: {config['bg_color']};
                border: {config['border']};
                padding: {config['padding']};
                border-radius: {config['border_radius']};
            }}
        """

        # Estilos para hover si es clickeable
        if self.is_clickable:
            style += """
                QLabel:hover {
                    background-color: rgba(59, 130, 246, 0.1);
                    cursor: pointer;
                }
            """

        self.setStyleSheet(style)

        # Configurar alineación según tipo
        if self.label_type in ['header', 'subheader']:
            self.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        elif self.label_type == 'metric':
            self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        else:
            self.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

    def _setup_interactions(self):
        """Configura las interacciones del widget."""
        # Habilitar tracking del mouse para hover
        self.setMouseTracking(True)

        # Configurar efectos visuales para algunos tipos
        if self.label_type in ['metric', 'status', 'header']:
            self._add_shadow_effect()

    def _add_shadow_effect(self):
        """Agrega efecto de sombra."""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(8)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)

    def set_clickable(self, clickable: bool):
        """
        Establece si la etiqueta es clickeable.

        Args:
            clickable: True si debe ser clickeable
        """
        self.is_clickable = clickable
        if clickable:
            self.setCursor(Qt.CursorShape.PointingHandCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)
        self._apply_type_style()

    def set_obra_status(self, status: str):
        """
        Configura la etiqueta para mostrar un estado de obra.

        Args:
            status: Estado de la obra
        """
        status = status.upper()
        if status in self.obra_status_colors:
            config = self.obra_status_colors[status]
            icon = config['icon']

            # Configurar texto con icono
            self.setText(f"{icon} {status}")

            # Aplicar colores específicos
            style = f"""
                QLabel {{
                    color: {config['color']};
                    background-color: {config['bg']};
                    border: none;
                    padding: 6px 12px;
                    border-radius: 12px;
                    font-weight: 600;
                    font-size: 12px;
                }}
            """
            self.setStyleSheet(style)
            self.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def set_metric_value(self, value: Union[int, float], format_type: str = "number",
                         prefix: str = "", suffix: str = ""):
        """
        Configura la etiqueta para mostrar una métrica.

        Args:
            value: Valor de la métrica
            format_type: Tipo de formato ('number', 'currency', 'percentage')
            prefix: Prefijo del texto
            suffix: Sufijo del texto
        """
        if format_type == "currency":
            formatted_value = f"${value:,.0f}"
        elif format_type == "percentage":
            formatted_value = f"{value:.1f}%"
        elif format_type == "number":
            if isinstance(value, float):
                formatted_value = f"{value:,.1f}"
            else:
                formatted_value = f"{value:,}"
        else:
            formatted_value = str(value)

        full_text = f"{prefix}{formatted_value}{suffix}"
        self.setText(full_text)

        # Aplicar color según valor (para métricas)
        if self.label_type == 'metric':
            if isinstance(value, (int, float)):
                if value >= 1000000:  # Valor alto
                    color = "#059669"  # Verde
                    bg_color = "#d1fae5"
                elif value >= 100000:  # Valor medio
                    color = "#d97706"  # Naranja
                    bg_color = "#fef3c7"
                else:  # Valor bajo
                    color = "#6b7280"  # Gris
                    bg_color = "#f3f4f6"

                style = f"""
                    QLabel {{
                        color: {color};
                        background-color: {bg_color};
                        border: 1px solid rgba(0,0,0,0.1);
                        padding: 12px 16px;
                        border-radius: 8px;
                        font-weight: bold;
                        font-size: 24px;
                    }}
                """
                self.setStyleSheet(style)

    def set_icon_text(self, icon: str, text: str):
        """
        Establece icono y texto.

        Args:
            icon: Emoji o carácter de icono
            text: Texto a mostrar
        """
        self.icon_text = icon
        self.setText(f"{icon} {text}")

    def update_dynamic_content(self, content_type: str, data: Dict[str, Any]):
        """
        Actualiza contenido dinámico según tipo.

        Args:
            content_type: Tipo de contenido ('date_countdown', 'progress', 'status_live')
            data: Datos para el contenido
        """
        if content_type == "date_countdown":
            self._update_date_countdown(data.get('target_date'))
        elif content_type == "progress":
            self._update_progress_display(data.get('current',
0),
                data.get('total',
                100))
        elif content_type == "status_live":
            self._update_live_status(data.get('status'), data.get('last_update'))

    def _update_date_countdown(self, target_date):
        """Actualiza cuenta regresiva a una fecha."""
        if not target_date:
            self.setText("📅 Sin fecha")
            return

        try:
            if isinstance(target_date, str):
                target = datetime.datetime.strptime(target_date, "%Y-%m-%d").date()
            else:
                target = target_date

            today = datetime.date.today()
            diff = target - today

            if diff.days > 0:
                self.setText(f"⏳ {diff.days} días restantes")
                self.set_obra_status('EN_TIEMPO')
            elif diff.days == 0:
                self.setText(f"🕐 Vence hoy")
                self.set_obra_status('PROXIMA_VENCER')
            else:
                self.setText(f"[WARNING] Vencida hace {abs(diff.days)} días")
                self.set_obra_status('VENCIDA')

        except (ValueError, TypeError, AttributeError) as e:
            # ValueError: fecha mal formateada
            # TypeError: tipo de dato incorrecto
            # AttributeError: objeto sin atributos de fecha
            self.setText("📅 Fecha inválida")

    def _update_progress_display(self, current: float, total: float):
        """Actualiza display de progreso."""
        if total == 0:
            percentage = 0
        else:
            percentage = (current / total) * 100

        self.set_metric_value(percentage, "percentage")

        # Cambiar color según progreso
        if percentage >= 90:
            self.label_type = 'success'
        elif percentage >= 70:
            self.label_type = 'warning'
        else:
            self.label_type = 'error'

        self._apply_type_style()

    def _update_live_status(self, status: str, last_update: Optional[datetime.datetime]):
        """Actualiza estado en vivo."""
        if last_update:
            time_diff = datetime.datetime.now() - last_update
            if time_diff.seconds < 60:
                time_text = "Ahora"
            elif time_diff.seconds < 3600:
                time_text = f"{time_diff.seconds // 60}m"
            else:
                time_text = f"{time_diff.seconds // 3600}h"

            self.setText(f"🔴 {status} (act. {time_text})")
        else:
            self.setText(f"⚫ {status}")

    def animate_value_change(self, old_value: str, new_value: str):
        """
        Anima el cambio de valor.

        Args:
            old_value: Valor anterior
            new_value: Nuevo valor
        """
        if not self.is_animated:
            self.setText(new_value)
            return

        # Animación de fade out/in
        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(200)
        self.fade_animation.setStartValue(1.0)
        self.fade_animation.setEndValue(0.3)
        self.fade_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        def change_text():
            self.setText(new_value)
            # Fade in
            fade_in = QPropertyAnimation(self, b"windowOpacity")
            fade_in.setDuration(200)
            fade_in.setStartValue(0.3)
            fade_in.setEndValue(1.0)
            fade_in.setEasingCurve(QEasingCurve.Type.InCubic)
            fade_in.start()

        self.fade_animation.finished.connect(change_text)
        self.fade_animation.start()

    def set_theme(self, dark_mode: bool):
        """
        Aplica tema oscuro o claro.

        Args:
            dark_mode: True para tema oscuro
        """
        self.current_theme = "dark" if dark_mode else "light"

        if dark_mode:
            # Ajustar colores para tema oscuro
            if self.label_type in self.type_configs:
                config = self.type_configs[self.label_type].copy()

                # Invertir colores principales
                if config['color'] == '#374151':
                    config['color'] = '#f9fafb'
                elif config['color'] == '#1f2937':
                    config['color'] = '#ffffff'
                elif config['color'] == '#4b5563':
                    config['color'] = '#d1d5db'

                # Ajustar fondos
                if config['bg_color'] == 'transparent':
                    config['bg_color'] = 'transparent'
                elif config['bg_color'] == '#f9fafb':
                    config['bg_color'] = '#374151'

                # Aplicar estilos ajustados
                style = f"""
                    QLabel {{
                        color: {config['color']};
                        background-color: {config['bg_color']};
                        border: {config['border']};
                        padding: {config['padding']};
                        border-radius: {config['border_radius']};
                    }}
                """
                self.setStyleSheet(style)
        else:
            # Aplicar tema claro normal
            self._apply_type_style()

    def mousePressEvent(self, event):
        """Maneja el click del mouse."""
        if self.is_clickable and event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)

    def enterEvent(self, event):
        """Maneja la entrada del mouse."""
        self.hover_enter.emit()
        if self.is_animated and self.is_clickable:
            # Animación de hover
            self.scale_animation = QPropertyAnimation(self, b"geometry")
            self.scale_animation.setDuration(150)
            current_geo = self.geometry()
            expanded_geo = current_geo.adjusted(-2, -2, 2, 2)
            self.scale_animation.setStartValue(current_geo)
            self.scale_animation.setEndValue(expanded_geo)
            self.scale_animation.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Maneja la salida del mouse."""
        self.hover_leave.emit()
        if self.scale_animation:
            self.scale_animation.stop()
        super().leaveEvent(event)


class StatusIndicatorLabel(EnhancedLabel):
    """Etiqueta especializada para indicadores de estado de obras."""

    def __init__(self, parent=None):
        super().__init__("", "status", parent)
        self.status_history = []
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_display)
        self.update_timer.start(30000)  # Actualizar cada 30 segundos

    def set_obra_status_with_history(self, status: str, timestamp: datetime.datetime = None):
        """
        Establece estado con historial.

        Args:
            status: Nuevo estado
            timestamp: Timestamp del cambio
        """
        if timestamp is None:
            timestamp = datetime.datetime.now()

        # Agregar al historial
        self.status_history.append({
            'status': status,
            'timestamp': timestamp
        })

        # Mantener solo los últimos 10 cambios
        if len(self.status_history) > 10:
            self.status_history = self.status_history[-10:]

        # Actualizar display
        self.set_obra_status(status)

    def _update_display(self):
        """Actualiza el display periódicamente."""
        if self.status_history:
            last_change = self.status_history[-1]
            time_since = datetime.datetime.now() - last_change['timestamp']

            # Agregar indicador de tiempo si es reciente
            if time_since.total_seconds() < 3600:  # Menos de 1 hora
                minutes = int(time_since.total_seconds() / 60)
                current_text = self.text()
                if "(" not in current_text:
                    self.setText(f"{current_text} ({minutes}m)")


class MetricDisplayLabel(EnhancedLabel):
    """Etiqueta especializada para mostrar métricas de obras."""

    def __init__(self, metric_name: str, parent=None):
        super().__init__("", "metric", parent)
        self.metric_name = metric_name
        self.previous_value = None
        self.trend_indicator = ""

    def update_metric(self,
value: Union[int,
        float],
        format_type: str = "number"):
        """
        Actualiza la métrica con indicador de tendencia.

        Args:
            value: Nuevo valor
            format_type: Tipo de formato
        """
        # Calcular tendencia
        if self.previous_value is not None:
            if value > self.previous_value:
                self.trend_indicator = "[TRENDING]"
            elif value < self.previous_value:
                self.trend_indicator = "📉"
            else:
                self.trend_indicator = "➡️"

        # Actualizar valor
        old_text = self.text()
        self.set_metric_value(value, format_type, suffix=f" {self.trend_indicator}")

        # Animar cambio si hay diferencia significativa
        if self.previous_value is not None and \
            abs(value - self.previous_value) > 0:
            self.animate_value_change(old_text, self.text())

        self.previous_value = value
