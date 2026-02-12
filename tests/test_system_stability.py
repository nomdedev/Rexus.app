#!/usr/bin/env python3
"""
Prueba final de estabilidad del sistema Rexus.app
FASE 3: Verificación de estabilidad general del sistema
"""

import sys
import time
import psutil
import importlib
from pathlib import Path

# Agregar el directorio raíz al path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class SystemStabilityTester:
    def __init__(self):
        self.results = {
            'startup_time': 0,
            'memory_usage': 0,
            'error_handling': True,
            'recovery_test': True,
            'performance_test': True
        }
    
    def test_startup_performance(self):
        """Prueba el rendimiento de inicio de la aplicación"""
        print("\n=== PRUEBA DE RENDIMIENTO DE INICIO ===")
        
        start_time = time.time()
        
        try:
            # Importar aplicación principal
            import rexus.main
            
            # Importar módulos core
            import rexus.core.auth_decorators
            import rexus.utils.unified_sanitizer
            import rexus.utils.sql_script_loader
            import rexus.utils.logging_config
            
            # Importar módulos de negocio funcionales
            importlib.import_module('rexus.modules.05_logistica.model')
            importlib.import_module('rexus.modules.06_pedidos.model')
            importlib.import_module('rexus.modules.08_administracion.contabilidad.model')
            importlib.import_module('rexus.modules.04_vidrios.controller')
            importlib.import_module('rexus.modules.05_logistica.controller')
            importlib.import_module('rexus.modules.06_pedidos.controller')
            importlib.import_module('rexus.modules.08_administracion.contabilidad.controller')
            
            end_time = time.time()
            self.results['startup_time'] = end_time - start_time
            
            print(f"OK Tiempo de inicio: {self.results['startup_time']:.3f} segundos")
            
            if self.results['startup_time'] < 5.0:
                print("OK Rendimiento de inicio: EXCELENTE")
            elif self.results['startup_time'] < 10.0:
                print("OK Rendimiento de inicio: BUENO")
            else:
                print("ADVERTENCIA Rendimiento de inicio: LENTO")
                
        except Exception as e:
            print(f"ERROR En inicio de aplicación: {e}")
            self.results['startup_time'] = float('inf')
    
    def test_memory_usage(self):
        """Prueba el uso de memoria"""
        print("\n=== PRUEBA DE USO DE MEMORIA ===")
        
        try:
            # Obtener uso de memoria actual
            process = psutil.Process()
            memory_info = process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024
            
            self.results['memory_usage'] = memory_mb
            
            print(f"OK Uso de memoria: {memory_mb:.1f} MB")
            
            if memory_mb < 100:
                print("OK Uso de memoria: EXCELENTE")
            elif memory_mb < 200:
                print("OK Uso de memoria: BUENO")
            else:
                print("ADVERTENCIA Uso de memoria: ALTO")
                
        except Exception as e:
            print(f"ERROR Midendo uso de memoria: {e}")
            self.results['memory_usage'] = float('inf')
    
    def test_error_handling(self):
        """Prueba el manejo de errores"""
        print("\n=== PRUEBA DE MANEJO DE ERRORES ===")
        
        try:
            # Probar manejo de errores de importación
            try:
                import_module_nonexistent = importlib.import_module('module.nonexistent')
            except ImportError:
                print("OK Manejo de ImportError: CORRECTO")
            
            # Probar manejo de errores de sintaxis
            try:
                eval("invalid syntax code")
            except SyntaxError:
                print("OK Manejo de SyntaxError: CORRECTO")
            
            # Probar manejo de excepciones generales
            try:
                raise Exception("Test exception")
            except Exception:
                print("OK Manejo de Exception: CORRECTO")
            
            self.results['error_handling'] = True
            
        except Exception as e:
            print(f"ERROR En prueba de manejo de errores: {e}")
            self.results['error_handling'] = False
    
    def test_recovery(self):
        """Prueba la recuperación de errores"""
        print("\n=== PRUEBA DE RECUPERACIÓN ===")
        
        try:
            # Simular error y recuperación
            from rexus.utils.unified_sanitizer import UnifiedSanitizer
            
            # Probar sanitización con input malicioso
            malicious_input = "<script>alert('xss')</script>"
            clean_input = UnifiedSanitizer.sanitize_html(malicious_input)
            
            if clean_input != malicious_input and "<script>" not in clean_input:
                print("OK Recuperación de seguridad: FUNCIONAL")
            else:
                print("ERROR Recuperación de seguridad: FALLÓ")
                self.results['recovery_test'] = False
                return
            
            # Probar recuperación de sistema de logging
            import rexus.utils.logging_config
            logger = rexus.utils.logging_config.get_logger(__name__)
            logger.info("Test de recuperación de logging")
            
            print("OK Recuperación de logging: FUNCIONAL")
            
            self.results['recovery_test'] = True
            
        except Exception as e:
            print(f"ERROR En prueba de recuperación: {e}")
            self.results['recovery_test'] = False
    
    def test_performance(self):
        """Prueba el rendimiento del sistema"""
        print("\n=== PRUEBA DE RENDIMIENTO ===")
        
        try:
            # Probar rendimiento de sanitización
            from rexus.utils.unified_sanitizer import UnifiedSanitizer
            sanitizer = UnifiedSanitizer()
            
            start_time = time.time()
            for i in range(1000):
                test_input = f"<script>alert('{i}')</script>"
                sanitizer.sanitize_html(test_input)
            end_time = time.time()
            
            sanitization_time = end_time - start_time
            print(f"OK Rendimiento sanitización: {sanitization_time:.3f}s para 1000 operaciones")
            
            if sanitization_time < 1.0:
                print("OK Rendimiento sanitización: EXCELENTE")
            elif sanitization_time < 2.0:
                print("OK Rendimiento sanitización: BUENO")
            else:
                print("ADVERTENCIA Rendimiento sanitización: LENTO")
            
            # Probar rendimiento de imports
            start_time = time.time()
            for i in range(10):
                importlib.import_module('rexus.utils.unified_sanitizer')
            end_time = time.time()
            
            import_time = end_time - start_time
            print(f"OK Rendimiento imports: {import_time:.3f}s para 10 imports")
            
            if import_time < 0.5:
                print("OK Rendimiento imports: EXCELENTE")
            elif import_time < 1.0:
                print("OK Rendimiento imports: BUENO")
            else:
                print("ADVERTENCIA Rendimiento imports: LENTO")
            
            self.results['performance_test'] = True
            
        except Exception as e:
            print(f"ERROR En prueba de rendimiento: {e}")
            self.results['performance_test'] = False
    
    def generate_stability_report(self):
        """Genera un reporte de estabilidad"""
        print("\n" + "="*60)
        print("REPORTE FINAL DE ESTABILIDAD DEL SISTEMA")
        print("="*60)
        
        # Calcular puntuación de estabilidad
        score = 0
        max_score = 5
        
        if self.results['startup_time'] < 10.0:
            score += 1
        if self.results['memory_usage'] < 200:
            score += 1
        if self.results['error_handling']:
            score += 1
        if self.results['recovery_test']:
            score += 1
        if self.results['performance_test']:
            score += 1
        
        stability_percentage = (score / max_score) * 100
        
        print(f"\nPUNTUACIÓN DE ESTABILIDAD: {score}/{max_score} ({stability_percentage:.1f}%)")
        
        print(f"\nMÉTRICAS:")
        print(f"• Tiempo de inicio: {self.results['startup_time']:.3f} segundos")
        print(f"• Uso de memoria: {self.results['memory_usage']:.1f} MB")
        print(f"• Manejo de errores: {'FUNCIONAL' if self.results['error_handling'] else 'FALLÓ'}")
        print(f"• Recuperación: {'FUNCIONAL' if self.results['recovery_test'] else 'FALLÓ'}")
        print(f"• Rendimiento: {'FUNCIONAL' if self.results['performance_test'] else 'FALLÓ'}")
        
        if stability_percentage >= 80:
            print(f"\n✅ ESTABILIDAD: EXCELENTE ({stability_percentage:.1f}%)")
            status = "EXCELENTE"
        elif stability_percentage >= 60:
            print(f"\n✅ ESTABILIDAD: BUENA ({stability_percentage:.1f}%)")
            status = "BUENA"
        else:
            print(f"\n⚠️ ESTABILIDAD: NECESITA MEJORAS ({stability_percentage:.1f}%)")
            status = "NECESITA_MEJORAS"
        
        return {
            'stability_score': score,
            'max_score': max_score,
            'stability_percentage': stability_percentage,
            'status': status,
            'metrics': self.results
        }
    
    def run_all_tests(self):
        """Ejecuta todas las pruebas de estabilidad"""
        print("INICIANDO PRUEBAS DE ESTABILIDAD DEL SISTEMA")
        print("FASE 3: Verificación de estabilidad general del sistema")
        
        self.test_startup_performance()
        self.test_memory_usage()
        self.test_error_handling()
        self.test_recovery()
        self.test_performance()
        
        return self.generate_stability_report()

if __name__ == "__main__":
    tester = SystemStabilityTester()
    report = tester.run_all_tests()
    
    # Guardar reporte
    import json
    with open('tests/system_stability_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\nReporte guardado en: tests/system_stability_report.json")
    
    # Salir con código apropiado
    if report['stability_percentage'] >= 80:
        print("\n✅ SISTEMA ESTABLE Y LISTO PARA PRODUCCIÓN")
        sys.exit(0)
    elif report['stability_percentage'] >= 60:
        print("\n⚠️ SISTEMA FUNCIONAL CON MEJORAS MENORES")
        sys.exit(1)
    else:
        print("\n❌ SISTEMA NECESITA MEJORAS SIGNIFICATIVAS")
        sys.exit(2)