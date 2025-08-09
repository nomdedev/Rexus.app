# Issues Generados - Auditoría Rexus.app 2025

**Fecha de generación**: 8 de agosto de 2025  
**Total de issues**: 20  
**Estado**: Listos para implementación  

---

## 🚨 ISSUES CRÍTICOS (Hacer Inmediatamente)

### Issue #001: [CRÍTICO] Migrar SQL embebido a archivos externos
**Prioridad**: 🔴 CRÍTICA  
**Etiquetas**: `security`, `sql-injection`, `refactoring`  
**Esfuerzo estimado**: 3 semanas  

**Descripción**:
Migrar todo el SQL embebido (f-strings peligrosos) a archivos externos usando SQLQueryManager.

**Módulos afectados**:
- `pedidos/model.py` (961 líneas, 100% SQL embebido)
- `usuarios/model.py` (queries de autenticación críticos)
- `inventario/model.py` (SQL híbrido)
- `obras/model.py` y `vidrios/model.py`

**Criterios de aceptación**:
- [ ] 0 f-strings con SQL detectados en auditoría
- [ ] Todos los módulos usan SQLQueryManager exclusivamente
- [ ] Scripts SQL organizados en `scripts/sql/[modulo]/`
- [ ] Tests de seguridad SQLi pasando al 100%

### Issue #002: [CRÍTICO] Unificar sistema de autenticación
**Prioridad**: 🔴 CRÍTICA  
**Etiquetas**: `security`, `authentication`, `imports`  
**Esfuerzo estimado**: 1 semana  

**Descripción**:
Eliminar imports duplicados de auth_decorators y unificar sistema de autenticación.

**Tareas**:
- [ ] Eliminar imports duplicados en todos los model.py
- [ ] Usar solo: `from rexus.core.auth_decorators import auth_required, admin_required`
- [ ] Validar que los 33 decoradores funcionen correctamente
- [ ] Documentar flujo de autenticación unificado

### Issue #003: [CRÍTICO] Implementar DataSanitizer consistente
**Prioridad**: 🔴 CRÍTICA  
**Etiquetas**: `security`, `input-validation`, `xss`  
**Esfuerzo estimado**: 1 semana  

**Descripción**:
Unificar la sanitización de datos y eliminar implementaciones inconsistentes.

**Problemas actuales**:
- Múltiples rutas de importación (`utils.data_sanitizer` vs `rexus.utils.data_sanitizer`)
- Métodos inexistentes (`sanitize_string()` vs `sanitize_text()`)
- Clases dummy sin funcionalidad real

**Solución**:
- [ ] Crear `utils/unified_sanitizer.py` con métodos estándar
- [ ] Implementar `SecurityUtils.sanitize_input()` consistente
- [ ] Migrar todos los módulos al sistema unificado
- [ ] Tests de XSS y validación de entradas

### Issue #004: [CRÍTICO] Corregir hashing inseguro en usuarios
**Prioridad**: 🔴 CRÍTICA  
**Etiquetas**: `security`, `password-hashing`, `users`  
**Esfuerzo estimado**: 1 semana  

**Descripción**:
Reemplazar hashlib inseguro por algoritmos seguros con salt.

**Problemas**:
- Uso de hashlib sin salt
- Autenticación con SQL directo vulnerable
- Gestión de sesiones no robusta

**Solución**:
- [ ] Implementar PBKDF2 o bcrypt para passwords
- [ ] Agregar salt único por usuario
- [ ] Migrar autenticación a sistema seguro
- [ ] Implementar gestión de sesiones robusta

---

## 🟠 ISSUES ALTA PRIORIDAD

### Issue #005: [ALTO] Refactorizar módulo inventario
**Prioridad**: 🟠 ALTA  
**Etiquetas**: `refactoring`, `architecture`, `maintainability`  
**Esfuerzo estimado**: 2 semanas  

**Descripción**:
Dividir inventario/model.py (2989 líneas) en submódulos especializados.

**Submódulos propuestos**:
- `inventario/models/items.py`
- `inventario/models/stock.py`
- `inventario/models/movements.py`
- `inventario/models/reports.py`

### Issue #006: [ALTO] Refactorizar módulo usuarios
**Prioridad**: 🟠 ALTA  
**Etiquetas**: `refactoring`, `users`, `security`  
**Esfuerzo estimado**: 2 semanas  

**Descripción**:
Dividir usuarios/model.py (1665 líneas) en submódulos especializados.

**Submódulos propuestos**:
- `usuarios/models/auth.py`
- `usuarios/models/permissions.py`
- `usuarios/models/sessions.py`
- `usuarios/models/profiles.py`

### Issue #007: [ALTO] Refactorizar módulo pedidos
**Prioridad**: 🟠 ALTA  
**Etiquetas**: `refactoring`, `orders`, `sql`  
**Esfuerzo estimado**: 2 semanas  

**Descripción**:
Refactorizar completamente pedidos/model.py (961 líneas, 100% SQL embebido).

**Tareas**:
- [ ] Migrar SQL a archivos externos
- [ ] Implementar validación de entradas
- [ ] Garantizar atomicidad de transacciones
- [ ] Dividir en submódulos lógicos

### Issue #008: [ALTO] Ampliar cobertura de testing
**Prioridad**: 🟠 ALTA  
**Etiquetas**: `testing`, `coverage`, `quality`  
**Esfuerzo estimado**: 2 semanas  

