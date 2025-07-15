#!/usr/bin/env python3
"""
Script para probar la aplicación completa con mock de base de datos
"""
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from src.core.login_dialog import LoginDialog

class MockSecurityManager:
    """Mock del security manager para testing sin base de datos"""
    
    def login(self, username, password):
        """Simula autenticación - acepta admin/admin123"""
        if username == "admin" and password == "admin123":
            return True
        return False
    
    def get_current_role(self):
        return "ADMIN"
    
    def get_current_user(self):
        return {
            "id": 1,
            "username": "admin",
            "rol": "ADMIN"
        }
    
    def get_user_modules(self, user_id):
        return ["inventario", "contabilidad", "obras", "administracion"]

class SimpleMainWindow(QMainWindow):
    """Ventana principal simple para testing"""
    
    def __init__(self, user_data, modulos_permitidos):
        super().__init__()
        self.setWindowTitle("Rexus.app - Sistema de Gestión")
        self.setGeometry(100, 100, 1200, 800)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout
        layout = QVBoxLayout(central_widget)
        
        # Contenido de bienvenida
        welcome_label = QLabel(f"""
        🎉 ¡Bienvenido a Rexus.app!
        
        Usuario: {user_data.get('username', 'N/A')}
        Rol: {user_data.get('rol', 'N/A')}
        
        Módulos disponibles:
        {chr(10).join(['• ' + modulo for modulo in modulos_permitidos])}
        
        🔧 El sistema de login está funcionando correctamente.
        ✅ El diseño visual del login se ve profesional.
        🏗️ La aplicación principal está lista para desarrollo.
        """)
        
        welcome_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                padding: 40px;
                background-color: #f8f9fa;
                border-radius: 12px;
                color: #2c3e50;
                line-height: 1.5;
            }
        """)
        
        layout.addWidget(welcome_label)
        
    def actualizar_usuario_label(self, user_data):
        """Compatibilidad con el sistema original"""
        pass
        
    def mostrar_mensaje(self, mensaje, tipo="info", duracion=2000):
        """Compatibilidad con el sistema original"""
        print(f"Mensaje ({tipo}): {mensaje}")

def main():
    app = QApplication(sys.argv)
    
    # Crear dialog de login
    login_dialog = LoginDialog()
    
    # Reemplazar el security manager con el mock
    login_dialog.security_manager = MockSecurityManager()
    
    def on_login_success(username, role):
        print(f"✅ Login exitoso: {username} ({role})")
        
        # Simular datos del usuario y módulos
        user_data = {
            "id": 1,
            "username": username,
            "rol": role
        }
        
        modulos_permitidos = ["inventario", "contabilidad", "obras", "administracion"]
        
        # Crear ventana principal
        main_window = SimpleMainWindow(user_data, modulos_permitidos)
        main_window.show()
        
        # Cerrar dialog de login
        login_dialog.accept()
    
    def on_login_failed(error):
        print(f"❌ Login fallido: {error}")
    
    # Conectar señales
    login_dialog.login_successful.connect(on_login_success)
    login_dialog.login_failed.connect(on_login_failed)
    
    # Mostrar login
    if login_dialog.exec() == LoginDialog.DialogCode.Accepted:
        return app.exec()
    else:
        return 0

if __name__ == "__main__":
    sys.exit(main())