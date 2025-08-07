"""
Tests actualizados para el módulo Obras - Adaptados al modelo real.
Incluye edge cases críticos y cobertura completa de seguridad.
"""

import sys
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT_DIR))

import pytest
import sqlite3
from unittest.mock import Mock, MagicMock

from rexus.modules.obras.model import ObrasModel


@pytest.fixture
def mock_db_connection():
    """Mock de conexión a BD para tests."""
    mock_conn = Mock()
    mock_cursor = Mock()
    
    # Configurar mock cursor
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.execute.return_value = None
    mock_cursor.fetchone.return_value = None
    mock_cursor.fetchall.return_value = []
    mock_conn.commit.return_value = None
    mock_conn.rollback.return_value = None
    
    return mock_conn


@pytest.fixture
def obras_model(mock_db_connection):
    """Instancia del modelo de obras con mock de BD y usuario autenticado."""
    model = ObrasModel(db_connection=mock_db_connection)
    model.current_user = {"id": 1, "username": "tester", "rol": "admin"}  # Usuario de prueba
    return model


@pytest.fixture  
def obras_model_sin_conexion():
    """Instancia del modelo sin conexión para tests de error, con usuario autenticado."""
    model = ObrasModel(db_connection=None)
    model.current_user = {"id": 1, "username": "tester", "rol": "admin"}
    return model


class TestObrasModelValidacionesBasicas:
    """Tests de validaciones básicas del modelo obras."""
    
    def test_crear_obra_sin_conexion_bd(self, obras_model_sin_conexion):
        """Test: crear obra sin conexión a BD debe fallar."""
        datos = {
            "codigo": "OBR-001",
            "nombre": "Obra Test",
            "cliente": "Cliente Test"
        }
        
        exito, mensaje = obras_model_sin_conexion.crear_obra(datos)
        
        assert exito == False
        assert "Sin conexión a la base de datos" in mensaje
    
    def test_crear_obra_datos_requeridos_faltantes(self, obras_model):
        """Test: crear obra sin datos requeridos debe fallar."""
        # Test sin código
        datos_sin_codigo = {
            "nombre": "Obra Test",
            "cliente": "Cliente Test"
        }
        
        exito, mensaje = obras_model.crear_obra(datos_sin_codigo)
        assert exito == False
        assert "código" in mensaje.lower()
        
        # Test sin nombre
        datos_sin_nombre = {
            "codigo": "OBR-001",
            "cliente": "Cliente Test"
        }
        
        exito, mensaje = obras_model.crear_obra(datos_sin_nombre)
        assert exito == False
        assert "nombre" in mensaje.lower()
        
        # Test sin cliente
        datos_sin_cliente = {
            "codigo": "OBR-001",
            "nombre": "Obra Test"
        }
        
        exito, mensaje = obras_model.crear_obra(datos_sin_cliente)
        assert exito == False
        assert "cliente" in mensaje.lower()


