019 - Re-auditoría profunda: `pedidos/controller.py`

Resumen rápido
- Archivo auditado: `rexus/modules/pedidos/controller.py`.
- Objetivo: validar controles de integridad de pedidos, paginación y manejo de estados.

Hallazgos
- Buen manejo de paginación y separación de responsabilidades.
- Validación detallada en `validar_datos_pedido` con chequeos de fecha, cantidades y precios.
- Uso de `try/except` amplio en métodos clave; se deben capturar excepciones específicas.
- Métodos `actualizar_pedido` y `eliminar_pedido` contienen TODOs; riesgo funcional si se espera comportamiento completo.

Recomendaciones
1. Completar `actualizar_pedido` y `eliminar_pedido` con lógica del modelo y tests.
2. Cambiar `print` por `logger` y capturar excepciones específicas.
3. Añadir pruebas de validación de `validar_datos_pedido` con casos límite.

Estado: listo.
