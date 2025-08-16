# ISSUE: Uso de exec/eval detectado (Revisión requerida)

Severidad: P0 — Crítico

Descripción
- Se han identificado referencias a ejecuciones dinámicas de código (`exec` / `eval`) y puntos donde se importa código dinámicamente. Estos patrones representan riesgo de ejecución remota (RCE) y dificultan la auditoría y el mantenimiento.

Ubicaciones encontradas (ejemplos detectados por la auditoría automática):
- `scripts/test_step_by_step.py` (referenciado en `AUDITORIA_EXPERTA_2025/patrones_riesgo.md`)
- `aplicar_estilos_premium.py` (referenciado en `AUDITORIA_EXPERTA_2025/patrones_riesgo.md`)
- `legacy_root/tools/development/maintenance/generar_informes_modulos.py` (usa exec(script_content, ...))
- `legacy_root/docs/CORRECCIONES_PASSWORDS_FINALIZADAS.md` (documenta usos históricos de exec/eval)

Nota: la búsqueda automática devolvió también entradas en archivos SQL (uso de `EXEC` en migraciones) — estos son instrucciones SQL legítimas (T-SQL) y deben revisarse por separado.

Acción propuesta
1. Revisar manualmente cada archivo listado y confirmar si el `exec`/`eval` es necesario.
2. Reemplazar import dinámico por importlib.import_module + getattr con whitelist de módulos/funciones permitidas.
3. Si la ejecución de scripts es necesaria, mover a un runner seguro que:
   - valide y sanee el input
   - exponga solo operaciones permitidas
   - funcione con una lista blanca
4. Crear tests de auditoría que fallen si aparecen nuevos `exec`/`eval` en el repo (script de CI que grep-ea y falla).

Responsable sugerido: equipo Seguridad / Mantenimiento
Plazo sugerido: 48h para los hallazgos P0 iniciales

Referencias rápidas
- Reemplazo recomendable: importlib.import_module(module_name)
- Añadir logger.exception(...) y no silenciar errores durante la migración

---

"""Generado automáticamente por la auditoría experta — revisar antes de cerrar."""
