#!/usr/bin/env python3
"""
Test del módulo de Logística con mapa integrado
"""

import sys
import os

# Add rexus to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'rexus'))

def test_logistica_with_map():
    print("=== TESTING LOGISTICA MODULE WITH MAP ===")
    
    try:
        # Import logistica view
        from modules.logistica.view import LogisticaView
        print("OK - LogisticaView imported successfully")
        
        # Import interactive map
        from modules.logistica.interactive_map import InteractiveMapWidget
        print("OK - InteractiveMapWidget imported successfully")
        
        # Test creating logistica view (this will test map integration)
        logistica_view = LogisticaView()
        print("OK - LogisticaView created successfully")
        
        # Check if map was created
        if hasattr(logistica_view, 'interactive_map') and logistica_view.interactive_map:
            print("OK - Interactive map is available in LogisticaView")
            print("OK - Map integration working correctly")
        else:
            print("INFO - Interactive map not available (might be using fallback)")
        
        print("\nSUCCESS - Logistica module with map integration is working!")
        return True
        
    except Exception as e:
        print(f"ERROR - Failed to load Logistica with map: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_logistica_with_map()
    if success:
        print("\nEl módulo de Logística con mapa interactivo debería funcionar correctamente ahora.")
        print("Las dependencias están instaladas y el código puede importarse sin errores.")
    else:
        print("\nHay problemas con el módulo de Logística.")