"""
Tests básicos para verificar la estructura del proyecto
"""

import sys
from pathlib import Path

import pytest

# Añadir src al path para imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class TestProjectStructure:
    """Tests para verificar que la estructura del proyecto es correcta"""

    def test_main_directories_exist(self):
        """Verifica que existan los directorios principales"""
        project_root = Path(__file__).parent.parent

        expected_dirs = [
            "src",
            "src/main",
            "src/core",
            "src/ui",
            "src/modules",
            "src/utils",
            "src/widgets",
            "tests",
            "scripts",
            "docs",
            "config",
        ]

        for dir_path in expected_dirs:
            assert (
                project_root / dir_path
            ).exists(), f"Directorio {dir_path} no existe"

    def test_main_files_exist(self):
        """Verifica que existan los archivos principales"""
        project_root = Path(__file__).parent.parent

        expected_files = [
            "src/main/app.py",
            "src/core/config.py",
            "src/ui/styles.py",
            "requirements.txt",
            "README.md",
        ]

        for file_path in expected_files:
            assert (project_root / file_path).exists(), f"Archivo {file_path} no existe"

    def test_imports_work(self):
        """Verifica que los imports principales funcionen"""
        try:
            from src.core.config import APP_CONFIG, UI_CONFIG
            from src.ui.styles import get_base_styles

            assert APP_CONFIG is not None
            assert UI_CONFIG is not None
            assert callable(get_base_styles)

        except ImportError as e:
            pytest.fail(f"Error en imports: {e}")


class TestConfiguration:
    """Tests para verificar la configuración"""

    def test_config_values(self):
        """Verifica que la configuración tenga valores válidos"""
        from src.core.config import APP_CONFIG, UI_CONFIG

        # Verificar APP_CONFIG
        assert "name" in APP_CONFIG
        assert "version" in APP_CONFIG
        assert APP_CONFIG["name"] == "Stock.app"

        # Verificar UI_CONFIG
        assert "colors" in UI_CONFIG
        assert "typography" in UI_CONFIG
        assert "button" in UI_CONFIG

    def test_styles_generation(self):
        """Verifica que se puedan generar estilos CSS"""
        from src.ui.styles import get_base_styles

        styles = get_base_styles()
        assert isinstance(styles, str)
        assert "QWidget" in styles
        assert "QPushButton" in styles
