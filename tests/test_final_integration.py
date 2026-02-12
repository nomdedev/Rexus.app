#!/usr/bin/env python3
"""
Pruebas finales de integración para el sistema Rexus.app
FASE 1: Verificación de importación de módulos principales
"""

import sys
import traceback
import importlib
from pathlib import Path

# Agregar el directorio raíz al path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class IntegrationTester:
    def __init__(self):
        self.results = {
            'modules_imported': [],
            'modules_failed': [],
            'syntax_errors': [],
            'import_errors': []
        }
    
    def test_module_import(self, module_name):
        """Intenta importar un módulo y registra el resultado"""
        try:
            module = importlib.import_module(module_name)
            self.results['modules_imported'].append(module_name)
            print(f"OK {module_name} - Importado exitosamente")
            return True
        except SyntaxError as e:
            error_msg = f"Error de sintaxis en {module_name}: {str(e)}"
            self.results['syntax_errors'].append(error_msg)
            self.results['modules_failed'].append(module_name)
            print(f"ERROR {module_name} - ERROR DE SINTAXIS: {str(e)}")
            return False
        except ImportError as e:
            error_msg = f"Error de importación en {module_name}: {str(e)}"
            self.results['import_errors'].append(error_msg)
            self.results['modules_failed'].append(module_name)
            print(f"ERROR {module_name} - ERROR DE IMPORTACIÓN: {str(e)}")
            return False
        except Exception as e:
            error_msg = f"Error general en {module_name}: {str(e)}"
            self.results['modules_failed'].append(module_name)
            print(f"ERROR {module_name} - ERROR: {str(e)}")
            return False
    
    def test_core_modules(self):
        """Prueba los módulos core del sistema"""
        print("\n=== PRUEBA DE MÓDULOS CORE ===")
        
        core_modules = [
            'rexus.core.auth_decorators',
            'rexus.utils.unified_sanitizer',
            'rexus.utils.sql_script_loader',
            'rexus.utils.logging_config',
            'rexus.utils.two_factor_auth',
            'rexus.utils.dependency_validator',
            'rexus.utils.task_queue'
        ]
        
        for module in core_modules:
            self.test_module_import(module)
    
    def test_main_modules(self):
        """Prueba los módulos principales del sistema"""
        print("\n=== PRUEBA DE MÓDULOS PRINCIPALES ===")
        
        main_modules = [
            'rexus.modules.01_obra',
            'rexus.modules.02_inventario',
            'rexus.modules.03_herrajes',
            'rexus.modules.04_vidrios',
            'rexus.modules.05_logistica',
            'rexus.modules.06_pedidos',
            'rexus.modules.07_compras',
            'rexus.modules.08_administracion',
            'rexus.modules.09_mantenimiento',
            'rexus.modules.10_auditoria',
            'rexus.modules.11_usuarios'
        ]
        
        for module in main_modules:
            self.test_module_import(module)
    
    def test_models(self):
        """Prueba los modelos de datos"""
        print("\n=== PRUEBA DE MODELOS ===")
        
        model_modules = [
            'rexus.modules.01_obra.model',
            'rexus.modules.02_inventario.model',
            'rexus.modules.03_herrajes.model',
            'rexus.modules.04_vidrios.model',
            'rexus.modules.05_logistica.model',
            'rexus.modules.06_pedidos.model',
            'rexus.modules.07_compras.model',
            'rexus.modules.08_administracion.contabilidad.model',
            'rexus.modules.11_usuarios.model'
        ]
        
        for module in model_modules:
            self.test_module_import(module)
    
    def test_controllers(self):
        """Prueba los controladores"""
        print("\n=== PRUEBA DE CONTROLADORES ===")
        
        controller_modules = [
            'rexus.modules.01_obra.controller',
            'rexus.modules.02_inventario.controller',
            'rexus.modules.03_herrajes.controller',
            'rexus.modules.04_vidrios.controller',
            'rexus.modules.05_logistica.controller',
            'rexus.modules.06_pedidos.controller',
            'rexus.modules.07_compras.controller',
            'rexus.modules.08_administracion.contabilidad.controller',
            'rexus.modules.11_usuarios.controller'
        ]
        
        for module in controller_modules:
            self.test_module_import(module)
    
    def test_main_application(self):
        """Prueba la aplicación principal"""
        print("\n=== PRUEBA DE APLICACIÓN PRINCIPAL ===")
        self.test_module_import('rexus.main')
    
    def generate_report(self):
        """Genera un reporte de los resultados"""
        print("\n" + "="*60)
        print("REPORTE FINAL DE PRUEBAS DE INTEGRACIÓN")
        print("="*60)
        
        total_modules = len(self.results['modules_imported']) + len(self.results['modules_failed'])
        success_rate = (len(self.results['modules_imported']) / total_modules * 100) if total_modules > 0 else 0
        
        print(f"\nRESUMEN:")
        print(f"• Módulos importados exitosamente: {len(self.results['modules_imported'])}")
        print(f"• Módulos con errores: {len(self.results['modules_failed'])}")
        print(f"• Tasa de éxito: {success_rate:.1f}%")
        
        if self.results['syntax_errors']:
            print(f"\nERRORES DE SINTAXIS ({len(self.results['syntax_errors'])}):")
            for error in self.results['syntax_errors']:
                print(f"  • {error}")
        
        if self.results['import_errors']:
            print(f"\nERRORES DE IMPORTACIÓN ({len(self.results['import_errors'])}):")
            for error in self.results['import_errors']:
                print(f"  • {error}")
        
        if self.results['modules_failed']:
            print(f"\nMÓDULOS FALLIDOS:")
            for module in self.results['modules_failed']:
                print(f"  • {module}")
        
        print(f"\nMÓDULOS FUNCIONALES:")
        for module in self.results['modules_imported']:
            print(f"  • {module}")
        
        return {
            'total_modules': total_modules,
            'successful_imports': len(self.results['modules_imported']),
            'failed_imports': len(self.results['modules_failed']),
            'success_rate': success_rate,
            'syntax_errors': len(self.results['syntax_errors']),
            'import_errors': len(self.results['import_errors']),
            'details': self.results
        }
    
    def run_all_tests(self):
        """Ejecuta todas las pruebas"""
        print("INICIANDO PRUEBAS DE INTEGRACIÓN FINALES")
        print("FASE 1: Verificación de importación de módulos principales")
        
        self.test_core_modules()
        self.test_main_modules()
        self.test_models()
        self.test_controllers()
        self.test_main_application()
        
        return self.generate_report()

if __name__ == "__main__":
    tester = IntegrationTester()
    report = tester.run_all_tests()
    
    # Guardar reporte
    import json
    with open('tests/integration_phase1_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\nReporte guardado en: tests/integration_phase1_report.json")
    
    # Salir con código apropiado
    if report['syntax_errors'] > 0:
        print("\nFALLIDO PRUEBAS FALLIDAS: Se encontraron errores de sintaxis")
        sys.exit(1)
    elif report['success_rate'] < 80:
        print("\nADVERTENCIA PRUEBAS PARCIALES: Muchos módulos no pudieron importarse")
        sys.exit(2)
    else:
        print("\nEXITO PRUEBAS EXITOSAS: La mayoría de los módulos importan correctamente")
        sys.exit(0)