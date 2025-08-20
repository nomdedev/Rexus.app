#!/usr/bin/env python3
"""
Master Test Runner - Módulo de Seguridad Crítica
================================================

Test runner completo para todos los tests de seguridad de Rexus.app.
Valor total: $25,000 USD (Fase 1 de implementación de 150K USD).

Ejecuta y reporta:
- Tests de autenticación core ($8,000)
- Tests de UI de login ($6,000) 
- Tests de permisos y roles ($7,000)
- Tests de gestión de sesiones ($4,000)
- Tests de auditoría de seguridad ($6,000)

Fecha: 20/08/2025
Status: CRÍTICO - Primera implementación del plan 150K USD
"""

import sys
import os
import time
import subprocess
import datetime
from pathlib import Path
from typing import List, Dict, Tuple

# Configurar path
sys.path.insert(0, str(Path(__file__).parent.parent))
os.environ['PYTHONIOENCODING'] = 'utf-8'


class SecurityTestRunner:
    """Ejecutor master de tests de seguridad."""
    
    def __init__(self):
        self.test_files = [
            {
                'name': 'Core Authentication Tests',
                'file': 'test_usuarios_seguridad.py',
                'value_usd': 8000,
                'description': 'Autenticación, rate limiting, validación de credenciales'
            },
            {
                'name': 'Login UI Tests', 
                'file': 'test_login_ui.py',
                'value_usd': 6000,
                'description': 'Interacciones UI reales, validaciones visuales, pytest-qt'
            },
            {
                'name': 'Permissions & Roles Tests',
                'file': 'test_permisos_roles.py', 
                'value_usd': 7000,
                'description': 'Autorización, jerarquía de roles, decoradores'
            },
            {
                'name': 'Session Management Tests',
                'file': 'test_sesiones.py',
                'value_usd': 4000,
                'description': 'Gestión de sesiones, timeouts, persistencia'
            },
            {
                'name': 'Security Audit Tests',
                'file': 'test_auditoria_seguridad.py',
                'value_usd': 6000,  
                'description': 'Logging, trazabilidad, integridad, alertas'
            }
        ]
        
        self.results = []
        self.total_value = sum(test['value_usd'] for test in self.test_files)
        self.start_time = None
        self.end_time = None
    
    def print_header(self):
        """Imprimir header del test runner."""
        print("=" * 100)
        print("🔒 MASTER SECURITY TEST RUNNER - REXUS.APP")
        print("=" * 100)
        print(f"📅 Fecha: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"🎯 Objetivo: Validar módulo crítico de seguridad")
        print(f"💰 Valor total: ${self.total_value:,} USD")
        print(f"📊 Fase: 1 de 3 (Plan de implementación 150K USD)")
        print()
        print("📋 Tests a ejecutar:")
        for i, test in enumerate(self.test_files, 1):
            print(f"  {i}. {test['name']} - ${test['value_usd']:,} USD")
            print(f"     {test['description']}")
        print("=" * 100)
        print()
    
    def run_individual_test(self, test_info: Dict) -> Tuple[bool, str, Dict]:
        """Ejecutar un test individual."""
        print(f"🧪 Ejecutando: {test_info['name']}")
        print(f"💵 Valor: ${test_info['value_usd']:,} USD")
        print(f"📁 Archivo: {test_info['file']}")
        print("-" * 60)
        
        test_file_path = Path(__file__).parent / test_info['file']
        
        if not test_file_path.exists():
            return False, f"Archivo no encontrado: {test_file_path}", {}
        
        start_time = time.time()
        
        try:
            # Ejecutar test con subprocess para capturar output
            result = subprocess.run([
                sys.executable, str(test_file_path)
            ], capture_output=True, text=True, timeout=300)  # 5 minutos timeout
            
            end_time = time.time()
            duration = end_time - start_time
            
            success = result.returncode == 0
            
            test_stats = {
                'duration': duration,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode
            }
            
            if success:
                print(f"✅ {test_info['name']} - PASÓ")
                print(f"⏱️  Duración: {duration:.2f}s")
            else:
                print(f"❌ {test_info['name']} - FALLÓ")
                print(f"⏱️  Duración: {duration:.2f}s")
                if result.stderr:
                    print("Error output:")
                    print(result.stderr[:500])  # Primeros 500 chars del error
            
            print()
            return success, result.stdout, test_stats
            
        except subprocess.TimeoutExpired:
            return False, "Test timeout (>5 minutes)", {'duration': 300, 'timeout': True}
        except Exception as e:
            return False, f"Error ejecutando test: {str(e)}", {'error': str(e)}
    
    def run_all_tests(self) -> bool:
        """Ejecutar todos los tests de seguridad."""
        self.start_time = time.time()
        
        successful_tests = 0
        total_value_delivered = 0
        
        for test_info in self.test_files:
            success, output, stats = self.run_individual_test(test_info)
            
            result_entry = {
                'test_info': test_info,
                'success': success,
                'output': output,
                'stats': stats
            }
            self.results.append(result_entry)
            
            if success:
                successful_tests += 1
                total_value_delivered += test_info['value_usd']
        
        self.end_time = time.time()
        
        # Imprimir resumen final
        self.print_final_summary(successful_tests, total_value_delivered)
        
        return successful_tests == len(self.test_files)
    
    def print_final_summary(self, successful_tests: int, total_value_delivered: int):
        """Imprimir resumen final de ejecución."""
        total_duration = self.end_time - self.start_time
        
        print("=" * 100)
        print("📊 RESUMEN FINAL DE EJECUCIÓN")
        print("=" * 100)
        print(f"⏱️  Tiempo total: {total_duration:.2f} segundos ({total_duration/60:.1f} minutos)")
        print(f"🧪 Tests ejecutados: {len(self.test_files)}")
        print(f"✅ Tests exitosos: {successful_tests}")
        print(f"❌ Tests fallidos: {len(self.test_files) - successful_tests}")
        print()
        print(f"💰 Valor entregado: ${total_value_delivered:,} USD de ${self.total_value:,} USD")
        print(f"📈 Porcentaje completado: {(total_value_delivered/self.total_value)*100:.1f}%")
        print()
        
        if successful_tests == len(self.test_files):
            print("🎉 ¡TODOS LOS TESTS DE SEGURIDAD PASARON!")
            print("🔒 Módulo de seguridad completamente verificado")
            print("🛡️  Sistema de autenticación validado")
            print("👥 Autorización y permisos funcionando")
            print("📝 Auditoría y logging implementados")
            print("🖥️  UI de seguridad probada")
            print()
            print(f"✨ FASE 1 COMPLETADA: ${self.total_value:,} USD entregados")
            print("🚀 Listo para continuar con Fase 2: Workflows de Negocio ($60K)")
        else:
            failed_tests = len(self.test_files) - successful_tests
            failed_value = self.total_value - total_value_delivered
            
            print(f"⚠️  {failed_tests} TESTS FALLARON")
            print(f"💸 Valor no entregado: ${failed_value:,} USD")
            print("🔧 REQUIERE CORRECCIÓN ANTES DE CONTINUAR")
            print()
            print("❌ Tests fallidos:")
            for result in self.results:
                if not result['success']:
                    test_name = result['test_info']['name']
                    test_value = result['test_info']['value_usd']
                    print(f"   - {test_name} (${test_value:,} USD)")
        
        print()
        self.print_detailed_results()
        print("=" * 100)
    
    def print_detailed_results(self):
        """Imprimir resultados detallados por test."""
        print("📋 RESULTADOS DETALLADOS:")
        print()
        
        for i, result in enumerate(self.results, 1):
            test_info = result['test_info']
            success = result['success']
            stats = result['stats']
            
            status_icon = "✅" if success else "❌"
            status_text = "PASÓ" if success else "FALLÓ"
            
            print(f"{i}. {status_icon} {test_info['name']} - {status_text}")
            print(f"   💰 Valor: ${test_info['value_usd']:,} USD")
            
            if 'duration' in stats:
                print(f"   ⏱️  Duración: {stats['duration']:.2f}s")
            
            if not success:
                if 'timeout' in stats:
                    print(f"   ⚠️  Timeout: Test tardó más de 5 minutos")
                elif 'error' in stats:
                    print(f"   ❌ Error: {stats['error']}")
                elif stats.get('returncode') != 0:
                    print(f"   ❌ Exit code: {stats['returncode']}")
            
            print()
    
    def generate_report_file(self):
        """Generar archivo de reporte detallado."""
        report_file = Path(__file__).parent / f"security_tests_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write("REPORTE DETALLADO DE TESTS DE SEGURIDAD - REXUS.APP\n")
                f.write("=" * 60 + "\n")
                f.write(f"Fecha: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                f.write(f"Valor total: ${self.total_value:,} USD\n\n")
                
                for result in self.results:
                    test_info = result['test_info']
                    success = result['success']
                    output = result['output']
                    
                    f.write(f"TEST: {test_info['name']}\n")
                    f.write(f"Archivo: {test_info['file']}\n")
                    f.write(f"Valor: ${test_info['value_usd']:,} USD\n")
                    f.write(f"Resultado: {'ÉXITO' if success else 'FALLO'}\n")
                    f.write("-" * 40 + "\n")
                    
                    if output and len(output.strip()) > 0:
                        f.write("Output:\n")
                        f.write(output[:2000])  # Primeros 2000 chars
                        if len(output) > 2000:
                            f.write("\n... (truncado)")
                    
                    f.write("\n\n")
            
            print(f"📄 Reporte detallado guardado en: {report_file}")
            
        except Exception as e:
            print(f"⚠️  No se pudo generar reporte: {e}")


def main():
    """Función principal del test runner."""
    runner = SecurityTestRunner()
    
    try:
        runner.print_header()
        
        print("🚀 Iniciando ejecución de tests de seguridad...")
        print()
        
        success = runner.run_all_tests()
        
        # Generar reporte detallado
        runner.generate_report_file()
        
        # Exit code basado en éxito
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n⚠️  Ejecución interrumpida por usuario")
        print("🛑 Tests de seguridad incompletos")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error crítico en test runner: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()