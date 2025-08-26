"""
AuthManager - Sistema de autorización para Rexus.app
Controla permisos y acceso a funcionalidades
"""

import logging
import hashlib
import secrets
from typing import Optional, Dict, Any, List
from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timedelta

# Sistema de logging
try:
    from ..utils.app_logger import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class UserRole(Enum):
    """Roles de usuario del sistema."""
    SUPER_ADMIN = "SUPER_ADMIN"
    ADMIN = "ADMIN"
    MANAGER = "MANAGER"
    USER = "USER"
    VIEWER = "VIEWER"


class SessionStatus(Enum):
    """Estados de sesión."""
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    TERMINATED = "TERMINATED"
    LOCKED = "LOCKED"


@dataclass
class UserSession:
    """Información de sesión de usuario."""
    session_id: str
    user_id: int
    username: str
    role: UserRole
    login_time: datetime
    last_activity: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    status: SessionStatus = SessionStatus.ACTIVE


@dataclass
class AuthResult:
    """Resultado de autenticación."""
    success: bool
    user_id: Optional[int] = None
    username: Optional[str] = None
    role: Optional[UserRole] = None
    session_id: Optional[str] = None
    message: str = ""
    error_code: Optional[str] = None


class AuthManager:
    """Gestor de autenticación y autorización."""
    
    def __init__(self, db_connection=None):
        """Inicializa el gestor de autenticación."""
        self.db_connection = db_connection
        self.active_sessions: Dict[str, UserSession] = {}
        self.session_timeout = timedelta(hours=8)  # 8 horas por defecto
        self.max_failed_attempts = 5
        self.lockout_duration = timedelta(minutes=30)
        self.failed_attempts: Dict[str, List[datetime]] = {}
        
        # Inicializar tablas si es necesario
        self._initialize_auth_tables()
    
    def _initialize_auth_tables(self):
        """Crea las tablas de autenticación si no existen."""
        if not self.db_connection:
            return
        
        try:
            cursor = self.db_connection.connection.cursor()
            
            # Tabla de usuarios con autenticación
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS auth_users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    role TEXT NOT NULL DEFAULT 'USER',
                    is_active BOOLEAN DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_login DATETIME,
                    failed_attempts INTEGER DEFAULT 0,
                    locked_until DATETIME
                )
            """)
            
            # Tabla de sesiones activas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS auth_sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_activity DATETIME DEFAULT CURRENT_TIMESTAMP,
                    ip_address TEXT,
                    user_agent TEXT,
                    status TEXT DEFAULT 'ACTIVE',
                    FOREIGN KEY (user_id) REFERENCES auth_users (id)
                )
            """)
            
            self.db_connection.connection.commit()
            logger.info("Tablas de autenticación inicializadas")
            
        except Exception as e:
            logger.error(f"Error inicializando tablas de autenticación: {e}")
    
    def hash_password(self, password: str, salt: str = None) -> tuple:
        """
        Genera hash seguro de contraseña.
        
        Args:
            password: Contraseña en texto plano
            salt: Salt opcional (se genera si no se proporciona)
            
        Returns:
            Tupla (password_hash, salt)
        """
        if not salt:
            salt = secrets.token_hex(32)
        
        # Usar PBKDF2 con SHA-256
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # 100,000 iteraciones
        )
        
        return password_hash.hex(), salt
    
    def verify_password(self, password: str, stored_hash: str, salt: str) -> bool:
        """
        Verifica contraseña contra hash almacenado.
        
        Args:
            password: Contraseña a verificar
            stored_hash: Hash almacenado
            salt: Salt utilizado
            
        Returns:
            True si la contraseña es correcta
        """
        try:
            calculated_hash, _ = self.hash_password(password, salt)
            return calculated_hash == stored_hash
        except Exception as e:
            logger.error(f"Error verificando contraseña: {e}")
            return False
    
    def authenticate_user(self, username: str, password: str, 
                         ip_address: str = None, user_agent: str = None) -> AuthResult:
        """
        Autentica un usuario con credenciales.
        
        Args:
            username: Nombre de usuario
            password: Contraseña
            ip_address: Dirección IP del cliente
            user_agent: User agent del cliente
            
        Returns:
            Resultado de autenticación
        """
        try:
            # Verificar si el usuario está bloqueado
            if self._is_user_locked(username):
                return AuthResult(
                    success=False,
                    message="Usuario temporalmente bloqueado",
                    error_code="USER_LOCKED"
                )
            
            # Obtener usuario de la base de datos
            user_data = self._get_user_by_username(username)
            if not user_data:
                self._record_failed_attempt(username, ip_address)
                return AuthResult(
                    success=False,
                    message="Credenciales inválidas",
                    error_code="INVALID_CREDENTIALS"
                )
            
            # Verificar contraseña
            if not self.verify_password(password, user_data['password_hash'], user_data['salt']):
                self._record_failed_attempt(username, ip_address)
                return AuthResult(
                    success=False,
                    message="Credenciales inválidas",
                    error_code="INVALID_CREDENTIALS"
                )
            
            # Verificar si el usuario está activo
            if not user_data.get('is_active', True):
                return AuthResult(
                    success=False,
                    message="Usuario desactivado",
                    error_code="USER_DISABLED"
                )
            
            # Crear sesión
            session = self._create_session(
                user_id=user_data['id'],
                username=username,
                role=UserRole(user_data['role']),
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            # Limpiar intentos fallidos
            self._clear_failed_attempts(username)
            
            # Actualizar último login
            self._update_last_login(user_data['id'])
            
            logger.info(f"Usuario {username} autenticado exitosamente desde {ip_address}")
            
            return AuthResult(
                success=True,
                user_id=user_data['id'],
                username=username,
                role=UserRole(user_data['role']),
                session_id=session.session_id,
                message="Autenticación exitosa"
            )
            
        except Exception as e:
            logger.exception(f"Error en autenticación: {e}")
            return AuthResult(
                success=False,
                message="Error interno del sistema",
                error_code="INTERNAL_ERROR"
            )
    
    def _create_session(self, user_id: int, username: str, role: UserRole,
                       ip_address: str = None, user_agent: str = None) -> UserSession:
        """Crea una nueva sesión de usuario."""
        session_id = secrets.token_urlsafe(32)
        now = datetime.now()
        
        session = UserSession(
            session_id=session_id,
            user_id=user_id,
            username=username,
            role=role,
            login_time=now,
            last_activity=now,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        # Almacenar en memoria
        self.active_sessions[session_id] = session
        
        # Persistir en base de datos
        if self.db_connection:
            try:
                cursor = self.db_connection.connection.cursor()
                cursor.execute("""
                    INSERT INTO auth_sessions 
                    (session_id, user_id, ip_address, user_agent)
                    VALUES (?, ?, ?, ?)
                """, (session_id, user_id, ip_address, user_agent))
                self.db_connection.connection.commit()
            except Exception as e:
                logger.error(f"Error persistiendo sesión: {e}")
        
        return session
    
    def validate_session(self, session_id: str) -> Optional[UserSession]:
        """
        Valida y actualiza una sesión existente.
        
        Args:
            session_id: ID de sesión
            
        Returns:
            Sesión si es válida, None en caso contrario
        """
        try:
            session = self.active_sessions.get(session_id)
            if not session:
                return None
            
            # Verificar expiración
            if datetime.now() - session.last_activity > self.session_timeout:
                self._terminate_session(session_id, "EXPIRED")
                return None
            
            # Actualizar actividad
            session.last_activity = datetime.now()
            
            # Actualizar en base de datos
            if self.db_connection:
                try:
                    cursor = self.db_connection.connection.cursor()
                    cursor.execute("""
                        UPDATE auth_sessions 
                        SET last_activity = CURRENT_TIMESTAMP
                        WHERE session_id = ?
                    """, (session_id,))
                    self.db_connection.connection.commit()
                except Exception as e:
                    logger.error(f"Error actualizando sesión: {e}")
            
            return session
            
        except Exception as e:
            logger.error(f"Error validando sesión: {e}")
            return None
    
    def logout_user(self, session_id: str) -> bool:
        """
        Cierra la sesión de un usuario.
        
        Args:
            session_id: ID de sesión
            
        Returns:
            True si se cerró exitosamente
        """
        try:
            session = self.active_sessions.get(session_id)
            if session:
                logger.info(f"Usuario {session.username} cerró sesión")
                self._terminate_session(session_id, "TERMINATED")
                return True
            return False
        except Exception as e:
            logger.error(f"Error cerrando sesión: {e}")
            return False
    
    def _terminate_session(self, session_id: str, reason: str):
        """Termina una sesión."""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
        
        if self.db_connection:
            try:
                cursor = self.db_connection.connection.cursor()
                cursor.execute("""
                    UPDATE auth_sessions 
                    SET status = ? 
                    WHERE session_id = ?
                """, (reason, session_id))
                self.db_connection.connection.commit()
            except Exception as e:
                logger.error(f"Error terminando sesión en BD: {e}")
    
    def _is_user_locked(self, username: str) -> bool:
        """Verifica si un usuario está temporalmente bloqueado."""
        if not self.db_connection:
            return False
        
        try:
            cursor = self.db_connection.connection.cursor()
            cursor.execute("""
                SELECT locked_until FROM auth_users 
                WHERE username = ? AND locked_until > CURRENT_TIMESTAMP
            """, (username,))
            
            return cursor.fetchone() is not None
            
        except Exception as e:
            logger.error(f"Error verificando bloqueo: {e}")
            return False
    
    def _record_failed_attempt(self, username: str, ip_address: str = None):
        """Registra un intento de login fallido."""
        if not self.db_connection:
            return
        
        try:
            cursor = self.db_connection.connection.cursor()
            
            # Incrementar contador de intentos fallidos
            cursor.execute("""
                UPDATE auth_users 
                SET failed_attempts = failed_attempts + 1
                WHERE username = ?
            """, (username,))
            
            # Verificar si debe bloquearse
            cursor.execute("""
                SELECT failed_attempts FROM auth_users WHERE username = ?
            """, (username,))
            
            result = cursor.fetchone()
            if result and result[0] >= self.max_failed_attempts:
                # Bloquear usuario
                lockout_until = datetime.now() + self.lockout_duration
                cursor.execute("""
                    UPDATE auth_users 
                    SET locked_until = ?
                    WHERE username = ?
                """, (lockout_until, username))
                
                logger.warning(f"Usuario {username} bloqueado hasta {lockout_until}")
            
            self.db_connection.connection.commit()
            
        except Exception as e:
            logger.error(f"Error registrando intento fallido: {e}")
    
    def _clear_failed_attempts(self, username: str):
        """Limpia los intentos fallidos de un usuario."""
        if not self.db_connection:
            return
        
        try:
            cursor = self.db_connection.connection.cursor()
            cursor.execute("""
                UPDATE auth_users 
                SET failed_attempts = 0, locked_until = NULL
                WHERE username = ?
            """, (username,))
            self.db_connection.connection.commit()
        except Exception as e:
            logger.error(f"Error limpiando intentos fallidos: {e}")
    
    def _get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Obtiene datos de usuario por nombre de usuario."""
        if not self.db_connection:
            return None
        
        try:
            cursor = self.db_connection.connection.cursor()
            cursor.execute("""
                SELECT id, username, password_hash, salt, role, is_active
                FROM auth_users 
                WHERE username = ? AND is_active = 1
            """, (username,))
            
            row = cursor.fetchone()
            if row:
                columns = [desc[0] for desc in cursor.description]
                return dict(zip(columns, row))
            
            return None
            
        except Exception as e:
            logger.error(f"Error obteniendo usuario: {e}")
            return None
    
    def _update_last_login(self, user_id: int):
        """Actualiza el timestamp del último login."""
        if not self.db_connection:
            return
        
        try:
            cursor = self.db_connection.connection.cursor()
            cursor.execute("""
                UPDATE auth_users 
                SET last_login = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (user_id,))
            self.db_connection.connection.commit()
        except Exception as e:
            logger.error(f"Error actualizando último login: {e}")


# Instancia global del gestor de autenticación
_auth_manager: Optional[AuthManager] = None


def init_auth_manager(db_connection=None) -> AuthManager:
    """Inicializa el gestor global de autenticación."""
    global _auth_manager
    _auth_manager = AuthManager(db_connection)
    return _auth_manager


def get_auth_manager() -> Optional[AuthManager]:
    """Obtiene la instancia global del gestor de autenticación."""
    return _auth_manager


def get_current_session() -> Optional[UserSession]:
    """Obtiene la sesión actual del usuario."""
    # En una implementación real, esto obtendría de variables globales o contexto
    # Por ahora retorna None para evitar errores
    return None


def require_role(required_role: UserRole):
    """Decorador que requiere un rol específico."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            session = get_current_session()
            if not session or session.role.value < required_role.value:
                raise PermissionError(f"Se requiere rol {required_role.value}")
            return func(*args, **kwargs)
        return wrapper
    return decorator


def require_login(func):
    """Decorador que requiere cualquier usuario autenticado."""
    return require_role(UserRole.VIEWER)(func)