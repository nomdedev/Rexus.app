"""
Controlador de Pedidos - Rexus.app v2.0.0

Maneja la lógica de negocio entre la vista y el modelo de pedidos.
"""

import datetime
from typing import Any, Dict, List, Optional

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QMessageBox

# Importar sistema de mensajería centralizado y logging
try:
    from rexus.utils.message_system import show_success, show_error, show_warning, show_info
    MESSAGING_AVAILABLE = True
except ImportError:
    # Fallback temporal con QMessageBox
    def show_success(parent, title, message): QMessageBox.information(parent, title, message)
    def show_error(parent, title, message): QMessageBox.critical(parent, title, message)
    def show_warning(parent, title, message): QMessageBox.warning(parent, title, message)
    def show_info(parent, title, message): QMessageBox.information(parent, title, message)
    MESSAGING_AVAILABLE = False

try:
    from rexus.utils.app_logger import get_logger
    logger = get_logger("pedidos.controller")
    LOGGING_AVAILABLE = True
except ImportError:
    # Fallback para logging
    class DummyLogger:
        def info(self, msg): print(f"[INFO] {msg}")
        def warning(self, msg): print(f"[WARNING] {msg}")
        def error(self, msg): print(f"[ERROR] {msg}")
        def debug(self, msg): print(f"[DEBUG] {msg}")
    logger = DummyLogger()
    LOGGING_AVAILABLE = False

# Importar decoradores de autenticación
try:
    from rexus.core.auth_decorators import auth_required, admin_required
except ImportError:
    def auth_required(func): return func
    def admin_required(func): return func


