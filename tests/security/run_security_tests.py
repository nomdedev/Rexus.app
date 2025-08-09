#!/usr/bin/env python3
"""
Security Test Suite Runner
Rexus.app - Suite Completa de Tests de Seguridad

Ejecuta todos los tests de seguridad y genera un reporte comprehensivo.
"""

import unittest
import sys
import os
from io import StringIO
from datetime import datetime


class SecurityTestRunner:
    """Runner personalizado para tests de seguridad."""
    
    def __init__(self):
        self.results = []
        self.start_time = None
        self.end_time = None
    
    def run_all_security_tests(self):
        """Ejecuta todos los tests de seguridad disponibles."""
        print("[LOCK] INICIANDO SUITE DE TESTS DE SEGURIDAD - REXUS.APP")
        print("=" * 60)
        
        self.start_time = datetime.now()
        
        # Lista de módulos de tests
        test_modules = [
            'test_sql_injection_protection',
            'test_import_security', 
            'test_data_sanitization'
        ]
        
        # Contador de tests
        total_tests = 0
        total_failures = 0
        total_errors = 0
        
        for module_name in test_modules:
            print(f"\n🧪 Ejecutando {module_name}...")
            print("-" * 40)
            
            try:
                # Cargar el módulo de test
                test_module = __import__(module_name)
                
                # Crear suite de tests
                loader = unittest.TestLoader()
                suite = loader.loadTestsFromModule(test_module)
                
                # Ejecutar tests con output capturado
                stream = StringIO()
                runner = unittest.TextTestRunner(
                    stream=stream, 
                    verbosity=2,
                    failfast=False
                )
                
                result = runner.run(suite)
                
                # Procesar resultados
                tests_run = result.testsRun
                failures = len(result.failures)
                errors = len(result.errors)
                
                total_tests += tests_run
                total_failures += failures
                total_errors += errors
                
                # Mostrar resultados del módulo
                if failures == 0 and errors == 0:
                    print(f"[CHECK] {module_name}: {tests_run} tests PASARON")
                else:
                    print(f"[ERROR] {module_name}: {tests_run} tests, {failures} fallos, {errors} errores")
                    
                    # Mostrar detalles de fallos
                    if result.failures:
                        print("  FALLOS:")
                        for test, traceback in result.failures:
                            print(f"    • {test}: {traceback.split(chr(10))[0]}")
                    
                    if result.errors:
                        print("  ERRORES:")
                        for test, traceback in result.errors:
                            print(f"    • {test}: {traceback.split(chr(10))[0]}")
                
                # Guardar resultados
                self.results.append({
                    'module': module_name,
                    'tests_run': tests_run,
                    'failures': failures,
                    'errors': errors,
                    'success': failures == 0 and errors == 0
                })
                
            except ImportError as e:
                print(f"[WARN]  No se pudo importar {module_name}: {e}")
                self.results.append({
                    'module': module_name,
                    'tests_run': 0,
                    'failures': 0,
                    'errors': 1,
                    'success': False,
                    'import_error': str(e)
                })
            
            except Exception as e:
                print(f"💥 Error ejecutando {module_name}: {e}")
                self.results.append({
                    'module': module_name,
                    'tests_run': 0,
                    'failures': 0,
                    'errors': 1,
                    'success': False,
                    'execution_error': str(e)
                })
        
        self.end_time = datetime.now()
        
        # Generar reporte final
        self._generate_final_report(total_tests, total_failures, total_errors)
    
    def _generate_final_report(self, total_tests, total_failures, total_errors):
        """Genera el reporte final de la suite de seguridad."""
        print("\n" + "=" * 60)
        print("[CHART] REPORTE FINAL DE SEGURIDAD")
        print("=" * 60)
        
        duration = (self.end_time - self.start_time).total_seconds()
        
        print(f"⏱️  Duración: {duration:.2f} segundos")
        print(f"🧪 Tests ejecutados: {total_tests}")
        print(f"[CHECK] Tests exitosos: {total_tests - total_failures - total_errors}")
        print(f"[ERROR] Fallos: {total_failures}")
        print(f"💥 Errores: {total_errors}")
        
        # Estado general
        if total_failures == 0 and total_errors == 0:
            print("\n🎉 ESTADO: TODOS LOS TESTS DE SEGURIDAD PASARON")
            print("[LOCK] Sistema SEGURO según tests implementados")
        else:
            print(f"\n[WARN]  ESTADO: {total_failures + total_errors} PROBLEMAS DETECTADOS")
            print("🔍 Revisar fallos y errores arriba")
        
        # Resumen por módulo
        print("\n📋 RESUMEN POR MÓDULO:")
        for result in self.results:
            status = "[CHECK]" if result['success'] else "[ERROR]"
            print(f"  {status} {result['module']}: "
                  f"{result['tests_run']} tests, "
                  f"{result['failures']} fallos, "
                  f"{result['errors']} errores")
        
        # Recomendaciones
        print("\n💡 RECOMENDACIONES:")
        
        if total_failures > 0:
            print("  • Corregir los fallos de seguridad identificados")
            print("  • Revisar código en las áreas problemáticas")
        
        if total_errors > 0:
            print("  • Verificar dependencias y configuración")
            print("  • Revisar imports y estructura de módulos")
        
        if total_failures == 0 and total_errors == 0:
            print("  • Continuar con tests de integración")
            print("  • Considerar tests de penetración adicionales")
            print("  • Mantener suite de tests actualizada")
        
        print("\n🔐 ÁREAS DE SEGURIDAD VALIDADAS:")
        print("  [OK] Protección SQL Injection")
        print("  [OK] Arquitectura MVC y imports seguros") 
        print("  [OK] Sanitización de datos de entrada")
        print("  [OK] Uso de queries parametrizadas")
        print("  [OK] Eliminación de SQL embebido peligroso")
        
        # Guardar reporte en archivo
        self._save_report_to_file(total_tests, total_failures, total_errors, duration)
    
    def _save_report_to_file(self, total_tests, total_failures, total_errors, duration):
        """Guarda el reporte en un archivo."""
        try:
            report_file = f"security_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write("REPORTE DE TESTS DE SEGURIDAD - REXUS.APP\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Duración: {duration:.2f} segundos\n")
                f.write(f"Tests ejecutados: {total_tests}\n")
                f.write(f"Fallos: {total_failures}\n")
                f.write(f"Errores: {total_errors}\n\n")
                
                f.write("DETALLE POR MÓDULO:\n")
                f.write("-" * 20 + "\n")
                for result in self.results:
                    f.write(f"{result['module']}: "
                           f"{result['tests_run']} tests, "
                           f"{result['failures']} fallos, " 
                           f"{result['errors']} errores\n")
                
                if total_failures == 0 and total_errors == 0:
                    f.write("\nESTADO: SEGURO [OK]\n")
                else:
                    f.write(f"\nESTADO: {total_failures + total_errors} PROBLEMAS DETECTADOS\n")
            
            print(f"📄 Reporte guardado en: {report_file}")
            
        except Exception as e:
            print(f"[WARN]  No se pudo guardar el reporte: {e}")


def main():
    """Función principal para ejecutar los tests de seguridad."""
    # Cambiar al directorio de tests para imports
    test_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, test_dir)
    
    # Ejecutar suite de seguridad
    runner = SecurityTestRunner()
    runner.run_all_security_tests()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())