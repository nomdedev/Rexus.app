#!/usr/bin/env python3
"""
TEST WIDGETS AVANZADOS
======================
"""

import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(__file__))

try:
    from PyQt6.QtWidgets import QApplication
    from rexus.modules.obras.widgets_advanced import PaginacionWidget, FiltrosAvanzadosWidget
    print("[CHECK] Widgets avanzados importados correctamente")
except Exception as e:
    print(f"[ERROR] Error al importar widgets: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)


def test_paginacion_widget():
    """Test del widget de paginación."""
    
    app = QApplication.instance()
    if not app:
        app = QApplication([])
    
    # Crear widget de paginación
    paginacion = PaginacionWidget()
    
    # Test con datos
    paginacion.actualizar_datos(total_items=150, pagina_actual=1)
    
    print(f"Página actual: {paginacion.pagina_actual}")
    print(f"Total páginas: {paginacion.total_paginas}")
    print(f"Items por página: {paginacion.items_por_pagina}")
    
    # Test navegación
    paginacion.ir_pagina_siguiente()
    print(f"Después de siguiente: página {paginacion.pagina_actual}")
    
    paginacion.ir_ultima_pagina()
    print(f"Última página: {paginacion.pagina_actual}")
    
    # Test rango
    inicio, fin = paginacion.obtener_rango_actual()
    print(f"Rango actual: {inicio} - {fin}")
    
    return True


def test_filtros_widget():
    """Test del widget de filtros."""
    
    app = QApplication.instance()
    if not app:
        app = QApplication([])
    
    # Crear widget de filtros
    filtros = FiltrosAvanzadosWidget()
    
    # Simular cambios
    filtros.combo_estado.setCurrentText("EN_PROCESO")
    filtros.txt_responsable.setText("Juan")
    
    # Obtener filtros
    filtros_dict = filtros.obtener_filtros()
    print(f"Filtros actuales: {filtros_dict}")
    
    return True


if __name__ == "__main__":
    try:
        test_paginacion_widget()
        print("[CHECK] Test paginación completado")
        
        test_filtros_widget()
        print("[CHECK] Test filtros completado")
        
        print("\n🎉 Todos los tests de widgets completados exitosamente")
        
    except Exception as e:
        print(f"[ERROR] Error en tests: {e}")
        import traceback
        traceback.print_exc()
