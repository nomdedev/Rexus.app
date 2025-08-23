"""
Controller de Notificaciones - Rexus.app v2.0.0

Controlador para gestionar notificaciones del sistema.
Coordina entre el modelo y la vista siguiendo el patrón MVC.
"""

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
