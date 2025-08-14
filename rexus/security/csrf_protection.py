"""
MIT License

Copyright (c) 2024 Rexus.app

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

CSRF Protection - Sistema de protección contra ataques Cross-Site Request Forgery
"""

import secrets
import time
import hmac
import hashlib
from typing import Dict, Optional, Tuple
from datetime import datetime


class CSRFToken:
    """Generador y validador de tokens CSRF."""

    def __init__(self, secret_key: str):
        """
        Inicializar generador de tokens CSRF.

        Args:
            secret_key: Clave secreta para firmar tokens
        """
        self.secret_key = secret_key.encode()
        self.token_lifetime = 3600  # 1 hora por defecto

    def generate_token(self, user_id: str = "anonymous", session_id: str = None) -> str:
        """
        Genera un token CSRF único.

        Args:
            user_id: ID del usuario (opcional)
            session_id: ID de sesión (opcional)

        Returns:
            Token CSRF firmado
        """
        # Generar componentes del token
        timestamp = str(int(time.time()))
        nonce = secrets.token_hex(16)

        # Crear payload
        payload = f"{user_id}:{session_id or 'no-session'}:{timestamp}:{nonce}"

        # Crear firma HMAC
        signature = hmac.new(
            self.secret_key,
            payload.encode(),
            hashlib.sha256
        ).hexdigest()

        # Token final: payload:signature (base64 para URL safety)
        import base64
        token_data = f"{payload}:{signature}"
        token = base64.urlsafe_b64encode(token_data.encode()).decode()

        return token

    def validate_token(self, token: str, user_id: str = "anonymous",
                      session_id: str = None) -> Tuple[bool, str]:
        """
        Valida un token CSRF.

        Args:
            token: Token a validar
            user_id: ID del usuario actual
            session_id: ID de sesión actual

        Returns:
            Tupla (es_válido, mensaje_error)
        """
        try:
            # Decodificar token
            import base64
            token_data = base64.urlsafe_b64decode(token.encode()).decode()
            parts = token_data.split(':')

            if len(parts) != 5:
                return False, "Formato de token inválido"

            token_user, token_session, timestamp, nonce, signature = parts

            # Verificar expiración
            token_time = int(timestamp)
            current_time = int(time.time())

            if current_time - token_time > self.token_lifetime:
                return False, "Token expirado"

            # Recrear payload y verificar firma
            payload = f"{token_user}:{token_session}:{timestamp}:{nonce}"
            expected_signature = hmac.new(
                self.secret_key,
                payload.encode(),
                hashlib.sha256
            ).hexdigest()

            if not hmac.compare_digest(signature, expected_signature):
                return False, "Firma inválida"

            # Verificar contexto de usuario/sesión
            if token_user != user_id:
                return False, "Token no corresponde al usuario"

            if session_id and token_session != session_id:
                return False, "Token no corresponde a la sesión"

            return True, "Token válido"

        except Exception as e:
            from ..utils.secure_logger import log_security_event
            log_security_event("CSRF_VALIDATION_ERROR", "HIGH", str(e))
            return False, f"Error validando token: {str(e)}"


class CSRFProtection:
    """Sistema de protección CSRF para la aplicación."""

    def __init__(self, secret_key: str):
        """
        Inicializar sistema de protección CSRF.

        Args:
            secret_key: Clave secreta para tokens
        """
        self.token_generator = CSRFToken(secret_key)
        self.active_tokens: Dict[str, Dict] = {}
        self.max_tokens_per_user = 10

    def generate_token_for_user(self, user_id: str, session_id: str = None) -> str:
        """
        Genera token CSRF para un usuario específico.

        Args:
            user_id: ID del usuario
            session_id: ID de sesión opcional

        Returns:
            Token CSRF
        """
        from ..utils.secure_logger import log_info

        # Limpiar tokens antiguos del usuario
        self._cleanup_user_tokens(user_id)

        # Generar nuevo token
        token = self.token_generator.generate_token(user_id, session_id)

        # Almacenar token activo
        if user_id not in self.active_tokens:
            self.active_tokens[user_id] = {}

        self.active_tokens[user_id][token] = {
            'created': datetime.now(),
            'session_id': session_id,
            'used': False
        }

        log_info(f"CSRF token generado para usuario: {user_id}")
        return token

    def validate_token_for_user(self, token: str, user_id: str,
                               session_id: str = None, consume: bool = True) -> Tuple[bool, str]:
        """
        Valida token CSRF para un usuario.

        Args:
            token: Token a validar
            user_id: ID del usuario
            session_id: ID de sesión
            consume: Si consumir el token tras validación exitosa

        Returns:
            Tupla (es_válido, mensaje)
        """
        from ..utils.secure_logger import log_security_event

        # Validar token cryptográficamente
        is_valid,
