-- Validar si un pedido ya existe por número (para creación)
-- Archivo: validar_pedido_duplicado_creacion.sql

SELECT COUNT(*) 
FROM pedidos 
WHERE numero_pedido = ? 
AND activo = 1;
