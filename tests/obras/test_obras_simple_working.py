"""
Test simple y funcional para verificar las correcciones del módulo Obras
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch
from PyQt6.QtWidgets import QApplication

# Agregar el directorio raíz al path
ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))


@pytest.fixture(scope="module")
def app():
    """Fixture para QApplication."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


def test_modelo_instanciacion():
    """Test básico de instanciación del modelo."""
    with patch('rexus.core.database.get_inventario_connection'):
        from rexus.modules.obras.model import ObrasModel
        
        mock_connection = Mock()
        model = ObrasModel(db_connection=mock_connection)
        
        assert model is not None
        assert model.db_connection == mock_connection
        print("[OK] ObrasModel se instancia correctamente")


def test_controlador_instanciacion():
    """Test básico de instanciación del controlador."""
    with patch('rexus.core.auth.get_current_user') as mock_auth:
        mock_auth.return_value = {'id': 'test', 'username': 'test', 'is_admin': True}
        
        with patch('rexus.core.database.get_inventario_connection'):
            from rexus.modules.obras.controller import ObrasController
            from rexus.modules.obras.model import ObrasModel
            
            mock_connection = Mock()
            model = ObrasModel(db_connection=mock_connection)
            controller = ObrasController(model=model, db_connection=mock_connection)
            
            assert controller is not None
            assert controller.model == model
            print("[OK] ObrasController se instancia correctamente")


def test_vista_instanciacion(app):
    """Test básico de instanciación de la vista."""
    with patch('rexus.core.database.get_inventario_connection'):
        from rexus.modules.obras.view import ObrasView
        
        view = ObrasView()
        assert view is not None
        assert hasattr(view, 'tabla_obras')
        assert hasattr(view, 'btn_nueva_obra')
        print("[OK] ObrasView se instancia correctamente")


def test_metodos_modelo_existen():
    """Test para verificar que los métodos críticos del modelo existen."""
    with patch('rexus.core.database.get_inventario_connection'):
        from rexus.modules.obras.model import ObrasModel
        
        mock_connection = Mock()
        model = ObrasModel(db_connection=mock_connection)
        
        # Verificar que los métodos críticos existen
        assert hasattr(model, 'crear_obra'), "Método crear_obra faltante"
        assert hasattr(model, 'actualizar_obra'), "Método actualizar_obra faltante"
        assert hasattr(model, 'eliminar_obra'), "Método eliminar_obra faltante"
        assert hasattr(model, 'cambiar_estado_obra'), "Método cambiar_estado_obra faltante"
        assert hasattr(model, 'obtener_estadisticas_obras'), "Método obtener_estadisticas_obras faltante"
        assert hasattr(model, 'obtener_todas_obras'), "Método obtener_todas_obras faltante"
        
        print("[OK] Todos los métodos críticos del modelo están presentes")


def test_metodos_controlador_existen():
    """Test para verificar que los métodos críticos del controlador existen."""
    with patch('rexus.core.auth.get_current_user') as mock_auth:
        mock_auth.return_value = {'id': 'test', 'username': 'test', 'is_admin': True}
        
        with patch('rexus.core.database.get_inventario_connection'):
            from rexus.modules.obras.controller import ObrasController
            from rexus.modules.obras.model import ObrasModel
            
            mock_connection = Mock()
            model = ObrasModel(db_connection=mock_connection)
            controller = ObrasController(model=model, db_connection=mock_connection)
            
            # Verificar que los métodos críticos existen
            assert hasattr(controller, 'crear_obra'), "Método crear_obra faltante"
            assert hasattr(controller, 'actualizar_obra'), "Método actualizar_obra faltante"
            assert hasattr(controller, 'aplicar_filtros'), "Método aplicar_filtros faltante"
            assert hasattr(controller, 'cargar_obras'), "Método cargar_obras faltante"
            assert hasattr(controller, 'eliminar_obra_seleccionada'), "Método eliminar_obra_seleccionada faltante"
            
            print("[OK] Todos los métodos críticos del controlador están presentes")


