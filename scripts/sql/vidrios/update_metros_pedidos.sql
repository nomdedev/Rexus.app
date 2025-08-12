-- Consulta segura para actualizar metros cuadrados pedidos en vidrios_obra
-- Reemplaza f-string en crear_pedido_obra()  
-- Parámetros: metros_cuadrados (float), vidrio_id (int), obra_id (int)

UPDATE [vidrios_obra]
SET metros_cuadrados_pedidos = metros_cuadrados_pedidos + ?
WHERE vidrio_id = ? AND obra_id = ?;