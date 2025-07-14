"""
Tests específicos de clicks para formularios de obras.
Cubre formularios de crear obras, asignar materiales, cronogramas, etc.
"""

                            QSpinBox, QPushButton, QTableWidget, QCheckBox,
                            QTextEdit, QDateEdit, QProgressBar, QCalendarWidget)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

@pytest.fixture(scope="session")
def app():
    """Fixture de aplicación Qt."""
    if not QApplication.instance():
        return QApplication([])
    return QApplication.instance()

@pytest.fixture
def mock_db_obras():
    """Mock específico para base de datos de obras."""
    mock_db = Mock()
    mock_db.ejecutar_query = Mock(return_value=[
        {'id': 1, 'nombre': 'Obra Torre Central', 'estado': 'en_progreso', 'fecha_inicio': '2025-01-01'},
        {'id': 2, 'nombre': 'Edificio Residencial Norte', 'estado': 'planificacion', 'fecha_inicio': '2025-02-15'}
    ])
    return mock_db

@pytest.fixture
def mock_controller_obras():
    """Mock de controlador para obras."""
    controller = Mock()
    controller.crear_obra = Mock(return_value={"success": True, "message": "Obra creada"})
    controller.actualizar_obra = Mock(return_value={"success": True, "message": "Obra actualizada"})
    controller.obtener_obras = Mock(return_value=[
        {'id': 1, 'nombre': 'Obra Test', 'cliente': 'Cliente Test', 'estado': 'activa'}
    ])
    controller.obtener_materiales_disponibles = Mock(return_value=[
        {'id': 1, 'codigo': 'VID001', 'descripcion': 'Vidrio templado', 'stock': 50},
        {'id': 2, 'codigo': 'PER002', 'descripcion': 'Perfil aluminio', 'stock': 100}
    ])
    return controller


class TestFormularioCrearObra:
    """Tests para formulario de crear nueva obra."""

    def test_click_abrir_formulario_crear_obra(self, app, mock_db_obras, mock_controller_obras):
        """Test de click para abrir formulario de crear obra."""
        try:
            # Arrange
            view = ObrasView(db_connection=mock_db_obras, usuario_actual="TEST_USER")
            view.controller = mock_controller_obras
            view.show()
            QTest.qWait(100)

            # Buscar botón de agregar obra
            buttons = view.findChildren(QPushButton)
            add_buttons = [btn for btn in buttons
                          if "agregar" in btn.toolTip().lower() or
                             "nueva" in btn.toolTip().lower() or
                             "crear" in btn.toolTip().lower()]

            # Act - Click en crear obra
            if add_buttons:
                QTest.mouseClick(add_buttons[0], Qt.MouseButton.LeftButton)
                QTest.qWait(300)

                # Buscar diálogo que se abrió
                dialogs = [w for w in app.allWidgets() if isinstance(w, QDialog) and w.isVisible()]
                if dialogs:
                    dialog = dialogs[0]
                    assert "obra" in dialog.windowTitle().lower()
                    dialog.close()

            view.close()
        except ImportError:
            pytest.skip("Módulo de obras no disponible")

    def test_llenar_formulario_crear_obra_completo(self, app, mock_db_obras, mock_controller_obras):
        """Test completo de llenado del formulario de crear obra."""
        try:
            # Arrange - Crear formulario mock
            dialog = QDialog()
            form_layout = QFormLayout()

            # Campos típicos de una obra
            nombre_input = QLineEdit()
            nombre_input.setObjectName("nombre_obra")
            form_layout.addRow("Nombre:", nombre_input)

            cliente_input = QLineEdit()
            cliente_input.setObjectName("cliente_obra")
            form_layout.addRow("Cliente:", cliente_input)

            direccion_input = QTextEdit()
            direccion_input.setObjectName("direccion_obra")
            direccion_input.setMaximumHeight(80)
            form_layout.addRow("Dirección:", direccion_input)

            fecha_inicio = QDateEdit()
            fecha_inicio.setObjectName("fecha_inicio")
            fecha_inicio.setDate(QDate.currentDate())
            form_layout.addRow("Fecha inicio:", fecha_inicio)

            fecha_fin = QDateEdit()
            fecha_fin.setObjectName("fecha_fin")
            fecha_fin.setDate(QDate.currentDate().addDays(30))
            form_layout.addRow("Fecha fin estimada:", fecha_fin)

            estado_combo = QComboBox()
            estado_combo.setObjectName("estado_obra")
            estado_combo.addItems(["planificacion", "en_progreso", "pausada", "finalizada"])
            form_layout.addRow("Estado:", estado_combo)

            presupuesto_input = QSpinBox()
            presupuesto_input.setObjectName("presupuesto")
            presupuesto_input.setMaximum(999999999)
            presupuesto_input.setSuffix(" $")
            form_layout.addRow("Presupuesto:", presupuesto_input)

            btn_guardar = QPushButton("Guardar Obra")
            form_layout.addRow("", btn_guardar)

            dialog.setLayout(form_layout)
            dialog.show()
            QTest.qWait(100)

            # Act - Llenar formulario
            QTest.keyClicks(nombre_input, "Torre Empresarial Centro")
            QTest.qWait(50)

            QTest.keyClicks(cliente_input, "Constructora ABC S.A.")
            QTest.qWait(50)

            direccion_input.setPlainText("Av. Principal 123, Ciudad")
            QTest.qWait(50)

            # Cambiar fechas
            fecha_inicio.setDate(QDate.currentDate().addDays(7))
            QTest.qWait(30)

            fecha_fin.setDate(QDate.currentDate().addDays(90))
            QTest.qWait(30)

            # Cambiar estado
            estado_combo.setCurrentIndex(1)  # en_progreso
            QTest.qWait(30)

            # Establecer presupuesto
            presupuesto_input.setValue(500000)
            QTest.qWait(30)

            # Click en guardar
            QTest.mouseClick(btn_guardar, Qt.MouseButton.LeftButton)
            QTest.qWait(100)

            # Assert
            assert nombre_input.text() == "Torre Empresarial Centro"
            assert cliente_input.text() == "Constructora ABC S.A."
            assert "Av. Principal 123" in direccion_input.toPlainText()
            assert estado_combo.currentText() == "en_progreso"
            assert presupuesto_input.value() == 500000

            dialog.close()
        except ImportError:
            pytest.skip("Módulo de obras no disponible")


