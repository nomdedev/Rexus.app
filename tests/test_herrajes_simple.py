"""
Script de prueba para el módulo Herrajes simplificado
"""

import os
import sys

# Añadir el directorio principal al path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from PyQt6.QtWidgets import QApplication

# Importación directa del archivo
sys.path.append(os.path.join(os.path.dirname(__file__), "rexus", "modules", "herrajes"))
from view_simple import HerrajesViewSimple


def test_herrajes_view():
    """Prueba la vista del módulo herrajes."""
    print("🔧 Iniciando prueba del módulo Herrajes...")

    app = QApplication(sys.argv)

    try:
        # Crear vista
        vista = HerrajesViewSimple()

        # Configurar ventana
        vista.setWindowTitle("Rexus - Gestión de Herrajes")
        vista.resize(1200, 800)
        vista.show()

        print("[CHECK] Vista de herrajes cargada correctamente")
        print("[CHART] Funcionalidades disponibles:")
        print("   - Búsqueda y filtros")
        print("   - Paginación")
        print("   - Estadísticas en tiempo real")
        print("   - Interfaz moderna responsive")
        print("   - Indicadores de carga")
        print("   - Atajos de teclado")

        # Ejecutar aplicación
        sys.exit(app.exec())

    except Exception as e:
        print(f"[ERROR] Error al cargar la vista: {e}")
        return False


if __name__ == "__main__":
    test_herrajes_view()
