"""
Security Manager - Gestión de Seguridad Centralizada para Rexus.app v2.0.0

Este módulo proporciona funcionalidades de seguridad centralizadas:
- Validación y sanitización de datos
- Detección de patrones maliciosos
- Control de acceso y autorización
- Audit trail de eventos de seguridad
- Prevención de ataques comunes (XSS, SQL injection, CSRF)

Fecha: 24/08/2025
Objetivo: Sistema robusto de seguridad para prevención de ataques
"""

import re
import hashlib
import secrets
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Set

# Importar logging
try:
    from ..utils.app_logger import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class SecurityManager:
    """Gestor centralizado de seguridad para Rexus.app."""
    
    def __init__(self):
        """Inicializa el gestor de seguridad."""
        self.blocked_ips: Set[str] = set()
        self.failed_attempts: Dict[str, List[datetime]] = {}
        self.csrf_tokens: Dict[str, str] = {}
        self.session_tokens: Dict[str, Dict[str, Any]] = {}
        
        # Patrones maliciosos para detección
        self.malicious_patterns = [
            r'<script[^>]*>.*?</script>',  # XSS básico
            r'javascript:',  # JavaScript injection
            r'on\w+\s*=',  # Event handlers
            r'union\s+select',  # SQL injection
            r'drop\s+table',  # SQL commands
            r'delete\s+from',  # SQL commands
            r'insert\s+into',  # SQL commands
            r'update\s+.*set',  # SQL commands
            r'exec\s*\(',  # Command injection
            r'eval\s*\(',  # Code injection
            r'\.\./+',  # Directory traversal
            r'\.\.\\+',  # Directory traversal (Windows)
        ]
        
        logger.info("SecurityManager inicializado")
    
    def sanitize_input(self, data: str) -> str:
        """
        Sanitiza datos de entrada para prevenir ataques.
        
        Args:
            data: Datos a sanitizar
            
        Returns:
            Datos sanitizados
        """
        if not isinstance(data, str):
            data = str(data)
        
        # Remover caracteres peligrosos
        sanitized = data.replace('<', '&lt;')
        sanitized = sanitized.replace('>', '&gt;')
        sanitized = sanitized.replace('"', '&quot;')
        sanitized = sanitized.replace("'", '&#x27;')
        sanitized = sanitized.replace('&', '&amp;')
        
        # Remover patrones maliciosos
        for pattern in self.malicious_patterns:
            sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)
        
        return sanitized.strip()
    
    def validate_input_length(self, data: str, max_length: int = 255) -> bool:
        """
        Valida la longitud de entrada.
        
        Args:
            data: Datos a validar
            max_length: Longitud máxima permitida
            
        Returns:
            True si la longitud es válida
        """
        return len(data) <= max_length if data else True
    
    def contains_malicious_patterns(self, text: str) -> bool:
        """
        Verifica si el texto contiene patrones maliciosos.
        
        Args:
            text: Texto a verificar
            
        Returns:
            True si contiene patrones maliciosos
        """
        if not isinstance(text, str):
            return False
        
        for pattern in self.malicious_patterns:
            if re.search(pattern, text, flags=re.IGNORECASE):
                logger.warning(f"Patrón malicioso detectado: {pattern} en texto: {text[:100]}...")
                return True
        
        return False
    
    def generate_csrf_token(self, session_id: str) -> str:
        """
        Genera un token CSRF para una sesión.
        
        Args:
            session_id: ID de la sesión
            
        Returns:
            Token CSRF
        """
        token = secrets.token_urlsafe(32)
        self.csrf_tokens[session_id] = token
        
        logger.debug(f"Token CSRF generado para sesión: {session_id}")
        return token
    
    def validate_csrf_token(self, session_id: str, token: str) -> bool:
        """
        Valida un token CSRF.
        
        Args:
            session_id: ID de la sesión
            token: Token a validar
            
        Returns:
            True si el token es válido
        """
        stored_token = self.csrf_tokens.get(session_id)
        
        if not stored_token:
            logger.warning(f"No se encontró token CSRF para sesión: {session_id}")
            return False
        
        is_valid = secrets.compare_digest(stored_token, token)
        
        if not is_valid:
            logger.warning(f"Token CSRF inválido para sesión: {session_id}")
        
        return is_valid
    
    def hash_password(self, password: str, salt: Optional[str] = None) -> tuple[str, str]:
        """
        Genera hash de contraseña con salt.
        
        Args:
            password: Contraseña a hashear
            salt: Salt opcional (se genera si no se proporciona)
            
        Returns:
            tuple: (hash, salt)
        """
        if salt is None:
            salt = secrets.token_hex(16)
        
        # Usar PBKDF2 con SHA256
        hashed = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # 100,000 iterations
        )
        
        return hashed.hex(), salt
    
    def verify_password(self, password: str, hashed: str, salt: str) -> bool:
        """
        Verifica una contraseña contra su hash.
        
        Args:
            password: Contraseña a verificar
            hashed: Hash almacenado
            salt: Salt utilizado
            
        Returns:
            True si la contraseña es correcta
        """
        try:
            computed_hash, _ = self.hash_password(password, salt)
            return secrets.compare_digest(computed_hash, hashed)
        except Exception as e:
            logger.exception(f"Error verificando contraseña: {e}")
            return False
    
    def is_ip_blocked(self, ip: str) -> bool:
        """
        Verifica si una IP está bloqueada.
        
        Args:
            ip: Dirección IP
            
        Returns:
            True si está bloqueada
        """
        return ip in self.blocked_ips
    
    def block_ip(self, ip: str, reason: str = "Security violation"):
        """
        Bloquea una dirección IP.
        
        Args:
            ip: Dirección IP a bloquear
            reason: Razón del bloqueo
        """
        self.blocked_ips.add(ip)
        logger.warning(f"IP bloqueada: {ip} - Razón: {reason}")
        
        # Auditar el evento
        self.audit_security_event("IP_BLOCKED", {
            'ip_address': ip,
            'reason': reason,
            'timestamp': datetime.now().isoformat()
        })
    
    def unblock_ip(self, ip: str):
        """
        Desbloquea una dirección IP.
        
        Args:
            ip: Dirección IP a desbloquear
        """
        if ip in self.blocked_ips:
            self.blocked_ips.remove(ip)
            logger.info(f"IP desbloqueada: {ip}")
    
    def record_failed_attempt(self, identifier: str) -> int:
        """
        Registra un intento fallido de autenticación.
        
        Args:
            identifier: Identificador (IP, username, etc.)
            
        Returns:
            Número de intentos fallidos
        """
        now = datetime.now()
        
        if identifier not in self.failed_attempts:
            self.failed_attempts[identifier] = []
        
        # Limpiar intentos antiguos (más de 1 hora)
        cutoff = now - timedelta(hours=1)
        self.failed_attempts[identifier] = [
            attempt for attempt in self.failed_attempts[identifier]
            if attempt > cutoff
        ]
        
        # Agregar nuevo intento
        self.failed_attempts[identifier].append(now)
        
        attempt_count = len(self.failed_attempts[identifier])
        
        logger.warning(f"Intento fallido registrado para {identifier}: {attempt_count} intentos en la última hora")
        
        return attempt_count
    
    def log_access_attempt(self, user_id=None, username=None, ip_address=None, 
                          success=True, action="login", details=None):
        """
        Registra un intento de acceso al sistema.
        
        Args:
            user_id: ID del usuario
            username: Nombre de usuario
            ip_address: Dirección IP
            success: Si el intento fue exitoso
            action: Tipo de acción
            details: Detalles adicionales
        """
        try:
            timestamp = datetime.now().isoformat()
            status = "SUCCESS" if success else "FAILED"
            
            log_entry = {
                'timestamp': timestamp,
                'user_id': user_id,
                'username': username or 'unknown',
                'ip_address': ip_address or 'unknown',
                'action': action,
                'status': status,
                'details': details or ''
            }
            
            # Log del evento
            if success:
                logger.info(f"[ACCESS] {status} - {action} by {username} from {ip_address}")
            else:
                logger.warning(f"[ACCESS] {status} - {action} attempt by {username} from {ip_address}")
                
                # Registrar intento fallido para posible bloqueo
                if ip_address:
                    failed_count = self.record_failed_attempt(ip_address)
                    if failed_count >= 5:  # Bloquear después de 5 intentos fallidos
                        self.block_ip(ip_address, f"Demasiados intentos fallidos de {action}")
                        
        except Exception as e:
            logger.exception(f"Error registrando intento de acceso: {e}")
    
    def detect_suspicious_activity(self, activity_data: Dict) -> bool:
        """
        Detecta actividad sospechosa basada en patrones.
        
        Args:
            activity_data: Datos de la actividad
            
        Returns:
            True si la actividad es sospechosa
        """
        suspicious_indicators = [
            # Múltiples requests en poco tiempo
            activity_data.get('requests_per_minute', 0) > 100,
            
            # Patrones de inyección en parámetros
            any(self.contains_malicious_patterns(str(value))
                for value in activity_data.get('parameters', {}).values()),
            
            # User agents sospechosos
            'sqlmap' in activity_data.get('user_agent', '').lower(),
            'nikto' in activity_data.get('user_agent', '').lower(),
            'burp' in activity_data.get('user_agent', '').lower(),
            
            # Intentos de acceso a archivos del sistema
            any(path in activity_data.get('requested_path', '')
                for path in ['/etc/', '/proc/', '..', '.env', 'passwd', 'shadow']),
        ]
        
        is_suspicious = any(suspicious_indicators)
        
        if is_suspicious:
            logger.warning(f"Actividad sospechosa detectada: {activity_data}")
            self.audit_security_event("SUSPICIOUS_ACTIVITY", activity_data)
        
        return is_suspicious
    
    def audit_security_event(self, event_type: str, details: Dict):
        """
        Registra un evento de seguridad para auditoría.
        
        Args:
            event_type: Tipo de evento
            details: Detalles del evento
        """
        audit_data = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'details': details
        }
        
        # Log del evento
        logger.info(f"Evento de seguridad: {event_type} - {details}")
        
        # En producción, aquí se podría integrar con sistema de auditoría
        # o guardar en base de datos específica de seguridad
    
    def get_security_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de seguridad.
        
        Returns:
            Estadísticas de seguridad
        """
        return {
            'blocked_ips_count': len(self.blocked_ips),
            'blocked_ips': list(self.blocked_ips),
            'active_csrf_tokens': len(self.csrf_tokens),
            'failed_attempts_unique_sources': len(self.failed_attempts),
            'total_failed_attempts': sum(len(attempts) for attempts in self.failed_attempts.values()),
            'active_sessions': len(self.session_tokens),
            'timestamp': datetime.now().isoformat()
        }
    
    def create_session(self, user_id: int, username: str, ip_address: str = None) -> str:
        """
        Crea una nueva sesión de usuario.
        
        Args:
            user_id: ID del usuario
            username: Nombre de usuario
            ip_address: Dirección IP
            
        Returns:
            Token de sesión
        """
        session_token = secrets.token_urlsafe(32)
        
        self.session_tokens[session_token] = {
            'user_id': user_id,
            'username': username,
            'ip_address': ip_address,
            'created_at': datetime.now(),
            'last_activity': datetime.now()
        }
        
        logger.info(f"Sesión creada para usuario {username} (ID: {user_id})")
        return session_token
    
    def validate_session(self, session_token: str, ip_address: str = None) -> Optional[Dict[str, Any]]:
        """
        Valida un token de sesión.
        
        Args:
            session_token: Token de sesión
            ip_address: Dirección IP para validación adicional
            
        Returns:
            Información de la sesión si es válida
        """
        session_data = self.session_tokens.get(session_token)
        
        if not session_data:
            return None
        
        # Validar IP si se proporciona
        if ip_address and session_data.get('ip_address') != ip_address:
            logger.warning(f"Intento de uso de sesión desde IP diferente: {ip_address} vs {session_data.get('ip_address')}")
            return None
        
        # Actualizar última actividad
        session_data['last_activity'] = datetime.now()
        
        return session_data
    
    def invalidate_session(self, session_token: str):
        """
        Invalida una sesión.
        
        Args:
            session_token: Token de sesión a invalidar
        """
        if session_token in self.session_tokens:
            user_info = self.session_tokens[session_token]
            del self.session_tokens[session_token]
            logger.info(f"Sesión invalidada para usuario {user_info.get('username')}")
    
    def cleanup_expired_sessions(self, max_age_hours: int = 24):
        """
        Limpia sesiones expiradas.
        
        Args:
            max_age_hours: Edad máxima de sesiones en horas
        """
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        expired_sessions = []
        
        for token, session_data in self.session_tokens.items():
            if session_data['last_activity'] < cutoff_time:
                expired_sessions.append(token)
        
        for token in expired_sessions:
            del self.session_tokens[token]
        
        if expired_sessions:
            logger.info(f"Limpiadas {len(expired_sessions)} sesiones expiradas")


# Instancia global
_security_manager = None


def get_security_manager() -> SecurityManager:
    """Obtiene la instancia global del security manager."""
    global _security_manager
    if _security_manager is None:
        _security_manager = SecurityManager()
    return _security_manager


# Funciones de conveniencia
def sanitize_input(data: str) -> str:
    """Función de conveniencia para sanitizar datos."""
    return get_security_manager().sanitize_input(data)


def validate_csrf(session_id: str, token: str) -> bool:
    """Función de conveniencia para validar CSRF."""
    return get_security_manager().validate_csrf_token(session_id, token)


def generate_csrf(session_id: str) -> str:
    """Función de conveniencia para generar CSRF."""
    return get_security_manager().generate_csrf_token(session_id)


def hash_password(password: str) -> tuple[str, str]:
    """Función de conveniencia para hashear contraseñas."""
    return get_security_manager().hash_password(password)


def verify_password(password: str, hashed: str, salt: str) -> bool:
    """Función de conveniencia para verificar contraseñas."""
    return get_security_manager().verify_password(password, hashed, salt)


def detect_suspicious_activity(activity_data: Dict) -> bool:
    """Función de conveniencia para detectar actividad sospechosa."""
    return get_security_manager().detect_suspicious_activity(activity_data)


def log_security_event(event_type: str, details: Dict):
    """Función de conveniencia para registrar eventos de seguridad."""
    return get_security_manager().audit_security_event(event_type, details)