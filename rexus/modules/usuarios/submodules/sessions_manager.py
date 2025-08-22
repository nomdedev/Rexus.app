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
from typing import Dict, Any, List
from dataclasses import dataclass

# Configurar logging
logger = logging.getLogger(__name__)

# Importar utilidades de seguridad
try:
    from rexus.core.auth_decorators import admin_required, auth_required
except ImportError:
    logger.warning("Security utilities not fully available")
    DataSanitizer = None
    admin_required = lambda x: x
    auth_required = lambda x: x


@dataclass
class SessionInfo:
    """Información de sesión de usuario."""
    session_id: str
    usuario_id: int
    username: str
    ip_address: str
    user_agent: str
    created_at: datetime.datetime
    last_activity: datetime.datetime
    is_active: bool


class SessionsManager:
    """Gestor especializado de sesiones de usuarios."""

    def __init__(self, db_connection=None):
        self.db_connection = db_connection
        self.sanitizer = DataSanitizer() if DataSanitizer else None

        # Configuración de sesiones
        self.session_timeout_minutes = 120  # 2 horas
        self.max_concurrent_sessions = 3
        self.session_cleanup_interval = 30  # minutos

        # Inicializar tabla de sesiones
        self._inicializar_tabla_sesiones()

    def crear_sesion(self, usuario_id: int, username: str, ip_address: str = None, user_agent: str = None) -> Dict[str, Any]:
        """
        Crea una nueva sesión para un usuario.

        Args:
            usuario_id: ID del usuario
            username: Nombre de usuario
            ip_address: Dirección IP del cliente
            user_agent: User-Agent del navegador

        Returns:
            Información de la sesión creada
        """
        try:
            if not self.db_connection:
                return {'success': False, 'message': 'Sin conexión a base de datos'}

            # Limpiar sesiones expiradas
            self._limpiar_sesiones_expiradas()

            # Verificar límite de sesiones concurrentes
            if not self._verificar_limite_sesiones(usuario_id):
                # Cerrar la sesión más antigua si se excede el límite
                self._cerrar_sesion_mas_antigua(usuario_id)

            # Generar ID de sesión seguro
            session_id = self._generar_session_id()

            cursor = self.db_connection.cursor()

            # Crear nueva sesión
            cursor.execute("""
                INSERT INTO sesiones_usuario (
                    session_id, usuario_id, username, ip_address, user_agent,
                    created_at, last_activity, is_active
                ) VALUES (?, ?, ?, ?, ?, GETDATE(), GETDATE(), 1)
            """,
(session_id,
                usuario_id,
                username,
                ip_address or 'unknown',
                user_agent or 'unknown'))

            self.db_connection.commit()

            logger.info(f"Sesión creada para usuario {username} (ID: {usuario_id})")

            return {
                'success': True,
                'session_id': session_id,
                'message': 'Sesión creada exitosamente'
            }

        except Exception as e:
            logger.error(f"Error creando sesión: {e}")
            if self.db_connection:
                try:
                    self.db_connection.rollback()
                except (sqlite3.Error, AttributeError):
                    pass
            return {'success': False, 'message': 'Error interno del sistema'}
        finally:
            if 'cursor' in locals():
                cursor.close()

    def validar_sesion(self, session_id: str) -> Dict[str, Any]:
        """
        Valida si una sesión es válida y actualiza la última actividad.

        Args:
            session_id: ID de la sesión

        Returns:
            Información de validación de sesión
        """
        try:
            if not self.db_connection or not session_id:
                return {'valid': False, 'message': 'Sesión inválida'}

            cursor = self.db_connection.cursor()

            # Obtener información de la sesión
            cursor.execute("""
                SELECT usuario_id, username, created_at, last_activity, is_active
                FROM sesiones_usuario
                WHERE session_id = ? AND is_active = 1
            """, (session_id,))

            result = cursor.fetchone()
            if not result:
                return {'valid': False, 'message': 'Sesión no encontrada'}

            usuario_id, username, created_at, last_activity, is_active = result

            # Verificar timeout
            now = datetime.datetime.now()
            if last_activity:
                tiempo_inactivo = now - last_activity
                if tiempo_inactivo.total_seconds() > (self.session_timeout_minutes * 60):
                    # Cerrar sesión por timeout
                    self.cerrar_sesion(session_id)
                    return {'valid': False, 'message': 'Sesión expirada por inactividad'}

            # Actualizar última actividad
            cursor.execute("""
                UPDATE sesiones_usuario
                SET last_activity = GETDATE()
                WHERE session_id = ?
            """, (session_id,))

            self.db_connection.commit()

            return {
                'valid': True,
                'usuario_id': usuario_id,
                'username': username,
                'created_at': created_at,
                'last_activity': now
            }

        except Exception as e:
            logger.error(f"Error validando sesión: {e}")
            return {'valid': False, 'message': 'Error interno del sistema'}
        finally:
            if 'cursor' in locals():
                cursor.close()

    def cerrar_sesion(self, session_id: str) -> Dict[str, Any]:
        """
        Cierra una sesión específica.

        Args:
            session_id: ID de la sesión a cerrar

        Returns:
            Resultado de la operación
        """
        try:
            if not self.db_connection:
                return {'success': False, 'message': 'Sin conexión a base de datos'}

            cursor = self.db_connection.cursor()

            # Marcar sesión como inactiva
            cursor.execute("""
                UPDATE sesiones_usuario
                SET is_active = 0, closed_at = GETDATE()
                WHERE session_id = ?
            """, (session_id,))

            if cursor.rowcount == 0:
                return {'success': False, 'message': 'Sesión no encontrada'}

            self.db_connection.commit()

            logger.info(f"Sesión cerrada: {session_id}")
            return {'success': True, 'message': 'Sesión cerrada correctamente'}

        except Exception as e:
            logger.error(f"Error cerrando sesión: {e}")
            if self.db_connection:
                try:
                    self.db_connection.rollback()
                except (sqlite3.Error, AttributeError):
                    pass
            return {'success': False, 'message': 'Error interno del sistema'}
        finally:
            if 'cursor' in locals():
                cursor.close()

    @admin_required
    def cerrar_todas_sesiones_usuario(self, usuario_id: int) -> Dict[str, Any]:
        """
        Cierra todas las sesiones de un usuario específico.

        Args:
            usuario_id: ID del usuario

        Returns:
            Resultado de la operación
        """
        try:
            if not self.db_connection:
                return {'success': False, 'message': 'Sin conexión a base de datos'}

            cursor = self.db_connection.cursor()

            # Cerrar todas las sesiones activas del usuario
            cursor.execute("""
                UPDATE sesiones_usuario
                SET is_active = 0, closed_at = GETDATE()
                WHERE usuario_id = ? AND is_active = 1
            """, (usuario_id,))

            sesiones_cerradas = cursor.rowcount
            self.db_connection.commit()

            logger.info(f"Cerradas {sesiones_cerradas} sesiones para usuario {usuario_id}")
            return {
                'success': True,
                'message': f'{sesiones_cerradas} sesiones cerradas',
                'sesiones_cerradas': sesiones_cerradas
            }

        except Exception as e:
            logger.error(f"Error cerrando sesiones del usuario: {e}")
            if self.db_connection:
                try:
                    self.db_connection.rollback()
                except (sqlite3.Error, AttributeError):
                    pass
            return {'success': False, 'message': 'Error interno del sistema'}
        finally:
            if 'cursor' in locals():
                cursor.close()
    def obtener_sesiones_usuario(self, usuario_id: int) -> List[SessionInfo]:
        """
        Obtiene todas las sesiones activas de un usuario.

        Args:
            usuario_id: ID del usuario

        Returns:
            Lista de sesiones activas
        """
        try:
            if not self.db_connection:
                return []

            cursor = self.db_connection.cursor()

            cursor.execute("""
                SELECT session_id, usuario_id, username, ip_address, user_agent,
                       created_at, last_activity, is_active
                FROM sesiones_usuario
                WHERE usuario_id = ? AND is_active = 1
                ORDER BY created_at DESC
            """, (usuario_id,))

            sesiones = []
            for row in cursor.fetchall():
                sesion = SessionInfo(
                    session_id=row[0],
                    usuario_id=row[1],
                    username=row[2],
                    ip_address=row[3],
                    user_agent=row[4],
                    created_at=row[5],
                    last_activity=row[6],
                    is_active=bool(row[7])
                )
                sesiones.append(sesion)

            return sesiones

        except Exception as e:
            logger.error(f"Error obteniendo sesiones del usuario: {e}")
            return []
        finally:
            if 'cursor' in locals():
                cursor.close()

    @admin_required
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
            logger.error(f"Error obteniendo estadísticas de sesiones: {e}")
            return {}
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
            logger.error(f"Error verificando límite de sesiones: {e}")
            return True
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
            logger.error(f"Error cerrando sesión más antigua: {e}")
        finally:
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
            logger.error(f"Error limpiando sesiones expiradas: {e}")
        finally:
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
            logger.error(f"Error inicializando tabla de sesiones: {e}")
        finally:
            if 'cursor' in locals():
                cursor.close()
