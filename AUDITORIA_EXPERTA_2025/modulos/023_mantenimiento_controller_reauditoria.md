023 - Re-auditoría profunda: `mantenimiento/controller.py`

Resumen rápido
- Archivo auditado: `rexus/modules/mantenimiento/controller.py`.
- Objetivo: revisar programación, ejecución y seguridad de tareas de mantenimiento.

Hallazgos clave
- Buen uso de un `ProgramacionMantenimientoModel` separado para la lógica de programación.
- Programación automática y reprogramación implementadas; riesgo de loops si no se controlan límites.
- Uso consistente de `auth_required` para métodos que modifican estado.
- Uso de `show_success`/`show_error` para UX coherente.
- Uso de `except Exception` amplio en muchos métodos; se recomienda capturar excepciones específicas.

Severidad
- Medio: posible reprogramación infinita si `dias_siguiente` se calcula mal o `requiere_seguimiento` siempre es True.
- Bajo: dependencia de `ProgramacionMantenimientoModel` para operaciones críticas — asegurar tests de integración.

Recomendaciones
1. Añadir un límite y contador de re-intentos o reprogramaciones para evitar reprogramaciones infinitas.
2. Capturar excepciones específicas en lugar de `Exception` y usar `logger.exception` para almacenar stacktraces.
3. Añadir monitoreo para alertar sobre reprogramaciones frecuentes de un mismo `programacion_id`.
4. Añadir tests que simulen programaciones y ejecuciones para verificar flujos y evitar loops.

### Estado de migración y mejoras (2025-08-18)
- Migración de prints a logger: EN PROGRESO
- Consolidación de mensajes hardcodeados: EN PROGRESO
- Migración SQL: COMPLETA
- No se detectaron señales faltantes críticas.

Recomendaciones adicionales:
- Unificar uso de logger centralizado y message_system.
- Documentar contratos de métodos y señales para facilitar testing.
- Añadir tests unitarios para flujos de mantenimiento y simulaciones.

Estado: listo.
