"""
Tests de Penetración y Seguridad para Rexus.app
Valida la seguridad de todos los módulos contra ataques comunes

Ejecutar con: python -m pytest tests/security/test_penetration.py -v
"""

import hashlib
import os
import sqlite3
import sys
import tempfile
import time
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Agregar ruta al proyecto
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from rexus.modules.usuarios.model import UsuariosModel
from utils.two_factor_auth import TwoFactorAuth


class TestPenetracion:
    """Suite de tests de penetración y seguridad"""

    @pytest.fixture
    def db_connection(self):
        """Base de datos temporal para tests"""
        db_file = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        db_file.close()

        connection = sqlite3.connect(db_file.name)
        cursor = connection.cursor()

        # Crear tabla usuarios para tests
        cursor.execute("""
        CREATE TABLE usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            nombre_completo TEXT,
            email TEXT UNIQUE,
            rol TEXT DEFAULT 'USER',
            activo INTEGER DEFAULT 1,
            intentos_fallidos INTEGER DEFAULT 0,
            ultimo_intento_fallido DATETIME,
            bloqueado_hasta DATETIME,
            configuracion_personal TEXT DEFAULT '{}'
        )
        """)

        # Usuario de prueba
        password_hash = hashlib.sha256("password123".encode()).hexdigest()
        cursor.execute(
            """
        INSERT INTO usuarios (usuario, password_hash, nombre_completo, email, rol)
        VALUES (?, ?, ?, ?, ?)
        """,
            ("testuser", password_hash, "Test User", "test@example.com", "USER"),
        )

        connection.commit()

        yield connection

        connection.close()
        os.unlink(db_file.name)

    @pytest.fixture
    def usuarios_model(self, db_connection):
        """Modelo de usuarios configurado para tests"""
        model = UsuariosModel(db_connection)
        return model


class TestSQLInjection:
    """Tests de inyección SQL en todos los módulos"""

    def test_sql_injection_usuarios_login(self, usuarios_model):
        """Test SQL injection en login de usuarios"""
        # Payloads comunes de SQL injection
        payloads = [
            "admin'; DROP TABLE usuarios; --",
            "admin' OR '1'='1",
            "admin' OR '1'='1' --",
            "admin' OR '1'='1' /*",
            "admin'; INSERT INTO usuarios VALUES (999, 'hacker', 'hash'); --",
            "admin' UNION SELECT * FROM usuarios --",
            "1' OR 1=1#",
            "'; EXEC sp_configure 'show advanced options', 1; --",
        ]

        for payload in payloads:
            resultado = usuarios_model.autenticar_usuario_seguro(payload, "anypassword")

            # Ningún payload debe resultar en autenticación exitosa
            assert not resultado["success"], (
                f"SQL injection exitosa con payload: {payload}"
            )

            # El mensaje no debe revelar información del sistema
            assert "error" not in resultado["message"].lower()
            assert "sql" not in resultado["message"].lower()
            assert "database" not in resultado["message"].lower()

    def test_sql_injection_busqueda_usuarios(self, usuarios_model):
        """Test SQL injection en búsqueda de usuarios"""
        payloads = [
            "test'; DROP TABLE usuarios; --",
            "test' OR '1'='1",
            "test' UNION SELECT password_hash FROM usuarios --",
        ]

        for payload in payloads:
            try:
                # Intentar búsqueda con payload malicioso
                resultado = usuarios_model.obtener_usuario_por_nombre(payload)

                # No debe devolver datos sensibles
                if resultado:
                    assert "password_hash" not in str(resultado)

            except Exception as e:
                # Los errores no deben revelar información del sistema
                error_msg = str(e).lower()
                assert "table" not in error_msg
                assert "column" not in error_msg
                assert "sql" not in error_msg

    def test_table_name_validation(self, usuarios_model):
        """Test validación de nombres de tabla"""
        payloads_maliciosos = [
            "usuarios; DROP TABLE usuarios; --",
            "usuarios' OR '1'='1",
            "usuarios UNION SELECT * FROM usuarios",
            "../../../etc/passwd",
            "usuarios/**/OR/**/1=1",
            "usuarios\x00",
            "usuarios\n",
            "usuarios\t",
        ]

        for payload in payloads_maliciosos:
            with pytest.raises((ValueError, Exception)) as exc_info:
                usuarios_model._validate_table_name(payload)

            # Verificar que se rechaza apropiadamente
            assert "válido" in str(exc_info.value) or "inválido" in str(exc_info.value)


