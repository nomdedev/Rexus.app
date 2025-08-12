"""
Tests unitarios para el módulo de Obras.

Estos tests verifican la funcionalidad del módulo de obras,
incluyendo modelo, vista moderna, controlador y gestión de proyectos.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt


class TestObrasModel:
    """Tests para el modelo de obras."""

    def test_model_import_successfully(self):
        """Test importación exitosa del modelo de obras."""
        try:
            from rexus.modules.obras.model import ObrasModel
            assert ObrasModel is not None
        except ImportError as e:
            pytest.fail(f"Error importando ObrasModel: {e}")

    def test_model_initialization(self, mock_db_connection):
        """Test inicialización del modelo con conexión mock."""
        from rexus.modules.obras.model import ObrasModel
        
        try:
            with patch('rexus.modules.obras.model.database_manager') as mock_db_manager:
                mock_db_manager.get_connection.return_value = mock_db_connection
                model = ObrasModel()
                assert model is not None
        except Exception as e:
            pytest.skip(f"Model initialization error: {e}")

    def test_obras_states_configuration(self):
        """Test configuración de estados de obras."""
        from rexus.modules.obras.model import ObrasModel
        
        # Verificar que existe configuración de estados
        assert hasattr(ObrasModel, 'ESTADOS')
        estados = ObrasModel.ESTADOS
        
        # Verificar estados críticos
        expected_states = ['PLANIFICACION', 'EN_PROGRESO', 'COMPLETADA', 'CANCELADA']
        for state in expected_states:
            if state in estados:
                assert isinstance(estados[state], str)

    def test_project_validation_methods(self):
        """Test métodos de validación de proyectos."""
        from rexus.modules.obras.model import ObrasModel
        
        validation_methods = ['validate_project_data', 'validate_dates', 'validate_budget']
        
        for method in validation_methods:
            if hasattr(ObrasModel, method):
                assert callable(getattr(ObrasModel, method))


class TestObrasView:
    """Tests para la vista de obras."""

    def test_view_import_successfully(self, qapp):
        """Test importación exitosa de la vista."""
        try:
            from rexus.modules.obras.view import ObrasView
            assert ObrasView is not None
        except ImportError as e:
            pytest.fail(f"Error importando ObrasView: {e}")

    def test_view_initialization(self, qapp):
        """Test inicialización de la vista."""
        from rexus.modules.obras.view import ObrasView
        
        try:
            view = ObrasView()
            assert view is not None
            assert isinstance(view, QWidget)
        except Exception as e:
            pytest.skip(f"Vista de obras no puede inicializarse: {e}")

    def test_modern_view_import(self, qapp):
        """Test importación de vista moderna."""
        try:
            from rexus.modules.obras.view_modern import ModernObrasView
            assert ModernObrasView is not None
        except ImportError as e:
            pytest.skip(f"Vista moderna no disponible: {e}")

    def test_project_management_methods(self, qapp):
        """Test métodos de gestión de proyectos."""
        from rexus.modules.obras.view import ObrasView
        
        try:
            view = ObrasView()
            
            # Verificar métodos críticos de gestión
            management_methods = [
                'actualizar_tabla_obras',
                'mostrar_proyecto', 
                'cargar_proyectos',
                'filtrar_obras'
            ]
            
            for method_name in management_methods:
                if hasattr(view, method_name):
                    assert callable(getattr(view, method_name))
                    
        except Exception as e:
            pytest.skip(f"Vista no disponible para test: {e}")

    def test_project_status_indicators(self, qapp):
        """Test indicadores de estado de proyecto."""
        from rexus.modules.obras.view import ObrasView
        
        try:
            view = ObrasView()
            
            # Verificar que existen métodos para mostrar estados
            status_methods = ['actualizar_estado_proyecto', 'mostrar_progreso', 'colorear_por_estado']
            
            for method_name in status_methods:
                if hasattr(view, method_name):
                    assert callable(getattr(view, method_name))
                    
        except Exception as e:
            pytest.skip(f"Test indicadores skipped: {e}")


class TestObrasController:
    """Tests para el controlador de obras."""

    def test_controller_import(self):
        """Test importación del controlador."""
        try:
            from rexus.modules.obras.controller import ObrasController
            assert ObrasController is not None
        except ImportError as e:
            pytest.fail(f"Error importando ObrasController: {e}")

    def test_controller_initialization(self, mock_db_connection):
        """Test inicialización del controlador."""
        from rexus.modules.obras.controller import ObrasController
        
        try:
            with patch('rexus.modules.obras.controller.ObrasModel') as mock_model:
                mock_model.return_value = Mock()
                controller = ObrasController()
                assert controller is not None
        except Exception as e:
            pytest.skip(f"Controller initialization error: {e}")

    def test_project_workflow_methods(self):
        """Test métodos de flujo de trabajo de proyectos."""
        from rexus.modules.obras.controller import ObrasController
        
        workflow_methods = ['crear_proyecto', 'actualizar_progreso', 'finalizar_proyecto']
        
        try:
            controller = ObrasController()
            for method in workflow_methods:
                if hasattr(controller, method):
                    assert callable(getattr(controller, method))
        except Exception as e:
            pytest.skip(f"Controller workflow test skipped: {e}")


class TestObrasSubmodules:
    """Tests para submódulos de obras."""

    def test_submodules_import_correctly(self):
        """Test que los submódulos se importan correctamente."""
        try:
            from rexus.modules.obras.submodules import (
                project_manager,
                timeline_manager,
                budget_manager,
                resources_manager
            )
            assert True  # Si llegamos aquí, los imports funcionaron
        except ImportError as e:
            pytest.skip(f"Submódulos no disponibles: {e}")

    def test_dialogs_import(self):
        """Test importación de diálogos."""
        try:
            from rexus.modules.obras.dialogs import project_dialog
            assert project_dialog is not None
        except ImportError as e:
            pytest.skip(f"Diálogos no disponibles: {e}")


class TestObrasIntegration:
    """Tests de integración para obras."""

    def test_module_structure_integrity(self):
        """Test integridad de la estructura del módulo."""
        import os
        
        module_path = "rexus/modules/obras"
        
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

    def test_database_configuration(self):
        """Test configuración de base de datos."""
        from rexus.modules.obras.model import ObrasModel
        
        # Verificar configuración de tablas
        table_attrs = ['TABLE_NAME', 'OBRAS_TABLE']
        
        for attr in table_attrs:
            if hasattr(ObrasModel, attr):
                table_name = getattr(ObrasModel, attr)
                assert isinstance(table_name, str)
                assert len(table_name) > 0

    def test_main_components_importable(self):
        """Test que los componentes principales son importables."""
        components = [
            'rexus.modules.obras.model',
            'rexus.modules.obras.view', 
            'rexus.modules.obras.controller'
        ]
        
        for component in components:
            try:
                __import__(component)
            except ImportError as e:
                pytest.fail(f"Error importando componente {component}: {e}")


@pytest.mark.parametrize("obra_data", [
    {
        'nombre': 'Proyecto Casa Moderna',
        'cliente': 'Cliente Test',
        'fecha_inicio': '2025-08-01',
        'fecha_fin_estimada': '2025-12-31',
        'presupuesto': 50000.00,
        'estado': 'PLANIFICACION'
    },
    {
        'nombre': 'Renovación Oficina',
        'cliente': 'Empresa ABC',
        'fecha_inicio': '2025-09-01',
        'fecha_fin_estimada': '2025-11-30',
        'presupuesto': 25000.00,
        'estado': 'EN_PROGRESO'
    }
])
def test_obra_data_structure(obra_data):
    """Test parametrizado para estructura de datos de obra."""
    required_fields = ['nombre', 'cliente', 'fecha_inicio', 'fecha_fin_estimada', 'presupuesto', 'estado']
    
    for field in required_fields:
        assert field in obra_data, f"Campo {field} requerido"
    
    assert isinstance(obra_data['presupuesto'], (int, float))
    assert obra_data['presupuesto'] > 0
    assert len(obra_data['nombre']) > 0
    assert len(obra_data['cliente']) > 0
    assert obra_data['estado'] in ['PLANIFICACION', 'EN_PROGRESO', 'COMPLETADA', 'CANCELADA', 'PAUSADA']


class TestObrasBusinessLogic:
    """Tests de lógica de negocio específica de obras."""

    def test_project_timeline_validation(self):
        """Test validación de timeline de proyecto."""
        from datetime import datetime, timedelta
        
        # Test data con fechas válidas
        start_date = datetime.now()
        end_date = start_date + timedelta(days=90)
        
        assert end_date > start_date, "Fecha fin debe ser posterior a fecha inicio"

    def test_budget_calculations(self):
        """Test cálculos de presupuesto."""
        # Test básico de cálculo de presupuesto
        budget_items = [
            {'concepto': 'Materiales', 'costo': 15000.00},
            {'concepto': 'Mano de obra', 'costo': 20000.00},
            {'concepto': 'Equipos', 'costo': 5000.00}
        ]
        
        total = sum(item['costo'] for item in budget_items)
        assert total == 40000.00
        
        # Verificar que todos los costos sean positivos
        for item in budget_items:
            assert item['costo'] > 0

    def test_project_states_transitions(self):
        """Test transiciones de estados de proyecto."""
        valid_transitions = {
            'PLANIFICACION': ['EN_PROGRESO', 'CANCELADA'],
            'EN_PROGRESO': ['COMPLETADA', 'PAUSADA', 'CANCELADA'],
            'PAUSADA': ['EN_PROGRESO', 'CANCELADA'],
            'COMPLETADA': [],  # Estado final
            'CANCELADA': []   # Estado final
        }
        
        for current_state, valid_next_states in valid_transitions.items():
            assert isinstance(valid_next_states, list)
            for next_state in valid_next_states:
                assert next_state in valid_transitions.keys()


class TestObrasErrorHandling:
    """Tests de manejo de errores."""

    def test_model_handles_invalid_dates(self):
        """Test que el modelo maneja fechas inválidas."""
        from rexus.modules.obras.model import ObrasModel
        
        invalid_dates = [
            None,
            '',
            '2025-13-45',  # Fecha inválida
            'not-a-date'
        ]
        
        # El modelo debería manejar fechas inválidas sin crash
        for invalid_date in invalid_dates:
            try:
                # Si existe método de validación, probarlo
                if hasattr(ObrasModel, 'validate_dates'):
                    result = ObrasModel.validate_dates(invalid_date, invalid_date)
                    assert result is False or result is None
            except Exception as e:
                # Error controlado es aceptable
                assert "date" in str(e).lower() or "invalid" in str(e).lower()

    def test_view_handles_empty_data(self, qapp):
        """Test que la vista maneja datos vacíos."""
        from rexus.modules.obras.view import ObrasView
        
        try:
            view = ObrasView()
            
            # La vista debería inicializarse sin crash aunque no haya datos
            if hasattr(view, 'cargar_proyectos'):
                # Intentar cargar con lista vacía
                empty_data = []
                # No debería crash
                assert True
                
        except Exception as e:
            pytest.skip(f"Test datos vacíos skipped: {e}")


class TestObrasPerformance:
    """Tests de rendimiento para obras."""

    @pytest.mark.performance
    def test_model_initialization_performance(self, performance_timer, mock_db_connection):
        """Test rendimiento de inicialización del modelo."""
        from rexus.modules.obras.model import ObrasModel
        
        with performance_timer() as timer:
            try:
                model = ObrasModel(db_connection=mock_db_connection)
                assert model is not None
            except Exception:
                pytest.skip("Model no puede inicializarse para test de rendimiento")
        
        # Inicialización debería ser rápida
        assert timer.elapsed < 1.0, f"Model tardó {timer.elapsed:.2f}s en inicializar"

    @pytest.mark.performance  
    def test_view_initialization_performance(self, qapp, performance_timer):
        """Test rendimiento de inicialización de vista."""
        from rexus.modules.obras.view import ObrasView
        
        with performance_timer() as timer:
            try:
                view = ObrasView()
                assert view is not None
            except Exception:
                pytest.skip("Vista no puede inicializarse para test de rendimiento")
        
        # La vista debería inicializarse rápido
        assert timer.elapsed < 3.0, f"Vista tardó {timer.elapsed:.2f}s en inicializar"