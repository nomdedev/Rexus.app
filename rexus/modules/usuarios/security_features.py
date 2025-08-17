"""
MIT License

Copyright (c) 2024 Rexus.app

Funcionalidades Avanzadas de Seguridad para Usuarios
Implementa lockout, 2FA, auditoría de sesiones y validación robusta
"""

import datetime
import json
from typing import Dict, Optional, Any

from rexus.utils.unified_sanitizer import sanitize_string
from rexus.utils.two_factor_auth import TwoFactorAuth
from rexus.utils.app_logger import get_logger, log_security, log_error


class UserSecurityManager:
    """Gestor avanzado de seguridad para usuarios."""

    # Configuración de seguridad
    MAX_LOGIN_ATTEMPTS = 3
    LOCKOUT_DURATION = 900  # 15 minutos
    PASSWORD_MIN_LENGTH = 8
    SESSION_TIMEOUT = 3600  # 1 hora

    def __init__(self, usuarios_model):
        self.usuarios_model = usuarios_model
        self.two_factor = TwoFactorAuth()
        self.failed_attempts = {}  # Cache en memoria para intentos fallidos
        self.logger = get_logger("usuarios.security")

    def validate_password_strength(self, password: str) -> Dict[str, Any]:
        """
        Valida la fortaleza de una contraseña.

        Returns:
            Dict con resultado de validación y detalles
        """
        issues = []
        score = 0

        if len(password) < self.PASSWORD_MIN_LENGTH:
            issues.append(f"Al menos {self.PASSWORD_MIN_LENGTH} caracteres")
        else:
            score += 2

        if not any(c.isupper() for c in password):
            issues.append("Al menos una letra mayúscula")
        else:
            score += 1

        if not any(c.islower() for c in password):
            issues.append("Al menos una letra minúscula")
        else:
            score += 1

        if not any(c.isdigit() for c in password):
            issues.append("Al menos un número")
        else:
            score += 1

        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if not any(c in special_chars for c in password):
            issues.append("Al menos un carácter especial")
        else:
            score += 2

        # Verificar patrones comunes débiles
        weak_patterns = ['123', 'abc', 'password', 'admin', 'user']
        if any(pattern in password.lower() for pattern in weak_patterns):
            issues.append("No usar patrones comunes")
            score -= 1

        strength_levels = {
            (0, 2): "Muy débil",
            (3, 4): "Débil",
            (5, 6): "Media",
            (7, 8): "Fuerte"
        }

        strength = "Muy débil"
        for (min_score, max_score), level in strength_levels.items():
            if min_score <= score <= max_score:
                strength = level
                break

        return {
            'valid': len(issues) == 0,
            'strength': strength,
            'score': score,
            'issues': issues,
            'requirements_met': len(issues) == 0
        }

    def register_login_attempt(self,
username: str,
        success: bool,
        ip_address: str = "unknown") -> Dict[str,
        Any]:
        """
        Registra un intento de login y maneja el lockout.

        Returns:
            Dict con estado del intento y información de lockout
        """
        username = sanitize_string(username)
        current_time = datetime.datetime.now()

        # Obtener datos del usuario
        user_data = self.usuarios_model.obtener_usuario_por_nombre(username)
        if not user_data:
            return {'success': False, 'error': 'Usuario no encontrado'}

        user_id = user_data['id']

        # Verificar si está bloqueado
        if self.is_user_locked(username):
            blocked_until = self.get_lockout_time(username)
            return {
                'success': False,
                'locked': True,
                'blocked_until': blocked_until,
                'message': f'Cuenta bloqueada hasta {blocked_until.strftime("%H:%M:%S")}'
            }

        if success:
            # Login exitoso - resetear intentos
            self.reset_failed_attempts(username)
            self.log_security_event(user_id, 'LOGIN_SUCCESS', f'Login exitoso desde {ip_address}')

            # Actualizar último login
            self.update_last_login(user_id, current_time, ip_address)

            return {
                'success': True,
                'message': 'Login exitoso',
                'requires_2fa': self.requires_2fa(username)
            }
        else:
            # Login fallido - incrementar intentos
            attempts = self.increment_failed_attempts(username)
            self.log_security_event(user_id, 'LOGIN_FAILED', f'Intento fallido #{attempts} desde {ip_address}')

            if attempts >= self.MAX_LOGIN_ATTEMPTS:
                # Bloquear usuario
                self.lock_user(username, self.LOCKOUT_DURATION)
                self.log_security_event(user_id, 'ACCOUNT_LOCKED', f'Cuenta bloqueada por {self.MAX_LOGIN_ATTEMPTS} intentos fallidos')

                return {
                    'success': False,
                    'locked': True,
                    'attempts': attempts,
                    'message': f'Cuenta bloqueada por {self.LOCKOUT_DURATION // 60} minutos'
                }
            else:
                remaining = self.MAX_LOGIN_ATTEMPTS - attempts
                return {
                    'success': False,
                    'attempts': attempts,
                    'remaining': remaining,
                    'message': f'Credenciales incorrectas. {remaining} intentos restantes'
                }

    def is_user_locked(self, username: str) -> bool:
        """Verifica si un usuario está bloqueado."""
        if username not in self.failed_attempts:
            return False

        attempt_data = self.failed_attempts[username]
        locked_until = attempt_data.get('locked_until')

        if locked_until and datetime.datetime.now() < locked_until:
            return True

        # Lockout expirado, limpiar
        if locked_until and datetime.datetime.now() >= locked_until:
            self.reset_failed_attempts(username)

        return False

    def get_lockout_time(self, username: str) -> Optional[datetime.datetime]:
        """Obtiene el tiempo hasta cuando está bloqueado el usuario."""
        if username in self.failed_attempts:
            return self.failed_attempts[username].get('locked_until')
        return None

    def increment_failed_attempts(self, username: str) -> int:
        """Incrementa los intentos fallidos para un usuario."""
        if username not in self.failed_attempts:
            self.failed_attempts[username] = {
                'count': 0,
                'first_attempt': datetime.datetime.now(),
                'last_attempt': None,
                'locked_until': None
            }

        self.failed_attempts[username]['count'] += 1
        self.failed_attempts[username]['last_attempt'] = datetime.datetime.now()

        return self.failed_attempts[username]['count']

    def reset_failed_attempts(self, username: str):
        """Resetea los intentos fallidos para un usuario."""
        if username in self.failed_attempts:
            del self.failed_attempts[username]

    def lock_user(self, username: str, duration_seconds: int):
        """Bloquea un usuario por un tiempo específico."""
        if username not in self.failed_attempts:
            self.failed_attempts[username] = {'count': 0}

        self.failed_attempts[username]['locked_until'] = (
            datetime.datetime.now() + datetime.timedelta(seconds=duration_seconds)
        )

    def unlock_user(self, username: str) -> bool:
        """Desbloquea manualmente un usuario."""
        try:
            user_data = self.usuarios_model.obtener_usuario_por_nombre(username)
            if not user_data:
                return False

            self.reset_failed_attempts(username)
            self.log_security_event(user_data['id'], 'ACCOUNT_UNLOCKED', 'Cuenta desbloqueada manualmente')

            return True
        except Exception as e:
            self.logger.error(f"Error desbloqueando usuario: {e}", exc_info=True)
            return False

    def requires_2fa(self, username: str) -> bool:
        """Verifica si un usuario requiere 2FA."""
        try:
            user_data = self.usuarios_model.obtener_usuario_por_nombre(username)
            if not user_data:
                return False

            config_personal = user_data.get('configuracion_personal', '{}')
            config_dict = json.loads(config_personal) if config_personal else {}

            return config_dict.get('2fa_enabled', False)
        except:
            return False

    def setup_2fa(self, username: str) -> Dict[str, Any]:
        """Configura 2FA para un usuario."""
        return self.two_factor.habilitar_2fa_usuario(self.usuarios_model, username)

    def verify_2fa_setup(self, username: str, verification_code: str) -> bool:
        """Verifica la configuración inicial de 2FA."""
        return self.two_factor.verificar_setup_2fa(self.usuarios_model, username, verification_code)

    def validate_2fa_login(self, username: str, code: str) -> bool:
        """Valida código 2FA durante login."""
        return self.two_factor.validar_2fa_login(self.usuarios_model, username, code)

    def disable_2fa(self, username: str) -> bool:
        """Deshabilita 2FA para un usuario."""
        success = self.two_factor.deshabilitar_2fa(self.usuarios_model, username)
        if success:
            user_data = self.usuarios_model.obtener_usuario_por_nombre(username)
            if user_data:
                self.log_security_event(user_data['id'], '2FA_DISABLED', '2FA deshabilitado')
        return success

    def log_security_event(self,
user_id: int,
        event_type: str,
        description: str):
        """Registra eventos de seguridad."""
        try:
            # Intentar usar sistema de auditoría si está disponible
            from rexus.core.audit_system import log_security_event
            log_security_event(event_type, description, user_id)
        except ImportError:
            # Fallback a print si no está disponible
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_security("INFO", f"User {user_id}: {event_type} - {description}")

    def update_last_login(self,
user_id: int,
        login_time: datetime.datetime,
        ip_address: str):
        """Actualiza el último login del usuario."""
        try:
            if hasattr(self.usuarios_model, 'actualizar_ultimo_login'):
                self.usuarios_model.actualizar_ultimo_login(user_id, login_time, ip_address)
        except Exception as e:
            self.logger.error(f"Error actualizando último login: {e}", exc_info=True)

    def get_user_security_status(self, username: str) -> Dict[str, Any]:
        """Obtiene el estado de seguridad completo de un usuario."""
        user_data = self.usuarios_model.obtener_usuario_por_nombre(username)
        if not user_data:
            return {'error': 'Usuario no encontrado'}

        config_personal = user_data.get('configuracion_personal', '{}')
        config_dict = json.loads(config_personal) if config_personal else {}

        failed_data = self.failed_attempts.get(username, {})

        return {
            'username': username,
            'is_locked': self.is_user_locked(username),
            'locked_until': self.get_lockout_time(username),
            'failed_attempts': failed_data.get('count', 0),
            'last_failed_attempt': failed_data.get('last_attempt'),
            '2fa_enabled': config_dict.get('2fa_enabled', False),
            '2fa_setup_date': config_dict.get('2fa_setup_date'),
            'last_login': user_data.get('ultimo_login'),
            'last_login_ip': user_data.get('ultimo_login_ip'),
            'account_created': user_data.get('fecha_creacion'),
            'account_status': user_data.get('estado', 'activo')
        }

    def get_security_dashboard(self) -> Dict[str, Any]:
        """Obtiene dashboard de seguridad del sistema."""
        try:
            # Estadísticas de usuarios
            total_users = len(self.usuarios_model.obtener_todos_usuarios())
            locked_users = len([u for u in self.failed_attempts.keys() if self.is_user_locked(u)])

            # Usuarios con 2FA habilitado
            users_with_2fa = 0
            for user in self.usuarios_model.obtener_todos_usuarios():
                config = json.loads(user.get('configuracion_personal', '{}')) if user.get('configuracion_personal') else {}
                if config.get('2fa_enabled', False):
                    users_with_2fa += 1

            # Estadísticas de intentos recientes
            recent_failed_attempts = sum(
                data['count'] for data in self.failed_attempts.values()
                if data.get('last_attempt') and
                (datetime.datetime.now() - data['last_attempt']).total_seconds() < 3600
            )

            return {
                'total_users': total_users,
                'locked_users': locked_users,
                'users_with_2fa': users_with_2fa,
                '2fa_adoption_rate': (users_with_2fa / total_users * 100) if total_users > 0 else 0,
                'recent_failed_attempts': recent_failed_attempts,
                'security_config': {
                    'max_login_attempts': self.MAX_LOGIN_ATTEMPTS,
                    'lockout_duration_minutes': self.LOCKOUT_DURATION // 60,
                    'password_min_length': self.PASSWORD_MIN_LENGTH,
                    'session_timeout_minutes': self.SESSION_TIMEOUT // 60
                }
            }
        except Exception as e:
            self.logger.error(f"Error generando dashboard de seguridad: {e}", exc_info=True)
            return {'error': str(e)}