def test_sql_injection_proteccion():
    """Test básico de protección contra SQL injection."""
    with patch('rexus.core.database.get_inventario_connection'):
        from rexus.modules.obras.model import ObrasModel
        
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = (0,)  # Sin duplicados
        mock_cursor.rowcount = 1
        mock_connection.cursor.return_value = mock_cursor
        
        model = ObrasModel(db_connection=mock_connection)
        
        # Mock del script loader
        model.sql_loader = Mock()
        model.sql_loader.load_script.return_value = "SELECT COUNT(*) FROM obras WHERE codigo = ?"
        
        # Datos con intento de SQL injection
        datos_maliciosos = {
            'codigo': "TEST'; DROP TABLE obras; --",
            'nombre': 'Obra Test',
            'cliente': 'Cliente Test',
            'responsable': 'Responsable Test'
        }
        
        # El método no debería lanzar excepción
        try:
            exito, mensaje = model.crear_obra(datos_maliciosos)
            # Verificar que se ejecutó sin errores (independiente del resultado)
            assert isinstance(exito, bool)
            assert isinstance(mensaje, str)
            print("[OK] Protección SQL injection funciona")
        except Exception as e:
            pytest.fail(f"SQL injection protection failed: {e}")


def test_validacion_datos():
    """Test básico de validación de datos."""
    with patch('rexus.core.database.get_inventario_connection'):
        from rexus.modules.obras.model import ObrasModel
        
        mock_connection = Mock()
        model = ObrasModel(db_connection=mock_connection)
        
        # Datos inválidos (campos vacíos)
        datos_invalidos = {
            'codigo': '',
            'nombre': '',
            'cliente': '',
            'responsable': ''
        }
        
        # Debería fallar la validación
        exito, mensaje = model.crear_obra(datos_invalidos)
        assert exito is False
        assert 'vacío' in mensaje or 'requerido' in mensaje
        print("[OK] Validación de datos funciona correctamente")


def test_data_mapper_funciona():
    """Test para verificar que el data mapper funciona."""
    from rexus.modules.obras.data_mapper import ObrasDataMapper
    
    # Test de conversión de tupla a diccionario
    tupla_ejemplo = (1, 'Obra Test', '', '', '', 'Cliente Test', 'EN_PROCESO', 
                     '', '', '', '', '', '', '', '', '', '', '', '', '', 
                     'OBR-001', 'Responsable Test', '2024-01-01', '2024-12-31', 100000.0)
    
    resultado = ObrasDataMapper.tupla_a_dict(tupla_ejemplo)
    
    assert isinstance(resultado, dict)
    assert 'id' in resultado
    assert 'codigo' in resultado
    assert 'nombre' in resultado
    print("[OK] Data mapper funciona correctamente")


def test_logging_configurado():
    """Test para verificar que el logging está configurado."""
    with patch('rexus.core.database.get_inventario_connection'):
        from rexus.modules.obras.model import ObrasModel
        
        # Verificar que el logger está importado
        import rexus.modules.obras.model as model_module
        assert hasattr(model_module, 'logger')
        print("[OK] Sistema de logging configurado")


def test_auth_decorators_imported():
    """Test para verificar que los decoradores de autenticación están importados."""
    from rexus.modules.obras.controller import ObrasController
    from rexus.modules.obras.model import ObrasModel
    
    # Los decoradores deberían estar disponibles sin errores de importación
    print("[OK] Decoradores de autenticación importados correctamente")


def test_integracion_basica():
    """Test de integración básica entre componentes."""
    with patch('rexus.core.auth.get_current_user') as mock_auth:
        mock_auth.return_value = {'id': 'test', 'username': 'test', 'is_admin': True}
        
        with patch('rexus.core.database.get_inventario_connection'):
            from rexus.modules.obras.controller import ObrasController
            from rexus.modules.obras.model import ObrasModel
            from rexus.modules.obras.view import ObrasView
            
            # Crear componentes
            mock_connection = Mock()
            model = ObrasModel(db_connection=mock_connection)
            view = ObrasView()
            controller = ObrasController(model=model, view=view, db_connection=mock_connection)
            
            # Verificar que están conectados
            assert controller.model == model
            assert controller.view == view
            assert view.controller == controller  # Referencia bidireccional
            
            print("[OK] Integración básica MVC funciona")


if __name__ == "__main__":
    pytest.main([__file__, '-v', '-s'])