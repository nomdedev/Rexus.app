INSERT INTO lotes_inventario
(producto_id, numero_lote, fecha_vencimiento, cantidad,
 proveedor, fecha_recepcion, serie, usuario, observaciones)
VALUES (?, ?, ?, ?, ?, GETDATE(), ?, ?, ?)