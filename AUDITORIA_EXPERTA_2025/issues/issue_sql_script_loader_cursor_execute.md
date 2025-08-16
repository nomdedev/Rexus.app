# ISSUE: `sql_script_loader.py` - `cursor.execute(script)`

Severidad: P0/P1

Resumen
- `rexus/utils/sql_script_loader.py` ejecuta scripts cargados por la aplicación. Verificar origen y permisos.

Acciones
- Implementar validaciones y controles de acceso para quien puede cargar/ejecutar scripts SQL.

