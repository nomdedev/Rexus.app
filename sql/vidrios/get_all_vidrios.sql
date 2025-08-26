-- Obtener todos los vidrios
SELECT id, tipo, espesor, color, precio_m2, proveedor,
       especificaciones, propiedades, activo, fecha_creacion,
       fecha_actualizacion, usuario_creacion, usuario_actualizacion
FROM vidrios
WHERE activo = 1
ORDER BY fecha_creacion DESC;
