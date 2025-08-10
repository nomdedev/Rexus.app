"""
Vista Simplificada de Vidrios - Rexus.app
Integra la nueva estructura de pestañas manteniendo compatibilidad.
"""

import logging
from PyQt6.QtCore import pyqtSignal
from rexus.ui.templates.base_module_view import BaseModuleView
from .view_tabs import VidriosTabsView


class VidriosView(BaseModuleView):
    """Vista principal del módulo de vidrios con estructura de pestañas."""

    # Señales para compatibilidad con el sistema principal
    datos_actualizados = pyqtSignal()
    error_ocurrido = pyqtSignal(str)
    buscar_requested = pyqtSignal(dict)
    agregar_requested = pyqtSignal(dict)
    editar_requested = pyqtSignal(int, dict)
    eliminar_requested = pyqtSignal(int)
    asignar_obra_requested = pyqtSignal(int, int)
    crear_pedido_requested = pyqtSignal(dict)
    filtrar_requested = pyqtSignal(dict)

    def __init__(self):
        super().__init__("🪟 Gestión de Vidrios")
        self.controller = None
        
        # Crear la vista con pestañas y añadirla al contenido principal
        self.tabs_view = VidriosTabsView()
        
        # Conectar señales de la vista de pestañas a las señales principales
        self.conectar_señales_tabs()
        
        # Añadir la vista de pestañas al contenido principal
        self.add_to_main_content(self.tabs_view)

    def conectar_señales_tabs(self):
        """Conecta las señales de la vista de pestañas a las señales principales."""
        try:
            # Conectar señales de datos si existen en la vista de pestañas
            if hasattr(self.tabs_view, 'datos_actualizados'):
                self.tabs_view.datos_actualizados.connect(self.datos_actualizados.emit)
            if hasattr(self.tabs_view, 'error_ocurrido'):
                self.tabs_view.error_ocurrido.connect(self.error_ocurrido.emit)
            if hasattr(self.tabs_view, 'buscar_requested'):
                self.tabs_view.buscar_requested.connect(self.buscar_requested.emit)
            if hasattr(self.tabs_view, 'agregar_requested'):
                self.tabs_view.agregar_requested.connect(self.agregar_requested.emit)
            if hasattr(self.tabs_view, 'editar_requested'):
                self.tabs_view.editar_requested.connect(self.editar_requested.emit)
            if hasattr(self.tabs_view, 'eliminar_requested'):
                self.tabs_view.eliminar_requested.connect(self.eliminar_requested.emit)
                
            logging.info("Señales de VidriosTabsView conectadas correctamente")
        except Exception as e:
            logging.error(f"Error conectando señales: {e}")

    def set_controller(self, controller):
        """Establece el controlador para la vista."""
        self.controller = controller
        if hasattr(self.tabs_view, 'set_controller'):
            self.tabs_view.set_controller(controller)

    def actualizar_datos(self):
        """Actualiza los datos de la vista."""
        if hasattr(self.tabs_view, 'actualizar_datos'):
            self.tabs_view.actualizar_datos()
        self.datos_actualizados.emit()

    def buscar(self):
        """Ejecuta una búsqueda en la vista."""
        if hasattr(self.tabs_view, 'buscar'):
            self.tabs_view.buscar()

    def nuevo_registro(self):
        """Crea un nuevo registro."""
        if hasattr(self.tabs_view, 'nuevo_registro'):
            self.tabs_view.nuevo_registro()

    def get_tabla_principal(self):
        """Retorna la tabla principal para compatibilidad."""
        if hasattr(self.tabs_view, 'get_tabla_principal'):
            return self.tabs_view.get_tabla_principal()
        return None

    def aplicar_tema_modular(self):
        """Aplica el tema modular."""
        if hasattr(self.tabs_view, 'aplicar_tema_modular'):
            self.tabs_view.aplicar_tema_modular()
