# -*- coding: utf-8 -*-
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

logger = get_logger()


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