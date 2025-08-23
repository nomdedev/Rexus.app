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
import sqlite3

class ProfilesManager:

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

            # Soft delete
            cursor.execute("""
                UPDATE usuarios
                SET activo = 0, updated_at = GETDATE()
                WHERE id = ?
            """, (usuario_id,))

            if cursor.rowcount == 0:
                return {'success': False, 'message': 'No se pudo eliminar el usuario'}

            self.db_connection.commit()

            logger.info("Usuario eliminado: %s (ID: %s)",
usuario.get("username",
                "N/A"),
                usuario_id)
            return {'success': True, 'message': 'Usuario eliminado exitosamente'}

        except sqlite3.Error as e:
            logger.error("Error de base de datos eliminando usuario: %s", e)
            try:
                self.db_connection.rollback()
            except sqlite3.Error:
                logger.error("Error adicional durante rollback")
            return {'success': False, 'message': 'Error de base de datos'}
        except Exception as e:
            logger.exception("Error inesperado eliminando usuario: %s", e)
            try:
                self.db_connection.rollback()
            except sqlite3.Error:
                pass
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
            cursor.execute("SELECT COUNT(*) FROM usuarios")
            stats['total_usuarios'] = cursor.fetchone()[0]

            # Usuarios activos
            cursor.execute("SELECT COUNT(*) FROM usuarios WHERE activo = 1")
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
                SELECT COUNT(*) FROM usuarios
                WHERE created_at > DATEADD(DAY, -30, GETDATE())
            """)
            stats['nuevos_usuarios_mes'] = cursor.fetchone()[0]

            # Usuarios con login reciente (últimos 7 días)
            cursor.execute("""
                SELECT COUNT(*) FROM usuarios
                WHERE last_login > DATEADD(DAY, -7, GETDATE())
            """)
            stats['usuarios_activos_semana'] = cursor.fetchone()[0]

            return stats

        except Exception as e:
        finally:
            if cursor is not None:
                try:
                    cursor.close()
                except Exception as e:
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
            cursor.execute("SELECT COUNT(*) FROM usuarios WHERE username = ?", (username,))
            if cursor.fetchone()[0] > 0:
                return False

            # Verificar email si está presente
            if email:
                cursor.execute("SELECT COUNT(*) FROM usuarios WHERE email = ?", (email,))
                if cursor.fetchone()[0] > 0:
                    return False

            return True

        except Exception as e:
        finally:
            if cursor is not None:
                try:
                    cursor.close()
                except Exception as e:
                    logger.error("Error cerrando cursor: %s", e)

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