message = self.token_generator.validate_token(token,
            user_id,
            session_id)

        if not is_valid:
            log_security_event("CSRF_TOKEN_INVALID",
"HIGH",
                f"User: {user_id},
                Error: {message}")
            return False, message

        # Verificar si el token está en tokens activos
        if user_id not in self.active_tokens or token not in self.active_tokens[user_id]:
            log_security_event("CSRF_TOKEN_NOT_ACTIVE", "HIGH", f"User: {user_id}")
            return False, "Token no está activo"

        token_info = self.active_tokens[user_id][token]

        # Verificar si ya fue usado (para tokens de un solo uso)
        if consume and token_info.get('used', False):
            log_security_event("CSRF_TOKEN_REUSED", "HIGH", f"User: {user_id}")
            return False, "Token ya fue utilizado"

        # Marcar como usado si es necesario
        if consume:
            token_info['used'] = True

        log_security_event("CSRF_TOKEN_VALID", "INFO", f"User: {user_id}")
        return True, "Token válido"

    def invalidate_user_tokens(self, user_id: str):
        """
        Invalida todos los tokens de un usuario.

        Args:
            user_id: ID del usuario
        """
        if user_id in self.active_tokens:
            del self.active_tokens[user_id]

        from ..utils.secure_logger import log_info
        log_info(f"Tokens CSRF invalidados para usuario: {user_id}")

    def _cleanup_user_tokens(self, user_id: str):
        """Limpia tokens antiguos del usuario."""
        if user_id not in self.active_tokens:
            return

        current_time = datetime.now()
        tokens_to_remove = []

        for token, info in self.active_tokens[user_id].items():
            # Remover tokens más antiguos que 1 hora
            if (current_time - info['created']).seconds > 3600:
                tokens_to_remove.append(token)

        for token in tokens_to_remove:
            del self.active_tokens[user_id][token]

        # Limitar número de tokens por usuario
        if len(self.active_tokens[user_id]) > self.max_tokens_per_user:
            # Mantener solo los más recientes
            sorted_tokens = sorted(
                self.active_tokens[user_id].items(),
                key=lambda x: x[1]['created'],
                reverse=True
            )

            self.active_tokens[user_id] = dict(sorted_tokens[:self.max_tokens_per_user])

    def cleanup_expired_tokens(self):
        """Limpieza periódica de tokens expirados."""
        datetime.now()
        users_to_cleanup = list(self.active_tokens.keys())

        for user_id in users_to_cleanup:
            self._cleanup_user_tokens(user_id)

            # Remover usuario si no tiene tokens
            if not self.active_tokens[user_id]:
                del self.active_tokens[user_id]

    def get_stats(self) -> Dict:
        """
        Obtiene estadísticas del sistema CSRF.

        Returns:
            Diccionario con estadísticas
        """
        total_tokens = sum(len(tokens) for tokens in self.active_tokens.values())
        active_users = len(self.active_tokens)

        return {
            'active_users': active_users,
            'total_tokens': total_tokens,
            'avg_tokens_per_user': total_tokens / active_users if active_users > 0 else 0
        }


# Instancia global para la aplicación
csrf_protection: Optional[CSRFProtection] = None


def init_csrf_protection(secret_key: str):
    """
    Inicializa el sistema de protección CSRF.

    Args:
        secret_key: Clave secreta
    """
    global csrf_protection
    csrf_protection = CSRFProtection(secret_key)


def get_csrf_protection() -> CSRFProtection:
    """
    Obtiene la instancia de protección CSRF.

    Returns:
        Instancia de CSRFProtection

    Raises:
        RuntimeError: Si no está inicializada
    """
    if csrf_protection is None:
        raise RuntimeError("CSRF protection no está inicializada. Llame init_csrf_protection() primero.")

    return csrf_protection


def generate_csrf_token(user_id: str, session_id: str = None) -> str:
    """
    Función de conveniencia para generar token CSRF.

    Args:
        user_id: ID del usuario
        session_id: ID de sesión

    Returns:
        Token CSRF
    """
    return get_csrf_protection().generate_token_for_user(user_id, session_id)


def validate_csrf_token(token: str, user_id: str, session_id: str = None) -> bool:
    """
    Función de conveniencia para validar token CSRF.

    Args:
        token: Token a validar
        user_id: ID del usuario
        session_id: ID de sesión

    Returns:
        True si el token es válido
    """
    is_valid,
_ = get_csrf_protection().validate_token_for_user(token,
        user_id,
        session_id)
    return is_valid
