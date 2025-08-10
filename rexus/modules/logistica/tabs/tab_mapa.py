"""
Pestaña de Mapa para el módulo de Logística

Maneja la visualización de ubicaciones y rutas en el mapa.
"""

from typing import Dict, Any
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout, QLabel, QFrame, QSplitter

from .base_tab import BaseTab
from ..constants import FILTROS_MAPA, ICONS, MESSAGES
from ..styles import FALLBACK_MAP_STYLE
from ..widgets import LogisticaButton, LogisticaGroupBox, FilterPanel


class TabMapa(BaseTab):
    """Pestaña para visualización de mapa y rutas."""
    
    # Señales específicas del mapa
    ubicacion_seleccionada = pyqtSignal(float, float)  # lat, lng
    marcador_agregado = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        self.marcadores = []
        super().__init__("Mapa", ICONS["tabs"]["mapa"], parent)
    
    def init_ui(self):
        """Inicializa la interfaz de la pestaña del mapa."""
        # Splitter principal
        splitter = QSplitter(self)
        
        # Panel de control izquierdo
        self.create_control_panel(splitter)
        
        # Área del mapa derecho
        self.create_map_area(splitter)
        
        # Configurar proporciones del splitter
        splitter.setStretchFactor(0, 1)  # Panel control
        splitter.setStretchFactor(1, 3)  # Área del mapa
        
        self.main_layout.addWidget(splitter)
    
    def create_control_panel(self, parent):
        """Crea el panel de control del mapa."""
        control_widget = LogisticaGroupBox("🗺️ Control de Mapa", parent)
        
        # Filtros del mapa
        filters_config = {"filtro_mapa": FILTROS_MAPA}
        self.filter_panel = FilterPanel(filters_config, self)
        self.filter_panel.filter_changed.connect(self.filtrar_mapa)
        control_widget.add_widget(self.filter_panel)
        
        # Botones de acción
        self.create_map_buttons(control_widget)
        
        # Lista de direcciones/marcadores
        self.create_address_list(control_widget)
        
        parent.addWidget(control_widget)
    
    def create_map_buttons(self, parent):
        """Crea botones de acción del mapa."""
        buttons_layout = QHBoxLayout()
        
        # Botón agregar marcador
        btn_agregar = LogisticaButton(
            "Agregar Marcador", "info", ICONS["buttons"]["agregar_marcador"], self
        )
        btn_agregar.clicked.connect(self.agregar_marcador_mapa)
        buttons_layout.addWidget(btn_agregar)
        
        # Botón limpiar marcadores
        btn_limpiar = LogisticaButton(
            "Limpiar", "secondary", ICONS["buttons"]["limpiar"], self
        )
        btn_limpiar.clicked.connect(self.limpiar_marcadores_mapa)
        buttons_layout.addWidget(btn_limpiar)
        
        # Botón centrar mapa
        btn_centrar = LogisticaButton(
            "Centrar", "info", "🎯", self
        )
        btn_centrar.clicked.connect(self.centrar_mapa)
        buttons_layout.addWidget(btn_centrar)
        
        parent.add_layout(buttons_layout)
    
    def create_address_list(self, parent):
        """Crea lista de direcciones."""
        direcciones_group = LogisticaGroupBox("📍 Direcciones", self)
        
        # Por ahora solo un label placeholder
        self.direcciones_label = QLabel("No hay direcciones registradas")
        direcciones_group.add_widget(self.direcciones_label)
        
        parent.add_widget(direcciones_group)
    
    def create_map_area(self, parent):
        """Crea el área del mapa."""
        map_group = LogisticaGroupBox("🌍 Mapa Interactivo", self)
        
        # Crear fallback del mapa
        self.create_static_map_fallback(map_group)
        
        parent.addWidget(map_group)
    
    def create_static_map_fallback(self, parent):
        """Crea un placeholder estático para el mapa."""
        fallback_frame = QFrame(self)
        fallback_frame.setStyleSheet(FALLBACK_MAP_STYLE)
        fallback_frame.setFixedHeight(400)
        
        layout = QVBoxLayout(fallback_frame)
        
        # Icono del mapa
        icon_label = QLabel("🗺️")
        icon_label.setStyleSheet("font-size: 64px;")
        layout.addWidget(icon_label)
        
        # Texto informativo
        info_label = QLabel("Mapa Interactivo")
        info_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(info_label)
        
        subtitle_label = QLabel("Funcionalidad de mapa en desarrollo")
        subtitle_label.setStyleSheet("font-size: 12px; color: #6c757d;")
        layout.addWidget(subtitle_label)
        
        # Botón de información
        btn_info = LogisticaButton(
            "Información de Cobertura", "info", ICONS["buttons"]["info"], self
        )
        btn_info.clicked.connect(self.mostrar_info_cobertura)
        layout.addWidget(btn_info)
        
        parent.add_widget(fallback_frame)
    
    def filtrar_mapa(self, filters: Dict[str, Any]):
        """Aplica filtros al mapa."""
        filtro = filters.get("filtro_mapa", "Todos los Servicios")
        self.show_success(f"Filtro aplicado: {filtro}")
    
    def agregar_marcador_mapa(self):
        """Agrega un marcador al mapa."""
        try:
            # Simular diálogo para agregar marcador
            direccion = "Dirección de ejemplo"
            descripcion = "Descripción de ejemplo"
            
            marcador = {
                "direccion": direccion,
                "descripcion": descripcion,
                "lat": -34.9215,  # Coordenadas de ejemplo (La Plata)
                "lng": -57.9545
            }
            
            self.marcadores.append(marcador)
            self.marcador_agregado.emit(marcador)
            self.actualizar_lista_direcciones()
            
            self.show_success("Marcador agregado correctamente")
            
        except Exception as e:
            self.show_error(f"Error agregando marcador: {str(e)}")
    
    def limpiar_marcadores_mapa(self):
        """Limpia todos los marcadores del mapa."""
        if self.ask_confirmation("¿Desea eliminar todos los marcadores?"):
            self.marcadores.clear()
            self.actualizar_lista_direcciones()
            self.show_success("Marcadores eliminados")
    
    def centrar_mapa(self):
        """Centra el mapa en la ubicación principal."""
        # Coordenadas de La Plata como centro
        self.ubicacion_seleccionada.emit(-34.9215, -57.9545)
        self.show_success("Mapa centrado en La Plata")
    
    def actualizar_lista_direcciones(self):
        """Actualiza la lista de direcciones mostrada."""
        if not self.marcadores:
            self.direcciones_label.setText("No hay direcciones registradas")
        else:
            texto = f"Direcciones registradas ({len(self.marcadores)}):\\n"
            for i, marcador in enumerate(self.marcadores[:5]):  # Mostrar máximo 5
                texto += f"{i+1}. {marcador['direccion']}\\n"
            if len(self.marcadores) > 5:
                texto += f"... y {len(self.marcadores) - 5} más"
            
            self.direcciones_label.setText(texto)
    
    def mostrar_info_cobertura(self):
        """Muestra información de cobertura de servicios."""
        info_text = """
        📍 Zonas de Cobertura:
        
        • Zona Centro: La Plata centro, Tolosa, Ringuelet
        • Zona Norte: Gonnet, City Bell, Villa Elisa  
        • Zona Este: Berisso, zonas industriales
        • Zona Sur: Los Hornos, Melchor Romero
        • Zona Oeste: Ensenada, puerto
        
        🚚 Tipos de Servicio:
        • Entrega Express: 30-60 minutos (zona centro)
        • Entrega Estándar: 60-120 minutos (todas las zonas)
        • Transporte de Obra: Coordinado según disponibilidad
        • Carga Pesada: Servicios especiales
        """
        
        self.show_success(info_text, "Información de Cobertura")
    
    def get_data(self) -> Dict[str, Any]:
        """Retorna los datos actuales del mapa."""
        return {
            "marcadores": self.marcadores,
            "filters": self.filter_panel.get_filters() if hasattr(self, 'filter_panel') else {}
        }
    
    def clear(self):
        """Limpia los marcadores y restablece el mapa."""
        self.marcadores.clear()
        self.actualizar_lista_direcciones()