# ISSUE: `reservas_manager.py` - SELECT TOP 1 / SCOPE_IDENTITY usages

Severidad: P1

Resumen
- `rexus/modules/inventario/submodules/reservas_manager.py` contiene `SELECT TOP 1` y `SELECT SCOPE_IDENTITY()` llamados directamente; revisar contexto y fallos en adaptadores SQL.

Acciones
- Asegurar compatibilidad entre motores DB y usar adaptadores que devuelvan lastrowid de forma consistente.

