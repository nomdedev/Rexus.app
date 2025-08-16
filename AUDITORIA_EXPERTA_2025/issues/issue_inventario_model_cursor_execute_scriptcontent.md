# ISSUE: `cursor.execute(script_content)` en `inventario/model.py`

Severidad: P0

Resumen
- Se detectó ejecución de `script_content` con `cursor.execute(script_content)` en `rexus/modules/inventario/model.py` (líneas múltiples). Ejecutar contenido arbitrario en la DB puede ser peligroso si el `script_content` proviene de fuentes no confiables.

Ubicación: `rexus/modules/inventario/model.py` (varias líneas: script_content)

Acciones sugeridas
1. Auditar el origen de `script_content`. Si viene de archivos SQL propios del proyecto, cargar desde `sql/` con un loader controlado.
2. Evitar interpolación directa; si el script requiere parámetros, usar placeholders y `cursor.execute(script, params)`.
3. Añadir logging y pruebas que confirmen el origen de los scripts.

