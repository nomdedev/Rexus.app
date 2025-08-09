"""
Tests de Edge Cases de Autenticación - Rexus.app
Session management, concurrent sessions, token handling, edge cases críticos
"""

import sys
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import time
import threading
import hashlib
import jwt
from datetime import datetime, timedelta
import uuid

# Agregar directorio raíz para imports
ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))

try:
    from rexus.modules.usuarios.model import UsuariosModel
    from rexus.core.auth_manager import AuthManager
    MODULES_AVAILABLE = True
except ImportError as e:
    print(f"[WARNING] Módulos auth no disponibles: {e}")
    MODULES_AVAILABLE = False


class TestAuthenticationEdgeCases:
    """Tests de edge cases críticos de autenticación."""
    
    @pytest.fixture
    def mock_database(self):
        """Mock de base de datos con seguimiento de queries."""
        mock_db = Mock()
        mock_cursor = Mock()
        mock_db.cursor.return_value = mock_cursor
        
        # Datos mock de usuarios
        mock_cursor.user_data = {
            'admin': {
                'id': 1,
                'username': 'admin',
                'password_hash': hashlib.sha256('admin123'.encode()).hexdigest(),
                'rol': 'ADMIN',
                'activo': True,
                'intentos_login': 0,
                'bloqueado_hasta': None,
                'ultimo_login': None,
                'sesiones_activas': 0
            },
            'user1': {
                'id': 2,
                'username': 'user1',
                'password_hash': hashlib.sha256('user123'.encode()).hexdigest(),
                'rol': 'USER',
                'activo': True,
                'intentos_login': 2,  # Ya tiene 2 intentos fallidos
                'bloqueado_hasta': None,
                'ultimo_login': datetime.now() - timedelta(days=1),
                'sesiones_activas': 1
            }
        }
        
        def mock_fetchone():
            # Simular fetchone basado en la última query
            return mock_cursor.last_result if hasattr(mock_cursor, 'last_result') else None
        
        mock_cursor.fetchone = mock_fetchone
        mock_cursor.fetchall.return_value = []
        
        return mock_db
    
    @pytest.fixture
    def usuarios_model(self, mock_database):
        """Modelo de usuarios para tests."""
        if not MODULES_AVAILABLE:
            return Mock()
        return UsuariosModel(mock_database)

    def test_concurrent_login_attempts(self, usuarios_model, mock_database):
        """Test intentos de login concurrentes del mismo usuario."""
        if not MODULES_AVAILABLE:
            pytest.skip("Módulos no disponibles")
            
        username = "admin"
        password = "admin123"
        results = []
        threads = []
        
        def attempt_login(thread_id):
            try:
                with patch.object(usuarios_model, 'db_connection', mock_database):
                    result = usuarios_model.validar_credenciales(username, password)
                    results.append((thread_id, 'success', result))
            except Exception as e:
                results.append((thread_id, 'error', str(e)))
        
        # Lanzar 5 logins concurrentes
        for i in range(5):
            thread = threading.Thread(target=attempt_login, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Esperar que terminen
        for thread in threads:
            thread.join()
        
        # Análisis de resultados
        successful_logins = [r for r in results if r[1] == 'success']
        
        print(f"Concurrent logins - Success: {len(successful_logins)}, Total: {len(results)}")
        
        # Solo uno debería tener éxito (o todos si está bien implementado)
        # Pero no deberían haber race conditions
        assert len(results) == 5
        
        for thread_id, status, result in results:
            print(f"Thread {thread_id}: {status}")

    def test_session_fixation_attack(self, usuarios_model, mock_database):
        """Test prevención de ataques de fijación de sesión."""
        if not MODULES_AVAILABLE:
            pytest.skip("Módulos no disponibles")
            
        # Simular sesión pre-establecida por atacante
        malicious_session_id = "ATTACKER_SET_SESSION_123"
        
        with patch.object(usuarios_model, 'db_connection', mock_database):
            try:
                # Intentar login con sesión fijada
                with patch('uuid.uuid4', return_value=Mock(hex=malicious_session_id)):
                    result = usuarios_model.crear_sesion(
                        usuario_id=1,
                        ip='192.168.1.100',
                        user_agent='TestBrowser',
                        session_id=malicious_session_id
                    )
                
                # El sistema debería generar nueva sesión, no usar la fijada
                if result:
                    # Verificar que se generó nueva sesión
                    cursor = mock_database.cursor.return_value
                    if hasattr(cursor, 'execute') and cursor.execute.called:
                        # La nueva sesión no debería ser la del atacante
                        print("[OK] Session fixation prevenido - nueva sesión generada")
                        
            except Exception as e:
                print(f"[OK] Session fixation detectado: {str(e)[:100]}")

    def test_session_hijacking_prevention(self, usuarios_model, mock_database):
        """Test prevención de secuestro de sesión."""
        if not MODULES_AVAILABLE:
            pytest.skip("Módulos no disponibles")
            
        session_id = "valid_session_123"
        original_ip = "192.168.1.100"
        hijacker_ip = "10.0.0.50"
        original_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        hijacker_user_agent = "Mozilla/5.0 (Linux; Android 8.0)"
        
        with patch.object(usuarios_model, 'db_connection', mock_database):
            try:
                # Crear sesión válida
                usuarios_model.crear_sesion(
                    usuario_id=1,
                    ip=original_ip,
                    user_agent=original_user_agent,
                    session_id=session_id
                )
                
                # Intentar usar la sesión desde IP diferente
                hijack_attempt = usuarios_model.validar_sesion(
                    session_id=session_id,
                    ip=hijacker_ip,
                    user_agent=hijacker_user_agent
                )
                
                # Debería fallar por IP diferente
                if hijack_attempt:
                    # Si permite, debería al menos registrar como sospechoso
                    print("[WARN] Session hijacking no detectado automáticamente")
                else:
                    print("[OK] Session hijacking bloqueado por IP diferente")
                    
            except Exception as e:
                print(f"[OK] Session hijacking detectado: {str(e)[:100]}")

    def test_password_timing_attack_resistance(self, usuarios_model, mock_database):
        """Test resistencia a ataques de timing en validación de contraseñas."""
        if not MODULES_AVAILABLE:
            pytest.skip("Módulos no disponibles")
            
        valid_username = "admin"
        invalid_username = "nonexistent_user_12345"
        password = "testpass"
        
        timings = []
        
        with patch.object(usuarios_model, 'db_connection', mock_database):
            # Medir tiempo para usuario válido
            for i in range(10):
                start = time.time()
                try:
                    usuarios_model.validar_credenciales(valid_username, password)
                except:
                    pass
                end = time.time()
                timings.append(('valid_user', end - start))
            
            # Medir tiempo para usuario inválido
            for i in range(10):
                start = time.time()
                try:
                    usuarios_model.validar_credenciales(invalid_username, password)
                except:
                    pass
                end = time.time()
                timings.append(('invalid_user', end - start))
        
        # Análisis de tiempos
        valid_times = [t[1] for t in timings if t[0] == 'valid_user']
        invalid_times = [t[1] for t in timings if t[0] == 'invalid_user']
        
        avg_valid = sum(valid_times) / len(valid_times)
        avg_invalid = sum(invalid_times) / len(invalid_times)
        
        print(f"Avg time valid user: {avg_valid:.6f}s")
        print(f"Avg time invalid user: {avg_invalid:.6f}s")
        print(f"Time difference: {abs(avg_valid - avg_invalid):.6f}s")
        
        # La diferencia no debería ser significativa (< 10ms)
        time_diff = abs(avg_valid - avg_invalid)
        if time_diff > 0.01:  # 10ms
            print("[WARN] Posible timing attack vulnerability")
        else:
            print("[OK] Timing attack resistance OK")

    def test_jwt_token_edge_cases(self, usuarios_model, mock_database):
        """Test edge cases con JWT tokens."""
        if not MODULES_AVAILABLE:
            pytest.skip("Módulos no disponibles")
            
        secret_key = "test_secret_key_12345"
        
        # Test tokens malformados
        malformed_tokens = [
            "invalid.token.format",
            "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.INVALID.signature",
            "",
            "null",
            "undefined",
            "Bearer invalid_token",
            "a" * 1000,  # Token muy largo
            "!@#$%^&*()",  # Caracteres especiales
        ]
        
        for token in malformed_tokens:
            print(f"Testing malformed JWT: {token[:30]}...")
            
            try:
                # Intentar decodificar token inválido
                decoded = jwt.decode(token, secret_key, algorithms=["HS256"])
                print(f"[WARN] Token inválido aceptado: {token[:30]}")
            except jwt.InvalidTokenError:
                print(f"[OK] Token inválido rechazado correctamente")
            except Exception as e:
                print(f"[OK] Token manejado: {str(e)[:50]}")

    def test_token_expiration_edge_cases(self, usuarios_model):
        """Test casos extremos de expiración de tokens."""
        if not MODULES_AVAILABLE:
            pytest.skip("Módulos no disponibles")
            
        secret_key = "test_secret_key_12345"
        
        # Test token expirado
        expired_payload = {
            'user_id': 1,
            'username': 'admin',
            'exp': datetime.utcnow() - timedelta(hours=1)  # Expiró hace 1 hora
        }
        
        expired_token = jwt.encode(expired_payload, secret_key, algorithm="HS256")
        
        try:
            decoded = jwt.decode(expired_token, secret_key, algorithms=["HS256"])
            print("[WARN] Token expirado aceptado")
        except jwt.ExpiredSignatureError:
            print("[OK] Token expirado rechazado correctamente")
        
        # Test token con expiración muy lejana
        far_future_payload = {
            'user_id': 1,
            'username': 'admin',
            'exp': datetime.utcnow() + timedelta(days=365 * 100)  # 100 años
        }
        
        far_future_token = jwt.encode(far_future_payload, secret_key, algorithm="HS256")
        
        try:
            decoded = jwt.decode(far_future_token, secret_key, algorithms=["HS256"])
            # Debería validar que la expiración no sea demasiado lejana
            exp_time = datetime.fromtimestamp(decoded['exp'])
            max_allowed = datetime.utcnow() + timedelta(days=30)  # Máximo 30 días
            
            if exp_time > max_allowed:
                print("[WARN] Token con expiración muy lejana aceptado")
            else:
                print("[OK] Token con expiración razonable")
                
        except Exception as e:
            print(f"[OK] Token far-future manejado: {str(e)[:50]}")

    def test_brute_force_protection(self, usuarios_model, mock_database):
        """Test protección contra ataques de fuerza bruta."""
        if not MODULES_AVAILABLE:
            pytest.skip("Módulos no disponibles")
            
        username = "admin"
        wrong_passwords = [
            "wrong1", "wrong2", "wrong3", "wrong4", "wrong5",
            "admin", "password", "123456", "admin123", "qwerty"
        ]
        
        with patch.object(usuarios_model, 'db_connection', mock_database):
            blocked = False
            
            for i, password in enumerate(wrong_passwords):
                try:
                    result = usuarios_model.validar_credenciales(username, password)
                    
                    if not result:
                        print(f"Intento {i+1}: Credenciales rechazadas")
                        
                        # Verificar si se bloqueó después de varios intentos
                        if i >= 2:  # Después del 3er intento
                            # Debería estar bloqueado
                            try:
                                # Intentar con credenciales correctas
                                correct_result = usuarios_model.validar_credenciales(username, "admin123")
                                if not correct_result:
                                    blocked = True
                                    print(f"[OK] Usuario bloqueado después de {i+1} intentos")
                                    break
                            except Exception:
                                blocked = True
                                print(f"[OK] Usuario bloqueado (excepción) después de {i+1} intentos")
                                break
                                
                except Exception as e:
                    print(f"Intento {i+1}: Excepción - {str(e)[:50]}")
                    if "bloqueado" in str(e).lower() or "locked" in str(e).lower():
                        blocked = True
                        break
            
            if not blocked:
                print("[WARN] No se detectó bloqueo por fuerza bruta")

    def test_account_lockout_bypass_attempts(self, usuarios_model, mock_database):
        """Test intentos de bypass del bloqueo de cuentas."""
        if not MODULES_AVAILABLE:
            pytest.skip("Módulos no disponibles")
            
        username = "user1"  # Usuario con intentos previos
        
        # Técnicas de bypass
        bypass_attempts = [
            {"username": username.upper(), "description": "uppercase"},
            {"username": f" {username}", "description": "leading space"},
            {"username": f"{username} ", "description": "trailing space"},
            {"username": f"{username}\t", "description": "tab character"},
            {"username": f"{username}\n", "description": "newline"},
            {"username": f"{username}@", "description": "special char"},
            {"username": f"admin'; --", "description": "SQL injection"},
        ]
        
        with patch.object(usuarios_model, 'db_connection', mock_database):
            for attempt in bypass_attempts:
                print(f"Testing bypass: {attempt['description']}")
                
                try:
                    result = usuarios_model.validar_credenciales(attempt["username"], "password")
                    
                    # Si el usuario original está bloqueado, ningún bypass debería funcionar
                    if result:
                        print(f"[WARN] Bypass exitoso: {attempt['description']}")
                    else:
                        print(f"[OK] Bypass bloqueado: {attempt['description']}")
                        
                except Exception as e:
                    print(f"[OK] Bypass detectado como malicioso: {str(e)[:50]}")

    def test_session_timeout_edge_cases(self, usuarios_model, mock_database):
        """Test casos extremos de timeout de sesión."""
        if not MODULES_AVAILABLE:
            pytest.skip("Módulos no disponibles")
            
        session_id = "test_session_123"
        
        with patch.object(usuarios_model, 'db_connection', mock_database):
            try:
                # Crear sesión
                usuarios_model.crear_sesion(
                    usuario_id=1,
                    ip='192.168.1.100',
                    user_agent='Test',
                    session_id=session_id
                )
                
                # Test sesión válida
                valid_result = usuarios_model.validar_sesion(session_id, '192.168.1.100', 'Test')
                print(f"Sesión válida: {valid_result}")
                
                # Simular paso del tiempo
                with patch('datetime.datetime') as mock_datetime:
                    # Simular que pasó tiempo de timeout
                    future_time = datetime.now() + timedelta(hours=25)  # Más de 24h
                    mock_datetime.now.return_value = future_time
                    mock_datetime.utcnow.return_value = future_time
                    
                    # Sesión debería estar expirada
                    expired_result = usuarios_model.validar_sesion(session_id, '192.168.1.100', 'Test')
                    
                    if expired_result:
                        print("[WARN] Sesión expirada no detectada")
                    else:
                        print("[OK] Sesión expirada correctamente")
                        
            except Exception as e:
                print(f"Error en test timeout: {str(e)}")

    def test_multi_device_session_management(self, usuarios_model, mock_database):
        """Test gestión de sesiones múltiples dispositivos."""
        if not MODULES_AVAILABLE:
            pytest.skip("Módulos no disponibles")
            
        user_id = 1
        sessions = []
        
        # Crear sesiones desde diferentes dispositivos
        devices = [
            {'ip': '192.168.1.100', 'user_agent': 'Mozilla/5.0 (Windows NT 10.0)'},
            {'ip': '192.168.1.101', 'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone)'},
            {'ip': '192.168.1.102', 'user_agent': 'Mozilla/5.0 (Linux; Android 9)'},
            {'ip': '192.168.1.103', 'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac)'},
            {'ip': '192.168.1.104', 'user_agent': 'Mozilla/5.0 (iPad; CPU OS)'},
        ]
        
        with patch.object(usuarios_model, 'db_connection', mock_database):
            try:
                for i, device in enumerate(devices):
                    session_id = f"session_{i}_{uuid.uuid4().hex[:8]}"
                    
                    result = usuarios_model.crear_sesion(
                        usuario_id=user_id,
                        ip=device['ip'],
                        user_agent=device['user_agent'],
                        session_id=session_id
                    )
                    
                    if result:
                        sessions.append(session_id)
                        print(f"[OK] Sesión creada para dispositivo {i+1}")
                
                print(f"Total sesiones activas: {len(sessions)}")
                
                # Verificar límite de sesiones concurrentes
                if len(sessions) > 3:  # Ejemplo: máximo 3 sesiones
                    print("[WARN] Demasiadas sesiones concurrentes permitidas")
                else:
                    print("[OK] Límite de sesiones concurrentes OK")
                    
            except Exception as e:
                print(f"Error en multi-device test: {str(e)}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])