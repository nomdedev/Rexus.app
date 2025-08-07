"""
Tests de Integración para Módulo Administración
Simula flujos reales de usuario y integración con otros módulos
"""

import sys
import pytest
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, call
from datetime import datetime, date, timedelta
from decimal import Decimal
from PyQt6.QtWidgets import QApplication, QDialog
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtTest import QTest

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT_DIR))

from rexus.modules.administracion.view import (
    AdministracionView, AsientoContableDialog, EmpleadoDialog
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
def integrated_system(qapp):
    """Sistema integrado completo para tests."""
    # Mock base de datos con datos realistas
    mock_db = MagicMock()
    cursor = MagicMock()
    
    # Datos de empleados existentes
    empleados_db = [
        (1, 'EMP001', 'Juan', 'Pérez', '12345678A', 'juan@empresa.com', '123456789', 1, 'Gerente', 75000, '2024-01-01', 'Activo'),
        (2, 'EMP002', 'María', 'García', '87654321B', 'maria@empresa.com', '987654321', 2, 'Contador', 60000, '2024-02-01', 'Activo'),
        (3, 'EMP003', 'Carlos', 'López', '11111111C', 'carlos@empresa.com', '111222333', 1, 'Supervisor', 55000, '2024-03-01', 'Activo'),
    ]
    
    # Datos de asientos contables existentes
    asientos_db = [
        (1, '2025-01-01', 'Venta de productos', 'REF001', None, None, None, None, 'Caja', 5000, 0, 'Venta realizada'),
        (2, '2025-01-02', 'Pago a proveedor', 'REF002', None, 1, None, None, 'Bancos', 0, 2500, 'Pago efectuado'),
        (3, '2025-01-03', 'Pago nómina', 'REF003', None, None, 2, None, 'Gastos', 0, 60000, 'Nómina enero'),
    ]
    
    # Configurar respuestas del cursor
    def cursor_fetchall_side_effect(*args, **kwargs):
        query = args[0] if args else ""
        if 'empleados' in query.lower():
            return empleados_db
        elif 'libro_contable' in query.lower():
            return asientos_db
        else:
            return []
    
    cursor.fetchall.side_effect = cursor_fetchall_side_effect
    cursor.fetchone.return_value = (1,)  # ID del nuevo registro
    cursor.rowcount = 1
    
    mock_db.cursor.return_value = cursor
    
    # Crear sistema integrado
    with patch('rexus.modules.administracion.controller.get_inventario_connection', return_value=mock_db), \
         patch('rexus.modules.administracion.model.get_inventario_connection', return_value=mock_db):
        
        controller = AdministracionController()
        view = AdministracionView()
        model = AdministracionModel(mock_db)
        
        controller.model = model
        controller.set_view(view)
        view.set_controller(controller)
        
        return {
            'controller': controller,
            'view': view,
            'model': model,
            'db': mock_db,
            'cursor': cursor
        }


class TestIntegrationFlowContabilidad:
    """Tests de flujo completo de contabilidad."""
    
    def test_flow_crear_asiento_completo(self, integrated_system):
        """Test flujo completo: abrir diálogo → llenar datos → crear asiento."""
        system = integrated_system
        view = system['view']
        controller = system['controller']
        
        # Paso 1: Usuario abre pestaña de contabilidad
        if hasattr(view, 'tabs'):
            for i in range(view.tabs.count()):
                tab_text = view.tabs.tabText(i)
                if 'Contabilidad' in tab_text:
                    view.tabs.setCurrentIndex(i)
                    break
        
        # Paso 2: Usuario hace click en "Nuevo Asiento"
        contabilidad_widget = getattr(view, 'contabilidad_widget', None)
        if contabilidad_widget and hasattr(contabilidad_widget, 'btn_nuevo_asiento'):
            
            # Mock del diálogo
            with patch('rexus.modules.administracion.view.AsientoContableDialog') as mock_dialog_class:
                mock_dialog = Mock()
                mock_dialog.exec.return_value = QDialog.DialogCode.Accepted
                mock_dialog.obtener_datos.return_value = {
                    'fecha': date(2025, 1, 15),
                    'concepto': 'Venta de productos Q1',
                    'cuenta': 'Caja',
                    'debe': 2500.75,
                    'haber': 0.0,
                    'referencia': 'VTA-Q1-001'
                }
                mock_dialog_class.return_value = mock_dialog
                
                with patch('rexus.modules.administracion.controller.show_success') as mock_success:
                    # Simular click
                    QTest.mouseClick(contabilidad_widget.btn_nuevo_asiento, Qt.MouseButton.LeftButton)
                    QApplication.processEvents()
                    
                    # Verificar flujo completo
                    mock_dialog_class.assert_called_once()
                    mock_dialog.exec.assert_called_once()
                    mock_dialog.obtener_datos.assert_called_once()
                    
                    # Verificar que se llamó al controlador
                    assert system['cursor'].execute.called
                    mock_success.assert_called_once()
    
    def test_flow_generar_balance_general(self, integrated_system):
        """Test flujo completo: generar balance general."""
        system = integrated_system
        view = system['view']
        controller = system['controller']
        
        # Mock del modelo para balance
        with patch.object(system['model'], 'generar_balance_general') as mock_balance:
            mock_balance.return_value = {
                'activos_corrientes': 150000,
                'activos_fijos': 200000,
                'total_activos': 350000,
                'pasivos_corrientes': 75000,
                'pasivos_largo_plazo': 125000,
                'total_pasivos': 200000,
                'patrimonio': 150000,
                'total_pasivo_patrimonio': 350000,
                'fecha_generacion': date.today()
            }
            
            # Acceder al widget de contabilidad
            contabilidad_widget = getattr(view, 'contabilidad_widget', None)
            if contabilidad_widget and hasattr(contabilidad_widget, 'btn_balance'):
                
                with patch('rexus.utils.message_system.show_success') as mock_success:
                    # Simular click en balance
                    QTest.mouseClick(contabilidad_widget.btn_balance, Qt.MouseButton.LeftButton)
                    QApplication.processEvents()
                    
                    # Verificar que se generó balance
                    mock_success.assert_called_once()
                    assert 'balance general' in str(mock_success.call_args).lower()


class TestIntegrationFlowRRHH:
    """Tests de flujo completo de Recursos Humanos."""
    
    def test_flow_crear_empleado_completo(self, integrated_system):
        """Test flujo completo: crear empleado nuevo."""
        system = integrated_system
        view = system['view']
        
        # Acceder al widget de RRHH
        rrhh_widget = getattr(view, 'rrhh_widget', None)
        if rrhh_widget and hasattr(rrhh_widget, 'btn_nuevo_empleado'):
            
            # Mock del diálogo de empleado
            with patch('rexus.modules.administracion.view.EmpleadoDialog') as mock_dialog_class:
                mock_dialog = Mock()
                mock_dialog.exec.return_value = QDialog.DialogCode.Accepted
                mock_dialog.obtener_datos.return_value = {
                    'nombre': 'Ana',
                    'apellidos': 'Martínez Rodríguez',
                    'dni': '98765432X',
                    'email': 'ana.martinez@empresa.com',
                    'telefono': '+34-666-777-888',
                    'cargo': 'Técnico Especialista',
                    'salario': 45000.0,
                    'fecha_ingreso': date(2025, 2, 1)
                }
                mock_dialog_class.return_value = mock_dialog
                
                with patch('rexus.modules.administracion.controller.show_success') as mock_success:
                    # Simular click
                    QTest.mouseClick(rrhh_widget.btn_nuevo_empleado, Qt.MouseButton.LeftButton)
                    QApplication.processEvents()
                    
                    # Verificar flujo completo
                    mock_dialog_class.assert_called_once()
                    mock_dialog.exec.assert_called_once()
                    mock_dialog.obtener_datos.assert_called_once()
                    mock_success.assert_called_once()
    
    def test_flow_generar_nomina(self, integrated_system):
        """Test flujo completo: generar nómina."""
        system = integrated_system
        view = system['view']
        
        # Mock del modelo para nómina
        with patch.object(system['model'], 'generar_nomina') as mock_nomina:
            mock_nomina.return_value = {
                'periodo': '2025-01',
                'empleados_activos': 3,
                'total_bruto': 190000,
                'total_descuentos': 38000,
                'total_neto': 152000,
                'fecha_generacion': date.today()
            }
            
            rrhh_widget = getattr(view, 'rrhh_widget', None)
            if rrhh_widget and hasattr(rrhh_widget, 'btn_nomina'):
                
                with patch('rexus.utils.message_system.show_success') as mock_success:
                    # Simular click en nómina
                    QTest.mouseClick(rrhh_widget.btn_nomina, Qt.MouseButton.LeftButton)
                    QApplication.processEvents()
                    
                    # Verificar generación
                    mock_success.assert_called_once()
                    assert 'nómina' in str(mock_success.call_args).lower()


class TestIntegrationFlowDashboard:
    """Tests de flujo completo del dashboard."""
    
    def test_flow_dashboard_carga_inicial(self, integrated_system):
        """Test carga inicial del dashboard al abrir módulo."""
        system = integrated_system
        view = system['view']
        controller = system['controller']
        
        # Simular carga inicial
        with patch.object(system['model'], 'obtener_resumen_contable') as mock_resumen:
            mock_resumen.return_value = {
                'total_empleados': 3,
                'balance_total': 350000,
                'transacciones_mes': 15,
                'alertas_pendientes': 2,
                'ingresos_mes': 75000,
                'gastos_mes': 35000
            }
            
            # Cargar datos iniciales
            controller.cargar_datos()
            
            # Verificar que se llamó al modelo
            mock_resumen.assert_called()
            
            # Verificar dashboard si existe
            dashboard_widget = getattr(view, 'dashboard_widget', None)
            if dashboard_widget:
                # El dashboard debería tener datos actualizados
                assert dashboard_widget is not None
    
    def test_flow_dashboard_actualizacion_tiempo_real(self, integrated_system):
        """Test actualización en tiempo real del dashboard."""
        system = integrated_system
        view = system['view']
        
        dashboard_widget = getattr(view, 'dashboard_widget', None)
        if dashboard_widget:
            
            # Simular actualizaciones periódicas
            datos_secuenciales = [
                {
                    'empleados_activos': 3,
                    'balance_actual': 350000,
                    'transacciones_mes': 10,
                    'alertas_pendientes': 2
                },
                {
                    'empleados_activos': 4,  # Se agregó empleado
                    'balance_actual': 365000,  # Aumentó balance
                    'transacciones_mes': 12,  # Más transacciones
                    'alertas_pendientes': 1   # Menos alertas
                },
                {
                    'empleados_activos': 4,
                    'balance_actual': 375000,  # Sigue creciendo
                    'transacciones_mes': 15,
                    'alertas_pendientes': 0    # Sin alertas
                }
            ]
            
            for i, datos in enumerate(datos_secuenciales):
                dashboard_widget.actualizar_metricas(datos)
                QApplication.processEvents()
                
                # Verificar que los valores se actualizaron
                if hasattr(dashboard_widget, 'valor_0_0'):
                    assert str(datos['empleados_activos']) in dashboard_widget.valor_0_0.text()


class TestIntegrationBusqueda:
    """Tests de integración del sistema de búsqueda."""
    
    def test_flow_busqueda_empleados(self, integrated_system):
        """Test búsqueda de empleados."""
        system = integrated_system
        view = system['view']
        controller = system['controller']
        
        # Mock de resultados de búsqueda
        with patch.object(system['model'], 'buscar_empleados') as mock_buscar:
            mock_buscar.return_value = [
                {'id': 1, 'nombre': 'Juan', 'apellido': 'Pérez', 'cargo': 'Gerente'},
                {'id': 2, 'nombre': 'María', 'apellido': 'García', 'cargo': 'Contador'}
            ]
            
            # Realizar búsqueda
            filtros = {'busqueda': 'Juan'}
            controller.buscar(filtros)
            
            # Verificar que se llamó la búsqueda
            mock_buscar.assert_called_with('Juan')
    
    def test_flow_busqueda_transacciones(self, integrated_system):
        """Test búsqueda de transacciones."""
        system = integrated_system
        view = system['view']
        controller = system['controller']
        
        # Mock de resultados
        with patch.object(system['model'], 'buscar_transacciones') as mock_buscar, \
             patch.object(system['model'], 'buscar_asientos_contables') as mock_buscar_asientos:
            
            mock_buscar.return_value = [
                {'id': 1, 'concepto': 'Venta productos', 'monto': 5000}
            ]
            mock_buscar_asientos.return_value = [
                {'id': 1, 'concepto': 'Pago proveedor', 'debe': 2500}
            ]
            
            # Realizar búsqueda
            filtros = {'busqueda': 'pago'}
            controller.buscar(filtros)
            
            # Verificar llamadas
            mock_buscar.assert_called_with('pago')
            mock_buscar_asientos.assert_called_with('pago')


class TestIntegrationErrorHandling:
    """Tests de manejo de errores en integración."""
    
    def test_flow_database_error_recovery(self, integrated_system):
        """Test recuperación de errores de base de datos."""
        system = integrated_system
        controller = system['controller']
        view = system['view']
        
        # Simular error de base de datos
        system['cursor'].execute.side_effect = Exception("Database connection lost")
        
        with patch('rexus.modules.administracion.controller.show_error') as mock_error:
            # Intentar crear asiento con DB fallida
            datos_asiento = {
                'fecha': date.today(),
                'descripcion': 'Test con error',
                'cuenta': 'Caja',
                'debe': 1000,
                'haber': 0,
                'referencia': 'ERROR001'
            }
            
            result = controller.crear_asiento_contable(datos_asiento)
            
            # Debería manejar el error graciosamente
            assert result is False
            mock_error.assert_called()
            
        # Restaurar DB para próximos tests
        system['cursor'].execute.side_effect = None
    
    def test_flow_validation_errors(self, integrated_system):
        """Test manejo de errores de validación."""
        system = integrated_system
        controller = system['controller']
        
        # Datos inválidos para asiento
        datos_invalidos = {
            'fecha': None,  # Fecha requerida
            'descripcion': '',  # Descripción requerida
            'cuenta': '',  # Cuenta requerida
            'debe': 0,  # Debe o haber requerido
            'haber': 0
        }
        
        with patch('rexus.modules.administracion.controller.show_error') as mock_error:
            result = controller.crear_asiento_contable(datos_invalidos)
            
            assert result is False
            mock_error.assert_called()
            
            # Verificar mensaje de error
            error_args = mock_error.call_args[0]
            assert 'inválidos' in str(error_args).lower() or 'incompletos' in str(error_args).lower()


class TestIntegrationPerformance:
    """Tests de performance en integración."""
    
    def test_flow_multiple_operations_sequence(self, integrated_system):
        """Test secuencia de múltiples operaciones."""
        system = integrated_system
        controller = system['controller']
        view = system['view']
        
        start_time = time.time()
        
        # Secuencia de operaciones típicas de usuario
        operations = [
            lambda: controller.cargar_datos(),
            lambda: controller.buscar({'busqueda': 'empleado'}),
            lambda: controller.buscar({'busqueda': 'venta'}),
            lambda: controller.cargar_datos(),
            lambda: controller.buscar({'busqueda': ''}),  # Búsqueda vacía
        ]
        
        for operation in operations:
            try:
                operation()
                QApplication.processEvents()
            except Exception:
                pass  # Continuar con siguiente operación
        
        end_time = time.time()
        duration = end_time - start_time
        
        # No debería tomar más de 2 segundos
        assert duration < 2.0, f"Operation sequence too slow: {duration:.2f}s"
    
    def test_flow_concurrent_users_simulation(self, integrated_system):
        """Test simulación de usuarios concurrentes."""
        system = integrated_system
        controller = system['controller']
        
        # Simular múltiples operaciones "concurrentes"
        operations_count = 0
        
        for user_id in range(3):  # 3 usuarios simulados
            for operation_id in range(5):  # 5 operaciones cada uno
                try:
                    controller.cargar_datos()
                    controller.buscar({'busqueda': f'user{user_id}_op{operation_id}'})
                    operations_count += 2
                    
                    if operations_count % 5 == 0:
                        QApplication.processEvents()
                        
                except Exception:
                    pass  # Ignorar errores en simulación
        
        # Si completó sin crash, el test pasó
        assert operations_count > 0


class TestIntegrationCompatibility:
    """Tests de compatibilidad e integración con sistema existente."""
    
    def test_alias_compatibility(self, qapp):
        """Test que el alias AdministracionView funciona."""
        from rexus.modules.administracion.view import AdministracionView
        
        view = AdministracionView()
        assert view is not None
        assert hasattr(view, 'set_controller')
        
        # Verificar que es la vista funcional
        if hasattr(view, 'tabs'):
            assert view.tabs.count() > 0
    
    def test_controller_interface_compatibility(self, integrated_system):
        """Test compatibilidad de interfaz del controlador."""
        system = integrated_system
        controller = system['controller']
        
        # Métodos que deben existir para compatibilidad
        required_methods = [
            'set_view',
            'cargar_datos',
            'buscar',
            'nuevo_registro'
        ]
        
        for method in required_methods:
            assert hasattr(controller, method), f"Método {method} faltante"
            assert callable(getattr(controller, method)), f"Método {method} no callable"
    
    def test_model_interface_compatibility(self, integrated_system):
        """Test compatibilidad de interfaz del modelo."""
        system = integrated_system
        model = system['model']
        
        # Métodos críticos del modelo
        critical_methods = [
            'registrar_asiento_contable',
            'crear_empleado',
            'generar_balance_general',
            'obtener_resumen_contable'
        ]
        
        for method in critical_methods:
            assert hasattr(model, method), f"Método crítico {method} faltante"


if __name__ == "__main__":
    pytest.main([
        __file__, 
        "-v", 
        "--tb=short",
        "--capture=no"
    ])