-- Sumar total de pedidos activos no cancelados
SELECT SUM(total) FROM pedidos WHERE activo = 1 AND estado != 'CANCELADO'