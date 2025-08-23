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
Diálogo de Login - Rexus.app v2.0.0

Sistema de autenticación con interfaz minimalista y profesional
"""


import logging
logger = logging.getLogger(__name__)

import os
import sys

                            self.show_error(error_msg)
                self.login_failed.emit(error_msg)
                self.password_edit.clear()
                self.password_edit.setFocus()

        except Exception as e:
            error_msg = f"Error de autenticación: {str(e)}"
            self.show_error(error_msg)
            self.login_failed.emit(error_msg)

        finally:
            # Rehabilitar botón
            self.login_button.setEnabled(True)
            self.login_button.setText("Iniciar Sesión")

    def show_error(self, message):
        """Muestra un mensaje de error minimalista."""
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setWindowTitle("Error")
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: white;
                border: 1px solid #ddd;
            }
            QMessageBox QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 4px;
                font-weight: 500;
                min-width: 80px;
            }
            QMessageBox QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        msg_box.exec()

    def keyPressEvent(self, event):
        """Maneja eventos de teclado."""
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
        else:
            super().keyPressEvent(event)

    def check_dev_auto_login(self):
        """
        Verifica si debe hacer auto-login en modo desarrollo.
        Se ejecuta automáticamente después de inicializar la UI.
        """
        try:
            # Verificar si está habilitado el auto-login de desarrollo
            auto_login_enabled = os.getenv('REXUS_DEV_AUTO_LOGIN', 'false').lower() == 'true'
            dev_user = os.getenv('REXUS_DEV_USER', '')
            dev_password = os.getenv('REXUS_DEV_PASSWORD', '')

            # Verificar modo desarrollo
            is_dev_mode = (
                '--dev' in sys.argv or
                os.getenv('REXUS_ENV') == 'development' or
                os.getenv('HOTRELOAD_ENABLED', '').lower() == 'true'
            )

            if is_dev_mode and auto_login_enabled and dev_user and dev_password:
                logger.info(f"[DEV] Auto-login habilitado - Usuario: {dev_user}")

                # Pre-llenar campos
                if hasattr(self, 'username_edit'):
                    self.username_edit.setText(dev_user)
                if hasattr(self, 'password_edit'):
                    self.password_edit.setText(dev_password)

                # Ejecutar login automáticamente después de mostrar el diálogo
                from PyQt6.QtCore import QTimer
                QTimer.singleShot(500, self.auto_login_dev)

        except Exception as e:
            logger.info(f)

    def auto_login_dev(self):
        """Ejecuta el login automático para desarrollo."""
        try:
            logger.info("[DEV] Ejecutando auto-login...")
            self.handle_login()
        except Exception as e:
            logger.info(f"[DEV] Error en auto-login: {e}")
