# Plan de Priorización - Auditoría Rexus.app 2025

**Fecha**: 8 de agosto de 2025  
**Estado**: En ejecución  
**Metodología**: Matriz de impacto/urgencia  

---

## 🚨 PRIORIDAD CRÍTICA (Hacer Inmediatamente)

### 1. SEGURIDAD CRÍTICA - SQL Injection y Sanitización
**Impacto**: 🔴 CRÍTICO | **Urgencia**: 🔴 INMEDIATA | **Esfuerzo**: 2-3 semanas

**Tareas**:
- [ ] Migrar todo el SQL embebido a archivos externos en módulos pedidos, usuarios, inventario
- [ ] Unificar imports de autenticación y eliminar duplicados
- [ ] Implementar DataSanitizer consistente en toda la aplicación
- [ ] Auditar y corregir hashing inseguro en módulo usuarios
- [ ] Validar que no haya secretos hardcodeados

**Beneficio**: Elimina vulnerabilidades críticas de seguridad

### 2. DEPENDENCIAS Y ENTORNO
**Impacto**: 🟠 ALTO | **Urgencia**: 🔴 INMEDIATA | **Esfuerzo**: 1 semana

**Tareas**:
- [x] ✅ Declarar todas las dependencias usadas (psutil, schedule agregados)
- [x] ✅ Resolver conflictos de versiones (PyQt6-tools removido)
- [ ] Implementar auditoría automática de dependencias (pip-audit, safety)
- [ ] Configurar entorno virtual documentado y reproducible
- [ ] Crear Dockerfile optimizado para producción

**Beneficio**: Estabilidad y reproducibilidad del entorno

---

## 🟠 PRIORIDAD ALTA (Hacer en 2-4 semanas)

### 3. REFACTORIZACIÓN MODULAR
**Impacto**: 🟠 ALTO | **Urgencia**: 🟡 MEDIA | **Esfuerzo**: 3-4 semanas

**Tareas**:
- [ ] Dividir módulo inventario (2989 líneas) en submódulos especializados
- [ ] Dividir módulo usuarios (1665 líneas) en auth, permissions, sessions
- [ ] Refactorizar completamente módulo pedidos (961 líneas, 100% SQL embebido)
- [ ] Eliminar código duplicado y dead code
- [ ] Implementar arquitectura MVC consistente

**Beneficio**: Mantenibilidad y escalabilidad del código

### 4. TESTING Y COBERTURA
**Impacto**: 🟠 ALTO | **Urgencia**: 🟡 MEDIA | **Esfuerzo**: 2-3 semanas

**Tareas**:
- [ ] Mejorar cobertura de tests unitarios (objetivo: >80%)
- [ ] Ampliar tests de integración, especialmente edge cases
- [ ] Implementar tests de seguridad automatizados (SQLi, XSS, roles)
- [ ] Configurar CI/CD con ejecución automática de tests
- [ ] Documentar estrategias de testing

**Beneficio**: Confiabilidad y prevención de regresiones

---

## 🟡 PRIORIDAD MEDIA (Hacer en 1-2 meses)

### 5. CALIDAD DE CÓDIGO
**Impacto**: 🟡 MEDIO | **Urgencia**: 🟡 MEDIA | **Esfuerzo**: 2-3 semanas

**Tareas**:
- [ ] Implementar linters (flake8) y formateadores (black) en CI/CD
- [ ] Agregar tipado estático (mypy) y corregir inconsistencias
- [ ] Unificar docstrings siguiendo PEP257/Google docstrings
- [ ] Optimizar performance en consultas y operaciones críticas
- [ ] Implementar logging consistente y estructurado

**Beneficio**: Código más limpio y mantenible

### 6. DOCUMENTACIÓN TÉCNICA
**Impacto**: 🟡 MEDIO | **Urgencia**: 🟡 MEDIA | **Esfuerzo**: 1-2 semanas

**Tareas**:
- [ ] Documentar arquitectura modular y flujos de datos
- [ ] Crear diagramas de arquitectura y dependencias
- [ ] Automatizar generación de documentación (Sphinx/MkDocs)
- [ ] Documentar APIs y interfaces públicas
- [ ] Mantener documentación de despliegue actualizada

**Beneficio**: Facilita onboarding y mantenimiento

---

## 🟢 PRIORIDAD BAJA (Hacer en 2-3 meses)

### 7. AUTOMATIZACIÓN Y CI/CD
**Impacto**: 🟡 MEDIO | **Urgencia**: 🟢 BAJA | **Esfuerzo**: 1-2 semanas

**Tareas**:
- [ ] Configurar pipelines completos de CI/CD
- [ ] Automatizar despliegues con rollback automático
- [ ] Implementar monitoreo y alertas en producción
- [ ] Configurar backups automáticos y procedimientos de restauración
- [ ] Implementar rate limiting y protecciones DDoS

**Beneficio**: Operaciones más eficientes y confiables

### 8. UX/UI Y FUNCIONALIDADES
**Impacto**: 🟢 BAJO | **Urgencia**: 🟢 BAJA | **Esfuerzo**: 2-3 semanas

**Tareas**:
- [ ] Mejorar interfaces de usuario y experiencia
- [ ] Optimizar performance del frontend
- [ ] Implementar funcionalidades adicionales solicitadas
- [ ] Mejorar accesibilidad y usabilidad
- [ ] Agregar internacionalización (i18n)

**Beneficio**: Mejor experiencia de usuario

---

## 📊 MATRIZ DE PRIORIZACIÓN

| Tarea | Impacto | Urgencia | Esfuerzo | Prioridad |
|-------|---------|----------|----------|-----------|
| Seguridad SQL | 🔴 CRÍTICO | 🔴 INMEDIATA | 3 sem | **CRÍTICA** |
| Dependencias | 🟠 ALTO | 🔴 INMEDIATA | 1 sem | **CRÍTICA** |
| Refactorización | 🟠 ALTO | 🟡 MEDIA | 4 sem | **ALTA** |
| Testing | 🟠 ALTO | 🟡 MEDIA | 3 sem | **ALTA** |
| Calidad código | 🟡 MEDIO | 🟡 MEDIA | 3 sem | **MEDIA** |
| Documentación | 🟡 MEDIO | 🟡 MEDIA | 2 sem | **MEDIA** |
| CI/CD | 🟡 MEDIO | 🟢 BAJA | 2 sem | **BAJA** |
| UX/UI | 🟢 BAJO | 🟢 BAJA | 3 sem | **BAJA** |

---

## 🎯 ROADMAP RECOMENDADO

### Mes 1 (Agosto 2025)
- ✅ Dependencias y entorno (completado)
- 🔄 Seguridad crítica SQL (en proceso)
- 🔄 Testing básico de seguridad

### Mes 2 (Septiembre 2025)
- Refactorización modular (inventario, usuarios)
- Testing y cobertura ampliada
- Documentación técnica básica

### Mes 3 (Octubre 2025)
- Calidad de código (linters, tipado)
- Automatización CI/CD
- Documentación completa

### Mes 4+ (Noviembre+ 2025)
- UX/UI y funcionalidades adicionales
- Optimizaciones de performance
- Mejoras de monitoreo

---

## 🚀 PRÓXIMOS PASOS INMEDIATOS

1. **Esta semana**: Comenzar migración SQL a archivos externos (módulo pedidos)
2. **Próxima semana**: Unificar sistema de autenticación y sanitización
3. **Mes actual**: Completar auditoría de seguridad crítica
4. **Seguimiento**: Actualizar este plan semanalmente

---

**Última actualización**: 8 de agosto de 2025  
**Próxima revisión**: 15 de agosto de 2025
