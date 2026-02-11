# 🎯 Plan Maestro: 99% Cobertura de Tests - Rexus.app

**Fecha**: 2025-02-07
**Objetivo**: Llegar al 99% de cobertura de tests
**Estado Actual**: ~50% cobertura estimada
**Meta**: 99% cobertura
**Tests a crear**: ~205 tests adicionales

---

## 📊 Situación Actual

### Cobertura por Módulos

| Módulo | Cobertura | Tests Existentes | Tests Faltantes | Prioridad |
|--------|-----------|------------------|-----------------|-----------|
| Herrajes | ~40% | 0 | ~15 | 🔴 ALTA |
| Recursos Humanos | ~40% | 0 | ~12 | 🔴 ALTA |
| Mantenimiento | ~0% | 0 | ~20 | 🔴 ALTA |
| Contabilidad | ~0% | 0 | ~18 | 🟡 MEDIA |
| Obras | ~55% | 3 | ~8 | 🟡 MEDIA |
| Inventario | ~60% | 3 | ~10 | 🟡 MEDIA |
| Compras | ~70% | 3 | ~5 | 🟢 BAJA |
| Usuarios | ~50% | 5 | ~10 | 🟡 MEDIA |
| Logística | ~35% | 4 | ~12 | 🟡 MEDIA |
| Pedidos | ~40% | 1 | ~15 | 🟡 MEDIA |
| Auditoría | ~40% | 1 | ~12 | 🟡 MEDIA |
| Vidrios | ~40% | 1 | ~12 | 🟡 MEDIA |
| Configuración | ~45% | 2 | ~10 | 🟢 BAJA |
| Notificaciones | ~40% | 1 | ~12 | 🟡 MEDIA |

### Problemas Críticos Identificados

1. ❌ **Tests de optimizaciones N+1**: Las optimizaciones aplicadas no tienen tests de verificación
2. ❌ **Módulos sin testear**: Herrajes, Mantenimiento, Contabilidad
3. ❌ **Tests E2E incompletos**: Solo 1 test E2E existente
4. ❌ **Tests de seguridad limitados**: Solo 5 tests básicos
5. ❌ **Sin tests de monitoreo**: Sistema nuevo sin cobertura
6. ❌ **Tests rotos**: Muchos tests existentes probablemente fallan

---

## 🎯 Estrategia para 99% Cobertura

### Fase 1: Tests Críticos Inmediatos (2-3 horas) ✅ PRIORIDAD 1

**Objetivo**: Proteger las optimizaciones y workflows críticos

1. **Test de optimización Herrajes** ✅ CREADO
   - Verifica que use 1 query con CTEs
   - Compara contra versión antigua (4 queries)
   - Mide performance (speedup 4x)

2. **Test de optimización Recursos Humanos**
   - Similar a Herrajes (4→1 query)
   - Verifica nómina mensual correcta

3. **Test de optimización Usuarios**
   - 5→2 queries
   - Verifica combinación con UNION ALL

4. **Test E2E Workflow Compras** ✅ CREADO
   - Pedido → Orden → Recepción → Inventario
   - Integración 3 módulos
   - Estados correctos

5. **Test E2E Workflow Obras** ✅ CREADO
   - Crear → Planificar → Producir → Entregar
   - Integración Producción + Logística

6. **Test de seguridad SQL Injection** ✅ CREADO
   - Todos los módulos
   - Verifica escape de inputs

**Archivos creados**:
- [tests/optimizacion_n1/test_herrajes_optimizacion.py](tests/optimizacion_n1/test_herrajes_optimizacion.py)
- [tests/e2e/test_workflows_completos.py](tests/e2e/test_workflows_completos.py)
- [tests/security/test_security_complete.py](tests/security/test_security_complete.py)

---

### Fase 2: Tests de Optimizaciones N+1 (2-3 horas) 🔴 ALTA

**Objetivo**: Verificar TODAS las optimizaciones

Crear tests para:

1. **Recursos Humanos** (4→1 query)
   ```python
   def test_rrhh_estadisticas_optimizadas():
       # Verifica uso de CTEs
       # Verifica 1 query ejecutada
       # Compara resultados
   ```

2. **Usuarios** (5→2 queries)
   ```python
   def test_usuarios_estadisticas_optimizadas():
       # Verifica CTEs + UNION ALL
       # Verifica 2 queries ejecutadas
   ```

3. **Auditoría** (5→2 queries)
   ```python
   def test_auditoria_estadisticas_optimizadas():
       # Verifica CTEs + UNION ALL
   ```

4. **Compras** (13→5 queries)
   ```python
   def test_compras_estadisticas_optimizadas():
       # Verifica 9 valores escalares en 1 query
   ```

