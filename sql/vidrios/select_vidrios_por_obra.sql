SELECT v.id, v.tipo as codigo, v.especificaciones as descripcion, v.tipo, v.proveedor,
       v.espesor, v.color, v.precio_m2, v.estado, v.dimensiones as ubicacion,
       vo.cantidad_utilizada, vo.fecha_asignacion
FROM vidrios v
INNER JOIN vidrios_por_obra vo ON v.id = vo.vidrio_id
WHERE vo.obra_id = @obra_id
ORDER BY v.tipo