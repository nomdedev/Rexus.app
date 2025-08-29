"""
Submódulo de Autenticación - Sistema de Usuarios Rexus.app

Gestiona procesos de autenticación, validación de credenciales,
bloqueo de cuentas y control de acceso.
"""

import datetime
import hashlib
import logging
from typing import Dict, Any, Optional
from rexus.utils.security import sanitize_string

logger = logging.getLogger(__name__)


class AutenticacionManager:
    """Gestor de autenticación de usuarios."""
    
    def __init__(self, db_connection=None, sql_manager=None):
        """Inicializar manager de autenticación."""
        self.db_connection = db_connection
        self.sql_manager = sql_manager
        self.sql_path = "sql/09_usuarios"
        self.max_intentos = 3
        self.tiempo_bloqueo_minutos = 30
    
    def autenticar_usuario(self, username: str, password: str) -> Dict[str, Any]:
        """Autenticar usuario con credenciales."""
        if not self.db_connection:
            return {"success": False, "error": "Sin conexión a base de datos"}
        
        try:
            username_safe = sanitize_string(username)
            
            # Verificar si la cuenta está bloqueada
            if self.verificar_cuenta_bloqueada(username_safe):
                return {
                    "success": False,
                    "error": "Cuenta bloqueada por múltiples intentos fallidos",
                }
            
            cursor = self.db_connection.cursor()
            
            # Obtener datos del usuario
            query = self.sql_manager.get_query(
                self.sql_path, "obtener_usuario_autenticacion"
            )
            cursor.execute(query, (username_safe,))
            
            usuario = cursor.fetchone()
            if not usuario:
                self._registrar_intento_fallido(username_safe)
                return {"success": False, "error": "Credenciales inválidas"}
            
            # Verificar contraseña
            password_hash = self._hash_password(password)
            if usuario['password_hash'] != password_hash:
                self._registrar_intento_fallido(username_safe)
                return {"success": False, "error": "Credenciales inválidas"}
            
            # Verificar estado del usuario
            if usuario['estado'] != 'ACTIVO':
                return {"success": False, "error": "Usuario inactivo"}
            
            # Limpiar intentos fallidos y actualizar último acceso
            self._limpiar_intentos_fallidos(usuario['id'])
            self._actualizar_ultimo_acceso(usuario['id'])
            
            return {
                "success": True,
                "user_id": usuario['id'],
                "username": usuario['username'],
                "nombre": usuario['nombre'],
                "rol": usuario['rol'],
                "permisos": self._obtener_permisos_usuario(usuario['id'])
            }
            
        except Exception as e:
            logger.error(f"Error en autenticación: {e}")
            return {"success": False, "error": "Error interno del sistema"}
    
    def verificar_cuenta_bloqueada(self, username: str) -> bool:
        """Verificar si una cuenta está bloqueada."""
        if not self.db_connection:
            return False
        
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM intentos_login 
                WHERE username = ? 
                AND exitoso = 0 
                AND fecha_intento > DATEADD(MINUTE, -?, GETDATE())
            """, (username, self.tiempo_bloqueo_minutos))
            
            intentos_recientes = cursor.fetchone()[0]
            return intentos_recientes >= self.max_intentos
            
        except Exception as e:
            logger.error(f"Error verificando bloqueo de cuenta: {e}")
            return False
    
    def _registrar_intento_fallido(self, username: str) -> None:
        """Registrar intento de login fallido."""
        if not self.db_connection:
            return
        
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                INSERT INTO intentos_login (username, exitoso, fecha_intento)
                VALUES (?, 0, GETDATE())
            """, (username,))
            self.db_connection.commit()
            
        except Exception as e:
            logger.error(f"Error registrando intento fallido: {e}")
    
    def _limpiar_intentos_fallidos(self, user_id: int) -> None:
        """Limpiar intentos fallidos después de login exitoso."""
        if not self.db_connection:
            return
        
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                DELETE FROM intentos_login 
                WHERE username = (SELECT username FROM usuarios WHERE id = ?)
            """, (user_id,))
            self.db_connection.commit()
            
        except Exception as e:
            logger.error(f"Error limpiando intentos fallidos: {e}")
    
    def _actualizar_ultimo_acceso(self, user_id: int) -> None:
        """Actualizar timestamp de último acceso."""
        if not self.db_connection:
            return
        
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                UPDATE usuarios 
                SET ultimo_acceso = GETDATE() 
                WHERE id = ?
            """, (user_id,))
            self.db_connection.commit()
            
        except Exception as e:
            logger.error(f"Error actualizando último acceso: {e}")
    
    def _hash_password(self, password: str) -> str:
        """Generar hash de contraseña."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _obtener_permisos_usuario(self, user_id: int) -> list:
        """Obtener permisos del usuario."""
        if not self.db_connection:
            return []
        
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                SELECT p.nombre 
                FROM permisos p
                JOIN usuario_permisos up ON p.id = up.permiso_id
                WHERE up.usuario_id = ?
            """, (user_id,))
            
            return [row[0] for row in cursor.fetchall()]
            
        except Exception as e:
            logger.error(f"Error obteniendo permisos: {e}")
            return []