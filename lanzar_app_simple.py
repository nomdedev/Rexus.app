#!/usr/bin/env python3
"""
Script simple para lanzar la aplicación sin problemas de conexión
"""

import sys
import os

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Función principal simplificada"""
    print("INICIANDO REXUS.APP v2.0.0")
    print("=" * 50)
    
    try:
        from PyQt6.QtWidgets import QApplication
        
        app = QApplication(sys.argv)
        
        # Importar y mostrar login
        from src.core.login_dialog import LoginDialog
        
        login_dialog = LoginDialog()
        
        def on_login_success(username, role):
            print(f"[OK] Login exitoso: {username} ({role})")
            
            # Cerrar login y abrir aplicación principal
            login_dialog.close()
            
            # Importar la aplicación principal
            from src.main.app import MainWindow
            
            # Crear datos básicos del usuario
            user_data = {
                'username': username,
                'rol': role,
                'id': 1
            }
            
            # Módulos permitidos según el rol
            if role == 'admin':
                modulos_permitidos = ['inventario', 'obras', 'usuarios', 'configuracion', 'contabilidad', 'logistica', 'mantenimiento']
            elif role == 'supervisor':
                modulos_permitidos = ['inventario', 'obras', 'contabilidad', 'logistica']
            else:
                modulos_permitidos = ['inventario', 'obras']
            
            # Crear y mostrar ventana principal
            main_window = MainWindow(user_data, modulos_permitidos)
            main_window.show()
        
        def on_login_failed(error_message):
            print(f"[ERROR] Login fallido: {error_message}")
        
        # Conectar señales
        login_dialog.login_successful.connect(on_login_success)
        login_dialog.login_failed.connect(on_login_failed)
        
        # Mostrar login
        login_dialog.show()
        
        # Ejecutar aplicación
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"[ERROR] Error general: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    main()