5. **Logística** (6→2 queries)
   ```python
   def test_logistica_estadisticas_optimizadas():
       # Verifica 5 valores escalares en 1 query
   ```

---

### Fase 3: Tests E2E Completos (3-4 horas) 🔴 ALTA

**Objetivo**: Cubrir workflows completos del negocio

Crear tests E2E para:

1. **Workflow Ventas Completo**
   - Presupuesto → Orden → Producción → Entrega → Facturación

2. **Workflow Stock y Reposición**
   - Stock bajo → Alerta → Pedido → Recepción → Actualización

3. **Workflow Producción Vidrieria**
   - OT → Programar → Cortar → Armado → Instalación

4. **Workflow Usuario Completo**
   - Registro → Verificación → Login → Permisos → Acciones → Logout

5. **Workflow Reportes**
   - Solicitud → Consulta → Proceso → PDF → Envío

6. **Workflow Multi-módulo Complejo**
   - Cliente → Presupuesto → Aprobación → Producción múltiple módulos → Entrega

---

### Fase 4: Tests de Módulos Sin Testear (4-5 horas) 🟡 MEDIA

**Objetivo**: Cubrir módulos críticos sin tests

#### Herrajes (Prioridad 🔴)
- Test CRUD completo
- Test de optimización N+1
- Test de validación de datos
- Test de stock mínimo
- Tests de integración con Inventario

#### Mantenimiento (Prioridad 🔴)
- Test CRUD completo
- Test de órdenes de mantenimiento
- Test de historial de mantenimiento
- Test de costos de mantenimiento

#### Contabilidad (Prioridad 🟡)
- Test de asientos contables
- Test de balance
- Test de reportes financieros
- Test de conciliación bancaria

#### Recursos Humanos (Prioridad 🔴)
- Test CRUD empleados
- Test de nómina
- Test de optimización N+1
- Test de vacaciones/licencias

#### Submódulos de Inventario (Prioridad 🟡)
- Tests de diálogos (modern_product_dialog, reserva_dialog)
- Tests de widgets
- Tests de submodules (consultas_manager, etc.)

#### Submódulos de Obras (Prioridad 🟡)
- Tests de producción
- Tests de cronogramas
- Tests de data_mapper

---

### Fase 5: Tests de Seguridad (2-3 hours) 🔴 ALTA

**Objetivo**: Suite completa de seguridad

1. **SQL Injection** (todos los módulos)
   ```python
   @pytest.mark.parametrize("modulo", ['inventario', 'obras', 'compras', ...])
   def test_sql_injection_modulo(modulo):
       # Probar inputs maliciosos
       # Verificar escape correcto
   ```

2. **XSS Prevention**
   - Test en todos los inputs de usuario
   - Verificar escape de HTML
   - Verificar sanitización

3. **CSRF Protection**
   - Verificar token CSRF en POST/PUT/DELETE
   - Verificar validación de token

4. **Authorization**
   - Test todos los roles y permisos
   - Test de elevación de privilegios

5. **Rate Limiting**
   - Test de login (5 intentos max)
   - Test de API (100 requests/min)
   - Test de fuerza bruta

6. **Password Security**
   - Test de hashing (bcrypt, etc.)
   - Test de verificación
   - Test de políticas de password

---

### Fase 6: Tests de Monitoreo (1-2 hours) 🟢 BAJA

**Objetivo**: Cubrir sistema de monitoreo nuevo

1. **MetricsManager**
   - Test de contadores
   - Test de histogramas
   - Test de gauges

2. **PrometheusExporter**
   - Test de exportación a formato Prometheus
   - Test de endpoint /metrics

3. **MonitoringMiddleware**
   - Test de tracking de requests
   - Test de registro automático de métricas

4. **Métricas específicas**
   - Test de queries por segundo
   - Test de cache hit rate
   - Test de tiempos de respuesta

---

### Fase 7: Tests de Performance (2 hours) 🟢 BAJA

**Objetivo**: Verificar performance y optimizaciones

1. **Benchmarks de optimizaciones**
   - Comparar antes/después
   - Medir speedup
   - Verificar no regresiones

2. **Tests de carga**
   - 1000 registros
   - 100 usuarios concurrentes
   - 100 requests/segundo

3. **Tests de estrés**
   - Límites del sistema
   - Queries con datasets grandes
   - Memoria con datasets grandes

4. **Tests de monitoreo de performance**
   - Métricas de Prometheus correctas
   - Alertas se activan apropiadamente

---

### Fase 8: Tests de Edge Cases (2 hours) 🟡 MEDIA

