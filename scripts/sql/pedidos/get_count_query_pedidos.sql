-- Consulta de conteo para paginación de pedidos  
-- Archivo: get_count_query_pedidos.sql

SELECT COUNT(*) FROM pedidos WHERE activo = 1;
