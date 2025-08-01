# TEST THEME_MANAGER: carga correcta de QSS por tema
@pytest.mark.parametrize("theme_name,selector", [
    ("light", "QWidget {"),
from PyQt6.QtWidgets import QApplication
import pytest

from utils.theme_manager import set_theme
    ("dark", "QWidget {"),
])
def test_set_theme_aplica_qss(tmp_path, theme_name, selector):
    app = QApplication.instance() or QApplication([])
    set_theme(app, theme_name)
    qss = app.styleSheet()
    assert selector in qss
    assert ("background" in qss or "color" in qss)
