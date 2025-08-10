# Estándares y Arquitectura de Testing para Rexus.app

## 🎯 Objetivos del Sistema de Testing

### 1. **Cobertura Completa**
- **Unitarios**: Lógica de negocio y funciones individuales
- **Integración**: Interacción entre componentes
- **UI**: Interfaz de usuario y workflows
- **E2E**: Flujos completos de usuario
- **Performance**: Rendimiento y escalabilidad
- **Seguridad**: Validación de vulnerabilidades

### 2. **Calidad y Mantenibilidad**
- Tests atómicos y determinísticos
- Documentación clara y completa
- Fixtures reutilizables
- Mocks apropiados para dependencias externas
- Assertions específicas y descriptivas

---

## 📁 Estructura Organizacional

### **Nivel 1: Por Tipo de Test**
```
tests/
├── unit/           # Tests unitarios (lógica pura)
├── integration/    # Tests de integración 
├── ui/            # Tests de interfaz de usuario
├── e2e/           # Tests end-to-end
├── performance/   # Tests de rendimiento
├── security/      # Tests de seguridad
└── fixtures/      # Datos y utilidades compartidas
```

### **Nivel 2: Por Módulo**
```
tests/unit/
├── core/          # Core del sistema (auth, db, etc.)
├── modules/       # Módulos de negocio
│   ├── inventario/
│   ├── obras/
│   ├── logistica/
│   ├── usuarios/
│   ├── administracion/
│   └── ...
└── utils/         # Utilidades y helpers
```

### **Nivel 3: Por Componente**
```
tests/unit/modules/inventario/
├── test_model.py      # Tests del modelo
├── test_view.py       # Tests de la vista
├── test_controller.py # Tests del controlador
└── test_utils.py      # Tests de utilidades específicas
```

---

## 🏗️ Arquitectura de Tests

### **Nomenclatura Estándar**
- **Archivos**: `test_[componente].py`
- **Clases**: `Test[ComponenteName]`
- **Métodos**: `test_[accion]_[escenario]_[resultado_esperado]`

**Ejemplos:**
```python
def test_crear_producto_con_datos_validos_retorna_exito()
def test_crear_producto_con_codigo_duplicado_retorna_error()
def test_buscar_productos_sin_filtros_retorna_todos()
```

### **Estructura de Test Individual**
```python
def test_nombre_descriptivo():
    """
    Descripción del test:
    - Qué funcionalidad se está probando
    - Qué escenario específico
    - Qué resultado se espera
    """
    # ARRANGE: Preparar datos y estado inicial
    datos = {"codigo": "PROD001", "nombre": "Test"}
    
    # ACT: Ejecutar la acción
    resultado = modelo.crear_producto(datos)
    
    # ASSERT: Verificar el resultado
    assert resultado.exito is True
    assert resultado.mensaje == "Producto creado exitosamente"
```

---

## 📋 Checklist de Calidad de Tests

### ✅ **Criterios Obligatorios**

#### **1. Funcionalidad**
- [ ] El test verifica una funcionalidad específica
- [ ] Cubre casos positivos y negativos
- [ ] Incluye validación de edge cases
- [ ] Maneja excepciones apropiadamente

#### **2. Independencia**
- [ ] No depende de otros tests
- [ ] No modifica estado global permanente
- [ ] Usa fixtures para datos de prueba
- [ ] Se puede ejecutar en cualquier orden

#### **3. Determinismo**
- [ ] Produce el mismo resultado en cada ejecución
- [ ] No depende de factores externos variables
- [ ] Usa mocks para servicios externos
- [ ] Controla el tiempo y aleatoriedad

#### **4. Velocidad**
- [ ] Se ejecuta rápidamente (< 1 segundo unitarios)
- [ ] Minimiza I/O y operaciones costosas
- [ ] Usa mocks para bases de datos
- [ ] Evita sleeps y waits innecesarios

