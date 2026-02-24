# Auditoría de Calidad de Código - Rexus.app

**Fecha:** 2026-02-24T14:32:02.481571
**Archivos analizados:** 259 / 259
**Líneas totales de código:** 99,405

---

## 📊 Resumen Ejecutivo

### Métricas Generales

- **Funciones totales:** 3,335
- **Clases totales:** 463
- **Cobertura de documentación:** 5.92%
- **Complejidad promedio:** 3.04
- **Comentarios:** 5.21% del código
- **Archivos con issues:** 204

---

## TOP 10 ARCHIVOS CON MAS PROBLEMAS

### 1. D:\martin\Proyectos\Rexus.app\rexus\modules\02_inventario\submodules\reportes_manager.py

- **Score de problemas:** 20
- **Cantidad de issues:** 6
- **Complejidad:** 127
- **Líneas:** 1106

**Tipos de problemas:**
- high_complexity: 5
- missing_module_docstring: 1

### 2. D:\martin\Proyectos\Rexus.app\rexus\modules\01_obras\validator_extended.py

- **Score de problemas:** 15
- **Cantidad de issues:** 5
- **Complejidad:** 92
- **Líneas:** 461

**Tipos de problemas:**
- high_complexity: 4
- missing_module_docstring: 1

### 3. D:\martin\Proyectos\Rexus.app\rexus\modules\01_obras\model.py

- **Score de problemas:** 14
- **Cantidad de issues:** 6
- **Complejidad:** 129
- **Líneas:** 802

**Tipos de problemas:**
- high_complexity: 5
- missing_module_docstring: 1

### 4. D:\martin\Proyectos\Rexus.app\rexus\monitoring\prometheus_exporter.py

- **Score de problemas:** 10
- **Cantidad de issues:** 1
- **Complejidad:** 0
- **Líneas:** 235

**Tipos de problemas:**
- syntax_error: 1

### 5. D:\martin\Proyectos\Rexus.app\rexus\utils\query_optimizer.py

- **Score de problemas:** 10
- **Cantidad de issues:** 1
- **Complejidad:** 0
- **Líneas:** 608

**Tipos de problemas:**
- syntax_error: 1

### 6. D:\martin\Proyectos\Rexus.app\rexus\utils\style_unifier.py

- **Score de problemas:** 10
- **Cantidad de issues:** 1
- **Complejidad:** 0
- **Líneas:** 248

**Tipos de problemas:**
- syntax_error: 1

### 7. D:\martin\Proyectos\Rexus.app\rexus\modules\03_herrajes\view.py

- **Score de problemas:** 10
- **Cantidad de issues:** 1
- **Complejidad:** 0
- **Líneas:** 1195

**Tipos de problemas:**
- syntax_error: 1

### 8. D:\martin\Proyectos\Rexus.app\rexus\modules\06_pedidos\improved_dialogs.py

- **Score de problemas:** 10
- **Cantidad de issues:** 1
- **Complejidad:** 0
- **Líneas:** 628

**Tipos de problemas:**
- syntax_error: 1

### 9. D:\martin\Proyectos\Rexus.app\rexus\modules\11_usuarios\improved_dialogs.py

- **Score de problemas:** 10
- **Cantidad de issues:** 1
- **Complejidad:** 0
- **Líneas:** 477

**Tipos de problemas:**
- syntax_error: 1

### 10. D:\martin\Proyectos\Rexus.app\rexus\modules\11_usuarios\model.py

- **Score de problemas:** 10
- **Cantidad de issues:** 1
- **Complejidad:** 0
- **Líneas:** 1688

**Tipos de problemas:**
- syntax_error: 1

---

## ANALISIS DE COMPLEJIDAD

### Funciones con Complejidad Muy Alta (>15)

