"""
Sistema de Autenticación Simple - Rexus.app v2.0.0

Sistema básico de autenticación que funciona con la estructura actual
"""

import hashlib
import os
from datetime import datetime
from typing import Optional, Dict, Any

class AuthManager:
    """Gestor de autenticación simple y funcional"""
    
    def __init__(self, db_connection=None):
        self.db_connection = db_connection
        self.current_user = None
        self.current_role = None
        self.session_active = False
        
        # La conexión se creará cuando sea necesaria


# Variable global para mantener el usuario actual (singleton)
_current_user = None
_auth_manager_instance = None


def get_current_user() -> Optional[Dict[str, Any]]:
    """
    Obtiene el usuario actualmente autenticado.
    
    Returns:
        Dict con información del usuario o None si no está autenticado
    """
    global _current_user
    if _current_user:
        return _current_user
    
    # Intentar obtener del auth manager
    global _auth_manager_instance
    if _auth_manager_instance and _auth_manager_instance.current_user:
        _current_user = _auth_manager_instance.current_user
        return _current_user
    
    return None


def set_current_user(user_data: Dict[str, Any]):
    """
    Establece el usuario actual después de la autenticación.
    
    Args:
        user_data: Información del usuario autenticado
    """
    global _current_user
    _current_user = user_data