**Descripción**:
Mejorar cobertura de tests unitarios e integración.

**Objetivos**:
- [ ] Cobertura >80% en módulos críticos
- [ ] Tests de edge cases y validaciones
- [ ] Tests de seguridad automatizados
- [ ] CI/CD con reports de cobertura

---

## 🟡 ISSUES MEDIA PRIORIDAD

### Issue #009: [MEDIO] Implementar linters y formateadores
**Prioridad**: 🟡 MEDIA  
**Etiquetas**: `code-quality`, `linting`, `formatting`  
**Esfuerzo estimado**: 1 semana  

**Tareas**:
- [ ] Configurar flake8 con reglas del proyecto
- [ ] Implementar black para formateo automático
- [ ] Agregar mypy para tipado estático
- [ ] Integrar en pre-commit hooks y CI/CD

### Issue #010: [MEDIO] Unificar docstrings y documentación
**Prioridad**: 🟡 MEDIA  
**Etiquetas**: `documentation`, `docstrings`, `standards`  
**Esfuerzo estimado**: 1 semana  

**Tareas**:
- [ ] Seguir estándar PEP257/Google docstrings
- [ ] Documentar todas las funciones públicas
- [ ] Generar documentación automática con Sphinx
- [ ] Crear guías de desarrollo actualizadas

### Issue #011: [MEDIO] Optimizar performance de consultas
**Prioridad**: 🟡 MEDIA  
**Etiquetas**: `performance`, `database`, `optimization`  
**Esfuerzo estimado**: 1 semana  

**Tareas**:
- [ ] Auditar consultas lentas
- [ ] Implementar índices optimizados
- [ ] Cachear consultas frecuentes
- [ ] Monitorear performance en producción

### Issue #012: [MEDIO] Implementar logging estructurado
**Prioridad**: 🟡 MEDIA  
**Etiquetas**: `logging`, `monitoring`, `debugging`  
**Esfuerzo estimado**: 1 semana  

**Tareas**:
- [ ] Unificar sistema de logging
- [ ] Implementar niveles y formatos consistentes
- [ ] Evitar exposición de información sensible
- [ ] Integrar con monitoreo en producción

---

## 🟢 ISSUES BAJA PRIORIDAD

### Issue #013: [BAJO] Configurar CI/CD completo
**Prioridad**: 🟢 BAJA  
**Etiquetas**: `ci-cd`, `automation`, `deployment`  
**Esfuerzo estimado**: 2 semanas  

### Issue #014: [BAJO] Implementar monitoreo en producción
**Prioridad**: 🟢 BAJA  
**Etiquetas**: `monitoring`, `alerts`, `production`  
**Esfuerzo estimado**: 1 semana  

### Issue #015: [BAJO] Optimizar Docker y despliegue
**Prioridad**: 🟢 BAJA  
**Etiquetas**: `docker`, `deployment`, `optimization`  
**Esfuerzo estimado**: 1 semana  

### Issue #016: [BAJO] Mejorar UX/UI interfaces
**Prioridad**: 🟢 BAJA  
**Etiquetas**: `ui-ux`, `frontend`, `usability`  
**Esfuerzo estimado**: 2 semanas  

### Issue #017: [BAJO] Implementar rate limiting
**Prioridad**: 🟢 BAJA  
**Etiquetas**: `security`, `rate-limiting`, `ddos`  
**Esfuerzo estimado**: 1 semana  

### Issue #018: [BAJO] Agregar internacionalización
**Prioridad**: 🟢 BAJA  
**Etiquetas**: `i18n`, `localization`, `languages`  
**Esfuerzo estimado**: 1 semana  

### Issue #019: [BAJO] Implementar backup automático
**Prioridad**: 🟢 BAJA  
**Etiquetas**: `backup`, `recovery`, `data-protection`  
**Esfuerzo estimado**: 1 semana  

### Issue #020: [BAJO] Mejorar accesibilidad web
**Prioridad**: 🟢 BAJA  
**Etiquetas**: `accessibility`, `a11y`, `standards`  
**Esfuerzo estimado**: 1 semana  

---

## 📊 RESUMEN POR PRIORIDAD

| Prioridad | Issues | Esfuerzo Total | Beneficio |
|-----------|---------|----------------|-----------|
| 🔴 CRÍTICA | 4 | 6 semanas | Elimina vulnerabilidades críticas |
| 🟠 ALTA | 4 | 8 semanas | Mejora arquitectura y mantenibilidad |
| 🟡 MEDIA | 4 | 4 semanas | Calidad de código y documentación |
| 🟢 BAJA | 8 | 10 semanas | Funcionalidades adicionales y optimizaciones |

**Total**: 20 issues, ~28 semanas de esfuerzo

---

## 🎯 PLAN DE IMPLEMENTACIÓN

### Sprint 1 (1-2 semanas): Issues Críticos #001-#002
- Migración SQL y unificación de autenticación

### Sprint 2 (3-4 semanas): Issues Críticos #003-#004
- Sanitización y hashing seguro

### Sprint 3 (5-8 semanas): Issues Alta Prioridad #005-#008
- Refactorización modular y testing

### Sprint 4+ (9+ semanas): Issues Media y Baja Prioridad
- Calidad, documentación y funcionalidades adicionales

---

**Generado**: 8 de agosto de 2025  
**Próxima actualización**: Cada sprint completado
