# CLAUDE.md - Configuración del Proyecto Rexus.app

## 📋 Información del Proyecto

**Nombre:** Rexus.app  
**Tipo:** Sistema de gestión empresarial  
**Framework:** Python + PyQt6  
**Base de Datos:** SQLite + SQL Server  
**Fecha:** 21/08/2025  

## 🏗️ Arquitectura del Proyecto

### Estructura Principal
```
rexus/
├── core/           # Componentes centrales (auth, database, etc.)
├── modules/        # Módulos de negocio
│   ├── configuracion/
│   ├── inventario/
│   ├── obras/
│   ├── compras/
│   ├── pedidos/
│   ├── vidrios/
│   └── notificaciones/
├── utils/          # Utilidades generales
├── ui/            # Componentes UI reutilizables
└── tests/         # Tests organizados por módulo
```

## 🧪 Estructura de Tests Recomendada

### Organización por Módulos y Tipos
```
tests/
├── unit/                          # Tests unitarios
│   ├── configuracion/
│   │   ├── test_model.py
│   │   ├── test_controller.py
│   │   └── test_view.py
│   ├── inventario/
│   │   ├── test_model.py
│   │   ├── test_submodules/
│   │   │   ├── test_productos_manager.py
│   │   │   ├── test_reportes_manager.py
│   │   │   └── test_reservas_manager.py
│   │   └── test_integration.py
│   ├── obras/
│   │   ├── test_model.py
│   │   ├── test_cronograma_view.py
│   │   └── test_components/
│   ├── compras/
│   │   ├── test_model.py
│   │   ├── test_proveedores_model.py
│   │   └── test_inventory_integration.py
│   ├── pedidos/
│   │   ├── test_model.py
│   │   └── test_workflows.py
│   ├── vidrios/
│   │   ├── test_model.py
│   │   └── test_submodules/
│   ├── notificaciones/
│   │   ├── test_model.py
│   │   └── test_controller.py
│   └── usuarios/
│       ├── test_auth.py
│       ├── test_permisos.py
│       └── test_sesiones.py
├── integration/                   # Tests de integración
│   ├── test_configuracion_persistence.py
│   ├── test_inventario_obras_integration.py
│   ├── test_compras_inventario_sync.py
│   ├── test_pedidos_obras_workflow.py
│   └── test_database_real.py
├── e2e/                          # Tests end-to-end
│   ├── test_workflows_completos.py
│   ├── test_inter_modulos.py
│   └── test_business_scenarios.py
├── ui/                           # Tests de interfaz
│   ├── test_login_ui.py
│   ├── test_accessibility.py
│   ├── test_ui_interactions.py
│   └── test_form_validations.py
├── performance/                  # Tests de performance
│   ├── test_database_performance.py
│   ├── test_ui_responsiveness.py
│   └── test_memory_usage.py
├── security/                     # Tests de seguridad
│   ├── test_authentication.py
│   ├── test_authorization.py
│   ├── test_sql_injection.py
│   └── test_data_validation.py
├── fixtures/                     # Datos de prueba
│   ├── sample_data.py
│   ├── mock_databases.py
│   └── test_configurations.py
├── utils/                        # Utilidades de testing
│   ├── test_helpers.py
│   ├── mock_factories.py
│   └── assertion_helpers.py
├── runners/                      # Scripts de ejecución
│   ├── run_all_tests.py
│   ├── run_by_module.py
│   ├── run_smoke_tests.py
│   └── generate_reports.py
└── conftest.py                   # Configuración global pytest
```

## 🎯 Convenciones de Naming

### Archivos de Test
- **Unit Tests:** `test_[component].py`
- **Integration:** `test_[module1]_[module2]_integration.py`
- **E2E:** `test_[workflow_name]_e2e.py`
- **UI:** `test_[view_name]_ui.py`
- **Performance:** `test_[feature]_performance.py`

### Funciones de Test
- **Funcionalidad básica:** `test_[action]_[expected_result]()`
- **Casos límite:** `test_[action]_[edge_case]_[result]()`
- **Errores:** `test_[action]_[error_condition]_raises_[exception]()`
- **Integración:** `test_[module1]_integrates_with_[module2]()`

