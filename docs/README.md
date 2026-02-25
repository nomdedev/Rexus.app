# Documentación de Rexus.app

**Última actualización:** 24 de Febrero de 2026  
**Versión:** 2.1.0  
**Estado:** Producción

---

## 🎯 Propósito

Esta carpeta contiene toda la documentación técnica y de desarrollo del proyecto Rexus.app, organizada por categorías para facilitar la navegación y el mantenimiento.

## 📚 Estructura de Documentación

### 👥 [Documentación de Usuario](user/)
- [Guía de Usuario Principal](user/user_guide.md) - Manual completo de uso
- [Guías por Módulo](user/user_guide/README.md) - Documentación específica
  - [Gestión de Obras](user/user_guide/obras_management.md)
  - [Gestión de Inventario](user/user_guide/inventory_management.md)
  - [Gestión de Pedidos](user/user_guide/orders_management.md)
  - [Gestión de Compras](user/user_guide/purchases_management.md)

### 🛠️ [Documentación para Desarrolladores](developer/)
- [Componentes de UI](developer/ui_components.md) - Componentes de interfaz
- [Base de Datos](developer/database/README.md)
  - [Esquema de Base de Datos](developer/database/schema.md)
  - [Referencia de Consultas SQL](developer/database/queries_reference.md)
  - [Gestión de Migraciones](developer/database/migrations.md)

### 🚀 [Documentación de Operaciones](operations/)
- [Guía de Despliegue](operations/deployment.md) - Despliegue en producción
- [Monitoreo y Métricas](operations/monitoring.md) - Sistema de monitoreo
- [Respaldo y Recuperación](operations/backup_recovery.md) - Estrategia de backups

### 🔒 [Seguridad y Auditorías](security/)
- [Auditoría Consolidada 2026](security/AUDITORIA_CONSOLIDADA_2026.md) - Resumen completo
- [Plan de Acción - Secrets Seguros](security/PLAN_ACCION_SECRETS_SEGUROS_20260224.md)
- [Auditoría de Seguridad](security/security_audit_20260224.md)
- [Matriz de Vulnerabilidades](security/MATRIZ_VULNERABILIDADES_ACTUALIZADA_20260224.md)

### 📊 [Reportes Técnicos](technical-reports/)
- [Análisis de Calidad de Código](technical-reports/code_quality_20260224.md)
- [Ejemplos de Calidad](technical-reports/code_quality_examples_20260224.md)
- [Resumen de Cobertura](technical-reports/coverage/COVERAGE_SUMMARY.md)

### 📖 [Guías Técnicas](guides/)
- [Guía Completa de Desarrollo](guides/DEVELOPER_GUIDE.md)
- [Guía Rápida de Optimización N+1](guides/GUIA_N1_QUICKSTART.md)
- [Guía de Implementación de Caché](guides/CACHING_QUICKSTART.md)
- [Arquitectura Repository + Service](guides/REPOSITORY_SERVICE_PATTERN.md)
- [Sistema de Monitoreo](guides/MONITOREO_PROMETHEUS_GRAFANA.md)

### 🔧 [Documentación Técnica](tecnica/)
- [Análisis Técnico Completo](tecnica/ANALISIS_TECNICO_COMPLETO.md)
- [Guía de Implementación Técnica](tecnica/TECHNICAL_IMPLEMENTATION_GUIDE.md)
- [Configuración Segura](tecnica/CONFIGURACION_SEGURA.md)
- [Configuración de Análisis de Código](tecnica/CONFIGURACION_ANALISIS_CODIGO.md)

### 📈 [Estado del Proyecto](progreso/)
- [Resumen Ejecutivo del Proyecto](progreso/RESUMEN_FINAL_PROYECTO.md)
- [Estado Actual del Desarrollo](progreso/ESTADO_ACTUAL_PROYECTO.md)
- [Reporte de Mejoras Implementadas](progreso/REPORTE_FINAL_MEJORAS.md)
- [Plan de Implementación Consolidado](progreso/PLAN_DE_IMPLEMENTACION_CONSOLIDADO.md)

---

## 🗺️ Mapa de Documentación por Tipo de Usuario

### 👤 Para Usuarios Finales
1. **Inicio Rápido**: [Manual de Usuario Principal](user/user_guide.md)
2. **Módulos Específicos**: [Guías de Módulos](user/user_guide/README.md)

