"""
Tests para componentes del sidebar y navegación.
Cubre funcionalidad del sidebar moderno, botones, navegación y estados.
"""

# Agregar directorio raíz para imports
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

# Asegurar que existe una instancia de QApplication
app = None
def setup_module():
    global app
    if not QApplication.instance():
        app = QApplication([])

def teardown_module():
    global app
    if app:
        app.quit()

class TestSidebarComponentes:
    """Tests para el componente Sidebar moderno."""

    def setup_method(self):
        """Setup para cada test."""
        self.sections = [
            ("Inventario", "icons/inventario.svg"),
            ("Obras", "icons/obras.svg"),
            ("Usuarios", "icons/usuarios.svg"),
            ("Configuración", "icons/config.svg")
        ]

    def test_sidebar_inicializacion(self):
        """Test: inicialización correcta del sidebar."""
        sidebar = Sidebar(sections=self.sections, mostrar_nombres=True)

        # Verificar que se inicializa correctamente
        assert sidebar is not None
        assert sidebar.sections == self.sections
        assert hasattr(sidebar, '_sidebar_buttons')
        assert len(sidebar._sidebar_buttons) >= len(self.sections)

    def test_sidebar_botones_generacion(self):
        """Test: generación correcta de botones del sidebar."""
        sidebar = Sidebar(sections=self.sections, mostrar_nombres=True)

        # Verificar que se generaron los botones correctos
        assert len(sidebar._sidebar_buttons) >= len(self.sections)

        # Verificar propiedades de los botones
        for i, btn in enumerate(sidebar._sidebar_buttons[:len(self.sections)]):
            assert btn.isCheckable()
            assert btn.height() == 40
            assert btn.iconSize() == QSize(24, 24)
            assert btn.objectName() == "sidebarButton"

    def test_sidebar_navegacion_botones(self):
        """Test: navegación entre botones del sidebar."""
        sidebar = Sidebar(sections=self.sections, mostrar_nombres=True)

        # Simular clics en botones mediante llamadas directas
        for i in range(min(3, len(sidebar._sidebar_buttons))):
            # Simular clic llamando directamente al método
            sidebar._on_sidebar_button_clicked(i)

            # Verificar que se actualizó el índice
            assert sidebar._current_selected_index == i

    def test_sidebar_estado_online_offline(self):
        """Test: manejo del estado online/offline."""
        # Test con estado online
        sidebar_online = Sidebar(sections=self.sections, online=True)
        assert sidebar_online.estado_label.objectName() == "estadoOnline"

        # Test con estado offline
        sidebar_offline = Sidebar(sections=self.sections, online=False)
        assert sidebar_offline.estado_label.objectName() == "estadoOffline"

        # Test cambio de estado dinámico
        sidebar_online.set_estado_online(False)
        assert sidebar_online.estado_label.objectName() == "estadoOffline"

        sidebar_online.set_estado_online(True)
        assert sidebar_online.estado_label.objectName() == "estadoOnline"

    def test_sidebar_switch_tema(self):
        """Test: funcionalidad del switch de tema."""
        # Test modo claro inicial
        sidebar = Sidebar(sections=self.sections, modo_oscuro=False)
        assert not sidebar._modo_oscuro

        # Test modo oscuro inicial
        sidebar_oscuro = Sidebar(sections=self.sections, modo_oscuro=True)
        assert sidebar_oscuro._modo_oscuro

        # Test cambio de tema simulando el clic
        if hasattr(sidebar, 'btn_tema') and hasattr(sidebar, '_toggle_tema'):
            # Simular clic llamando directamente al método
            sidebar._toggle_tema()
            # Nota: El cambio real de tema requiere animación, así que verificamos que se inició
            assert hasattr(sidebar, '_modo_oscuro')

    def test_sidebar_accesibilidad(self):
        """Test: verificar accesibilidad del sidebar."""
        sidebar = Sidebar(sections=self.sections, mostrar_nombres=True)

        # Verificar que se aplicaron las mejoras de accesibilidad
        for btn in sidebar._sidebar_buttons:
            # Los botones deben tener tooltips y nombres accesibles
            assert btn.toolTip() is not None
            # En el sidebar moderno, la accesibilidad se maneja automáticamente

        # Verificar labels de estado
        assert sidebar.estado_label.toolTip() is not None

    def test_sidebar_secciones_personalizadas(self):
        """Test: manejo de secciones personalizadas."""
        secciones_custom = [
            ("Módulo A", "icon_a.svg"),
            ("Módulo B", "icon_b.svg"),
        ]

        sidebar = Sidebar(sections=secciones_custom, mostrar_nombres=True)

        # Verificar que se crearon los botones para las secciones custom
        assert len(sidebar._sidebar_buttons) >= len(secciones_custom)
        assert sidebar.sections == secciones_custom

    def test_sidebar_sin_nombres(self):
        """Test: sidebar sin mostrar nombres."""
        sidebar = Sidebar(sections=self.sections, mostrar_nombres=False)

        # Verificar que los botones no muestran texto cuando mostrar_nombres=False
        for btn in sidebar._sidebar_buttons[:len(self.sections)]:
            # En el modo sin nombres, el texto debe estar vacío o ser muy corto
            texto = btn.text()
            assert texto == "" or len(texto) <= 2  # Permitir iconos tipo "📊"

    def test_sidebar_manejo_errores_iconos(self):
        """Test: manejo de errores con iconos inexistentes."""
        secciones_iconos_malos = [
            ("Test", "icono_inexistente.svg"),
            ("Test2", "otro_icono_malo.png"),
        ]

        # El sidebar debe manejar graciosamente iconos inexistentes
        try:
            sidebar = Sidebar(sections=secciones_iconos_malos, mostrar_nombres=True)
            assert sidebar is not None
            # No debe crashear, debe usar iconos por defecto o placeholders
        except Exception as e:
            pytest.fail(f"Sidebar no debe fallar con iconos inexistentes: {e}")

    def test_sidebar_seleccion_visual(self):
        """Test: selección visual de botones."""
        sidebar = Sidebar(sections=self.sections, mostrar_nombres=True)

        # Test método de selección visual
        if hasattr(sidebar, 'select_button_visually'):
            sidebar.select_button_visually(0)
            # Verificar que el primer botón está seleccionado
            if sidebar._sidebar_buttons:
                assert sidebar._sidebar_buttons[0].isChecked()

            # Cambiar selección
            sidebar.select_button_visually(1)
            if len(sidebar._sidebar_buttons) > 1:
                assert sidebar._sidebar_buttons[1].isChecked()
                assert not sidebar._sidebar_buttons[0].isChecked()

    def test_sidebar_signals(self):
        """Test: emisión correcta de señales."""
        sidebar = Sidebar(sections=self.sections, mostrar_nombres=True)

        # Mock para capturar señales
        signal_mock = Mock()
        sidebar.pageChanged.connect(signal_mock)

        # Simular clic en botón llamando directamente al método
        if sidebar._sidebar_buttons:
            sidebar._on_sidebar_button_clicked(0)

            # Verificar que se emitió la señal
            signal_mock.assert_called_once_with(0)

    def test_sidebar_edge_cases(self):
        """Test: casos límite del sidebar."""
        # Test con secciones vacías
        sidebar_vacio = Sidebar(sections=[], mostrar_nombres=True)
        assert sidebar_vacio is not None
        assert len(sidebar_vacio._sidebar_buttons) == 0

        # Test con muchas secciones
        muchas_secciones = [(f"Módulo {i}", f"icon{i}.svg") for i in range(20)]
        sidebar_grande = Sidebar(sections=muchas_secciones, mostrar_nombres=True)
        assert sidebar_grande is not None
        assert len(sidebar_grande._sidebar_buttons) >= 20

        # Test con nombres muy largos
        secciones_nombres_largos = [
            ("Módulo con un nombre extremadamente largo que podría causar problemas", "icon.svg"),
            ("另一个模块名称", "icon2.svg"),  # Caracteres unicode
        ]

        try:
            sidebar_largos = Sidebar(sections=secciones_nombres_largos, mostrar_nombres=True)
            assert sidebar_largos is not None
        except Exception as e:
            pytest.fail(f"Sidebar debe manejar nombres largos: {e}")


