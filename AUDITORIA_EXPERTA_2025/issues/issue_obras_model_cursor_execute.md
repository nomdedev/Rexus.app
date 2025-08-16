# ISSUE: `cursor.execute(...)` en `obras/model.py`

Severidad: P1

Resumen
- `rexus/modules/obras/model.py` ejecuta consultas dinámicas; validar sanitización y transacciones.

Acciones
- Revisar y parametrizar; asegurar commit/rollback en operaciones compuestas.

