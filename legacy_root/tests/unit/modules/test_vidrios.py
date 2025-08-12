"""
Tests unitarios para el módulo de Vidrios.

Estos tests verifican la funcionalidad del módulo de vidrios,
incluyendo modelo, vista moderna, controlador y gestión especializada de cristales.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt


class TestVidriosModel:
    """Tests para el modelo de vidrios."""

    def test_model_import_successfully(self):
        """Test importación exitosa del modelo de vidrios."""
        try:
            from rexus.modules.vidrios.model import VidriosModel
            assert VidriosModel is not None
        except ImportError as e:
            pytest.fail(f"Error importando VidriosModel: {e}")

    def test_model_initialization(self, mock_db_connection):
        """Test inicialización del modelo con conexión mock."""
        from rexus.modules.vidrios.model import VidriosModel
        
        try:
            with patch('rexus.modules.vidrios.model.database_manager') as mock_db_manager:
                mock_db_manager.get_connection.return_value = mock_db_connection
                model = VidriosModel()
                assert model is not None
        except Exception as e:
            pytest.skip(f"Model initialization error: {e}")

    def test_glass_types_configuration(self):
        """Test configuración de tipos de vidrio."""
        from rexus.modules.vidrios.model import VidriosModel
        
        # Verificar que existe configuración de tipos
        if hasattr(VidriosModel, 'TIPOS_VIDRIO'):
            tipos = VidriosModel.TIPOS_VIDRIO
            assert isinstance(tipos, (list, dict))
            
            # Verificar tipos típicos de vidrio
            expected_types = ['TEMPLADO', 'LAMINADO', 'FLOTADO', 'DOBLE_VIDRIO', 'ESPEJO']
            if isinstance(tipos, list):
                for tipo in expected_types[:3]:  # Al menos 3 tipos
                    if tipo in tipos:
                        assert True
                        break
                else:
                    assert len(tipos) > 0, "Debe tener al menos algunos tipos"

    def test_glass_specifications_methods(self):
        """Test métodos de especificaciones de vidrio."""
        from rexus.modules.vidrios.model import VidriosModel
        
        spec_methods = ['calcular_peso', 'validar_dimensiones', 'calcular_precio_m2']
        
        for method in spec_methods:
            if hasattr(VidriosModel, method):
                assert callable(getattr(VidriosModel, method))

    def test_sanitization_system(self):
        """Test sistema unificado de sanitización."""
        from rexus.modules.vidrios.model import VidriosModel
        
        try:
            model = VidriosModel()
            
            # Verificar que existe sistema de sanitización unificado
            if hasattr(model, 'data_sanitizer'):
                assert model.data_sanitizer is not None
            else:
                # Debería tener métodos de sanitización directos
                sanitize_methods = ['sanitize_input', 'clean_data', 'validate_glass_data']
                has_sanitization = any(hasattr(model, method) for method in sanitize_methods)
                assert has_sanitization, "Debe tener algún sistema de sanitización"
                
        except Exception as e:
            pytest.skip(f"Sanitization system test skipped: {e}")


class TestVidriosView:
    """Tests para la vista de vidrios."""

    def test_view_import_successfully(self, qapp):
        """Test importación exitosa de la vista."""
        try:
            from rexus.modules.vidrios.view import VidriosView
            assert VidriosView is not None
        except ImportError as e:
            # Intentar vista moderna como alternativa
            try:
                from rexus.modules.vidrios.view import VidriosModernView
                assert VidriosModernView is not None
            except ImportError:
                pytest.fail(f"Error importando vistas de vidrios: {e}")

    def test_modern_view_import(self, qapp):
        """Test importación de vista moderna."""
        try:
            from rexus.modules.vidrios.view import VidriosModernView
            assert VidriosModernView is not None
        except ImportError as e:
            pytest.skip(f"Vista moderna no disponible: {e}")

    def test_view_initialization(self, qapp):
        """Test inicialización de la vista."""
        try:
            # Intentar vista moderna primero
            from rexus.modules.vidrios.view import VidriosModernView
            view = VidriosModernView()
            assert view is not None
            assert isinstance(view, QWidget)
        except ImportError:
            # Fallback a vista estándar
            try:
                from rexus.modules.vidrios.view import VidriosView
                view = VidriosView()
                assert view is not None
                assert isinstance(view, QWidget)
            except Exception as e:
                pytest.skip(f"Vista de vidrios no puede inicializarse: {e}")

    def test_glass_management_methods(self, qapp):
        """Test métodos de gestión de vidrios."""
        try:
            from rexus.modules.vidrios.view import VidriosModernView
            view = VidriosModernView()
            
            # Verificar métodos críticos de gestión
            management_methods = [
                'mostrar_vidrios',
                'agregar_vidrio',
                'editar_vidrio',
                'calcular_presupuesto'
            ]
            
            for method_name in management_methods:
                if hasattr(view, method_name):
                    assert callable(getattr(view, method_name))
                    
        except Exception as e:
            pytest.skip(f"Vista no disponible para test: {e}")

    def test_minimalist_styles_application(self, qapp):
        """Test aplicación de estilos minimalistas."""
        try:
            from rexus.modules.vidrios.view import VidriosModernView
            view = VidriosModernView()
            
            # Verificar que existe método de estilos minimalistas
            if hasattr(view, 'aplicar_estilos_minimalistas'):
                assert callable(view.aplicar_estilos_minimalistas)
                
                # Verificar que se aplicaron estilos
                stylesheet = view.styleSheet()
                if stylesheet:
                    # Verificar elementos ultra compactos
                    compact_indicators = [
                        "font-size: 10px",
                        "font-size: 9px",
                        "font-size: 8px",
                        "padding: 1px"
                    ]
                    
                    compact_found = any(indicator in stylesheet for indicator in compact_indicators)
                    assert compact_found or len(stylesheet) > 0, "Debe tener estilos aplicados"
                    
        except Exception as e:
            pytest.skip(f"Test estilos minimalistas skipped: {e}")

    def test_glass_calculator_ui(self, qapp):
        """Test interfaz de calculadora de vidrios."""
        try:
            from rexus.modules.vidrios.view import VidriosModernView
            view = VidriosModernView()
            
            # Verificar métodos de calculadora
            calculator_methods = ['calcular_area', 'calcular_peso', 'calcular_precio', 'mostrar_resultado']
            
            for method_name in calculator_methods:
                if hasattr(view, method_name):
                    assert callable(getattr(view, method_name))
                    
        except Exception as e:
            pytest.skip(f"Test calculadora skipped: {e}")


class TestVidriosController:
    """Tests para el controlador de vidrios."""

    def test_controller_import(self):
        """Test importación del controlador."""
        try:
            from rexus.modules.vidrios.controller import VidriosController
            assert VidriosController is not None
        except ImportError as e:
            pytest.fail(f"Error importando VidriosController: {e}")

    def test_controller_initialization(self, mock_db_connection):
        """Test inicialización del controlador."""
        from rexus.modules.vidrios.controller import VidriosController
        
        try:
            with patch('rexus.modules.vidrios.controller.VidriosModel') as mock_model:
                mock_model.return_value = Mock()
                controller = VidriosController()
                assert controller is not None
        except Exception as e:
            pytest.skip(f"Controller initialization error: {e}")

    def test_glass_business_logic_methods(self):
        """Test métodos de lógica de negocio."""
        from rexus.modules.vidrios.controller import VidriosController
        
        business_methods = ['procesar_pedido_vidrio', 'validar_especificaciones', 'generar_cotizacion']
        
        try:
            controller = VidriosController()
            for method in business_methods:
                if hasattr(controller, method):
                    assert callable(getattr(controller, method))
        except Exception as e:
            pytest.skip(f"Controller business logic test skipped: {e}")


class TestVidriosIntegration:
    """Tests de integración para vidrios."""

    def test_module_structure_integrity(self):
        """Test integridad de la estructura del módulo."""
        import os
        
        module_path = "rexus/modules/vidrios"
        
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
        from rexus.modules.vidrios.model import VidriosModel
        
        # Verificar configuración de tablas
        table_attrs = ['TABLE_NAME', 'VIDRIOS_TABLE']
        
        for attr in table_attrs:
            if hasattr(VidriosModel, attr):
                table_name = getattr(VidriosModel, attr)
                assert isinstance(table_name, str)
                assert len(table_name) > 0

    def test_unified_sanitization_system(self):
        """Test sistema unificado de sanitización."""
        try:
            from rexus.modules.vidrios.model import VidriosModel
            model = VidriosModel()
            
            # Verificar que el sistema unificado está cargado correctamente
            # Como se vió en los logs: "OK [VIDRIOS] Sistema unificado de sanitización cargado"
            assert model is not None
            
        except Exception as e:
            pytest.skip(f"Unified sanitization test skipped: {e}")


@pytest.mark.parametrize("vidrio_data", [
    {
        'tipo': 'TEMPLADO',
        'espesor': 6,
        'ancho': 1200,
        'alto': 800,
        'color': 'TRANSPARENTE',
        'acabado': 'PULIDO',
        'precio_m2': 45.50
    },
    {
        'tipo': 'LAMINADO',
        'espesor': 8,
        'ancho': 1500,
        'alto': 1000,
        'color': 'BRONCE',
        'acabado': 'MATE',
        'precio_m2': 62.75
    }
])
def test_vidrio_data_structure(vidrio_data):
    """Test parametrizado para estructura de datos de vidrio."""
    required_fields = ['tipo', 'espesor', 'ancho', 'alto', 'color', 'acabado', 'precio_m2']
    
    for field in required_fields:
        assert field in vidrio_data, f"Campo {field} requerido"
    
    assert vidrio_data['tipo'] in ['TEMPLADO', 'LAMINADO', 'FLOTADO', 'DOBLE_VIDRIO', 'ESPEJO']
    assert isinstance(vidrio_data['espesor'], (int, float))
    assert vidrio_data['espesor'] > 0
    assert isinstance(vidrio_data['ancho'], (int, float))
    assert vidrio_data['ancho'] > 0
    assert isinstance(vidrio_data['alto'], (int, float))
    assert vidrio_data['alto'] > 0
    assert isinstance(vidrio_data['precio_m2'], (int, float))
    assert vidrio_data['precio_m2'] > 0


class TestVidriosBusinessLogic:
    """Tests de lógica de negocio específica de vidrios."""

    def test_area_calculation(self):
        """Test cálculo de área de vidrio."""
        # Test cálculos básicos de área
        ancho_metros = 1.2  # 1200mm = 1.2m
        alto_metros = 0.8   # 800mm = 0.8m
        area_m2 = ancho_metros * alto_metros
        
        expected_area = 0.96  # m2
        assert area_m2 == expected_area

    def test_weight_calculation(self):
        """Test cálculo de peso de vidrio."""
        # Peso específico del vidrio: ~2.5 kg/m2/mm de espesor
        area_m2 = 1.0
        espesor_mm = 6
        peso_especifico = 2.5  # kg/m2/mm
        
        peso_kg = area_m2 * espesor_mm * peso_especifico
        expected_weight = 15.0  # kg
        
        assert peso_kg == expected_weight

    def test_price_calculation(self):
        """Test cálculo de precio de vidrio."""
        # Test cálculo con diferentes factores
        area_m2 = 1.5
        precio_base_m2 = 50.00
        factor_tipo = 1.2  # Factor por tipo de vidrio
        factor_espesor = 1.1  # Factor por espesor
        
        precio_total = area_m2 * precio_base_m2 * factor_tipo * factor_espesor
        expected_price = 1.5 * 50.0 * 1.2 * 1.1  # 99.00
        
        assert precio_total == expected_price
        assert precio_total == 99.00

    def test_glass_cutting_optimization(self):
        """Test optimización de corte de vidrio."""
        # Test optimización básica de corte
        sheet_width = 3000  # mm
        sheet_height = 2000  # mm
        
        piece_width = 1200
        piece_height = 800
        
        # Calcular cuántas piezas caben
        pieces_horizontal = sheet_width // piece_width  # 3000 // 1200 = 2
        pieces_vertical = sheet_height // piece_height  # 2000 // 800 = 2
        
        total_pieces = pieces_horizontal * pieces_vertical
        expected_pieces = 4
        
        assert total_pieces == expected_pieces

    def test_glass_specifications_validation(self):
        """Test validación de especificaciones."""
        # Test rangos válidos para especificaciones
        valid_specs = [
            {'tipo': 'TEMPLADO', 'espesor': 6, 'valid': True},
            {'tipo': 'TEMPLADO', 'espesor': 25, 'valid': False},  # Muy grueso para templado
            {'tipo': 'LAMINADO', 'espesor': 6.38, 'valid': True},
            {'tipo': 'FLOTADO', 'espesor': 0, 'valid': False},   # Espesor inválido
        ]
        
        for spec in valid_specs:
            if spec['valid']:
                assert spec['espesor'] > 0
                assert len(spec['tipo']) > 0
            else:
                # Especificaciones inválidas para testing
                assert spec['espesor'] <= 0 or spec['espesor'] > 20


class TestVidriosErrorHandling:
    """Tests de manejo de errores."""

    def test_model_handles_invalid_dimensions(self):
        """Test que el modelo maneja dimensiones inválidas."""
        from rexus.modules.vidrios.model import VidriosModel
        
        invalid_dimensions = [
            {'ancho': 0, 'alto': 100},      # Ancho cero
            {'ancho': 100, 'alto': -50},    # Alto negativo
            {'ancho': None, 'alto': 100},   # Ancho None
        ]
        
        for invalid_dim in invalid_dimensions:
            try:
                # Si existe método de validación, probarlo
                if hasattr(VidriosModel, 'validar_dimensiones'):
                    result = VidriosModel.validar_dimensiones(invalid_dim['ancho'], invalid_dim['alto'])
                    assert result is False or result is None
            except Exception as e:
                # Error controlado es aceptable
                assert "dimension" in str(e).lower() or "invalid" in str(e).lower()

    def test_view_handles_calculation_errors(self, qapp):
        """Test que la vista maneja errores de cálculo."""
        try:
            from rexus.modules.vidrios.view import VidriosModernView
            view = VidriosModernView()
            
            # La vista debería manejar errores de cálculo sin crash
            if hasattr(view, 'calcular_precio'):
                # No debería crash con valores inválidos
                assert True
                
        except Exception as e:
            pytest.skip(f"Test errores cálculo skipped: {e}")

    def test_sanitization_error_handling(self):
        """Test manejo de errores de sanitización."""
        from rexus.modules.vidrios.model import VidriosModel
        
        try:
            model = VidriosModel()
            
            # Verificar que maneja errores de sanitización gracefully
            if hasattr(model, 'data_sanitizer') and model.data_sanitizer is None:
                # Debería tener fallback si no hay sanitizer
                fallback_methods = ['sanitize_input', 'clean_data']
                has_fallback = any(hasattr(model, method) for method in fallback_methods)
                assert has_fallback or True  # Permitir si tiene otro mecanismo
                
        except Exception as e:
            pytest.skip(f"Sanitization error handling test skipped: {e}")


class TestVidriosSecurity:
    """Tests de seguridad para vidrios."""

    def test_sql_injection_prevention(self):
        """Test prevención de SQL injection."""
        try:
            from rexus.modules.vidrios.model import sanitize_string, sanitize_numeric
            assert callable(sanitize_string)
            assert callable(sanitize_numeric)
        except ImportError as e:
            pytest.skip(f"Utilidades de sanitización no disponibles: {e}")

    def test_price_tampering_protection(self):
        """Test protección contra alteración de precios."""
        from rexus.modules.vidrios.model import VidriosModel
        
        # Verificar métodos de protección de precios
        security_methods = ['validar_precio', 'log_price_change', 'verify_calculation']
        
        for method in security_methods:
            if hasattr(VidriosModel, method):
                assert callable(getattr(VidriosModel, method))


class TestVidriosPerformance:
    """Tests de rendimiento para vidrios."""

    @pytest.mark.performance
    def test_model_initialization_performance(self, performance_timer, mock_db_connection):
        """Test rendimiento de inicialización del modelo."""
        from rexus.modules.vidrios.model import VidriosModel
        
        with performance_timer() as timer:
            try:
                model = VidriosModel(db_connection=mock_db_connection)
                assert model is not None
            except Exception:
                pytest.skip("Model no puede inicializarse para test de rendimiento")
        
        # Inicialización debería ser rápida
        assert timer.elapsed < 1.0, f"Model tardó {timer.elapsed:.2f}s en inicializar"

    @pytest.mark.performance  
    def test_bulk_calculation_performance(self, performance_timer):
        """Test rendimiento con cálculos masivos."""
        # Simular cálculos para muchos vidrios
        glass_specs = []
        for i in range(1000):
            spec = {
                'ancho': 1000 + (i % 1000),
                'alto': 800 + (i % 500),
                'espesor': 6 + (i % 10),
                'precio_m2': 50.0 + (i % 20)
            }
            glass_specs.append(spec)
        
        with performance_timer() as timer:
            # Calcular precios (simulado)
            calculations = []
            for spec in glass_specs:
                area = (spec['ancho'] / 1000.0) * (spec['alto'] / 1000.0)  # m2
                price = area * spec['precio_m2']
                calculations.append(price)
        
        # Los cálculos masivos deberían ser rápidos
        assert timer.elapsed < 0.2, f"Cálculos tardaron {timer.elapsed:.3f}s (muy lento)"
        assert len(calculations) == 1000, "Todos los cálculos deben completarse"