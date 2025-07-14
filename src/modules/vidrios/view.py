"""Vista de Vidrios"""

from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget


class VidriosView(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        title_label = QLabel("🪟 Vidrios")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(title_label)
