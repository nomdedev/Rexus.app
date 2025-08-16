# Índice de issues generados por auditoría (automático)

Se generaron los siguientes issues a partir del escaneo de patrones de riesgo:

- `issue_exec_eval.md` — Uso de `exec` / `eval` detectado (P0)
- `issue_cursor_execute_unparametrized.md` — `cursor.execute(...)` sin parámetros o con query dinámica (P0/P1)

Siguientes pasos recomendados:
1. Revisar cada issue y asignar responsables.
2. Para cada archivo listado en los issues, crear un issue por archivo si se desea granularidad (puedo generarlos automáticamente).
3. Ejecutar las pruebas de auditoría (grep en CI) y aplicar correcciones críticas.

Si quieres, procedo a:
- Generar un issue por cada archivo detectado (granular), o
- Ejecutar el dry-run de migración prints→logging ahora.

Elige: "generar issues por archivo" o "ejecutar dry-run prints" o ambos.
