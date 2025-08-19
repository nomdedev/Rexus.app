UPDATE [vidrios_obra]
SET metros_cuadrados_pedidos = metros_cuadrados_pedidos + ?
WHERE vidrio_id = ? AND obra_id = ?;