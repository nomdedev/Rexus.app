#!/usr/bin/env python3

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
os.environ['PYTHONIOENCODING'] = 'utf-8'

try:
    print("1. Configurando logs...")
    import logging
    logging.getLogger().setLevel(logging.CRITICAL)

    print("2. Importando PyQt6...")
    from PyQt6.QtWidgets import QApplication

    print("3. Creando QApplication...")
    app = QApplication.instance()
    if app is None:
        app = QApplication([])

    print("4. Importando ObrasModernView...")
    from rexus.modules.obras.view import ObrasModernView

    print("5. Creando instancia...")
    view = ObrasModernView()

    print("6. Verificando método...")
    if hasattr(view, 'cargar_obras_en_tabla'):
        print("   - cargar_obras_en_tabla: OK")

    print("7. Verificando tabla...")
    if hasattr(view, 'tabla_obras'):
        print("   - tabla_obras: OK")
        print(f"   - Filas en tabla: {view.tabla_obras.rowCount()}")

    print("SUCCESS: Obras funcionando correctamente")

except Exception as e:
    print(f"ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
