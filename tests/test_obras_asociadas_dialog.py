#!/usr/bin/env python3
"""
Test para verificar la funcionalidad de obras asociadas
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import QApplication
from rexus.modules.inventario.obras_asociadas_dialog import ObrasAsociadasDialog

def test_obras_asociadas_dialog():
    """Test básico del diálogo de obras asociadas"""
    
    app = QApplication(sys.argv)
    
    # Datos de prueba para un material
    item_data = {
        'id': 1,
        'codigo': 'TEST001',
        'descripcion': 'Material de prueba',
        'tipo': 'Perfil',
        'categoria': 'Aluminio',
        'stock_actual': 100,
        'stock_minimo': 10,
        'precio_unitario': 25.50
    }
    
    try:
        # Crear y mostrar diálogo
        dialog = ObrasAsociadasDialog(item_data)
        
        print("[CHECK] Diálogo creado exitosamente")
        print(f"   Título: {dialog.windowTitle()}")
        print(f"   Material: {item_data['codigo']} - {item_data['descripcion']}")
        
        # Verificar componentes
        assert hasattr(dialog, 'tabla_obras'), "[ERROR] Tabla de obras no encontrada"
        assert hasattr(dialog, 'item_inventario'), "[ERROR] Datos del item no encontrados"
        
        print("[CHECK] Componentes del diálogo verificados")
        
        # No mostrar el diálogo para no bloquear la ejecución
        # dialog.show()
        
        print("[CHECK] Test completado exitosamente")
        
    except Exception as e:
        print(f"[ERROR] Error en test: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        app.quit()

if __name__ == "__main__":
    test_obras_asociadas_dialog()
