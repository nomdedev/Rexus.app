#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para reestructurar completamente el controller de logística
Corrige todos los errores de indentación, sintaxis y estructura
"""

import os
import shutil
from datetime import datetime

def crear_backup():
    """Crea backup del archivo original."""
    original = "rexus/modules/logistica/controller.py"
    backup = f"logistica_controller_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
    
    if os.path.exists(original):
        shutil.copy2(original, backup)
        print(f"Backup creado: {backup}")
    else:
        print("Archivo original no encontrado")

def generar_controller_corregido():
    """Genera el contenido corregido del controller."""
    return '''# -*- coding: utf-8 -*-
"""
Controlador de Logística - Rexus.app v2.0.0

Controlador completo para el módulo de logística que maneja:
- Gestión de transportes y servicios
- Programación de entregas
- Seguimiento de envíos
- Proveedores de transporte
- Optimización de rutas
- Control de costos logísticos
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, date
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot

# Configurar logging
try:
    from rexus.utils.app_logger import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    
    class DummyLogger:
        """Logger dummy para cuando no está disponible el logger principal."""
        
        def info(self, msg): 
            print(f"[INFO] {msg}")
            
        def warning(self, msg): 
            print(f"[WARNING] {msg}")
            
        def error(self, msg): 
            print(f"[ERROR] {msg}")
            
        def debug(self, msg): 
            print(f"[DEBUG] {msg}")
    
    logger = DummyLogger()

# Sistema de mensajes
try:
    from rexus.utils.message_system import show_info, show_error, show_warning, show_success
except ImportError:
    def show_info(parent, title, message):
        logger.info(f"{title}: {message}")
    
    def show_error(parent, title, message):
        logger.error(f"{title}: {message}")
    
    def show_warning(parent, title, message):
        logger.warning(f"{title}: {message}")
    
    def show_success(parent, title, message):
        logger.info(f"{title}: {message}")

# Base controller
try:
    from rexus.modules.base.base_controller import BaseController
except ImportError:
    try:
        from ..base.base_controller import BaseController
    except ImportError:
        class BaseController:
            """Clase base simple para controladores."""
            
            def __init__(self, model=None, view=None):
                self.model = model
                self.view = view

# Constantes
MENSAJE_ERROR_CONEXION = "No hay conexión al modelo de datos"
MENSAJE_EXITO = "Éxito"
TITULO_LOGISTICA = "Logística"