def clear_current_user():
    """Limpia el usuario actual (logout)."""
    global _current_user
    _current_user = None


    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Autentica un usuario con username y password
        
        Args:
            username: Nombre de usuario
            password: Contraseña
            
        Returns:
            Dict con información del usuario si es válido, None si no
        """
        # Crear conexión solo cuando se necesite autenticar
        if not self.db_connection:
            try:
                from rexus.core.database import UsersDatabaseConnection
                self.db_connection = UsersDatabaseConnection(auto_connect=True)
            except Exception as e:
                print(f"Error conectando a la base de datos para autenticación: {e}")
                return None
        
        try:
            # Buscar usuario por nombre de usuario
            user_data = self.db_connection.execute_query("""
                SELECT id, usuario, password_hash, rol, estado, nombre, apellido, email
                FROM usuarios 
                WHERE usuario = ? AND estado = 'Activo'
            """, (username,))
            
            if not user_data:
                return None
            
            user_data = user_data[0]  # Obtener primera fila
            
            # Verificar password usando sistema seguro
            # Verificar contraseña con sistema seguro
            from rexus.utils.password_security import verify_password_secure
            is_password_valid = verify_password_secure(password, user_data[2])
            
            if is_password_valid:
                # Autenticación exitosa
                nombre = user_data[5] or ''
                apellido = user_data[6] or ''
                nombre_completo = f"{nombre} {apellido}".strip()
                
                user_info = {
                    'id': user_data[0],
                    'username': user_data[1],
                    'role': user_data[3],
                    'status': user_data[4],
                    'nombre': nombre,
                    'apellido': apellido,
                    'nombre_completo': nombre_completo,
                    'email': user_data[7] or ''
                }
                
                # Actualizar último login
                self.db_connection.execute_non_query("""
                    UPDATE usuarios 
                    SET ultimo_login = GETDATE() 
                    WHERE id = ?
                """, (user_data[0],))
                
                # Establecer sesión
                self.current_user = user_info
                self.current_role = user_info['role']
                self.session_active = True
                
                return user_info
            
            return None
            
        except Exception as e:
            print(f"Error en autenticación: {e}")
            return None
    
    def logout(self):
        """Cierra la sesión actual"""
        self.current_user = None
        self.current_role = None
        self.session_active = False
    
    def is_authenticated(self) -> bool:
        """Verifica si hay una sesión activa"""
        return self.session_active and self.current_user is not None
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """Retorna el usuario actual"""
        return self.current_user
    
    def get_current_role(self) -> Optional[str]:
        """Retorna el rol del usuario actual"""
        return self.current_role
    
    def has_permission(self, module: str, action: str = 'read') -> bool:
        """
        Verifica si el usuario actual tiene permiso para un módulo/acción
        
        Args:
            module: Nombre del módulo
            action: Acción (read, write, delete, admin)
            
        Returns:
            True si tiene permiso, False si no
        """
        if not self.is_authenticated():
            return False
        
        # Administradores tienen todos los permisos
        if self.current_role == 'admin':
            return True
        
        # Supervisores tienen permisos de lectura/escritura
        if self.current_role == 'supervisor':
            return action in ['read', 'write']
        
        # Usuarios tienen solo lectura
        if self.current_role == 'usuario':
            return action == 'read'
        
        return False
    
    def create_user(self, username: str, password: str, role: str = 'usuario', 
                   nombre: str = '', apellido: str = '', email: str = '') -> bool:
        """
        Crea un nuevo usuario
        
        Args:
            username: Nombre de usuario único
            password: Contraseña
            role: Rol del usuario (admin, supervisor, usuario)
            nombre: Nombre completo
            apellido: Apellido
            email: Email
            
        Returns:
            True si se creó exitosamente, False si no
        """
        # Crear conexión si no existe
        if not self.db_connection:
            try:
                from rexus.core.database import UsersDatabaseConnection
                self.db_connection = UsersDatabaseConnection(auto_connect=True)
            except Exception as e:
                print(f"Error conectando a la base de datos: {e}")
                return False
        
        try:
            # Verificar que el usuario no exista
            existing_user = self.db_connection.execute_query("SELECT id FROM usuarios WHERE usuario = ?", (username,))
            if existing_user:
                return False
            
            # Crear hash seguro de contraseña
            # Usar sistema de hashing seguro
            from rexus.utils.password_security import hash_password_secure
            password_hash = hash_password_secure(password)
            
            # Insertar usuario
            result = self.db_connection.execute_non_query("""
                INSERT INTO usuarios (usuario, password_hash, rol, nombre, apellido, email, estado)
                VALUES (?, ?, ?, ?, ?, ?, 'Activo')
            """, (username, password_hash, role, nombre, apellido, email))
            
            return result
            
        except Exception as e:
            print(f"Error creando usuario: {e}")
            return False
    
    def change_password(self, user_id: int, new_password: str) -> bool:
        """
        Cambia la contraseña de un usuario
        
        Args:
            user_id: ID del usuario
            new_password: Nueva contraseña
            
        Returns:
            True si se cambió exitosamente, False si no
        """
        if not self.db_connection:
            return False
        
        try:
            # Crear hash seguro de nueva contraseña
            # Usar sistema de hashing seguro
            from rexus.utils.password_security import hash_password_secure
            password_hash = hash_password_secure(new_password)
            
            # Actualizar contraseña
            result = self.db_connection.execute_non_query("""
                UPDATE usuarios 
                SET password_hash = ? 
                WHERE id = ?
            """, (password_hash, user_id))
            
            return result
            
        except Exception as e:
            print(f"Error cambiando contraseña: {e}")
            return False
    
    def get_all_users(self) -> list:
        """
        Obtiene todos los usuarios
        
        Returns:
            Lista de diccionarios con información de usuarios
        """
        if not self.db_connection:
            return []
        
        try:
            user_data = self.db_connection.execute_query("""
                SELECT id, usuario, rol, nombre, apellido, email, estado, ultimo_login
                FROM usuarios
                ORDER BY usuario
            """)
            
            users = []
            for row in user_data:
                users.append({
                    'id': row[0],
                    'username': row[1],
                    'role': row[2],
                    'nombre': row[3],
                    'apellido': row[4],
                    'email': row[5],
                    'status': row[6],
                    'ultimo_login': row[7]
                })
            
            return users
            
        except Exception as e:
            print(f"Error obteniendo usuarios: {e}")
            return []
    
    def update_user(self, user_id: int, username: str = None, role: str = None,
                   nombre: str = None, apellido: str = None, email: str = None,
                   status: str = None) -> bool:
        """
        Actualiza información de un usuario
        
        Args:
            user_id: ID del usuario
            username: Nuevo nombre de usuario (opcional)
            role: Nuevo rol (opcional)
            nombre: Nuevo nombre (opcional)
            apellido: Nuevo apellido (opcional)
            email: Nuevo email (opcional)
            status: Nuevo estado (opcional)
            
        Returns:
            True si se actualizó exitosamente, False si no
        """
        if not self.db_connection:
            return False
        
        try:
            # Construir query dinámico
            updates = []
            params = []
            
            if username:
                updates.append("usuario = ?")
                params.append(username)
            if role:
                updates.append("rol = ?")
                params.append(role)
            if nombre:
                updates.append("nombre = ?")
                params.append(nombre)
            if apellido:
                updates.append("apellido = ?")
                params.append(apellido)
            if email:
                updates.append("email = ?")
                params.append(email)
            if status:
                updates.append("estado = ?")
                params.append(status)
            
            if not updates:
                return False
            
            params.append(user_id)
            
            # SEGURIDAD: Usar queries predefinidas para evitar construcción dinámica
            if not updates:
                return False
            
            # Mapear campos permitidos a queries seguras predefinidas
            allowed_fields = {
                'nombre': 'UPDATE usuarios SET nombre = ? WHERE id = ?',
                'apellido': 'UPDATE usuarios SET apellido = ? WHERE id = ?', 
                'email': 'UPDATE usuarios SET email = ? WHERE id = ?',
                'estado': 'UPDATE usuarios SET estado = ? WHERE id = ?'
            }
            
            # Procesar cada update de forma segura
            success = True
            for update in updates:
                field_name = update.split(' = ?')[0].strip()
                if field_name in allowed_fields and field_name in [u.split(' = ?')[0].strip() for u in updates]:
                    # Encontrar el valor correspondiente 
                    field_index = [u.split(' = ?')[0].strip() for u in updates].index(field_name)
                    field_value = params[field_index]
                    query = allowed_fields[field_name]
                    result = self.db_connection.execute_non_query(query, (field_value, params[-1]))
                    if not result:
                        success = False
                        break
            
            result = success
            
            return result
            
        except Exception as e:
            print(f"Error actualizando usuario: {e}")
            return False

# Instancia global del gestor de autenticación
_auth_manager = None

def get_auth_manager():
    """Obtiene la instancia global del gestor de autenticación"""
    global _auth_manager
    if _auth_manager is None:
        _auth_manager = AuthManager()
    return _auth_manager

def reset_auth_manager():
    """Reinicia el gestor de autenticación"""
    global _auth_manager
    _auth_manager = None