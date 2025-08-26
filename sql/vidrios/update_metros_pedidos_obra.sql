UPDATE vidrios_por_obra 
SET metros_pedidos = metros_pedidos + @metros_cuadrados
WHERE vidrio_id = @vidrio_id AND obra_id = @obra_id
