"""
Transport Manager para el módulo de Logística

Maneja todas las operaciones CRUD de transportes.
Extraído de view.py para mejorar la mantenibilidad.
"""

import logging
from PyQt6.QtWidgets import QMessageBox
from rexus.modules.logistica.dialogo_transporte import DialogoNuevoTransporte

logger = logging.getLogger(__name__)

class LogisticaTransportManager:
    """Gestor de transportes para el módulo de logística."""

    def __init__(self, parent_view):
        """Inicializa el gestor de transportes.
        
        Args:
            parent_view: Vista principal de logística
        """
        self.parent_view = parent_view
        self.controller = None

    def set_controller(self, controller):
        """Establece la referencia al controlador."""
        self.controller = controller

    def mostrar_dialogo_nuevo_transporte(self):
        """Muestra el diálogo para crear un nuevo transporte."""
        try:
            dialogo = DialogoNuevoTransporte(parent=self.parent_view)
            
            if dialogo.exec() == dialogo.DialogCode.Accepted:
                datos_transporte = dialogo.obtener_datos()
                
                if self.controller:
                    resultado = self.controller.crear_transporte(datos_transporte)
                    if resultado:
                        self._mostrar_mensaje_exito("Transporte creado exitosamente")
                        self._actualizar_tabla_transportes()
                    else:
                        self._mostrar_mensaje_error("Error al crear el transporte")
                else:
                    self._mostrar_mensaje_info("Modo demo: Transporte simulado creado")

        except Exception as e:

    def editar_transporte_seleccionado(self):
        """Edita el transporte seleccionado en la tabla."""
        if not hasattr(self.parent_view, 'table_manager'):
            return

        transporte = self.parent_view.table_manager.get_transporte_seleccionado()
        if not transporte:
            self._mostrar_mensaje_advertencia("Seleccione un transporte para editar")
            return

        try:
            dialogo = DialogoNuevoTransporte(
                parent=self.parent_view,
                datos_iniciales=transporte
            )
            
            if dialogo.exec() == dialogo.DialogCode.Accepted:
                datos_actualizados = dialogo.obtener_datos()
                
                if self.controller:
                    resultado = self.controller.actualizar_transporte(
                        transporte.get('id'), 
                        datos_actualizados
                    )
                    if resultado:
                        self._mostrar_mensaje_exito("Transporte actualizado exitosamente")
                        self._actualizar_tabla_transportes()
                    else:
                        self._mostrar_mensaje_error("Error al actualizar el transporte")
                else:
                    self._mostrar_mensaje_info("Modo demo: Transporte simulado actualizado")

        except Exception as e:

    def eliminar_transporte_seleccionado(self):
        """Elimina el transporte seleccionado."""
        if not hasattr(self.parent_view, 'table_manager'):
            return

        transporte = self.parent_view.table_manager.get_transporte_seleccionado()
        if not transporte:
            self._mostrar_mensaje_advertencia("Seleccione un transporte para eliminar")
            return

        # Confirmar eliminación
        respuesta = QMessageBox.question(
            self.parent_view,
            "Confirmar Eliminación",
            f"¿Está seguro de eliminar el transporte {transporte.get('codigo', 'N/A')}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if respuesta == QMessageBox.StandardButton.Yes:
            try:
                if self.controller:
                    resultado = self.controller.eliminar_transporte(transporte.get('id'))
                    if resultado:
                        self._mostrar_mensaje_exito("Transporte eliminado exitosamente")
                        self._actualizar_tabla_transportes()
                    else:
                        self._mostrar_mensaje_error("Error al eliminar el transporte")
                else:
                    self._mostrar_mensaje_info("Modo demo: Transporte simulado eliminado")

            except Exception as e:

    def buscar_transportes(self, termino_busqueda=""):
        """Busca transportes por término de búsqueda."""
        if hasattr(self.parent_view, 'table_manager'):
            self.parent_view.table_manager.buscar_en_tabla_transportes(termino_busqueda)

    def actualizar_estado_botones(self):
        """Actualiza el estado de los botones según la selección."""
        if not hasattr(self.parent_view, 'table_manager'):
            return

        hay_seleccion = (
            self.parent_view.table_manager.tabla_transportes and
            self.parent_view.table_manager.tabla_transportes.currentRow() >= 0
        )

        # Actualizar botones si existen
        if hasattr(self.parent_view, 'btn_editar_transporte'):
            self.parent_view.btn_editar_transporte.setEnabled(hay_seleccion)
        
        if hasattr(self.parent_view, 'btn_eliminar_transporte'):
            self.parent_view.btn_eliminar_transporte.setEnabled(hay_seleccion)

    def exportar_transportes_excel(self):
        """Exporta la lista de transportes a Excel."""
        try:
            if hasattr(self.parent_view, 'exportar_a_excel'):
                self.parent_view.exportar_a_excel()
            else:
                self._mostrar_mensaje_info("Función de exportación no disponible")

        except Exception as e:

    def _actualizar_tabla_transportes(self):
        """Actualiza la tabla de transportes."""
        if hasattr(self.parent_view, 'table_manager'):
            self.parent_view.table_manager.configurar_tabla_transportes()

    def _mostrar_mensaje_exito(self, mensaje):
        """Muestra mensaje de éxito."""
        QMessageBox.information(self.parent_view, "Éxito", mensaje)

    def _mostrar_mensaje_error(self, mensaje):
        """Muestra mensaje de error."""
        QMessageBox.critical(self.parent_view, "Error", mensaje)

    def _mostrar_mensaje_advertencia(self, mensaje):
        """Muestra mensaje de advertencia."""
        QMessageBox.warning(self.parent_view, "Advertencia", mensaje)

    def _mostrar_mensaje_info(self, mensaje):
        """Muestra mensaje informativo."""
        QMessageBox.information(self.parent_view, "Información", mensaje)

    def obtener_transportes_disponibles(self):
        """Obtiene lista de transportes disponibles."""
        if self.controller and hasattr(self.controller, 'obtener_transportes_disponibles'):
            return self.controller.obtener_transportes_disponibles()
        
        # Datos demo si no hay controlador
        return [
            {
                'id': 1,
                'codigo': 'TRK001',
                'tipo': 'Camión',
                'disponible': True,
                'capacidad_kg': 5000
            },
            {
                'id': 2,
                'codigo': 'VAN002',
                'tipo': 'Furgoneta',
                'disponible': True,
                'capacidad_kg': 1000
            }
        ]

    def obtener_estadisticas_transportes(self):
        """Obtiene estadísticas de transportes."""
        transportes = self.obtener_transportes_disponibles()
        
        total = len(transportes)
        disponibles = len([t for t in transportes if t.get('disponible', False)])
        en_uso = total - disponibles
        
        return {
            'total': total,
            'disponibles': disponibles,
            'en_uso': en_uso,
            'porcentaje_utilizacion': (en_uso / total * 100) if total > 0 else 0
        }