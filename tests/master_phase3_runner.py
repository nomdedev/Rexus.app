"""
🎯 MASTER TEST RUNNER - PHASE 3: INTEGRATION & E2E TESTS
=====================================================

Este es el runner principal para ejecutar todos los tests de Phase 3 de forma integral.
Incluye validación completa de integración y E2E workflows para Rexus.app.

Phase 3 incluye:
- Tests integrales de módulo Vidrios
- Tests integrales de módulo Notificaciones  
- Tests avanzados de integración Inventario
- Tests avanzados de integración Obras
- Tests E2E de workflows inter-módulos
- Tests de integración real con base de datos

Author: Claude Code Assistant
"""

import unittest
import sys
import os
import time
from datetime import datetime
import subprocess
from pathlib import Path

# Agregar el directorio raíz al path para imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Importar logging
from rexus.utils.app_logger import get_logger

logger = get_logger("test.master_phase3_runner")


class Phase3TestRunner:
    """Runner principal para todos los tests de Phase 3"""
    
    def __init__(self):
        self.test_modules = [
            'tests.test_vidrios_workflows_completos',
            'tests.test_notificaciones_workflows_completos', 
            'tests.test_inventario_integracion_avanzada',
            'tests.test_obras_integracion_avanzada',
            'tests.test_e2e_workflows_inter_modulos',
            'tests.test_database_integration_real'
        ]
        
        self.results = {}
        self.start_time = None
        self.end_time = None
        
    def print_header(self):
        """Imprime header del runner"""
        print("=" * 100)
        print("🎯 REXUS.APP - MASTER TEST RUNNER PHASE 3")
        print("   INTEGRATION & E2E TESTS COMPREHENSIVE SUITE")
        print("=" * 100)
        print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🔧 Python: {sys.version}")
        print(f"📁 Working Dir: {os.getcwd()}")
        print("=" * 100)
        
    def run_module_tests(self, module_name, description):
        """Ejecuta tests de un módulo específico"""
        print(f"\n🔄 EJECUTANDO: {description}")
        print("-" * 80)
        
        try:
            # Importar y ejecutar el módulo de tests
            loader = unittest.TestLoader()
            
            # Importar el módulo dinámicamente
            module = __import__(module_name, fromlist=[''])
            
            # Cargar todos los tests del módulo
            suite = loader.loadTestsFromModule(module)
            
            # Ejecutar tests
            runner = unittest.TextTestRunner(
                verbosity=2,
                stream=sys.stdout,
                buffer=True
            )
            
            start_time = time.time()
            result = runner.run(suite)
            end_time = time.time()
            
            # Guardar resultados
            self.results[module_name] = {
                'description': description,
                'tests_run': result.testsRun,
                'failures': len(result.failures),
                'errors': len(result.errors),
                'skipped': len(result.skipped) if hasattr(result, 'skipped') else 0,
                'success': result.wasSuccessful(),
                'duration': end_time - start_time
            }
            
            if result.wasSuccessful():
                print(f"✅ {description} - TODOS LOS TESTS PASARON")
            else:
                print(f"❌ {description} - ALGUNOS TESTS FALLARON")
                
            print(f"⏱️  Duración: {end_time - start_time:.2f}s")
            
            return result.wasSuccessful()
            
        except ImportError as e:
            logger.error(f"No se pudo importar {module_name}: {e}")
            print(f"⚠️  SALTANDO {description} - Módulo no disponible")
            
            self.results[module_name] = {
                'description': description,
                'error': f"ImportError: {e}",
                'success': False,
                'skipped': True
            }
            
            return False
            
        except Exception as e:
            logger.error(f"Error ejecutando tests de {module_name}: {e}")
            print(f"❌ ERROR en {description}: {e}")
            
            self.results[module_name] = {
                'description': description,
                'error': str(e),
                'success': False
            }
            
            return False
    
    def run_all_tests(self, skip_performance=False):
        """Ejecuta todos los tests de Phase 3"""
        self.print_header()
        self.start_time = time.time()
        
        print("🚀 INICIANDO EJECUCIÓN DE TODOS LOS TESTS DE PHASE 3...")
        print()
        
        # Definir tests a ejecutar
        test_definitions = [
            ('tests.test_vidrios_workflows_completos', 
             '📋 Tests Integrales - Módulo Vidrios'),
            
            ('tests.test_notificaciones_workflows_completos', 
             '🔔 Tests Integrales - Módulo Notificaciones'),
            
            ('tests.test_inventario_integracion_avanzada', 
             '📦 Tests Integración Avanzada - Inventario'),
            
            ('tests.test_obras_integracion_avanzada', 
             '🏗️  Tests Integración Avanzada - Obras'),
            
            ('tests.test_e2e_workflows_inter_modulos', 
             '🔄 Tests E2E - Workflows Inter-Módulos'),
            
            ('tests.test_database_integration_real', 
             '🗄️  Tests Integración Real - Base de Datos')
        ]
        
        # Ejecutar cada suite de tests
        all_successful = True
        
        for module_name, description in test_definitions:
            success = self.run_module_tests(module_name, description)
            all_successful = all_successful and success
        
        self.end_time = time.time()
        
        # Imprimir resumen final
        self.print_final_summary(all_successful)
        
        return all_successful
    
    def run_quick_validation(self):
        """Ejecuta una validación rápida de los tests más críticos"""
        self.print_header()
        print("⚡ MODO VALIDACIÓN RÁPIDA - Tests Críticos de Phase 3")
        print()
        
        self.start_time = time.time()
        
        # Solo ejecutar tests más críticos y rápidos
        critical_tests = [
            ('tests.test_vidrios_workflows_completos', 
             '📋 Validación Rápida - Vidrios'),
            
            ('tests.test_inventario_integracion_avanzada', 
             '📦 Validación Rápida - Inventario'),
            
            ('tests.test_database_integration_real', 
             '🗄️  Validación Rápida - Base de Datos')
        ]
        
        all_successful = True
        
        for module_name, description in critical_tests:
            success = self.run_module_tests(module_name, description)
            all_successful = all_successful and success
        
        self.end_time = time.time()
        self.print_final_summary(all_successful, quick_mode=True)
        
        return all_successful
    
    def print_final_summary(self, all_successful, quick_mode=False):
        """Imprime resumen final de la ejecución"""
        total_duration = self.end_time - self.start_time
        
        print("\n" + "=" * 100)
        print("📊 RESUMEN FINAL DE EJECUCIÓN" + (" (MODO RÁPIDO)" if quick_mode else ""))
        print("=" * 100)
        
        # Estadísticas generales
        total_tests = 0
        total_failures = 0
        total_errors = 0
        total_skipped = 0
        successful_modules = 0
        
        for module_name, result in self.results.items():
            if not result.get('skipped', False):
                total_tests += result.get('tests_run', 0)
                total_failures += result.get('failures', 0)
                total_errors += result.get('errors', 0)
                total_skipped += result.get('skipped', 0)
                
                if result.get('success', False):
                    successful_modules += 1
        
        print(f"⏱️  Duración Total: {total_duration:.2f} segundos")
        print(f"📁 Módulos Ejecutados: {len([r for r in self.results.values() if not r.get('skipped', False)])}")
        print(f"✅ Módulos Exitosos: {successful_modules}")
        print(f"🧪 Tests Totales: {total_tests}")
        print(f"❌ Fallos: {total_failures}")
        print(f"💥 Errores: {total_errors}")
        print(f"⏭️  Saltados: {total_skipped}")
        
        print("\n📋 DETALLE POR MÓDULO:")
        print("-" * 100)
        
        for module_name, result in self.results.items():
            status = "✅" if result.get('success', False) else "❌"
            
            if result.get('skipped', False):
                status = "⏭️ "
                print(f"{status} {result['description']:<50} | SALTADO")
            else:
                duration = result.get('duration', 0)
                tests = result.get('tests_run', 0)
                failures = result.get('failures', 0)
                errors = result.get('errors', 0)
                
                print(f"{status} {result['description']:<50} | "
                      f"Tests: {tests:3d} | "
                      f"Fallos: {failures:2d} | "
                      f"Errores: {errors:2d} | "
                      f"Tiempo: {duration:6.2f}s")
        
        print("=" * 100)
        
        if all_successful:
            print("🎉 ¡TODOS LOS TESTS DE PHASE 3 PASARON EXITOSAMENTE!")
            print("✨ La implementación de Phase 3 está COMPLETA y VALIDADA")
        else:
            print("⚠️  ALGUNOS TESTS FALLARON - Revisar módulos marcados con ❌")
            print("🔧 Se recomienda investigar y corregir los fallos antes de continuar")
        
        print("=" * 100)
    
    def generate_report(self, output_file='phase3_test_report.txt'):
        """Genera reporte detallado de la ejecución"""
        if not self.results:
            print("⚠️  No hay resultados para generar reporte")
            return False
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("REPORTE DE EJECUCIÓN - PHASE 3 TESTS\n")
                f.write("=" * 80 + "\n")
                f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Duración Total: {(self.end_time - self.start_time):.2f} segundos\n\n")
                
                for module_name, result in self.results.items():
                    f.write(f"MÓDULO: {module_name}\n")
                    f.write(f"Descripción: {result['description']}\n")
                    
                    if result.get('skipped', False):
                        f.write("Estado: SALTADO\n")
                        f.write(f"Razón: {result.get('error', 'No especificada')}\n")
                    else:
                        f.write(f"Tests Ejecutados: {result.get('tests_run', 0)}\n")
                        f.write(f"Fallos: {result.get('failures', 0)}\n")
                        f.write(f"Errores: {result.get('errors', 0)}\n")
                        f.write(f"Duración: {result.get('duration', 0):.2f}s\n")
                        f.write(f"Éxito: {'SÍ' if result.get('success', False) else 'NO'}\n")
                    
                    f.write("-" * 40 + "\n")
            
            print(f"📄 Reporte generado: {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error generando reporte: {e}")
            print(f"❌ Error generando reporte: {e}")
            return False