#### **5. Legibilidad**
- [ ] Nombre descriptivo y claro
- [ ] Documentación explicativa
- [ ] Estructura AAA (Arrange-Act-Assert)
- [ ] Assertions específicas y descriptivas

#### **6. Mantenibilidad**
- [ ] Usa fixtures reutilizables
- [ ] Evita duplicación de código
- [ ] Sigue convenciones del proyecto
- [ ] Es fácil de modificar y extender

---

## 🎨 Patrones y Mejores Prácticas

### **1. Fixtures Estratégicas**
```python
@pytest.fixture(scope="function")
def producto_valido():
    """Producto con datos válidos para tests."""
    return {
        'codigo': 'PROD001',
        'nombre': 'Producto Test',
        'precio': 100.00
    }

@pytest.fixture(scope="function") 
def modelo_con_mock_db(mock_db):
    """Modelo de inventario con base de datos mockeada."""
    return InventarioModel(mock_db)
```

### **2. Tests Parametrizados**
```python
@pytest.mark.parametrize("codigo,nombre,esperado", [
    ("", "Producto", False),           # Código vacío
    ("PROD001", "", False),            # Nombre vacío  
    ("PROD001", "Producto", True),     # Datos válidos
])
def test_validar_producto(codigo, nombre, esperado):
    resultado = validar_producto(codigo, nombre)
    assert resultado == esperado
```

### **3. Mocks Específicos**
```python
def test_crear_producto_error_db(modelo_con_mock_db):
    # Simular error de base de datos
    modelo_con_mock_db.db.cursor().execute.side_effect = Exception("Error DB")
    
    resultado = modelo_con_mock_db.crear_producto({"codigo": "PROD001"})
    
    assert resultado.exito is False
    assert "Error DB" in resultado.mensaje
```

### **4. Tests de UI**
```python
def test_boton_guardar_habilita_con_datos_validos(qapp):
    """Test que el botón se habilita con datos válidos."""
    dialog = ProductoDialog()
    
    # Llenar campos con datos válidos
    dialog.input_codigo.setText("PROD001")
    dialog.input_nombre.setText("Producto Test")
    
    # Verificar que el botón se habilitó
    assert dialog.btn_guardar.isEnabled() is True
```

---

## 📊 Métricas y Reportes

### **Cobertura Mínima por Tipo**
- **Unitarios**: 90%+ de cobertura de código
- **Integración**: 80%+ de flujos principales
- **UI**: 70%+ de componentes críticos
- **E2E**: 100% de workflows principales

### **Criterios de Aceptación**
- ✅ Todos los tests pasan
- ✅ Cobertura >= 85% total
- ✅ No hay tests skipeados sin justificación
- ✅ Tiempo total < 5 minutos para suite completa
- ✅ No hay warnings o deprecations

---

## 🔧 Herramientas y Configuración

### **pytest.ini**
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short --strict-markers
markers =
    unit: Tests unitarios
    integration: Tests de integración  
    ui: Tests de interfaz de usuario
    slow: Tests que toman más tiempo
    skip_ci: Tests que se saltan en CI
```

### **Comandos Útiles**
```bash
# Ejecutar todos los tests
pytest

# Solo tests unitarios
pytest -m unit

# Con cobertura
pytest --cov=rexus --cov-report=html

# Tests específicos
pytest tests/unit/modules/inventario/

# Con profiling
pytest --profile
```

---

## 📝 Documentación de Tests

Cada archivo de test debe incluir:

```python
"""
Tests para [Componente/Módulo]

Descripción:
    Tests que validan [funcionalidad principal]

Scope:
    - Funcionalidades cubiertas
    - Edge cases considerados
    - Limitaciones conocidas

Dependencies:
    - Fixtures requeridas
    - Mocks utilizados
    - Configuración especial

Author: [Nombre]
Date: [Fecha]
Version: [Version]
"""
```

---

Esta arquitectura asegura tests robustos, mantenibles y que agreguen valor real al desarrollo del sistema Rexus.app.
