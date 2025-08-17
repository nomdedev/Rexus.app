-- scripts/sql/logistica/eliminar_producto_entrega.sql
-- Elimina un producto específico de una entrega
-- Parámetro: id (int) - ID del detalle de entrega a eliminar

DELETE FROM [detalle_entregas] 
WHERE id = ?;
