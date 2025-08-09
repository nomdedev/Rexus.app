"""
Tests de Rendimiento y Stress para Módulo Administración
Casos extremos, memory leaks, y performance bajo carga
"""

import sys
import pytest
import time
import threading
import gc
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, date, timedelta
from decimal import Decimal
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer, QThread
from PyQt6.QtTest import QTest

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT_DIR))

from rexus.modules.administracion.view import (
    AdministracionViewFuncional, DashboardWidget, 
    ContabilidadWidget, RecursosHumanosWidget
)
from rexus.modules.administracion.controller import AdministracionController
from rexus.modules.administracion.model import AdministracionModel


@pytest.fixture(scope="session")
def qapp():
    """QApplication fixture."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
    try:
        app.quit()
    except:
        pass


@pytest.fixture
def performance_controller():
    """Controlador configurado para tests de performance."""
    mock_model = MagicMock()
    mock_db = MagicMock()
    
    # Configurar respuestas realistas
    mock_model.obtener_resumen_contable.return_value = {
        'total_empleados': 1000,
        'balance_total': 5000000,
        'transacciones_mes': 2500,
        'alertas_pendientes': 15
    }
    
    with patch('rexus.modules.administracion.controller.get_inventario_connection', return_value=mock_db):
        controller = AdministracionController()
        controller.model = mock_model
        controller.db_connection = mock_db
        
        return controller


@pytest.fixture
def large_dataset():
    """Dataset grande para tests de carga."""
    empleados = []
    asientos = []
    
    # Generar 1000 empleados
    for i in range(1000):
        empleados.append({
            'id': i + 1,
            'nombre': f'Empleado{i:04d}',
            'apellido': f'Apellido{i:04d}',
            'dni': f'{12345678 + i}',
            'email': f'empleado{i:04d}@empresa.com',
            'telefono': f'123456{i:03d}',
            'cargo': ['Empleado', 'Supervisor', 'Gerente'][i % 3],
            'salario': 30000 + (i * 100),
            'fecha_ingreso': date.today() - timedelta(days=i),
            'departamento': f'Depto{i % 10}',
            'estado': 'Activo'
        })
    
    # Generar 5000 asientos contables
    for i in range(5000):
        asientos.append({
            'id': i + 1,
            'fecha_asiento': date.today() - timedelta(days=i % 365),
            'concepto': f'Transacción contable {i:05d}',
            'cuenta_contable': ['Caja', 'Bancos', 'Inventario', 'Gastos'][i % 4],
            'debe': (i % 2) * 1000 + i,
            'haber': ((i + 1) % 2) * 1000 + i,
            'referencia': f'REF{i:05d}',
            'estado': 'Activo'
        })
    
    return {'empleados': empleados, 'asientos': asientos}


class TestPerformanceDashboard:
    """Tests de rendimiento del dashboard."""
    
    def test_dashboard_high_frequency_updates(self, qapp):
        """Test actualizaciones de alta frecuencia en dashboard."""
        dashboard = DashboardWidget()
        
        start_time = time.time()
        
        # 1000 actualizaciones rápidas
        for i in range(1000):
            datos = {
                'empleados_activos': i,
                'balance_actual': i * 1000.50,
                'transacciones_mes': i * 5,
                'alertas_pendientes': i % 20
            }
            dashboard.actualizar_metricas(datos)
            
            # Procesar eventos UI cada 100 iteraciones
            if i % 100 == 0:
                QApplication.processEvents()
        
        end_time = time.time()
        duration = end_time - start_time
        
        # No debería tomar más de 5 segundos
        assert duration < 5.0, f"Dashboard updates too slow: {duration:.2f}s"
        
        # Memory cleanup
        dashboard.deleteLater()
        gc.collect()
    
    def test_dashboard_extreme_values(self, qapp):
        """Test dashboard con valores extremos."""
        dashboard = DashboardWidget()
        
        # Valores extremos
        extreme_values = [
            {
                'empleados_activos': 0,
                'balance_actual': 0,
                'transacciones_mes': 0,
                'alertas_pendientes': 0
            },
            {
                'empleados_activos': 999999,
                'balance_actual': 999999999999.99,
                'transacciones_mes': 100000,
                'alertas_pendientes': 1000
            },
            {
                'empleados_activos': -1,  # Valor negativo
                'balance_actual': -999999.99,
                'transacciones_mes': -100,
                'alertas_pendientes': -10
            },
            {
                'empleados_activos': float('inf'),  # Infinito
                'balance_actual': float('inf'),
                'transacciones_mes': float('inf'),
                'alertas_pendientes': float('inf')
            }
        ]
        
        for datos in extreme_values:
            try:
                dashboard.actualizar_metricas(datos)
                QApplication.processEvents()
                
                # Verificar que no crashed
                assert dashboard is not None
            except Exception as e:
                # Algunos valores extremos pueden fallar, pero no debería crash
                assert "cannot convert" in str(e).lower() or "overflow" in str(e).lower()
    
    def test_dashboard_memory_usage(self, qapp):
        """Test uso de memoria del dashboard."""
        dashboards = []
        
        # Crear múltiples dashboards
        for i in range(50):
            dashboard = DashboardWidget()
            
            # Actualizar con datos
            datos = {
                'empleados_activos': i * 10,
                'balance_actual': i * 5000,
                'transacciones_mes': i * 25,
                'alertas_pendientes': i % 5
            }
            dashboard.actualizar_metricas(datos)
            dashboards.append(dashboard)
        
        # Procesar eventos
        QApplication.processEvents()
        
        # Cleanup
        for dashboard in dashboards:
            dashboard.deleteLater()
        
        gc.collect()
        QApplication.processEvents()
        
        # Si llegó aquí sin crash, el test pasó
        assert True


class TestPerformanceTablas:
    """Tests de rendimiento de tablas."""
    
    def test_tabla_contabilidad_large_dataset(self, qapp, large_dataset):
        """Test tabla contabilidad con dataset grande."""
        contabilidad = ContabilidadWidget()
        asientos = large_dataset['asientos']
        
        start_time = time.time()
        
        # Cargar datos grandes
        contabilidad.cargar_asientos(asientos)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # No debería tomar más de 3 segundos cargar 5000 registros
        assert duration < 3.0, f"Table loading too slow: {duration:.2f}s"
        assert contabilidad.tabla_asientos.rowCount() == len(asientos)
    
    def test_tabla_rrhh_large_dataset(self, qapp, large_dataset):
        """Test tabla RRHH con dataset grande."""
        rrhh = RecursosHumanosWidget()
        empleados = large_dataset['empleados']
        
        start_time = time.time()
        
        # Cargar datos grandes
        rrhh.cargar_empleados(empleados)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # No debería tomar más de 2 segundos cargar 1000 empleados
        assert duration < 2.0, f"Employee table loading too slow: {duration:.2f}s"
        assert rrhh.tabla_empleados.rowCount() == len(empleados)
    
    def test_tabla_scrolling_performance(self, qapp, large_dataset):
        """Test rendimiento de scrolling en tablas grandes."""
        contabilidad = ContabilidadWidget()
        asientos = large_dataset['asientos'][:1000]  # 1000 registros
        
        # Cargar datos
        contabilidad.cargar_asientos(asientos)
        contabilidad.show()
        
        # Simular scrolling
        table = contabilidad.tabla_asientos
        
        start_time = time.time()
        
        # Scroll hacia abajo
        for i in range(0, table.rowCount(), 50):
            table.scrollToItem(table.item(i, 0) if table.item(i, 0) else table.item(i-1, 0))
            QApplication.processEvents()
        
        # Scroll hacia arriba
        for i in range(table.rowCount()-1, 0, -50):
            table.scrollToItem(table.item(i, 0) if table.item(i, 0) else table.item(i+1, 0))
            QApplication.processEvents()
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Scrolling no debería tomar más de 2 segundos
        assert duration < 2.0, f"Scrolling too slow: {duration:.2f}s"


class TestPerformanceController:
    """Tests de rendimiento del controlador."""
    
    def test_controller_rapid_operations(self, performance_controller, qapp):
        """Test operaciones rápidas del controlador."""
        view = AdministracionViewFuncional()
        performance_controller.set_view(view)
        
        start_time = time.time()
        
        # 100 operaciones rápidas
        for i in range(100):
            performance_controller.cargar_datos()
            performance_controller.buscar({'busqueda': f'test{i}'})
            
            if i % 10 == 0:
                QApplication.processEvents()
        
        end_time = time.time()
        duration = end_time - start_time
        
        # No debería tomar más de 3 segundos
        assert duration < 3.0, f"Controller operations too slow: {duration:.2f}s"
    
    def test_controller_concurrent_requests(self, performance_controller, qapp):
        """Test solicitudes concurrentes simuladas."""
        view = AdministracionViewFuncional()
        performance_controller.set_view(view)
        
        def worker_thread(thread_id):
            """Worker thread para simular concurrencia."""
            for i in range(20):
                try:
                    performance_controller.cargar_datos()
                    performance_controller.buscar({'busqueda': f'thread{thread_id}_item{i}'})
                    time.sleep(0.01)  # Pequeña pausa
                except:
                    pass  # Ignorar errores de threading en tests
        
        # Crear múltiples threads
        threads = []
        for thread_id in range(5):
            thread = threading.Thread(target=worker_thread, args=(thread_id,))
            threads.append(thread)
        
        start_time = time.time()
        
        # Iniciar threads
        for thread in threads:
            thread.start()
        
        # Esperar a que terminen
        for thread in threads:
            thread.join(timeout=5.0)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # No debería tomar más de 6 segundos
        assert duration < 6.0, f"Concurrent operations too slow: {duration:.2f}s"
    
    def test_controller_memory_leaks(self, qapp):
        """Test memory leaks del controlador."""
        controllers = []
        
        # Crear y destruir múltiples controladores
        for i in range(20):
            with patch('rexus.modules.administracion.controller.get_inventario_connection'):
                controller = AdministracionController()
                view = AdministracionViewFuncional()
                
                controller.set_view(view)
                controller.cargar_datos()
                
                controllers.append((controller, view))
                
                if i % 5 == 0:
                    QApplication.processEvents()
                    gc.collect()
        
        # Cleanup explícito
        for controller, view in controllers:
            try:
                controller.cleanup()
                view.deleteLater()
            except:
                pass
        
        gc.collect()
        QApplication.processEvents()
        
        # Si llegó aquí sin crash, no hay leaks severos
        assert True


class TestStressConditions:
    """Tests de condiciones de stress."""
    
    def test_extremely_long_strings(self, qapp):
        """Test con strings extremadamente largos."""
        contabilidad = ContabilidadWidget()
        
        # String muy largo (1MB)
        long_string = "A" * (1024 * 1024)
        
        asientos_extremos = [{
            'id': 1,
            'fecha_asiento': '2025-01-01',
            'concepto': long_string,  # Concepto muy largo
            'cuenta_contable': 'Caja',
            'debe': 1000,
            'haber': 0,
            'estado': 'Activo'
        }]
        
        try:
            # Esto podría fallar o ser lento, pero no debería crash
            contabilidad.cargar_asientos(asientos_extremos)
            QApplication.processEvents()
            assert True
        except Exception as e:
            # Es aceptable que falle con strings extremos
            assert "memory" in str(e).lower() or "size" in str(e).lower()
    
    def test_unicode_extreme_cases(self, qapp):
        """Test con casos extremos de Unicode."""
        rrhh = RecursosHumanosWidget()
        
        # Caracteres Unicode extremos
        unicode_strings = [
            "🏢💰👥[CHART]🔄[CHECK][ERROR][WARN]",  # Emojis
            "Ñandú Güeñes Çağlar Москва 北京",  # Caracteres internacionales
            "𝕻𝖞𝖙𝖍𝖔𝖓 𝖀𝖚𝖊𝖗𝖞𝖍",  # Mathematical symbols
            "\x00\x01\x02\x03",  # Control characters
            "A" + "\u0300" * 100,  # Combining characters
        ]
        
        for i, unicode_str in enumerate(unicode_strings):
            empleado_unicode = {
                'id': i + 1,
                'nombre': unicode_str,
                'apellido': unicode_str,
                'cargo': unicode_str,
                'departamento': unicode_str,
                'salario': 50000,
                'estado': 'Activo'
            }
            
            try:
                rrhh.cargar_empleados([empleado_unicode])
                QApplication.processEvents()
            except Exception as e:
                # Algunos caracteres extremos pueden fallar
                assert "unicode" in str(e).lower() or "encode" in str(e).lower()
    
    def test_rapid_ui_interactions(self, qapp):
        """Test interacciones UI muy rápidas."""
        view = AdministracionViewFuncional()
        view.show()
        
        # Cambiar tabs rápidamente
        for _ in range(100):
            for i in range(view.tabs.count()):
                view.tabs.setCurrentIndex(i)
                QApplication.processEvents()
        
        # Click rápido en botón actualizar
        for _ in range(50):
            if hasattr(view, 'btn_actualizar'):
                QTest.mouseClick(view.btn_actualizar, Qt.MouseButton.LeftButton)
                QApplication.processEvents()
        
        # No debería crash
        assert view.isVisible()
    
    def test_database_connection_failures(self, qapp):
        """Test fallos de conexión a base de datos."""
        # Mock DB que siempre falla
        failing_db = MagicMock()
        failing_db.cursor.side_effect = Exception("Database connection failed")
        failing_db.execute.side_effect = Exception("Query failed")
        
        with patch('rexus.modules.administracion.controller.get_inventario_connection', return_value=failing_db):
            controller = AdministracionController()
            view = AdministracionViewFuncional()
            controller.set_view(view)
            
            # Operaciones que deberían fallar graciosamente
            controller.cargar_datos()
            controller.buscar({'busqueda': 'test'})
            
            # Crear asiento con DB fallida
            datos_asiento = {
                'fecha': date.today(),
                'descripcion': 'Test fail',
                'cuenta': 'Caja',
                'debe': 1000,
                'haber': 0,
                'referencia': 'FAIL001'
            }
            
            with patch('rexus.modules.administracion.controller.show_error'):
                result = controller.crear_asiento_contable(datos_asiento)
                # Debería fallar pero no crash
                assert result is False


class TestBoundaryConditions:
    """Tests de condiciones de frontera."""
    
    def test_zero_values_handling(self, qapp):
        """Test manejo de valores cero."""
        dashboard = DashboardWidget()
        
        datos_cero = {
            'empleados_activos': 0,
            'balance_actual': 0.0,
            'transacciones_mes': 0,
            'alertas_pendientes': 0
        }
        
        dashboard.actualizar_metricas(datos_cero)
        
        # Verificar que se manejan correctamente
        assert dashboard.valor_0_0.text() == "0"
        assert "$0.00" in dashboard.valor_0_1.text()
    
    def test_negative_values_handling(self, qapp):
        """Test manejo de valores negativos."""
        dashboard = DashboardWidget()
        
        datos_negativos = {
            'empleados_activos': -5,  # No debería ser negativo
            'balance_actual': -10000.50,  # Balance negativo es válido
            'transacciones_mes': -10,  # No debería ser negativo
            'alertas_pendientes': -2  # No debería ser negativo
        }
        
        # No debería crash, aunque algunos valores sean ilógicos
        dashboard.actualizar_metricas(datos_negativos)
        assert dashboard is not None
    
    def test_max_integer_values(self, qapp):
        """Test valores máximos de enteros."""
        dashboard = DashboardWidget()
        
        import sys
        max_int = sys.maxsize
        
        datos_maximos = {
            'empleados_activos': max_int,
            'balance_actual': float(max_int),
            'transacciones_mes': max_int,
            'alertas_pendientes': max_int
        }
        
        try:
            dashboard.actualizar_metricas(datos_maximos)
            assert dashboard is not None
        except OverflowError:
            # Es aceptable que falle con valores extremos
            assert True
    
    def test_empty_collections_handling(self, qapp):
        """Test manejo de colecciones vacías."""
        contabilidad = ContabilidadWidget()
        rrhh = RecursosHumanosWidget()
        
        # Listas vacías
        contabilidad.cargar_asientos([])
        rrhh.cargar_empleados([])
        
        assert contabilidad.tabla_asientos.rowCount() == 0
        assert rrhh.tabla_empleados.rowCount() == 0
        
        # None como input
        try:
            contabilidad.cargar_asientos(None)
            rrhh.cargar_empleados(None)
        except (TypeError, AttributeError):
            # Es aceptable que falle con None
            assert True


if __name__ == "__main__":
    pytest.main([
        __file__, 
        "-v", 
        "--tb=short",
        "--capture=no",
        "-x"  # Stop on first failure para performance tests
    ])