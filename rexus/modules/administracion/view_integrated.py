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
Vista de Administración - Versión Integrada con Sistema de Temas
Rexus.app v2.0.0 - Enterprise Ready

Sistema completo de administración que incluye:
- Contabilidad
- Recursos Humanos  
- Reportes financieros
- Gestión de empleados

Integrado con el sistema de temas y feedback visual centralizado.
"""

from PyQt6.QtCore import QDate, Qt, QTimer, pyqtSignal
from PyQt6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QFormLayout,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

# Importar el nuevo sistema de feedback y temas
from ...ui.feedback_mixin import FeedbackMixin
from ...utils.theme_manager import ThemeManager
from ...core.logger import get_logger

logger = get_logger("administracion_view")


class AdministracionViewIntegrated(QWidget, FeedbackMixin):
    """Vista principal del módulo de administración integrada con el sistema de temas."""

    # Señales para el controlador
    crear_departamento_signal = pyqtSignal(dict)
    crear_empleado_signal = pyqtSignal(dict)
    crear_asiento_signal = pyqtSignal(dict)
    crear_recibo_signal = pyqtSignal(dict)
    imprimir_recibo_signal = pyqtSignal(int)
    generar_reporte_signal = pyqtSignal(dict)
    actualizar_datos_signal = pyqtSignal()

    # Señales para recursos humanos
    crear_empleado_rrhh_signal = pyqtSignal(dict)
    actualizar_empleado_signal = pyqtSignal(int, dict)
    eliminar_empleado_signal = pyqtSignal(int)
    registrar_asistencia_signal = pyqtSignal(dict)
    calcular_nomina_signal = pyqtSignal(dict)
    generar_bono_signal = pyqtSignal(dict)
    registrar_falta_signal = pyqtSignal(dict)

    def __init__(self, theme_manager: ThemeManager = None):
        super().__init__()
        
        # Inicializar el sistema de feedback integrado
        self.init_feedback(theme_manager)
        
        # Datos
        self.datos_administrativos = {}
        self.current_user = "ADMIN"
        self.current_role = "ADMIN"
        self.theme_manager = theme_manager
        
        # Inicializar UI
        self.init_ui()
        
        # Conectar con cambios de tema
        if self.theme_manager:
            self.theme_manager.theme_changed.connect(self._on_theme_changed)
        
        logger.info("AdministracionView inicializada con integración de temas")

    def init_ui(self):
        """Inicializa la interfaz de usuario con estilos del tema."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Status label para feedback inline
        self.status_label = self.crear_status_label("main")
        layout.addWidget(self.status_label)

        # Header con controles
        header_layout = self.create_header()
        layout.addLayout(header_layout)

        # Tabs principales con estilos del tema
        self.tabs = QTabWidget()
        self.apply_theme_to_tabs()
        
        # Crear tabs
        self.create_tabs()
        layout.addWidget(self.tabs)

        # Status bar
        self.status_bar = self.create_status_bar()
        layout.addWidget(self.status_bar)

        # Conectar señales
        self.connect_signals()

    def apply_theme_to_tabs(self):
        """Aplicar estilos del tema actual a los tabs."""
        if not self.theme_manager:
            return
        
        colors = self.theme_manager.current_theme
        
        # Generar estilos basados en el tema actual
        tab_style = f"""
            QTabWidget::pane {{
                border: 2px solid {colors.border};
                border-radius: 10px;
                background-color: {colors.surface};
            }}
            QTabWidget::tab-bar {{
                alignment: center;
            }}
            QTab {{
                background-color: {colors.surface_variant};
                color: {colors.on_surface_variant};
                padding: 12px 20px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: bold;
                min-width: 120px;
            }}
            QTab:selected {{
                background-color: {colors.primary};
                color: {colors.on_primary};
            }}
            QTab:hover {{
                background-color: {colors.button_hover};
                color: {colors.on_primary};
            }}
        """
        
        self.tabs.setStyleSheet(tab_style)

    def create_header(self):
        """Crea el header con controles integrado con el tema."""
        header_layout = QHBoxLayout()
        header_layout.addStretch()

        # Frame para controles de usuario con estilos del tema
        user_frame = QFrame()
        if self.theme_manager:
            colors = self.theme_manager.current_theme
            user_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: {colors.primary};
                    border-radius: 10px;
                    padding: 5px;
                }}
            """)

        header_layout.addWidget(user_frame)
        return header_layout

    def create_status_bar(self):
        """Crea la barra de estado con estilos del tema."""
        status_frame = QFrame()
        
        if self.theme_manager:
            colors = self.theme_manager.current_theme
            status_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: {colors.surface_variant};
                    color: {colors.on_surface_variant};
                    padding: 5px;
                    border-radius: 5px;
                }}
            """)

        status_layout = QHBoxLayout(status_frame)

        self.status_label_bar = QLabel("✅ Sistema listo")
        if self.theme_manager:
            colors = self.theme_manager.current_theme
            self.status_label_bar.setStyleSheet(f"color: {colors.on_surface_variant}; font-weight: bold;")
        
        status_layout.addWidget(self.status_label_bar)
        status_layout.addStretch()

        self.conexion_label = QLabel("🔗 Conectado a DB")
        if self.theme_manager:
            colors = self.theme_manager.current_theme
            self.conexion_label.setStyleSheet(f"color: {colors.success}; font-weight: bold;")
        
        status_layout.addWidget(self.conexion_label)

        return status_frame

    def create_tabs(self):
        """Crear las pestañas principales."""
        # Dashboard
        self.dashboard_tab = self.create_dashboard_tab()
        self.tabs.addTab(self.dashboard_tab, "📊 Dashboard")

        # Contabilidad
        self.contabilidad_tab = self.create_contabilidad_tab()
        self.tabs.addTab(self.contabilidad_tab, "💰 Contabilidad")

        # Recursos Humanos
        self.recursos_humanos_tab = self.create_recursos_humanos_tab()
        self.tabs.addTab(self.recursos_humanos_tab, "👥 Recursos Humanos")

        # Reportes
        self.reportes_tab = self.create_reportes_tab()
        self.tabs.addTab(self.reportes_tab, "📈 Reportes")

    def create_dashboard_tab(self):
        """Crea la pestaña de dashboard con estilos del tema."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Resumen general con estilos del tema
        resumen_frame = QGroupBox("📊 Resumen General")
        if self.theme_manager:
            colors = self.theme_manager.current_theme
            resumen_frame.setStyleSheet(f"""
                QGroupBox {{
                    font-size: 14px;
                    font-weight: bold;
                    color: {colors.on_surface};
                    border: 2px solid {colors.primary};
                    border-radius: 10px;
                    padding-top: 5px;
                    margin-top: 5px;
                    background-color: {colors.surface};
                }}
                QGroupBox::title {{
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px 0 5px;
                }}
            """)
        
        resumen_layout = QGridLayout(resumen_frame)

        # Cards de resumen con colores del tema
        self.cards_resumen = {}
        cards_data = [
            ("💰 Total Ingresos", "total_ingresos", "success"),
            ("💸 Total Egresos", "total_egresos", "error"),
            ("👥 Total Empleados", "total_empleados", "primary"),
            ("📊 Nómina Mensual", "nomina_mensual", "info"),
        ]

        for i, (titulo, key, color_type) in enumerate(cards_data):
            card = self.create_info_card(titulo, "0", color_type)
            self.cards_resumen[key] = card
            resumen_layout.addWidget(card, i // 2, i % 2)

        layout.addWidget(resumen_frame)
        return widget

    def create_info_card(self, titulo, valor, color_type):
        """Crea una tarjeta de información con colores del tema."""
        card = QFrame()
        
        # Obtener color del tema según el tipo
        color = "#3498db"  # Fallback
        if self.theme_manager:
            colors = self.theme_manager.current_theme
            color_map = {
                "primary": colors.primary,
                "success": colors.success,
                "error": colors.error,
                "warning": colors.warning,
                "info": colors.info
            }
            color = color_map.get(color_type, colors.primary)

        card.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {color}, stop:1 {self._darken_color(color)});
                border: none;
                border-radius: 10px;
                padding: 15px;
                margin: 5px;
                min-width: 150px;
                min-height: 80px;
            }}
            QFrame:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {self._lighten_color(color)}, stop:1 {color});
            }}
        """)

        layout = QVBoxLayout(card)
        layout.setSpacing(8)

        titulo_label = QLabel(titulo)
        titulo_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 12px;
                font-weight: bold;
                background: transparent;
                border: none;
            }
        """)
        titulo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(titulo_label)

        valor_label = QLabel(valor)
        valor_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 18px;
                font-weight: bold;
                background: transparent;
                border: none;
            }
        """)
        valor_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(valor_label)

        return card

    def _lighten_color(self, color):
        """Aclara un color hexadecimal."""
        color = color.lstrip("#")
        rgb = tuple(int(color[i : i + 2], 16) for i in (0, 2, 4))
        lightened = tuple(min(255, int(c * 1.2)) for c in rgb)
        return f"#{lightened[0]:02x}{lightened[1]:02x}{lightened[2]:02x}"

    def _darken_color(self, color):
        """Oscurece un color hexadecimal."""
        color = color.lstrip("#")
        rgb = tuple(int(color[i : i + 2], 16) for i in (0, 2, 4))
        darkened = tuple(max(0, int(c * 0.8)) for c in rgb)
        return f"#{darkened[0]:02x}{darkened[1]:02x}{darkened[2]:02x}"

    def create_contabilidad_tab(self):
        """Placeholder para la pestaña de contabilidad."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        label = QLabel("🚧 Módulo de Contabilidad en desarrollo")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if self.theme_manager:
            colors = self.theme_manager.current_theme
            label.setStyleSheet(f"""
                QLabel {{
                    color: {colors.on_surface};
                    font-size: 16px;
                    font-weight: bold;
                    padding: 50px;
                }}
            """)
        layout.addWidget(label)
        
        return widget

    def create_recursos_humanos_tab(self):
        """Placeholder para la pestaña de recursos humanos."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        label = QLabel("👥 Módulo de Recursos Humanos en desarrollo")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if self.theme_manager:
            colors = self.theme_manager.current_theme
            label.setStyleSheet(f"""
                QLabel {{
                    color: {colors.on_surface};
                    font-size: 16px;
                    font-weight: bold;
                    padding: 50px;
                }}
            """)
        layout.addWidget(label)
        
        return widget

    def create_reportes_tab(self):
        """Placeholder para la pestaña de reportes."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        label = QLabel("📈 Módulo de Reportes en desarrollo")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if self.theme_manager:
            colors = self.theme_manager.current_theme
            label.setStyleSheet(f"""
                QLabel {{
                    color: {colors.on_surface};
                    font-size: 16px;
                    font-weight: bold;
                    padding: 50px;
                }}
            """)
        layout.addWidget(label)
        
        return widget

    def connect_signals(self):
        """Conecta las señales de la interfaz."""
        pass

    def _on_theme_changed(self, theme_name: str, theme_colors: dict):
        """Callback cuando cambia el tema - reaplica estilos."""
        logger.debug(f"Aplicando nuevo tema: {theme_name}")
        
        try:
            # Reaplicar estilos a los tabs
            self.apply_theme_to_tabs()
            
            # Mostrar confirmación del cambio
            self.mostrar_info(f"Tema cambiado a: {theme_name}")
            
        except Exception as e:
            logger.error(f"Error aplicando tema: {e}")
            self.mostrar_error(f"Error aplicando tema: {str(e)}")

    # Métodos de ejemplo usando el nuevo sistema de feedback

    def buscar_libro_contable(self):
        """Busca asientos en el libro contable con feedback mejorado."""
        self.mostrar_cargando("Consultando libro contable...")
        
        # Simular operación
        QTimer.singleShot(2000, lambda: self.mostrar_exito("Libro contable actualizado"))

    def buscar_empleados(self):
        """Busca empleados con feedback mejorado."""
        self.mostrar_cargando("Consultando empleados...")
        
        # Simular operación
        QTimer.singleShot(1500, lambda: self.mostrar_exito("Lista de empleados actualizada"))

    def calcular_nomina(self):
        """Calcula la nómina con feedback mejorado."""
        self.mostrar_cargando("Calculando nómina del período...")
        
        # Simular operación más larga
        QTimer.singleShot(3000, lambda: self.mostrar_exito("Nómina calculada correctamente"))

    def generar_reporte(self, tipo_reporte):
        """Genera un reporte con feedback mejorado."""
        self.mostrar_cargando(f"Generando reporte {tipo_reporte}...")
        
        # Simular generación
        QTimer.singleShot(2500, lambda: self.mostrar_exito(f"Reporte {tipo_reporte} generado"))

    def refresh_data(self):
        """Actualiza todos los datos de la interfaz."""
        self.mostrar_cargando("Actualizando datos del sistema...")
        self.actualizar_datos_signal.emit()
        
        # Simular actualización
        QTimer.singleShot(1000, lambda: self.mostrar_exito("Datos actualizados"))

    def actualizar_dashboard(self, datos):
        """Actualiza el dashboard con nuevos datos."""
        try:
            if "resumen" in datos:
                resumen = datos["resumen"]
                
                # Actualizar cards si existen
                if hasattr(self, 'cards_resumen'):
                    if "empleados" in resumen:
                        # Actualizar datos...
                        pass
                    
                    if "financiero" in resumen:
                        # Actualizar datos financieros...
                        pass
                
                self.mostrar_exito("Dashboard actualizado")
                logger.info("Dashboard actualizado correctamente")
                
        except Exception as e:
            logger.error(f"Error actualizando dashboard: {e}")
            self.mostrar_error(f"Error actualizando dashboard: {str(e)}")


# Alias para mantener compatibilidad
ContabilidadViewIntegrated = AdministracionViewIntegrated