# ISSUE: Queries construidas con f-strings en `inventario/reportes_manager.py`

Severidad: P1

Resumen
- `rexus/modules/inventario/submodules/reportes_manager.py` contiene `cursor.execute(f"""...{var}...")` en varios lugares. Evitar interpolación directa.

Acciones
- Reescribir usando placeholders y pasar parámetros separados.

