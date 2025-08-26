SELECT id, codigo, nombre, tipo, descripcion, precio_unitario, stock_actual, stock_minimo
FROM herrajes 
WHERE codigo = @codigo
