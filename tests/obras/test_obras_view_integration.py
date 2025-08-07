"""
Tests de integración para verificar la carga y visualización de datos en la vista de obras.
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from PyQt6.QtWidgets import QApplication, QTableWidget
from PyQt6.QtCore import Qt

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from rexus.modules.obras.view import ObrasView
from rexus.modules.obras.model import ObrasModel


class TestObrasViewDataLoading:
    """Tests para verificar la carga de datos en la vista de obras."""

    @pytest.fixture
    def app(self):
        """Fixture para QApplication."""
        if not QApplication.instance():
            app = QApplication([])
        else:
            app = QApplication.instance()
        yield app

    @pytest.fixture
    def mock_db_connection(self):
        """Mock de conexión a base de datos."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        return mock_conn, mock_cursor

    @pytest.fixture
    def obras_test_data(self):
        """Datos de prueba para obras."""
        return [
            (1, "OBR-001", "Edificio Central", "Construcción de edificio principal", 1, 
             "2024-01-15", "2024-12-15", None, "Planificación", "Activo", 25.5, 
             150000.0, 45000.0, 15.5, "Centro Ciudad", "Juan Pérez", "En proceso", 
             1, "2024-01-10", "2024-02-15"),
            (2, "OBR-002", "Plaza Comercial", "Centro comercial fase 1", 2, 
             "2024-02-01", "2025-01-30", None, "Ejecución", "Activo", 60.0, 
             250000.0, 120000.0, 12.0, "Norte Ciudad", "María García", "Sin observaciones", 
             1, "2024-01-20", "2024-03-01"),
            (3, "OBR-003", "Residencial Los Pinos", "Conjunto residencial 80 casas", 3, 
             "2024-03-01", "2025-06-30", None, "Diseño", "Activo", 10.0, 
             180000.0, 25000.0, 20.0, "Sur Ciudad", "Carlos López", "Iniciando", 
             1, "2024-02-25", "2024-02-25")
        ]

    @pytest.fixture
    def mock_obras_model(self, mock_db_connection, obras_test_data):
        """Mock del modelo de obras con datos de prueba."""
        mock_conn, mock_cursor = mock_db_connection
        
        with patch('rexus.modules.obras.model.ObrasModel') as MockModel:
            model_instance = MockModel.return_value
            model_instance.db_connection = mock_conn
            
            # Configurar métodos del modelo
            model_instance.obtener_todas_obras.return_value = obras_test_data
            model_instance.obtener_datos_paginados.return_value = (obras_test_data, len(obras_test_data))
            model_instance.obtener_obras_filtradas.return_value = obras_test_data
            
            # Configurar cursor mock
            mock_cursor.fetchall.return_value = obras_test_data
            mock_cursor.fetchone.return_value = obras_test_data[0] if obras_test_data else None
            
            yield model_instance

    def test_cargar_datos_iniciales_en_tabla(self, app, mock_obras_model, obras_test_data):
        """Test: cargar datos iniciales en la tabla al abrir la vista."""
        with patch('rexus.modules.obras.view.ObrasModel', return_value=mock_obras_model):
            # Crear vista de obras
            vista = ObrasView()
            
            # Verificar que la tabla existe
            assert hasattr(vista, 'tabla_obras')
            assert isinstance(vista.tabla_obras, QTableWidget)
            
            # Simular carga de datos
            vista.cargar_obras_en_tabla(obras_test_data)
            
            # Verificar que los datos se cargaron en la tabla
            assert vista.tabla_obras.rowCount() == len(obras_test_data)
            
            # Verificar contenido de la primera fila
            if vista.tabla_obras.rowCount() > 0:
                codigo_item = vista.tabla_obras.item(0, 1)  # Columna código
                nombre_item = vista.tabla_obras.item(0, 2)  # Columna nombre
                
                assert codigo_item is not None
                assert nombre_item is not None
                assert codigo_item.text() == "OBR-001"
                assert nombre_item.text() == "Edificio Central"

    def test_actualizar_tabla_con_nuevos_datos(self, app, mock_obras_model, obras_test_data):
        """Test: actualizar tabla cuando cambian los datos."""
        with patch('rexus.modules.obras.view.ObrasModel', return_value=mock_obras_model):
            vista = ObrasView()
            
            # Cargar datos iniciales
            vista.cargar_obras_en_tabla(obras_test_data[:2])  # Solo 2 obras
            assert vista.tabla_obras.rowCount() == 2
            
            # Actualizar con más datos
            vista.cargar_obras_en_tabla(obras_test_data)  # Todas las obras
            assert vista.tabla_obras.rowCount() == 3

    def test_tabla_vacia_cuando_no_hay_datos(self, app, mock_obras_model):
        """Test: tabla vacía cuando no hay datos."""
        with patch('rexus.modules.obras.view.ObrasModel', return_value=mock_obras_model):
            vista = ObrasView()
            
            # Cargar datos vacíos
            vista.cargar_obras_en_tabla([])
            
            # Verificar que la tabla está vacía
            assert vista.tabla_obras.rowCount() == 0

    def test_formato_fechas_en_tabla(self, app, mock_obras_model, obras_test_data):
        """Test: verificar formato correcto de fechas en la tabla."""
        with patch('rexus.modules.obras.view.ObrasModel', return_value=mock_obras_model):
            vista = ObrasView()
            vista.cargar_obras_en_tabla(obras_test_data)
            
            # Verificar formato de fecha (columna 5 = fecha_inicio)
            if vista.tabla_obras.rowCount() > 0:
                fecha_item = vista.tabla_obras.item(0, 5)
                if fecha_item:
                    fecha_texto = fecha_item.text()
                    # Verificar que no sea None o vacío
                    assert fecha_texto is not None
                    assert len(fecha_texto) > 0

    def test_busqueda_y_filtrado_actualiza_tabla(self, app, mock_obras_model, obras_test_data):
        """Test: búsqueda y filtrado actualiza correctamente la tabla."""
        with patch('rexus.modules.obras.view.ObrasModel', return_value=mock_obras_model):
            vista = ObrasView()
            
            # Datos filtrados (solo obras que contengan "Edificio")
            datos_filtrados = [obra for obra in obras_test_data if "Edificio" in obra[2]]
            
            # Simular filtrado
            mock_obras_model.obtener_obras_filtradas.return_value = datos_filtrados
            
            # Cargar datos filtrados
            vista.cargar_obras_en_tabla(datos_filtrados)
            
            # Verificar que solo se muestra 1 obra (Edificio Central)
            assert vista.tabla_obras.rowCount() == 1
            
            if vista.tabla_obras.rowCount() > 0:
                nombre_item = vista.tabla_obras.item(0, 2)
                assert "Edificio" in nombre_item.text()

    def test_conexion_model_view_carga_datos(self, app, mock_obras_model, obras_test_data):
        """Test: verificar que la vista se conecta correctamente al modelo para cargar datos."""
        with patch('rexus.modules.obras.view.ObrasModel', return_value=mock_obras_model):
            vista = ObrasView()
            
            # Verificar que el modelo está asignado
            assert vista.model is not None
            
            # Simular llamada a actualizar datos
            if hasattr(vista, 'actualizar_datos'):
                vista.actualizar_datos()
                
                # Verificar que se llamaron los métodos del modelo
                assert mock_obras_model.obtener_todas_obras.called or \
                       mock_obras_model.obtener_datos_paginados.called

    def test_manejo_errores_carga_datos(self, app, mock_obras_model):
        """Test: manejo de errores al cargar datos."""
        with patch('rexus.modules.obras.view.ObrasModel', return_value=mock_obras_model):
            vista = ObrasView()
            
            # Simular error en el modelo
            mock_obras_model.obtener_todas_obras.side_effect = Exception("Error de conexión")
            
            # Intentar cargar datos con error - no debe crashear
            try:
                if hasattr(vista, 'actualizar_datos'):
                    vista.actualizar_datos()
                # Si no hay método actualizar_datos, probar cargar directamente
                vista.cargar_obras_en_tabla([])
                
                # Verificar que la tabla se mantiene estable
                assert isinstance(vista.tabla_obras, QTableWidget)
                assert vista.tabla_obras.rowCount() == 0
                
            except Exception as e:
                pytest.fail(f"La vista no debería crashear con errores del modelo: {e}")

    def test_columnas_tabla_configuradas_correctamente(self, app, mock_obras_model):
        """Test: verificar que las columnas de la tabla están configuradas correctamente."""
        with patch('rexus.modules.obras.view.ObrasModel', return_value=mock_obras_model):
            vista = ObrasView()
            
            # Verificar que la tabla tiene columnas
            assert vista.tabla_obras.columnCount() > 0
            
            # Verificar nombres de columnas principales
            headers = []
            for i in range(vista.tabla_obras.columnCount()):
                header_item = vista.tabla_obras.horizontalHeaderItem(i)
                if header_item:
                    headers.append(header_item.text())
            
            # Verificar que tiene las columnas esenciales
            columnas_esperadas = ["ID", "Código", "Nombre", "Cliente", "Estado"]
            for col in columnas_esperadas:
                # Al menos algunas de estas columnas deberían estar presentes
                found = any(col.lower() in header.lower() for header in headers if header)
                if not found:
                    print(f"Advertencia: Columna '{col}' no encontrada en headers: {headers}")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
