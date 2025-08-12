# 🧪 Estándares de Testing - Rexus.app

**Versión**: 2.0.0  
**Última actualización**: 2025-08-12  
**Estado**: ✅ Implementado y Validado

---

## 📋 Resumen Ejecutivo

Este documento establece los estándares de testing para el proyecto Rexus.app, basado en la experiencia adquirida durante la corrección de errores críticos y la implementación de tests para módulos principales.

### 🎯 **Objetivos de Testing**

1. **Prevenir regresiones** en funcionalidad crítica
2. **Validar cambios de UI/UX** sin romper usabilidad
3. **Asegurar calidad** de código en módulos de negocio
4. **Facilitar refactoring** con confianza
5. **Documentar comportamiento esperado** del sistema

---

## 🏗️ Estructura de Tests

### Directorio Base: `tests/`

```
tests/
├── conftest.py                 # Fixtures globales y configuración
├── pytest.ini                 # Configuración de pytest
├── unit/                       # Tests unitarios
│   ├── core/                  # Tests de sistema core
│   ├── security/              # Tests de seguridad
│   ├── utils/                 # Tests de utilidades
│   ├── modules/               # Tests de módulos de negocio
│   └── ui/                    # Tests de interfaz de usuario
├── integration/               # Tests de integración (futuro)
└── fixtures/                  # Fixtures compartidas
```

### 📦 **Tests por Módulo**

Cada módulo de negocio debe tener:

```
tests/unit/modules/test_{modulo}.py
├── Test{Modulo}Model          # Tests del modelo
├── Test{Modulo}View           # Tests de la vista  
├── Test{Modulo}Controller     # Tests del controlador
├── Test{Modulo}Integration    # Tests de integración interna
├── Test{Modulo}Security       # Tests de seguridad específicos
└── Test{Modulo}Performance    # Tests de rendimiento
```

---

## 🎯 Categorías de Tests

### 1. **Tests de Modelo** (Críticos)

```python
class TestInventarioModel:
    def test_model_initialization(self, mock_db_connection):
        """Test inicialización del modelo."""
        
    def test_crud_operations(self, sample_data):
        """Test operaciones CRUD básicas."""
        
    def test_data_validation(self, invalid_data_samples):
        """Test validación de datos."""
        
    def test_error_handling(self):
        """Test manejo de errores."""
```

**Requisitos**:
- ✅ Usar mocks para base de datos
- ✅ Probar con datos válidos e inválidos
- ✅ Verificar manejo de excepciones
- ✅ Validar sanitización de entrada

### 2. **Tests de Vista** (UI/UX)

```python
class TestInventarioView:
    def test_view_initialization(self, qapp):
        """Test inicialización de vista."""
        
    def test_style_application(self, qapp):
        """Test aplicación de estilos."""
        
    def test_responsive_layout(self, qapp):
        """Test layout responsivo."""
        
    def test_user_interactions(self, qapp):
        """Test interacciones de usuario."""
```

**Requisitos**:
- ✅ Usar fixture `qapp` para QApplication
- ✅ Validar aplicación de estilos
- ✅ Verificar layouts compactos/responsivos
- ✅ Probar señales y slots

### 3. **Tests de Controlador** (Lógica)

```python
class TestInventarioController:
    def test_controller_initialization(self):
        """Test inicialización del controlador."""
        
    def test_model_view_coordination(self):
        """Test coordinación modelo-vista."""
        
    def test_business_logic(self):
        """Test lógica de negocio."""
```

**Requisitos**:
- ✅ Mockear dependencias
- ✅ Probar coordinación entre componentes
- ✅ Validar flujos de trabajo

### 4. **Tests de Seguridad** (Críticos)

```python
class TestModuloSecurity:
    def test_sql_injection_prevention(self):
        """Test prevención de SQL injection."""
        
    def test_input_sanitization(self):
        """Test sanitización de entrada."""
        
    def test_xss_protection(self):
        """Test protección XSS."""
        
    def test_authentication_required(self):
        """Test autenticación requerida."""
```

### 5. **Tests de Rendimiento** (Marcados)

