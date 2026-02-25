# Referencias Cruzadas - Documentación Rexus.app

**Última actualización:** 24 de Febrero 2026
**Versión:** 2.1.0

---

## Propósito

Este documento conecta temas relacionados que se encuentran dispersos en diferentes documentos de la documentación de Rexus.app, permitiendo navegar entre temas relacionados eficientemente.

## Índice de Temas

- [Seguridad](#seguridad)
- [Performance y Optimización](#performance-y-optimización)
- [Arquitectura y Patrones](#arquitectura-y-patrones)
- [Testing y Calidad](#testing-y-calidad)
- [Base de Datos](#base-de-datos)
- [Desarrollo y Guías](#desarrollo-y-guías)
- [Monitoreo y Logging](#monitoreo-y-logging)
- [Configuración](#configuración)
- [Documentación y Mantenimiento](#documentación-y-mantenimiento)
- [Reportes de Auditoría](#reportes-de-auditoría)

---

## Seguridad

### Documentos principales de seguridad

| Documento | Ruta | Descripción |
|-----------|------|-------------|
| **Auditoría de Seguridad** | `auditoria/AUDITORIA_EXPERTA_2025/FASE1_1_AUDITORIA_SEGURIDAD.md` | Análisis completo de seguridad (95/100) |
| **Configuración Segura** | `tecnica/CONFIGURACION_SEGURA.md` | Guía de configuración segura del sistema |
| **Correcciones de Seguridad** | `progreso/REPORTE_IMPLEMENTACION_CORRECCIONES.md` | Correcciones implementadas |

### Temas relacionados

#### Autenticación y Contraseñas
- **Auditoría:** `auditoria/AUDITORIA_EXPERTA_2025/FASE1_1_AUDITORIA_SEGURIDAD.md` - Sección 2
- **Plan de Mejoras:** `progreso/PLAN_DE_IMPLEMENTACION_CONSOLIDADO.md` - Fase 1.1
- **Implementación:** `progreso/REPORTE_FINAL_MEJORAS.md` - Sección Seguridad

#### SQL Injection
- **Auditoría:** `auditoria/AUDITORIA_EXPERTA_2025/FASE1_1_AUDITORIA_SEGURIDAD.md` - Sección 3
- **Guías:** `guias/GUIA_N1_QUICKSTART.md` - Ejemplos de SQL seguro
- **Plan de Implementación:** `progreso/PLAN_DE_IMPLEMENTACION_CONSOLIDADO.md` - Sección 3.1

#### Permisos y Autorización
- **Análisis Técnico:** `tecnica/ANALISIS_TECNICO_COMPLETO.md` - Sección de Seguridad
- **Guía de Desarrollo:** `guias/DEVELOPER_GUIDE.md` - Sección de Seguridad

---

## Performance y Optimización

### Documentos principales de performance

| Documento | Ruta | Descripción |
|-----------|------|-------------|
| **Auditoría de Performance** | `auditoria/AUDITORIA_EXPERTA_2025/FASE2_1_AUDITORIA_PERFORMANCE.md` | Análisis completo (92/100) |
| **Guía N+1 QuickStart** | `guias/GUIA_N1_QUICKSTART.md` | Guía rápida de optimización N+1 |
| **Optimizaciones Completadas** | `progreso/OPTIMIZACION_N1_COMPLETADAS.md` | Registro de optimizaciones |
| **Caching QuickStart** | `guias/CACHING_QUICKSTART.md` | Guía de implementación de caché |

### Temas relacionados

#### Problema N+1
- **Guía Educativa:** `guias/GUIA_N1_QUICKSTART.md` - Explicación completa con ejemplos
- **Optimizaciones:** `progreso/OPTIMIZACION_N1_COMPLETADAS.md` - Optimizaciones por módulo
- **Auditoría:** `auditoria/AUDITORIA_EXPERTA_2025/FASE2_1_AUDITORIA_PERFORMANCE.md` - Sección Queries

#### Caching con Redis
- **Guía Rápida:** `guias/CACHING_QUICKSTART.md` - Implementación paso a paso
- **Progreso:** `progreso/PROGRESO_ACTUAL.md` - Sección Caching
- **Resumen Final:** `progreso/RESUMEN_FINAL_PROYECTO.md` - Impacto del caché

#### Optimización de Queries
- **Auditoría Performance:** `auditoria/AUDITORIA_EXPERTA_2025/FASE2_1_AUDITORIA_PERFORMANCE.md` - Análisis de queries
- **Análisis Técnico:** `tecnica/ANALISIS_TECNICO_COMPLETO.md` - Sección Base de Datos
- **Plan:** `progreso/PLAN_DE_IMPLEMENTACION_CONSOLIDADO.md` - Fase 2.2

---

## Arquitectura y Patrones

### Documentos principales de arquitectura

| Documento | Ruta | Descripción |
|-----------|------|-------------|
| **Repository + Service Pattern** | `guias/REPOSITORY_SERVICE_PATTERN.md` | Arquitectura de acceso a datos |
| **Auditoría de Arquitectura** | `auditoria/AUDITORIA_EXPERTA_2025/FASE2_3_AUDITORIA_ARQUITECTURA.md` | Análisis (88/100) |
| **Análisis Técnico Completo** | `tecnica/ANALISIS_TECNICO_COMPLETO.md` | Arquitectura del sistema |
| **Technical Implementation Guide** | `tecnica/TECHNICAL_IMPLEMENTATION_GUIDE.md` | Guía de implementación técnica |

### Temas relacionados

#### Repository Pattern
- **Guía Principal:** `guias/REPOSITORY_SERVICE_PATTERN.md` - Documentación completa
- **Progreso:** `progreso/PROGRESO_ACTUAL.md` - Sección Repository Pattern
- **Resumen Final:** `progreso/RESUMEN_FINAL_PROYECTO.md` - Arquitectura implementada

#### Service Layer
- **Guía Principal:** `guias/REPOSITORY_SERVICE_PATTERN.md` - Sección BaseService
- **Plan:** `progreso/PLAN_DE_IMPLEMENTACION_CONSOLIDADO.md` - Fase 3.3

#### MVC
- **Análisis Técnico:** `tecnica/ANALISIS_TECNICO_COMPLETO.md` - Sección MVC
- **Auditoría Arquitectura:** `auditoria/AUDITORIA_EXPERTA_2025/FASE2_3_AUDITORIA_ARQUITECTURA.md` - Sección 1

#### God Objects
- **Plan de Mejora:** `progreso/PLAN_MEJORA_GOD_OBJECTS.md` - Plan de refactorización
- **Auditoría Código:** `auditoria/AUDITORIA_EXPERTA_2025/FASE3_1_AUDITORIA_CODIGO.md` - Sección God Objects

---

## Testing y Calidad

### Documentos principales de testing

| Documento | Ruta | Descripción |
|-----------|------|-------------|
| **Auditoría de Testing** | `auditoria/AUDITORIA_EXPERTA_2025/FASE2_2_AUDITORIA_TESTING.md` | Análisis completo (80/100) |
| **Developer Guide** | `guias/DEVELOPER_GUIDE.md` - Sección Testing | Guía de testing |
| **Informe Final Auditoría** | `auditoria/INFORME_FINAL_AUDITORIA_COMPLETA.md` - Sección Testing | Resultados |

### Temas relacionados

#### Tests Unitarios
- **Guía Desarrollo:** `guias/DEVELOPER_GUIDE.md` - Sección Testing
- **Plan:** `progreso/PLAN_DE_IMPLEMENTACION_CONSOLIDADO.md` - Fase 2.3
- **Informe:** `auditoria/INFORME_FINAL_AUDITORIA_COMPLETA.md` - Tests críticos

#### Tests de Seguridad
- **Plan:** `progreso/PLAN_DE_IMPLEMENTACION_CONSOLIDADO.md` - Fase 3.1
- **Auditoría Seguridad:** `auditoria/AUDITORIA_EXPERTA_2025/FASE1_1_AUDITORIA_SEGURIDAD.md` - Tests

#### Cobertura de Código
- **Auditoría Testing:** `auditoria/AUDITORIA_EXPERTA_2025/FASE2_2_AUDITORIA_TESTING.md` - Métricas
- **Progreso:** `progreso/PROGRESO_ACTUAL.md` - Cobertura actual

---

## Base de Datos

### Documentos principales de base de datos

| Documento | Ruta | Descripción |
|-----------|------|-------------|
| **Auditoría Base de Datos** | `auditoria/AUDITORIA_EXPERTA_2025/FASE1_2_AUDITORIA_BASE_DE_DATOS.md` | Análisis (90/100) |
| **Análisis Técnico** | `tecnica/ANALISIS_TECNICO_COMPLETO.md` - Sección BD | Arquitectura de BD |

### Temas relacionados

#### Backups
- **Auditoría BD:** `auditoria/AUDITORIA_EXPERTA_2025/FASE1_2_AUDITORIA_BASE_DE_DATOS.md` - Sección Backups
- **Plan:** `progreso/PLAN_DE_IMPLEMENTACION_CONSOLIDADO.md` - Fase 1.2
- **Informe Final:** `auditoria/INFORME_FINAL_AUDITORIA_COMPLETA.md` - Sistema de backups

#### SQL Server
- **Análisis Técnico:** `tecnica/ANALISIS_TECNICO_COMPLETO.md` - Sección SQL Server
- **Configuración:** `tecnica/CONFIGURACION_SEGURA.md` - Configuración segura

#### Connection Pooling
- **Auditoría Performance:** `auditoria/AUDITORIA_EXPERTA_2025/FASE2_1_AUDITORIA_PERFORMANCE.md` - Sección Pooling
- **Informe Final:** `auditoria/INFORME_FINAL_AUDITORIA_COMPLETA.md` - Implementación

---

## Desarrollo y Guías

### Documentos principales de desarrollo

| Documento | Ruta | Descripción |
|-----------|------|-------------|
| **Developer Guide** | `guias/DEVELOPER_GUIDE.md` | Guía completa de desarrollo |
| **Guía N+1 QuickStart** | `guias/GUIA_N1_QUICKSTART.md` | Guía rápida de optimización N+1 |
| **Caching QuickStart** | `guias/CACHING_QUICKSTART.md` | Guía de implementación de caché |
| **Monitoreo Prometheus Grafana** | `guias/MONITOREO_PROMETHEUS_GRAFANA.md` | Sistema de monitoreo |

### Temas relacionados

#### Instalación y Configuración
- **Developer Guide:** `guias/DEVELOPER_GUIDE.md` - Sección Instalación
- **Configuraciones:** `tecnica/CONFIGURACIONES.md` - Variables de entorno

#### Git Workflow
- **Developer Guide:** `guias/DEVELOPER_GUIDE.md` - Sección Git Workflow
- **Plan:** `progreso/PLAN_DE_IMPLEMENTACION_CONSOLIDADO.md` - CI/CD

#### Troubleshooting
- **Developer Guide:** `guias/DEVELOPER_GUIDE.md` - Sección Troubleshooting
- **Progreso:** `progreso/MEJORAS_PENDIENTES.md` - Problemas conocidos

---

## Monitoreo y Logging

### Documentos principales de monitoreo

| Documento | Ruta | Descripción |
|-----------|------|-------------|
| **Monitoreo Prometheus Grafana** | `guias/MONITOREO_PROMETHEUS_GRAFANA.md` | Sistema de monitoreo |
| **Auditoría Logging** | `auditoria/AUDITORIA_EXPERTA_2025/FASE3_2_AUDITORIA_LOGGING_MONITOREO.md` | Análisis (95/100) |

### Temas relacionados

#### Prometheus
- **Guía Monitoreo:** `guias/MONITOREO_PROMETHEUS_GRAFANA.md` - Configuración Prometheus
- **Informe Final:** `auditoria/INFORME_FINAL_AUDITORIA_COMPLETA.md` - Métricas Prometheus

#### Grafana
- **Guía Monitoreo:** `guias/MONITOREO_PROMETHEUS_GRAFANA.md` - Dashboards Grafana
- **Progreso:** `progreso/PROGRESO_ACTUAL.md` - Sección Monitoreo

#### Logging
- **Auditoría Logging:** `auditoria/AUDITORIA_EXPERTA_2025/FASE3_2_AUDITORIA_LOGGING_MONITOREO.md` - Análisis completo
- **Developer Guide:** `guias/DEVELOPER_GUIDE.md` - Sección Logging

---

## Configuración

### Documentos principales de configuración

| Documento | Ruta | Descripción |
|-----------|------|-------------|
| **Configuraciones** | `tecnica/CONFIGURACIONES.md` | Configuración del sistema |
| **Configuración Segura** | `tecnica/CONFIGURACION_SEGURA.md` | Configuración segura |
| **Auditoría Configuración** | `auditoria/AUDITORIA_EXPERTA_2025/FASE3_3_AUDITORIA_CONFIGURACION.md` | Análisis (90/100) |

### Temas relacionados

#### Variables de Entorno
- **Configuraciones:** `tecnica/CONFIGURACIONES.md` - Variables principales
- **Configuración Segura:** `tecnica/CONFIGURACION_SEGURA.md` - Variables sensibles

#### Secrets Management
- **Auditoría Configuración:** `auditoria/AUDITORIA_EXPERTA_2025/FASE3_3_AUDITORIA_CONFIGURACION.md` - Sección Secrets
- **Informe Final:** `auditoria/INFORME_FINAL_AUDITORIA_COMPLETA.md` - Gestión de secrets

---

## Mapa de Documentos por Tipo de Usuario

### Para Desarrolladores Nuevos
1. **Inicio:** `README.md`
2. **Guía Principal:** `guias/DEVELOPER_GUIDE.md`
3. **Reglas Críticas:** `CLAUDE.md` (raíz del proyecto)
4. **Primeros Pasos:** `guias/GUIA_N1_QUICKSTART.md`

### Para Arquitectos/Lead Developers
1. **Arquitectura:** `tecnica/ANALISIS_TECNICO_COMPLETO.md`
2. **Patrones:** `guias/REPOSITORY_SERVICE_PATTERN.md`
3. **Auditoría Arquitectura:** `auditoria/AUDITORIA_EXPERTA_2025/FASE2_3_AUDITORIA_ARQUITECTURA.md`

### Para DevOps/SRE
1. **Monitoreo:** `guias/MONITOREO_PROMETHEUS_GRAFANA.md`
2. **Configuración:** `tecnica/CONFIGURACIONES.md`
3. **Logging:** `auditoria/AUDITORIA_EXPERTA_2025/FASE3_2_AUDITORIA_LOGGING_MONITOREO.md`

### Para QA/Testers
1. **Testing:** `guias/DEVELOPER_GUIDE.md` - Sección Testing
2. **Auditoría Testing:** `auditoria/AUDITORIA_EXPERTA_2025/FASE2_2_AUDITORIA_TESTING.md`
3. **Tests de Seguridad:** `auditoria/AUDITORIA_EXPERTA_2025/FASE1_1_AUDITORIA_SEGURIDAD.md`

### Para Security Engineers
1. **Auditoría Seguridad:** `auditoria/AUDITORIA_EXPERTA_2025/FASE1_1_AUDITORIA_SEGURIDAD.md`
2. **Configuración Segura:** `tecnica/CONFIGURACION_SEGURA.md`
3. **Informe Final:** `auditoria/INFORME_FINAL_AUDITORIA_COMPLETA.md` - Sección Seguridad

---

## Rutas de Aprendizaje Recomendadas

### Ruta: Optimización de Performance
1. `guias/GUIA_N1_QUICKSTART.md` - Entender el problema N+1
2. `progreso/OPTIMIZACION_N1_COMPLETADAS.md` - Ver optimizaciones aplicadas
3. `guias/CACHING_QUICKSTART.md` - Implementar caché
4. `auditoria/AUDITORIA_EXPERTA_2025/FASE2_1_AUDITORIA_PERFORMANCE.md` - Auditoría completa

### Ruta: Implementación de Seguridad
1. `auditoria/AUDITORIA_EXPERTA_2025/FASE1_1_AUDITORIA_SEGURIDAD.md` - Entender problemas
2. `tecnica/CONFIGURACION_SEGURA.md` - Configurar de forma segura
3. `progreso/PLAN_DE_IMPLEMENTACION_CONSOLIDADO.md` - Fase 1 (Correcciones críticas)
4. `auditoria/INFORME_FINAL_AUDITORIA_COMPLETA.md` - Ver resultados

### Ruta: Refactorización de Arquitectura
1. `tecnica/ANALISIS_TECNICO_COMPLETO.md` - Entender arquitectura actual
2. `guias/REPOSITORY_SERVICE_PATTERN.md` - Aprender patrón Repository+Service
3. `progreso/PLAN_MEJORA_GOD_OBJECTS.md` - Plan de refactorización
4. `auditoria/AUDITORIA_EXPERTA_2025/FASE2_3_AUDITORIA_ARQUITECTURA.md` - Auditoría arquitectura

### Ruta: Monitoreo y Observabilidad
1. `guias/MONITOREO_PROMETHEUS_GRAFANA.md` - Sistema de monitoreo
2. `auditoria/AUDITORIA_EXPERTA_2025/FASE3_2_AUDITORIA_LOGGING_MONITOREO.md` - Auditoría logging
3. `progreso/PROGRESO_ACTUAL.md` - Ver estado actual del monitoreo

---

## Glosario de Términos

| Término | Definición | Documentos Relacionados |
|---------|------------|-------------------------|
| **N+1** | Problema de queries en bucle | `guias/GUIA_N1_QUICKSTART.md` |
| **Repository Pattern** | Patrón de acceso a datos | `guias/REPOSITORY_SERVICE_PATTERN.md` |
| **Service Layer** | Capa de lógica de negocio | `guias/REPOSITORY_SERVICE_PATTERN.md` |
| **God Object** | Objeto con demasiadas responsabilidades | `progreso/PLAN_MEJORA_GOD_OBJECTS.md` |
| **Cache Hit Rate** | Porcentaje de aciertos en caché | `guias/CACHING_QUICKSTART.md` |
| **Connection Pooling** | Reutilización de conexiones BD | `auditoria/AUDITORIA_EXPERTA_2025/FASE1_2_AUDITORIA_BASE_DE_DATOS.md` |

---

## Actualizaciones Pendientes

### Documentos que necesitan revisión
- [ ] Actualizar `guias/DEVELOPER_GUIDE.md` con últimos cambios
- [ ] Revisar `progreso/MEJORAS_PENDIENTES.md` para eliminar items completados
- [ ] Actualizar `tecnica/ANALISIS_TECNICO_COMPLETO.md` con nueva arquitectura

### Enlaces a verificar
- [ ] Verificar enlaces a `CLAUDE.md` desde documentos
- [ ] Verificar enlaces cruzados en auditorías
- [ ] Actualizar rutas relativas tras reorganización

---

## Documentación y Mantenimiento

### Documentos principales de documentación

| Documento | Ruta | Descripción |
|-----------|------|-------------|
| **Resumen Ejecutivo** | `RESUMEN_EJECUTIVO_DOCUMENTACION.md` | Vista general y estadísticas completas |
| **Guía de Mantenimiento** | `MANTENIMIENTO_DOCUMENTACION.md` | Procesos y responsabilidades de mantenimiento |
| **Informe de Revisión** | `INFORME_REVISION_DOCUMENTACION_20260224.md` | Estado actual de la documentación |

### Temas relacionados

#### Gestión de Documentación
- **Resumen Ejecutivo:** `RESUMEN_EJECUTIVO_DOCUMENTACION.md` - Estadísticas y mapas de navegación
- **Mantenimiento:** `MANTENIMIENTO_DOCUMENTACION.md` - Procesos de mantenimiento
- **Guías de Estilo:** `MANTENIMIENTO_DOCUMENTACION.md#plantillas-y-estándares` - Plantillas y formatos

#### Automatización de Documentación
- **Scripts de Validación:** `MANTENIMIENTO_DOCUMENTACION.md#scripts-de-automatización` - Scripts automáticos
- **Integración CI/CD:** `MANTENIMIENTO_DOCUMENTACION.md#integración-con-cicd` - Integración continua
- **Métricas de Calidad:** `MANTENIMIENTO_DOCUMENTACION.md#métricas-y-kpis` - Indicadores de calidad

---

## Reportes de Auditoría

### Documentos principales de auditoría

| Documento | Ruta | Descripción |
|-----------|------|-------------|
| **Análisis Completo** | `../reports/ANALISIS_COMPLETO_REXUS_20260224.md` | Análisis integral de todos los módulos |
| **Metodología** | `../reports/METODOLOGIA_ANALISIS_20260224.md` | Metodología utilizada para auditorías |
| **Reporte de Seguridad** | `../reports/security_audit_20260224.md` | Análisis de seguridad exhaustivo |
| **Matriz de Trazabilidad** | `../reports/MATRIZ_TRAZABILIDAD_AUDITORIA_20260224.md` | Trazabilidad completa de requisitos |

### Auditorías por Módulo

#### Módulos Principales
- **Obras:** `../reports/obras_audit_20260224.md` - Auditoría completa del módulo de obras
- **Inventario:** `../reports/inventario_audit_20260224.md` - Auditoría completa del módulo de inventario
- **Pedidos:** `../reports/pedidos_audit_20260224.md` - Auditoría completa del módulo de pedidos
- **Compras:** `../reports/compras_audit_20260224.md` - Auditoría completa del módulo de compras
- **Logística:** `../reports/logistica_audit_20260224.md` - Auditoría completa del módulo de logística
- **Usuarios:** `../reports/usuarios_audit_20260224.md` - Auditoría completa del módulo de usuarios

#### Módulos de Soporte
- **Configuración:** `../reports/configuracion_audit_20260224.md` - Auditoría del módulo de configuración
- **Notificaciones:** `../reports/notificaciones_audit_20260224.md` - Auditoría del módulo de notificaciones
- **Mantenimiento:** `../reports/mantenimiento_audit_20260224.md` - Auditoría del módulo de mantenimiento
- **Recursos Humanos:** `../reports/administracion_audit_20260224.md` - Auditoría del módulo de RRHH
- **Contabilidad:** No disponible - Pendiente de auditoría
- **Herrajes:** `../reports/herrajes_audit_20260224.md` - Auditoría del módulo de herrajes
- **Vidrios:** `../reports/vidrios_audit_20260224.md` - Auditoría del módulo de vidrios

### Temas relacionados

#### Integración con Documentación Técnica
- **Conexión Bidireccional:** `RESUMEN_EJECUTIVO_DOCUMENTACION.md#conexiones-con-documentación-existente` - Integración completa
- **Referencias Cruzadas:** `CROSSREFERENCES.md` - Enlaces entre auditorías y documentación
- **Implementación de Recomendaciones:** `progreso/REPORTE_FINAL_MEJORAS.md` - Mejoras implementadas

#### Análisis y Reportes
- **Análisis de Base de Datos:** `../reports/database_audit_20260224.md` - Auditoría de base de datos
- **Análisis de Calidad de Código:** `../reports/code_quality_20260224.md` - Auditoría de código
- **Análisis de Testing:** `../reports/testing_audit_20260224.md` - Auditoría de pruebas

---

**Versión:** 2.1.0
**Próxima revisión:** 24 de Marzo 2026
**Mantenedor:** Rexus.app Documentation Team
