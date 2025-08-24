"""Controlador de Obras"""

import logging
from typing import Dict, Any, Optional

from PyQt6.QtWidgets import QMessageBox

logger = logging.getLogger(__name__)


class ObrasController:
    """Controlador para el módulo de obras."""
    
    def __init__(self, model=None, view=None):
        """Inicializar controlador."""
        self.model = model
        self.view = view
        self.usuario_actual = "sistema"
        self.registros_por_pagina = 50
        self.pagina_actual = 0
        
    def _ensure_model_available(self, operation: str = "operación") -> bool:
        """Verificar que el modelo esté disponible."""
        if not self.model:
            self.mostrar_mensaje_error(f"Modelo no disponible para {operation}")
            return False
        return True
    
    def _ensure_view_available(self, operation: str = "operación") -> bool:
        """Verificar que la vista esté disponible."""
        if not self.view:
            logger.error(f"Vista no disponible para {operation}")
            return False
        return True
    
    def mostrar_mensaje_error(self, mensaje: str) -> None:
        """Mostrar mensaje de error."""
        if self.view:
            QMessageBox.critical(self.view, "Error", mensaje)
        else:
            logger.error(mensaje)
    
    def mostrar_error(self, titulo: str, mensaje: str) -> None:
        """Mostrar mensaje de error con título."""
        if self.view:
            QMessageBox.critical(self.view, titulo, mensaje)
        else:
            logger.error(f"{titulo}: {mensaje}")
    
    def mostrar_exito(self, mensaje: str) -> None:
        """Mostrar mensaje de éxito."""
        if self.view:
            QMessageBox.information(self.view, "Éxito", mensaje)
        else:
            logger.info(mensaje)
    
    def mostrar_advertencia(self, mensaje: str) -> None:
        """Mostrar mensaje de advertencia."""
        if self.view:
            QMessageBox.warning(self.view, "Advertencia", mensaje)
        else:
            logger.warning(mensaje)
    
    def eliminar_obra_seleccionada(self) -> None:
        """Eliminar la obra seleccionada."""
        if not self._ensure_model_available("eliminar obra") or not self._ensure_view_available("eliminar obra"):
            return
            
        try:
            # Verificar métodos de vista
            if self.view is not None and hasattr(self.view, 'obtener_obra_seleccionada'):
                obra_seleccionada = self.view.obtener_obra_seleccionada()
            else:
                self.mostrar_error("Error", "La vista no implementa obtener_obra_seleccionada")
                return
                
            if not obra_seleccionada:
                self.mostrar_advertencia("Seleccione una obra para eliminar")
                return
                
            # Confirmar eliminación
            respuesta = QMessageBox.question(
                self.view,
                "Confirmar eliminación",
                f"¿Está seguro de que desea eliminar la obra '{obra_seleccionada.get('nombre', 'Desconocida')}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if respuesta == QMessageBox.StandardButton.Yes:
                # Verificar métodos de modelo
                if self.model is not None and hasattr(self.model, 'eliminar_obra'):
                    exito, mensaje = self.model.eliminar_obra(obra_seleccionada["id"], self.usuario_actual)
                else:
                    self.mostrar_error("Error", "El modelo no implementa eliminar_obra")
                    return
                    
                if exito:
                    self.mostrar_exito(mensaje)
                    self.cargar_obras()  # Recargar la tabla
                else:
                    self.mostrar_error("Error", f"No se pudo eliminar la obra: {mensaje}")
                    
        except Exception as e:
            logger.error(f"Error eliminando obra: {e}")
            self.mostrar_error("Error", f"Error inesperado eliminando obra: {str(e)}")
    
    def cambiar_estado_obra(self) -> None:
        """Cambiar el estado de la obra seleccionada."""
        if not self._ensure_model_available("cambiar estado") or not self._ensure_view_available("cambiar estado"):
            return
            
        try:
            # Verificar métodos de vista
            if self.view is not None and hasattr(self.view, 'obtener_obra_seleccionada'):
                obra_seleccionada = self.view.obtener_obra_seleccionada()
            else:
                self.mostrar_error("Error", "La vista no implementa obtener_obra_seleccionada")
                return
                
            if not obra_seleccionada:
                self.mostrar_advertencia("Seleccione una obra para cambiar su estado")
                return
                
            # Solicitar nuevo estado
            if self.view is not None and hasattr(self.view, 'mostrar_dialogo_cambiar_estado'):
                nuevo_estado = self.view.mostrar_dialogo_cambiar_estado(obra_seleccionada["estado_actual"])
            else:
                # Estados básicos si no hay diálogo
                estados = ["planificada", "en_progreso", "pausada", "completada", "cancelada"]
                nuevo_estado = estados[0]  # Por defecto
                
            if nuevo_estado and nuevo_estado != obra_seleccionada["estado_actual"]:
                # Verificar métodos de modelo
                if self.model is not None and hasattr(self.model, 'cambiar_estado_obra'):
                    exito, mensaje = self.model.cambiar_estado_obra(
                        obra_seleccionada["id"], 
                        nuevo_estado, 
                        self.usuario_actual
                    )
                else:
                    self.mostrar_error("Error", "El modelo no implementa cambiar_estado_obra o es None")
                    return
                    
                if exito:
                    self.mostrar_exito(mensaje)
                    self.cargar_obras()  # Recargar la tabla
                else:
                    self.mostrar_error("Error", f"No se pudo cambiar el estado: {mensaje}")
                    
        except Exception as e:
            logger.error(f"Error cambiando estado: {e}")
            self.mostrar_error("Error", f"Error inesperado cambiando estado: {str(e)}")
    
    def cargar_obras(self, filtros: Optional[Dict[str, Any]] = None) -> None:
        """Cargar las obras en la vista."""
        if not self._ensure_model_available("cargar obras") or not self._ensure_view_available("cargar obras"):
            return
            
        try:
            # Aplicar filtros si existen
            if filtros is None and self.view is not None and hasattr(self.view, 'obtener_filtros_aplicados'):
                filtros = self.view.obtener_filtros_aplicados()
                
            # Verificar métodos de modelo
            if self.model is not None and hasattr(self.model, 'obtener_obras'):
                obras = self.model.obtener_obras(filtros)
            else:
                self.mostrar_error("Error", "El modelo no implementa obtener_obras o es None")
                return
                
            # Verificar métodos de vista
            if self.view is not None and hasattr(self.view, 'cargar_obras_en_tabla'):
                self.view.cargar_obras_en_tabla(obras)
            else:
                logger.warning("La vista no implementa cargar_obras_en_tabla o self.view es None")
                
            # Actualizar estadísticas si está disponible
            self.actualizar_estadisticas()
            
        except Exception as e:
            logger.error(f"Error cargando obras: {e}")
            self.mostrar_error("Error", f"Error cargando obras: {str(e)}")
    
    def actualizar_estadisticas(self) -> None:
        """Actualizar las estadísticas en la vista."""
        if not self._ensure_model_available("actualizar estadísticas"):
            return
            
        try:
            # Verificar que el modelo no sea None y que tenga el método
            if self.model is not None and hasattr(self.model, 'obtener_estadisticas_obras'):
                estadisticas = self.model.obtener_estadisticas_obras()
            else:
                logger.warning("El modelo no implementa obtener_estadisticas_obras o es None")
                return
                
            # Verificar métodos de vista
            if self.view and hasattr(self.view, 'actualizar_estadisticas'):
                self.view.actualizar_estadisticas(estadisticas)
            else:
                logger.warning("La vista no implementa actualizar_estadisticas")
                
        except Exception as e:
            logger.error(f"Error actualizando estadísticas: {e}")
    
    def buscar_obras(self, termino: str) -> None:
        """Buscar obras por término."""
        if not self._ensure_model_available("buscar obras"):
            return
            
        try:
            filtros = {"busqueda": termino} if termino else None
            self.cargar_obras(filtros)
            
        except Exception as e:
            logger.error(f"Error buscando obras: {e}")
            self.mostrar_error("Error", f"Error en búsqueda: {str(e)}")
    
    def crear_nueva_obra(self, datos_obra: Dict[str, Any]) -> Optional[int]:
        """Crear una nueva obra."""
        if not self._ensure_model_available("crear obra"):
            return None
            
        try:
            # Verificar que el modelo no sea None y que tenga el método
            if self.model is not None and hasattr(self.model, 'crear_obra'):
                exito, resultado = self.model.crear_obra(datos_obra, self.usuario_actual)
            else:
                self.mostrar_error("Error", "El modelo no implementa crear_obra")
                return None
                
            if exito:
                self.mostrar_exito("Obra creada exitosamente")
                self.cargar_obras()  # Recargar la tabla
                return resultado  # ID de la nueva obra
            else:
                self.mostrar_error("Error", f"No se pudo crear la obra: {resultado}")
                return None
                
        except Exception as e:
            logger.error(f"Error creando obra: {e}")
            self.mostrar_error("Error", f"Error creando obra: {str(e)}")
            return None
    
    def actualizar_obra(self, obra_id: int, datos_actualizados: Dict[str, Any]) -> bool:
        """Actualizar una obra existente."""
        if not self._ensure_model_available("actualizar obra"):
            return False
            
        try:
            # Verificar que el modelo no sea None y que tenga el método
            if self.model is not None and hasattr(self.model, 'actualizar_obra'):
                exito, mensaje = self.model.actualizar_obra(obra_id, datos_actualizados, self.usuario_actual)
            else:
                self.mostrar_error("Error", "El modelo no implementa actualizar_obra")
                return False
                
            if exito:
                self.mostrar_exito("Obra actualizada exitosamente")
                self.cargar_obras()  # Recargar la tabla
                return True
            else:
                self.mostrar_error("Error", f"No se pudo actualizar la obra: {mensaje}")
                return False
                
        except Exception as e:
            logger.error(f"Error actualizando obra: {e}")
            self.mostrar_error("Error", f"Error actualizando obra: {str(e)}")
            return False
    
    def obtener_obra_por_codigo(self, codigo: str) -> Optional[Dict[str, Any]]:
        """Obtener obra por código."""
        if not self._ensure_model_available("obtener obra por código"):
            return None
            
        try:
            # Verificar que el modelo no sea None y que tenga el método
            if self.model is not None and hasattr(self.model, 'obtener_obra_por_codigo'):
                return self.model.obtener_obra_por_codigo(codigo)
            else:
                self.mostrar_error("Error", "El modelo no implementa obtener_obra_por_codigo")
                return None
                
        except Exception as e:
            logger.error(f"Error obteniendo obra por código: {e}")
            self.mostrar_error("Error", f"Error obteniendo obra: {str(e)}")
            return None
    
    def cargar_pagina(self, pagina: int) -> None:
        """Cargar una página específica de obras."""
        if not self._ensure_model_available("cargar página"):
            return
            
        try:
            self.pagina_actual = pagina
            offset = pagina * self.registros_por_pagina
            
            # Verificar que el modelo no sea None y que tenga el método
            if self.model is not None and hasattr(self.model, 'obtener_datos_paginados'):
                datos, total = self.model.obtener_datos_paginados(offset, self.registros_por_pagina)
            else:
                self.mostrar_error("Error", "El modelo no implementa obtener_datos_paginados")
                return
                
            # Verificar métodos de vista
            if self.view and hasattr(self.view, 'cargar_obras_en_tabla'):
                self.view.cargar_obras_en_tabla(datos)
            
            if self.view and hasattr(self.view, 'actualizar_paginacion'):
                total_paginas = (total + self.registros_por_pagina - 1) // self.registros_por_pagina
                self.view.actualizar_paginacion(pagina, total_paginas)
                
        except Exception as e:
            logger.error(f"Error cargando página: {e}")
            self.mostrar_error("Error", f"Error cargando página: {str(e)}")
    
    def exportar_obras(self, formato: str = "xlsx") -> None:
        """Exportar las obras a un archivo."""
        if not self._ensure_model_available("exportar obras"):
            return
            
        try:
            # Verificar que el modelo no sea None y que tenga el método
            if self.model is not None and hasattr(self.model, 'obtener_datos_paginados'):
                datos, total = self.model.obtener_datos_paginados(0, 10000)  # Obtener todos los registros
            else:
                self.mostrar_error("Error", "El modelo no implementa obtener_datos_paginados")
                return
                
            if not datos:
                self.mostrar_advertencia("No hay obras para exportar")
                return
                
            # Crear el archivo de exportación
            try:
                from datetime import datetime
                archivo_nombre = f"obras_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{formato}"
                
                # Datos básicos para exportar
                export_data = {
                    'obras': datos,
                    'total': total,
                    'fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                # Guardar archivo (implementación básica)
                import json
                with open(archivo_nombre, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, ensure_ascii=False, indent=2)
                    
                self.mostrar_exito(f"Obras exportadas exitosamente a {archivo_nombre}")
                
            except ImportError:
                logger.warning("Módulo de exportación no disponible")
                self.mostrar_advertencia("Funcionalidad de exportación no disponible")
                
        except Exception as e:
            logger.error(f"Error exportando obras: {e}")
            self.mostrar_error("Error", f"Error exportando obras: {str(e)}")
    
    def configurar_vista(self, configuracion: Dict[str, Any]) -> None:
        """Configurar la vista con parámetros específicos."""
        if not self._ensure_view_available("configurar vista"):
            return
            
        try:
            # Aplicar configuración si la vista lo soporta
            if self.view and hasattr(self.view, 'aplicar_configuracion'):
                self.view.aplicar_configuracion(configuracion)
            else:
                logger.warning("La vista no implementa aplicar_configuracion o self.view es None")
                
        except Exception as e:
            logger.error(f"Error configurando vista: {e}")
            self.mostrar_error("Error", f"Error en configuración: {str(e)}")
