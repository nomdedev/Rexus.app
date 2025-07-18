"""
Controlador de Compras

Maneja la lógica de negocio entre la vista y el modelo de compras.
"""

from datetime import date, datetime

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QMessageBox


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
        """Muestra un mensaje informativo."""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle(titulo)
        msg.setText(mensaje)
        msg.exec()

    def mostrar_error(self, titulo, mensaje):
        """Muestra un mensaje de error."""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle(titulo)
        msg.setText(mensaje)
        msg.exec()

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
