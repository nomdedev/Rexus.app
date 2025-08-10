# Checklist de Calidad para Tests

## ✅ Verificación Pre-Commit

### **Estructura y Nomenclatura**
- [ ] El archivo sigue el patrón `test_*.py`
- [ ] Las clases usan el patrón `Test*`
- [ ] Los métodos usan el patrón `test_*_*_*` (acción_escenario_resultado)
- [ ] Está en la carpeta correcta según el tipo de test

### **Documentación**
- [ ] Cada archivo tiene docstring descriptivo
- [ ] Cada clase de test tiene docstring con scope y dependencies
- [ ] Al menos 80% de los métodos de test tienen docstring
- [ ] Los docstrings explican qué, por qué y cómo

### **Estructura del Test**
- [ ] Sigue patrón AAA (Arrange-Act-Assert) o Given-When-Then
- [ ] Cada test verifica una sola funcionalidad
- [ ] Los tests son independientes (no dependen de orden)
- [ ] No hay estado compartido entre tests

### **Assertions y Validaciones**
- [ ] Todos los tests tienen al menos una assertion
- [ ] Las assertions son específicas y descriptivas
- [ ] No hay assertions genéricas como `assert True`
- [ ] Se validan tanto casos positivos como negativos

### **Fixtures y Mocks**
- [ ] Usa fixtures de pytest en lugar de setUp/tearDown
- [ ] Los mocks están correctamente configurados
- [ ] Las dependencias externas están mockeadas
- [ ] Los datos de prueba son realistas pero seguros

### **Performance y Eficiencia**
- [ ] Tests unitarios se ejecutan en < 1 segundo
- [ ] No hay sleeps o waits innecesarios
- [ ] Se minimizan las operaciones de I/O
- [ ] Se usan mocks para operaciones costosas

### **Manejo de Errores**
- [ ] Se prueban casos de error y excepciones
- [ ] Se valida el manejo correcto de datos inválidos
- [ ] Se verifican los mensajes de error
- [ ] Se cubren edge cases y valores límite

### **Imports y Dependencias**
- [ ] Solo se importa lo necesario
- [ ] No hay imports problemáticos (time.sleep, random, etc.)
- [ ] Se usa pytest como framework principal
- [ ] Las dependencias están disponibles en el entorno de test

---

## 🎯 Criterios de Aceptación

### **Score Mínimo: 80/100**
Para que un test sea aceptado debe obtener al menos 80 puntos en la auditoría automática.

### **Criterios Obligatorios (Score = 0 si falla)**
- ✅ Sin errores de sintaxis
- ✅ Al menos una assertion por test
- ✅ Nomenclatura correcta
- ✅ No hay imports problemáticos

### **Criterios de Calidad (Bonificación)**
- ✅ +10 pts: >80% de tests documentados
- ✅ +10 pts: 100% de tests con assertions válidas
- ✅ +5 pts: Usa fixtures de pytest
- ✅ +5 pts: Estructura AAA clara
- ✅ +5 pts: Cubre casos negativos

### **Penalizaciones**
- ❌ -20 pts: Por cada error crítico
- ❌ -5 pts: Por cada warning
- ❌ -10 pts: Tests sin documentación
- ❌ -15 pts: Assertions débiles o genéricas

---

## 📋 Review Checklist

### **Antes de escribir el test:**
1. [ ] ¿Qué funcionalidad específica estoy probando?
2. [ ] ¿Qué casos positivos y negativos debo cubrir?
3. [ ] ¿Qué dependencias necesito mockear?
4. [ ] ¿En qué categoría va este test? (unit/integration/ui/e2e)

### **Durante el desarrollo:**
1. [ ] ¿El test es fácil de leer y entender?
2. [ ] ¿Las assertions son específicas?
3. [ ] ¿Estoy probando comportamiento, no implementación?
4. [ ] ¿El test fallará por las razones correctas?

### **Antes del commit:**
1. [ ] ¿El test pasa consistentemente?
2. [ ] ¿No interfiere con otros tests?
3. [ ] ¿La documentación está completa?
4. [ ] ¿Ejecuté el auditor de calidad?

---

## 🚀 Comandos de Verificación

```bash
# Ejecutar auditor de calidad
python tests/fixtures/test_auditor.py

# Ejecutar tests específicos
pytest tests/unit/modules/inventario/ -v

# Verificar cobertura
pytest --cov=rexus tests/ --cov-report=html

# Solo tests rápidos
pytest -m "not slow" tests/

# Verificar performance
pytest --durations=10 tests/
```

---

## 📊 Métricas de Calidad

### **Por Archivo**
- Score: X/100
- Documentación: X%
- Assertions válidas: X%
- Tiempo promedio: X ms
- Último audit: fecha

### **Por Módulo**
- Total tests: X
- Score promedio: X/100
- Cobertura: X%
- Tests fallidos: X

### **Global**
- Tests totales: X
- Score promedio: X/100
- Cobertura global: X%
- Tiempo total suite: X min

---

Usar este checklist antes de cada commit para mantener la calidad alta y consistente en toda la suite de tests.
