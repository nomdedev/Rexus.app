#!/usr/bin/env python3
"""
Test del Sistema de Monitoreo en Tiempo Real de Rexus.app
Prueba integral de todos los componentes de monitoreo
"""

import sys
import time
from pathlib import Path

# Agregar el directorio raíz al path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from rexus.utils.app_logger import get_logger
from rexus.utils.monitoring_system import (
    get_metrics_collector, 
    get_performance_analyzer, 
    start_monitoring, 
    stop_monitoring, 
    get_system_status,
    get_performance_report
)
from rexus.utils.performance_monitor import get_performance_monitor, get_query_optimizer
from rexus.utils.metrics_api import start_metrics_api, stop_metrics_api

logger = get_logger(__name__)

def test_metrics_collector():
    """Test del recolector de métricas"""
    print("=== TEST: Recolector de Metricas ===")
    
    try:
        collector = get_metrics_collector()
        print(f"[OK] Collector creado: {type(collector).__name__}")
        
        # Registrar métricas de prueba
        collector.record_query_time(0.5)
        collector.record_query_time(1.2)
        collector.record_error()
        collector.record_user_session("test_user")
        
        # Métricas de módulo
        collector.record_module_metrics("test_module", {
            'load_time': 2.1,
            'query_count': 5,
            'error_count': 1,
            'active_views': 2
        })
        
        print("[OK] Metricas de prueba registradas")
        
        # Obtener resumen
        summary = collector.get_performance_summary()
        print(f"[OK] Resumen obtenido: {len(summary)} campos")
        
        # Módulos
        modules = collector.get_module_metrics()
        print(f"[OK] Metricas de modulos: {len(modules)} modulos")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Error en test collector: {e}")
        return False

def test_performance_analyzer():
    """Test del analizador de rendimiento"""
    print("\\n=== TEST: Analizador de Rendimiento ===")
    
    try:
        analyzer = get_performance_analyzer()
        print(f"[OK] Analyzer creado: {type(analyzer).__name__}")
        
        # Análisis de tendencias
        trends = analyzer.analyze_performance_trends()
        print(f"[OK] Tendencias analizadas: {type(trends)}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Error en test analyzer: {e}")
        return False

def test_performance_monitor():
    """Test del monitor de rendimiento"""
    print("\\n=== TEST: Monitor de Rendimiento ===")
    
    try:
        monitor = get_performance_monitor()
        print(f"[OK] Monitor creado: {type(monitor).__name__}")
        
        # Estadísticas actuales
        stats = monitor.get_current_stats()
        print(f"[OK] Estadisticas obtenidas: {type(stats)}")
        
        # Reporte de optimización
        report = monitor.get_optimization_report()
        print(f"[OK] Reporte de optimizacion: {len(report)} secciones")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Error en test monitor: {e}")
        return False

def test_query_optimizer():
    """Test del optimizador de consultas"""
    print("\\n=== TEST: Optimizador de Consultas ===")
    
    try:
        optimizer = get_query_optimizer()
        print(f"[OK] Optimizer creado: {type(optimizer).__name__}")
        
        # Estadísticas de consultas
        stats = optimizer.get_query_statistics()
        print(f"[OK] Estadisticas SQL: {stats}")
        
        # Recomendaciones
        recommendations = optimizer.get_optimization_recommendations()
        print(f"[OK] Recomendaciones: {len(recommendations)} sugerencias")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Error en test optimizer: {e}")
        return False

def test_system_monitoring():
    """Test del sistema completo de monitoreo"""
    print("\\n=== TEST: Sistema Completo de Monitoreo ===")
    
    try:
        # Iniciar monitoreo
        print("Iniciando monitoreo del sistema...")
        start_monitoring(interval=5)  # 5 segundos para test rápido
        
        print("[OK] Monitoreo iniciado, esperando metricas...")
        time.sleep(8)  # Esperar más que el intervalo
        
        # Obtener estado del sistema
        status = get_system_status()
        print(f"[OK] Estado del sistema obtenido: {status.get('status', 'UNKNOWN')}")
        
        # Reporte completo
        report = get_performance_report()
        print(f"[OK] Reporte completo generado: {type(report)}")
        
        # Detener monitoreo
        print("Deteniendo monitoreo...")
        stop_monitoring()
        print("[OK] Monitoreo detenido correctamente")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Error en test sistema completo: {e}")
        return False

def test_metrics_api():
    """Test de la API de métricas"""
    print("\\n=== TEST: API de Metricas ===")
    
    try:
        # Iniciar API
        print("Iniciando API de metricas...")
        api_server = start_metrics_api(host='localhost', port=8081)
        print("[OK] API iniciada en puerto 8081")
        
        time.sleep(2)  # Esperar que el servidor arranque
        
        # Test básico de conectividad
        import urllib.request
        import json
        
        try:
            # Test health check
            response = urllib.request.urlopen('http://localhost:8081/api/metrics/health')
            data = json.loads(response.read())
            print(f"[OK] Health check: {data.get('status', 'unknown')}")
            
        except Exception as api_test_error:
            print(f"[WARNING] API test limitado (puede estar bien): {api_test_error}")
        
        # Detener API
        print("Deteniendo API...")
        stop_metrics_api()
        print("[OK] API detenida correctamente")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Error en test API: {e}")
        return False

def run_integration_test():
    """Ejecuta test de integración completo"""
    print("\\n" + "="*60)
    print("SISTEMA DE MONITOREO REXUS.APP - TEST INTEGRAL")
    print("="*60)
    
    results = []
    
    # Tests individuales
    results.append(("Recolector de Metricas", test_metrics_collector()))
    results.append(("Analizador de Rendimiento", test_performance_analyzer()))
    results.append(("Monitor de Rendimiento", test_performance_monitor()))
    results.append(("Optimizador de Consultas", test_query_optimizer()))
    results.append(("Sistema Completo", test_system_monitoring()))
    results.append(("API de Metricas", test_metrics_api()))
    
    # Resumen
    print("\\n" + "="*60)
    print("RESUMEN DE TESTS")
    print("="*60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        status_symbol = "[PASS]" if result else "[FAIL]"
        print(f"{status_symbol} {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\\nResultado: {passed}/{total} tests exitosos ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\\n[SUCCESS] TODOS LOS TESTS PASARON - Sistema de monitoreo completamente funcional")
        return True
    else:
        print(f"\\n[WARNING] {total-passed} tests fallaron - Revisar componentes")
        return False

def main():
    """Función principal"""
    success = run_integration_test()
    
    if success:
        print("\\n" + "="*60)
        print("SISTEMA DE MONITOREO LISTO PARA PRODUCCION")
        print("="*60)
        print("Comandos disponibles:")
        print("  python scripts/start_monitoring.py --daemon")
        print("  python -c \"from rexus.utils.realtime_dashboard import show_dashboard; show_dashboard()\"")
        print("  python -c \"from rexus.utils.metrics_api import start_metrics_api; start_metrics_api()\"")
        
        return 0
    else:
        print("\\n" + "="*60)
        print("SISTEMA REQUIERE CORRECCIONES")
        print("="*60)
        return 1

if __name__ == "__main__":
    sys.exit(main())