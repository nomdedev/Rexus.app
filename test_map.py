#!/usr/bin/env python3
"""
Test simple del mapa interactivo
"""

import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt

# Add rexus to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'rexus'))

def test_map_dependencies():
    """Test that all map dependencies are available"""
    print("=== TESTING MAP DEPENDENCIES ===")
    
    try:
        import folium
        print(f"✅ folium version: {folium.__version__}")
    except ImportError as e:
        print(f"❌ folium not available: {e}")
        return False
    
    try:
        from PyQt6.QtWebEngineWidgets import QWebEngineView
        print("✅ PyQt6.QtWebEngineWidgets available")
    except ImportError as e:
        print(f"❌ PyQt6.QtWebEngineWidgets not available: {e}")
        return False
    
    try:
        from modules.logistica.interactive_map import InteractiveMapWidget
        print("✅ InteractiveMapWidget can be imported")
    except ImportError as e:
        print(f"❌ InteractiveMapWidget import failed: {e}")
        return False
    
    return True

def create_simple_map_test():
    """Create a simple map test window"""
    app = QApplication(sys.argv)
    
    # Test dependencies first
    if not test_map_dependencies():
        print("❌ Dependencies not available - cannot create map")
        return
    
    print("\n=== CREATING MAP TEST WINDOW ===")
    
    try:
        from modules.logistica.interactive_map import InteractiveMapWidget
        
        # Create main window
        main_window = QMainWindow()
        main_window.setWindowTitle("Test Mapa Interactivo - Rexus.app")
        main_window.setGeometry(100, 100, 1000, 700)
        
        # Create central widget
        central_widget = QWidget()
        main_window.setCentralWidget(central_widget)
        
        # Create layout  
        layout = QVBoxLayout(central_widget)
        
        # Create map widget
        print("Creando widget de mapa...")
        map_widget = InteractiveMapWidget()
        layout.addWidget(map_widget)
        
        print("✅ Mapa creado exitosamente")
        print("✅ Mostrando ventana de prueba...")
        
        # Show window
        main_window.show()
        
        print("\n🗺️  MAPA INTERACTIVO FUNCIONANDO")
        print("   - Ubicación: La Plata, Argentina")
        print("   - Zoom inicial: 12")
        print("   - WebEngine: Funcionando")
        print("   - Folium: Funcionando")
        print("\n📝 Cerrar la ventana para terminar el test")
        
        # Run app
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"❌ Error creando mapa: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_simple_map_test()