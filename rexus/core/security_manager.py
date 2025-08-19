"""
Security Manager - Gestión de Seguridad Centralizada

Este módulo proporciona funcionalidades de seguridad centralizadas para Rexus.app:
- Validación y sanitización de datos
- Detección de patrones maliciosos
- Control de acceso y autorización
- Audit trail de eventos de seguridad
- Prevención de ataques comunes (XSS, SQL injection, CSRF)
"""

import re
import hashlib
import secrets
import logging
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta
import html

# Configurar logging
logger = logging.getLogger(__name__)

class SecurityManager:
    """Gestor centralizado de seguridad."""

    def __init__(self):
        """Inicializa el gestor de seguridad."""
        self.csrf_tokens = {}
        self.blocked_ips = set()
        self.failed_attempts = {}

        # Patrones maliciosos comunes
        self.malicious_patterns = [
            r'<script[^>]*>.*?</script>',  # XSS Scripts
            r'javascript:',  # JavaScript URLs
            r'on\w+\s*=',   # Event handlers
            r'union.*select',  # SQL Union attacks
            r'drop\s+table',   # SQL Drop commands
            r'exec\s*\(',      # Command execution
            r'eval\s*\(',      # Code evaluation
        ]

    def sanitize_input(self,
data: Union[str,
        Dict,
        List]) -> Union[str,
        Dict,
        List]:
        """
        Sanitiza datos de entrada de forma recursiva.

        Args:
            data: Datos a sanitizar (str, dict, list)

        Returns:
            Datos sanitizados
        """
        if isinstance(data, str):
            return self._sanitize_string(data)
        elif isinstance(data, dict):
            return {key: self.sanitize_input(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self.sanitize_input(item) for item in data]
        else:
            return data

    def _sanitize_string(self, text: str) -> str:
        """Sanitiza una cadena de texto."""
        if not isinstance(text, str):
            return text

        # Escape HTML entities
        sanitized = html.escape(text)

        # Remover patrones maliciosos
        for pattern in self.malicious_patterns:
            sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)

        # Limpiar caracteres de control
        sanitized = ''.join(char for char in sanitized if ord(char) >= 32 or char in '\t\n\r')

        return sanitized.strip()

    def validate_sql_query(self, query: str) -> bool:
        """
        Valida que una consulta SQL no contenga patrones peligrosos.

        Args:
            query: Consulta SQL a validar

        Returns:
            bool: True si la consulta es segura
        """
        if not query or not isinstance(query, str):
            return False

        query_lower = query.lower().strip()

        # Patrones peligrosos en SQL
        dangerous_patterns = [
            r';\s*(drop|alter|create|truncate)',
            r'union.*select',
            r'exec\s*\(',
            r'xp_',
            r'sp_',
            r'--',  # Comentarios SQL
            r'/\*',  # Comentarios de bloque
        ]

        for pattern in dangerous_patterns:
            if re.search(pattern, query_lower):
                logger.warning("SQL query rejected - dangerous pattern detected: %s", pattern)
                return False

        return True

    def generate_csrf_token(self, session_id: str) -> str:
        """
        Genera un token CSRF para una sesión.

        Args:
            session_id: ID de la sesión

        Returns:
            str: Token CSRF
        """
        token = secrets.token_urlsafe(32)
        self.csrf_tokens[session_id] = {
            'token': token,
            'created': datetime.now(),
            'expires': datetime.now() + timedelta(hours=2)
        }
        return token

    def validate_csrf_token(self, session_id: str, token: str) -> bool:
        """
        Valida un token CSRF.

        Args:
            session_id: ID de la sesión
            token: Token a validar

        Returns:
            bool: True si el token es válido
        """
        if session_id not in self.csrf_tokens:
            return False

        stored_token = self.csrf_tokens[session_id]

        # Verificar expiración
        if datetime.now() > stored_token['expires']:
            del self.csrf_tokens[session_id]
            return False

        # Verificar token
        return secrets.compare_digest(stored_token['token'], token)

    def hash_password(self,
password: str,
        salt: Optional[str] = None) -> tuple[str,
        str]:
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
        hashed = hashlib.pbkdf2_hmac('sha256',
                                   password.encode('utf-8'),
                                   salt.encode('utf-8'),
                                   100000)  # 100,000 iterations

        return hashed.hex(), salt

    def verify_password(self, password: str, hashed: str, salt: str) -> bool:
        """
        Verifica una contraseña contra su hash.

        Args:
            password: Contraseña a verificar
            hashed: Hash almacenado
            salt: Salt utilizado

        Returns:
            bool: True si la contraseña es correcta
        """
        try:
            computed_hash, _ = self.hash_password(password, salt)
            return secrets.compare_digest(computed_hash, hashed)
        except Exception as e:
            logger.error("Error verifying password: %s", e)
            return False

    def is_ip_blocked(self, ip: str) -> bool:
        """
        Verifica si una IP está bloqueada.

        Args:
            ip: Dirección IP

        Returns:
            bool: True si está bloqueada
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
        logger.warning("IP blocked: %s - Reason: %s", ip, reason)

    def record_failed_attempt(self, identifier: str) -> int:
        """
        Registra un intento fallido de autenticación.

        Args:
            identifier: Identificador (IP, username, etc.)

        Returns:
            int: Número de intentos fallidos
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

        return len(self.failed_attempts[identifier])

    def log_access_attempt(self, user_id=None, username=None, ip_address=None, 
                          success=True, action="login", details=None):
        """
        Registra un intento de acceso al sistema.
        
        Args:
            user_id (int): ID del usuario
            username (str): Nombre de usuario
            ip_address (str): Dirección IP
            success (bool): Si el intento fue exitoso
            action (str): Tipo de acción (login, logout, access_module, etc.)
            details (str): Detalles adicionales
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
                        self.block_ip(ip_address, f"Too many failed {action} attempts")
                        
        except Exception as e:
            logger.error(f"Error logging access attempt: {e}")

    def validate_input_length(self, data: str, max_length: int = 1000) -> bool:
        """
        Valida la longitud de entrada.

        Args:
            data: Datos a validar
            max_length: Longitud máxima permitida

        Returns:
            bool: True si la longitud es válida
        """
        return len(data) <= max_length if data else True

    def detect_suspicious_activity(self, activity_data: Dict) -> bool:
        """
        Detecta actividad sospechosa basada en patrones.

        Args:
            activity_data: Datos de la actividad

        Returns:
            bool: True si la actividad es sospechosa
        """
        suspicious_indicators = [
            # Múltiples requests en poco tiempo
            activity_data.get('requests_per_minute', 0) > 100,

            # Patrones de inyección en parámetros
            any(self._contains_malicious_pattern(str(value))
                for value in activity_data.get('parameters', {}).values()),

            # User agents sospechosos
            'sqlmap' in activity_data.get('user_agent', '').lower(),
            'nikto' in activity_data.get('user_agent', '').lower(),

            # Intentos de acceso a archivos del sistema
            any(path in activity_data.get('requested_path', '')
                for path in ['/etc/', '/proc/', '..', '.env']),
        ]

        return any(suspicious_indicators)

    def _contains_malicious_pattern(self, text: str) -> bool:
        """Verifica si el texto contiene patrones maliciosos."""
        if not isinstance(text, str):
            return False

        for pattern in self.malicious_patterns:
            if re.search(pattern, text, flags=re.IGNORECASE):
                return True
        return False

    def audit_security_event(self, event_type: str, details: Dict):
        """
        Registra un evento de seguridad para auditoría.

        Args:
            event_type: Tipo de evento (login, blocked_ip, etc.)
            details: Detalles del evento
        """
        audit_data = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'details': details
        }

        # Log del evento
        logger.info("Security event: %s - %s", event_type, details)

        # Aquí se podría integrar con el sistema de auditoría central
        # o guardar en base de datos específica de seguridad

    def get_security_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de seguridad.

        Returns:
            Dict: Estadísticas de seguridad
        """
        return {
            'blocked_ips_count': len(self.blocked_ips),
            'active_csrf_tokens': len(self.csrf_tokens),
            'failed_attempts_unique_sources': len(self.failed_attempts),
            'total_failed_attempts': sum(len(attempts) for attempts in self.failed_attempts.values())
        }


# Instancia global
_security_manager = None

def get_security_manager() -> SecurityManager:
    """Obtiene la instancia global del security manager."""
    global _security_manager
    if _security_manager is None:
        _security_manager = SecurityManager()
    return _security_manager

# Funciones de conveniencia
def sanitize_input(data):
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
