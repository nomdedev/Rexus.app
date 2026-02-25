"""
Rate Limiter - Protección contra ataques de fuerza bruta

Implementa rate limiting para prevenir ataques de fuerza bruta en intentos de login.
Bloquea temporalmente usuarios después de múltiples intentos fallidos.
"""

from datetime import datetime, timedelta
import math
from typing import Optional, Tuple


class RateLimiter:
    """
    Limita la tasa de intentos de login para prevenir ataques de fuerza bruta.

    Attributes:
        max_attempts (int): Máximo número de intentos permitidos
        lockout_minutes (int): Minutos de bloqueo después de exceder intentos
        attempts (dict): Diccionario que rastrea intentos por usuario
    """

    def __init__(
        self,
        max_attempts: int = 3,
        lockout_minutes: int = 15,
        max_requests: Optional[int] = None,
        window_seconds: Optional[int] = None,
    ):
        """
        Inicializa el RateLimiter.

        Args:
            max_attempts: Máximo número de intentos fallidos permitidos (default: 3)
            lockout_minutes: Minutos a bloquear después de exceder intentos (default: 15)
        """
        if max_requests is not None:
            max_attempts = max_requests
        if window_seconds is not None:
            lockout_minutes = max(1, math.ceil(window_seconds / 60))

        self.max_attempts = max_attempts
        self.lockout_minutes = lockout_minutes
        self.window_seconds = int(window_seconds) if window_seconds is not None else lockout_minutes * 60
        self.attempts = {}  # {username: {"count": int, "last_attempt": datetime}}
        self._request_buckets = {}  # {(action, identifier): [datetime, ...]}

    def is_allowed(self, action: str, identifier: str) -> bool:
        """Compatibilidad para control de tasa genérico por acción+identificador."""
        now = datetime.now()
        key = (action, identifier)

        if key not in self._request_buckets:
            self._request_buckets[key] = []

        window_start = now - timedelta(seconds=self.window_seconds)
        recent_requests = [ts for ts in self._request_buckets[key] if ts >= window_start]
        self._request_buckets[key] = recent_requests

        if len(recent_requests) >= self.max_attempts:
            return False

        self._request_buckets[key].append(now)
        return True

    def is_blocked(self, username: str) -> Tuple[bool, Optional[datetime]]:
        """
        Verifica si un usuario está bloqueado temporalmente.

        Args:
            username: Nombre de usuario a verificar

        Returns:
            Tuple[bool, Optional[datetime]]:
                - (True, locked_until) si está bloqueado
                - (False, None) si no está bloqueado
        """
        if username not in self.attempts:
            return False, None

        data = self.attempts[username]

        # Verificar si excedió el máximo de intentos
        if data["count"] >= self.max_attempts:
            locked_until = data["last_attempt"] + timedelta(minutes=self.lockout_minutes)

            # Si aún está dentro del período de bloqueo
            if datetime.now() < locked_until:
                return True, locked_until
            else:
                # Resetear si pasó el tiempo de bloqueo
                del self.attempts[username]
                return False, None

        return False, None

    def record_failed_attempt(self, username: str) -> int:
        """
        Registra un intento fallido de login.

        Args:
            username: Nombre de usuario

        Returns:
            int: Número de intentos fallidos registrados
        """
        if username not in self.attempts:
            self.attempts[username] = {"count": 0, "last_attempt": None}

        self.attempts[username]["count"] += 1
        self.attempts[username]["last_attempt"] = datetime.now()

        return self.attempts[username]["count"]

    def record_successful_attempt(self, username: str):
        """
        Registra un login exitoso y limpia el historial de intentos fallidos.

        Args:
            username: Nombre de usuario
        """
        if username in self.attempts:
            del self.attempts[username]

    def get_remaining_attempts(self, username: str) -> int:
        """
        Obtiene el número de intentos restantes antes del bloqueo.

        Args:
            username: Nombre de usuario

        Returns:
            int: Intentos restantes (0 si está bloqueado)
        """
        is_blocked, _ = self.is_blocked(username)

        if is_blocked:
            return 0

        if username not in self.attempts:
            return self.max_attempts

        return max(0, self.max_attempts - self.attempts[username]["count"])

    def get_lockout_time_remaining(self, username: str) -> Optional[int]:
        """
        Obtiene el tiempo restante de bloqueo en segundos.

        Args:
            username: Nombre de usuario

        Returns:
            Optional[int]: Segundos restantes de bloqueo, o None si no está bloqueado
        """
        is_blocked, locked_until = self.is_blocked(username)

        if not is_blocked or locked_until is None:
            return None

        remaining = (locked_until - datetime.now()).total_seconds()
        return int(max(0, remaining))

    def reset_attempts(self, username: str):
        """
        Limpia manualmente el historial de intentos de un usuario.
        Útil para administradores que necesitan desbloquear usuarios.

        Args:
            username: Nombre de usuario
        """
        if username in self.attempts:
            del self.attempts[username]


# Instancia global del RateLimiter
_rate_limiter = None


def get_rate_limiter() -> RateLimiter:
    """
    Obtiene la instancia singleton del RateLimiter.

    Returns:
        RateLimiter: Instancia del RateLimiter
    """
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter(
            max_attempts=3,      # 3 intentos fallidos permitidos
            lockout_minutes=15   # 15 minutos de bloqueo
        )
    return _rate_limiter


def reset_rate_limiter():
    """Resetea la instancia global del RateLimiter (útil para tests)."""
    global _rate_limiter
    _rate_limiter = None