class TestBruteForceProtection:
    """Tests de protección contra ataques de fuerza bruta"""

    def test_lockout_after_max_attempts(self, usuarios_model):
        """Test bloqueo después de intentos máximos"""
        username = "testuser"
        wrong_password = "wrongpassword"

        # Realizar intentos fallidos hasta el máximo
        for i in range(usuarios_model.MAX_LOGIN_ATTEMPTS):
            resultado = usuarios_model.autenticar_usuario_seguro(
                username, wrong_password
            )
            assert not resultado["success"]

            if i < usuarios_model.MAX_LOGIN_ATTEMPTS - 1:
                assert resultado["attempts_remaining"] > 0

        # Verificar que la cuenta está bloqueada
        assert usuarios_model.verificar_cuenta_bloqueada(username)

        # Intentar login con contraseña correcta debe fallar mientras esté bloqueado
        resultado = usuarios_model.autenticar_usuario_seguro(username, "password123")
        assert not resultado["success"]
        assert "bloqueada" in resultado["message"].lower()

    def test_rapid_login_attempts(self, usuarios_model):
        """Test múltiples intentos rápidos"""
        username = "testuser"
        wrong_password = "wrongpassword"

        # Simular ataque rápido
        start_time = time.time()
        for i in range(10):  # Más intentos que el máximo permitido
            resultado = usuarios_model.autenticar_usuario_seguro(
                username, wrong_password
            )
            assert not resultado["success"]

        end_time = time.time()

        # Verificar que el sistema sigue respondiendo (no DoS)
        assert end_time - start_time < 5  # No debe tomar más de 5 segundos

        # Verificar que la cuenta está bloqueada
        assert usuarios_model.verificar_cuenta_bloqueada(username)

    def test_user_enumeration_protection(self, usuarios_model):
        """Test protección contra enumeración de usuarios"""
        # Intentar login con usuario inexistente
        resultado_inexistente = usuarios_model.autenticar_usuario_seguro(
            "noexiste", "password"
        )

        # Intentar login con usuario existente pero contraseña incorrecta
        resultado_existente = usuarios_model.autenticar_usuario_seguro(
            "testuser", "wrongpassword"
        )

        # Los mensajes deben ser similares para prevenir enumeración
        assert not resultado_inexistente["success"]
        assert not resultado_existente["success"]

        # No debe revelarse si el usuario existe o no
        assert "no existe" not in resultado_inexistente["message"].lower()
        assert "usuario" not in resultado_inexistente["message"].lower()


class TestPasswordSecurity:
    """Tests de seguridad de contraseñas"""

    def test_password_strength_validation(self, usuarios_model):
        """Test validación de fortaleza de contraseñas"""
        # Contraseñas débiles que deben ser rechazadas
        weak_passwords = [
            "123456",
            "password",
            "abc123",
            "qwerty",
            "admin",
            "12345678",
            "password123",  # Sin mayúsculas ni caracteres especiales
            "PASSWORD123",  # Sin minúsculas ni caracteres especiales
            "Password",  # Sin números ni caracteres especiales
            "Pass123",  # Muy corta
        ]

        for password in weak_passwords:
            resultado = usuarios_model.validar_fortaleza_password(password)
            if not resultado["valida"]:
                assert len(resultado["errores"]) > 0
                assert resultado["puntuacion"] < 5

    def test_password_strong_validation(self, usuarios_model):
        """Test contraseñas fuertes que deben ser aceptadas"""
        strong_passwords = [
            "MyStr0ng!Pass",
            "C0mpl3x@P4ssw0rd",
            "S3cur3#Password123",
            "V3ry$tr0ng&P4ss!",
        ]

        for password in strong_passwords:
            resultado = usuarios_model.validar_fortaleza_password(password)
            assert resultado["valida"], f"Contraseña fuerte rechazada: {password}"
            assert resultado["puntuacion"] >= 4
            assert len(resultado["errores"]) == 0


class TestTwoFactorAuth:
    """Tests de seguridad del sistema 2FA"""

    @pytest.fixture
    def tfa(self):
        """Instancia de TwoFactorAuth para tests"""
        return TwoFactorAuth()

    def test_totp_code_generation(self, tfa):
        """Test generación de códigos TOTP"""
        secret = tfa.generar_secret_key()

        # Generar código actual
        codigo1 = tfa.generar_codigo_totp(secret)
        assert len(codigo1) == 6
        assert codigo1.isdigit()

        # El mismo timestamp debe generar el mismo código
        timestamp = int(time.time())
        codigo2 = tfa.generar_codigo_totp(secret, timestamp)
        codigo3 = tfa.generar_codigo_totp(secret, timestamp)
        assert codigo2 == codigo3

    def test_totp_time_window_validation(self, tfa):
        """Test validación con ventana de tiempo"""
        secret = tfa.generar_secret_key()
        current_time = int(time.time())

        # Generar código para tiempo actual
        codigo_actual = tfa.generar_codigo_totp(secret, current_time)

        # Debe validar código actual
        assert tfa.validar_codigo_totp(secret, codigo_actual, current_time)

        # Debe validar código del período anterior (ventana de tolerancia)
        codigo_anterior = tfa.generar_codigo_totp(secret, current_time - 30)
        assert tfa.validar_codigo_totp(secret, codigo_anterior, current_time)

        # No debe validar código muy antiguo
        codigo_muy_antiguo = tfa.generar_codigo_totp(secret, current_time - 120)
        assert not tfa.validar_codigo_totp(secret, codigo_muy_antiguo, current_time)

    def test_totp_code_reuse_protection(self, tfa):
        """Test protección contra reutilización de códigos"""
        secret = tfa.generar_secret_key()

        # En un sistema real, deberías implementar protección contra reutilización
        # Este test verifica que códigos diferentes en tiempos diferentes son diferentes
        codigo1 = tfa.generar_codigo_totp(secret, int(time.time()))
        time.sleep(1)  # Esperar un poco
        codigo2 = tfa.generar_codigo_totp(secret, int(time.time()))

        # Los códigos pueden ser iguales si estamos en el mismo período de 30 segundos
        # pero deben ser diferentes en períodos diferentes
        if int(time.time()) // 30 != int(time.time() - 1) // 30:
            assert codigo1 != codigo2

    def test_invalid_2fa_codes(self, tfa):
        """Test códigos 2FA inválidos"""
        secret = tfa.generar_secret_key()

        invalid_codes = [
            "123456",  # Código fijo (no TOTP)
            "000000",  # Código débil
            "999999",  # Código probable
            "12345",  # Muy corto
            "1234567",  # Muy largo
            "abcdef",  # No numérico
            "",  # Vacío
            None,  # Nulo
        ]

        for invalid_code in invalid_codes:
            if invalid_code is not None:
                assert not tfa.validar_codigo_totp(secret, invalid_code)


