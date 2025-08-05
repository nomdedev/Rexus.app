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

Vista de Mantenimiento
"""

# 🔒 XSS Protection Added - Validate all user inputs
# Use SecurityUtils.sanitize_input() for text fields
# Use SecurityUtils.validate_email() for email fields
# XSS Protection Added

import logging

from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

from rexus.utils.data_sanitizer import DataSanitizer
from rexus.utils.security import SecurityUtils


class MantenimientoView(QWidget):
    """
    Vista principal para la gestión de mantenimientos.
    Permite mostrar el estado, feedback visual y cargar la vista completa.
    """

    def __init__(self):
        super().__init__()
        self.label_feedback = None
        self._feedback_timer = None
        self.logger = logging.getLogger(__name__)
        self.init_ui()

    def init_ui(self):
        # Intentar cargar la vista completa primero
        try:
            self.logger.info("Iniciando carga de vista completa de mantenimiento")
            from .view_completa import MantenimientoCompletaView

            completa_view = MantenimientoCompletaView()

            # Crear un layout para contener la vista completa
            layout = QVBoxLayout(self)
            layout.setContentsMargins(0, 0, 0, 0)

            # Agregar label de feedback
            self.label_feedback = QLabel("")
            self.label_feedback.setObjectName("label_feedback")
            self.label_feedback.setVisible(False)
            self.label_feedback.setAccessibleName("Mensaje de feedback")
            self.label_feedback.setAccessibleDescription(
                "Mensajes de estado y feedback para el usuario"
            )
            self.label_feedback.setStyleSheet("""
                QLabel[feedback="info"] { 
                    color: #2980b9; background: #e8f4fd; 
                    border: 1px solid #2980b9; border-radius: 4px; 
                    padding: 8px; margin: 4px; font-weight: bold; 
                }
                QLabel[feedback="exito"] { 
                    color: #27ae60; background: #edfcf1; 
                    border: 1px solid #27ae60; border-radius: 4px; 
                    padding: 8px; margin: 4px; font-weight: bold; 
                }
                QLabel[feedback="advertencia"] { 
                    color: #f39c12; background: #fef9e7; 
                    border: 1px solid #f39c12; border-radius: 4px; 
                    padding: 8px; margin: 4px; font-weight: bold; 
                }
                QLabel[feedback="error"] { 
                    color: #e74c3c; background: #fdeaea; 
                    border: 1px solid #e74c3c; border-radius: 4px; 
                    padding: 8px; margin: 4px; font-weight: bold; 
                }
                QLabel[feedback="cargando"] { 
                    color: #8e44ad; background: #f4ecf7; 
                    border: 1px solid #8e44ad; border-radius: 4px; 
                    padding: 8px; margin: 4px; font-weight: bold; 
                }
            """)
            layout.addWidget(self.label_feedback)
            layout.addWidget(completa_view)

            self.logger.info("Vista completa de mantenimiento cargada exitosamente")

        except Exception as e:
            self.logger.error(
                f"Error cargando vista completa de mantenimiento: {str(e)}"
            )
            # Fallback a vista simple si hay problemas
            layout = QVBoxLayout(self)

            # Agregar label de feedback también al fallback
            self.label_feedback = QLabel("")
            self.label_feedback.setObjectName("label_feedback")
            self.label_feedback.setVisible(False)
            layout.addWidget(self.label_feedback)

            title_label = QLabel("🔧 Mantenimiento")
            title_label.setStyleSheet(
                "font-size: 24px; font-weight: bold; color: #2c3e50;"
            )
            layout.addWidget(title_label)

            error_label = QLabel("Vista completa no disponible. Usando vista básica.")
            error_label.setStyleSheet("color: #e74c3c; font-style: italic;")
            layout.addWidget(error_label)

            print(f"Error cargando vista completa de mantenimiento: {e}")

    def mostrar_mensaje(self, mensaje: str, tipo: str = "info"):
        """Muestra un mensaje de feedback visual al usuario.

        Args:
            mensaje: El mensaje a mostrar
            tipo: Tipo de mensaje ('info', 'exito', 'advertencia', 'error', 'cargando')
        """
        try:
            self.logger.info(
                f"Mostrando mensaje de feedback - Tipo: {tipo}, Mensaje: {mensaje}"
            )

            if not hasattr(self, "label_feedback") or self.label_feedback is None:
                self.logger.warning("Label de feedback no disponible")
                return

            # Sanitizar mensaje de entrada
            mensaje_limpio = (
                DataSanitizer.sanitize_text(mensaje)
                if hasattr(DataSanitizer, "sanitize_text")
                else mensaje
            )

            iconos = {
                "info": "ℹ️ ",
                "exito": "✅ ",
                "advertencia": "⚠️ ",
                "error": "❌ ",
                "cargando": "🔄 ",
            }
            icono = iconos.get(tipo, "ℹ️ ")

            self.label_feedback.clear()
            self.label_feedback.setProperty("feedback", tipo)
            self.label_feedback.setText(f"{icono}{mensaje_limpio}")
            self.label_feedback.setVisible(True)
            self.label_feedback.setAccessibleDescription(
                f"Mensaje de feedback tipo {tipo}"
            )

            # Auto-ocultar después de tiempo apropiado
            tiempo = (
                6000 if tipo == "error" else 4000 if tipo == "advertencia" else 3000
            )

            try:
                from PyQt6.QtCore import QTimer

                if hasattr(self, "_feedback_timer") and self._feedback_timer:
                    self._feedback_timer.stop()
                self._feedback_timer = QTimer(self)
                self._feedback_timer.setSingleShot(True)
                self._feedback_timer.timeout.connect(self.ocultar_feedback)
                self._feedback_timer.start(tiempo)
            except ImportError:
                self.logger.warning("QTimer no disponible para auto-ocultar feedback")
                pass

        except Exception as e:
            self.logger.error(f"Error al mostrar mensaje de feedback: {str(e)}")

    def ocultar_feedback(self):
        """Oculta el feedback visual."""
        try:
            self.logger.debug("Ocultando feedback visual")

            if hasattr(self, "label_feedback") and self.label_feedback:
                self.label_feedback.setVisible(False)
                self.label_feedback.clear()
            if hasattr(self, "_feedback_timer") and self._feedback_timer:
                self._feedback_timer.stop()

        except Exception as e:
            self.logger.error(f"Error al ocultar feedback: {str(e)}")
