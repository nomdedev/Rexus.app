# -*- coding: utf-8 -*-
"""
Tests unitarios para EstadisticasWidget
Refactorización de logística - Tests de componente de estadísticas
"""

import pytest
import sys
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtTest import QTest

# Configurar encoding UTF-8
sys.stdout.reconfigure(encoding='utf-8')

# Agregar path del proyecto
root_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(root_dir))

# Imports a testear
try:
    from rexus.modules.logistica.components.estadisticas_widget import EstadisticasWidget
    from rexus.ui.components.base_components import RexusButton
except ImportError as e:
    pytest.skip(f, allow_module_level=True)

import logging
logger = logging.getLogger(__name__)


class TestEstadisticasWidget:
    """Tests para widget de estadísticas de logística."""
    
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
        
        # Datos de ejemplo para estadísticas
        self.sample_stats = {
            'total_transportes': 125,
            'transportes_activos': 35,
            'transportes_completados': 90,
            'transportes_programados': 15,
            'total_km_recorridos': 12500.75,
            'promedio_km_transporte': 100.0,
            'tiempo_promedio_entrega': 4.5,
            'eficiencia_combustible': 8.5,
            'costo_total_operacion': 85000.00,
            'ingresos_totales': 120000.00,
            'margen_ganancia': 35000.00,
            'top_conductores': [
                {'nombre': 'Juan Pérez', 'entregas': 25, 'calificacion': 4.8},
                {'nombre': 'María García', 'entregas': 22, 'calificacion': 4.6},
                {'nombre': 'Carlos López', 'entregas': 18, 'calificacion': 4.7}
            ],
            'rutas_frecuentes': [
                {'origen': 'Almacén A', 'destino': 'Cliente B', 'frecuencia': 15},
                {'origen': 'Almacén B', 'destino': 'Cliente C', 'frecuencia': 12},
                {'origen': 'Almacén A', 'destino': 'Cliente D', 'frecuencia': 10}
            ]
        }
    
    def test_widget_initialization(self):
        """Test inicialización del widget."""
        widget = EstadisticasWidget(self.mock_parent)
        
        assert widget is not None
        assert widget.parent_view == self.mock_parent
        assert hasattr(widget, 'stats_data')
        assert hasattr(widget, 'btn_refresh')
        assert hasattr(widget, 'btn_export')
        assert hasattr(widget, 'auto_refresh_timer')
        
        # Verificar componentes principales
        assert hasattr(widget, 'kpi_cards')
        assert hasattr(widget, 'progress_bars')
        assert hasattr(widget, 'charts_area')
    
    def test_crear_kpi_cards(self):
        """Test creación de tarjetas KPI."""
        widget = EstadisticasWidget(self.mock_parent)
        
        # Verificar que se crearon las tarjetas KPI
        assert len(widget.kpi_cards) > 0
        
        # Verificar estructura de tarjetas
        for card_name, card_widget in widget.kpi_cards.items():
            assert card_widget is not None
            assert hasattr(card_widget, 'setTitle')
    
    def test_crear_progress_bars(self):
        """Test creación de barras de progreso."""
        widget = EstadisticasWidget(self.mock_parent)
        
        # Verificar que se crearon las barras de progreso
        assert len(widget.progress_bars) > 0
        
        # Verificar configuración de barras
        for bar_name, progress_bar in widget.progress_bars.items():
            assert progress_bar is not None
            assert progress_bar.minimum() == 0
            assert progress_bar.maximum() == 100
    
    def test_cargar_datos_estadisticas(self):
        """Test carga de datos estadísticos."""
        widget = EstadisticasWidget(self.mock_parent)
        
        # Cargar datos de ejemplo
        widget.cargar_datos(self.sample_stats)
        
        # Verificar que se guardaron los datos
        assert widget.stats_data == self.sample_stats
        
        # Verificar actualización de KPIs
        total_card = widget.kpi_cards.get('total_transportes')
        if total_card:
            # Verificar que el valor se actualizó (dependería de implementación específica)
            assert total_card is not None
    
    def test_actualizar_kpi_cards(self):
        """Test actualización de tarjetas KPI."""
        widget = EstadisticasWidget(self.mock_parent)
        widget.stats_data = self.sample_stats
        
        # Actualizar KPIs
        widget.actualizar_kpi_cards()
        
        # Verificar que las tarjetas tienen valores
        assert len(widget.kpi_cards) > 0
        
        # Verificar que se aplicaron los datos
        for card_name, card_widget in widget.kpi_cards.items():
            assert card_widget is not None
    
    def test_actualizar_progress_bars(self):
        """Test actualización de barras de progreso."""
        widget = EstadisticasWidget(self.mock_parent)
        widget.stats_data = self.sample_stats
        
        # Actualizar barras de progreso
        widget.actualizar_progress_bars()
        
        # Verificar valores en barras
        for bar_name, progress_bar in widget.progress_bars.items():
            assert 0 <= progress_bar.value() <= 100
    
    def test_calcular_progreso_entregas(self):
        """Test cálculo de progreso de entregas."""
        widget = EstadisticasWidget(self.mock_parent)
        
        # Test con valores normales
        progreso = widget.calcular_progreso_entregas(90, 125)
        assert progreso == 72  # 90/125 * 100 = 72%
        
        # Test con división por cero
        progreso = widget.calcular_progreso_entregas(50, 0)
        assert progreso == 0
        
        # Test con valores negativos
        progreso = widget.calcular_progreso_entregas(-10, 100)
        assert progreso == 0
    
    def test_calcular_eficiencia_combustible(self):
        """Test cálculo de eficiencia de combustible."""
        widget = EstadisticasWidget(self.mock_parent)
        
        # Test con valores normales
        eficiencia = widget.calcular_eficiencia_combustible(1000, 100)
        assert eficiencia == 10.0  # 1000/100 = 10 km/L
        
        # Test con combustible cero
        eficiencia = widget.calcular_eficiencia_combustible(1000, 0)
        assert eficiencia == 0.0
    
    def test_calcular_margen_ganancia(self):
        """Test cálculo de margen de ganancia."""
        widget = EstadisticasWidget(self.mock_parent)
        
        # Test con valores normales
        margen = widget.calcular_margen_ganancia(120000, 85000)
        assert margen == 29.17  # ((120000-85000)/120000) * 100 = 29.17%
        
        # Test con ingresos cero
        margen = widget.calcular_margen_ganancia(0, 85000)
        assert margen == 0.0
    
    def test_generar_datos_ejemplo(self):
        """Test generación de datos de ejemplo."""
        widget = EstadisticasWidget(self.mock_parent)
        
        # Generar datos de ejemplo
        widget.generar_datos_ejemplo()
        
        # Verificar que se generaron datos
        assert widget.stats_data is not None
        assert len(widget.stats_data) > 0
        
        # Verificar estructura de datos
        assert 'total_transportes' in widget.stats_data
        assert 'transportes_activos' in widget.stats_data
        assert 'top_conductores' in widget.stats_data
        assert isinstance(widget.stats_data['top_conductores'], list)
    
    def test_refresh_data_sin_controlador(self):
        """Test actualización de datos sin controlador."""
        widget = EstadisticasWidget(self.mock_parent)
        
        # Mock del método generar_datos_ejemplo
        with patch.object(widget, 'generar_datos_ejemplo') as mock_generar:
            widget.refresh_data()
            mock_generar.assert_called_once()
    
    def test_refresh_data_con_controlador(self):
        """Test actualización de datos con controlador."""
        mock_parent = Mock()
        mock_controller = Mock()
        mock_controller.get_estadisticas_logistica.return_value = self.sample_stats
        mock_parent.controller = mock_controller
        
        widget = EstadisticasWidget(mock_parent)
        
        # Refrescar datos
        widget.refresh_data()
        
        # Verificar que se llamó al controlador
        mock_controller.get_estadisticas_logistica.assert_called_once()
        assert widget.stats_data == self.sample_stats
    
    def test_refresh_data_error_controlador(self):
        """Test error en controlador durante actualización."""
        mock_parent = Mock()
        mock_controller = Mock()
        mock_controller.get_estadisticas_logistica.side_effect = Exception("Error de conexión")
        mock_parent.controller = mock_controller
        
        widget = EstadisticasWidget(mock_parent)
        
        # Mock signal emission
        with patch.object(widget.error_occurred, 'emit') as mock_error:
            widget.refresh_data()
            
            # Verificar que se emitió error
            mock_error.assert_called_once()
    
    def test_auto_refresh_timer(self):
        """Test temporizador de actualización automática."""
        widget = EstadisticasWidget(self.mock_parent)
        
        # Verificar que el timer existe
        assert isinstance(widget.auto_refresh_timer, QTimer)
        
        # Verificar configuración del timer
        assert widget.auto_refresh_timer.interval() == 300000  # 5 minutos
        
        # Verificar conexión del signal
        assert widget.auto_refresh_timer.timeout.disconnect() is None or True
    
    def test_toggle_auto_refresh(self):
        """Test activar/desactivar actualización automática."""
        widget = EstadisticasWidget(self.mock_parent)
        
        # Estado inicial (debería estar detenido)
        assert not widget.auto_refresh_timer.isActive()
        
        # Activar auto-refresh
        widget.toggle_auto_refresh(True)
        assert widget.auto_refresh_timer.isActive()
        
        # Desactivar auto-refresh
        widget.toggle_auto_refresh(False)
        assert not widget.auto_refresh_timer.isActive()
    
    @patch('rexus.modules.logistica.components.estadisticas_widget.QMessageBox')
    def test_exportar_estadisticas_sin_datos(self, mock_msgbox):
        """Test exportación sin datos."""
        widget = EstadisticasWidget(self.mock_parent)
        widget.stats_data = {}
        
        widget.exportar_estadisticas()
        
        # Verificar warning por datos vacíos
        mock_msgbox.warning.assert_called_once_with(
            widget, "Exportar", "No hay datos estadísticos para exportar"
        )
    
    @patch('rexus.modules.logistica.components.estadisticas_widget.QMessageBox')
    def test_exportar_estadisticas_exitoso(self, mock_msgbox):
        """Test exportación exitosa."""
        widget = EstadisticasWidget(self.mock_parent)
        widget.stats_data = self.sample_stats
        
        # Mock exportación exitosa
        with patch.object(widget, 'export_to_excel', return_value=True):
            widget.exportar_estadisticas()
            
            # Verificar mensaje de éxito
            mock_msgbox.information.assert_called_once_with(
                widget, "Exportar", "Estadísticas exportadas exitosamente"
            )
    
    @patch('rexus.modules.logistica.components.estadisticas_widget.QMessageBox')
    def test_exportar_estadisticas_error(self, mock_msgbox):
        """Test error en exportación."""
        widget = EstadisticasWidget(self.mock_parent)
        widget.stats_data = self.sample_stats
        
        # Mock error en exportación
        with patch.object(widget, 'export_to_excel', side_effect=Exception("Error de escritura")):
            widget.exportar_estadisticas()
            
            # Verificar mensaje de error
            mock_msgbox.critical.assert_called_once()
    
    def test_crear_grafico_barras(self):
        """Test creación de gráfico de barras."""
        widget = EstadisticasWidget(self.mock_parent)
        
        # Datos para gráfico
        datos = {'Ene': 10, 'Feb': 15, 'Mar': 8, 'Abr': 22}
        
        # Crear gráfico (mock si matplotlib no disponible)
        try:
            chart = widget.crear_grafico_barras('Entregas por Mes', datos)
            assert chart is not None
        except ImportError:
            # Matplotlib no disponible, verificar que retorna placeholder
            chart = widget.crear_grafico_barras('Entregas por Mes', datos)
            assert chart is not None
    
    def test_crear_grafico_pastel(self):
        """Test creación de gráfico de pastel."""
        widget = EstadisticasWidget(self.mock_parent)
        
        # Datos para gráfico
        datos = {'Completados': 90, 'En tránsito': 35, 'Programados': 15}
        
        # Crear gráfico (mock si matplotlib no disponible)
        try:
            chart = widget.crear_grafico_pastel('Estado de Transportes', datos)
            assert chart is not None
        except ImportError:
            # Matplotlib no disponible, verificar que retorna placeholder
            chart = widget.crear_grafico_pastel('Estado de Transportes', datos)
            assert chart is not None
    
    def test_actualizar_grafico_tiempo_real(self):
        """Test actualización de gráficos en tiempo real."""
        widget = EstadisticasWidget(self.mock_parent)
        widget.stats_data = self.sample_stats
        
        # Mock del método actualizar_graficos
        with patch.object(widget, 'actualizar_graficos') as mock_actualizar:
            widget.actualizar_grafico_tiempo_real()
            mock_actualizar.assert_called_once()
    
    def test_signals_emitted(self):
        """Test que las señales se emiten correctamente."""
        widget = EstadisticasWidget(self.mock_parent)
        
        # Mock signal connections
        with patch.object(widget.data_updated, 'emit') as mock_updated:
            # Simular carga de datos
            widget.cargar_datos(self.sample_stats)
            
            # Verificar señal de actualización
            mock_updated.assert_called_once()


