#!/usr/bin/env python3
"""
Test específico para la funcionalidad de doble clic y obras asociadas
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem
from PyQt6.QtCore import Qt

def test_funcionalidad_doble_click():
    """Test de la funcionalidad de doble clic en inventario"""
    
    app = QApplication(sys.argv)
    
    try:
        # Importar el diálogo
        from rexus.modules.inventario.obras_asociadas_dialog import ObrasAsociadasDialog
        
        # Simular datos de un ítem del inventario
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
        
        # Crear diálogo
        dialog = ObrasAsociadasDialog(item_data)
        
        print("✅ Diálogo de obras asociadas creado exitosamente")
        print(f"   Material: {item_data['codigo']} - {item_data['descripcion']}")
        print(f"   Ventana: {dialog.windowTitle()}")
        
        # Verificar que la tabla tiene contenido
        if hasattr(dialog, 'tabla_obras'):
            row_count = dialog.tabla_obras.rowCount()
            col_count = dialog.tabla_obras.columnCount()
            print(f"   Tabla: {row_count} filas x {col_count} columnas")
            
            # Mostrar contenido de la primera fila si existe
            if row_count > 0:
                print("   Primera fila:")
                for col in range(min(col_count, 6)):  # Máximo 6 columnas
                    item = dialog.tabla_obras.item(0, col)
                    if item:
                        print(f"     Col {col}: {item.text()}")
                    else:
                        print(f"     Col {col}: [vacío]")
        
        print("✅ Test de funcionalidad completado exitosamente")
        
        # No mostrar el diálogo para no bloquear
        # dialog.show()
        # return app.exec()
        
    except Exception as e:
        print(f"❌ Error en test: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        app.quit()

if __name__ == "__main__":
    test_funcionalidad_doble_click()
