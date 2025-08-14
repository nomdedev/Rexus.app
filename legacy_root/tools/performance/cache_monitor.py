#!/usr/bin/env python3
"""
Monitor de Cache y Rendimiento
Monitorea la efectividad del sistema de cache y las optimizaciones aplicadas.
"""

import sys
import time
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime, timedelta

# Agregar el directorio raíz al path
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))


class CacheMonitor:
    """Monitor del sistema de cache y rendimiento."""

    def __init__(self):
        self.start_time = datetime.now()

    def get_cache_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del sistema de cache."""
        try:
            from rexus.core.cache_manager import cache_manager
            return cache_manager.get_stats()
        except Exception as e:
            print(f"[WARNING] No se pudo obtener stats de cache: {e}")
            return {"error": str(e)}

    def get_query_optimizer_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del optimizador de consultas."""
        try:
            from rexus.core.query_optimizer import query_optimizer
            return query_optimizer.get_query_stats()
        except Exception as e:
            print(f"[WARNING] No se pudo obtener stats de query optimizer: {e}")
            return {"error": str(e)}

    def get_recommendations(self) -> List[str]:
        """Obtiene recomendaciones de optimización."""
        try:
            from rexus.core.query_optimizer import query_optimizer
            return query_optimizer.get_recommendations()
        except Exception as e:
            print(f"[WARNING] No se pudo obtener recomendaciones: {e}")
            return [f"Error obteniendo recomendaciones: {e}"]

    def generate_performance_report(self) -> Dict[str, Any]:
        """Genera un reporte completo de rendimiento."""
        print("="*60)
        print("[PERFORMANCE] REPORTE DE RENDIMIENTO DEL SISTEMA")
        print("="*60)
        print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Tiempo de monitoreo: {datetime.now() - self.start_time}")

        report = {
            'timestamp': datetime.now().isoformat(),
            'cache_stats': self.get_cache_stats(),
            'query_stats': self.get_query_optimizer_stats(),
            'recommendations': self.get_recommendations(),
            'performance_score': 0
        }

        # Mostrar estadísticas de cache
        print(f"\n[CACHE] Estadísticas del Sistema de Cache:")
        cache_stats = report['cache_stats']

        if 'error' not in cache_stats:
            print(f"  - Backend: {cache_stats.get('backend', 'desconocido')}")
            print(f"  - Hits: {cache_stats.get('hits', 0)}")
            print(f"  - Misses: {cache_stats.get('misses', 0)}")
            print(f"  - Sets: {cache_stats.get('sets', 0)}")
            print(f"  - Errores: {cache_stats.get('errors', 0)}")

            hit_rate = cache_stats.get('hit_rate', 0)
            print(f"  - Hit Rate: {hit_rate:.2f}%")

            # Evaluar cache performance
            if hit_rate >= 80:
                cache_score = 100
                print(f"  - Estado Cache: [EXCELENTE] Hit rate superior al 80%")
            elif hit_rate >= 60:
                cache_score = 80
                print(f"  - Estado Cache: [BUENO] Hit rate aceptable")
            elif hit_rate >= 40:
                cache_score = 60
                print(f"  - Estado Cache: [REGULAR] Hit rate bajo")
            else:
                cache_score = 40
                print(f"  - Estado Cache: [MALO] Hit rate muy bajo")
        else:
            cache_score = 0
            print(f"  - Error: {cache_stats['error']}")

        # Mostrar estadísticas de queries
        print(f"\n[QUERIES] Estadísticas del Optimizador:")
        query_stats = report['query_stats']

        if 'error' not in query_stats:
            print(f"  - Total consultas ejecutadas: {query_stats.get('total_queries_executed', 0)}")
            print(f"  - Tiempo total ejecución: {query_stats.get('total_execution_time', 0)}s")
            print(f"  - Tiempo promedio por query: {query_stats.get('average_query_time', 0)}s")
            print(f"  - Consultas lentas detectadas: {query_stats.get('slow_queries_count', 0)}")

            # Cache statistics del query optimizer
            cache_info = query_stats.get('cache_statistics', {})
            total_cache_hits = cache_info.get('total_cache_hits', 0)
            cache_hit_ratio = cache_info.get('cache_hit_ratio', 0)

            print(f"  - Cache hits en queries: {total_cache_hits}")
            print(f"  - Query cache hit ratio: {cache_hit_ratio}%")

            # Evaluar query performance
            avg_time = query_stats.get('average_query_time', 0)
            slow_count = query_stats.get('slow_queries_count', 0)

            if avg_time < 0.01 and slow_count == 0:
                query_score = 100
                print(f"  - Estado Queries: [EXCELENTE] Rendimiento óptimo")
            elif avg_time < 0.05 and slow_count <= 2:
                query_score = 80
                print(f"  - Estado Queries: [BUENO] Rendimiento aceptable")
            elif avg_time < 0.1 and slow_count <= 5:
                query_score = 60
                print(f"  - Estado Queries: [REGULAR] Algunas consultas lentas")
            else:
                query_score = 40
                print(f"  - Estado Queries: [MALO] Múltiples consultas lentas")

            # Mostrar consultas más lentas
            slowest_queries = query_stats.get('slowest_queries', [])
            if slowest_queries:
                print(f"\n  [TOP QUERIES LENTAS]:")
                for i, query in enumerate(slowest_queries[:3], 1):
                    print(f"    {i}. Hash: {query.get('hash', 'N/A')[:8]} - "
                          f"Tiempo: {query.get('avg_time', 0)}s - "
                          f"Ejecutada: {query.get('execution_count', 0)} veces")

            # Mostrar consultas más frecuentes
            frequent_queries = query_stats.get('most_frequent_queries', [])
            if frequent_queries:
                print(f"\n  [TOP QUERIES FRECUENTES]:")
                for i, query in enumerate(frequent_queries[:3], 1):
                    print(f"    {i}. Hash: {query.get('hash', 'N/A')[:8]} - "
                          f"Ejecutada: {query.get('execution_count', 0)} veces - "
                          f"Cache hits: {query.get('cache_hits', 0)}")
        else:
            query_score = 0
            print(f"  - Error: {query_stats['error']}")

        # Calcular puntuación general
        performance_score = (cache_score + query_score) / 2
        report['performance_score'] = performance_score

        # Mostrar recomendaciones
        print(f"\n[RECOMENDACIONES] Sugerencias de Optimización:")
        for i, rec in enumerate(report['recommendations'], 1):
            print(f"  {i}. {rec}")

        # Mostrar puntuación final
        print(f"\n[PUNTUACIÓN] Rendimiento General: {performance_score:.1f}/100")
        if performance_score >= 90:
            status = "[EXCELENTE]"
        elif performance_score >= 80:
            status = "[MUY BUENO]"
        elif performance_score >= 70:
            status = "[BUENO]"
        elif performance_score >= 60:
            status = "[REGULAR]"
        else:
            status = "[NECESITA MEJORAS]"

        print(f"Estado del Sistema: {status}")

        return report

    def simulate_cache_usage(self) -> Dict[str, Any]:
        """Simula uso del cache para testear funcionalidad."""
        print(f"\n[TEST] Simulando uso del sistema de cache...")

        test_results = {
            'cache_set_tests': 0,
            'cache_get_tests': 0,
            'cache_hit_tests': 0,
            'errors': []
        }

        try:
            from rexus.core.cache_manager import cache_manager

            # Test básico de set/get
            test_key = f"cache_test_{int(time.time())}"
            test_value = {"test": "data", "timestamp": datetime.now().isoformat()}

            # Test SET
            if cache_manager.set(test_key, test_value, 60):
                test_results['cache_set_tests'] += 1
                print(f"  [OK] Cache SET exitoso")
            else:
                test_results['errors'].append("Cache SET falló")
                print(f"  [ERROR] Cache SET falló")

            # Test GET
            retrieved_value = cache_manager.get(test_key)
            if retrieved_value is not None:
                test_results['cache_get_tests'] += 1
                test_results['cache_hit_tests'] += 1
                print(f"  [OK] Cache GET exitoso - Hit")
            else:
                test_results['errors'].append("Cache GET falló")
                print(f"  [ERROR] Cache GET falló")

            # Test de cache miss
            miss_value = cache_manager.get("clave_inexistente")
            if miss_value is None:
                print(f"  [OK] Cache MISS funcionando correctamente")
            else:
                test_results['errors'].append("Cache debería retornar None para clave inexistente")

            # Limpiar test
            cache_manager.delete(test_key)

        except Exception as e:
            test_results['errors'].append(f"Error en test de cache: {e}")
            print(f"  [ERROR] Error en test de cache: {e}")

        print(f"  - Tests SET: {test_results['cache_set_tests']}")
        print(f"  - Tests GET: {test_results['cache_get_tests']}")
        print(f"  - Tests HIT: {test_results['cache_hit_tests']}")
        print(f"  - Errores: {len(test_results['errors'])}")

        return test_results


def main():
    """Función principal."""
    try:
        monitor = CacheMonitor()

        # Generar reporte de rendimiento
        performance_report = monitor.generate_performance_report()

        # Simular uso de cache
        cache_test_results = monitor.simulate_cache_usage()

        # Determinar éxito general
        success = (
            performance_report['performance_score'] >= 60 and
            len(cache_test_results['errors']) == 0
        )

        print(f"\n" + "="*60)
        if success:
            print("[ÉXITO] Sistema de cache y optimizaciones funcionando correctamente")
        else:
            print("[ADVERTENCIA] Se detectaron problemas en el sistema de cache")
        print("="*60)

        return success

    except Exception as e:
        print(f"\n[ERROR] Error durante el monitoreo: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
