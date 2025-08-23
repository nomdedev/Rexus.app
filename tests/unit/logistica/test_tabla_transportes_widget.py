# -*- coding: utf-8 -*-
"""
Tests unitarios para TablaTransportesWidget
Refactorización de logística - Tests de componente de tabla
"""

import pytest
import sys
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtTest import QTest

# Configurar encoding UTF-8
sys.stdout.reconfigure(encoding='utf-8')

# Agregar path del proyecto
root_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(root_dir))

# Imports a testear
try:
    from rexus.modules.logistica.components.tabla_transportes_widget import TablaTransportesWidget
    from rexus.ui.components.base_components import RexusButton, RexusLineEdit
except ImportError as e:
    pytest.skip(f, allow_module_level=True)

import logging
logger = logging.getLogger(__name__)


class TestTablaTransportesWidget:
    """Tests para widget de tabla de transportes."""
    
    @classmethod
    def setup_class(cls):
        """Configuración inicial para todos los tests."""
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()
    
    def setup_method(self):
        """Configuración para cada test."""
        self.mock_parent = Mock()
        self.mock_db = Mock()
        self.mock_cursor = Mock()
        self.mock_db.cursor.return_value = self.mock_cursor
        
        # Datos de ejemplo para tests
        self.sample_transportes = [
            {
                'id': 1, 'numero': 'T-001', 'estado': 'En tránsito',
                'origen': 'Almacén A', 'destino': 'Cliente B',
                'conductor': 'Juan Pérez', 'vehiculo': 'V-123',
                'fecha_salida': '2025-08-23', 'observaciones': 'Entrega urgente'
            },
            {
                'id': 2, 'numero': 'T-002', 'estado': 'Programado',
                'origen': 'Almacén B', 'destino': 'Cliente C', 
                'conductor': 'María García', 'vehiculo': 'V-456',
                'fecha_salida': '2025-08-24', 'observaciones': 'Normal'
            }
        ]
    
    def test_widget_initialization(self):
        """Test inicialización del widget."""
        widget = TablaTransportesWidget(self.mock_parent)
        
        assert widget is not None
        assert widget.parent_view == self.mock_parent
        assert widget.current_selection is None
        assert hasattr(widget, 'tabla_transportes')
        assert hasattr(widget, 'search_input')
        assert hasattr(widget, 'btn_new')
        assert hasattr(widget, 'btn_edit')
        assert hasattr(widget, 'btn_delete')
    
    def test_configurar_tabla(self):
        """Test configuración de tabla."""
        widget = TablaTransportesWidget(self.mock_parent)
        
        # Verificar configuración de columnas
        assert widget.tabla_transportes.columnCount() == 9
        
        # Verificar headers
        headers = []
        for col in range(widget.tabla_transportes.columnCount()):
            headers.append(widget.tabla_transportes.horizontalHeaderItem(col).text())
        
        expected_headers = [
            "ID", "Número", "Estado", "Origen", "Destino", 
            "Conductor", "Vehículo", "Fecha Salida", "Observaciones"
        ]
        assert headers == expected_headers
        
        # Verificar configuraciones básicas
        assert widget.tabla_transportes.alternatingRowColors() is True
    
    def test_cargar_transportes(self):
        """Test carga de transportes en tabla."""
        widget = TablaTransportesWidget(self.mock_parent)
        
        # Cargar transportes de ejemplo
        widget.cargar_transportes(self.sample_transportes)
        
        # Verificar que se cargaron los datos
        assert widget.tabla_transportes.rowCount() == len(self.sample_transportes)
        assert len(widget.data) == len(self.sample_transportes)
        
        # Verificar datos en primera fila
        first_row_id = widget.tabla_transportes.item(0, 0).text()
        first_row_numero = widget.tabla_transportes.item(0, 1).text()
        
        assert first_row_id == "1"
        assert first_row_numero == "T-001"
    
    def test_cargar_datos_ejemplo(self):
        """Test carga de datos de ejemplo."""
        widget = TablaTransportesWidget(self.mock_parent)
        
        # Llamar método de datos de ejemplo
        widget.cargar_datos_ejemplo()
        
        # Verificar que se cargaron datos
        assert widget.tabla_transportes.rowCount() > 0
        assert len(widget.data) > 0
        
        # Verificar estructura de datos
        primer_transporte = widget.data[0]
        assert 'id' in primer_transporte
        assert 'numero' in primer_transporte
        assert 'estado' in primer_transporte
    
    def test_buscar_transportes_sin_filtro(self):
        """Test búsqueda sin filtro."""
        widget = TablaTransportesWidget(self.mock_parent)
        widget.data = self.sample_transportes.copy()
        
        # Buscar con campo vacío
        widget.search_input.setText("")
        
        with patch.object(widget, 'refresh_data') as mock_refresh:
            widget.buscar_transportes()
            mock_refresh.assert_called_once()
    
    def test_buscar_transportes_con_filtro(self):
        """Test búsqueda con filtro específico."""
        widget = TablaTransportesWidget(self.mock_parent)
        widget.data = self.sample_transportes.copy()
        
        # Mock del método cargar_transportes
        with patch.object(widget, 'cargar_transportes') as mock_cargar:
            # Buscar por número
            widget.search_input.setText("T-001")
            widget.buscar_transportes()
            
            # Verificar que se llamó cargar_transportes con datos filtrados
            mock_cargar.assert_called_once()
            called_data = mock_cargar.call_args[0][0]
            
            # Verificar filtrado
            assert len(called_data) == 1
            assert called_data[0]['numero'] == 'T-001'
    
    def test_selection_changed_enable_buttons(self):
        """Test habilitación de botones al seleccionar."""
        widget = TablaTransportesWidget(self.mock_parent)
        widget.cargar_transportes(self.sample_transportes)
        
        # Verificar estado inicial de botones
        assert widget.btn_edit.isEnabled() is False
        assert widget.btn_delete.isEnabled() is False
        
        # Simular selección de fila
        widget.tabla_transportes.selectRow(0)
        widget.on_selection_changed()
        
        # Verificar que los botones se habilitaron
        assert widget.btn_edit.isEnabled() is True
        assert widget.btn_delete.isEnabled() is True
        assert widget.current_selection is not None
    
    def test_selection_changed_disable_buttons(self):
        """Test deshabilitación de botones al deseleccionar."""
        widget = TablaTransportesWidget(self.mock_parent)
        widget.cargar_transportes(self.sample_transportes)
        
        # Simular selección y luego deselección
        widget.tabla_transportes.selectRow(0)
        widget.on_selection_changed()
        
        # Limpiar selección
        widget.tabla_transportes.clearSelection()
        widget.on_selection_changed()
        
        # Verificar que los botones se deshabilitaron
        assert widget.btn_edit.isEnabled() is False
        assert widget.btn_delete.isEnabled() is False
        assert widget.current_selection is None
    
    @patch('rexus.modules.logistica.components.tabla_transportes_widget.QMessageBox')
    def test_eliminar_transporte_sin_seleccion(self, mock_msgbox):
        """Test eliminación sin selección."""
        widget = TablaTransportesWidget(self.mock_parent)
        
        # Intentar eliminar sin selección
        widget.eliminar_transporte()
        
        # Verificar que se mostró warning
        mock_msgbox.warning.assert_called_once()
    
    @patch('rexus.modules.logistica.components.tabla_transportes_widget.QMessageBox')
    def test_eliminar_transporte_confirmado(self, mock_msgbox):
        """Test eliminación confirmada."""
        widget = TablaTransportesWidget(self.mock_parent)
        widget.cargar_transportes(self.sample_transportes)
        
        # Seleccionar transporte
        widget.tabla_transportes.selectRow(0)
        widget.on_selection_changed()
        
        # Mock confirmación
        mock_msgbox.question.return_value = mock_msgbox.StandardButton.Yes
        
        with patch.object(widget, 'refresh_data') as mock_refresh:
            widget.eliminar_transporte()
            
            # Verificar que se emitió señal
            # (En test real verificaríamos la señal transport_deleted)
            mock_refresh.assert_called_once()
    
    @patch('rexus.modules.logistica.components.tabla_transportes_widget.QMessageBox')
    def test_eliminar_transporte_cancelado(self, mock_msgbox):
        """Test eliminación cancelada."""
        widget = TablaTransportesWidget(self.mock_parent)
        widget.cargar_transportes(self.sample_transportes)
        
        # Seleccionar transporte
        widget.tabla_transportes.selectRow(0)
        widget.on_selection_changed()
        
        # Mock cancelación
        mock_msgbox.question.return_value = mock_msgbox.StandardButton.No
        
        with patch.object(widget, 'refresh_data') as mock_refresh:
            widget.eliminar_transporte()
            
            # Verificar que NO se refrescaron datos
            mock_refresh.assert_not_called()
    
    def test_nuevo_transporte_con_parent(self):
        """Test creación de nuevo transporte con parent disponible."""
        mock_parent = Mock()
        mock_parent.mostrar_dialogo_nuevo_transporte = Mock()
        
        widget = TablaTransportesWidget(mock_parent)
        widget.nuevo_transporte()
        
        # Verificar que se llamó método del parent
        mock_parent.mostrar_dialogo_nuevo_transporte.assert_called_once()
    
    @patch('rexus.modules.logistica.components.tabla_transportes_widget.QMessageBox')
    def test_nuevo_transporte_sin_parent(self, mock_msgbox):
        """Test creación de nuevo transporte sin parent disponible."""
        widget = TablaTransportesWidget(None)
        widget.nuevo_transporte()
        
        # Verificar que se mostró mensaje placeholder
        mock_msgbox.information.assert_called_once()
    
    @patch('rexus.modules.logistica.components.tabla_transportes_widget.QMessageBox')
    def test_exportar_datos_vacios(self, mock_msgbox):
        """Test exportación sin datos."""
        widget = TablaTransportesWidget(self.mock_parent)
        widget.data = []
        
        widget.exportar_datos()
        
        # Verificar warning por datos vacíos
        mock_msgbox.warning.assert_called_once_with(
            widget, "Exportar", "No hay datos para exportar"
        )
    
    @patch('rexus.modules.logistica.components.tabla_transportes_widget.QMessageBox')
    def test_exportar_datos_exitoso(self, mock_msgbox):
        """Test exportación exitosa."""
        widget = TablaTransportesWidget(self.mock_parent)
        widget.data = self.sample_transportes.copy()
        
        # Mock exportación exitosa
        with patch.object(widget, 'export_to_excel', return_value=True):
            widget.exportar_datos()
            
            # Verificar mensaje de éxito
            mock_msgbox.information.assert_called_once_with(
                widget, "Exportar", "Datos exportados exitosamente"
            )
    
    @patch('rexus.modules.logistica.components.tabla_transportes_widget.QMessageBox')
    def test_exportar_datos_error(self, mock_msgbox):
        """Test error en exportación."""
        widget = TablaTransportesWidget(self.mock_parent)
        widget.data = self.sample_transportes.copy()
        
        # Mock error en exportación
        with patch.object(widget, 'export_to_excel', side_effect=Exception("Error de test")):
            widget.exportar_datos()
            
            # Verificar mensaje de error
            mock_msgbox.critical.assert_called_once()
    
    def test_get_selected_transport_sin_seleccion(self):
        """Test obtener transporte seleccionado sin selección."""
        widget = TablaTransportesWidget(self.mock_parent)
        
        result = widget.get_selected_transport()
        
        assert result == {}
    
    def test_get_selected_transport_con_seleccion(self):
        """Test obtener transporte seleccionado con selección."""
        widget = TablaTransportesWidget(self.mock_parent)
        widget.current_selection = self.sample_transportes[0]
        
        result = widget.get_selected_transport()
        
        assert result == self.sample_transportes[0]
    
    def test_update_transport(self):
        """Test actualización de transporte."""
        widget = TablaTransportesWidget(self.mock_parent)
        widget.data = self.sample_transportes.copy()
        
        # Datos actualizados
        updated_data = self.sample_transportes[0].copy()
        updated_data['estado'] = 'Completado'
        updated_data['observaciones'] = 'Entregado exitosamente'
        
        with patch.object(widget, 'cargar_transportes') as mock_cargar:
            widget.update_transport(updated_data)
            
            # Verificar que se actualizó el dato en la lista
            assert widget.data[0]['estado'] == 'Completado'
            assert widget.data[0]['observaciones'] == 'Entregado exitosamente'
            
            # Verificar que se recargó la tabla
            mock_cargar.assert_called_once_with(widget.data)
    
    def test_signals_emitted(self):
        """Test que las señales se emiten correctamente."""
        widget = TablaTransportesWidget(self.mock_parent)
        
        # Mock signal connections
        with patch.object(widget.transport_selected, 'emit') as mock_selected, \
             patch.object(widget.transport_edited, 'emit') as mock_edited:
            
            # Simular selección
            widget.cargar_transportes(self.sample_transportes)
            widget.tabla_transportes.selectRow(0)
            widget.on_selection_changed()
            
            # Verificar señal de selección
            mock_selected.assert_called_once()
            
            # Simular edición
            widget.editar_transporte()
            mock_edited.assert_called_once()


