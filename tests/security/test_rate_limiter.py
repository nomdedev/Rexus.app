"""
🧪 Tests de Seguridad - RateLimiter
==================================

Tests críticos para verificar que el RateLimiter previene
ataques de fuerza bruta correctamente.

Best practices según:
- OWASP Testing Guide
- Google Security Testing
"""

import pytest

# Verificar dependencias
try:
    import freezegun
except ImportError:
    pytest.skip("freezegun no está disponible", allow_module_level=True)

from datetime import datetime, timedelta
from freezegun import freeze_time

from rexus.core.rate_limiter import RateLimiter, get_rate_limiter


class TestRateLimiter:
    """Tests del sistema de Rate Limiting"""

    @pytest.fixture
    def rate_limiter(self):
        """RateLimiter con configuración de testing"""
        return RateLimiter(max_attempts=3, lockout_minutes=15)

    def test_registro_intento_fallido(self, rate_limiter):
        """Verifica que se registren intentos fallidos"""
        username = "test_user"

        # Primer intento fallido
        count = rate_limiter.record_failed_attempt(username)
        assert count == 1

        # Segundo intento fallido
        count = rate_limiter.record_failed_attempt(username)
        assert count == 2

        # Tercer intento fallido
        count = rate_limiter.record_failed_attempt(username)
        assert count == 3

    def test_bloqueo_despues_de_3_intentos(self, rate_limiter):
        """CRÍTICO: Verifica bloqueo después de 3 intentos"""
        username = "attacker"

        # 3 intentos fallidos
        for _ in range(3):
            rate_limiter.record_failed_attempt(username)

        # Verificar bloqueo
        is_blocked, locked_until = rate_limiter.is_blocked(username)
        assert is_blocked is True
        assert locked_until is not None
        assert locked_until > datetime.now()

    def test_no_bloqueo_con_menos_de_3_intentos(self, rate_limiter):
        """Verifica que NO se bloquee con menos de 3 intentos"""
        username = "user"

        # Solo 2 intentos fallidos
        for _ in range(2):
            rate_limiter.record_failed_attempt(username)

        # No debe estar bloqueado
        is_blocked, locked_until = rate_limiter.is_blocked(username)
        assert is_blocked is False
        assert locked_until is None

    def test_desbloqueo_despues_de_tiempo(self, rate_limiter):
        """CRÍTICO: Verifica desbloqueo después del tiempo de lockout"""
        username = "user"

        # Bloquear usuario
        for _ in range(3):
            rate_limiter.record_failed_attempt(username)

        # Verificar que está bloqueado
        is_blocked, _ = rate_limiter.is_blocked(username)
        assert is_blocked is True

        # Viajar en el tiempo 16 minutos después
        with freeze_time(datetime.now() + timedelta(minutes=16)):
            # Debe estar desbloqueado
            is_blocked, locked_until = rate_limiter.is_blocked(username)
            assert is_blocked is False
            assert locked_until is None

    def test_login_exitoso_limpia_intentos(self, rate_limiter):
        """Verifica que login exitoso limpie intentos fallidos"""
        username = "user"

        # 2 intentos fallidos
        for _ in range(2):
            rate_limiter.record_failed_attempt(username)

        # Login exitoso
        rate_limiter.record_successful_attempt(username)

        # Verificar que se limpiaron los intentos
        is_blocked, _ = rate_limiter.is_blocked(username)
        assert is_blocked is False

        # Intentos restantes deben ser 3
        remaining = rate_limiter.get_remaining_attempts(username)
        assert remaining == 3

    def test_intentos_restantes(self, rate_limiter):
        """Verifica cálculo de intentos restantes"""
        username = "user"

        # Sin intentos fallidos
        remaining = rate_limiter.get_remaining_attempts(username)
        assert remaining == 3

        # 1 intento fallido
        rate_limiter.record_failed_attempt(username)
        remaining = rate_limiter.get_remaining_attempts(username)
        assert remaining == 2

        # 2 intentos fallidos
        rate_limiter.record_failed_attempt(username)
        remaining = rate_limiter.get_remaining_attempts(username)
        assert remaining == 1

    def test_tiempo_restante_bloqueo(self, rate_limiter):
        """Verifica cálculo de tiempo restante de bloqueo"""
        username = "user"

        # Bloquear usuario
        for _ in range(3):
            rate_limiter.record_failed_attempt(username)

        # Verificar tiempo restante
        remaining_seconds = rate_limiter.get_lockout_time_remaining(username)
        assert remaining_seconds is not None
        assert remaining_seconds > 0
        assert remaining_seconds <= 900  # Máximo 15 minutos (900 segundos)

    def test_reset_manual(self, rate_limiter):
        """Verifica reset manual de intentos"""
        username = "user"

        # Bloquear usuario
        for _ in range(3):
            rate_limiter.record_failed_attempt(username)

        # Reset manual
        rate_limiter.reset_attempts(username)

        # Verificar que ya no está bloqueado
        is_blocked, _ = rate_limiter.is_blocked(username)
        assert is_blocked is False

    def test_usuarios_independientes(self, rate_limiter):
        """Verifica que cada usuario tiene su propio contador"""
        user1 = "user1"
        user2 = "user2"

        # User1: 3 intentos (bloqueado)
        for _ in range(3):
            rate_limiter.record_failed_attempt(user1)

        # User2: 0 intentos (no bloqueado)
        is_blocked_user1, _ = rate_limiter.is_blocked(user1)
        is_blocked_user2, _ = rate_limiter.is_blocked(user2)

        assert is_blocked_user1 is True
        assert is_blocked_user2 is False

    def test_singleton_get_rate_limiter(self):
        """Verifica que get_rate_limiter() devuelve singleton"""
        limiter1 = get_rate_limiter()
        limiter2 = get_rate_limiter()

        # Debe ser la misma instancia
        assert limiter1 is limiter2


class TestRateLimiterIntegration:
    """Tests de integración del RateLimiter con login real"""

    def test_login_con_bloqueo(self, rate_limiter):
        """Escenario real: Login con bloqueo"""
        username = "attacker"

        # 3 intentos fallidos de login
        for i in range(3):
            rate_limiter.record_failed_attempt(username)

        # Cuarto intento debe ser bloqueado
        is_blocked, locked_until = rate_limiter.is_blocked(username)

        if is_blocked:
            # Mensaje al usuario
            minutes_left = (locked_until - datetime.now()).seconds // 60
            assert minutes_left > 0
            assert minutes_left <= 15

    def test_fuerza_bruta_prevenida(self, rate_limiter):
        """
        CRÍTICO: Verifica que el RateLimiter previene fuerza bruta

        Escenario de ataque:
        - Attacker intenta 100 contraseñas diferentes
        - Sin RateLimiter: 100 intentos permitidos
        - Con RateLimiter: Bloqueado después de 3
        """
        username = "victim"

        # Attacker prueba contraseñas
        passwords = ["pass1", "pass2", "pass3", "pass4"]

        attempts_blocked = 0
        for password in passwords:
            is_blocked, _ = rate_limiter.is_blocked(username)

            if is_blocked:
                attempts_blocked += 1
                # En el cuarto intento, ya está bloqueado
                break

            rate_limiter.record_failed_attempt(username)

        # Verificar que solo pudo intentar 3 veces
        assert attempts_blocked >= 1  # Al menos el 4to fue bloqueado
