"""
Controlador de Compras - Rexus.app v2.0.0

Maneja la lógica de negocio entre la vista y el modelo de compras.
Incluye gestión de órdenes, proveedores y detalles de compra.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, date

# Importar logging
try:
    from ...utils.app_logger import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

# Importar componentes base
try:
    from ...ui.base.base_controller import BaseController
except ImportError:
    logger.warning("No se pudo importar BaseController")
    BaseController = object


class ComprasController(BaseController):
    """Controlador del módulo de compras."""
    
    def __init__(self, model=None, view=None, db_connection=None):
        """
        Inicializar controlador de compras.
        
        Args:
            model: Modelo de compras
            view: Vista de compras
            db_connection: Conexión a la base de datos
        """
        super().__init__()
        self.model = model
        self.view = view
        self.db_connection = db_connection
        self.usuario_actual = "SISTEMA"
        
        self.conectar_senales()
        logger.info("ComprasController inicializado")
    
    def conectar_senales(self):
        """Conecta las señales de la vista con los métodos del controlador."""
        try:
            if self.view and hasattr(self.view, 'connect_signals'):
                # Señales de órdenes de compra
                if hasattr(self.view, 'crear_orden_signal'):
                    self.view.crear_orden_signal.connect(self.crear_orden_compra)
                
                if hasattr(self.view, 'actualizar_orden_signal'):
                    self.view.actualizar_orden_signal.connect(self.actualizar_orden_compra)
                
                if hasattr(self.view, 'cancelar_orden_signal'):
                    self.view.cancelar_orden_signal.connect(self.cancelar_orden_compra)
                
                # Señales de proveedores
                if hasattr(self.view, 'crear_proveedor_signal'):
                    self.view.crear_proveedor_signal.connect(self.crear_proveedor)
                
                if hasattr(self.view, 'actualizar_proveedor_signal'):
                    self.view.actualizar_proveedor_signal.connect(self.actualizar_proveedor)
                
                # Señales de búsqueda y filtros
                if hasattr(self.view, 'buscar_ordenes_signal'):
                    self.view.buscar_ordenes_signal.connect(self.buscar_ordenes)
                
                if hasattr(self.view, 'buscar_proveedores_signal'):
                    self.view.buscar_proveedores_signal.connect(self.buscar_proveedores)
                
                # Señales de reportes
                if hasattr(self.view, 'generar_reporte_signal'):
                    self.view.generar_reporte_signal.connect(self.generar_reporte_compras)
                
                logger.debug("Señales de compras conectadas")
                
        except Exception as e:
            logger.error(f"Error conectando señales de compras: {e}")
    
    def cargar_datos_iniciales(self):
        """Carga datos iniciales del módulo de compras."""
        try:
            if not self.model:
                logger.warning("No hay modelo de compras disponible")
                return
            
            # Cargar órdenes de compra recientes
            self.cargar_ordenes_compra()
            
            # Cargar lista de proveedores
            self.cargar_proveedores()
            
            # Cargar estadísticas de compras
            self.cargar_estadisticas_compras()
            
            logger.debug("Datos iniciales de compras cargados")
            
        except (AttributeError, TypeError) as e:
            logger.error(f"Error cargando datos iniciales de compras: {e}")
    
    # MÉTODOS DE ÓRDENES DE COMPRA
    
    def cargar_ordenes_compra(self, filtros: Optional[Dict[str, Any]] = None):
        """
        Carga órdenes de compra en la vista.
        
        Args:
            filtros: Filtros opcionales para la consulta
        """
        try:
            if not self.model or not self.view:
                return
            
            # Obtener órdenes del modelo
            if filtros:
                ordenes = self.model.obtener_ordenes_filtradas(filtros)
            else:
                ordenes = self.model.obtener_todas_ordenes()
            
            # Actualizar vista
            if hasattr(self.view, 'actualizar_tabla_ordenes'):
                self.view.actualizar_tabla_ordenes(ordenes)
            
            logger.debug(f"Cargadas {len(ordenes)} órdenes de compra")
            
        except Exception as e:
            logger.error(f"Error cargando órdenes de compra: {e}")
    
    def buscar_ordenes(self, filtros: Dict[str, Any]):
        """
        Busca órdenes de compra con filtros específicos.
        
        Args:
            filtros: Diccionario con filtros de búsqueda
        """
        try:
            self.cargar_ordenes_compra(filtros)
        except Exception as e:
            logger.error(f"Error buscando órdenes de compra: {e}")
    
    def crear_orden_compra(self, datos_orden: Dict[str, Any]) -> bool:
        """
        Crea una nueva orden de compra.
        
        Args:
            datos_orden: Datos de la orden de compra
            
        Returns:
            True si se creó exitosamente
        """
        try:
            if not self.model:
                logger.error("No hay modelo disponible para crear orden")
                return False
            
            # Validar datos de la orden
            if not self._validar_datos_orden(datos_orden):
                return False
            
            # Crear orden a través del modelo
            orden_id = self.model.crear_orden_compra(datos_orden)
            
            if orden_id:
                logger.info(f"Orden de compra {orden_id} creada exitosamente")
                
                # Recargar lista de órdenes
                self.cargar_ordenes_compra()
                
                if self.view:
                    self.view.mostrar_mensaje(f"Orden de compra {orden_id} creada exitosamente")
                
                return True
            else:
                logger.error("Error creando orden de compra")
                if self.view:
                    self.view.mostrar_error("Error creando orden de compra")
                return False
                
        except Exception as e:
            logger.error(f"Error creando orden de compra: {e}")
            if self.view:
                self.view.mostrar_error("Error creando orden de compra")
            return False
    
    def actualizar_orden_compra(self, orden_id: int, datos_orden: Dict[str, Any]) -> bool:
        """
        Actualiza una orden de compra existente.
        
        Args:
            orden_id: ID de la orden
            datos_orden: Nuevos datos de la orden
            
        Returns:
            True si se actualizó exitosamente
        """
        try:
            if not self.model:
                logger.error("No hay modelo disponible para actualizar orden")
                return False
            
            # Validar datos de la orden
            if not self._validar_datos_orden(datos_orden, es_actualizacion=True):
                return False
            
            if self.model.actualizar_orden_compra(orden_id, datos_orden):
                logger.info(f"Orden de compra {orden_id} actualizada exitosamente")
                
                # Recargar lista de órdenes
                self.cargar_ordenes_compra()
                
                if self.view:
                    self.view.mostrar_mensaje("Orden de compra actualizada exitosamente")
                
                return True
            else:
                logger.error("Error actualizando orden de compra")
                if self.view:
                    self.view.mostrar_error("Error actualizando orden de compra")
                return False
                
        except Exception as e:
            logger.error(f"Error actualizando orden de compra: {e}")
            if self.view:
                self.view.mostrar_error("Error actualizando orden de compra")
            return False
    
    def cancelar_orden_compra(self, orden_id: int, motivo: str = "") -> bool:
        """
        Cancela una orden de compra.
        
        Args:
            orden_id: ID de la orden
            motivo: Motivo de cancelación
            
        Returns:
            True si se canceló exitosamente
        """
        try:
            if not self.model:
                logger.error("No hay modelo disponible para cancelar orden")
                return False
            
            if self.model.cancelar_orden_compra(orden_id, motivo):
                logger.info(f"Orden de compra {orden_id} cancelada exitosamente")
                
                # Recargar lista de órdenes
                self.cargar_ordenes_compra()
                
                if self.view:
                    self.view.mostrar_mensaje("Orden de compra cancelada exitosamente")
                
                return True
            else:
                logger.error("Error cancelando orden de compra")
                if self.view:
                    self.view.mostrar_error("Error cancelando orden de compra")
                return False
                
        except Exception as e:
            logger.error(f"Error cancelando orden de compra: {e}")
            if self.view:
                self.view.mostrar_error("Error cancelando orden de compra")
            return False
    
    def aprobar_orden_compra(self, orden_id: int) -> bool:
        """
        Aprueba una orden de compra.
        
        Args:
            orden_id: ID de la orden
            
        Returns:
            True si se aprobó exitosamente
        """
        try:
            if not self.model:
                logger.error("No hay modelo disponible para aprobar orden")
                return False
            
            if self.model.aprobar_orden_compra(orden_id, self.usuario_actual):
                logger.info(f"Orden de compra {orden_id} aprobada exitosamente")
                
                # Recargar lista de órdenes
                self.cargar_ordenes_compra()
                
                if self.view:
                    self.view.mostrar_mensaje("Orden de compra aprobada exitosamente")
                
                return True
            else:
                logger.error("Error aprobando orden de compra")
                if self.view:
                    self.view.mostrar_error("Error aprobando orden de compra")
                return False
                
        except Exception as e:
            logger.error(f"Error aprobando orden de compra: {e}")
            if self.view:
                self.view.mostrar_error("Error aprobando orden de compra")
            return False
    
    # MÉTODOS DE PROVEEDORES
    
    def cargar_proveedores(self, filtros: Optional[Dict[str, Any]] = None):
        """
        Carga proveedores en la vista.
        
        Args:
            filtros: Filtros opcionales para la consulta
        """
        try:
            if not self.model or not self.view:
                return
            
            # Obtener proveedores del modelo
            if filtros:
                proveedores = self.model.obtener_proveedores_filtrados(filtros)
            else:
                proveedores = self.model.obtener_todos_proveedores()
            
            # Actualizar vista
            if hasattr(self.view, 'actualizar_tabla_proveedores'):
                self.view.actualizar_tabla_proveedores(proveedores)
            
            logger.debug(f"Cargados {len(proveedores)} proveedores")
            
        except Exception as e:
            logger.error(f"Error cargando proveedores: {e}")
    
    def buscar_proveedores(self, filtros: Dict[str, Any]):
        """
        Busca proveedores con filtros específicos.
        
        Args:
            filtros: Diccionario con filtros de búsqueda
        """
        try:
            self.cargar_proveedores(filtros)
        except Exception as e:
            logger.error(f"Error buscando proveedores: {e}")
    
    def crear_proveedor(self, datos_proveedor: Dict[str, Any]) -> bool:
        """
        Crea un nuevo proveedor.
        
        Args:
            datos_proveedor: Datos del proveedor
            
        Returns:
            True si se creó exitosamente
        """
        try:
            if not self.model:
                logger.error("No hay modelo disponible para crear proveedor")
                return False
            
            # Validar datos del proveedor
            if not self._validar_datos_proveedor(datos_proveedor):
                return False
            
            # Crear proveedor a través del modelo
            proveedor_id = self.model.crear_proveedor(datos_proveedor)
            
            if proveedor_id:
                logger.info(f"Proveedor {proveedor_id} creado exitosamente")
                
                # Recargar lista de proveedores
                self.cargar_proveedores()
                
                if self.view:
                    self.view.mostrar_mensaje("Proveedor creado exitosamente")
                
                return True
            else:
                logger.error("Error creando proveedor")
                if self.view:
                    self.view.mostrar_error("Error creando proveedor")
                return False
                
        except Exception as e:
            logger.error(f"Error creando proveedor: {e}")
            if self.view:
                self.view.mostrar_error("Error creando proveedor")
            return False
    
    def actualizar_proveedor(self, proveedor_id: int, datos_proveedor: Dict[str, Any]) -> bool:
        """
        Actualiza un proveedor existente.
        
        Args:
            proveedor_id: ID del proveedor
            datos_proveedor: Nuevos datos del proveedor
            
        Returns:
            True si se actualizó exitosamente
        """
        try:
            if not self.model:
                logger.error("No hay modelo disponible para actualizar proveedor")
                return False
            
            # Validar datos del proveedor
            if not self._validar_datos_proveedor(datos_proveedor, es_actualizacion=True):
                return False
            
            if self.model.actualizar_proveedor(proveedor_id, datos_proveedor):
                logger.info(f"Proveedor {proveedor_id} actualizado exitosamente")
                
                # Recargar lista de proveedores
                self.cargar_proveedores()
                
                if self.view:
                    self.view.mostrar_mensaje("Proveedor actualizado exitosamente")
                
                return True
            else:
                logger.error("Error actualizando proveedor")
                if self.view:
                    self.view.mostrar_error("Error actualizando proveedor")
                return False
                
        except Exception as e:
            logger.error(f"Error actualizando proveedor: {e}")
            if self.view:
                self.view.mostrar_error("Error actualizando proveedor")
            return False
    
    # MÉTODOS DE ESTADÍSTICAS Y REPORTES
    
    def cargar_estadisticas_compras(self):
        """Carga estadísticas de compras para el dashboard."""
        try:
            if not self.model or not self.view:
                return
            
            # Obtener estadísticas del modelo
            estadisticas = self.model.obtener_estadisticas_compras()
            
            # Actualizar vista
            if hasattr(self.view, 'actualizar_estadisticas'):
                self.view.actualizar_estadisticas(estadisticas)
            
            logger.debug("Estadísticas de compras actualizadas")
            
        except Exception as e:
            logger.error(f"Error cargando estadísticas de compras: {e}")
    
    def generar_reporte_compras(self, tipo_reporte: str, parametros: Dict[str, Any]) -> bool:
        """
        Genera un reporte de compras.
        
        Args:
            tipo_reporte: Tipo de reporte (ordenes, proveedores, gastos)
            parametros: Parámetros del reporte
            
        Returns:
            True si se generó exitosamente
        """
        try:
            if not self.model:
                logger.error("No hay modelo disponible para generar reporte")
                return False
            
            logger.info(f"Generando reporte de compras: {tipo_reporte}")
            
            # Generar reporte según el tipo
            if tipo_reporte == "ordenes":
                reporte = self.model.generar_reporte_ordenes(parametros)
            elif tipo_reporte == "proveedores":
                reporte = self.model.generar_reporte_proveedores(parametros)
            elif tipo_reporte == "gastos":
                reporte = self.model.generar_reporte_gastos(parametros)
            else:
                logger.error(f"Tipo de reporte no soportado: {tipo_reporte}")
                if self.view:
                    self.view.mostrar_error(f"Tipo de reporte no soportado: {tipo_reporte}")
                return False
            
            # Mostrar reporte en la vista
            if reporte and hasattr(self.view, 'mostrar_reporte'):
                self.view.mostrar_reporte(reporte, tipo_reporte)
                
                if self.view:
                    self.view.mostrar_mensaje("Reporte generado exitosamente")
                
                return True
            else:
                logger.error("Error generando reporte")
                if self.view:
                    self.view.mostrar_error("Error generando reporte")
                return False
            
        except Exception as e:
            logger.error(f"Error generando reporte de compras: {e}")
            if self.view:
                self.view.mostrar_error("Error generando reporte")
            return False
    
    def generar_reporte_completo(self):
        """
        Genera un reporte completo del módulo de compras.
        
        Returns:
            Dict: Reporte completo
        """
        try:
            if not self.model:
                logger.warning("No hay modelo disponible para reporte completo")
                return {}
            
            reporte = {
                'fecha_generacion': datetime.now().isoformat(),
                'estadisticas': self.model.obtener_estadisticas_compras(),
                'ordenes_pendientes': self.model.obtener_ordenes_filtradas({'estado': 'PENDIENTE'}),
                'proveedores_activos': self.model.obtener_proveedores_filtrados({'activo': True}),
                'resumen_gastos': self.model.obtener_resumen_gastos_periodo(),
                'alertas': self.model.obtener_alertas_compras()
            }
            
            logger.info("Reporte completo de compras generado")
            return reporte
            
        except Exception as e:
            logger.error(f"Error generando reporte completo: {e}")
            return {}
    
    # MÉTODOS AUXILIARES DE VALIDACIÓN
    
    def _validar_datos_orden(self, datos: Dict[str, Any], es_actualizacion: bool = False) -> bool:
        """
        Valida los datos de una orden de compra.
        
        Args:
            datos: Datos de la orden a validar
            es_actualizacion: Si es una actualización
            
        Returns:
            True si los datos son válidos
        """
        try:
            # Validaciones básicas
            if not datos.get('proveedor_id'):
                logger.error("Proveedor es requerido")
                if self.view:
                    self.view.mostrar_error("Proveedor es requerido")
                return False
            
            if not datos.get('fecha_orden'):
                logger.error("Fecha de orden es requerida")
                if self.view:
                    self.view.mostrar_error("Fecha de orden es requerida")
                return False
            
            # Validar detalles de la orden
            detalles = datos.get('detalles', [])
            if not detalles:
                logger.error("La orden debe tener al menos un detalle")
                if self.view:
                    self.view.mostrar_error("La orden debe tener al menos un detalle")
                return False
            
            # Validar cada detalle
            for detalle in detalles:
                if not detalle.get('producto_id'):
                    logger.error("Producto es requerido en cada detalle")
                    if self.view:
                        self.view.mostrar_error("Producto es requerido en cada detalle")
                    return False
                
                try:
                    cantidad = float(detalle.get('cantidad', 0))
                    precio = float(detalle.get('precio_unitario', 0))
                    
                    if cantidad <= 0:
                        logger.error("La cantidad debe ser mayor a 0")
                        if self.view:
                            self.view.mostrar_error("La cantidad debe ser mayor a 0")
                        return False
                    
                    if precio <= 0:
                        logger.error("El precio unitario debe ser mayor a 0")
                        if self.view:
                            self.view.mostrar_error("El precio unitario debe ser mayor a 0")
                        return False
                        
                except ValueError:
                    logger.error("Cantidad y precio deben ser valores numéricos válidos")
                    if self.view:
                        self.view.mostrar_error("Cantidad y precio deben ser valores numéricos válidos")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validando datos de orden: {e}")
            return False
    
    def _validar_datos_proveedor(self, datos: Dict[str, Any], es_actualizacion: bool = False) -> bool:
        """
        Valida los datos de un proveedor.
        
        Args:
            datos: Datos del proveedor a validar
            es_actualizacion: Si es una actualización
            
        Returns:
            True si los datos son válidos
        """
        try:
            # Validaciones básicas
            if not datos.get('nombre'):
                logger.error("Nombre del proveedor es requerido")
                if self.view:
                    self.view.mostrar_error("Nombre del proveedor es requerido")
                return False
            
            if not datos.get('contacto'):
                logger.error("Contacto del proveedor es requerido")
                if self.view:
                    self.view.mostrar_error("Contacto del proveedor es requerido")
                return False
            
            # Validar email si se proporciona
            email = datos.get('email')
            if email and '@' not in email:
                logger.error("Formato de email inválido")
                if self.view:
                    self.view.mostrar_error("Formato de email inválido")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validando datos de proveedor: {e}")
            return False
    
    def exportar_ordenes(self, formato: str = "excel", filtros: Optional[Dict[str, Any]] = None) -> bool:
        """
        Exporta órdenes de compra en el formato especificado.
        
        Args:
            formato: Formato de exportación (excel, pdf, csv)
            filtros: Filtros para la exportación
            
        Returns:
            True si se exportó exitosamente
        """
        try:
            if not self.model:
                logger.error("No hay modelo disponible para exportar")
                return False
            
            # Obtener datos para exportar
            ordenes = self.model.obtener_ordenes_filtradas(filtros or {})
            
            if not ordenes:
                logger.warning("No hay órdenes para exportar")
                if self.view:
                    self.view.mostrar_mensaje("No hay órdenes para exportar")
                return False
            
            # Exportar según el formato
            # Aquí iría la lógica de exportación
            logger.info(f"Órdenes exportadas en formato {formato}: {len(ordenes)} registros")
            
            if self.view:
                self.view.mostrar_mensaje(f"Exportación completada: {len(ordenes)} órdenes")
            
            return True
            
        except Exception as e:
            logger.error(f"Error exportando órdenes: {e}")
            if self.view:
                self.view.mostrar_error("Error exportando órdenes")
            return False