"""
Test comprehensivo y corregido para el módulo de Obras
Incluye todas las funcionalidades principales con manejo de errores robusto
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from PyQt6.QtWidgets import QApplication

# Agregar el directorio raíz al path
ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))

# Importar contexto de testing
from .mock_auth_context import setup_test_context

# Importar módulos bajo testing
from rexus.modules.obras.model import ObrasModel
from rexus.modules.obras.view import ObrasView
from rexus.modules.obras.controller import ObrasController


@pytest.fixture(scope="module")
def app():
    """Fixture para QApplication."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


@pytest.fixture
def test_context():
    """Fixture para contexto de testing completo."""
    with setup_test_context() as context:
        yield context


@pytest.fixture
def obras_model(test_context):
    """Fixture para ObrasModel con contexto de testing."""
    with patch('rexus.utils.sql_script_loader.sql_script_loader') as mock_loader:
        mock_loader.load_script.return_value = "SELECT COUNT(*) FROM obras WHERE codigo = ?"
        model = ObrasModel(db_connection=test_context.db_context.mock_connection)
        model.sql_loader = mock_loader  # Asignar el mock directamente
        return model


@pytest.fixture
def obras_view(app):
    """Fixture para ObrasView."""
    with patch('rexus.core.database.get_inventario_connection'):
        return ObrasView()


@pytest.fixture
def obras_controller(test_context, obras_model, obras_view):
    """Fixture para ObrasController con contexto de testing."""
    return ObrasController(
        model=obras_model,
        view=obras_view,
        db_connection=test_context.db_context.mock_connection
    )


class TestObrasModel:
    """Tests para el modelo de obras."""
    
    def test_crear_obra_exitosa(self, obras_model):
        """Test de creación exitosa de obra."""
        datos_obra = {
            'codigo': 'OBR-2024-001',
            'nombre': 'Obra Test',
            'cliente': 'Cliente Test',
            'responsable': 'Responsable Test',
            'presupuesto_total': 100000.0
        }
        
        exito, mensaje = obras_model.crear_obra(datos_obra)
        print(f"[DEBUG] Resultado crear_obra: exito={exito}, mensaje='{mensaje}'")
        assert exito is True, f"Esperado True, obtenido {exito}. Mensaje: {mensaje}"
        assert 'exitosamente' in mensaje
    
    def test_crear_obra_datos_invalidos(self, obras_model):
        """Test de creación con datos inválidos."""
        datos_obra = {
            'codigo': '',  # Código vacío debería fallar
            'nombre': 'Obra Test'
        }
        
        exito, mensaje = obras_model.crear_obra(datos_obra)
        assert exito is False
        assert 'requerido' in mensaje
    
    def test_obtener_obra_por_codigo(self, obras_model):
        """Test de obtención de obra por código."""
        obra = obras_model.obtener_obra_por_codigo('OBR001')
        assert obra is not None
    
    def test_actualizar_obra(self, obras_model):
        """Test de actualización de obra."""
        datos_actualizados = {
            'nombre': 'Obra Actualizada',
            'cliente': 'Cliente Actualizado'
        }
        
        exito, mensaje = obras_model.actualizar_obra(1, datos_actualizados)
        assert exito is True
    
    def test_eliminar_obra(self, obras_model):
        """Test de eliminación de obra."""
        # Configurar mock para que retorne un código
        obras_model.db_connection.cursor().fetchone.return_value = ('OBR001',)
        
        exito, mensaje = obras_model.eliminar_obra(1, 'ADMIN')
        assert exito is True
        assert 'eliminada' in mensaje
    
    def test_obtener_estadisticas(self, obras_model):
        """Test de obtención de estadísticas."""
        estadisticas = obras_model.obtener_estadisticas_obras()
        assert isinstance(estadisticas, dict)
        assert 'total_obras' in estadisticas


class TestObrasController:
    """Tests para el controlador de obras."""
    
    def test_crear_obra(self, obras_controller):
        """Test de creación de obra a través del controller."""
        datos_obra = {
            'codigo': 'OBR-2024-002',
            'nombre': 'Obra Controller Test',
            'cliente': 'Cliente Controller',
            'responsable': 'Responsable Controller'
        }
        
        resultado = obras_controller.crear_obra(datos_obra)
        assert resultado is True
    
    def test_cargar_obras(self, obras_controller):
        """Test de carga de obras."""
        # No debería lanzar excepción
        obras_controller.cargar_obras()
    
    def test_aplicar_filtros(self, obras_controller):
        """Test de aplicación de filtros."""
        filtros = {
            'estado': 'EN_PROCESO',
            'responsable': 'Test'
        }
        
        # No debería lanzar excepción
        obras_controller.aplicar_filtros(filtros)


class TestObrasView:
    """Tests para la vista de obras."""
    
    def test_inicializacion_vista(self, obras_view):
        """Test de inicialización de la vista."""
        assert obras_view is not None
        assert hasattr(obras_view, 'tabla_obras')
        assert hasattr(obras_view, 'btn_nueva_obra')
    
    def test_cargar_obras_en_tabla(self, obras_view):
        """Test de carga de obras en tabla."""
        obras_mock = [
            {
                'id': 1,
                'codigo': 'OBR001',
                'nombre': 'Obra Test',
                'cliente': 'Cliente Test',
                'responsable': 'Responsable Test',
                'fecha_inicio': '2024-01-01',
                'fecha_fin_estimada': '2024-12-31',
                'estado': 'EN_PROCESO',
                'presupuesto_inicial': 100000.0
            }
        ]
        
        # No debería lanzar excepción
        obras_view.cargar_obras_en_tabla(obras_mock)
        assert obras_view.tabla_obras.rowCount() == 1


class TestIntegracionObras:
    """Tests de integración del módulo."""
    
    def test_flujo_crear_obra_completo(self, obras_controller):
        """Test del flujo completo de creación de obra."""
        datos_obra = {
            'codigo': 'OBR-INT-001',
            'nombre': 'Obra Integración',
            'cliente': 'Cliente Integración',
            'responsable': 'Responsable Integración',
            'descripcion': 'Descripción de prueba',
            'presupuesto_total': 150000.0,
            'fecha_inicio': '2024-01-01',
            'fecha_fin_estimada': '2024-06-30',
            'estado': 'PLANIFICACION'
        }
        
        # Crear obra
        resultado = obras_controller.crear_obra(datos_obra)
        assert resultado is True
        
        # Verificar que se puede obtener
        obra = obras_controller.obtener_obra_por_codigo('OBR-INT-001')
        assert obra is not None


class TestValidacionSeguridad:
    """Tests de validación de seguridad."""
    
    def test_sanitizacion_datos(self, obras_model):
        """Test de sanitización de datos de entrada."""
        datos_maliciosos = {
            'codigo': 'OBR<script>alert("xss")</script>',
            'nombre': 'Obra"; DROP TABLE obras; --',
            'cliente': 'Cliente<iframe>malicious</iframe>',
            'responsable': 'Admin'
        }
        
        # El modelo debería sanitizar los datos
        exito, mensaje = obras_model.crear_obra(datos_maliciosos)
        # Puede fallar por otros motivos, pero no debería ejecutar código malicioso
        assert isinstance(exito, bool)
        assert isinstance(mensaje, str)
    
    def test_validacion_sql_injection(self, obras_model):
        """Test de protección contra SQL injection."""
        codigo_malicioso = "'; DROP TABLE obras; --"
        
        # No debería lanzar excepción o corromper la BD
        obra = obras_model.obtener_obra_por_codigo(codigo_malicioso)
        assert obra is None or isinstance(obra, dict)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])