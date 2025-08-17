-- Buscar vidrios asociados a una obra específica
SELECT 
    v.id,
    v.codigo_vidrio,
    v.descripcion,
    v.espesor,
    v.tipo_vidrio,
    v.color,
    vo.cantidad_asignada,
    vo.cantidad_utilizada,
    vo.fecha_asignacion,
    vo.estado_asignacion
FROM vidrios v
INNER JOIN vidrios_obra vo ON v.id = vo.vidrio_id
WHERE vo.obra_id = ?
AND v.estado = 'ACTIVO'
ORDER BY vo.fecha_asignacion DESC