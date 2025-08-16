# ISSUE: Validación de `self._validate_table_name(...)` en `logistica/model.py`

Severidad: P1/P0 (según contexto)

Resumen
- `logistica/model.py` construye queries dinámicamente usando `self._validate_table_name(self.tabla_entregas)`. Revisar que `_validate_table_name` haga una sanitización robusta o preferir whitelists.

Acciones
1. Revisar la implementación de `_validate_table_name`.
2. Reemplazar construcción dinámica por parametrización o asegurarse de whitelisting.

