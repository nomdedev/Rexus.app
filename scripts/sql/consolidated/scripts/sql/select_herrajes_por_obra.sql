SELECT
    h.id, h.codigo, h.descripcion, h.proveedor, h.precio_unitario,
    h.unidad_medida, ho.cantidad_requerida, ho.cantidad_pedida,
    ho.fecha_asignacion, ho.observaciones as obs_obra
FROM productos h
INNER JOIN productos_obra ho ON h.id = ho.herraje_id
WHERE ho.obra_id = ?
ORDER BY h.codigo;