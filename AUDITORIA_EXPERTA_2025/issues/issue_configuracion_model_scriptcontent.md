# ISSUE: `cursor.execute(script_content)` en `configuracion/model.py`

Severidad: P0

Resumen
- Ejecución de `script_content` observada en `rexus/modules/configuracion/model.py`.

Acciones
- Validar origen y usar loader controlado para scripts SQL; evitar ejecutar contenidos recibidos en runtime sin validación.

