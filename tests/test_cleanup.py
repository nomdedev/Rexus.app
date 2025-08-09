#!/usr/bin/env python3
"""
Script para limpiar y organizar la estructura de tests.
Elimina tests obsoletos y crea una estructura clara.
"""

import os
import shutil
from pathlib import Path

def cleanup_old_tests():
    """Elimina tests obsoletos y archivos duplicados."""
    tests_dir = Path(__file__).parent
    
    # Archivos y directorios a eliminar
    to_remove = [
        # Tests obsoletos
        "test_integration.py",  # Malformado
        "test_mainwindow.py",   # Vacío
        "test_click_simulation.py",
        "test_click_simulation_fixed.py",
        "test_errores_criticos_no_cubiertos.py",
        "test_errores_criticos_robustos.py",
        
        # Directorios con tests duplicados
        "accesibilidad/",
        "fixtures/",
        "general/",
        "produccion/",
        "reports/",
        "sidebar/",
        "ui/",
        "utilitarios/",
        "utils/",
        "verificacion/",
        "visual/",
        
        # Tests específicos duplicados
        "test_*.py",  # Muchos tests en raíz duplicados
    ]
    
    print("🧹 Limpiando estructura de tests obsoletos...")
    
    for item in to_remove:
        path = tests_dir / item
        if path.exists():
            if path.is_dir():
                shutil.rmtree(path)
                print(f"   [CHECK] Eliminado directorio: {item}")
            else:
                path.unlink()
                print(f"   [CHECK] Eliminado archivo: {item}")
    
    print("[CHECK] Limpieza completada")

if __name__ == "__main__":
    cleanup_old_tests()