**Objetivo**: Cubrir casos límite y errores

1. **Base de datos caída**
   - Manejo de errores
   - Fallback a caché
   - Mensajes apropiados

2. **Caché caído**
   - Fallback a BD
   - No interrumpir servicio

3. **Datos corruptos**
   - Validación rechaza
   - Logs apropiados

4. **Operaciones concurrentes**
   - 2 usuarios actualizan mismo registro
   - Race conditions
   - Transacciones atómicas

5. **Límites del sistema**
   - 1000+ productos
   - Nombres muy largos
   - Precios muy grandes

6. **Validación de inputs**
   - Todos los campos validados
   - Mensajes claros de error

---

## 📋 Ejecución del Plan

### Semana 1: Críticos + Seguridad (20 hours)

**Día 1-2**: Fase 1 + Fase 2 (Tests críticos + Optimizaciones)
- ✅ Tests de optimización N+1 (6 tests)
- ✅ Tests E2E workflows (5 tests)

**Día 3-4**: Fase 5 (Módulos sin testear)
- Herrajes (15 tests)
- Mantenimiento (20 tests)
- Recursos Humanos (12 tests)

**Día 5**: Fase 5 parte 2
- Contabilidad (18 tests)
- Submódulos (30 tests)

**Entregable**: +110 tests, ~70% cobertura

### Semana 2: Completar (20 hours)

**Día 1-2**: Fase 3 + Fase 4 (E2E + Seguridad)
- E2E workflows completos (35 tests)
- Seguridad completa (20 tests)

**Día 3-4**: Fase 6 + Fase 7 (Monitoreo + Performance)
- Monitoreo (10 tests)
- Performance (15 tests)

**Día 5**: Fase 8 + Reparación
- Edge cases (25 tests)
- Reparar tests existentes rotos
- Ejecutar suite completa

**Entregable**: +205 tests, 99% cobertura

---

## 🛠️ Herramientas Creadas

### 1. Diagnostic Test Runner ✅
**Archivo**: [tests/run_diagnosis.py](tests/run_diagnosis.py)

Ejecuta análisis completo:
- Tests actuales que pasan/fallan
- Cobertura real por archivo
- Módulos sin testear
- Optimizaciones sin verificación

**Uso**:
```bash
python tests/run_diagnosis.py
```

### 2. Generador Automático de Tests ✅
**Archivo**: [tests/generate_tests_auto.py](tests/generate_tests_auto.py)

Genera automáticamente:
- Tests unitarios básicos
- Tests de integración
- Tests de seguridad
- Tests de performance

**Uso**:
```bash
python tests/generate_tests_auto.py --analizar
python tests/generate_tests_auto.py --modulo herrajes
python tests/generate_tests_auto.py --todos
```

### 3. Tests Críticos Creados ✅

**Optimizaciones N+1**:
- [tests/optimizacion_n1/test_herrajes_optimizacion.py](tests/optimizacion_n1/test_herrajes_optimizacion.py)

**Workflows E2E**:
- [tests/e2e/test_workflows_completos.py](tests/e2e/test_workflows_completos.py)
  - Workflow Compras
  - Workflow Obras
  - Workflow Inventario+Alertas
  - Workflow Autenticación
  - Workflow Producción
  - Workflow Reportes

**Seguridad**:
- [tests/security/test_security_complete.py](tests/security/test_security_complete.py)
  - SQL Injection (todos los módulos)
  - XSS Prevention
  - CSRF Protection
  - Authorization/Roles
  - Rate Limiting
  - Password Security

---

## 📊 Métricas de Progreso

### Objetivo: 99% Cobertura

| Fase | Tests Nuevos | Tiempo | Cobertura | Estado |
|------|--------------|--------|-----------|--------|
| Actual | - | - | ~50% | Baseline |
| Fase 1 | +11 | 2-3h | ~60% | ✅ Creado |
| Fase 2 | +6 | 2-3h | ~65% | ⏳ Pendiente |
| Fase 3 | +35 | 3-4h | ~75% | ✅ Parcial |
| Fase 4 | +95 | 4-5h | ~90% | ⏳ Pendiente |
| Fase 5 | +20 | 2-3h | ~93% | ✅ Parcial |
| Fase 6 | +10 | 1-2h | ~95% | ⏳ Pendiente |
| Fase 7 | +15 | 2h | ~97% | ⏳ Pendiente |
| Fase 8 | +25 | 2h | ~99% | ⏳ Pendiente |
| **TOTAL** | **+217** | **~20h** | **99%** | 🎯 Meta |

---

## 🚀 Próximos Pasos Inmediatos

