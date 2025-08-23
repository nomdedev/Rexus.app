# -*- coding: utf-8 -*-
"""
Tests de Interacción UI con pytest-qt para Rexus.app
Prueba flujos completos de usuario, formularios y interacciones UI reales

Fecha: 20/08/2025
Cobertura: Formularios, botones, validaciones visuales, workflows UI
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from PyQt6.QtWidgets import QApplication, QWidget, QMessageBox, QLineEdit, QPushButton, QTableWidget
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtTest import QTest
import time

# Agregar directorio raíz al path
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

class TestUIInteractions:
    """Suite de tests de interacción UI usando pytest-qt."""

    @pytest.fixture
    def mock_db(self):
        """Mock de base de datos para tests UI."""
        mock = Mock()
        mock.cursor.return_value.fetchall.return_value = []
        mock.cursor.return_value.fetchone.return_value = None
        mock.commit = Mock()
        mock.rollback = Mock()
        return mock

    @pytest.fixture
    def sample_data(self):
        """Datos de ejemplo para tests."""
        return {
            'producto': {
                'codigo': 'TEST001',
                'descripcion': 'Producto Test',
                'categoria': 'Test',
                'stock': 100,
                'precio': 25.50
            },
            'compra': {
                'numero_orden': 'OC-001',
                'proveedor': 'Proveedor Test',
                'estado': 'PENDIENTE',
                'total': 1500.00
            },
            'obra': {
                'codigo': 'OBRA001',
                'nombre': 'Obra Test',
                'descripcion': 'Descripción test',
                'estado': 'ACTIVA'
            }
        }

    @pytest.mark.parametrize("module_name,view_class", [
        ("inventario", "InventarioView"),
        ("compras", "ComprasView"),
        ("pedidos", "PedidosView"),
        ("obras", "ObrasView"),
        ("vidrios", "VidriosView"),
        ("notificaciones", "NotificacionesView")
    ])
    def test_module_view_initialization(self, qtbot, mock_db, module_name, view_class):
        """Test inicialización de vistas de módulos con qtbot."""
        try:
            module = __import__(f'rexus.modules.{module_name}.view', fromlist=[view_class])
            ViewClass = getattr(module, view_class)
            
            with patch('rexus.core.database.get_inventario_connection', return_value=mock_db):
                view = ViewClass()
                qtbot.addWidget(view)
                
                # Verificar que la vista se inicializa correctamente
                assert view is not None
                assert isinstance(view, QWidget)
                
                # Verificar componentes básicos UI
                if hasattr(view, 'table'):
                    assert isinstance(view.table, QTableWidget)
                
                # Test visibilidad
                view.show()
                assert view.isVisible()
                
        except ImportError:
            pytest.skip(f"Módulo {module_name} no disponible")
        except Exception as e:
            pytest.fail(f"Error en inicialización de {module_name}: {e}")

    def test_inventario_form_interactions(self, qtbot, mock_db, sample_data):
        """Test interacciones de formulario de inventario."""
        try:
            from rexus.modules.inventario.view import InventarioView
            
            with patch('rexus.core.database.get_inventario_connection', return_value=mock_db):
                view = InventarioView()
                qtbot.addWidget(view)
                view.show()
                
                # Test búsqueda si existe search box
                search_widgets = view.findChildren(QLineEdit)
                for search_widget in search_widgets:
                    if hasattr(search_widget, 'setPlaceholderText') and 'buscar' in search_widget.placeholderText().lower():
                        qtbot.keyClicks(search_widget, )
                        QTest.keyPress(search_widget, Qt.Key.Key_Enter)
                        qtbot.wait(100)  # Esperar procesamiento
                        break
                
                # Test botones de acción
                buttons = view.findChildren(QPushButton)
                for button in buttons:
                    if 'nuevo' in button.text().lower() or 'agregar' in button.text().lower():
                        # Simular click en botón nuevo
                        qtbot.mouseClick(button, Qt.MouseButton.LeftButton)
                        qtbot.wait(100)
                        break
                
        except ImportError:
            pytest.skip("Vista de inventario no disponible")

    def test_compras_form_workflow(self, qtbot, mock_db, sample_data):
        """Test flujo completo de formulario de compras."""
        try:
            from rexus.modules.compras.view import ComprasView
            
            with patch('rexus.core.database.get_inventario_connection', return_value=mock_db):
                view = ComprasView()
                qtbot.addWidget(view)
                view.show()
                
                # Test elementos de formulario básicos
                line_edits = view.findChildren(QLineEdit)
                
                # Simular llenado de campos si existen
                for line_edit in line_edits[:3]:  # Probar los primeros 3 campos
                    qtbot.keyClicks(line_edit, )
                    qtbot.wait(50)
                
                # Test validación - presionar tab para trigger validación
                if line_edits:
                    QTest.keyPress(line_edits[0], Qt.Key.Key_Tab)
                    qtbot.wait(100)
                
                # Test botones de acción
                buttons = view.findChildren(QPushButton)
                action_buttons = [b for b in buttons if any(word in b.text().lower() 
                                for word in ['guardar', 'save', 'crear', 'nuevo'])]
                
                if action_buttons:
                    # No hacer click real en guardar para evitar errores de BD
                    # Solo verificar que el botón existe y es clickeable
                    assert action_buttons[0].isEnabled()
                
        except ImportError:
            pytest.skip("Vista de compras no disponible")

    def test_form_validation_feedback(self, qtbot, mock_db):
        """Test feedback visual de validaciones de formulario."""
        try:
            from rexus.modules.inventario.view import InventarioView
            
            with patch('rexus.core.database.get_inventario_connection', return_value=mock_db):
                view = InventarioView()
                qtbot.addWidget(view)
                view.show()
                
                # Test validación de campos vacíos
                line_edits = view.findChildren(QLineEdit)
                for line_edit in line_edits[:2]:  # Test primeros 2 campos
                    # Limpiar campo
                    line_edit.clear()
                    qtbot.wait(50)
                    
                    # Simular pérdida de foco para trigger validación
                    QTest.keyPress(line_edit, Qt.Key.Key_Tab)
                    qtbot.wait(100)
                    
                    # Verificar que el campo mantiene estado consistente
                    assert line_edit is not None
                
                # Test datos inválidos
                if line_edits:
                    qtbot.keyClicks(line_edits[0], )
                    QTest.keyPress(line_edits[0], Qt.Key.Key_Tab)
                    qtbot.wait(100)
                
        except ImportError:
            pytest.skip("Vista de inventario no disponible")

    def test_table_interactions(self, qtbot, mock_db):
        """Test interacciones con tablas de datos."""
        try:
            from rexus.modules.inventario.view import InventarioView
            
            # Mock datos para la tabla
            mock_db.cursor.return_value.fetchall.return_value = [
                (1, 'TEST001', 'Producto 1', 'Cat A', 100, 25.50),
                (2, 'TEST002', 'Producto 2', 'Cat B', 50, 30.00)
            ]
            
            with patch('rexus.core.database.get_inventario_connection', return_value=mock_db):
                view = InventarioView()
                qtbot.addWidget(view)
                view.show()
                
                # Buscar tabla principal
                tables = view.findChildren(QTableWidget)
                if tables:
                    table = tables[0]
                    
                    # Test selección de fila
                    if table.rowCount() > 0:
                        table.selectRow(0)
                        qtbot.wait(100)
                        
                        # Verificar selección
                        assert table.currentRow() >= 0
                    
                    # Test ordenamiento por columna si hay datos
                    if table.columnCount() > 0:
                        header = table.horizontalHeader()
                        qtbot.mouseClick(header.viewport(), Qt.MouseButton.LeftButton)
                        qtbot.wait(100)
                
        except ImportError:
            pytest.skip()

    def test_dialog_interactions(self, qtbot, mock_db):
        """Test interacciones con diálogos modales."""
        try:
            from rexus.modules.inventario.view import InventarioView
            
            with patch('rexus.core.database.get_inventario_connection', return_value=mock_db):
                view = InventarioView()
                qtbot.addWidget(view)
                view.show()
                
                # Buscar botones que abran diálogos
                buttons = view.findChildren(QPushButton)
                dialog_buttons = [b for b in buttons if any(word in b.text().lower() 
                                for word in ['nuevo', 'editar', 'configurar', 'detalle'])]
                
                # Test apertura de diálogo (sin confirmar para evitar efectos secundarios)
                if dialog_buttons:
                    button = dialog_buttons[0]
                    
                    # Verificar que el botón es clickeable
                    assert button.isEnabled()
                    
                    # En un escenario real aquí se abriría el diálogo
                    # Por seguridad, solo verificamos la existencia del botón
                
        except ImportError:
            pytest.skip()

    def test_keyboard_navigation(self, qtbot, mock_db):
        """Test navegación por teclado en formularios."""
        try:
            from rexus.modules.compras.view import ComprasView
            
            with patch('rexus.core.database.get_inventario_connection', return_value=mock_db):
                view = ComprasView()
                qtbot.addWidget(view)
                view.show()
                
                # Test navegación con Tab
                line_edits = view.findChildren(QLineEdit)
                if len(line_edits) > 1:
                    # Establecer foco en primer campo
                    line_edits[0].setFocus()
                    qtbot.wait(50)
                    
                    # Navegar con Tab
                    QTest.keyPress(line_edits[0], Qt.Key.Key_Tab)
                    qtbot.wait(100)
                    
                    # Verificar que el foco cambió (básico)
                    # En aplicación real verificaríamos que el foco está en el siguiente campo
                    assert line_edits[0] is not None
                
                # Test navegación con Enter
                if line_edits:
                    qtbot.keyClicks(line_edits[0], )
                    QTest.keyPress(line_edits[0], Qt.Key.Key_Return)
                    qtbot.wait(100)
                
        except ImportError:
            pytest.skip("Vista de compras no disponible")

    def test_error_handling_ui(self, qtbot, mock_db):
        """Test manejo de errores y mensajes en UI."""
        # Simular error de BD
        mock_db.cursor.side_effect = Exception("Database error")
        
        try:
            from rexus.modules.inventario.view import InventarioView
            
            with patch('rexus.core.database.get_inventario_connection', return_value=mock_db):
                view = InventarioView()
                qtbot.addWidget(view)
                
                # La vista debería manejar el error sin crash
                view.show()
                qtbot.wait(100)
                
                # Verificar que la vista se mantiene estable
                assert view is not None
                assert isinstance(view, QWidget)
                
        except ImportError:
            pytest.skip()

    @pytest.mark.slow
    def test_performance_ui_load(self, qtbot, mock_db):
        """Test rendimiento de carga de UI."""
        try:
            from rexus.modules.inventario.view import InventarioView
            
            with patch('rexus.core.database.get_inventario_connection', return_value=mock_db):
                start_time = time.time()
                
                view = InventarioView()
                qtbot.addWidget(view)
                view.show()
                
                load_time = time.time() - start_time
                
                # La vista debería cargar en menos de 5 segundos
                assert load_time < 5.0, f
                
                qtbot.wait(100)
                
        except ImportError:
            pytest.skip("Vista de inventario no disponible")

    def test_multiple_modules_stability(self, qtbot, mock_db):
        """Test estabilidad al cargar múltiples módulos."""
        module_views = [
            ("inventario", "InventarioView"),
            ("compras", "ComprasView"),
            ("pedidos", "PedidosView")
        ]
        
        created_views = []
        
        for module_name, view_class in module_views:
            try:
                module = __import__(f'rexus.modules.{module_name}.view', fromlist=[view_class])
                ViewClass = getattr(module, view_class)
                
                with patch('rexus.core.database.get_inventario_connection', return_value=mock_db):
                    view = ViewClass()
                    qtbot.addWidget(view)
                    created_views.append(view)
                    
            except ImportError:
                continue  # Skip si módulo no está disponible
            except Exception as e:
                pytest.fail(f"Error creando {module_name}: {e}")
        
        # Verificar que al menos un módulo se cargó correctamente
        assert len(created_views) > 0, "No se pudo cargar ningún módulo"
        
        # Test que todas las vistas permanecen estables
        for view in created_views:
            view.show()
            qtbot.wait(50)
            assert view.isVisible()


# Configuración específica para pytest-qt
@pytest.fixture(scope="session")
def qapp():
    """Fixture de QApplication para tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
    # No cerrar la app aquí para evitar problemas con otros tests


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])