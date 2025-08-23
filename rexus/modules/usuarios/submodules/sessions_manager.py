"""
Sessions Manager - Módulo especializado para gestión de sesiones de usuarios
Refactorizado de UsuariosModel para mejor mantenibilidad

Responsabilidades:
- Gestión de sesiones de usuario
- Control de sesiones concurrentes
- Timeout automático de sesiones
- Auditoría de actividad de sesión
"""

import datetime
import secrets
import logging
                def obtener_estadisticas_sesiones(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de sesiones del sistema.

        Returns:
            Estadísticas de sesiones
        """
        try:
            if not self.db_connection:
                return {}

            cursor = self.db_connection.cursor()

            stats = {}

            # Sesiones activas totales
            cursor.execute("SELECT COUNT(*) FROM sesiones_usuario WHERE is_active = 1")
            stats['sesiones_activas'] = cursor.fetchone()[0]

            # Usuarios únicos con sesiones activas
            cursor.execute("""
                SELECT COUNT(DISTINCT usuario_id)
                FROM sesiones_usuario
                WHERE is_active = 1
            """)
            stats['usuarios_conectados'] = cursor.fetchone()[0]

            # Promedio de duración de sesiones (últimas 24 horas)
            cursor.execute("""
                SELECT AVG(DATEDIFF(MINUTE,
created_at,
                    COALESCE(closed_at,
                    GETDATE())))
                FROM sesiones_usuario
                WHERE created_at > DATEADD(DAY, -1, GETDATE())
            """)
            result = cursor.fetchone()[0]
            stats['duracion_promedio_minutos'] = float(result) if result else 0

            # Top IPs por número de sesiones (últimas 24 horas)
            cursor.execute("""
                SELECT TOP 5 ip_address, COUNT(*) as cantidad
                FROM sesiones_usuario
                WHERE created_at > DATEADD(DAY, -1, GETDATE())
                GROUP BY ip_address
                ORDER BY cantidad DESC
            """)

            stats['top_ips'] = []
            for row in cursor.fetchall():
                stats['top_ips'].append({
                    'ip': row[0],
                    'sesiones': row[1]
                })

            return stats

        except Exception as e:
        finally:
            if 'cursor' in locals():
                cursor.close()

    def _generar_session_id(self) -> str:
        """
        Genera un ID de sesión seguro y único.

        Returns:
            ID de sesión
        """
        return secrets.token_urlsafe(32)

    def _verificar_limite_sesiones(self, usuario_id: int) -> bool:
        """
        Verifica si el usuario puede crear una nueva sesión.

        Args:
            usuario_id: ID del usuario

        Returns:
            True si puede crear una nueva sesión
        """
        try:
            if not self.db_connection:
                return True

            cursor = self.db_connection.cursor()

            cursor.execute("""
                SELECT COUNT(*) FROM sesiones_usuario
                WHERE usuario_id = ? AND is_active = 1
            """, (usuario_id,))

            sesiones_activas = cursor.fetchone()[0]
            return sesiones_activas < self.max_concurrent_sessions

        except Exception as e:
        finally:
            if 'cursor' in locals():
                cursor.close()

    def _cerrar_sesion_mas_antigua(self, usuario_id: int) -> None:
        """
        Cierra la sesión más antigua del usuario.

        Args:
            usuario_id: ID del usuario
        """
        try:
            if not self.db_connection:
                return

            cursor = self.db_connection.cursor()

            # Obtener la sesión más antigua
            cursor.execute("""
                SELECT TOP 1 session_id FROM sesiones_usuario
                WHERE usuario_id = ? AND is_active = 1
                ORDER BY created_at ASC
            """, (usuario_id,))

            result = cursor.fetchone()
            if result:
                self.cerrar_sesion(result[0])
                logger.info(f"Sesión más antigua cerrada para usuario {usuario_id}")

        except Exception as e:
            if 'cursor' in locals():
                cursor.close()

    def _limpiar_sesiones_expiradas(self) -> None:
        """Limpia sesiones expiradas del sistema."""
        try:
            if not self.db_connection:
                return

            cursor = self.db_connection.cursor()

            # Calcular tiempo límite
            tiempo_limite = datetime.datetime.now() - datetime.timedelta(minutes=self.session_timeout_minutes)

            # Cerrar sesiones expiradas
            cursor.execute("""
                UPDATE sesiones_usuario
                SET is_active = 0, closed_at = GETDATE()
                WHERE is_active = 1 AND last_activity < ?
            """, (tiempo_limite,))

            sesiones_cerradas = cursor.rowcount
            if sesiones_cerradas > 0:
                self.db_connection.commit()
                logger.info(f"Limpiadas {sesiones_cerradas} sesiones expiradas")

        except Exception as e:
            if 'cursor' in locals():
                cursor.close()

    def _inicializar_tabla_sesiones(self) -> None:
        """Inicializa la tabla de sesiones si no existe."""
        try:
            if not self.db_connection:
                return

            cursor = self.db_connection.cursor()

            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='sesiones_usuario' AND xtype='U')
                CREATE TABLE sesiones_usuario (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    session_id NVARCHAR(64) UNIQUE NOT NULL,
                    usuario_id INT NOT NULL,
                    username NVARCHAR(50) NOT NULL,
                    ip_address NVARCHAR(45) NULL,
                    user_agent NVARCHAR(500) NULL,
                    created_at DATETIME DEFAULT GETDATE(),
                    last_activity DATETIME DEFAULT GETDATE(),
                    closed_at DATETIME NULL,
                    is_active BIT DEFAULT 1,
                    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
                )
            """)

            self.db_connection.commit()

        except Exception as e:
            if 'cursor' in locals():
                cursor.close()
