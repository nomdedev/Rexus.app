# ISSUE: `cursor.execute(...)` sin parámetros o con query dinámica (Inseguridad potencial)

Severidad: P0/P1 (evaluar por caso)

Descripción
- Se detectaron múltiples llamadas a `cursor.execute(...)` en el código. Muchas están correctamente parametrizadas; sin embargo, varias ocurrencias pasan una sola cadena `query` o `script_content` sin parámetros, o construyen queries con f-strings/concatenación en managers y scripts.
- Las llamadas que ejecutan contenido dinámico (p. ej. `cursor.execute(script_content)`) o construyen SQL con interpolación deben revisarse para evitar inyección SQL.

Ejemplos representativos (ubicaciones detectadas):
- `tools/deploy_production.py` — `cursor.execute("SELECT 1")` (uso legítimo, revisar contexto)
- `rexus/utils/sql_query_manager.py` — `return cursor.execute(query)` (posible flujo donde query viene de fuente externa)
- `rexus/utils/sql_script_loader.py` — `cursor.execute(script)` (ejecución de scripts, revisar origen de `script`)
- `scripts/create_compras_tables.py` — `cursor.execute(sql_content)` (migraciones iniciales)
- Modelos con ejecuciones dinámicas o queries sin params:
  - `rexus/modules/usuarios/model.py` (varias llamadas a `cursor.execute(sql_ultimo_id)` y `cursor.execute(sql)`)
  - `rexus/modules/inventario/model.py` (varios `cursor.execute(script_content)`)
  - `rexus/modules/vidrios/model.py` (uso de `cursor.execute(script_content)` y `SELECT SUM...`)
  - `rexus/modules/compras/model.py` (varias consultas ejecutadas directamente)
  - `rexus/modules/logistica/model.py` (uso de `self._validate_table_name` en queries dinámicas)

Acciones propuestas
1. Priorizar el listado de llamadas donde el `query` proviene de una variable (no literal) o donde `script_content` se ejecuta tal cual. Marcar como P0 si la fuente es input del usuario o externo.
2. Reescribir para usar consultas parametrizadas: `cursor.execute(query, params)` o usar `sql_manager.get_query(module, name)` y pasar solo parámetros.
3. Para scripts/migraciones: cargar archivos SQL estáticos y ejecutarlos con un loader controlado que no concatene valores.
4. Añadir context managers para manejo de cursores/transactions (with conn.cursor(): ...; asegurar commit/rollback en excepciones).
5. Añadir tests que simulen inyección básica para los endpoints críticos.

Responsable sugerido: equipo Backend / DB
Plazo sugerido: 72h para los casos críticos

Notas
- Algunas llamadas como `cursor.execute("SELECT 1")` son benignas; revisar caso por caso.
- Para queries que dependen de `self._validate_table_name(...)` o similares, validar la función que limpia el nombre de tabla y preferir parametrización o whitelists.

---

"""Generado automáticamente por la auditoría experta — revisar antes de cerrar."""
