UPDATE herrajes_obra
SET cantidad_pedida = cantidad_pedida + @cantidad
WHERE herraje_id = @herraje_id AND obra_id = @obra_id;