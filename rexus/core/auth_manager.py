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

# Importar SQLQueryManager
try:
    from ..utils.sql_query_manager import SQLQueryManager
except ImportError:
    logger.error("SQLQueryManager es requerido para AuthManager")
    raise ImportError("SQLQueryManager no disponible - es requerido para AuthManager")


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
        
        # Inicializar SQLQueryManager
        self.sql_manager = SQLQueryManager()
        
        # Inicializar tablas si es necesario
        self._initialize_auth_tables()
    
    def _initialize_auth_tables(self):
        """Crea las tablas de autenticación si no existen."""
        if not self.db_connection:
            return
        
        try:
            # Las tablas auth_users y auth_sessions ya existen en SQL Server
            logger.info("Tablas de autenticación verificadas")
            
        except Exception as e:
            logger.error(f"Error inicializando tablas de autenticación: {e}")
    
    def hash_password(self, password: str, salt: Optional[str] = None) -> tuple:
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
                         ip_address: Optional[str] = None, user_agent: Optional[str] = None) -> AuthResult:
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
                self._record_failed_attempt(username)
                return AuthResult(
                    success=False,
                    message="Credenciales inválidas",
                    error_code="INVALID_CREDENTIALS"
                )
            
            # Verificar contraseña
            if not self.verify_password(password, user_data['password_hash'], user_data['salt']):
                self._record_failed_attempt(username)
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
                       ip_address: Optional[str] = None, user_agent: Optional[str] = None) -> UserSession:
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
            ip_address=ip_address or 'unknown',
            user_agent=user_agent or 'unknown'
        )
        
        # Almacenar en memoria
        self.active_sessions[session_id] = session
        
        # Persistir en base de datos
        if self.db_connection and self.sql_manager:
            try:
                cursor = self.db_connection.connection.cursor()
                sql_insert_session = self.sql_manager.get_query('auth', 'insert_session')
                cursor.execute(sql_insert_session, (session_id, user_id, username, ip_address, user_agent))
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
            if self.db_connection and self.sql_manager:
                try:
                    cursor = self.db_connection.connection.cursor()
                    sql_update_activity = self.sql_manager.get_query('auth', 'update_session_activity')
                    cursor.execute(sql_update_activity, (session_id,))
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
        
        if self.db_connection and self.sql_manager:
            try:
                cursor = self.db_connection.connection.cursor()
                sql_terminate_session = self.sql_manager.get_query('auth', 'terminate_session')
                cursor.execute(sql_terminate_session, (reason, reason.upper(), session_id))
                self.db_connection.connection.commit()
            except Exception as e:
                logger.error(f"Error terminando sesión en BD: {e}")
    
    def _is_user_locked(self, username: str) -> bool:
        """Verifica si un usuario está temporalmente bloqueado."""
        if not self.db_connection or not self.sql_manager:
            return False
        
        try:
            cursor = self.db_connection.connection.cursor()
            sql_check_locked = self.sql_manager.get_query('auth', 'check_user_locked')
            cursor.execute(sql_check_locked, (username,))
            
            return cursor.fetchone() is not None
            
        except Exception as e:
            logger.error(f"Error verificando bloqueo: {e}")
            return False
    
    def _record_failed_attempt(self, username: str):
        """Registra un intento de login fallido."""
        if not self.db_connection or not self.sql_manager:
            return
        
        try:
            cursor = self.db_connection.connection.cursor()
            
            # Incrementar contador de intentos fallidos
            sql_increment_failed = self.sql_manager.get_query('auth', 'increment_failed_attempts')
            cursor.execute(sql_increment_failed, (username,))
            
            # Verificar si debe bloquearse
            sql_get_failed = self.sql_manager.get_query('auth', 'get_failed_attempts')
            cursor.execute(sql_get_failed, (username,))
            
            result = cursor.fetchone()
            if result and result[0] >= self.max_failed_attempts:
                # Bloquear usuario
                lockout_until = datetime.now() + self.lockout_duration
                sql_lock_user = self.sql_manager.get_query('auth', 'lock_user')
                cursor.execute(sql_lock_user, (lockout_until, username))
                
                logger.warning(f"Usuario {username} bloqueado hasta {lockout_until}")
            
            self.db_connection.connection.commit()
            
        except Exception as e:
            logger.error(f"Error registrando intento fallido: {e}")
    
    def _clear_failed_attempts(self, username: str):
        """Limpia los intentos fallidos de un usuario."""
        if not self.db_connection or not self.sql_manager:
            return
        
        try:
            cursor = self.db_connection.connection.cursor()
            sql_clear_failed = self.sql_manager.get_query('auth', 'clear_failed_attempts')
            cursor.execute(sql_clear_failed, (username,))
            self.db_connection.connection.commit()
        except Exception as e:
            logger.error(f"Error limpiando intentos fallidos: {e}")
    
    def _get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Obtiene datos de usuario por nombre de usuario."""
        if not self.db_connection or not self.sql_manager:
            return None
        
        try:
            cursor = self.db_connection.connection.cursor()
            sql_get_user = self.sql_manager.get_query('auth', 'get_user_by_username')
            cursor.execute(sql_get_user, (username,))
            
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
        if not self.db_connection or not self.sql_manager:
            return
        
        try:
            cursor = self.db_connection.connection.cursor()
            sql_update_login = self.sql_manager.get_query('auth', 'update_last_login')
            cursor.execute(sql_update_login, (user_id,))
            self.db_connection.connection.commit()
        except Exception as e:
            logger.error(f"Error actualizando último login: {e}")
    
    def get_user_session_history(self, user_id: int) -> List[Dict[str, Any]]:
        """Obtiene el historial de sesiones de un usuario para auditoría."""
        if not self.db_connection or not self.sql_manager:
            return []
        
        try:
            cursor = self.db_connection.connection.cursor()
            sql_get_history = self.sql_manager.get_query('auth', 'get_user_session_history')
            cursor.execute(sql_get_history, (user_id,))
            
            sessions = []
            for row in cursor.fetchall():
                sessions.append({
                    'session_id': row[0],
                    'usuario': row[1],
                    'ip_address': row[2],
                    'user_agent': row[3],
                    'login_time': row[4],
                    'logout_time': row[5],
                    'status': row[6],
                    'logout_reason': row[7]
                })
            
            return sessions
            
        except Exception as e:
            logger.error(f"Error obteniendo historial de sesiones: {e}")
            return []
    
    def get_active_sessions(self) -> List[Dict[str, Any]]:
        """Obtiene todas las sesiones activas para monitoreo."""
        if not self.db_connection or not self.sql_manager:
            return []
        
        try:
            cursor = self.db_connection.connection.cursor()
            sql_get_active = self.sql_manager.get_query('auth', 'get_active_sessions')
            cursor.execute(sql_get_active)
            
            sessions = []
            for row in cursor.fetchall():
                sessions.append({
                    'session_id': row[0],
                    'usuario': row[1],
                    'ip_address': row[2],
                    'login_time': row[3],
                    'last_activity': row[4],
                    'rol': row[5],
                    'nombre': row[6],
                    'apellido': row[7]
                })
            
            return sessions
            
        except Exception as e:
            logger.error(f"Error obteniendo sesiones activas: {e}")
            return []
    
    def cleanup_expired_sessions(self, timeout_hours: int = 8) -> int:
        """Limpia sesiones expiradas. Retorna número de sesiones limpiadas."""
        if not self.db_connection or not self.sql_manager:
            return 0
        
        try:
            cursor = self.db_connection.connection.cursor()
            sql_cleanup = self.sql_manager.get_query('auth', 'cleanup_expired_sessions')
            cursor.execute(sql_cleanup, (timeout_hours,))
            
            cleaned_count = cursor.rowcount
            self.db_connection.connection.commit()
            
            if cleaned_count > 0:
                logger.info(f"Limpiadas {cleaned_count} sesiones expiradas")
            
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Error limpiando sesiones expiradas: {e}")
            return 0


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
    auth_manager = get_auth_manager()
    if auth_manager and hasattr(auth_manager, 'active_sessions') and auth_manager.active_sessions:
        # Retorna la primera sesión activa (simplificado)
        for session in auth_manager.active_sessions.values():
            if session and session.login_time:
                return session
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