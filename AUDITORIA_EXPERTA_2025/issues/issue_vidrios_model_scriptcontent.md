# ISSUE: `cursor.execute(script_content)` en `vidrios/model.py`

Severidad: P0

Resumen
- `rexus/modules/vidrios/model.py` ejecuta `script_content` directamente en varios puntos.

Ubicación: `rexus/modules/vidrios/model.py` (líneas donde aparece `script_content`)

Acciones sugeridas
- Igual que para inventario: validar origen, usar loader seguro o parametrización, añadir pruebas.

