-- Actualizar metros pedidos en vidrios por obra
UPDATE vidrios_por_obra
SET metros_pedidos = metros_pedidos + ?
WHERE vidrio_id = ? AND obra_id = ?;
