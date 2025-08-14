"""Controlador de Logística"""

from PyQt6.QtCore import QObject
from rexus.utils.error_handler import error_boundary as safe_method_decorator
from rexus.core.auth_manager import auth_required


class LogisticaController(QObject):
    def __init__(self,
model=None,
        view=None,
        db_connection=None,
        usuarios_model=None):
        super().__init__()
        self.model = model
        self.view = view
        self.db_connection = db_connection
        self.usuarios_model = usuarios_model
        self.usuario_actual = "SISTEMA"

        # Conectar señales de la vista
        if self.view:
            self.conectar_senales_vista()

    def conectar_senales_vista(self):
        """Conecta todas las señales de la vista con sus métodos correspondientes."""
        try:
            # Verificar que la vista existe antes de conectar señales
            if not self.view:
                return

            # Señales existentes
            if hasattr(self.view, 'crear_entrega_solicitada'):
                self.view.crear_entrega_solicitada.connect(self.guardar_entrega)

            # Nuevas señales para transportes
            if hasattr(self.view, 'solicitud_crear_transporte'):
                self.view.solicitud_crear_transporte.connect(self.crear_transporte)
            if hasattr(self.view, 'solicitud_actualizar_transporte'):
                self.view.solicitud_actualizar_transporte.connect(self.actualizar_transporte)
            if hasattr(self.view, 'solicitud_eliminar_transporte'):
                self.view.solicitud_eliminar_transporte.connect(self.eliminar_transporte)
            if hasattr(self.view, 'solicitud_actualizar_estadisticas'):
                self.view.solicitud_actualizar_estadisticas.connect(self.cargar_estadisticas)
        except Exception as e:
            print(f"Error conectando señales: {e}")

    @safe_method_decorator
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

    @auth_required
    def guardar_entrega(self, datos):
        """Guarda una nueva entrega."""
        if self.model:
            try:
                self.model.crear_entrega(datos)
                self.cargar_entregas()
                if self.view:
                    from rexus.utils.message_system import show_success
                    show_success(self.view, "Logística", "Entrega guardada exitosamente")
            except Exception as e:
                if self.view:
                    from rexus.utils.message_system import show_error
                    show_error(self.view, "Error", f"Error al guardar entrega: {str(e)}")
                else:
                    print(f"Error al guardar entrega: {e}")

    def cargar_services(self):
        """Carga los servicios en la tabla."""
        if self.model and self.view and hasattr(self.model, 'obtener_services'):
            try:
                services = self.model.obtener_services()
                self.view.cargar_services_en_tabla(services)
            except Exception as e:
                print(f"Error cargando servicios: {e}")

    @auth_required
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

    # Nuevos métodos para manejo de transportes
    @auth_required
    def crear_transporte(self, datos):
        """Crea un nuevo transporte."""
        try:
            if self.model and hasattr(self.model, 'crear_transporte'):
                resultado = self.model.crear_transporte(datos)
                if resultado:
                    print("[OK] Transporte creado exitosamente")
                    self.cargar_datos_iniciales()
                else:
                    print("[ERROR] Error al crear el transporte")
            else:
                # Simulación para pruebas
                print("[OK] Transporte creado exitosamente (simulado)")
                if self.view and \
                    hasattr(self.view, 'actualizar_tabla_transportes'):
                    self.view.actualizar_tabla_transportes()
        except Exception as e:
            print(f"[ERROR] Error al crear transporte: {str(e)}")

    @auth_required
    def actualizar_transporte(self, datos):
        """Actualiza un transporte existente."""
        try:
            if self.model and hasattr(self.model, 'actualizar_transporte'):
                resultado = self.model.actualizar_transporte(datos)
                if resultado:
                    print("[OK] Transporte actualizado exitosamente")
                    self.cargar_datos_iniciales()
                else:
                    print("[ERROR] Error al actualizar el transporte")
            else:
                # Simulación para pruebas
                print("[OK] Transporte actualizado exitosamente (simulado)")
                if self.view and \
                    hasattr(self.view, 'actualizar_tabla_transportes'):
                    self.view.actualizar_tabla_transportes()
        except Exception as e:
            print(f"[ERROR] Error al actualizar transporte: {str(e)}")

    @auth_required
    def eliminar_transporte(self, transporte_id):
        """Elimina un transporte."""
        try:
            if self.model and hasattr(self.model, 'eliminar_transporte'):
                resultado = self.model.eliminar_transporte(transporte_id)
                if resultado:
                    print("[OK] Transporte eliminado exitosamente")
                    self.cargar_datos_iniciales()
                else:
                    print("[ERROR] Error al eliminar el transporte")
            else:
                # Simulación para pruebas
                print("[OK] Transporte eliminado exitosamente (simulado)")
                if self.view and \
                    hasattr(self.view, 'actualizar_tabla_transportes'):
                    self.view.actualizar_tabla_transportes()
        except Exception as e:
            print(f"[ERROR] Error al eliminar transporte: {str(e)}")

    def buscar_transportes(self, termino, estado):
        """Busca transportes según criterios."""
        try:
            if self.model and hasattr(self.model, 'buscar_transportes'):
                transportes = self.model.buscar_transportes(termino, estado)
                if self.view:
                    self.view.cargar_transportes(transportes)
            else:
                # Simulación para pruebas
                transportes_simulados = [
                    {
                        'id': 1,
                        'origen': 'Ciudad A',
                        'destino': 'Ciudad B',
                        'estado': estado or 'En tránsito',
                        'conductor': 'Juan Pérez',
                        'fecha': '2025-01-15'
                    }
                ]
                if self.view:
                    self.view.cargar_transportes(transportes_simulados)
        except Exception as e:
            print(f"Error buscando transportes: {e}")

    def cargar_estadisticas(self):
        """Carga y actualiza las estadísticas del dashboard."""
        try:
            if self.model and hasattr(self.model, 'obtener_estadisticas'):
                stats = self.model.obtener_estadisticas()
            else:
                # Simulación para pruebas - valores estáticos para evitar warnings de seguridad
                stats = {
                    'total_transportes': 156,
                    'en_transito': 23,
                    'entregados_hoy': 8,
                    'pendientes': 12
                }

            if self.view:
                self.view.actualizar_estadisticas(stats)
        except Exception as e:
            print(f"Error cargando estadísticas: {e}")
