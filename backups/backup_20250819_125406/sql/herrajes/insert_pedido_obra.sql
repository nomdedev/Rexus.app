INSERT INTO pedidos_herrajes (
    obra_id, proveedor, fecha_pedido, estado, total_estimado
) VALUES (
    ?, ?, GETDATE(), 'PENDIENTE', ?
);