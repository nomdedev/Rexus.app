-- Obtener entregas base con información de obras y transportes (SQLite)
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
    COALESCE(o.nombre_obra, o.descripcion, 'Sin asignar') as obra_nombre,
    COALESCE(o.direccion, '') as obra_direccion,
    COALESCE(t.codigo, 'Sin asignar') as transporte_codigo,
    COALESCE(t.tipo, 'No especificado') as transporte_tipo,
    COALESCE(t.proveedor, 'Sin proveedor') as transporte_proveedor
FROM entregas e
LEFT JOIN obras o ON e.obra_id = o.id
LEFT JOIN transportes t ON e.transporte_id = t.id
WHERE 1=1