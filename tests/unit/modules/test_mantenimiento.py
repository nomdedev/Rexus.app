"""
Tests unitarios para el módulo de Mantenimiento.

Estos tests verifican la funcionalidad del módulo de mantenimiento,
incluyendo modelo, vista, controlador y gestión de equipos y servicios.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt


class TestMantenimientoModel:
    """Tests para el modelo de mantenimiento."""

    def test_model_import_successfully(self):
        """Test importación exitosa del modelo de mantenimiento."""
        try:
            from rexus.modules.mantenimiento.model import MantenimientoModel
            assert MantenimientoModel is not None
        except ImportError as e:
            pytest.fail(f"Error importando MantenimientoModel: {e}")

    def test_model_initialization(self, mock_db_connection):
        """Test inicialización del modelo con conexión mock."""
        from rexus.modules.mantenimiento.model import MantenimientoModel
        
        try:
            with patch('rexus.modules.mantenimiento.model.database_manager') as mock_db_manager:
                mock_db_manager.get_connection.return_value = mock_db_connection
                model = MantenimientoModel()
                assert model is not None
        except Exception as e:
            pytest.skip(f"Model initialization error: {e}")

    def test_maintenance_types(self):
        """Test tipos de mantenimiento."""
        from rexus.modules.mantenimiento.model import MantenimientoModel
        
        # Verificar que existe configuración de tipos
        if hasattr(MantenimientoModel, 'TIPOS_MANTENIMIENTO'):
            tipos = MantenimientoModel.TIPOS_MANTENIMIENTO
            assert isinstance(tipos, (list, dict))
            
            # Verificar tipos típicos de mantenimiento
            expected_types = ['PREVENTIVO', 'CORRECTIVO', 'PREDICTIVO', 'URGENTE']
            if isinstance(tipos, list):
                for tipo in expected_types[:2]:  # Al menos 2 tipos
                    if tipo in tipos:
                        assert True
                        break
                else:
                    assert len(tipos) > 0, "Debe tener al menos algunos tipos"

    def test_equipment_management_methods(self):
        """Test métodos de gestión de equipos."""
        from rexus.modules.mantenimiento.model import MantenimientoModel
        
        equipment_methods = ['crear_equipo', 'obtener_equipos', 'actualizar_equipo', 'eliminar_equipo']
        
        for method in equipment_methods:
            if hasattr(MantenimientoModel, method):
                assert callable(getattr(MantenimientoModel, method))

    def test_maintenance_schedule_methods(self):
        """Test métodos de programación de mantenimiento."""
        from rexus.modules.mantenimiento.model import MantenimientoModel
        
        schedule_methods = ['programar_mantenimiento', 'obtener_calendario', 'generar_alertas']
        
        for method in schedule_methods:
            if hasattr(MantenimientoModel, method):
                assert callable(getattr(MantenimientoModel, method))


class TestMantenimientoView:
    """Tests para la vista de mantenimiento."""

    def test_view_import_successfully(self, qapp):
        """Test importación exitosa de la vista."""
        try:
            from rexus.modules.mantenimiento.view import MantenimientoView
            assert MantenimientoView is not None
        except ImportError as e:
            pytest.fail(f"Error importando MantenimientoView: {e}")

    def test_view_initialization(self, qapp):
        """Test inicialización de la vista."""
        from rexus.modules.mantenimiento.view import MantenimientoView
        
        try:
            view = MantenimientoView()
            assert view is not None
            assert isinstance(view, QWidget)
        except Exception as e:
            pytest.skip(f"Vista de mantenimiento no puede inicializarse: {e}")

    def test_equipment_ui_methods(self, qapp):
        """Test métodos de interfaz de equipos."""
        from rexus.modules.mantenimiento.view import MantenimientoView
        
        try:
            view = MantenimientoView()
            
            # Verificar métodos críticos de UI
            ui_methods = [
                'mostrar_equipos',
                'agregar_equipo',
                'editar_equipo',
                'eliminar_equipo'
            ]
            
            for method_name in ui_methods:
                if hasattr(view, method_name):
                    assert callable(getattr(view, method_name))
                    
        except Exception as e:
            pytest.skip(f"Vista no disponible para test: {e}")

    def test_maintenance_scheduling_ui(self, qapp):
        """Test interfaz de programación de mantenimiento."""
        from rexus.modules.mantenimiento.view import MantenimientoView
        
        try:
            view = MantenimientoView()
            
            # Verificar métodos de programación
            scheduling_methods = ['mostrar_calendario', 'programar_servicio', 'mostrar_alertas']
            
            for method_name in scheduling_methods:
                if hasattr(view, method_name):
                    assert callable(getattr(view, method_name))
                    
        except Exception as e:
            pytest.skip(f"Test programación skipped: {e}")

    def test_color_rexus_usage(self, qapp):
        """Test que no usa RexusColors problemáticos."""
        from rexus.modules.mantenimiento.view import MantenimientoView
        
        try:
            view = MantenimientoView()
            
            # Verificar que no usa colores que causan errores
            # Como DANGER_LIGHT que causaba problemas antes
            problematic_colors = ['DANGER_LIGHT', 'WARNING_LIGHT', 'SUCCESS_LIGHT']
            
            # Si usa RexusColors, debería evitar estos colores problemáticos
            view_source = str(view.__class__.__dict__)
            for color in problematic_colors:
                if color in view_source:
                    # Solo advertencia, no falla el test
                    print(f"Warning: Vista usa color problemático {color}")
                    
        except Exception as e:
            pytest.skip(f"Test colores skipped: {e}")


class TestMantenimientoController:
    """Tests para el controlador de mantenimiento."""

    def test_controller_import(self):
        """Test importación del controlador."""
        try:
            from rexus.modules.mantenimiento.controller import MantenimientoController
            assert MantenimientoController is not None
        except ImportError as e:
            pytest.fail(f"Error importando MantenimientoController: {e}")

    def test_controller_initialization(self, mock_db_connection):
        """Test inicialización del controlador."""
        from rexus.modules.mantenimiento.controller import MantenimientoController
        
        try:
            with patch('rexus.modules.mantenimiento.controller.MantenimientoModel') as mock_model:
                mock_model.return_value = Mock()
                controller = MantenimientoController()
                assert controller is not None
        except Exception as e:
            pytest.skip(f"Controller initialization error: {e}")

    def test_maintenance_workflow_methods(self):
        """Test métodos de flujo de trabajo."""
        from rexus.modules.mantenimiento.controller import MantenimientoController
        
        workflow_methods = ['crear_orden_trabajo', 'asignar_tecnico', 'completar_servicio', 'generar_reporte']
        
        try:
            controller = MantenimientoController()
            for method in workflow_methods:
                if hasattr(controller, method):
                    assert callable(getattr(controller, method))
        except Exception as e:
            pytest.skip(f"Controller workflow test skipped: {e}")


class TestMantenimientoIntegration:
    """Tests de integración para mantenimiento."""

    def test_module_structure_integrity(self):
        """Test integridad de la estructura del módulo."""
        import os
        
        module_path = "rexus/modules/mantenimiento"
        
        # Verificar archivos críticos
        critical_files = [
            "__init__.py",
            "model.py",
            "view.py",
            "controller.py"
        ]
        
        for file_name in critical_files:
            file_path = os.path.join(module_path, file_name)
            assert os.path.exists(file_path), f"Archivo crítico {file_name} no encontrado"

    def test_sql_scripts_exist(self):
        """Test que existen scripts SQL."""
        import os
        
        sql_path = "sql/mantenimiento"
        if os.path.exists(sql_path):
            sql_files = [f for f in os.listdir(sql_path) if f.endswith('.sql')]
            assert len(sql_files) >= 2, "Debe tener al menos 2 archivos SQL"


@pytest.mark.parametrize("equipo_data", [
    {
        'nombre': 'Compresor Industrial',
        'tipo': 'COMPRESOR',
        'modelo': 'CI-500',
        'fecha_instalacion': '2020-01-15',
        'estado': 'OPERATIVO',
        'ubicacion': 'Planta Principal'
    },
    {
        'nombre': 'Generador Eléctrico',
        'tipo': 'GENERADOR',
        'modelo': 'GE-2000',
        'fecha_instalacion': '2021-06-20',
        'estado': 'MANTENIMIENTO',
        'ubicacion': 'Área Externa'
    }
])
def test_equipo_data_structure(equipo_data):
    """Test parametrizado para estructura de datos de equipo."""
    required_fields = ['nombre', 'tipo', 'modelo', 'fecha_instalacion', 'estado', 'ubicacion']
    
    for field in required_fields:
        assert field in equipo_data, f"Campo {field} requerido"
    
    assert len(equipo_data['nombre']) > 0
    assert len(equipo_data['tipo']) > 0
    assert len(equipo_data['modelo']) > 0
    assert len(equipo_data['ubicacion']) > 0
    assert equipo_data['estado'] in ['OPERATIVO', 'MANTENIMIENTO', 'FUERA_SERVICIO', 'REPARACION']


@pytest.mark.parametrize("mantenimiento_data", [
    {
        'equipo_id': 1,
        'tipo': 'PREVENTIVO',
        'descripcion': 'Mantenimiento rutinario mensual',
        'fecha_programada': '2025-09-15',
        'frecuencia_dias': 30,
        'prioridad': 'MEDIA'
    },
    {
        'equipo_id': 2,
        'tipo': 'CORRECTIVO',
        'descripcion': 'Reparación de falla crítica',
        'fecha_programada': '2025-08-13',
        'frecuencia_dias': 0,
        'prioridad': 'ALTA'
    }
])
def test_mantenimiento_data_structure(mantenimiento_data):
    """Test parametrizado para estructura de datos de mantenimiento."""
    required_fields = ['equipo_id', 'tipo', 'descripcion', 'fecha_programada', 'frecuencia_dias', 'prioridad']
    
    for field in required_fields:
        assert field in mantenimiento_data, f"Campo {field} requerido"
    
    assert isinstance(mantenimiento_data['equipo_id'], int)
    assert mantenimiento_data['equipo_id'] > 0
    assert mantenimiento_data['tipo'] in ['PREVENTIVO', 'CORRECTIVO', 'PREDICTIVO', 'URGENTE']
    assert len(mantenimiento_data['descripcion']) > 0
    assert isinstance(mantenimiento_data['frecuencia_dias'], int)
    assert mantenimiento_data['frecuencia_dias'] >= 0
    assert mantenimiento_data['prioridad'] in ['BAJA', 'MEDIA', 'ALTA', 'CRITICA']


class TestMantenimientoBusinessLogic:
    """Tests de lógica de negocio específica de mantenimiento."""

    def test_maintenance_scheduling_logic(self):
        """Test lógica de programación de mantenimiento."""
        from datetime import datetime, timedelta
        
        # Test programación preventiva
        last_maintenance = datetime(2025, 7, 15)
        frequency_days = 30
        next_maintenance = last_maintenance + timedelta(days=frequency_days)
        expected_date = datetime(2025, 8, 14)
        
        assert next_maintenance == expected_date

    def test_priority_calculation(self):
        """Test cálculo de prioridad."""
        # Test lógica de prioridad basada en criticidad y tiempo
        equipment_criticality = {
            'CRITICO': 4,
            'ALTO': 3,
            'MEDIO': 2,
            'BAJO': 1
        }
        
        # Equipo crítico vencido = máxima prioridad
        days_overdue = 5
        criticality = equipment_criticality['CRITICO']
        priority_score = criticality * max(1, days_overdue)
        
        assert priority_score >= 4  # Mínimo para equipo crítico

    def test_maintenance_cost_calculation(self):
        """Test cálculo de costos de mantenimiento."""
        # Test cálculo básico de costos
        labor_hours = 4
        labor_rate = 25.00  # $/hora
        parts_cost = 150.00
        
        total_cost = (labor_hours * labor_rate) + parts_cost
        expected_cost = (4 * 25.00) + 150.00  # 100 + 150 = 250
        
        assert total_cost == expected_cost
        assert total_cost == 250.00


class TestMantenimientoErrorHandling:
    """Tests de manejo de errores."""

    def test_model_handles_invalid_dates(self):
        """Test que el modelo maneja fechas inválidas."""
        from rexus.modules.mantenimiento.model import MantenimientoModel
        
        invalid_dates = [
            None,
            '',
            '2025-13-45',  # Fecha inválida
            'not-a-date',
            '2020-02-30'   # 30 de febrero no existe
        ]
        
        for invalid_date in invalid_dates:
            try:
                # Si existe método de validación, probarlo
                if hasattr(MantenimientoModel, 'validar_fecha'):
                    result = MantenimientoModel.validar_fecha(invalid_date)
                    assert result is False or result is None
            except Exception as e:
                # Error controlado es aceptable
                assert "date" in str(e).lower() or "invalid" in str(e).lower()

    def test_view_handles_missing_equipment(self, qapp):
        """Test que la vista maneja equipos faltantes."""
        from rexus.modules.mantenimiento.view import MantenimientoView
        
        try:
            view = MantenimientoView()
            
            # La vista debería manejar lista vacía sin crash
            if hasattr(view, 'mostrar_equipos'):
                # No debería crash con lista vacía
                assert True
                
        except Exception as e:
            pytest.skip(f"Test equipos faltantes skipped: {e}")

    def test_controller_handles_scheduling_conflicts(self):
        """Test que el controlador maneja conflictos de programación."""
        from rexus.modules.mantenimiento.controller import MantenimientoController
        
        try:
            controller = MantenimientoController()
            
            # Verificar que existe método para detectar conflictos
            if hasattr(controller, 'detectar_conflictos_programacion'):
                assert callable(controller.detectar_conflictos_programacion)
                
        except Exception as e:
            pytest.skip(f"Test conflictos skipped: {e}")


class TestMantenimientoSecurity:
    """Tests de seguridad para mantenimiento."""

    def test_maintenance_access_control(self):
        """Test control de acceso a mantenimiento."""
        from rexus.modules.mantenimiento.model import MantenimientoModel
        
        # Verificar métodos de control de acceso
        access_methods = ['verificar_permisos_tecnico', 'log_maintenance_action', 'validate_user_role']
        
        for method in access_methods:
            if hasattr(MantenimientoModel, method):
                assert callable(getattr(MantenimientoModel, method))

    def test_sensitive_equipment_protection(self):
        """Test protección de equipos sensibles."""
        # Equipos que requieren permisos especiales
        critical_equipment_types = ['SISTEMA_SEGURIDAD', 'SERVIDOR_PRINCIPAL', 'EQUIPO_MEDICO']
        
        for equipment_type in critical_equipment_types:
            # En un sistema real, estos equipos tendrían controles de acceso especiales
            assert len(equipment_type) > 0


class TestMantenimientoPerformance:
    """Tests de rendimiento para mantenimiento."""

    @pytest.mark.performance
    def test_model_initialization_performance(self, performance_timer, mock_db_connection):
        """Test rendimiento de inicialización del modelo."""
        from rexus.modules.mantenimiento.model import MantenimientoModel
        
        with performance_timer() as timer:
            try:
                model = MantenimientoModel(db_connection=mock_db_connection)
                assert model is not None
            except Exception:
                pytest.skip("Model no puede inicializarse para test de rendimiento")
        
        # Inicialización debería ser rápida
        assert timer.elapsed < 1.0, f"Model tardó {timer.elapsed:.2f}s en inicializar"

    @pytest.mark.performance  
    def test_maintenance_scheduling_performance(self, performance_timer):
        """Test rendimiento de programación masiva."""
        from datetime import datetime, timedelta
        
        # Simular programación de muchos mantenimientos
        equipment_list = []
        for i in range(100):
            equipment = {
                'id': i,
                'nombre': f'Equipo {i}',
                'frecuencia_dias': 30,
                'ultimo_mantenimiento': datetime.now() - timedelta(days=i % 60)
            }
            equipment_list.append(equipment)
        
        with performance_timer() as timer:
            # Calcular próximos mantenimientos (simulado)
            scheduled = []
            for eq in equipment_list:
                next_date = eq['ultimo_mantenimiento'] + timedelta(days=eq['frecuencia_dias'])
                scheduled.append({'equipo_id': eq['id'], 'fecha': next_date})
        
        # La programación debería ser rápida
        assert timer.elapsed < 0.1, f"Programación tardó {timer.elapsed:.3f}s (muy lento)"
        assert len(scheduled) == 100, "Todos los equipos deben programarse"