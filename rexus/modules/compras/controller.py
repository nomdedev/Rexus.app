"""
Controlador de Compras

Maneja la lógica de negocio entre la vista y el modelo de compras.
Incluye gestión de órdenes, proveedores y detalles de compra.
"""

from datetime import date, datetime

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QMessageBox
from rexus.utils.message_system import show_success, show_error, show_warning
from rexus.core.auth_manager import AuthManager
from rexus.modules.compras.detalle_model import DetalleComprasModel
from rexus.modules.compras.proveedores_model import ProveedoresModel


class ComprasController(QObject):
    """Controlador para el módulo de compras."""

    # Señales
    datos_actualizados = pyqtSignal()

    def __init__(self, model, view, db_connection=None):
        """
        Inicializa el controlador.

        Args:
            model: Modelo de compras
            view: Vista de compras
            db_connection: Conexión a la base de datos
        """
        super().__init__()
        self.model = model
        self.view = view
        self.db_connection = db_connection

        # Inicializar modelos adicionales
        self.detalle_model = DetalleComprasModel(db_connection)
        self.proveedores_model = ProveedoresModel(db_connection)

        # Conectar señales
        self.conectar_señales()

        # Cargar datos iniciales
        self.cargar_datos_iniciales()

    def conectar_señales(self):
        """Conecta las señales entre vista y controlador."""
        # Señales de la vista
        self.view.orden_creada.connect(self.crear_orden)
        self.view.orden_actualizada.connect(self.actualizar_estado_orden)
        self.view.busqueda_realizada.connect(self.buscar_compras)

        # Señales del controlador
        self.datos_actualizados.connect(self.actualizar_vista)

    def cargar_datos_iniciales(self):
        """Carga los datos iniciales en la vista."""
        try:
            # Obtener todas las compras
            compras = self.model.obtener_todas_compras()
            self.view.cargar_compras_en_tabla(compras)

            # Obtener estadísticas
            stats = self.model.obtener_estadisticas_compras()
            self.view.actualizar_estadisticas(stats)

            print(
                f"[COMPRAS CONTROLLER] Datos iniciales cargados: {len(compras)} compras"
            )

        except Exception as e:
            print(f"[ERROR COMPRAS CONTROLLER] Error cargando datos iniciales: {e}")
            self.mostrar_error("Error cargando datos iniciales", str(e))

    def crear_orden(self, datos_orden):
        # 🔒 VERIFICACIÓN DE AUTORIZACIÓN REQUERIDA
        # TODO: Implementar @auth_required o verificación manual
        # if not AuthManager.check_permission('crear_orden'):
        #     raise PermissionError("Acceso denegado - Permisos insuficientes")

        """
        Crea una nueva orden de compra.

        Args:
            datos_orden: Diccionario con los datos de la orden
        """
        try:
            # Validar datos
            if not self.validar_datos_orden(datos_orden):
                return

            # Crear la orden
            exito = self.model.crear_compra(
                proveedor=datos_orden["proveedor"],
                numero_orden=datos_orden["numero_orden"],
                fecha_pedido=datos_orden["fecha_pedido"],
                fecha_entrega_estimada=datos_orden["fecha_entrega_estimada"],
                estado=datos_orden["estado"],
                observaciones=datos_orden["observaciones"],
                usuario_creacion=datos_orden["usuario_creacion"],
                descuento=datos_orden["descuento"],
                impuestos=datos_orden["impuestos"],
            )

            if exito:
                self.mostrar_mensaje("Éxito", "Orden creada exitosamente")
                self.datos_actualizados.emit()
            else:
                self.mostrar_error("Error", "No se pudo crear la orden")

        except Exception as e:
            print(f"[ERROR COMPRAS CONTROLLER] Error creando orden: {e}")
            self.mostrar_error("Error creando orden", str(e))

    def actualizar_estado_orden(self, orden_id, nuevo_estado):
        # 🔒 VERIFICACIÓN DE AUTORIZACIÓN REQUERIDA
        # TODO: Implementar @auth_required o verificación manual
        # if not AuthManager.check_permission('actualizar_estado_orden'):
        #     raise PermissionError("Acceso denegado - Permisos insuficientes")

        """
        Actualiza el estado de una orden.

        Args:
            orden_id: ID de la orden
            nuevo_estado: Nuevo estado
        """
        try:
            exito = self.model.actualizar_estado_compra(orden_id, nuevo_estado)

            if exito:
                self.mostrar_mensaje("Éxito", f"Estado actualizado a {nuevo_estado}")
                self.datos_actualizados.emit()
            else:
                self.mostrar_error("Error", "No se pudo actualizar el estado")

        except Exception as e:
            print(f"[ERROR COMPRAS CONTROLLER] Error actualizando estado: {e}")
            self.mostrar_error("Error actualizando estado", str(e))

    def buscar_compras(self, filtros):
        """
        Busca compras con filtros.

        Args:
            filtros: Diccionario con filtros de búsqueda
        """
        try:
            # Convertir fechas None a valores apropiados
            fecha_inicio = filtros.get("fecha_inicio")
            fecha_fin = filtros.get("fecha_fin")

            # Buscar compras
            compras = self.model.buscar_compras(
                proveedor=filtros.get("proveedor", ""),
                estado=filtros.get("estado", ""),
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                numero_orden=filtros.get("numero_orden", ""),
            )

            # Actualizar vista
            self.view.cargar_compras_en_tabla(compras)

            # Actualizar estadísticas basadas en la búsqueda
            stats = self.calcular_estadisticas_filtradas(compras)
            self.view.actualizar_estadisticas(stats)

            print(
                f"[COMPRAS CONTROLLER] Búsqueda completada: {len(compras)} resultados"
            )

        except Exception as e:
            print(f"[ERROR COMPRAS CONTROLLER] Error en búsqueda: {e}")
            self.mostrar_error("Error en búsqueda", str(e))

    def calcular_estadisticas_filtradas(self, compras):
        """
        Calcula estadísticas para un conjunto filtrado de compras.

        Args:
            compras: Lista de compras filtradas

        Returns:
            Dict: Estadísticas calculadas
        """
        try:
            total_ordenes = len(compras)
            monto_total = sum(compra.get("total_final", 0) for compra in compras)

            # Contar por estado
            estados_count = {}
            for compra in compras:
                estado = compra.get("estado", "DESCONOCIDO")
                estados_count[estado] = estados_count.get(estado, 0) + 1

            # Convertir a formato esperado
            ordenes_por_estado = [
                {"estado": estado, "cantidad": cantidad}
                for estado, cantidad in estados_count.items()
            ]

            return {
                "total_ordenes": total_ordenes,
                "ordenes_por_estado": ordenes_por_estado,
                "monto_total": monto_total,
                "proveedores_activos": [],  # Simplificado por ahora
            }

        except Exception as e:
            print(f"[ERROR COMPRAS CONTROLLER] Error calculando estadísticas: {e}")
            return {
                "total_ordenes": 0,
                "ordenes_por_estado": [],
                "monto_total": 0,
                "proveedores_activos": [],
            }

    def actualizar_vista(self):
        # 🔒 VERIFICACIÓN DE AUTORIZACIÓN REQUERIDA
        # TODO: Implementar @auth_required o verificación manual
        # if not AuthManager.check_permission('actualizar_vista'):
        #     raise PermissionError("Acceso denegado - Permisos insuficientes")

        """Actualiza toda la vista con datos frescos."""
        try:
            # Realizar nueva búsqueda con filtros actuales
            filtros = {
                "proveedor": self.view.input_busqueda.text(),
                "estado": self.view.combo_estado.currentText()
                if self.view.combo_estado.currentText() != "Todos"
                else "",
                "fecha_inicio": self.view.date_desde.date().toPython(),
                "fecha_fin": self.view.date_hasta.date().toPython(),
            }

            self.buscar_compras(filtros)

        except Exception as e:
            print(f"[ERROR COMPRAS CONTROLLER] Error actualizando vista: {e}")

    def validar_datos_orden(self, datos):
        """
        Valida los datos de una orden antes de crearla.

        Args:
            datos: Diccionario con datos de la orden

        Returns:
            bool: True si los datos son válidos
        """
        errores = []

        # Validar campos obligatorios
        if not datos.get("proveedor", "").strip():
            errores.append("El proveedor es obligatorio")

        if not datos.get("numero_orden", "").strip():
            errores.append("El número de orden es obligatorio")

        # Validar fechas
        fecha_pedido = datos.get("fecha_pedido")
        fecha_entrega = datos.get("fecha_entrega_estimada")

        if fecha_pedido and fecha_entrega:
            if fecha_entrega < fecha_pedido:
                errores.append(
                    "La fecha de entrega no puede ser anterior a la fecha de pedido"
                )

        # Validar valores numéricos
        if datos.get("descuento", 0) < 0:
            errores.append("El descuento no puede ser negativo")

        if datos.get("impuestos", 0) < 0:
            errores.append("Los impuestos no pueden ser negativos")

        # Mostrar errores si existen
        if errores:
            self.mostrar_error("Datos inválidos", "\n".join(errores))
            return False

        return True

    def mostrar_mensaje(self, titulo, mensaje):
        """Muestra un mensaje informativo con el sistema mejorado."""
        if titulo == "Éxito":
            show_success(self.view, titulo, mensaje)
        else:
            from rexus.utils.message_system import show_info
            show_info(self.view, titulo, mensaje)

    def mostrar_error(self, titulo, mensaje):
        """Muestra un mensaje de error con el sistema mejorado."""
        show_error(self.view, titulo, mensaje)

    def obtener_resumen_compras(self):
        """
        Obtiene un resumen de las compras para reportes.

        Returns:
            Dict: Resumen de compras
        """
        try:
            stats = self.model.obtener_estadisticas_compras()
            compras_recientes = self.model.obtener_todas_compras()

            return {
                "estadisticas": stats,
                "compras_recientes": compras_recientes[:10],  # Últimas 10
                "fecha_actualizacion": datetime.now().isoformat(),
            }

        except Exception as e:
            print(f"[ERROR COMPRAS CONTROLLER] Error obteniendo resumen: {e}")
            return {
                "estadisticas": {},
                "compras_recientes": [],
                "fecha_actualizacion": datetime.now().isoformat(),
            }

    # === MÉTODOS PARA GESTIÓN DE PROVEEDORES ===

    def crear_proveedor(self, datos_proveedor):
        """
        Crea un nuevo proveedor.

        Args:
            datos_proveedor: Diccionario con datos del proveedor
        """
        try:
            exito = self.proveedores_model.crear_proveedor(
                nombre=datos_proveedor.get("nombre", ""),
                razon_social=datos_proveedor.get("razon_social", ""),
                ruc=datos_proveedor.get("ruc", ""),
                telefono=datos_proveedor.get("telefono", ""),
                email=datos_proveedor.get("email", ""),
                direccion=datos_proveedor.get("direccion", ""),
                contacto_principal=datos_proveedor.get("contacto_principal", ""),
                categoria=datos_proveedor.get("categoria", ""),
                observaciones=datos_proveedor.get("observaciones", ""),
                usuario_creacion=datos_proveedor.get("usuario_creacion", "Sistema")
            )

            if exito:
                show_success(self.view, "Éxito", "Proveedor creado exitosamente")
                return True
            else:
                show_error(self.view, "Error", "No se pudo crear el proveedor")
                return False

        except Exception as e:
            print(f"[ERROR COMPRAS CONTROLLER] Error creando proveedor: {e}")
            show_error(self.view, "Error creando proveedor", str(e))
            return False

    def obtener_proveedores(self):
        """
        Obtiene todos los proveedores.

        Returns:
            List[Dict]: Lista de proveedores
        """
        try:
            return self.proveedores_model.obtener_todos_proveedores()
        except Exception as e:
            print(f"[ERROR COMPRAS CONTROLLER] Error obteniendo proveedores: {e}")
            return []

    def buscar_proveedores(self, filtros):
        """
        Busca proveedores con filtros.

        Args:
            filtros: Diccionario con filtros de búsqueda

        Returns:
            List[Dict]: Lista de proveedores filtrados
        """
        try:
            return self.proveedores_model.buscar_proveedores(
                nombre=filtros.get("nombre", ""),
                categoria=filtros.get("categoria", ""),
                estado=filtros.get("estado", ""),
                ruc=filtros.get("ruc", "")
            )
        except Exception as e:
            print(f"[ERROR COMPRAS CONTROLLER] Error buscando proveedores: {e}")
            return []

    def obtener_estadisticas_proveedor(self, proveedor_id):
        """
        Obtiene estadísticas de un proveedor específico.

        Args:
            proveedor_id: ID del proveedor

        Returns:
            Dict: Estadísticas del proveedor
        """
        try:
            return self.proveedores_model.obtener_estadisticas_proveedor(proveedor_id)
        except Exception as e:
            print(f"[ERROR COMPRAS CONTROLLER] Error obteniendo estadísticas proveedor: {e}")
            return {}

    # === MÉTODOS PARA GESTIÓN DE DETALLES DE COMPRAS ===

    def obtener_items_compra(self, compra_id):
        """
        Obtiene los items de una orden de compra.

        Args:
            compra_id: ID de la orden de compra

        Returns:
            List[Dict]: Lista de items
        """
        try:
            return self.detalle_model.obtener_items_compra(compra_id)
        except Exception as e:
            print(f"[ERROR COMPRAS CONTROLLER] Error obteniendo items: {e}")
            return []

    def agregar_item_compra(self, datos_item):
        """
        Agrega un item a una orden de compra.

        Args:
            datos_item: Diccionario con datos del item
        """
        try:
            exito = self.detalle_model.agregar_item_compra(
                compra_id=datos_item.get("compra_id"),
                descripcion=datos_item.get("descripcion", ""),
                categoria=datos_item.get("categoria", ""),
                cantidad=datos_item.get("cantidad", 1),
                precio_unitario=datos_item.get("precio_unitario", 0.0),
                unidad=datos_item.get("unidad", "UN"),
                observaciones=datos_item.get("observaciones", ""),
                usuario_creacion=datos_item.get("usuario_creacion", "Sistema")
            )

            if exito:
                show_success(self.view, "Éxito", "Item agregado exitosamente")
                return True
            else:
                show_error(self.view, "Error", "No se pudo agregar el item")
                return False

        except Exception as e:
            print(f"[ERROR COMPRAS CONTROLLER] Error agregando item: {e}")
            show_error(self.view, "Error agregando item", str(e))
            return False

    def obtener_resumen_compra(self, compra_id):
        """
        Obtiene el resumen financiero de una orden de compra.

        Args:
            compra_id: ID de la orden de compra

        Returns:
            Dict: Resumen financiero
        """
        try:
            return self.detalle_model.obtener_resumen_compra(compra_id)
        except Exception as e:
            print(f"[ERROR COMPRAS CONTROLLER] Error obteniendo resumen: {e}")
            return {}

    def obtener_productos_por_categoria(self):
        """
        Obtiene productos agrupados por categoría.

        Returns:
            Dict: Productos por categoría
        """
        try:
            return self.detalle_model.obtener_productos_por_categoria()
        except Exception as e:
            print(f"[ERROR COMPRAS CONTROLLER] Error obteniendo productos por categoría: {e}")
            return {}

    def buscar_productos_similares(self, descripcion, limite=10):
        """
        Busca productos similares para sugerencias.

        Args:
            descripcion: Descripción a buscar
            limite: Número máximo de resultados

        Returns:
            List[Dict]: Lista de productos similares
        """
        try:
            return self.detalle_model.buscar_productos_similares(descripcion, limite)
        except Exception as e:
            print(f"[ERROR COMPRAS CONTROLLER] Error buscando productos similares: {e}")
            return []

    # === MÉTODOS DE UTILIDAD ===

    def generar_reporte_completo(self):
        """
        Genera un reporte completo del módulo de compras.

        Returns:
            Dict: Reporte completo
        """
        try:
            # Obtener estadísticas generales
            stats_generales = self.model.obtener_estadisticas_compras()
            
            # Obtener datos de proveedores
            proveedores = self.proveedores_model.obtener_todos_proveedores()
            
            # Obtener productos por categoría
            productos_categoria = self.detalle_model.obtener_productos_por_categoria()
            
            # Obtener compras recientes
            compras_recientes = self.model.obtener_todas_compras()[:20]  # Últimas 20

            return {
                "fecha_reporte": datetime.now().isoformat(),
                "estadisticas_generales": stats_generales,
                "total_proveedores": len(proveedores),
                "proveedores_activos": len([p for p in proveedores if p.get("estado") == "ACTIVO"]),
                "categorias_productos": list(productos_categoria.keys()),
                "total_categorias": len(productos_categoria),
                "compras_recientes": compras_recientes,
                "resumen": {
                    "modulo": "Compras",
                    "estado": "Operativo",
                    "ultima_actualizacion": datetime.now().isoformat()
                }
            }

        except Exception as e:
            print(f"[ERROR COMPRAS CONTROLLER] Error generando reporte: {e}")
            return {
                "fecha_reporte": datetime.now().isoformat(),
                "error": str(e),
                "estado": "Error"
            }
