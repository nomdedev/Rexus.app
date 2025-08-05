"""Controlador de Logística"""

from PyQt6.QtCore import QObject
from rexus.utils.error_handler import RexusErrorHandler as ErrorHandler, error_boundary as safe_method_decorator
from rexus.core.auth_manager import AuthManager


class LogisticaController(QObject):
    def __init__(self, model=None, view=None, db_connection=None, usuarios_model=None):
        super().__init__()
        self.model = model
        self.view = view
        self.db_connection = db_connection
        self.usuarios_model = usuarios_model
        self.usuario_actual = "SISTEMA"
        
        # Conectar señales de la vista
        if self.view:
            self.view.crear_entrega_solicitada.connect(self.guardar_entrega)
    
    @safe_method_decorator("cargar datos iniciales de logística")
    def cargar_datos_iniciales(self):
        """Carga los datos iniciales del módulo."""
        self.cargar_entregas()
        self.cargar_services()
    
    def cargar_entregas(self):
        """Carga las entregas en la tabla."""
        if self.model and self.view:
            try:
                entregas = self.model.obtener_entregas()
                self.view.cargar_entregas_en_tabla(entregas)
            except Exception as e:
                print(f"Error cargando entregas: {e}")

    @auth_required(permission='CREATE')
    def guardar_entrega(self, datos):
        """Guarda una nueva entrega."""
        if self.model:
            try:
                self.model.crear_entrega(datos)
                self.cargar_entregas()
                if self.view:
                    ErrorHandler.mostrar_informacion(self.view, "Logística", "Entrega guardada exitosamente")
            except Exception as e:
                ErrorHandler.manejar_error_base_datos(self.view, "guardar entrega", e)

    def cargar_services(self):
        """Carga los servicios en la tabla."""
        if self.model and self.view and hasattr(self.model, 'obtener_services'):
            try:
                services = self.model.obtener_services()
                self.view.cargar_services_en_tabla(services)
            except Exception as e:
                print(f"Error cargando servicios: {e}")

    @auth_required(permission='CREATE')
    def guardar_service(self, datos):
        """Guarda un nuevo servicio."""
        if self.model and hasattr(self.model, 'crear_service'):
            try:
                self.model.crear_service(datos)
                self.cargar_services()
            except Exception as e:
                print(f"Error guardando servicio: {e}")
                if self.view:
                    self.view.mostrar_error(f"Error al guardar servicio: {str(e)}")
