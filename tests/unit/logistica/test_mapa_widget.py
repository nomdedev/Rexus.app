# -*- coding: utf-8 -*-
"""
Tests unitarios para MapaWidget
Refactorización de logística - Tests de componente de mapa
"""

import pytest
import sys
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtTest import QTest

# Configurar encoding UTF-8
sys.stdout.reconfigure(encoding='utf-8')

# Agregar path del proyecto
root_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(root_dir))

# Imports a testear
try:
    from rexus.modules.logistica.components.mapa_widget import MapaWidget
    from rexus.ui.components.base_components import RexusButton, RexusLineEdit
except ImportError as e:
    pytest.skip(f, allow_module_level=True)

import logging
logger = logging.getLogger(__name__)


class TestMapaWidget:
    """Tests para widget de mapa de logística."""
    
    @classmethod
    def setup_class(cls):
        """Configuración inicial para todos los tests."""
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()
    
    def setup_method(self):
        """Configuración para cada test."""
        self.mock_parent = Mock()
        self.mock_db = Mock()
        self.mock_cursor = Mock()
        self.mock_db.cursor.return_value = self.mock_cursor
        
        # Datos de ejemplo para mapas
        self.sample_locations = [
            {
                'id': 1, 'nombre': 'Almacén Principal', 'tipo': 'almacen',
                'lat': -34.6037, 'lon': -58.3816, 'direccion': 'Av. Corrientes 1000',
                'activo': True, 'descripcion': 'Almacén central'
            },
            {
                'id': 2, 'nombre': 'Cliente A', 'tipo': 'cliente',
                'lat': -34.6118, 'lon': -58.3960, 'direccion': 'Florida 500',
                'activo': True, 'descripcion': 'Cliente importante'
            },
            {
                'id': 3, 'nombre': 'Depósito Norte', 'tipo': 'deposito',
                'lat': -34.5875, 'lon': -58.3974, 'direccion': 'Av. Santa Fe 2000',
                'activo': False, 'descripcion': 'Depósito secundario'
            }
        ]
        
        self.sample_routes = [
            {
                'id': 1, 'origen_id': 1, 'destino_id': 2,
                'distancia_km': 2.5, 'tiempo_estimado': 15,
                'estado_trafico': 'normal', 'costo_combustible': 150.0,
                'coordenadas': [[-34.6037, -58.3816], [-34.6118, -58.3960]]
            },
            {
                'id': 2, 'origen_id': 1, 'destino_id': 3,
                'distancia_km': 3.2, 'tiempo_estimado': 22,
                'estado_trafico': 'congestion', 'costo_combustible': 200.0,
                'coordenadas': [[-34.6037, -58.3816], [-34.5875, -58.3974]]
            }
        ]
    
    def test_widget_initialization(self):
        """Test inicialización del widget."""
        widget = MapaWidget(self.mock_parent)
        
        assert widget is not None
        assert widget.parent_view == self.mock_parent
        assert hasattr(widget, 'map_data')
        assert hasattr(widget, 'locations')
        assert hasattr(widget, 'routes')
        assert hasattr(widget, 'selected_location')
        assert hasattr(widget, 'current_route')
        
        # Verificar componentes UI
        assert hasattr(widget, 'mapa_view')
        assert hasattr(widget, 'btn_add_location')
        assert hasattr(widget, 'btn_calculate_route')
        assert hasattr(widget, 'btn_toggle_traffic')
        assert hasattr(widget, 'search_location')
    
    def test_setup_ui_components(self):
        """Test configuración de componentes UI."""
        widget = MapaWidget(self.mock_parent)
        
        # Verificar toolbar
        assert hasattr(widget, 'toolbar')
        
        # Verificar controles de mapa
        assert hasattr(widget, 'zoom_in_btn')
        assert hasattr(widget, 'zoom_out_btn')
        assert hasattr(widget, 'center_btn')
        
        # Verificar panel de información
        assert hasattr(widget, 'info_panel')
    
    def test_cargar_ubicaciones(self):
        """Test carga de ubicaciones en mapa."""
        widget = MapaWidget(self.mock_parent)
        
        # Cargar ubicaciones de ejemplo
        widget.cargar_ubicaciones(self.sample_locations)
        
        # Verificar que se cargaron las ubicaciones
        assert len(widget.locations) == len(self.sample_locations)
        assert widget.locations == self.sample_locations
    
    def test_agregar_ubicacion(self):
        """Test agregar nueva ubicación."""
        widget = MapaWidget(self.mock_parent)
        
        nueva_ubicacion = {
            'id': 4, 'nombre': 'Nuevo Punto', 'tipo': 'punto_interes',
            'lat': -34.6000, 'lon': -58.4000, 'direccion': 'Nueva Dirección',
            'activo': True, 'descripcion': 'Punto de interés'
        }
        
        # Mock del método crear_marcador
        with patch.object(widget, 'crear_marcador') as mock_marcador:
            widget.agregar_ubicacion(nueva_ubicacion)
            
            # Verificar que se agregó a la lista
            assert nueva_ubicacion in widget.locations
            
            # Verificar que se creó el marcador
            mock_marcador.assert_called_once_with(nueva_ubicacion)
    
    def test_crear_marcador_almacen(self):
        """Test creación de marcador para almacén."""
        widget = MapaWidget(self.mock_parent)
        
        ubicacion_almacen = self.sample_locations[0]  # Almacén Principal
        
        # Mock de la librería folium si está disponible
        with patch('folium.Marker') as mock_marker:
            resultado = widget.crear_marcador(ubicacion_almacen)
            
            if hasattr(widget, 'folium_available') and widget.folium_available:
                mock_marker.assert_called_once()
                assert resultado is not None
            else:
                # Sin folium, debería retornar diccionario con datos
                assert isinstance(resultado, dict)
                assert resultado['nombre'] == 'Almacén Principal'
    
    def test_crear_marcador_cliente(self):
        """Test creación de marcador para cliente."""
        widget = MapaWidget(self.mock_parent)
        
        ubicacion_cliente = self.sample_locations[1]  # Cliente A
        
        # Mock de la librería folium
        with patch('folium.Marker') as mock_marker:
            resultado = widget.crear_marcador(ubicacion_cliente)
            
            if hasattr(widget, 'folium_available') and widget.folium_available:
                mock_marker.assert_called_once()
                assert resultado is not None
            else:
                assert isinstance(resultado, dict)
                assert resultado['tipo'] == 'cliente'
    
    def test_calcular_ruta_exitoso(self):
        """Test cálculo de ruta exitoso."""
        widget = MapaWidget(self.mock_parent)
        widget.cargar_ubicaciones(self.sample_locations)
        
        origen = self.sample_locations[0]
        destino = self.sample_locations[1]
        
        # Mock del servicio de rutas
        with patch.object(widget, 'calcular_ruta_servicio') as mock_servicio:
            mock_servicio.return_value = self.sample_routes[0]
            
            with patch.object(widget.route_calculated, 'emit') as mock_signal:
                resultado = widget.calcular_ruta(origen['id'], destino['id'])
                
                # Verificar resultado
                assert resultado is not None
                assert resultado['distancia_km'] == 2.5
                
                # Verificar señal emitida
                mock_signal.assert_called_once_with(resultado)
    
    def test_calcular_ruta_sin_ubicaciones(self):
        """Test cálculo de ruta sin ubicaciones válidas."""
        widget = MapaWidget(self.mock_parent)
        
        resultado = widget.calcular_ruta(999, 998)  # IDs inexistentes
        
        # Debería retornar None o dict vacío
        assert resultado is None or resultado == {}
    
    def test_calcular_ruta_servicio_mock(self):
        """Test servicio de cálculo de rutas (mock)."""
        widget = MapaWidget(self.mock_parent)
        
        lat_origen, lon_origen = -34.6037, -58.3816
        lat_destino, lon_destino = -34.6118, -58.3960
        
        # Simular cálculo sin servicios externos
        resultado = widget.calcular_ruta_servicio(
            lat_origen, lon_origen, lat_destino, lon_destino
        )
        
        # Verificar estructura del resultado
        assert isinstance(resultado, dict)
        assert 'distancia_km' in resultado
        assert 'tiempo_estimado' in resultado
        assert 'coordenadas' in resultado
    
    def test_buscar_ubicacion_existente(self):
        """Test búsqueda de ubicación existente."""
        widget = MapaWidget(self.mock_parent)
        widget.cargar_ubicaciones(self.sample_locations)
        
        # Buscar por nombre
        resultado = widget.buscar_ubicacion("Almacén Principal")
        
        assert resultado is not None
        assert resultado['nombre'] == 'Almacén Principal'
        assert resultado['tipo'] == 'almacen'
    
    def test_buscar_ubicacion_inexistente(self):
        """Test búsqueda de ubicación inexistente."""
        widget = MapaWidget(self.mock_parent)
        widget.cargar_ubicaciones(self.sample_locations)
        
        resultado = widget.buscar_ubicacion("Ubicación Inexistente")
        
        assert resultado is None
    
    def test_buscar_ubicacion_parcial(self):
        """Test búsqueda parcial de ubicación."""
        widget = MapaWidget(self.mock_parent)
        widget.cargar_ubicaciones(self.sample_locations)
        
        # Buscar por texto parcial
        resultados = widget.buscar_ubicaciones_parcial("Cliente")
        
        assert len(resultados) == 1
        assert resultados[0]['nombre'] == 'Cliente A'
    
    def test_centrar_mapa_ubicacion(self):
        """Test centrar mapa en ubicación."""
        widget = MapaWidget(self.mock_parent)
        
        ubicacion = self.sample_locations[0]
        
        # Mock del método de centrado
        with patch.object(widget, 'update_map_center') as mock_center:
            widget.centrar_mapa(ubicacion['lat'], ubicacion['lon'])
            
            mock_center.assert_called_once_with(ubicacion['lat'], ubicacion['lon'])
    
    def test_toggle_traffic_activar(self):
        """Test activar capa de tráfico."""
        widget = MapaWidget(self.mock_parent)
        
        # Activar tráfico
        with patch.object(widget, 'mostrar_capa_trafico') as mock_traffic:
            widget.toggle_traffic(True)
            
            assert widget.traffic_enabled is True
            mock_traffic.assert_called_once_with(True)
    
    def test_toggle_traffic_desactivar(self):
        """Test desactivar capa de tráfico."""
        widget = MapaWidget(self.mock_parent)
        widget.traffic_enabled = True
        
        # Desactivar tráfico
        with patch.object(widget, 'mostrar_capa_trafico') as mock_traffic:
            widget.toggle_traffic(False)
            
            assert widget.traffic_enabled is False
            mock_traffic.assert_called_once_with(False)
    
    def test_zoom_in(self):
        """Test zoom in del mapa."""
        widget = MapaWidget(self.mock_parent)
        
        zoom_inicial = widget.current_zoom
        
        with patch.object(widget, 'update_zoom') as mock_zoom:
            widget.zoom_in()
            
            mock_zoom.assert_called_once_with(zoom_inicial + 1)
    
    def test_zoom_out(self):
        """Test zoom out del mapa."""
        widget = MapaWidget(self.mock_parent)
        
        zoom_inicial = widget.current_zoom
        
        with patch.object(widget, 'update_zoom') as mock_zoom:
            widget.zoom_out()
            
            mock_zoom.assert_called_once_with(zoom_inicial - 1)
    
    def test_zoom_limits(self):
        """Test límites de zoom."""
        widget = MapaWidget(self.mock_parent)
        
        # Test zoom mínimo
        widget.current_zoom = widget.MIN_ZOOM
        with patch.object(widget, 'update_zoom') as mock_zoom:
            widget.zoom_out()
            mock_zoom.assert_not_called()  # No debe hacer zoom out
        
        # Test zoom máximo
        widget.current_zoom = widget.MAX_ZOOM
        with patch.object(widget, 'update_zoom') as mock_zoom:
            widget.zoom_in()
            mock_zoom.assert_not_called()  # No debe hacer zoom in
    
    def test_seleccionar_ubicacion(self):
        """Test selección de ubicación."""
        widget = MapaWidget(self.mock_parent)
        widget.cargar_ubicaciones(self.sample_locations)
        
        ubicacion = self.sample_locations[0]
        
        with patch.object(widget.location_selected, 'emit') as mock_signal:
            widget.seleccionar_ubicacion(ubicacion)
            
            # Verificar selección
            assert widget.selected_location == ubicacion
            
            # Verificar señal emitida
            mock_signal.assert_called_once_with(ubicacion['lat'], ubicacion['lon'])
    
    def test_limpiar_seleccion(self):
        """Test limpiar selección."""
        widget = MapaWidget(self.mock_parent)
        widget.selected_location = self.sample_locations[0]
        
        widget.limpiar_seleccion()
        
        assert widget.selected_location is None
    
    def test_exportar_mapa_sin_datos(self):
        """Test exportación sin datos."""
        widget = MapaWidget(self.mock_parent)
        
        with patch('rexus.modules.logistica.components.mapa_widget.QMessageBox') as mock_msgbox:
            widget.exportar_mapa()
            
            mock_msgbox.warning.assert_called_once_with(
                widget, "Exportar", "No hay datos del mapa para exportar"
            )
    
    def test_exportar_mapa_con_datos(self):
        """Test exportación con datos."""
        widget = MapaWidget(self.mock_parent)
        widget.cargar_ubicaciones(self.sample_locations)
        
        with patch('rexus.modules.logistica.components.mapa_widget.QMessageBox') as mock_msgbox, \
             patch.object(widget, 'save_map_html', return_value=True) as mock_save:
            
            widget.exportar_mapa()
            
            mock_save.assert_called_once()
            mock_msgbox.information.assert_called_once_with(
                widget, "Exportar", "Mapa exportado exitosamente"
            )
    
    def test_refresh_data_sin_controlador(self):
        """Test actualización sin controlador."""
        widget = MapaWidget(self.mock_parent)
        
        with patch.object(widget, 'cargar_datos_ejemplo') as mock_ejemplo:
            widget.refresh_data()
            mock_ejemplo.assert_called_once()
    
    def test_refresh_data_con_controlador(self):
        """Test actualización con controlador."""
        mock_parent = Mock()
        mock_controller = Mock()
        mock_controller.get_ubicaciones_logistica.return_value = self.sample_locations
        mock_parent.controller = mock_controller
        
        widget = MapaWidget(mock_parent)
        
        widget.refresh_data()
        
        mock_controller.get_ubicaciones_logistica.assert_called_once()
        assert widget.locations == self.sample_locations
    
    def test_refresh_data_error_controlador(self):
        """Test error en controlador."""
        mock_parent = Mock()
        mock_controller = Mock()
        mock_controller.get_ubicaciones_logistica.side_effect = Exception("Error de conexión")
        mock_parent.controller = mock_controller
        
        widget = MapaWidget(mock_parent)
        
        with patch.object(widget.error_occurred, 'emit') as mock_error:
            widget.refresh_data()
            
            mock_error.assert_called_once()
    
    def test_calcular_distancia_haversine(self):
        """Test cálculo de distancia usando fórmula de Haversine."""
        widget = MapaWidget(self.mock_parent)
        
        # Buenos Aires a La Plata (aproximadamente)
        lat1, lon1 = -34.6037, -58.3816
        lat2, lon2 = -34.9214, -57.9544
        
        distancia = widget.calcular_distancia_haversine(lat1, lon1, lat2, lon2)
        
        # La distancia debería ser aproximadamente 56 km
        assert 50 <= distancia <= 65
    
    def test_generar_datos_ejemplo(self):
        """Test generación de datos de ejemplo."""
        widget = MapaWidget(self.mock_parent)
        
        widget.cargar_datos_ejemplo()
        
        # Verificar que se generaron ubicaciones
        assert len(widget.locations) > 0
        assert len(widget.map_data) > 0
        
        # Verificar estructura de ubicaciones
        primera_ubicacion = widget.locations[0]
        assert 'lat' in primera_ubicacion
        assert 'lon' in primera_ubicacion
        assert 'nombre' in primera_ubicacion
        assert 'tipo' in primera_ubicacion
    
    def test_validar_coordenadas_validas(self):
        """Test validación de coordenadas válidas."""
        widget = MapaWidget(self.mock_parent)
        
        # Coordenadas válidas (Buenos Aires)
        assert widget.validar_coordenadas(-34.6037, -58.3816) is True
        
        # Coordenadas en el límite
        assert widget.validar_coordenadas(-90, -180) is True
        assert widget.validar_coordenadas(90, 180) is True
    
    def test_validar_coordenadas_invalidas(self):
        """Test validación de coordenadas inválidas."""
        widget = MapaWidget(self.mock_parent)
        
        # Coordenadas fuera de rango
        assert widget.validar_coordenadas(-91, -58) is False
        assert widget.validar_coordenadas(91, -58) is False
        assert widget.validar_coordenadas(-34, -181) is False
        assert widget.validar_coordenadas(-34, 181) is False
    
    def test_signals_emitted(self):
        """Test que las señales se emiten correctamente."""
        widget = MapaWidget(self.mock_parent)
        
        # Mock signal connections
        with patch.object(widget.location_selected, 'emit') as mock_location, \
             patch.object(widget.route_calculated, 'emit') as mock_route:
            
            # Simular selección de ubicación
            ubicacion = self.sample_locations[0]
            widget.seleccionar_ubicacion(ubicacion)
            mock_location.assert_called_once()
            
            # Simular cálculo de ruta
            with patch.object(widget, 'calcular_ruta_servicio', return_value=self.sample_routes[0]):
                widget.calcular_ruta(1, 2)
                mock_route.assert_called_once()


