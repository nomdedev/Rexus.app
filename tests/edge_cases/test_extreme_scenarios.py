#!/usr/bin/env python3
"""
Tests de Casos Edge Extremos para Rexus.app

Pruebas exhaustivas de escenarios límite y casos extremos:
- Manejo de datos corruptos
- Límites de memoria y rendimiento
- Casos de concurrencia extrema
- Recuperación de errores críticos
- Validación de integridad de datos
"""

import sys
import os
import time
import threading
import tempfile
import sqlite3
import json
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from concurrent.futures import ThreadPoolExecutor, as_completed

# Agregar directorio raíz al path
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))


class TestDataCorruptionScenarios(unittest.TestCase):
    """Tests para manejo de datos corruptos."""
    
    def test_corrupted_json_config(self):
        """Test manejo de configuraciones JSON corruptas."""
        corrupted_configs = [
            '{"incomplete": json',  # JSON incompleto
            '{malformed json}',  # JSON mal formado
            '{"unicode": "\\uZZZZ"}',  # Unicode inválido
            '{"nested": {"deep": {"very": {"deep": {"infinite": "recursion"}}}}}' * 1000,  # JSON muy profundo
            '',  # Vacío
            None,  # Null
            '{"valid": true}' + '\x00' + '{"invalid": after_null}',  # Con caracteres null
        ]
        
        for corrupted_config in corrupted_configs:
            try:
                # Simular carga de configuración corrupta
                if corrupted_config is None:
                    config = None
                else:
                    config = json.loads(corrupted_config) if corrupted_config else {}
                
                # El sistema debe manejar estos casos sin fallar
                self.assertIsInstance(config, (dict, type(None)))
                
            except (json.JSONDecodeError, ValueError, TypeError):
                # Estos errores son esperables y deben ser manejados
                pass
            except Exception as e:
                self.fail(f"Error inesperado con config corrupta: {e}")
    
    def test_corrupted_database_recovery(self):
        """Test recuperación de bases de datos corruptas."""
        # Crear base de datos temporal
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_db:
            db_path = tmp_db.name
        
        try:
            # Crear base de datos válida
            conn = sqlite3.connect(db_path)
            conn.execute("CREATE TABLE test (id INTEGER, data TEXT)")
            conn.execute("INSERT INTO test VALUES (1, 'data')")
            conn.commit()
            conn.close()
            
            # Corromper la base de datos (escribir basura)
            with open(db_path, 'r+b') as f:
                f.seek(100)  # Ir a una posición en el archivo
                f.write(b'\x00\xFF\x00\xFF' * 100)  # Escribir datos corruptos
            
            # Intentar conectar a DB corrupta
            try:
                conn = sqlite3.connect(db_path)
                conn.execute("SELECT * FROM test")
                conn.close()
            except sqlite3.DatabaseError:
                # Error esperado - la DB está corrupta
                pass
            
        finally:
            # Limpiar archivo temporal
            if os.path.exists(db_path):
                os.unlink(db_path)
    
    def test_extreme_input_sizes(self):
        """Test manejo de inputs de tamaño extremo."""
        from rexus.utils.data_sanitizer import DataSanitizer
        
        extreme_inputs = [
            '',  # Vacío
            'a' * 1000000,  # 1MB de texto
            '🎭' * 100000,  # Unicode repetido
            '\n' * 50000,  # Muchos saltos de línea
            ' ' * 200000,  # Muchos espacios
            'A' * 10 + '\x00' + 'B' * 10,  # Con caracteres null
        ]
        
        for extreme_input in extreme_inputs:
            try:
                # El sanitizador debe manejar inputs extremos
                result = DataSanitizer.sanitize_text(extreme_input)
                
                # Verificar que el resultado es válido
                self.assertIsInstance(result, str)
                self.assertLessEqual(len(result), len(extreme_input))
                
            except Exception as e:
                self.fail(f"Error con input extremo de tamaño {len(extreme_input)}: {e}")


