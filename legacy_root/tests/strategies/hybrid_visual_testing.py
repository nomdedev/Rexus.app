"""
Estrategia de Testing Visual Híbrida - Rexus.app

ANÁLISIS DE APPROACHES:

1. MOCKS para Tests Visuales:
   ✅ PROS:
   - Velocidad extrema de ejecución
   - Control total sobre escenarios
   - Aislamiento completo de dependencias
   - Determinísticos y repetibles
   - No requieren setup de datos
   - Ideales para CI/CD
   
   ❌ CONTRAS:
   - No validan integración real
   - Pueden ocultar bugs de datos reales
   - Requieren mantenimiento cuando cambia la API
   - No detectan problemas de performance con datos grandes

2. DATOS REALES para Tests Visuales:
   ✅ PROS:
   - Validación completa end-to-end
   - Detectan problemas de performance real
   - Validan comportamiento con datos complejos
   - Detectan edge cases con datos reales
   - Mayor confianza en el comportamiento
   
   ❌ CONTRAS:
   - Lentos de ejecutar
   - Difíciles de setup y teardown
   - Pueden ser frágiles (dependencias externas)
   - Difíciles de reproducir consistentemente

RECOMENDACIÓN PARA REXUS.APP:

🎯 ESTRATEGIA HÍBRIDA - "Testing Pyramid Visual":

NIVEL 1 (70%) - UNIT TESTS CON MOCKS:
- Tests rápidos de componentes individuales
- Validación de lógica de rendering
- Comportamiento de widgets específicos

NIVEL 2 (20%) - INTEGRATION TESTS CON DATOS SINTÉTICOS:
- Tests de interacción entre componentes
- Flujos de navegación
- Validación de estados

NIVEL 3 (10%) - E2E TESTS CON DATOS REALES:
- Tests críticos de flujos completos
- Validación de performance
- Tests de regresión visual

RAZONES ESPECÍFICAS PARA REXUS.APP:
1. Es una app empresarial crítica (necesita confiabilidad)
2. Maneja datos financieros (precisión es crucial)
3. Tiene múltiples módulos interdependientes
4. Usuarios empresariales (UX consistente es vital)
5. PyQt6 permite mocking efectivo de componentes UI
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
import json
import time
from typing import Dict, List, Any, Optional
from enum import Enum


class TestingStrategy(Enum):
    """Estrategias de testing disponibles."""
    MOCK_ONLY = "mock_only"
    REAL_DATA = "real_data"
    HYBRID = "hybrid"


class VisualTestConfig:
    """Configuración para tests visuales."""
    
    def __init__(self):
        self.strategy = TestingStrategy.HYBRID
        self.screenshot_enabled = True
        self.performance_tracking = True
        self.mock_database = True
        self.real_data_percentage = 10  # % de tests con datos reales
        
    def should_use_real_data(self, test_name: str) -> bool:
        """Determina si un test específico debe usar datos reales."""
        critical_tests = [
            'test_complete_user_workflow',
            'test_financial_calculations',
            'test_inventory_complex_queries',
            'test_reports_generation'
        ]
        return any(critical in test_name for critical in critical_tests)


class MockDataFactory:
    """Factory para generar datos mock consistentes."""
    
    @staticmethod
    def create_usuarios_mock(count: int = 5) -> List[Dict]:
        """Crea datos mock de usuarios."""
        return [
            {
                'id': i,
                'username': f'user{i}',
                'email': f'user{i}@rexus.app',
                'role': ['admin', 'supervisor', 'usuario'][i % 3],
                'status': 'active',
                'created_at': '2024-01-01',
                'nombre_completo': f'Usuario {i}',
                'permissions': ['read', 'write'] if i % 2 == 0 else ['read']
            }
            for i in range(1, count + 1)
        ]
    
    @staticmethod
    def create_inventario_mock(count: int = 20) -> List[Dict]:
        """Crea datos mock de inventario."""
        materiales = ['Vidrio Templado', 'Herraje Premium', 'Sellador', 'Marco Aluminio']
        return [
            {
                'id': i,
                'codigo': f'MAT{i:03d}',
                'descripcion': f'{materiales[i % len(materiales)]} {i}',
                'stock': (i * 10) % 100,
                'precio_unitario': round(50.0 + (i * 5.5), 2),
                'categoria': ['vidrios', 'herrajes', 'selladores', 'marcos'][i % 4],
                'proveedor': f'Proveedor {(i % 3) + 1}',
                'ubicacion': f'Pasillo {i % 5 + 1}',
                'stock_minimo': 10,
                'activo': True
            }
            for i in range(1, count + 1)
        ]
    
    @staticmethod
    def create_obras_mock(count: int = 10) -> List[Dict]:
        """Crea datos mock de obras."""
        estados = ['planificacion', 'en_progreso', 'pausada', 'completada']
        return [
            {
                'id': i,
                'codigo': f'OBR{i:03d}',
                'descripcion': f'Obra de Construcción {i}',
                'cliente': f'Cliente {i}',
                'responsable_id': (i % 3) + 1,
                'estado': estados[i % len(estados)],
                'fecha_inicio': '2024-01-01',
                'fecha_estimada': '2024-06-01',
                'presupuesto': round(10000 + (i * 5000), 2),
                'direccion': f'Calle {i}, Ciudad',
                'tipo_obra': ['residencial', 'comercial', 'industrial'][i % 3]
            }
            for i in range(1, count + 1)
        ]


class VisualTestValidator:
    """Validador para tests visuales."""
    
    def __init__(self, config: VisualTestConfig):
        self.config = config
        self.screenshots = []
        self.performance_metrics = {}
    
    def validate_widget_rendering(self, widget: QWidget, test_name: str) -> Dict[str, Any]:
        """Valida el rendering de un widget."""
        start_time = time.time()
        
        # Verificaciones básicas
        results = {
            'widget_valid': widget is not None,
            'widget_visible': widget.isVisible() if widget else False,
            'has_layout': widget.layout() is not None if widget else False,
            'children_count': len(widget.children()) if widget else 0,
            'size_valid': widget.size().isValid() if widget else False
        }
        
        # Screenshot si está habilitado
        if self.config.screenshot_enabled and widget:
            screenshot = self._take_screenshot(widget, test_name)
            results['screenshot_path'] = screenshot
        
        # Métricas de performance
        if self.config.performance_tracking:
            render_time = time.time() - start_time
            self.performance_metrics[test_name] = render_time
            results['render_time'] = render_time
        
        return results
    
    def _take_screenshot(self, widget: QWidget, test_name: str) -> Optional[str]:
        """Toma screenshot del widget."""
        try:
            pixmap = widget.grab()
            screenshot_path = f"tests/screenshots/{test_name}.png"
            pixmap.save(screenshot_path)
            self.screenshots.append(screenshot_path)
            return screenshot_path
        except Exception:
            return None
    
    def validate_data_consistency(self, expected_data: List[Dict], displayed_data: List[Dict]) -> Dict[str, Any]:
        """Valida consistencia entre datos esperados y mostrados."""
        return {
            'count_matches': len(expected_data) == len(displayed_data),
            'data_types_consistent': all(
                type(expected.get('id')) == type(displayed.get('id'))
                for expected, displayed in zip(expected_data, displayed_data)
            ),
            'required_fields_present': all(
                all(field in displayed for field in ['id', 'descripcion'])
                for displayed in displayed_data
            ) if displayed_data else True
        }


class HybridTestRunner:
    """Runner para ejecutar tests híbridos."""
    
    def __init__(self):
        self.config = VisualTestConfig()
        self.validator = VisualTestValidator(self.config)
        self.mock_factory = MockDataFactory()
    
    def run_visual_test(self, test_func, test_name: str, **kwargs):
        """Ejecuta un test visual con la estrategia apropiada."""
        use_real_data = self.config.should_use_real_data(test_name)
        
        if use_real_data:
            return self._run_with_real_data(test_func, test_name, **kwargs)
        else:
            return self._run_with_mock_data(test_func, test_name, **kwargs)
    
    def _run_with_mock_data(self, test_func, test_name: str, **kwargs):
        """Ejecuta test con datos mock."""
        # Preparar mocks
        mock_data = self._prepare_mock_data(test_name)
        
        with patch('rexus.core.database.DatabaseConnection') as mock_db:
            mock_db.return_value.execute_query.return_value = mock_data
            
            # Ejecutar test
            result = test_func(**kwargs)
            
            # Validar resultado
            if isinstance(result, QWidget):
                validation = self.validator.validate_widget_rendering(result, test_name)
                return {'test_result': result, 'validation': validation, 'strategy': 'mock'}
            
            return {'test_result': result, 'strategy': 'mock'}
    
    def _run_with_real_data(self, test_func, test_name: str, **kwargs):
        """Ejecuta test con datos reales."""
        # Setup datos reales (si es necesario)
        real_data_setup = self._setup_real_data(test_name)
        
        try:
            # Ejecutar test con datos reales
            result = test_func(**kwargs)
            
            # Validar resultado
            if isinstance(result, QWidget):
                validation = self.validator.validate_widget_rendering(result, test_name)
                return {'test_result': result, 'validation': validation, 'strategy': 'real_data'}
            
            return {'test_result': result, 'strategy': 'real_data'}
            
        finally:
            # Cleanup datos reales
            self._cleanup_real_data(real_data_setup)
    
    def _prepare_mock_data(self, test_name: str) -> List[Dict]:
        """Prepara datos mock según el tipo de test."""
        if 'usuario' in test_name or 'user' in test_name:
            return self.mock_factory.create_usuarios_mock()
        elif 'inventario' in test_name:
            return self.mock_factory.create_inventario_mock()
        elif 'obra' in test_name:
            return self.mock_factory.create_obras_mock()
        else:
            return []
    
    def _setup_real_data(self, test_name: str) -> Dict[str, Any]:
        """Setup para datos reales."""
        # En un caso real, aquí se configurarían datos de test en DB
        return {'setup_completed': True, 'test_name': test_name}
    
    def _cleanup_real_data(self, setup_info: Dict[str, Any]):
        """Cleanup de datos reales."""
        # En un caso real, aquí se limpiarían los datos de test
        pass


# Decorador para tests visuales híbridos
def hybrid_visual_test(test_name: str = None):
    """Decorador para tests visuales híbridos."""
    def decorator(test_func):
        def wrapper(*args, **kwargs):
            runner = HybridTestRunner()
            actual_test_name = test_name or test_func.__name__
            return runner.run_visual_test(test_func, actual_test_name, **kwargs)
        return wrapper
    return decorator


# Fixtures para testing híbrido
@pytest.fixture(scope="function")
def hybrid_test_runner():
    """Fixture para runner de tests híbridos."""
    return HybridTestRunner()


@pytest.fixture(scope="function")
def mock_data_factory():
    """Fixture para factory de datos mock."""
    return MockDataFactory()


@pytest.fixture(scope="function")
def visual_validator(hybrid_test_runner):
    """Fixture para validador visual."""
    return hybrid_test_runner.validator


@pytest.fixture(scope="function")
def usuarios_mock_data(mock_data_factory):
    """Fixture para datos mock de usuarios."""
    return mock_data_factory.create_usuarios_mock()


@pytest.fixture(scope="function")
def inventario_mock_data(mock_data_factory):
    """Fixture para datos mock de inventario."""
    return mock_data_factory.create_inventario_mock()


@pytest.fixture(scope="function")
def obras_mock_data(mock_data_factory):
    """Fixture para datos mock de obras."""
    return mock_data_factory.create_obras_mock()


# Ejemplo de configuración específica para diferentes módulos
MODULE_TEST_CONFIGS = {
    'usuarios': {
        'mock_percentage': 80,
        'critical_tests': ['test_user_creation_complete_flow'],
        'performance_threshold': 0.5  # segundos
    },
    'inventario': {
        'mock_percentage': 70,
        'critical_tests': ['test_inventory_bulk_operations', 'test_stock_calculations'],
        'performance_threshold': 1.0
    },
    'obras': {
        'mock_percentage': 60,
        'critical_tests': ['test_project_timeline_complex', 'test_budget_calculations'],
        'performance_threshold': 1.5
    },
    'reportes': {
        'mock_percentage': 30,  # Los reportes necesitan más datos reales
        'critical_tests': ['test_financial_reports', 'test_inventory_reports'],
        'performance_threshold': 3.0
    }
}


def get_module_config(module_name: str) -> Dict[str, Any]:
    """Obtiene configuración específica para un módulo."""
    return MODULE_TEST_CONFIGS.get(module_name, {
        'mock_percentage': 70,
        'critical_tests': [],
        'performance_threshold': 1.0
    })
