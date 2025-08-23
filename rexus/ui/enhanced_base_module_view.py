# -*- coding: utf-8 -*-
"""
Vista Base Mejorada para Módulos - Rexus.app
Extensión de BaseModuleView con componentes modernos y funcionalidades avanzadas

Mejoras implementadas:
1. Integración de componentes UI modernos
2. Soporte para temas claro/oscuro
3. Animaciones sutiles y transiciones
4. Mejor responsividad
5. Estados de carga y feedback visual
6. Herramientas de accesibilidad
7. Dashboard integrado con métricas

Autor: Rexus Development Team
Fecha: 23/08/2025
Versión: 1.0.0
"""

import sys
from typing import Dict, List, Any, Optional, Callable
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QIcon, QPalette, QColor
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
    QScrollArea, QSplitter, QStackedWidget, QApplication,
    QProgressBar, QGraphicsOpacityEffect
)

# Imports de componentes modernos
from .modern_components import (
    ModernComponents, ModernTheme, get_current_theme, 
    ModernButton, ModernCard, ModernTable, ModernTabWidget
)

# Import del sistema de cache si está disponible
try:
    from rexus.utils.report_cache_integration import get_performance_monitor
    CACHE_AVAILABLE = True
except ImportError:
    CACHE_AVAILABLE = False

import logging
logger = logging.getLogger(__name__)


