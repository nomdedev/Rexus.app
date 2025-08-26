-- Insertar pedido de vidrios
INSERT INTO pedidos_vidrios
(obra_id, proveedor, fecha_pedido, estado, total_estimado)
VALUES (?, ?, GETDATE(), 'PENDIENTE', ?);
