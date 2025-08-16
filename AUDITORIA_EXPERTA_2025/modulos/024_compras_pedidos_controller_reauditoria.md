024 - Re-auditoría profunda: `compras/pedidos/controller.py`

Resumen rápido
- Archivo auditado: `rexus/modules/compras/pedidos/controller.py`.
- Objetivo: revisar autorización, validación y flujo de creación/actualización de pedidos de compras.

Hallazgos clave
- Buen uso de `auth_required` y `permission_required` decoradores, pero existen duplicaciones `@auth_required` en varios métodos.
- Mensajería con `show_success`/`show_error`, pero uso de `print` para logs; mezclar estilos reduce coherencia.
- Métodos devuelven listas/tuplas o booleans dependiendo del flujo; recomendar normalizar respuesta.
- Uso de `PedidosModel` local para operaciones; buena inyección por defecto.

Recomendaciones
1. Eliminar duplicados de decoradores y revisar que `permission_required` recibe permisos correctos.
2. Reemplazar `print` por logger y unificar sistema de logs.
3. Añadir pruebas de permisos para rutas críticas (crear, actualizar estado).
4. Normalizar respuestas (usar estructuras {exito: bool, mensaje: str, data: ...}).

Estado: listo.
