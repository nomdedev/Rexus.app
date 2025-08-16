021 - Re-auditoría profunda: `obras/controller.py`

Resumen rápido
- Archivo auditado: `rexus/modules/obras/controller.py`.
- Objetivo: revisar integridad de datos, manejo de permisos y comunicación con otros módulos.

Hallazgos
- Buen uso de señales y separación de responsabilidades.
- Uso de `ask_question` y sistema moderno de mensajes: coherente con UX.
- `_get_current_auth_user` intenta leer `AuthManager.current_user_role` sin comprobaciones robustas; riesgo si atributos no existen.
- Uso frecuente de `except Exception` y prints.

Recomendaciones
1. Añadir verificaciones `hasattr` o try/except más fino al acceder a atributos de `AuthManager`.
2. Unificar manejo de mensajes (usar `show_*` consistentemente).
3. Registrar eventos críticos (creación/eliminación) en sistema de auditoría.
4. Añadir tests que mockeen `AuthManager` y verifiquen fallbacks.

Estado: listo.