```python
class TestModuloPerformance:
    @pytest.mark.performance
    def test_initialization_performance(self, performance_timer):
        """Test rendimiento de inicialización."""
        with performance_timer() as timer:
            # Operación a medir
            pass
        assert timer.elapsed < 2.0  # Umbral razonable
```

---

## 🛠️ Fixtures Estándar

### Fixtures Obligatorias (conftest.py)

```python
@pytest.fixture(scope="session", autouse=True)
def qapp():
    """QApplication para tests de UI."""
    
@pytest.fixture(scope="function")
def mock_db_connection():
    """Mock de conexión a base de datos."""
    
@pytest.fixture(scope="function")
def sample_user_data():
    """Datos de usuario válidos."""
    
@pytest.fixture(scope="function")
def invalid_data_samples():
    """Datos inválidos para tests negativos."""
    
@pytest.fixture(scope="session")
def test_database_path(tmp_path_factory):
    """Base de datos temporal para tests."""
    
@pytest.fixture(scope="function")
def performance_timer():
    """Timer para medir rendimiento."""
```

### Fixtures por Módulo

Cada módulo puede tener fixtures específicas:

```python
@pytest.fixture(scope="function")
def sample_inventario_data():
    """Datos específicos de inventario."""
    
@pytest.fixture(scope="function")
def mock_inventario_model():
    """Mock específico del modelo."""
```

---

## ✅ Criterios de Calidad

### Cobertura Mínima por Módulo

- **Modelo**: 80%+ de cobertura de métodos públicos
- **Vista**: 60%+ de métodos críticos (init, setup_ui, apply_theme)
- **Controlador**: 70%+ de lógica de negocio
- **Seguridad**: 100% de funciones críticas

### Tipos de Tests Requeridos

#### ✅ **Tests Obligatorios**
- Import y inicialización básica
- Funcionalidad CRUD principal
- Manejo de errores críticos
- Aplicación de estilos (si aplica)
- Validación de entrada

#### 🟡 **Tests Recomendados**
- Rendimiento de operaciones críticas
- Integración entre componentes
- Tests parametrizados para datos
- Edge cases y boundary conditions

#### 🔵 **Tests Opcionales**
- Tests de UI automatizados
- Tests de carga/stress
- Tests de compatibilidad
- Tests de accesibilidad

---

## 🚀 Comandos de Testing

### Ejecución Básica

```bash
# Todos los tests
cd tests && python -m pytest

# Tests de un módulo específico
cd tests && python -m pytest unit/modules/test_inventario.py -v

# Tests de UI solamente
cd tests && python -m pytest unit/ui/ -v

# Tests de rendimiento
cd tests && python -m pytest -m performance

# Tests con cobertura
cd tests && python -m pytest --cov=rexus --cov-report=html
```

### Ejecución Avanzada

```bash
# Tests con timeout
cd tests && python -m pytest --timeout=30

# Tests paralelos
cd tests && python -m pytest -n 4

# Tests específicos con patrón
cd tests && python -m pytest -k "test_style" -v

# Tests con reporte JUnit
cd tests && python -m pytest --junitxml=reports/junit.xml
```

---

## 🎨 Estándares de Estilos en Tests

### Naming Conventions

```python
# Clases de test
class TestModuleNameComponent:  # PascalCase
    
# Métodos de test  
def test_feature_description(self):  # snake_case
    
# Fixtures
@pytest.fixture
def sample_module_data():  # snake_case descriptivo
```

### Estructura de Test Estándar

```python
def test_feature_description(self, fixtures):
    """
    Descripción clara de qué se está probando.
    
    Validates:
    - Comportamiento específico A
    - Comportamiento específico B
    - Manejo de error X
    """
    # ARRANGE - Preparar datos y mocks
    test_data = {"key": "value"}
    
    # ACT - Ejecutar la funcionalidad
    result = function_under_test(test_data)
    
    # ASSERT - Verificar resultados
    assert result is not None
    assert result.property == expected_value
```

### Skip y Fallback Patterns

