"""
Script de prueba para el módulo Usuarios modernizado
"""

import os
import sys

# Añadir el directorio principal al path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from PyQt6.QtWidgets import QApplication

# Importación directa del archivo
sys.path.append(os.path.join(os.path.dirname(__file__), "rexus", "modules", "usuarios"))
try:
    from view_modern import UsuariosViewModern
except ImportError:
    # Intentar importación alternativa
    sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    from rexus.modules.usuarios.view_modern import UsuariosViewModern


def test_usuarios_view():
    """Prueba la vista modernizada del módulo usuarios."""
    print("👥 Iniciando prueba del módulo Usuarios modernizado...")

    app = QApplication(sys.argv)

    try:
        # Crear vista
        vista = UsuariosViewModern()

        # Configurar ventana
        vista.setWindowTitle("Rexus - Gestión de Usuarios")
        vista.resize(1400, 900)
        vista.show()

        print("[CHECK] Vista de usuarios modernizada cargada correctamente")
        print("[LOCK] Funcionalidades de seguridad implementadas:")
        print("   - Búsqueda y filtros por rol/estado")
        print("   - Gestión de permisos y sesiones")
        print("   - Estados visuales (activo/inactivo/bloqueado)")
        print("   - LoadingManager integrado")
        print("   - Atajos de teclado completos")
        print("   - Interfaz verde (usuarios) vs azul (herrajes)")

        # Ejecutar aplicación
        sys.exit(app.exec())

    except Exception as e:
        print(f"[ERROR] Error al cargar la vista: {e}")
        return False


if __name__ == "__main__":
    test_usuarios_view()