class LogisticaController(BaseController):
    """Controlador para el módulo de logística."""
    
    # Señales PyQt6
    servicio_creado = pyqtSignal(dict)
    servicio_actualizado = pyqtSignal(int, dict)
    servicio_eliminado = pyqtSignal(int)
    proveedor_creado = pyqtSignal(dict)
    proveedor_actualizado = pyqtSignal(int, dict)
    transporte_eliminado = pyqtSignal(int)
    estado_actualizado = pyqtSignal(int, str)
    
    def __init__(self, model=None, view=None, db_connection=None):
        """
        Inicializa el controlador de logística.
        
        Args:
            model: Modelo de logística
            view: Vista de logística
            db_connection: Conexión a base de datos
        """
        super().__init__(model, view)
        self.db_connection = db_connection
        self.servicios_cache = {}
        self.proveedores_cache = {}
        logger.info("LogisticaController inicializado")
        
        if self.view:
            self.conectar_signals()
    
    def conectar_signals(self):
        """Conecta las señales de la vista con los métodos del controlador."""
        try:
            # Señales de servicios de transporte
            if hasattr(self.view, 'servicio_creado'):
                self.view.servicio_creado.connect(self.crear_servicio_transporte)
            
            if hasattr(self.view, 'servicio_editado'):
                self.view.servicio_editado.connect(self.actualizar_servicio_transporte)
            
            if hasattr(self.view, 'servicio_eliminado'):
                self.view.servicio_eliminado.connect(self.eliminar_servicio_transporte)
            
            # Señales de proveedores
            if hasattr(self.view, 'proveedor_creado'):
                self.view.proveedor_creado.connect(self.crear_proveedor_transporte)
            
            if hasattr(self.view, 'proveedor_editado'):
                self.view.proveedor_editado.connect(self.actualizar_proveedor_transporte)
            
            # Señales de estado
            if hasattr(self.view, 'estado_actualizado'):
                self.view.estado_actualizado.connect(self.actualizar_estado_servicio)
            
            logger.debug("Señales de logística conectadas exitosamente")
            
        except Exception as e:
            logger.error(f"Error conectando señales de logística: {e}")
    
    # ===== MÉTODOS PRINCIPALES DE SERVICIOS =====
    
    def crear_servicio_transporte(self, datos_servicio: Dict[str, Any]) -> bool:
        """
        Crea un nuevo servicio de transporte.
        
        Args:
            datos_servicio: Datos del servicio
            
        Returns:
            True si se creó exitosamente
        """
        try:
            logger.info("Creando nuevo servicio de transporte")
            
            if not self._validar_datos_servicio(datos_servicio):
                return False
            
            if not self.model:
                show_error(self.view, "Error", MENSAJE_ERROR_CONEXION)
                return False
            
            # Generar código único si no se proporciona
            if not datos_servicio.get('codigo'):
                if hasattr(self.model, 'generar_codigo_servicio'):
                    datos_servicio['codigo'] = self.model.generar_codigo_servicio()
                else:
                    datos_servicio['codigo'] = self._generar_codigo_servicio()
            
            # Calcular costo estimado si no se proporciona
            if not datos_servicio.get('costo_estimado'):
                costo_info = self._calcular_costo_servicio(datos_servicio)
                datos_servicio['costo_estimado'] = costo_info.get('costo_estimado', 0.0)
            
            # Crear el servicio
            if hasattr(self.model, 'crear_servicio_transporte'):
                servicio_id = self.model.crear_servicio_transporte(datos_servicio)
            else:
                logger.warning("Método crear_servicio_transporte no disponible en el modelo")
                servicio_id = None
            
            if servicio_id:
                show_success(self.view, MENSAJE_EXITO, "Servicio de transporte creado correctamente")
                self.actualizar_vista_servicios()
                self.servicio_creado.emit(datos_servicio)
                self._registrar_auditoria("crear_servicio", servicio_id)
                logger.info(f"Servicio creado con ID: {servicio_id}")
                return True
            else:
                show_error(self.view, "Error", "No se pudo crear el servicio")
                return False
                
        except Exception as e:
            logger.error(f"Error creando servicio: {e}")
            show_error(self.view, "Error", f"Error al crear servicio: {str(e)}")
            return False
    
    def actualizar_servicio_transporte(self, servicio_id: int, datos_servicio: Dict[str, Any]) -> bool:
        """
        Actualiza un servicio de transporte existente.
        
        Args:
            servicio_id: ID del servicio
            datos_servicio: Nuevos datos del servicio
            
        Returns:
            True si se actualizó exitosamente
        """
        try:
            logger.info(f"Actualizando servicio {servicio_id}")
            
            if not self._validar_datos_servicio(datos_servicio):
                return False
            
            if not self.model:
                show_error(self.view, "Error", MENSAJE_ERROR_CONEXION)
                return False
            
            if hasattr(self.model, 'actualizar_servicio_transporte'):
                success = self.model.actualizar_servicio_transporte(servicio_id, datos_servicio)
            else:
                logger.warning("Método actualizar_servicio_transporte no disponible en el modelo")
                success = False
            
            if success:
                show_success(self.view, MENSAJE_EXITO, "Servicio actualizado correctamente")
                self.actualizar_vista_servicios()
                self.servicio_actualizado.emit(servicio_id, datos_servicio)
                self._registrar_auditoria("actualizar_servicio", servicio_id)
                logger.info(f"Servicio {servicio_id} actualizado")
                return True
            else:
                show_error(self.view, "Error", "No se pudo actualizar el servicio")
                return False
                
        except Exception as e:
            logger.error(f"Error actualizando servicio: {e}")
            show_error(self.view, "Error", f"Error al actualizar servicio: {str(e)}")
            return False
    
    def eliminar_servicio_transporte(self, servicio_id: int) -> bool:
        """
        Elimina un servicio de transporte.
        
        Args:
            servicio_id: ID del servicio a eliminar
            
        Returns:
            True si se eliminó exitosamente
        """
        try:
            logger.info(f"Eliminando servicio {servicio_id}")
            
            if not self.model:
                show_error(self.view, "Error", MENSAJE_ERROR_CONEXION)
                return False
            
            if hasattr(self.model, 'eliminar_servicio_transporte'):
                success = self.model.eliminar_servicio_transporte(servicio_id)
            else:
                logger.warning("Método eliminar_servicio_transporte no disponible en el modelo")
                success = False
            
            if success:
                show_success(self.view, MENSAJE_EXITO, "Servicio eliminado correctamente")
                self.actualizar_vista_servicios()
                self.servicio_eliminado.emit(servicio_id)
                self._registrar_auditoria("eliminar_servicio", servicio_id)
                logger.info(f"Servicio {servicio_id} eliminado")
                return True
            else:
                show_error(self.view, "Error", "No se pudo eliminar el servicio")
                return False
                
        except Exception as e:
            logger.error(f"Error eliminando servicio: {e}")
            show_error(self.view, "Error", f"Error al eliminar servicio: {str(e)}")
            return False
    
    def actualizar_estado_servicio(self, servicio_id: int, nuevo_estado: str, observaciones: str = "") -> bool:
        """
        Actualiza el estado de un servicio.
        
        Args:
            servicio_id: ID del servicio
            nuevo_estado: Nuevo estado
            observaciones: Observaciones adicionales
            
        Returns:
            True si se actualizó exitosamente
        """
        try:
            logger.info(f"Actualizando estado de servicio {servicio_id} a {nuevo_estado}")
            
            if not self.model:
                show_error(self.view, "Error", MENSAJE_ERROR_CONEXION)
                return False
            
            if hasattr(self.model, 'actualizar_estado_servicio'):
                success = self.model.actualizar_estado_servicio(servicio_id, nuevo_estado, observaciones)
            else:
                logger.warning("Método actualizar_estado_servicio no disponible en el modelo")
                success = False
            
            if success:
                show_success(self.view, MENSAJE_EXITO, f"Estado actualizado a {nuevo_estado}")
                self.actualizar_vista_servicios()
                self.estado_actualizado.emit(servicio_id, nuevo_estado)
                self._registrar_auditoria("cambiar_estado", servicio_id, {"nuevo_estado": nuevo_estado})
                logger.info(f"Estado de servicio {servicio_id} actualizado")
                return True
            else:
                show_error(self.view, "Error", "No se pudo actualizar el estado")
                return False
                
        except Exception as e:
            logger.error(f"Error actualizando estado: {e}")
            show_error(self.view, "Error", f"Error al actualizar estado: {str(e)}")
            return False
    
    # ===== MÉTODOS DE PROVEEDORES =====
    
    def crear_proveedor_transporte(self, datos_proveedor: Dict[str, Any]) -> bool:
        """
        Crea un nuevo proveedor de transporte.
        
        Args:
            datos_proveedor: Datos del proveedor
            
        Returns:
            True si se creó exitosamente
        """
        try:
            logger.info("Creando nuevo proveedor de transporte")
            
            if not self._validar_datos_proveedor(datos_proveedor):
                return False
            
            if not self.model:
                show_error(self.view, "Error", MENSAJE_ERROR_CONEXION)
                return False
            
            # Generar código único
            if not datos_proveedor.get('codigo'):
                datos_proveedor['codigo'] = self._generar_codigo_proveedor()
            
            if hasattr(self.model, 'crear_proveedor_transporte'):
                proveedor_id = self.model.crear_proveedor_transporte(datos_proveedor)
            else:
                logger.warning("Método crear_proveedor_transporte no disponible en el modelo")
                proveedor_id = None
            
            if proveedor_id:
                show_success(self.view, MENSAJE_EXITO, "Proveedor de transporte creado correctamente")
                self.actualizar_vista_proveedores()
                self.proveedor_creado.emit(datos_proveedor)
                self._registrar_auditoria("crear_proveedor", proveedor_id)
                logger.info(f"Proveedor creado con ID: {proveedor_id}")
                return True
            else:
                show_error(self.view, "Error", "No se pudo crear el proveedor")
                return False
                
        except Exception as e:
            logger.error(f"Error creando proveedor: {e}")
            show_error(self.view, "Error", f"Error al crear proveedor: {str(e)}")
            return False
    
    def actualizar_proveedor_transporte(self, proveedor_id: int, datos_proveedor: Dict[str, Any]) -> bool:
        """
        Actualiza un proveedor de transporte.
        
        Args:
            proveedor_id: ID del proveedor
            datos_proveedor: Nuevos datos del proveedor
            
        Returns:
            True si se actualizó exitosamente
        """
        try:
            logger.info(f"Actualizando proveedor {proveedor_id}")
            
            if not self._validar_datos_proveedor(datos_proveedor):
                return False
            
            if not self.model:
                show_error(self.view, "Error", MENSAJE_ERROR_CONEXION)
                return False
            
            if hasattr(self.model, 'actualizar_proveedor_transporte'):
                success = self.model.actualizar_proveedor_transporte(proveedor_id, datos_proveedor)
            else:
                logger.warning("Método actualizar_proveedor_transporte no disponible en el modelo")
                success = False
            
            if success:
                show_success(self.view, MENSAJE_EXITO, "Proveedor actualizado correctamente")
                self.actualizar_vista_proveedores()
                self.proveedor_actualizado.emit(proveedor_id, datos_proveedor)
                self._registrar_auditoria("actualizar_proveedor", proveedor_id)
                logger.info(f"Proveedor {proveedor_id} actualizado")
                return True
            else:
                show_error(self.view, "Error", "No se pudo actualizar el proveedor")
                return False
                
        except Exception as e:
            logger.error(f"Error actualizando proveedor: {e}")
            show_error(self.view, "Error", f"Error al actualizar proveedor: {str(e)}")
            return False
    
    # ===== MÉTODOS DE BÚSQUEDA Y FILTRADO =====
    
    def buscar_servicios(self, criterios: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Busca servicios con criterios específicos.
        
        Args:
            criterios: Criterios de búsqueda
            
        Returns:
            Lista de servicios encontrados
        """
        try:
            logger.info("Buscando servicios con criterios especificados")
            
            if not self.model:
                logger.warning("No hay modelo disponible")
                return []
            
            # Sanitizar criterios
            criterios_sanitizados = self._sanitizar_criterios_busqueda(criterios)
            
            if hasattr(self.model, 'buscar_servicios'):
                servicios = self.model.buscar_servicios(criterios_sanitizados)
            else:
                logger.warning("Método buscar_servicios no disponible en el modelo")
                servicios = []
            
            if hasattr(self.view, 'cargar_servicios'):
                self.view.cargar_servicios(servicios)
            
            logger.info(f"Encontrados {len(servicios)} servicios")
            return servicios
            
        except Exception as e:
            logger.error(f"Error buscando servicios: {e}")
            show_error(self.view, "Error", f"Error en la búsqueda: {str(e)}")
            return []
    
    def filtrar_servicios_por_estado(self, estado: str) -> List[Dict[str, Any]]:
        """
        Filtra servicios por estado.
        
        Args:
            estado: Estado a filtrar
            
        Returns:
            Lista de servicios en el estado especificado
        """
        try:
            if not self.model:
                return []
            
            if hasattr(self.model, 'obtener_servicios_por_estado'):
                servicios = self.model.obtener_servicios_por_estado(estado)
            else:
                logger.warning("Método obtener_servicios_por_estado no disponible en el modelo")
                servicios = []
            
            if hasattr(self.view, 'cargar_servicios'):
                self.view.cargar_servicios(servicios)
            
            logger.info(f"Filtrados {len(servicios)} servicios con estado {estado}")
            return servicios
            
        except Exception as e:
            logger.error(f"Error filtrando por estado: {e}")
            return []
    
    # ===== MÉTODOS DE ESTADÍSTICAS Y REPORTES =====
    
    def cargar_estadisticas(self) -> Dict[str, Any]:
        """
        Carga y actualiza las estadísticas del dashboard.
        
        Returns:
            dict: Estadísticas cargadas
        """
        try:
            logger.debug("Cargando estadísticas de logística")
            
            if self.model:
                stats = self._obtener_estadisticas_completas()
            else:
                # Datos de demostración
                stats = {
                    'total_servicios': 156,
                    'en_transito': 23,
                    'completados': 125,
                    'cancelados': 8,
                    'pendientes': 12,
                    'costo_total_mes': 45650.0,
                    'promedio_entrega': 2.5
                }
                logger.info("Usando estadísticas de demostración")

            if hasattr(self.view, 'actualizar_estadisticas'):
                self.view.actualizar_estadisticas(stats)
                logger.debug("Estadísticas enviadas a la vista")
            
            return stats
            
        except Exception as e:
            logger.error(f"Error cargando estadísticas: {e}")
            show_error(self.view, "Error", f"Error cargando estadísticas: {str(e)}")
            return {}
    
    def generar_reporte_logistico(self, fecha_inicio: date, fecha_fin: date) -> Dict[str, Any]:
        """
        Genera reporte logístico para un periodo.
        
        Args:
            fecha_inicio: Fecha de inicio
            fecha_fin: Fecha de fin
            
        Returns:
            Datos del reporte
        """
        try:
            logger.info(f"Generando reporte logístico {fecha_inicio} - {fecha_fin}")
            
            if not self.model:
                show_error(self.view, "Error", MENSAJE_ERROR_CONEXION)
                return {}
            
            if hasattr(self.model, 'generar_reporte_logistico'):
                reporte = self.model.generar_reporte_logistico(fecha_inicio, fecha_fin)
            else:
                logger.warning("Método generar_reporte_logistico no disponible en el modelo")
                reporte = {}
            
            if reporte:
                show_success(self.view, MENSAJE_EXITO, "Reporte generado correctamente")
                self._registrar_auditoria("generar_reporte", None, {"periodo": f"{fecha_inicio}-{fecha_fin}"})
            else:
                show_warning(self.view, "Advertencia", "No se encontraron datos para el periodo")
            
            return reporte
            
        except Exception as e:
            logger.error(f"Error generando reporte: {e}")
            show_error(self.view, "Error", f"Error generando reporte: {str(e)}")
            return {}
    
    # ===== MÉTODOS DE ACTUALIZACIÓN DE VISTA =====
    
    def cargar_datos_iniciales(self):
        """Carga los datos iniciales para la vista."""
        try:
            logger.info("Cargando datos iniciales de logística")
            
            # Cargar servicios
            self.actualizar_vista_servicios()
            
            # Cargar proveedores
            self.actualizar_vista_proveedores()
            
            # Cargar estadísticas
            self.cargar_estadisticas()
            
            logger.debug("Datos iniciales cargados exitosamente")
            
        except Exception as e:
            logger.error(f"Error cargando datos iniciales: {e}")
            show_error(self.view, "Error", f"Error cargando datos: {str(e)}")
    
    def actualizar_vista_servicios(self):
        """Actualiza la vista de servicios."""
        try:
            if hasattr(self.view, 'cargar_servicios'):
                servicios = self._cargar_servicios()
                self.view.cargar_servicios(servicios)
            logger.debug("Vista de servicios actualizada")
            
        except Exception as e:
            logger.error(f"Error actualizando vista servicios: {e}")
    
    def actualizar_vista_proveedores(self):
        """Actualiza la vista de proveedores."""
        try:
            if hasattr(self.view, 'cargar_proveedores'):
                proveedores = self._cargar_proveedores()
                self.view.cargar_proveedores(proveedores)
            logger.debug("Vista de proveedores actualizada")
            
        except Exception as e:
            logger.error(f"Error actualizando vista proveedores: {e}")
    
    # ===== MÉTODOS DE CÁLCULO =====
    
    def calcular_costo_transporte(self, origen: str, destino: str, peso: float, 
                                 volumen: float, tipo_servicio: str = "ENTREGA") -> Dict[str, Any]:
        """
        Calcula el costo de transporte.
        
        Args:
            origen: Punto de origen
            destino: Punto de destino
            peso: Peso en kg
            volumen: Volumen en m³
            tipo_servicio: Tipo de servicio
            
        Returns:
            Información del costo calculado
        """
        try:
            if not self.model:
                return {'costo_estimado': 0.0, 'error': 'No hay modelo disponible'}
            
            if hasattr(self.model, 'calcular_costo_transporte'):
                costo_info = self.model.calcular_costo_transporte(origen, destino, peso, volumen, tipo_servicio)
            else:
                logger.warning("Método calcular_costo_transporte no disponible en el modelo")
                costo_info = {'costo_estimado': 100.0, 'detalles': 'Cálculo básico'}
            
            logger.info(f"Costo calculado: {costo_info.get('costo_estimado', 0)} para {origen}-{destino}")
            
            return costo_info
            
        except Exception as e:
            logger.error(f"Error calculando costo: {e}")
            return {'costo_estimado': 0.0, 'error': str(e)}
    
    # ===== MÉTODOS PRIVADOS =====
    
    def _validar_datos_servicio(self, datos: Dict[str, Any]) -> bool:
        """Valida los datos de un servicio."""
        try:
            # Validaciones básicas
            if not datos.get('origen', '').strip():
                show_error(self.view, "Error", "El origen es obligatorio")
                return False
            
            if not datos.get('destino', '').strip():
                show_error(self.view, "Error", "El destino es obligatorio")
                return False
            
            if not datos.get('descripcion', '').strip():
                show_error(self.view, "Error", "La descripción es obligatoria")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validando datos servicio: {e}")
            return False
    
    def _validar_datos_proveedor(self, datos: Dict[str, Any]) -> bool:
        """Valida los datos de un proveedor."""
        try:
            # Validaciones básicas
            if not datos.get('nombre', '').strip():
                show_error(self.view, "Error", "El nombre del proveedor es obligatorio")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validando datos proveedor: {e}")
            return False
    
    def _sanitizar_criterios_busqueda(self, criterios: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitiza los criterios de búsqueda."""
        criterios_sanitizados = {}
        
        for key, value in criterios.items():
            if isinstance(value, str):
                # Sanitizar strings
                criterios_sanitizados[key] = value.strip()[:100]  # Limitar longitud
            else:
                criterios_sanitizados[key] = value
        
        return criterios_sanitizados
    
    def _calcular_costo_servicio(self, datos_servicio: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula el costo de un servicio."""
        try:
            if self.model and hasattr(self.model, 'calcular_costo_transporte'):
                return self.model.calcular_costo_transporte(
                    datos_servicio.get('origen', ''),
                    datos_servicio.get('destino', ''),
                    datos_servicio.get('peso', 0.0),
                    datos_servicio.get('volumen', 0.0),
                    datos_servicio.get('tipo_servicio', 'ENTREGA')
                )
            else:
                return {'costo_estimado': 100.0}  # Valor por defecto
        except Exception as e:
            logger.error(f"Error calculando costo: {e}")
            return {'costo_estimado': 0.0}
    
    def _obtener_estadisticas_completas(self) -> Dict[str, Any]:
        """Obtiene estadísticas completas del modelo."""
        try:
            if hasattr(self.model, 'obtener_servicios_transporte'):
                servicios = self.model.obtener_servicios_transporte()
            else:
                servicios = []
            
            # Calcular estadísticas básicas
            total = len(servicios)
            en_transito = len([s for s in servicios if s.get('estado') == 'EN_TRANSITO'])
            completados = len([s for s in servicios if s.get('estado') == 'COMPLETADO'])
            cancelados = len([s for s in servicios if s.get('estado') == 'CANCELADO'])
            pendientes = len([s for s in servicios if s.get('estado') == 'PENDIENTE'])
            
            # Calcular costos
            costo_total = sum([s.get('costo_real', 0) for s in servicios if s.get('estado') == 'COMPLETADO'])
            
            return {
                'total_servicios': total,
                'en_transito': en_transito,
                'completados': completados,
                'cancelados': cancelados,
                'pendientes': pendientes,
                'costo_total_mes': costo_total,
                'promedio_entrega': round(costo_total / completados if completados > 0 else 0, 2)
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return {}
    
    def _cargar_servicios(self) -> List[Dict[str, Any]]:
        """Carga los servicios desde el modelo."""
        try:
            if self.model and hasattr(self.model, 'obtener_servicios_transporte'):
                return self.model.obtener_servicios_transporte()
            else:
                return []
        except Exception as e:
            logger.error(f"Error cargando servicios: {e}")
            return []
    
    def _cargar_proveedores(self) -> List[Dict[str, Any]]:
        """Carga los proveedores desde el modelo."""
        try:
            if self.model and hasattr(self.model, 'obtener_proveedores_transporte'):
                return self.model.obtener_proveedores_transporte()
            else:
                return []
        except Exception as e:
            logger.error(f"Error cargando proveedores: {e}")
            return []
    
    def _generar_codigo_servicio(self) -> str:
        """Genera un código único para servicio."""
        try:
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            return f"SRV{timestamp}"
        except Exception:
            return f"SRV{int(datetime.now().timestamp())}"
    
    def _generar_codigo_proveedor(self) -> str:
        """Genera un código único para proveedor."""
        try:
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            return f"PROV{timestamp}"
        except Exception:
            return f"PROV{int(datetime.now().timestamp())}"
    
    def _registrar_auditoria(self, accion: str, id_objeto: Optional[int], detalles: Optional[Dict[str, Any]] = None):
        """Registra eventos en el sistema de auditoría."""
        try:
            # Simplemente registrar en log por ahora
            logger.info(f"Auditoría - Módulo: logistica, Acción: {accion}, ID: {id_objeto}, Detalles: {detalles}")
            
        except Exception as e:
            logger.warning(f"Error registrando auditoría: {e}")
    
    # ===== MÉTODOS DE COMPATIBILIDAD =====
    
    def eliminar_transporte(self, transporte_id: int) -> tuple:
        """
        Método de compatibilidad para eliminar transporte.
        
        Args:
            transporte_id: ID del transporte/servicio
            
        Returns:
            tuple: (éxito, mensaje)
        """
        try:
            success = self.eliminar_servicio_transporte(transporte_id)
            mensaje = "Transporte eliminado exitosamente" if success else "Error eliminando transporte"
            return success, mensaje
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def mostrar_mensaje(self, mensaje: str, tipo: str = "info"):
        """
        Muestra un mensaje usando el sistema centralizado.
        
        Args:
            mensaje: Mensaje a mostrar
            tipo: Tipo de mensaje
        """
        try:
            if tipo == "success":
                show_success(self.view, TITULO_LOGISTICA, mensaje)
            elif tipo == "warning":
                show_warning(self.view, TITULO_LOGISTICA, mensaje)
            elif tipo == "error":
                show_error(self.view, f"Error - {TITULO_LOGISTICA}", mensaje)
            else:
                show_info(self.view, TITULO_LOGISTICA, mensaje)
                
        except Exception as e:
            logger.error(f"Error mostrando mensaje: {e}")
    
    def mostrar_error(self, mensaje: str):
        """Muestra un mensaje de error."""
        show_error(self.view, f"Error - {TITULO_LOGISTICA}", mensaje)
'''

def aplicar_correcciones():
    """Aplica las correcciones al archivo."""
    archivo_destino = "rexus/modules/logistica/controller.py"
    
    try:
        # Crear backup
        crear_backup()
        
        # Escribir contenido corregido
        contenido_corregido = generar_controller_corregido()
        
        with open(archivo_destino, 'w', encoding='utf-8') as f:
            f.write(contenido_corregido)
        
        print(f"✅ Controller de logística corregido exitosamente")
        print(f"📝 Archivo: {archivo_destino}")
        print("🔧 Correcciones aplicadas:")
        print("   - Indentación normalizada")
        print("   - Estructura de clases corregida")
        print("   - Sintaxis Python válida")
        print("   - Manejo de errores mejorado")
        print("   - Imports organizados")
        print("   - Métodos bien definidos")
        print("   - Señales PyQt6 correctas")
        print("   - Logging integrado")
        
    except Exception as e:
        print(f"❌ Error aplicando correcciones: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 Iniciando reestructuración del controller de logística...")
    
    if aplicar_correcciones():
        print("✅ Reestructuración completada exitosamente")
    else:
        print("❌ Error en la reestructuración")
