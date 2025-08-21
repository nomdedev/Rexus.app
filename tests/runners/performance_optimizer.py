#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Performance Optimizer - Identifica y optimiza tests lentos
Sistema para mejorar la velocidad de ejecución de tests
"""

import subprocess
import time
import os
import sys
from pathlib import Path

# Configurar encoding
os.environ['PYTHONIOENCODING'] = 'utf-8'

class TestPerformanceOptimizer:
    """Optimizador de performance para tests."""
    
    def __init__(self):
        self.test_directory = Path(__file__).parent.parent
        self.slow_threshold = 1.0  # Tests que toman más de 1 segundo
        
    def run_individual_module_tests(self):
        """Ejecuta tests por módulo individual para evitar conflictos de nombres."""
        print("OPTIMIZADOR DE PERFORMANCE - ANALISIS POR MODULOS")
        print("=" * 60)
        
        modules = [
            'unit/usuarios',
            'unit/inventario', 
            'unit/configuracion',
            'unit/compras',
            'unit/administracion',
            'unit/auditoria',
            'unit/obras',
            'integration',
            'e2e'
        ]
        
        results = {}
        total_tests = 0
        total_time = 0
        
        for module in modules:
            module_path = self.test_directory / module
            if not module_path.exists():
                print(f"WARNING: Modulo {module} no existe, omitiendo...")
                continue
                
            print(f"\nAnalizando modulo: {module}")
            print("-" * 40)
            
            start_time = time.time()
            
            try:
                # Ejecutar pytest con durations para este módulo específico
                cmd = [
                    'python', '-m', 'pytest', 
                    str(module_path),
                    '--durations=0',
                    '--tb=no',
                    '-q'
                ]
                
                result = subprocess.run(
                    cmd, 
                    cwd=self.test_directory,
                    capture_output=True, 
                    text=True,
                    timeout=60
                )
                
                end_time = time.time()
                module_time = end_time - start_time
                
                if result.returncode == 0:
                    # Extraer información de tests
                    output_lines = result.stdout.split('\n')
                    
                    test_count = 0
                    for line in output_lines:
                        if 'passed' in line and 'in' in line:
                            # Buscar línea como "5 passed in 0.12s"
                            parts = line.split()
                            if len(parts) >= 3 and parts[1] == 'passed':
                                test_count = int(parts[0])
                            break
                    
                    results[module] = {
                        'status': 'PASSED',
                        'tests': test_count,
                        'time': module_time,
                        'output': result.stdout
                    }
                    
                    total_tests += test_count
                    total_time += module_time
                    
                    print(f"PASSED: {test_count} tests - {module_time:.2f}s")
                    
                else:
                    results[module] = {
                        'status': 'FAILED', 
                        'tests': 0,
                        'time': module_time,
                        'error': result.stderr
                    }
                    print(f"FAILED - {module_time:.2f}s")
                    print(f"Error: {result.stderr[:200]}...")
                    
            except subprocess.TimeoutExpired:
                results[module] = {
                    'status': 'TIMEOUT',
                    'tests': 0, 
                    'time': 60.0,
                    'error': 'Test execution timed out after 60 seconds'
                }
                print(f"TIMEOUT - >60s")
                
            except Exception as e:
                results[module] = {
                    'status': 'ERROR',
                    'tests': 0,
                    'time': 0,
                    'error': str(e)
                }
                print(f"ERROR - {str(e)}")
        
        self.generate_performance_report(results, total_tests, total_time)
        return results
    
    def generate_performance_report(self, results, total_tests, total_time):
        """Genera reporte de performance detallado."""
        print("\n" + "=" * 60)
        print("REPORTE DE PERFORMANCE")
        print("=" * 60)
        
        print(f"\nRESUMEN GENERAL:")
        print(f"   Tests ejecutados: {total_tests}")
        print(f"   Tiempo total: {total_time:.2f}s")
        print(f"   Promedio por test: {total_time/total_tests:.3f}s" if total_tests > 0 else "   Promedio: N/A")
        
        # Módulos por performance
        print(f"\nPERFORMANCE POR MODULO:")
        sorted_modules = sorted(
            [(k, v) for k, v in results.items() if v['status'] == 'PASSED'],
            key=lambda x: x[1]['time'],
            reverse=True
        )
        
        for module, data in sorted_modules:
            tests_per_second = data['tests'] / data['time'] if data['time'] > 0 else 0
            print(f"   {module:20} | {data['time']:6.2f}s | {data['tests']:3d} tests | {tests_per_second:5.1f} tests/s")
        
        # Módulos con problemas
        problematic = [(k, v) for k, v in results.items() if v['status'] != 'PASSED']
        if problematic:
            print(f"\nMODULOS CON PROBLEMAS:")
            for module, data in problematic:
                print(f"   {module:20} | {data['status']:8} | {data.get('error', '')[:50]}...")
        
        # Recomendaciones
        print(f"\nRECOMENDACIONES:")
        
        slow_modules = [m for m, d in sorted_modules if d['time'] > 2.0]
        if slow_modules:
            print(f"   - Optimizar modulos lentos: {', '.join(slow_modules)}")
        
        if problematic:
            print(f"   - Corregir {len(problematic)} modulos con errores")
            
        if total_time > 10:
            print(f"   - Implementar ejecucion paralela (pytest-xdist)")
            
        fast_modules = [m for m, d in sorted_modules if d['time'] < 0.5]
        if fast_modules:
            print(f"   - {len(fast_modules)} modulos ya estan optimizados")

def main():
    """Ejecutar analisis de performance."""
    print("Iniciando analisis de performance de tests...")
    
    optimizer = TestPerformanceOptimizer()
    results = optimizer.run_individual_module_tests()
    
    print(f"\nAnalisis completado. Revisa el reporte arriba.")
    return results

if __name__ == '__main__':
    main()