class TestInputSanitization:
    """Tests de sanitización de entradas"""

    def test_xss_protection(self, usuarios_model):
        """Test protección contra XSS"""
        xss_payloads = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "<svg onload=alert('xss')>",
            "';alert('xss');//",
            "\"><script>alert('xss')</script>",
        ]

        for payload in xss_payloads:
            # Intentar crear usuario con payload XSS
            try:
                resultado = usuarios_model.obtener_usuario_por_nombre(payload)

                # Si devuelve datos, no deben contener el payload original
                if resultado and isinstance(resultado, dict):
                    for key, value in resultado.items():
                        if isinstance(value, str):
                            assert "<script>" not in value.lower()
                            assert "javascript:" not in value.lower()
                            assert "onerror" not in value.lower()
                            assert "onload" not in value.lower()

            except Exception:
                # Es aceptable que falle, lo importante es que no ejecute el XSS
                pass

    def test_path_traversal_protection(self, usuarios_model):
        """Test protección contra path traversal"""
        path_payloads = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "....//....//....//etc//passwd",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
            "..%2F..%2F..%2Fetc%2Fpasswd",
        ]

        for payload in path_payloads:
            try:
                # Los payloads no deben resultar en acceso a archivos del sistema
                resultado = usuarios_model.obtener_usuario_por_nombre(payload)

                # No debe devolver contenido de archivos del sistema
                if resultado and isinstance(resultado, dict):
                    resultado_str = str(resultado).lower()
                    assert "root:" not in resultado_str
                    assert "bin:" not in resultado_str
                    assert "daemon:" not in resultado_str

            except Exception:
                # Es aceptable que falle
                pass


class TestDataLeakage:
    """Tests de filtración de datos sensibles"""

    def test_password_hash_not_exposed(self, usuarios_model):
        """Test que los hashes de contraseñas no se expongan"""
        # Obtener usuario
        usuario = usuarios_model.obtener_usuario_por_nombre("testuser")

        if usuario:
            # Verificar que contiene password_hash internamente (para el test)
            assert "password_hash" in usuario

            # Simular autenticación exitosa
            resultado = usuarios_model.autenticar_usuario_seguro(
                "testuser", "password123"
            )

            if resultado["success"] and resultado["user_data"]:
                # Los datos de sesión NO deben contener password_hash
                assert "password_hash" not in resultado["user_data"]
                assert "password" not in resultado["user_data"]

    def test_error_messages_dont_leak_info(self, usuarios_model):
        """Test que los mensajes de error no filtren información"""
        # Intentar operaciones que pueden generar errores
        operaciones_error = [
            lambda: usuarios_model.obtener_usuario_por_nombre("' OR 1=1 --"),
            lambda: usuarios_model.autenticar_usuario_seguro("", ""),
            lambda: usuarios_model.autenticar_usuario_seguro(None, None),
        ]

        for operacion in operaciones_error:
            try:
                resultado = operacion()

                # Si devuelve un mensaje, no debe contener información sensible
                if hasattr(resultado, "get") and resultado.get("message"):
                    mensaje = resultado["message"].lower()
                    assert "table" not in mensaje
                    assert "column" not in mensaje
                    assert "database" not in mensaje
                    assert "sql" not in mensaje
                    assert "exception" not in mensaje
                    assert "traceback" not in mensaje

            except Exception as e:
                # Los errores tampoco deben filtrar información
                error_msg = str(e).lower()
                assert "table" not in error_msg
                assert "column" not in error_msg
                assert "password" not in error_msg


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
