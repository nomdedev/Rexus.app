#!/usr/bin/env python3
"""
Script de prueba para el sistema de login
"""

import sys
import os
from pathlib import Path

# Configurar paths
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Cargar variables de entorno
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("[OK] Variables de entorno cargadas")
    print(f"DB_SERVER: {os.getenv('DB_SERVER', 'NOT_FOUND')}")
except Exception as e:
    print(f"[ERROR] Error cargando .env: {e}")

# Probar PyQt6
try:
    from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QMessageBox
    from PyQt6.QtCore import Qt
    print("[OK] PyQt6 disponible")
except ImportError as e:
    print(f"[ERROR] PyQt6 no disponible: {e}")
    sys.exit(1)

# Probar autenticación
try:
    from src.core.auth import AuthManager
    print("[OK] AuthManager importado")
except ImportError as e:
    print(f"[ERROR] No se pudo importar AuthManager: {e}")
    sys.exit(1)

class SimpleLoginTest(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Test Login Rexus.app')
        self.setGeometry(300, 300, 400, 200)

        layout = QVBoxLayout()

        # Labels
        layout.addWidget(QLabel('Usuario:'))
        self.username_input = QLineEdit()
        self.username_input.setText('admin')
        layout.addWidget(self.username_input)

        layout.addWidget(QLabel('Contraseña:'))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setText('admin')
        layout.addWidget(self.password_input)

        # Botón
        login_btn = QPushButton('Iniciar Sesión')
        login_btn.clicked.connect(self.test_login)
        layout.addWidget(login_btn)

        # Resultado
        self.result_label = QLabel('Ingrese credenciales y haga clic en Iniciar Sesión')
        layout.addWidget(self.result_label)

        self.setLayout(layout)

    def test_login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        try:
            auth = AuthManager()
            result = auth.authenticate_user(username, password)

            if result:
                self.result_label.setText(f"[CHECK] Login exitoso: {result['username']} ({result['role']})")
                self.result_label.setStyleSheet("color: green; font-weight: bold;")

                # Mostrar datos completos en un mensaje
                details = f"""
Usuario: {result['username']}
Rol: {result['role']}
Nombre: {result['nombre_completo']}
Email: {result['email']}
ID: {result['id']}
"""
                QMessageBox.information(self, "Login Exitoso", details)

            else:
                self.result_label.setText("[ERROR] Login fallido: Credenciales incorrectas")
                self.result_label.setStyleSheet("color: red; font-weight: bold;")
                QMessageBox.warning(self, "Login Fallido", "Usuario o contraseña incorrectos")

        except Exception as e:
            error_msg = f"Error de autenticación: {str(e)}"
            self.result_label.setText(f"[ERROR] {error_msg}")
            self.result_label.setStyleSheet("color: red; font-weight: bold;")
            QMessageBox.critical(self, "Error", error_msg)

def main():
    app = QApplication(sys.argv)

    # Mostrar información del sistema
    print(f"[INFO] Python: {sys.version}")
    print(f"[INFO] Directorio actual: {os.getcwd()}")
    print(f"[INFO] Variables de entorno cargadas: {os.getenv('DB_SERVER') is not None}")

    window = SimpleLoginTest()
    window.show()

    sys.exit(app.exec())

if __name__ == '__main__':
    main()
