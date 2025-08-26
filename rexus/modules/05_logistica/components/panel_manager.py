"""
Panel Manager para el módulo de Logística

Maneja la creación de paneles de UI (gráficos, métricas, filtros, etc.).
Extraído de view.py para mejorar la mantenibilidad.
"""


import logging
logger = logging.getLogger(__name__)

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QComboBox, QProgressBar,
    QFrame, QScrollArea, QGroupBox
)
from PyQt6.QtCore import Qt

from rexus.ui.components.base_components import (
    RexusButton, RexusLineEdit, RexusComboBox, RexusGroupBox
)

class LogisticaPanelManager:
    """Gestor de paneles UI para el módulo de logística."""

    def __init__(self, parent_view):
        """Inicializa el gestor de paneles.
        
        Args:
            parent_view: Vista principal de logística
        """
        self.parent_view = parent_view

    def crear_panel_graficos_mejorado(self) -> QWidget:
        """Crea el panel de gráficos mejorado."""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Título
        titulo = QLabel("[CHART] Gráficos y Análisis")
        titulo.setStyleSheet("font-weight: bold; font-size: 14px; margin: 10px;")
        layout.addWidget(titulo)

        # Placeholder para gráficos
        placeholder = QLabel("Gráficos de rendimiento logístico\n(Integración pendiente)")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder.setStyleSheet("color: #666; font-style: italic; padding: 20px;")
        layout.addWidget(placeholder)

        return panel

    def crear_panel_metricas_compacto(self) -> QWidget:
        """Crea el panel de métricas compacto."""
        panel = QWidget()
        layout = QGridLayout(panel)

        # Métricas demo
        metricas = [
            ("🚚 Transportes Activos", "12"),
            ("[PACKAGE] Entregas Hoy", "28"),
            ("⏱️ Tiempo Promedio", "2.5h"),
            ("[CHECK] Eficiencia", "94%")
        ]

        for i, (etiqueta, valor) in enumerate(metricas):
            # Widget de métrica
            metrica_widget = QFrame()
            metrica_widget.setFrameStyle(QFrame.Shape.StyledPanel)
            metrica_layout = QVBoxLayout(metrica_widget)

            # Etiqueta
            lbl_etiqueta = QLabel(etiqueta)
            lbl_etiqueta.setStyleSheet("font-size: 12px; color: #666;")
            metrica_layout.addWidget(lbl_etiqueta)

            # Valor
            lbl_valor = QLabel(valor)
            lbl_valor.setStyleSheet("font-size: 18px; font-weight: bold; color: #2196F3;")
            metrica_layout.addWidget(lbl_valor)

            # Agregar al grid
            layout.addWidget(metrica_widget, i // 2, i % 2)

        return panel

    def crear_panel_resumen_optimizado(self) -> QWidget:
        """Crea el panel de resumen optimizado."""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Título
        titulo = QLabel("[CLIPBOARD] Resumen del Día")
        titulo.setStyleSheet("font-weight: bold; font-size: 14px; margin: 10px;")
        layout.addWidget(titulo)

        # Información de resumen
        resumen_info = [
            "• 28 entregas programadas para hoy",
            "• 12 transportes disponibles",
            "• 3 rutas optimizadas activas",
            "• 2 servicios en seguimiento especial"
        ]

        for info in resumen_info:
            lbl = QLabel(info)
            lbl.setStyleSheet("margin: 5px; padding: 5px;")
            layout.addWidget(lbl)

        # Barra de progreso del día
        lbl_progreso = QLabel("Progreso del día:")
        layout.addWidget(lbl_progreso)
        
        progreso = QProgressBar()
        progreso.setValue(67)
        progreso.setStyleSheet("""
            QProgressBar {
                border: 2px solid grey;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #2196F3;
                border-radius: 3px;
            }
        """)
        layout.addWidget(progreso)

        layout.addStretch()
        return panel

    def crear_panel_filtros_servicios_optimizado(self) -> QWidget:
        """Crea el panel de filtros de servicios optimizado."""
        panel = RexusGroupBox("[SEARCH] Filtros de Servicios")
        layout = QVBoxLayout(panel)

        # Filtro por tipo
        layout.addWidget(QLabel("Tipo de Servicio:"))
        combo_tipo = RexusComboBox()
        combo_tipo.addItems(["Todos", "Entrega", "Recolección", "Transferencia"])
        layout.addWidget(combo_tipo)

        # Filtro por estado
        layout.addWidget(QLabel("Estado:"))
        combo_estado = RexusComboBox()
        combo_estado.addItems(["Todos", "Pendiente", "En Tránsito", "Completado", "Cancelado"])
        layout.addWidget(combo_estado)

        # Filtro por zona
        layout.addWidget(QLabel("Zona:"))
        combo_zona = RexusComboBox()
        combo_zona.addItems(["Todas", "Norte", "Sur", "Este", "Oeste", "Centro"])
        layout.addWidget(combo_zona)

        # Botones de acción
        btn_aplicar = RexusButton("Aplicar Filtros")
        btn_limpiar = RexusButton("Limpiar")
        
        botones_layout = QHBoxLayout()
        botones_layout.addWidget(btn_aplicar)
        botones_layout.addWidget(btn_limpiar)
        layout.addLayout(botones_layout)

        layout.addStretch()
        return panel

    def crear_panel_control_mapa_optimizado(self) -> QWidget:
        """Crea el panel de control del mapa optimizado."""
        panel = RexusGroupBox("🗺️ Control de Mapa")
        layout = QVBoxLayout(panel)

        # Controles de vista
        layout.addWidget(QLabel("Vista del Mapa:"))
        combo_vista = RexusComboBox()
        combo_vista.addItems(["Satelital", "Calles", "Híbrido", "Terreno"])
        layout.addWidget(combo_vista)

        # Controles de zoom
        layout.addWidget(QLabel("Zoom:"))
        zoom_layout = QHBoxLayout()
        btn_zoom_menos = RexusButton("-")
        btn_zoom_mas = RexusButton("+")
        btn_zoom_menos.setMaximumWidth(30)
        btn_zoom_mas.setMaximumWidth(30)
        zoom_layout.addWidget(btn_zoom_menos)
        zoom_layout.addStretch()
        zoom_layout.addWidget(btn_zoom_mas)
        layout.addLayout(zoom_layout)

        # Capas del mapa
        layout.addWidget(QLabel("Capas:"))
        
        # Checkboxes para capas (simulados con botones por simplicidad)
        capas = ["Rutas", "Transportes", "Entregas", "Zonas"]
        for capa in capas:
            btn_capa = RexusButton(f"🔲 {capa}")
            btn_capa.setCheckable(True)
            btn_capa.setChecked(True)
            layout.addWidget(btn_capa)

        # Botón de actualizar
        btn_actualizar = RexusButton("🔄 Actualizar Mapa")
        layout.addWidget(btn_actualizar)

        layout.addStretch()
        return panel

    def crear_widget_direcciones_mejorado(self) -> QWidget:
        """Crea widget de direcciones mejorado."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Título
        titulo = QLabel("📍 Gestión de Direcciones")
        titulo.setStyleSheet("font-weight: bold; font-size: 14px; margin: 10px;")
        layout.addWidget(titulo)

        # Campos de dirección
        layout.addWidget(QLabel("Dirección de Origen:"))
        self.origen_edit = RexusLineEdit()
        self.origen_edit.setPlaceholderText("Ingrese dirección de origen...")
        layout.addWidget(self.origen_edit)

        layout.addWidget(QLabel("Dirección de Destino:"))
        self.destino_edit = RexusLineEdit()
        self.destino_edit.setPlaceholderText("Ingrese dirección de destino...")
        layout.addWidget(self.destino_edit)

        # Botones de acción
        botones_layout = QHBoxLayout()
        btn_calcular = RexusButton("🧭 Calcular Ruta")
        btn_limpiar = RexusButton("🧹 Limpiar")
        
        botones_layout.addWidget(btn_calcular)
        botones_layout.addWidget(btn_limpiar)
        layout.addLayout(botones_layout)

        # Información de ruta
        self.info_ruta = QLabel("Seleccione origen y destino para calcular ruta")
        self.info_ruta.setStyleSheet("color: #666; font-style: italic; padding: 10px;")
        layout.addWidget(self.info_ruta)

        layout.addStretch()
        return widget

    def get_combo_tipo_servicio(self):
        """Retorna combo de tipo de servicio."""
        combo = RexusComboBox()
        combo.addItems(["Entrega", "Recolección", "Transferencia", "Urgente"])
        return combo

    def get_combo_estado_servicio(self):
        """Retorna combo de estado de servicio.""" 
        combo = RexusComboBox()
        combo.addItems(["Pendiente", "En Tránsito", "Completado", "Cancelado"])
        return combo