class Phase3CLIRunner:
    """Interface CLI para ejecutar tests de Phase 3"""
    
    @staticmethod
    def show_help():
        """Muestra ayuda de la CLI"""
        print("""
🎯 REXUS.APP - PHASE 3 TEST RUNNER
==================================

Uso: python master_phase3_runner.py [COMANDO]

COMANDOS:
  all          Ejecuta todos los tests de Phase 3 (por defecto)
  quick        Ejecuta validación rápida de tests críticos
  help         Muestra esta ayuda
  
EJEMPLOS:
  python master_phase3_runner.py
  python master_phase3_runner.py all
  python master_phase3_runner.py quick
  python master_phase3_runner.py help

DESCRIPCIÓN:
  Este runner ejecuta la suite completa de tests de Phase 3,
  que incluye tests de integración avanzada y workflows E2E.
        """)
    
    @staticmethod
    def main():
        """Función principal de la CLI"""
        # Obtener comando
        command = sys.argv[1] if len(sys.argv) > 1 else 'all'
        
        if command == 'help':
            Phase3CLIRunner.show_help()
            return
        
        # Crear runner
        runner = Phase3TestRunner()
        
        try:
            if command == 'quick':
                success = runner.run_quick_validation()
            elif command == 'all':
                success = runner.run_all_tests()
            else:
                print(f"❌ Comando desconocido: {command}")
                Phase3CLIRunner.show_help()
                sys.exit(1)
            
            # Generar reporte
            runner.generate_report()
            
            # Exit code
            sys.exit(0 if success else 1)
            
        except KeyboardInterrupt:
            print("\n⚠️  Ejecución interrumpida por el usuario")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Error ejecutando tests: {e}")
            print(f"❌ Error inesperado: {e}")
            sys.exit(1)


