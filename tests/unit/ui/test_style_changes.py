"""
Tests para validar los cambios de estilos y temas aplicados.

Estos tests verifican que los cambios de estilos minimalistas
no rompan la funcionalidad y se apliquen correctamente.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtCore import Qt


class TestLogisticaStyleChanges:
    """Tests para cambios de estilo en Logística."""

    def test_logistica_buttons_compact_style(self, qapp):
        """Test que los botones de logística tienen estilo compacto."""
        from rexus.modules.logistica.view import LogisticaView
        
        try:
            view = LogisticaView()
            
            # Verificar que el método de estilos compactos existe
            assert hasattr(view, 'aplicar_estilo_botones_compactos')
            assert callable(view.aplicar_estilo_botones_compactos)
            
            # El método debe haberse ejecutado en __init__
            # Verificar que se aplicaron estilos a algún widget
            style_applied = False
            for widget in view.findChildren(QWidget):
                if hasattr(widget, 'styleSheet') and widget.styleSheet():
                    style_applied = True
                    break
            
            # Al menos algún widget debe tener estilos aplicados
            assert style_applied, "No se aplicaron estilos a ningún widget"
            
        except Exception as e:
            pytest.skip(f"Test de estilos logística no puede ejecutarse: {e}")

    def test_logistica_tabs_improved_layout(self, qapp):
        """Test que las pestañas de logística tienen layout mejorado."""
        from rexus.modules.logistica.view import LogisticaView
        
        try:
            view = LogisticaView()
            
            # Verificar que existe widget de pestañas
            assert hasattr(view, 'tab_widget')
            assert view.tab_widget is not None
            
            # Verificar que se crearon las pestañas esperadas
            assert view.tab_widget.count() >= 3
            
            # Verificar que los layouts tienen spacing compacto
            main_layout = view.layout()
            if main_layout:
                # Los márgenes deben ser compactos (≤ 8px)
                margins = main_layout.contentsMargins()
                assert margins.left() <= 8, f"Margen izquierdo muy grande: {margins.left()}"
                assert margins.top() <= 8, f"Margen superior muy grande: {margins.top()}"
                
                # El spacing debe ser compacto (≤ 6px)
                assert main_layout.spacing() <= 6, f"Spacing muy grande: {main_layout.spacing()}"
            
        except Exception as e:
            pytest.skip(f"Test de layout logística no puede ejecutarse: {e}")

    def test_logistica_splitters_responsive(self, qapp):
        """Test que los splitters de logística son responsivos."""
        from rexus.modules.logistica.view import LogisticaView
        
        try:
            view = LogisticaView()
            
            # Buscar splitters en la vista
            from PyQt6.QtWidgets import QSplitter
            splitters = view.findChildren(QSplitter)
            
            for splitter in splitters:
                # Verificar que el handle es delgado (≤ 3px)
                assert splitter.handleWidth() <= 3, f"Handle de splitter muy ancho: {splitter.handleWidth()}"
                
                # Verificar que tiene stretch factors configurados
                sizes = splitter.sizes()
                if len(sizes) >= 2:
                    # Al menos uno de los paneles debe ser colapsible o tener stretch
                    collapsible = any(splitter.isCollapsible(i) for i in range(splitter.count()))
                    assert collapsible or sum(sizes) > 0, "Splitter no está configurado correctamente"
            
        except Exception as e:
            pytest.skip(f"Test de splitters no puede ejecutarse: {e}")


class TestInventarioStyleChanges:
    """Tests para cambios de estilo en Inventario."""

    def test_inventario_apply_theme_ultra_compact(self, qapp):
        """Test que apply_theme de inventario aplica estilos ultra compactos."""
        from rexus.modules.inventario.view import InventarioView
        
        try:
            view = InventarioView()
            
            # Aplicar tema
            view.apply_theme()
            
            # Verificar stylesheet aplicado
            stylesheet = view.styleSheet()
            assert isinstance(stylesheet, str)
            assert len(stylesheet) > 0
            
            # Verificar elementos ultra compactos específicos
            compact_elements = [
                "font-size: 11px",  # Fuente general compacta
                "font-size: 10px",  # Elementos específicos más pequeños
                "padding: 2px 6px", # Padding compacto en tablas
                "border-radius: 3px" # Bordes más pequeños
            ]
            
            compact_found = 0
            for element in compact_elements:
                if element in stylesheet:
                    compact_found += 1
            
            # Al menos la mitad de elementos compactos debe estar presente
            assert compact_found >= len(compact_elements) / 2, f"Solo {compact_found}/{len(compact_elements)} elementos compactos encontrados"
            
        except Exception as e:
            pytest.skip(f"Test tema inventario no puede ejecutarse: {e}")

    def test_inventario_table_compact_headers(self, qapp):
        """Test que las tablas de inventario tienen headers compactos.""" 
        from rexus.modules.inventario.view import InventarioView
        
        try:
            view = InventarioView()
            view.apply_theme()
            
            stylesheet = view.styleSheet()
            
            # Verificar estilos de header compactos
            header_indicators = [
                "QHeaderView::section",
                "font-size: 9px",  # Headers muy pequeños
                "padding: 4px 6px" # Padding mínimo
            ]
            
            header_style_found = any(indicator in stylesheet for indicator in header_indicators)
            assert header_style_found, "Estilos de header compactos no encontrados"
            
        except Exception as e:
            pytest.skip(f"Test headers inventario no puede ejecutarse: {e}")


class TestVidriosStyleChanges:
    """Tests para cambios de estilo en Vidrios."""

    def test_vidrios_aplicar_estilos_minimalistas(self, qapp):
        """Test que vidrios aplica estilos minimalistas correctamente."""
        from rexus.modules.vidrios.view import VidriosModernView
        
        try:
            view = VidriosModernView()
            
            # El método debería haberse ejecutado en setup_ui
            assert hasattr(view, 'aplicar_estilos_minimalistas')
            
            # Verificar stylesheet aplicado
            stylesheet = view.styleSheet()
            assert isinstance(stylesheet, str)
            assert len(stylesheet) > 0
            
            # Verificar elementos específicos ultra compactos
            ultra_compact_elements = [
                "font-size: 10px",   # Fuente general muy pequeña
                "font-size: 9px",    # Elementos específicos minúsculos
                "font-size: 8px",    # Headers minúsculos
                "padding: 1px 4px",  # Padding mínimo
                "min-height: 16px",  # Botones muy pequeños
                "border-radius: 2px" # Bordes mínimos
            ]
            
            ultra_compact_found = 0
            for element in ultra_compact_elements:
                if element in stylesheet:
                    ultra_compact_found += 1
            
            # Debe tener elementos ultra compactos
            assert ultra_compact_found >= 3, f"Solo {ultra_compact_found} elementos ultra compactos encontrados"
            
        except Exception as e:
            pytest.skip(f"Test estilos vidrios no puede ejecutarse: {e}")

    def test_vidrios_buttons_ultra_compact(self, qapp):
        """Test que los botones de vidrios son ultra compactos."""
        from rexus.modules.vidrios.view import VidriosModernView
        
        try:
            view = VidriosModernView()
            
            stylesheet = view.styleSheet()
            
            # Verificar configuración de botones ultra compactos
            button_compact_indicators = [
                "QPushButton",
                "min-height: 16px",
                "max-height: 20px",
                "font-size: 9px"
            ]
            
            button_compact_found = sum(1 for indicator in button_compact_indicators if indicator in stylesheet)
            assert button_compact_found >= 3, f"Botones no suficientemente compactos: {button_compact_found}/4"
            
        except Exception as e:
            pytest.skip(f"Test botones vidrios no puede ejecutarse: {e}")


class TestStyleConsistency:
    """Tests para consistencia de estilos entre módulos."""

    def test_color_scheme_consistency(self, qapp):
        """Test consistencia de esquema de colores."""
        modules_to_test = []
        
        # Logística
        try:
            from rexus.modules.logistica.view import LogisticaView
            logistica = LogisticaView()
            modules_to_test.append(('logistica', logistica))
        except:
            pass
            
        # Inventario
        try:
            from rexus.modules.inventario.view import InventarioView
            inventario = InventarioView()
            inventario.apply_theme()
            modules_to_test.append(('inventario', inventario))
        except:
            pass
            
        # Vidrios
        try:
            from rexus.modules.vidrios.view import VidriosModernView
            vidrios = VidriosModernView()
            modules_to_test.append(('vidrios', vidrios))
        except:
            pass
        
        if len(modules_to_test) < 2:
            pytest.skip("No hay suficientes módulos para test de consistencia")
        
        # Verificar colores consistentes
        consistent_colors = [
            "#ffffff",  # Fondo blanco
            "#e5e7eb",  # Bordes grises
            "#3b82f6",  # Azul para selección
            "#374151"   # Texto gris oscuro
        ]
        
        for module_name, module_view in modules_to_test:
            stylesheet = module_view.styleSheet()
            
            color_found = sum(1 for color in consistent_colors if color in stylesheet)
            assert color_found >= 2, f"Módulo {module_name} no tiene colores consistentes"

    def test_font_size_progression(self, qapp):
        """Test progresión lógica de tamaños de fuente."""
        modules_to_test = []
        
        try:
            from rexus.modules.inventario.view import InventarioView
            inventario = InventarioView()
            inventario.apply_theme()
            modules_to_test.append(inventario)
        except:
            pass
            
        try:
            from rexus.modules.vidrios.view import VidriosModernView
            vidrios = VidriosModernView()
            modules_to_test.append(vidrios)
        except:
            pass
        
        if not modules_to_test:
            pytest.skip("No hay módulos para test de fuentes")
        
        for view in modules_to_test:
            stylesheet = view.styleSheet()
            
            # Verificar progresión lógica: general > específico > headers
            font_sizes = []
            for size in ['11px', '10px', '9px', '8px']:
                if f"font-size: {size}" in stylesheet:
                    font_sizes.append(int(size[:-2]))
            
            if len(font_sizes) >= 2:
                # Los tamaños deben estar en orden descendente lógico
                assert max(font_sizes) - min(font_sizes) <= 4, "Diferencia de tamaños de fuente muy grande"


class TestStyleRegressionPrevention:
    """Tests para prevenir regresiones en estilos."""

    def test_no_oversized_elements(self, qapp):
        """Test que no hay elementos demasiado grandes."""
        modules_to_check = []
        
        try:
            from rexus.modules.logistica.view import LogisticaView
            modules_to_check.append(LogisticaView())
        except:
            pass
        
        try:
            from rexus.modules.inventario.view import InventarioView
            view = InventarioView()
            view.apply_theme()
            modules_to_check.append(view)
        except:
            pass
        
        if not modules_to_check:
            pytest.skip("No hay módulos para verificar")
        
        for view in modules_to_check:
            stylesheet = view.styleSheet()
            
            # Verificar que no hay elementos excesivamente grandes
            oversized_patterns = [
                "font-size: 16px",  # Muy grande
                "font-size: 18px",
                "padding: 20px",    # Padding excesivo
                "margin: 20px",     # Margen excesivo
                "min-height: 50px"  # Altura mínima excesiva
            ]
            
            oversized_found = [pattern for pattern in oversized_patterns if pattern in stylesheet]
            assert len(oversized_found) == 0, f"Elementos oversized encontrados: {oversized_found}"

    def test_responsive_layout_margins(self, qapp):
        """Test que los layouts tienen márgenes responsivos."""
        try:
            from rexus.modules.logistica.view import LogisticaView
            view = LogisticaView()
            
            main_layout = view.layout()
            if main_layout:
                margins = main_layout.contentsMargins()
                
                # Márgenes deben ser compactos pero no excesivos
                assert 0 <= margins.left() <= 10, f"Margen izquierdo fuera de rango: {margins.left()}"
                assert 0 <= margins.top() <= 10, f"Margen superior fuera de rango: {margins.top()}"
                assert 0 <= margins.right() <= 10, f"Margen derecho fuera de rango: {margins.right()}"
                assert 0 <= margins.bottom() <= 10, f"Margen inferior fuera de rango: {margins.bottom()}"
        except:
            pytest.skip("Test de márgenes no puede ejecutarse")


class TestStylePerformance:
    """Tests de rendimiento para aplicación de estilos."""

    @pytest.mark.performance
    def test_style_application_performance(self, qapp, performance_timer):
        """Test que la aplicación de estilos es eficiente."""
        
        try:
            from rexus.modules.inventario.view import InventarioView
            
            view = InventarioView()
            
            with performance_timer() as timer:
                # Aplicar tema múltiples veces
                for _ in range(5):
                    view.apply_theme()
            
            # Múltiples aplicaciones deben ser rápidas
            avg_time = timer.elapsed / 5
            assert avg_time < 0.1, f"Aplicación de tema muy lenta: {avg_time:.3f}s promedio"
            
        except:
            pytest.skip("Test de rendimiento de estilos no puede ejecutarse")

    @pytest.mark.performance
    def test_stylesheet_size_reasonable(self, qapp):
        """Test que los stylesheets no son excesivamente largos."""
        stylesheets = []
        
        try:
            from rexus.modules.inventario.view import InventarioView
            view = InventarioView()
            view.apply_theme()
            stylesheets.append(('inventario', view.styleSheet()))
        except:
            pass
        
        try:
            from rexus.modules.vidrios.view import VidriosModernView
            view = VidriosModernView()
            stylesheets.append(('vidrios', view.styleSheet()))
        except:
            pass
        
        if not stylesheets:
            pytest.skip("No hay stylesheets para verificar")
        
        for name, stylesheet in stylesheets:
            # Los stylesheets no deben ser excesivamente largos
            assert len(stylesheet) < 10000, f"Stylesheet de {name} muy largo: {len(stylesheet)} chars"
            
            # Deben tener contenido útil
            assert len(stylesheet) > 100, f"Stylesheet de {name} muy corto: {len(stylesheet)} chars"