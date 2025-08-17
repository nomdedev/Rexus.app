-- Crea un nuevo pago de material
-- Parámetros: producto, proveedor, cantidad, precio_unitario, total, pagado, pendiente, estado, fecha_compra, fecha_pago, usuario_creacion
INSERT INTO pagos_materiales
(producto, proveedor, cantidad, precio_unitario, total, pagado,
 pendiente, estado, fecha_compra, fecha_pago, usuario_creacion)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)