-- Actualizar totales del pedido
-- Archivo: actualizar_totales_pedido.sql

UPDATE pedidos 
SET subtotal = ?, 
    descuento = ?, 
    impuestos = ?, 
    total = ?
WHERE id = ?;
