"""
Dashboard Premium - Rexus.app v2.0.0

Dashboard moderno y profesional con estadísticas en tiempo real,
accesos rápidos inteligentes y diseño premium.
"""

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QFrame, QScrollArea,
    QGroupBox, QProgressBar, QTabWidget
)

import datetime


class MetricCard(QFrame):
    """Tarjeta de métrica moderna con animaciones."""

    def __init__(self,
titulo,
        valor,
        tendencia=None,
        color="#3b82f6",
        icono=None):
        super().__init__()
        self.titulo = titulo
        self.valor_actual = valor
        self.color = color

        self.setup_ui()
        self.setup_styles()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(20, 15, 20, 15)

        # Header con icono
        header_layout = QHBoxLayout()

        # Título
        self.titulo_label = QLabel(self.titulo)
        self.titulo_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                font-weight: 600;
                color: #64748b;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
        """)

        header_layout.addWidget(self.titulo_label)
        header_layout.addStretch()

        layout.addLayout(header_layout)

        # Valor principal
        self.valor_label = QLabel(str(self.valor_actual))
        self.valor_label.setStyleSheet(f"""
            QLabel {{
                font-size: 28px;
                font-weight: 700;
                color: {self.color};
                margin: 8px 0;
            }}
        """)
        layout.addWidget(self.valor_label)

        # Tendencia (opcional)
        self.tendencia_label = QLabel("↗ +12% vs mes anterior")
        self.tendencia_label.setStyleSheet("""
            QLabel {
                font-size: 11px;
                color: #16a34a;
                background-color: rgba(22, 163, 74, 0.1);
                padding: 4px 8px;
                border-radius: 4px;
            }
        """)
        layout.addWidget(self.tendencia_label)

    def setup_styles(self):
        self.setStyleSheet(f"""
            MetricCard {{
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                border-left: 4px solid {self.color};
            }}
            MetricCard:hover {{
                border-color: {self.color};
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(0,0,0,0.1);
            }}
        """)

    def actualizar_valor(self, nuevo_valor):
        """Actualiza el valor de la métrica."""
        self.valor_actual = nuevo_valor
        self.valor_label.setText(str(nuevo_valor))


class QuickActionButton(QPushButton):
    """Botón de acción rápida con diseño premium."""

    def __init__(self, titulo, descripcion, icono=None, color="#3b82f6"):
        super().__init__()
        self.titulo = titulo
        self.descripcion = descripcion
        self.color = color

        self.setup_ui()
        self.setup_styles()

    def setup_ui(self):
        self.setFixedHeight(80)
        self.setText(f"[ROCKET] {self.titulo}\n{self.descripcion}")
        self.setToolTip(f"Acceso rápido a {self.titulo}")

    def setup_styles(self):
        self.setStyleSheet(f"""
            QuickActionButton {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 {self.color}, stop: 1 {self._darken_color(self.color)});
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 12px;
                font-weight: 600;
                text-align: left;
                padding: 12px 16px;
            }}
            QuickActionButton:hover {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 {self._lighten_color(self.color)}, stop: 1 {self.color});
                transform: translateY(-2px);
            }}
            QuickActionButton:pressed {{
                background-color: {self._darken_color(self.color)};
                transform: translateY(0px);
            }}
        """)

    def _lighten_color(self, color):
        """Aclara un color hexadecimal."""
        return "#4f46e5" if color == "#3b82f6" else color

    def _darken_color(self, color):
        """Oscurece un color hexadecimal."""
        return "#1e40af" if color == "#3b82f6" else color


class ActivityFeed(QFrame):
    """Feed de actividad reciente del sistema."""

    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_styles()
        self.cargar_actividades()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        # Header
        header = QLabel("[CHART] Actividad Reciente")
        header.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: 700;
                color: #1e293b;
                margin-bottom: 8px;
            }
        """)
        layout.addWidget(header)

        # Lista de actividades
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self.actividades_widget = QWidget()
        self.actividades_layout = QVBoxLayout(self.actividades_widget)

        self.scroll_area.setWidget(self.actividades_widget)
        layout.addWidget(self.scroll_area)

    def setup_styles(self):
        self.setStyleSheet("""
            ActivityFeed {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)

    def cargar_actividades(self):
        """Carga las actividades recientes."""
        actividades = [
            ("[OK]", "Pedido PED-001 completado", "Hace 5 min", "#16a34a"),
            ("📦",
"Nuevo producto agregado al inventario",
                "Hace 12 min",
                "#3b82f6"),
            ("👤", "Usuario 'jperez' inició sesión", "Hace 18 min", "#6366f1"),
            ("[TOOL]",
"Mantenimiento preventivo programado",
                "Hace 1 hora",
                "#f59e0b"),
            ("[CHART]",
"Reporte mensual generado",
                "Hace 2 horas",
                "#8b5cf6"),
        ]

        for icono, texto, tiempo, color in actividades:
            self.agregar_actividad(icono, texto, tiempo, color)

    def agregar_actividad(self, icono, texto, tiempo, color):
        """Agrega una actividad al feed."""
        item = QFrame()
        item.setFixedHeight(50)

        layout = QHBoxLayout(item)
        layout.setContentsMargins(12, 8, 12, 8)

        # Icono
        icono_label = QLabel(icono)
        icono_label.setStyleSheet(f"""
            QLabel {{
                background-color: {color};
                color: white;
                border-radius: 15px;
                padding: 6px;
                font-size: 12px;
                min-width: 30px;
                max-width: 30px;
                text-align: center;
            }}
        """)
        layout.addWidget(icono_label)

        # Contenido
        content_layout = QVBoxLayout()

        texto_label = QLabel(texto)
        texto_label.setStyleSheet("""
            QLabel {
                font-size: 13px;
                font-weight: 500;
                color: #1e293b;
            }
        """)
        content_layout.addWidget(texto_label)

        tiempo_label = QLabel(tiempo)
        tiempo_label.setStyleSheet("""
            QLabel {
                font-size: 11px;
                color: #64748b;
            }
        """)
        content_layout.addWidget(tiempo_label)

        layout.addLayout(content_layout)
        layout.addStretch()

        item.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border-bottom: 1px solid #f1f5f9;
            }
            QFrame:hover {
                background-color: rgba(59, 130, 246, 0.05);
                border-radius: 6px;
            }
        """)

        self.actividades_layout.addWidget(item)


