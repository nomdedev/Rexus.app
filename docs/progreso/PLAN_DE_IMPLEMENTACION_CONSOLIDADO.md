# 🚀 PLAN DE IMPLEMENTACIÓN CONSOLIDADO
## Rexus.app - Plan Detallado de Correcciones Prioritarias

**Fecha:** 7 de Febrero de 2026  
**Versión:** Rexus.app v2.0.0  
**Basado en:** 5 Auditorías Exhaustivas Completadas  
**Horas Estimadas Totales:** 150-200 horas

---

## 📊 RESUMEN EJECUTIVO

### 🎯 **OBJETIVO: HABILITAR PRODUCCIÓN EMPRESARIAL**

Este plan consolida las correcciones identificadas en las auditorías de Seguridad, Base de Datos, Performance, Testing y Arquitectura, priorizadas por severidad e impacto en producción.

### 📈 **PUNTUACIÓN ACTUAL: 69/100**
### 🎯 **PUNTUACIÓN META: 85/100**

---

## 🔴 FASE 1 - CORRECCIONES CRÍTICAS (48-72 horas)

### Objetivo: Resolver problemas que impiden producción

### 1.1 🔴 **CRÍTICO: Reemplazar SHA-256 por bcrypt/Argon2**

**Archivo:** [`rexus/core/auth_manager.py:188-191`](rexus/core/auth_manager.py:188-191)

**Severidad:** 🔴 CRÍTICA  
**CVSS Score:** 8.5 (HIGH)  
**Tiempo:** 2-3 horas  
**Riesgo:** Medio (requiere migración de DB)

**Pasos:**
1. Importar `verify_password_secure` desde [`rexus/utils/password_security.py`](rexus/utils/password_security.py:88)
2. Reemplazar líneas 188-191
3. Crear script de migración de hashes existentes
4. Ejecutar migración en base de datos
5. Verificar funcionalidad con tests

**Código de Corrección:**
```python
# ANTES (INSEGURO):
# rexus/core/auth_manager.py:188-191
# TODO: Implementar verificación segura (PBKDF2, bcrypt, argon2)
# Por ahora usar SHA-256
password_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
password_valid = password_hash == stored_hash

# DESPUÉS (SEGURO):
from rexus.utils.password_security import verify_password_secure
password_valid = verify_password_secure(password, stored_hash)
```

**Script de Migración:**
```python
# scripts/migrate_password_hashes.py
def migrate_password_hashes():
    """
    Migrar hashes SHA-256 existentes a bcrypt/Argon2.
    
    Proceso:
    1. Detectar usuarios con hash SHA-256 (64 chars hex)
    2. Forzar reset de contraseña en próximo login
    3. Opcional: Re-hash si se tiene contraseña temporal
    """
    # Implementación pendiente
```

**Criterio de Aceptación:**
- ✅ SHA-256 eliminado del código
- ✅ Todos los nuevos hashes usan bcrypt/Argon2
- ✅ Tests de autenticación pasan
- ✅ Documentación actualizada

---

### 1.2 🔴 **CRÍTICO: Implementar Sistema de Backups Automatizados**

**Severidad:** 🔴 CRÍTICA  
**Impacto:** Pérdida total de datos en caso de fallo  
**Tiempo:** 8-12 horas  
**Riesgo:** Alto (afecta disponibilidad)

**Pasos:**

**A. Crear Scripts de Backup:**
```python
# scripts/automated_backup.py
import subprocess
from datetime import datetime

def backup_database(database_name, backup_type='FULL'):
    """Ejecuta backup de base de datos"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f'D:/backups/{database_name}_{backup_type.lower()}_{timestamp}.bak'
    
    if backup_type == 'FULL':
        sql = f"""
        BACKUP DATABASE [{database_name}]
        TO DISK = '{backup_path}'
        WITH FORMAT, COMPRESSION, STATS = 10
        """
    elif backup_type == 'DIFF':
        sql = f"""
        BACKUP DATABASE [{database_name}]
        TO DISK = '{backup_path}'
        WITH DIFFERENTIAL, COMPRESSION, STATS = 10
        """
    elif backup_type == 'LOG':
        sql = f"""
        BACKUP LOG [{database_name}]
        TO DISK = '{backup_path}'
        WITH COMPRESSION, STATS = 10
        """
    
    # Ejecutar backup
    subprocess.run(['sqlcmd', '-S', 'localhost', '-Q', sql])
    print(f"Backup completado: {backup_path}")

# Backup diario completo
backup_database('inventario', 'FULL')
backup_database('users', 'FULL')
backup_database('auditoria', 'FULL')
```

