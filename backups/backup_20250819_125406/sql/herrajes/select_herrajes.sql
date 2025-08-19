SELECT
    id, codigo, descripcion, proveedor, precio_unitario,
    unidad_medida, categoria, estado, observaciones,
    fecha_actualizacion
FROM herrajes
WHERE 1=1
ORDER BY codigo;