class LoadingOverlay(QWidget):
    """Overlay de carga moderno con spinner."""
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Layout y componentes
        layout = QVBoxLayout(self)
        
        # Fondo semi-transparente
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(0, 0, 0, 0.3);
            }
        """)
        
        # Contenedor central
        container = QFrame()
        container.setStyleSheet(f"""
            QFrame {{
                background: {get_current_theme().get_color('background')};
                border: 1px solid {get_current_theme().get_color('border')};
                border-radius: 12px;
                padding: 30px;
            }}
        """)
        container.setFixedSize(200, 120)
        
        container_layout = QVBoxLayout(container)
        
        # Barra de progreso
        self.progress_bar = ModernComponents.create_progress_bar()
        self.progress_bar.setRange(0, 0)  # Spinner infinito
        
        # Texto de carga
        self.loading_label = QLabel("Cargando...")
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_label.setStyleSheet(f"""
            QLabel {{
                font-size: 14px;
                font-weight: 500;
                color: {get_current_theme().get_color('text_primary')};
                margin-top: 10px;
            }}
        """)
        
        container_layout.addWidget(self.progress_bar)
        container_layout.addWidget(self.loading_label)
        
        layout.addWidget(container, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Animación de opacidad
        self.opacity_effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.opacity_effect)
        
        # Inicialmente oculto
        self.hide()
    
    def show_loading(self, message: str = "Cargando..."):
        """Mostrar overlay de carga."""
        self.loading_label.setText(message)
        
        # Animación de entrada
        self.opacity_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.opacity_animation.setDuration(200)
        self.opacity_animation.setStartValue(0.0)
        self.opacity_animation.setEndValue(1.0)
        
        self.show()
        self.opacity_animation.start()
    
    def hide_loading(self):
        """Ocultar overlay de carga."""
        # Animación de salida
        self.opacity_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.opacity_animation.setDuration(200)
        self.opacity_animation.setStartValue(1.0)
        self.opacity_animation.setEndValue(0.0)
        self.opacity_animation.finished.connect(self.hide)
        
        self.opacity_animation.start()
    
    def update_message(self, message: str):
        """Actualizar mensaje de carga."""
        self.loading_label.setText(message)


class ModernStatusBar(QWidget):
    """Barra de estado moderna con indicadores visuales."""
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.theme = get_current_theme()
        self._setup_ui()
    
    def _setup_ui(self):
        """Configurar interfaz de la barra de estado."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 6, 12, 6)
        layout.setSpacing(12)
        
        # Estado principal
        self.status_label = QLabel("Listo")
        self.status_label.setStyleSheet(f"""
            QLabel {{
                font-size: 12px;
                color: {self.theme.get_color('text_secondary')};
                font-weight: 500;
            }}
        """)
        layout.addWidget(self.status_label)
        
        # Separador
        layout.addStretch()
        
        # Indicadores de rendimiento (si cache disponible)
        if CACHE_AVAILABLE:
            self.cache_indicator = QLabel("Cache: --")
            self.cache_indicator.setStyleSheet(f"""
                QLabel {{
                    font-size: 11px;
                    color: {self.theme.get_color('text_disabled')};
                    padding: 2px 6px;
                    border: 1px solid {self.theme.get_color('border')};
                    border-radius: 4px;
                }}
            """)
            layout.addWidget(self.cache_indicator)
            
            # Timer para actualizar indicadores
            self.update_timer = QTimer()
            self.update_timer.timeout.connect(self._update_cache_stats)
            self.update_timer.start(5000)  # Actualizar cada 5 segundos
        
        # Indicador de conexión
        self.connection_indicator = QLabel("●")
        self.connection_indicator.setStyleSheet(f"""
            QLabel {{
                font-size: 14px;
                color: {self.theme.get_color('success')};
                font-weight: bold;
            }}
        """)
        layout.addWidget(self.connection_indicator)
        
        # Aplicar estilos del contenedor
        self.setStyleSheet(f"""
            QWidget {{
                background: {self.theme.get_color('surface')};
                border-top: 1px solid {self.theme.get_color('border')};
            }}
        """)
    
    def set_status(self, message: str, status_type: str = "info"):
        """Establecer mensaje de estado."""
        self.status_label.setText(message)
        
        # Colores según tipo
        colors = {
            'info': self.theme.get_color('text_secondary'),
            'success': self.theme.get_color('success'),
            'warning': self.theme.get_color('warning'),
            'error': self.theme.get_color('error')
        }
        
        color = colors.get(status_type, colors['info'])
        self.status_label.setStyleSheet(f"""
            QLabel {{
                font-size: 12px;
                color: {color};
                font-weight: 500;
            }}
        """)
    
    def set_connection_status(self, connected: bool):
        """Establecer estado de conexión."""
        if connected:
            self.connection_indicator.setStyleSheet(f"""
                QLabel {{
                    font-size: 14px;
                    color: {self.theme.get_color('success')};
                    font-weight: bold;
                }}
            """)
            self.connection_indicator.setToolTip("Conectado")
        else:
            self.connection_indicator.setStyleSheet(f"""
                QLabel {{
                    font-size: 14px;
                    color: {self.theme.get_color('error')};
                    font-weight: bold;
                }}
            """)
            self.connection_indicator.setToolTip("Desconectado")
    
    def _update_cache_stats(self):
        """Actualizar estadísticas de cache."""
        if not CACHE_AVAILABLE:
            return
        
        try:
            monitor = get_performance_monitor()
            stats = monitor.get_performance_summary(hours=1)
            
            if stats.get('total_reports', 0) > 0:
                hit_rate = stats.get('cache_hit_rate', 0)
                self.cache_indicator.setText(f"Cache: {hit_rate}%")
                
                # Color basado en rendimiento
                if hit_rate >= 80:
                    color = self.theme.get_color('success')
                elif hit_rate >= 60:
                    color = self.theme.get_color('warning')
                else:
                    color = self.theme.get_color('error')
                
                self.cache_indicator.setStyleSheet(f"""
                    QLabel {{
                        font-size: 11px;
                        color: {color};
                        padding: 2px 6px;
                        border: 1px solid {self.theme.get_color('border')};
                        border-radius: 4px;
                    }}
                """)
            
        except Exception as e:
            logger.error(f"Error actualizando stats de cache: {e}")


