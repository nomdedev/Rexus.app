import sys
import os
sys.path.insert(0, os.getcwd())

# Test simple imports
modules = ['administracion', 'herrajes', 'mantenimiento']

for module in modules:
    print(f"\nTesting {module}:")
    try:
        exec(f"from rexus.modules.{module}.view import *")
        print(f"  Import OK")
    except Exception as e:
        print(f"  Import ERROR: {e}")