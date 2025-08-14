#!/usr/bin/env python3
"""
Creación de Índices de Rendimiento
Genera y aplica índices optimizados para mejorar el rendimiento de consultas.
"""

import sys
from pathlib import Path
from typing import List, Dict, Any

# Agregar el directorio raíz al path
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from rexus.core.database import get_inventario_connection


class PerformanceIndexManager:
    """Gestiona la creación de índices de rendimiento."""

    def __init__(self):
        self.indexes = {
            # Índices para tabla obras
            'obras': [
                {
                    'name': 'idx_obras_activo_fecha',
                    'sql': 'CREATE INDEX IF NOT EXISTS idx_obras_activo_fecha ON obras (activo, fecha_creacion DESC)',
                    'description': 'Optimiza obtener_todas_obras y filtros por fecha'
                },
                {
                    'name': 'idx_obras_estado',
                    'sql': 'CREATE INDEX IF NOT EXISTS idx_obras_estado ON obras (estado) WHERE activo = 1',
                    'description': 'Optimiza estadísticas por estado'
                },
                {
                    'name': 'idx_obras_codigo_activo',
                    'sql': 'CREATE INDEX IF NOT EXISTS idx_obras_codigo_activo ON obras (codigo_obra, activo)',
                    'description': 'Optimiza búsqueda por código'
                }
            ],

            # Índices para tabla inventario_perfiles
            'inventario_perfiles': [
                {
                    'name': 'idx_inventario_tipo',
                    'sql': 'CREATE INDEX IF NOT EXISTS idx_inventario_tipo ON inventario_perfiles (tipo) WHERE tipo IS NOT NULL',
                    'description': 'Optimiza obtener_categorias'
                },
                {
                    'name': 'idx_inventario_stock',
                    'sql': 'CREATE INDEX IF NOT EXISTS idx_inventario_stock ON inventario_perfiles (stock_actual, stock_minimo)',
                    'description': 'Optimiza consultas de stock bajo'
                },
                {
                    'name': 'idx_inventario_activo_fecha',
                    'sql': 'CREATE INDEX IF NOT EXISTS idx_inventario_activo_fecha ON inventario_perfiles (activo, fecha_actualizacion DESC)',
                    'description': 'Optimiza listados paginados de productos'
                }
            ],

            # Índices para tabla compras
            'compras': [
                {
                    'name': 'idx_compras_estado_fecha',
                    'sql': 'CREATE INDEX IF NOT EXISTS idx_compras_estado_fecha ON compras (estado, fecha_pedido DESC)',
                    'description': 'Optimiza filtros por estado y fecha'
                },
                {
                    'name': 'idx_compras_proveedor',
                    'sql': 'CREATE INDEX IF NOT EXISTS idx_compras_proveedor ON compras (proveedor_id)',
                    'description': 'Optimiza consultas por proveedor'
                }
            ],

            # Índices para tabla usuarios
            'usuarios': [
                {
                    'name': 'idx_usuarios_activo_rol',
                    'sql': 'CREATE INDEX IF NOT EXISTS idx_usuarios_activo_rol ON usuarios (activo, rol)',
                    'description': 'Optimiza consultas de usuarios por rol'
                },
                {
                    'name': 'idx_usuarios_ultimo_acceso',
                    'sql': 'CREATE INDEX IF NOT EXISTS idx_usuarios_ultimo_acceso ON usuarios (ultimo_acceso DESC)',
                    'description': 'Optimiza estadísticas de actividad'
                }
            ],

            # Índices para tabla auditoria
            'auditoria': [
                {
                    'name': 'idx_auditoria_fecha_accion',
                    'sql': 'CREATE INDEX IF NOT EXISTS idx_auditoria_fecha_accion ON auditoria (fecha DESC, accion)',
                    'description': 'Optimiza consultas de auditoría por fecha'
                },
                {
                    'name': 'idx_auditoria_usuario',
                    'sql': 'CREATE INDEX IF NOT EXISTS idx_auditoria_usuario ON auditoria (usuario_id)',
                    'description': 'Optimiza consultas de auditoría por usuario'
                }
            ]
        }

    def create_all_indexes(self) -> Dict[str, Any]:
        """Crea todos los índices de rendimiento."""
        print("="*60)
        print("[PERFORMANCE] CREACIÓN DE ÍNDICES DE RENDIMIENTO")
        print("="*60)

        results = {
            'indexes_created': 0,
            'indexes_failed': 0,
            'details': []
        }

        # Obtener conexión a la base de datos
        try:
            connection = get_inventario_connection()
            cursor = connection.cursor()

            for table, indexes in self.indexes.items():
                print(f"\n[TABLA] Procesando {table}:")

                for index_info in indexes:
                    try:
                        # Ejecutar creación del índice
                        cursor.execute(index_info['sql'])
                        connection.commit()

                        print(f"  [OK] {index_info['name']} - {index_info['description']}")
                        results['indexes_created'] += 1
                        results['details'].append({
                            'table': table,
                            'name': index_info['name'],
                            'status': 'created',
                            'description': index_info['description']
                        })

                    except Exception as e:
                        print(f"  [ERROR] {index_info['name']} - {e}")
                        results['indexes_failed'] += 1
                        results['details'].append({
                            'table': table,
                            'name': index_info['name'],
                            'status': 'failed',
                            'error': str(e)
                        })

            cursor.close()
            connection.close()

        except Exception as e:
            print(f"[ERROR] Error conectando a base de datos: {e}")
            return results

        # Mostrar resumen
        print(f"\n[RESUMEN] Índices de Rendimiento:")
        print(f"  - Creados exitosamente: {results['indexes_created']}")
        print(f"  - Fallaron: {results['indexes_failed']}")
        print(f"  - Total procesados: {len(results['details'])}")

        if results['indexes_created'] > 0:
            print(f"\n[ÉXITO] Se crearon {results['indexes_created']} índices.")
            print("Las consultas optimizadas deberían mostrar mejoras de rendimiento.")

        return results

    def analyze_query_performance(self) -> Dict[str, Any]:
        """Analiza el rendimiento de consultas después de crear índices."""
        print("\n" + "="*60)
        print("[PERFORMANCE] ANÁLISIS POST-ÍNDICES")
        print("="*60)

        analysis = {
            'queries_tested': 0,
            'performance_improvements': [],
            'recommendations': []
        }

        try:
            connection = get_inventario_connection()
            cursor = connection.cursor()

            # Test queries representativas
            test_queries = [
                {
                    'name': 'Obtener obras activas',
                    'sql': 'SELECT COUNT(*) FROM obras WHERE activo = 1',
                    'expected_improvement': 'Debe usar idx_obras_activo_fecha'
                },
                {
                    'name': 'Estadísticas por estado',
                    'sql': 'SELECT estado, COUNT(*) FROM obras WHERE activo = 1 GROUP BY estado',
                    'expected_improvement': 'Debe usar idx_obras_estado'
                },
                {
                    'name': 'Categorías de productos',
                    'sql': 'SELECT DISTINCT tipo FROM inventario_perfiles WHERE tipo IS NOT NULL',
                    'expected_improvement': 'Debe usar idx_inventario_tipo'
                },
                {
                    'name': 'Productos con stock bajo',
                    'sql': 'SELECT COUNT(*) FROM inventario_perfiles WHERE stock_actual <= stock_minimo',
                    'expected_improvement': 'Debe usar idx_inventario_stock'
                }
            ]

            for query_info in test_queries:
                try:
                    import time

                    # Medir tiempo de ejecución
                    start_time = time.time()
                    cursor.execute(query_info['sql'])
                    cursor.fetchall()
                    execution_time = time.time() - start_time

                    analysis['queries_tested'] += 1
                    analysis['performance_improvements'].append({
                        'query': query_info['name'],
                        'execution_time_ms': round(execution_time * 1000, 2),
                        'expected_improvement': query_info['expected_improvement']
                    })

                    print(f"  [QUERY] {query_info['name']}: {execution_time*1000:.2f}ms")

                except Exception as e:
                    print(f"  [ERROR] {query_info['name']}: {e}")

            cursor.close()
            connection.close()

        except Exception as e:
            print(f"[ERROR] Error analizando rendimiento: {e}")

        # Generar recomendaciones
        if analysis['queries_tested'] > 0:
            avg_time = sum(q['execution_time_ms'] for q in analysis['performance_improvements']) / len(analysis['performance_improvements'])

            if avg_time < 10:
                analysis['recommendations'].append("Excelente: Consultas promedio bajo 10ms")
            elif avg_time < 50:
                analysis['recommendations'].append("Bueno: Consultas promedio bajo 50ms")
            else:
                analysis['recommendations'].append("Revisar: Consultas promedio sobre 50ms")

        analysis['recommendations'].extend([
            "Monitorear rendimiento con query_optimizer",
            "Aplicar cache a consultas más frecuentes",
            "Revisar queries que no usan los nuevos índices"
        ])

        print(f"\n[ANÁLISIS] Consultas probadas: {analysis['queries_tested']}")
        print("[RECOMENDACIONES]")
        for i, rec in enumerate(analysis['recommendations'], 1):
            print(f"  {i}. {rec}")

        return analysis


def main():
    """Función principal."""
    try:
        manager = PerformanceIndexManager()

        # Crear índices
        index_results = manager.create_all_indexes()

        # Analizar rendimiento
        analysis_results = manager.analyze_query_performance()

        # Determinar éxito general
        success = (
            index_results['indexes_created'] > 0 and
            index_results['indexes_failed'] == 0 and
            analysis_results['queries_tested'] > 0
        )

        if success:
            print(f"\n[ÉXITO] Optimizaciones de rendimiento aplicadas correctamente")
            print("El sistema debería mostrar mejoras en el rendimiento de consultas.")
        else:
            print(f"\n[ADVERTENCIA] Algunas optimizaciones fallaron")
            print("Revisar errores y aplicar manualmente si es necesario.")

        return success

    except Exception as e:
        print(f"\n[ERROR] Error durante la optimización: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