**B. Configurar Tareas Programadas:**
- **Windows:** Task Scheduler
  - Full backup: Diario a las 2:00 AM
  - Differential: Cada 6 horas (8:00 AM, 2:00 PM, 8:00 PM)
  - Log backup: Cada 15 minutos

**C. Implementar Monitoreo:**
```python
# Tabla de control de backups
CREATE TABLE backup_control (
    id INT IDENTITY(1,1) PRIMARY KEY,
    database_name NVARCHAR(100),
    backup_type NVARCHAR(20), -- FULL, DIFF, LOG
    backup_path NVARCHAR(500),
    backup_size_mb DECIMAL(10,2),
    start_time DATETIME2,
    end_time DATETIME2,
    status NVARCHAR(20), -- SUCCESS, FAILED
    error_message NVARCHAR(MAX),
    created_at DATETIME2 DEFAULT GETDATE()
);

# Alertas
- Email si backup falla
- Notificación si backup no se ejecuta
- Reporte diario de estado de backups
```

**D. Documentar Procedimientos de Recuperación:**
```python
# docs/DISASTER_RECOVERY.md
# Escenario 1: Recuperación de Base de Datos Completa
# Escenario 2: Recuperación de Tabla Específica
# Escenario 3: Recuperación Point-in-Time
```

**Criterios de Aceptación:**
- ✅ Scripts de backup implementados
- ✅ Tareas programadas configuradas
- ✅ Monitoreo de backups funcionando
- ✅ Procedimientos de recuperación documentados
- ✅ Restauración de backups probada exitosamente

---

### 1.3 🟡 **ALTO: Eliminar Tablas Redundantes de BD**

**Tiempo:** 2-3 horas  
**Riesgo:** Medio (requiere migración de datos)

**Pasos:**
1. Verificar que `inventario_items` no tiene datos críticos
2. Migrar `reservas_stock` a `reservas_materiales`
3. Eliminar `inventario_items`
4. Eliminar `reservas_stock`

**Criterios de Aceptación:**
- ✅ Tablas redundantes eliminadas
- ✅ Datos migrados correctamente
- ✅ Tests pasan sin errores

---

## 🟡 FASE 2 - CORRECCIONES ALTAS (40-60 horas)

### Objetivo: Alcanzar 50% de cobertura y mejorar monitoreo

### 2.1 🟡 **ALTO: Implementar Monitoreo de Métricas**

**Tiempo:** 8-12 horas  
**Riesgo:** Bajo

**Pasos:**

**A. Instalar Dependencias:**
```bash
pip install prometheus_client
```

**B. Implementar Exporters:**
```python
# rexus/monitoring/metrics_exporter.py
from prometheus_client import Counter, Histogram, Gauge

# Métricas de caché
cache_hits = Counter('cache_hits_total', 'Total cache hits', ['cache_type'])
cache_misses = Counter('cache_misses_total', 'Total cache misses', ['cache_type'])
cache_hit_rate = Gauge('cache_hit_rate', 'Cache hit rate', ['cache_type'])

# Métricas de queries
query_duration = Histogram('query_duration_seconds', 'Query duration', ['module', 'query_name'])
query_errors = Counter('query_errors_total', 'Query errors', ['module', 'query_name'])

# Métricas de aplicación
request_duration = Histogram('request_duration_seconds', 'Request duration')
active_users = Gauge('active_users', 'Active users')
memory_usage = Gauge('memory_usage_bytes', 'Memory usage')
```

**C. Configurar Prometheus:**
```yaml
# monitoring/prometheus/prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'rexus'
    static_configs:
      - targets: ['localhost:8000']
```

**D. Crear Dashboard en Grafana:**
- Panel de Caché: Hit rate, latencia, tamaño
- Panel de Queries: Duración, filas retornadas, errores
- Panel de Aplicación: Requests, usuarios, memoria

**Criterios de Aceptación:**
- ✅ Exporters implementados
- ✅ Prometheus configurado
- ✅ Dashboard de Grafana creado
- ✅ Alertas configuradas

---

### 2.2 🟡 **ALTO: Implementar Cache Warming**

**Tiempo:** 4-6 horas  
**Riesgo:** Bajo

