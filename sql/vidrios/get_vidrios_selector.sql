-- Obtener vidrios para selector
SELECT v.id, v.tipo as codigo, v.especificaciones as descripcion, v.tipo, v.proveedor,    
       v.espesor, v.color, v.precio_m2, v.estado, v.dimensiones as ubicacion,
       v.propiedades as observaciones, v.fecha_creacion
FROM vidrios v
WHERE v.estado = 'ACTIVO'
ORDER BY v.tipo, v.especificaciones;
