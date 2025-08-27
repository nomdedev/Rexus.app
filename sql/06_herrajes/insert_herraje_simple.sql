-- Inserta un nuevo herraje (estructura simplificada)
INSERT INTO herrajes (codigo, nombre, tipo, descripcion, precio_unitario, stock_actual, stock_minimo)
VALUES (@codigo, @nombre, @tipo, @descripcion, @precio_unitario, @stock_actual, @stock_minimo)
