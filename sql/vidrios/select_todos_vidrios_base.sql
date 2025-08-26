SELECT id, tipo, espesor, color, precio_m2, proveedor, 
       especificaciones, propiedades, activo, fecha_creacion, 
       fecha_actualizacion, dimensiones, stock, estado
FROM vidrios
WHERE activo = 1
ORDER BY tipo
