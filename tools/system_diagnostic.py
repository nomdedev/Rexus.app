#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Diagnostico Completo - Rexus.app
Identifica y corrige problemas del sistema en tiempo real
"""

import os
import sys
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Any
import importlib

# Configurar encoding UTF-8
os.environ['PYTHONIOENCODING'] = 'utf-8'

class SystemDiagnostic:
    """Diagnostico completo del sistema Rexus.app."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.issues_found = []
        self.fixes_applied = []
        
        # Configurar logging sin Unicode para evitar errores
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.project_root / 'logs' / 'diagnostic.log', encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def run_full_diagnostic(self) -> Dict[str, Any]:
        """Ejecuta diagnostico completo del sistema."""
        print("SISTEMA DE DIAGNOSTICO COMPLETO - REXUS.APP")
        print("=" * 60)
        
        diagnostics = [
            ("Encoding y Unicode", self.diagnose_encoding_issues),
            ("Imports de modulos", self.diagnose_import_issues),
            ("Base de datos", self.diagnose_database_issues),
            ("Sistema de archivos", self.diagnose_file_system),
            ("Dependencias Python", self.diagnose_dependencies),
            ("Configuracion del entorno", self.diagnose_environment),
            ("Tests y validaciones", self.diagnose_test_system),
            ("Logs y errores", self.diagnose_error_logs)
        ]
        
        results = {}
        for name, diagnostic_func in diagnostics:
            print(f"\\nDiagnosticando: {name}")
            print("-" * 40)
            try:
                result = diagnostic_func()
                results[name] = result
                self.print_diagnostic_result(name, result)
            except Exception as e:
                error_result = {
                    'status': 'ERROR',
                    'message': f'Error durante diagnostico: {str(e)}'
                }
                results[name] = error_result
                print(f"ERROR: {str(e)}")
                self.issues_found.append(f"{name}: {str(e)}")
        
        self.generate_diagnostic_report(results)
        return results
    
    def diagnose_encoding_issues(self) -> Dict[str, Any]:
        """Diagnostica problemas de encoding Unicode."""
        issues = []
        fixes = []
        
        # Verificar encoding del sistema
        try:
            test_unicode = "✅ ❌ 🎯 🚀"
            print(test_unicode)
            encoding_ok = True
        except UnicodeEncodeError:
            issues.append("Sistema no soporta Unicode en consola")
            encoding_ok = False
        
        # Verificar PYTHONIOENCODING
        if os.environ.get('PYTHONIOENCODING') != 'utf-8':
            issues.append("PYTHONIOENCODING no configurado como utf-8")
            os.environ['PYTHONIOENCODING'] = 'utf-8'
            fixes.append("Configurado PYTHONIOENCODING=utf-8")
        
        # Verificar archivos con problemas de encoding
        problematic_files = []
        for file_path in self.project_root.rglob("*.py"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Buscar caracteres problemáticos en prints o strings
                    if '✅' in content or '❌' in content or '🎯' in content:
                        if 'print(' in content:
                            problematic_files.append(str(file_path.relative_to(self.project_root)))
            except Exception:
                pass
        
        return {
            'status': 'WARNING' if issues else 'PASSED',
            'encoding_support': encoding_ok,
            'issues_found': len(issues),
            'issues': issues,
            'fixes_applied': fixes,
            'problematic_files': problematic_files
        }
    
    def diagnose_import_issues(self) -> Dict[str, Any]:
        """Diagnostica problemas de imports."""
        critical_modules = [
            'rexus.main.app',
            'rexus.core.database',
            'rexus.modules.usuarios',
            'rexus.modules.inventario',
            'rexus.modules.compras',
            'rexus.modules.obras',
            'rexus.modules.configuracion',
            'rexus.modules.administracion',
            'rexus.modules.auditoria'
        ]
        
        import_results = {}
        failed_imports = []
        
        # Agregar path del proyecto
        sys.path.insert(0, str(self.project_root))
        
        for module_name in critical_modules:
            try:
                module = importlib.import_module(module_name)
                import_results[module_name] = 'SUCCESS'
            except Exception as e:
                import_results[module_name] = f'FAILED: {str(e)}'
                failed_imports.append(module_name)
        
        success_rate = ((len(critical_modules) - len(failed_imports)) / len(critical_modules)) * 100
        
        return {
            'status': 'PASSED' if success_rate >= 90 else 'WARNING' if success_rate >= 70 else 'FAILED',
            'success_rate': success_rate,
            'total_modules': len(critical_modules),
            'failed_modules': len(failed_imports),
            'import_results': import_results,
            'failed_imports': failed_imports
        }
    
    def diagnose_database_issues(self) -> Dict[str, Any]:
        """Diagnostica problemas de base de datos."""
        issues = []
        
        # Verificar archivos de base de datos
        db_files = [
            'data/usuarios.db',
            'data/inventario.db', 
            'data/auditoria.db'
        ]
        
        missing_dbs = []
        existing_dbs = []
        
        for db_file in db_files:
            db_path = self.project_root / db_file
            if db_path.exists():
                existing_dbs.append(db_file)
            else:
                missing_dbs.append(db_file)
        
        # Verificar conexiones
        connection_test = None
        try:
            sys.path.insert(0, str(self.project_root))
            from rexus.core.database import DatabaseConnection
            db = DatabaseConnection()
            connection_test = "SUCCESS"
        except Exception as e:
            connection_test = f"FAILED: {str(e)}"
            issues.append(f"Error de conexion: {str(e)}")
        
        return {
            'status': 'WARNING' if issues or missing_dbs else 'PASSED',
            'existing_databases': len(existing_dbs),
            'missing_databases': len(missing_dbs),
            'missing_dbs': missing_dbs,
            'connection_test': connection_test,
            'issues': issues
        }
    
    def diagnose_file_system(self) -> Dict[str, Any]:
        """Diagnostica estructura del sistema de archivos."""
        required_dirs = [
            'rexus/main',
            'rexus/core', 
            'rexus/modules',
            'rexus/utils',
            'tests',
            'logs',
            'data'
        ]
        
        missing_dirs = []
        existing_dirs = []
        
        for directory in required_dirs:
            dir_path = self.project_root / directory
            if dir_path.exists():
                existing_dirs.append(directory)
            else:
                missing_dirs.append(directory)
        
        # Verificar permisos de escritura
        write_test = None
        try:
            test_file = self.project_root / 'temp_write_test.txt'
            with open(test_file, 'w') as f:
                f.write('test')
            test_file.unlink()
            write_test = "SUCCESS"
        except Exception as e:
            write_test = f"FAILED: {str(e)}"
        
        return {
            'status': 'WARNING' if missing_dirs else 'PASSED',
            'existing_directories': len(existing_dirs),
            'missing_directories': len(missing_dirs),
            'missing_dirs': missing_dirs,
            'write_permissions': write_test
        }
    
    def diagnose_dependencies(self) -> Dict[str, Any]:
        """Diagnostica dependencias de Python."""
        required_packages = [
            'PyQt6',
            'pytest',
            'requests',
            'sqlalchemy',
            'pandas'
        ]
        
        installed_packages = {}
        missing_packages = []
        
        for package in required_packages:
            try:
                module = importlib.import_module(package.lower().replace('-', '_'))
                version = getattr(module, '__version__', 'unknown')
                installed_packages[package] = version
            except ImportError:
                missing_packages.append(package)
        
        return {
            'status': 'WARNING' if missing_packages else 'PASSED',
            'installed_packages': installed_packages,
            'missing_packages': missing_packages,
            'total_required': len(required_packages),
            'installed_count': len(installed_packages)
        }
    
    def diagnose_environment(self) -> Dict[str, Any]:
        """Diagnostica configuracion del entorno."""
        env_issues = []
        
        # Verificar variables de entorno criticas
        critical_env_vars = ['PYTHONIOENCODING']
        optional_env_vars = ['REXUS_ENV', 'REXUS_DEV_MODE']
        
        env_status = {}
        for var in critical_env_vars + optional_env_vars:
            value = os.environ.get(var)
            env_status[var] = value if value else 'NOT_SET'
            
            if var in critical_env_vars and not value:
                env_issues.append(f"Variable critica {var} no configurada")
        
        # Verificar archivos de configuracion
        config_files = ['.env', 'requirements.txt', 'CLAUDE.md']
        missing_configs = []
        
        for config_file in config_files:
            if not (self.project_root / config_file).exists():
                missing_configs.append(config_file)
        
        return {
            'status': 'WARNING' if env_issues or missing_configs else 'PASSED',
            'environment_variables': env_status,
            'issues': env_issues,
            'missing_configs': missing_configs
        }
    
    def diagnose_test_system(self) -> Dict[str, Any]:
        """Diagnostica sistema de tests."""
        test_result = None
        test_count = 0
        
        try:
            # Contar archivos de test
            test_files = list((self.project_root / 'tests').rglob('test_*.py'))
            test_count = len(test_files)
            
            # Ejecutar tests rapidos
            cmd = ['python', '-m', 'pytest', 'tests/', '--collect-only', '-q']
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                test_result = "COLLECTION_SUCCESS"
            else:
                test_result = f"COLLECTION_FAILED: {result.stderr[:100]}"
                
        except Exception as e:
            test_result = f"ERROR: {str(e)}"
        
        return {
            'status': 'PASSED' if test_result == "COLLECTION_SUCCESS" else 'WARNING',
            'test_files_count': test_count,
            'collection_result': test_result
        }
    
    def diagnose_error_logs(self) -> Dict[str, Any]:
        """Diagnostica logs de errores."""
        log_files = ['errors.log', 'database.log', 'modules.log']
        log_analysis = {}
        
        total_errors = 0
        recent_errors = 0
        
        for log_file in log_files:
            log_path = self.project_root / 'logs' / log_file
            if log_path.exists():
                try:
                    with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        error_count = content.count('ERROR')
                        total_errors += error_count
                        
                        # Contar errores recientes (ultimas 100 lineas)
                        lines = content.split('\\n')
                        recent_lines = lines[-100:] if len(lines) > 100 else lines
                        recent_error_count = sum(1 for line in recent_lines if 'ERROR' in line)
                        recent_errors += recent_error_count
                        
                        log_analysis[log_file] = {
                            'total_errors': error_count,
                            'recent_errors': recent_error_count,
                            'file_size': log_path.stat().st_size
                        }
                except Exception as e:
                    log_analysis[log_file] = {'error': str(e)}
            else:
                log_analysis[log_file] = {'status': 'missing'}
        
        return {
            'status': 'WARNING' if recent_errors > 10 else 'PASSED',
            'total_errors': total_errors,
            'recent_errors': recent_errors,
            'log_analysis': log_analysis
        }
    
    def print_diagnostic_result(self, name: str, result: Dict[str, Any]):
        """Imprime resultado de diagnostico."""
        status = result.get('status', 'UNKNOWN')
        status_symbol = {
            'PASSED': '[PASS]',
            'WARNING': '[WARN]',
            'FAILED': '[FAIL]',
            'ERROR': '[ERR]'
        }.get(status, '[???]')
        
        print(f"{status_symbol} {name}")
        
        # Imprimir detalles relevantes
        if 'success_rate' in result:
            print(f"    Tasa de exito: {result['success_rate']:.1f}%")
        
        if 'issues_found' in result and result['issues_found'] > 0:
            print(f"    Problemas encontrados: {result['issues_found']}")
        
        if 'missing_dbs' in result and result['missing_dbs']:
            print(f"    BD faltantes: {len(result['missing_dbs'])}")
        
        if 'recent_errors' in result and result['recent_errors'] > 0:
            print(f"    Errores recientes: {result['recent_errors']}")
    
    def generate_diagnostic_report(self, results: Dict[str, Any]):
        """Genera reporte final de diagnostico."""
        print("\\n" + "=" * 60)
        print("REPORTE FINAL DE DIAGNOSTICO")
        print("=" * 60)
        
        total_diagnostics = len(results)
        passed = sum(1 for r in results.values() if r.get('status') == 'PASSED')
        warnings = sum(1 for r in results.values() if r.get('status') == 'WARNING')
        failed = sum(1 for r in results.values() if r.get('status') == 'FAILED')
        errors = sum(1 for r in results.values() if r.get('status') == 'ERROR')
        
        print(f"\\nRESUMEN:")
        print(f"  Total diagnosticos: {total_diagnostics}")
        print(f"  Pasados: {passed}")
        print(f"  Advertencias: {warnings}")
        print(f"  Fallidos: {failed}")
        print(f"  Errores: {errors}")
        
        overall_score = ((passed * 100) + (warnings * 75) + (failed * 25) + (errors * 0)) / total_diagnostics
        print(f"\\nPUNTUACION GENERAL: {overall_score:.1f}/100")
        
        if overall_score >= 90:
            print("ESTADO: EXCELENTE - Sistema funcionando correctamente")
        elif overall_score >= 80:
            print("ESTADO: BUENO - Requiere ajustes menores")
        elif overall_score >= 70:
            print("ESTADO: ACEPTABLE - Requiere atencion")
        else:
            print("ESTADO: CRITICO - Requiere intervencion inmediata")
        
        # Recomendaciones
        print(f"\\nRECOMENDACIONES:")
        if failed > 0 or errors > 0:
            print("  - Corregir diagnosticos fallidos inmediatamente")
        if warnings > 0:
            print("  - Revisar y resolver advertencias")
        if overall_score < 90:
            print("  - Ejecutar herramientas de reparacion automatica")
        if overall_score >= 90:
            print("  - Mantener monitoreo regular del sistema")

def main():
    """Ejecutar diagnostico completo del sistema."""
    print("Iniciando diagnostico completo del sistema Rexus.app...")
    
    diagnostic = SystemDiagnostic()
    results = diagnostic.run_full_diagnostic()
    
    print(f"\\nDiagnostico completado. Revisa el reporte arriba.")
    
    # Guardar resultados
    import json
    report_path = diagnostic.project_root / 'reports' / 'system_diagnostic.json'
    report_path.parent.mkdir(exist_ok=True)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"Reporte guardado en: {report_path}")
    return results

if __name__ == '__main__':
    main()