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

Diálogo de Configuración de Seguridad Avanzada
Interfaz para 2FA, cambio de contraseñas y configuraciones de seguridad
"""


import logging
logger = logging.getLogger(__name__)

import base64
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                success = self.security_manager.disable_2fa(self.current_username)

                if success:
                    QMessageBox.information(self, "2FA Deshabilitado", "Two-Factor Authentication deshabilitado")
                    self.security_updated.emit(self.current_username, "2FA_DISABLED")
                    self.load_user_security_status()
                else:
                    QMessageBox.warning(self, "Error", "Error deshabilitando 2FA")

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error deshabilitando 2FA: {e}")

    def unlock_account(self):
        """Desbloquea la cuenta del usuario."""
        reply = QMessageBox.question(
            self,
            "Confirmar",
            "¿Desbloquear cuenta manualmente?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                success = self.security_manager.unlock_user(self.current_username)

                if success:
                    QMessageBox.information(self, "Cuenta Desbloqueada", "Cuenta desbloqueada exitosamente")
                    self.security_updated.emit(self.current_username, "ACCOUNT_UNLOCKED")
                    self.load_user_security_status()
                else:
                    QMessageBox.warning(self, "Error", "Error desbloqueando cuenta")

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error desbloqueando cuenta: {e}")

    def save_changes(self):
        """Guarda los cambios de configuración."""
        try:
            changes_made = False

            # Cambio de contraseña
            if self.new_password.text():
                if not self.current_password.text():
                    QMessageBox.warning(self, "Error", "Ingrese su contraseña actual")
                    return

                if self.new_password.text() != self.confirm_password.text():
                    QMessageBox.warning(self, "Error", "Las contraseñas no coinciden")
                    return

                # Validar contraseña actual
                if not self.usuarios_model.validar_usuario(self.current_username, self.current_password.text()):
                    QMessageBox.warning(self, "Error", "Contraseña actual incorrecta")
                    return

                # Validar fortaleza de nueva contraseña
                result = self.security_manager.validate_password_strength(self.new_password.text())
                if not result['valid']:
                    QMessageBox.warning(
                        self,
                        "Contraseña Débil",
                        "La contraseña no cumple los requisitos de seguridad:\n• " + "\n• ".join(result['issues'])
                    )
                    return

                # Cambiar contraseña
                if hasattr(self.usuarios_model, 'cambiar_password'):
                    success = self.usuarios_model.cambiar_password(self.current_username, self.new_password.text())
                    if success:
                        changes_made = True
                        self.security_updated.emit(self.current_username, "PASSWORD_CHANGED")
                    else:
                        QMessageBox.warning(self, "Error", "Error cambiando contraseña")
                        return

            if changes_made:
                QMessageBox.information(self, "Éxito", "Configuración de seguridad actualizada")

            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error guardando cambios: {e}")


def show_security_config(usuarios_model, username: str, parent=None) -> bool:
    """
    Muestra el diálogo de configuración de seguridad.

    Returns:
        bool: True si se realizaron cambios
    """
    dialog = SecurityConfigDialog(usuarios_model, username, parent)
    return dialog.exec() == QDialog.DialogCode.Accepted


if __name__ == "__main__":
    # Test del diálogo
    import sys
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    # Mock del modelo de usuarios para testing
    class MockUsuariosModel:
        def obtener_usuario_por_nombre(self, username):
            return {
                'id': 1,
                'username': username,
                'configuracion_personal': '{}',
                'ultimo_login': '2025-01-01 10:00:00',
                'fecha_creacion': '2024-12-01'
            }

        def obtener_todos_usuarios(self):
            return [{'id': 1, 'username': 'admin'}]

    dialog = SecurityConfigDialog(MockUsuariosModel(), )
    dialog.show()

    sys.exit(app.exec())