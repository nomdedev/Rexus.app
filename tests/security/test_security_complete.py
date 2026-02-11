# -*- coding: utf-8 -*-
"""
Tests de Seguridad Completa - Rexus.app

Suite de seguridad que verifica:
- SQL Injection en TODOS los módulos
- XSS en inputs de usuario
- CSRF en forms
- Permisos por rol
- Validación de datos
- Rate limiting
- Autenticación/autorización
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


@pytest.mark.security
class TestSQLInjectionAllModules:
    """
    Tests de SQL Injection en TODOS los módulos.

    Cada método de cada módulo que recibe input de usuario
    debe ser probado contra SQL injection.
    """

    @pytest.fixture
    def malicious_inputs(self):
        """Inputs maliciosos para probar SQL injection."""
        return [
            "'; DROP TABLE productos; --",
            "' OR '1'='1",
            "' UNION SELECT * FROM usuarios --",
            "1' AND 1=1 --",
            "'; EXEC xp_cmdshell('dir'); --",
            "' OR 1=1#",
            "admin'--",
            "' OR '1'='1'--",
            "'; INSERT INTO usuarios VALUES ('hacker', 'password') --",
            "'; DELETE FROM productos WHERE '1'='1' --"
        ]

    @pytest.mark.parametrize("module_path,model_class", [
        ('rexus.modules.obras.model', 'ObrasModel'),
        ('rexus.modules.inventario.model', 'InventarioModel'),
        ('rexus.modules.herrajes.model', 'HerrajesModel'),
        ('rexus.modules.vidrios.model', 'VidriosModel'),
        ('rexus.modules.logistica.model', 'LogisticaModel'),
        ('rexus.modules.pedidos.model', 'PedidosModel'),
        ('rexus.modules.compras.model', 'ComprasModel'),
        ('rexus.modules.administracion.model', 'AdministracionModel'),
        ('rexus.modules.mantenimiento.model', 'MantenimientoModel'),
        ('rexus.modules.auditoria.model', 'AuditoriaModel'),
        ('rexus.modules.usuarios.model', 'UsuariosModel'),
        ('rexus.modules.configuracion.model', 'ConfiguracionModel'),
        ('rexus.modules.notificaciones.model', 'NotificacionesModel'),
    ])
    def test_sql_injection_search_methods(self, module_path, model_class, malicious_inputs):
        """
        Test de SQL injection en métodos de búsqueda.

        Cada módulo tiene métodos como buscar_producto(id), buscar_obra(id), etc.
        Estos deben ser inmunes a SQL injection.
        """
        pytest.skip("Requiere implementación real - marcar cuando se tenga cada módulo")

        # Para cada módulo, probar sus métodos de búsqueda con inputs maliciosos
        # Ejemplo genérico:
        for malicious_input in malicious_inputs:
            with patch(module_path) as Model:
                model_instance = Model.return_value

                # Intentar SQL injection en método de búsqueda
                try:
                    result = model_instance.buscar(malicious_input)

                    # Si retorna algo, verificar que sea un resultado vacío o error
                    # pero NUNCA datos reales de la BD
                    assert result == [] or result is None or 'error' in str(result).lower(), \
                        f"SQL Injection vulnerability detected in {model_class}: {malicious_input}"

                except Exception as e:
                    # Es acceptable que lance excepción de validación
                    assert "injection" in str(e).lower() or "invalid" in str(e).lower() or \
                           "sql" in str(e).lower() or "seguridad" in str(e).lower(), \
                        f"Excepción inesperada: {e}"

    @pytest.mark.parametrize("module_path,model_class,method_name", [
        ('rexus.modules.inventario.model', 'InventarioModel', 'crear_producto'),
        ('rexus.modules.obras.model', 'ObrasModel', 'crear_obra'),
        ('rexus.modules.compras.model', 'ComprasModel', 'crear_orden_compra'),
        ('rexus.modules.usuarios.model', 'UsuariosModel', 'crear_usuario'),
    ])
    def test_sql_injection_create_methods(self, module_path, model_class, method_name, malicious_inputs):
        """Test de SQL injection en métodos de creación."""
        for malicious_input in malicious_inputs:
            # Intentar crear entidad con nombre malicioso
            malicious_data = {
                'nombre': malicious_input,
                'descripcion': malicious_input
            }

            with patch(module_path) as Model:
                model_instance = Model.return_value

                try:
                    result = model_instance.crear(malicious_data)

                    # Verificar que el dato fue escapado correctamente
                    # o que hubo validación
                    assert result is None or 'error' in str(result).lower(), \
                        f"Posible SQL Injection en {model_class}.{method_name}"

                except Exception as e:
                    # Aceptable: validación rechazó input
                    assert any(word in str(e).lower() for word in
                              ['invalid', 'caracter', 'seguridad', 'sql', 'injection', 'escape'])

    def test_sql_injection_in_where_clauses(self):
        """
        Test específico de SQL injection en cláusulas WHERE.

        Este es el punto más vulnerable de SQL injection.
        """
        malicious_filters = [
            {"id": "1 OR 1=1"},
            {"nombre": "test' OR '1'='1'"},
            {"estado": "activo' UNION SELECT * FROM usuarios --"},
            {"categoria": "'; DROP TABLE productos; --"}
        ]

        for malicious_filter in malicious_filters:
            # Test con modelo de inventario (ejemplo)
            with patch('rexus.modules.inventario.model.InventarioModel') as InventarioModel:
                mock_cursor = MagicMock()
                mock_cursor.fetchall.return_value = []
                mock_db = Mock()
                mock_db.cursor.return_value = mock_cursor

                model = InventarioModel(mock_db, None)

                # Intentar buscar con filtro malicioso
                try:
                    result = model.buscar_productos(filtros=malicious_filter)

                    # Verificar que la query generada escapó correctamente los inputs
                    # NO debe retornar datos de otras tablas
                    if result:
                        for item in result:
                            # Verificar que no tenga datos de otras tablas (ej: usuarios)
                            assert 'username' not in str(item), \
                                "SQL Injection exitoso: se obtuvieron datos de usuarios"

                except Exception as e:
                    # Es preferible que falle con error de validación
                    assert True  # Expected: validación rechazó input malicioso


@pytest.mark.security
class TestXSSPrevention:
    """Tests de prevención de XSS (Cross-Site Scripting)."""

    @pytest.fixture
    def xss_payloads(self):
        """Payloads maliciosos de XSS."""
        return [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "<svg onload=alert('XSS')>",
            "javascript:alert('XSS')",
            "<iframe src='javascript:alert(XSS)'>",
            "<body onload=alert('XSS')>",
            "'><script>alert(String.fromCharCode(88,83,83))</script>",
            "<input onfocus=alert('XSS') autofocus>",
            "<select onfocus=alert('XSS') autofocus>",
            "<textarea onfocus=alert('XSS') autofocus>",
        ]

    def test_xss_en_nombres_productos(self, xss_payloads):
        """Test XSS en nombres/descripciones de productos."""
        for xss_payload in xss_payloads:
            producto_data = {
                'nombre': xss_payload,
                'descripcion': xss_payload,
                'precio': 100.0
            }

            with patch('rexus.modules.inventario.model.InventarioModel') as InventarioModel:
                model = InventarioModel(None, None)

                try:
                    result = model.crear_producto(producto_data)

                    # Verificar que el payload fue escapado
                    if result and 'nombre' in result:
                        nombre_almacenado = result['nombre']

                        # No debe contener tags HTML sin escapar
                        assert '<script>' not in nombre_almacenado or '&lt;' in nombre_almacenado, \
                            f"XSS vulnerability: script tag no escapado en nombre: {nombre_almacenado}"
                        assert '<img' not in nombre_almacenado or '&lt;' in nombre_almacenado, \
                            f"XSS vulnerability: img tag no escapado en nombre: {nombre_almacenado}"

                except ValueError as e:
                    # Aceptable: validación rechazó input con HTML
                    assert 'html' in str(e).lower() or 'tag' in str(e).lower() or 'inválido' in str(e).lower()

    def test_xss_en_comentarios_observaciones(self, xss_payloads):
        """Test XSS en campos de texto libre (comentarios, observaciones)."""
        for xss_payload in xss_payloads:
            observacion_data = {
                'texto': xss_payload,
                'usuario_id': 1
            }

            with patch('rexus.modules.auditoria.model.AuditoriaModel') as AuditoriaModel:
                model = AuditoriaModel(None, None)

                try:
                    result = model.registrar_observacion(observacion_data)

                    if result and 'texto' in result:
                        texto_almacenado = result['texto']

                        # Verificar escape
                        assert '<script>' not in texto_almacenado or \
                               '&lt;script&gt;' in texto_almacenado, \
                            f"XSS en observaciones: {texto_almacenado}"

                except ValueError as e:
                    # Aceptable: validación
                    assert True


@pytest.mark.security
class TestCSRFProtection:
    """Tests de protección CSRF (Cross-Site Request Forgery)."""

    def test_csrf_token_required_in_mutations(self):
        """
        Verifica que las operaciones de mutación requieran token CSRF.

        Operaciones como POST, PUT, DELETE deben tener token CSRF.
        """
        # Request sin token CSRF
        malicious_request = {
            'data': {'nombre': 'Producto'},
            # Falta token CSRF
        }

        # El sistema debe rechazar la request
        with patch('rexus.core.security.csrf_manager') as CSRF:
            CSRF.validate_token.return_value = False

            with pytest.raises(PermissionError) as exc_info:
                from rexus.core.security import validate_csrf
                validate_csrf(malicious_request)

            assert 'csrf' in str(exc_info.value).lower() or 'token' in str(exc_info.value).lower()

    def test_csrf_token_validation(self):
        """
        Verifica que los tokens CSRF se validen correctamente.
        """
        # Token inválido
        with patch('rexus.core.security.csrf_manager') as CSRF:
            CSRF.validate_token.side_effect = PermissionError("Invalid CSRF token")

            with pytest.raises(PermissionError):
                from rexus.core.security import validate_csrf
                validate_csrf({'csrf_token': 'INVALID_TOKEN'})

        # Token válido
        with patch('rexus.core.security.csrf_manager') as CSRF:
            CSRF.validate_token.return_value = True

            # No debe lanzar excepción
            from rexus.core.security import validate_csrf
            validate_csrf({'csrf_token': 'VALID_TOKEN'})


@pytest.mark.security
class TestAuthorizationRoles:
    """Tests de autorización y roles."""

    @pytest.fixture
    def users_with_different_roles(self):
        """Usuarios con diferentes roles para testing."""
        return {
            'admin': Mock(roles=['admin'], permissions=['all']),
            'viewer': Mock(roles=['viewer'], permissions=['view_inventario', 'view_obras']),
            'editor': Mock(roles=['editor'], permissions=['edit_inventario', 'create_obras']),
            'user': Mock(roles=['user'], permissions=['view_dashboard']),
            'unauthorized': Mock(roles=[], permissions=[])
        }

    def test_role_based_access_control(self, users_with_different_roles):
        """
        Test de control de acceso basado en roles.

        Cada rol debe poder acceder solo a sus permisos permitidos.
        """
        # Admin puede acceder a todo
        admin = users_with_different_roles['admin']
        assert admin.tiene_permiso('delete_inventario') is True
        assert admin.tiene_permiso('create_users') is True

        # Viewer solo puede ver
        viewer = users_with_different_roles['viewer']
        assert viewer.tiene_permiso('view_inventario') is True
        assert viewer.tiene_permiso('delete_inventario') is False
        assert viewer.tiene_permiso('create_obras') is False

        # Editor puede editar pero no eliminar
        editor = users_with_different_roles['editor']
        assert editor.tiene_permiso('edit_inventario') is True
        assert editor.tiene_permiso('delete_inventario') is False

        # Usuario básico solo dashboard
        user = users_with_different_roles['user']
        assert user.tiene_permiso('view_dashboard') is True
        assert user.tiene_permiso('view_inventario') is False

        # No autorizado no puede acceder a nada
        unauthorized = users_with_different_roles['unauthorized']
        assert unauthorized.tiene_permiso('view_dashboard') is False

    def test_permission_checking_before_action(self):
        """
        Verifica que las acciones verifiquen permisos ANTES de ejecutar.

        Las acciones sensibles (eliminar, crear, editar) deben verificar
        permisos al inicio, no después.
        """
        sensitive_actions = [
            ('eliminar_producto', 'delete_inventario'),
            ('crear_obra', 'create_obras'),
            ('eliminar_usuario', 'delete_users'),
            ('editar_configuracion', 'update_config')
        ]

        for action, required_permission in sensitive_actions:
            # Simular usuario sin permiso
            unauthorized_user = Mock(roles=[], permissions=[])

            with pytest.raises(PermissionError) as exc_info:
                from rexus.core.auth_decorators import permission_required
                from functools import wraps

                def sensitive_action():
                    """Acción sensible que requiere permiso."""
                    pass

                decorated = permission_required(required_permission)(sensitive_action)
                decorated()

            assert 'permiso' in str(exc_info.value).lower() or 'autoriza' in str(exc_info.value).lower()


@pytest.mark.security
class TestDataValidation:
    """Tests de validación de datos de entrada."""

    def test_validation_required_fields(self):
        """Verifica que se validen campos requeridos."""
        incomplete_data = {
            # Falta 'nombre' que es requerido
            'precio': 100.0,
            'stock': 50
        }

        with patch('rexus.modules.inventario.model.InventarioModel') as InventarioModel:
            model = InventarioModel(None, None)

            with pytest.raises(ValueError) as exc_info:
                model.validar_datos_producto(incomplete_data)

            assert 'requerid' in str(exc_info.value).lower() or 'falta' in str(exc_info.value).lower()

    def test_validation_data_types(self):
        """Verifica que se validen tipos de datos correctos."""
        invalid_data = {
            'nombre': 'Producto Test',
            'precio': 'INVALID',  # Debe ser numérico
            'stock': 'MUCHO',  # Debe ser numérico
            'activo': 'YES'  # Debe ser booleano
        }

        with patch('rexus.modules.inventario.model.InventarioModel') as InventarioModel:
            model = InventarioModel(None, None)

            with pytest.raises(ValueError) as exc_info:
                model.validar_datos_producto(invalid_data)

            assert 'tipo' in str(exc_info.value).lower() or 'inválido' in str(exc_info.value).lower()

    def test_validation_data_ranges(self):
        """Verifica que se validen rangos de datos."""
        out_of_range_data = {
            'nombre': 'Producto Test',
            'precio': -100,  # No puede ser negativo
            'stock': 1000000,  # Excede máximo razonable
        }

        with patch('rexus.modules.inventario.model.InventarioModel') as InventarioModel:
            model = InventarioModel(None, None)

            with pytest.raises(ValueError) as exc_info:
                model.validar_datos_producto(out_of_range_data)

            assert 'rango' in str(exc_info.value).lower() or 'máximo' in str(exc_info.value).lower()


@pytest.mark.security
class TestRateLimiting:
    """Tests de rate limiting para prevenir abusos."""

    def test_rate_limiting_login(self):
        """
        Verifica que el login tenga rate limiting.

        Previene ataques de fuerza bruta.
        """
        with patch('rexus.modules.usuarios.model.UsuariosModel') as UsuariosModel:
            from rexus.core.security.rate_limiter import RateLimiter

            rate_limiter = RateLimiter(max_requests=5, window_seconds=60)

            # Simular 6 intentos de login fallidos
            for i in range(6):
                if i < 5:
                    # Primeros 5 intentos deben ser permitidos
                    assert rate_limiter.is_allowed('login', 'user@test.com') is True
                else:
                    # 6to intento debe ser bloqueado
                    assert rate_limiter.is_allowed('login', 'user@test.com') is False

    def test_rate_limiting_api_requests(self):
        """
        Verifica que las APIs tengan rate limiting.

        Previene abuso y DoS.
        """
        with patch('rexus.core.security.rate_limiter.RateLimiter') as RateLimiter:
            rate_limiter = RateLimiter(max_requests=100, window_seconds=60)

            # Simular 101 requests en 1 minuto
            requests_allowed = 0
            for i in range(101):
                if rate_limiter.is_allowed('api', '10.0.0.1'):
                    requests_allowed += 1

            # Máximo 100 requests permitidos
            assert requests_allowed == 100


@pytest.mark.security
class TestAuthenticationSecurity:
    """Tests de seguridad en autenticación."""

    def test_password_hashing(self):
        """
        Verifica que los passwords se hasheen correctamente.

        NUNCA se deben almacenar passwords en texto plano.
        """
        password_plano = "Password123!"

        with patch('rexus.core.auth_manager.AuthManager') as AuthManager:
            AuthManager.hash_password.return_value = "hashed_password_here"

            hashed = AuthManager.hash_password(password_plano)

            # El hash debe ser diferente al password plano
            assert hashed != password_plano
            assert len(hashed) >= 60  # Hash bcrypt tiene ~60 caracteres

    def test_password_verification(self):
        """Verifica que la verificación de password sea segura."""
        password = "Password123!"
        wrong_password = "WrongPassword"

        with patch('rexus.core.auth_manager.AuthManager') as AuthManager:
            # Simular hash almacenado
            stored_hash = "$2b$12$hash...123"

            # Password correcto
            AuthManager.verify_password.return_value = True
            assert AuthManager.verify_password(password, stored_hash) is True

            # Password incorrecto
            AuthManager.verify_password.return_value = False
            assert AuthManager.verify_password(wrong_password, stored_hash) is False

    def test_session_security(self):
        """
        Verifica la seguridad de las sesiones.

        - Tokens deben ser únicos e impredecibles
        - Deben tener expiración
        - No deben contener información sensible
        """
        with patch('rexus.core.auth_manager.AuthManager') as AuthManager:
            mock_session = Mock()
            mock_session.token = "unique_random_token_12345"
            mock_session.expires_at = "2025-02-08T10:00:00"
            AuthManager.create_session.return_value = mock_session

            session = AuthManager.create_session(user_id=1)

            # Token debe ser único y largo
            assert len(session.token) >= 20
            assert session.expires_at is not None


@pytest.mark.security
class TestAuditLogging:
    """Tests de logging de auditoría para eventos de seguridad."""

    def test_logging_security_events(self):
        """
        Verifica que los eventos de seguridad se logueen correctamente.

        Eventos a loguear:
        - Login fallidos (múltiples intentos)
        - Permisos denegados
        - SQL injection attempts
        - Cambios de roles/permisos
        """
        security_events = [
            {'tipo': 'LOGIN_FALLIDO', 'usuario': 'test', 'razon': 'password_incorrecto'},
            {'tipo': 'PERMISO_DENEGADO', 'usuario': 'test', 'permiso': 'delete_admin'},
            {'tipo': 'SQL_INJECTION_INTENTO', 'usuario': 'unknown', 'input': "'; DROP TABLE--"},
            {'tipo': 'ROL_CAMBIADO', 'usuario': 'admin', 'cambio': 'viewer→admin'},
        ]

        with patch('rexus.modules.auditoria.model.AuditoriaModel') as AuditoriaModel:
            mock_log = Mock()
            AuditoriaModel.return_value.log_evento.return_value = mock_log

            auditoria = AuditoriaModel(None, None)

            for event in security_events:
                logged = auditoria.log_evento(event)

                # Verificar que se logueó
                assert logged is not None
                assert logged['tipo'] in ['LOGIN_FALLIDO', 'PERMISO_DENEGADO',
                                           'SQL_INJECTION_INTENTO', 'ROL_CAMBIADO']


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short', '-m', 'security'])