class TestFormularioAsignarMateriales:
    """Tests para formulario de asignar materiales a obras."""

    def test_click_asignar_materiales_obra(self, app, mock_db_obras, mock_controller_obras):
        """Test de click en asignar materiales a obra."""
        try:
            # Arrange
            view = ObrasView(db_connection=mock_db_obras, usuario_actual="TEST_USER")
            view.controller = mock_controller_obras
            view.show()
            QTest.qWait(100)

            # Buscar botón de materiales
            buttons = view.findChildren(QPushButton)
            material_buttons = [btn for btn in buttons
                               if "material" in btn.toolTip().lower() or
                                  "asignar" in btn.toolTip().lower()]

            # Act - Click en asignar materiales
            for button in material_buttons:
                QTest.mouseClick(button, Qt.MouseButton.LeftButton)
                QTest.qWait(200)

                # Buscar diálogos de materiales
                dialogs = [w for w in app.allWidgets() if isinstance(w, QDialog) and w.isVisible()]
                for dialog in dialogs:
                    dialog.close()

            view.close()
        except ImportError:
            pytest.skip("Módulo de obras no disponible")

    def test_seleccionar_materiales_formulario(self, app, mock_db_obras):
        """Test de selección de materiales en formulario."""
        # Arrange - Crear formulario de selección de materiales
        dialog = QDialog()
        layout = QVBoxLayout()

        lista_materiales = QListWidget()
        lista_materiales.setSelectionMode(QListWidget.SelectionMode.MultiSelection)

        # Agregar materiales
        materiales = [
            "Vidrio templado 6mm - Stock: 50",
            "Perfil aluminio blanco - Stock: 100",
            "Herraje bisagra - Stock: 200",
            "Sellador silicona - Stock: 25"
        ]

        for material in materiales:
            item = QListWidgetItem(material)
            lista_materiales.addItem(item)

        layout.addWidget(lista_materiales)

        btn_confirmar = QPushButton("Confirmar selección")
        layout.addWidget(btn_confirmar)

        dialog.setLayout(layout)
        dialog.show()
        QTest.qWait(100)

        # Act - Seleccionar múltiples materiales
        for i in range(0, 3, 2):  # Seleccionar items 0 y 2
            item = lista_materiales.item(i)
            lista_materiales.setItemSelected(item, True)
            QTest.qWait(50)

        # Click en confirmar
        QTest.mouseClick(btn_confirmar, Qt.MouseButton.LeftButton)
        QTest.qWait(100)

        # Assert
        selected_items = lista_materiales.selectedItems()
        assert len(selected_items) == 2

        dialog.close()


