-- Obtener vidrios para selector
SELECT v.id, v.codigo, v.descripcion, v.tipo, v.proveedor,    
       v.espesor, v.color, v.precio_m2, v.estado, v.ubicacion,
       v.observaciones, v.fecha_creacion
FROM vidrios v
WHERE v.activo = 1
ORDER BY v.tipo, v.descripcion;
