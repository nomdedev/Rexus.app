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
from datetime import datetime
from typing import Dict, Any, List
from enum import Enum

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



class PermissionLevel(Enum):
    """Niveles de permisos del sistema."""
    NONE = 0
    READ = 1
    WRITE = 2
    ADMIN = 3


class SystemModule(Enum):
    """Módulos del sistema con permisos granulares."""
    USUARIOS = "usuarios"
    INVENTARIO = "inventario"
    OBRAS = "obras"
    COMPRAS = "compras"
    LOGISTICA = "logistica"
    HERRAJES = "herrajes"
    VIDRIOS = "vidrios"
    AUDITORIA = "auditoria"
    ADMINISTRACION = "administracion"
    CONFIGURACION = "configuracion"


class UserRole(Enum):
    """Roles seguros del sistema."""
    VIEWER = "viewer"
    OPERATOR = "operator"
    SUPERVISOR = "supervisor"
    ADMIN = "admin"


class PermissionsManager:
    """Gestor especializado de permisos y roles."""

    def __init__(self, db_connection=None):
        self.db_connection = db_connection
        # Usar unified_sanitizer en lugar de DataSanitizer
        try:
            from rexus.utils.unified_sanitizer import unified_sanitizer
            self.sanitizer = unified_sanitizer
        except ImportError:
            self.sanitizer = None

        # Configuración de permisos por defecto
        self.default_permissions = {
            'viewer': [
                'inventario:read', 'obras:read', 'compras:read'
            ],
            'operator': [
                'inventario:read', 'inventario:write',
                'obras:read', 'obras:write',
                'compras:read', 'compras:write',
                'logistica:read', 'logistica:write'
            ],
            'supervisor': [
                'inventario:read', 'inventario:write', 'inventario:admin',
                'obras:read', 'obras:write', 'obras:admin',
                'compras:read', 'compras:write', 'compras:admin',
                'logistica:read', 'logistica:write', 'logistica:admin',
                'herrajes:read', 'herrajes:write', 'herrajes:admin',
                'vidrios:read', 'vidrios:write', 'vidrios:admin'
            ],
            'admin': [
                'usuarios:read', 'usuarios:write', 'usuarios:admin',
                'inventario:read', 'inventario:write', 'inventario:admin',
                'obras:read', 'obras:write', 'obras:admin',
                'compras:read', 'compras:write', 'compras:admin',
                'logistica:read', 'logistica:write', 'logistica:admin',
                'herrajes:read', 'herrajes:write', 'herrajes:admin',
                'vidrios:read', 'vidrios:write', 'vidrios:admin',
                'auditoria:read', 'auditoria:write', 'auditoria:admin',
                'administracion:read', 'administracion:write', 'administracion:admin',
                'configuracion:read', 'configuracion:write', 'configuracion:admin'
            ]
        }
    def obtener_permisos_usuario(self, usuario_id: int) -> List[str]:
        """
        Obtiene todos los permisos de un usuario.

        Args:
            usuario_id: ID del usuario

        Returns:
            Lista de permisos en formato 'modulo:accion'
        """
        try:
            if not self.db_connection:
                return []

            cursor = None


            cursor = self.db_connection.cursor()

            # Obtener rol del usuario
            cursor.execute("""
                SELECT rol FROM usuarios
                WHERE id = ? AND activo = 1
            """, (usuario_id,))

            result = cursor.fetchone()
            if not result:
                return []

            rol = result[0]

            # Obtener permisos del rol
            permisos_rol = self._obtener_permisos_por_rol(rol)

            # Obtener permisos específicos del usuario
            cursor.execute("""
                SELECT modulo, accion FROM permisos_usuarios
                WHERE usuario_id = ? AND activo = 1
            """, (usuario_id,))

            permisos_especificos = []
            for row in cursor.fetchall():
                permisos_especificos.append(f"{row[0]}:{row[1]}")

            # Combinar permisos
            todos_permisos = list(set(permisos_rol + permisos_especificos))

            return todos_permisos

        except Exception as e:
            logger.error("Error obteniendo permisos: %s", e)
            return []
        finally:
            if cursor is not None:
                    cursor.close()
    def verificar_permiso_usuario(self,
usuario_id: int,
        modulo: str,
        accion: str) -> bool:
        """
        Verifica si un usuario tiene un permiso específico.

        Args:
            usuario_id: ID del usuario
            modulo: Módulo del sistema
            accion: Acción requerida (read, write, admin)

        Returns:
            True si tiene el permiso
        """
        try:
            permisos = self.obtener_permisos_usuario(usuario_id)
            permiso_requerido = f"{modulo.lower()}:{accion.lower()}"

            # Verificar permiso específico
            if permiso_requerido in permisos:
                return True

            # Verificar permisos de nivel superior
            if accion.lower() == 'read':
                permisos_superiores = [
                    f"{modulo.lower()}:write",
                    f"{modulo.lower()}:admin"
                ]
                return any(p in permisos for p in permisos_superiores)

            if accion.lower() == 'write':
                return f"{modulo.lower()}:admin" in permisos

            return False

        except Exception as e:
            logger.error("Error verificando permiso: %s", e)
            return False

    @admin_required
    def asignar_permiso_usuario(self,
usuario_id: int,
        modulo: str,
        accion: str) -> Dict[str,
        Any]:
        """
        Asigna un permiso específico a un usuario.

        Args:
            usuario_id: ID del usuario
            modulo: Módulo del sistema
            accion: Acción a permitir

        Returns:
            Resultado de la operación
        """
        try:
            if not self.db_connection:
                return {'success': False, 'message': 'Sin conexión a base de datos'}

            # Sanitizar y validar módulo y acción
            modulo = self._sanitize_input(modulo)
            accion = self._sanitize_input(accion)
            
            if not self._validar_modulo_accion(modulo, accion):
                return {'success': False, 'message': 'Módulo o acción inválida'}

            cursor = None


            cursor = self.db_connection.cursor()

            # Verificar que el usuario existe
            cursor.execute("SELECT COUNT(*) FROM usuarios WHERE id = ? AND activo = 1", (usuario_id,))
            if cursor.fetchone()[0] == 0:
                return {'success': False, 'message': 'Usuario no encontrado'}

            # Crear tabla de permisos si no existe
            self._crear_tabla_permisos_usuarios(cursor)

            # Verificar si ya tiene el permiso
            cursor.execute("""
                SELECT COUNT(*) FROM permisos_usuarios
                WHERE usuario_id = ? AND modulo = ? AND accion = ? AND activo = 1
            """, (usuario_id, modulo, accion))

            if cursor.fetchone()[0] > 0:
                return {'success': True, 'message': 'El usuario ya tiene este permiso'}

            # Insertar permiso
            cursor.execute("""
                INSERT INTO permisos_usuarios (usuario_id, modulo, accion, activo, created_at)
                VALUES (?, ?, ?, 1, ?)
            """, (usuario_id, modulo, accion, datetime.now()))

            self.db_connection.commit()

            # Log de auditoría de seguridad
            self._log_permission_change("ASSIGN", usuario_id, f"{modulo}:{accion}")
            
            logger.info("Permiso asignado: %s:%s a usuario %s", modulo, accion, usuario_id)
            return {'success': True, 'message': 'Permiso asignado correctamente'}

        except Exception as e:
            logger.error("Error asignando permiso: %s", e)
            if self.db_connection:
                try:
                    self.db_connection.rollback()
                except Exception as rollback_error:
                    logger.error("Error en rollback: %s", rollback_error)
                    return {'success': False, 'message': 'Error crítico del sistema'}
            return {'success': False, 'message': 'Error interno del sistema'}
        finally:
            if cursor is not None:
                    cursor.close()

    @admin_required
    def revocar_permiso_usuario(self,
usuario_id: int,
        modulo: str,
        accion: str) -> Dict[str,
        Any]:
        """
        Revoca un permiso específico de un usuario.

        Args:
            usuario_id: ID del usuario
            modulo: Módulo del sistema
            accion: Acción a revocar

        Returns:
            Resultado de la operación
        """
        try:
            if not self.db_connection:
                return {'success': False, 'message': 'Sin conexión a base de datos'}

            # Sanitizar entrada
            modulo = self._sanitize_input(modulo)
            accion = self._sanitize_input(accion)

            cursor = None
            cursor = self.db_connection.cursor()

            # Soft delete del permiso
            cursor.execute("""
                UPDATE permisos_usuarios
                SET activo = 0, updated_at = ?
                WHERE usuario_id = ? AND modulo = ? AND accion = ? AND activo = 1
            """, (datetime.now(), usuario_id, modulo, accion))

            if cursor.rowcount == 0:
                return {'success': False, 'message': 'Permiso no encontrado o ya revocado'}

            self.db_connection.commit()

            # Log de auditoría de seguridad
            self._log_permission_change("REVOKE", usuario_id, f"{modulo}:{accion}")
            
            logger.info("Permiso revocado: %s:%s de usuario %s", modulo, accion, usuario_id)
            return {'success': True, 'message': 'Permiso revocado correctamente'}

        except Exception as e:
            logger.error("Error revocando permiso: %s", e)
            if self.db_connection:
                try:
                    self.db_connection.rollback()
                except Exception as rollback_error:
                    logger.error("Error en rollback: %s", rollback_error)
                    return {'success': False, 'message': 'Error crítico del sistema'}
            return {'success': False, 'message': 'Error interno del sistema'}
        finally:
            if cursor is not None:
                    cursor.close()

    @admin_required
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

        except Exception as e:
            logger.error("Error cambiando rol: %s", e)
            if self.db_connection:
                try:
                    self.db_connection.rollback()
                except Exception:
                    logger.error("Error en operación de base de datos: %s", e)
                    return {'success': False, 'message': 'Error crítico del sistema'}
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
            logger.error("Error obteniendo módulos permitidos: %s", e)
            return []

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
            logger.error("Error creando tabla permisos_usuarios: %s", e)
    def obtener_estadisticas_permisos(self) -> Dict[str, Any]:
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
            logger.error("Error obteniendo estadísticas de permisos: %s", e)
            return {}
        finally:
            if cursor is not None:
                    cursor.close()
