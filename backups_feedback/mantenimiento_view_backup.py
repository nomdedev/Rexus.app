"""
MIT License

Copyright (c) 2024 Rexus.app

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""Vista de Mantenimiento""""""

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