class TestMapaWidgetIntegration:
    """Tests de integración para MapaWidget."""
    
    @classmethod
    def setup_class(cls):
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
    
    def test_widget_creation_and_interaction(self):
        """Test creación e interacción del widget."""
        mock_parent = Mock()
        widget = MapaWidget(mock_parent)
        
        # Verificar creación
        assert widget.isVisible() is False
        
        # Cargar datos y mostrar
        widget.cargar_datos_ejemplo()
        widget.show()
        
        # Verificar que tiene datos
        assert len(widget.locations) > 0
        
        # Limpiar
        widget.hide()
    
    def test_location_search_integration(self):
        """Test integración de búsqueda de ubicaciones."""
        mock_parent = Mock()
        widget = MapaWidget(mock_parent)
        widget.cargar_ubicaciones(self.sample_locations)
        
        # Simular búsqueda
        widget.search_location.setText("Almacén")
        
        # Mock del método de búsqueda
        with patch.object(widget, 'on_search_changed') as mock_search:
            widget.search_location.textChanged.emit("Almacén")
            # La señal debería haberse conectado en la inicialización
            # Este test verifica la integración del componente de búsqueda
    
    def test_route_calculation_integration(self):
        """Test integración de cálculo de rutas."""
        mock_parent = Mock()
        widget = MapaWidget(mock_parent)
        widget.cargar_ubicaciones(self.sample_locations)
        
        # Seleccionar origen y destino
        origen = widget.locations[0]
        destino = widget.locations[1]
        
        widget.selected_location = origen
        
        # Mock del cálculo de ruta
        with patch.object(widget, 'calcular_ruta_servicio', return_value=self.sample_routes[0]):
            resultado = widget.calcular_ruta(origen['id'], destino['id'])
            
            assert resultado is not None
            assert 'distancia_km' in resultado


class TestMapaWidgetPerformance:
    """Tests de rendimiento para MapaWidget."""
    
    @classmethod
    def setup_class(cls):
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
    
    def test_large_locations_performance(self):
        """Test rendimiento con muchas ubicaciones."""
        mock_parent = Mock()
        widget = MapaWidget(mock_parent)
        
        # Generar muchas ubicaciones
        large_locations = []
        for i in range(1000):
            large_locations.append({
                'id': i,
                'nombre': f'Ubicación {i}',
                'tipo': 'punto',
                'lat': -34.6 + (i * 0.001),
                'lon': -58.4 + (i * 0.001),
                'direccion': f'Dirección {i}',
                'activo': True,
                'descripcion': f'Descripción {i}'
            })
        
        import time
        start_time = time.time()
        
        # Cargar ubicaciones
        widget.cargar_ubicaciones(large_locations)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Verificar rendimiento (menos de 2 segundos)
        assert duration < 2.0, f"Carga tardó {duration:.2f} segundos"
        assert len(widget.locations) == 1000


if __name__ == '__main__':
    pytest.main([__file__, '-v'])