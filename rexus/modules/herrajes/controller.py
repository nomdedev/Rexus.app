"""
Controlador de Herrajes - Rexus.app v2.0.0

Maneja la lógica entre el modelo y la vista para herrajes.
"""

from typing import Any, Dict, List, Optional
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import QMessageBox
from rexus.core.auth_manager import auth_required, admin_required, manager_required

from .model import HerrajesModel


class HerrajesController(QObject):
    """Controlador para la gestión de herrajes."""
    
    # Señales para comunicación con otros módulos
    herraje_creado = pyqtSignal(dict)
    herraje_actualizado = pyqtSignal(dict)
    herraje_eliminado = pyqtSignal(int)
    stock_actualizado = pyqtSignal(int, int)

    def __init__(self, model=None, view=None, db_connection=None, usuario_actual=None):
        super().__init__()
        
        # Si model es pasado como primer parámetro (patrón MVC estándar)
        if model is not None:
            self.model = model
            self.view = view
        else:
            # Compatibilidad hacia atrás: view como primer parámetro
            self.view = model  # En este caso, 'model' es realmente 'view'
            self.model = HerrajesModel(db_connection)
            
        self.db_connection = db_connection
        self.usuario_actual = usuario_actual or {"id": 1, "nombre": "SISTEMA"}

        # Conectar señales si la vista está disponible
        if self.view:
            self.connect_signals()
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
        # 🔒 VERIFICACIÓN DE AUTORIZACIÓN REQUERIDA
        # TODO: Implementar @auth_required o verificación manual
        # if not AuthManager.check_permission('crear_pedido_obra'):
        #     raise PermissionError("Acceso denegado - Permisos insuficientes")

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
        # 🔒 VERIFICACIÓN DE AUTORIZACIÓN REQUERIDA
        # TODO: Implementar @auth_required o verificación manual
        # if not AuthManager.check_permission('actualizar_datos'):
        #     raise PermissionError("Acceso denegado - Permisos insuficientes")

        """Actualiza todos los datos de la vista."""
        self.cargar_datos_iniciales()

    def get_herrajes_data(self):
        """Obtiene datos de herrajes para uso externo."""
        try:
            return self.model.obtener_todos_herrajes()
        except Exception as e:
            print(f"[ERROR HERRAJES CONTROLLER] Error obteniendo datos: {e}")
            return []
    
    def crear_herraje(self, datos_herraje:
        # 🔒 VERIFICACIÓN DE AUTORIZACIÓN REQUERIDA
        # TODO: Implementar @auth_required o verificación manual
        # if not AuthManager.check_permission('crear_herraje'):
        #     raise PermissionError("Acceso denegado - Permisos insuficientes")
 Dict[str, Any]):
        """Crea un nuevo herraje."""
        try:
            exito, mensaje = self.model.crear_herraje(datos_herraje)
            
            if exito:
                self.mostrar_exito(mensaje)
                self.cargar_datos_iniciales()
                
                # Emitir señal
                herraje_creado = self.model.obtener_herraje_por_id(datos_herraje.get("id"))
                if herraje_creado:
                    self.herraje_creado.emit(herraje_creado)
            else:
                self.mostrar_error(mensaje)
                
        except Exception as e:
            print(f"[ERROR HERRAJES CONTROLLER] Error creando herraje: {e}")
            self.mostrar_error(f"Error creando herraje: {str(e)}")
    
    def actualizar_herraje(self, herraje_id:
        # 🔒 VERIFICACIÓN DE AUTORIZACIÓN REQUERIDA
        # TODO: Implementar @auth_required o verificación manual
        # if not AuthManager.check_permission('actualizar_herraje'):
        #     raise PermissionError("Acceso denegado - Permisos insuficientes")
 int, datos_herraje: Dict[str, Any]):
        """Actualiza un herraje existente."""
        try:
            exito, mensaje = self.model.actualizar_herraje(herraje_id, datos_herraje)
            
            if exito:
                self.mostrar_exito(mensaje)
                self.cargar_datos_iniciales()
                
                # Emitir señal
                herraje_actualizado = self.model.obtener_herraje_por_id(herraje_id)
                if herraje_actualizado:
                    self.herraje_actualizado.emit(herraje_actualizado)
            else:
                self.mostrar_error(mensaje)
                
        except Exception as e:
            print(f"[ERROR HERRAJES CONTROLLER] Error actualizando herraje: {e}")
            self.mostrar_error(f"Error actualizando herraje: {str(e)}")
    
    def eliminar_herraje(self, herraje_id:
        # 🔒 VERIFICACIÓN DE AUTORIZACIÓN REQUERIDA
        # TODO: Implementar @auth_required o verificación manual
        # if not AuthManager.check_permission('eliminar_herraje'):
        #     raise PermissionError("Acceso denegado - Permisos insuficientes")
 int):
        """Elimina un herraje."""
        try:
            # Confirmar eliminación
            if self.view:
                respuesta = QMessageBox.question(
                    self.view,
                    "Confirmar eliminación",
                    f"¿Está seguro de eliminar el herraje con ID {herraje_id}?\n\n"
                    "Esta acción no se puede deshacer.",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                
                if respuesta == QMessageBox.StandardButton.Yes:
                    exito, mensaje = self.model.eliminar_herraje(herraje_id)
                    
                    if exito:
                        self.mostrar_exito(mensaje)
                        self.cargar_datos_iniciales()
                        self.herraje_eliminado.emit(herraje_id)
                    else:
                        self.mostrar_error(mensaje)
                
        except Exception as e:
            print(f"[ERROR HERRAJES CONTROLLER] Error eliminando herraje: {e}")
            self.mostrar_error(f"Error eliminando herraje: {str(e)}")
    
    def actualizar_stock_herraje(self, herraje_id:
        # 🔒 VERIFICACIÓN DE AUTORIZACIÓN REQUERIDA
        # TODO: Implementar @auth_required o verificación manual
        # if not AuthManager.check_permission('actualizar_stock_herraje'):
        #     raise PermissionError("Acceso denegado - Permisos insuficientes")
 int, nuevo_stock: int, tipo_movimiento: str = "AJUSTE"):
        """Actualiza el stock de un herraje."""
        try:
            exito, mensaje = self.model.actualizar_stock(herraje_id, nuevo_stock, tipo_movimiento)
            
            if exito:
                self.mostrar_exito(mensaje)
                self.cargar_datos_iniciales()
                self.stock_actualizado.emit(herraje_id, nuevo_stock)
            else:
                self.mostrar_error(mensaje)
                
        except Exception as e:
            print(f"[ERROR HERRAJES CONTROLLER] Error actualizando stock: {e}")
            self.mostrar_error(f"Error actualizando stock: {str(e)}")
    
    def obtener_herraje_por_id(self, herraje_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene un herraje por su ID."""
        try:
            return self.model.obtener_herraje_por_id(herraje_id)
        except Exception as e:
            print(f"[ERROR HERRAJES CONTROLLER] Error obteniendo herraje: {e}")
            return None
    
    def obtener_proveedores(self) -> List[str]:
        """Obtiene la lista de proveedores."""
        try:
            return self.model.obtener_proveedores()
        except Exception as e:
            print(f"[ERROR HERRAJES CONTROLLER] Error obteniendo proveedores: {e}")
            return []
    
    def obtener_tipos_herrajes(self) -> List[str]:
        """Obtiene la lista de tipos de herrajes."""
        return list(self.model.TIPOS_HERRAJES.keys())
    
    def obtener_estados_herrajes(self) -> List[str]:
        """Obtiene la lista de estados de herrajes."""
        return list(self.model.ESTADOS.keys())
    
    def obtener_unidades_medida(self) -> List[str]:
        """Obtiene la lista de unidades de medida."""
        return list(self.model.UNIDADES.keys())
    
    def set_usuario_actual(self, usuario: Dict[str, Any]):
        """Establece el usuario actual."""
        self.usuario_actual = usuario
        print(f"[HERRAJES CONTROLLER] Usuario actual: {usuario.get('nombre', 'Desconocido')}")
    
    def mostrar_exito(self, mensaje: str):
        """Muestra un mensaje de éxito."""
        if self.view and hasattr(self.view, "show_success"):
            self.view.show_success(mensaje)
    
    def mostrar_error(self, mensaje: str):
        """Muestra un mensaje de error."""
        if self.view and hasattr(self.view, "show_error"):
            self.view.show_error(mensaje)
    
    def mostrar_advertencia(self, mensaje: str):
        """Muestra un mensaje de advertencia."""
        if self.view:
            QMessageBox.warning(self.view, "Advertencia", mensaje)
    
    def mostrar_info(self, mensaje: str):
        """Muestra un mensaje informativo."""
        if self.view:
            QMessageBox.information(self.view, "Información", mensaje)
    
    def get_view(self):
        """Retorna la vista del módulo."""
        return self.view
    
    def cleanup(self):
        """Limpia recursos al cerrar el módulo."""
        try:
            print("[HERRAJES CONTROLLER] Limpiando recursos...")
            # Desconectar señales si es necesario
            # Cerrar conexiones, etc.
        except Exception as e:
            print(f"[ERROR HERRAJES CONTROLLER] Error en cleanup: {e}")
