"""
Test simple para verificar que la vista de obras carga datos correctamente.
"""

import sys
import os
from PyQt6.QtWidgets import QApplication

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

def test_cargar_datos_obras_simple():
    """Test simple para verificar la carga de datos en la vista."""
    print("[TEST] Iniciando test de carga de datos...")
    
    try:
        # Inicializar QApplication
        if not QApplication.instance():
            app = QApplication([])
        
        # Importar la vista
        from rexus.modules.obras.view import ObrasView
        
        # Crear vista (sin inicializar modelo automático para evitar errores DB)
        print("[TEST] Creando vista...")
        vista = ObrasView.__new__(ObrasView)  # Crear sin llamar __init__
        vista.controller = None
        vista.model = None
        
        # Inicializar solo los componentes necesarios manualmente
        from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableWidget
        QWidget.__init__(vista)
        
        # Crear tabla manualmente
        layout = QVBoxLayout(vista)
        vista.tabla_obras = QTableWidget()
        vista.tabla_obras.setColumnCount(9)
        vista.tabla_obras.setHorizontalHeaderLabels([
            "Código", "Nombre", "Cliente", "Responsable", 
            "Fecha Inicio", "Fecha Fin", "Estado", "Presupuesto", "Acciones"
        ])
        layout.addWidget(vista.tabla_obras)
        
        print("[TEST] Vista creada correctamente")
        
        # Datos de prueba
        datos_prueba = [
            {
                'codigo': 'OBR-001',
                'nombre': 'Edificio Central',
                'cliente': 'Cliente A',
                'responsable': 'Juan Pérez',
                'fecha_inicio': '2024-01-15',
                'fecha_fin_estimada': '2024-12-15',
                'estado': 'Activo',
                'presupuesto_inicial': 150000
            },
            {
                'codigo': 'OBR-002',
                'nombre': 'Plaza Comercial',
                'cliente': 'Cliente B', 
                'responsable': 'María García',
                'fecha_inicio': '2024-02-01',
                'fecha_fin_estimada': '2025-01-30',
                'estado': 'En Progreso',
                'presupuesto_inicial': 250000
            }
        ]
        
        print(f"[TEST] Cargando {len(datos_prueba)} obras...")
        
        # Cargar datos en la tabla
        vista.cargar_obras_en_tabla(datos_prueba)
        
        # Verificar que se cargaron los datos
        filas_cargadas = vista.tabla_obras.rowCount()
        print(f"[TEST] Filas cargadas en tabla: {filas_cargadas}")
        
        if filas_cargadas == len(datos_prueba):
            print("✅ [TEST] Los datos se cargaron correctamente en la tabla")
            
            # Verificar contenido de la primera fila
            codigo_celda = vista.tabla_obras.item(0, 0)
            nombre_celda = vista.tabla_obras.item(0, 1)
            
            if codigo_celda and nombre_celda:
                print(f"[TEST] Primera fila - Código: {codigo_celda.text()}, Nombre: {nombre_celda.text()}")
                
                if codigo_celda.text() == "OBR-001" and nombre_celda.text() == "Edificio Central":
                    print("✅ [TEST] El contenido de las celdas es correcto")
                    return True
                else:
                    print("❌ [TEST] El contenido de las celdas no coincide")
                    return False
            else:
                print("❌ [TEST] Las celdas están vacías")
                return False
        else:
            print(f"❌ [TEST] Se esperaban {len(datos_prueba)} filas, pero se cargaron {filas_cargadas}")
            return False
            
    except Exception as e:
        print(f"❌ [TEST] Error durante el test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if test_cargar_datos_obras_simple():
        print("\n🎉 [RESUMEN] Test completado exitosamente - La vista puede cargar y mostrar datos")
        sys.exit(0)
    else:
        print("\n💥 [RESUMEN] Test falló - Hay problemas con la carga de datos en la vista")
        sys.exit(1)
