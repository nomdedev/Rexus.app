#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Automated Validator - Sistema de Validación Automática
Valida integridad, calidad y funcionalidad del sistema de tests
"""

import subprocess
import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Any
import re

# Configurar encoding
os.environ['PYTHONIOENCODING'] = 'utf-8'

class AutomatedTestValidator:
    """Sistema de validación automática para tests."""
    
    def __init__(self):
        self.test_directory = Path(__file__).parent.parent
        self.project_root = self.test_directory.parent
        self.validation_results = {}
        
    def run_full_validation(self) -> Dict[str, Any]:
        """Ejecuta validación completa del sistema."""
        print("SISTEMA DE VALIDACION AUTOMATICA")
        print("=" * 50)
        
        validations = [
            ("Estructura de archivos", self.validate_file_structure),
            ("Calidad de codigo", self.validate_code_quality),
            ("Funcionalidad de tests", self.validate_test_functionality),
            ("Cobertura de modulos", self.validate_module_coverage),
            ("Performance general", self.validate_performance),
            ("Integridad de datos", self.validate_data_integrity)
        ]
        
        for name, validator in validations:
            print(f"\nValidando: {name}")
            print("-" * 30)
            try:
                result = validator()
                self.validation_results[name] = result
                self.print_validation_result(name, result)
            except Exception as e:
                self.validation_results[name] = {
                    'status': 'ERROR',
                    'message': f'Error durante validacion: {str(e)}'
                }
                print(f"ERROR: {str(e)}")
        
        self.generate_validation_report()
        return self.validation_results
    
    def validate_file_structure(self) -> Dict[str, Any]:
        """Valida la estructura de archivos de tests."""
        expected_structure = {
            'unit': ['usuarios', 'inventario', 'configuracion', 'compras', 'administracion', 'auditoria', 'obras'],
            'integration': ['test_compras_inventario_integration.py'],
            'e2e': ['test_workflow_compra_completo.py'],
            'utils': ['security_helpers.py', 'mock_factories.py'],
            'runners': ['performance_optimizer.py', 'automated_validator.py']
        }
        
        missing_items = []
        existing_items = []
        
        for category, items in expected_structure.items():
            category_path = self.test_directory / category
            if not category_path.exists():
                missing_items.append(f"Directorio: {category}")
                continue
                
            existing_items.append(f"Directorio: {category}")
            
            for item in items:
                item_path = category_path / item
                if item.endswith('.py'):
                    # Es un archivo
                    if item_path.exists():
                        existing_items.append(f"Archivo: {category}/{item}")
                    else:
                        missing_items.append(f"Archivo: {category}/{item}")
                else:
                    # Es un subdirectorio
                    if item_path.exists():
                        existing_items.append(f"Subdirectorio: {category}/{item}")
                        # Verificar archivos de test dentro del subdirectorio
                        test_files = list(item_path.glob("test_*.py"))
                        if test_files:
                            existing_items.append(f"Tests en {category}/{item}: {len(test_files)} archivos")
                        else:
                            missing_items.append(f"Tests en {category}/{item}: Sin archivos test_*.py")
                    else:
                        missing_items.append(f"Subdirectorio: {category}/{item}")
        
        return {
            'status': 'PASSED' if not missing_items else 'WARNING',
            'existing': len(existing_items),
            'missing': len(missing_items),
            'missing_items': missing_items,
            'existing_items': existing_items
        }
    
    def validate_code_quality(self) -> Dict[str, Any]:
        """Valida la calidad del código en tests."""
        quality_issues = []
        code_metrics = {
            'total_files': 0,
            'lines_of_code': 0,
            'files_with_encoding': 0,
            'files_with_docstrings': 0
        }
        
        # Buscar todos los archivos Python en tests
        for py_file in self.test_directory.rglob("*.py"):
            if py_file.name.startswith('__'):
                continue
                
            code_metrics['total_files'] += 1
            
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                    code_metrics['lines_of_code'] += len(lines)
                    
                    # Verificar encoding UTF-8
                    if 'utf-8' in content[:200]:
                        code_metrics['files_with_encoding'] += 1
                    else:
                        quality_issues.append(f"Sin encoding UTF-8: {py_file.relative_to(self.test_directory)}")
                    
                    # Verificar docstrings
                    if '"""' in content:
                        code_metrics['files_with_docstrings'] += 1
                    
                    # Buscar problemas comunes
                    if 'password' in content.lower() and 'hash' not in content.lower():
                        quality_issues.append(f"Posible password hardcodeado: {py_file.relative_to(self.test_directory)}")
                    
                    if 'print(' in content:
                        # Contar prints excesivos
                        print_count = content.count('print(')
                        if print_count > 10:
                            quality_issues.append(f"Muchos prints de debug: {py_file.relative_to(self.test_directory)} ({print_count})")
                            
            except Exception as e:
                quality_issues.append(f"Error leyendo {py_file.relative_to(self.test_directory)}: {str(e)}")
        
        quality_score = 100
        if quality_issues:
            quality_score = max(0, 100 - (len(quality_issues) * 10))
        
        return {
            'status': 'PASSED' if quality_score >= 80 else 'WARNING' if quality_score >= 60 else 'FAILED',
            'quality_score': quality_score,
            'metrics': code_metrics,
            'issues': quality_issues
        }
    
    def validate_test_functionality(self) -> Dict[str, Any]:
        """Valida que los tests funcionen correctamente."""
        try:
            # Ejecutar tests con timeout
            cmd = ['python', '-m', 'pytest', '--tb=no', '-q', '--timeout=120']
            
            result = subprocess.run(
                cmd,
                cwd=self.test_directory,
                capture_output=True,
                text=True,
                timeout=180
            )
            
            # Parsear resultados
            output = result.stdout
            
            passed_match = re.search(r'(\d+) passed', output)
            failed_match = re.search(r'(\d+) failed', output)
            error_match = re.search(r'(\d+) error', output)
            
            passed = int(passed_match.group(1)) if passed_match else 0
            failed = int(failed_match.group(1)) if failed_match else 0
            errors = int(error_match.group(1)) if error_match else 0
            
            total = passed + failed + errors
            success_rate = (passed / total * 100) if total > 0 else 0
            
            return {
                'status': 'PASSED' if success_rate >= 95 else 'WARNING' if success_rate >= 80 else 'FAILED',
                'passed': passed,
                'failed': failed,
                'errors': errors,
                'total': total,
                'success_rate': success_rate,
                'output': output[:500] if result.stderr else output[:500]
            }
            
        except subprocess.TimeoutExpired:
            return {
                'status': 'FAILED',
                'message': 'Tests excedieron timeout de 3 minutos'
            }
        except Exception as e:
            return {
                'status': 'ERROR',
                'message': f'Error ejecutando tests: {str(e)}'
            }
    
    def validate_module_coverage(self) -> Dict[str, Any]:
        """Valida la cobertura de módulos."""
        expected_modules = [
            'usuarios', 'inventario', 'configuracion', 
            'compras', 'administracion', 'auditoria', 'obras'
        ]
        
        covered_modules = []
        missing_modules = []
        
        for module in expected_modules:
            module_path = self.test_directory / 'unit' / module
            if module_path.exists():
                test_files = list(module_path.glob("test_*.py"))
                if test_files:
                    covered_modules.append(f"{module} ({len(test_files)} archivos)")
                else:
                    missing_modules.append(f"{module} (sin tests)")
            else:
                missing_modules.append(f"{module} (sin directorio)")
        
        coverage_percentage = (len(covered_modules) / len(expected_modules)) * 100
        
        return {
            'status': 'PASSED' if coverage_percentage >= 90 else 'WARNING' if coverage_percentage >= 70 else 'FAILED',
            'coverage_percentage': coverage_percentage,
            'covered_modules': covered_modules,
            'missing_modules': missing_modules,
            'total_expected': len(expected_modules)
        }
    
    def validate_performance(self) -> Dict[str, Any]:
        """Valida la performance de los tests."""
        try:
            # Ejecutar test rápido para medir performance
            cmd = ['python', '-m', 'pytest', '--durations=5', '--tb=no', '-q']
            
            import time
            start_time = time.time()
            
            result = subprocess.run(
                cmd,
                cwd=self.test_directory,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Analizar durations
            output = result.stdout
            slow_tests = []
            
            for line in output.split('\n'):
                if 's call' in line and '::' in line:
                    # Línea como "0.50s call     tests/unit/usuarios/test_auth.py::TestUsuariosAuth::test_login_admin_success"
                    time_match = re.match(r'(\d+\.\d+)s', line)
                    if time_match:
                        test_time = float(time_match.group(1))
                        if test_time > 1.0:  # Tests que toman más de 1 segundo
                            slow_tests.append(f"{line.strip()}")
            
            return {
                'status': 'PASSED' if execution_time < 30 else 'WARNING' if execution_time < 60 else 'FAILED',
                'execution_time': execution_time,
                'slow_tests_count': len(slow_tests),
                'slow_tests': slow_tests[:5],  # Solo primeros 5
                'performance_rating': 'Excellent' if execution_time < 15 else 'Good' if execution_time < 30 else 'Needs Improvement'
            }
            
        except Exception as e:
            return {
                'status': 'ERROR',
                'message': f'Error validando performance: {str(e)}'
            }
    
    def validate_data_integrity(self) -> Dict[str, Any]:
        """Valida la integridad de datos de prueba."""
        integrity_issues = []
        
        # Verificar security_helpers.py
        security_file = self.test_directory / 'utils' / 'security_helpers.py'
        if security_file.exists():
            try:
                with open(security_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                if 'password123' in content.lower() or 'admin123' in content.lower():
                    integrity_issues.append("Passwords genéricos detectados en security_helpers.py")
                
                if 'TestSecurityManager' not in content:
                    integrity_issues.append("TestSecurityManager no encontrado en security_helpers.py")
                    
            except Exception as e:
                integrity_issues.append(f"Error leyendo security_helpers.py: {str(e)}")
        else:
            integrity_issues.append("security_helpers.py no encontrado")
        
        # Verificar mock_factories.py
        mock_file = self.test_directory / 'utils' / 'mock_factories.py'
        if not mock_file.exists():
            integrity_issues.append("mock_factories.py no encontrado")
        
        return {
            'status': 'PASSED' if not integrity_issues else 'FAILED',
            'issues_count': len(integrity_issues),
            'issues': integrity_issues
        }
    
    def print_validation_result(self, name: str, result: Dict[str, Any]):
        """Imprime resultado de validación."""
        status = result.get('status', 'UNKNOWN')
        status_symbol = {
            'PASSED': 'PASS',
            'WARNING': 'WARN', 
            'FAILED': 'FAIL',
            'ERROR': 'ERR'
        }.get(status, '???')
        
        print(f"[{status_symbol}] {name}")
        
        # Imprimir detalles específicos
        if 'success_rate' in result:
            print(f"    Tasa de éxito: {result['success_rate']:.1f}% ({result['passed']}/{result['total']} tests)")
        
        if 'coverage_percentage' in result:
            print(f"    Cobertura: {result['coverage_percentage']:.1f}% ({len(result['covered_modules'])}/{result['total_expected']} módulos)")
        
        if 'execution_time' in result:
            print(f"    Tiempo: {result['execution_time']:.1f}s ({result['performance_rating']})")
        
        if 'quality_score' in result:
            print(f"    Calidad: {result['quality_score']}/100")
        
        if result.get('issues'):
            print(f"    Problemas: {len(result['issues'])} detectados")
    
    def generate_validation_report(self):
        """Genera reporte final de validación."""
        print("\n" + "=" * 50)
        print("REPORTE FINAL DE VALIDACION")
        print("=" * 50)
        
        total_validations = len(self.validation_results)
        passed = sum(1 for r in self.validation_results.values() if r.get('status') == 'PASSED')
        warnings = sum(1 for r in self.validation_results.values() if r.get('status') == 'WARNING')
        failed = sum(1 for r in self.validation_results.values() if r.get('status') == 'FAILED')
        errors = sum(1 for r in self.validation_results.values() if r.get('status') == 'ERROR')
        
        print(f"\nRESUMEN:")
        print(f"  Total validaciones: {total_validations}")
        print(f"  Pasadas: {passed}")
        print(f"  Advertencias: {warnings}")
        print(f"  Fallidas: {failed}")
        print(f"  Errores: {errors}")
        
        overall_score = ((passed * 100) + (warnings * 75) + (failed * 25) + (errors * 0)) / total_validations
        print(f"\nPUNTUACION GENERAL: {overall_score:.1f}/100")
        
        if overall_score >= 90:
            print("ESTADO: EXCELENTE - Sistema listo para producción")
        elif overall_score >= 80:
            print("ESTADO: BUENO - Requiere ajustes menores")
        elif overall_score >= 70:
            print("ESTADO: ACEPTABLE - Requiere mejoras importantes")
        else:
            print("ESTADO: CRITICO - Requiere correcciones inmediatas")
        
        # Recomendaciones
        print(f"\nRECOMENDACIONES:")
        if failed > 0 or errors > 0:
            print("  - Corregir validaciones fallidas y errores inmediatamente")
        if warnings > 0:
            print("  - Revisar y resolver advertencias")
        if overall_score < 90:
            print("  - Ejecutar análisis detallado de problemas específicos")
        if overall_score >= 90:
            print("  - Mantener calidad actual con monitoreo continuo")

def main():
    """Ejecutar validación automática completa."""
    print("Iniciando validacion automatica del sistema...")
    
    validator = AutomatedTestValidator()
    results = validator.run_full_validation()
    
    print(f"\nValidacion completada. Revisa el reporte arriba.")
    return results

if __name__ == '__main__':
    main()