### 👨‍💻 Para Desarrolladores
1. **Configuración Inicial**: [Guía de Desarrollo](guides/DEVELOPER_GUIDE.md)
2. **Base de Datos**: [Documentación de BD](developer/database/README.md)
3. **Componentes UI**: [Componentes de Interfaz](developer/ui_components.md)

### 🔧 Para Administradores de Sistemas
1. **Despliegue**: [Guía de Despliegue](operations/deployment.md)
2. **Monitoreo**: [Monitoreo y Métricas](operations/monitoring.md)
3. **Seguridad**: [Auditoría de Seguridad](security/AUDITORIA_CONSOLIDADA_2026.md)

### 🔍 Para Auditores y Analistas
1. **Auditoría Completa**: [Auditoría Consolidada](security/AUDITORIA_CONSOLIDADA_2026.md)
2. **Reportes Técnicos**: [Reportes Técnicos](technical-reports/)
3. **Estado del Proyecto**: [Resumen Ejecutivo](progreso/RESUMEN_FINAL_PROYECTO.md)

---

## 🚀 Rutas de Aprendizaje Recomendadas

### 🆕 Ruta de Onboarding (Nuevo Desarrollador)
1. [Manual de Usuario](user/user_guide.md) - Entender el sistema
2. [Guía de Desarrollo](guides/DEVELOPER_GUIDE.md) - Prácticas de desarrollo
3. [Base de Datos](developer/database/README.md) - Estructura de datos
4. [Componentes UI](developer/ui_components.md) - Interfaz de usuario

### ⚡ Ruta de Optimización (Performance)
1. [Guía N+1 QuickStart](guides/GUIA_N1_QUICKSTART.md) - Entender problema N+1
2. [Guía de Caching](guides/CACHING_QUICKSTART.md) - Implementar caché
3. [Reportes de Performance](technical-reports/) - Análisis detallado

### 🔒 Ruta de Seguridad
1. [Auditoría Consolidada](security/AUDITORIA_CONSOLIDADA_2026.md) - Estado actual
2. [Configuración Segura](tecnica/CONFIGURACION_SEGURA.md) - Prácticas seguras
3. [Plan de Acción](security/PLAN_ACCION_SECRETS_SEGUROS_20260224.md) - Mejoras pendientes

---

## 📋 Convenciones de Nomenclatura

### Prefijos de Documentos
- `GUIA_` - Tutoriales y guías paso a paso
- `AUDITORIA_` - Reportes de auditoría y análisis
- `PLAN_` - Planes de implementación y mejora
- `REPORTE_` - Reportes de estado y avances
- `ANALISIS_` - Análisis técnicos y de código
- `CONFIGURACION_` - Documentación de configuración

### Sufijos de Documentos
- `_QUICKSTART.md` - Guías rápidas de inicio
- `_COMPLETO.md` / `_COMPLETA.md` - Documentación exhaustiva
- `_CONSOLIDADO.md` - Documentos que consolidan información
- `_FINAL.md` - Documentos finales de una fase o proyecto

---

## 🔍 Búsqueda Rápida

### Por Tema
- **Seguridad**: Ver directorio [security/](security/)
- **Performance**: Ver [guides/GUIA_N1_QUICKSTART.md](guides/GUIA_N1_QUICKSTART.md)
- **Base de Datos**: Ver [developer/database/](developer/database/)
- **Despliegue**: Ver [operations/](operations/)

### Por Rol
- **Desarrollador**: [developer/](developer/) + [guides/](guides/)
- **Administrador**: [operations/](operations/) + [security/](security/)
- **Usuario Final**: [user/](user/)
- **Auditor**: [security/](security/) + [technical-reports/](technical-reports/)

---

## 📞 Soporte y Contacto

Para consultas sobre la documentación:

- **Equipo de Documentación:** docs@rexus.app
- **Equipo de Desarrollo:** dev@rexus.app
- **Equipo de Operaciones:** ops@rexus.app

---

## 🔄 Mantenimiento

Esta documentación se mantiene activamente con:

- **Actualizaciones semanales** de contenido
- **Revisiones mensuales** de estructura
- **Auditorías trimestrales** de completitud

**Última revisión:** 24 de Febrero 2026  
**Próxima revisión programada:** 3 de Marzo 2026
