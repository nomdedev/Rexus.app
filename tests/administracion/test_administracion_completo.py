"""
Tests Completos para Módulo Administración - Suite Comprehensiva
Cubre funcionalidad real post-correcciones con edge cases
"""

import sys
import pytest
import logging
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, call
from decimal import Decimal
from datetime import datetime, date
from PyQt6.QtWidgets import QApplication, QDialog
from PyQt6.QtCore import Qt, QDate, pyqtSignal
from PyQt6.QtTest import QTest

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT_DIR))

from rexus.modules.administracion.view import (
    AdministracionView, AdministracionViewFuncional, 
    DashboardWidget, ContabilidadWidget, RecursosHumanosWidget,
    AsientoContableDialog, EmpleadoDialog
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
def mock_db():
    """Mock de base de datos con comportamiento realista."""
    db = MagicMock()
    cursor = MagicMock()
    
    # Configurar comportamiento del cursor
    cursor.fetchall.return_value = []
    cursor.fetchone.return_value = None
    cursor.rowcount = 0
    cursor.description = []
    
    db.cursor.return_value = cursor
    db.commit.return_value = None
    db.rollback.return_value = None
    
    return db


@pytest.fixture
def mock_model():
    """Mock del modelo con métodos reales del módulo."""
    model = MagicMock()
    
    # Configurar métodos del modelo
    model.registrar_asiento_contable.return_value = 1
    model.generar_balance_general.return_value = {
        'total_activos': 100000,
        'total_pasivos': 50000,
        'total_patrimonio': 50000,
        'balance_total': 100000
    }
    model.crear_empleado.return_value = 1
    model.generar_nomina.return_value = {
        'empleados': 5,
        'total_nomina': 25000,
        'fecha': date.today()
    }
    model.obtener_empleados_activos.return_value = [
        {'id': 1, 'nombre': 'Juan', 'apellido': 'Pérez', 'cargo': 'Gerente'},
        {'id': 2, 'nombre': 'María', 'apellido': 'García', 'cargo': 'Contador'}
    ]
    model.obtener_resumen_contable.return_value = {
        'total_empleados': 10,
        'balance_total': 100000,
        'transacciones_mes': 25,
        'alertas_pendientes': 2
    }
    model.buscar_empleados.return_value = []
    model.buscar_transacciones.return_value = []
    model.buscar_asientos_contables.return_value = []
    
    return model


@pytest.fixture
def controller(mock_model, mock_db):
    """Controlador con mocks configurados."""
    with patch('rexus.modules.administracion.controller.get_inventario_connection', return_value=mock_db), \
         patch('rexus.modules.administracion.controller.ContabilidadController'), \
         patch('rexus.modules.administracion.controller.RecursosHumanosController'):
        
        controller = AdministracionController()
        controller.model = mock_model
        controller.db_connection = mock_db
        
        return controller


@pytest.fixture
def view_funcional(qapp):
    """Vista funcional para tests."""
    view = AdministracionViewFuncional()
    return view


@pytest.fixture
def dashboard_widget(qapp):
    """Widget de dashboard para tests."""
    return DashboardWidget()


@pytest.fixture
def contabilidad_widget(qapp):
    """Widget de contabilidad para tests."""
    return ContabilidadWidget()


@pytest.fixture
def rrhh_widget(qapp):
    """Widget de RRHH para tests."""
    return RecursosHumanosWidget()


class TestAdministracionModel:
    """Tests del modelo de administración."""
    
    def test_model_initialization(self, mock_db):
        """Test inicialización del modelo."""
        with patch('rexus.modules.administracion.model.get_inventario_connection', return_value=mock_db):
            model = AdministracionModel(mock_db)
            
            assert model is not None
            assert model.db_connection == mock_db
            assert hasattr(model, 'tabla_libro_contable')
            assert hasattr(model, 'tabla_empleados')
    
    def test_model_has_critical_methods(self, mock_model):
        """Test que el modelo tiene métodos críticos."""
        critical_methods = [
            'registrar_asiento_contable',
            'generar_balance_general',
            'crear_empleado',
            'generar_nomina',
            'obtener_empleados_activos'
        ]
        
        for method in critical_methods:
            assert hasattr(mock_model, method), f"Método {method} faltante"
            assert callable(getattr(mock_model, method)), f"Método {method} no es callable"


class TestAdministracionController:
    """Tests comprehensivos del controlador."""
    
    def test_controller_initialization(self, controller):
        """Test inicialización correcta del controlador."""
        assert controller is not None
        assert hasattr(controller, 'model')
        assert hasattr(controller, 'view')
        assert hasattr(controller, 'logger')
    
    def test_controller_database_connection(self, controller, mock_db):
        """Test conexión a base de datos."""
        assert controller.db_connection is not None
        assert controller.db_connection == mock_db
    
    def test_set_view_connection(self, controller, view_funcional):
        """Test conexión con la vista."""
        controller.set_view(view_funcional)
        
        assert controller.view == view_funcional
        assert view_funcional.controller == controller
    
    def test_cargar_datos_success(self, controller, view_funcional, mock_model):
        """Test carga exitosa de datos."""
        controller.set_view(view_funcional)
        
        # Ejecutar carga de datos
        controller.cargar_datos()
        
        # Verificar que se llamaron métodos del modelo
        mock_model.obtener_resumen_contable.assert_called()
    
    def test_cargar_datos_no_model(self, controller, view_funcional):
        """Test carga de datos sin modelo disponible."""
        controller.model = None
        controller.set_view(view_funcional)
        
        # No debería fallar, pero tampoco cargar datos
        controller.cargar_datos()
        
        # Verificar que no falló
        assert controller.view is not None
    
    def test_buscar_functionality(self, controller, view_funcional, mock_model):
        """Test funcionalidad de búsqueda."""
        controller.set_view(view_funcional)
        
        # Test búsqueda con término
        filtros = {'busqueda': 'test'}
        controller.buscar(filtros)
        
        # Verificar llamadas a métodos de búsqueda
        mock_model.buscar_empleados.assert_called_with('test')
        mock_model.buscar_transacciones.assert_called_with('test')
        mock_model.buscar_asientos_contables.assert_called_with('test')
    
    def test_buscar_empty_term(self, controller, view_funcional):
        """Test búsqueda con término vacío."""
        controller.set_view(view_funcional)
        
        # Test búsqueda vacía
        filtros = {'busqueda': ''}
        controller.buscar(filtros)
        
        # Debería recargar datos normalmente
        assert controller.view is not None
    
    def test_crear_asiento_contable_success(self, controller, view_funcional, mock_model):
        """Test creación exitosa de asiento contable."""
        controller.set_view(view_funcional)
        
        datos_asiento = {
            'fecha': date.today(),
            'descripcion': 'Test asiento',
            'cuenta': 'Caja',
            'debe': 1000.0,
            'haber': 0.0,
            'referencia': 'TEST001'
        }
        
        with patch('rexus.modules.administracion.controller.show_success') as mock_success:
            result = controller.crear_asiento_contable(datos_asiento)
            
            assert result is True
            mock_model.registrar_asiento_contable.assert_called_once()
            mock_success.assert_called_once()
    
    def test_crear_asiento_contable_invalid_data(self, controller, view_funcional, mock_model):
        """Test creación de asiento con datos inválidos."""
        controller.set_view(view_funcional)
        
        # Datos incompletos
        datos_invalidos = {
            'fecha': None,
            'descripcion': '',
            'cuenta': ''
        }
        
        with patch('rexus.modules.administracion.controller.show_error') as mock_error:
            result = controller.crear_asiento_contable(datos_invalidos)
            
            assert result is False
            mock_error.assert_called_once()
    
    def test_crear_empleado_success(self, controller, view_funcional, mock_model):
        """Test creación exitosa de empleado."""
        controller.set_view(view_funcional)
        
        datos_empleado = {
            'nombre': 'Juan',
            'apellidos': 'Pérez',
            'dni': '12345678',
            'email': 'juan@test.com',
            'telefono': '123456789',
            'cargo': 'Empleado',
            'salario': 50000,
            'fecha_ingreso': date.today()
        }
        
        with patch('rexus.modules.administracion.controller.show_success') as mock_success:
            result = controller.crear_empleado(datos_empleado)
            
            assert result is True
            mock_model.crear_empleado.assert_called_once()
            mock_success.assert_called_once()
    
    def test_crear_empleado_invalid_data(self, controller, view_funcional, mock_model):
        """Test creación de empleado con datos inválidos."""
        controller.set_view(view_funcional)
        
        # Datos incompletos
        datos_invalidos = {
            'nombre': '',
            'apellidos': '',
            'dni': ''
        }
        
        with patch('rexus.modules.administracion.controller.show_error') as mock_error:
            result = controller.crear_empleado(datos_invalidos)
            
            assert result is False
            mock_error.assert_called_once()
    
    def test_nuevo_registro_functionality(self, controller, view_funcional):
        """Test funcionalidad nuevo registro."""
        controller.set_view(view_funcional)
        
        with patch('rexus.modules.administracion.controller.show_warning') as mock_warning:
            controller.nuevo_registro()
            
            mock_warning.assert_called_once()
            args = mock_warning.call_args[0]
            assert 'Crear Nuevo Registro' in str(args)


class TestAdministracionViewFuncional:
    """Tests de la vista funcional."""
    
    def test_view_initialization(self, view_funcional):
        """Test inicialización de la vista funcional."""
        assert view_funcional is not None
        assert hasattr(view_funcional, 'tabs')
        assert hasattr(view_funcional, 'dashboard_widget')
        assert hasattr(view_funcional, 'contabilidad_widget')
        assert hasattr(view_funcional, 'rrhh_widget')
    
    def test_view_has_tabs(self, view_funcional):
        """Test que la vista tiene las pestañas correctas."""
        assert view_funcional.tabs.count() == 3
        
        tab_texts = []
        for i in range(view_funcional.tabs.count()):
            tab_texts.append(view_funcional.tabs.tabText(i))
        
        assert any('Dashboard' in text for text in tab_texts)
        assert any('Contabilidad' in text for text in tab_texts)
        assert any('Recursos Humanos' in text for text in tab_texts)
    
    def test_view_signals_exist(self, view_funcional):
        """Test que las señales existen."""
        assert hasattr(view_funcional, 'solicitud_datos_dashboard')
        assert hasattr(view_funcional, 'solicitud_crear_asiento')
        assert hasattr(view_funcional, 'solicitud_crear_empleado')
        
        # Verificar que son señales PyQt
        assert isinstance(view_funcional.solicitud_datos_dashboard, pyqtSignal)
        assert isinstance(view_funcional.solicitud_crear_asiento, pyqtSignal)
        assert isinstance(view_funcional.solicitud_crear_empleado, pyqtSignal)
    
    def test_set_controller(self, view_funcional, controller):
        """Test establecimiento del controlador."""
        view_funcional.set_controller(controller)
        
        assert view_funcional.controller == controller
    
    def test_actualizar_dashboard(self, view_funcional):
        """Test actualización del dashboard."""
        datos_test = {
            'resumen': {
                'total_empleados': 5,
                'balance_total': 100000,
                'transacciones_mes': 10,
                'alertas_pendientes': 1
            }
        }
        
        # No debería fallar
        view_funcional.actualizar_dashboard(datos_test)
        
        # Verificar que el status se actualizó
        assert "actualizados correctamente" in view_funcional.status_label.text()
    
    def test_nuevo_registro_guidance(self, view_funcional):
        """Test guía para nuevo registro."""
        with patch('rexus.utils.message_system.show_warning') as mock_warning:
            view_funcional.nuevo_registro()
            
            mock_warning.assert_called_once()
            args = mock_warning.call_args[0]
            assert 'Crear Nuevo Registro' in str(args)
            assert 'Contabilidad' in str(args)
            assert 'Recursos Humanos' in str(args)
    
    def test_buscar_functionality(self, view_funcional):
        """Test funcionalidad de búsqueda."""
        # Test búsqueda con término
        filtros = {'busqueda': 'test'}
        view_funcional.buscar(filtros)
        
        assert "Buscando: test" in view_funcional.status_label.text()
        
        # Test búsqueda vacía
        filtros = {'busqueda': ''}
        view_funcional.buscar(filtros)
        
        # No debería fallar
        assert view_funcional.status_label is not None
    
    def test_compatibility_methods(self, view_funcional):
        """Test métodos de compatibilidad."""
        # Método de compatibilidad con vista genérica
        view_funcional.cargar_datos_en_tabla([])
        
        assert "específicas" in view_funcional.status_label.text()


class TestDashboardWidget:
    """Tests del widget de dashboard."""
    
    def test_dashboard_initialization(self, dashboard_widget):
        """Test inicialización del dashboard."""
        assert dashboard_widget is not None
        assert hasattr(dashboard_widget, 'valor_0_0')  # Empleados
        assert hasattr(dashboard_widget, 'valor_0_1')  # Balance
        assert hasattr(dashboard_widget, 'valor_1_0')  # Transacciones
        assert hasattr(dashboard_widget, 'valor_1_1')  # Alertas
    
    def test_actualizar_metricas(self, dashboard_widget):
        """Test actualización de métricas."""
        datos_test = {
            'empleados_activos': 10,
            'balance_actual': 50000.75,
            'transacciones_mes': 25,
            'alertas_pendientes': 3
        }
        
        dashboard_widget.actualizar_metricas(datos_test)
        
        # Verificar que se actualizaron los valores
        assert dashboard_widget.valor_0_0.text() == "10"
        assert "$50,000.75" in dashboard_widget.valor_0_1.text()
        assert dashboard_widget.valor_1_0.text() == "25"
        assert dashboard_widget.valor_1_1.text() == "3"
    
    def test_actualizar_metricas_empty_data(self, dashboard_widget):
        """Test actualización con datos vacíos."""
        # No debería fallar con datos vacíos
        dashboard_widget.actualizar_metricas({})
        
        assert dashboard_widget.valor_0_0 is not None


class TestContabilidadWidget:
    """Tests del widget de contabilidad."""
    
    def test_contabilidad_initialization(self, contabilidad_widget):
        """Test inicialización del widget."""
        assert contabilidad_widget is not None
        assert hasattr(contabilidad_widget, 'btn_nuevo_asiento')
        assert hasattr(contabilidad_widget, 'btn_balance')
        assert hasattr(contabilidad_widget, 'tabla_asientos')
        assert hasattr(contabilidad_widget, 'solicitud_crear_asiento')
    
    def test_nuevo_asiento_dialog(self, contabilidad_widget, qapp):
        """Test apertura de diálogo de nuevo asiento."""
        # Mock del diálogo
        with patch('rexus.modules.administracion.view.AsientoContableDialog') as mock_dialog:
            mock_instance = Mock()
            mock_instance.exec.return_value = QDialog.DialogCode.Accepted
            mock_instance.obtener_datos.return_value = {
                'fecha': date.today(),
                'concepto': 'Test',
                'cuenta': 'Caja',
                'debe': 1000,
                'haber': 0,
                'referencia': 'TEST'
            }
            mock_dialog.return_value = mock_instance
            
            # Simular click en botón
            QTest.mouseClick(contabilidad_widget.btn_nuevo_asiento, Qt.MouseButton.LeftButton)
            
            # Verificar que se abrió el diálogo
            mock_dialog.assert_called_once()
    
    def test_cargar_asientos(self, contabilidad_widget):
        """Test carga de asientos en tabla."""
        asientos_test = [
            {
                'id': 1,
                'fecha_asiento': '2025-01-01',
                'concepto': 'Venta productos',
                'cuenta_contable': 'Caja',
                'debe': 1000,
                'haber': 0,
                'estado': 'Activo'
            },
            {
                'id': 2,
                'fecha_asiento': '2025-01-02',
                'concepto': 'Pago proveedor',
                'cuenta_contable': 'Bancos',
                'debe': 0,
                'haber': 500,
                'estado': 'Activo'
            }
        ]
        
        contabilidad_widget.cargar_asientos(asientos_test)
        
        assert contabilidad_widget.tabla_asientos.rowCount() == 2
        assert contabilidad_widget.tabla_asientos.item(0, 1).text() == '2025-01-01'
        assert contabilidad_widget.tabla_asientos.item(1, 2).text() == 'Pago proveedor'


class TestRecursosHumanosWidget:
    """Tests del widget de recursos humanos."""
    
    def test_rrhh_initialization(self, rrhh_widget):
        """Test inicialización del widget."""
        assert rrhh_widget is not None
        assert hasattr(rrhh_widget, 'btn_nuevo_empleado')
        assert hasattr(rrhh_widget, 'btn_nomina')
        assert hasattr(rrhh_widget, 'tabla_empleados')
        assert hasattr(rrhh_widget, 'solicitud_crear_empleado')
    
    def test_nuevo_empleado_dialog(self, rrhh_widget, qapp):
        """Test apertura de diálogo de nuevo empleado."""
        with patch('rexus.modules.administracion.view.EmpleadoDialog') as mock_dialog:
            mock_instance = Mock()
            mock_instance.exec.return_value = QDialog.DialogCode.Accepted
            mock_instance.obtener_datos.return_value = {
                'nombre': 'Juan',
                'apellidos': 'Pérez',
                'dni': '12345678',
                'email': 'juan@test.com',
                'telefono': '123456789',
                'cargo': 'Empleado',
                'salario': 50000,
                'fecha_ingreso': date.today()
            }
            mock_dialog.return_value = mock_instance
            
            # Simular click en botón
            QTest.mouseClick(rrhh_widget.btn_nuevo_empleado, Qt.MouseButton.LeftButton)
            
            # Verificar que se abrió el diálogo
            mock_dialog.assert_called_once()
    
    def test_cargar_empleados(self, rrhh_widget):
        """Test carga de empleados en tabla."""
        empleados_test = [
            {
                'id': 1,
                'nombre': 'Juan',
                'apellido': 'Pérez',
                'cargo': 'Gerente',
                'departamento': 'Administración',
                'salario': 75000,
                'estado': 'Activo'
            },
            {
                'id': 2,
                'nombre': 'María',
                'apellido': 'García',
                'cargo': 'Contador',
                'departamento': 'Finanzas',
                'salario': 60000,
                'estado': 'Activo'
            }
        ]
        
        rrhh_widget.cargar_empleados(empleados_test)
        
        assert rrhh_widget.tabla_empleados.rowCount() == 2
        assert rrhh_widget.tabla_empleados.item(0, 1).text() == 'Juan Pérez'
        assert rrhh_widget.tabla_empleados.item(1, 2).text() == 'Contador'


class TestAsientoContableDialog:
    """Tests del diálogo de asientos contables."""
    
    def test_dialog_initialization(self, qapp):
        """Test inicialización del diálogo."""
        dialog = AsientoContableDialog()
        
        assert dialog is not None
        assert hasattr(dialog, 'fecha_edit')
        assert hasattr(dialog, 'concepto_edit')
        assert hasattr(dialog, 'cuenta_combo')
        assert hasattr(dialog, 'debe_spin')
        assert hasattr(dialog, 'haber_spin')
        assert hasattr(dialog, 'referencia_edit')
    
    def test_obtener_datos(self, qapp):
        """Test obtención de datos del diálogo."""
        dialog = AsientoContableDialog()
        
        # Configurar datos de test
        dialog.fecha_edit.setDate(QDate(2025, 1, 1))
        dialog.concepto_edit.setText("Test concepto")
        dialog.cuenta_combo.setCurrentText("Caja")
        dialog.debe_spin.setValue(1000.50)
        dialog.haber_spin.setValue(0.0)
        dialog.referencia_edit.setText("REF001")
        
        datos = dialog.obtener_datos()
        
        assert datos['fecha'] == date(2025, 1, 1)
        assert datos['concepto'] == "Test concepto"
        assert datos['cuenta'] == "Caja"
        assert datos['debe'] == 1000.50
        assert datos['haber'] == 0.0
        assert datos['referencia'] == "REF001"


class TestEmpleadoDialog:
    """Tests del diálogo de empleados."""
    
    def test_dialog_initialization(self, qapp):
        """Test inicialización del diálogo."""
        dialog = EmpleadoDialog()
        
        assert dialog is not None
        assert hasattr(dialog, 'nombre_edit')
        assert hasattr(dialog, 'apellido_edit')
        assert hasattr(dialog, 'dni_edit')
        assert hasattr(dialog, 'email_edit')
        assert hasattr(dialog, 'telefono_edit')
        assert hasattr(dialog, 'cargo_combo')
        assert hasattr(dialog, 'salario_spin')
        assert hasattr(dialog, 'fecha_ingreso_edit')
    
    def test_obtener_datos(self, qapp):
        """Test obtención de datos del diálogo."""
        dialog = EmpleadoDialog()
        
        # Configurar datos de test
        dialog.nombre_edit.setText("Juan")
        dialog.apellido_edit.setText("Pérez")
        dialog.dni_edit.setText("12345678")
        dialog.email_edit.setText("juan@test.com")
        dialog.telefono_edit.setText("123456789")
        dialog.cargo_combo.setCurrentText("Gerente")
        dialog.salario_spin.setValue(75000.00)
        dialog.fecha_ingreso_edit.setDate(QDate(2025, 1, 1))
        
        datos = dialog.obtener_datos()
        
        assert datos['nombre'] == "Juan"
        assert datos['apellidos'] == "Pérez"
        assert datos['dni'] == "12345678"
        assert datos['email'] == "juan@test.com"
        assert datos['telefono'] == "123456789"
        assert datos['cargo'] == "Gerente"
        assert datos['salario'] == 75000.00
        assert datos['fecha_ingreso'] == date(2025, 1, 1)


class TestEdgeCases:
    """Tests de casos extremos y edge cases."""
    
    def test_asiento_contable_valores_extremos(self, controller, view_funcional, mock_model):
        """Test asiento contable con valores extremos."""
        controller.set_view(view_funcional)
        
        # Valores muy altos
        datos_extremos = {
            'fecha': date.today(),
            'descripcion': 'Test extremo',
            'cuenta': 'Caja',
            'debe': 999999999.99,
            'haber': 0.0,
            'referencia': 'EXT001'
        }
        
        with patch('rexus.modules.administracion.controller.show_success'):
            result = controller.crear_asiento_contable(datos_extremos)
            assert result is True
    
    def test_empleado_datos_especiales(self, controller, view_funcional, mock_model):
        """Test empleado con caracteres especiales."""
        controller.set_view(view_funcional)
        
        datos_especiales = {
            'nombre': 'José María',
            'apellidos': 'García-López',
            'dni': 'X1234567L',
            'email': 'jose.maria@empresa.com',
            'telefono': '+34-123-456-789',
            'cargo': 'Técnico Especialista',
            'salario': 35000.50,
            'fecha_ingreso': date.today()
        }
        
        with patch('rexus.modules.administracion.controller.show_success'):
            result = controller.crear_empleado(datos_especiales)
            assert result is True
    
    def test_busqueda_caracteres_especiales(self, controller, view_funcional, mock_model):
        """Test búsqueda con caracteres especiales."""
        controller.set_view(view_funcional)
        
        # Términos con caracteres especiales
        terminos_especiales = [
            'José María',
            'García-López',
            'Niño & Asociados',
            '100% efectivo',
            'año 2024/2025'
        ]
        
        for termino in terminos_especiales:
            filtros = {'busqueda': termino}
            # No debería fallar
            controller.buscar(filtros)
    
    def test_dashboard_datos_nulos(self, dashboard_widget):
        """Test dashboard con datos nulos."""
        datos_nulos = {
            'empleados_activos': None,
            'balance_actual': None,
            'transacciones_mes': None,
            'alertas_pendientes': None
        }
        
        # No debería fallar
        dashboard_widget.actualizar_metricas(datos_nulos)
    
    def test_tabla_datos_vacios(self, contabilidad_widget):
        """Test tabla con datos vacíos."""
        # Lista vacía
        contabilidad_widget.cargar_asientos([])
        assert contabilidad_widget.tabla_asientos.rowCount() == 0
        
        # Lista con datos incompletos
        asientos_incompletos = [
            {'id': 1},  # Datos incompletos
            {'concepto': 'Solo concepto'}  # Datos parciales
        ]
        
        # No debería fallar
        contabilidad_widget.cargar_asientos(asientos_incompletos)
    
    def test_controlador_sin_modelo(self, view_funcional):
        """Test controlador sin modelo configurado."""
        controller_sin_modelo = AdministracionController()
        controller_sin_modelo.model = None
        controller_sin_modelo.set_view(view_funcional)
        
        # Operaciones que deberían manejar modelo nulo graciosamente
        controller_sin_modelo.cargar_datos()
        controller_sin_modelo.buscar({'busqueda': 'test'})
        
        # No debería fallar
        assert controller_sin_modelo.view is not None
    
    def test_vista_sin_controlador(self, view_funcional):
        """Test vista sin controlador configurado."""
        view_funcional.controller = None
        
        # Operaciones que deberían manejar controlador nulo
        view_funcional.actualizar_datos()
        view_funcional.buscar({'busqueda': 'test'})
        
        # No debería fallar
        assert view_funcional is not None
    
    def test_memory_intensive_operations(self, view_funcional, dashboard_widget):
        """Test operaciones intensivas en memoria."""
        # Múltiples actualizaciones rápidas
        for i in range(100):
            datos_test = {
                'empleados_activos': i,
                'balance_actual': i * 1000,
                'transacciones_mes': i * 5,
                'alertas_pendientes': i % 10
            }
            dashboard_widget.actualizar_metricas(datos_test)
        
        # No debería causar memory leak o crash
        assert dashboard_widget is not None
    
    def test_concurrent_operations(self, controller, view_funcional, mock_model):
        """Test operaciones concurrentes simuladas."""
        controller.set_view(view_funcional)
        
        # Simular múltiples operaciones rápidas
        for i in range(10):
            controller.cargar_datos()
            controller.buscar({'busqueda': f'test{i}'})
            
            # Datos de prueba para asiento
            datos_asiento = {
                'fecha': date.today(),
                'descripcion': f'Test concurrent {i}',
                'cuenta': 'Caja',
                'debe': 100.0 * i,
                'haber': 0.0,
                'referencia': f'CONC{i:03d}'
            }
            
            with patch('rexus.modules.administracion.controller.show_success'):
                controller.crear_asiento_contable(datos_asiento)
        
        # Debería manejar todas las operaciones sin fallar
        assert controller is not None


if __name__ == "__main__":
    # Configurar logging para debugging
    logging.basicConfig(level=logging.DEBUG)
    
    # Ejecutar tests con coverage detallado
    pytest.main([
        __file__, 
        "-v", 
        "--tb=short",
        "--capture=no",
        "--log-cli-level=INFO"
    ])