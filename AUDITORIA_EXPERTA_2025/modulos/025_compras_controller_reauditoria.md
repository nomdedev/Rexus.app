025 - Re-auditoría profunda: `compras/controller.py`

Resumen rápido
- Archivo auditado: `rexus/modules/compras/controller.py`.
- Objetivo: validar integraciones (inventario), manejo de errores y sanitización.

Hallazgos clave
- Integración con inventario mediante `InventoryIntegration` con fallback si no está disponible.
- Uso de `validar_datos_orden` con buenas comprobaciones de fechas y valores numéricos.
- Uso mixto de `print` y `mensaje` mediante `show_*` (inconsistencia).
- Uso de `try/except` amplio; considerar capturar errores específicos.

Recomendaciones
1. Añadir pruebas de integración que incluyan `InventoryIntegration` (mock o integración de test).
2. Reemplazar `print` por logger y unificar los mensajes para soporte internacional.
3. Añadir control de concurrencia si múltiples procesos pueden procesar la misma orden (locks optimistas/pessimistas).
4. Validar que `items_recibidos` contiene los campos esperados antes de pasarlos a `inventory_integration`.

Estado: listo.
