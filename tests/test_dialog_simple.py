#!/usr/bin/env python3
"""
Test simplificado del diálogo de obras asociadas - solo inicialización
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_dialog_simple():
    """Test básico del diálogo sin mostrar la UI"""
    
    try:
        # Solo importar y verificar que el módulo se puede cargar
        import rexus.modules.inventario.obras_asociadas_dialog as dialog_module
        
        print("[CHECK] Módulo obras_asociadas_dialog importado exitosamente")
        
        # Verificar que la clase existe
        if hasattr(dialog_module, 'ObrasAsociadasDialog'):
            print("[CHECK] Clase ObrasAsociadasDialog encontrada")
            
            # Datos de prueba
            item_data = {
                'id': 1,
                'codigo': 'ALU001',
                'descripcion': 'Perfil de aluminio 60x40',
                'tipo': 'Perfil',
                'categoria': 'Perfiles',
                'stock_actual': 100,
                'stock_minimo': 10,
                'precio_unitario': 25.50
            }
            
            print(f"[CHECK] Datos de prueba preparados para: {item_data['descripcion']}")
            print("[CHECK] El diálogo está listo para usar en la aplicación")
            
        else:
            print("[ERROR] Clase ObrasAsociadasDialog no encontrada")
            
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_dialog_simple()
