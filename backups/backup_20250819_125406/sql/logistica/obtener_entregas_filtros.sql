SELECT
    e.id,
    e.numero_entrega,
    e.fecha_entrega,
    e.estado,
    e.obra_id,
    e.transporte_id,
    e.observaciones,
    o.nombre as obra_nombre,
    o.direccion as obra_direccion,
    t.nombre as transporte_nombre,
    t.tipo as transporte_tipo
FROM [entregas] e
LEFT JOIN [obras] o ON e.obra_id = o.id
LEFT JOIN [transportes] t ON e.transporte_id = t.id
WHERE 1=1