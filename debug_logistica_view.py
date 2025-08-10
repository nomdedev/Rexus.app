#!/usr/bin/env python3

import traceback
import sys
sys.stdout.reconfigure(encoding='utf-8')

try:
    from rexus.modules.logistica.view import LogisticaView
    print("✅ Import successful")
    
    view = LogisticaView()
    print("✅ Instantiation successful")
    
except Exception as e:
    print(f"❌ Error: {e}")
    traceback.print_exc()