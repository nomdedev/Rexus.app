## Auditoría: rexus/modules/obras/controller.py

Resumen
- Archivo: `rexus/modules/obras/controller.py`
- Alcance: Gestión de obras (CRUD, filtros, estado)

Hallazgos clave
- Buenas validaciones en `validar_datos_obra` (fechas, presupuesto, campos obligatorios).
- Uso de un sistema moderno de mensajes (`rexus.utils.message_system`) lo cual mejora consistencia.
- `_get_current_auth_user` intenta leer `AuthManager.current_user`/role; la dependencia a variables globales del AuthManager complica pruebas.
- Uso correcto de decoradores `@auth_required` y `@admin_required` en métodos sensibles.
- Manejo de confirmaciones mediante `ask_question` está encapsulado correctamente.

Riesgos y severidad
- Dependencia global al AuthManager: medio — dificulta inyección de contexto en tests.
- Robustez: bajo — código defensivo y mensajes de error adecuados.

Recomendaciones
1. Inyectar `auth_manager` o `current_user` en el constructor para permitir testing y evitar acoplamiento global.
2. Documentar contract de `message_system` y usarlo uniformemente en toda la app.
3. Añadir tests unitarios para validaciones de fechas y presupuesto.

Estado: informe creado.
