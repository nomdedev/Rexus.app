-- Obtiene información completa de un vidrio por ID
SELECT id, tipo, grosor, ancho, alto, color, precio_unitario, 
       stock_actual, stock_minimo, fecha_creacion, fecha_modificacion
FROM vidrios 
WHERE id = @vidrio_id AND activo = 1