**Pasos:**
```python
# rexus/utils/cache_warming.py
def warm_up_cache():
    """Precarga datos críticos en caché"""
    from rexus.utils.cache_manager import CacheManager
    from rexus.modules.configuracion.model import ConfiguracionModel
    from rexus.modules.usuarios.model import UsuariosModel
    from rexus.modules.inventario.model import InventarioModel
    
    cache = CacheManager.get_instance()
    
    critical_data = [
        ('configuracion:all', lambda: ConfiguracionModel().obtener_todas()),
        ('usuarios:activos', lambda: UsuariosModel().obtener_usuarios_activos()),
        ('permisos:todos', lambda: UsuariosModel().obtener_todos_permisos()),
        ('inventario:categorias', lambda: InventarioModel().obtener_categorias()),
    ]
    
    for key, loader in critical_data:
        try:
            data = loader()
            cache.set(key, data, ttl=1800)  # 30 minutos
            logger.info(f"✅ Cache warmed: {key}")
        except Exception as e:
            logger.error(f"❌ Error warming cache {key}: {e}")

# Ejecutar al inicio de aplicación
# rexus/main/app.py
if __name__ == '__main__':
    warm_up_cache()
    # ... resto del código
```

**Criterios de Aceptación:**
- ✅ Función de warm-up implementada
- ✅ Datos críticos precargados al inicio
- ✅ Logs de warm-up funcionando

---

### 2.3 🔴 **CRÍTICO: Tests de Modelos Core**

**Tiempo:** 20-24 horas  
**Riesgo:** Medio

**Meta:** 30% de cobertura en modelos core

**Pasos:**

**A. Tests para InventarioModel:**
```python
# tests/unit/inventario/test_inventario_model_crud.py
class TestInventarioModelCRUD:
    """Tests CRUD completos para InventarioModel."""
    
    def test_crear_producto(self):
        """Test de creación de producto."""
        # Implementar test
    
    def test_obtener_producto_por_id(self):
        """Test de obtención por ID."""
        # Implementar test
    
    def test_actualizar_producto(self):
        """Test de actualización."""
        # Implementar test
    
    def test_eliminar_producto(self):
        """Test de eliminación."""
        # Implementar test
    
    def test_validar_stock_negativo(self):
        """Test de validación de stock negativo."""
        # Implementar test
```

**B. Tests para ObrasModel:**
```python
# tests/unit/obras/test_obras_model_crud.py
class TestObrasModelCRUD:
    """Tests CRUD completos para ObrasModel."""
    
    def test_crear_obra(self):
        """Test de creación de obra."""
        # Implementar test
    
    def test_actualizar_estado_obra(self):
        """Test de actualización de estado."""
        # Implementar test
    
    # ... más tests
```

**C. Tests para UsuariosModel:**
```python
# tests/unit/usuarios/test_usuarios_model_auth.py
class TestUsuariosModelAuth:
    """Tests de autenticación para UsuariosModel."""
    
    def test_verificar_credenciales_correctas(self):
        """Test de credenciales correctas."""
        # Implementar test
    
    def test_verificar_credenciales_incorrectas(self):
        """Test de credenciales incorrectas."""
        # Implementar test
    
    # ... más tests
```

**Criterios de Aceptación:**
- ✅ Tests CRUD para 5 modelos core
- ✅ 30% de cobertura en modelos core
- ✅ Tests pasando consistentemente

---

### 2.4 🟡 **ALTO: Estandarizar Herencia de Controladores**

**Tiempo:** 4-6 horas  
**Riesgo:** Medio

**Pasos:**
1. Ampliar `BaseController` con funcionalidad común
2. Migrar todos los controladores a heredar de `BaseController`
3. Eliminar herencia directa de `QObject`
4. Actualizar tests

**Criterios de Aceptación:**
- ✅ Todos los controladores heredan de `BaseController`
- ✅ Funcionalidad consistente
- ✅ Tests pasan

---

## 🟢 FASE 3 - CORRECCIONES MEDIAS (60-80 horas)

### Objetivo: Alcanzar 80% de cobertura y mejorar arquitectura

### 3.1 🟡 **ALTO: Tests de Seguridad Completos**

**Tiempo:** 16-20 horas  
**Riesgo:** Alto

**Pasos:**

**A. Tests de SQL Injection por Módulo:**
```python
# tests/security/test_sql_injection_completo.py
@pytest.mark.parametrize("module_name,model_class", [
    ('inventario', 'InventarioModel'),
    ('obras', 'ObrasModel'),
    ('usuarios', 'UsuariosModel'),
    ('pedidos', 'PedidosModel'),
    ('compras', 'ComprasModel'),
])
def test_sql_injection_search(module_name, model_class):
    """Test de SQL injection en métodos de búsqueda."""
    malicious_inputs = [
        "'; DROP TABLE usuarios; --",
        "1' OR '1'='1",
        "admin'--",
        "' UNION SELECT * FROM usuarios --",
    ]
    
    for malicious_input in malicious_inputs:
        with pytest.raises(Exception):
            model = get_model(model_name)
            model.buscar(malicious_input)
```

