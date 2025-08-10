#!/usr/bin/env python3

import traceback
import sys

sys.stdout.reconfigure(encoding='utf-8')

try:
    from rexus.modules.obras.view import ObrasView
    print("✓ Importación exitosa")
    
    vista = ObrasView()
    print("✓ Instancia creada exitosamente")
    
except Exception as e:
    print(f"✗ Error: {e}")
    print("\nTraceback completo:")
    traceback.print_exc()