def create_security_manager(usuarios_model) -> UserSecurityManager:
    """Factory function para crear el gestor de seguridad."""
    return UserSecurityManager(usuarios_model)


# Funciones de utilidad para integración fácil
def validate_login_with_security(usuarios_model, username: str, password: str, ip_address: str = "unknown") -> Dict[str, Any]:
    """
    Valida login con todas las funcionalidades de seguridad.

    Returns:
        Dict con resultado completo de validación
    """
    security_manager = create_security_manager(usuarios_model)

    # Verificar si está bloqueado antes de validar credenciales
    if security_manager.is_user_locked(username):
        return security_manager.register_login_attempt(username, False, ip_address)

    # Validar credenciales básicas
    user_valid = usuarios_model.validar_usuario(username, password)

    # Registrar intento
    return security_manager.register_login_attempt(username, user_valid, ip_address)


if __name__ == "__main__":
    # Test básico del sistema de seguridad
    logger = get_logger("usuarios.security")
    logger.info("Sistema de seguridad avanzada para usuarios inicializado")

    # Ejemplo de validación de contraseña
    security = UserSecurityManager(None)

    test_passwords = [
        "123",
        "password",
        "Password1",
        "MyStr0ng!P@ssw0rd"
    ]

    for pwd in test_passwords:
        result = security.validate_password_strength(pwd)
        logger = get_logger("usuarios.security")
        logger.info(f"Contraseña '{pwd}': {result['strength']} - {result['issues']}")
