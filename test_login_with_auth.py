#!/usr/bin/env python3
"""
Script para probar el diálogo de login con autenticación mockeada
"""
import sys
from PyQt6.QtWidgets import QApplication
from src.core.login_dialog import LoginDialog

class MockSecurityManager:
    """Mock del security manager para testing"""
    
    def login(self, username, password):
        """Simula autenticación - acepta admin/admin123"""
        if username == "admin" and password == "admin123":
            return True
        return False
    
    def get_current_role(self):
        return "Administrador"
    
    def get_current_user(self):
        return {
            "id": 1,
            "username": "admin",
            "rol": "Administrador"
        }
    
    def get_user_modules(self, user_id):
        return ["todos"]

def main():
    app = QApplication(sys.argv)
    
    # Crear y mostrar el diálogo de login
    login_dialog = LoginDialog()
    
    # Reemplazar el security manager con el mock
    login_dialog.security_manager = MockSecurityManager()
    
    # Conectar señales
    def on_login_success(username, role):
        print(f"Login exitoso: {username} ({role})")
        print("El diseño del login se ve profesional y moderno!")
        login_dialog.accept()
    
    def on_login_failed(error):
        print(f"Login fallido: {error}")
    
    login_dialog.login_successful.connect(on_login_success)
    login_dialog.login_failed.connect(on_login_failed)
    
    # Mostrar el diálogo
    result = login_dialog.exec()
    
    if result == LoginDialog.DialogCode.Accepted:
        print("Autenticación completada correctamente")
    else:
        print("Login cancelado")
    
    return result

if __name__ == "__main__":
    sys.exit(main())