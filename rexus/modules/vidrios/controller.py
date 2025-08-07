"""Controlador de Vidrios"""

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QMessageBox
from rexus.core.auth_decorators import auth_required, admin_required, permission_required

class VidriosController(QObject):
    
    vidrio_agregado = pyqtSignal(dict)
    vidrio_actualizado = pyqtSignal(dict)
    vidrio_eliminado = pyqtSignal(int)
    pedido_creado = pyqtSignal(int)
    
    def __init__(self, model=None, view=None, db_connection=None):
        super().__init__()
        self.model = model
        self.view = view
        self.db_connection = db_connection
        self.usuario_actual = "SISTEMA"
        self.conectar_senales()

    def conectar_senales(self):
        """Conecta las señales de la vista con los métodos del controlador."""
        if self.view:
            self.view.buscar_requested.connect(self.buscar_vidrios)
            self.view.agregar_requested.connect(self.agregar_vidrio)
            self.view.editar_requested.connect(self.editar_vidrio)
            self.view.eliminar_requested.connect(self.eliminar_vidrio)
            self.view.asignar_obra_requested.connect(self.asignar_vidrio_obra)
            self.view.crear_pedido_requested.connect(self.crear_pedido)
            self.view.filtrar_requested.connect(self.filtrar_vidrios)

    def cargar_datos(self, filtros=None):
        """Carga los datos de vidrios en la vista."""
        if not self.model:
            return
            
        try:
            vidrios = self.model.obtener_todos_vidrios(filtros)
            if self.view:
                self.view.actualizar_tabla(vidrios)
                
            # Cargar estadísticas
            estadisticas = self.model.obtener_estadisticas()
            if self.view:
                self.view.actualizar_estadisticas(estadisticas)
                
        except Exception as e:
            self.mostrar_error(f"Error cargando datos: {e}")
    
    def cargar_datos_iniciales(self):
        """Carga los datos iniciales de vidrios."""
        self.cargar_datos()

    def buscar_vidrios(self, termino):
        """Busca vidrios por término de búsqueda."""
        if not self.model:
            return
            
        try:
            vidrios = self.model.buscar_vidrios(termino)
            if self.view:
                self.view.actualizar_tabla(vidrios)
        except Exception as e:
            self.mostrar_error(f"Error en búsqueda: {e}")

    def agregar_vidrio(self, datos_vidrio):
        """Agrega un nuevo vidrio."""
        if not self.model:
            return
            
        try:
            vidrio_id = self.model.crear_vidrio(datos_vidrio)
            if vidrio_id:
                self.mostrar_mensaje("Vidrio agregado exitosamente")
                self.cargar_datos()
                self.vidrio_agregado.emit(datos_vidrio)
            else:
                self.mostrar_error("Error al agregar vidrio")
        except Exception as e:
            self.mostrar_error(f"Error agregando vidrio: {e}")

    def editar_vidrio(self, vidrio_id, datos_vidrio):
        """Edita un vidrio existente."""
        if not self.model:
            return
            
        try:
            if self.model.actualizar_vidrio(vidrio_id, datos_vidrio):
                self.mostrar_mensaje("Vidrio actualizado exitosamente")
                self.cargar_datos()
                self.vidrio_actualizado.emit(datos_vidrio)
            else:
                self.mostrar_error("Error al actualizar vidrio")
        except Exception as e:
            self.mostrar_error(f"Error editando vidrio: {e}")

    @admin_required
    def eliminar_vidrio(self, vidrio_id):
        """Elimina un vidrio."""
        if not self.model:
            return
            
        try:
            if self.model.eliminar_vidrio(vidrio_id):
                self.mostrar_mensaje("Vidrio eliminado exitosamente")
                self.cargar_datos()
                self.vidrio_eliminado.emit(vidrio_id)
            else:
                self.mostrar_error("Error al eliminar vidrio")
        except Exception as e:
            self.mostrar_error(f"Error eliminando vidrio: {e}")

    def asignar_vidrio_obra(self, vidrio_id, obra_id, metros_cuadrados, medidas_especificas=None):
        """Asigna un vidrio a una obra específica."""
        if not self.model:
            return
            
        try:
            if self.model.asignar_vidrio_obra(vidrio_id, obra_id, metros_cuadrados, medidas_especificas):
                self.mostrar_mensaje("Vidrio asignado a la obra exitosamente")
            else:
                self.mostrar_error("Error al asignar vidrio a la obra")
        except Exception as e:
            self.mostrar_error(f"Error asignando vidrio a obra: {e}")

    @auth_required
    def crear_pedido(self, obra_id, proveedor, vidrios_lista):
        """Crea un pedido de vidrios para una obra."""
        if not self.model:
            return
            
        try:
            pedido_id = self.model.crear_pedido_obra(obra_id, proveedor, vidrios_lista)
            if pedido_id:
                self.mostrar_mensaje(f"Pedido #{pedido_id} creado exitosamente")
                self.pedido_creado.emit(pedido_id)
            else:
                self.mostrar_error("Error al crear pedido")
        except Exception as e:
            self.mostrar_error(f"Error creando pedido: {e}")

    def filtrar_vidrios(self, filtros):
        """Filtra vidrios por criterios específicos."""
        self.cargar_datos(filtros)

    def obtener_vidrios_por_obra(self, obra_id):
        """Obtiene vidrios asignados a una obra específica."""
        if not self.model:
            return []
            
        try:
            return self.model.obtener_vidrios_por_obra(obra_id)
        except Exception as e:
            self.mostrar_error(f"Error obteniendo vidrios por obra: {e}")
            return []

    def actualizar_por_obra(self, obra_data):
        """Actualiza vidrios cuando se crea una obra."""
        print(f"[VIDRIOS] Actualizando por obra: {obra_data}")

    def mostrar_mensaje(self, mensaje):
        """Muestra un mensaje informativo."""
        if self.view:
            QMessageBox.information(self.view, "Vidrios", mensaje)

    def mostrar_error(self, mensaje):
        """Muestra un mensaje de error."""
        if self.view:
            QMessageBox.critical(self.view, "Error - Vidrios", mensaje)
        print(f"[ERROR VIDRIOS] {mensaje}")
