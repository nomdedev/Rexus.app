# ISSUE: `sql_query_manager.py` - retorno directo de `cursor.execute(query)`

Severidad: P1

Resumen
- `rexus/utils/sql_query_manager.py` hace `return cursor.execute(query)`; si `query` viene de fuentes externas, debe validarse.

Acciones
- Añadir validación de query (whitelist o schema) y wrapping que provea logging y manejo de transacciones.

