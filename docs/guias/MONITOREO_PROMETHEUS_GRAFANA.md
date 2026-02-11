# Monitoreo con Prometheus y Grafana

## 📊 Sistema de Monitoreo - Guía Completa

Sistema de monitoreo en tiempo real para Rexus.app con **Prometheus** (recolección de métricas) y **Grafana** (visualización).

---

## 🎯 Objetivos

### Visibilidad en Tiempo Real
- ✅ Métricas de performance (tiempos de respuesta)
- ✅ Métricas de negocio (queries, errores, caché)
- ✅ Alertas automáticas (problemas antes de que impacten usuarios)
- ✅ Históricos (tendencias y anomalías)

### Problemas Resueltos
- ❌ **Antes**: ¿Cómo saber si la app está lenta sin quejas de usuarios?
- ❌ **Antes**: ¿Cuántas queries por segundo se ejecutan?
- ❌ **Antes**: ¿El caché está funcionando bien?
- ✅ **Ahora**: Dashboards en tiempo real con todas las métricas

---

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                    Rexus.app (Flask)                         │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  MonitoringMiddleware                                  │ │
│  │  - Trackea todas las requests                          │ │
│  │  - Registra tiempos de respuesta                       │ │
│  │  - Cuenta errores                                      │ │
│  └────────────────────────────────────────────────────────┘ │
│                              ↓                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  MetricsManager                                        │ │
│  │  - Contadores (events)                                 │ │
│  │  - Histogramas (distribuciones)                        │ │
│  │  - Gauges (valores actuales)                           │ │
│  └────────────────────────────────────────────────────────┘ │
│                              ↓                              │
│  /metrics endpoint (formato Prometheus)                   │
└─────────────────────────────────────────────────────────────┘
                              ↓
                    Scrape cada 10s
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    Prometheus                               │
│  - Recolecta métricas                                      │
│  - Almacena time-series                                    │
│  - Evalúa reglas de alerta                                 │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                     Grafana                                 │
│  - Visualiza métricas                                      │
│  - Dashboards interactivos                                 │
│  - Alertas visuales                                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Estructura de Archivos

```
rexus/
├── monitoring/                      # Sistema de monitoreo
│   ├── __init__.py
│   ├── metrics_manager.py           # Gestor de métricas
│   ├── prometheus_exporter.py       # Exportador a Prometheus
│   └── middleware.py                # Middleware Flask
│
monitoring/                          # Configuraciones
├── prometheus/
│   ├── prometheus.yml               # Config de Prometheus
│   └── alerts.yml                   # Reglas de alerta
├── grafana/
│   ├── dashboard-rexus.json         # Dashboard Rexus.app
│   └── provisioning/                # Config automática Grafana
│
docker-compose.monitoring.yml        # Infraestructura de monitoreo
```

---

## 🚀 Instalación y Configuración

### Paso 1: Levantar Infraestructura

```bash
# Levantar Prometheus + Grafana + Redis
docker-compose -f docker-compose.monitoring.yml up -d

# Verificar que estén corriendo
docker ps

# Ver logs
docker-compose -f docker-compose.monitoring.yml logs -f
```

### Paso 2: Configurar Flask App

```python
from flask import Flask
from rexus.monitoring.middleware import MonitoringMiddleware

app = Flask(__name__)

# Inicializar middleware de monitoreo
monitoring = MonitoringMiddleware()
monitoring.init_app(app)

# Tu código existente...
@app.route('/api/productos')
def listar_productos():
    # El middleware trackea automáticamente:
    # - Tiempo de respuesta
    # - Código de estado
    # - Contador de requests
    return jsonify(productos)
```

### Paso 3: Acceder a Dashboards

1. **Prometheus**: http://localhost:9090
   - Interface de consultas
   - Ver métricas crudas
   - Probar queries

2. **Grafana**: http://localhost:3000
   - Usuario: `admin`
   - Password: `admin123`
   - Dashboard: "Rexus.app - Performance"

---

## 📏 Métricas Disponibles

### Métricas HTTP

```
# Requests por segundo
rate(rexus_counter_http_requests_total[1m])

# Latencia P95
histogram_quantile(0.95, rate(rexus_histogram_http_request_duration_seconds_bucket[5m]))

# Requests por endpoint
sum(rate(rexus_counter_http_requests_total[5m])) by (endpoint)
```

### Métricas de Base de Datos

```
# Queries por segundo
sum(rate(rexus_counter_database_queries_total[1m])) by (query_type, table)

# Duración P95 de queries
histogram_quantile(0.95, rate(rexus_histogram_database_query_duration_seconds_bucket[5m]))

# Queries totales
rexus_counter_database_queries_total{query_type="SELECT", table="inventario_perfiles"}
```

### Métricas de Caché

```
# Cache hit rate
sum(rate(rexus_counter_cache_operations_total{result="hit"}[5m])) /
sum(rate(rexus_counter_cache_operations_total[5m]))

# Operaciones de caché por segundo
rate(rexus_counter_cache_operations_total[1m])
```

### Métricas de Errores

```
# Errores por segundo por tipo
rate(rexus_counter_errors_total[1m])

# Errores totales
rexus_counter_errors_total{error_type="ValueError"}
```

---

## 🔔 Alertas Configuradas

### Alerta: Alta Tasa de Errores
```
HighErrorRate - Activado cuando: rate(errors) > 0.1/sec por 5min
```

