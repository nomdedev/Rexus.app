# -*- coding: utf-8 -*-
"""
Tests unitarios para ServiciosWidget
Tests del widget de gestión de servicios logísticos
"""

import pytest
import sys
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QDialog
from PyQt6.QtCore import Qt
from PyQt6.QtTest import QTest

# Configurar encoding UTF-8
sys.stdout.reconfigure(encoding='utf-8')

# Agregar path del proyecto
root_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(root_dir))

# Imports a testear
try:
    from rexus.modules.logistica.components.servicios_widget import (
        ServiciosWidget, DialogoNuevoServicio, DialogoProgramarServicio
    )
    from rexus.ui.components.base_components import RexusButton
except ImportError as e:
    pytest.skip(f, allow_module_level=True)

import logging
logger = logging.getLogger(__name__)


class TestServiciosWidget:
    """Tests para widget de servicios logísticos."""
    
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
        self.servicios_ejemplo = [
            {
                'id': 1, 'tipo': 'Entrega', 'estado': 'En progreso',
                'cliente': 'Cliente A', 'origen': 'Almacén',
                'destino': 'Oficina Norte', 'programado': '09:00',
                'conductor': 'Juan Pérez', 'observaciones': 'Urgente'
            },
            {
                'id': 2, 'tipo': 'Recogida', 'estado': 'Programado',
                'cliente': 'Cliente B', 'origen': 'Sede Sur',
                'destino': 'Almacén', 'programado': '14:00',
                'conductor': 'María García', 'observaciones': 'Normal'
            }
        ]
    
    def test_widget_initialization(self):
        """Test inicialización del widget."""
        widget = ServiciosWidget(self.mock_parent)
        
        assert widget is not None
        assert widget.parent_view == self.mock_parent
        assert hasattr(widget, 'servicios_activos')
        assert hasattr(widget, 'servicios_programados')
        assert hasattr(widget, 'tabla_activos')
        assert hasattr(widget, 'tabla_programados')
        assert hasattr(widget, 'btn_nuevo_servicio')
        
        # Verificar listas inicializadas
        assert isinstance(widget.servicios_activos, list)
        assert isinstance(widget.servicios_programados, list)
    
    def test_control_panel_creation(self):
        """Test creación del panel de control."""
        widget = ServiciosWidget(self.mock_parent)
        
        # Verificar botones principales
        assert hasattr(widget, 'btn_nuevo_servicio')
        assert hasattr(widget, 'btn_programar') 
        assert hasattr(widget, 'btn_mantenimiento')
        assert hasattr(widget, 'btn_reportes')
        
        # Verificar campos de filtro
        assert hasattr(widget, 'search_input')
        assert hasattr(widget, 'combo_estado')
        assert hasattr(widget, 'combo_tipo')
        
        # Verificar opciones de filtro
        assert widget.combo_estado.count() == 5  # Todos, Activos, etc.
        assert widget.combo_tipo.count() == 5    # Todos, Entrega, etc.
    
    def test_tablas_configuration(self):
        """Test configuración de tablas."""
        widget = ServiciosWidget(self.mock_parent)
        
        # Verificar configuración de tabla activos
        assert widget.tabla_activos.columnCount() == 9
        assert widget.tabla_activos.alternatingRowColors() is True
        
        # Verificar configuración de tabla programados
        assert widget.tabla_programados.columnCount() == 9
        assert widget.tabla_programados.alternatingRowColors() is True
        
        # Verificar headers
        headers_expected = [
            "ID", "Tipo", "Estado", "Cliente", "Origen",
            "Destino", "Programado", "Conductor", "Observaciones"
        ]
        
        for col in range(widget.tabla_activos.columnCount()):
            header_text = widget.tabla_activos.horizontalHeaderItem(col).text()
            assert header_text == headers_expected[col]
    
    def test_cargar_datos_ejemplo(self):
        """Test carga de datos de ejemplo."""
        widget = ServiciosWidget(self.mock_parent)
        
        # Ejecutar carga de datos
        widget.cargar_datos_ejemplo()
        
        # Verificar que se cargaron datos
        assert len(widget.servicios_activos) > 0
        assert len(widget.servicios_programados) > 0
        
        # Verificar que las tablas tienen datos
        assert widget.tabla_activos.rowCount() > 0
        assert widget.tabla_programados.rowCount() > 0
    
    def test_cargar_servicios_en_tabla(self):
        """Test carga de servicios en tabla específica."""
        widget = ServiciosWidget(self.mock_parent)
        
        # Cargar servicios en tabla activos
        widget.cargar_servicios_en_tabla(widget.tabla_activos, self.servicios_ejemplo)
        
        # Verificar datos cargados
        assert widget.tabla_activos.rowCount() == len(self.servicios_ejemplo)
        
        # Verificar contenido de primera fila
        first_id = widget.tabla_activos.item(0, 0).text()
        first_tipo = widget.tabla_activos.item(0, 1).text()
        
        assert first_id == "1"
        assert first_tipo == "Entrega"
    
    def test_selection_changed_activos(self):
        """Test cambio de selección en tabla de activos."""
        widget = ServiciosWidget(self.mock_parent)
        widget.cargar_servicios_en_tabla(widget.tabla_activos, self.servicios_ejemplo)
        
        # Verificar estado inicial de botones
        assert widget.btn_completar.isEnabled() is False
        assert widget.btn_pausar.isEnabled() is False
        assert widget.btn_cancelar.isEnabled() is False
        
        # Simular selección
        widget.tabla_activos.selectRow(0)
        widget.tabla_activos.itemSelectionChanged.emit()
        
        # Los botones deberían habilitarse
        # (En implementación real verificaríamos que se llama on_service_selection_changed)
    
    def test_selection_changed_programados(self):
        """Test cambio de selección en tabla de programados."""
        widget = ServiciosWidget(self.mock_parent)
        widget.cargar_servicios_en_tabla(widget.tabla_programados, self.servicios_ejemplo)
        
        # Verificar estado inicial de botones
        assert widget.btn_iniciar.isEnabled() is False
        assert widget.btn_editar_programacion.isEnabled() is False
        assert widget.btn_eliminar_programacion.isEnabled() is False
        
        # Simular selección
        widget.tabla_programados.selectRow(0)
        widget.tabla_programados.itemSelectionChanged.emit()
        
        # Los botones deberían habilitarse tras selección
    
    @patch('rexus.modules.logistica.components.servicios_widget.DialogoNuevoServicio')
    @patch('rexus.modules.logistica.components.servicios_widget.QMessageBox')
    def test_crear_nuevo_servicio_aceptado(self, mock_msgbox, mock_dialogo_class):
        """Test creación de servicio aceptado."""
        widget = ServiciosWidget(self.mock_parent)
        
        # Mock del diálogo
        mock_dialogo = Mock()
        mock_dialogo.exec.return_value = QDialog.DialogCode.Accepted
        mock_dialogo.get_service_data.return_value = {
            'tipo': 'Entrega', 'cliente': 'Test Cliente'
        }
        mock_dialogo_class.return_value = mock_dialogo
        
        # Mock de la señal
        with patch.object(widget.service_created, 'emit') as mock_signal:
            with patch.object(widget, 'refresh_data') as mock_refresh:
                widget.crear_nuevo_servicio()
                
                # Verificar que se emitió señal
                mock_signal.assert_called_once()
                
                # Verificar mensaje de éxito
                mock_msgbox.information.assert_called_once()
                
                # Verificar refresh
                mock_refresh.assert_called_once()
    
    @patch('rexus.modules.logistica.components.servicios_widget.DialogoNuevoServicio')
    def test_crear_nuevo_servicio_cancelado(self, mock_dialogo_class):
        """Test creación de servicio cancelado."""
        widget = ServiciosWidget(self.mock_parent)
        
        # Mock del diálogo cancelado
        mock_dialogo = Mock()
        mock_dialogo.exec.return_value = QDialog.DialogCode.Rejected
        mock_dialogo_class.return_value = mock_dialogo
        
        # Mock de la señal
        with patch.object(widget.service_created, 'emit') as mock_signal:
            widget.crear_nuevo_servicio()
            
            # Verificar que NO se emitió señal
            mock_signal.assert_not_called()
    
    @patch('rexus.modules.logistica.components.servicios_widget.QMessageBox')
    def test_completar_servicio_sin_seleccion(self, mock_msgbox):
        """Test completar servicio sin selección."""
        widget = ServiciosWidget(self.mock_parent)
        
        # Mock tabla sin selección
        widget.tabla_activos.currentRow = Mock(return_value=-1)
        
        # Ejecutar completar servicio
        widget.completar_servicio()
        
        # No debería hacer nada (sin error, pero sin acción)
        # En implementación real podría mostrar mensaje
    
    @patch('rexus.modules.logistica.components.servicios_widget.QMessageBox')
    def test_completar_servicio_con_seleccion(self, mock_msgbox):
        """Test completar servicio con selección."""
        widget = ServiciosWidget(self.mock_parent)
        widget.cargar_servicios_en_tabla(widget.tabla_activos, self.servicios_ejemplo)
        
        # Mock selección
        widget.tabla_activos.currentRow = Mock(return_value=0)
        
        # Mock item con datos
        mock_item = Mock()
        mock_item.data.return_value = self.servicios_ejemplo[0]
        widget.tabla_activos.item = Mock(return_value=mock_item)
        
        with patch.object(widget.service_completed, 'emit') as mock_signal:
            with patch.object(widget, 'refresh_data') as mock_refresh:
                widget.completar_servicio()
                
                # Verificar señal emitida
                mock_signal.assert_called_once_with(1)  # ID del servicio
                
                # Verificar mensaje y refresh
                mock_msgbox.information.assert_called_once()
                mock_refresh.assert_called_once()
    
    @patch('rexus.modules.logistica.components.servicios_widget.QMessageBox')
    def test_generar_reporte_servicios_sin_datos(self, mock_msgbox):
        """Test generar reporte sin datos."""
        widget = ServiciosWidget(self.mock_parent)
        widget.servicios_activos = []
        widget.servicios_programados = []
        
        widget.generar_reporte_servicios()
        
        # Verificar warning
        mock_msgbox.warning.assert_called_once_with(
            widget, "Reporte", "No hay servicios para exportar"
        )
    
    @patch('rexus.modules.logistica.components.servicios_widget.QMessageBox')
    def test_generar_reporte_servicios_exitoso(self, mock_msgbox):
        """Test generar reporte exitoso."""
        widget = ServiciosWidget(self.mock_parent)
        widget.servicios_activos = self.servicios_ejemplo
        widget.servicios_programados = []
        
        with patch.object(widget, 'export_to_excel', return_value=True):
            widget.generar_reporte_servicios()
            
            # Verificar mensaje de éxito
            mock_msgbox.information.assert_called_once_with(
                widget, "Éxito", "Reporte generado exitosamente"
            )
    
    @patch('rexus.modules.logistica.components.servicios_widget.QMessageBox')
    def test_generar_reporte_servicios_error(self, mock_msgbox):
        """Test error en generación de reporte."""
        widget = ServiciosWidget(self.mock_parent)
        widget.servicios_activos = self.servicios_ejemplo
        widget.servicios_programados = []
        
        with patch.object(widget, 'export_to_excel', side_effect=Exception("Error test")):
            widget.generar_reporte_servicios()
            
            # Verificar mensaje de error
            mock_msgbox.critical.assert_called_once()
    
    @patch('rexus.modules.logistica.components.servicios_widget.QMessageBox')
    def test_pausar_servicio(self, mock_msgbox):
        """Test pausar servicio."""
        widget = ServiciosWidget(self.mock_parent)
        
        widget.pausar_servicio()
        
        # Verificar mensaje informativo
        mock_msgbox.information.assert_called_once_with(widget, "Pausa", "Servicio pausado")
    
    @patch('rexus.modules.logistica.components.servicios_widget.QMessageBox')
    def test_cancelar_servicio_confirmado(self, mock_msgbox):
        """Test cancelar servicio confirmado."""
        widget = ServiciosWidget(self.mock_parent)
        
        # Mock confirmación
        mock_msgbox.question.return_value = mock_msgbox.StandardButton.Yes
        
        widget.cancelar_servicio()
        
        # Verificar mensajes
        mock_msgbox.question.assert_called_once()
        mock_msgbox.information.assert_called_once_with(widget, "Cancelado", "Servicio cancelado")
    
    @patch('rexus.modules.logistica.components.servicios_widget.QMessageBox')
    def test_cancelar_servicio_rechazado(self, mock_msgbox):
        """Test cancelar servicio rechazado."""
        widget = ServiciosWidget(self.mock_parent)
        
        # Mock rechazo
        mock_msgbox.question.return_value = mock_msgbox.StandardButton.No
        
        widget.cancelar_servicio()
        
        # Verificar solo pregunta, sin acción
        mock_msgbox.question.assert_called_once()
        # No debería llamar información de cancelación
        assert mock_msgbox.information.call_count == 0
    
    def test_hex_to_rgb(self):
        """Test conversión hexadecimal a RGB."""
        # Test método estático
        result = ServiciosWidget.hex_to_rgb("#FF0000")
        assert result == (255, 0, 0)
        
        result = ServiciosWidget.hex_to_rgb("#00FF00")
        assert result == (0, 255, 0)
        
        result = ServiciosWidget.hex_to_rgb("#0000FF")
        assert result == (0, 0, 255)
        
        # Test sin #
        result = ServiciosWidget.hex_to_rgb("FFFFFF")
        assert result == (255, 255, 255)


