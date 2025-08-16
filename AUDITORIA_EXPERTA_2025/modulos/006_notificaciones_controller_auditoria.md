## Auditoría: rexus/modules/notificaciones/controller.py

Resumen
- Archivo: `rexus/modules/notificaciones/controller.py`
- Alcance: Gestión y creación de notificaciones, contador de no leídas, eventos del sistema

Hallazgos clave
- Buena separación de responsabilidades y manejo de tipos/validaciones (tipo, prioridad).
- Uso de `@auth_required` y `@admin_required` (aunque import location varía entre módulos).
- Manejo defensivo cuando no hay `usuario_actual`.
- Implementaciones completas de conteo/estadísticas.

Riesgos y severidad
- Consistencia: bajo — import de decoradores desde `auth_manager` puede no ser correcto si los decoradores están en `auth_decorators`.
- Robustez: bajo — buenas defensas, pero necesita pruebas de límites (fechas, formatos de notificación).

Recomendaciones
1. Unificar la importación de decoradores de seguridad en todo el proyecto.
2. Añadir validaciones estrictas para `usuario_destino` y `modulo_origen`.
3. Escribir tests que validen conteos y el comportamiento de `marcar_como_leida`.

Estado: informe creado.
