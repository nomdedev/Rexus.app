SELECT COUNT(*)
FROM pedidos
WHERE numero_pedido = ?
AND id != ?
AND activo = 1;