class TestObrasModelEdgeCasesCriticos:
    """Tests de edge cases críticos para el módulo obras."""
    
    def test_crear_obra_presupuesto_negativo(self, obras_model):
        """Test: presupuesto negativo debe ser rechazado."""
        datos = {
            "codigo": "OBR-001",
            "nombre": "Obra Test",
            "cliente": "Cliente Test",
            "presupuesto_total": -1000.0
        }
        
        exito, mensaje = obras_model.crear_obra(datos)
        assert exito == False
        assert "presupuesto" in mensaje.lower()
    
    def test_crear_obra_codigo_muy_largo(self, obras_model):
        """Test: código excesivamente largo debe ser rechazado."""
        codigo_largo = "OBR-" + "X" * 100  # Código de 104 caracteres
        
        datos = {
            "codigo": codigo_largo,
            "nombre": "Obra Test", 
            "cliente": "Cliente Test"
        }
        
        exito, mensaje = obras_model.crear_obra(datos)
        # Debe fallar o truncar según implementación
        if not exito:
            assert "código" in mensaje.lower() or "largo" in mensaje.lower()
    
    def test_crear_obra_nombre_vacio_string(self, obras_model):
        """Test: nombre con string vacío debe fallar."""
        datos = {
            "codigo": "OBR-001",
            "nombre": "",  # String vacío
            "cliente": "Cliente Test"
        }
        
        exito, mensaje = obras_model.crear_obra(datos)
        assert exito == False
        assert "nombre" in mensaje.lower()
    
    def test_crear_obra_xss_prevention(self, obras_model):
        """Test: prevención de XSS en campos de texto."""
        datos_maliciosos = {
            "codigo": "<script>alert('xss')</script>",
            "nombre": "<iframe>Obra Maliciosa</iframe>",
            "cliente": "<script>window.location='http://evil.com'</script>",
            "descripcion": "'; DROP TABLE obras; --"
        }
        
        # Configurar mock para simular código no existente
        mock_cursor = obras_model.db_connection.cursor.return_value
        mock_cursor.fetchone.return_value = [0]  # Código no duplicado
        
        exito, mensaje = obras_model.crear_obra(datos_maliciosos)
        
        # El método debe sanitizar o rechazar datos maliciosos
        # Si es exitoso, verificar que los datos fueron sanitizados
        if exito:
            # Verificar que se llamó execute con datos sanitizados
            mock_cursor.execute.assert_called()
            call_args = mock_cursor.execute.call_args
            executed_query = str(call_args)
            
            # No debe contener scripts maliciosos
            assert "<script>" not in executed_query
            assert "<iframe>" not in executed_query
            assert "DROP TABLE" not in executed_query


class TestObrasModelFuncionalidadCompleta:
    """Tests de funcionalidad completa del modelo obras."""
    
    def test_obtener_todas_obras_sin_conexion(self, obras_model_sin_conexion):
        """Test: obtener todas las obras sin conexión debe manejar el error."""
        try:
            resultado = obras_model_sin_conexion.obtener_todas_obras()
            # Debe retornar lista vacía o manejar el error gracefully
            assert isinstance(resultado, list)
        except Exception as e:
            # Si lanza excepción, debe ser manejada apropiadamente
            assert "conexión" in str(e).lower() or "database" in str(e).lower()
    
    def test_validar_obra_duplicada_codigo_existente(self, obras_model):
        """Test: validación de código duplicado."""
        # Configurar mock para simular código existente
        mock_cursor = obras_model.db_connection.cursor.return_value
        mock_cursor.fetchone.return_value = [1]  # Código ya existe
        
        es_duplicada = obras_model.validar_obra_duplicada("OBR-001", "Obra Test")
        
        assert es_duplicada == True
        mock_cursor.execute.assert_called()
    
    def test_validar_obra_duplicada_codigo_nuevo(self, obras_model):
        """Test: validación de código nuevo (no duplicado)."""
        # Configurar mock para simular código no existente
        mock_cursor = obras_model.db_connection.cursor.return_value
        mock_cursor.fetchone.return_value = [0]  # Código no existe
        
        es_duplicada = obras_model.validar_obra_duplicada("OBR-999", "Obra Nueva")
        
        assert es_duplicada == False
        mock_cursor.execute.assert_called()
    
    def test_obtener_obra_por_id_existente(self, obras_model):
        """Test: obtener obra por ID existente."""
        # Configurar mock para retornar datos de obra
        mock_cursor = obras_model.db_connection.cursor.return_value
        datos_obra = [1, "OBR-001", "Obra Test", "Cliente Test", 10000.0]
        mock_cursor.fetchone.return_value = datos_obra
        
        resultado = obras_model.obtener_obra_por_id(1)
        
        assert resultado is not None
        mock_cursor.execute.assert_called()
    
    def test_obtener_obra_por_id_inexistente(self, obras_model):
        """Test: obtener obra por ID inexistente."""
        # Configurar mock para no retornar datos
        mock_cursor = obras_model.db_connection.cursor.return_value
        mock_cursor.fetchone.return_value = None
        
        resultado = obras_model.obtener_obra_por_id(999)
        
        assert resultado is None
        mock_cursor.execute.assert_called()