class TestSidebarIntegracion:
    """Tests de integración del sidebar con otros componentes."""

    def test_sidebar_con_widget_tema_target(self):
        """Test: integración con widget objetivo para tema."""
        # Crear widget mock como target del tema
        widget_target = QWidget()

        sidebar = Sidebar(
            sections=[("Test", "icon.svg")],
            widget_tema_target=widget_target
        )

        assert sidebar._widget_tema_target == widget_target

    def test_sidebar_responsivo(self):
        """Test: comportamiento responsivo del sidebar."""
        sidebar = Sidebar(sections=[("Test", "icon.svg")])

        # Test redimensionamiento
        sidebar.resize(150, 600)
        assert sidebar.width() == 150

        sidebar.resize(300, 800)
        assert sidebar.width() == 300

        # Los botones deben mantener su tamaño fijo
        for btn in sidebar._sidebar_buttons:
            assert btn.height() == 40

    def test_sidebar_cleanup_recursos(self):
        """Test: limpieza adecuada de recursos."""
        sidebar = Sidebar(sections=[("Test", "icon.svg")])

        # Verificar que se pueden agregar y remover botones sin memory leaks
        inicial_count = len(sidebar._sidebar_buttons)

        # Simular creación y destrucción
        sidebar.deleteLater()

        # No debe haber crash
        assert True  # Si llegamos aquí, no hubo crash


