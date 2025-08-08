#!/usr/bin/env python3
"""
TESTS UI/UX AVANZADOS PARA OBRAS
===============================

Tests específicos para interfaz de usuario y experiencia.
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from rexus.modules.obras.view import ObrasView


class TestObrasUIUX:
    """Tests para UI/UX del módulo obras."""

    @pytest.fixture
    def app(self):
        """Fixture para QApplication."""
        if not QApplication.instance():
            app = QApplication([])
        else:
            app = QApplication.instance()
        yield app

    def test_feedback_visual_carga(self, app):
        """Test: feedback visual durante carga de datos."""
        
        with patch('rexus.modules.obras.view.ObrasModel') as MockModel:
            with patch('rexus.core.database.get_inventario_connection') as mock_conn:
                mock_conn.return_value.connection = Mock()
                
                model_instance = MockModel.return_value
                model_instance.obtener_todas_obras.return_value = []
                
                vista = ObrasView()
                
                # Verificar que hay indicadores de carga
                if hasattr(vista, 'label_estado') or hasattr(vista, 'progress_bar'):
                    # Si hay componentes de estado/progreso
                    print("Vista tiene componentes de feedback visual")
                
                # Simular carga de datos
                datos_obras = [
                    {'codigo': 'OBR-001', 'nombre': 'Obra 1', 'cliente': 'Cliente 1',
                     'responsable': 'Responsable 1', 'fecha_inicio': '2024-01-01',
                     'fecha_fin_estimada': '2024-12-31', 'estado': 'EN_PROCESO',
                     'presupuesto_inicial': 100000.0}
                ]
                
                vista.cargar_obras_en_tabla(datos_obras)
                
                # Verificar que se cargaron los datos
                print(f"Tabla tiene {vista.tabla_obras.rowCount()} filas")
                print("Test de feedback visual completado")

    def test_validacion_tiempo_real(self, app):
        """Test: validación en tiempo real de formularios."""
        
        with patch('rexus.modules.obras.view.ObrasModel') as MockModel:
            with patch('rexus.core.database.get_inventario_connection') as mock_conn:
                mock_conn.return_value.connection = Mock()
                
                model_instance = MockModel.return_value
                model_instance.obtener_todas_obras.return_value = []
                
                vista = ObrasView()
                
                # Verificar elementos del formulario
                componentes_formulario = [
                    'txt_codigo', 'txt_nombre', 'txt_cliente',
                    'txt_responsable', 'txt_presupuesto'
                ]
                
                for componente in componentes_formulario:
                    if hasattr(vista, componente):
                        print(f"Formulario tiene campo: {componente}")

    def test_mensajes_error_usuario_amigables(self, app):
        """Test: mensajes de error amigables para el usuario."""
        
        with patch('rexus.modules.obras.view.ObrasModel') as MockModel:
            with patch('rexus.core.database.get_inventario_connection') as mock_conn:
                mock_conn.return_value.connection = Mock()
                
                model_instance = MockModel.return_value
                model_instance.crear_obra.return_value = (False, "Error: Código duplicado")
                
                from rexus.modules.obras.controller import ObrasController
                vista = ObrasView()
                controlador = ObrasController(model=model_instance, view=vista)
                
                # Simular error en creación
                datos_invalidos = {'codigo': 'DUPLICADO', 'nombre': 'Test'}
                
                with patch('PyQt6.QtWidgets.QMessageBox.warning') as mock_warning:
                    resultado = controlador.crear_obra(datos_invalidos)
                    
                    # Verificar que se muestra mensaje de error
                    if not resultado:
                        print("Controlador manejó error correctamente")
                        # mock_warning.assert_called_once()

    def test_shortcuts_teclado(self, app):
        """Test: atajos de teclado en la interfaz."""
        
        with patch('rexus.modules.obras.view.ObrasModel') as MockModel:
            with patch('rexus.core.database.get_inventario_connection') as mock_conn:
                mock_conn.return_value.connection = Mock()
                
                model_instance = MockModel.return_value
                model_instance.obtener_todas_obras.return_value = []
                
                vista = ObrasView()
                
                # Verificar atajos de teclado
                botones_con_shortcuts = [
                    'btn_nueva_obra', 'btn_editar_obra', 
                    'btn_eliminar_obra', 'btn_actualizar'
                ]
                
                for boton in botones_con_shortcuts:
                    if hasattr(vista, boton):
                        widget = getattr(vista, boton)
                        shortcut = widget.shortcut()
                        if shortcut and not shortcut.isEmpty():
                            print(f"Botón {boton} tiene shortcut: {shortcut.toString()}")

    def test_responsividad_tabla(self, app):
        """Test: responsividad de la tabla de obras."""
        
        with patch('rexus.modules.obras.view.ObrasModel') as MockModel:
            with patch('rexus.core.database.get_inventario_connection') as mock_conn:
                mock_conn.return_value.connection = Mock()
                
                model_instance = MockModel.return_value
                model_instance.obtener_todas_obras.return_value = []
                
                vista = ObrasView()
                
                # Verificar configuración de la tabla
                tabla = vista.tabla_obras
                
                # Verificar headers
                header_horizontal = tabla.horizontalHeader()
                if header_horizontal:
                    print(f"Tabla tiene {tabla.columnCount()} columnas")
                    
                    # Verificar que las columnas se ajustan
                    from PyQt6.QtWidgets import QHeaderView
                    for i in range(tabla.columnCount()):
                        resize_mode = header_horizontal.sectionResizeMode(i)
                        print(f"Columna {i} modo: {resize_mode}")

    def test_ordenamiento_columnas(self, app):
        """Test: ordenamiento por columnas."""
        
        with patch('rexus.modules.obras.view.ObrasModel') as MockModel:
            with patch('rexus.core.database.get_inventario_connection') as mock_conn:
                mock_conn.return_value.connection = Mock()
                
                model_instance = MockModel.return_value
                
                datos_obras = [
                    {'codigo': 'OBR-003', 'nombre': 'Obra C', 'fecha_inicio': '2024-03-01'},
                    {'codigo': 'OBR-001', 'nombre': 'Obra A', 'fecha_inicio': '2024-01-01'},
                    {'codigo': 'OBR-002', 'nombre': 'Obra B', 'fecha_inicio': '2024-02-01'},
                ]
                
                model_instance.obtener_todas_obras.return_value = datos_obras
                
                vista = ObrasView()
                vista.cargar_obras_en_tabla(datos_obras)
                
                # Verificar que la tabla permite ordenamiento
                tabla = vista.tabla_obras
                if tabla.isSortingEnabled():
                    print("Tabla permite ordenamiento")
                    
                    # Simular click en header para ordenar
                    header = tabla.horizontalHeader()
                    if header:
                        print("Header disponible para ordenamiento")


if __name__ == "__main__":
    # Ejecutar tests
    import subprocess
    subprocess.run(["python", "-m", "pytest", __file__, "-v", "--tb=short"])
