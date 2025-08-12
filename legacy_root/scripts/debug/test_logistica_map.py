#!/usr/bin/env python3
"""
Debug script to test logistica map tab functionality
"""

import sys
from pathlib import Path

# Add project root to path
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

def test_logistica_view_creation():
    """Test creating LogisticaView and accessing map tab"""
    try:
        print("Testing LogisticaView creation...")
        
        from PyQt6.QtWidgets import QApplication
        from src.modules.logistica.view import LogisticaView
        
        # Create minimal Qt application
        app = QApplication.instance()
        if not app:
            app = QApplication([])
        
        # Create view
        view = LogisticaView()
        print("SUCCESS: LogisticaView created")
        
        # Check if map tab exists
        if hasattr(view, 'create_mapa_tab'):
            print("SUCCESS: create_mapa_tab method exists")
            
            # Try to call create_mapa_tab
            try:
                map_widget = view.create_mapa_tab()
                print("SUCCESS: create_mapa_tab executed successfully")
                print(f"Map widget type: {type(map_widget)}")
                return True
            except Exception as e:
                print(f"FAILED: Error calling create_mapa_tab - {e}")
                return False
        else:
            print("FAILED: create_mapa_tab method not found")
            return False
            
    except Exception as e:
        print(f"FAILED: Error creating LogisticaView - {e}")
        return False

def test_interactive_map_widget():
    """Test creating InteractiveMapWidget directly"""
    try:
        print("Testing InteractiveMapWidget creation...")
        
        from PyQt6.QtWidgets import QApplication
        from src.modules.logistica.interactive_map import InteractiveMapWidget
        
        # Create minimal Qt application
        app = QApplication.instance()
        if not app:
            app = QApplication([])
        
        # Create widget
        widget = InteractiveMapWidget()
        print("SUCCESS: InteractiveMapWidget created")
        print(f"Widget minimum height: {widget.web_view.minimumHeight()}")
        
        # Check if web_view exists and is configured
        if hasattr(widget, 'web_view'):
            print("SUCCESS: web_view attribute exists")
            print(f"WebView type: {type(widget.web_view)}")
            return True
        else:
            print("FAILED: web_view attribute not found")
            return False
            
    except Exception as e:
        print(f"FAILED: Error creating InteractiveMapWidget - {e}")
        return False

def test_map_tab_integration():
    """Test full integration of map tab in logistica view"""
    try:
        print("Testing full map tab integration...")
        
        from PyQt6.QtWidgets import QApplication, QMainWindow
        from src.modules.logistica.view import LogisticaView
        
        # Create Qt application
        app = QApplication.instance()
        if not app:
            app = QApplication([])
        
        # Create main window and view
        window = QMainWindow()
        view = LogisticaView()
        window.setCentralWidget(view)
        
        # Check if tabs are created properly
        if hasattr(view, 'tab_widget'):
            tab_count = view.tab_widget.count()
            print(f"SUCCESS: Tab widget has {tab_count} tabs")
            
            # Look for map tab
            for i in range(tab_count):
                tab_text = view.tab_widget.tabText(i)
                print(f"Tab {i}: {tab_text}")
                if "mapa" in tab_text.lower() or "map" in tab_text.lower():
                    print(f"SUCCESS: Found map tab at index {i}")
                    
                    # Try to access the tab widget
                    tab_widget = view.tab_widget.widget(i)
                    print(f"Map tab widget type: {type(tab_widget)}")
                    return True
            
            print("WARNING: No map tab found in tab widget")
            return False
        else:
            print("FAILED: No tab_widget attribute found")
            return False
            
    except Exception as e:
        print(f"FAILED: Error testing map tab integration - {e}")
        return False

if __name__ == "__main__":
    print("=== TESTING LOGISTICA MAP TAB FUNCTIONALITY ===")
    
    # Test 1: LogisticaView creation
    view_ok = test_logistica_view_creation()
    print()
    
    # Test 2: InteractiveMapWidget creation
    widget_ok = test_interactive_map_widget() 
    print()
    
    # Test 3: Full integration
    integration_ok = test_map_tab_integration()
    print()
    
    print("=== RESULTS ===")
    print(f"LogisticaView creation: {'OK' if view_ok else 'FAILED'}")
    print(f"InteractiveMapWidget: {'OK' if widget_ok else 'FAILED'}")
    print(f"Map tab integration: {'OK' if integration_ok else 'FAILED'}")
    
    if all([view_ok, widget_ok, integration_ok]):
        print("\nAll tests passed! Map should be working.")
        print("If user still can't see map, check:")
        print("1. Is the map tab being selected/clicked?")
        print("2. Are there any runtime errors in the console?")
        print("3. Is QtWebEngine properly initialized?")
    else:
        print("\nSome tests failed. This explains why the map doesn't work.")