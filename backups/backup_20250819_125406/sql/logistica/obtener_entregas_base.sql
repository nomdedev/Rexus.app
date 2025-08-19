SELECT
    e.id,
    e.id as numero_entrega,
    e.fecha_programada,
    e.fecha_entrega,
    e.estado,
    e.obra_id,
    e.transporte_id,
    e.observaciones,
    e.direccion_entrega,
    e.contacto,
    e.telefono,
    e.costo_envio,
    ISNULL(o.nombre, 'Sin asignar') as obra_nombre,
    ISNULL(o.direccion, '') as obra_direccion,
    ISNULL(t.codigo, 'Sin asignar') as transporte_codigo,
    ISNULL(t.tipo, 'No especificado') as transporte_tipo,
    ISNULL(t.proveedor, 'Sin proveedor') as transporte_proveedor
FROM [entregas] e
LEFT JOIN [obras] o ON e.obra_id = o.id
LEFT JOIN [transportes] t ON e.transporte_id = t.id
WHERE 1=1