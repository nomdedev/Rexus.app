"""
Tests de integración REPARADOS para la vista de obras.
Utilizan el nuevo adapter y mocking mejorado.
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from PyQt6.QtWidgets import QApplication, QTableWidget
from PyQt6.QtCore import Qt

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Imports reparados
from rexus.modules.obras.model_adapter import MockObrasModel, ObrasModelAdapter


class TestObrasViewDataLoadingFixed:
    """Tests REPARADOS para verificar la carga de datos en la vista de obras."""

    @pytest.fixture
    def app(self):
        """Fixture para QApplication."""
        if not QApplication.instance():
            app = QApplication([])
        else:
            app = QApplication.instance()
        yield app

    @pytest.fixture
    def mock_obras_model(self):
        """Mock del modelo de obras con datos de prueba."""
        return MockObrasModel()

    @pytest.fixture
    def obras_test_data(self):
        """Datos de prueba consistentes con el modelo real."""
        return [
            {
                'id': 1,
                'codigo': 'OBR-001',
                'nombre': 'Edificio Central',
                'descripcion': 'Construcción de edificio principal',
                'cliente': 'Cliente A',
                'fecha_inicio': '2024-01-15',
                'fecha_fin_estimada': '2024-12-15',
                'estado': 'EN_PROCESO',
                'presupuesto_inicial': 150000.0,
                'responsable': 'Juan Pérez'
            },
            {
                'id': 2,
                'codigo': 'OBR-002',
                'nombre': 'Plaza Comercial',
                'descripcion': 'Centro comercial fase 1',
                'cliente': 'Cliente B',
                'fecha_inicio': '2024-02-01',
                'fecha_fin_estimada': '2025-01-30',
                'estado': 'PLANIFICACION',
                'presupuesto_inicial': 250000.0,
                'responsable': 'María García'
            }
        ]

    def test_cargar_datos_iniciales_en_tabla_fixed(self, app, mock_obras_model, obras_test_data):
        """Test REPARADO: cargar datos iniciales en la tabla."""
        
        # Mock del modelo a nivel global
        with patch('rexus.modules.obras.view.ObrasModel', return_value=mock_obras_model):
            # Mock de la conexión de BD
            with patch('rexus.core.database.get_inventario_connection') as mock_conn:
                mock_conn.return_value.connection = Mock()
                
                # Importar y crear vista después del mock
                from rexus.modules.obras.view import ObrasView
                vista = ObrasView()
                
                # Verificar que la tabla existe
                assert hasattr(vista, 'tabla_obras')
                assert isinstance(vista.tabla_obras, QTableWidget)
                
                # Cargar datos en formato de diccionario
                vista.cargar_obras_en_tabla(obras_test_data)
                
                # Verificar que los datos se cargaron
                assert vista.tabla_obras.rowCount() == len(obras_test_data)
                
                # Verificar contenido de la primera fila
                if vista.tabla_obras.rowCount() > 0:
                    codigo_item = vista.tabla_obras.item(0, 0)  # Columna código
                    nombre_item = vista.tabla_obras.item(0, 1)  # Columna nombre
                    
                    assert codigo_item is not None
                    assert nombre_item is not None
                    assert codigo_item.text() == "OBR-001"
                    assert nombre_item.text() == "Edificio Central"

    def test_actualizar_tabla_con_nuevos_datos_fixed(self, app, mock_obras_model, obras_test_data):
        """Test REPARADO: actualizar tabla cuando cambian los datos."""
        
        with patch('rexus.modules.obras.view.ObrasModel', return_value=mock_obras_model):
            with patch('rexus.core.database.get_inventario_connection') as mock_conn:
                mock_conn.return_value.connection = Mock()
                
                from rexus.modules.obras.view import ObrasView
                vista = ObrasView()
                
                # Cargar datos iniciales
                vista.cargar_obras_en_tabla(obras_test_data)
                assert vista.tabla_obras.rowCount() == 2
                
                # Agregar nueva obra
                nueva_obra = {
                    'id': 3,
                    'codigo': 'OBR-003',
                    'nombre': 'Residencial Los Pinos',
                    'descripcion': 'Conjunto residencial',
                    'cliente': 'Cliente C',
                    'fecha_inicio': '2024-03-01',
                    'fecha_fin_estimada': '2025-06-30',
                    'estado': 'PLANIFICACION',
                    'presupuesto_inicial': 180000.0,
                    'responsable': 'Carlos López'
                }
                
                obras_actualizadas = obras_test_data + [nueva_obra]
                vista.cargar_obras_en_tabla(obras_actualizadas)
                
                # Verificar actualización
                assert vista.tabla_obras.rowCount() == 3

    def test_tabla_vacia_cuando_no_hay_datos_fixed(self, app, mock_obras_model):
        """Test REPARADO: tabla vacía cuando no hay datos."""
        
        # Configurar mock para devolver lista vacía
        mock_obras_model._obras = []
        
        with patch('rexus.modules.obras.view.ObrasModel', return_value=mock_obras_model):
            with patch('rexus.core.database.get_inventario_connection') as mock_conn:
                mock_conn.return_value.connection = Mock()
                
                from rexus.modules.obras.view import ObrasView
                vista = ObrasView()
                
                # Cargar datos vacíos
                vista.cargar_obras_en_tabla([])
                
                # Verificar tabla vacía
                assert vista.tabla_obras.rowCount() == 0

    def test_manejo_errores_carga_datos_fixed(self, app):
        """Test REPARADO: manejo de errores al cargar datos."""
        
        # Mock que simula error en el modelo
        mock_model_error = Mock()
        mock_model_error.obtener_todas_obras.side_effect = Exception("Error de BD")
        
        with patch('rexus.modules.obras.view.ObrasModel', return_value=mock_model_error):
            with patch('rexus.core.database.get_inventario_connection') as mock_conn:
                mock_conn.return_value.connection = Mock()
                
                from rexus.modules.obras.view import ObrasView
                vista = ObrasView()
                
                # Verificar que no se produce crash
                assert vista.tabla_obras.rowCount() == 0
                assert vista.model is not None  # Modelo se inicializó aunque falló la carga

    def test_formato_fechas_en_tabla_fixed(self, app, mock_obras_model, obras_test_data):
        """Test REPARADO: verificar formato correcto de fechas."""
        
        with patch('rexus.modules.obras.view.ObrasModel', return_value=mock_obras_model):
            with patch('rexus.core.database.get_inventario_connection') as mock_conn:
                mock_conn.return_value.connection = Mock()
                
                from rexus.modules.obras.view import ObrasView
                vista = ObrasView()
                
                vista.cargar_obras_en_tabla(obras_test_data)
                
                # Verificar formato de fecha
                if vista.tabla_obras.rowCount() > 0:
                    fecha_item = vista.tabla_obras.item(0, 4)  # Columna fecha inicio
                    assert fecha_item is not None
                    
                    fecha_text = fecha_item.text()
                    # Verificar que la fecha está en formato correcto (sin hora)
                    assert len(fecha_text) == 10  # YYYY-MM-DD
                    assert fecha_text.count('-') == 2

    def test_columnas_tabla_configuradas_correctamente_fixed(self, app, mock_obras_model):
        """Test REPARADO: verificar configuración de columnas."""
        
        with patch('rexus.modules.obras.view.ObrasModel', return_value=mock_obras_model):
            with patch('rexus.core.database.get_inventario_connection') as mock_conn:
                mock_conn.return_value.connection = Mock()
                
                from rexus.modules.obras.view import ObrasView
                vista = ObrasView()
                
                # Verificar número de columnas
                assert vista.tabla_obras.columnCount() == 9
                
                # Verificar headers
                headers_esperados = [
                    "Código", "Nombre", "Cliente", "Responsable",
                    "Fecha Inicio", "Fecha Fin", "Estado", "Presupuesto", "Acciones"
                ]
                
                for i, header_esperado in enumerate(headers_esperados):
                    header_actual = vista.tabla_obras.horizontalHeaderItem(i)
                    assert header_actual is not None
                    assert header_actual.text() == header_esperado


if __name__ == "__main__":
    # Ejecutar tests
    import subprocess
    subprocess.run(["python", "-m", "pytest", __file__, "-v"])
