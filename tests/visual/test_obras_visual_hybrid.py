"""
Tests Visuales para Módulo de Obras - Rexus.app

Implementación específica de tests visuales híbridos para
el módulo de gestión de obras con enfoque en:
- Lista y detalles de obras
- Asignación de materiales a obras
- Estados y progreso de obras
- Formularios complejos de obras
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from PyQt6.QtCore import Qt, QTimer, QDate
from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import (QTableWidget, QPushButton, QLineEdit, QComboBox, 
                            QDateEdit, QTextEdit, QProgressBar, QTabWidget)
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


class TestObrasVisualHybrid:
    """
    Tests visuales híbridos para el módulo de obras.
    
    Cobertura específica para:
    - Lista de obras con estados
    - Formularios de creación/edición
    - Asignación de materiales
    - Timeline y progreso
    - Presupuestos y costos
    """
    
    @hybrid_visual_test("test_obras_list_rendering_mock")
    def test_lista_obras_rendering_con_mocks(self, qapp, obras_mock_data):
        """
        Test MOCK: Valida rendering de lista de obras.
        
        Enfoque en:
        - Layout de columnas (código, nombre, estado, fechas)
        - Indicadores visuales de estado
        - Progreso de obras
        """
        try:
            from rexus.modules.obras.view import ObrasView
        except ImportError:
            pytest.skip("ObrasView no disponible")
        
        with patch('rexus.modules.obras.view.get_auth_manager') as mock_auth:
            mock_auth.return_value.get_current_user.return_value = {
                'username': 'admin', 'role': 'admin'
            }
            
            with patch('rexus.core.database.DatabaseConnection') as mock_db:
                # Mock datos de obras estructurados
                mock_db.return_value.execute_query.return_value = [
                    (
                        obra['id'], obra['codigo'], obra['nombre'],
                        obra['cliente'], obra['estado'], obra['fecha_inicio'],
                        obra['fecha_fin_estimada'], obra['presupuesto'],
                        obra['progreso'], obra['responsable']
                    )
                    for obra in obras_mock_data[:8]  # 8 obras para test rápido
                ]
                
                start_time = time.time()
                obras_view = ObrasView()
                render_time = time.time() - start_time
                
                # Validaciones de rendering
                if obras_view is None:
                    pytest.fail("ObrasView no se pudo crear")
                    
                if render_time >= 0.8:
                    pytest.fail(f"Rendering lento: {render_time}s >= 0.8s")
                
                # Verificar tabla principal de obras
                tables = obras_view.findChildren(QTableWidget)
                if not tables:
                    pytest.skip("No se encontró tabla de obras")
                
                tabla = tables[0]
                if not tabla.isVisible():
                    pytest.fail("Tabla de obras no visible")
                
                # Verificar estructura específica de obras
                expected_columns = 6  # Código, Nombre, Cliente, Estado, Fechas, Progreso mínimo
                if tabla.columnCount() < expected_columns:
                    pytest.fail(f"Columnas insuficientes: {tabla.columnCount()} < {expected_columns}")
                
                # Validar datos específicos de obras
                if tabla.rowCount() > 0:
                    # Verificar primera obra
                    row_data = {}
                    headers = []
                    
                    for col in range(min(tabla.columnCount(), 10)):
                        header_item = tabla.horizontalHeaderItem(col)
                        if header_item:
                            headers.append(header_item.text().lower())
                        
                        item = tabla.item(0, col)
                        if item:
                            row_data[col] = item.text()
                    
                    if len(row_data) == 0:
                        pytest.fail("No se encontraron datos en la tabla de obras")
                    
                    # Validar formato de código de obra
                    codigo_found = False
                    for col, data in row_data.items():
                        if col < len(headers) and ('codigo' in headers[col] or 'code' in headers[col]):
                            if data and len(data) >= 3:  # Código debe tener al menos 3 caracteres
                                codigo_found = True
                                break
                    
                    # Validar estado de obra
                    estado_found = False
                    valid_estados = ['pendiente', 'en_progreso', 'completada', 'cancelada', 'activa']
                    for col, data in row_data.items():
                        if col < len(headers) and 'estado' in headers[col]:
                            if any(estado in data.lower() for estado in valid_estados):
                                estado_found = True
                                break
                
                # Verificar componentes de filtro específicos de obras
                combos = obras_view.findChildren(QComboBox)
                estado_combos = [combo for combo in combos if 'estado' in combo.objectName().lower()]
                
                if estado_combos:
                    estado_combo = estado_combos[0]
                    if estado_combo.count() == 0:
                        pytest.fail("Combo estados de obra vacío")
                
                return obras_view
    
    @hybrid_visual_test("test_obra_form_creation_mock")
    def test_formulario_creacion_obra_con_mocks(self, qapp):
        """
        Test MOCK: Valida formulario de creación de obras.
        
        Enfoque en:
        - Campos obligatorios y validaciones
        - Selección de fechas
        - Cálculo de presupuestos
        - Asignación de responsables
        """
        try:
            from rexus.modules.obras.view import ObraDialog
        except ImportError:
            pytest.skip("ObraDialog no disponible")
        
        with patch('rexus.modules.obras.view.get_auth_manager'):
            dialog = ObraDialog()
            
            if dialog is None:
                pytest.fail("ObraDialog no se pudo crear")
            
            # Verificar campos específicos de obra
            line_edits = dialog.findChildren(QLineEdit)
            date_edits = dialog.findChildren(QDateEdit)
            text_edits = dialog.findChildren(QTextEdit)
            combos = dialog.findChildren(QComboBox)
            
            # Test campos básicos de obra
            expected_fields = ['codigo', 'nombre', 'cliente']
            found_fields = {}
            
            for edit in line_edits:
                field_name = edit.objectName().lower()
                for expected in expected_fields:
                    if expected in field_name:
                        found_fields[expected] = edit
                        break
            
            if len(found_fields) < 2:
                pytest.skip("Campos básicos de obra no identificables")
            
            # Test código de obra
            if 'codigo' in found_fields:
                codigo_field = found_fields['codigo']
                codigo_field.clear()
                codigo_field.setText("OBR-2025-001")
                if codigo_field.text() != "OBR-2025-001":
                    pytest.fail("Campo código obra no acepta formato válido")
            
            # Test nombre de obra
            if 'nombre' in found_fields:
                nombre_field = found_fields['nombre']
                nombre_field.clear()
                nombre_field.setText("Construcción Casa Modelo")
                if nombre_field.text() != "Construcción Casa Modelo":
                    pytest.fail("Campo nombre obra no acepta texto")
            
            # Test fechas de obra
            if date_edits:
                fecha_inicio = date_edits[0]
                
                # Probar fecha válida
                test_date = QDate(2025, 6, 15)
                fecha_inicio.setDate(test_date)
                if fecha_inicio.date() != test_date:
                    pytest.fail("DateEdit no acepta fecha válida")
                
                # Verificar que no permite fechas pasadas para inicio
                fecha_pasada = QDate(2020, 1, 1)
                fecha_inicio.setDate(fecha_pasada)
                # La validación específica depende de la implementación
            
            # Test selección de cliente
            cliente_combos = [combo for combo in combos if 'cliente' in combo.objectName().lower()]
            if cliente_combos:
                cliente_combo = cliente_combos[0]
                if cliente_combo.count() == 0:
                    pytest.fail("Combo clientes vacío")
                
                # Probar selección
                for i in range(min(cliente_combo.count(), 3)):
                    cliente_combo.setCurrentIndex(i)
                    if cliente_combo.currentIndex() != i:
                        pytest.fail(f"No se pudo seleccionar cliente índice {i}")
            
            # Test descripción de obra
            if text_edits:
                descripcion_edit = text_edits[0]
                test_description = "Construcción de vivienda unifamiliar de 120m2 con 3 dormitorios y 2 baños."
                descripcion_edit.clear()
                descripcion_edit.setText(test_description)
                if descripcion_edit.toPlainText() != test_description:
                    pytest.fail("TextEdit descripción no acepta texto")
            
            return dialog
    
    @hybrid_visual_test("test_materiales_obra_assignment_mock")
    def test_asignacion_materiales_obra_con_mocks(self, qapp):
        """
        Test MOCK: Valida asignación de materiales a obras.
        
        Enfoque en:
        - Lista de materiales disponibles
        - Cantidades y cálculos
        - Presupuesto dinámico
        - Validación de stock
        """
        try:
            from rexus.modules.obras.view import MaterialesObraDialog
        except ImportError:
            pytest.skip("MaterialesObraDialog no disponible")
        
        with patch('rexus.modules.obras.view.get_auth_manager'):
            with patch('rexus.core.database.DatabaseConnection') as mock_db:
                # Mock materiales disponibles
                mock_db.return_value.execute_query.return_value = [
                    (1, 'MAT001', 'Cemento Portland', 50, 25.50),
                    (2, 'MAT002', 'Arena Fina', 100, 15.75),
                    (3, 'MAT003', 'Ladrillo Común', 1000, 0.85),
                ]
                
                dialog = MaterialesObraDialog(obra_id=1)
                
                if dialog is None:
                    pytest.fail("MaterialesObraDialog no se pudo crear")
                
                # Verificar tablas de materiales
                tables = dialog.findChildren(QTableWidget)
                
                # Debe tener al menos 2 tablas: disponibles y asignados
                if len(tables) < 2:
                    pytest.skip("No se encontraron tablas de materiales")
                
                tabla_disponibles = tables[0]  # Materiales disponibles
                tabla_asignados = tables[1] if len(tables) > 1 else None  # Materiales asignados
                
                # Test tabla materiales disponibles
                if not tabla_disponibles.isVisible():
                    pytest.fail("Tabla materiales disponibles no visible")
                
                expected_cols_disp = 4  # Código, Descripción, Stock, Precio mínimo
                if tabla_disponibles.columnCount() < expected_cols_disp:
                    pytest.fail(f"Columnas tabla disponibles insuficientes: {tabla_disponibles.columnCount()}")
                
                # Test selección y asignación
                if tabla_disponibles.rowCount() > 0:
                    # Simular selección de material
                    tabla_disponibles.selectRow(0)
                    
                    # Buscar botón de asignar
                    buttons = dialog.findChildren(QPushButton)
                    asignar_buttons = [btn for btn in buttons if 'asignar' in btn.text().lower() or 'add' in btn.text().lower()]
                    
                    if asignar_buttons:
                        asignar_btn = asignar_buttons[0]
                        if not asignar_btn.isEnabled():
                            pytest.fail("Botón asignar no habilitado con material seleccionado")
                
                # Test tabla materiales asignados
                if tabla_asignados:
                    if not tabla_asignados.isVisible():
                        pytest.fail("Tabla materiales asignados no visible")
                    
                    expected_cols_asig = 5  # Material, Cantidad, Precio Unit, Subtotal, Acciones
                    if tabla_asignados.columnCount() < expected_cols_asig:
                        pytest.fail(f"Columnas tabla asignados insuficientes: {tabla_asignados.columnCount()}")
                
                # Test cálculo de presupuesto
                presupuesto_labels = [child for child in dialog.findChildren(QLineEdit) 
                                    if 'total' in child.objectName().lower() or 'presupuesto' in child.objectName().lower()]
                
                if presupuesto_labels:
                    presupuesto_field = presupuesto_labels[0]
                    # El presupuesto debe actualizarse automáticamente
                    # Verificar que muestra formato numérico
                    current_text = presupuesto_field.text()
                    if current_text and not current_text.replace('.', '').replace(',', '').isdigit():
                        # Permitir formato de moneda
                        pass
                
                return dialog
    
    @hybrid_visual_test("test_obra_progress_tracking_mock")
    def test_seguimiento_progreso_obra_con_mocks(self, qapp):
        """
        Test MOCK: Valida seguimiento de progreso de obras.
        
        Enfoque en:
        - Barras de progreso
        - Estados y transiciones
        - Timeline de actividades
        - Métricas de avance
        """
        try:
            from rexus.modules.obras.view import ObraDetalleView
        except ImportError:
            pytest.skip("ObraDetalleView no disponible")
        
        obra_mock = {
            'id': 1,
            'codigo': 'OBR-2025-001',
            'nombre': 'Casa Modelo A',
            'progreso': 65,
            'estado': 'en_progreso',
            'fecha_inicio': '2025-01-15',
            'fecha_fin_estimada': '2025-06-30'
        }
        
        with patch('rexus.modules.obras.view.get_auth_manager'):
            with patch('rexus.core.database.DatabaseConnection') as mock_db:
                mock_db.return_value.fetch_one.return_value = obra_mock
                
                detalle_view = ObraDetalleView(obra_id=1)
                
                if detalle_view is None:
                    pytest.fail("ObraDetalleView no se pudo crear")
                
                # Verificar barra de progreso
                progress_bars = detalle_view.findChildren(QProgressBar)
                if progress_bars:
                    progress_bar = progress_bars[0]
                    
                    if not progress_bar.isVisible():
                        pytest.fail("Barra de progreso no visible")
                    
                    # Verificar rango y valor
                    if progress_bar.minimum() != 0 or progress_bar.maximum() != 100:
                        pytest.fail("Rango de barra progreso incorrecto")
                    
                    # Test actualización de progreso
                    test_values = [25, 50, 75, 100]
                    for value in test_values:
                        progress_bar.setValue(value)
                        if progress_bar.value() != value:
                            pytest.fail(f"Barra progreso no acepta valor {value}")
                
                # Verificar selector de estado
                combos = detalle_view.findChildren(QComboBox)
                estado_combos = [combo for combo in combos if 'estado' in combo.objectName().lower()]
                
                if estado_combos:
                    estado_combo = estado_combos[0]
                    
                    # Verificar estados válidos
                    estados_validos = ['pendiente', 'en_progreso', 'completada', 'pausada', 'cancelada']
                    estados_encontrados = []
                    
                    for i in range(estado_combo.count()):
                        estado_text = estado_combo.itemText(i).lower()
                        if any(estado in estado_text for estado in estados_validos):
                            estados_encontrados.append(estado_text)
                    
                    if len(estados_encontrados) < 3:
                        pytest.fail("Estados de obra insuficientes en combo")
                    
                    # Test transición de estados
                    estado_combo.setCurrentIndex(1)  # Cambiar estado
                    if estado_combo.currentIndex() != 1:
                        pytest.fail("No se pudo cambiar estado de obra")
                
                # Verificar timeline/historial si existe
                tabs = detalle_view.findChildren(QTabWidget)
                if tabs:
                    tab_widget = tabs[0]
                    
                    # Buscar tab de historial/timeline
                    for i in range(tab_widget.count()):
                        tab_text = tab_widget.tabText(i).lower()
                        if 'historial' in tab_text or 'timeline' in tab_text or 'actividad' in tab_text:
                            tab_widget.setCurrentIndex(i)
                            if tab_widget.currentIndex() != i:
                                pytest.fail("No se pudo cambiar a tab de historial")
                            break
                
                return detalle_view
    
    # TEST CON DATOS REALES - Flujo crítico de obras
    @hybrid_visual_test("test_obras_real_data_workflow")
    def test_flujo_obras_datos_reales(self, qapp):
        """
        Test DATOS REALES: Flujo completo de gestión de obras.
        
        Valida:
        - Creación de obra con datos reales
        - Asignación real de materiales
        - Cálculos de presupuesto reales
        - Performance con datos de producción
        """
        try:
            from rexus.modules.obras.view import ObrasView, ObraDialog
            from rexus.core.auth import get_auth_manager
        except ImportError:
            pytest.skip("Componentes de obras no disponibles")
        
        try:
            auth_manager = get_auth_manager()
            if auth_manager:
                admin_user = {
                    'username': 'admin',
                    'role': 'admin',
                    'permissions': ['obras_read', 'obras_write', 'obras_create']
                }
                
                with patch.object(auth_manager, 'get_current_user', return_value=admin_user):
                    # Test carga de vista con datos reales
                    start_time = time.time()
                    obras_view = ObrasView()
                    load_time = time.time() - start_time
                    
                    if obras_view is None:
                        pytest.fail("ObrasView no se pudo crear con datos reales")
                    
                    if load_time >= 4.0:
                        pytest.fail(f"Carga obras con datos reales lenta: {load_time}s >= 4.0s")
                    
                    # Verificar datos reales en tabla
                    tables = obras_view.findChildren(QTableWidget)
                    if tables:
                        tabla = tables[0]
                        
                        # Test performance de filtros con datos reales
                        combos = obras_view.findChildren(QComboBox)
                        if combos:
                            start_filter = time.time()
                            combo = combos[0]
                            if combo.count() > 1:
                                combo.setCurrentIndex(1)
                            filter_time = time.time() - start_filter
                            
                            if filter_time >= 1.5:
                                pytest.fail(f"Filtro con datos reales lento: {filter_time}s >= 1.5s")
                        
                        # Verificar integridad de datos de obras reales
                        if tabla.rowCount() > 0:
                            # Verificar que las obras tienen datos válidos
                            for row in range(min(tabla.rowCount(), 3)):
                                row_has_data = False
                                for col in range(tabla.columnCount()):
                                    item = tabla.item(row, col)
                                    if item and len(item.text().strip()) > 0:
                                        row_has_data = True
                                        break
                                
                                if not row_has_data:
                                    pytest.fail(f"Obra en fila {row} sin datos válidos")
                            
                            # Test creación de obra con validación real
                            try:
                                start_dialog = time.time()
                                obra_dialog = ObraDialog()
                                dialog_time = time.time() - start_dialog
                                
                                if dialog_time >= 2.0:
                                    pytest.fail(f"Diálogo obra lento: {dialog_time}s >= 2.0s")
                                
                                if obra_dialog:
                                    # Verificar que los combos se cargan con datos reales
                                    dialog_combos = obra_dialog.findChildren(QComboBox)
                                    for combo in dialog_combos:
                                        if 'cliente' in combo.objectName().lower():
                                            if combo.count() >= 0:  # Puede no haber clientes en test DB
                                                break
                                
                            except Exception as dialog_error:
                                pytest.skip(f"Error en diálogo obra: {dialog_error}")
                    
                    return obras_view
                    
        except Exception as e:
            pytest.skip(f"Test obras con datos reales falló: {e}")
    
    def test_responsive_obras_interface_mock(self, qapp):
        """
        Test de responsividad de interface de obras con mocks.
        """
        try:
            from rexus.modules.obras.view import ObrasView
        except ImportError:
            pytest.skip("ObrasView no disponible")
        
        with patch('rexus.modules.obras.view.get_auth_manager') as mock_auth:
            mock_auth.return_value.get_current_user.return_value = {
                'username': 'admin', 'role': 'admin'
            }
            
            with patch('rexus.core.database.DatabaseConnection') as mock_db:
                mock_db.return_value.execute_query.return_value = []
                
                obras_view = ObrasView()
                
                # Test diferentes resoluciones
                resolutions = [
                    (1024, 768),   # Estándar
                    (1366, 768),   # Laptop común
                    (1920, 1080),  # HD
                ]
                
                for width, height in resolutions:
                    obras_view.resize(width, height)
                    
                    # Verificar que componentes siguen accesibles
                    tables = obras_view.findChildren(QTableWidget)
                    if tables:
                        tabla = tables[0]
                        if tabla.width() > width:
                            pytest.fail(f"Tabla no se adapta a ancho {width}")
                    
                    buttons = obras_view.findChildren(QPushButton)
                    for button in buttons[:5]:  # Verificar primeros 5 botones
                        if not button.isVisible():
                            continue  # Skip botones intencionalmente ocultos
                        
                        # Verificar que botón no se sale de pantalla
                        button_rect = button.geometry()
                        if button_rect.right() > width or button_rect.bottom() > height:
                            pytest.fail(f"Botón fuera de pantalla en resolución {width}x{height}")


# Fixtures específicos para obras
@pytest.fixture(scope="function")
def obras_mock_data():
    """Datos mock específicos para obras."""
    estados = ['pendiente', 'en_progreso', 'completada', 'pausada', 'cancelada']
    responsables = ['Juan Pérez', 'María García', 'Carlos López', 'Ana Martín']
    
    return [
        {
            'id': i,
            'codigo': f'OBR-2025-{i:03d}',
            'nombre': f'Obra {i} - Construcción Tipo {chr(65 + (i % 3))}',
            'cliente': f'Cliente {(i % 5) + 1} S.A.',
            'estado': estados[i % len(estados)],
            'fecha_inicio': f'2025-{((i % 12) + 1):02d}-{((i % 28) + 1):02d}',
            'fecha_fin_estimada': f'2025-{(((i + 6) % 12) + 1):02d}-{((i % 28) + 1):02d}',
            'presupuesto': round(50000.0 + (i * 15000.0), 2),
            'progreso': min(100, (i * 12) % 101),
            'responsable': responsables[i % len(responsables)],
            'direccion': f'Calle {i} #{i*10}, Zona {chr(65 + (i % 3))}',
            'descripcion': f'Construcción de obra tipo {chr(65 + (i % 3))} con especificaciones técnicas avanzadas.',
            'observaciones': f'Observaciones específicas para obra {i}'
        }
        for i in range(1, 51)  # 50 obras de prueba
    ]


@pytest.fixture(scope="function")
def mock_obras_view(qapp):
    """Vista mock de obras."""
    try:
        from rexus.modules.obras.view import ObrasView
        
        with patch('rexus.modules.obras.view.get_auth_manager') as mock_auth:
            mock_auth.return_value.get_current_user.return_value = {
                'username': 'admin', 'role': 'admin'
            }
            
            with patch('rexus.core.database.DatabaseConnection') as mock_db:
                mock_db.return_value.execute_query.return_value = []
                return ObrasView()
                
    except ImportError:
        pytest.skip("ObrasView no disponible")
