# ISSUE: `cursor.execute(query)` en `inventario/controller.py` — revisar origen de `query`

Severidad: P1

Resumen
- `inventario/controller.py` llama a `cursor.execute(query)` en la línea detectada; confirmar si `query` viene de código interno o entrada del usuario.

Acciones
1. Si `query` proviene de entrada externa, parametrizar y sanitizar.
2. Añadir logging contextual y pruebas.

