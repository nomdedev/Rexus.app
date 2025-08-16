020 - Re-auditoría profunda: `notificaciones/controller.py`

Resumen rápido
- Archivo auditado: `rexus/modules/notificaciones/controller.py`.
- Objetivo: fiabilidad de entrega, límites y validaciones.

Hallazgos
- Buenas validaciones en `crear_notificacion` (tipo, prioridad, titulo/mensaje).
- Uso de `model` específico `NotificacionesModel`; debiera utilizarse inyección de dependencias para facilitar tests.
- Métodos de conteo y estadística están en el controller; podrían delegarse al modelo para simplificar.
- Uso de `try/except` y prints; cambiar a logger.

Recomendaciones
1. Inyectar `NotificacionesModel` en el constructor para facilitar mocking en tests.
2. Mover lógicas de estadística al modelo para single responsibility.
3. Añadir límites/filtros anti-spam (ratelimits) para `crear_notificacion`.
4. Usar logger y capturar excepciones específicas.

Estado: listo.
