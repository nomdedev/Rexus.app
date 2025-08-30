# ISSUE: `query_optimizer.py` - uso de cursor.execute(query, ids)

Severidad: P1

Resumen
- `rexus/utils/query_optimizer.py` usa `cursor.execute(query, ids)` con listas/tuplas dinámicas; asegurarse de que `ids` no provienen de input inseguro.

Acciones
- Validar contenido de `ids` y limitar longitud antes de pasarlo a execute.

