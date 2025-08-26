-- Obtener detalle completo de vidrios
SELECT id, tipo as tipo, especificaciones as especificaciones, tipo, proveedor, espesor,  
       color, precio_m2, estado, dimensiones as dimensiones, propiedades as propiedades,  
       fecha_creacion, fecha_actualizacion, usuario_creacion, usuario_actualizacion
FROM vidrios
WHERE estado = 'ACTIVO'
ORDER BY fecha_creacion DESC;
