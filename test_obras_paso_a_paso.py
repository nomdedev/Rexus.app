#!/usr/bin/env python3

import sys
sys.stdout.reconfigure(encoding='utf-8')

print("=== Test paso a paso del constructor de ObrasView ===")

try:
    print("1. Importando PyQt6...")
    from PyQt6.QtWidgets import QApplication, QWidget
    print("   ✓ PyQt6 importado")
    
    print("2. Creando QApplication...")
    app = QApplication([])
    print("   ✓ QApplication creada")
    
    print("3. Importando ObrasView...")
    from rexus.modules.obras.view import ObrasView
    print("   ✓ ObrasView importado")
    
    print("4. Creando instancia de ObrasView...")
    vista = ObrasView()
    print("   ✓ ObrasView creada exitosamente")
    
    print("5. Verificando estructura...")
    print(f"   - Tipo: {type(vista)}")
    print(f"   - Es QWidget: {isinstance(vista, QWidget)}")
    
    print("\n✅ ÉXITO: ObrasView funciona correctamente")
    
except Exception as e:
    print(f"\n❌ ERROR en paso: {e}")
    import traceback
    traceback.print_exc()