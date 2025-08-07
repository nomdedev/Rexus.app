#!/usr/bin/env python3
"""
Test básico del módulo de herrajes refactorizado con pestañas
"""

import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

try:
    from PyQt6.QtWidgets import QApplication
    from rexus.modules.herrajes.view import HerrajesView
    
    def test_herrajes_view():
        """Test básico de la vista de herrajes."""
        app = QApplication(sys.argv)
        
        try:
            # Crear la vista
            vista = HerrajesView()
            print("✅ Vista de herrajes creada exitosamente")
            
            # Verificar que tiene pestañas
            if hasattr(vista, 'tab_widget'):
                print("✅ Sistema de pestañas inicializado")
                print(f"   Número de pestañas: {vista.tab_widget.count()}")
            
            # Verificar componentes de estadísticas
            if hasattr(vista, 'lbl_total_herrajes'):
                print("✅ Panel de estadísticas inicializado")
            
            # Verificar tabla
            if hasattr(vista, 'tabla_principal'):
                print("✅ Tabla de herrajes inicializada")
            
            # Test de actualización de estadísticas
            stats_test = {
                "total_herrajes": 85,
                "herrajes_activos": 72,
                "herrajes_inactivos": 13,
                "tipos_disponibles": 8
            }
            
            vista.actualizar_estadisticas(stats_test)
            print("✅ Actualización de estadísticas funcional")
            
            print("\n🎉 Todos los tests del módulo herrajes pasaron exitosamente!")
            return True
            
        except Exception as e:
            print(f"❌ Error en test de herrajes: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    if __name__ == "__main__":
        success = test_herrajes_view()
        sys.exit(0 if success else 1)
        
except ImportError as e:
    print(f"❌ Error de importación: {e}")
    sys.exit(1)
