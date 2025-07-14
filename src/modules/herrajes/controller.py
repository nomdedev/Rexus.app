"""
Controlador de Herrajes

Maneja la lógica entre el modelo y la vista para herrajes.
"""

from PyQt6.QtCore import QObject, pyqtSlot
from PyQt6.QtWidgets import QMessageBox


class HerrajesController(QObject):
    """Controlador para la gestión de herrajes."""

    def __init__(self, model=None, view=None, db_connection=None, usuarios_model=None):
        super().__init__()
        self.model = model
        self.view = view
        self.db_connection = db_connection
        self.usuarios_model = usuarios_model
        self.usuario_actual = "SISTEMA"

        # Conectar señales si la vista está disponible
        if self.view:
            self.connect_signals()

        # Cargar datos iniciales
        self.cargar_datos_iniciales()

    def connect_signals(self):
        """Conecta las señales de la vista con los métodos del controlador."""
        if hasattr(self.view, "buscar_herrajes"):
            self.view.buscar_herrajes.connect(self.buscar_herrajes)
        if hasattr(self.view, "filtrar_herrajes"):
            self.view.filtrar_herrajes.connect(self.aplicar_filtros)
        if hasattr(self.view, "asignar_herraje_obra"):
            self.view.asignar_herraje_obra.connect(self.asignar_herraje_obra)
        if hasattr(self.view, "crear_pedido_obra"):
            self.view.crear_pedido_obra.connect(self.crear_pedido_obra)
        if hasattr(self.view, "obtener_estadisticas"):
            self.view.obtener_estadisticas.connect(self.cargar_estadisticas)

    def cargar_datos_iniciales(self):
        """Carga los datos iniciales en la vista."""
        print("[HERRAJES CONTROLLER] Cargando datos iniciales...")

        try:
            # Cargar herrajes
            herrajes = self.model.obtener_todos_herrajes() if self.model else []

            if self.view and hasattr(self.view, "cargar_herrajes_en_tabla"):
                self.view.cargar_herrajes_en_tabla(herrajes)

            # Cargar estadísticas
            self.cargar_estadisticas()

            print(
                f"[HERRAJES CONTROLLER] Datos iniciales cargados: {len(herrajes)} herrajes"
            )

        except Exception as e:
            print(f"[ERROR HERRAJES CONTROLLER] Error cargando datos iniciales: {e}")
            if self.view and hasattr(self.view, "show_error"):
                self.view.show_error(f"Error cargando datos: {e}")

    def cargar_estadisticas(self):
        """Carga las estadísticas en la vista."""
        try:
            if self.model:
                estadisticas = self.model.obtener_estadisticas()
            else:
                estadisticas = {
                    "total_herrajes": 0,
                    "proveedores_activos": 0,
                    "valor_total_inventario": 0.0,
                    "pedidos_pendientes": 0,
                }

            if self.view and hasattr(self.view, "actualizar_estadisticas"):
                self.view.actualizar_estadisticas(estadisticas)

        except Exception as e:
            print(f"[ERROR HERRAJES CONTROLLER] Error cargando estadísticas: {e}")

    @pyqtSlot(str)
    def buscar_herrajes(self, termino_busqueda):
        """Busca herrajes por término de búsqueda."""
        try:
            if self.model:
                herrajes = self.model.buscar_herrajes(termino_busqueda)
            else:
                herrajes = []

            if self.view and hasattr(self.view, "cargar_herrajes_en_tabla"):
                self.view.cargar_herrajes_en_tabla(herrajes)

        except Exception as e:
            print(f"[ERROR HERRAJES CONTROLLER] Error buscando herrajes: {e}")
            if self.view and hasattr(self.view, "show_error"):
                self.view.show_error(f"Error en búsqueda: {e}")

    @pyqtSlot(dict)
    def aplicar_filtros(self, filtros):
        """Aplica filtros a la lista de herrajes."""
        try:
            if self.model:
                herrajes = self.model.obtener_todos_herrajes(filtros)
            else:
                herrajes = []

            if self.view and hasattr(self.view, "cargar_herrajes_en_tabla"):
                self.view.cargar_herrajes_en_tabla(herrajes)

        except Exception as e:
            print(f"[ERROR HERRAJES CONTROLLER] Error aplicando filtros: {e}")
            if self.view and hasattr(self.view, "show_error"):
                self.view.show_error(f"Error aplicando filtros: {e}")

    @pyqtSlot(int, int, float, str)
    def asignar_herraje_obra(
        self, herraje_id, obra_id, cantidad_requerida, observaciones
    ):
        """Asigna un herraje a una obra específica."""
        try:
            if self.model:
                exito = self.model.asignar_herraje_obra(
                    herraje_id, obra_id, cantidad_requerida, observaciones
                )

                if exito:
                    if self.view and hasattr(self.view, "show_success"):
                        self.view.show_success("Herraje asignado a obra exitosamente")
                    self.cargar_datos_iniciales()  # Recargar datos
                else:
                    if self.view and hasattr(self.view, "show_error"):
                        self.view.show_error("Error asignando herraje a obra")
            else:
                if self.view and hasattr(self.view, "show_error"):
                    self.view.show_error("No hay conexión a base de datos")

        except Exception as e:
            print(f"[ERROR HERRAJES CONTROLLER] Error asignando herraje a obra: {e}")
            if self.view and hasattr(self.view, "show_error"):
                self.view.show_error(f"Error asignando herraje: {e}")

    @pyqtSlot(int, str, list)
    def crear_pedido_obra(self, obra_id, proveedor, herrajes_lista):
        """Crea un pedido de herrajes para una obra."""
        try:
            if self.model:
                pedido_id = self.model.crear_pedido_obra(
                    obra_id, proveedor, herrajes_lista
                )

                if pedido_id:
                    if self.view and hasattr(self.view, "show_success"):
                        self.view.show_success(
                            f"Pedido #{pedido_id} creado exitosamente"
                        )
                    self.cargar_datos_iniciales()  # Recargar datos
                else:
                    if self.view and hasattr(self.view, "show_error"):
                        self.view.show_error("Error creando pedido")
            else:
                if self.view and hasattr(self.view, "show_error"):
                    self.view.show_error("No hay conexión a base de datos")

        except Exception as e:
            print(f"[ERROR HERRAJES CONTROLLER] Error creando pedido: {e}")
            if self.view and hasattr(self.view, "show_error"):
                self.view.show_error(f"Error creando pedido: {e}")

    def obtener_herrajes_por_obra(self, obra_id):
        """Obtiene herrajes asociados a una obra específica."""
        try:
            if self.model:
                return self.model.obtener_herrajes_por_obra(obra_id)
            else:
                return []

        except Exception as e:
            print(
                f"[ERROR HERRAJES CONTROLLER] Error obteniendo herrajes por obra: {e}"
            )
            return []

    def mostrar_estadisticas_detalladas(self):
        """Muestra estadísticas detalladas en un diálogo."""
        try:
            if self.model:
                estadisticas = self.model.obtener_estadisticas()

                # Crear mensaje con estadísticas detalladas
                mensaje = f"""
ESTADÍSTICAS DETALLADAS DE HERRAJES

📊 Resumen General:
• Total de herrajes: {estadisticas["total_herrajes"]}
• Proveedores activos: {estadisticas["proveedores_activos"]}
• Valor total inventario: ${estadisticas["valor_total_inventario"]:.2f}

🏪 Herrajes por Proveedor:
"""

                for proveedor_info in estadisticas["herrajes_por_proveedor"]:
                    mensaje += f"• {proveedor_info['proveedor']}: {proveedor_info['cantidad']} herrajes\n"

                # Mostrar en un diálogo
                msg_box = QMessageBox()
                msg_box.setWindowTitle("Estadísticas Detalladas - Herrajes")
                msg_box.setText(mensaje)
                msg_box.setIcon(QMessageBox.Icon.Information)
                msg_box.exec()

            else:
                if self.view and hasattr(self.view, "show_error"):
                    self.view.show_error("No hay conexión a base de datos")

        except Exception as e:
            print(f"[ERROR HERRAJES CONTROLLER] Error mostrando estadísticas: {e}")
            if self.view and hasattr(self.view, "show_error"):
                self.view.show_error(f"Error mostrando estadísticas: {e}")

    def actualizar_datos(self):
        """Actualiza todos los datos de la vista."""
        self.cargar_datos_iniciales()

    def get_herrajes_data(self):
        """Obtiene datos de herrajes para uso externo."""
        try:
            if self.model:
                return self.model.obtener_todos_herrajes()
            else:
                return []

        except Exception as e:
            print(f"[ERROR HERRAJES CONTROLLER] Error obteniendo datos: {e}")
            return []
