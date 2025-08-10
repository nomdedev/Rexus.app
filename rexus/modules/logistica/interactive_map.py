"""
Componente de Mapa Interactivo para Logística

Implementa mapas interactivos usando Folium y QWebEngineView
centrado en La Plata y alrededores.
"""

import folium
import tempfile
import os
from typing import List, Dict, Tuple, Optional
from PyQt6.QtCore import QUrl, pyqtSignal
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QComboBox
from rexus.utils.unified_sanitizer import unified_sanitizer, sanitize_string, sanitize_numeric


class InteractiveMapWidget(QWidget):
    """Widget de mapa interactivo para el módulo de logística."""
    
    # Señales
    location_clicked = pyqtSignal(float, float)  # lat, lng
    marker_clicked = pyqtSignal(dict)  # marker data
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Coordenadas de La Plata, Argentina
        self.la_plata_coords = (-34.9214, -57.9544)
        self.current_zoom = 12
        
        # Datos de ubicaciones
        self.locations = []
        self.map_html_path = None
        
        self.init_ui()
        self.create_initial_map()
    
    def init_ui(self):
        """Inicializa la interfaz del widget."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Panel de controles
        controls_layout = QHBoxLayout()
        
        # Botón para centrar en La Plata
        btn_center = QPushButton("📍 Centrar en La Plata")
        btn_center.clicked.connect(self.center_on_la_plata)
        btn_center.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        controls_layout.addWidget(btn_center)
        
        # Selector de zoom
        controls_layout.addWidget(QLabel("Zoom:"))
        self.zoom_combo = QComboBox()
        self.zoom_combo.addItems(["10", "12", "14", "16", "18"])
        self.zoom_combo.setCurrentText("12")
        self.zoom_combo.currentTextChanged.connect(self.change_zoom)
        controls_layout.addWidget(self.zoom_combo)
        
        # Botón actualizar
        btn_refresh = QPushButton("🔄 Actualizar")
        btn_refresh.clicked.connect(self.refresh_map)
        btn_refresh.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        controls_layout.addWidget(btn_refresh)
        
        controls_layout.addStretch()
        
        # Label de información
        self.info_label = QLabel("Mapa de La Plata y alrededores")
        self.info_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-weight: bold;
                padding: 4px;
            }
        """)
        controls_layout.addWidget(self.info_label)
        
        layout.addLayout(controls_layout)
        
        # WebView para mostrar el mapa
        self.web_view = QWebEngineView()
        self.web_view.setMinimumHeight(500)
        layout.addWidget(self.web_view)
    
    def create_initial_map(self):
        """Crea el mapa inicial centrado en La Plata."""
        # Crear mapa con Folium
        m = folium.Map(
            location=self.la_plata_coords,
            zoom_start=self.current_zoom,
            tiles='OpenStreetMap'
        )
        
        # Agregar marcador de La Plata
        folium.Marker(
            self.la_plata_coords,
            popup="La Plata - Ciudad Principal",
            tooltip="La Plata",
            icon=folium.Icon(color='red', icon='home')
        ).add_to(m)
        
        # Agregar ubicaciones importantes de La Plata
        important_locations = [
            {"name": "Centro de La Plata", "coords": (-34.9214, -57.9544), "type": "centro"},
            {"name": "Berisso", "coords": (-34.8833, -57.8833), "type": "ciudad"},
            {"name": "Ensenada", "coords": (-34.8667, -57.9333), "type": "ciudad"},
            {"name": "Los Hornos", "coords": (-34.9667, -57.9667), "type": "barrio"},
            {"name": "Gonnet", "coords": (-34.8833, -58.0000), "type": "barrio"},
            {"name": "City Bell", "coords": (-34.8667, -58.0167), "type": "barrio"},
            {"name": "Villa Elisa", "coords": (-34.8500, -58.0167), "type": "barrio"},
            {"name": "Tolosa", "coords": (-34.9000, -57.9667), "type": "barrio"},
            {"name": "Ringuelet", "coords": (-34.9167, -57.9500), "type": "barrio"},
            {"name": "San Carlos", "coords": (-34.9500, -57.9500), "type": "barrio"},
        ]
        
        # Agregar marcadores para ubicaciones importantes
        for location in important_locations:
            color = self._get_marker_color(location["type"])
            icon = self._get_marker_icon(location["type"])
            
            folium.Marker(
                location["coords"],
                popup=f"{location['name']} ({location['type'].title()})",
                tooltip=location["name"],
                icon=folium.Icon(color=color, icon=icon)
            ).add_to(m)
        
        # Agregar círculo para mostrar área de cobertura
        folium.Circle(
            location=self.la_plata_coords,
            radius=15000,  # 15km de radio
            popup="Área de Cobertura de Servicios",
            color="blue",
            fill=True,
            fillColor="lightblue",
            fillOpacity=0.2
        ).add_to(m)
        
        # Guardar mapa como HTML temporal
        self.save_and_load_map(m)
    
    def _get_marker_color(self, location_type: str) -> str:
        """Obtiene el color del marcador según el tipo de ubicación."""
        colors = {
            "centro": "red",
            "ciudad": "blue",
            "barrio": "green",
            "servicio": "orange",
            "obra": "purple",
            "entrega": "pink"
        }
        return colors.get(location_type, "gray")
    
    def _get_marker_icon(self, location_type: str) -> str:
        """Obtiene el ícono del marcador según el tipo de ubicación."""
        icons = {
            "centro": "home",
            "ciudad": "star",
            "barrio": "info-sign",
            "servicio": "truck",
            "obra": "wrench",
            "entrega": "gift"
        }
        return icons.get(location_type, "info-sign")
    
    def add_service_markers(self, services: List[Dict]):
        """Agrega marcadores para servicios en el mapa."""
        try:
            # Crear nuevo mapa
            m = folium.Map(
                location=self.la_plata_coords,
                zoom_start=self.current_zoom,
                tiles='OpenStreetMap'
            )
            
            # Agregar marcador principal de La Plata
            folium.Marker(
                self.la_plata_coords,
                popup="La Plata - Ciudad Principal",
                tooltip="La Plata",
                icon=folium.Icon(color='red', icon='home')
            ).add_to(m)
            
            # Agregar marcadores de servicios
            for service in services:
                if 'coords' in service and service['coords']:
                    lat, lng = service['coords']
                    
                    popup_text = f"""
                    <b>{service.get('tipo', 'Servicio')}</b><br>
                    Cliente: {service.get('cliente', 'N/A')}<br>
                    Dirección: {service.get('direccion', 'N/A')}<br>
                    Estado: {service.get('estado', 'N/A')}<br>
                    Fecha: {service.get('fecha', 'N/A')}
                    """
                    
                    folium.Marker(
                        [lat, lng],
                        popup=popup_text,
                        tooltip=service.get('cliente', 'Servicio'),
                        icon=folium.Icon(
                            color=self._get_marker_color('servicio'),
                            icon=self._get_marker_icon('servicio')
                        )
                    ).add_to(m)
            
            # Guardar y cargar mapa actualizado
            self.save_and_load_map(m)
            
        except Exception as e:
            print(f"Error agregando marcadores de servicios: {e}")
    
    def add_obra_markers(self, obras: List[Dict]):
        """Agrega marcadores para entregas de obras en el mapa."""
        try:
            # Crear nuevo mapa
            m = folium.Map(
                location=self.la_plata_coords,
                zoom_start=self.current_zoom,
                tiles='OpenStreetMap'
            )
            
            # Agregar marcador principal de La Plata
            folium.Marker(
                self.la_plata_coords,
                popup="La Plata - Ciudad Principal",
                tooltip="La Plata",
                icon=folium.Icon(color='red', icon='home')
            ).add_to(m)
            
            # Agregar marcadores de obras
            for obra in obras:
                if 'coords' in obra and obra['coords']:
                    lat, lng = obra['coords']
                    
                    popup_text = f"""
                    <b>Obra: {obra.get('nombre', 'Sin nombre')}</b><br>
                    Cliente: {obra.get('cliente', 'N/A')}<br>
                    Dirección: {obra.get('direccion', 'N/A')}<br>
                    Estado: {obra.get('estado', 'N/A')}<br>
                    Responsable: {obra.get('responsable', 'N/A')}<br>
                    Presupuesto: ${obra.get('presupuesto', 0):,.2f}
                    """
                    
                    # Color según estado de obra
                    color = self._get_obra_color(obra.get('estado', 'PLANIFICACION'))
                    
                    folium.Marker(
                        [lat, lng],
                        popup=popup_text,
                        tooltip=obra.get('nombre', 'Obra'),
                        icon=folium.Icon(
                            color=color,
                            icon=self._get_marker_icon('obra')
                        )
                    ).add_to(m)
            
            # Guardar y cargar mapa actualizado
            self.save_and_load_map(m)
            
        except Exception as e:
            print(f"Error agregando marcadores de obras: {e}")
    
    def add_combined_markers(self, services: Optional[List[Dict]] = None, obras: Optional[List[Dict]] = None):
        """Agrega marcadores combinados de servicios y obras en el mapa."""
        try:
            # Crear nuevo mapa
            m = folium.Map(
                location=self.la_plata_coords,
                zoom_start=self.current_zoom,
                tiles='OpenStreetMap'
            )
            
            # Agregar marcador principal de La Plata
            folium.Marker(
                self.la_plata_coords,
                popup="La Plata - Ciudad Principal",
                tooltip="La Plata",
                icon=folium.Icon(color='red', icon='home')
            ).add_to(m)
            
            # Agregar marcadores de servicios
            if services:
                for service in services:
                    if 'coords' in service and service['coords']:
                        lat, lng = service['coords']
                        
                        popup_text = f"""
                        <b>🚚 SERVICIO</b><br>
                        Tipo: {service.get('tipo', 'Servicio')}<br>
                        Cliente: {service.get('cliente', 'N/A')}<br>
                        Dirección: {service.get('direccion', 'N/A')}<br>
                        Estado: {service.get('estado', 'N/A')}<br>
                        Fecha: {service.get('fecha', 'N/A')}
                        """
                        
                        folium.Marker(
                            [lat, lng],
                            popup=popup_text,
                            tooltip=f"🚚 {service.get('cliente', 'Servicio')}",
                            icon=folium.Icon(
                                color='orange',
                                icon='truck'
                            )
                        ).add_to(m)
            
            # Agregar marcadores de obras
            if obras:
                for obra in obras:
                    if 'coords' in obra and obra['coords']:
                        lat, lng = obra['coords']
                        
                        popup_text = f"""
                        <b>🏗️ OBRA</b><br>
                        Nombre: {obra.get('nombre', 'Sin nombre')}<br>
                        Cliente: {obra.get('cliente', 'N/A')}<br>
                        Dirección: {obra.get('direccion', 'N/A')}<br>
                        Estado: {obra.get('estado', 'N/A')}<br>
                        Responsable: {obra.get('responsable', 'N/A')}<br>
                        Presupuesto: ${obra.get('presupuesto', 0):,.2f}
                        """
                        
                        color = self._get_obra_color(obra.get('estado', 'PLANIFICACION'))
                        
                        folium.Marker(
                            [lat, lng],
                            popup=popup_text,
                            tooltip=f"🏗️ {obra.get('nombre', 'Obra')}",
                            icon=folium.Icon(
                                color=color,
                                icon='wrench'
                            )
                        ).add_to(m)
            
            # Agregar área de cobertura
            folium.Circle(
                location=self.la_plata_coords,
                radius=15000,
                popup="Área de Cobertura de Servicios",
                color="blue",
                fill=True,
                fillColor="lightblue",
                fillOpacity=0.2
            ).add_to(m)
            
            # Guardar y cargar mapa actualizado
            self.save_and_load_map(m)
            
        except Exception as e:
            print(f"Error agregando marcadores combinados: {e}")
    
    def _get_obra_color(self, estado: str) -> str:
        """Obtiene el color del marcador según el estado de la obra."""
        colors = {
            "PLANIFICACION": "blue",
            "EN_PROCESO": "orange", 
            "PAUSADA": "gray",
            "FINALIZADA": "green",
            "CANCELADA": "red"
        }
        return colors.get(estado.upper(), "purple")
    
    def add_custom_marker(self, lat: float, lng: float, title: str, 
                         description: str, marker_type: str = "servicio"):
        """Agrega un marcador personalizado al mapa."""
        try:
            location_data = {
                'coords': (lat, lng),
                'title': title,
                'description': description,
                'type': marker_type
            }
            self.locations.append(location_data)
            
            # Recrear mapa con todas las ubicaciones
            self.refresh_map()
            
        except Exception as e:
            print(f"Error agregando marcador personalizado: {e}")
    
    def add_address_markers(self, direcciones: List[Dict]):
        """Agrega marcadores para direcciones en el mapa."""
        try:
            # Crear nuevo mapa
            m = folium.Map(
                location=self.la_plata_coords,
                zoom_start=self.current_zoom,
                tiles='OpenStreetMap'
            )
            
            # Agregar marcador principal de La Plata
            folium.Marker(
                self.la_plata_coords,
                popup="<b>La Plata - Ciudad Principal</b><br>Centro de operaciones",
                tooltip="La Plata",
                icon=folium.Icon(color='red', icon='home')
            ).add_to(m)
            
            # Agregar marcadores de direcciones
            for direccion in direcciones:
                if 'coords' in direccion and direccion['coords']:
                    lat, lng = direccion['coords']
                    
                    # Crear popup con información de la dirección
                    popup_text = f"""
                    <b>📍 {direccion.get('tipo', 'Ubicación')}</b><br>
                    <b>Dirección:</b> {direccion.get('direccion', 'N/A')}<br>
                    <b>Ciudad:</b> {direccion.get('ciudad', 'N/A')}<br>
                    <b>Descripción:</b> {direccion.get('descripcion', 'Sin descripción')}
                    """
                    
                    # Color según tipo de ubicación
                    tipo = direccion.get('tipo', '').lower()
                    if 'almacén' in tipo or 'almacen' in tipo:
                        color = 'blue'
                        icon = 'warehouse'
                    elif 'sucursal' in tipo:
                        color = 'green'
                        icon = 'building'
                    elif 'depósito' in tipo or 'deposito' in tipo:
                        color = 'orange'
                        icon = 'archive'
                    else:
                        color = 'purple'
                        icon = 'map-marker'
                    
                    folium.Marker(
                        [lat, lng],
                        popup=popup_text,
                        tooltip=f"{direccion.get('tipo', 'Ubicación')}: {direccion.get('direccion', 'N/A')}",
                        icon=folium.Icon(
                            color=color,
                            icon=icon if icon != 'warehouse' and icon != 'archive' else 'home'
                        )
                    ).add_to(m)
            
            # Agregar área de cobertura
            folium.Circle(
                location=self.la_plata_coords,
                radius=20000,
                popup="Área de Cobertura - Logística",
                color="blue",
                fill=True,
                fillColor="lightblue",
                fillOpacity=0.15,
                weight=2
            ).add_to(m)
            
            # Guardar y cargar mapa actualizado
            self.save_and_load_map(m)
            
            # Actualizar información
            self.info_label.setText(f"Mapa con {len(direcciones)} direcciones cargadas")
            
        except Exception as e:
            print(f"Error agregando marcadores de direcciones: {e}")

    def save_and_load_map(self, folium_map):
        """Guarda el mapa de Folium como HTML y lo carga en WebView."""
        try:
            # Crear archivo temporal
            if self.map_html_path and os.path.exists(self.map_html_path):
                os.remove(self.map_html_path)
            
            temp_file = tempfile.NamedTemporaryFile(
                suffix='.html', 
                delete=False, 
                mode='w', 
                encoding='utf-8'
            )
            
            # Guardar mapa
            folium_map.save(temp_file.name)
            temp_file.close()
            
            self.map_html_path = temp_file.name
            
            # Cargar en WebView
            self.web_view.load(QUrl.fromLocalFile(os.path.abspath(self.map_html_path)))
            
            # Actualizar información
            self.info_label.setText(f"Mapa actualizado - Marcadores: {len(self.locations)}")
            
        except Exception as e:
            print(f"Error guardando/cargando mapa: {e}")
    
    def center_on_la_plata(self):
        """Centra el mapa en La Plata."""
        self.create_initial_map()
    
    def change_zoom(self, zoom_str: str):
        """Cambia el nivel de zoom del mapa."""
        try:
            self.current_zoom = int(zoom_str)
            self.refresh_map()
        except ValueError:
            pass
    
    def refresh_map(self):
        """Actualiza el mapa con las ubicaciones actuales."""
        try:
            # Crear nuevo mapa
            m = folium.Map(
                location=self.la_plata_coords,
                zoom_start=self.current_zoom,
                tiles='OpenStreetMap'
            )
            
            # Agregar marcador principal
            folium.Marker(
                self.la_plata_coords,
                popup="La Plita - Ciudad Principal",
                tooltip="La Plata",
                icon=folium.Icon(color='red', icon='home')
            ).add_to(m)
            
            # Agregar todas las ubicaciones guardadas
            for location in self.locations:
                folium.Marker(
                    location['coords'],
                    popup=location['description'],
                    tooltip=location['title'],
                    icon=folium.Icon(
                        color=self._get_marker_color(location['type']),
                        icon=self._get_marker_icon(location['type'])
                    )
                ).add_to(m)
            
            # Agregar área de cobertura
            folium.Circle(
                location=self.la_plata_coords,
                radius=15000,
                popup="Área de Cobertura de Servicios",
                color="blue",
                fill=True,
                fillColor="lightblue",
                fillOpacity=0.2
            ).add_to(m)
            
            self.save_and_load_map(m)
            
        except Exception as e:
            print(f"Error actualizando mapa: {e}")
    
    def clear_markers(self):
        """Limpia todos los marcadores del mapa."""
        self.locations.clear()
        self.create_initial_map()
    
    def get_la_plata_addresses(self) -> List[Dict]:
        """Retorna una lista de direcciones comunes de La Plata para demo."""
        return [
            {"address": "Calle 7 entre 47 y 48, La Plata", "coords": (-34.9214, -57.9544)},
            {"address": "Av. 13 y 60, La Plata", "coords": (-34.9156, -57.9578)},
            {"address": "Calle 50 entre 15 y 16, Berisso", "coords": (-34.8833, -57.8833)},
            {"address": "Calle 25 entre 3 y 4, Gonnet", "coords": (-34.8833, -58.0000)},
            {"address": "Av. 122 y 82, Los Hornos", "coords": (-34.9667, -57.9667)},
            {"address": "Calle 1 y 57, Tolosa", "coords": (-34.9000, -57.9667)},
            {"address": "Calle 10 y 38, City Bell", "coords": (-34.8667, -58.0167)},
            {"address": "Av. 44 y 150, Villa Elisa", "coords": (-34.8500, -58.0167)},
            {"address": "Calle 520 y 15, Melchor Romero", "coords": (-34.9833, -58.0167)},
            {"address": "Calle 2 y 64, Ringuelet", "coords": (-34.9167, -57.9500)},
        ]
    
    def cleanup(self):
        """Limpia recursos del widget."""
        if self.map_html_path and os.path.exists(self.map_html_path):
            try:
                os.remove(self.map_html_path)
            except (OSError, PermissionError) as e:
                print(f"[WARNING INTERACTIVE_MAP] Could not remove temp file: {e}")
    
    def __del__(self):
        """Destructor del widget."""
        self.cleanup()


def geocode_address_la_plata(address: str) -> Tuple[float, float]:
    """
    Función simple de geocodificación para direcciones de La Plata.
    En un entorno real, usarías una API como Google Maps o Nominatim.
    """
    # Direcciones comunes de La Plata (simuladas)
    addresses_map = {
        "la plata centro": (-34.9214, -57.9544),
        "berisso": (-34.8833, -57.8833),
        "ensenada": (-34.8667, -57.9333),
        "gonnet": (-34.8833, -58.0000),
        "city bell": (-34.8667, -58.0167),
        "villa elisa": (-34.8500, -58.0167),
        "los hornos": (-34.9667, -57.9667),
        "tolosa": (-34.9000, -57.9667),
        "ringuelet": (-34.9167, -57.9500),
        "san carlos": (-34.9500, -57.9500),
    }
    
    # Buscar coincidencia aproximada
    address_lower = address.lower()
    for key, coords in addresses_map.items():
        if key in address_lower:
            return coords
    
    # Si no se encuentra, retornar coordenadas de La Plata centro
    return (-34.9214, -57.9544)