```python
def test_complex_feature(self):
    try:
        from complex_module import ComplexClass
        instance = ComplexClass()
        # Test logic here
    except ImportError as e:
        pytest.skip(f"Module not available: {e}")
    except Exception as e:
        pytest.skip(f"Test cannot run: {e}")
```

---

## 🔧 Configuración de Pytest

### pytest.ini

```ini
[tool:pytest]
testpaths = .
python_files = test_*.py *_test.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --strict-markers
    --disable-warnings
markers =
    performance: marks tests as performance tests
    slow: marks tests as slow running
    integration: marks tests as integration tests
    ui: marks tests as UI tests
    security: marks tests as security tests
```

---

## 📊 Métricas y Reportes

### Métricas de Calidad

- **Test Success Rate**: >95%
- **Test Coverage**: >70% global
- **Test Execution Time**: <5min suite completa
- **Flaky Test Rate**: <2%

### Reportes Automáticos

```bash
# Generar reporte de cobertura HTML
cd tests && python -m pytest --cov=rexus --cov-report=html

# Generar reporte XML para CI/CD
cd tests && python -m pytest --junitxml=reports/junit.xml

# Reporte de rendimiento
cd tests && python -m pytest -m performance --benchmark-save=performance
```

---

## 🚨 Casos Críticos a Probar

### 1. **Regresiones de Estilos**

```python
def test_no_oversized_elements(self, qapp):
    """Prevenir elementos UI excesivamente grandes."""
    
def test_compact_layout_maintained(self, qapp):
    """Verificar que layouts siguen siendo compactos."""
```

### 2. **Errores de Conexión DB**

```python
def test_handles_none_connection(self):
    """Manejar conexión DB nula gracefully."""
    
def test_cursor_access_pattern(self):
    """Verificar patrón correcto: db.connection.cursor()."""
```

### 3. **Imports y Dependencies**

```python
def test_all_imports_available(self):
    """Verificar que imports críticos funcionan."""
    
def test_fallback_when_optional_missing(self):
    """Verificar fallbacks para dependencias opcionales."""
```

---

## 🎯 Roadmap de Testing

### Fase 1: Completado ✅
- [x] Corrección de fixtures básicas
- [x] Tests para módulos críticos (logística, usuarios, inventario)
- [x] Validación de cambios de estilos
- [x] Tests de regresión básicos

### Fase 2: En Progreso 🔄
- [x] Documentación de estándares
- [ ] Tests para módulos restantes (obras, compras, etc.)
- [ ] Tests de integración entre módulos
- [ ] Configuración de CI/CD con tests

### Fase 3: Futuro 🔮
- [ ] Tests de performance automatizados
- [ ] Tests de UI end-to-end
- [ ] Tests de carga y stress
- [ ] Tests de accesibilidad

---

## 📚 Referencias y Recursos

### Documentación
- [Pytest Documentation](https://docs.pytest.org)
- [PyQt6 Testing Guide](https://doc.qt.io/qtforpython-6/tutorials/index.html)
- [Python Testing Best Practices](https://python-testing-best-practices.readthedocs.io)

### Tools y Libraries
- `pytest`: Framework principal
- `pytest-qt`: Tests de PyQt6
- `pytest-cov`: Cobertura de código
- `pytest-mock`: Mocking avanzado
- `pytest-timeout`: Timeouts para tests
- `pytest-xdist`: Ejecución paralela

---

## ✅ Checklist para Nuevos Tests

Antes de crear tests para un nuevo módulo:

- [ ] Verificar que existe estructura base del módulo
- [ ] Crear fixtures específicas si es necesario
- [ ] Implementar tests de importación básica
- [ ] Agregar tests de inicialización
- [ ] Incluir tests de funcionalidad crítica
- [ ] Agregar tests de manejo de errores
- [ ] Validar estilos/UI si aplica
- [ ] Documentar casos especiales
- [ ] Ejecutar tests localmente
- [ ] Verificar cobertura mínima

---

**Este documento es la guía definitiva para testing en Rexus.app. Debe actualizarse con cada cambio significativo en la arquitectura de tests.**