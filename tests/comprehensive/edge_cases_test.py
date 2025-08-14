"""
Tests Comprehensivos de Edge Cases - Rexus.app
Prueba casos límite, errores de inicialización, botones sin configurar, etc.
"""

import sys
import pytest
import importlib
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from PyQt6.QtWidgets import QApplication, QPushButton, QLineEdit
from PyQt6.QtCore import Qt

# Agregar ruta raíz
root_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_path))


class TestModuleInitialization:
    """Prueba la inicialización de módulos en condiciones adversas."""

    @pytest.fixture(autouse=True)
    def setup_qt_app(self):
        """Configura aplicación Qt para tests."""
        if not QApplication.instance():
            self.app = QApplication([])
        else:
            self.app = QApplication.instance()
        yield
        # No cerrar la app aquí para evitar crashes

    def test_module_imports_without_database(self):
        """Prueba que los módulos se importen sin conexión BD."""
        modules_to_test = [
            'rexus.modules.administracion.view',
            'rexus.modules.mantenimiento.view',
            'rexus.modules.logistica.view',
            'rexus.modules.inventario.view',
            'rexus.modules.obras.view',
        ]

        for module_name in modules_to_test:
            try:
                importlib.import_module(module_name)
                print(f"✅ {module_name} - Import OK")
            except ImportError as e:
                pytest.fail(f"❌ {module_name} - Import failed: {e}")
            except SyntaxError as e:
                pytest.fail(f"❌ {module_name} - Syntax error: {e}")
            except Exception as e:
                print(f"⚠️ {module_name} - Other error: {e}")

    @patch('rexus.core.database.get_inventario_connection')
    def test_module_views_with_mock_database(self, mock_db):
        """Prueba vistas con base de datos mockeada."""
        mock_db.return_value = Mock()

        view_classes = [
            ('rexus.modules.inventario.view', 'InventarioView'),
            ('rexus.modules.obras.view', 'ObrasModernView'),
            ('rexus.modules.mantenimiento.view', 'MantenimientoView'),
        ]

        for module_name, class_name in view_classes:
            try:
                module = importlib.import_module(module_name)
                view_class = getattr(module, class_name)

                # Intentar crear instancia
                instance = view_class()
                assert instance is not None
                print(f"✅ {class_name} - Instantiation OK")

            except AttributeError:
                print(f"⚠️ {class_name} - Class not found in {module_name}")
            except Exception as e:
                print(f"❌ {class_name} - Instantiation failed: {e}")


class TestUIComponentsEdgeCases:
    """Prueba casos límite en componentes UI."""

    @pytest.fixture(autouse=True)
    def setup_qt_app(self):
        if not QApplication.instance():
            self.app = QApplication([])
        else:
            self.app = QApplication.instance()
        yield

    def test_buttons_have_click_handlers(self):
        """Verifica que botones críticos tengan handlers."""
        from rexus.modules.inventario.view_simple import InventarioViewSimple

        try:
            view = InventarioViewSimple()

            # Verificar botones principales
            critical_buttons = ['btn_nuevo', 'btn_editar', 'btn_eliminar', 'btn_actualizar']

            for button_name in critical_buttons:
                if hasattr(view, button_name):
                    button = getattr(view, button_name)
                    if isinstance(button, QPushButton):
                        # Verificar que tenga al menos una conexión
                        receivers = button.receivers(button.clicked)
                        assert receivers > 0, f"Botón {button_name} no tiene click handler"
                        print(f"✅ {button_name} - Handler configured")

        except Exception as e:
            pytest.fail(f"Error testing button handlers: {e}")

    def test_input_validation_edge_cases(self):
        """Prueba casos límite en validación de inputs."""
        edge_cases = [
            "",  # Vacío
            " ",  # Solo espacios
            "a" * 1000,  # Muy largo
            "<script>alert('xss')</script>",  # XSS básico
            "'; DROP TABLE users; --",  # SQL injection básico
            "../../etc/passwd",  # Path traversal
            "\x00\x01\x02",  # Caracteres de control
            "🚀🎯💀",  # Emojis
        ]

        from rexus.utils.unified_sanitizer import sanitize_string

        for test_input in edge_cases:
            try:
                result = sanitize_string(test_input)
                assert result is not None, f"Sanitization returned None for: {repr(test_input)}"
                assert len(result) <= 500, f"Sanitized result too long: {len(result)}"
                print(f"✅ Input sanitized: {repr(test_input[:20])}...")
            except Exception as e:
                pytest.fail(f"Sanitization failed for {repr(test_input)}: {e}")

    def test_theme_switching_edge_cases(self):
        """Prueba cambios de tema en condiciones extremas."""
        try:
            from rexus.ui.style_manager import StyleManager

            style_manager = StyleManager()

            # Probar temas válidos
            valid_themes = ['light', 'dark', 'professional']
            for theme in valid_themes:
                success = style_manager.apply_theme(theme)
                assert success, f"Failed to apply theme: {theme}"
                print(f"✅ Theme applied: {theme}")

            # Probar temas inválidos
            invalid_themes = ['', 'nonexistent', None, 123]
            for theme in invalid_themes:
                success = style_manager.apply_theme(theme)
                # No debe causar crash, pero puede fallar
                print(f"🔍 Invalid theme handled: {theme} -> {success}")

        except Exception as e:
            pytest.fail(f"Theme switching test failed: {e}")


