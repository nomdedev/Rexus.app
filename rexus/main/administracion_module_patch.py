from PyQt6.QtWidgets import QWidget
import importlib
administracion_view = importlib.import_module('rexus.modules.12_administracion.view')
AdministracionView = administracion_view.AdministracionView

# ...existing code...

def _create_administracion_module(self) -> QWidget:
    """Crea el módulo de administración usando la vista real"""
    try:
        view = AdministracionView()
        return view
    except Exception as e:
        print(f"Error creando administración real: {e}")
        return self._create_fallback_module("Administración")
