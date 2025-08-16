# ISSUE: `cursor.execute(...)` en `compras/model.py` — revisar parametrización

Severidad: P1

Resumen
- Múltiples `cursor.execute(...)` en `rexus/modules/compras/model.py`. Revisar que las queries estén parametrizadas y no se construyan con f-strings.

Ubicación: `rexus/modules/compras/model.py`

Acciones
1. Revisar cada `cursor.execute(sql_...)` y convertir a `cursor.execute(sql, params)` si corresponde.
2. Añadir tests y validaciones de sanitización.

