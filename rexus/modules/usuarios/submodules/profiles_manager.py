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
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

# Configurar logging
logger = logging.getLogger(__name__)

# Importar utilidades de seguridad
try:
    from rexus.utils.data_sanitizer import DataSanitizer
    from rexus.core.auth_decorators import admin_required, auth_required
except ImportError:
    logger.warning("Security utilities not fully available")
    DataSanitizer = None
    admin_required = lambda x: x
    auth_required = lambda x: x


class ProfilesManager:
    """Gestor especializado de perfiles de usuarios."""
    
    def __init__(self, db_connection=None):
        self.db_connection = db_connection
        self.data_sanitizer = DataSanitizer() if DataSanitizer else None
        
        # Configuración de validaciones
        self.username_min_length = 3
        self.username_max_length = 50
        self.email_max_length = 100
        self.nombre_max_length = 100
    
    @admin_required
    def crear_usuario(self, datos_usuario: Dict[str, Any]) -> Dict[str, Any]:
        """
        Crea un nuevo usuario en el sistema.
        
        Args:
            datos_usuario: Datos del usuario a crear
            
        Returns:
            Resultado de la operación
        """
        try:
            if not self.db_connection:
                return {'success': False, 'message': 'Sin conexión a base de datos'}
            
            # Validar datos requeridos
            validacion = self._validar_datos_usuario(datos_usuario)
            if not validacion['valid']:
                return {'success': False, 'message': validacion['message']}
            
            # Verificar unicidad de username y email
            if not self._verificar_unicidad_usuario(datos_usuario.get('username'), datos_usuario.get('email')):
                return {'success': False, 'message': 'Username o email ya existe'}
            
            cursor = self.db_connection.cursor()
            
            # Sanitizar datos
            datos_limpios = self._sanitizar_datos_usuario(datos_usuario)
            
            # Insertar usuario
            cursor.execute("""
                INSERT INTO usuarios (
                    username, password, nombre_completo, email, telefono,
                    direccion, rol, activo, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, 1, GETDATE(), GETDATE())
            """, (
                datos_limpios['username'],
                datos_limpios['password_hash'],  # Ya hasheada por auth_manager
                datos_limpios.get('nombre_completo', ''),
                datos_limpios.get('email', ''),
                datos_limpios.get('telefono', ''),
                datos_limpios.get('direccion', ''),
                datos_limpios.get('rol', 'viewer')
            ))
            
            # Obtener ID del usuario creado
            cursor.execute("SELECT @@IDENTITY")
            usuario_id = cursor.fetchone()[0]
            
            self.db_connection.commit()
            
            logger.info(f"Usuario creado: {datos_limpios['username']} (ID: {usuario_id})")
            return {
                'success': True,
                'message': 'Usuario creado exitosamente',
                'usuario_id': usuario_id
            }
            
        except Exception as e:
            logger.error(f"Error creando usuario: {e}")
            if self.db_connection:
                try:
                    self.db_connection.rollback()
                except Exception:
                    pass
            return {'success': False, 'message': 'Error interno del sistema'}
        finally:
            if 'cursor' in locals():
                cursor.close()
    
    @auth_required
    def obtener_usuario_por_id(self, usuario_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene un usuario por su ID.
        
        Args:
            usuario_id: ID del usuario
            
        Returns:
            Datos del usuario o None
        """
        try:
            if not self.db_connection:
                return None
            
            cursor = self.db_connection.cursor()
            
            cursor.execute("""
                SELECT id, username, nombre_completo, email, telefono, direccion,
                       rol, activo, created_at, updated_at, last_login
                FROM usuarios 
                WHERE id = ?
            """, (usuario_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            return self._row_to_dict(row)
            
        except Exception as e:
            logger.error(f"Error obteniendo usuario por ID: {e}")
            return None
        finally:
            if 'cursor' in locals():
                cursor.close()
    
    @auth_required
    def obtener_usuario_por_username(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene un usuario por su username.
        
        Args:
            username: Username del usuario
            
        Returns:
            Datos del usuario o None
        """
        try:
            if not self.db_connection:
                return None
            
            # Sanitizar entrada
            if self.data_sanitizer:
                username_clean = self.data_sanitizer.sanitize_string(username, self.username_max_length)
            else:
                username_clean = str(username)[:self.username_max_length]
            
            cursor = self.db_connection.cursor()
            
            cursor.execute("""
                SELECT id, username, nombre_completo, email, telefono, direccion,
                       rol, activo, created_at, updated_at, last_login
                FROM usuarios 
                WHERE username = ?
            """, (username_clean,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            return self._row_to_dict(row)
            
        except Exception as e:
            logger.error(f"Error obteniendo usuario por username: {e}")
            return None
        finally:
            if 'cursor' in locals():
                cursor.close()
    
    @auth_required
    def obtener_usuario_por_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene un usuario por su email.
        
        Args:
            email: Email del usuario
            
        Returns:
            Datos del usuario o None
        """
        try:
            if not self.db_connection:
                return None
            
            # Sanitizar entrada
            if self.data_sanitizer:
                email_clean = self.data_sanitizer.sanitize_string(email, self.email_max_length)
            else:
                email_clean = str(email)[:self.email_max_length]
            
            cursor = self.db_connection.cursor()
            
            cursor.execute("""
                SELECT id, username, nombre_completo, email, telefono, direccion,
                       rol, activo, created_at, updated_at, last_login
                FROM usuarios 
                WHERE email = ?
            """, (email_clean,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            return self._row_to_dict(row)
            
        except Exception as e:
            logger.error(f"Error obteniendo usuario por email: {e}")
            return None
        finally:
            if 'cursor' in locals():
                cursor.close()
    
    @auth_required
    def obtener_todos_usuarios(self, incluir_inactivos: bool = False) -> List[Dict[str, Any]]:
        """
        Obtiene todos los usuarios del sistema.
        
        Args:
            incluir_inactivos: Si incluir usuarios inactivos
            
        Returns:
            Lista de usuarios
        """
        try:
            if not self.db_connection:
                return []
            
            cursor = self.db_connection.cursor()
            
            if incluir_inactivos:
                query = """
                    SELECT id, username, nombre_completo, email, telefono, direccion,
                           rol, activo, created_at, updated_at, last_login
                    FROM usuarios 
                    ORDER BY created_at DESC
                """
                cursor.execute(query)
            else:
                query = """
                    SELECT id, username, nombre_completo, email, telefono, direccion,
                           rol, activo, created_at, updated_at, last_login
                    FROM usuarios 
                    WHERE activo = 1
                    ORDER BY created_at DESC
                """
                cursor.execute(query)
            
            usuarios = []
            for row in cursor.fetchall():
                usuarios.append(self._row_to_dict(row))
            
            return usuarios
            
        except Exception as e:
            logger.error(f"Error obteniendo todos los usuarios: {e}")
            return []
        finally:
            if 'cursor' in locals():
                cursor.close()
    
    @auth_required
    def actualizar_usuario(self, usuario_id: int, datos_actualizados: Dict[str, Any]) -> Dict[str, Any]:
        """
        Actualiza los datos de un usuario.
        
        Args:
            usuario_id: ID del usuario a actualizar
            datos_actualizados: Datos a actualizar
            
        Returns:
            Resultado de la operación
        """
        try:
            if not self.db_connection:
                return {'success': False, 'message': 'Sin conexión a base de datos'}
            
            # Validar que el usuario existe
            if not self.obtener_usuario_por_id(usuario_id):
                return {'success': False, 'message': 'Usuario no encontrado'}
            
            # Validar datos actualizados
            validacion = self._validar_datos_actualizacion(datos_actualizados)
            if not validacion['valid']:
                return {'success': False, 'message': validacion['message']}
            
            cursor = self.db_connection.cursor()
            
            # Sanitizar datos
            datos_limpios = self._sanitizar_datos_usuario(datos_actualizados)
            
            # Construir query de actualización dinámicamente
            campos_update = []
            valores = []
            
            campos_permitidos = ['nombre_completo', 'email', 'telefono', 'direccion', 'rol']
            
            for campo in campos_permitidos:
                if campo in datos_limpios:
                    campos_update.append(f"{campo} = ?")
                    valores.append(datos_limpios[campo])
            
            if not campos_update:
                return {'success': False, 'message': 'No hay campos para actualizar'}
            
            # Agregar updated_at y usuario_id
            campos_update.append("updated_at = GETDATE()")
            valores.append(usuario_id)
            
            query = f"UPDATE usuarios SET {', '.join(campos_update)} WHERE id = ?"
            cursor.execute(query, valores)
            
            if cursor.rowcount == 0:
                return {'success': False, 'message': 'No se pudo actualizar el usuario'}
            
            self.db_connection.commit()
            
            logger.info(f"Usuario actualizado: ID {usuario_id}")
            return {'success': True, 'message': 'Usuario actualizado exitosamente'}
            
        except Exception as e:
            logger.error(f"Error actualizando usuario: {e}")
            if self.db_connection:
                try:
                    self.db_connection.rollback()
                except Exception:
                    pass
            return {'success': False, 'message': 'Error interno del sistema'}
        finally:
            if 'cursor' in locals():
                cursor.close()
    
    @admin_required
    def eliminar_usuario(self, usuario_id: int) -> Dict[str, Any]:
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
            
            logger.info(f"Usuario eliminado: {usuario['username']} (ID: {usuario_id})")
            return {'success': True, 'message': 'Usuario eliminado exitosamente'}
            
        except Exception as e:
            logger.error(f"Error eliminando usuario: {e}")
            if self.db_connection:
                try:
                    self.db_connection.rollback()
                except Exception:
                    pass
            return {'success': False, 'message': 'Error interno del sistema'}
        finally:
            if 'cursor' in locals():
                cursor.close()
    
    @auth_required
    def obtener_estadisticas_usuarios(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de usuarios del sistema.
        
        Returns:
            Estadísticas de usuarios
        """
        try:
            if not self.db_connection:
                return {}
            
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
            logger.error(f"Error obteniendo estadísticas: {e}")
            return {}
        finally:
            if 'cursor' in locals():
                cursor.close()
    
    def _validar_datos_usuario(self, datos: Dict[str, Any]) -> Dict[str, Any]:
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
    
    def _validar_datos_actualizacion(self, datos: Dict[str, Any]) -> Dict[str, Any]:
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
            if email and ('@' not in email or '.' not in email.split('@')[-1]):
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
            logger.error(f"Error verificando unicidad: {e}")
            return False
        finally:
            if 'cursor' in locals():
                cursor.close()
    
    def _sanitizar_datos_usuario(self, datos: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitiza los datos de usuario.
        
        Args:
            datos: Datos a sanitizar
            
        Returns:
            Datos sanitizados
        """
        if not self.data_sanitizer:
            return datos
        
        datos_limpios = {}
        
        # Campos de texto
        campos_texto = ['username', 'nombre_completo', 'email', 'telefono', 'direccion', 'rol']
        for campo in campos_texto:
            if campo in datos:
                datos_limpios[campo] = self.data_sanitizer.sanitize_string(datos[campo], 200)
        
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