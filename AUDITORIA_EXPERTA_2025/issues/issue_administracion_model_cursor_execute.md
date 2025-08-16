# ISSUE: `cursor.execute(...)` en `administracion/model.py`

Severidad: P1

Resumen
- `rexus/modules/administracion/model.py` contiene ejecuciones SQL; revisar parametrización y validación de nombres dinámicos.

Acciones
- Validar inputs y usar placeholders.

