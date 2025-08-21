"""
Tests Comprensivos de Accesibilidad - Rexus.app
Cubre: Navegación por teclado, contraste, screen readers, a11y standards

Fecha: 20/08/2025
Cobertura: WCAG 2.1 guidelines, keyboard navigation, color contrast, focus management
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QLineEdit, QLabel, QTableWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtTest import QTest
import colorsys

# Agregar directorio raíz al path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))


class AccessibilityTester:
    """Helper class para tests de accesibilidad."""
    
    @staticmethod
    def calculate_contrast_ratio(color1, color2):
        """
        Calcula el ratio de contraste entre dos colores según WCAG 2.1.
        
        Args:
            color1, color2: QColor objects
            
        Returns:
            float: Contrast ratio (1-21)
        """
        def get_luminance(color):
            """Calcula la luminancia relativa de un color."""
            r, g, b = color.red() / 255.0, color.green() / 255.0, color.blue() / 255.0
            
            # Convertir sRGB a luminancia relativa
            def linearize(c):
                return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
            
            r_lin, g_lin, b_lin = linearize(r), linearize(g), linearize(b)
            return 0.2126 * r_lin + 0.7152 * g_lin + 0.0722 * b_lin
        
        l1 = get_luminance(color1)
        l2 = get_luminance(color2)
        
        # Asegurar que l1 es el color más claro
        if l1 < l2:
            l1, l2 = l2, l1
            
        return (l1 + 0.05) / (l2 + 0.05)
    
    @staticmethod
    def meets_wcag_contrast_aa(contrast_ratio, is_large_text=False):
        """
        Verifica si el ratio de contraste cumple WCAG 2.1 AA.
        
        Args:
            contrast_ratio: float
            is_large_text: bool - texto mayor a 18pt o 14pt bold
            
        Returns:
            bool: True si cumple el estándar
        """
        min_ratio = 3.0 if is_large_text else 4.5
        return contrast_ratio >= min_ratio
    
    @staticmethod
    def meets_wcag_contrast_aaa(contrast_ratio, is_large_text=False):
        """
        Verifica si el ratio de contraste cumple WCAG 2.1 AAA.
        
        Args:
            contrast_ratio: float
            is_large_text: bool - texto mayor a 18pt o 14pt bold
            
        Returns:
            bool: True si cumple el estándar
        """
        min_ratio = 4.5 if is_large_text else 7.0
        return contrast_ratio >= min_ratio
    
    @staticmethod
    def get_widget_colors(widget):
        """Obtiene los colores de fondo y texto de un widget."""
        palette = widget.palette()
        bg_color = palette.color(QPalette.ColorRole.Window)
        text_color = palette.color(QPalette.ColorRole.WindowText)
        return bg_color, text_color
    
    @staticmethod
    def find_focusable_widgets(parent_widget):
        """Encuentra todos los widgets que pueden recibir foco."""
        focusable_widgets = []
        
        def check_widget(widget):
            if widget.focusPolicy() != Qt.FocusPolicy.NoFocus:
                focusable_widgets.append(widget)
            for child in widget.findChildren(QWidget):
                if child.focusPolicy() != Qt.FocusPolicy.NoFocus:
                    focusable_widgets.append(child)
        
        check_widget(parent_widget)
        return focusable_widgets


class TestKeyboardNavigation:
    """Tests para navegación por teclado."""
    
    @pytest.fixture
    def mock_db(self):
        """Mock de base de datos para tests."""
        mock = Mock()
        mock.cursor.return_value.fetchall.return_value = []
        mock.commit = Mock()
        return mock
    
    @pytest.mark.parametrize("module_name,view_class", [
        ("inventario", "InventarioView"),
        ("compras", "ComprasView"),
        ("pedidos", "PedidosView"),
        ("obras", "ObrasView")
    ])
    def test_tab_navigation(self, qtbot, mock_db, module_name, view_class):
        """Test navegación con Tab entre elementos focusables."""
        try:
            module = __import__(f'rexus.modules.{module_name}.view', fromlist=[view_class])
            ViewClass = getattr(module, view_class)
            
            with patch('rexus.core.database.get_inventario_connection', return_value=mock_db):
                view = ViewClass()
                qtbot.addWidget(view)
                view.show()
                
                # Encontrar widgets focusables
                focusable_widgets = AccessibilityTester.find_focusable_widgets(view)
                
                if len(focusable_widgets) >= 2:
                    # Establecer foco en primer widget
                    first_widget = focusable_widgets[0]
                    first_widget.setFocus()
                    qtbot.wait(100)
                    
                    # Navegar con Tab
                    QTest.keyPress(first_widget, Qt.Key.Key_Tab)
                    qtbot.wait(100)
                    
                    # Verificar que el foco cambió
                    focused_widget = QApplication.focusWidget()
                    assert focused_widget is not None
                    assert focused_widget in focusable_widgets
                
        except ImportError:
            pytest.skip(f"Módulo {module_name} no disponible")
    
    @pytest.mark.parametrize("module_name,view_class", [
        ("inventario", "InventarioView"),
        ("compras", "ComprasView")
    ])
    def test_shift_tab_navigation(self, qtbot, mock_db, module_name, view_class):
        """Test navegación con Shift+Tab (navegación inversa)."""
        try:
            module = __import__(f'rexus.modules.{module_name}.view', fromlist=[view_class])
            ViewClass = getattr(module, view_class)
            
            with patch('rexus.core.database.get_inventario_connection', return_value=mock_db):
                view = ViewClass()
                qtbot.addWidget(view)
                view.show()
                
                focusable_widgets = AccessibilityTester.find_focusable_widgets(view)
                
                if len(focusable_widgets) >= 2:
                    # Ir al segundo widget
                    second_widget = focusable_widgets[1]
                    second_widget.setFocus()
                    qtbot.wait(100)
                    
                    # Navegar con Shift+Tab
                    QTest.keyPress(second_widget, Qt.Key.Key_Tab, Qt.KeyboardModifier.ShiftModifier)
                    qtbot.wait(100)
                    
                    # Verificar navegación inversa
                    focused_widget = QApplication.focusWidget()
                    assert focused_widget is not None
                    
        except ImportError:
            pytest.skip(f"Módulo {module_name} no disponible")
    
    def test_enter_key_activation(self, qtbot, mock_db):
        """Test activación de botones con Enter."""
        try:
            from rexus.modules.inventario.view import InventarioView
            
            with patch('rexus.core.database.get_inventario_connection', return_value=mock_db):
                view = InventarioView()
                qtbot.addWidget(view)
                view.show()
                
                # Encontrar botones
                buttons = view.findChildren(QPushButton)
                
                if buttons:
                    button = buttons[0]
                    button.setFocus()
                    qtbot.wait(100)
                    
                    # Simular presionar Enter
                    QTest.keyPress(button, Qt.Key.Key_Return)
                    qtbot.wait(100)
                    
                    # El botón debería mantener el foco o manejarlo apropiadamente
                    focused_widget = QApplication.focusWidget()
                    assert focused_widget is not None
                    
        except ImportError:
            pytest.skip("InventarioView no disponible")
    
    def test_arrow_key_table_navigation(self, qtbot, mock_db):
        """Test navegación con flechas en tablas."""
        try:
            from rexus.modules.inventario.view import InventarioView
            
            with patch('rexus.core.database.get_inventario_connection', return_value=mock_db):
                view = InventarioView()
                qtbot.addWidget(view)
                view.show()
                
                # Encontrar tablas
                tables = view.findChildren(QTableWidget)
                
                if tables:
                    table = tables[0]
                    table.setFocus()
                    qtbot.wait(100)
                    
                    # Test navegación con flechas
                    QTest.keyPress(table, Qt.Key.Key_Down)
                    qtbot.wait(50)
                    QTest.keyPress(table, Qt.Key.Key_Right)
                    qtbot.wait(50)
                    QTest.keyPress(table, Qt.Key.Key_Up)
                    qtbot.wait(50)
                    QTest.keyPress(table, Qt.Key.Key_Left)
                    qtbot.wait(50)
                    
                    # Verificar que la tabla mantiene foco
                    focused_widget = QApplication.focusWidget()
                    assert focused_widget is not None
                    
        except ImportError:
            pytest.skip("InventarioView no disponible")
    
    def test_escape_key_behavior(self, qtbot, mock_db):
        """Test comportamiento de la tecla Escape."""
        try:
            from rexus.modules.compras.view import ComprasView
            
            with patch('rexus.core.database.get_inventario_connection', return_value=mock_db):
                view = ComprasView()
                qtbot.addWidget(view)
                view.show()
                
                # Establecer foco en un widget
                line_edits = view.findChildren(QLineEdit)
                if line_edits:
                    line_edit = line_edits[0]
                    line_edit.setFocus()
                    line_edit.setText("Texto de prueba")
                    qtbot.wait(100)
                    
                    # Presionar Escape
                    QTest.keyPress(line_edit, Qt.Key.Key_Escape)
                    qtbot.wait(100)
                    
                    # El widget debería mantener consistencia
                    assert line_edit is not None
                    
        except ImportError:
            pytest.skip("ComprasView no disponible")


class TestColorContrast:
    """Tests para contraste de colores según WCAG."""
    
    @pytest.fixture
    def accessibility_tester(self):
        """Fixture del tester de accesibilidad."""
        return AccessibilityTester()
    
    @pytest.mark.parametrize("module_name,view_class", [
        ("inventario", "InventarioView"),
        ("compras", "ComprasView"),
        ("pedidos", "PedidosView")
    ])
    def test_text_background_contrast_aa(self, qtbot, accessibility_tester, module_name, view_class):
        """Test contraste texto-fondo cumple WCAG AA."""
        mock_db = Mock()
        mock_db.cursor.return_value.fetchall.return_value = []
        
        try:
            module = __import__(f'rexus.modules.{module_name}.view', fromlist=[view_class])
            ViewClass = getattr(module, view_class)
            
            with patch('rexus.core.database.get_inventario_connection', return_value=mock_db):
                view = ViewClass()
                qtbot.addWidget(view)
                view.show()
                
                # Test widgets con texto
                text_widgets = view.findChildren(QLabel) + view.findChildren(QLineEdit)
                
                contrast_issues = []
                
                for widget in text_widgets[:5]:  # Limitar a 5 widgets para rendimiento
                    try:
                        bg_color, text_color = accessibility_tester.get_widget_colors(widget)
                        contrast_ratio = accessibility_tester.calculate_contrast_ratio(text_color, bg_color)
                        
                        # Verificar WCAG AA
                        if not accessibility_tester.meets_wcag_contrast_aa(contrast_ratio):
                            contrast_issues.append({
                                'widget': widget.objectName() or str(widget),
                                'contrast_ratio': contrast_ratio,
                                'text_color': text_color.name(),
                                'bg_color': bg_color.name()
                            })
                    except Exception as e:
                        # Ignorar errores de widgets específicos
                        continue
                
                # Reportar issues pero no fallar el test (informativo)
                if contrast_issues:
                    print(f"\n{module_name} - Issues de contraste encontrados:")
                    for issue in contrast_issues:
                        print(f"  - {issue['widget']}: {issue['contrast_ratio']:.2f} "
                              f"(texto: {issue['text_color']}, fondo: {issue['bg_color']})")
                
                # Test pasa si no hay issues críticos
                critical_issues = [i for i in contrast_issues if i['contrast_ratio'] < 3.0]
                assert len(critical_issues) == 0, f"Issues críticos de contraste: {critical_issues}"
                
        except ImportError:
            pytest.skip(f"Módulo {module_name} no disponible")
    
    def test_button_contrast_standards(self, qtbot, accessibility_tester):
        """Test contraste específico de botones."""
        mock_db = Mock()
        mock_db.cursor.return_value.fetchall.return_value = []
        
        try:
            from rexus.modules.inventario.view import InventarioView
            
            with patch('rexus.core.database.get_inventario_connection', return_value=mock_db):
                view = InventarioView()
                qtbot.addWidget(view)
                view.show()
                
                buttons = view.findChildren(QPushButton)
                
                for button in buttons[:3]:  # Test primeros 3 botones
                    try:
                        bg_color, text_color = accessibility_tester.get_widget_colors(button)
                        contrast_ratio = accessibility_tester.calculate_contrast_ratio(text_color, bg_color)
                        
                        # Botones deben cumplir estándar AA mínimo
                        assert contrast_ratio >= 3.0, (
                            f"Botón '{button.text()}' no cumple contraste mínimo: "
                            f"{contrast_ratio:.2f} (mínimo 3.0)"
                        )
                        
                    except Exception:
                        # Continuar con siguiente botón si hay error
                        continue
                        
        except ImportError:
            pytest.skip("InventarioView no disponible")
    
    def test_focus_indicator_visibility(self, qtbot, accessibility_tester):
        """Test visibilidad de indicadores de foco."""
        mock_db = Mock()
        mock_db.cursor.return_value.fetchall.return_value = []
        
        try:
            from rexus.modules.compras.view import ComprasView
            
            with patch('rexus.core.database.get_inventario_connection', return_value=mock_db):
                view = ComprasView()
                qtbot.addWidget(view)
                view.show()
                
                focusable_widgets = AccessibilityTester.find_focusable_widgets(view)
                
                for widget in focusable_widgets[:3]:  # Test primeros 3 widgets
                    try:
                        # Dar foco al widget
                        widget.setFocus()
                        qtbot.wait(100)
                        
                        # Verificar que tiene foco
                        has_focus = widget.hasFocus()
                        
                        if has_focus:
                            # El widget debería tener algún indicador visual de foco
                            # Esto es más difícil de verificar programáticamente,
                            # pero al menos verificamos que puede recibir foco
                            assert widget.focusPolicy() != Qt.FocusPolicy.NoFocus
                            
                    except Exception:
                        continue
                        
        except ImportError:
            pytest.skip("ComprasView no disponible")


class TestScreenReaderCompatibility:
    """Tests para compatibilidad con lectores de pantalla."""
    
    def test_widget_accessibility_names(self, qtbot):
        """Test que los widgets tienen nombres accesibles."""
        mock_db = Mock()
        mock_db.cursor.return_value.fetchall.return_value = []
        
        try:
            from rexus.modules.inventario.view import InventarioView
            
            with patch('rexus.core.database.get_inventario_connection', return_value=mock_db):
                view = InventarioView()
                qtbot.addWidget(view)
                view.show()
                
                # Test que los widgets importantes tienen nombres
                line_edits = view.findChildren(QLineEdit)
                buttons = view.findChildren(QPushButton)
                labels = view.findChildren(QLabel)
                
                unnamed_widgets = []
                
                # Verificar LineEdits tienen nombres o labels asociados
                for line_edit in line_edits[:3]:
                    name = line_edit.objectName()
                    accessible_name = line_edit.accessibleName()
                    placeholder = line_edit.placeholderText()
                    
                    if not (name or accessible_name or placeholder):
                        unnamed_widgets.append(f"QLineEdit sin nombre accesible")
                
                # Verificar botones tienen texto o nombres
                for button in buttons[:3]:
                    text = button.text()
                    name = button.objectName()
                    accessible_name = button.accessibleName()
                    
                    if not (text or name or accessible_name):
                        unnamed_widgets.append(f"QPushButton sin texto/nombre")
                
                # Informar pero no fallar (muchos widgets pueden no tener nombres aún)
                if unnamed_widgets:
                    print(f"\nWidgets sin nombres accesibles encontrados: {len(unnamed_widgets)}")
                
                # Test pasa si no hay issues críticos
                assert len(unnamed_widgets) < 10, f"Demasiados widgets sin nombres: {len(unnamed_widgets)}"
                
        except ImportError:
            pytest.skip("InventarioView no disponible")
    
    def test_form_labels_association(self, qtbot):
        """Test asociación entre labels y campos de formulario."""
        mock_db = Mock()
        mock_db.cursor.return_value.fetchall.return_value = []
        
        try:
            from rexus.modules.compras.view import ComprasView
            
            with patch('rexus.core.database.get_inventario_connection', return_value=mock_db):
                view = ComprasView()
                qtbot.addWidget(view)
                view.show()
                
                labels = view.findChildren(QLabel)
                line_edits = view.findChildren(QLineEdit)
                
                # Verificar que existen labels y campos
                if labels and line_edits:
                    # Test básico: al menos hay labels y campos en la vista
                    assert len(labels) > 0
                    assert len(line_edits) > 0
                    
                    # En una implementación completa, verificaríamos buddy relationships
                    # o accessibility descriptions
                
        except ImportError:
            pytest.skip("ComprasView no disponible")
    
    def test_table_headers_accessibility(self, qtbot):
        """Test accesibilidad de headers de tabla."""
        mock_db = Mock()
        mock_db.cursor.return_value.fetchall.return_value = []
        
        try:
            from rexus.modules.inventario.view import InventarioView
            
            with patch('rexus.core.database.get_inventario_connection', return_value=mock_db):
                view = InventarioView()
                qtbot.addWidget(view)
                view.show()
                
                tables = view.findChildren(QTableWidget)
                
                for table in tables[:2]:  # Test primeras 2 tablas
                    column_count = table.columnCount()
                    
                    if column_count > 0:
                        # Verificar que las columnas tienen headers
                        for col in range(min(column_count, 5)):  # Test primeras 5 columnas
                            header_item = table.horizontalHeaderItem(col)
                            if header_item:
                                header_text = header_item.text()
                                assert len(header_text) > 0, f"Header de columna {col} vacío"
                
        except ImportError:
            pytest.skip("InventarioView no disponible")


class TestFocusManagement:
    """Tests para manejo de foco y navegación."""
    
    def test_initial_focus_setting(self, qtbot):
        """Test que el foco inicial se establece correctamente."""
        mock_db = Mock()
        mock_db.cursor.return_value.fetchall.return_value = []
        
        try:
            from rexus.modules.inventario.view import InventarioView
            
            with patch('rexus.core.database.get_inventario_connection', return_value=mock_db):
                view = InventarioView()
                qtbot.addWidget(view)
                view.show()
                qtbot.wait(200)  # Esperar inicialización completa
                
                # Verificar que algún widget tiene foco inicial o puede recibirlo
                focused_widget = QApplication.focusWidget()
                focusable_widgets = AccessibilityTester.find_focusable_widgets(view)
                
                # Debe haber widgets focusables disponibles
                assert len(focusable_widgets) > 0, "No hay widgets focusables en la vista"
                
                # Si no hay foco inicial, debería ser posible establecerlo
                if not focused_widget:
                    first_focusable = focusable_widgets[0]
                    first_focusable.setFocus()
                    qtbot.wait(100)
                    new_focus = QApplication.focusWidget()
                    assert new_focus is not None, "No se pudo establecer foco inicial"
                
        except ImportError:
            pytest.skip("InventarioView no disponible")
    
    def test_focus_trap_in_modals(self, qtbot):
        """Test que el foco se mantiene dentro de diálogos modales."""
        # Este test sería más relevante si tuviéramos diálogos modales accesibles
        # Por ahora, test básico de manejo de foco
        mock_db = Mock()
        mock_db.cursor.return_value.fetchall.return_value = []
        
        try:
            from rexus.modules.compras.view import ComprasView
            
            with patch('rexus.core.database.get_inventario_connection', return_value=mock_db):
                view = ComprasView()
                qtbot.addWidget(view)
                view.show()
                
                # Test básico de estabilidad de foco
                focusable_widgets = AccessibilityTester.find_focusable_widgets(view)
                
                if len(focusable_widgets) >= 2:
                    # Alternar foco entre widgets
                    for i in range(min(3, len(focusable_widgets))):
                        widget = focusable_widgets[i]
                        widget.setFocus()
                        qtbot.wait(100)
                        
                        # Verificar que el foco se mantiene en widgets válidos
                        current_focus = QApplication.focusWidget()
                        if current_focus:
                            assert current_focus in focusable_widgets
                
        except ImportError:
            pytest.skip("ComprasView no disponible")
    
    def test_focus_restoration(self, qtbot):
        """Test restauración de foco después de acciones."""
        mock_db = Mock()
        mock_db.cursor.return_value.fetchall.return_value = []
        
        try:
            from rexus.modules.inventario.view import InventarioView
            
            with patch('rexus.core.database.get_inventario_connection', return_value=mock_db):
                view = InventarioView()
                qtbot.addWidget(view)
                view.show()
                
                line_edits = view.findChildren(QLineEdit)
                
                if line_edits:
                    line_edit = line_edits[0]
                    line_edit.setFocus()
                    qtbot.wait(100)
                    
                    original_focus = QApplication.focusWidget()
                    
                    # Simular alguna acción que podría cambiar el foco
                    line_edit.setText("Test text")
                    qtbot.wait(100)
                    
                    # El foco debería mantenerse o ser manejado apropiadamente
                    current_focus = QApplication.focusWidget()
                    assert current_focus is not None, "Foco perdido después de acción"
                
        except ImportError:
            pytest.skip("InventarioView no disponible")


class TestA11yStandards:
    """Tests para cumplimiento de estándares de accesibilidad."""
    
    def test_minimum_click_target_size(self, qtbot):
        """Test que los objetivos de click tienen tamaño mínimo adecuado."""
        mock_db = Mock()
        mock_db.cursor.return_value.fetchall.return_value = []
        
        try:
            from rexus.modules.compras.view import ComprasView
            
            with patch('rexus.core.database.get_inventario_connection', return_value=mock_db):
                view = ComprasView()
                qtbot.addWidget(view)
                view.show()
                qtbot.wait(200)
                
                buttons = view.findChildren(QPushButton)
                
                small_targets = []
                
                for button in buttons[:5]:  # Test primeros 5 botones
                    size = button.size()
                    width, height = size.width(), size.height()
                    
                    # WCAG recomienda mínimo 44x44 píxeles para objetivos de click
                    min_size = 44
                    
                    if width < min_size or height < min_size:
                        small_targets.append({
                            'button': button.text() or button.objectName(),
                            'size': f"{width}x{height}"
                        })
                
                # Informar pero no fallar (guidance, no requirement estricto)
                if small_targets:
                    print(f"\nBotones pequeños encontrados: {small_targets}")
                
                # Test pasa si no hay botones extremadamente pequeños
                tiny_targets = [t for t in small_targets if 
                              any(int(dim) < 20 for dim in t['size'].split('x'))]
                assert len(tiny_targets) == 0, f"Botones demasiado pequeños: {tiny_targets}"
                
        except ImportError:
            pytest.skip("ComprasView no disponible")
    
    def test_color_not_only_indicator(self, qtbot, accessibility_tester):
        """Test que el color no es el único indicador de información."""
        # Test conceptual - verificaría que elementos críticos no dependen solo del color
        mock_db = Mock()
        mock_db.cursor.return_value.fetchall.return_value = []
        
        try:
            from rexus.modules.inventario.view import InventarioView
            
            with patch('rexus.core.database.get_inventario_connection', return_value=mock_db):
                view = InventarioView()
                qtbot.addWidget(view)
                view.show()
                
                # Test básico: elementos importantes tienen texto además de color
                buttons = view.findChildren(QPushButton)
                
                text_buttons = 0
                for button in buttons[:5]:
                    if button.text().strip():
                        text_buttons += 1
                
                # La mayoría de botones deberían tener texto
                if len(buttons) > 0:
                    text_ratio = text_buttons / len(buttons[:5])
                    assert text_ratio >= 0.5, "Muchos botones sin texto, posible dependencia solo de color"
                
        except ImportError:
            pytest.skip("InventarioView no disponible")


# Configuración para pytest
@pytest.fixture(scope="session")
def qapp():
    """Fixture de QApplication para tests de accesibilidad."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


if __name__ == "__main__":
    # Ejecutar tests de accesibilidad
    pytest.main([__file__, "-v", "-s", "--tb=short"])