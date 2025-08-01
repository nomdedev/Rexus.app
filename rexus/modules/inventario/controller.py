"""
Controlador de Inventario

Maneja la lógica entre el modelo y la vista de inventario con sistema de reservas.
Integrado con el sistema de seguridad global.
"""

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QMessageBox

from rexus.core.security import get_security_manager
from rexus.utils.error_handler import ErrorHandler, safe_method_decorator


class InventarioController(QObject):
    """Controlador para el módulo de inventario con sistema de reservas."""

    # Señales
    datos_actualizados = pyqtSignal()
    error_ocurrido = pyqtSignal(str)
    reserva_creada = pyqtSignal(dict)
    reserva_liberada = pyqtSignal(int)

    def __init__(self, model=None, view=None, db_connection=None):
        super().__init__()
        self.model = model
        self.view = view
        self.db_connection = db_connection
        self.usuario_actual = "SISTEMA"
        self.security_manager = get_security_manager()

        # Conectar señales de la vista
        if self.view:
            self.view.set_controller(self)
            self.conectar_senales()

    def set_security_manager(self, security_manager):
        """Establece el gestor de seguridad."""
        self.security_manager = security_manager

    def verificar_permiso(self, accion):
        """Verifica si el usuario tiene permiso para realizar una acción."""
        if not self.security_manager:
            return True  # Si no hay security manager, permitir todo

        # Mapear acciones a permisos
        permisos_requeridos = {
            "ver_inventario": "VER_INVENTARIO",
            "crear_producto": "CREAR_PRODUCTO",
            "editar_producto": "EDITAR_PRODUCTO",
            "eliminar_producto": "ELIMINAR_PRODUCTO",
            "movimiento_inventario": "MOVIMIENTO_INVENTARIO",
            "exportar_inventario": "EXPORTAR_INVENTARIO",
            "crear_reserva": "CREAR_RESERVA",
            "liberar_reserva": "LIBERAR_RESERVA",
            "ver_reservas": "VER_RESERVAS",
        }

        permiso_requerido = permisos_requeridos.get(accion)
        if not permiso_requerido:
            return True

        return self.security_manager.has_permission(permiso_requerido, "INVENTARIO")

    def mostrar_error_permiso(self, accion):
        """Muestra un mensaje de error por falta de permisos."""
        QMessageBox.warning(
            None,
            "Permisos Insuficientes",
            f"No tienes permisos para realizar la acción: {accion}\n"
            "Contacta al administrador del sistema.",
        )

    def log_auditoria(self, accion, descripcion, datos_adicionales=None):
        """Registra una acción en el log de auditoría."""
        if self.security_manager:
            usuario_actual = self.security_manager.get_current_user()
            if usuario_actual:
                # Manejar diferentes tipos de datos de usuario
                if isinstance(usuario_actual, dict):
                    usuario_id = usuario_actual.get("id", 0)
                elif isinstance(usuario_actual, str):
                    usuario_id = 0  # Usuario por defecto si es string
                else:
                    usuario_id = 0

                if isinstance(usuario_id, str):
                    usuario_id = int(usuario_id) if usuario_id.isdigit() else 0

                self.security_manager.log_security_event(
                    usuario_id=usuario_id,
                    accion=accion,
                    modulo="INVENTARIO",
                    detalles=f"{descripcion}. Datos: {datos_adicionales}",
                )

    def conectar_senales(self):
        """Conecta las señales de la vista con los métodos del controlador."""
        if self.view:
            # Conectar señales de búsqueda y filtros
            self.view.buscar_btn.clicked.connect(self.buscar_productos)
            self.view.limpiar_btn.clicked.connect(self.limpiar_filtros)

            # Conectar señales de acciones
            self.view.nuevo_producto_btn.clicked.connect(self.nuevo_producto)
            self.view.editar_producto_btn.clicked.connect(self.editar_producto)
            self.view.eliminar_producto_btn.clicked.connect(self.eliminar_producto)
            self.view.movimiento_btn.clicked.connect(self.registrar_movimiento)
            self.view.exportar_btn.clicked.connect(self.exportar_inventario)

    def inicializar(self):
        """Inicializa el controlador cargando datos iniciales."""
        try:
            self.cargar_datos_iniciales()
            self.cargar_obras()
            self.cargar_categorias()
            self.actualizar_estadisticas()
        except Exception as e:
            ErrorHandler.mostrar_error_operacion(self.view, "inicializar inventario", e)
            self.error_ocurrido.emit(f"Error al inicializar: {str(e)}")

    def cargar_datos_iniciales(self):
        """Carga los datos iniciales del inventario."""
        try:
            print("[INVENTARIO CONTROLLER] Iniciando carga de datos...")
            
            # Verificar componentes
            if not self.model:
                print("[INVENTARIO CONTROLLER] ERROR: No hay modelo disponible")
                self.error_ocurrido.emit("Error: No hay modelo disponible")
                return
                
            if not self.view:
                print("[INVENTARIO CONTROLLER] ERROR: No hay vista disponible")
                self.error_ocurrido.emit("Error: No hay vista disponible") 
                return
            
            # Obtener productos del modelo
            print("[INVENTARIO CONTROLLER] Obteniendo productos del modelo...")
            productos = self.model.obtener_todos_productos()
            print(f"[INVENTARIO CONTROLLER] Modelo retornó {len(productos)} productos")
            
            # Cargar en la vista
            if productos:
                print("[INVENTARIO CONTROLLER] Cargando productos en la tabla...")
                self.view.cargar_inventario_en_tabla(productos)
                print(f"[INVENTARIO CONTROLLER] Datos cargados exitosamente: {len(productos)} productos")
            else:
                print("[INVENTARIO CONTROLLER] ADVERTENCIA: No se obtuvieron productos del modelo")
                # Intentar cargar datos demo si no hay productos reales
                print("[INVENTARIO CONTROLLER] Intentando cargar datos demo...")
                datos_demo = self._get_datos_demo()
                self.view.cargar_inventario_en_tabla(datos_demo)
                print(f"[INVENTARIO CONTROLLER] Datos demo cargados: {len(datos_demo)} productos")

            # Cargar disponibilidad
            self.cargar_disponibilidad()
            print("[INVENTARIO CONTROLLER] Carga de datos completada")

        except Exception as e:
            print(f"[INVENTARIO CONTROLLER] ERROR en cargar_datos_iniciales: {e}")
            import traceback
            traceback.print_exc()
            self.error_ocurrido.emit(f"Error al cargar datos: {str(e)}")
    
    def _get_datos_demo(self):
        """Obtiene datos demo cuando no hay datos reales disponibles."""
        return [
            {
                'id': 1,
                'codigo': 'DEMO-001',
                'descripcion': 'Producto Demo 1',
                'categoria': 'Demo',
                'stock_actual': 100,
                'stock_minimo': 10,
                'precio_unitario': 25.50,
                'estado': 'ACTIVO',
                'ubicacion': 'Almacén Demo',
                'proveedor': 'Proveedor Demo'
            },
            {
                'id': 2,
                'codigo': 'DEMO-002', 
                'descripcion': 'Producto Demo 2',
                'categoria': 'Demo',
                'stock_actual': 50,
                'stock_minimo': 5,
                'precio_unitario': 15.75,
                'estado': 'ACTIVO',
                'ubicacion': 'Almacén Demo',
                'proveedor': 'Proveedor Demo'
            }
        ]

    def cargar_obras(self):
        """Carga las obras disponibles en el selector."""
        try:
            if self.model:
                obras = self.model.obtener_obras_activas()
                if self.view:
                    self.view.cargar_obras_en_selector(obras)
        except Exception as e:
            self.error_ocurrido.emit(f"Error al cargar obras: {str(e)}")

    def cargar_categorias(self):
        """Carga las categorías disponibles en los filtros."""
        try:
            if self.model:
                categorias = self.model.obtener_categorias()
                if self.view:
                    # Cargar en ambos combos de categorías
                    self.view.categoria_combo.clear()
                    self.view.categoria_combo.addItem("Todas")
                    for categoria in categorias:
                        self.view.categoria_combo.addItem(categoria)

                    self.view.categoria_filter.clear()
                    self.view.categoria_filter.addItem("Todas las categorías")
                    for categoria in categorias:
                        self.view.categoria_filter.addItem(categoria)
        except Exception as e:
            self.error_ocurrido.emit(f"Error al cargar categorías: {str(e)}")

    def actualizar_estadisticas(self):
        """Actualiza las estadísticas generales."""
        try:
            if self.model:
                stats = self.model.obtener_estadisticas_generales()
                if self.view:
                    self.view.actualizar_stats(stats)
        except Exception as e:
            self.error_ocurrido.emit(f"Error al actualizar estadísticas: {str(e)}")

    def buscar_productos(self):
        """Realiza búsqueda de productos."""
        try:
            if self.model and self.view:
                filtros = {
                    "busqueda": self.view.busqueda_input.text(),
                    "categoria": self.view.categoria_combo.currentText()
                    if self.view.categoria_combo.currentText() != "Todas"
                    else None,
                }

                productos = self.model.buscar_productos(filtros)
                self.view.cargar_inventario_en_tabla(productos)

        except Exception as e:
            self.error_ocurrido.emit(f"Error en búsqueda: {str(e)}")

    def filtrar_inventario(self, filtros=None):
        """Filtra el inventario según los criterios especificados."""
        try:
            if self.model and self.view:
                if filtros is None:
                    # Obtener filtros desde la vista
                    filtros = {
                        "busqueda": self.view.busqueda_input.text(),
                        "categoria": self.view.categoria_combo.currentText()
                        if self.view.categoria_combo.currentText() != "Todas"
                        else None,
                    }

                productos = self.model.buscar_productos(filtros)
                self.view.cargar_inventario_en_tabla(productos)

        except Exception as e:
            self.error_ocurrido.emit(f"Error al filtrar inventario: {str(e)}")

    def limpiar_filtros(self):
        """Limpia los filtros de búsqueda."""
        try:
            if self.view:
                self.view.busqueda_input.clear()
                self.view.categoria_combo.setCurrentIndex(0)

            self.cargar_datos_iniciales()

        except Exception as e:
            self.error_ocurrido.emit(f"Error al limpiar filtros: {str(e)}")

    def nuevo_producto(self):
        """Abre diálogo para agregar nuevo producto."""
        if not self.verificar_permiso("crear_producto"):
            self.mostrar_error_permiso("crear producto")
            return

        # TODO: Implementar diálogo de nuevo producto
        if self.view:
            self.view.show_info(
                "Próximamente", "Función de nuevo producto en desarrollo"
            )

        self.log_auditoria("CREAR_PRODUCTO", "Intento de crear nuevo producto")

    @safe_method_decorator
    def agregar_producto(self, datos_producto):
        """Agrega un nuevo producto al inventario."""
        if not self.verificar_permiso("crear_producto"):
            self.mostrar_error_permiso("crear producto")
            return

        try:
            if self.model:
                # Crear el producto usando el modelo
                exito = self.model.crear_producto(datos_producto)
                
                if exito:
                    if self.view:
                        self.view.show_success("Producto agregado correctamente")
                    
                    # Log de auditoría
                    self.log_auditoria(
                        "PRODUCTO_CREADO", 
                        f"Producto creado: {datos_producto.get('codigo', 'N/A')}", 
                        datos_producto
                    )
                    
                    # Recargar datos
                    self.cargar_datos_iniciales()
                    self.actualizar_estadisticas()
                    
                else:
                    if self.view:
                        self.view.show_error("Error al crear el producto en la base de datos")
            else:
                if self.view:
                    self.view.show_error("No hay conexión al modelo de datos")
                
        except Exception as e:
            error_msg = f"Error al agregar producto: {str(e)}"
            if self.view:
                self.view.show_error(error_msg)
            self.error_ocurrido.emit(error_msg)

    def editar_producto(self):
        """Abre diálogo para editar producto seleccionado."""
        if not self.verificar_permiso("editar_producto"):
            self.mostrar_error_permiso("editar producto")
            return

        # TODO: Implementar diálogo de edición
        if self.view:
            self.view.show_info("Próximamente", "Función de edición en desarrollo")

        self.log_auditoria("EDITAR_PRODUCTO", "Intento de editar producto")

    def eliminar_producto(self):
        """Elimina producto seleccionado."""
        if not self.verificar_permiso("eliminar_producto"):
            self.mostrar_error_permiso("eliminar producto")
            return

        # TODO: Implementar eliminación
        if self.view:
            self.view.show_info("Próximamente", "Función de eliminación en desarrollo")

        self.log_auditoria("ELIMINAR_PRODUCTO", "Intento de eliminar producto")

    def registrar_movimiento(self):
        """Registra movimiento de inventario."""
        if not self.verificar_permiso("movimiento_inventario"):
            self.mostrar_error_permiso("registrar movimiento")
            return

        # TODO: Implementar registro de movimientos
        if self.view:
            self.view.show_info("Próximamente", "Función de movimientos en desarrollo")

        self.log_auditoria("MOVIMIENTO_INVENTARIO", "Intento de registrar movimiento")

    def exportar_inventario(self):
        """Exporta inventario a archivo."""
        if not self.verificar_permiso("exportar_inventario"):
            self.mostrar_error_permiso("exportar inventario")
            return

        # TODO: Implementar exportación
        if self.view:
            self.view.show_info("Próximamente", "Función de exportación en desarrollo")

        self.log_auditoria("EXPORTAR_INVENTARIO", "Intento de exportar inventario")

    # Métodos para el sistema de reservas
    def cargar_reservas_obra(self, obra_id):
        """Carga las reservas de una obra específica."""
        if not self.verificar_permiso("ver_reservas"):
            self.mostrar_error_permiso("ver reservas")
            return

        try:
            if self.model:
                reservas = self.model.obtener_reservas_por_obra(obra_id)
                if self.view:
                    self.view.cargar_reservas_en_tabla(reservas)

                # Actualizar estadísticas de reservas
                stats = self.model.obtener_estadisticas_reservas(obra_id)
                if hasattr(self.view, "actualizar_stats_reservas"):
                    self.view.actualizar_stats_reservas(stats)

        except Exception as e:
            self.error_ocurrido.emit(f"Error al cargar reservas: {str(e)}")

    def crear_reserva(self, reserva_data):
        """Crea una nueva reserva de material."""
        if not self.verificar_permiso("crear_reserva"):
            self.mostrar_error_permiso("crear reserva")
            return

        try:
            if self.model:
                reserva_id = self.model.crear_reserva(reserva_data)
                if reserva_id:
                    self.reserva_creada.emit(reserva_data)
                    self.log_auditoria(
                        "CREAR_RESERVA",
                        f"Reserva creada para obra {reserva_data.get('obra_id')}",
                        reserva_data,
                    )

                    # Actualizar vista
                    self.cargar_reservas_obra(reserva_data.get("obra_id"))
                    self.cargar_disponibilidad()

                    if self.view:
                        self.view.show_success("Reserva creada exitosamente")
                else:
                    if self.view:
                        self.view.show_error("Error al crear la reserva")

        except Exception as e:
            self.error_ocurrido.emit(f"Error al crear reserva: {str(e)}")

    def liberar_reserva(self, reserva_id):
        """Libera una reserva de material."""
        if not self.verificar_permiso("liberar_reserva"):
            self.mostrar_error_permiso("liberar reserva")
            return

        try:
            if self.model:
                if self.model.liberar_reserva(reserva_id):
                    self.reserva_liberada.emit(reserva_id)
                    self.log_auditoria(
                        "LIBERAR_RESERVA", f"Reserva {reserva_id} liberada"
                    )

                    # Actualizar vista
                    self.cargar_datos_iniciales()
                    self.cargar_disponibilidad()

                    if self.view:
                        self.view.show_success("Reserva liberada exitosamente")
                else:
                    if self.view:
                        self.view.show_error("Error al liberar la reserva")

        except Exception as e:
            self.error_ocurrido.emit(f"Error al liberar reserva: {str(e)}")

    def generar_reporte_reservas(self, obra_id):
        """Genera un reporte de reservas para una obra."""
        if not self.verificar_permiso("exportar_inventario"):
            self.mostrar_error_permiso("generar reporte")
            return

        try:
            if self.model:
                reporte = self.model.generar_reporte_reservas_obra(obra_id)

                if reporte:
                    # Mostrar reporte en ventana o guardarlo
                    if self.view:
                        self.view.show_info(
                            "Reporte Generado",
                            f"Reporte de reservas generado exitosamente\n"
                            f"Total de reservas: {reporte.get('total_reservas', 0)}\n"
                            f"Valor total: ${reporte.get('valor_total', 0.0):.2f}",
                        )
                    self.log_auditoria(
                        "GENERAR_REPORTE",
                        f"Reporte de reservas generado para obra {obra_id}",
                    )
                else:
                    if self.view:
                        self.view.show_error("Error al generar el reporte")

        except Exception as e:
            self.error_ocurrido.emit(f"Error al generar reporte: {str(e)}")

    def cargar_disponibilidad(self):
        """Carga la disponibilidad de materiales."""
        if not self.verificar_permiso("ver_inventario"):
            return

        try:
            if self.model:
                disponibilidad = self.model.obtener_disponibilidad_materiales()
                if self.view:
                    self.view.cargar_disponibilidad_en_tabla(disponibilidad)

        except Exception as e:
            self.error_ocurrido.emit(f"Error al cargar disponibilidad: {str(e)}")

    def actualizar_por_obra(self, obra_id):
        """Actualiza datos cuando se modifica una obra."""
        try:
            self.cargar_obras()
            self.cargar_reservas_obra(obra_id)
            self.cargar_disponibilidad()
            self.actualizar_estadisticas()
        except Exception as e:
            self.error_ocurrido.emit(f"Error al actualizar por obra: {str(e)}")

    def filtrar_disponibilidad(self, filtros):
        """Filtra la disponibilidad según los criterios especificados."""
        if not self.verificar_permiso("ver_inventario"):
            return

        try:
            if self.model:
                disponibilidad = self.model.obtener_disponibilidad_material(
                    categoria=filtros.get("categoria"),
                    estado=filtros.get("estado"),
                    busqueda=filtros.get("busqueda"),
                )
                if self.view:
                    self.view.cargar_disponibilidad_en_tabla(disponibilidad)
        except Exception as e:
            self.error_ocurrido.emit(f"Error al filtrar disponibilidad: {str(e)}")

    def mostrar_detalle_disponibilidad(self, item):
        """Muestra el detalle de disponibilidad de un producto."""
        if not self.verificar_permiso("ver_inventario"):
            return

        try:
            if self.model:
                detalle = self.model.obtener_detalle_disponibilidad(item["id"])

                if detalle and self.view:
                    mensaje = f"""
                    Detalle de Disponibilidad - {item["descripcion"]}

                    Código: {item["codigo"]}
                    Stock Total: {detalle.get("stock_total", 0)}
                    Stock Reservado: {detalle.get("stock_reservado", 0)}
                    Stock Disponible: {detalle.get("stock_disponible", 0)}
                    Stock Mínimo: {detalle.get("stock_minimo", 0)}

                    Reservas Activas: {detalle.get("reservas_activas", 0)}
                    Valor Total Reservado: ${detalle.get("valor_reservado", 0.0):.2f}
                    """

                    self.view.show_info("Detalle de Disponibilidad", mensaje)

        except Exception as e:
            self.error_ocurrido.emit(f"Error al mostrar detalle: {str(e)}")

    def obtener_productos(self):
        """Obtiene todos los productos del inventario."""
        if self.model:
            return self.model.obtener_todos_productos()
        return []

    def obtener_productos_disponibles(self):
        """Obtiene productos disponibles para reserva."""
        if self.model:
            return self.model.obtener_productos_disponibles_para_reserva()
        return []

    def obtener_info_obra(self, obra_id):
        """Obtiene información de una obra específica."""
        if self.model:
            return self.model.obtener_info_obra(obra_id)
        return None
