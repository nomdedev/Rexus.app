# Checklist de Auditoría de Tests por Módulo - Rexus.app

Fecha: 20/08/2025

Este checklist debe aplicarse a cada módulo del sistema para asegurar una cobertura de tests profesional, relevante y alineada con el comportamiento real del sistema.

---

## Plantilla de Auditoría por Módulo

### 1. Cobertura de Tests de UI/Frontend
- [ ] ¿Existen tests para la inicialización de la vista principal del módulo?
- [ ] ¿Se testean todos los formularios y componentes visuales relevantes?
- [ ] ¿Se simulan flujos de usuario (llenado, envío, feedback visual)?
- [ ] ¿Se testean mensajes de error y validaciones negativas?
- [ ] ¿Se cubre la accesibilidad (contraste, navegación por teclado, focus)?
- [ ] ¿Se usan herramientas de automatización UI (pytest-qt, qtbot, Selenium)?

### 2. Cobertura de Tests de Backend/Lógica
- [ ] ¿Se testean los métodos principales de negocio del módulo?
- [ ] ¿Se cubren validaciones, persistencia y manejo de errores?
- [ ] ¿Se prueban casos límite y entradas inválidas?
- [ ] ¿Se testea la seguridad y el control de acceso?

### 3. Integración y Comunicación entre Módulos
- [ ] ¿Existen tests de integración con otros módulos?
- [ ] ¿Se simulan flujos completos que involucren varios módulos?
- [ ] ¿Se testean errores de integración y recuperación ante fallos?

### 4. Organización y Correspondencia
- [ ] ¿La estructura de tests es clara y modular?
- [ ] ¿Los tests reflejan el comportamiento real esperado?
- [ ] ¿La documentación de los tests es suficiente y clara?

### 5. Feedback Visual y Experiencia de Usuario
- [ ] ¿Se verifica el feedback visual ante acciones del usuario?
- [ ] ¿Se testean los mensajes y notificaciones?
- [ ] ¿Se cubre la experiencia de usuario en escenarios de error?

---

## Ejemplo de Aplicación (rellenar por módulo)

### Módulo: __________________________
- [ ] UI/Frontend: ____________________
- [ ] Backend/Lógica: _________________
- [ ] Integración: ____________________
- [ ] Organización: ___________________
- [ ] Feedback Visual: ________________
- Observaciones:

---

**Este checklist debe completarse y actualizarse para cada módulo tras cada ciclo de desarrollo y testing.**
