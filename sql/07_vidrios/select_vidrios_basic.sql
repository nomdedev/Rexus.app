-- Obtiene todos los vidrios activos básico
SELECT id, tipo, grosor, ancho, alto, color, precio_unitario, 
       stock_actual, stock_minimo, fecha_creacion
FROM vidrios 
WHERE activo = 1
ORDER BY tipo, grosor, ancho, alto
