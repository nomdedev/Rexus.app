-- Obtiene movimientos de inventario desde la tabla historial
SELECT id, accion, usuario, fecha, detalles
FROM historial
WHERE accion LIKE 'INVENTARIO_%'