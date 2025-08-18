## Auditoría: rexus/modules/usuarios/controller.py

Resumen
- Archivo: `rexus/modules/usuarios/controller.py`
- Alcance: CRUD de usuarios, autenticación, sanitización y validaciones

Hallazgos clave
- Buen enfoque en seguridad: `sanitizar_datos_usuario` y `SecurityUtils` para mitigar SQL/XSS.
- Duplicación de decoradores `@auth_required` y `@admin_required` en algunos métodos — error de copia/pega que debe corregirse.
- Validaciones completas en `validar_datos_usuario` (unicidad, contraseñas, roles, permisos).
- Buen manejo de bloqueo de cuentas (verificar usuario bloqueado) en `autenticar_usuario`.
- Mezcla de `QMessageBox` y `message_system` en distintos lugares; estandarizar.

Riesgos y severidad
- Seguridad: bajo-medio — sanitización presente pero debe cubrir más superficies (ej.: logs, exportes).
- Bugs: bajo — duplicación de decoradores puede alterar comportamiento (doble check o errores inesperados).

Recomendaciones
1. Remover decoradores duplicados y revisar lista de métodos con permisos.
2. Asegurar sanitización también en logs y todos los puntos de salida.
3. Añadir tests unitarios para flujos de autenticación y bloqueo.
4. Documentar contract de `SecurityUtils`.

### Estado de migración y mejoras (2025-08-18)
- Migración de prints a logger: EN PROGRESO
- Consolidación de mensajes hardcodeados: EN PROGRESO
- Migración SQL: PENDIENTE (prioridad alta)
- Decoradores duplicados detectados, pendiente limpieza completa.

Recomendaciones adicionales:
- Completar migración SQL y eliminar queries hardcodeadas.
- Unificar uso de `message_system` y logger centralizado.
- Remover decoradores duplicados y revisar permisos.
- Documentar contratos de métodos y señales.
- Añadir tests unitarios para autenticación, bloqueo y flujos críticos.

Estado: informe creado.