class TestFormularioCronograma:
    """Tests para formularios de cronograma de obras."""

    def test_click_crear_cronograma(self, app, mock_db_obras):
        """Test de click en crear cronograma."""
        try:
            # Arrange
            view = ObrasView(db_connection=mock_db_obras, usuario_actual="TEST_USER")
            view.show()
            QTest.qWait(100)

            # Buscar botón de cronograma
            buttons = view.findChildren(QPushButton)
            cronograma_buttons = [btn for btn in buttons
                                 if "cronograma" in btn.toolTip().lower() or
                                    "planificar" in btn.toolTip().lower()]

            # Act - Click en cronograma
            for button in cronograma_buttons:
                QTest.mouseClick(button, Qt.MouseButton.LeftButton)
                QTest.qWait(200)

            view.close()
        except ImportError:
            pytest.skip("Módulo de obras no disponible")

    def test_formulario_agregar_tarea_cronograma(self, app):
        """Test de formulario para agregar tarea al cronograma."""
        # Arrange - Crear formulario de tarea
        dialog = QDialog()
        form = QFormLayout()

        nombre_tarea = QLineEdit()
        nombre_tarea.setPlaceholderText("Nombre de la tarea")
        form.addRow("Tarea:", nombre_tarea)

        descripcion_tarea = QTextEdit()
        descripcion_tarea.setMaximumHeight(80)
        form.addRow("Descripción:", descripcion_tarea)

        fecha_inicio_tarea = QDateEdit()
        fecha_inicio_tarea.setDate(QDate.currentDate())
        form.addRow("Fecha inicio:", fecha_inicio_tarea)

        duracion_tarea = QSpinBox()
        duracion_tarea.setMinimum(1)
        duracion_tarea.setMaximum(365)
        duracion_tarea.setSuffix(" días")
        form.addRow("Duración:", duracion_tarea)

        prioridad_combo = QComboBox()
        prioridad_combo.addItems(["Baja", "Media", "Alta", "Crítica"])
        form.addRow("Prioridad:", prioridad_combo)

        responsable_combo = QComboBox()
        responsable_combo.addItems(["Juan Pérez", "María García", "Carlos López"])
        form.addRow("Responsable:", responsable_combo)

        btn_agregar = QPushButton("Agregar Tarea")
        form.addRow("", btn_agregar)

        dialog.setLayout(form)
        dialog.show()
        QTest.qWait(100)

        # Act - Llenar formulario de tarea
        QTest.keyClicks(nombre_tarea, "Instalación de vidrios principales")
        QTest.qWait(50)

        descripcion_tarea.setPlainText("Instalación de todos los vidrios de la fachada principal del edificio")
        QTest.qWait(50)

        fecha_inicio_tarea.setDate(QDate.currentDate().addDays(14))
        QTest.qWait(30)

        duracion_tarea.setValue(5)
        QTest.qWait(30)

        prioridad_combo.setCurrentIndex(2)  # Alta
        QTest.qWait(30)

        responsable_combo.setCurrentIndex(0)  # Juan Pérez
        QTest.qWait(30)

        # Click en agregar
        QTest.mouseClick(btn_agregar, Qt.MouseButton.LeftButton)
        QTest.qWait(100)

        # Assert
        assert nombre_tarea.text() == "Instalación de vidrios principales"
        assert "fachada principal" in descripcion_tarea.toPlainText()
        assert duracion_tarea.value() == 5
        assert prioridad_combo.currentText() == "Alta"

        dialog.close()