class PremiumDashboard(QWidget):
    """Dashboard premium con diseño moderno y funcionalidad completa."""

    # Señales para navegación
    navegar_modulo = pyqtSignal(str)

    def __init__(self, user_data=None):
        super().__init__()
        self.user_data = user_data or {}
        self.setup_ui()
        self.setup_timer()

    def setup_ui(self):
        """Configura la interfaz del dashboard."""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header premium
        self.setup_header(layout)

        # Métricas principales
        self.setup_metricas(layout)

        # Contenido principal en tabs
        self.setup_contenido_principal(layout)

        # Footer con información del sistema
        self.setup_footer(layout)

        self.aplicar_estilos()

    def setup_header(self, layout):
        """Configura el header premium."""
        header = QFrame()
        header.setFixedHeight(80)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(24, 16, 24, 16)

        # Información del usuario
        user_info = QVBoxLayout()

        bienvenida = QLabel(f"¡Bienvenido, {self.user_data.get('username', 'Usuario')}! 👋")
        bienvenida.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: 700;
                color: #1e293b;
                margin-bottom: 4px;
            }
        """)
        user_info.addWidget(bienvenida)

        fecha = QLabel(datetime.datetime.now().strftime("%A, %d de %B de %Y"))
        fecha.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #64748b;
                font-weight: 500;
            }
        """)
        user_info.addWidget(fecha)

        header_layout.addLayout(user_info)
        header_layout.addStretch()

        # Estado del sistema
        estado = QLabel("🟢 Sistema Operativo")
        estado.setStyleSheet("""
            QLabel {
                background-color: rgba(22, 163, 74, 0.1);
                color: #16a34a;
                padding: 8px 16px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: 600;
            }
        """)
        header_layout.addWidget(estado)

        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #ffffff, stop: 1 #f8fafc);
                border-radius: 12px;
                border: 1px solid #e2e8f0;
            }
        """)

        layout.addWidget(header)

    def setup_metricas(self, layout):
        """Configura las métricas principales."""
        metricas_frame = QFrame()
        metricas_layout = QGridLayout(metricas_frame)
        metricas_layout.setSpacing(16)
        metricas_layout.setContentsMargins(0, 0, 0, 0)

        # Datos de métricas
        metricas_data = [
            ("Pedidos Activos", "24", "#3b82f6"),
            ("Inventario", "1,245", "#16a34a"),
            ("Obras en Curso", "8", "#f59e0b"),
            ("Facturación Mensual", "$125,400", "#8b5cf6"),
            ("Usuarios Activos", "12", "#ef4444"),
            ("Alertas", "3", "#f97316")
        ]

        self.metric_cards = {}

        for i, (titulo, valor, color) in enumerate(metricas_data):
            card = MetricCard(titulo, valor, color=color)
            row, col = divmod(i, 3)
            metricas_layout.addWidget(card, row, col)
            self.metric_cards[titulo.lower().replace(" ", "_")] = card

        layout.addWidget(metricas_frame)

    def setup_contenido_principal(self, layout):
        """Configura el contenido principal con tabs."""
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                background-color: white;
            }
            QTabWidget::tab-bar {
                alignment: left;
            }
            QTabBar::tab {
                background-color: #f1f5f9;
                border: 1px solid #e2e8f0;
                padding: 12px 24px;
                margin-right: 2px;
                font-weight: 600;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom-color: white;
                color: #3b82f6;
            }
            QTabBar::tab:hover {
                background-color: #e2e8f0;
            }
        """)

        # Tab 1: Accesos Rápidos
        self.setup_accesos_rapidos_tab(tabs)

        # Tab 2: Actividad Reciente
        self.setup_actividad_tab(tabs)

        # Tab 3: Estadísticas
        self.setup_estadisticas_tab(tabs)

        layout.addWidget(tabs)

    def setup_accesos_rapidos_tab(self, tabs):
        """Configura la pestaña de accesos rápidos."""
        accesos_widget = QWidget()
        accesos_layout = QGridLayout(accesos_widget)
        accesos_layout.setSpacing(16)
        accesos_layout.setContentsMargins(20, 20, 20, 20)

        # Botones de acceso rápido
        accesos = [
            ("Nuevo Pedido",
"Crear pedido rápidamente",
                "#3b82f6",
                "Pedidos"),
            ("Gestionar Inventario",
"Actualizar stock y productos",
                "#16a34a",
                "Inventario"),
            ("Ver Obras", "Administrar proyectos", "#f59e0b", "Obras"),
            ("Configurar Sistema",
"Ajustes y preferencias",
                "#8b5cf6",
                "Configuración"),
            ("Generar Reportes",
"Análisis y estadísticas",
                "#ef4444",
                "Administración"),
            ("Gestión de Usuarios",
"Administrar permisos",
                "#6366f1",
                "Usuarios")
        ]

        for i, (titulo, desc, color, modulo) in enumerate(accesos):
            btn = QuickActionButton(titulo, desc, color=color)
            btn.clicked.connect(lambda checked, m=modulo: self.navegar_modulo.emit(m))
            row, col = divmod(i, 3)
            accesos_layout.addWidget(btn, row, col)

        tabs.addTab(accesos_widget, "[ROCKET] Accesos Rápidos")

    def setup_actividad_tab(self, tabs):
        """Configura la pestaña de actividad."""
        actividad_widget = QWidget()
        actividad_layout = QHBoxLayout(actividad_widget)
        actividad_layout.setContentsMargins(0, 0, 0, 0)

        # Feed de actividades
        activity_feed = ActivityFeed()
        actividad_layout.addWidget(activity_feed, 2)

        # Panel lateral con estadísticas rápidas
        stats_panel = self.crear_panel_estadisticas_laterales()
        actividad_layout.addWidget(stats_panel, 1)

        tabs.addTab(actividad_widget, "[CHART] Actividad Reciente")

    def setup_estadisticas_tab(self, tabs):
        """Configura la pestaña de estadísticas."""
        stats_widget = QWidget()
        stats_layout = QVBoxLayout(stats_widget)
        stats_layout.setContentsMargins(20, 20, 20, 20)

        # Gráficos de progreso
        progress_group = QGroupBox("📈 Progreso del Sistema")
        progress_layout = QVBoxLayout(progress_group)

        progresos = [
            ("Completitud del Sistema", 95, "#16a34a"),
            ("Migración SQL", 100, "#3b82f6"),
            ("Funcionalidades CRUD", 85, "#f59e0b"),
            ("Testing Cobertura", 88, "#8b5cf6")
        ]

        for nombre, valor, color in progresos:
            item_layout = QHBoxLayout()

            label = QLabel(nombre)
            label.setMinimumWidth(180)
            item_layout.addWidget(label)

            progress = QProgressBar()
            progress.setValue(valor)
            progress.setStyleSheet(f"""
                QProgressBar {{
                    border: 1px solid #e2e8f0;
                    border-radius: 6px;
                    text-align: center;
                    font-weight: 600;
                    height: 20px;
                }}
                QProgressBar::chunk {{
                    background-color: {color};
                    border-radius: 5px;
                }}
            """)
            item_layout.addWidget(progress, 1)

            valor_label = QLabel(f"{valor}%")
            valor_label.setMinimumWidth(50)
            valor_label.setStyleSheet("font-weight: 600;")
            item_layout.addWidget(valor_label)

            progress_layout.addLayout(item_layout)

        stats_layout.addWidget(progress_group)
        stats_layout.addStretch()

        tabs.addTab(stats_widget, "[CHART] Estadísticas")

    def crear_panel_estadisticas_laterales(self):
        """Crea el panel de estadísticas laterales."""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                margin-left: 16px;
            }
        """)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 16, 16, 16)

        # Header
        header = QLabel("[CHART] Resumen Rápido")
        header.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: 700;
                color: #1e293b;
                margin-bottom: 16px;
            }
        """)
        layout.addWidget(header)

        # Estadísticas
        stats = [
            ("Uptime del Sistema", "99.9%", "#16a34a"),
            ("Último Backup", "Hace 2h", "#3b82f6"),
            ("Espacio en Disco", "76% libre", "#f59e0b"),
            ("Conexiones DB", "8/20", "#8b5cf6")
        ]

        for nombre, valor, color in stats:
            stat_frame = QFrame()
            stat_layout = QVBoxLayout(stat_frame)
            stat_layout.setContentsMargins(12, 8, 12, 8)

            nombre_label = QLabel(nombre)
            nombre_label.setStyleSheet("font-size: 12px; color: #64748b; font-weight: 500;")
            stat_layout.addWidget(nombre_label)

            valor_label = QLabel(valor)
            valor_label.setStyleSheet(f"font-size: 14px; color: {color}; font-weight: 600;")
            stat_layout.addWidget(valor_label)

            stat_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: rgba{self._hex_to_rgba(color, 0.1)};
                    border-left: 3px solid {color};
                    border-radius: 6px;
                    margin-bottom: 8px;
                }}
            """)

            layout.addWidget(stat_frame)

        layout.addStretch()
        return panel

    def setup_footer(self, layout):
        """Configura el footer."""
        footer = QFrame()
        footer.setFixedHeight(40)
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(0, 8, 0, 8)

        version_label = QLabel("Rexus.app v2.0.0 - Sistema Completamente Optimizado")
        version_label.setStyleSheet("""
            QLabel {
                color: #64748b;
                font-size: 11px;
                font-weight: 500;
            }
        """)

        footer_layout.addWidget(version_label)
        footer_layout.addStretch()

        status_label = QLabel("🟢 Todos los sistemas operativos")
        status_label.setStyleSheet("""
            QLabel {
                color: #16a34a;
                font-size: 11px;
                font-weight: 600;
            }
        """)
        footer_layout.addWidget(status_label)

        layout.addWidget(footer)

    def aplicar_estilos(self):
        """Aplica estilos generales al dashboard."""
        self.setStyleSheet("""
            PremiumDashboard {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #f8fafc, stop: 1 #e2e8f0);
            }
        """)

    def setup_timer(self):
        """Configura el timer para actualizaciones automáticas."""
        self.timer = QTimer()
        self.timer.timeout.connect(self.actualizar_metricas)
        self.timer.start(30000)  # Actualizar cada 30 segundos

    def actualizar_metricas(self):
        """Actualiza las métricas en tiempo real."""
        # Simulación de actualización de métricas
        import random

        if "pedidos_activos" in self.metric_cards:
            nuevo_valor = random.randint(20, 30)
            self.metric_cards["pedidos_activos"].actualizar_valor(nuevo_valor)

        if "inventario" in self.metric_cards:
            nuevo_valor = random.randint(1200, 1300)
            self.metric_cards["inventario"].actualizar_valor(f"{nuevo_valor:,}")

    def _hex_to_rgba(self, hex_color, alpha):
        """Convierte color hex a rgba."""
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        return f"({r}, {g}, {b}, {alpha})"