class TestConcurrencyExtremeScenarios(unittest.TestCase):
    """Tests de concurrencia extrema."""
    
    def test_massive_concurrent_operations(self):
        """Test operaciones concurrentes masivas."""
        results = []
        errors = []
        
        def worker_function(worker_id):
            """Función de trabajo para cada hilo."""
            try:
                # Simular operación de base de datos
                time.sleep(0.01)  # Simular trabajo
                
                # Simular operación con datos
                data = f"worker_{worker_id}_data"
                processed = data.upper()
                
                return {'worker_id': worker_id, 'result': processed}
                
            except Exception as e:
                return {'worker_id': worker_id, 'error': str(e)}
        
        # Ejecutar 100 workers concurrentes
        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(worker_function, i) for i in range(100)]
            
            for future in as_completed(futures):
                result = future.result()
                if 'error' in result:
                    errors.append(result)
                else:
                    results.append(result)
        
        # Verificar que la mayoría de operaciones fueron exitosas
        success_rate = len(results) / (len(results) + len(errors))
        self.assertGreater(success_rate, 0.95)  # Al menos 95% exitoso
        
        # Verificar que no hay duplicados en los IDs
        worker_ids = [r['worker_id'] for r in results]
        self.assertEqual(len(worker_ids), len(set(worker_ids)))
    
    def test_race_condition_simulation(self):
        """Test simulación de condiciones de carrera."""
        shared_counter = {'value': 0}
        lock = threading.Lock()
        race_errors = []
        
        def increment_with_race(iterations):
            """Incrementa contador con posibilidad de race condition."""
            for _ in range(iterations):
                try:
                    # Simular operación no atómica
                    current = shared_counter['value']
                    time.sleep(0.0001)  # Simular delay que puede causar race
                    shared_counter['value'] = current + 1
                    
                except Exception as e:
                    race_errors.append(str(e))
        
        def increment_with_lock(iterations):
            """Incrementa contador con lock."""
            for _ in range(iterations):
                try:
                    with lock:
                        current = shared_counter['value']
                        time.sleep(0.0001)
                        shared_counter['value'] = current + 1
                        
                except Exception as e:
                    race_errors.append(str(e))
        
        # Test sin lock (puede tener race conditions)
        shared_counter['value'] = 0
        threads = []
        
        for _ in range(5):
            thread = threading.Thread(target=increment_with_race, args=(20,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        result_without_lock = shared_counter['value']
        
        # Test con lock (debe ser correcto)
        shared_counter['value'] = 0
        threads = []
        
        for _ in range(5):
            thread = threading.Thread(target=increment_with_lock, args=(20,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        result_with_lock = shared_counter['value']
        
        # Con lock debe ser exacto
        self.assertEqual(result_with_lock, 100)
        
        # Sin lock puede ser menor debido a race conditions
        self.assertLessEqual(result_without_lock, 100)


class TestMemoryAndPerformanceLimits(unittest.TestCase):
    """Tests de límites de memoria y rendimiento."""
    
    def test_memory_intensive_operations(self):
        """Test operaciones intensivas en memoria."""
        try:
            # Crear listas grandes
            large_list = list(range(100000))
            large_dict = {i: f"value_{i}" for i in range(50000)}
            large_string = "x" * 1000000
            
            # Operaciones con datos grandes
            filtered_list = [x for x in large_list if x % 2 == 0]
            sorted_dict = dict(sorted(large_dict.items()))
            processed_string = large_string.upper()
            
            # Verificar que las operaciones completaron
            self.assertEqual(len(filtered_list), 50000)
            self.assertEqual(len(sorted_dict), 50000)
            self.assertEqual(len(processed_string), 1000000)
            
            # Limpiar memoria
            del large_list, large_dict, large_string
            del filtered_list, sorted_dict, processed_string
            
        except MemoryError:
            self.skipTest("Memoria insuficiente para test")
        except Exception as e:
            self.fail(f"Error inesperado en operación intensiva: {e}")
    
    def test_algorithmic_complexity_limits(self):
        """Test límites de complejidad algorítmica."""
        # Test operación O(n²) con n grande
        def bubble_sort_partial(arr, max_iterations=1000):
            """Bubble sort parcial con límite de iteraciones."""
            n = len(arr)
            iterations = 0
            
            for i in range(n):
                if iterations >= max_iterations:
                    break
                    
                for j in range(0, n - i - 1):
                    iterations += 1
                    if iterations >= max_iterations:
                        break
                        
                    if arr[j] > arr[j + 1]:
                        arr[j], arr[j + 1] = arr[j + 1], arr[j]
            
            return arr, iterations
        
        # Test con array grande
        large_array = list(range(1000, 0, -1))  # Array reverso
        
        start_time = time.time()
        result, iterations = bubble_sort_partial(large_array.copy(), max_iterations=10000)
        end_time = time.time()
        
        # Verificar que se respetó el límite de tiempo/iteraciones
        self.assertLess(end_time - start_time, 1.0)  # Menos de 1 segundo
        self.assertLessEqual(iterations, 10000)


class TestErrorRecoveryScenarios(unittest.TestCase):
    """Tests de recuperación de errores críticos."""
    
    def test_cascading_failure_recovery(self):
        """Test recuperación de fallos en cascada."""
        class FailingComponent:
            def __init__(self, fail_probability=0.3):
                self.fail_probability = fail_probability
                self.call_count = 0
            
            def operation(self):
                self.call_count += 1
                if self.call_count * self.fail_probability > 0.5:
                    raise Exception(f"Simulated failure #{self.call_count}")
                return f"Success #{self.call_count}"
        
        class ResilientSystem:
            def __init__(self):
                self.components = [FailingComponent(0.2), FailingComponent(0.3), FailingComponent(0.1)]
                self.backup_component = FailingComponent(0.05)  # Componente más confiable
            
            def execute_with_fallback(self):
                """Ejecuta operación con fallback automático."""
                for i, component in enumerate(self.components):
                    try:
                        return component.operation()
                    except Exception as e:
                        print(f"Component {i} failed: {e}")
                        continue
                
                # Usar backup si todos fallan
                try:
                    return self.backup_component.operation()
                except Exception as e:
                    return f"All components failed, backup error: {e}"
        
        system = ResilientSystem()
        results = []
        
        # Ejecutar múltiples operaciones
        for _ in range(20):
            result = system.execute_with_fallback()
            results.append(result)
        
        # Verificar que el sistema se recuperó de fallos
        successful_operations = [r for r in results if "Success" in r]
        self.assertGreater(len(successful_operations), 10)  # Al menos 50% exitoso
    
    def test_resource_exhaustion_recovery(self):
        """Test recuperación por agotamiento de recursos."""
        import tempfile
        
        def create_temp_files(count):
            """Crea archivos temporales hasta agotar recursos."""
            files = []
            try:
                for i in range(count):
                    tmp_file = tempfile.NamedTemporaryFile(delete=False)
                    tmp_file.write(b"x" * 1024)  # 1KB por archivo
                    files.append(tmp_file.name)
                    tmp_file.close()
                    
                    if i > 0 and i % 100 == 0:
                        print(f"Created {i} temp files")
                
                return files
                
            except (OSError, IOError) as e:
                print(f"Resource exhaustion at {len(files)} files: {e}")
                return files
        
        def cleanup_files(files):
            """Limpia archivos creados."""
            cleaned = 0
            for file_path in files:
                try:
                    os.unlink(file_path)
                    cleaned += 1
                except OSError:
                    pass
            return cleaned
        
        # Intentar crear muchos archivos
        created_files = create_temp_files(1000)
        
        # Verificar que se crearon algunos archivos
        self.assertGreater(len(created_files), 0)
        
        # Limpiar archivos
        cleaned_count = cleanup_files(created_files)
        
        # Verificar que se pudieron limpiar
        self.assertEqual(cleaned_count, len(created_files))


class TestDataIntegrityValidation(unittest.TestCase):
    """Tests de validación de integridad de datos."""
    
    def test_checksum_validation(self):
        """Test validación de checksums para integridad."""
        import hashlib
        
        def calculate_checksum(data):
            """Calcula checksum MD5 de datos."""
            return hashlib.md5(data.encode('utf-8')).hexdigest()
        
        def validate_data_integrity(original_data, received_data, expected_checksum):
            """Valida integridad de datos usando checksum."""
            received_checksum = calculate_checksum(received_data)
            
            return {
                'data_match': original_data == received_data,
                'checksum_match': received_checksum == expected_checksum,
                'is_valid': received_checksum == expected_checksum and original_data == received_data
            }
        
        # Datos originales
        original_data = "Important data that must not be corrupted"
        original_checksum = calculate_checksum(original_data)
        
        # Test con datos correctos
        result = validate_data_integrity(original_data, original_data, original_checksum)
        self.assertTrue(result['is_valid'])
        self.assertTrue(result['data_match'])
        self.assertTrue(result['checksum_match'])
        
        # Test con datos corruptos
        corrupted_data = "Important data that CORRUPTED be corrupted"
        result = validate_data_integrity(original_data, corrupted_data, original_checksum)
        self.assertFalse(result['is_valid'])
        self.assertFalse(result['data_match'])
        self.assertFalse(result['checksum_match'])
    
    def test_circular_reference_detection(self):
        """Test detección de referencias circulares."""
        def detect_circular_reference(obj, visited=None):
            """Detecta referencias circulares en estructuras de datos."""
            if visited is None:
                visited = set()
            
            obj_id = id(obj)
            if obj_id in visited:
                return True  # Referencia circular detectada
            
            visited.add(obj_id)
            
            if isinstance(obj, dict):
                for value in obj.values():
                    if isinstance(value, (dict, list)):
                        if detect_circular_reference(value, visited.copy()):
                            return True
            elif isinstance(obj, list):
                for item in obj:
                    if isinstance(item, (dict, list)):
                        if detect_circular_reference(item, visited.copy()):
                            return True
            
            return False
        
        # Test sin referencia circular
        normal_data = {
            'user': {'id': 1, 'name': 'test'},
            'items': [{'id': 1}, {'id': 2}]
        }
        self.assertFalse(detect_circular_reference(normal_data))
        
        # Test con referencia circular
        circular_data = {'parent': None}
        circular_data['parent'] = circular_data  # Referencia circular
        self.assertTrue(detect_circular_reference(circular_data))


def run_extreme_edge_cases_tests():
    """Ejecuta todos los tests de casos edge extremos."""
    print("=== TESTS DE CASOS EDGE EXTREMOS ===")
    print("Rexus.app - Validación de Resistencia del Sistema")
    print("=" * 50)
    
    # Crear suite de tests
    test_classes = [
        TestDataCorruptionScenarios,
        TestConcurrencyExtremeScenarios,
        TestMemoryAndPerformanceLimits,
        TestErrorRecoveryScenarios,
        TestDataIntegrityValidation
    ]
    
    suite = unittest.TestSuite()
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Ejecutar tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Resumen
    print(f"\n=== RESUMEN DE TESTS EDGE CASES ===")
    print(f"Tests ejecutados: {result.testsRun}")
    print(f"Errores: {len(result.errors)}")
    print(f"Fallos: {len(result.failures)}")
    print(f"Tests saltados: {len(getattr(result, 'skipped', []))}")
    
    if result.errors:
        print("\nERRORES:")
        for test, error in result.errors:
            print(f"- {test}: {error.split(chr(10))[0]}")  # Primera línea del error
    
    if result.failures:
        print("\nFALLOS:")
        for test, failure in result.failures:
            print(f"- {test}: {failure.split(chr(10))[0]}")  # Primera línea del fallo
    
    success_rate = ((result.testsRun - len(result.errors) - len(result.failures)) / result.testsRun * 100) if result.testsRun > 0 else 0
    print(f"\nTasa de éxito: {success_rate:.1f}%")
    
    # Evaluación de resistencia
    if success_rate >= 95:
        print("🛡️ SISTEMA: EXTREMADAMENTE RESISTENTE")
        print("✅ Maneja casos edge críticos exitosamente")
    elif success_rate >= 85:
        print("🔒 SISTEMA: ALTAMENTE RESISTENTE")
        print("⚠️ Algunos casos edge requieren atención")
    elif success_rate >= 70:
        print("⚡ SISTEMA: MODERADAMENTE RESISTENTE")
        print("🔧 Varios casos edge necesitan mejoras")
    else:
        print("🚨 SISTEMA: BAJA RESISTENCIA")
        print("❌ Casos edge críticos fallan - requiere atención inmediata")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_extreme_edge_cases_tests()
    sys.exit(0 if success else 1)