-- Actualiza un vidrio existente
UPDATE vidrios 
SET tipo = @tipo, 
    grosor = @grosor, 
    ancho = @ancho, 
    alto = @alto, 
    color = @color,
    precio_unitario = @precio_unitario, 
    stock_actual = @stock_actual, 
    stock_minimo = @stock_minimo,
    fecha_modificacion = @fecha_modificacion
WHERE id = @vidrio_id AND activo = 1
