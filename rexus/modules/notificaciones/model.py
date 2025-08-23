"""
Modelo de Notificaciones - Rexus.app v2.0.0

Sistema completo de notificaciones y alertas del sistema.
Incluye utilidades de seguridad para prevenir SQL injection y XSS.
"""


import logging
logger = logging.getLogger(__name__)

import datetime
import json
import sys
                def eliminar_notificacion(self, notificacion_id: int) -> bool:
        """
        Elimina una notificación del sistema.

        Args:
            notificacion_id: ID de la notificación

        Returns:
            bool: True si se eliminó exitosamente
        """
        if not self.db_connection:
            logger.info("[WARNING] Sin BD - simulando eliminación")
            return True

        try:
            cursor = self.db_connection.cursor()

            # Marcar como inactiva en lugar de eliminar (soft delete)
            cursor.execute("""
                UPDATE notificaciones
                SET activa = 0
                WHERE id = ?
            """, (notificacion_id,))

            self.db_connection.commit()

            # Invalidar cache después de eliminar
            self._invalidar_cache_notificaciones()

            return True

        except Exception as e:
            logger.info(f"[ERROR NOTIFICACIONES] Error eliminando notificación: {str(e)}")
            if self.db_connection:
                self.db_connection.rollback()
            return False
    def crear_notificacion_sistema(self, evento: str, modulo: str,
                                 detalles: Optional[Dict] = None) -> bool:
        """
        Crea notificaciones automáticas del sistema.

        Args:
            evento: Tipo de evento (error, alerta, info)
            modulo: Módulo que genera el evento
            detalles: Información adicional

        Returns:
            bool: True si se creó exitosamente
        """
        # Mapear eventos a notificaciones
        eventos_map = {
            'error_bd': {
                'titulo': 'Error de Base de Datos',
                'mensaje': f'Se detectó un error en el módulo {modulo}',
                'tipo': 'error',
                'prioridad': 4
            },
            'backup_completado': {
                'titulo': 'Backup Completado',
                'mensaje': 'El respaldo del sistema se completó exitosamente',
                'tipo': 'success',
                'prioridad': 2
            },
            'login_fallido': {
                'titulo': 'Intento de Login Fallido',
                'mensaje': f'Múltiples intentos fallidos desde {modulo}',
                'tipo': 'warning',
                'prioridad': 3
            },
            'sistema_iniciado': {
                'titulo': 'Sistema Iniciado',
                'mensaje': 'Rexus.app se ha iniciado correctamente',
                'tipo': 'info',
                'prioridad': 1
            }
        }

        if evento not in eventos_map:
            logger.info(f"[WARNING] Evento desconocido: {evento}")
            return False

        config = eventos_map[evento]

        # Agregar detalles al mensaje si se proporcionan
        if detalles:
            config['mensaje'] += f" - Detalles: {json.dumps(detalles)}"

        return self.crear_notificacion(
            titulo=config['titulo'],
            mensaje=config['mensaje'],
            tipo=config['tipo'],
            prioridad=config['prioridad'],
            modulo_origen=modulo,
            metadata=detalles
        )

    def _invalidar_cache_notificaciones(self) -> None:
        """
        Invalida el cache de notificaciones después de cambios.
        """
        try:
            # Invalidar cache de obtención de notificaciones
            invalidate_cache('obtener_notificaciones_usuario')
            # Invalidar cache de conteo de no leídas
            invalidate_cache('contar_no_leidas')
            logger.info("[NOTIFICACIONES] Cache invalidado después de cambios")
        except Exception as e:
            logger.info(f"[WARNING NOTIFICACIONES] Error invalidando cache: {e}")

    @classmethod
    def limpiar_notificaciones_expiradas(cls, db_connection) -> int:
        """
        Limpia notificaciones expiradas del sistema.

        Args:
            db_connection: Conexión a la base de datos

        Returns:
            int: Número de notificaciones limpiadas
        """
        if not db_connection:
            return 0

        try:
            cursor = db_connection.cursor()

            # Marcar como inactivas las notificaciones expiradas
            cursor.execute("""
                UPDATE notificaciones
                SET activa = 0
                WHERE fecha_expiracion < GETDATE() AND activa = 1
            """)

            affected_rows = cursor.rowcount
            db_connection.commit()

            if affected_rows > 0:
                logger.info(f"[NOTIFICACIONES] {affected_rows} notificaciones expiradas limpiadas")

            return affected_rows

        except Exception as e:
            logger.info(f"[ERROR NOTIFICACIONES] Error limpiando expiradas: {e}")
            return 0
