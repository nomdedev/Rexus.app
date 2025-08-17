-- Crear nueva orden de compra
INSERT INTO compras
(proveedor, numero_orden, fecha_pedido, fecha_entrega_estimada,
 estado, observaciones, usuario_creacion, descuento, impuestos,
 fecha_creacion, fecha_actualizacion)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE(), GETDATE())