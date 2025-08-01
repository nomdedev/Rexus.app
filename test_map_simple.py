#!/usr/bin/env python3
"""
Test simple del mapa interactivo sin Unicode
"""

import sys
import os

# Add rexus to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'rexus'))

def test_map():
    print("=== TESTING MAP DEPENDENCIES ===")
    
    # Test folium
    try:
        import folium
        print(f"OK - folium version: {folium.__version__}")
    except ImportError as e:
        print(f"ERROR - folium: {e}")
        return False
    
    # Test PyQt6 WebEngine
    try:
        from PyQt6.QtWebEngineWidgets import QWebEngineView
        print("OK - PyQt6 WebEngine available")
    except ImportError as e:
        print(f"ERROR - PyQt6 WebEngine: {e}")
        return False
    
    # Test map widget import
    try:
        from modules.logistica.interactive_map import InteractiveMapWidget
        print("OK - InteractiveMapWidget import successful")
    except ImportError as e:
        print(f"ERROR - InteractiveMapWidget: {e}")
        return False
    
    print("\n=== CREATING SIMPLE MAP ===")
    
    # Create a simple folium map to test
    try:
        # La Plata coordinates
        la_plata = [-34.9214, -57.9544]
        
        # Create map
        m = folium.Map(location=la_plata, zoom_start=12)
        
        # Add marker
        folium.Marker(
            la_plata,
            popup="La Plata - Rexus.app",
            tooltip="Click para más info"
        ).add_to(m)
        
        # Save to temp file
        temp_file = "temp_map_test.html"
        m.save(temp_file)
        
        print(f"OK - Map created and saved to {temp_file}")
        print("OK - All dependencies working correctly")
        
        # Clean up
        if os.path.exists(temp_file):
            os.remove(temp_file)
            print("OK - Cleanup completed")
        
        return True
        
    except Exception as e:
        print(f"ERROR creating map: {e}")
        return False

if __name__ == "__main__":
    success = test_map()
    if success:
        print("\nSUCCESS: Map dependencies are working!")
        print("The interactive map should now be visible in Logistica module.")
    else:
        print("\nFAILED: Map dependencies have issues.")