class PedidosController(QObject):
    """Controlador para el módulo de pedidos."""

    # Señales para comunicación con otros módulos
    pedido_creado = pyqtSignal(dict)
    pedido_actualizado = pyqtSignal(dict)
    pedido_eliminado = pyqtSignal(int)
    estado_cambiado = pyqtSignal(int, str)

    def __init__(self, model=None, view=None, usuario_actual=None):
        super().__init__()
        
        # Crear modelo si no se proporciona
        if model is None:
            from rexus.modules.pedidos.model import PedidosModel
            model = PedidosModel()
            
        self.model = model
        self.view = view
        self.db_connection = model.db_connection if model else None
        self.usuario_actual = usuario_actual or {"id": 1, "nombre": "SISTEMA"}

        # Conectar señales si hay vista
        if self.view:
            self.conectar_señales()
            self.cargar_pedidos()

    def conectar_señales(self):
        """Conecta las señales entre vista y controlador."""
        if not self.view:
            return

        # Señales de la vista
        if hasattr(self.view, "solicitud_crear_pedido"):
            self.view.solicitud_crear_pedido.connect(self.crear_pedido)
        if hasattr(self.view, "solicitud_actualizar_pedido"):
            self.view.solicitud_actualizar_pedido.connect(self.actualizar_pedido)
        if hasattr(self.view, "solicitud_eliminar_pedido"):
            self.view.solicitud_eliminar_pedido.connect(self.eliminar_pedido)
        if hasattr(self.view, "solicitud_cambiar_estado"):
            self.view.solicitud_cambiar_estado.connect(self.cambiar_estado)

        # Establecer controlador en la vista
        self.view.set_controller(self)

    def cargar_datos_iniciales(self):
        """Carga los datos iniciales de pedidos."""
        self.cargar_pedidos()

    def cargar_pedidos(self, filtros: Optional[Dict[str, Any]] = None):
        """Carga los pedidos desde el modelo."""
        try:
            pedidos = self.model.obtener_pedidos(filtros)

            if self.view and hasattr(self.view, "cargar_pedidos_en_tabla"):
                self.view.cargar_pedidos_en_tabla(pedidos)

            # Actualizar estadísticas
            self.actualizar_estadisticas()

            print(f"[PEDIDOS CONTROLLER] Cargados {len(pedidos)} pedidos")

        except Exception as e:
            print(f"[ERROR PEDIDOS CONTROLLER] Error cargando pedidos: {e}")
            self.mostrar_error(f"Error cargando pedidos: {str(e)}")

    def crear_pedido(self, datos_pedido:Dict[str, Any]):
        """Crea un nuevo pedido."""
        try:
            # Validar datos
            if not self.validar_datos_pedido(datos_pedido):
                return

            # Agregar usuario creador
            datos_pedido["usuario_creador"] = self.usuario_actual.get("id", 1)

            # Crear pedido
            pedido_id = self.model.crear_pedido(datos_pedido)

            if pedido_id:
                self.mostrar_exito("Pedido creado exitosamente")
                self.cargar_pedidos()

                # Emitir señal
                pedido = self.model.obtener_pedido_por_id(pedido_id)
                if pedido:
                    self.pedido_creado.emit(pedido)

                # Volver a la lista
                if self.view and hasattr(self.view, "tab_widget"):
                    self.view.tab_widget.setCurrentIndex(0)
            else:
                self.mostrar_error("No se pudo crear el pedido")

        except Exception as e:
            print(f"[ERROR PEDIDOS CONTROLLER] Error creando pedido: {e}")
            self.mostrar_error(f"Error creando pedido: {str(e)}")

    @auth_required
    def actualizar_pedido(self, datos_pedido:Dict[str, Any]):
        """Actualiza un pedido existente."""
        try:
            if not datos_pedido.get("id"):
                self.mostrar_error("ID de pedido requerido para actualización")
                return

            # Validar datos
            if not self.validar_datos_pedido(datos_pedido, es_actualizacion=True):
                return

            # Implementar actualización de pedidos
            logger.info(f"Actualizando pedido ID: {pedido_id}")
            
            # Agregar información de auditoría
            datos_pedido['usuario_modificacion'] = self.usuario_actual.get('id', 1)
            datos_pedido['fecha_modificacion'] = datetime.datetime.now()
            
            if self.model.actualizar_pedido(pedido_id, datos_pedido):
                success_msg = "Pedido actualizado exitosamente"
                logger.info(f"Pedido {pedido_id} actualizado correctamente")
                
                self.mostrar_mensaje(success_msg, "success")
                self.pedido_actualizado.emit({"id": pedido_id, **datos_pedido})
                self.cargar_pedidos()  # Recargar vista
            else:
                error_msg = "No se pudo actualizar el pedido"
                logger.error(f"Fallo al actualizar pedido {pedido_id}")
                self.mostrar_error(error_msg)

        except Exception as e:
            logger.error(f"Error actualizando pedido: {e}", exc_info=True)
            self.mostrar_error(f"Error actualizando pedido: {str(e)}")

    @admin_required
    def eliminar_pedido(self, pedido_id:str):
        """Elimina un pedido."""
        try:
            # Confirmar eliminación
            if self.view:
                respuesta = QMessageBox.question(
                    self.view,
                    "Confirmar eliminación",
                    f"¿Está seguro de eliminar el pedido {pedido_id}?\\n\\n"
                    "Esta acción no se puede deshacer.",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No,
                )

                if respuesta == QMessageBox.StandardButton.Yes:
                    # Implementar eliminación de pedidos
                    logger.info(f"Eliminando pedido ID: {pedido_id}")
                    
                    if self.model.eliminar_pedido(pedido_id):
                        success_msg = f"Pedido {pedido_id} eliminado exitosamente"
                        logger.info(f"Pedido {pedido_id} eliminado correctamente")
                        
                        self.mostrar_mensaje(success_msg, "success")
                        self.pedido_eliminado.emit(int(pedido_id))
                        self.cargar_pedidos()  # Recargar vista
                    else:
                        error_msg = f"No se pudo eliminar el pedido {pedido_id}"
                        logger.error(f"Fallo al eliminar pedido {pedido_id}")
                        self.mostrar_error(error_msg)

        except Exception as e:
            logger.error(f"Error eliminando pedido: {e}", exc_info=True)
            self.mostrar_error(f"Error eliminando pedido: {str(e)}")

    def cambiar_estado(self, pedido_id:str, nuevo_estado: str):
        """Cambia el estado de un pedido."""
        try:
            exito = self.model.actualizar_estado_pedido(
                int(pedido_id),
                nuevo_estado,
                self.usuario_actual.get("id", 1),
                f"Estado cambiado a {nuevo_estado}",
            )

            if exito:
                self.mostrar_exito(f"Estado cambiado a {nuevo_estado}")
                self.cargar_pedidos()
                self.estado_cambiado.emit(int(pedido_id), nuevo_estado)
            else:
                self.mostrar_error("No se pudo cambiar el estado del pedido")

        except Exception as e:
            print(f"[ERROR PEDIDOS CONTROLLER] Error cambiando estado: {e}")
            self.mostrar_error(f"Error cambiando estado: {str(e)}")

    def actualizar_estadisticas(self):
        """Actualiza las estadísticas del módulo."""
        try:
            stats = self.model.obtener_estadisticas()

            # Actualizar estadísticas en la vista
            if self.view and \
                hasattr(self.view, "actualizar_estadisticas_completas"):
                self.view.actualizar_estadisticas_completas(stats)

        except Exception as e:
            print(f"[ERROR PEDIDOS CONTROLLER] Error actualizando estadísticas: {e}")

    def validar_datos_pedido(
        self, datos: Dict[str, Any], es_actualizacion: bool = False
    ) -> bool:
        """Valida los datos del pedido."""
        errores = []

        # Validaciones básicas
        if not datos.get("tipo_pedido"):
            errores.append("Tipo de pedido es obligatorio")

        if not datos.get("prioridad"):
            errores.append("Prioridad es obligatoria")

        if not datos.get("responsable_entrega"):
            errores.append("Responsable de entrega es obligatorio")

        # Validar detalles del pedido
        detalles = datos.get("detalles", [])
        if not detalles:
            errores.append("El pedido debe tener al menos un producto")

        for i, detalle in enumerate(detalles):
            if not detalle.get("descripcion"):
                errores.append(f"Descripción requerida en producto {i + 1}")

            if not detalle.get("cantidad") or detalle["cantidad"] <= 0:
                errores.append(f"Cantidad debe ser mayor a 0 en producto {i + 1}")

            if not detalle.get("precio_unitario") or detalle["precio_unitario"] <= 0:
                errores.append(
                    f"Precio unitario debe ser mayor a 0 en producto {i + 1}"
                )

        # Validar fechas
        fecha_entrega = datos.get("fecha_entrega_solicitada")
        if fecha_entrega:
            if isinstance(fecha_entrega, str):
                try:
                    fecha_entrega = datetime.datetime.strptime(
                        fecha_entrega, "%Y-%m-%d"
                    ).date()
                except (ValueError, TypeError) as e:
                    errores.append(f"Formato de fecha de entrega inválido: {e}")

            if fecha_entrega and fecha_entrega < datetime.date.today():
                errores.append("La fecha de entrega no puede ser anterior a hoy")

        if errores:
            mensaje_error = "Errores de validación:\\n\\n" + "\\n".join(
                f"• {error}" for error in errores
            )
            self.mostrar_error(mensaje_error)
            return False

        return True

    def obtener_pedido_por_id(self, pedido_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene un pedido por su ID."""
        try:
            return self.model.obtener_pedido_por_id(pedido_id)
        except Exception as e:
            print(f"[ERROR PEDIDOS CONTROLLER] Error obteniendo pedido: {e}")
            return None

    def buscar_productos_inventario(self, busqueda: str) -> List[Dict[str, Any]]:
        """Busca productos en el inventario."""
        try:
            return self.model.buscar_productos_inventario(busqueda)
        except Exception as e:
            print(f"[ERROR PEDIDOS CONTROLLER] Error buscando productos: {e}")
            return []

    def obtener_estados_validos(self) -> List[str]:
        """Obtiene la lista de estados válidos."""
        return list(self.model.ESTADOS.keys())

    def obtener_tipos_pedido(self) -> List[str]:
        """Obtiene la lista de tipos de pedido."""
        return list(self.model.TIPOS_PEDIDO.keys())

    def obtener_prioridades(self) -> List[str]:
        """Obtiene la lista de prioridades."""
        return list(self.model.PRIORIDADES.keys())

    def set_usuario_actual(self, usuario: Dict[str, Any]):
        """Establece el usuario actual."""
        self.usuario_actual = usuario
        print(
            f"[PEDIDOS CONTROLLER] Usuario actual: {usuario.get('nombre', 'Desconocido')}"
        )

    def mostrar_exito(self, mensaje: str):
        """Muestra un mensaje de éxito."""
        logger.info(f"Éxito en pedidos: {mensaje}")
        self.mostrar_mensaje(mensaje, "success")


    def cargar_pagina(self, pagina, registros_por_pagina=50):
        """Carga una página específica de datos"""
        try:
            if self.model:
                offset = (pagina - 1) * registros_por_pagina

                # Obtener datos paginados
                datos, total_registros = self.model.obtener_datos_paginados(
                    offset=offset,
                    limit=registros_por_pagina
                )

                if self.view:
                    # Cargar datos en la tabla
                    if hasattr(self.view, 'cargar_en_tabla'):
                        self.view.cargar_en_tabla(datos)

                    # Actualizar controles de paginación
                    total_paginas = (total_registros + registros_por_pagina - 1) // registros_por_pagina
                    if hasattr(self.view, 'actualizar_controles_paginacion'):
                        self.view.actualizar_controles_paginacion(
                            pagina, total_paginas, total_registros, len(datos)
                        )

        except Exception as e:
            print(f"[ERROR] Error cargando página: {e}")
            if hasattr(self, 'mostrar_error'):
                self.mostrar_error("Error", f"Error cargando página: {str(e)}")

    def cambiar_registros_por_pagina(self, registros):
        """Cambia la cantidad de registros por página y recarga"""
        self.registros_por_pagina = registros
        self.cargar_pagina(1, registros)

    def obtener_total_registros(self):
        """Obtiene el total de registros disponibles"""
        try:
            if self.model:
                return self.model.obtener_total_registros()
            return 0
        except Exception as e:
            print(f"[ERROR] Error obteniendo total de registros: {e}")
            return 0

    def mostrar_error(self, mensaje: str):
        """Muestra un mensaje de error con logging."""
        logger.error(f"Error en pedidos: {mensaje}")
        
        if self.view:
            show_error(self.view, "Error - Pedidos", mensaje)
        else:
            # Fallback si no hay vista
            logger.error(f"[NO VIEW] Error: {mensaje}")

    def mostrar_advertencia(self, mensaje: str):
        """Muestra un mensaje de advertencia."""
        logger.warning(f"Advertencia en pedidos: {mensaje}")
        self.mostrar_mensaje(mensaje, "warning")

    def mostrar_info(self, mensaje: str):
        """Muestra un mensaje informativo."""
        logger.info(f"Info en pedidos: {mensaje}")
        self.mostrar_mensaje(mensaje, "info")

    def get_view(self):
        """Retorna la vista del módulo."""
        return self.view

    def mostrar_mensaje(self, mensaje, tipo="info"):
        """
        Muestra un mensaje usando el sistema centralizado.
        
        Args:
            mensaje: Mensaje a mostrar
            tipo: Tipo de mensaje ('info', 'success', 'warning', 'error')
        """
        logger.info(f"Mensaje mostrado: {mensaje}")
        
        if self.view:
            if tipo == "success":
                show_success(self.view, "Pedidos", mensaje)
            elif tipo == "warning":
                show_warning(self.view, "Pedidos", mensaje)
            elif tipo == "error":
                show_error(self.view, "Error - Pedidos", mensaje)
            else:
                show_info(self.view, "Pedidos", mensaje)

    def cleanup(self):
        """Limpia recursos al cerrar el módulo."""
        try:
            print("[PEDIDOS CONTROLLER] Limpiando recursos...")
            # Desconectar señales si es necesario
            # Cerrar conexiones, etc.
        except Exception as e:
            print(f"[ERROR PEDIDOS CONTROLLER] Error en cleanup: {e}")
