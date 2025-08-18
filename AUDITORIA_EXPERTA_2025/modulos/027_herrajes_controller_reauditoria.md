027 - Re-auditoría profunda: `herrajes/controller.py`

Resumen rápido
- Archivo auditado: `rexus/modules/herrajes/controller.py`.
- Objetivo: revisar sanitización, export, CRUD y consistencia de modelos.

Hallazgos clave
- Uso de `unified_sanitizer` y funciones `sanitize_string`/`sanitize_numeric` en creación/actualización — positivo.
- Duplicada importación de `sanitize_string, sanitize_numeric` encontrada en el archivo (pequeño bug sobrante).
- Uso de `print` y `logging` mezclados.
- `eliminar_herraje` emite `self.herraje_eliminado.emit(hash(codigo))` — uso de hash como ID puede confundir consumidores.
- Exportación: lógica simulada; debe implementarse o documentarse como 'no implementada'.

Recomendaciones
1. Eliminar import duplicado y limpiar imports.
2. Emitir IDs reales (int/uuid) en señales en lugar de `hash(codigo)`.
3. Implementar o desactivar export real; documentar el comportamiento simulado.
4. Unificar logging y añadir tests para CRUD.

### Estado de migración y mejoras (2025-08-18)
- Migración de prints a logger: COMPLETA
- Consolidación de mensajes hardcodeados: EN PROGRESO
- Migración SQL: COMPLETA
- No se detectaron señales faltantes críticas.

Recomendaciones adicionales:
- Finalizar consolidación de mensajes hardcodeados.
- Documentar contratos de métodos y señales para facilitar testing.
- Añadir tests unitarios para flujos de herrajes y simulaciones.

Estado: listo.