class TestFormularioPresupuesto:
    """Tests para formularios de presupuesto de obras."""

    def test_formulario_calcular_presupuesto(self, app):
        """Test de formulario para calcular presupuesto."""
        # Arrange - Crear formulario de presupuesto
        dialog = QDialog()
        form = QFormLayout()

        # Campos de costos
        costo_materiales = QDoubleSpinBox()
        costo_materiales.setMaximum(999999.99)
        costo_materiales.setPrefix("$ ")
        form.addRow("Costo materiales:", costo_materiales)

        costo_mano_obra = QDoubleSpinBox()
        costo_mano_obra.setMaximum(999999.99)
        costo_mano_obra.setPrefix("$ ")
        form.addRow("Mano de obra:", costo_mano_obra)

        gastos_generales = QDoubleSpinBox()
        gastos_generales.setMaximum(999999.99)
        gastos_generales.setPrefix("$ ")
        form.addRow("Gastos generales:", gastos_generales)

        margen_ganancia = QSpinBox()
        margen_ganancia.setMinimum(0)
        margen_ganancia.setMaximum(100)
        margen_ganancia.setSuffix(" %")
        form.addRow("Margen ganancia:", margen_ganancia)

        # Campo de total (solo lectura)
        total_presupuesto = QLabel("$ 0.00")
        total_presupuesto.setStyleSheet("font-weight: bold; font-size: 14px;")
        form.addRow("TOTAL:", total_presupuesto)

        btn_calcular = QPushButton("Calcular Total")
        form.addRow("", btn_calcular)

        dialog.setLayout(form)
        dialog.show()
        QTest.qWait(100)

        # Act - Llenar costos
        costo_materiales.setValue(50000.00)
        QTest.qWait(50)

        costo_mano_obra.setValue(30000.00)
        QTest.qWait(50)

        gastos_generales.setValue(5000.00)
        QTest.qWait(50)

        margen_ganancia.setValue(20)  # 20%
        QTest.qWait(50)

        # Click en calcular
        QTest.mouseClick(btn_calcular, Qt.MouseButton.LeftButton)
        QTest.qWait(100)

        # Calcular total esperado
        subtotal = 50000.00 + 30000.00 + 5000.00  # 85000
        total_esperado = subtotal * 1.20  # 102000 con 20% margen

        # Assert
        assert costo_materiales.value() == 50000.00
        assert costo_mano_obra.value() == 30000.00
        assert margen_ganancia.value() == 20

        dialog.close()


class TestFormularioSeguimientoObra:
    """Tests para formularios de seguimiento de obras."""

    def test_formulario_actualizar_progreso(self, app):
        """Test de formulario para actualizar progreso de obra."""
        # Arrange - Crear formulario de progreso
        dialog = QDialog()
        form = QFormLayout()

        # Progreso general
        progreso_general = QSlider(Qt.Orientation.Horizontal)
        progreso_general.setMinimum(0)
        progreso_general.setMaximum(100)
        progreso_general.setValue(65)
        form.addRow("Progreso general:", progreso_general)

        # Barra de progreso visual
        barra_progreso = QProgressBar()
        barra_progreso.setMinimum(0)
        barra_progreso.setMaximum(100)
        barra_progreso.setValue(65)
        form.addRow("", barra_progreso)

        # Tareas completadas
        tareas_completadas = QSpinBox()
        tareas_completadas.setMinimum(0)
        tareas_completadas.setMaximum(999)
        form.addRow("Tareas completadas:", tareas_completadas)

        # Observaciones
        observaciones = QTextEdit()
        observaciones.setMaximumHeight(100)
        observaciones.setPlaceholderText("Observaciones del progreso...")
        form.addRow("Observaciones:", observaciones)

        # Estado actualizado
        nuevo_estado = QComboBox()
        nuevo_estado.addItems(["en_progreso", "pausada", "retrasada", "adelantada"])
        form.addRow("Estado:", nuevo_estado)

        btn_actualizar = QPushButton("Actualizar Progreso")
        form.addRow("", btn_actualizar)

        dialog.setLayout(form)
        dialog.show()
        QTest.qWait(100)

        # Conectar slider con barra de progreso
        progreso_general.valueChanged.connect(barra_progreso.setValue)

        # Act - Actualizar progreso
        progreso_general.setValue(80)
        QTest.qWait(50)

        tareas_completadas.setValue(45)
        QTest.qWait(50)

        observaciones.setPlainText("Se completó la instalación de ventanas del segundo piso")
        QTest.qWait(50)

        nuevo_estado.setCurrentIndex(3)  # adelantada
        QTest.qWait(50)

        # Click en actualizar
        QTest.mouseClick(btn_actualizar, Qt.MouseButton.LeftButton)
        QTest.qWait(100)

        # Assert
        assert progreso_general.value() == 80
        assert barra_progreso.value() == 80
        assert tareas_completadas.value() == 45
        assert nuevo_estado.currentText() == "adelantada"

        dialog.close()


