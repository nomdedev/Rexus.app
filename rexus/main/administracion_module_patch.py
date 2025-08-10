from rexus.modules.administracion.view import AdministracionView

# ...existing code...

def _create_administracion_module(self) -> QWidget:
    """Crea el módulo de administración usando la vista real"""
    try:
        view = AdministracionView()
        return view
    except Exception as e:
        print(f"Error creando administración real: {e}")
        return self._create_fallback_module("Administración")
