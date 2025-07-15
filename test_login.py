#!/usr/bin/env python3
"""
Script simple para probar el diálogo de login mejorado
"""
import sys
from PyQt6.QtWidgets import QApplication
from src.core.login_dialog import LoginDialog

def main():
    app = QApplication(sys.argv)
    
    # Crear y mostrar el diálogo de login
    login_dialog = LoginDialog()
    
    # Conectar señales básicas para testing
    def on_login_success(username, role):
        print(f"Login exitoso: {username} ({role})")
        login_dialog.accept()
    
    def on_login_failed(error):
        print(f"Login fallido: {error}")
    
    login_dialog.login_successful.connect(on_login_success)
    login_dialog.login_failed.connect(on_login_failed)
    
    # Mostrar el diálogo
    result = login_dialog.exec()
    
    if result == LoginDialog.DialogCode.Accepted:
        print("Diálogo aceptado")
    else:
        print("Diálogo cancelado")
    
    return result

if __name__ == "__main__":
    sys.exit(main())