-- Consulta base para paginación de pedidos
-- Archivo: get_base_query_pedidos.sql

SELECT * FROM pedidos WHERE activo = 1 ORDER BY fecha_pedido DESC;
