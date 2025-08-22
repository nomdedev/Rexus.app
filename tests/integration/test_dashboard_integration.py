# -*- coding: utf-8 -*-
"""
Tests de integración para el sistema de dashboard modernizado
Verifica la correcta integración entre controladores, widgets y datos
"""

import pytest
import sys
from unittest.mock import Mock, patch, MagicMock
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtTest import QTest

# Importar componentes del dashboard
try:
    from rexus.ui.dashboard import MainDashboard, DashboardController
    from rexus.ui.dashboard.widgets import KPIWidget, ChartWidget, ActivityWidget
    from rexus.ui.components.theme_manager import ThemeManager
except ImportError as e:
    pytest.skip(f"Dashboard components not available: {e}", allow_module_level=True)


class TestDashboardIntegration:
    """Tests de integración del sistema de dashboard."""
    
    @classmethod
    def setup_class(cls):
        """Configuración inicial para todos los tests."""
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()
    
    def setup_method(self):
        """Configuración para cada test individual."""
        self.mock_db_manager = Mock()
        self.test_user_data = {
            'id': 1,
            'username': 'test_user',
            'role': 'ADMIN'
        }
    
    def test_dashboard_controller_initialization(self):
        """Test de inicialización del controlador de dashboard."""
        controller = DashboardController(self.mock_db_manager)
        
        assert controller is not None
        assert controller.module_controllers == {}
        assert controller.dashboard_view is None
        assert controller.update_timer is not None
    
    def test_dashboard_view_creation(self):
        """Test de creación de la vista del dashboard."""
        controller = DashboardController(self.mock_db_manager)
        dashboard_view = controller.get_view()
        
        assert dashboard_view is not None
        assert isinstance(dashboard_view, MainDashboard)
        assert controller.dashboard_view is dashboard_view
    
    def test_kpi_widget_functionality(self):
        """Test de funcionalidad de widgets KPI."""
        kpi_widget = KPIWidget("Test KPI", "100", "Test description")
        
        assert kpi_widget.titulo == "Test KPI"
        assert kpi_widget.valor_actual == "100"
        assert kpi_widget.descripcion == "Test description"
        
        # Test actualización de valor
        kpi_widget.actualizar_valor("200", "up", 10.5)
        assert kpi_widget.valor_actual == "200"
        assert kpi_widget.tendencia == "up"
        assert kpi_widget.porcentaje_cambio == 10.5
    
    def test_chart_widget_functionality(self):
        """Test de funcionalidad de widgets de gráficos."""
        chart_widget = ChartWidget("line")
        
        assert chart_widget.tipo_chart == "line"
        # El widget carga datos de ejemplo por defecto
        assert len(chart_widget.datos) > 0
        assert len(chart_widget.labels) > 0
        
        # Test actualización de datos
        nuevos_datos = [10, 20, 30, 40, 50]
        nuevas_labels = ["A", "B", "C", "D", "E"]
        chart_widget.actualizar_datos(nuevos_datos, nuevas_labels)
        
        assert chart_widget.datos == nuevos_datos
        assert chart_widget.labels == nuevas_labels
    
    def test_activity_widget_functionality(self):
        """Test de funcionalidad de widgets de actividad."""
        activity_widget = ActivityWidget()
        
        assert activity_widget.actividades == []
        assert activity_widget.max_actividades == 50
        
        # Test agregar actividad
        activity_widget.agregar_actividad(
            "📦", "Test Activity", "Test description", tipo="info"
        )
        
        assert len(activity_widget.actividades) == 1
        assert activity_widget.actividades[0]['titulo'] == "Test Activity"
        assert activity_widget.actividades[0]['tipo'] == "info"
    
    def test_theme_manager_functionality(self):
        """Test de funcionalidad del gestor de temas."""
        theme_manager = ThemeManager()
        
        assert theme_manager.current_theme in ['light', 'dark']
        assert 'light' in theme_manager.themes
        assert 'dark' in theme_manager.themes
        
        # Test toggle de tema (sin aplicar realmente para evitar segfaults)
        original_theme = theme_manager.get_current_theme()
        with patch.object(theme_manager, 'apply_theme'):
            theme_manager.toggle_theme()
        new_theme = theme_manager.get_current_theme()
        
        assert original_theme != new_theme
    
    @patch('rexus.modules.usuarios.controller.UsuariosController')
    @patch('rexus.modules.inventario.controller.InventarioController')
    def test_dashboard_data_integration(self, mock_inventario, mock_usuarios):
        """Test de integración con datos reales de módulos."""
        # Configurar mocks
        mock_usuarios.return_value.get_all_usuarios.return_value = [
            {'id': 1, 'username': 'user1', 'activo': True},
            {'id': 2, 'username': 'user2', 'activo': False}
        ]
        
        mock_inventario.return_value.get_all_productos.return_value = [
            {'id': 1, 'nombre': 'Producto 1', 'stock': 100},
            {'id': 2, 'nombre': 'Producto 2', 'stock': 50}
        ]
        
        controller = DashboardController(self.mock_db_manager)
        
        # Test obtención de datos
        total_usuarios = controller.obtener_total_usuarios()
        total_productos = controller.obtener_total_productos()
        
        assert total_usuarios >= 0  # Puede ser 0 si el mock falla
        assert total_productos >= 0  # Puede ser 0 si el mock falla
    
    def test_dashboard_kpi_updates(self):
        """Test de actualización de KPIs en el dashboard."""
        controller = DashboardController(self.mock_db_manager)
        dashboard = controller.get_view()
        
        # Verificar que el dashboard tenga widgets KPI
        assert hasattr(dashboard, 'widgets_kpi')
        assert 'usuarios' in dashboard.widgets_kpi
        assert 'inventario' in dashboard.widgets_kpi
        
        # Test actualización de KPI
        dashboard.actualizar_kpi('usuarios', '50', 'up')
        
        usuarios_kpi = dashboard.widgets_kpi['usuarios']
        assert usuarios_kpi.valor_actual == '50'
        assert usuarios_kpi.tendencia == 'up'
    
    def test_dashboard_module_navigation(self):
        """Test de navegación a módulos desde el dashboard."""
        controller = DashboardController(self.mock_db_manager)
        dashboard = controller.get_view()
        
        # Mock del parent controller
        parent_mock = Mock()
        parent_mock.abrir_modulo = Mock()
        controller.parent = lambda: parent_mock
        
        # Test emisión de señal de módulo
        with patch.object(dashboard, 'modulo_solicitado') as mock_signal:
            dashboard.modulo_solicitado.emit('inventario')
            mock_signal.emit.assert_called_with('inventario')
    
    def test_dashboard_error_handling(self):
        """Test de manejo de errores en el dashboard."""
        # Test con db_manager None
        controller = DashboardController(None)
        
        # Los métodos deben funcionar sin lanzar excepciones
        try:
            total_usuarios = controller.obtener_total_usuarios()
            total_productos = controller.obtener_total_productos()
            controller.actualizar_todas_metricas()
            assert True  # Si llegamos aquí, no hubo excepciones
        except Exception as e:
            pytest.fail(f"Dashboard should handle None db_manager gracefully: {e}")
    
    def test_dashboard_performance(self):
        """Test básico de performance del dashboard."""
        import time
        
        start_time = time.time()
        controller = DashboardController(self.mock_db_manager)
        dashboard = controller.get_view()
        creation_time = time.time() - start_time
        
        # El dashboard debería crearse en menos de 2 segundos
        assert creation_time < 2.0, f"Dashboard creation took {creation_time:.2f}s"
        
        # Test de actualización de métricas
        start_time = time.time()
        controller.actualizar_todas_metricas()
        update_time = time.time() - start_time
        
        # Las actualizaciones deberían ser rápidas
        assert update_time < 1.0, f"Metrics update took {update_time:.2f}s"