class TestDialogoNuevoServicio:
    """Tests para diálogo de nuevo servicio."""
    
    @classmethod
    def setup_class(cls):
        """Configuración inicial."""
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
    
    def test_dialogo_initialization(self):
        """Test inicialización del diálogo."""
        dialogo = DialogoNuevoServicio()
        
        assert dialogo is not None
        assert dialogo.isModal() is True
        assert dialogo.windowTitle() == "Nuevo Servicio"
        
        # Verificar campos
        assert hasattr(dialogo, 'combo_tipo')
        assert hasattr(dialogo, 'input_cliente')
        assert hasattr(dialogo, 'input_origen')
        assert hasattr(dialogo, 'input_destino')
        assert hasattr(dialogo, 'date_programado')
        assert hasattr(dialogo, 'combo_conductor')
        assert hasattr(dialogo, 'text_observaciones')
    
    def test_get_service_data(self):
        """Test obtención de datos del servicio."""
        dialogo = DialogoNuevoServicio()
        
        # Configurar datos de prueba
        dialogo.combo_tipo.setCurrentText("Entrega")
        dialogo.input_cliente.setText("Cliente Test")
        dialogo.input_origen.setText("Origen Test")
        dialogo.input_destino.setText("Destino Test")
        dialogo.combo_conductor.setCurrentText("Juan Pérez")
        dialogo.text_observaciones.setPlainText("Observaciones test")
        
        # Obtener datos
        data = dialogo.get_service_data()
        
        # Verificar datos
        assert data['tipo'] == "Entrega"
        assert data['cliente'] == "Cliente Test"
        assert data['origen'] == "Origen Test"
        assert data['destino'] == "Destino Test"
        assert data['conductor'] == "Juan Pérez"
        assert data['observaciones'] == "Observaciones test"
        assert 'fecha' in data