# ================================
# FUNCIONES DE UTILIDAD ADICIONALES
# ================================

def run_specific_test_class(test_class_name, module_name):
    """Ejecuta una clase de test específica"""
    try:
        module = __import__(module_name, fromlist=[''])
        test_class = getattr(module, test_class_name)
        
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromTestCase(test_class)
        
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        return result.wasSuccessful()
        
    except Exception as e:
        print(f"❌ Error ejecutando {test_class_name}: {e}")
        return False


def validate_test_environment():
    """Valida que el entorno esté configurado para ejecutar tests"""
    print("🔍 Validando entorno de tests...")
    
    required_modules = [
        'unittest',
        'PyQt6.QtTest',
        'rexus.utils.app_logger'
    ]
    
    missing_modules = []
    
    for module_name in required_modules:
        try:
            __import__(module_name)
        except ImportError:
            missing_modules.append(module_name)
    
    if missing_modules:
        print(f"❌ Módulos faltantes: {', '.join(missing_modules)}")
        return False
    
    print("✅ Entorno de tests validado correctamente")
    return True


def check_test_coverage():
    """Verifica que todos los archivos de test de Phase 3 existan"""
    test_files = [
        'test_vidrios_workflows_completos.py',
        'test_notificaciones_workflows_completos.py',
        'test_inventario_integracion_avanzada.py',
        'test_obras_integracion_avanzada.py',
        'test_e2e_workflows_inter_modulos.py',
        'test_database_integration_real.py'
    ]
    
    tests_dir = Path(__file__).parent
    missing_files = []
    
    for test_file in test_files:
        if not (tests_dir / test_file).exists():
            missing_files.append(test_file)
    
    if missing_files:
        print(f"⚠️  Archivos de test faltantes: {', '.join(missing_files)}")
        return False
    
    print("✅ Todos los archivos de test de Phase 3 están presentes")
    return True


# ================================
# EJECUCIÓN PRINCIPAL
# ================================

if __name__ == '__main__':
    print("🎯 REXUS.APP - MASTER PHASE 3 TEST RUNNER")
    print("=" * 80)
    
    # Validar entorno antes de ejecutar
    if not validate_test_environment():
        print("❌ Entorno no válido para ejecutar tests")
        sys.exit(1)
    
    if not check_test_coverage():
        print("⚠️  Algunos archivos de test no están disponibles")
        print("   Los tests faltantes serán saltados automáticamente")
    
    # Ejecutar CLI
    Phase3CLIRunner.main()