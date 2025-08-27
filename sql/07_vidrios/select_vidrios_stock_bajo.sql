-- Obtiene vidrios con stock bajo
SELECT id, tipo, grosor, ancho, alto, color, precio_unitario, 
       stock_actual, stock_minimo, fecha_creacion
FROM vidrios 
WHERE activo = 1 AND stock_actual <= stock_minimo
ORDER BY tipo, grosor, ancho, alto