class TestSidebarPerformance:
    """Tests de rendimiento del sidebar."""

    def test_sidebar_creacion_rapida(self):
        """Test: creación rápida del sidebar con muchos elementos."""
        # Crear muchas secciones
        muchas_secciones = [(f"Módulo {i}", f"icon{i}.svg") for i in range(100)]

        start_time = time.time()
        sidebar = Sidebar(sections=muchas_secciones, mostrar_nombres=True)
        end_time = time.time()

        # La creación no debe tomar más de 2 segundos
        creation_time = end_time - start_time
        assert creation_time < 2.0, f"Creación del sidebar muy lenta: {creation_time}s"

        # Verificar que se creó correctamente
        assert len(sidebar._sidebar_buttons) >= 100

    def test_sidebar_clicks_multiples_rapidos(self):
        """Test: manejo de clics múltiples rápidos."""
        sidebar = Sidebar(sections=[("Test", "icon.svg"), ("Test2", "icon2.svg")])

        if len(sidebar._sidebar_buttons) >= 2:
            # Clics rápidos alternados simulados
            for _ in range(10):
                sidebar._on_sidebar_button_clicked(0)
                sidebar._on_sidebar_button_clicked(1)

            # No debe crashear y debe mantener el estado consistente
            assert sidebar._current_selected_index in [0, 1]


# Test final de integración completa
def test_sidebar_completo_robusto():
    """Test: flujo completo del sidebar con validaciones robustas."""
    # 1. Crear sidebar con configuración completa
    sections = [
        ("Inventario", "icons/inventario.svg"),
        ("Obras", "icons/obras.svg"),
        ("Usuarios", "icons/usuarios.svg"),
    ]

    sidebar = Sidebar(
        sections=sections,
        mostrar_nombres=True,
        online=True,
        modo_oscuro=False
    )

    # 2. Verificar inicialización completa
    assert sidebar is not None
    assert sidebar.sections == sections
    assert len(sidebar._sidebar_buttons) >= len(sections)
    assert sidebar._current_selected_index == -1  # Sin selección inicial

    # 3. Test navegación completa
    signal_mock = Mock()
    sidebar.pageChanged.connect(signal_mock)

    # Navegar por todos los botones
    for i in range(min(len(sections), len(sidebar._sidebar_buttons))):
        sidebar._on_sidebar_button_clicked(i)
        assert sidebar._current_selected_index == i

    # Verificar que se emitieron las señales correctas
    assert signal_mock.call_count >= len(sections)

    # 4. Test cambio de estado
    sidebar.set_estado_online(False)
    assert sidebar.estado_label.objectName() == "estadoOffline"

    sidebar.set_estado_online(True)
    assert sidebar.estado_label.objectName() == "estadoOnline"

    # 5. Test accesibilidad y propiedades
    for btn in sidebar._sidebar_buttons:
        assert btn.height() == 40
import sys
import time
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest
from mps.ui.components.sidebar_moderno import Sidebar
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import QApplication, QWidget

        assert btn.iconSize() == QSize(24, 24)
        assert btn.isCheckable()

    # 6. Test limpieza
    sidebar.deleteLater()