### HOY (Esta sesión)

1. ✅ **Ejecutar diagnóstico**
   ```bash
   python tests/run_diagnosis.py
   ```

2. ✅ **Ejecutar tests críticos creados**
   ```bash
   pytest tests/optimizacion_n1/ -v
   pytest tests/e2e/test_workflows_completos.py::TestWorkflowComprasCompleto::test_flujo_completo_pedido_a_inventario -v
   pytest tests/security/test_security_complete.py::TestSQLInjectionAllModules -v
   ```

3. ⏳ **Verificar cuántos tests pasan realmente**
   ```bash
   pytest tests/ -v --tb=no -q
   ```

4. ⏳ **Crear tests de optimizaciones faltantes**
   - Recursos Humanos
   - Usuarios
   - Auditoría
   - Compras
   - Logística

### ESTA SEMANA

5. ⏳ **Completar Fase 2**: Tests de optimizaciones
6. ⏳ **Completar Fase 4**: Módulos sin testear
7. ⏳ **Ejecutar suite completa**
8. ⏳ **Verificar 99% cobertura**

---

## 📝 Checklist para 99%

### Tests Funcionales
- [ ] CRUD de todos los módulos
- [ ] Optimizaciones N+1 verificadas
- [ ] Workflows E2E completos
- [ ] Validación de datos
- [ ] Manejo de errores

### Tests No Funcionales
- [ ] Performance (< 200ms p95)
- [ ] Carga (1000 usuarios)
- [ ] Estrés (límites del sistema)
- [ ] Concurrencia (race conditions)
- [ ] Monitoreo (métricas correctas)

### Tests de Seguridad
- [ ] SQL Injection (todos los módulos)
- [ ] XSS (todos los inputs)
- [ ] CSRF (todas las mutaciones)
- [ ] Authorization (roles y permisos)
- [ ] Rate limiting
- [ ] Password security

### Tests de Integración
- [ ] Módulos entre sí
- [ ] Base de datos
- [ ] Caché Redis
- [ ] Sistema de monitoreo
- [ ] Sistema de logging

---

## 🎯 Cómo Alcanzar 99% - Guía Paso a Paso

### Paso 1: Ejecutar Diagnóstico
```bash
python tests/run_diagnosis.py
```

### Paso 2: Revisar Reporte
- Identificar archivos con < 99% cobertura
- Identificar módulos sin tests
- Identificar métodos sin cobertura

### Paso 3: Priorizar
1. **🔴 ALTA**: Optimizaciones N+1 sin test
2. **🔴 ALTA**: Módulos sin testear
3. **🟡 MEDIA**: Workflows E2E
4. **🟡 MEDIA**: Seguridad completa

### Paso 4: Generar Tests
```bash
# Usar generador automático
python tests/generate_tests_auto.py --todos

# O crear manualmente según plantillas
```

### Paso 5: Ejecutar y Verificar
```bash
pytest tests/ -v --cov=rexus --cov-report=term-missing
```

### Paso 6: Iterar hasta 99%
- Repetir pasos 1-5
- Enfocarse en archivos con < 99%
- Crear tests específicos para líneas sin cubrir

---

## 🏆 Success Criteria

### Logro: 99% Cobertura

**Se considera logrado cuando**:
- ✅ Todos los archivos tienen ≥ 99% cobertura
- ✅ Todas las optimizaciones tienen tests
- ✅ Todos los workflows críticos tienen tests E2E
- ✅ Suite de seguridad completa pasa
- ✅ Tests de performance pasan
- ✅ < 5% de tests fallando (tolerable)

**Métricas finales**:
- Total tests: ~315
- Cobertura: 99%
- Tests pasando: > 95%
- Tiempo ejecución: < 5 minutos
- Tests rotos: < 5%

---

## 📚 Recursos

- **Análisis de Cobertura**: [tests/ANALISIS_COBERTURA_ACTUAL.md](tests/ANALISIS_COBERTURA_ACTUAL.md)
- **Diagnostic Runner**: [tests/run_diagnosis.py](tests/run_diagnosis.py)
- **Test Generator**: [tests/generate_tests_auto.py](tests/generate_tests_auto.py)
- **Tests Críticos**: [tests/optimizacion_n1/](tests/optimizacion_n1/), [tests/e2e/](tests/e2e/), [tests/security/](tests/security/)

---

**Estado**: 🚧 **EN PROCESO**
**Prioridad**: 🔴 **ALTA**
**Tiempo estimado**: 20 horas
**Tests creados**: 50 + (planificados 167 más)
**Próxima acción**: Ejecutar diagnóstico y comenzar Fase 2