- **_evaluate_condition** (17) en `D:\martin\Proyectos\Rexus.app\rexus\core\business_rules.py`
- **get_connection** (16) en `D:\martin\Proyectos\Rexus.app\rexus\core\database_pool.py`
- **main** (30) en `D:\martin\Proyectos\Rexus.app\rexus\main\app.py`
- **validate** (28) en `D:\martin\Proyectos\Rexus.app\rexus\security\password_policy.py`
- **add_form_group** (18) en `D:\martin\Proyectos\Rexus.app\rexus\utils\dialog_utils.py`
- **format_relative_date** (17) en `D:\martin\Proyectos\Rexus.app\rexus\utils\format_utils.py`
- **_validate_by_type** (20) en `D:\martin\Proyectos\Rexus.app\rexus\utils\input_validator.py`
- **validar_datos_obra** (16) en `D:\martin\Proyectos\Rexus.app\rexus\modules\01_obras\controller.py`
- **crear_obra** (20) en `D:\martin\Proyectos\Rexus.app\rexus\modules\01_obras\model.py`
- **_validar_formatos** (23) en `D:\martin\Proyectos\Rexus.app\rexus\modules\01_obras\validator_extended.py`

**Total funciones de alta complejidad:** 87

---

## COBERTURA DE DOCUMENTACION

- **Cobertura en funciones:** 85.55%
- **Cobertura en clases:** 87.26%
- **Funciones documentadas:** 2,853 / 3,335
- **Clases documentadas:** 404 / 463

---

## RECOMENDACIONES PRIORIZADAS

### [ALTA] 1. Documentation (Prioridad: high)

**Problema:** Baja cobertura de documentación (5.92%)

**Recomendación:** Añadir docstrings a todas las funciones y clases públicas siguiendo el estilo de Google o NumPy

**Impacto:** Mejora la mantenibilidad y facilita la colaboración

---

### [ALTA] 2. Testing (Prioridad: high)

**Problema:** Cobertura de pruebas no evaluada

**Recomendación:** Implementar pytest con mínimo 70% de cobertura

**Impacto:** Previene regresiones y mejora la calidad

---

### [ALTA] 3. Error Handling (Prioridad: high)

**Problema:** Manejo de errores inconsistente

**Recomendación:** Implementar manejo de errores centralizado y logging estructurado

**Impacto:** Mejora la robustez y facilita el debugging

---

### [MEDIA] 4. Comments (Prioridad: medium)

**Problema:** Baja proporción de comentarios (5.21%)

**Recomendación:** Añadir comentarios explicativos en lógica compleja y algoritmos

**Impacto:** Facilita la comprensión del código

---

### [MEDIA] 5. Type Safety (Prioridad: medium)

**Problema:** Falta de type hints

**Recomendación:** Añadir type hints a todas las funciones según PEP 484

**Impacto:** Mejora la documentación y permite verificación estática con mypy

---

### [MEDIA] 6. Organization (Prioridad: medium)

**Problema:** Posible duplicación de código

**Recomendación:** Extraer lógica común a utilidades reutilizables

**Impacto:** Reduce la duplicación y mejora la consistencia

---

---

## MODULOS MAS GRANDES

- **utils:** 17,675 líneas
- **core:** 9,762 líneas
- **modules\01_obras:** 5,132 líneas
- **modules\02_inventario\submodules:** 4,629 líneas
- **modules\11_usuarios:** 4,579 líneas


---

## CODIGO DUPLICADO

Se detectaron **20** bloques de codigo potencialmente duplicados.

---

## PROXIMOS PASOS SUGERIDOS

1. **Atender problemas críticos** en los archivos identificados
2. **Mejorar documentación** hasta alcanzar >80% de cobertura
3. **Refactorizar funciones complejas** para reducir complejidad ciclomática
4. **Implementar testing** con mínimo 70% de cobertura
5. **Establecer linting** automático (flake8, black, mypy)
6. **Configurar pre-commit hooks** para mantener calidad
7. **Documentar arquitectura** y patrones de diseño

---

*Reporte generado automáticamente por el script de auditoría de Rexus.app*