**B. Tests de XSS en Inputs:**
```python
# tests/security/test_xss_prevention.py
@pytest.mark.parametrize("input_field,xss_payload", [
    ('nombre', '<script>alert("XSS")</script>'),
    ('descripcion', '<img src=x onerror=alert("XSS")>'),
    ('observaciones', 'javascript:alert("XSS")'),
])
def test_xss_sanitization(input_field, xss_payload):
    """Test de sanitización de XSS."""
    model = InventarioModel()
    with pytest.raises(ValueError):
        model.validar_campo(input_field, xss_payload)
```

**Criterios de Aceptación:**
- ✅ Tests de SQL injection para todos los módulos
- ✅ Tests de XSS implementados
- ✅ Tests de CSRF implementados
- ✅ 80% de cobertura de seguridad

---

### 3.2 🟡 **ALTO: Tests E2E de Workflows Completos**

**Tiempo:** 16-20 horas  
**Riesgo:** Alto

**Pasos:**

**A. Workflow Compras Completo:**
```python
# tests/e2e/test_workflow_compras_completo.py
def test_workflow_completo_pedido_a_inventario():
    """
    Test E2E: Pedido → Compra → Recepción → Inventario
    """
    # 1. Crear pedido
    pedido = PedidosModel().crear_pedido({
        'cliente_id': 1,
        'productos': [{'producto_id': 1, 'cantidad': 10}]
    })
    
    # 2. Generar compra desde pedido
    compra = ComprasModel().generar_compra_desde_pedido(pedido['id'])
    
    # 3. Recibir compra
    ComprasModel().recibir_compra(compra['id'])
    
    # 4. Verificar actualización de inventario
    stock = InventarioModel().obtener_stock(1)
    assert stock == 10  # Stock actualizado
```

**B. Workflow Obras Completo:**
```python
# tests/e2e/test_workflow_obras_completo.py
def test_workflow_obra_completa():
    """
    Test E2E: Crear → Planificar → Producir → Entregar
    """
    # 1. Crear obra
    obra = ObrasModel().crear_obra({...})
    
    # 2. Asignar materiales
    ObrasModel().asignar_materiales(obra['id'], [...])
    
    # 3. Registrar producción
    ObrasModel().registrar_produccion(obra['id'], {...})
    
    # 4. Marcar como completada
    ObrasModel().actualizar_estado(obra['id'], 'COMPLETADA')
```

**Criterios de Aceptación:**
- ✅ 4 workflows E2E implementados
- ✅ Tests pasan consistentemente
- ✅ Cobertura de flujos críticos

---

### 3.3 🟢 **MEDIO: Implementar Service Layer**

**Tiempo:** 16-20 horas  
**Riesgo:** Medio

**Pasos:**

**A. Crear ObrasService:**
```python
# rexus/services/obras/obras_service.py
class ObrasService(BaseService):
    """Servicio para gestión de obras."""
    
    def crear_obra_completa(self, datos: dict) -> ServiceResult:
        """
        Crea obra completa con todas las validaciones y procesos asociados.
        
        Orquesta:
        1. Validar datos
        2. Crear obra
        3. Asignar materiales si se especifican
        4. Crear cronograma si se especifica
        5. Notificar stakeholders
        """
        # Implementación
```

**B. Crear PedidosService:**
```python
# rexus/services/pedidos/pedidos_service.py
class PedidosService(BaseService):
    """Servicio para gestión de pedidos."""
    
    def procesar_pedido_completo(self, pedido_id: int) -> ServiceResult:
        """
        Procesa pedido completo de principio a fin.
        
        Orquesta:
        1. Validar stock disponible
        2. Reservar materiales
        3. Generar orden de producción
        4. Notificar logística
        """
        # Implementación
```

**Criterios de Aceptación:**
- ✅ 4 servicios implementados
- ✅ Lógica compleja movida a servicios
- ✅ Models simplificados

---

### 3.4 🟢 **MEDIO: Implementar Repository Pattern**

**Tiempo:** 16-20 horas  
**Riesgo:** Medio

**Pasos:**