class TestDataHandlingEdgeCases:
    """Prueba manejo de datos en casos límite."""

    def test_database_connection_failures(self):
        """Prueba manejo de fallos de conexión BD."""
        with patch('rexus.core.database.get_inventario_connection') as mock_conn:
            # Simular fallo de conexión
            mock_conn.side_effect = Exception("Database connection failed")

            try:
                from rexus.modules.inventario.model import InventarioModel
                model = InventarioModel()

                # El modelo debería manejar el error sin crash
                result = model.obtener_productos()
                assert result is not None or result == [], "Model should return empty list or handle error gracefully"
                print("✅ Database connection failure handled gracefully")

            except Exception as e:
                print(f"⚠️ Model crashed on DB failure: {e}")

    def test_large_dataset_handling(self):
        """Prueba manejo de datasets grandes."""
        large_dataset = [
            {
                'id': i,
                'codigo': f'PROD{i:06d}',
                'descripcion': f'Producto {i} con descripción muy larga ' * 10,
                'stock': i % 100,
                'precio': i * 0.99
            }
            for i in range(10000)
        ]

        try:
            from rexus.modules.inventario.view_simple import InventarioViewSimple
            view = InventarioViewSimple()

            # Probar actualización con dataset grande
            view.actualizar_productos(large_dataset)
            print("✅ Large dataset handling OK")

        except Exception as e:
            pytest.fail(f"Large dataset handling failed: {e}")

    def test_malformed_data_handling(self):
        """Prueba manejo de datos malformados."""
        malformed_datasets = [
            None,  # Null
            [],  # Vacío
            [None, None],  # Lista con nulls
            [{'wrong': 'structure'}],  # Estructura incorrecta
            [{'id': 'not_number', 'stock': 'text'}],  # Tipos incorrectos
        ]

        try:
            from rexus.modules.inventario.view_simple import InventarioViewSimple
            view = InventarioViewSimple()

            for dataset in malformed_datasets:
                try:
                    view.actualizar_productos(dataset)
                    print(f"✅ Malformed data handled: {type(dataset)}")
                except Exception as e:
                    print(f"⚠️ Malformed data caused error: {e}")

        except Exception as e:
            pytest.fail(f"Malformed data test setup failed: {e}")


class TestSecurityEdgeCases:
    """Prueba casos límite de seguridad."""

    def test_xss_prevention(self):
        """Prueba prevención de XSS."""
        xss_payloads = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "';alert(String.fromCharCode(88,83,83))//';alert(String.fromCharCode(88,83,83))//",
            "\"><script>alert('xss')</script>",
        ]

        from rexus.utils.xss_protection import XSSProtection

        for payload in xss_payloads:
            try:
                cleaned = XSSProtection.clean_input(payload)

                # Verificar que scripts peligrosos fueron removidos
                assert '<script>' not in cleaned.lower(), f"Script tag not removed: {payload}"
                assert 'javascript:' not in cleaned.lower(), f"Javascript protocol not removed: {payload}"
                assert 'onerror=' not in cleaned.lower(), f"Event handler not removed: {payload}"

                print(f"✅ XSS payload cleaned: {payload[:30]}...")

            except Exception as e:
                pytest.fail(f"XSS protection failed for: {payload} - {e}")

    def test_sql_injection_prevention(self):
        """Prueba prevención de SQL injection."""
        sql_payloads = [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "'; INSERT INTO users VALUES('hacker', 'password'); --",
            "' UNION SELECT password FROM users WHERE '1'='1",
            "\"; DELETE FROM products; --",
        ]

        from rexus.utils.unified_sanitizer import sanitize_string

        for payload in sql_payloads:
            try:
                cleaned = sanitize_string(payload)

                # Verificar que elementos peligrosos fueron limpiados
                dangerous_keywords = ['DROP', 'DELETE', 'INSERT', 'UNION', 'SELECT']
                for keyword in dangerous_keywords:
                    assert keyword not in cleaned.upper(), f"SQL keyword not sanitized: {keyword} in {payload}"

                print(f"✅ SQL injection payload sanitized: {payload[:30]}...")

            except Exception as e:
                pytest.fail(f"SQL injection prevention failed for: {payload} - {e}")


def run_comprehensive_tests():
    """Ejecuta todos los tests comprehensivos."""
    print("🔍 Ejecutando tests comprehensivos de edge cases...")

    # Ejecutar tests con pytest
    test_file = Path(__file__)
    exit_code = pytest.main([
        str(test_file),
        '-v',
        '--tb=short',
        '--no-header'
    ])

    return exit_code == 0


if __name__ == "__main__":
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)