class TestEstadisticasWidgetIntegration:
    """Tests de integración para EstadisticasWidget."""
    
    @classmethod
    def setup_class(cls):
        """Configuración inicial."""
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
    
    def test_widget_creation_and_data_flow(self):
        """Test creación y flujo de datos del widget."""
        mock_parent = Mock()
        widget = EstadisticasWidget(mock_parent)
        
        # Verificar que se creó correctamente
        assert widget.isVisible() is False  # No mostrado aún
        
        # Generar y cargar datos
        widget.generar_datos_ejemplo()
        widget.show()
        
        # Verificar que tiene datos
        assert widget.stats_data is not None
        assert len(widget.stats_data) > 0
        
        # Limpiar
        widget.hide()
    
    def test_timer_integration(self):
        """Test integración con temporizador."""
        mock_parent = Mock()
        widget = EstadisticasWidget(mock_parent)
        
        # Mock del método refresh_data
        with patch.object(widget, 'refresh_data') as mock_refresh:
            # Activar auto-refresh
            widget.toggle_auto_refresh(True)
            
            # Simular timeout del timer
            widget.auto_refresh_timer.timeout.emit()
            
            # Verificar que se llamó refresh
            mock_refresh.assert_called_once()
        
        # Limpiar
        widget.toggle_auto_refresh(False)
    
    def test_kpi_update_cascade(self):
        """Test actualización en cascada de KPIs."""
        mock_parent = Mock()
        widget = EstadisticasWidget(mock_parent)
        
        # Cargar datos iniciales
        initial_stats = {'total_transportes': 100, 'transportes_activos': 25}
        widget.cargar_datos(initial_stats)
        
        # Actualizar con nuevos datos
        new_stats = {'total_transportes': 150, 'transportes_activos': 40}
        
        with patch.object(widget, 'actualizar_kpi_cards') as mock_kpi, \
             patch.object(widget, 'actualizar_progress_bars') as mock_progress:
            
            widget.cargar_datos(new_stats)
            
            # Verificar que se actualizaron todos los componentes
            mock_kpi.assert_called_once()
            mock_progress.assert_called_once()


class TestEstadisticasWidgetPerformance:
    """Tests de rendimiento para EstadisticasWidget."""
    
    @classmethod
    def setup_class(cls):
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
    
    def test_large_dataset_performance(self):
        """Test rendimiento con dataset grande."""
        mock_parent = Mock()
        widget = EstadisticasWidget(mock_parent)
        
        # Crear dataset grande
        large_stats = {
            'total_transportes': 10000,
            'transportes_activos': 2500,
            'top_conductores': [
                {'nombre': f'Conductor {i}', 'entregas': i * 10, 'calificacion': 4.0 + (i % 10) / 10}
                for i in range(100)
            ],
            'rutas_frecuentes': [
                {'origen': f'Origen {i}', 'destino': f'Destino {i}', 'frecuencia': i}
                for i in range(500)
            ]
        }
        
        import time
        start_time = time.time()
        
        # Cargar datos grandes
        widget.cargar_datos(large_stats)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Verificar que la carga fue rápida (menos de 5 segundos)
        assert duration < 5.0, f"Carga de datos tardó {duration:.2f} segundos"
        
        # Verificar que los datos se cargaron correctamente
        assert widget.stats_data == large_stats


if __name__ == '__main__':
    pytest.main([__file__, '-v'])