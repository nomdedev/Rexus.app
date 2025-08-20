# Auditoría de Cobertura de Tests - Rexus.app

Fecha: 20/08/2025

Este documento detalla los faltantes y oportunidades de mejora en la cobertura de tests del proyecto, identificando áreas críticas sin pruebas suficientes o sin pruebas automatizadas de calidad.

---

## 1. Formularios y Vistas de Usuario (UI)

### Cobertura Actual:
- Se testean vistas principales como `ObrasModernView` e `InventarioView` para inicialización y existencia de componentes críticos (tablas, pestañas, widgets).
- Hay un test automatizado de contraste y estilos visuales (`contrast_test.py`).

### Faltantes:
- **No hay tests de interacción real de usuario:**
  - No se simula el llenado, envío y validación de formularios desde la UI.
  - No se prueban flujos completos de usuario (input, submit, feedback visual).
- **No se cubren todos los formularios secundarios:**
  - Faltan tests para formularios de módulos como Compras, Pedidos, Vidrios, Notificaciones, etc.
- **No hay pruebas de accesibilidad profunda:**
  - Navegación por teclado, focus, etiquetas, roles accesibles.
- **No se usan herramientas de automatización UI (pytest-qt, qtbot, Selenium).**
- **No se testean mensajes de error visuales ni validaciones negativas.**

---

## 2. Validadores de Formularios

### Cobertura Actual:
- Se testean validadores de campos obligatorios, emails, teléfonos, números y longitud de texto (`FormValidator`).

### Faltantes:
- **No se testean validadores personalizados de cada módulo.**
- **No se cubren todos los escenarios límite (inputs inválidos, edge cases complejos).**
- **No se verifica la integración de validadores con la UI (feedback visual).**

---

## 3. Integración y Módulos Críticos

### Cobertura Actual:
- Tests de inicialización de vistas y mocks de conexiones a base de datos.
- Validación de disponibilidad de módulos y métodos críticos.

### Faltantes:
- **No hay tests de integración de extremo a extremo (E2E) que recorran todo el flujo de usuario.**
- **No se testean errores de conexión, caídas de servicios o recuperación ante fallos.**
- **No se cubren todos los módulos secundarios (ej: Notificaciones, Configuración, etc.).**

---

## 4. Accesibilidad y Experiencia de Usuario

### Cobertura Actual:
- Test de contraste y estilos visuales.

### Faltantes:
- **No hay tests de accesibilidad automatizados (a11y).**
- **No se verifica la usabilidad para usuarios con discapacidad.**
- **No se testean atajos de teclado, navegación por tabulación, ni lectores de pantalla.**

---

## 5. Recomendaciones Generales

- Implementar tests de interacción de usuario con herramientas como `pytest-qt`, `qtbot` o Selenium.
- Cubrir todos los formularios y vistas, incluyendo secundarios y modales.
- Agregar tests de validación negativa y feedback visual de errores.
- Incluir pruebas de accesibilidad automatizadas.
- Documentar los criterios de aceptación de cada test y mantener checklist de cobertura.

---

**Este documento debe actualizarse tras cada ciclo de desarrollo y testing.**