class TestTablaTransportesWidgetIntegration:
    """Tests de integración para TablaTransportesWidget."""
    
    @classmethod
    def setup_class(cls):
        """Configuración inicial."""
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
    
    def test_widget_creation_and_interaction(self):
        """Test creación y interacción básica del widget."""
        mock_parent = Mock()
        widget = TablaTransportesWidget(mock_parent)
        
        # Verificar que se creó correctamente
        assert widget.isVisible() is False  # No mostrado aún
        
        # Cargar datos y mostrar
        widget.cargar_datos_ejemplo()
        widget.show()
        
        # Verificar que tiene datos
        assert widget.tabla_transportes.rowCount() > 0
        
        # Limpiar
        widget.hide()
    
    def test_refresh_data_with_controller(self):
        """Test actualización con controlador mock."""
        mock_parent = Mock()
        mock_controller = Mock()
        mock_controller.get_transportes.return_value = [
            {'id': 99, 'numero': 'T-TEST', 'estado': 'Test'}
        ]
        
        mock_parent.controller = mock_controller
        
        widget = TablaTransportesWidget(mock_parent)
        widget.refresh_data()
        
        # Verificar que se llamó al controlador
        mock_controller.get_transportes.assert_called_once()
    
    def test_error_handling_in_refresh(self):
        """Test manejo de errores en refresh_data."""
        mock_parent = Mock()
        mock_controller = Mock()
        mock_controller.get_transportes.side_effect = Exception("Error de conexión")
        
        mock_parent.controller = mock_controller
        
        widget = TablaTransportesWidget(mock_parent)
        
        # Mock signal emission
        with patch.object(widget.error_occurred, 'emit') as mock_error:
            widget.refresh_data()
            
            # Verificar que se emitió error
            mock_error.assert_called_once()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])