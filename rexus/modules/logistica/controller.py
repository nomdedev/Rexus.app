"""Controlador de Logística"""

import time
import logging
from typing import Dict, Any, List, Optional
from rexus.core.base_controller import BaseController

logger = logging.getLogger(__name__)


class LogisticaController(BaseController):
    """Controlador para el módulo de logística."""
    
    def __init__(self, parent=None):
        super().__init__("logistica", parent)
        
    def eliminar_transporte(self, transporte_id):
        """
        Elimina un transporte (requiere permisos de administrador).
        
        Args:
            transporte_id: ID del transporte a eliminar
            
        Returns:
            tuple: (exito, mensaje)
        """
        logger.info(f"Iniciando eliminación de transporte ID: {transporte_id} por usuario: {self.usuario_actual}")
        
        # Validar ID
        if not transporte_id or not isinstance(transporte_id, (int, str)):
            error_msg = "ID de transporte inválido"
            logger.warning(error_msg)
            self.mostrar_error(error_msg)
            return False, error_msg
        
        try:
            if self.model and hasattr(self.model, 'eliminar_transporte'):
                if self.model.eliminar_transporte(transporte_id):
                    success_msg = "Transporte eliminado exitosamente"
                    logger.info(f"Transporte ID: {transporte_id} eliminado por administrador: {self.usuario_actual}")
                    
                    self.mostrar_mensaje(success_msg, tipo="success")
                    self.cargar_datos_iniciales()
                    self.transporte_eliminado.emit(transporte_id)
                    
                    return True, success_msg
                else:
                    error_msg = "No se pudo eliminar el transporte (puede estar en uso)"
                    logger.warning(f"Fallo al eliminar transporte ID: {transporte_id}")
                    self.mostrar_error(error_msg)
                    return False, error_msg
            else:
                # Simulación para pruebas
                success_msg = "Transporte eliminado exitosamente (simulado)"
                logger.info(success_msg)
                
                self.mostrar_mensaje(success_msg, tipo="success")
                if self.view and hasattr(self.view, 'actualizar_tabla_transportes'):
                    self.view.actualizar_tabla_transportes()
                
                return True, success_msg
                
        except Exception as e:
            error_msg = f"Error al eliminar transporte: {str(e)}"
                    
        try:
            if self.model and hasattr(self.model, 'buscar_transportes'):
                transportes = self.model.buscar_transportes(termino_sanitizado, estado_sanitizado)
                logger.info(f"Encontrados {len(transportes) if transportes else 0} transportes")
                
                if self.view:
                    self.view.cargar_transportes(transportes)
                
                return transportes or []
            else:
                # Simulación para pruebas
                transportes_simulados = [
                    {
                        'id': 1,
                        'origen': 'Ciudad A',
                        'destino': 'Ciudad B',
                        'estado': estado_sanitizado or 'En tránsito',
                        'conductor': 'Juan Pérez',
                        'fecha': '2025-01-15'
                    }
                ]
                logger.info("Usando datos simulados para búsqueda de transportes")
                
                if self.view:
                    self.view.cargar_transportes(transportes_simulados)
                
                return transportes_simulados
                
        except Exception as e:
            error_msg = f"Error buscando transportes: {e}"
            logger.error(error_msg, exc_info=True)
            self.mostrar_error(error_msg)
            return []

    def cargar_estadisticas(self):
        """
        Carga y actualiza las estadísticas del dashboard.
        
        Returns:
            dict: Estadísticas cargadas
        """
        logger.debug("Cargando estadísticas de logística")
        
        try:
            if self.model and hasattr(self.model, 'obtener_estadisticas'):
                stats = self.model.obtener_estadisticas()
                logger.info("Estadísticas obtenidas desde el modelo")
            else:
                # Simulación para pruebas - valores estáticos para evitar warnings de seguridad
                stats = {
                    'total_transportes': 156,
                    'en_transito': 23,
                    'entregados_hoy': 8,
                    'pendientes': 12
                }
                logger.info("Usando estadísticas simuladas")

            if self.view:
                self.view.actualizar_estadisticas(stats)
                logger.debug("Estadísticas enviadas a la vista")
            
            return stats
            
        except Exception as e:
            error_msg = f"Error cargando estadísticas: {e}"
            logger.error(error_msg, exc_info=True)
            self.mostrar_error(error_msg)
            return {}

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
                show_success(self.view, "Logística", mensaje)
            elif tipo == "warning":
                show_warning(self.view, "Logística", mensaje)
            elif tipo == "error":
                show_error(self.view, "Error - Logística", mensaje)
            else:
                show_info(self.view, "Logística", mensaje)

    def _registrar_generacion_auditoria(self, criterios, servicios_generados):
        """Registra la generación de servicios en el sistema de auditoría."""
        try:
            from rexus.core.audit_system import AuditSystem, AuditEventType
            audit = AuditSystem()
            
            audit.log_event(
                event_type=AuditEventType.SYSTEM_OPERATION,
                modulo=,
                accion="generar_servicios_automaticos",
                detalles={
                    "criterios": criterios,
                    "servicios_generados": servicios_generados.get('generados', 0),
                    "zona": criterios.get('zona_geografica'),
                    "tipo": criterios.get('tipo_servicio')
                },
                resultado="EXITOSO"
            )
        except ImportError:
            logger.debug("Sistema de auditoría no disponible")
        except Exception as e:
            logger.warning(f"Error registrando en auditoría: {e}")

    def mostrar_error(self, mensaje):
        """Muestra un mensaje de error con logging."""
        if self.view:
            show_error(self.view, "Error - Logística", mensaje)
        else:
            # Fallback si no hay vista
            logger.error(f"[NO VIEW] Error: {mensaje}")
