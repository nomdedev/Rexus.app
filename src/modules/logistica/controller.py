"""Controlador de Logística"""

from PyQt6.QtCore import QObject


class LogisticaController(QObject):
    def cargar_entregas(self):
        if self.model and self.view:
            entregas = self.model.obtener_entregas()
            self.view.cargar_entregas_en_tabla(entregas)

    def guardar_entrega(self, datos):
        if self.model:
            self.model.crear_entrega(datos)
            self.cargar_entregas()

    # Métodos para Service (placeholder, requiere implementación en el modelo)
    def cargar_services(self):
        if self.model and self.view and hasattr(self.model, 'obtener_services'):
            services = self.model.obtener_services()
            self.view.cargar_services_en_tabla(services)

    def guardar_service(self, datos):
        if self.model and hasattr(self.model, 'crear_service'):
            self.model.crear_service(datos)
            self.cargar_services()
    def __init__(self, model=None, view=None, db_connection=None, usuarios_model=None):
        super().__init__()
        self.model = model
        self.view = view
        self.db_connection = db_connection
        self.usuarios_model = usuarios_model
        self.usuario_actual = "SISTEMA"
