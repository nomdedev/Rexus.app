#!/usr/bin/env python3
"""
Test script to check if QWebEngineView is available
"""

def test_webengine():
    """Test if QtWebEngine is available"""
    try:
        print("Testing QtWebEngine availability...")
        from PyQt6.QtWebEngineWidgets import QWebEngineView
        print("SUCCESS: QWebEngineView imported successfully")
        return True
    except ImportError as e:
        print(f"FAILED: QtWebEngine not available - {e}")
        return False
        
def test_folium():
    """Test if Folium is available"""
    try:
        print("Testing Folium availability...")
        import folium
        print("SUCCESS: Folium imported successfully")
        return True
    except ImportError as e:
        print(f"FAILED: Folium not available - {e}")
        return False

def test_logistica_import():
    """Test importing logistica interactive map"""
    try:
        print("Testing logistica interactive map import...")
        import sys
        from pathlib import Path
        root_dir = Path(__file__).parent.parent.parent
        sys.path.insert(0, str(root_dir))
        
        from src.modules.logistica.interactive_map import InteractiveMapWidget
        print("SUCCESS: InteractiveMapWidget imported successfully")
        return True
    except Exception as e:
        print(f"FAILED: Could not import InteractiveMapWidget - {e}")
        return False

if __name__ == "__main__":
    print("=== TESTING LOGISTICA MAP DEPENDENCIES ===")
    
    webengine_ok = test_webengine()
    folium_ok = test_folium()
    map_import_ok = test_logistica_import()
    
    print("\n=== RESULTS ===")
    print(f"QtWebEngine: {'OK' if webengine_ok else 'FAILED'}")
    print(f"Folium: {'OK' if folium_ok else 'FAILED'}")
    print(f"InteractiveMapWidget: {'OK' if map_import_ok else 'FAILED'}")
    
    if all([webengine_ok, folium_ok, map_import_ok]):
        print("\nAll dependencies are available. Map should work!")
    else:
        print("\nSome dependencies are missing. This explains why the map doesn't work.")
        print("To fix: pip install PyQt6-WebEngine folium")