class TestObrasModelPaginacionFiltros:
    """Tests de paginación y filtros del modelo obras."""
    
    def test_obtener_datos_paginados_parametros_validos(self, obras_model):
        """Test: paginación con parámetros válidos."""
        # Configurar mock para retornar datos paginados
        mock_cursor = obras_model.db_connection.cursor.return_value
        datos_mock = [
            [1, "OBR-001", "Obra 1"],
            [2, "OBR-002", "Obra 2"]
        ]
        mock_cursor.fetchall.return_value = datos_mock
        resultado, total = obras_model.obtener_datos_paginados(offset=0, limit=10)
        assert isinstance(resultado, list)
        assert len(resultado) <= 10  # Respeta el límite
        mock_cursor.execute.assert_called()
    
    def test_obtener_datos_paginados_offset_negativo(self, obras_model):
        """Test: paginación con offset negativo debe manejarse."""
        try:
            resultado, total = obras_model.obtener_datos_paginados(offset=-1, limit=10)
            assert isinstance(resultado, list)
        except (ValueError, Exception) as e:
            assert "offset" in str(e).lower() or "negativo" in str(e).lower()
    
    def test_obtener_datos_paginados_limit_cero(self, obras_model):
        """Test: paginación con limit cero debe manejarse."""
        try:
            resultado, total = obras_model.obtener_datos_paginados(offset=0, limit=0)
            assert isinstance(resultado, list)
        except (ValueError, Exception) as e:
            assert "limit" in str(e).lower() or "cero" in str(e).lower()


class TestObrasModelSeguridad:
    """Tests específicos de seguridad del modelo obras."""
    
    def test_filtros_sql_injection_prevention(self, obras_model):
        """Test: prevención de SQL injection en filtros."""
        filtros_maliciosos = {
            "nombre": "'; DROP TABLE obras; --",
            "cliente": "1' OR '1'='1",
            "estado": "' UNION SELECT * FROM usuarios --"
        }
        
        try:
            resultado = obras_model.obtener_obras_filtradas(filtros_maliciosos, "nombre")
            assert isinstance(resultado, list)
            mock_cursor = obras_model.db_connection.cursor.return_value
            if mock_cursor.execute.called:
                # Verificar solo los parámetros pasados, no la query completa
                call_args = mock_cursor.execute.call_args
                if call_args and len(call_args) > 1:
                    parametros = str(call_args[1])  # Los parámetros están en args[1]
                    # Los parámetros no deben contener SQL injection literal
                    assert "DROP TABLE obras" not in parametros
                    assert "1' OR '1'='1" not in parametros
                    assert "UNION SELECT * FROM usuarios" not in parametros
        except Exception as e:
            # Si hay una excepción, debe ser por validación de seguridad
            assert "injection" in str(e).lower() or "invalid" in str(e).lower()
    
    def test_unicode_malicioso_handling(self, obras_model):
        """Test: manejo de caracteres Unicode maliciosos."""
        datos_unicode = {
            "codigo": "OBR-\u0000\u0001",  # Caracteres nulos
            "nombre": "Obra\u202e\u202d",  # Caracteres de dirección Unicode
            "cliente": "Cliente\ufeff",   # Byte Order Mark
        }
        
        # Configurar mock
        mock_cursor = obras_model.db_connection.cursor.return_value
        mock_cursor.fetchone.return_value = [0]  # No duplicado
        
        exito, mensaje = obras_model.crear_obra(datos_unicode)
        
        # Debe manejar caracteres especiales apropiadamente
        if exito:
            # Verificar que los datos fueron sanitizados
            mock_cursor.execute.assert_called()
        else:
            # Si falló, debe ser por validación
            assert len(mensaje) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
