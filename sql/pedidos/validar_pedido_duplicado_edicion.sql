-- Validar si un pedido ya existe por número (para edición)
-- Archivo: validar_pedido_duplicado_edicion.sql

SELECT COUNT(*) 
FROM pedidos 
WHERE numero_pedido = ? 
AND id != ? 
AND activo = 1;
