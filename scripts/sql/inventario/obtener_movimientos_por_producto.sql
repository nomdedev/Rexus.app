SELECT id, accion, usuario, fecha, detalles
FROM historial
WHERE accion LIKE 'INVENTARIO_%' AND detalles LIKE ?