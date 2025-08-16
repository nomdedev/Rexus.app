# ISSUE: Scripts múltiples ejecutados en `inventario/model.py`

Severidad: P0

Resumen
- `inventario/model.py` ejecuta múltiples `script_content` en varios puntos; centralizar ejecución y validar origen.

Acciones
- Mover scripts a `sql/` y usar loader con whitelist.

