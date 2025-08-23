"""
Sistema de Seguridad Global - Stock.App v1.1.3

Sistema centralizado de autenticación, autorización y control de acceso
para toda la aplicación.
"""

import logging
import uuid
                        allowed_updates = {
                'username': 'UPDATE usuarios SET username = ? WHERE id = ?',
                'email': 'UPDATE usuarios SET email = ? WHERE id = ?',
                'nombre': 'UPDATE usuarios SET nombre = ? WHERE id = ?',
                'apellido': 'UPDATE usuarios SET apellido = ? WHERE id = ?',
                'rol': 'UPDATE usuarios SET rol = ? WHERE id = ?',
                'activo': 'UPDATE usuarios SET activo = ? WHERE id = ?',
                'bloqueado': 'UPDATE usuarios SET bloqueado = ? WHERE id = ?',
                'password_hash': 'UPDATE usuarios SET password_hash = ? WHERE id = ?'
            }

            # Ejecutar updates de forma segura
            for i, field in enumerate(fields):
                field_name = field.replace(' = ?', '').strip()
                if field_name in allowed_updates:
                    cursor.execute(allowed_updates[field_name], (values[i], values[-1]))

            self.db_connection.commit()

            # Log
            self.log_security_event(
                user_id, "USER_UPDATED", "USUARIOS", f"Usuario actualizado: {kwargs}"
            )

            return True

        except Exception as e:
                self.db_connection.rollback()
            return False

    def get_security_logs(self, limit: int = 100) -> List[Dict]:
        """Obtiene logs de seguridad."""
        try:
            cursor = self.db_connection.cursor()
            cursor.execute(
                """
                SELECT ls.id, u.username, ls.accion, ls.modulo, ls.detalles,
                       ls.ip_address, ls.fecha
                FROM logs_seguridad ls
                LEFT JOIN usuarios u ON ls.usuario_id = u.id
                ORDER BY ls.fecha DESC
                OFFSET 0 ROWS FETCH NEXT ? ROWS ONLY
            """,
                (limit,),
            )

            logs = []
            for row in cursor.fetchall():
                logs.append(
                    {
                        "id": row[0],
                        "username": row[1],
                        "accion": row[2],
                        "modulo": row[3],
                        "detalles": row[4],
                        "ip_address": row[5],
                        "fecha": row[6],
                    }
                )

            return logs

        except Exception as e:


# Instancia global del gestor de seguridad
security_manager = None


def get_security_manager() -> SecurityManager:
    """Obtiene la instancia global del gestor de seguridad."""
    return security_manager


def init_security_manager(db_connection) -> SecurityManager:
    """Inicializa el gestor de seguridad."""
    global security_manager
    security_manager = SecurityManager(db_connection)
    # ELIMINADO: No crear usuarios por defecto - RIESGO DE SEGURIDAD
    return security_manager


def initialize_security_manager(db_connection=None) -> SecurityManager:
    """Inicializa el gestor de seguridad - alias para init_security_manager."""
    if not db_connection:
        from rexus.core.database import UsersDatabaseConnection
        db_connection = UsersDatabaseConnection()
        db_connection.trusted = False
        db_connection.connect()

    manager = init_security_manager(db_connection)
    # ELIMINADO: No crear usuarios por defecto - RIESGO DE SEGURIDAD
    return manager
