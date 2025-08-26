-- Obtener detalle completo de vidrios
SELECT id, codigo, descripcion, tipo, proveedor, espesor,  
       color, precio_m2, estado, ubicacion, observaciones,  
       fecha_creacion, fecha_actualizacion, usuario_creacion, usuario_modificacion
FROM vidrios
WHERE activo = 1
ORDER BY fecha_creacion DESC;
