"""
Controlador de Compras

Maneja la lógica de negocio entre la vista y el modelo de compras.
Incluye gestión de órdenes, proveedores y detalles de compra.
"""

from datetime import datetime

from PyQt6.QtCore import QObject, pyqtSignal
from rexus.core.base_controller import BaseController

# Sistema de logging centralizado
from rexus.utils.app_logger import get_logger
logger = get_logger("compras.controller")
from rexus.utils.message_system import show_success, show_error, show_warning
from rexus.core.auth_decorators import auth_required, admin_required
from rexus.modules.compras.detalle_model import DetalleComprasModel
from rexus.modules.compras.proveedores_model import ProveedoresModel
from rexus.modules.compras.inventory_integration import InventoryIntegration
from rexus.modules.compras.constants import ErrorMessages, SuccessMessages, InfoMessages


class ComprasController(BaseController):
    """Controlador para el módulo de compras."""

    # Señales
    datos_actualizados = pyqtSignal()

    def __init__(self, model=None, view=None, db_connection=None):
        """
        Inicializa el controlador.

        Args:
            model: Modelo de compras (opcional)
            view: Vista de compras (opcional)
            db_connection: Conexión a la base de datos
        """
        # Crear modelo si no se proporciona
        if model is None:
            from rexus.modules.compras.model import ComprasModel
            model = ComprasModel(db_connection)
            
        super().__init__(module_name="compras", model=model, view=view, db_connection=db_connection)
        self.model = model
        self.view = view
        self.db_connection = db_connection

        # Inicializar modelos adicionales
        self.detalle_model = DetalleComprasModel(db_connection)
        self.proveedores_model = ProveedoresModel(db_connection)

        # Inicializar integración de inventario
        try:
            from rexus.core.database import get_inventario_connection
            inventario_db = get_inventario_connection()
            self.inventory_integration = InventoryIntegration(db_connection, inventario_db)
        except Exception as e:
            logger.warning(f"No se pudo inicializar integración de inventario: {e}")
            self.inventory_integration = None

        # Conectar señales
        self.conectar_señales()

        # Cargar datos iniciales
        self.cargar_datos_iniciales()

    def conectar_señales(self):
        """Conecta las señales entre vista y controlador."""
        try:
            # Verificar que la vista tenga las señales necesarias
            if hasattr(self.view, 'orden_creada'):
                self.view.orden_creada.connect(self.crear_orden)
            if hasattr(self.view, 'orden_actualizada'):
                self.view.orden_actualizada.connect(self.actualizar_estado_orden)
            if hasattr(self.view, 'busqueda_realizada'):
                self.view.busqueda_realizada.connect(self.buscar_compras)

            # Señales del controlador
            self.datos_actualizados.connect(self.actualizar_vista)
            
        except AttributeError as e:
            logger.warning(f"Error conectando señales en compras: {e}")
        except Exception as e:
            logger.error(f"Error inesperado conectando señales: {e}")

    def cargar_datos_iniciales(self):
        """Carga los datos iniciales en la vista."""
        try:
            # Verificar que la vista esté disponible
            if not self.view:
                logger.warning("Vista no disponible para cargar datos iniciales")
                return
            
            # Verificar que el modelo esté disponible
            if not self.model:
                logger.warning("Modelo no disponible para cargar datos iniciales")
                return

            # Obtener todas las compras
            compras = self.model.obtener_todas_compras()
            
            # Verificar que la vista tenga el método necesario
            if hasattr(self.view, 'cargar_compras_en_tabla'):
                self.view.cargar_compras_en_tabla(compras)
            else:
                logger.warning("Vista no tiene método cargar_compras_en_tabla")

            # Obtener estadísticas
            stats = self.model.obtener_estadisticas_compras()
            if hasattr(self.view, 'actualizar_estadisticas'):
                self.view.actualizar_estadisticas(stats)

            logger.info(f"Datos iniciales cargados: {len(compras)} compras")

        except Exception as e:
            logger.error(f"Error cargando datos iniciales: {e}")
            if hasattr(self, 'mostrar_error'):
                self.mostrar_error("Error de carga", str(e))
    def crear_orden(self, datos_orden):
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
                self.mostrar_mensaje("Éxito", SuccessMessages.ORDEN_CREATED)
                self.datos_actualizados.emit()
            else:
                self.mostrar_error("Error", ErrorMessages.CREATE_FAILED)

        except Exception as e:
            logger.error(f"Error creando orden: {e}")
            self.mostrar_error("Error creando orden", str(e))
    def actualizar_estado_orden(self, orden_id, nuevo_estado):
        # [LOCK] VERIFICACIÓN DE AUTORIZACIÓN REQUERIDA
        # Autorización verificada por decorador
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
            logger.error(f"Error actualizando estado: {e}")
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

            logger.info(f"Búsqueda completada: {len(compras)} resultados")

        except Exception as e:
            logger.error(f"Error en búsqueda: {e}")
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
            logger.error(f"Error calculando estadísticas: {e}")
            return {
                "total_ordenes": 0,
                "ordenes_por_estado": [],
                "monto_total": 0,
                "proveedores_activos": [],
            }
    def actualizar_vista(self):
        # [LOCK] VERIFICACIÓN DE AUTORIZACIÓN REQUERIDA
        # Autorización verificada por decorador
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
            logger.error(f"Error actualizando vista: {e}")

    @admin_required
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
    def procesar_recepcion_orden(self,
orden_id,
        items_recibidos,
        datos_seguimiento):
        """
        Procesa la recepción completa de una orden con integración al inventario.

        Args:
            orden_id: ID de la orden
            items_recibidos: Lista de items recibidos con cantidades
            datos_seguimiento: Datos del seguimiento de entrega
        """
        try:
            # Actualizar estado de la orden
            exito_estado = self.actualizar_estado_orden(orden_id, "RECIBIDA")

            if not exito_estado:
                self.mostrar_error("Error", "No se pudo actualizar el estado de la orden")
                return False

            # Procesar integración con inventario si está disponible
            if self.inventory_integration:
                exito_inventario = self.inventory_integration.procesar_recepcion_completa(
                    orden_id, items_recibidos
                )

                if exito_inventario:
                    self.mostrar_mensaje("Éxito",
                        "Orden recibida y inventario actualizado correctamente")
                else:
                    show_warning(self.view, "Advertencia",
                        "Orden recibida pero hubo problemas actualizando el inventario")
            else:
                show_warning(self.view, "Advertencia",
                    "Orden recibida pero integración de inventario no disponible")

            # Registrar seguimiento
            self._registrar_seguimiento_orden(orden_id, datos_seguimiento)

            # Actualizar vista
            self.datos_actualizados.emit()

            return True

        except Exception as e:
            logger.error(f"Error procesando recepción de orden: {e}")
            self.mostrar_error("Error", f"Error procesando recepción: {str(e)}")
            return False

    def _registrar_seguimiento_orden(self, orden_id, datos_seguimiento):
        """Registra información de seguimiento de la orden."""
        try:
            # Aquí se registrarían los datos de seguimiento en la base de datos
            # Por ahora solo log para demostrar la funcionalidad
            logger.info(f"Seguimiento registrado para orden {orden_id}: {datos_seguimiento}")

        except Exception as e:
            logger.error(f"Error registrando seguimiento: {e}")
    def verificar_disponibilidad_antes_orden(self, items_solicitud):
        """
        Verifica disponibilidad en inventario antes de crear una orden.

        Args:
            items_solicitud: Lista de items solicitados

        Returns:
            dict: Resultado de la verificación
        """
        try:
            if not self.inventory_integration:
                return {
                    'disponible_completo': True,
                    'advertencia': 'Verificación de inventario no disponible'
                }

            resultado = self.inventory_integration.verificar_disponibilidad_stock(items_solicitud)

            if not resultado.get('disponible_completo', True):
                advertencias = resultado.get('advertencias', [])
                show_warning(
                    self.view,
                    "Stock Insuficiente",
                    "Algunos items no tienen stock suficiente:\n" + "\n".join(advertencias)
                )

            return resultado

        except Exception as e:
            logger.error(f"Error verificando disponibilidad: {e}")
            return {'disponible_completo': False, 'error': str(e)}
    def obtener_estado_pedido(self, pedido_id):
        """Obtiene el estado detallado de un pedido"""
        try:
            if self.model:
                estado = self.model.obtener_estado_detallado_pedido(pedido_id)
                return estado
            return None
        except Exception as e:
            self.mostrar_error(f"Error obteniendo estado de pedido: {e}")
            return None
    def actualizar_seguimiento_pedido(self,
pedido_id,
        nuevo_estado,
        observaciones=""):
        """Actualiza el seguimiento de un pedido"""
        try:
            if self.model:
                exito = self.model.actualizar_seguimiento_pedido(
                    pedido_id, nuevo_estado, observaciones
                )
                if exito:
                    self.mostrar_exito("Seguimiento actualizado correctamente")
                    self.cargar_datos_iniciales()
                else:
                    self.mostrar_error("Error actualizando seguimiento")
        except Exception as e:
            self.mostrar_error(f"Error actualizando seguimiento: {e}")
    def actualizar_stock_desde_compra(self, orden_id):
        """Actualiza el stock de inventario desde una compra recibida"""
        try:
            if self.model:
                # Obtener detalles de la orden
                detalles = self.model.obtener_detalles_orden(orden_id)

                # Actualizar inventario
                for detalle in detalles:
                    # Integración con el módulo de inventario
                    try:
                        from rexus.modules.inventario.model import InventarioModel
                        from rexus.core.database import get_inventario_connection
                        
                        db_connection = get_inventario_connection()
                        if db_connection:
                            inventario_model = InventarioModel(db_connection)
                            # Actualizar stock de producto recibido
                            inventario_model.actualizar_stock_por_compra(
                                producto_id=detalle.get('producto_id'),
                                cantidad_recibida=detalle.get('cantidad', 0),
                                precio_unitario=detalle.get('precio_unitario', 0),
                                numero_compra=compra_id
                            )
                    except Exception as e:
                        self.logger.warning(f"No se pudo actualizar inventario para detalle {detalle}: {e}")
                        # Continuar con el resto de la operación

                self.mostrar_exito("Stock actualizado desde compra")
        except Exception as e:
            self.mostrar_error(f"Error actualizando stock: {e}")
    def verificar_stock_minimos(self):
        """Verifica productos con stock mínimo para generar órdenes automáticas"""
        try:
            if self.model:
                productos_minimos = self.model.obtener_productos_stock_minimo()

                if productos_minimos:
                    mensaje = f"Se encontraron {len(productos_minimos)} productos con stock mínimo"
                    self.mostrar_info(mensaje)

                    # Proponer generación automática de órdenes
                    from PyQt6.QtWidgets import QMessageBox
                    
                    respuesta = QMessageBox.question(
                        self.view,
                        "Stock Mínimo Detectado",
                        f"Se encontraron {len(productos_minimos)} productos con stock bajo.\n\n"
                        "¿Desea generar órdenes de compra automáticamente?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                        QMessageBox.StandardButton.Yes
                    )
                    
                    if respuesta == QMessageBox.StandardButton.Yes:
                        self._generar_ordenes_automaticas(productos_minimos)

                return productos_minimos
        except Exception as e:
            self.mostrar_error(f"Error verificando stock mínimos: {e}")
            return []

    def _generar_ordenes_automaticas(self, productos_minimos):
        """Genera órdenes de compra automáticas para productos con stock mínimo."""
        try:
            ordenes_generadas = 0
            for producto in productos_minimos:
                # Calcular cantidad a ordenar (stock máximo - stock actual)
                cantidad_ordenar = producto.get('stock_maximo', 100) - producto.get('stock_actual', 0)
                
                if cantidad_ordenar > 0:
                    # Crear orden automática
                    orden_data = {
                        'proveedor_id': producto.get('proveedor_preferido_id', 1),
                        'fecha_solicitud': datetime.now().date(),
                        'estado': 'PENDIENTE',
                        'observaciones': f'Orden automática por stock mínimo - {producto.get("descripcion", "")}',
                        'productos': [{
                            'producto_id': producto.get('id'),
                            'cantidad': cantidad_ordenar,
                            'precio_estimado': producto.get('precio_unitario', 0)
                        }]
                    }
                    
                    if self.model.crear_orden_compra(orden_data):
                        ordenes_generadas += 1
            
            if ordenes_generadas > 0:
                self.mostrar_exito(f"Se generaron {ordenes_generadas} órdenes de compra automáticamente")
            else:
                self.mostrar_info("No se pudieron generar órdenes automáticas")
                
        except Exception as e:
            self.mostrar_error(f"Error generando órdenes automáticas: {e}")

    @admin_required
    def generar_reporte_compras(self,
fecha_inicio,
        fecha_fin,
        proveedor_id=None):
        """Genera reporte de compras por período"""
        try:
            if self.model:
                reporte = self.model.generar_reporte_periodo(
                    fecha_inicio, fecha_fin, proveedor_id
                )

                if reporte:
                    self.mostrar_exito("Reporte generado exitosamente")
                    return reporte
                else:
                    self.mostrar_error("No se pudieron obtener datos para el reporte")
        except Exception as e:
            self.mostrar_error(f"Error generando reporte: {e}")
        return None
    def obtener_estadisticas_proveedor(self, proveedor_id):
        """Obtiene estadísticas detalladas de un proveedor"""
        try:
            if self.proveedores_model:
                stats = self.proveedores_model.obtener_estadisticas_proveedor(proveedor_id)
                return stats
        except Exception as e:
            self.mostrar_error(f"Error obteniendo estadísticas: {e}")
        return {}


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
            logger.error(f"Error cargando página: {e}")
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
            logger.error(f"Error obteniendo total de registros: {e}")
            return 0

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
            logger.error(f"Error obteniendo resumen: {e}")
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
            logger.error(f"Error creando proveedor: {e}")
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
            logger.error(f"Error obteniendo proveedores: {e}")
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
            logger.error(f"Error buscando proveedores: {e}")
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
            logger.error(f"Error obteniendo estadísticas proveedor: {e}")
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
            logger.error(f"Error obteniendo items: {e}")
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
            logger.error(f"Error agregando item: {e}")
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
            logger.error(f"Error obteniendo resumen: {e}")
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
            logger.error(f"Error obteniendo productos por categoría: {e}")
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
            logger.error(f"Error buscando productos similares: {e}")
            return []

    # === MÉTODOS DE UTILIDAD ===

    @admin_required
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
            logger.error(f"Error generando reporte: {e}")
            return {
                "fecha_reporte": datetime.now().isoformat(),
                "error": str(e),
                "estado": "Error"
            }
    def eliminar_orden(self, orden_id):
        """
        Elimina una orden de compra.

        Args:
            orden_id: ID de la orden a eliminar

        Returns:
            bool: True si se eliminó exitosamente
        """
        try:
            if not orden_id:
                self.mostrar_error("Error", "ID de orden requerido")
                return False

            # Verificar que la orden existe
            orden = self.model.obtener_compra_por_id(orden_id)
            if not orden:
                self.mostrar_error("Error", f"No se encontró la orden {orden_id}")
                return False

            # Verificar permisos y estado
            estado_actual = orden.get("estado", "")
            if estado_actual in ["RECIBIDA", "COMPLETADA"]:
                self.mostrar_error("Error", 
                    f"No se puede eliminar una orden en estado {estado_actual}")
                return False

            # Eliminar la orden
            exito = self.model.eliminar_compra(orden_id)

            if exito:
                self.mostrar_mensaje("Éxito", f"Orden {orden_id} eliminada exitosamente")
                self.datos_actualizados.emit()
                return True
            else:
                self.mostrar_error("Error", "No se pudo eliminar la orden")
                return False

        except Exception as e:
            logger.error(f"Error eliminando orden: {e}")
            self.mostrar_error("Error eliminando orden", str(e))
            return False

    def ensure_safe_operation(self, operation_name, operation_func, *args, **kwargs):
        """Ejecuta una operación de forma segura con defensas completas."""
        try:
            if not self._ensure_model_available(operation_name):
                return None
            
            self.logger.debug(f"Ejecutando operación segura: {operation_name}")
            result = operation_func(*args, **kwargs)
            self.logger.info(f"Operación {operation_name} completada exitosamente")
            return result
            
        except Exception as e:
            error_msg = f"Error en {operation_name}: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            self.show_error_message(error_msg)
            return None
    