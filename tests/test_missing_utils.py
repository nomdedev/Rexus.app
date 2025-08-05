import sys
import os
sys.path.insert(0, os.getcwd())

missing_imports = [
    'rexus.utils.sql_script_loader',
    'rexus.modules.herrajes.improved_dialogs',
    'utils.data_sanitizer',
    'utils.sql_security'
]

print("Testing missing imports:")
for imp in missing_imports:
    try:
        exec(f"import {imp}")
        print(f"  {imp}: OK")
    except Exception as e:
        print(f"  {imp}: MISSING - {e}")