**A. Crear ObrasRepository:**
```python
# rexus/repositories/obras/obras_repository.py
class ObrasRepository(BaseRepository):
    """Repositorio para obras."""
    
    def get_by_codigo(self, codigo: str) -> Optional[Obra]:
        """Obtener obra por código."""
        query = "SELECT * FROM obras WHERE codigo_obra = ?"
        # Implementación
    
    def get_obras_by_estado(self, estado: str) -> List[Obra]:
        """Obtener obras por estado."""
        query = "SELECT * FROM obras WHERE estado = ?"
        # Implementación
```

**B. Crear PedidosRepository:**
```python
# rexus/repositories/pedidos/pedidos_repository.py
class PedidosRepository(BaseRepository):
    """Repositorio para pedidos."""
    # Implementación similar
```

**Criterios de Aceptación:**
- ✅ 4 repositorios implementados
- ✅ Queries complejas movidas a repositorios
- ✅ Models simplificados

---

## 📊 CRONOGRAMA DE IMPLEMENTACIÓN

### Semana 1 (48-72 horas) - 🔴 CRÍTICO

**Día 1-2 (8-12 horas):**
- ✅ Reemplazar SHA-256 por bcrypt/Argon2
- ✅ Crear script de migración de hashes
- ✅ Ejecutar migración

**Día 3-4 (12-16 horas):**
- ✅ Implementar sistema de backups automatizados
- ✅ Configurar tareas programadas
- ✅ Probar restauración

**Día 5-6 (8-12 horas):**
- ✅ Eliminar tablas redundantes
- ✅ Implementar monitoreo de métricas
- ✅ Configurar Prometheus/Grafana

**Día 7 (8-12 horas):**
- ✅ Implementar cache warming
- ✅ Tests de modelos core (CRUD básico)

**Entregables:**
- ✅ Sistema de autenticación seguro
- ✅ Sistema de backups funcionando
- ✅ Monitoreo de métricas operativo
- ✅ 20% cobertura de tests

---

### Semana 2-3 (40-60 horas) - 🟡 ALTO

**Día 8-10 (16-20 horas):**
- ✅ Tests de modelos core completos
- ✅ Estandarizar herencia de controladores
- ✅ Tests de seguridad completos

**Día 11-13 (16-20 horas):**
- ✅ Tests E2E de workflows completos
- ✅ Implementar Service Layer
- ✅ Implementar Repository Pattern

**Día 14 (8-12 horas):**
- ✅ Refactorización de modelos grandes
- ✅ Documentación de arquitectura

**Entregables:**
- ✅ 50% cobertura de tests
- ✅ 80% cobertura de seguridad
- ✅ Arquitectura mejorada
- ✅ Service Layer implementado

---

## 📈 MÉTRICAS DE ÉXITO

### Criterios de Aceptación por Fase

**Fase 1 - CRÍTICA:**
- [ ] SHA-256 eliminado
- [ ] Backups automatizados funcionando
- [ ] Monitoreo operativo
- [ ] 20% cobertura tests

**Fase 2 - ALTA:**
- [ ] 50% cobertura tests
- [ ] 80% cobertura seguridad
- [ ] Cache warming implementado
- [ ] Controladores estandarizados

**Fase 3 - MEDIA:**
- [ ] Service Layer implementado
- [ ] Repository Pattern implementado
- [ ] Workflows E2E probados
- [ ] Documentación creada

---

## 🏆 CONCLUSIÓN

### Tiempo Total Estimado

- **Fase 1 (CRÍTICA):** 48-72 horas (1-2 semanas)
- **Fase 2 (ALTA):** 40-60 horas (1-2 semanas)
- **Fase 3 (MEDIA):** 60-80 horas (2-3 semanas)

**TOTAL:** 150-200 horas (4-7 semanas)

### Puntuación Esperada

**Actual:** 69/100  
**Post-Fase 1:** 75/100  
**Post-Fase 2:** 82/100  
**Post-Fase 3:** 85/100

### Recomendación Final

**SE RECOMIENDA:**
1. ✅ Completar Fase 1 antes de producción
2. ✅ Completar Fase 2 para producción empresarial
3. ✅ Completar Fase 3 para excelencia operacional

---

## 📝 FIRMAS

**Autor:** AI Expert Team - Roo Code  
**Fecha:** 7 de Febrero de 2026  
**Versión:** 1.0  
**Próxima Revisión:** Post-Fase 1

---

**FIN DEL PLAN DE IMPLEMENTACIÓN CONSOLIDADO**