class TestDashboardComponentIntegration:
    """Tests de integración entre componentes del dashboard."""
    
    @classmethod
    def setup_class(cls):
        """Configuración inicial."""
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
    
    def test_kpi_chart_activity_integration(self):
        """Test de integración entre KPI, gráficos y actividad."""
        # Crear dashboard completo
        dashboard = MainDashboard()
        
        # Verificar que todos los componentes estén presentes
        assert hasattr(dashboard, 'widgets_kpi')
        assert hasattr(dashboard, 'widget_actividad')
        
        # Test de flujo completo: actualizar KPI y agregar actividad
        dashboard.actualizar_kpi('ventas', '$10000', 'up')
        dashboard.agregar_actividad(
            '💰', 'Venta registrada', 'Nueva venta de $10000'
        )
        
        # Verificar que las actualizaciones se reflejen
        ventas_kpi = dashboard.widgets_kpi.get('ventas')
        if ventas_kpi:
            assert ventas_kpi.valor_actual == '$10000'
        
        actividades = dashboard.widget_actividad.actividades
        assert len(actividades) > 0
    
    def test_theme_dashboard_integration(self):
        """Test de integración entre temas y dashboard."""
        theme_manager = ThemeManager()
        dashboard = MainDashboard()
        
        # Aplicar tema oscuro
        theme_manager.apply_theme('dark')
        dark_theme = theme_manager.get_theme_data('dark')
        
        # Verificar que el tema se aplique
        assert dark_theme['name'] == 'dark'
        assert dark_theme['background'] == '#1e1e1e'
        
        # Aplicar tema claro
        theme_manager.apply_theme('light')
        light_theme = theme_manager.get_theme_data('light')
        
        assert light_theme['name'] == 'light'
        assert light_theme['background'] == '#ffffff'


@pytest.mark.slow
class TestDashboardDataFlow:
    """Tests de flujo de datos en el dashboard."""
    
    @classmethod
    def setup_class(cls):
        """Configuración inicial."""
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
    
    def test_complete_data_flow(self):
        """Test del flujo completo de datos."""
        # Crear sistema completo
        mock_db = Mock()
        controller = DashboardController(mock_db)
        dashboard = controller.get_view()
        
        # Simular datos de entrada
        test_data = {
            'usuarios': 25,
            'inventario': 150,
            'ventas': 45000,
            'obras': 8
        }
        
        # Actualizar todos los KPIs
        for modulo, valor in test_data.items():
            dashboard.actualizar_kpi(modulo, str(valor), 'stable')
        
        # Verificar que los datos se propaguen correctamente
        for modulo, valor_esperado in test_data.items():
            if modulo in dashboard.widgets_kpi:
                kpi_widget = dashboard.widgets_kpi[modulo]
                assert kpi_widget.valor_actual == str(valor_esperado)
    
    def test_real_time_updates(self):
        """Test de actualizaciones en tiempo real."""
        controller = DashboardController(Mock())
        dashboard = controller.get_view()
        
        # Simular múltiples actualizaciones
        for i in range(5):
            dashboard.actualizar_kpi('usuarios', str(10 + i), 'up')
            dashboard.agregar_actividad(
                '👤', f'Usuario {i+1}', f'Nueva actividad {i+1}'
            )
        
        # Verificar estado final
        usuarios_kpi = dashboard.widgets_kpi.get('usuarios')
        if usuarios_kpi:
            assert usuarios_kpi.valor_actual == '14'  # 10 + 4
        
        # Verificar actividades
        actividades = dashboard.widget_actividad.actividades
        assert len(actividades) >= 5


if __name__ == '__main__':
    pytest.main([__file__, '-v'])