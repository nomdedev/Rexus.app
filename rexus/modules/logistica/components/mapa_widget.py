# -*- coding: utf-8 -*-
"""
Widget de mapas para logística
Visualización geográfica de rutas, ubicaciones y seguimiento en tiempo real
"""

import logging
import tempfile
import os
from typing import Dict, List, Any, Optional, Tuple
from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton, 
    QLabel, QComboBox, QFrame, QMessageBox, QProgressBar,
    QScrollArea, QCheckBox, QSlider, QSpinBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QUrl
from PyQt6.QtWebEngineWidgets import QWebEngineView

from .base_logistica_widget import BaseLogisticaWidget
from rexus.ui.components.base_components import RexusButton, RexusGroupBox

logger = logging.getLogger(__name__)

# Verificar disponibilidad de librerías de mapas
try:
    import folium
    import folium.plugins
    FOLIUM_AVAILABLE = True
except ImportError:
    FOLIUM_AVAILABLE = False
    logger.warning()


class MapaWidget(BaseLogisticaWidget):
    """Widget para visualización de mapas y rutas logísticas."""
    
    # Señales específicas
    location_selected = pyqtSignal(float, float)  # lat, lon
    route_calculated = pyqtSignal(dict)
    marker_clicked = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.mapa_html_path = None
        self.markers_data = []
        self.rutas_data = []
        self.centro_mapa = (-34.6037, -58.3816)  # Buenos Aires por defecto
        self.zoom_nivel = 10
        
    def create_ui(self):
        """Crear interfaz de mapas."""
        layout = QVBoxLayout(self)
        
        # Panel de control de mapas
        control_panel = self.create_map_control_panel()
        layout.addWidget(control_panel)
        
        # Área principal del mapa
        map_area = self.create_map_area()
        layout.addWidget(map_area, 1)  # Expandir área del mapa
        
        # Panel de información lateral
        info_panel = self.create_info_panel()
        
        # Layout horizontal para mapa e información
        main_layout = QHBoxLayout()
        main_layout.addWidget(map_area, 3)  # Mapa ocupa 3 partes
        main_layout.addWidget(info_panel, 1)  # Info ocupa 1 parte
        
        layout.addLayout(main_layout)
    
    def create_map_control_panel(self) -> RexusGroupBox:
        """Crear panel de control del mapa."""
        group = RexusGroupBox("🗺️ Control de Mapas")
        layout = QHBoxLayout()
        
        # Botones de acción
        self.btn_centrar = RexusButton("📍 Centrar")
        self.btn_rutas = RexusButton("🛣️ Ver Rutas")
        self.btn_ubicaciones = RexusButton("📍 Ubicaciones")
        self.btn_trafico = RexusButton("🚦 Tráfico")
        self.btn_actualizar = RexusButton("🔄 Actualizar")
        
        # Selector de vista
        self.combo_vista = QComboBox()
        self.combo_vista.addItems(["Mapa", "Satélite", "Híbrido", "Terreno"])
        
        # Control de zoom
        self.zoom_label = QLabel("Zoom:")
        self.zoom_slider = QSlider(Qt.Orientation.Horizontal)
        self.zoom_slider.setMinimum(1)
        self.zoom_slider.setMaximum(18)
        self.zoom_slider.setValue(self.zoom_nivel)
        self.zoom_slider.setMaximumWidth(100)
        
        # Filtros
        self.check_transportes = QCheckBox("Transportes")
        self.check_almacenes = QCheckBox("Almacenes")
        self.check_clientes = QCheckBox("Clientes")
        
        # Configuración inicial
        self.check_transportes.setChecked(True)
        self.check_almacenes.setChecked(True)
        self.check_clientes.setChecked(True)
        
        layout.addWidget(self.btn_centrar)
        layout.addWidget(self.btn_rutas)
        layout.addWidget(self.btn_ubicaciones)
        layout.addWidget(self.btn_trafico)
        layout.addWidget(self.btn_actualizar)
        layout.addStretch()
        layout.addWidget(QLabel("Vista:"))
        layout.addWidget(self.combo_vista)
        layout.addWidget(self.zoom_label)
        layout.addWidget(self.zoom_slider)
        layout.addWidget(self.check_transportes)
        layout.addWidget(self.check_almacenes)
        layout.addWidget(self.check_clientes)
        
        group.setLayout(layout)
        return group
    
    def create_map_area(self) -> QFrame:
        """Crear área principal del mapa."""
        frame = QFrame()
        frame.setFrameStyle(QFrame.Shape.StyledPanel)
        layout = QVBoxLayout(frame)
        
        if FOLIUM_AVAILABLE:
            # Crear vista web para mapa interactivo
            self.web_view = QWebEngineView()
            self.web_view.setMinimumSize(600, 400)
            layout.addWidget(self.web_view)
            
            # Generar mapa inicial
            self.generar_mapa_inicial()
            
        else:
            # Vista alternativa sin folium
            self.create_mapa_alternativo(layout)
        
        return frame
    
    def create_mapa_alternativo(self, layout):
        """Crear vista alternativa del mapa cuando folium no está disponible."""
        # Simulación de mapa con widgets Qt
        mapa_frame = QFrame()
        mapa_frame.setStyleSheet("""
            QFrame {
                background-color: #e8f4f8;
                border: 2px solid #2196F3;
                border-radius: 8px;
            }
        """)
        mapa_frame.setMinimumSize(600, 400)
        
        mapa_layout = QVBoxLayout(mapa_frame)
        
        # Título
        titulo = QLabel("🗺️ Vista de Mapa Simulada")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo.setStyleSheet("font-size: 18px; font-weight: bold; color: #2196F3;")
        
        # Información de ubicaciones
        info_label = QLabel("""
        📍 Ubicaciones Activas:
        
        🏢 Almacén Central: -34.6037, -58.3816
        🚛 Transporte T-001: En ruta
        🏪 Cliente ABC: -34.5895, -58.3974
        🏪 Cliente XYZ: -34.6158, -58.3731
        
        ⚠️ Para vista completa de mapas, instale: pip install folium
        """)
        info_label.setStyleSheet("color: #333; padding: 20px; font-size: 12px;")
        
        mapa_layout.addWidget(titulo)
        mapa_layout.addWidget(info_label)
        mapa_layout.addStretch()
        
        layout.addWidget(mapa_frame)
    
    def create_info_panel(self) -> RexusGroupBox:
        """Crear panel de información lateral."""
        group = RexusGroupBox("📋 Información del Mapa")
        layout = QVBoxLayout()
        
        # Scroll area para información
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # Estadísticas rápidas
        stats_frame = self.create_quick_stats()
        scroll_layout.addWidget(stats_frame)
        
        # Lista de ubicaciones activas
        ubicaciones_frame = self.create_ubicaciones_activas()
        scroll_layout.addWidget(ubicaciones_frame)
        
        # Rutas programadas
        rutas_frame = self.create_rutas_programadas()
        scroll_layout.addWidget(rutas_frame)
        
        # Alertas del mapa
        alertas_frame = self.create_alertas_mapa()
        scroll_layout.addWidget(alertas_frame)
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        
        layout.addWidget(scroll)
        group.setLayout(layout)
        return group
    
    def create_quick_stats(self) -> QFrame:
        """Crear estadísticas rápidas."""
        frame = QFrame()
        frame.setFrameStyle(QFrame.Shape.Box)
        frame.setStyleSheet("QFrame { padding: 10px; }")
        
        layout = QVBoxLayout(frame)
        
        title = QLabel("📊 Estadísticas Rápidas")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)
        
        # Métricas
        stats_text = QLabel("""
        🚛 Transportes en ruta: 5
        📍 Ubicaciones activas: 12
        🛣️ Rutas programadas: 8
        ⏱️ Tiempo promedio: 45 min
        🎯 Eficiencia: 87%
        """)
        stats_text.setStyleSheet("color: #555; font-size: 11px;")
        layout.addWidget(stats_text)
        
        return frame
    
    def create_ubicaciones_activas(self) -> QFrame:
        """Crear lista de ubicaciones activas."""
        frame = QFrame()
        frame.setFrameStyle(QFrame.Shape.Box)
        frame.setStyleSheet("QFrame { padding: 10px; }")
        
        layout = QVBoxLayout(frame)
        
        title = QLabel("📍 Ubicaciones Activas")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)
        
        # Lista de ubicaciones
        ubicaciones = [
            ("🏢 Almacén Central", "Activo", "#4CAF50"),
            ("🚛 Transporte T-001", "En ruta", "#FF9800"),
            ("🚛 Transporte T-002", "Parado", "#F44336"),
            ("🏪 Cliente Norte", "Esperando", "#2196F3"),
            ("🏪 Cliente Sur", "Completado", "#4CAF50")
        ]
        
        for ubicacion, estado, color in ubicaciones:
            ub_layout = QHBoxLayout()
            
            ub_label = QLabel(ubicacion)
            ub_label.setStyleSheet("font-size: 11px;")
            
            estado_label = QLabel(estado)
            estado_label.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 10px;")
            
            ub_layout.addWidget(ub_label)
            ub_layout.addStretch()
            ub_layout.addWidget(estado_label)
            
            layout.addLayout(ub_layout)
        
        return frame
    
    def create_rutas_programadas(self) -> QFrame:
        """Crear lista de rutas programadas."""
        frame = QFrame()
        frame.setFrameStyle(QFrame.Shape.Box)
        frame.setStyleSheet("QFrame { padding: 10px; }")
        
        layout = QVBoxLayout(frame)
        
        title = QLabel("🛣️ Rutas Programadas")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)
        
        # Lista de rutas
        rutas = [
            "Ruta A: Centro → Norte (30 min)",
            "Ruta B: Sur → Este (25 min)",
            "Ruta C: Oeste → Centro (40 min)",
            "Ruta D: Norte → Sur (50 min)"
        ]
        
        for ruta in rutas:
            ruta_label = QLabel(f"• {ruta}")
            ruta_label.setStyleSheet("font-size: 11px; color: #555;")
            layout.addWidget(ruta_label)
        
        return frame
    
    def create_alertas_mapa(self) -> QFrame:
        """Crear panel de alertas del mapa."""
        frame = QFrame()
        frame.setFrameStyle(QFrame.Shape.Box)
        frame.setStyleSheet("QFrame { padding: 10px; }")
        
        layout = QVBoxLayout(frame)
        
        title = QLabel("⚠️ Alertas")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)
        
        # Alertas
        alertas = [
            ("🚦 Congestión en Ruta Norte", "#FF9800"),
            ("⛽ Vehículo con combustible bajo", "#F44336"),
            ("📍 Nueva ubicación agregada", "#4CAF50"),
            ("⏰ Retraso en entrega programada", "#FF9800")
        ]
        
        for alerta, color in alertas:
            alerta_label = QLabel(f"• {alerta}")
            alerta_label.setStyleSheet(f"font-size: 10px; color: {color};")
            alerta_label.setWordWrap(True)
            layout.addWidget(alerta_label)
        
        return frame
    
    def generar_mapa_inicial(self):
        """Generar mapa inicial con folium."""
        if not FOLIUM_AVAILABLE:
            return
        
        try:
            # Crear mapa centrado en ubicación por defecto
            mapa = folium.Map(
                location=self.centro_mapa,
                zoom_start=self.zoom_nivel,
                tiles='OpenStreetMap'
            )
            
            # Agregar marcadores de ejemplo
            self.agregar_marcadores_ejemplo(mapa)
            
            # Agregar rutas de ejemplo
            self.agregar_rutas_ejemplo(mapa)
            
            # Guardar mapa temporal
            self.mapa_html_path = tempfile.mktemp(suffix='.html')
            mapa.save(self.mapa_html_path)
            
            # Cargar en vista web
            self.web_view.load(QUrl.fromLocalFile(self.mapa_html_path))
            
        except Exception as e:
    
    def agregar_marcadores_ejemplo(self, mapa):
        """Agregar marcadores de ejemplo al mapa."""
        marcadores = [
            {
                'lat': -34.6037, 'lon': -58.3816,
                'popup': 'Almacén Central',
                'icon': 'warehouse', 'color': 'blue'
            },
            {
                'lat': -34.5895, 'lon': -58.3974,
                'popup': 'Cliente ABC - En espera',
                'icon': 'customer', 'color': 'green'
            },
            {
                'lat': -34.6158, 'lon': -58.3731,
                'popup': 'Transporte T-001 - En ruta',
                'icon': 'truck', 'color': 'orange'
            },
            {
                'lat': -34.5989, 'lon': -58.3731,
                'popup': 'Cliente XYZ - Completado',
                'icon': 'customer', 'color': 'darkgreen'
            }
        ]
        
        for marcador in marcadores:
            folium.Marker(
                location=[marcador['lat'], marcador['lon']],
                popup=marcador['popup'],
                icon=folium.Icon(color=marcador['color'])
            ).add_to(mapa)
    
    def agregar_rutas_ejemplo(self, mapa):
        """Agregar rutas de ejemplo al mapa."""
        # Ruta de ejemplo: Almacén a Cliente ABC
        ruta_coords = [
            [-34.6037, -58.3816],  # Almacén
            [-34.5950, -58.3880],  # Punto intermedio
            [-34.5895, -58.3974]   # Cliente ABC
        ]
        
        folium.PolyLine(
            locations=ruta_coords,
            color='red',
            weight=3,
            opacity=0.8,
            popup='Ruta: Almacén → Cliente ABC'
        ).add_to(mapa)
        
        # Ruta de ejemplo 2: Cliente ABC a Cliente XYZ
        ruta_coords_2 = [
            [-34.5895, -58.3974],  # Cliente ABC
            [-34.6020, -58.3850],  # Punto intermedio
            [-34.5989, -58.3731]   # Cliente XYZ
        ]
        
        folium.PolyLine(
            locations=ruta_coords_2,
            color='blue',
            weight=3,
            opacity=0.8,
            popup='Ruta: Cliente ABC → Cliente XYZ'
        ).add_to(mapa)
    
    def connect_signals(self):
        """Conectar señales del widget."""
        # Controles del mapa
        self.btn_centrar.clicked.connect(self.centrar_mapa)
        self.btn_rutas.clicked.connect(self.mostrar_rutas)
        self.btn_ubicaciones.clicked.connect(self.mostrar_ubicaciones)
        self.btn_trafico.clicked.connect(self.mostrar_trafico)
        self.btn_actualizar.clicked.connect(self.actualizar_mapa)
        
        # Controles de vista
        self.combo_vista.currentTextChanged.connect(self.cambiar_vista)
        self.zoom_slider.valueChanged.connect(self.cambiar_zoom)
        
        # Filtros
        self.check_transportes.stateChanged.connect(self.aplicar_filtros)
        self.check_almacenes.stateChanged.connect(self.aplicar_filtros)
        self.check_clientes.stateChanged.connect(self.aplicar_filtros)
    
    def refresh_data(self):
        """Actualizar datos del mapa."""
        try:
            if FOLIUM_AVAILABLE:
                self.generar_mapa_inicial()
            else:
                logger.info("Mapa actualizado (modo simulación)")
                
        except Exception as e:
    
    # Métodos de control del mapa
    
    def centrar_mapa(self):
        """Centrar mapa en ubicación por defecto."""
        if FOLIUM_AVAILABLE:
            self.generar_mapa_inicial()
        QMessageBox.information(self, "Centrar", "Mapa centrado en ubicación principal")
    
    def mostrar_rutas(self):
        """Mostrar/ocultar rutas en el mapa."""
        QMessageBox.information(self, "Rutas", "Rutas mostradas/ocultadas")
    
    def mostrar_ubicaciones(self):
        """Mostrar/ocultar ubicaciones en el mapa."""
        QMessageBox.information(self, "Ubicaciones", "Ubicaciones mostradas/ocultadas")
    
    def mostrar_trafico(self):
        """Mostrar información de tráfico."""
        QMessageBox.information(self, "Tráfico", "Información de tráfico actualizada")
    
    def actualizar_mapa(self):
        """Actualizar mapa completamente."""
        self.refresh_data()
        QMessageBox.information(self, "Actualizar", "Mapa actualizado exitosamente")
    
    def cambiar_vista(self, vista: str):
        """Cambiar tipo de vista del mapa."""
        logger.info(f"Cambiando vista del mapa a: {vista}")
        
        if FOLIUM_AVAILABLE:
            # Regenerar mapa con nueva vista
            try:
                tile_map = {
                    'Mapa': 'OpenStreetMap',
                    'Satélite': 'Esri.WorldImagery', 
                    'Híbrido': 'CartoDB.Positron',
                    'Terreno': 'Stamen.Terrain'
                }
                
                # Aquí se regeneraría el mapa con el tile seleccionado
                self.generar_mapa_con_vista(tile_map.get(vista, 'OpenStreetMap'))
                
            except Exception as e:
    def generar_mapa_con_vista(self, tile_type: str):
        """Generar mapa con tipo de tile específico."""
        if not FOLIUM_AVAILABLE:
            return
        
        try:
            mapa = folium.Map(
                location=self.centro_mapa,
                zoom_start=self.zoom_nivel,
                tiles=tile_type
            )
            
            self.agregar_marcadores_ejemplo(mapa)
            self.agregar_rutas_ejemplo(mapa)
            
            if self.mapa_html_path:
                os.remove(self.mapa_html_path)
            
            self.mapa_html_path = tempfile.mktemp(suffix='.html')
            mapa.save(self.mapa_html_path)
            self.web_view.load(QUrl.fromLocalFile(self.mapa_html_path))
            
        except Exception as e:
    def cambiar_zoom(self, valor: int):
        """Cambiar nivel de zoom del mapa."""
        self.zoom_nivel = valor
        logger.info(f"Zoom cambiado a: {valor}")
        
        # En implementación real, actualizaría el mapa
        if FOLIUM_AVAILABLE and hasattr(self, 'web_view'):
            # Se podría inyectar JavaScript para cambiar zoom sin regenerar
            pass
    
    def aplicar_filtros(self):
        """Aplicar filtros de visualización."""
        transportes = self.check_transportes.isChecked()
        almacenes = self.check_almacenes.isChecked()
        clientes = self.check_clientes.isChecked()
        
        logger.info(f"Filtros aplicados - Transportes: {transportes}, Almacenes: {almacenes}, Clientes: {clientes}")
        
        # En implementación real, filtraría marcadores
        if FOLIUM_AVAILABLE:
            self.generar_mapa_con_filtros(transportes, almacenes, clientes)
    
    def generar_mapa_con_filtros(self, show_transportes: bool, show_almacenes: bool, show_clientes: bool):
        """Generar mapa aplicando filtros."""
        # Implementación de filtros específicos
        pass
    
    def agregar_ubicacion(self, lat: float, lon: float, nombre: str, tipo: str):
        """Agregar nueva ubicación al mapa."""
        nueva_ubicacion = {
            'lat': lat, 'lon': lon, 'nombre': nombre, 'tipo': tipo
        }
        self.markers_data.append(nueva_ubicacion)
        
        # Regenerar mapa si es necesario
        if FOLIUM_AVAILABLE:
            self.generar_mapa_inicial()
    
    def calcular_ruta(self, origen: Tuple[float, float], destino: Tuple[float, float]):
        """Calcular ruta entre dos puntos."""
        # Simulación de cálculo de ruta
        ruta_info = {
            'origen': origen,
            'destino': destino,
            'distancia': 15.5,  # km
            'tiempo_estimado': 25,  # minutos
            'ruta_optima': True
        }
        
        self.route_calculated.emit(ruta_info)
        return ruta_info
    
    def cleanup(self):
        """Limpiar recursos del mapa."""
        if self.mapa_html_path and os.path.exists(self.mapa_html_path):
            try:
                os.remove(self.mapa_html_path)
            except Exception as e:
                logger.warning(f"No se pudo eliminar archivo temporal: {e}")
    
    def __del__(self):
        """Destructor para limpieza."""
        self.cleanup()