## Auditoría: rexus/modules/compras/pedidos/controller.py

Resumen
- Archivo: `rexus/modules/compras/pedidos/controller.py`
- Alcance: Pedidos de compras, creación, estado y detalles.

Hallazgos clave
- Uso correcto de decoradores de seguridad (`@auth_required`, `@permission_required`) aunque hay duplicaciones `@auth_required` repetidos en algunos métodos.
- Buen manejo de validaciones y mensajes usando `message_system`.
- Dependencia en `PedidosModel` y contratos claros para los métodos del modelo.

Riesgos y severidad
- Seguridad: bajo-medio — duplicación de decoradores puede crear comportamientos inesperados.
- Robustez: bajo — manejo de excepciones presente.

Recomendaciones
1. Eliminar decoradores duplicados y estandarizar import/location de decoradores.
2. Añadir tests para permisos (permission_required) sobre métodos sensibles.
3. Documentar contrato de `PedidosModel`.

Estado: informe creado.

### Estado de migración y mejoras (2025-08-18)
- Migración de prints a logger: EN PROGRESO
- Consolidación de mensajes hardcodeados: EN PROGRESO
- Migración SQL: EN PROGRESO
- Se detectaron errores recientes de columnas inexistentes y métodos faltantes en la vista.

Recomendaciones adicionales:
- Completar migración SQL y eliminar queries hardcodeadas.
- Unificar uso de logger centralizado y message_system.
- Implementar y documentar métodos faltantes en la vista.
- Añadir tests unitarios para flujos de compras/pedidos y validación de errores.

Estado: informe creado.