class TestDialogoProgramarServicio:
    """Tests para diálogo de programar servicio."""
    
    @classmethod
    def setup_class(cls):
        """Configuración inicial."""
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
    
    def test_dialogo_initialization(self):
        """Test inicialización del diálogo."""
        dialogo = DialogoProgramarServicio()
        
        assert dialogo is not None
        assert dialogo.isModal() is True
        assert dialogo.windowTitle() == "Programar Servicio"
        
        # Verificar botón de cerrar
        assert hasattr(dialogo, 'btn_cerrar')
    
    def test_get_programacion_data(self):
        """Test obtención de datos de programación."""
        dialogo = DialogoProgramarServicio()
        
        data = dialogo.get_programacion_data()
        
        # Por ahora retorna diccionario vacío
        assert isinstance(data, dict)
        assert len(data) == 0


class TestServiciosWidgetIntegration:
    """Tests de integración para ServiciosWidget."""
    
    @classmethod
    def setup_class(cls):
        """Configuración inicial."""
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
    
    def test_widget_complete_workflow(self):
        """Test workflow completo del widget."""
        mock_parent = Mock()
        widget = ServiciosWidget(mock_parent)
        
        # Cargar datos
        widget.refresh_data()
        
        # Verificar datos cargados
        assert len(widget.servicios_activos) > 0
        assert len(widget.servicios_programados) > 0
        
        # Verificar tablas pobladas
        assert widget.tabla_activos.rowCount() > 0
        assert widget.tabla_programados.rowCount() > 0
    
    def test_error_handling(self):
        """Test manejo de errores."""
        mock_parent = Mock()
        widget = ServiciosWidget(mock_parent)
        
        # Mock error en refresh_data
        with patch.object(widget, 'cargar_datos_ejemplo', side_effect=Exception("Error test")):
            with patch.object(widget.error_occurred, 'emit') as mock_error:
                widget.refresh_data()
                
                # Verificar que se emitió error
                mock_error.assert_called_once()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])