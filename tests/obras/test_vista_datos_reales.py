"""
Test simple para verificar la carga de datos reales en la vista de obras.
"""

import sys
import os
from PyQt6.QtWidgets import QApplication

# Agregar el directorio raíz al path
sys.path.insert(0, os.getcwd())

def test_vista_con_datos_reales():
    """Test de la vista con datos reales de la base de datos."""
    print("🧪 [TEST] Iniciando test de vista con datos reales...")
    
    try:
        # Importar después de configurar el path
        from rexus.modules.obras.view import ObrasView
        
        app = QApplication([])
        
        print("🔧 [TEST] Creando vista de obras...")
        vista = ObrasView()
        
        print("[CHECK] [TEST] Vista creada correctamente")
        print(f"[CHART] [TEST] Filas en tabla: {vista.tabla_obras.rowCount()}")
        print(f"📋 [TEST] Columnas en tabla: {vista.tabla_obras.columnCount()}")
        
        # Verificar headers de columnas
        headers = []
        for col in range(vista.tabla_obras.columnCount()):
            header = vista.tabla_obras.horizontalHeaderItem(col)
            headers.append(header.text() if header else f"Col{col}")
        
        print(f"🏷️ [TEST] Headers: {headers}")
        
        # Mostrar contenido si hay datos
        if vista.tabla_obras.rowCount() > 0:
            print("\n📋 [TEST] Contenido de la primera obra:")
            for col in range(min(vista.tabla_obras.columnCount(), 8)):  # Mostrar hasta 8 columnas
                item = vista.tabla_obras.item(0, col)
                header_text = headers[col] if col < len(headers) else f"Col{col}"
                value = item.text() if item else "None"
                print(f"   {header_text}: '{value}'")
            
            print(f"\n📈 [TEST] Total de obras mostradas: {vista.tabla_obras.rowCount()}")
            return True
        else:
            print("[WARN] [TEST] No hay datos en la tabla")
            return False
            
    except Exception as e:
        print(f"[ERROR] [TEST] Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_vista_con_datos_reales()
    if success:
        print("\n🎉 [TEST] Test completado exitosamente - Los datos se están mostrando")
    else:
        print("\n💥 [TEST] Test falló - Hay problemas con la carga de datos")