class EnhancedBaseModuleView(QWidget):
    """Vista base mejorada para módulos con componentes modernos."""
    
    # Señales para comunicación entre componentes
    module_loaded = pyqtSignal()
    data_updated = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    status_changed = pyqtSignal(str, str)  # message, type
    
    def __init__(self, module_name: str = "", parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self.module_name = module_name
        self.theme = get_current_theme()
        self.controller = None
        self.data = {}
        self.widgets = {}
        self.is_loading = False
        
        # Configurar interfaz
        self._setup_main_layout()
        self._setup_components()
        self._connect_signals()
        
        # Aplicar tema moderno
        ModernComponents.apply_modern_theme(self, self.theme)
    
    def _setup_main_layout(self):
        """Configurar layout principal."""
        # Layout principal vertical
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Header del módulo
        self._create_header()
        
        # Área de contenido con scroll
        self._create_content_area()
        
        # Barra de estado
        self._create_status_bar()
        
        # Overlay de carga
        self._create_loading_overlay()
    
    def _create_header(self):
        """Crear header del módulo."""
        self.header = QWidget()
        self.header.setFixedHeight(80)
        self.header.setStyleSheet(f"""
            QWidget {{
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 {self.theme.get_color('primary')},
                    stop: 1 {self.theme.get_color('accent')}
                );
                border-bottom: 1px solid {self.theme.get_color('border')};
            }}
        """)
        
        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(24, 16, 24, 16)
        header_layout.setSpacing(16)
        
        # Título del módulo
        self.module_title = QLabel(self.module_name or "Módulo")
        self.module_title.setStyleSheet(f"""
            QLabel {{
                font-size: 24px;
                font-weight: 700;
                color: {self.theme.get_color('text_inverse')};
            }}
        """)
        header_layout.addWidget(self.module_title)
        
        # Espaciador
        header_layout.addStretch()
        
        # Botones de acción del header
        self.header_buttons = []
        
        # Botón de actualizar
        refresh_button = ModernButton("🔄", "secondary")
        refresh_button.setMaximumWidth(40)
        refresh_button.clicked.connect(self.refresh_data)
        refresh_button.setStyleSheet(f"""
            QPushButton {{
                background: rgba(255, 255, 255, 0.2);
                color: {self.theme.get_color('text_inverse')};
                border: 1px solid rgba(255, 255, 255, 0.3);
            }}
            
            QPushButton:hover {{
                background: rgba(255, 255, 255, 0.3);
            }}
        """)
        header_layout.addWidget(refresh_button)
        self.header_buttons.append(refresh_button)
        
        # Botón de configuración
        settings_button = ModernButton("⚙️", "secondary")
        settings_button.setMaximumWidth(40)
        settings_button.clicked.connect(self.show_settings)
        settings_button.setStyleSheet(f"""
            QPushButton {{
                background: rgba(255, 255, 255, 0.2);
                color: {self.theme.get_color('text_inverse')};
                border: 1px solid rgba(255, 255, 255, 0.3);
            }}
            
            QPushButton:hover {{
                background: rgba(255, 255, 255, 0.3);
            }}
        """)
        header_layout.addWidget(settings_button)
        self.header_buttons.append(settings_button)
        
        self.main_layout.addWidget(self.header)
    
    def _create_content_area(self):
        """Crear área de contenido principal."""
        # Splitter para dividir contenido
        self.content_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Panel lateral izquierdo (opcional)
        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(250)
        self.sidebar.setStyleSheet(f"""
            QWidget {{
                background: {self.theme.get_color('surface')};
                border-right: 1px solid {self.theme.get_color('border')};
            }}
        """)
        
        # Layout del sidebar
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setContentsMargins(16, 16, 16, 16)
        self.sidebar_layout.setSpacing(12)
        
        # Título del sidebar
        sidebar_title = QLabel("Panel de Control")
        sidebar_title.setStyleSheet(f"""
            QLabel {{
                font-size: 16px;
                font-weight: 600;
                color: {self.theme.get_color('text_primary')};
                margin-bottom: 8px;
            }}
        """)
        self.sidebar_layout.addWidget(sidebar_title)
        
        # Espaciador para contenido personalizado del sidebar
        self.sidebar_content = QWidget()
        self.sidebar_content_layout = QVBoxLayout(self.sidebar_content)
        self.sidebar_content_layout.setContentsMargins(0, 0, 0, 0)
        self.sidebar_layout.addWidget(self.sidebar_content)
        
        # Espaciador al final
        self.sidebar_layout.addStretch()
        
        # Área de contenido principal con scroll
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Widget de contenido scrolleable
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(24, 24, 24, 24)
        self.content_layout.setSpacing(16)
        
        self.scroll_area.setWidget(self.content_widget)
        
        # Añadir al splitter
        self.content_splitter.addWidget(self.sidebar)
        self.content_splitter.addWidget(self.scroll_area)
        
        # Configurar proporciones del splitter
        self.content_splitter.setStretchFactor(0, 0)  # Sidebar fijo
        self.content_splitter.setStretchFactor(1, 1)  # Contenido expandible
        
        self.main_layout.addWidget(self.content_splitter)
        
        # El sidebar está oculto por defecto
        self.sidebar.hide()
    
    def _create_status_bar(self):
        """Crear barra de estado."""
        self.status_bar = ModernStatusBar(self)
        self.main_layout.addWidget(self.status_bar)
    
    def _create_loading_overlay(self):
        """Crear overlay de carga."""
        self.loading_overlay = LoadingOverlay(self)
    
    def _setup_components(self):
        """Configurar componentes específicos del módulo."""
        # Dashboard de métricas rápidas
        self._create_quick_stats()
        
        # Área de contenido principal (tabs)
        self._create_main_content()
        
        # Panel de acciones rápidas
        self._create_quick_actions()
    
    def _create_quick_stats(self):
        """Crear dashboard de estadísticas rápidas."""
        stats_container = QWidget()
        stats_layout = QHBoxLayout(stats_container)
        stats_layout.setContentsMargins(0, 0, 0, 0)
        stats_layout.setSpacing(16)
        
        # Estadísticas por defecto (se pueden personalizar)
        self.stat_cards = []
        
        # Total de registros
        total_card = ModernComponents.create_stats_card(
            "Total Registros", "0", "En el sistema"
        )
        stats_layout.addWidget(total_card)
        self.stat_cards.append(total_card)
        
        # Registros activos
        active_card = ModernComponents.create_stats_card(
            "Activos", "0", "Registros activos"
        )
        stats_layout.addWidget(active_card)
        self.stat_cards.append(active_card)
        
        # Última actualización
        updated_card = ModernComponents.create_stats_card(
            "Actualización", "--", "Última sincronización"
        )
        stats_layout.addWidget(updated_card)
        self.stat_cards.append(updated_card)
        
        # Rendimiento
        if CACHE_AVAILABLE:
            performance_card = ModernComponents.create_stats_card(
                "Rendimiento", "--", "Cache hit ratio"
            )
            stats_layout.addWidget(performance_card)
            self.stat_cards.append(performance_card)
        
        stats_layout.addStretch()
        
        self.content_layout.addWidget(stats_container)
        self.widgets['stats_container'] = stats_container
    
    def _create_main_content(self):
        """Crear área de contenido principal con tabs."""
        self.main_tabs = ModernComponents.create_tab_widget()
        
        # Tab por defecto
        default_tab = QWidget()
        default_layout = QVBoxLayout(default_tab)
        default_layout.setContentsMargins(16, 16, 16, 16)
        
        # Mensaje de bienvenida
        welcome_label = QLabel(f"Bienvenido al módulo {self.module_name}")
        welcome_label.setStyleSheet(f"""
            QLabel {{
                font-size: 18px;
                font-weight: 500;
                color: {self.theme.get_color('text_secondary')};
                text-align: center;
                padding: 40px;
            }}
        """)
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        default_layout.addWidget(welcome_label)
        
        self.main_tabs.addTab(default_tab, "📋 Principal")
        
        self.content_layout.addWidget(self.main_tabs)
        self.widgets['main_tabs'] = self.main_tabs
    
    def _create_quick_actions(self):
        """Crear panel de acciones rápidas."""
        actions_card = ModernComponents.create_card("Acciones Rápidas")
        
        # Botones de acción por defecto
        default_actions = [
            {'text': '➕ Nuevo', 'type': 'primary', 'callback': self.create_new_record},
            {'text': '📊 Reportes', 'type': 'secondary', 'callback': self.show_reports},
            {'text': '📤 Exportar', 'type': 'secondary', 'callback': self.export_data},
            {'text': '🔧 Configurar', 'type': 'ghost', 'callback': self.show_settings}
        ]
        
        actions_panel = ModernComponents.create_button_panel(default_actions)
        actions_card.add_content(actions_panel)
        
        self.content_layout.addWidget(actions_card)
        self.widgets['actions_card'] = actions_card
    
    def _connect_signals(self):
        """Conectar señales internas."""
        # Conectar señales de estado
        self.status_changed.connect(self.status_bar.set_status)
        self.error_occurred.connect(self._handle_error)
        self.data_updated.connect(self._handle_data_update)
    
    def resizeEvent(self, event):
        """Manejar redimensionamiento."""
        super().resizeEvent(event)
        
        # Redimensionar overlay de carga
        if hasattr(self, 'loading_overlay'):
            self.loading_overlay.resize(self.size())
    
    # Métodos públicos para personalización
    
    def set_module_name(self, name: str):
        """Establecer nombre del módulo."""
        self.module_name = name
        self.module_title.setText(name)
    
    def add_sidebar_widget(self, widget: QWidget):
        """Añadir widget al sidebar."""
        self.sidebar_content_layout.addWidget(widget)
        self.sidebar.show()
    
    def add_tab(self, widget: QWidget, title: str, icon: Optional[QIcon] = None):
        """Añadir nueva pestaña."""
        if icon:
            self.main_tabs.addTab(widget, icon, title)
        else:
            self.main_tabs.addTab(widget, title)
    
    def update_stat_card(self, index: int, title: str, value: str, 
                        subtitle: str = "", trend: str = ""):
        """Actualizar tarjeta de estadísticas."""
        if 0 <= index < len(self.stat_cards):
            # Recrear la tarjeta con nuevos valores
            old_card = self.stat_cards[index]
            new_card = ModernComponents.create_stats_card(title, value, subtitle, trend)
            
            # Reemplazar en layout
            layout = old_card.parent().layout()
            layout.replaceWidget(old_card, new_card)
            old_card.deleteLater()
            self.stat_cards[index] = new_card
    
    def show_loading(self, message: str = "Cargando..."):
        """Mostrar estado de carga."""
        self.is_loading = True
        self.loading_overlay.show_loading(message)
        self.status_changed.emit(message, "info")
    
    def hide_loading(self):
        """Ocultar estado de carga."""
        self.is_loading = False
        self.loading_overlay.hide_loading()
        self.status_changed.emit("Listo", "success")
    
    def show_sidebar(self, show: bool = True):
        """Mostrar/ocultar sidebar."""
        if show:
            self.sidebar.show()
        else:
            self.sidebar.hide()
    
    def toggle_dark_mode(self):
        """Alternar modo oscuro."""
        from .modern_components import toggle_dark_mode
        toggle_dark_mode()
        self.theme = get_current_theme()
        ModernComponents.apply_modern_theme(self, self.theme)
    
    # Métodos virtuales para override en subclases
    
    def refresh_data(self):
        """Actualizar datos del módulo."""
        self.show_loading("Actualizando datos...")
        
        # Simular carga
        QTimer.singleShot(1000, lambda: self.hide_loading())
        
        logger.info(f"Datos actualizados en módulo {self.module_name}")
    
    def create_new_record(self):
        """Crear nuevo registro."""
        self.status_changed.emit("Función de creación no implementada", "warning")
    
    def show_reports(self):
        """Mostrar reportes."""
        self.status_changed.emit("Función de reportes no implementada", "warning")
    
    def export_data(self):
        """Exportar datos."""
        self.status_changed.emit("Función de exportación no implementada", "warning")
    
    def show_settings(self):
        """Mostrar configuración."""
        self.status_changed.emit("Función de configuración no implementada", "warning")
    
    # Métodos de manejo de eventos internos
    
    def _handle_error(self, error_message: str):
        """Manejar errores."""
        self.hide_loading()
        logger.error(f"Error en módulo {self.module_name}: {error_message}")
    
    def _handle_data_update(self, data: Dict[str, Any]):
        """Manejar actualización de datos."""
        self.data.update(data)
        self.hide_loading()
        
        # Actualizar estadísticas automáticamente
        self._update_automatic_stats(data)
    
    def _update_automatic_stats(self, data: Dict[str, Any]):
        """Actualizar estadísticas automáticamente."""
        # Estadísticas básicas automáticas
        if 'total_records' in data:
            self.update_stat_card(0, "Total Registros", str(data['total_records']), "En el sistema")
        
        if 'active_records' in data:
            self.update_stat_card(1, "Activos", str(data['active_records']), "Registros activos")
        
        # Timestamp de actualización
        from datetime import datetime
        now = datetime.now().strftime("%H:%M")
        self.update_stat_card(2, "Actualización", now, "Última sincronización")
        
        # Estadísticas de cache
        if CACHE_AVAILABLE and len(self.stat_cards) > 3:
            try:
                monitor = get_performance_monitor()
                stats = monitor.get_performance_summary(hours=1)
                hit_ratio = stats.get('cache_hit_rate', 0)
                self.update_stat_card(3, "Rendimiento", f"{hit_ratio}%", "Cache hit ratio")
            except Exception as e:
                logger.error(f"Error obteniendo stats de cache: {e}")


# Ejemplo de uso específico para un módulo
class ExampleModuleView(EnhancedBaseModuleView):
    """Ejemplo de implementación específica de módulo."""
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__("Ejemplo de Módulo", parent)
        self._setup_specific_content()
    
    def _setup_specific_content(self):
        """Configurar contenido específico del módulo."""
        
        # Tab de datos
        data_tab = QWidget()
        data_layout = QVBoxLayout(data_tab)
        
        # Tabla de ejemplo
        table = ModernComponents.create_table(0, 4, ['ID', 'Nombre', 'Estado', 'Fecha'])
        data_layout.addWidget(table)
        
        self.add_tab(data_tab, "📊 Datos")
        
        # Tab de configuración
        config_tab = QWidget()
        config_layout = QVBoxLayout(config_tab)
        
        config_card = ModernComponents.create_card("Configuración del Módulo")
        
        # Controles de configuración
        search_box = ModernComponents.create_search_box("Buscar configuración...")
        config_card.add_content(search_box)
        
        config_layout.addWidget(config_card)
        
        self.add_tab(config_tab, "⚙️ Configuración")
    
    def refresh_data(self):
        """Implementación específica de actualización."""
        self.show_loading("Cargando datos del ejemplo...")
        
        # Simular carga de datos
        def finish_loading():
            # Simular datos actualizados
            fake_data = {
                'total_records': 156,
                'active_records': 142,
                'last_update': '2025-08-23 15:30:00'
            }
            
            self.data_updated.emit(fake_data)
        
        QTimer.singleShot(2000, finish_loading)


if __name__ == '__main__':
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # Crear ventana de ejemplo
    window = ExampleModuleView()
    window.setWindowTitle("Vista Base Mejorada - Ejemplo")
    window.setGeometry(100, 100, 1200, 800)
    window.show()
    
    sys.exit(app.exec())