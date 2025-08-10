#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.abspath('.'))
sys.stdout.reconfigure(encoding='utf-8')

try:
    print("Testing Logistica view...")
    from rexus.modules.logistica.view import LogisticaView
    print("IMPORT: successful")
    
    # Try to instantiate
    view = LogisticaView()
    print("CREATE: View created successfully")
    print("ATTRS:", len(dir(view)), "attributes/methods")
    
except ImportError as e:
    print(f"IMPORT ERROR: {e}")
except Exception as e:
    print(f"OTHER ERROR: {e}")
    import traceback
    traceback.print_exc()