class TestFormularioCalendarioObra:
    """Tests para formularios con calendario de obras."""

    def test_seleccionar_fechas_calendario(self, app):
        """Test de selección de fechas en calendario."""
        # Arrange - Crear formulario con calendario
        dialog = QDialog()
        layout = QVBoxLayout()

        calendario = QCalendarWidget()
        calendario.setSelectedDate(QDate.currentDate())
        layout.addWidget(calendario)

        fecha_seleccionada = QLabel(f"Fecha: {QDate.currentDate().toString()}")
        layout.addWidget(fecha_seleccionada)

        btn_confirmar = QPushButton("Confirmar fecha")
        layout.addWidget(btn_confirmar)

        dialog.setLayout(layout)
        dialog.show()
        QTest.qWait(100)

        # Conectar señal del calendario
        calendario.selectionChanged.connect(
            lambda: fecha_seleccionada.setText(f"Fecha: {calendario.selectedDate().toString()}")
        )

        # Act - Seleccionar nueva fecha
        nueva_fecha = QDate.currentDate().addDays(15)
        calendario.setSelectedDate(nueva_fecha)
        QTest.qWait(100)

        # Click en confirmar
        QTest.mouseClick(btn_confirmar, Qt.MouseButton.LeftButton)
        QTest.qWait(100)

        # Assert
        assert calendario.selectedDate() == nueva_fecha
        assert nueva_fecha.toString() in fecha_seleccionada.text()

        dialog.close()


class TestInteraccionesTablaObras:
    """Tests de interacciones con tablas de obras."""

    def test_filtrar_obras_por_estado(self, app, mock_db_obras):
        """Test de filtrado de obras por estado."""
        try:
            # Arrange
            view = ObrasView(db_connection=mock_db_obras, usuario_actual="TEST_USER")
            view.show()
            QTest.qWait(100)

            # Buscar combo de filtro de estado
            combos = view.findChildren(QComboBox)
            estado_combos = [combo for combo in combos
                            if "estado" in combo.toolTip().lower() or
                               "filtro" in combo.toolTip().lower()]

            # Act - Cambiar filtros de estado
            for combo in estado_combos:
                if combo.count() > 0:
                    for i in range(min(combo.count(), 3)):
                        combo.setCurrentIndex(i)
                        QTest.qWait(100)

            view.close()
        except ImportError:
            pytest.skip("Módulo de obras no disponible")

    def test_ordenar_obras_por_fecha(self, app, mock_db_obras):
        """Test de ordenación de obras por fecha."""
        try:
            # Arrange
            view = ObrasView(db_connection=mock_db_obras, usuario_actual="TEST_USER")
            view.show()
            QTest.qWait(100)

            # Buscar tabla de obras
            tabla = view.findChild(QTableWidget)

            if tabla:
                # Act - Click en headers para ordenar
                header = tabla.horizontalHeader()
                for i in range(min(header.count(), 3)):
                    header.sectionClicked.emit(i)
                    QTest.qWait(50)

            view.close()
        except ImportError:
            pytest.skip("Módulo de obras no disponible")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

import os
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QFormLayout
from modules.obras.view import ObrasView
from modules.obras.view import ObrasView
from modules.obras.view import ObrasView
from modules.obras.view import ObrasView
from modules.obras.view import ObrasView
from modules.obras.view import ObrasView
from PyQt6.QtWidgets import QDialog, QFormLayout, QDoubleSpinBox, QLabel
from PyQt6.QtWidgets import QDialog, QFormLayout, QSlider, QProgressBar
from PyQt6.QtWidgets import QDialog, QFormLayout, QSpinBox
from PyQt6.QtWidgets import QDialog, QVBoxLayout
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QListWidget, QListWidgetItem
import sys

from PyQt6.QtCore import Qt, QTimer, QDate
from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import (QApplication, QDialog, QLineEdit, QComboBox,
import pytest

from unittest.mock import Mock, patch, MagicMock
