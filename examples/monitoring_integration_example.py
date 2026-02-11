"""
Ejemplo de Integración de Monitoreo en Rexus.app

Este archivo muestra cómo integrar el sistema de monitoreo
en la aplicación Flask principal.
"""

from flask import Flask, jsonify, request
import time
import random

# Importar componentes de monitoreo
from rexus.monitoring.middleware import (
    MonitoringMiddleware,
    track_module,
    track_endpoint
)
from rexus.monitoring.metrics_manager import MetricsManager

# Crear app Flask
app = Flask(__name__)

# ==================== INICIALIZAR MONITOREO ====================
# El middleware trackea automáticamente todas las requests
monitoring = MonitoringMiddleware()
monitoring.init_app(app)

# ==================== MÉTRICAS PERSONALIZADAS ====================

@app.route('/health')
def health_check():
    """Health check básico."""
    return jsonify({'status': 'healthy', 'timestamp': time.time()})

@app.route('/api/productos', methods=['GET'])
@track_endpoint('productos_list')
def listar_productos():
    """
    Ejemplo de endpoint con monitoreo.

    El decorator @track_endpoint registra automáticamente:
    - productos_list_duration (histograma)
    - productos_list_total (contador)
    """
    # Simular delay de BD
    time.sleep(random.uniform(0.01, 0.1))

    # Simular datos
    productos = [
        {'id': 1, 'nombre': 'Producto 1', 'precio': 100},
        {'id': 2, 'nombre': 'Producto 2', 'precio': 200},
    ]

    # Métrica personalizada: número de productos
    MetricsManager.gauge('productos_total', len(productos))

    return jsonify(productos)


@app.route('/api/productos', methods=['POST'])
@track_endpoint('productos_create')
def crear_producto():
    """Crear un producto nuevo."""
    data = request.get_json()

    # Medir operación específica
    with MetricsManager.measure_operation('producto_creation'):
        # Simular validación
        time.sleep(0.01)

        # Simular inserción en BD
        time.sleep(random.uniform(0.05, 0.15))

        # Contador personalizado
        MetricsManager.counter('productos_creados', labels={
            'categoria': data.get('categoria', 'unknown')
        })

        # Registrar producto creado
        MetricsManager.gauge('productos_total', 123, {'categoria': 'Perfiles'})

    return jsonify({'id': random.randint(1, 1000), **data}), 201


@app.route('/api/estadisticas')
def get_estadisticas():
    """Obtener estadísticas (query compleja)."""
    # Trackear operación compleja
    with MetricsManager.measure_operation('estadisticas_calculation'):
        # Simular cálculo complejo
        time.sleep(random.uniform(0.1, 0.5))

        stats = {
            'total_productos': 1234,
            'valor_inventario': 150000.00,
            'productos_bajo_stock': 42
        }

    return jsonify(stats)


@app.route('/api/cache-test')
def cache_test():
    """Test de operaciones de caché."""
    key = request.args.get('key', 'test')

    # Usar context manager de caché
    with MetricsManager.track_cache_operation('get', 'redis') as (hit):
        # Simular lookup de caché
        time.sleep(0.001)

        # Simular cache hit o miss aleatorio
        hit = random.choice([True, False])

        if hit:
            MetricsManager.counter('cache_hits_total')
        else:
            MetricsManager.counter('cache_misses_total')

    return jsonify({'cached': hit})


@app.route('/api/simular-error')
def simular_error():
    """Endpoint para testear alertas de errores."""
    if random.random() < 0.3:  # 30% de error
        raise ValueError("Error simulado para testear monitoreo")

    return jsonify({'message': 'Ok'})


# ==================== MÓDULOS CON DECORATOR ====================

@track_module('inventario')
def procesar_inventario(producto_id):
    """
    Ejemplo de función de módulo con monitoreo.

    El decorator registra automáticamente:
    - module_calls_total{module="inventario", function="procesar_inventario"}
    - inventario_procesar_inventario_duration
    """
    time.sleep(random.uniform(0.05, 0.2))

    # Métrica de negocio
    MetricsManager.counter('inventario_procesado', labels={
        'producto_id': str(producto_id)
    })

    return {'procesado': True}


@app.route('/api/inventario/<int:producto_id>/procesar')
def api_procesar_inventario(producto_id):
    """API para procesar inventario."""
    resultado = procesar_inventario(producto_id)
    return jsonify(resultado)


# ==================== MÉTRICAS DE NEGOCIO ====================

@app.route('/api/ventas/registro', methods=['POST'])
def registrar_venta():
    """Registrar una venta (métricas de negocio)."""
    data = request.get_json()
    monto = data.get('monto', 0)

    # Métricas de negocio
    MetricsManager.counter('ventas_total', labels={
        'metodo_pago': data.get('metodo_pago', 'unknown')
    })

    MetricsManager.histogram('venta_monto', monto, {
        'moneda': 'ARS'
    })

    # Actualizar gauge de ventas del día
    MetricsManager.gauge('ventas_hoy_monto', monto)

    return jsonify({'venta_id': random.randint(1, 1000), 'monto': monto})


# ==================== ENDPOINT ADMIN ====================

@app.route('/admin/metrics')
def admin_metrics():
    """Endpoint admin para ver todas las métricas (debug)."""
    all_metrics = MetricsManager.get_all_metrics()
    return jsonify(all_metrics)


# ==================== MAIN ====================

if __name__ == '__main__':
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║           Rexus.app - Sistema de Monitoreo Activo            ║
    ╠════════════════════════════════════════════════════════════════╣
    ║  Endpoints disponibles:                                       ║
    ║  - GET  /health                Health check                   ║
    ║  - GET  /metrics               Métricas Prometheus           ║
    ║  - GET  /api/productos          Listar productos             ║
    ║  - POST /api/productos          Crear producto               ║
    ║  - GET  /api/estadisticas       Estadísticas complejas       ║
    ║  - GET  /api/cache-test         Test caché                   ║
    ║  - GET  /api/simular-error      Simular errores              ║
    ║  - GET  /admin/metrics          Ver todas las métricas       ║
    ╠════════════════════════════════════════════════════════════════╣
    ║  Monitoreo disponible en:                                   ║
    ║  - Prometheus: http://localhost:9090                        ║
    ║  - Grafana:    http://localhost:3000 (admin/admin123)       ║
    ╚════════════════════════════════════════════════════════════════╝
    """)

    # Levantar servidor de desarrollo
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
