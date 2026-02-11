# Resumen maestro — Auditoría de módulos

**Fecha:** 15 de agosto de 2025

Este archivo consolida el estado de auditoría por módulo (view / model) y las recomendaciones globales prioritarias.

## Estado por módulo
- administracion
  - model: Done (`administracion_model.md`)
  - view: Done (`administracion_view.md`)
- auditoria
  - model: Done (`auditoria_model.md`)
  - view: Done (`auditoria_view.md`)
- compras
  - model: Done (`compras_model.md`)
  - view: Done (`compras_view.md`, `compras_view_complete.md`)
- configuracion
  - model: Done (`configuracion_model.md`)
  - view: Done (`configuracion_view.md`)
- herrajes
  - model: Done (`herrajes_model.md`)
  - view: Done (`herrajes_view.md`)
- inventario
  - model: Done (`inventario_model.md`)
  - view: Done (`inventario_view.md`)
- logistica
  - model: Done (`logistica_model.md`)
  - view: Done (`logistica_view.md`)
- mantenimiento
  - model: Done (`mantenimiento_model.md`)
  - view: Done (`mantenimiento_view.md`)
- notificaciones
  - model: Done (`notificaciones_model.md`)
  - view: Done (`notificaciones_view.md`)
- obras
  - model: Done (`obras_model.md`)
  - view: Done (`obras_view.md`)
- pedidos
  - model: Done (`pedidos_model.md`)
  - view: Done (`pedidos_view.md`, `pedidos_view_complete.md`)
- usuarios
  - model: Done (`usuarios_model.md`)
  - view: Done (`usuarios_view.md`)
- vidrios
  - model: Done (`vidrios_model.md`)
  - view: Done (`vidrios_view.md`)

## Observaciones globales
- Cobertura: Todos los módulos principales (`rexus/modules/*`) tienen auditoría de `model.py` y `view.py` en `AUDITORIA_EXPERTA_2025/modulos/`.
- Patrones recurrentes detectados:
  - Dependencia de utilidades externas (`sql_query_manager`, `unified_sanitizer`, `sql_security`). Verificar disponibilidad en despliegues.
  - SQL orientado a SQL Server en muchos modelos (GETDATE, ISNULL, TOP, INFORMATION_SCHEMA). Documentar o abstraer para portabilidad.
  - Manejo de errores consistente pero mayormente log-only; falta integración con monitoreo/alertas.
  - Falta de tests unitarios e integración para la mayoría de módulos.
  - Cacheo por nombre de función usado en varias partes: revisar robustez ante refactors.

## Recomendaciones prioritarias (ordenadas)
1. Añadir tests unitarios para las piezas críticas: `compras`, `inventario`, `auditoria`, `configuracion`.
2. Implementar manejo centralizado de errores y envío de alertas para fallas críticas (integración con Sentry o similar).
3. Normalizar la compatibilidad con RDBMS diferentes (crear capa de abstracción o SQL templates por motor).
4. Forzar validación y sanitización de entrada en todos los métodos públicos (usar `unified_sanitizer` y `validate_table_name`).
5. Revisar estrategias de cache: usar claves deterministas basadas en argumentos en lugar de nombres de función simples.

## Próximos pasos propuestos (elijo uno para ejecutar ahora si confirmas)
- 1) Auditar controladores / controllers y `rexus/main/app.py` (recomendado para ver flujo de inicialización y wiring).
- 2) Generar conjunto de tests básicos (pruebas rápidas) para `inventario` y `compras`.
- 3) Crear un checklist de trabajo (priorizado) en `checklist_pendientes.md` con tareas accionables.

---

Si confirmas, ejecuto la opción 1 y comienzo a auditar `rexus/main/app.py` y los controladores para completar la visión del flujo de la aplicación.
