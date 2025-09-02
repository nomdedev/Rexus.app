"""
Controller de Notificaciones - Rexus.app v2.0.0

Controlador para gestionar notificaciones del sistema.
Coordina entre el modelo y la vista siguiendo el patrón MVC.
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta

# Importar logging centralizado
from rexus.utils.app_logger import get_logger

from rexus.core.auth_manager import admin_required, auth_required
from rexus.modules.notificaciones.model import NotificacionesModel, TipoNotificacion

# Configurar logger
logger = get_logger("notificaciones.controller")


class NotificacionesController:
    """Controlador para el módulo de notificaciones."""

    def __init__(self, db_connection=None, view=None, usuario_actual=None):
        """
        Inicializa el controlador de notificaciones.

        Args:
            db_connection: Conexión a la base de datos
            view: Vista asociada
            usuario_actual: Información del usuario actual
        """
        self.model = NotificacionesModel(db_connection)
        self.view = view
        self.usuario_actual = usuario_actual or {}

        logger.info("OK [NOTIFICACIONES CONTROLLER] Inicializado correctamente")

    @auth_required
    def obtener_notificaciones_usuario(self, solo_no_leidas: bool = False,
                                     limite: int = 50) -> List[Dict]:
        """
        Obtiene las notificaciones del usuario actual.

        Args:
            solo_no_leidas: Si obtener solo las no leídas
            limite: Máximo número de notificaciones

        Returns:
            List[Dict]: Lista de notificaciones
        """
        try:
            usuario_id = self.usuario_actual.get('id')
            if not usuario_id:
                logger.info("[ERROR] No hay usuario actual")
                return []

            notificaciones = self.model.obtener_notificaciones_usuario(
                usuario_id, solo_no_leidas, limite
            )

            if self.view:
                self.view.mostrar_notificaciones(notificaciones)

            return notificaciones

        except (AttributeError, RuntimeError, ConnectionError, ValueError) as e:
            logger.error(f"[ERROR NOTIFICACIONES CONTROLLER] Error obteniendo notificaciones: {str(e)}")
            if self.view:
                self.view.mostrar_error(f"Error cargando notificaciones: {str(e)}")
            return []

    @auth_required
    def marcar_como_leida(self, notificacion_id: int) -> bool:
        """
        Marca una notificación como leída.

        Args:
            notificacion_id: ID de la notificación

        Returns:
            bool: True si se marcó exitosamente
        """
        try:
            usuario_id = self.usuario_actual.get('id')
            if not usuario_id:
                logger.info("[ERROR] No hay usuario actual")
                return False

            resultado = self.model.marcar_como_leida(notificacion_id, usuario_id)

            if resultado and self.view:
                self.view.actualizar_estado_notificacion(notificacion_id, 'leida')
                # Actualizar contador de no leídas
                self.actualizar_contador_no_leidas()

            return resultado

        except (AttributeError, RuntimeError, ConnectionError, ValueError) as e:
            logger.error(f"[ERROR NOTIFICACIONES CONTROLLER] Error marcando como leída: {str(e)}")
            if self.view:
                self.view.mostrar_error(f"Error marcando notificación: {str(e)}")
            return False

    @auth_required
    def contar_no_leidas(self) -> int:
        """
        Obtiene el conteo de notificaciones no leídas.

        Returns:
            int: Número de notificaciones no leídas
        """
        try:
            usuario_id = self.usuario_actual.get('id')
            if not usuario_id:
                return 0

            count = self.model.contar_no_leidas(usuario_id)
            return count

        except (AttributeError, RuntimeError, ConnectionError, ValueError) as e:
            logger.error(f"[ERROR NOTIFICACIONES CONTROLLER] Error contando no leídas: {str(e)}")
            return 0

    @auth_required
    def actualizar_contador_no_leidas(self):
        """Actualiza el contador en la vista."""
        try:
            count = self.contar_no_leidas()
            if self.view:
                self.view.actualizar_contador_no_leidas(count)

        except (AttributeError, RuntimeError, ConnectionError, ValueError) as e:
            logger.error(f"[ERROR NOTIFICACIONES CONTROLLER] Error actualizando contador: {str(e)}")

    @auth_required
    def crear_notificacion(self, titulo: str, mensaje: str,
                          tipo: str = "info", prioridad: int = 2,
                          usuario_destino: Optional[int] = None,
                          modulo_origen: str = None) -> bool:
        """
        Crea una nueva notificación.

        Args:
            titulo: Título de la notificación
            mensaje: Contenido del mensaje
            tipo: Tipo de notificación
            prioridad: Nivel de prioridad (1-4)
            usuario_destino: ID del usuario destinatario (None = todos)
            modulo_origen: Módulo que genera la notificación

        Returns:
            bool: True si se creó exitosamente
        """
        try:
            # Validar datos
            if not titulo or not mensaje:
                if self.view:
                    self.view.mostrar_error("Título y mensaje son requeridos")
                return False

            if tipo not in [t.value for t in TipoNotificacion]:
                tipo = "info"

            if not (1 <= prioridad <= 4):
                prioridad = 2

            resultado = self.model.crear_notificacion(
                titulo=titulo,
                mensaje=mensaje,
                tipo=tipo,
                prioridad=prioridad,
                usuario_destino=usuario_destino,
                modulo_origen=modulo_origen
            )

            if resultado:
                if self.view:
                    self.view.mostrar_mensaje("Notificación creada exitosamente", "success")
                    # Refrescar la lista si está mostrando notificaciones
                    self.obtener_notificaciones_usuario()

            return resultado

        except (AttributeError, RuntimeError, ConnectionError, ValueError) as e:
            logger.error(f"[ERROR NOTIFICACIONES CONTROLLER] Error creando notificación: {str(e)}")
            if self.view:
                self.view.mostrar_error(f"Error creando notificación: {str(e)}")
            return False

    @admin_required
    def eliminar_notificacion(self, notificacion_id: int) -> bool:
        """
        Elimina una notificación (solo administradores).

        Args:
            notificacion_id: ID de la notificación

        Returns:
            bool: True si se eliminó exitosamente
        """
        try:
            resultado = self.model.eliminar_notificacion(notificacion_id)

            if resultado:
                if self.view:
                    self.view.mostrar_mensaje("Notificación eliminada exitosamente", "success")
                    self.view.remover_notificacion_de_lista(notificacion_id)

            return resultado

        except (AttributeError, RuntimeError, ConnectionError, ValueError) as e:
            logger.error(f"[ERROR NOTIFICACIONES CONTROLLER] Error eliminando notificación: {str(e)}")
            if self.view:
                self.view.mostrar_error(f"Error eliminando notificación: {str(e)}")
            return False

    def manejar_evento_sistema(self, evento: str, modulo: str,
                              detalles: Optional[Dict] = None) -> bool:
        """
        Maneja eventos del sistema creando notificaciones automáticas.

        Args:
            evento: Tipo de evento
            modulo: Módulo que genera el evento
            detalles: Información adicional

        Returns:
            bool: True si se procesó exitosamente
        """
        try:
            resultado = self.model.crear_notificacion_sistema(evento, modulo, detalles)

            if resultado and self.view:
                # Actualizar vista si está visible
                self.actualizar_contador_no_leidas()

            return resultado

        except (AttributeError, RuntimeError, ConnectionError, ValueError) as e:
            logger.error(f"[ERROR NOTIFICACIONES CONTROLLER] Error manejando evento: {str(e)}")
            return False

    def inicializar_notificaciones_sistema(self):
        """Inicializa notificaciones del sistema al startup."""
        try:
            # Crear notificación de sistema iniciado
            self.manejar_evento_sistema(
                'sistema_iniciado',
                'sistema',
                {'timestamp': datetime.now().isoformat()}
            )

        except (AttributeError, RuntimeError, ConnectionError, ValueError) as e:
            logger.error(f"[ERROR NOTIFICACIONES CONTROLLER] Error inicializando: {str(e)}")

    def procesar_notificaciones_programadas(self):
        """Procesa notificaciones programadas (para ejecutar periódicamente)."""
        try:
            # Aquí se pueden agregar lógicas para notificaciones programadas
            # Por ejemplo: recordatorios de mantenimiento, alertas de stock bajo, etc.
            pass

        except (AttributeError, RuntimeError, ConnectionError, ValueError) as e:
            logger.error(f"[ERROR NOTIFICACIONES CONTROLLER] Error procesando programadas: {str(e)}")

    def obtener_estadisticas(self) -> Dict:
        """
        Obtiene estadísticas de notificaciones para el usuario actual.

        Returns:
            Dict: Estadísticas de notificaciones
        """
        try:
            usuario_id = self.usuario_actual.get('id')
            if not usuario_id:
                return {}

            # Obtener todas las notificaciones del usuario
            todas = self.model.obtener_notificaciones_usuario(usuario_id, False, 1000)

            stats = {
                'total': len(todas),
                'no_leidas': sum(1 for n in todas if not n['leida']),
                'por_tipo': {},
                'por_prioridad': {},
                'ultimas_24h': 0
            }

            # Contar por tipo y prioridad
            for notif in todas:
                tipo = notif['tipo']
                prioridad = notif['prioridad']

                stats['por_tipo'][tipo] = stats['por_tipo'].get(tipo, 0) + 1
                stats['por_prioridad'][prioridad] = stats['por_prioridad'].get(prioridad, 0) + 1

                # Contar las de últimas 24 horas
                if notif['fecha_creacion']:
                    hace_24h = datetime.now() - timedelta(hours=24)
                    if isinstance(notif['fecha_creacion'], datetime):
                        if notif['fecha_creacion'] > hace_24h:
                            stats['ultimas_24h'] += 1

            return stats

        except (AttributeError, RuntimeError, ConnectionError, ValueError) as e:
            logger.error(f"[ERROR NOTIFICACIONES CONTROLLER] Error obteniendo estadísticas: {str(e)}")
            return {}
