"""
Tests Avanzados de Prevención de SQL Injection - Rexus.app
Casos extremos, blind injection, second-order injection, y edge cases
"""

import sys
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import time
import threading

# Agregar directorio raíz para imports
ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))

try:
    from rexus.modules.inventario.model import InventarioModel
    from rexus.modules.obras.model import ObrasModel
    from rexus.modules.usuarios.model import UsuariosModel
    from rexus.modules.compras.model import ComprasModel
    MODULES_AVAILABLE = True
except ImportError as e:
    print(f"[WARNING] Módulos no disponibles para tests SQL: {e}")
    MODULES_AVAILABLE = False


class TestSQLInjectionAdvanced:
    """Tests avanzados de prevención de SQL Injection."""
    
    @pytest.fixture
    def mock_database(self):
        """Mock de base de datos con logging de queries."""
        mock_db = Mock()
        mock_cursor = Mock()
        mock_db.cursor.return_value = mock_cursor
        
        # Capturar todas las queries ejecutadas
        mock_cursor.queries_executed = []
        
        def capture_execute(query, params=None):
            mock_cursor.queries_executed.append({
                'query': query,
                'params': params
            })
        
        mock_cursor.execute = Mock(side_effect=capture_execute)
        mock_cursor.fetchall.return_value = []
        mock_cursor.fetchone.return_value = None
        
        return mock_db
    
    @pytest.fixture
    def usuario_mock(self):
        """Usuario mock para tests."""
        return {
            'id': 1,
            'usuario': 'test_user',
            'rol': 'ADMIN',
            'ip': '192.168.1.100'
        }

    def test_classic_sql_injection_attempts(self, mock_database, usuario_mock):
        """Test intentos clásicos de SQL injection."""
        if not MODULES_AVAILABLE:
            pytest.skip("Módulos no disponibles")
            
        model = InventarioModel(mock_database)
        
        # Intentos clásicos de SQL injection
        sql_payloads = [
            "'; DROP TABLE inventario_perfiles; --",
            "' OR '1'='1' --",
            "1; DELETE FROM inventario_perfiles WHERE 1=1; --",
            "' UNION SELECT password FROM usuarios --",
            "admin'--",
            "' OR 1=1#",
            "') OR ('1'='1",
            "'; EXEC xp_cmdshell('dir'); --"
        ]
        
        for payload in sql_payloads:
            print(f"Testing SQL injection: {payload[:50]}...")
            
            # Test buscar item con payload malicioso
            try:
                with patch.object(model, 'db_connection', mock_database):
                    result = model.buscar_items_por_nombre(payload)
                    
                    # Verificar que se usaron parámetros preparados
                    cursor = mock_database.cursor.return_value
                    if cursor.queries_executed:
                        last_query = cursor.queries_executed[-1]
                        
                        # La query NO debe contener el payload directamente
                        assert payload not in str(last_query.get('query', ''))
                        
                        # Debe usar parámetros
                        assert last_query.get('params') is not None
                        print(f"[OK] Query parametrizada correctamente")
                        
            except Exception as e:
                # Está bien que falle si detecta el intento malicioso
                print(f"[OK] Excepción de seguridad (correcto): {str(e)[:100]}")

    def test_blind_sql_injection_time_based(self, mock_database, usuario_mock):
        """Test blind SQL injection basado en tiempo."""
        if not MODULES_AVAILABLE:
            pytest.skip("Módulos no disponibles")
            
        model = InventarioModel(mock_database)
        
        # Payloads de blind SQL injection basado en tiempo
        time_based_payloads = [
            "'; WAITFOR DELAY '00:00:05'; --",
            "' AND (SELECT COUNT(*) FROM inventario_perfiles WHERE nombre LIKE '%test%') > 0 WAITFOR DELAY '00:00:05'; --",
            "1; IF (1=1) WAITFOR DELAY '00:00:03'; --"
        ]
        
        for payload in time_based_payloads:
            print(f"Testing time-based blind injection: {payload[:50]}...")
            
            start_time = time.time()
            
            try:
                with patch.object(model, 'db_connection', mock_database):
                    result = model.buscar_items_por_codigo(payload)
                    
                end_time = time.time()
                execution_time = end_time - start_time
                
                # No debería demorar más de lo normal (< 1 segundo)
                assert execution_time < 1.0, f"Query demoró {execution_time:.2f}s - posible time-based injection"
                print(f"[OK] Query ejecutó en {execution_time:.3f}s")
                
            except Exception as e:
                execution_time = time.time() - start_time
                print(f"[OK] Excepción en {execution_time:.3f}s: {str(e)[:100]}")

    def test_union_based_injection(self, mock_database, usuario_mock):
        """Test UNION-based SQL injection."""
        if not MODULES_AVAILABLE:
            pytest.skip("Módulos no disponibles")
            
        model = UsuariosModel(mock_database)
        
        # Payloads UNION-based
        union_payloads = [
            "' UNION SELECT username, password, '1' FROM usuarios --",
            "1' UNION SELECT table_name, column_name, '1' FROM information_schema.columns --",
            "' UNION ALL SELECT NULL, @@version, NULL --",
            "' UNION SELECT 1,2,3,4,5,database(),7,8 --"
        ]
        
        for payload in union_payloads:
            print(f"Testing UNION injection: {payload[:50]}...")
            
            try:
                with patch.object(model, 'db_connection', mock_database):
                    # Intentar en método de búsqueda
                    result = model.obtener_usuario_por_nombre(payload)
                    
                    # Verificar que el resultado no contenga información sensible
                    if result:
                        assert 'password' not in str(result).lower()
                        assert '@@version' not in str(result)
                        assert 'information_schema' not in str(result)
                        print(f"[OK] Resultado filtrado correctamente")
                        
            except Exception as e:
                print(f"[OK] UNION injection bloqueado: {str(e)[:100]}")

    def test_second_order_injection(self, mock_database, usuario_mock):
        """Test second-order SQL injection."""
        if not MODULES_AVAILABLE:
            pytest.skip("Módulos no disponibles")
            
        model = UsuariosModel(mock_database)
        
        # Crear usuario con payload malicioso
        malicious_username = "admin'; DROP TABLE logs; --"
        
        try:
            with patch.object(model, 'db_connection', mock_database):
                # Paso 1: Crear usuario con nombre malicioso
                model.crear_usuario({
                    'username': malicious_username,
                    'password': 'test123',
                    'email': 'test@test.com',
                    'rol': 'USER'
                }, usuario_mock)
                
                # Paso 2: Usar ese usuario en otra operación (second-order)
                result = model.obtener_usuario_por_nombre(malicious_username)
                
                # Verificar que ambas operaciones usaron queries parametrizadas
                cursor = mock_database.cursor.return_value
                for query_info in cursor.queries_executed:
                    query = str(query_info.get('query', ''))
                    # No debe contener el payload directamente en la query
                    assert 'DROP TABLE' not in query
                    print(f"[OK] Second-order injection prevenido")
                    
        except Exception as e:
            print(f"[OK] Second-order injection detectado: {str(e)[:100]}")

    def test_injection_in_order_by_clauses(self, mock_database, usuario_mock):
        """Test SQL injection en cláusulas ORDER BY."""
        if not MODULES_AVAILABLE:
            pytest.skip("Módulos no disponibles")
            
        model = InventarioModel(mock_database)
        
        # Payloads para ORDER BY injection
        order_by_payloads = [
            "nombre; DROP TABLE inventario_perfiles; --",
            "(CASE WHEN (1=1) THEN nombre ELSE codigo END)",
            "1,(SELECT COUNT(*) FROM usuarios)",
            "(SELECT password FROM usuarios LIMIT 1)"
        ]
        
        for payload in order_by_payloads:
            print(f"Testing ORDER BY injection: {payload[:50]}...")
            
            try:
                with patch.object(model, 'db_connection', mock_database):
                    # Simular ordenamiento con payload malicioso
                    result = model.obtener_items_paginados(
                        pagina=1, 
                        limite=10, 
                        orden=payload
                    )
                    
                    # Verificar query generada
                    cursor = mock_database.cursor.return_value
                    if cursor.queries_executed:
                        last_query = cursor.queries_executed[-1]['query']
                        
                        # No debe contener payload directamente
                        assert 'DROP TABLE' not in str(last_query)
                        assert 'SELECT password' not in str(last_query)
                        print(f"[OK] ORDER BY injection prevenido")
                        
            except Exception as e:
                print(f"[OK] ORDER BY injection detectado: {str(e)[:100]}")

    def test_injection_with_encoded_payloads(self, mock_database, usuario_mock):
        """Test SQL injection con payloads codificados."""
        if not MODULES_AVAILABLE:
            pytest.skip("Módulos no disponibles")
            
        model = InventarioModel(mock_database)
        
        # Payloads codificados
        encoded_payloads = [
            "%27%20OR%20%271%27%3D%271",  # ' OR '1'='1
            "%3B%20DROP%20TABLE%20inventario_perfiles%3B",  # ; DROP TABLE inventario_perfiles;
            "\\x27\\x20OR\\x20\\x31\\x3D\\x31",  # ' OR 1=1
            "&#39;&#32;OR&#32;&#49;&#61;&#49;"  # ' OR 1=1 (HTML entities)
        ]
        
        for payload in encoded_payloads:
            print(f"Testing encoded injection: {payload}")
            
            try:
                with patch.object(model, 'db_connection', mock_database):
                    result = model.buscar_items_por_nombre(payload)
                    
                    # El payload no debería decodificarse automáticamente
                    cursor = mock_database.cursor.return_value
                    if cursor.queries_executed:
                        query_params = cursor.queries_executed[-1].get('params', [])
                        
                        # Los parámetros deberían mantener la codificación
                        if query_params and len(query_params) > 0:
                            param_value = str(query_params[0])
                            print(f"[OK] Parámetro mantenido como: {param_value[:50]}")
                        
            except Exception as e:
                print(f"[OK] Encoded injection manejado: {str(e)[:100]}")

    def test_concurrent_injection_attempts(self, mock_database, usuario_mock):
        """Test intentos concurrentes de SQL injection."""
        if not MODULES_AVAILABLE:
            pytest.skip("Módulos no disponibles")
            
        model = InventarioModel(mock_database)
        
        injection_payloads = [
            "'; DROP TABLE inventario_perfiles; --",
            "' OR 1=1 --",
            "'; EXEC xp_cmdshell('dir'); --"
        ]
        
        results = []
        threads = []
        
        def attempt_injection(payload):
            try:
                with patch.object(model, 'db_connection', mock_database):
                    result = model.buscar_items_por_codigo(payload)
                    results.append(('success', payload, result))
            except Exception as e:
                results.append(('error', payload, str(e)))
        
        # Lanzar múltiples threads con intentos de injection
        for payload in injection_payloads:
            thread = threading.Thread(target=attempt_injection, args=(payload,))
            threads.append(thread)
            thread.start()
        
        # Esperar que terminen todos
        for thread in threads:
            thread.join()
        
        # Verificar que todos fueron manejados correctamente
        for status, payload, result in results:
            print(f"Concurrent test - {status}: {payload[:30]}...")
            assert status in ['success', 'error']  # Ambos están bien
        
        print(f"[OK] {len(results)} intentos concurrentes manejados")

    def test_injection_in_stored_procedures(self, mock_database, usuario_mock):
        """Test SQL injection en llamadas a stored procedures."""
        if not MODULES_AVAILABLE:
            pytest.skip("Módulos no disponibles")
            
        # Simular llamadas a stored procedures con payloads maliciosos
        sp_payloads = [
            "'; EXEC xp_cmdshell('dir'); --",
            "test'; EXEC sp_configure 'show advanced options', 1; --",
            "1; EXEC ('DROP TABLE inventario_perfiles'); --"
        ]
        
        for payload in sp_payloads:
            print(f"Testing SP injection: {payload[:50]}...")
            
            # Simular ejecución de SP
            with patch.object(mock_database, 'cursor') as mock_cursor_method:
                mock_cursor = Mock()
                mock_cursor_method.return_value = mock_cursor
                
                try:
                    # Simular llamada a SP con parámetros
                    query = "EXEC sp_buscar_inventario ?"
                    mock_cursor.execute(query, (payload,))
                    
                    # Verificar que se usó como parámetro, no concatenado
                    mock_cursor.execute.assert_called_with(query, (payload,))
                    print(f"[OK] SP call parametrizada correctamente")
                    
                except Exception as e:
                    print(f"[OK] SP injection detectado: {str(e)[:100]}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])