### Alerta: Queries Lentas
```
SlowDatabaseQueries - Activado cuando: P95 latency > 1s por 10min
```

### Alerta: Bajo Cache Hit Rate
```
HighCacheMissRate - Activado cuando: hit rate < 50% por 10min
```

### Alerta: Aplicación Down
```
ApplicationDown - Activado cuando: app no responde por 2min
```

---

## 💡 Uso Avanzado

### Trackear Módulos Específicos

```python
from rexus.monitoring.middleware import track_module

@track_module('inventario')
def crear_producto(producto_data):
    # Registra automáticamente:
    # - module_calls_total{module="inventario", function="crear_producto"}
    # - inventario_crear_producto_duration
    return repository.create(producto_data)
```

### Trackear Endpoints Específicos

```python
from rexus.monitoring.middleware import track_endpoint

@app.route('/api/estadisticas')
@track_endpoint('estadisticas_complex')
def get_estadisticas():
    # Registra duración específica para este endpoint
    return jsonify(calculos_complejos())
```

### Métricas Personalizadas

```python
from rexus.monitoring.metrics_manager import MetricsManager

# Contador personalizado
MetricsManager.counter('productos_creados', labels={'categoria': 'Perfiles'})

# Histograma personalizado
MetricsManager.histogram('carrito_compra_total', 1500.00, {'moneda': 'ARS'})

# Gauge personalizado (valor actual)
MetricsManager.gauge('usuarios_conectados', 42)
```

### Context Managers

```python
# Medir operación compleja
with MetricsManager.measure_operation('calculo_inventario'):
    # Código a medir
    productos = repo.find_all()
    for p in productos:
        p.actualizar_stock()

# Medir operación de caché
with MetricsManager.track_cache_operation('get', 'redis') as (hit):
    data = cache.get(key)
    hit = data is not None  # Indica si fue cache hit
```

---

## 📊 Dashboards de Grafana

### Dashboard Principal: "Rexus.app - Performance"

**Paneles incluidos**:
1. Requests por segundo (gráfico de línea)
2. Duración P95 (gráfico de línea)
3. Queries BD por segundo (gráfico por tipo)
4. Duración queries BD (gráfico P95)
5. Cache hit rate (gráfico de porcentaje)
6. Errores por segundo (gráfico por tipo)
7. Módulos más activos (tabla)

**Actualización**: Cada 10 segundos
**Rango**: Última 1 hora

---

## 🛠️ Troubleshooting

### Problema: Prometheus no scrapea métricas

**Verificar**:
```bash
# Endpoint existe?
curl http://localhost:5000/metrics

# Prometheus tiene configurado el target?
# Ir a http://localhost:9090/targets
```

### Problema: No aparecen métricas en Grafana

**Verificar**:
1. Prometheus está corriendo: `docker ps | grep prometheus`
2. Datasource configurado en Grafana: Configuration → Data Sources → Prometheus
3. Query es correcto: Probar en Prometheus primero

### Problema: Métricas no se actualizan

**Verificar**:
```python
# Middleware inicializado?
app.before_request_funcs  # Debe tener funciones de monitoreo

# Métricas se están registrando?
from rexus.monitoring.metrics_manager import MetricsManager
MetricsManager.get_all_metrics()  # Debe tener datos
```

---

## 📈 Ejemplos de Queries Útiles

### Encontrar endpoints lentos
```promql
topk(10, sum(rate(rexus_histogram_http_request_duration_seconds_sum[5m])) by (endpoint) /
        sum(rate(rexus_histogram_http_request_duration_seconds_count[5m])) by (endpoint))
```

### Queries más lentas por tabla
```promql
histogram_quantile(0.95, sum(rate(rexus_histogram_database_query_duration_seconds_bucket[10m])) by (le, table))
```

### Tasa de errores en las últimas 24h
```promql
increase(rexus_counter_errors_total[24h])
```

### Cache hit rate por tipo de operación
```promql
sum(rate(rexus_counter_cache_operations_total{result="hit"}[5m])) by (operation) /
sum(rate(rexus_counter_cache_operations_total[5m])) by (operation)
```

---

## 🔒 Seguridad

### Proteger Endpoint /metrics

En producción, restringir acceso a métricas:

```python
from functools import wraps
from flask import request

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or auth.username != 'admin' or auth.password != 'secret':
            return "Unauthorized", 401
        return f(*args, **kwargs)
    return decorated

# Aplicar a endpoint /metrics
@app.route('/metrics')
@require_auth
def metrics():
    # ... código de métricas
```

---

## 📚 Recursos Adicionales

- **Prometheus Query Language**: https://prometheus.io/docs/prometheus/latest/querying/basics/
- **Grafana Dashboards**: https://grafana.com/docs/grafana/latest/dashboards/
- **Best Practices**: https://prometheus.io/docs/practices/naming/

---

## ✅ Checklist de Implementación

- [x] MetricsManager implementado
- [x] PrometheusExporter creado
- [x] MonitoringMiddleware para Flask
- [x] Configuración de Prometheus
- [x] Configuración de Grafana
- [x] Docker Compose para monitoreo
- [x] Alertas configuradas
- [x] Dashboard creado
- [ ] Integrar en app principal (pendiente)
- [ ] Probar en producción

---

**Fecha**: 2025-02-07
**Implementado por**: Claude Sonnet (AI Assistant)
**Componentes**: 6 archivos creados
**Stack**: Prometheus + Grafana + Redis Exporter
**Próximo paso**: Integrar middleware en app Flask principal
