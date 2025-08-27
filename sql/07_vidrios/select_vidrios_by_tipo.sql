-- Obtiene vidrios por tipo
SELECT id, tipo, grosor, ancho, alto, color, precio_unitario, 
       stock_actual, stock_minimo, fecha_creacion
FROM vidrios 
WHERE activo = 1 AND tipo = @tipo
ORDER BY grosor, ancho, alto
