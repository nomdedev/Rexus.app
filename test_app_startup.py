
import sys
import os
from pathlib import Path

# Add project root to path
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

def test_app_startup():
    try:
        from PyQt6.QtWidgets import QApplication
        from rexus.main.app import MainWindow
        
        app = QApplication([])
        
        # Simular usuario admin
        user_data = {
            'username': 'admin',
            'rol': 'ADMIN', 
            'id': 1,
            'activo': True
        }
        
        modules = ['Inventario', 'Obras', 'Pedidos']
        
        main_window = MainWindow(user_data, modules)
        
        print("✅ Aplicación iniciada correctamente")
        print(f"🔍 Módulos cargados: {len(modules)}")
        
        # No mostrar ventana, solo test de inicialización
        app.quit()
        return True
        
    except Exception as e:
        print(f"❌ Error iniciando aplicación: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_app_startup()
    sys.exit(0 if success else 1)
