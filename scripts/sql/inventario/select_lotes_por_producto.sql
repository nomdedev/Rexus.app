SELECT id, producto_id, numero_lote, fecha_vencimiento, cantidad,
       proveedor, fecha_recepcion, serie, observaciones
FROM lotes_inventario
WHERE producto_id = ?
ORDER BY fecha_recepcion DESC, fecha_vencimiento