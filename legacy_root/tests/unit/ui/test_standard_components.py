#!/usr/bin/env python
"""Test script for standard components"""

import sys
from PyQt6.QtWidgets import QApplication

print("Testing StandardComponents...")

try:
    app = QApplication(sys.argv)

    from rexus.ui.standard_components import StandardComponents
    print("  StandardComponents import: OK")

    # Test create_group_box
    gb = StandardComponents.create_group_box('Test Group')
    print("  create_group_box: OK")

    # Test other methods
    table = StandardComponents.create_standard_table()
    print("  create_standard_table: OK")

    panel = StandardComponents.create_control_panel()
    print("  create_control_panel: OK")

    print("All tests passed!")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

finally:
    try:
        app.quit()
    except:
        pass
