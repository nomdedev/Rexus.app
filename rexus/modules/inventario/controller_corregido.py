"""
Controlador de Inventario Corregido - Rexus.app v2.0.0

Controla la interacción entre el modelo refactorizado y la vista de inventario.
Corrige todos los errores de sincronización vista-controlador identificados.
"""

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QMessageBox

from rexus.core.auth_decorators import (
from rexus.utils.unified_sanitizer import unified_sanitizer, sanitize_string, sanitize_numeric
    admin_required,
    auth_required,
    permission_required,
)
from rexus.core.auth_manager import (
    AuthManager,
    admin_required,
    auth_required,
    manager_required,
)
from rexus.core.security import get_security_manager
from rexus.utils.error_handler import RexusErrorHandler as ErrorHandler
from rexus.utils.error_handler import error_boundary as safe_method_decorator
from rexus.utils.security import SecurityUtils


class InventarioControllerCorregido(QObject):
    """Controlador corregido para el módulo de inventario."""

    # Señales
    datos_actualizados = pyqtSignal()
    error_ocurrido = pyqtSignal(str)
    producto_seleccionado_signal = pyqtSignal(dict)

    def __init__(self, model=None, view=None, db_connection=None):
        super().__init__()
        self.model = model
        self.view = view
        self.db_connection = db_connection
        self.usuario_actual = "SISTEMA"

        # Obtener información del usuario autenticado
        auth_manager = AuthManager()
        if hasattr(auth_manager, "current_user") and auth_manager.current_user:
            self.usuario_actual = auth_manager.current_user.get("username", "SISTEMA")

        self.inicializar()

    def inicializar(self):
        """Inicializa el controlador."""
        try:
            print("[INVENTARIO CONTROLLER] Inicializando controlador corregido...")
            self.conectar_senales()
            self.cargar_inventario()
            print("[INVENTARIO CONTROLLER] Controlador inicializado exitosamente")
        except Exception as e:
            print(f"[ERROR INVENTARIO CONTROLLER] Error en inicialización: {e}")
            ErrorHandler.mostrar_error_operacion(self.view, "inicializar inventario", e)

    def conectar_senales(self):
        """Conecta las señales de la vista con los métodos del controlador."""
        if not self.view:
            return

        try:
            print("[INVENTARIO CONTROLLER] Conectando señales de la vista...")

            # Conectar señales de búsqueda y filtros (nombres corregidos)
            if hasattr(self.view, "btn_buscar"):
                self.view.btn_buscar.clicked.connect(self.buscar_productos)
                print("✅ Conectado: btn_buscar")
            else:
                print("⚠️ No encontrado: btn_buscar")

            if hasattr(self.view, "btn_actualizar"):
                self.view.btn_actualizar.clicked.connect(self.cargar_inventario)
                print("✅ Conectado: btn_actualizar")
            else:
                print("⚠️ No encontrado: btn_actualizar")
                
            if hasattr(self.view, "btn_limpiar"):
                self.view.btn_limpiar.clicked.connect(self.limpiar_filtros)
                print("✅ Conectado: btn_limpiar")
            else:
                print("⚠️ No encontrado: btn_limpiar")

            # Conectar señales de acciones (nombres corregidos)
            if hasattr(self.view, "btn_nuevo_producto"):
                self.view.btn_nuevo_producto.clicked.connect(self.nuevo_producto)
                print("✅ Conectado: btn_nuevo_producto")
            else:
                print("⚠️ No encontrado: btn_nuevo_producto")

            if hasattr(self.view, "btn_editar"):
                self.view.btn_editar.clicked.connect(self.editar_producto)
                print("✅ Conectado: btn_editar")
            else:
                print("⚠️ No encontrado: btn_editar")

            if hasattr(self.view, "btn_eliminar"):
                self.view.btn_eliminar.clicked.connect(self.eliminar_producto)
                print("✅ Conectado: btn_eliminar")
            else:
                print("⚠️ No encontrado: btn_eliminar")
                
            if hasattr(self.view, "btn_movimiento"):
                self.view.btn_movimiento.clicked.connect(self.registrar_movimiento)
                print("✅ Conectado: btn_movimiento")
            else:
                print("⚠️ No encontrado: btn_movimiento")
                
            if hasattr(self.view, "btn_exportar"):
                self.view.btn_exportar.clicked.connect(self.exportar_inventario)
                print("✅ Conectado: btn_exportar")
            else:
                print("⚠️ No encontrado: btn_exportar")
                print("✅ Conectado: btn_editar")
            else:
                print("⚠️ No encontrado: btn_editar")

            if hasattr(self.view, "btn_eliminar"):
                self.view.btn_eliminar.clicked.connect(self.eliminar_producto)
                print("✅ Conectado: btn_eliminar")
            else:
                print("⚠️ No encontrado: btn_eliminar")

            # Conectar señales de selección de tabla
            if hasattr(self.view, "tabla_inventario"):
                self.view.tabla_inventario.itemSelectionChanged.connect(
                    self.producto_seleccionado
                )
                print("✅ Conectado: tabla_inventario.itemSelectionChanged")
            else:
                print("⚠️ No encontrado: tabla_inventario")

            # Conectar campo de búsqueda si existe
            if hasattr(self.view, "input_busqueda"):
                self.view.input_busqueda.textChanged.connect(
                    self.filtrar_en_tiempo_real
                )
                print("✅ Conectado: input_busqueda.textChanged")
            else:
                print("⚠️ No encontrado: input_busqueda")

            print("[INVENTARIO CONTROLLER] Señales conectadas correctamente")

        except Exception as e:
            print(f"[ERROR INVENTARIO CONTROLLER] Error conectando señales: {e}")

    @safe_method_decorator
    @auth_required
    def cargar_inventario(self):
        """Carga el inventario completo."""
        try:
            print("[INVENTARIO CONTROLLER] Cargando inventario...")

            if not self.model:
                print("[ERROR] No hay modelo disponible")
                return

            # Usar el método del modelo refactorizado
            if hasattr(self.model, "obtener_productos_paginados"):
                resultado = self.model.obtener_productos_paginados(offset=0, limit=100)
                productos = resultado.get("productos", [])
                total = resultado.get("total", 0)
                print(
                    f"[INVENTARIO CONTROLLER] Cargados {len(productos)} productos de {total} total"
                )
            else:
                print("[ERROR] Método obtener_productos_paginados no disponible")
                productos = []

            # Actualizar vista
            if self.view and hasattr(self.view, "actualizar_tabla"):
                self.view.actualizar_tabla(productos)
            elif self.view and hasattr(self.view, "mostrar_productos"):
                self.view.mostrar_productos(productos)
            else:
                print("[ERROR] Vista no tiene método para mostrar productos")

            # Emitir señal de datos actualizados
            self.datos_actualizados.emit()

        except Exception as e:
            print(f"[ERROR INVENTARIO CONTROLLER] Error cargando inventario: {e}")
            ErrorHandler.mostrar_error_operacion(self.view, "cargar inventario", e)

    @safe_method_decorator
    @auth_required
    def buscar_productos(self):
        """Busca productos según los filtros aplicados."""
        try:
            if not self.view or not self.model:
                return

            # Obtener término de búsqueda
            termino = ""
            if hasattr(self.view, "input_busqueda"):
                termino = self.view.input_busqueda.text().strip()

            if not termino:
                # Si no hay término, cargar todos los productos
                self.cargar_inventario()
                return

            print(f"[INVENTARIO CONTROLLER] Buscando productos: '{termino}'")

            # Sanitizar entrada
            termino_sanitizado = (
                SecurityUtils.sanitize_sql_input(termino)
                if hasattr(SecurityUtils, "sanitize_sql_input")
                else termino
            )

            # Buscar con el modelo
            if hasattr(self.model, "buscar_productos"):
                productos = self.model.buscar_productos(termino_sanitizado, limite=50)
                print(f"[INVENTARIO CONTROLLER] Encontrados {len(productos)} productos")

                # Actualizar vista
                if hasattr(self.view, "actualizar_tabla"):
                    self.view.actualizar_tabla(productos)
                elif hasattr(self.view, "mostrar_productos"):
                    self.view.mostrar_productos(productos)

            else:
                print("[ERROR] Método buscar_productos no disponible en el modelo")

        except Exception as e:
            print(f"[ERROR INVENTARIO CONTROLLER] Error en búsqueda: {e}")
            ErrorHandler.mostrar_error_operacion(self.view, "buscar productos", e)

    def filtrar_en_tiempo_real(self, texto):
        """Filtra productos en tiempo real mientras se escribe."""
        if len(texto) >= 3:  # Comenzar búsqueda con 3 caracteres
            self.buscar_productos()
        elif len(texto) == 0:  # Si se borra todo, mostrar todos
            self.cargar_inventario()

    @safe_method_decorator
    @auth_required
    def producto_seleccionado(self):
        """Maneja la selección de un producto en la tabla."""
        try:
            if not self.view or not hasattr(self.view, "tabla_inventario"):
                return

            tabla = self.view.tabla_inventario
            fila_actual = tabla.currentRow()

            if fila_actual >= 0:
                # Habilitar botones de edición y eliminación
                if hasattr(self.view, "btn_editar"):
                    self.view.btn_editar.setEnabled(True)
                if hasattr(self.view, "btn_eliminar"):
                    self.view.btn_eliminar.setEnabled(True)

                # Obtener datos del producto (si la tabla tiene método para ello)
                if hasattr(self.view, "obtener_producto_seleccionado"):
                    producto = self.view.obtener_producto_seleccionado()
                    if producto:
                        self.producto_seleccionado_signal.emit(producto)
            else:
                # Deshabilitar botones si no hay selección
                if hasattr(self.view, "btn_editar"):
                    self.view.btn_editar.setEnabled(False)
                if hasattr(self.view, "btn_eliminar"):
                    self.view.btn_eliminar.setEnabled(False)

        except Exception as e:
            print(f"[ERROR INVENTARIO CONTROLLER] Error en selección de producto: {e}")

    @safe_method_decorator
    @auth_required
    @permission_required("create_producto")
    def nuevo_producto(self):
        """Abre el diálogo para crear un nuevo producto."""
        try:
            print("[INVENTARIO CONTROLLER] Abriendo diálogo de nuevo producto...")
            # TODO: Implementar diálogo de nuevo producto
            QMessageBox.information(
                self.view,
                "Nuevo Producto",
                "Funcionalidad de nuevo producto será implementada próximamente.",
            )
        except Exception as e:
            print(f"[ERROR INVENTARIO CONTROLLER] Error en nuevo producto: {e}")
            ErrorHandler.mostrar_error_operacion(self.view, "crear nuevo producto", e)

    @safe_method_decorator
    @auth_required
    @permission_required("update_producto")
    def editar_producto(self):
        """Abre el diálogo para editar el producto seleccionado."""
        try:
            print("[INVENTARIO CONTROLLER] Abriendo diálogo de editar producto...")
            # TODO: Implementar diálogo de edición
            QMessageBox.information(
                self.view,
                "Editar Producto",
                "Funcionalidad de editar producto será implementada próximamente.",
            )
        except Exception as e:
            print(f"[ERROR INVENTARIO CONTROLLER] Error en editar producto: {e}")
            ErrorHandler.mostrar_error_operacion(self.view, "editar producto", e)

    @safe_method_decorator
    @auth_required
    @permission_required("delete_producto")
    def eliminar_producto(self):
        """Elimina el producto seleccionado."""
        try:
            print("[INVENTARIO CONTROLLER] Iniciando eliminación de producto...")
            # TODO: Implementar eliminación
            QMessageBox.information(
                self.view,
                "Eliminar Producto",
                "Funcionalidad de eliminar producto será implementada próximamente.",
            )
        except Exception as e:
            print(f"[ERROR INVENTARIO CONTROLLER] Error en eliminar producto: {e}")
            ErrorHandler.mostrar_error_operacion(self.view, "eliminar producto", e)

    def obtener_estadisticas(self):
        """Obtiene estadísticas del inventario."""
        try:
            if not self.model:
                return {}

            if hasattr(self.model, "obtener_estadisticas_inventario"):
                return self.model.obtener_estadisticas_inventario()
            else:
                return {
                    "total_productos": 0,
                    "stock_bajo": 0,
                    "sin_stock": 0,
                    "valor_total": 0.0,
                }
        except Exception as e:
            print(f"[ERROR INVENTARIO CONTROLLER] Error obteniendo estadísticas: {e}")
            return {}
