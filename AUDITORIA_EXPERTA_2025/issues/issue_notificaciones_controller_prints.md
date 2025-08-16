# ISSUE: `print()`/logging -> notificaciones/controller.py

Severidad: P1

Resumen
- Dry-run detectó que `notificaciones/controller.py` necesita un logger y migración de `print()` hacia `logger`.

Propuesta de cambio (generado por dry-run): añadir import de `get_logger` desde `rexus.utils.app_logger` y crear `logger = get_logger("notificaciones.controller")`.

Ubicación: `rexus/modules/notificaciones/controller.py`

Acciones recomendadas
1. Revisar el patch propuesto por `tools/migrate_prints_dryrun.py` y confirmar la integración del logger central.
2. Reemplazar cualquier `print(...)` por `logger.debug/info/warning/error` según el contexto.
3. Añadir test unitario que verifique que no hay `print` en este archivo.

