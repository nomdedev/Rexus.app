"""
Profiles Manager - Módulo especializado para gestión de perfiles de usuarios
Refactorizado de UsuariosModel para mejor mantenibilidad

Responsabilidades:
- CRUD de usuarios
- Gestión de perfiles y datos personales
- Validación de datos de usuario
- Gestión de configuraciones personales
"""

import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

# SQLQueryManager unificado
try:
    from rexus.core.sql_query_manager import SQLQueryManager
except ImportError:
    from rexus.utils.sql_script_loader import sql_script_loader
    
    class SQLQueryManager:
        def __init__(self):
            self.sql_loader = sql_script_loader

        def get_query(self, path, filename):
            script_name = filename
            return self.sql_loader.load_script(script_name)

class ProfilesManager:
    """Gestor de perfiles de usuarios."""
    
    def __init__(self, db_connection=None):
        """Inicializa el gestor de perfiles."""
        self.db_connection = db_connection
        self.sql_manager = SQLQueryManager()
        self.sql_path = 'usuarios'
        self.logger = logger
        self.username_min_length = 3
        self.username_max_length = 50

    def eliminar_usuario(self, usuario_id: int) -> Optional[Dict[str, Any]]:
        """
        Elimina un usuario (soft delete).

        Args:
            usuario_id: ID del usuario a eliminar

        Returns:
            Resultado de la operación
        """
        try:
            if not self.db_connection:
                return {'success': False, 'message': 'Sin conexión a base de datos'}

            # Verificar que el usuario existe
            usuario = self.obtener_usuario_por_id(usuario_id)
            if not usuario:
                return {'success': False, 'message': 'Usuario no encontrado'}

            cursor = None


            cursor = self.db_connection.cursor()

            # Soft delete usando archivo SQL externo
            params = {'usuario_id': usuario_id}
            cursor.execute(
                self.sql_manager.get_query('sql/09_usuarios', 'update_eliminar_usuario_logico.sql'),
                params
            )

            if cursor.rowcount == 0:
                return {'success': False, 'message': 'No se pudo eliminar el usuario'}

            self.db_connection.commit()

            self.logger.info("Usuario eliminado: %s (ID: %s)",
usuario.get("username",
                "N/A"),
                usuario_id)
            return {'success': True, 'message': 'Usuario eliminado exitosamente'}

        except Exception as e:
            self.logger.error("Error eliminando usuario: %s", e)
            try:
                self.db_connection.rollback()
            except (AttributeError, RuntimeError, ConnectionError) as rollback_error:
                self.logger.error("Error adicional durante rollback: %s", rollback_error)
            return {'success': False, 'message': 'Error interno del sistema'}

    def obtener_estadisticas_usuarios(self):
        """
        Obtiene estadísticas de usuarios del sistema.

        Returns:
            Estadísticas de usuarios
        """
        try:
            if not self.db_connection:
                return {}

            cursor = None


            cursor = self.db_connection.cursor()

            stats = {}

            # Total de usuarios
            cursor.execute(self.sql_manager.ejecutar_consulta_archivo('sql/09_usuarios/count_usuarios_1.sql', params))
            stats['total_usuarios'] = cursor.fetchone()[0]

            # Usuarios activos
            cursor.execute(self.sql_manager.ejecutar_consulta_archivo('sql/09_usuarios/count_usuarios_3.sql', params))
            stats['usuarios_activos'] = cursor.fetchone()[0]

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

            # Nuevos usuarios (últimos 30 días)
            cursor.execute("""
                SELECT COUNT(*), {} FROM usuarios
                WHERE created_at > DATEADD(DAY, -30, GETDATE())
            """)
            stats['nuevos_usuarios_mes'] = cursor.fetchone()[0]

            # Usuarios con login reciente (últimos 7 días)
            cursor.execute("""
                SELECT COUNT(*), {} FROM usuarios
                WHERE last_login > DATEADD(DAY, -7, GETDATE())
            """)
            stats['usuarios_activos_semana'] = cursor.fetchone()[0]

            return stats

        except Exception as e:
            logger.error(f"Error obteniendo estadísticas de usuario: {e}")
            return {}
        finally:
            if cursor is not None:
                try:
                    cursor.close()
                except Exception as e:
                    logger.error(f"Error cerrando cursor: {e}")
        """
        Valida los datos de un usuario.

        Args:
            datos: Datos a validar

        Returns:
            Resultado de validación
        """
        errores = []

        # Validar username
        username = datos.get('username', '')
        if not username:
            errores.append('Username es requerido')
        elif len(username) < self.username_min_length:
            errores.append(f'Username debe tener al menos {self.username_min_length} caracteres')
        elif len(username) > self.username_max_length:
            errores.append(f'Username no puede exceder {self.username_max_length} caracteres')

        # Validar email
        email = datos.get('email', '')
        if email:
            if '@' not in email or '.' not in email.split('@')[-1]:
                errores.append('Email tiene formato inválido')
            elif len(email) > self.email_max_length:
                errores.append(f'Email no puede exceder {self.email_max_length} caracteres')

        # Validar nombre completo
        nombre = datos.get('nombre_completo', '')
        if nombre and len(nombre) > self.nombre_max_length:
            errores.append(f'Nombre completo no puede exceder {self.nombre_max_length} caracteres')

        # Validar rol
        rol = datos.get('rol', 'viewer')
        roles_validos = ['viewer', 'operator', 'supervisor', 'admin']
        if rol not in roles_validos:
            errores.append(f'Rol inválido. Roles válidos: {", ".join(roles_validos)}')

        return {
            'valid': len(errores) == 0,
            'message': '; '.join(errores) if errores else 'Datos válidos'
        }

    def _validar_datos_actualizacion(self,
datos: Dict[str,
        Any]) -> Dict[str,
        Any]:
        """
        Valida datos para actualización (menos estricta).

        Args:
            datos: Datos a validar

        Returns:
            Resultado de validación
        """
        errores = []

        # Validar email si está presente
        if 'email' in datos:
            email = datos['email']
            if email and \
                ('@' not in email or '.' not in email.split('@')[-1]):
                errores.append('Email tiene formato inválido')

        # Validar rol si está presente
        if 'rol' in datos:
            rol = datos['rol']
            roles_validos = ['viewer', 'operator', 'supervisor', 'admin']
            if rol not in roles_validos:
                errores.append(f'Rol inválido. Roles válidos: {", ".join(roles_validos)}')

        return {
            'valid': len(errores) == 0,
            'message': '; '.join(errores) if errores else 'Datos válidos'
        }

    def _verificar_unicidad_usuario(self, username: str, email: str) -> bool:
        """
        Verifica que username y email sean únicos.

        Args:
            username: Username a verificar
            email: Email a verificar

        Returns:
            True si son únicos
        """
        try:
            if not self.db_connection:
                return True

            cursor = None


            cursor = self.db_connection.cursor()

            # Verificar username
            cursor.execute(self.sql_manager.ejecutar_consulta_archivo('sql/09_usuarios/count_usuarios_5.sql', params), (username,))
            if cursor.fetchone()[0] > 0:
                return False

            # Verificar email si está presente
            if email:
                cursor.execute(self.sql_manager.ejecutar_consulta_archivo('sql/09_usuarios/count_usuarios_7.sql', params), (email,))
                if cursor.fetchone()[0] > 0:
                    return False

            return True

        except Exception as e:
            self.logger.error("Error verificando unicidad de usuario: %s", e)
            return False
        finally:
            if cursor is not None:
                try:
                    cursor.close()
                except Exception as e:
                    self.logger.error("Error cerrando cursor: %s", e)

    def sanitizar_datos_usuario(self, datos: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitiza los datos de usuario.

        Args:
            datos: Datos a sanitizar

        Returns:
            Datos sanitizados
        """
        if not self.sanitizer:
            return datos

        datos_limpios = {}

        # Campos de texto
        campos_texto = ['username', 'nombre_completo', 'email', 'telefono', 'direccion', 'rol']
        for campo in campos_texto:
            if campo in datos:
                datos_limpios[campo] = sanitize_string(datos[campo], 200)

        # Campos especiales
        if 'password_hash' in datos:
            datos_limpios['password_hash'] = datos['password_hash']  # Ya hasheada

        return datos_limpios

    def _row_to_dict(self, row) -> Dict[str, Any]:
        """
        Convierte una fila de base de datos a diccionario.

        Args:
            row: Fila de la base de datos

        Returns:
            Diccionario con datos del usuario
        """
        return {
            'id': row[0],
            'username': row[1],
            'nombre_completo': row[2],
            'email': row[3],
            'telefono': row[4],
            'direccion': row[5],
            'rol': row[6],
            'activo': bool(row[7]),
            'created_at': row[8],
            'updated_at': row[9],
            'last_login': row[10] if len(row) > 10 else None
        }
