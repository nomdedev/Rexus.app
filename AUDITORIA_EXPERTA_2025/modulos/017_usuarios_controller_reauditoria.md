017 - Re-auditoría profunda: `usuarios/controller.py`

Resumen rápido
- Archivo auditado: `rexus/modules/usuarios/controller.py`.
- Objetivo: seguridad de autenticación, control de bloqueo, sanitización y auditoría.

Hallazgos clave
- Buenas prácticas: amplia sanitización (`sanitize_sql_input`, `sanitize_html_input`) y comprobaciones de `is_safe_input`.
- Registro de auditoría simple con `print` en `registrar_auditoria`; debería integrarse con el sistema de logging/auditoría central.
- Manejo de bloqueo de usuarios y control de intentos: presente y detallado.
- Decoradores de autorización (`auth_required`, `admin_required`) aplicados, aunque hay duplicados en algunos métodos (`@auth_required` repetido).
- Uso repetido de `except Exception` y manejo de errores con mensajes al usuario; riesgo de enmascarar excepciones.

Severidad
- Alto: duplicación de decoradores y manejo genérico de excepciones en funciones críticas de seguridad.
- Medio: logging con `print` en vez de un logger centralizado o sistema de auditoría robusto.

Recomendaciones
1. Eliminar duplicados de decoradores y revisar meta-decoradores para evitar usos repetidos.
2. Integrar `registrar_auditoria` con un logger/auditoría central y persistir eventos críticos (login fallido, bloqueo, reset de password).
3. Usar excepciones específicas y `logger.exception()` donde corresponda.
4. Añadir tests que simulen ataques de fuerza bruta para validar bloqueo.
5. Revisar almacenamiento de contraseñas y usar hashing fuerte (BCrypt/Argon2) en el modelo (si no está ya).

Estado: listo (archivo creado).
