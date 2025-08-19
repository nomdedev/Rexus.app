SELECT COUNT(*)
FROM pedidos
WHERE numero_pedido = ?
AND activo = 1;