"""
MIT License

Copyright (c) 2024 Rexus.app

User Enumeration Protection - Sistema de protección contra enumeración de usuarios
"""

import time
import hashlib
import secrets
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta


class UserEnumerationProtection:
    """Sistema de protección contra enumeración de usuarios."""
    
    def __init__(self):
        """Inicializar sistema de protección."""
        self.failed_attempts: Dict[str, List[float]] = {}
        self.suspicious_patterns: Dict[str, List[Dict]] = {}
        self.blocked_ips: Dict[str, float] = {}
        
        # Configuración de protección
        self.max_attempts_per_ip = 5
        self.block_duration = 900  # 15 minutos
        self.pattern_detection_window = 300  # 5 minutos
        self.min_response_time = 1.0  # Tiempo mínimo de respuesta en segundos
        
    def record_login_attempt(self, ip_address: str, username: str, 
                           success: bool, user_exists: bool) -> bool:
        """
        Registra un intento de login y determina si debe ser bloqueado.
        
        Args:
            ip_address: Dirección IP del cliente
            username: Nombre de usuario intentado
            success: Si el login fue exitoso
            user_exists: Si el usuario existe (para detección de patrones)
            
        Returns:
            True si el intento debe ser bloqueado
        """
        from ..utils.secure_logger import log_security_event
        
        current_time = time.time()
        
        # Limpiar intentos antiguos
        self._cleanup_old_attempts(current_time)
        
        # Verificar si la IP está bloqueada
        if self._is_ip_blocked(ip_address, current_time):
            log_security_event("IP_BLOCKED_ATTEMPT", "HIGH", f"IP: {ip_address}, User: {username}")
            return True
        
        # Registrar el intento
        if ip_address not in self.failed_attempts:
            self.failed_attempts[ip_address] = []
        
        if not success:
            self.failed_attempts[ip_address].append(current_time)
            
            # Detectar patrones sospechosos
            self._detect_suspicious_patterns(ip_address, username, user_exists, current_time)
            
            # Verificar si se debe bloquear la IP
            if len(self.failed_attempts[ip_address]) >= self.max_attempts_per_ip:
                self.blocked_ips[ip_address] = current_time + self.block_duration
                log_security_event("IP_BLOCKED", "HIGH", f"IP: {ip_address}, Attempts: {len(self.failed_attempts[ip_address])}")
                return True
        else:
            # Limpiar intentos fallidos en login exitoso
            if ip_address in self.failed_attempts:
                self.failed_attempts[ip_address] = []
        
        return False
    
    def _is_ip_blocked(self, ip_address: str, current_time: float) -> bool:
        """Verifica si una IP está bloqueada."""
        if ip_address in self.blocked_ips:
            if current_time < self.blocked_ips[ip_address]:
                return True
            else:
                # Desbloquear IP expirada
                del self.blocked_ips[ip_address]
        return False
    
    def _detect_suspicious_patterns(self, ip_address: str, username: str, 
                                   user_exists: bool, current_time: float):
        """Detecta patrones sospechosos de enumeración de usuarios."""
        from ..utils.secure_logger import log_security_event
        
        if ip_address not in self.suspicious_patterns:
            self.suspicious_patterns[ip_address] = []
        
        # Registrar patrón
        pattern = {
            'username': username,
            'user_exists': user_exists,
            'timestamp': current_time
        }
        self.suspicious_patterns[ip_address].append(pattern)
        
        # Limpiar patrones antiguos
        cutoff_time = current_time - self.pattern_detection_window
        self.suspicious_patterns[ip_address] = [
            p for p in self.suspicious_patterns[ip_address] 
            if p['timestamp'] > cutoff_time
        ]
        
        # Analizar patrones recientes
        recent_patterns = self.suspicious_patterns[ip_address]
        
        if len(recent_patterns) >= 10:  # Muchos intentos en poco tiempo
            # Detectar enumeración sistemática
            usernames_tried = set(p['username'] for p in recent_patterns)
            existing_users = sum(1 for p in recent_patterns if p['user_exists'])
            
            if len(usernames_tried) >= 5:  # Intentando múltiples usuarios
                log_security_event("USER_ENUMERATION_DETECTED", "HIGH", 
                                 f"IP: {ip_address}, Users tried: {len(usernames_tried)}")
            
            if existing_users > 0 and len(usernames_tried) - existing_users > 20:
                log_security_event("SYSTEMATIC_USER_SCAN", "CRITICAL", 
                                 f"IP: {ip_address}, Invalid attempts: {len(usernames_tried) - existing_users}")
    
    def _cleanup_old_attempts(self, current_time: float):
        """Limpia intentos antiguos para evitar acumulación de memoria."""
        cutoff_time = current_time - self.block_duration
        
        # Limpiar intentos fallidos antiguos
        for ip in list(self.failed_attempts.keys()):
            self.failed_attempts[ip] = [
                timestamp for timestamp in self.failed_attempts[ip]
                if timestamp > cutoff_time
            ]
            if not self.failed_attempts[ip]:
                del self.failed_attempts[ip]
        
        # Limpiar IPs bloqueadas expiradas
        for ip in list(self.blocked_ips.keys()):
            if current_time >= self.blocked_ips[ip]:
                del self.blocked_ips[ip]
    
    def get_response_delay(self, username: str, user_exists: bool) -> float:
        """
        Calcula delay consistente para evitar timing attacks.
        
        Args:
            username: Nombre de usuario
            user_exists: Si el usuario existe
            
        Returns:
            Tiempo de delay en segundos
        """
        # Usar hash del username para delay consistente
        username_hash = hashlib.sha256(username.encode()).hexdigest()
        # Convertir primeros 8 caracteres a número
        hash_num = int(username_hash[:8], 16)
        
        # Delay base + variación determinística
        base_delay = self.min_response_time
        variation = (hash_num % 1000) / 1000.0  # 0-1 segundos
        
        return base_delay + variation
    
    def simulate_password_check(self, username: str) -> str:
        """
        Simula verificación de contraseña para usuarios inexistentes.
        
        Args:
            username: Nombre de usuario
            
        Returns:
            Hash simulado (no usado, solo para consumir tiempo)
        """
        # Realizar operaciones de hash para simular verificación real
        fake_salt = hashlib.sha256(f"fake_salt_{username}".encode()).hexdigest()[:16]
        fake_password = "fake_password_simulation"
        
        # Simular múltiples rounds de hashing (como bcrypt)
        result = fake_password
        for _ in range(12):  # Simular 12 rounds
            result = hashlib.sha256((result + fake_salt).encode()).hexdigest()
        
        return result
    
    def get_generic_error_message(self) -> str:
        """
        Retorna mensaje de error genérico para evitar revelación de información.
        
        Returns:
            Mensaje de error genérico
        """
        return "Credenciales inválidas"
    
    def is_ip_allowed(self, ip_address: str) -> Tuple[bool, str]:
        """
        Verifica si una IP puede realizar intentos de login.
        
        Args:
            ip_address: Dirección IP
            
        Returns:
            Tupla (permitido, mensaje_error)
        """
        current_time = time.time()
        
        if self._is_ip_blocked(ip_address, current_time):
            time_remaining = int(self.blocked_ips[ip_address] - current_time)
            return False, f"IP bloqueada. Intente nuevamente en {time_remaining} segundos."
        
        return True, ""
    
    def get_stats(self) -> Dict:
        """
        Obtiene estadísticas del sistema de protección.
        
        Returns:
            Diccionario con estadísticas
        """
        current_time = time.time()
        self._cleanup_old_attempts(current_time)
        
        total_failed_attempts = sum(len(attempts) for attempts in self.failed_attempts.values())
        active_blocked_ips = len(self.blocked_ips)
        active_monitoring_ips = len(self.failed_attempts)
        
        return {
            'active_blocked_ips': active_blocked_ips,
            'active_monitoring_ips': active_monitoring_ips,
            'total_recent_failed_attempts': total_failed_attempts,
            'block_duration_seconds': self.block_duration,
            'max_attempts_per_ip': self.max_attempts_per_ip
        }


# Instancia global del sistema de protección
user_enum_protection: Optional[UserEnumerationProtection] = None


def init_user_enumeration_protection():
    """Inicializa el sistema de protección contra enumeración de usuarios."""
    global user_enum_protection
    user_enum_protection = UserEnumerationProtection()


def get_user_enumeration_protection() -> UserEnumerationProtection:
    """
    Obtiene la instancia del sistema de protección.
    
    Returns:
        Instancia de UserEnumerationProtection
        
    Raises:
        RuntimeError: Si no está inicializada
    """
    if user_enum_protection is None:
        init_user_enumeration_protection()
    
    return user_enum_protection


def record_login_attempt(ip_address: str, username: str, success: bool, user_exists: bool) -> bool:
    """Función de conveniencia para registrar intento de login."""
    return get_user_enumeration_protection().record_login_attempt(
        ip_address, username, success, user_exists
    )


def get_response_delay(username: str, user_exists: bool) -> float:
    """Función de conveniencia para obtener delay de respuesta."""
    return get_user_enumeration_protection().get_response_delay(username, user_exists)


def simulate_password_check(username: str) -> str:
    """Función de conveniencia para simular verificación de contraseña."""
    return get_user_enumeration_protection().simulate_password_check(username)