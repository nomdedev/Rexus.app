
"""
Modelo de Usuarios - Rexus.app
Gestión de usuarios del sistema - USA ÚNICAMENTE LA BASE DE DATOS USERS EXISTENTE
"""

import logging
import hashlib
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class UsuariosModel:
    """Modelo para gestión de usuarios. USA ÚNICAMENTE LA DB USERS EXISTENTE."""
    
    def __init__(self, db_connection=None):
        """Inicializa el modelo de usuarios."""
        self.db_connection = db_connection
        self.sql_manager = None
        self.data_sanitizer = None
        
    def validar_credenciales(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Valida las credenciales de un usuario contra la base de datos users EXISTENTE.
        NO CREA USUARIOS - Solo usa los que ya están en la DB.
        
        Args:
            username: Nombre de usuario
            password: Contraseña en texto plano
            
        Returns:
            Dict con información del usuario si es válido, None si no
        """
        try:
            if not username or not password:
                logger.warning("Username o password vacíos")
                return None
            
            # Usar la función de conexión directa a la base de datos users
            from ...core.database import get_users_connection
            
            db_users = get_users_connection(auto_connect=True)
            
            if not db_users:
                logger.error("No se pudo conectar a la base de datos users")
                return None
            
            # Buscar usuario en la tabla usuarios existente
            query = """
                SELECT
                    id,
                    usuario,
                    password_hash,
                    nombre_completo,
                    email,
                    telefono,
                    rol,
                    estado,
                    intentos_fallidos,
                    bloqueado_hasta,
                    ultimo_acceso,
                    fecha_creacion,
                    fecha_modificacion
                FROM usuarios
                WHERE LOWER(usuario) = LOWER(?)
                    AND activo = 1
                    AND estado IN ('ACTIVO', 'PRIMERA_VEZ')
            """
            
            user_data = db_users.execute_query(query, (username,))
            
            if not user_data:
                logger.warning(f"Usuario '{username}' no encontrado o inactivo en la base de datos users")
                return None
                
            user_row = user_data[0]  # Primer resultado
            
            # Verificar contraseña hasheada
            stored_hash = user_row[2]  # password_hash
            if not self._verify_password(password, stored_hash):
                logger.warning(f"Contraseña incorrecta para usuario '{username}'")
                # Incrementar intentos fallidos en la DB real
                self._incrementar_intentos_fallidos(username, db_users)
                return None
            
            # Mapear datos del usuario
            usuario = {
                'id': user_row[0],
                'usuario': user_row[1],
                'nombre_completo': user_row[3],
                'email': user_row[4],
                'telefono': user_row[5],
                'rol': user_row[6],
                'estado': user_row[7],
                'intentos_fallidos': user_row[8],
                'bloqueado_hasta': user_row[9],
                'ultimo_acceso': user_row[10],
                'fecha_creacion': user_row[11],
                'fecha_modificacion': user_row[12]
            }
            
            # Actualizar último acceso en la DB real
            self._actualizar_ultimo_acceso(user_row[0], db_users)
            
            # Obtener permisos del usuario desde la tabla de permisos existente
            usuario['permisos'] = self._obtener_permisos_usuario(user_row[0], db_users)
            
            logger.info(f"Usuario '{username}' autenticado exitosamente desde base de datos users")
            return usuario
            
        except Exception as e:
            logger.error(f"Error validando credenciales contra DB users: {e}")
            return None
    
    def _verify_password(self, password: str, stored_hash: str) -> bool:
        """
        Verifica si una contraseña coincide con el hash almacenado.
        Soporta diferentes algoritmos de hash que pueden estar en la DB.
        
        Args:
            password: Contraseña en texto plano
            stored_hash: Hash almacenado en la base de datos
            
        Returns:
            True si la contraseña es correcta
        """
        if not stored_hash:
            return False
            
        # Intentar varios métodos de hash que pueden estar en la DB
        password_bytes = password.encode('utf-8')
        
        # SHA-256
        sha256_hash = hashlib.sha256(password_bytes).hexdigest()
        if sha256_hash == stored_hash:
            return True
            
        # MD5 (por compatibilidad con sistemas antiguos)
        md5_hash = hashlib.md5(password_bytes).hexdigest()
        if md5_hash == stored_hash:
            return True
            
        # Texto plano (muy inseguro pero podría existir en DB legacy)
        if password == stored_hash:
            logger.warning("Contraseña almacenada en texto plano - considerar migrar a hash")
            return True
            
        return False
    
    def _incrementar_intentos_fallidos(self, username: str, db_users) -> None:
        """
        Incrementa el contador de intentos fallidos en la tabla usuarios REAL.
        
        Args:
            username: Nombre de usuario
            db_users: Conexión a la base de datos users
        """
        try:
            query = """
                UPDATE usuarios 
                SET intentos_fallidos = intentos_fallidos + 1
                WHERE LOWER(usuario) = LOWER(?)
            """
            db_users.execute_non_query(query, (username,))
            logger.info(f"Incrementados intentos fallidos para usuario '{username}' en DB users")
        except Exception as e:
            logger.error(f"Error incrementando intentos fallidos en DB users: {e}")
    
    def _actualizar_ultimo_acceso(self, user_id: int, db_users) -> None:
        """
        Actualiza la fecha de último acceso en la tabla usuarios REAL.
        
        Args:
            user_id: ID del usuario
            db_users: Conexión a la base de datos users
        """
        try:
            query = """
                UPDATE usuarios 
                SET ultimo_acceso = CURRENT_TIMESTAMP,
                    intentos_fallidos = 0
                WHERE id = ?
            """
            db_users.execute_non_query(query, (user_id,))
            logger.debug(f"Actualizado último acceso para usuario ID: {user_id} en DB users")
        except Exception as e:
            logger.error(f"Error actualizando último acceso en DB users: {e}")
    
    def _obtener_permisos_usuario(self, user_id: int, db_users) -> List[str]:
        """
        Obtiene los permisos/módulos habilitados desde la tabla de permisos REAL.
        
        Args:
            user_id: ID del usuario
            db_users: Conexión a la base de datos users
            
        Returns:
            Lista de módulos permitidos para el usuario
        """
        try:
            # Verificar si existe la tabla permisos_usuario
            query_tabla = "SELECT name FROM sqlite_master WHERE type='table' AND name='permisos_usuario'"
            tablas = db_users.execute_query(query_tabla)
            
            if not tablas:
                logger.warning("Tabla 'permisos_usuario' no existe - usando permisos por rol")
                return self._obtener_permisos_por_rol(user_id, db_users)
            
            # Obtener permisos desde la tabla real
            query = "SELECT modulo FROM permisos_usuario WHERE usuario_id = ?"
            permisos_result = db_users.execute_query(query, (user_id,))
            
            permisos = [row[0] for row in permisos_result]
            
            if not permisos:
                # Si no tiene permisos específicos, usar permisos por rol
                permisos = self._obtener_permisos_por_rol(user_id, db_users)
            
            logger.debug(f"Usuario ID {user_id} tiene permisos para: {permisos}")
            return permisos
            
        except Exception as e:
            logger.error(f"Error obteniendo permisos del usuario desde DB users: {e}")
            return []
    
    def _obtener_permisos_por_rol(self, user_id: int, db_users) -> List[str]:
        """
        Obtiene permisos basados en el rol del usuario si no hay tabla de permisos específica.
        
        Args:
            user_id: ID del usuario
            db_users: Conexión a la base de datos users
            
        Returns:
            Lista de módulos basada en el rol
        """
        try:
            query = "SELECT rol FROM usuarios WHERE id = ?"
            rol_result = db_users.execute_query(query, (user_id,))
            
            if not rol_result:
                return []
                
            rol = rol_result[0][0]
            
            # Definir permisos por rol
            permisos_por_rol = {
                'ADMINISTRADOR': [
                    'administracion', 'inventario', 'compras', 'obras', 
                    'pedidos', 'vidrios', 'herrajes', 'logistica', 
                    'usuarios', 'configuracion', 'auditoria', 'notificaciones', 'mantenimiento'
                ],
                'SUPERVISOR': [
                    'inventario', 'compras', 'obras', 'pedidos', 'vidrios', 
                    'herrajes', 'logistica', 'notificaciones'
                ],
                'USUARIO': [
                    'inventario', 'pedidos', 'vidrios'
                ],
                'VENDEDOR': [
                    'pedidos', 'vidrios', 'herrajes'
                ]
            }
            
            permisos = permisos_por_rol.get(rol, ['inventario'])  # Mínimo inventario por defecto
            logger.info(f"Asignados permisos por rol '{rol}': {permisos}")
            return permisos
            
        except Exception as e:
            logger.error(f"Error obteniendo permisos por rol: {e}")
            return ['inventario']  # Permiso mínimo por defecto
        
    def buscar_usuarios_filtrado(self, filtros: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Busca usuarios aplicando filtros."""
        try:
            if not self.db_connection:
                logger.warning("No hay conexión a base de datos disponible")
                return []
            
            # Preparar parámetros para la consulta
            params = {
                'busqueda': filtros.get('busqueda') if filtros.get('busqueda') else None,
                'rol': filtros.get('rol') if filtros.get('rol') and filtros['rol'] != 'Todos' else None,
                'estado': filtros.get('estado') if filtros.get('estado') and filtros['estado'] != 'Todos' else None
            }
            
            # Ejecutar consulta usando SQL Manager
            if self.sql_manager:
                usuarios = self.sql_manager.ejecutar_consulta_archivo(
                    'usuarios/buscar_usuarios_filtrado.sql',
                    params
                )
            else:
                # Fallback básico
                usuarios = []
            
            # Convertir a lista de diccionarios si es necesario
            if usuarios and not isinstance(usuarios[0], dict):
                # Convertir tuplas a diccionarios
                columns = ['id', 'username', 'email', 'nombre_completo', 'departamento', 
                          'cargo', 'telefono', 'activo', 'fecha_creacion', 'ultimo_acceso', 'rol', 'estado']
                usuarios = [dict(zip(columns, row)) for row in usuarios]
            
            # Sanitizar datos de salida si está disponible
            if self.data_sanitizer and usuarios:
                usuarios = [self.data_sanitizer.sanitize_dict(usuario) for usuario in usuarios]
            
            logger.info(f"Filtrados {len(usuarios) if usuarios else 0} usuarios exitosamente")
            return usuarios or []
            
        except Exception as e:
            logger.error(f"Error filtrando usuarios: {e}")
            return []
