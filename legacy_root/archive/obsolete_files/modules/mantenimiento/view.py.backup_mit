"""Vista de Mantenimiento"""

from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

class MantenimientoView(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # Intentar cargar la vista completa primero
        try:
            from .view_completa import MantenimientoCompletaView
            completa_view = MantenimientoCompletaView()
            
            # Crear un layout para contener la vista completa
            layout = QVBoxLayout(self)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.addWidget(completa_view)
            
        except Exception as e:
            # Fallback a vista simple si hay problemas
            layout = QVBoxLayout(self)
            title_label = QLabel("🔧 Mantenimiento")
            title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
            layout.addWidget(title_label)
            
            error_label = QLabel("Vista completa no disponible. Usando vista básica.")
            error_label.setStyleSheet("color: #e74c3c; font-style: italic;")
            layout.addWidget(error_label)
            
            print(f"Error cargando vista completa de mantenimiento: {e}")
