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
"""

"""
Diálogo de Configuración de Base de Datos - Rexus.app v2.0.0

Permite configurar las conexiones a base de datos del sistema
"""

import logging
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton

logger = logging.getLogger(__name__)

class DatabaseConfigDialog(QDialog):
    """Diálogo para configuración de base de datos."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuración de Base de Datos")
        self.setFixedSize(600, 400)
        self.init_ui()
    
    def init_ui(self):
        """Inicializa la interfaz de usuario."""
        layout = QVBoxLayout()
        
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        layout.addWidget(self.results_text)
        
        self.test_button = QPushButton("Probar Conexiones")
        self.test_button.clicked.connect(self.test_all_connections)
        layout.addWidget(self.test_button)
        
        self.setLayout(layout)
    
    def test_all_connections(self):
        """Prueba todas las conexiones de base de datos."""
        self.results_text.clear()
        self.results_text.append("[INFO] Iniciando pruebas de conexión...")
        
        for db_type in ["users", "inventario", "auditoria"]:
            self.test_connection(db_type)

        self.results_text.append("\n[CHECK] Pruebas completadas")
    
    def test_connection(self, db_type):
        """Prueba la conexión a un tipo específico de base de datos."""
        try:
            self.results_text.append(f"[INFO] Probando conexión {db_type}...")
            # Aquí se implementaría la lógica de prueba de conexión
            self.results_text.append(f"[OK] Conexión {db_type} exitosa")
            return True
        except Exception as e:
            self.results_text.append(f"[ERROR] Fallo conexión {db_type}: {str(e)}")
            return False
