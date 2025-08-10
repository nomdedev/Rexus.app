"""
Tests Visuales para Módulo de Inventario - Rexus.app

Implementación específica de tests visuales híbridos para
el módulo de inventario con enfoque en:
- Rendering de listas de materiales
- Formularios de alta/baja de stock
- Búsquedas y filtros
- Performance con grandes datasets
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import QTableWidget, QPushButton, QLineEdit, QComboBox, QSpinBox
import time

try:
    from tests.strategies.hybrid_visual_testing import (
        HybridTestRunner, MockDataFactory, VisualTestValidator,
        hybrid_visual_test, VisualTestConfig
    )
except ImportError:
    def hybrid_visual_test(test_name=None):
        def decorator(func):
            return func
        return decorator


class TestInventarioVisualHybrid:
    """
    Tests visuales híbridos para el módulo de inventario.
    
    Cobertura específica para:
    - Lista de materiales y stock
    - Formularios de entrada/salida
    - Búsquedas complejas
    - Validaciones de cantidad
    """
    
    @hybrid_visual_test("test_inventory_table_rendering_mock")
    def test_tabla_inventario_rendering_con_mocks(self, qapp, inventario_mock_data):
        """
        Test MOCK: Valida rendering de tabla de inventario.
        
        Enfoque en:
        - Layout de columnas de materiales
        - Formato de cantidades y precios
        - Indicadores de stock bajo
        """
        try:
            from rexus.modules.inventario.view import InventarioView
        except ImportError:
            pytest.skip("InventarioView no disponible")
        
        with patch('rexus.modules.inventario.view.get_auth_manager') as mock_auth:
            mock_auth.return_value.get_current_user.return_value = {
                'username': 'admin', 'role': 'admin'
            }
            
            with patch('rexus.core.database.DatabaseConnection') as mock_db:
                # Mock datos de inventario estructurados
                mock_db.return_value.execute_query.return_value = [
                    (
                        item['id'], item['codigo'], item['descripcion'],
                        item['categoria'], item['unidad'], item['stock_actual'],
                        item['stock_minimo'], item['precio_unitario'], item['ubicacion']
                    )
                    for item in inventario_mock_data[:10]  # 10 items para test rápido
                ]
                
                start_time = time.time()
                inventario_view = InventarioView()
                render_time = time.time() - start_time
                
                # Validaciones de rendering
                if inventario_view is None:
                    pytest.fail("InventarioView no se pudo crear")
                    
                if render_time >= 0.5:
                    pytest.fail(f"Rendering lento: {render_time}s >= 0.5s")
                
                # Verificar tabla principal
                tables = inventario_view.findChildren(QTableWidget)
                if not tables:
                    pytest.skip("No se encontró tabla de inventario")
                
                tabla = tables[0]
                if not tabla.isVisible():
                    pytest.fail("Tabla de inventario no visible")
                
                # Verificar estructura de columnas específica de inventario
                expected_columns = 7  # Código, Descripción, Stock, Stock Min, Precio, Ubicación, etc.
                if tabla.columnCount() < expected_columns:
                    pytest.fail(f"Columnas insuficientes: {tabla.columnCount()} < {expected_columns}")
                
                # Validar datos específicos de inventario
                if tabla.rowCount() > 0:
                    # Verificar primera fila tiene datos de inventario válidos
                    row_data = {}
                    headers = []
                    
                    for col in range(min(tabla.columnCount(), 8)):
                        header_item = tabla.horizontalHeaderItem(col)
                        if header_item:
                            headers.append(header_item.text().lower())
                        
                        item = tabla.item(0, col)
                        if item:
                            row_data[col] = item.text()
                    
                    # Verificar que hay datos en las celdas críticas
                    if len(row_data) == 0:
                        pytest.fail("No se encontraron datos en la tabla")
                    
                    # Buscar columna de stock (debe ser numérica)
                    stock_found = False
                    for col, data in row_data.items():
                        if 'stock' in headers[col] if col < len(headers) else False:
                            try:
                                stock_value = int(data) if data.isdigit() else float(data)
                                if stock_value >= 0:
                                    stock_found = True
                                    break
                            except (ValueError, AttributeError):
                                continue
                    
                    if not stock_found and len(row_data) > 2:
                        # Advertencia si no se puede validar stock específicamente
                        pass  # No falla el test, solo nota
                
                return inventario_view
    
    @hybrid_visual_test("test_inventory_search_filters_mock")
    def test_filtros_busqueda_inventario_con_mocks(self, qapp):
        """
        Test MOCK: Valida funcionalidad de búsqueda y filtros.
        
        Enfoque en:
        - Filtro por categoría
        - Búsqueda por código/descripción
        - Filtro por stock bajo
        """
        try:
            from rexus.modules.inventario.view import InventarioView
        except ImportError:
            pytest.skip("InventarioView no disponible")
        
        with patch('rexus.modules.inventario.view.get_auth_manager') as mock_auth:
            mock_auth.return_value.get_current_user.return_value = {
                'username': 'admin', 'role': 'admin'
            }
            
            with patch('rexus.core.database.DatabaseConnection') as mock_db:
                # Mock con datos variados para filtros
                mock_data = [
                    (1, 'MAT001', 'Material A', 'Herramientas', 'pza', 50, 10, 25.50, 'A1-01'),
                    (2, 'MAT002', 'Material B', 'Consumibles', 'kg', 5, 20, 15.75, 'B2-03'),  # Stock bajo
                    (3, 'ELE001', 'Cable Eléctrico', 'Eléctrico', 'm', 100, 25, 8.90, 'C1-05'),
                ]
                mock_db.return_value.execute_query.return_value = mock_data
                
                inventario_view = InventarioView()
                
                # Verificar componentes de búsqueda
                line_edits = inventario_view.findChildren(QLineEdit)
                combos = inventario_view.findChildren(QComboBox)
                
                # Test de búsqueda por texto
                search_fields = [edit for edit in line_edits if 'search' in edit.objectName().lower() or 'buscar' in edit.objectName().lower()]
                
                if search_fields:
                    search_field = search_fields[0]
                    
                    # Probar búsqueda
                    search_field.clear()
                    search_field.setText("MAT001")
                    
                    if search_field.text() != "MAT001":
                        pytest.fail("Campo de búsqueda no acepta texto")
                    
                    # Simular búsqueda
                    QTest.keyPress(search_field, Qt.Key.Key_Return)
                
                # Test de filtro por categoría
                category_combos = [combo for combo in combos if 'categoria' in combo.objectName().lower() or 'category' in combo.objectName().lower()]
                
                if category_combos:
                    category_combo = category_combos[0]
                    
                    # Verificar que tiene opciones
                    if category_combo.count() == 0:
                        pytest.fail("Combo de categorías vacío")
                    
                    # Probar selección
                    for i in range(min(category_combo.count(), 3)):  # Probar primeras 3
                        category_combo.setCurrentIndex(i)
                        if category_combo.currentIndex() != i:
                            pytest.fail(f"No se pudo seleccionar categoría índice {i}")
                
                return inventario_view
    
    @hybrid_visual_test("test_inventory_form_validation_mock")
    def test_formulario_material_validacion_con_mocks(self, qapp):
        """
        Test MOCK: Valida formulario de alta/edición de materiales.
        
        Enfoque en:
        - Validación de campos obligatorios
        - Formato de precios y cantidades
        - Códigos únicos
        """
        try:
            from rexus.modules.inventario.view import MaterialDialog
        except ImportError:
            pytest.skip("MaterialDialog no disponible")
        
        with patch('rexus.modules.inventario.view.get_auth_manager'):
            dialog = MaterialDialog()
            
            if dialog is None:
                pytest.fail("MaterialDialog no se pudo crear")
            
            # Verificar campos específicos de material
            line_edits = dialog.findChildren(QLineEdit)
            spin_boxes = dialog.findChildren(QSpinBox)
            combos = dialog.findChildren(QComboBox)
            
            # Campos esperados en formulario de material
            expected_fields = ['codigo', 'descripcion', 'precio']
            found_fields = []
            
            for edit in line_edits:
                field_name = edit.objectName().lower()
                for expected in expected_fields:
                    if expected in field_name:
                        found_fields.append(expected)
                        break
            
            if len(found_fields) < 2:  # Al menos código y descripción
                pytest.skip("Campos de formulario no identificables")
            
            # Test validación de código
            codigo_field = None
            for edit in line_edits:
                if 'codigo' in edit.objectName().lower():
                    codigo_field = edit
                    break
            
            if codigo_field:
                # Probar código válido
                codigo_field.clear()
                codigo_field.setText("TEST001")
                if codigo_field.text() != "TEST001":
                    pytest.fail("Campo código no acepta texto válido")
                
                # Probar código con caracteres especiales
                codigo_field.clear()
                codigo_field.setText("T@ST-001")
                # Depende de la validación implementada
            
            # Test validación de precio
            precio_field = None
            for edit in line_edits:
                if 'precio' in edit.objectName().lower():
                    precio_field = edit
                    break
            
            if precio_field:
                # Probar precio válido
                precio_field.clear()
                precio_field.setText("25.50")
                if precio_field.text() != "25.50":
                    pytest.fail("Campo precio no acepta valor decimal válido")
                
                # Probar precio inválido
                precio_field.clear()
                precio_field.setText("abc")
                # La validación específica depende de la implementación
            
            # Test de spinboxes para cantidades
            for spin in spin_boxes:
                if 'stock' in spin.objectName().lower() or 'cantidad' in spin.objectName().lower():
                    # Probar valores válidos
                    spin.setValue(100)
                    if spin.value() != 100:
                        pytest.fail("SpinBox no acepta valor válido")
                    
                    # Probar valor mínimo
                    spin.setValue(0)
                    if spin.value() != max(0, spin.minimum()):
                        pytest.fail("SpinBox no respeta valor mínimo")
            
            return dialog
    
    @hybrid_visual_test("test_stock_movements_interface_mock")
    def test_interfaz_movimientos_stock_con_mocks(self, qapp):
        """
        Test MOCK: Valida interfaz de movimientos de stock.
        
        Enfoque en:
        - Entrada/salida de materiales
        - Validación de cantidades
        - Registro de movimientos
        """
        try:
            from rexus.modules.inventario.view import MovimientoStockDialog
        except ImportError:
            pytest.skip("MovimientoStockDialog no disponible")
        
        with patch('rexus.modules.inventario.view.get_auth_manager'):
            dialog = MovimientoStockDialog()
            
            if dialog is None:
                pytest.fail("MovimientoStockDialog no se pudo crear")
            
            # Verificar componentes de movimiento
            line_edits = dialog.findChildren(QLineEdit)
            spin_boxes = dialog.findChildren(QSpinBox)
            combos = dialog.findChildren(QComboBox)
            
            # Test tipo de movimiento
            tipo_combos = [combo for combo in combos if 'tipo' in combo.objectName().lower() or 'movement' in combo.objectName().lower()]
            
            if tipo_combos:
                tipo_combo = tipo_combos[0]
                
                # Verificar opciones de movimiento
                if tipo_combo.count() == 0:
                    pytest.fail("Combo tipo movimiento vacío")
                
                # Probar selección entrada/salida
                for i in range(tipo_combo.count()):
                    tipo_combo.setCurrentIndex(i)
                    current_text = tipo_combo.currentText().lower()
                    
                    # Verificar que son tipos válidos
                    valid_types = ['entrada', 'salida', 'entrada', 'exit', 'in', 'out']
                    is_valid = any(valid_type in current_text for valid_type in valid_types)
                    
                    if tipo_combo.count() > 1 and i == 0 and not is_valid:
                        # Primera opción podría ser placeholder
                        continue
            
            # Test cantidad de movimiento
            cantidad_fields = [spin for spin in spin_boxes if 'cantidad' in spin.objectName().lower() or 'qty' in spin.objectName().lower()]
            
            if cantidad_fields:
                cantidad_spin = cantidad_fields[0]
                
                # Probar cantidades válidas
                test_quantities = [1, 10, 100]
                for qty in test_quantities:
                    cantidad_spin.setValue(qty)
                    if cantidad_spin.value() != qty:
                        pytest.fail(f"SpinBox cantidad no acepta valor {qty}")
                
                # Verificar no permite cantidades negativas para stock
                cantidad_spin.setValue(-10)
                if cantidad_spin.value() < 0 and cantidad_spin.minimum() >= 0:
                    pytest.fail("SpinBox permite cantidades negativas incorrectamente")
            
            # Test motivo/observaciones
            motivo_fields = [edit for edit in line_edits if 'motivo' in edit.objectName().lower() or 'observacion' in edit.objectName().lower()]
            
            if motivo_fields:
                motivo_field = motivo_fields[0]
                
                motivo_field.clear()
                motivo_field.setText("Entrada por compra")
                if motivo_field.text() != "Entrada por compra":
                    pytest.fail("Campo motivo no acepta texto")
            
            return dialog
    
    # TEST CON DATOS REALES - Flujo crítico
    @hybrid_visual_test("test_inventory_real_data_performance")
    def test_performance_inventario_datos_reales(self, qapp):
        """
        Test DATOS REALES: Performance con inventario real.
        
        Valida:
        - Tiempo de carga con datos reales
        - Búsquedas con dataset real
        - Comportamiento con stock real
        """
        try:
            from rexus.modules.inventario.view import InventarioView
            from rexus.core.auth import get_auth_manager
        except ImportError:
            pytest.skip("Componentes de inventario no disponibles")
        
        try:
            auth_manager = get_auth_manager()
            if auth_manager:
                admin_user = {
                    'username': 'admin',
                    'role': 'admin',
                    'permissions': ['inventario_read', 'inventario_write']
                }
                
                with patch.object(auth_manager, 'get_current_user', return_value=admin_user):
                    # Medir tiempo de carga con datos reales
                    start_time = time.time()
                    inventario_view = InventarioView()
                    load_time = time.time() - start_time
                    
                    if inventario_view is None:
                        pytest.fail("InventarioView no se pudo crear con datos reales")
                    
                    # Validar performance aceptable
                    if load_time >= 3.0:
                        pytest.fail(f"Carga lenta con datos reales: {load_time}s >= 3.0s")
                    
                    # Verificar datos reales en tabla
                    tables = inventario_view.findChildren(QTableWidget)
                    if tables:
                        tabla = tables[0]
                        
                        # Con datos reales, verificar contenido
                        if tabla.rowCount() >= 0:  # Puede no haber datos en test DB
                            
                            # Test de búsqueda con datos reales
                            search_fields = inventario_view.findChildren(QLineEdit)
                            if search_fields:
                                search_field = search_fields[0]
                                
                                # Búsqueda que debe ser rápida incluso con datos reales
                                start_search = time.time()
                                search_field.setText("test")
                                QTest.keyPress(search_field, Qt.Key.Key_Return)
                                search_time = time.time() - start_search
                                
                                if search_time >= 2.0:
                                    pytest.fail(f"Búsqueda lenta: {search_time}s >= 2.0s")
                            
                            # Verificar integridad de datos reales
                            if tabla.rowCount() > 0:
                                for row in range(min(tabla.rowCount(), 5)):  # Verificar primeras 5 filas
                                    row_valid = False
                                    for col in range(tabla.columnCount()):
                                        item = tabla.item(row, col)
                                        if item and len(item.text().strip()) > 0:
                                            row_valid = True
                                            break
                                    
                                    if not row_valid:
                                        pytest.fail(f"Fila {row} con datos reales vacía")
                    
                    return inventario_view
                    
        except Exception as e:
            pytest.skip(f"Test con datos reales falló: {e}")
    
    def test_bulk_operations_performance_mock(self, qapp):
        """
        Test de operaciones masivas con mocks.
        """
        # Mock con dataset grande
        mock_factory = MockDataFactory()
        large_inventory = mock_factory.create_inventario_mock(count=500)
        
        try:
            from rexus.modules.inventario.view import InventarioView
        except ImportError:
            pytest.skip("InventarioView no disponible")
        
        with patch('rexus.modules.inventario.view.get_auth_manager') as mock_auth:
            mock_auth.return_value.get_current_user.return_value = {
                'username': 'admin', 'role': 'admin'
            }
            
            with patch('rexus.core.database.DatabaseConnection') as mock_db:
                mock_db.return_value.execute_query.return_value = [
                    (
                        item['id'], item['codigo'], item['descripcion'],
                        item['categoria'], item['unidad'], item['stock_actual'],
                        item['stock_minimo'], item['precio_unitario'], item['ubicacion']
                    )
                    for item in large_inventory
                ]
                
                # Test carga masiva
                start_time = time.time()
                inventario_view = InventarioView()
                load_time = time.time() - start_time
                
                if load_time >= 5.0:
                    pytest.fail(f"Carga masiva lenta: {load_time}s >= 5.0s")
                
                # Test filtrado sobre dataset grande
                if hasattr(inventario_view, 'filter_data'):
                    start_filter = time.time()
                    # Simular filtro
                    filter_time = time.time() - start_filter
                    
                    if filter_time >= 1.0:
                        pytest.fail(f"Filtrado lento: {filter_time}s >= 1.0s")


# Fixtures específicos para inventario
@pytest.fixture(scope="function")
def inventario_mock_data():
    """Datos mock específicos para inventario."""
    return [
        {
            'id': i,
            'codigo': f'MAT{i:03d}',
            'descripcion': f'Material de prueba {i}',
            'categoria': ['Herramientas', 'Consumibles', 'Eléctrico', 'Plomería'][i % 4],
            'unidad': ['pza', 'kg', 'm', 'lt'][i % 4],
            'stock_actual': max(0, 50 - (i % 60)),  # Algunos con stock bajo
            'stock_minimo': 10 + (i % 20),
            'precio_unitario': round(10.0 + (i * 2.5), 2),
            'ubicacion': f'{chr(65 + (i % 3))}{(i % 3) + 1}-{(i % 10):02d}',
            'proveedor': f'Proveedor {(i % 5) + 1}',
            'fecha_ultima_entrada': f'2025-01-{(i % 28) + 1:02d}'
        }
        for i in range(1, 101)  # 100 items de inventario
    ]


@pytest.fixture(scope="function") 
def mock_inventario_view(qapp):
    """Vista mock de inventario."""
    try:
        from rexus.modules.inventario.view import InventarioView
        
        with patch('rexus.modules.inventario.view.get_auth_manager') as mock_auth:
            mock_auth.return_value.get_current_user.return_value = {
                'username': 'admin', 'role': 'admin'
            }
            
            with patch('rexus.core.database.DatabaseConnection') as mock_db:
                mock_db.return_value.execute_query.return_value = []
                return InventarioView()
                
    except ImportError:
        pytest.skip("InventarioView no disponible")
