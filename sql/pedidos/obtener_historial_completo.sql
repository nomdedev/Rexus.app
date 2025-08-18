-- Obtener historial completo de estado
SELECT * FROM pedidos_historial
WHERE pedido_id = ?
ORDER BY fecha_cambio DESC