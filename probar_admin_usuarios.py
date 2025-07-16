#!/usr/bin/env python3
"""
Script para probar la vista de administración de usuarios
"""

import sys
import os
from PyQt6.QtWidgets import QApplication

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Función principal para probar la vista de administración"""
    app = QApplication(sys.argv)
    
    try:
        from src.modules.usuarios.view_admin import UsersAdminView
        
        # Crear y mostrar la vista
        admin_view = UsersAdminView()
        admin_view.setWindowTitle("Gestión de Usuarios - Rexus.app")
        admin_view.resize(1000, 700)
        admin_view.show()
        
        print("Vista de administración de usuarios iniciada")
        print("Funcionalidades disponibles:")
        print("- Crear nuevos usuarios")
        print("- Editar usuarios existentes")
        print("- Asignar roles y permisos")
        print("- Ver estadísticas de usuarios")
        print("- Filtrar y buscar usuarios")
        
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"Error iniciando vista: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()