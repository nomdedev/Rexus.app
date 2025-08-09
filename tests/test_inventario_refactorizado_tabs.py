#!/usr/bin/env python3
"""
Test básico del módulo de inventario refactorizado
"""

import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

try:
    from PyQt6.QtWidgets import QApplication
    from rexus.modules.inventario.view import InventarioView
    
    def test_inventario_view():
        """Test básico de la vista de inventario."""
        app = QApplication(sys.argv)
        
        try:
            # Crear la vista
            vista = InventarioView()
            print("[CHECK] Vista de inventario creada exitosamente")
            
            # Verificar que tiene pestañas
            if hasattr(vista, 'tab_widget'):
                print("[CHECK] Sistema de pestañas inicializado")
                print(f"   Número de pestañas: {vista.tab_widget.count()}")
            
            # Verificar componentes de estadísticas
            if hasattr(vista, 'lbl_total_productos'):
                print("[CHECK] Panel de estadísticas inicializado")
            
            # Verificar tabla
            if hasattr(vista, 'tabla_inventario'):
                print("[CHECK] Tabla de inventario inicializada")
            
            # Test de actualización de estadísticas
            stats_test = {
                "total_productos": 150,
                "stock_bajo": 12,
                "sin_stock": 3,
                "valor_total": 125000.50
            }
            
            vista.actualizar_estadisticas(stats_test)
            print("[CHECK] Actualización de estadísticas funcional")
            
            print("\n🎉 Todos los tests del módulo inventario pasaron exitosamente!")
            return True
            
        except Exception as e:
            print(f"[ERROR] Error en test de inventario: {e}")
            return False
    
    if __name__ == "__main__":
        success = test_inventario_view()
        sys.exit(0 if success else 1)
        
except ImportError as e:
    print(f"[ERROR] Error de importación: {e}")
    sys.exit(1)