## ⚙️ Configuración de Testing

### pytest.ini
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --strict-markers
    --disable-warnings
    --cov=rexus
    --cov-report=html
    --cov-report=term
    --durations=10
markers =
    unit: Unit tests
    integration: Integration tests  
    e2e: End-to-end tests
    ui: UI tests
    performance: Performance tests
    security: Security tests
    slow: Tests that take longer than usual
    database: Tests that require database
    external: Tests that require external resources
```

### Fixtures Globales (conftest.py)
- `mock_database`: Mock de base de datos
- `test_user`: Usuario de prueba
- `auth_bypass`: Bypass de autenticación para tests
- `sample_data`: Datos de muestra para tests
- `temp_files`: Archivos temporales para tests

## 🔧 Herramientas de Testing

### Framework Principal
- **pytest**: Framework de testing principal
- **pytest-qt**: Testing de interfaces PyQt6
- **pytest-mock**: Mocking avanzado
- **pytest-cov**: Cobertura de código
- **pytest-xdist**: Ejecución paralela

### Utilidades Adicionales
- **factory_boy**: Generación de datos de prueba
- **freezegun**: Manipulación de tiempo en tests
- **responses**: Mocking de HTTP requests
- **SQLAlchemy-Utils**: Utilidades para testing de BD

## 📊 Métricas de Calidad

### Objetivos de Cobertura
- **Módulos críticos:** ≥ 90%
- **Módulos estándar:** ≥ 80%
- **Utilidades:** ≥ 85%
- **UI básica:** ≥ 70%

### KPIs de Testing
- **Tiempo ejecución completa:** < 10 minutos
- **Tests unitarios:** < 2 minutos
- **Tests de integración:** < 5 minutos
- **Tests E2E:** < 8 minutos

## 🚀 Scripts de Ejecución

### Comandos Frecuentes
```bash
# Tests completos
pytest tests/

# Por módulo específico
pytest tests/unit/inventario/

# Solo tests rápidos
pytest -m "not slow"

# Con cobertura
pytest --cov=rexus --cov-report=html

# Tests específicos
pytest tests/unit/configuracion/test_model.py::test_crear_configuracion

# Tests paralelos
pytest -n auto

# Solo tests fallidos anteriormente
pytest --lf

# Tests modificados
pytest --testmon
```

## 📋 Estado Actual del Testing (21/08/2025)

### Completado ✅
- Sistema de autenticación bypass global
- Tests básicos para módulos principales
- Configuración UTF-8 para compatibilidad
- Correcciones críticas de mocks

### Pendiente ⚠️
- Reorganización en estructura por carpetas
- Tests de reportes de inventario
- Corrección de tests FAILED → PASSED
- Optimización de tests lentos (>30s)

### Próximos Pasos 🎯
1. **Migrar tests actuales** a nueva estructura de carpetas
2. **Crear tests faltantes** para funcionalidades sin cobertura
3. **Optimizar performance** de tests lentos
4. **Automatizar ejecución** en CI/CD

---

## 📝 Notas para Claude

### Contexto del Proyecto
- Sistema empresarial complejo con múltiples módulos interconectados
- Arquitectura MVC con PyQt6 para UI
- Base de datos híbrida (SQLite desarrollo, SQL Server producción)
- ~13,763 líneas de tests implementadas
- 140+ errores identificados que requieren corrección

### Comandos de Testing Específicos
```bash
# Ejecutar tests por prioridad
python tests/runners/run_smoke_tests.py     # Tests críticos
python tests/runners/run_by_module.py inventario  # Módulo específico
python tests/runners/run_all_tests.py      # Suite completa

# Debugging tests específicos
pytest tests/unit/inventario/test_model.py::test_crear_producto -v -s

# Tests con timeout extendido
pytest tests/e2e/ --timeout=300

# Solo tests que fallan actualmente
pytest --tb=short --maxfail=5
```

### Patrones de Implementación
- Usar `@pytest.fixture` para datos de prueba reutilizables
- Implementar `setUp`/`tearDown` para limpieza de BD
- Mock de conexiones externas (BD, APIs)
- Configurar encoding UTF-8 al inicio de cada test
- Usar `unittest.mock.patch` para aislar componentes