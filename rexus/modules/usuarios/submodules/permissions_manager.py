"""
Permissions Manager - Módulo especializado para gestión de permisos
Refactorizado de UsuariosModel para mejor mantenibilidad

Responsabilidades:
- Gestión de roles y permisos
- Verificación de permisos por módulo
- Asignación y revocación de permisos
- Control de acceso basado en roles (RBAC)
"""

import logging
import re
import sqlite3

class PermissionsManager:

    def cambiar_rol_usuario(self,
usuario_id: int,
        nuevo_rol: str) -> Dict[str,
        Any]:
        """
        Cambia el rol de un usuario.

        Args:
            usuario_id: ID del usuario
            nuevo_rol: Nuevo rol a asignar

        Returns:
            Resultado de la operación
        """
        try:
            if not self.db_connection:
                return {'success': False, 'message': 'Sin conexión a base de datos'}

            # Sanitizar y validar rol usando enum seguro
            nuevo_rol = self._sanitize_input(nuevo_rol)
            if not self._validate_role(nuevo_rol):
                valid_roles = [role.value for role in UserRole]
                return {
                    'success': False,
                    'message': f'Rol inválido. Roles válidos: {", ".join(valid_roles)}'
                }

            cursor = None


            cursor = self.db_connection.cursor()

            # Actualizar rol
            cursor.execute("""
                UPDATE usuarios
                SET rol = ?, updated_at = ?
                WHERE id = ? AND activo = 1
            """, (nuevo_rol, datetime.now(), usuario_id))

            if cursor.rowcount == 0:
                return {'success': False, 'message': 'Usuario no encontrado'}

            self.db_connection.commit()

            # Log de auditoría de seguridad
            self._log_permission_change("ROLE_CHANGE", usuario_id, nuevo_rol)
            
            logger.info("Rol cambiado a %s para usuario %s", nuevo_rol, usuario_id)
            return {"success": True, "message": "Rol cambiado a {}".format(nuevo_rol)}

        except sqlite3.Error as e:
            logger.error("Error de base de datos cambiando rol: %s", e)
            if self.db_connection:
                try:
                    self.db_connection.rollback()
                except sqlite3.Error:
                    logger.error("Error adicional durante rollback")
            return {'success': False, 'message': 'Error de base de datos'}
        except Exception as e:
            logger.exception("Error inesperado cambiando rol: %s", e)
            if self.db_connection:
                try:
                    self.db_connection.rollback()
                except sqlite3.Error:
                    pass
            return {'success': False, 'message': 'Error interno del sistema'}
        finally:
            if cursor is not None:
                    cursor.close()

    def obtener_modulos_permitidos(self, usuario_data: Dict[str, Any]) -> List[str]:
        """
        Obtiene los módulos a los que tiene acceso un usuario.

        Args:
            usuario_data: Datos del usuario

        Returns:
            Lista de módulos accesibles
        """
        try:
            usuario_id = (usuario_data.get('id') or '')
            if not usuario_id:
                return []

            permisos = self.obtener_permisos_usuario(usuario_id)
            modulos = set()

            for permiso in permisos:
                if ':' in permiso:
                    modulo = permiso.split(':')[0]
                    modulos.add(modulo)

            return list(modulos)

        except Exception as e:
            logger.exception("Error obteniendo módulos permitidos: %s", e)
            # FIXME: Specify concrete exception types instead of generic Exceptionreturn []

    def _obtener_permisos_por_rol(self, rol: str) -> List[str]:
        """
        Obtiene permisos por defecto de un rol.

        Args:
            rol: Nombre del rol

        Returns:
            Lista de permisos
        """
        return self.default_permissions.get(rol.lower(), [])

    def _sanitize_input(self, value: str) -> str:
        """
        Sanitiza entrada para prevenir ataques de inyección.
        
        Args:
            value: Valor a sanitizar
            
        Returns:
            Valor sanitizado
            
        Raises:
            ValueError: Si la entrada es inválida
        """
        if not isinstance(value, str):
            raise ValueError("Input must be string")
        
        # Remover caracteres peligrosos
        sanitized = re.sub(r'[^\w\-]', '', value.strip())
        if len(sanitized) > 50:  # Límite razonable
            raise ValueError("Input too long")
        if not sanitized:
            raise ValueError("Input cannot be empty after sanitization")
            
        return sanitized.lower()

    def _validate_role(self, role: str) -> bool:
        """
        Valida rol contra enumeración segura.
        
        Args:
            role: Rol a validar
            
        Returns:
            True si el rol es válido
        """
        try:
            UserRole(role.lower())
            return True
        except ValueError:
            return False

    def _validate_input_length(self, value: str, max_length: int = 50) -> bool:
        """
        Valida longitud de entrada.
        
        Args:
            value: Valor a validar
            max_length: Longitud máxima permitida
            
        Returns:
            True si la longitud es válida
        """
        return isinstance(value, str) and len(value.strip()) <= max_length

    def _log_permission_change(self, action: str, user_id: int, permission: str, actor_id: int = None):
        """
        Registra cambios de permisos para auditoría de seguridad.
        
        Args:
            action: Acción realizada (ASSIGN, REVOKE, ROLE_CHANGE)
            user_id: ID del usuario objetivo
            permission: Permiso o rol modificado
            actor_id: ID del usuario que realiza la acción
        """
        audit_logger = logging.getLogger('security.audit')
        audit_logger.info(
            "PERMISSION_CHANGE: action=%s, target_user=%s, permission=%s, actor=%s, timestamp=%s",
            action, user_id, permission, actor_id or 'SYSTEM', datetime.now().isoformat()
        )

    def _validar_modulo_accion(self, modulo: str, accion: str) -> bool:
        """
        Valida que el módulo y acción sean válidos.

        Args:
            modulo: Módulo a validar
            accion: Acción a validar

        Returns:
            True si son válidos
        """
        modulos_validos = [m.value for m in SystemModule]
        acciones_validas = ['read', 'write', 'admin']

        return (modulo.lower() in modulos_validos and
                accion.lower() in acciones_validas)

    def _crear_tabla_permisos_usuarios(self, cursor) -> None:
        """
        Crea la tabla de permisos de usuarios si no existe.

        Args:
            cursor: Cursor de base de datos
        """
        try:
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='permisos_usuarios' AND xtype='U')
                CREATE TABLE permisos_usuarios (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    usuario_id INT NOT NULL,
                    modulo NVARCHAR(50) NOT NULL,
                    accion NVARCHAR(20) NOT NULL,
                    activo BIT DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME NULL,
                    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
                )
            """)
        except Exception as e:
            logger.exception("Error creando tabla permisos_usuarios: %s", e)
            # FIXME: Specify concrete exception types instead of generic Exceptiondef obtener_estadisticas_permisos(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de permisos del sistema.

        Returns:
            Estadísticas de permisos
        """
        try:
            if not self.db_connection:
                return {}

            cursor = None


            cursor = self.db_connection.cursor()

            stats = {}

            # Usuarios por rol
            cursor.execute("""
                SELECT rol, COUNT(*) as cantidad
                FROM usuarios
                WHERE activo = 1
                GROUP BY rol
            """)

            stats['usuarios_por_rol'] = {}
            for row in cursor.fetchall():
                stats['usuarios_por_rol'][row[0]] = row[1]

            # Permisos específicos asignados
            cursor.execute("""
                SELECT COUNT(*) FROM permisos_usuarios WHERE activo = 1
            """)
            stats['permisos_especificos'] = cursor.fetchone()[0]

            # Módulos más utilizados
            cursor.execute("""
                SELECT modulo, COUNT(*) as cantidad
                FROM permisos_usuarios
                WHERE activo = 1
                GROUP BY modulo
                ORDER BY cantidad DESC
            """)

            stats['modulos_mas_utilizados'] = []
            for row in cursor.fetchall()[:5]:
                stats['modulos_mas_utilizados'].append({
                    'modulo': row[0],
                    'cantidad': row[1]
                })

            return stats

        except Exception as e:
            logger.exception("Error obteniendo estadísticas de permisos: %s", e)
            # FIXME: Specify concrete exception types instead of generic Exceptionreturn {}
        finally:
            if cursor is not None:
                    cursor.close()
