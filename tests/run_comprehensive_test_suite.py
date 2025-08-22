# -*- coding: utf-8 -*-
"""
Suite Completa de Tests para Rexus.app - Runner Principal
Ejecuta todos los tests implementados para conseguir cobertura completa del sistema

Fecha: 20/08/2025
Objetivo: Ejecutar y reportar cobertura de 100k USD en tests automatizados
"""

import sys
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Tuple
import json
from datetime import datetime

# Agregar directorio raíz al path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))


class ComprehensiveTestRunner:
    """Runner principal para ejecutar toda la suite de tests."""
    
    def __init__(self):
        self.test_suites = {
            # Tests existentes actualizados
            'critical_modules': {
                'file': 'test_critical_modules.py',
                'description': 'Tests críticos de módulos principales',
                'priority': 'high',
                'estimated_time': 30
            },
            'form_validators': {
                'file': 'test_form_validators_none_handling.py', 
                'description': 'Tests de validadores de formularios',
                'priority': 'high',
                'estimated_time': 15
            },
            'inventario': {
                'file': 'test_inventario_simple.py',
                'description': 'Tests básicos del módulo inventario',
                'priority': 'medium',
                'estimated_time': 20
            },
            'obras': {
                'file': 'test_obras_completo.py',
                'description': 'Tests completos del módulo obras',
                'priority': 'medium', 
                'estimated_time': 25
            },
            'database_integration': {
                'file': 'test_database_integration_migrated.py',
                'description': 'Tests de integración con base de datos',
                'priority': 'high',
                'estimated_time': 20
            },
            
            # Nuevos tests implementados
            'ui_interactions': {
                'file': 'ui/test_ui_interactions.py',
                'description': 'Tests de interacción UI con pytest-qt',
                'priority': 'high',
                'estimated_time': 45
            },
            'compras_complete': {
                'file': 'test_compras_complete.py',
                'description': 'Tests completos del módulo Compras',
                'priority': 'high',
                'estimated_time': 40
            },
            'pedidos_complete': {
                'file': 'test_pedidos_complete.py',
                'description': 'Tests completos del módulo Pedidos',
                'priority': 'high', 
                'estimated_time': 40
            },
            'vidrios_complete': {
                'file': 'test_vidrios_complete.py',
                'description': 'Tests completos del módulo Vidrios',
                'priority': 'high',
                'estimated_time': 35
            },
            'notificaciones_complete': {
                'file': 'test_notificaciones_complete.py',
                'description': 'Tests completos del módulo Notificaciones',
                'priority': 'high',
                'estimated_time': 30
            },
            'form_validations_comprehensive': {
                'file': 'test_form_validations_comprehensive.py',
                'description': 'Tests comprensivos de validaciones de formularios',
                'priority': 'high',
                'estimated_time': 35
            },
            'accessibility_comprehensive': {
                'file': 'test_accessibility_comprehensive.py',
                'description': 'Tests comprensivos de accesibilidad',
                'priority': 'medium',
                'estimated_time': 30
            },
            'e2e_integration_workflows': {
                'file': 'test_e2e_integration_workflows.py',
                'description': 'Tests end-to-end de workflows completos',
                'priority': 'critical',
                'estimated_time': 60
            },
            
            # Tests de auditoría existentes
            'contrast_ui': {
                'file': 'ui/contrast_test.py',
                'description': 'Tests de contraste y estilos UI',
                'priority': 'medium',
                'estimated_time': 15
            },
            'modules_audit': {
                'file': 'audit/modules_audit.py',
                'description': 'Auditoría de módulos del sistema',
                'priority': 'medium',
                'estimated_time': 20
            },
            'edge_cases': {
                'file': 'comprehensive/edge_cases_test.py',
                'description': 'Tests de casos límite',
                'priority': 'medium',
                'estimated_time': 25
            }
        }
        
        self.results = {}
        self.total_tests_run = 0
        self.total_tests_passed = 0
        self.total_tests_failed = 0
        self.total_time = 0
        
    def run_single_test_suite(self, suite_name: str, suite_config: Dict) -> Dict:
        """Ejecuta una suite individual de tests."""
        print(f"\n{'='*80}")
        print(f"EJECUTANDO: {suite_name.upper()}")
        print(f"Descripción: {suite_config['description']}")
        print(f"Prioridad: {suite_config['priority'].upper()}")
        print(f"Tiempo estimado: {suite_config['estimated_time']}s")
        print(f"{'='*80}")
        
        test_file = root_dir / "tests" / suite_config['file']
        
        if not test_file.exists():
            return {
                'status': 'SKIPPED',
                'reason': 'Archivo no encontrado',
                'tests_run': 0,
                'tests_passed': 0,
                'tests_failed': 0,
                'time_taken': 0,
                'output': f"Archivo {test_file} no encontrado"
            }
        
        start_time = time.time()
        
        try:
            # Ejecutar tests con python directamente primero
            if test_file.name.endswith('contrast_test.py') or 'audit' in test_file.name:
                # Tests que se ejecutan directamente con Python
                result = subprocess.run([
                    sys.executable, str(test_file)
                ], capture_output=True, text=True, timeout=suite_config['estimated_time'] * 2)
            else:
                # Tests que usan pytest o unittest
                if 'accessibility' in suite_name or 'ui_interactions' in suite_name:
                    # Tests que requieren pytest-qt
                    result = subprocess.run([
                        sys.executable, "-m", "pytest", str(test_file), 
                        "-v", "-s", "--tb=short", f"--timeout={suite_config['estimated_time']}"
                    ], capture_output=True, text=True, timeout=suite_config['estimated_time'] * 2)
                else:
                    # Tests que usan unittest
                    result = subprocess.run([
                        sys.executable, str(test_file)
                    ], capture_output=True, text=True, timeout=suite_config['estimated_time'] * 2)
            
            end_time = time.time()
            time_taken = end_time - start_time
            
            # Parsear resultados
            output = result.stdout + result.stderr
            tests_info = self._parse_test_output(output, result.returncode)
            
            return {
                'status': 'PASSED' if result.returncode == 0 else 'FAILED',
                'tests_run': tests_info['tests_run'],
                'tests_passed': tests_info['tests_passed'], 
                'tests_failed': tests_info['tests_failed'],
                'time_taken': time_taken,
                'output': output,
                'return_code': result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {
                'status': 'TIMEOUT',
                'reason': f'Timeout después de {suite_config["estimated_time"] * 2}s',
                'tests_run': 0,
                'tests_passed': 0,
                'tests_failed': 0,
                'time_taken': suite_config['estimated_time'] * 2,
                'output': 'Test suite timeout'
            }
        except Exception as e:
            return {
                'status': 'ERROR',
                'reason': str(e),
                'tests_run': 0,
                'tests_passed': 0,
                'tests_failed': 0,
                'time_taken': time.time() - start_time,
                'output': f"Error ejecutando tests: {e}"
            }
    
    def _parse_test_output(self, output: str, return_code: int) -> Dict:
        """Parsea la salida de tests para extraer estadísticas."""
        tests_run = 0
        tests_passed = 0
        tests_failed = 0
        
        # Patrones comunes en salidas de tests
        import re
        
        # Unittest patterns
        unittest_pattern = r'Ran (\d+) tests? in'
        unittest_match = re.search(unittest_pattern, output)
        if unittest_match:
            tests_run = int(unittest_match.group(1))
            if return_code == 0:
                tests_passed = tests_run
            else:
                # Buscar fallos
                failed_pattern = r'FAILED \(.*?failures=(\d+)'
                failed_match = re.search(failed_pattern, output)
                if failed_match:
                    tests_failed = int(failed_match.group(1))
                    tests_passed = tests_run - tests_failed
                else:
                    tests_failed = tests_run
        
        # Pytest patterns
        pytest_pattern = r'(\d+) passed.*?(\d+) failed'
        pytest_match = re.search(pytest_pattern, output)
        if pytest_match:
            tests_passed = int(pytest_match.group(1))
            tests_failed = int(pytest_match.group(2))
            tests_run = tests_passed + tests_failed
        
        # Fallback: si no encontramos patrones específicos
        if tests_run == 0:
            if '✅' in output or 'PASSED' in output:
                tests_run = 1
                tests_passed = 1 if return_code == 0 else 0
                tests_failed = 0 if return_code == 0 else 1
            elif '❌' in output or 'FAILED' in output:
                tests_run = 1
                tests_passed = 0
                tests_failed = 1
            else:
                # Estimar basado en contenido
                test_methods = len(re.findall(r'test_\w+', output))
                if test_methods > 0:
                    tests_run = test_methods
                    tests_passed = test_methods if return_code == 0 else 0
                    tests_failed = 0 if return_code == 0 else test_methods
        
        return {
            'tests_run': tests_run,
            'tests_passed': tests_passed,
            'tests_failed': tests_failed
        }
    
    def run_all_tests(self, priority_filter: str = None) -> Dict:
        """Ejecuta toda la suite de tests."""
        print(f"\n🚀 INICIANDO SUITE COMPLETA DE TESTS - REXUS.APP")
        print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🎯 Objetivo: Cobertura completa de $100K USD en tests")
        
        if priority_filter:
            print(f"🔍 Filtro de prioridad: {priority_filter.upper()}")
        
        # Filtrar suites por prioridad si se especifica
        suites_to_run = {}
        if priority_filter:
            for name, config in self.test_suites.items():
                if config['priority'] == priority_filter:
                    suites_to_run[name] = config
        else:
            suites_to_run = self.test_suites
        
        total_estimated_time = sum(config['estimated_time'] for config in suites_to_run.values())
        print(f"⏱️ Tiempo total estimado: {total_estimated_time}s ({total_estimated_time/60:.1f} minutos)")
        print(f"📊 Total de suites: {len(suites_to_run)}")
        
        start_time = time.time()
        
        # Ejecutar en orden de prioridad
        priority_order = ['critical', 'high', 'medium', 'low']
        for priority in priority_order:
            priority_suites = {name: config for name, config in suites_to_run.items() 
                             if config['priority'] == priority}
            
            if priority_suites:
                print(f"\n🔥 EJECUTANDO TESTS DE PRIORIDAD: {priority.upper()}")
                print(f"{'='*60}")
                
                for suite_name, suite_config in priority_suites.items():
                    result = self.run_single_test_suite(suite_name, suite_config)
                    self.results[suite_name] = result
                    
                    # Actualizar totales
                    self.total_tests_run += result.get('tests_run', 0)
                    self.total_tests_passed += result.get('tests_passed', 0) 
                    self.total_tests_failed += result.get('tests_failed', 0)
                    
                    # Mostrar resultado inmediato
                    status_emoji = {
                        'PASSED': '✅',
                        'FAILED': '❌', 
                        'SKIPPED': '⚠️',
                        'TIMEOUT': '⏰',
                        'ERROR': '💥'
                    }.get(result['status'], '❓')
                    
                    print(f"\n{status_emoji} {suite_name}: {result['status']} "
                          f"({result.get('tests_passed', 0)}/{result.get('tests_run', 0)} tests passed, "
                          f"{result.get('time_taken', 0):.1f}s)")
                    
                    if result['status'] in ['FAILED', 'ERROR', 'TIMEOUT']:
                        print(f"   Razón: {result.get('reason', 'Ver output para detalles')}")
        
        self.total_time = time.time() - start_time
        
        return self._generate_final_report()
    
    def _generate_final_report(self) -> Dict:
        """Genera el reporte final de todos los tests."""
        
        # Calcular estadísticas
        suites_passed = len([r for r in self.results.values() if r['status'] == 'PASSED'])
        suites_failed = len([r for r in self.results.values() if r['status'] == 'FAILED'])
        suites_skipped = len([r for r in self.results.values() if r['status'] == 'SKIPPED'])
        suites_error = len([r for r in self.results.values() if r['status'] in ['ERROR', 'TIMEOUT']])
        
        success_rate = (self.total_tests_passed / self.total_tests_run * 100) if self.total_tests_run > 0 else 0
        
        # Generar reporte
        report = {
            'execution_summary': {
                'total_suites': len(self.results),
                'suites_passed': suites_passed,
                'suites_failed': suites_failed,
                'suites_skipped': suites_skipped,
                'suites_error': suites_error,
                'total_tests_run': self.total_tests_run,
                'total_tests_passed': self.total_tests_passed,
                'total_tests_failed': self.total_tests_failed,
                'success_rate': success_rate,
                'total_time': self.total_time,
                'timestamp': datetime.now().isoformat()
            },
            'suite_details': self.results,
            'coverage_assessment': self._assess_coverage(),
            'recommendations': self._generate_recommendations()
        }
        
        return report
    
    def _assess_coverage(self) -> Dict:
        """Evalúa la cobertura de tests implementada."""
        
        # Módulos principales cubiertos
        modules_covered = []
        if 'compras_complete' in self.results and self.results['compras_complete']['status'] == 'PASSED':
            modules_covered.append('Compras')
        if 'pedidos_complete' in self.results and self.results['pedidos_complete']['status'] == 'PASSED':
            modules_covered.append('Pedidos') 
        if 'vidrios_complete' in self.results and self.results['vidrios_complete']['status'] == 'PASSED':
            modules_covered.append('Vidrios')
        if 'notificaciones_complete' in self.results and self.results['notificaciones_complete']['status'] == 'PASSED':
            modules_covered.append('Notificaciones')
        if 'inventario' in self.results and self.results['inventario']['status'] == 'PASSED':
            modules_covered.append('Inventario')
        if 'obras' in self.results and self.results['obras']['status'] == 'PASSED':
            modules_covered.append('Obras')
        
        # Áreas de testing cubiertas
        areas_covered = []
        if 'ui_interactions' in self.results and self.results['ui_interactions']['status'] == 'PASSED':
            areas_covered.append('Interacciones UI')
        if 'form_validations_comprehensive' in self.results and self.results['form_validations_comprehensive']['status'] == 'PASSED':
            areas_covered.append('Validaciones de Formularios')
        if 'accessibility_comprehensive' in self.results and self.results['accessibility_comprehensive']['status'] == 'PASSED':
            areas_covered.append('Accesibilidad')
        if 'e2e_integration_workflows' in self.results and self.results['e2e_integration_workflows']['status'] == 'PASSED':
            areas_covered.append('Workflows E2E')
        
        # Calcular valor estimado de cobertura
        base_value_per_module = 8000  # $8K por módulo principal
        base_value_per_area = 5000    # $5K por área especializada
        
        estimated_value = (len(modules_covered) * base_value_per_module + 
                          len(areas_covered) * base_value_per_area)
        
        return {
            'modules_covered': modules_covered,
            'areas_covered': areas_covered,
            'total_modules': len(modules_covered),
            'total_areas': len(areas_covered),
            'estimated_coverage_value_usd': estimated_value,
            'coverage_percentage': min(estimated_value / 100000 * 100, 100),
            'goal_achievement': estimated_value >= 100000
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Genera recomendaciones basadas en los resultados."""
        recommendations = []
        
        # Basado en fallos
        failed_suites = [name for name, result in self.results.items() if result['status'] == 'FAILED']
        if failed_suites:
            recommendations.append(f"Revisar y corregir los tests fallidos: {', '.join(failed_suites)}")
        
        # Basado en tests no ejecutados
        skipped_suites = [name for name, result in self.results.items() if result['status'] == 'SKIPPED']
        if skipped_suites:
            recommendations.append(f"Implementar los tests faltantes: {', '.join(skipped_suites)}")
        
        # Basado en cobertura
        coverage = self._assess_coverage()
        if coverage['estimated_coverage_value_usd'] < 100000:
            remaining = 100000 - coverage['estimated_coverage_value_usd']
            recommendations.append(f"Implementar ${remaining:,} USD adicionales en tests para alcanzar meta")
        
        # Recomendaciones específicas
        if 'accessibility_comprehensive' not in self.results or self.results['accessibility_comprehensive']['status'] != 'PASSED':
            recommendations.append("Priorizar implementación de tests de accesibilidad")
        
        if 'e2e_integration_workflows' not in self.results or self.results['e2e_integration_workflows']['status'] != 'PASSED':
            recommendations.append("Completar tests end-to-end para workflows críticos")
        
        return recommendations
    
    def print_final_report(self, report: Dict):
        """Imprime el reporte final formateado."""
        
        print(f"\n{'='*100}")
        print(f"🎯 REPORTE FINAL - SUITE COMPLETA DE TESTS REXUS.APP")
        print(f"{'='*100}")
        
        summary = report['execution_summary']
        coverage = report['coverage_assessment']
        
        # Resumen de ejecución
        print(f"\n📊 RESUMEN DE EJECUCIÓN:")
        print(f"   • Total de suites ejecutadas: {summary['total_suites']}")
        print(f"   • Suites exitosas: {summary['suites_passed']} ✅")
        print(f"   • Suites fallidas: {summary['suites_failed']} ❌") 
        print(f"   • Suites saltadas: {summary['suites_skipped']} ⚠️")
        print(f"   • Suites con error: {summary['suites_error']} 💥")
        
        print(f"\n🧪 TESTS INDIVIDUALES:")
        print(f"   • Tests ejecutados: {summary['total_tests_run']}")
        print(f"   • Tests exitosos: {summary['total_tests_passed']} ✅")
        print(f"   • Tests fallidos: {summary['total_tests_failed']} ❌")
        print(f"   • Tasa de éxito: {summary['success_rate']:.1f}% 📈")
        
        print(f"\n⏱️ TIEMPO DE EJECUCIÓN:")
        print(f"   • Tiempo total: {summary['total_time']:.1f}s ({summary['total_time']/60:.1f} minutos)")
        
        # Cobertura
        print(f"\n🎯 COBERTURA DE TESTS:")
        print(f"   • Módulos cubiertos: {coverage['total_modules']} ({', '.join(coverage['modules_covered'])})")
        print(f"   • Áreas cubiertas: {coverage['total_areas']} ({', '.join(coverage['areas_covered'])})")
        print(f"   • Valor estimado: ${coverage['estimated_coverage_value_usd']:,} USD 💰")
        print(f"   • Porcentaje de meta: {coverage['coverage_percentage']:.1f}% de $100K USD")
        
        # Status de meta
        if coverage['goal_achievement']:
            print(f"\n🎉 ¡META ALCANZADA! Se ha logrado cobertura de tests por valor de $100K+ USD")
        else:
            remaining = 100000 - coverage['estimated_coverage_value_usd']
            print(f"\n🔄 Meta en progreso: Faltan ${remaining:,} USD en cobertura de tests")
        
        # Recomendaciones
        if report['recommendations']:
            print(f"\n💡 RECOMENDACIONES:")
            for i, rec in enumerate(report['recommendations'], 1):
                print(f"   {i}. {rec}")
        
        # Status final
        overall_success = (summary['suites_failed'] + summary['suites_error']) == 0 and coverage['coverage_percentage'] >= 80
        
        if overall_success:
            print(f"\n🎊 RESULTADO FINAL: ÉXITO COMPLETO")
            print(f"   La suite de tests está funcionando correctamente y proporciona cobertura robusta.")
        else:
            print(f"\n⚠️ RESULTADO FINAL: REQUIERE ATENCIÓN")
            print(f"   Hay áreas que necesitan ser corregidas o completadas.")
        
        print(f"\n{'='*100}")
        print(f"📅 Reporte generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*100}")
    
    def save_report(self, report: Dict, filename: str = None):
        """Guarda el reporte en archivo JSON."""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"test_report_{timestamp}.json"
        
        report_file = root_dir / "tests" / filename
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\n💾 Reporte guardado en: {report_file}")


def main():
    """Función principal para ejecutar la suite completa."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Suite Completa de Tests Rexus.app')
    parser.add_argument('--priority', choices=['critical', 'high', 'medium', 'low'], 
                       help='Filtrar por prioridad de tests')
    parser.add_argument('--save-report', action='store_true', 
                       help='Guardar reporte en archivo JSON')
    parser.add_argument('--quick', action='store_true',
                       help='Ejecutar solo tests críticos y de alta prioridad')
    
    args = parser.parse_args()
    
    runner = ComprehensiveTestRunner()
    
    # Determinar filtro de prioridad
    priority_filter = args.priority
    if args.quick:
        # Modo rápido: solo critical y high
        priority_filter = None
        runner.test_suites = {name: config for name, config in runner.test_suites.items() 
                             if config['priority'] in ['critical', 'high']}
    
    # Ejecutar tests
    try:
        report = runner.run_all_tests(priority_filter)
        
        # Mostrar reporte
        runner.print_final_report(report)
        
        # Guardar reporte si se solicita
        if args.save_report:
            runner.save_report(report)
        
        # Determinar código de salida
        success = (report['execution_summary']['suites_failed'] + 
                  report['execution_summary']['suites_error']) == 0
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print(f"\n\n⚠️ Ejecución interrumpida por el usuario")
        return 2
    except Exception as e:
        print(f"\n\n💥 Error crítico ejecutando tests: {e}")
        return 3


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)